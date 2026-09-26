"""
LangGraph 共享状态定义
"""
from dataclasses import dataclass, field
from typing import Annotated, Any, Dict, List, Optional, Sequence
from typing_extensions import TypedDict

from langchain_core.messages import BaseMessage
import operator


@dataclass
class AgentStep:
    """Agent 执行步骤定义"""
    agent_name: str
    display_name: str = ""
    depends_on: List[str] = field(default_factory=list)
    parallel_group: Optional[str] = None  # 同一组的步骤可并行执行


class AgentState(TypedDict):
    """多智能体系统的共享状态"""

    # 对话/上下文消息
    messages: Annotated[Sequence[BaseMessage], operator.add]

    # 学生与任务信息
    student_id: str
    task_type: str  # resource_generation / path_planning / tutoring / profile_update
    context: Dict[str, Any]

    # 画像数据（会被多个节点读写）
    profile: Dict[str, Any]

    # 调度字段
    next_agent: str  # supervisor 决定下一个执行谁：profiler / resource_generator / path_planner / tutor / finish / __parallel__
    _parallel_agents: Optional[List[str]]  # 并行调度时，需要并行执行的 agent 名称列表

    # 各节点产出
    results: Annotated[Dict[str, Any], operator.or_]

    # 最终结果
    final_output: Optional[Dict[str, Any]]

    # 迭代与错误
    iteration: int
    error: Optional[str]
