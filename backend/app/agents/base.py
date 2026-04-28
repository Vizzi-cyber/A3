"""
智能体基类定义
所有智能体继承此类，实现统一的接口规范
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime, timezone
from enum import Enum
import json

class AgentStatus(Enum):
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class AgentMessage:
    """智能体间消息传递格式"""
    def __init__(
        self,
        from_agent: str,
        to_agent: str,
        message_type: str,  # task_assignment / query / response / notification
        payload: Dict[str, Any],
        priority: str = "normal",  # low / normal / high / urgent
        requires_response: bool = True
    ):
        self.message_id = f"msg_{datetime.now(timezone.utc).timestamp()}"
        self.timestamp = datetime.now(timezone.utc).isoformat()
        self.from_agent = from_agent
        self.to_agent = to_agent
        self.message_type = message_type
        self.payload = payload
        self.priority = priority
        self.requires_response = requires_response

    def to_dict(self) -> Dict:
        return {
            "message_id": self.message_id,
            "timestamp": self.timestamp,
            "from_agent": self.from_agent,
            "to_agent": self.to_agent,
            "message_type": self.message_type,
            "payload": self.payload,
            "priority": self.priority,
            "requires_response": self.requires_response
        }

class BaseAgent(ABC):
    """
    智能体基类
    所有具体智能体必须继承此类并实现抽象方法
    """

    def __init__(self, agent_id: str, agent_name: str, description: str = ""):
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.description = description
        self.status = AgentStatus.IDLE
        self.message_queue: List[AgentMessage] = []
        self.tools: Dict[str, Callable] = {}
        self.memory: Dict[str, Any] = {}  # 智能体记忆
        self.logger = self._setup_logger()

    def _setup_logger(self):
        """设置日志记录器"""
        import logging
        logger = logging.getLogger(self.agent_id)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                f'[%(asctime)s] [{self.agent_id}] %(levelname)s: %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    def register_tool(self, tool_name: str, tool_func: Callable):
        """注册工具函数"""
        self.tools[tool_name] = tool_func
        self.logger.info(f"Tool '{tool_name}' registered")

    def use_tool(self, tool_name: str, **kwargs) -> Any:
        """使用工具"""
        if tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' not found")
        return self.tools[tool_name](**kwargs)

    def receive_message(self, message: AgentMessage):
        """接收消息"""
        self.message_queue.append(message)
        self.logger.info(f"Received message from {message.from_agent}: {message.message_type}")

    def send_message(
        self,
        to_agent: str,
        message_type: str,
        payload: Dict[str, Any],
        priority: str = "normal",
        requires_response: bool = True
    ) -> AgentMessage:
        """发送消息"""
        message = AgentMessage(
            from_agent=self.agent_id,
            to_agent=to_agent,
            message_type=message_type,
            payload=payload,
            priority=priority,
            requires_response=requires_response
        )
        self.logger.info(f"Sending message to {to_agent}: {message_type}")
        return message

    @abstractmethod
    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        智能体核心处理逻辑
        子类必须实现此方法
        """
        pass

    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        获取系统提示词
        子类必须实现此方法
        """
        pass

    def update_memory(self, key: str, value: Any):
        """更新记忆"""
        self.memory[key] = value

    def get_memory(self, key: str, default: Any = None) -> Any:
        """获取记忆"""
        return self.memory.get(key, default)

    def clear_memory(self):
        """清空记忆"""
        self.memory.clear()

    def get_status(self) -> Dict[str, Any]:
        """获取智能体状态"""
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "status": self.status.value,
            "queue_size": len(self.message_queue),
            "memory_keys": list(self.memory.keys()),
            "registered_tools": list(self.tools.keys())
        }

    async def run_with_reflection(
        self,
        context: Dict[str, Any],
        max_iterations: int = 3,
        quality_threshold: float = 0.8
    ) -> Dict[str, Any]:
        """
        带反思的执行流程
        执行-评估-修正的循环
        """
        best_result = None
        best_score = 0.0

        for iteration in range(max_iterations):
            self.logger.info(f"Reflection iteration {iteration + 1}/{max_iterations}")

            # 执行
            result = await self.process(context)

            # 自我评估
            score = await self._self_evaluate(result)
            result["_evaluation_score"] = score
            result["_iteration"] = iteration + 1

            if score > best_score:
                best_score = score
                best_result = result

            # 如果达到质量阈值，提前退出
            if score >= quality_threshold:
                self.logger.info(f"Quality threshold reached: {score}")
                break

            # 准备下一轮迭代的修正
            context["_previous_result"] = result
            context["_feedback"] = await self._generate_feedback(result)

        best_result["_total_iterations"] = iteration + 1
        return best_result

    async def _self_evaluate(self, result: Dict[str, Any]) -> float:
        """
        自我评估生成结果的质量
        子类可重写此方法
        """
        # 默认实现：检查必要字段是否存在
        score = 0.0
        if "content" in result or "output" in result:
            score += 0.5
        if "confidence" in result:
            score += 0.3
        if result.get("status") == "success":
            score += 0.2
        return score

    async def _generate_feedback(self, result: Dict[str, Any]) -> str:
        """
        根据评估结果生成改进反馈
        子类可重写此方法
        """
        score = result.get("_evaluation_score", 0)
        if score < 0.5:
            return "需要大幅改进，请重新思考核心逻辑"
        elif score < 0.8:
            return "基本可用，但需要补充细节和完善"
        else:
            return "质量良好，可进行微调优化"
