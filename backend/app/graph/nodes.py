"""
LangGraph 节点实现
每个节点对应一个子智能体的实际执行
"""
import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.types import Send

from ..agents import ProfilerAgent, ResourceGeneratorAgent, PathPlannerAgent, TutorAgent
from ..services.llm_factory import LLMFactory
from ..core.safety import SafetyGuard
from .state import AgentState, AgentStep

logger = logging.getLogger("graph.nodes")

# ---------- 声明式路由配置 ----------
# 每种 task_type 对应的 Agent 执行步骤序列，按顺序执行
TASK_ROUTES: Dict[str, List[str]] = {
    "profile_update": ["profiler"],
    "resource_generation": ["profiler", "resource_generator"],
    "path_planning": ["profiler", "path_planner", "resource_generator"],
    "tutoring": ["tutor"],
}

# ---------- 并行路由配置（V2，支持 parallel_group）----------
TASK_ROUTES_V2: Dict[str, List[AgentStep]] = {
    "profile_update": [
        AgentStep(agent_name="profiler", display_name="画像师"),
    ],
    "resource_generation": [
        AgentStep(agent_name="profiler", display_name="画像师"),
        AgentStep(agent_name="resource_generator", display_name="资源生成师"),
    ],
    "path_planning": [
        AgentStep(agent_name="profiler", display_name="画像师"),
        AgentStep(agent_name="path_planner", display_name="路径规划师"),
        AgentStep(agent_name="resource_generator", display_name="资源生成师"),
    ],
    "tutoring": [
        AgentStep(agent_name="tutor", display_name="辅导助手"),
    ],
    # 示例：错误分析任务（支持并行）
    # "error_analysis": [
    #     AgentStep(agent_name="profiler", display_name="画像师"),
    #     AgentStep(agent_name="error_catcher", display_name="错误捕捉", parallel_group="analysis"),
    #     AgentStep(agent_name="misconception_tracer", display_name="思维溯源", parallel_group="analysis"),
    #     AgentStep(agent_name="tutor", display_name="辅导助手", depends_on=["error_catcher", "misconception_tracer"]),
    # ],
}

# ---------- 单节点重试 ----------

async def _call_with_retry(
    agent_fn,
    context: Dict[str, Any],
    max_retries: int = 2,
    timeout: float = 30.0,
) -> Dict[str, Any]:
    """带指数退避重试的 Agent 调用包装"""
    last_error = None
    for attempt in range(max_retries + 1):
        try:
            return await asyncio.wait_for(agent_fn(context), timeout=timeout)
        except asyncio.TimeoutError:
            last_error = f"timeout after {timeout}s"
            if attempt < max_retries:
                wait = 2 ** attempt  # 1s, 2s
                logger.warning(f"Agent retry {attempt + 1}/{max_retries}, waiting {wait}s")
                await asyncio.sleep(wait)
        except Exception as e:
            last_error = str(e)
            if attempt < max_retries:
                wait = 2 ** attempt
                logger.warning(f"Agent retry {attempt + 1}/{max_retries} after error: {e}")
                await asyncio.sleep(wait)
    return {"status": "error", "message": f"Failed after {max_retries + 1} attempts: {last_error}"}

# Agent 工作流事件推送（轻量级，不影响核心逻辑）
try:
    from ..api.agent_flow import flow_store
except ImportError:
    flow_store = None


# 全局智能体实例（通过 LLMFactory 统一获取，支持 spark / deepseek / openai）
_llm = LLMFactory.get_default_llm()
_profiler = ProfilerAgent(llm=_llm)
_resource_gen = ResourceGeneratorAgent(llm=_llm)
_path_planner = PathPlannerAgent(llm=_llm)
_tutor = TutorAgent(llm=_llm)


def _safe_topic(ctx: Dict[str, Any]) -> str:
    topic = ctx.get("topic", "")
    if not topic:
        return "未指定主题"
    check = SafetyGuard.check_input(topic)
    return topic if check["safe"] else "通用学习内容"


# ---------- 事件推送辅助 ----------
def _push(run_id: str, node: str, status: str, task: str = "", log: str = ""):
    if flow_store and run_id:
        flow_store.push_event(run_id, node, status, task, log)


# ---------- Supervisor ----------
async def supervisor_node(state: AgentState) -> Dict[str, Any]:
    """
    路由调度节点：根据声明式配置决定下一步执行哪个智能体。
    支持串行和并行（通过 AgentStep.parallel_group + LangGraph Send）。
    """
    run_id = state.get("context", {}).get("_run_id", "")
    _push(run_id, "supervisor", "running", "分析任务类型，路由到对应智能体...")
    task_type = state["task_type"]
    results = state.get("results", {})
    iteration = state.get("iteration", 0)

    # 防止无限循环
    if iteration >= 8:
        return {"next_agent": "finish", "iteration": iteration + 1}

    # 优先使用 V2 配置（支持并行）
    steps_v2 = TASK_ROUTES_V2.get(task_type)
    if steps_v2:
        return await _route_v2(state, steps_v2, results, iteration, run_id)

    # 降级到 V1 简单配置
    steps = TASK_ROUTES.get(task_type)
    if not steps:
        _push(run_id, "supervisor", "completed", f"未知任务类型: {task_type}，直接汇总")
        return {"next_agent": "finish", "iteration": iteration + 1}

    for step in steps:
        if step not in results:
            _push(run_id, "supervisor", "completed", f"路由决策：调用 {step}")
            return {"next_agent": step, "iteration": iteration + 1}

    _push(run_id, "supervisor", "completed", "所有任务完成，进入汇总")
    return {"next_agent": "finish", "iteration": iteration + 1}


async def _route_v2(
    state: AgentState,
    steps: List[AgentStep],
    results: Dict[str, Any],
    iteration: int,
    run_id: str,
) -> Dict[str, Any]:
    """V2 路由：支持依赖检查和并行 fan-out"""
    # 找出所有就绪的步骤（未完成 + 依赖已满足）
    ready_steps: List[AgentStep] = []
    for step in steps:
        if step.agent_name in results:
            continue
        deps_met = all(dep in results for dep in step.depends_on)
        if deps_met:
            ready_steps.append(step)

    if not ready_steps:
        _push(run_id, "supervisor", "completed", "所有任务完成，进入汇总")
        return {"next_agent": "finish", "iteration": iteration + 1}

    # 检查是否有可并行的步骤（同一 parallel_group）
    parallel_groups: Dict[str, List[AgentStep]] = {}
    sequential: List[AgentStep] = []
    for step in ready_steps:
        if step.parallel_group:
            parallel_groups.setdefault(step.parallel_group, []).append(step)
        else:
            sequential.append(step)

    # 如果有并行组且组内有多个步骤，通过 _parallel_agents 通知 router_edge
    for group_name, group_steps in parallel_groups.items():
        if len(group_steps) > 1:
            _push(run_id, "supervisor", "completed", f"并行调度：{group_name} 组内 {len(group_steps)} 个步骤")
            return {
                "next_agent": "__parallel__",
                "iteration": iteration + 1,
                "_parallel_agents": [s.agent_name for s in group_steps],
            }

    # 串行：取第一个就绪步骤
    next_step = ready_steps[0]
    _push(run_id, "supervisor", "completed", f"路由决策：调用 {next_step.display_name or next_step.agent_name}")
    return {"next_agent": next_step.agent_name, "iteration": iteration + 1}


# ---------- Profiler ----------
async def profiler_node(state: AgentState) -> Dict[str, Any]:
    run_id = state.get("context", {}).get("_run_id", "")
    _push(run_id, "profiler", "running", "正在分析学生画像，提取6维特征...")
    ctx = state.get("context", {})
    profile = state.get("profile", {})
    inputs = ctx.get("inputs", [])
    if not inputs and ctx.get("user_request"):
        inputs = [ctx.get("user_request")]

    action = ctx.get("profile_action", "update")

    def _profiler_cache_key(ctx: Dict[str, Any]) -> str:
        from ..core.cache import prompt_cache
        salt = f"{ctx.get('student_id', '')}_{ctx.get('action', '')}"
        return prompt_cache.hash_prompt({"inputs": ctx.get("inputs", [])}, extra_salt=salt)

    result = await _call_with_retry(
        lambda ctx: _profiler.cached_process(ctx, cache_key_fn=_profiler_cache_key),
        {
            "action": action,
            "student_id": state["student_id"],
            "inputs": inputs,
            "current_profile": profile,
        },
    )

    updates: Dict[str, Any] = {"results": {"profiler": result}}
    if result.get("status") == "success" and "profile" in result:
        updates["profile"] = result["profile"]
        updates["messages"] = [
            SystemMessage(content=f"[画像师] 学生画像已更新: {json.dumps(result['profile'], ensure_ascii=False)[:300]}...")
        ]
        _push(run_id, "profiler", "completed", "画像分析完成，6维特征已提取")
    else:
        updates["messages"] = [
            SystemMessage(content=f"[画像师] 执行结果: {json.dumps(result, ensure_ascii=False)[:300]}")
        ]
        _push(run_id, "profiler", "completed", "画像分析完成")
    return updates


# ---------- Resource Generator ----------
async def resource_generator_node(state: AgentState) -> Dict[str, Any]:
    run_id = state.get("context", {}).get("_run_id", "")
    _push(run_id, "resource_generator", "running", "正在生成个性化学习资源...")
    ctx = state.get("context", {})
    profile = state.get("profile", {})
    task = ctx.get("resource_task", "generate_document")

    # 如果是路径规划后的资源匹配
    if state["task_type"] == "path_planning" and "path_planner" in state.get("results", {}):
        path_data = state["results"]["path_planner"]
        path_nodes = []
        if isinstance(path_data.get("path"), dict):
            stages = path_data["path"].get("stages", [])
            path_nodes = [s.get("title", "") for s in stages]
        result = await _call_with_retry(
            _resource_gen.process,
            {
                "task": "match_resources",
                "topic": ctx.get("topic", ""),
                "path_nodes": path_nodes,
                "profile": profile,
            },
        )
    else:
        def _resource_cache_key(ctx: Dict[str, Any]) -> str:
            from ..core.cache import prompt_cache
            return prompt_cache.hash_prompt(
                {"task": ctx.get("task", ""), "topic": ctx.get("topic", ""), "difficulty": ctx.get("difficulty", "")},
                extra_salt="resource_gen",
            )

        result = await _call_with_retry(
            lambda ctx: _resource_gen.cached_process(ctx, cache_key_fn=_resource_cache_key),
            {
                "task": task,
                "topic": _safe_topic(ctx),
                "difficulty": ctx.get("difficulty", profile.get("knowledge_level", "medium")),
                "cognitive_style": profile.get("cognitive_style", {}).get("primary", "visual"),
                "profile": profile,
                "constraints": ctx.get("constraints", {}),
            },
        )

    _push(run_id, "resource_generator", "completed", "资源生成完成")
    return {
        "results": {"resource_generator": result},
        "messages": [
            SystemMessage(content=f"[资源生成师] 执行结果: {json.dumps(result, ensure_ascii=False)[:300]}")
        ],
    }


# ---------- Path Planner ----------
async def path_planner_node(state: AgentState) -> Dict[str, Any]:
    run_id = state.get("context", {}).get("_run_id", "")
    _push(run_id, "path_planner", "running", "正在规划DAG学习路径...")
    ctx = state.get("context", {})
    profile = state.get("profile", {})
    task = ctx.get("path_task", "generate_path")

    def _path_planner_cache_key(ctx: Dict[str, Any]) -> str:
        from ..core.cache import prompt_cache
        salt = f"{ctx.get('student_id', '')}_{ctx.get('target', '')}"
        return prompt_cache.hash_prompt(
            {"task": ctx.get("task", ""), "feedback": ctx.get("feedback", "")},
            extra_salt=salt,
        )

    result = await _call_with_retry(
        lambda ctx: _path_planner.cached_process(ctx, cache_key_fn=_path_planner_cache_key),
        {
            "task": task,
            "student_id": state["student_id"],
            "profile": profile,
            "target": ctx.get("target", ctx.get("topic", "未指定目标")),
            "current_path": ctx.get("current_path", {}),
            "feedback": ctx.get("feedback", ""),
        },
    )

    _push(run_id, "path_planner", "completed", "学习路径规划完成")
    return {
        "results": {"path_planner": result},
        "messages": [
            SystemMessage(content=f"[路径规划师] 执行结果: {json.dumps(result, ensure_ascii=False)[:300]}")
        ],
    }


# ---------- Tutor ----------
async def tutor_node(state: AgentState) -> Dict[str, Any]:
    run_id = state.get("context", {}).get("_run_id", "")
    _push(run_id, "tutor", "running", "正在生成个性化辅导回答...")
    ctx = state.get("context", {})
    profile = state.get("profile", {})
    question = ctx.get("question", ctx.get("user_request", ""))
    session_id = ctx.get("session_id", f"{state['student_id']}_default")

    result = await _call_with_retry(
        _tutor.process,
        {
            "task": "answer_question",
            "session_id": session_id,
            "question": question,
            "profile": profile,
        },
        timeout=45.0,  # 辅导回答可能较慢
    )

    _push(run_id, "tutor", "completed", "辅导回答生成完成")
    return {
        "results": {"tutor": result},
        "messages": [
            HumanMessage(content=question),
            SystemMessage(content=f"[辅导助手] {result.get('answer', '')}"),
        ],
    }


# ---------- Assembler ----------
async def assembler_node(state: AgentState) -> Dict[str, Any]:
    """结果汇总节点"""
    run_id = state.get("context", {}).get("_run_id", "")
    _push(run_id, "assembler", "running", "正在汇总所有智能体结果...")
    results = state.get("results", {})
    task_type = state["task_type"]

    failed = [k for k, v in results.items() if isinstance(v, dict) and v.get("status") in ("failed", "blocked")]
    success_count = len(results) - len(failed)

    final_output = {
        "status": "partial_failure" if failed else "success",
        "task_type": task_type,
        "student_id": state["student_id"],
        "assembled_at": datetime.now(timezone.utc).isoformat(),
        "completed_agents": list(results.keys()),
        "failed_agents": failed,
        "summary": f"成功执行 {success_count}/{len(results)} 个智能体",
        "data": results,
    }

    # 针对 tutoring 直接透出回答
    if task_type == "tutoring" and "tutor" in results:
        final_output["answer"] = results["tutor"].get("answer", "")

    _push(run_id, "assembler", "completed", f"汇总完成：{success_count}/{len(results)} 个智能体成功")
    return {"final_output": final_output, "next_agent": "__end__"}


# 路由函数
def router_edge(state: AgentState):
    """
    路由函数：返回 str 或 list[Send]。
    当 supervisor_node 调度并行任务时，构造 Send 对象列表。
    """
    parallel_agents = state.get("_parallel_agents")
    if parallel_agents and isinstance(parallel_agents, list):
        iteration = state.get("iteration", 0)
        sends = []
        for agent_name in parallel_agents:
            sends.append(Send(agent_name, {
                **state,
                "next_agent": agent_name,
                "iteration": iteration + 1,
            }))
        return sends
    return state["next_agent"]
