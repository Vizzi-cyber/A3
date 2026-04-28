"""
LangGraph 状态图构建器
"""
from typing import Any, Dict

from langgraph.graph import StateGraph, END

from .state import AgentState
from .nodes import (
    supervisor_node,
    profiler_node,
    resource_generator_node,
    path_planner_node,
    tutor_node,
    assembler_node,
    router_edge,
)


def build_learning_graph() -> StateGraph:
    """构建并返回学习系统的多智能体状态图"""
    workflow = StateGraph(AgentState)

    # 注册节点
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("profiler", profiler_node)
    workflow.add_node("resource_generator", resource_generator_node)
    workflow.add_node("path_planner", path_planner_node)
    workflow.add_node("tutor", tutor_node)
    workflow.add_node("assembler", assembler_node)

    # 设置入口
    workflow.set_entry_point("supervisor")

    # Supervisor 的条件路由
    workflow.add_conditional_edges(
        "supervisor",
        router_edge,
        {
            "profiler": "profiler",
            "resource_generator": "resource_generator",
            "path_planner": "path_planner",
            "tutor": "tutor",
            "finish": "assembler",
        },
    )

    # 各子智能体执行完后回到 supervisor
    for node_name in ["profiler", "resource_generator", "path_planner", "tutor"]:
        workflow.add_edge(node_name, "supervisor")

    # assembler 结束后流程终止
    workflow.add_edge("assembler", END)

    return workflow.compile()


class LearningGraphRunner:
    """面向业务层的图执行封装"""

    def __init__(self):
        self.graph = build_learning_graph()

    async def run(
        self,
        student_id: str,
        task_type: str,
        context: Dict[str, Any],
        profile: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        执行一次多智能体工作流

        Args:
            student_id: 学生ID
            task_type: resource_generation / path_planning / tutoring / profile_update
            context: 任务上下文（topic, difficulty, user_request 等）
            profile: 当前学生画像（可选）
        """
        initial_state: AgentState = {
            "messages": [],
            "student_id": student_id,
            "task_type": task_type,
            "context": context,
            "profile": profile or {},
            "next_agent": "supervisor",
            "results": {},
            "final_output": None,
            "iteration": 0,
            "error": None,
        }
        final_state = await self.graph.ainvoke(initial_state)
        return final_state.get("final_output", {"status": "error", "message": "No final output produced"})


# 不再在模块导入时创建全局单例，改由 lifespan 延迟初始化，避免阻塞启动
