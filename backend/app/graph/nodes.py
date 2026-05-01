"""
LangGraph 节点实现
每个节点对应一个子智能体的实际执行
"""
import json
from datetime import datetime, timezone
from typing import Any, Dict

from langchain_core.messages import HumanMessage, SystemMessage

from ..agents import ProfilerAgent, ResourceGeneratorAgent, PathPlannerAgent, TutorAgent
from ..services.llm_factory import LLMFactory
from ..core.safety import SafetyGuard
from .state import AgentState


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


# ---------- Supervisor ----------
async def supervisor_node(state: AgentState) -> Dict[str, Any]:
    """
    课程设计师节点：根据当前状态决定下一步执行哪个智能体。
    """
    task_type = state["task_type"]
    results = state.get("results", {})
    iteration = state.get("iteration", 0)

    # 防止无限循环
    if iteration >= 8:
        return {"next_agent": "finish", "iteration": iteration + 1}

    # 根据任务类型和已有结果做路由决策
    if task_type == "profile_update":
        if "profiler" not in results:
            return {"next_agent": "profiler", "iteration": iteration + 1}
        return {"next_agent": "finish", "iteration": iteration + 1}

    if task_type == "resource_generation":
        if "profiler" not in results:
            return {"next_agent": "profiler", "iteration": iteration + 1}
        if "resource_generator" not in results:
            return {"next_agent": "resource_generator", "iteration": iteration + 1}
        return {"next_agent": "finish", "iteration": iteration + 1}

    if task_type == "path_planning":
        if "profiler" not in results:
            return {"next_agent": "profiler", "iteration": iteration + 1}
        if "path_planner" not in results:
            return {"next_agent": "path_planner", "iteration": iteration + 1}
        if "resource_generator" not in results:
            # 路径规划完后匹配资源
            return {"next_agent": "resource_generator", "iteration": iteration + 1}
        return {"next_agent": "finish", "iteration": iteration + 1}

    if task_type == "tutoring":
        if "tutor" not in results:
            return {"next_agent": "tutor", "iteration": iteration + 1}
        return {"next_agent": "finish", "iteration": iteration + 1}

    # 默认兜底
    return {"next_agent": "finish", "iteration": iteration + 1}


# ---------- Profiler ----------
async def profiler_node(state: AgentState) -> Dict[str, Any]:
    ctx = state.get("context", {})
    profile = state.get("profile", {})
    inputs = ctx.get("inputs", [])
    if not inputs and ctx.get("user_request"):
        inputs = [ctx.get("user_request")]

    action = ctx.get("profile_action", "update")
    result = await _profiler.process({
        "action": action,
        "student_id": state["student_id"],
        "inputs": inputs,
        "current_profile": profile,
    })

    updates: Dict[str, Any] = {"results": {"profiler": result}}
    if result.get("status") == "success" and "profile" in result:
        updates["profile"] = result["profile"]
        updates["messages"] = [
            SystemMessage(content=f"[画像师] 学生画像已更新: {json.dumps(result['profile'], ensure_ascii=False)[:300]}...")
        ]
    else:
        updates["messages"] = [
            SystemMessage(content=f"[画像师] 执行结果: {json.dumps(result, ensure_ascii=False)[:300]}")
        ]
    return updates


# ---------- Resource Generator ----------
async def resource_generator_node(state: AgentState) -> Dict[str, Any]:
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
        result = await _resource_gen.process({
            "task": "match_resources",
            "topic": ctx.get("topic", ""),
            "path_nodes": path_nodes,
            "profile": profile,
        })
    else:
        result = await _resource_gen.process({
            "task": task,
            "topic": _safe_topic(ctx),
            "difficulty": ctx.get("difficulty", profile.get("knowledge_level", "medium")),
            "cognitive_style": profile.get("cognitive_style", {}).get("primary", "visual"),
            "profile": profile,
            "constraints": ctx.get("constraints", {}),
        })

    return {
        "results": {"resource_generator": result},
        "messages": [
            SystemMessage(content=f"[资源生成师] 执行结果: {json.dumps(result, ensure_ascii=False)[:300]}")
        ],
    }


# ---------- Path Planner ----------
async def path_planner_node(state: AgentState) -> Dict[str, Any]:
    ctx = state.get("context", {})
    profile = state.get("profile", {})
    task = ctx.get("path_task", "generate_path")

    result = await _path_planner.process({
        "task": task,
        "student_id": state["student_id"],
        "profile": profile,
        "target": ctx.get("target", ctx.get("topic", "未指定目标")),
        "current_path": ctx.get("current_path", {}),
        "feedback": ctx.get("feedback", ""),
    })

    return {
        "results": {"path_planner": result},
        "messages": [
            SystemMessage(content=f"[路径规划师] 执行结果: {json.dumps(result, ensure_ascii=False)[:300]}")
        ],
    }


# ---------- Tutor ----------
async def tutor_node(state: AgentState) -> Dict[str, Any]:
    ctx = state.get("context", {})
    profile = state.get("profile", {})
    question = ctx.get("question", ctx.get("user_request", ""))
    session_id = ctx.get("session_id", f"{state['student_id']}_default")

    result = await _tutor.process({
        "task": "answer_question",
        "session_id": session_id,
        "question": question,
        "profile": profile,
    })

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

    return {"final_output": final_output, "next_agent": "__end__"}


# 路由函数
def router_edge(state: AgentState) -> str:
    return state["next_agent"]
