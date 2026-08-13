"""
智能体基类定义
所有智能体继承此类，实现统一的接口规范
"""
import json
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional
from datetime import datetime, timezone
from enum import Enum

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
        """创建消息（供上层调度器转发）"""
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

    def apply_guards(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """输出质量守卫（防幻觉第⑤⑥道防线，规则校验，零 LLM 成本）

        - 结构校验：复用 agent 内部已产生的 _schema_check 结果
        - 引用核查：教育内容输出鼓励标注来源（verify_citations）
        - 结果合并：combine_guard_results 汇总到 result["_guards"]
        """
        from ..core.safety import HallucinationGuard, combine_guard_results

        # 守卫仅对成功输出生效（错误结果无需质量校验）
        if not isinstance(result, dict) or result.get("status") != "success":
            return result

        guard_results = []
        if "_schema_check" in result and isinstance(result["_schema_check"], dict):
            guard_results.append(result["_schema_check"])

        text_fields = [
            str(result.get(k, ""))
            for k in ("message", "answer", "analysis", "explanation", "content")
            if result.get(k)
        ]
        if text_fields:
            text = "\n".join(text_fields)[:2000]
            guard_results.append(HallucinationGuard.verify_citations(text))

        if guard_results:
            result["_guards"] = combine_guard_results(*guard_results)
        return result

    async def self_correct_output(self, context: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        """LLM 事实核查自我修正（防幻觉第⑥道防线，仅低质量结果触发一次）"""
        from ..core.safety import HallucinationGuard

        if not isinstance(result, dict) or not hasattr(self, "llm") or not self.llm:
            return result

        text_fields = {
            k: str(result.get(k, ""))
            for k in ("content", "message", "answer", "analysis", "explanation")
            if result.get(k) and len(str(result.get(k))) > 80
        }
        if not text_fields:
            return result
        field = max(text_fields, key=lambda k: len(text_fields[k]))
        original_text = text_fields[field]

        try:
            self.logger.info(f"Applying self-correction to field '{field}'")
            corrected = await HallucinationGuard.self_correct(
                self.llm, "", original_text,
            )
            if corrected and corrected.strip() and corrected.strip() != original_text.strip():
                result[field] = corrected
                result["_self_corrected"] = True
        except Exception as e:
            self.logger.warning(f"Self-correction failed: {e}")
        return result

    async def cached_process(
        self,
        context: Dict[str, Any],
        cache_key_fn: Optional[Callable[[Dict[str, Any]], str]] = None,
    ) -> Dict[str, Any]:
        """
        带缓存的 process 调用。
        cache_key_fn: 自定义缓存 key 计算函数，默认用 context 的 JSON hash。
        只缓存 status=="success" 的结果。
        """
        from ..core.cache import prompt_cache

        if cache_key_fn:
            cache_key = cache_key_fn(context)
        else:
            cache_key = prompt_cache.hash_prompt(
                {"context": context},
                extra_salt=self.agent_id,
            )

        cached = await prompt_cache.get(cache_key)
        if cached is not None:
            self.logger.info(f"Cache hit, key={cache_key[:8]}")
            return cached

        result = await self.process(context)

        if isinstance(result, dict) and result.get("status") == "success":
            result = self.apply_guards(result)
            await prompt_cache.set(cache_key, result)

        return result

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
        quality_threshold: float = 0.8,
        timeout_per_iteration: float = 60.0,
        enable_llm_evaluation: bool = True,
    ) -> Dict[str, Any]:
        """
        带反思的执行流程：执行-评估-修正循环。
        enable_llm_evaluation=True 时使用 LLM 评估质量，否则用规则评估。
        """
        import asyncio
        best_result = None
        best_score = 0.0
        iteration = 0

        for iteration in range(max_iterations):
            self.logger.info(f"Reflection iteration {iteration + 1}/{max_iterations}")

            try:
                result = await asyncio.wait_for(self.process(context), timeout=timeout_per_iteration)
            except asyncio.TimeoutError:
                self.logger.warning(f"Process timeout at iteration {iteration + 1}")
                result = {"status": "error", "message": "Processing timeout"}
            except Exception as e:
                self.logger.warning(f"Process error at iteration {iteration + 1}: {e}")
                result = {"status": "error", "message": str(e)}

            if enable_llm_evaluation and hasattr(self, "llm") and self.llm:
                score = await self._self_evaluate(result)
            else:
                score = self._rule_based_evaluate(result)

            result["_evaluation_score"] = score
            result["_iteration"] = iteration + 1

            if score > best_score:
                best_score = score
                best_result = result

            if score >= quality_threshold:
                self.logger.info(f"Quality threshold reached: {score}")
                break

            context["_previous_result"] = result
            context["_feedback"] = await self._generate_feedback(result, enable_llm_evaluation)

        if best_result is None:
            best_result = {"status": "error", "message": "No iterations executed"}
        best_result["_total_iterations"] = iteration + 1

        # 防幻觉挂接：规则守卫（引用核查/结果合并）+ 低质量自我纠错
        best_result = self.apply_guards(best_result)
        if best_score < quality_threshold and enable_llm_evaluation:
            best_result = await self.self_correct_output(context, best_result)
        return best_result

    def _rule_based_evaluate(self, result: Dict[str, Any]) -> float:
        """基于规则的质量评估（作为 fallback）"""
        score = 0.0
        if "content" in result or "output" in result:
            score += 0.5
        if "confidence" in result:
            score += 0.3
        if result.get("status") == "success":
            score += 0.2
        return score

    async def _self_evaluate(self, result: Dict[str, Any]) -> float:
        """用 LLM 评估结果质量。子类可覆盖为专用评估逻辑。"""
        if not hasattr(self, "llm") or not self.llm:
            return self._rule_based_evaluate(result)

        result_text = json.dumps(result, ensure_ascii=False, default=str)[:2000]
        messages = [
            {"role": "system", "content": (
                "你是一个教育内容质量评估专家。请评估以下智能体输出的质量，"
                "从准确性、完整性、可用性三个维度打分（0-1之间）。\n"
                '返回 JSON：{"score": 0.0-1.0, "reason": "简要说明"}'
            )},
            {"role": "user", "content": f"智能体输出：\n{result_text}"},
        ]
        try:
            data = await self.llm.generate_json(messages, temperature=0.1, max_tokens=200)
            return float(data.get("score", 0.5))
        except Exception as e:
            self.logger.warning(f"LLM evaluation failed, falling back to rule-based: {e}")
            return self._rule_based_evaluate(result)

    async def _generate_feedback(self, result: Dict[str, Any], use_llm: bool = True) -> str:
        """生成改进反馈。use_llm=True 时用 LLM 生成，否则用规则。"""
        if not use_llm or not hasattr(self, "llm") or not self.llm:
            score = result.get("_evaluation_score", 0)
            if score < 0.5:
                return "需要大幅改进，请重新思考核心逻辑"
            elif score < 0.8:
                return "基本可用，但需要补充细节和完善"
            else:
                return "质量良好，可进行微调优化"

        result_text = json.dumps(result, ensure_ascii=False, default=str)[:2000]
        messages = [
            {"role": "system", "content": "你是教育内容质量审核专家。根据评估结果给出简洁的改进建议，不超过两句话。"},
            {"role": "user", "content": f"评估结果：\n{result_text}"},
        ]
        try:
            return await self.llm.ainvoke(messages, temperature=0.3, max_tokens=200)
        except Exception:
            return "请重新检查输出质量"
