"""
课程设计师智能体
主管智能体，负责任务分解、流程编排、质量把控
现在可以直接调用真实子智能体实例执行子任务
"""
from typing import Any, Dict, List, Optional
from datetime import datetime
import asyncio

from .base import BaseAgent, AgentMessage
from .profiler import ProfilerAgent
from .resource_generator import ResourceGeneratorAgent
from .path_planner import PathPlannerAgent
from .tutor import TutorAgent
from ..services.llm_factory import BaseLLM, LLMFactory


class CourseDesignerAgent(BaseAgent):
    """
    课程设计师智能体 - 系统中枢
    负责任务接收、分解、调度和质量把控
    """

    def __init__(self, llm: Optional[BaseLLM] = None):
        super().__init__(
            agent_id="course_designer",
            agent_name="课程设计师",
            description="负责任务分解和流程编排的主管智能体"
        )
        self.sub_agents: Dict[str, BaseAgent] = {}
        self.task_history: List[Dict] = []
        self.llm = llm or LLMFactory.get_default_llm()
        self._init_default_sub_agents()

    def _init_default_sub_agents(self):
        """初始化默认子智能体"""
        self.register_sub_agent("profiler", ProfilerAgent(self.llm))
        self.register_sub_agent("resource_generator", ResourceGeneratorAgent(self.llm))
        self.register_sub_agent("path_planner", PathPlannerAgent(self.llm))
        self.register_sub_agent("tutor", TutorAgent(self.llm))

    def register_sub_agent(self, agent_id: str, agent: BaseAgent):
        """注册子智能体"""
        self.sub_agents[agent_id] = agent
        self.logger.info(f"Sub-agent '{agent_id}' registered")

    def get_system_prompt(self) -> str:
        return """你是"课程设计师"，一个专业的学习系统架构师。

【角色职责】
1. 理解学生的学习需求，转化为可执行的任务
2. 将复杂任务拆解为子任务，分配给合适的智能体
3. 协调各智能体的执行顺序和依赖关系
4. 把控最终输出质量

【决策原则】
- 任务分解要合理，避免子任务过于细碎或庞大
- 充分考虑学生画像，匹配合适的资源类型
- 优先保证核心功能，加分项作为增强
- 质量不达标的输出必须要求修正

【可用子智能体】
- profiler: 画像师，负责查询和更新学生画像
- resource_generator: 资源生成师，负责生成多模态学习资源
- path_planner: 路径规划师，负责规划学习路径
- tutor: 辅导助手，负责答疑和辅导

【输出格式】
所有输出必须是JSON格式，包含：
{
    "task_plan": {"子任务列表"},
    "execution_order": ["执行顺序"],
    "quality_criteria": {"质量标准"},
    "estimated_time": "预估时间"
}

重要：不要输出思考过程、分析步骤或'让我想想'之类的内心独白，直接输出最终JSON结果。"""

    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        核心处理流程
        """
        self.status = "running"
        task_type = context.get("task_type", "unknown")
        student_id = context.get("student_id")

        self.logger.info(f"Processing task: {task_type} for student {student_id}")

        try:
            # 1. 查询学生画像（通过 profiler）
            profile = await self._get_student_profile(student_id)

            # 2. 解析需求
            requirements = self._parse_requirements(context, profile)

            # 3. 制定任务计划
            task_plan = self._create_task_plan(task_type, requirements, profile)

            # 4. 执行子任务（并行或串行）
            results = await self._execute_sub_tasks(task_plan, context, profile)

            # 5. 质量检查和汇总
            final_output = await self._assemble_output(results, requirements)

            self.status = "completed"
            return {
                "status": "success",
                "task_type": task_type,
                "student_id": student_id,
                "task_plan": task_plan,
                "results": results,
                "final_output": final_output,
                "completed_at": datetime.now().isoformat()
            }

        except Exception as e:
            self.status = "failed"
            self.logger.error(f"Task failed: {str(e)}")
            return {
                "status": "failed",
                "error": str(e),
                "task_type": task_type
            }

    async def _get_student_profile(self, student_id: str) -> Dict[str, Any]:
        """获取学生画像 - 调用 profiler 智能体"""
        profiler = self.sub_agents.get("profiler")
        if profiler:
            result = await profiler.process({
                "action": "analyze",
                "student_id": student_id,
                "inputs": [f"查询学生 {student_id} 的画像"],
            })
            if result.get("status") == "success" and "profile" in result:
                return result["profile"]
        # fallback
        return {
            "student_id": student_id,
            "cognitive_style": "visual",
            "knowledge_level": "intermediate",
            "weak_areas": ["recursion", "dynamic_programming"],
            "preferred_content_types": ["video", "interactive"],
            "study_pace": "moderate"
        }

    def _parse_requirements(
        self,
        context: Dict[str, Any],
        profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """解析需求"""
        user_request = context.get("user_request", "")

        # 分析请求类型
        if "生成" in user_request or "资源" in user_request:
            req_type = "resource_generation"
        elif "路径" in user_request or "规划" in user_request:
            req_type = "path_planning"
        elif "辅导" in user_request or "问题" in user_request:
            req_type = "tutoring"
        else:
            req_type = "general"

        return {
            "request_type": req_type,
            "user_request": user_request,
            "target_topic": context.get("topic", ""),
            "difficulty": context.get("difficulty", profile.get("knowledge_level", "medium")),
            "cognitive_style": profile.get("cognitive_style", "visual"),
            "constraints": context.get("constraints", {})
        }

    def _create_task_plan(
        self,
        task_type: str,
        requirements: Dict[str, Any],
        profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """创建任务计划"""

        if task_type == "resource_generation":
            return {
                "task_type": "resource_generation",
                "sub_tasks": [
                    {
                        "id": "st_1",
                        "agent": "resource_generator",
                        "task": "generate_outline",
                        "params": {
                            "topic": requirements["target_topic"],
                            "difficulty": requirements["difficulty"]
                        },
                        "dependencies": []
                    },
                    {
                        "id": "st_2",
                        "agent": "resource_generator",
                        "task": "generate_document",
                        "params": {
                            "cognitive_style": requirements["cognitive_style"]
                        },
                        "dependencies": ["st_1"]
                    },
                    {
                        "id": "st_3",
                        "agent": "resource_generator",
                        "task": "generate_questions",
                        "params": {"count": 5},
                        "dependencies": ["st_1"]
                    },
                    {
                        "id": "st_4",
                        "agent": "resource_generator",
                        "task": "generate_code_examples",
                        "params": {"language": "Python"},
                        "dependencies": ["st_1"]
                    },
                    {
                        "id": "st_5",
                        "agent": "resource_generator",
                        "task": "generate_mindmap",
                        "params": {},
                        "dependencies": ["st_1"]
                    }
                ],
                "parallel_groups": [
                    ["st_1"],
                    ["st_2", "st_3", "st_4", "st_5"]
                ]
            }

        elif task_type == "path_planning":
            return {
                "task_type": "path_planning",
                "sub_tasks": [
                    {
                        "id": "st_1",
                        "agent": "path_planner",
                        "task": "analyze_knowledge_state",
                        "params": {},
                        "dependencies": []
                    },
                    {
                        "id": "st_2",
                        "agent": "path_planner",
                        "task": "generate_path",
                        "params": {
                            "target": requirements["target_topic"]
                        },
                        "dependencies": ["st_1"]
                    },
                    {
                        "id": "st_3",
                        "agent": "resource_generator",
                        "task": "match_resources",
                        "params": {},
                        "dependencies": ["st_2"]
                    }
                ]
            }

        else:
            return {
                "task_type": "general",
                "sub_tasks": [
                    {
                        "id": "st_1",
                        "agent": "tutor",
                        "task": "answer_question",
                        "params": {"question": requirements["user_request"]},
                        "dependencies": []
                    }
                ]
            }

    async def _execute_sub_tasks(
        self,
        task_plan: Dict[str, Any],
        context: Dict[str, Any],
        profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行子任务 - 调用真实子智能体"""
        sub_tasks = task_plan.get("sub_tasks", [])
        parallel_groups = task_plan.get("parallel_groups", [])

        results = {}
        completed_tasks = set()

        for group in parallel_groups:
            # 获取当前组可执行的任务
            group_tasks = [st for st in sub_tasks if st["id"] in group]

            # 并行执行
            tasks = []
            for st in group_tasks:
                task = self._execute_single_sub_task(st, context, profile, results)
                tasks.append(task)

            group_results = await asyncio.gather(*tasks, return_exceptions=True)

            # 收集结果
            for st, result in zip(group_tasks, group_results):
                if isinstance(result, Exception):
                    self.logger.error(f"Sub-task {st['id']} failed: {str(result)}")
                    results[st["id"]] = {"status": "failed", "error": str(result)}
                else:
                    results[st["id"]] = result
                    completed_tasks.add(st["id"])

        return results

    async def _execute_single_sub_task(
        self,
        sub_task: Dict[str, Any],
        context: Dict[str, Any],
        profile: Dict[str, Any],
        previous_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行单个子任务 - 调用真实子智能体"""
        agent_id = sub_task["agent"]
        task = sub_task["task"]
        params = sub_task["params"]

        self.logger.info(f"Executing sub-task: {sub_task['id']} via {agent_id}")

        agent = self.sub_agents.get(agent_id)
        if not agent:
            return {
                "status": "failed",
                "error": f"Agent '{agent_id}' not found"
            }

        # 构造子智能体的 context
        agent_context = {
            "task": task,
            "topic": context.get("topic", params.get("topic", "")),
            "difficulty": context.get("difficulty", profile.get("knowledge_level", "medium")),
            "cognitive_style": profile.get("cognitive_style", {}).get("primary", "visual") if isinstance(profile.get("cognitive_style"), dict) else profile.get("cognitive_style", "visual"),
            "profile": profile,
            "constraints": params,
            "student_id": context.get("student_id"),
        }

        # 对于 path_planner 特殊处理
        if agent_id == "path_planner":
            agent_context = {
                "task": task,
                "student_id": context.get("student_id"),
                "profile": profile,
                "target": context.get("topic", context.get("target", "未指定")),
                "current_path": context.get("current_path", {}),
                "feedback": context.get("feedback", ""),
            }

        # 对于 tutor 特殊处理
        if agent_id == "tutor":
            agent_context = {
                "task": "answer_question",
                "session_id": f"{context.get('student_id', 'anon')}_cd",
                "question": params.get("question", context.get("user_request", "")),
                "profile": profile,
            }

        return await agent.process(agent_context)

    async def _assemble_output(
        self,
        results: Dict[str, Any],
        requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """汇总输出"""
        # 检查是否有失败的任务
        failed_tasks = [
            k for k, v in results.items()
            if isinstance(v, dict) and v.get("status") == "failed"
        ]

        if failed_tasks:
            return {
                "status": "partial_failure",
                "message": f"Some tasks failed: {failed_tasks}",
                "results": results
            }

        # 组装最终输出
        return {
            "status": "success",
            "content_type": requirements["request_type"],
            "assembled_at": datetime.now().isoformat(),
            "components": list(results.keys()),
            "summary": self._generate_summary(results)
        }

    def _generate_summary(self, results: Dict[str, Any]) -> str:
        """生成结果摘要"""
        success_count = sum(
            1 for v in results.values()
            if isinstance(v, dict) and v.get("status") == "success"
        )
        return f"Successfully completed {success_count}/{len(results)} sub-tasks"
