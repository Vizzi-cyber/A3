"""
辅导助手智能体
采用苏格拉底式问答，引导学生自主思考，不直接给答案
"""
from typing import Any, Dict, List, Optional, Union

from .base import BaseAgent
from ..services.llm_factory import BaseLLM, LLMFactory
from ..core.safety import SafetyGuard


class TutorAgent(BaseAgent):
    """辅导助手智能体"""

    def __init__(self, llm: Optional[BaseLLM] = None):
        super().__init__(
            agent_id="tutor",
            agent_name="辅导助手",
            description="通过苏格拉底式提问引导学生独立思考"
        )
        self.llm = llm or LLMFactory.get_default_llm()
        self.session_histories: Dict[str, List[Dict[str, Any]]] = {}

    def get_system_prompt(self) -> str:
        return (
            "你是一位耐心的学习辅导助手，笃信苏格拉底式教学法。"
            "当学生提问时，你不应直接给出完整答案，而是通过循序渐进的提问，"
            "引导学生发现自己的知识盲区，并自主推导出结论。"
            "你的语气应温和、鼓励，避免批评。"
            "重要：不要输出思考过程、分析步骤或'让我想想'之类的内心独白，直接给出对学生的回复内容。"
        )

    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        context:
        {
            "task": "answer_question" | "hint" | "encourage",
            "session_id": "sess_xxx",
            "question": "为什么递归要有终止条件？",
            "profile": {...},
            "history": [...],
            "llm_provider": "bigmodel" | "deepseek" | "openai" | "spark" | None
        }
        """
        self.status = "running"
        task = context.get("task", "answer_question")
        question = context.get("question", "")
        session_id = context.get("session_id", "default")
        provider = context.get("llm_provider")

        # 动态切换 LLM 提供商
        llm = self.llm
        if provider:
            try:
                llm = LLMFactory.get_llm(provider)
            except Exception as e:
                self.logger.warning(f"Failed to switch LLM provider '{provider}': {e}, using default")

        safety = SafetyGuard.check_input(question)
        if not safety["safe"]:
            return {"status": "blocked", "reason": safety["message"]}

        try:
            # 维护会话历史
            history = self.session_histories.setdefault(session_id, [])
            if task == "answer_question":
                result = await self._socratic_answer(question, history, context.get("profile", {}), llm)
            elif task == "hint":
                result = await self._give_hint(question, history, llm)
            elif task == "encourage":
                result = await self._encourage(history, llm)
            else:
                result = {"status": "failed", "error": f"Unknown task: {task}"}

            # 输出安全
            if result.get("status") == "success" and isinstance(result.get("answer"), str):
                out_safe = SafetyGuard.check_output(result["answer"])
                if not out_safe["safe"]:
                    result["status"] = "blocked"
                    result["answer"] = "[内容已拦截] 回答包含不适宜内容，请换种方式提问。"

            self.status = "completed"
            return result
        except Exception as e:
            self.status = "failed"
            self.logger.error(f"TutorAgent error: {e}")
            return {"status": "failed", "error": str(e)}

    async def _socratic_answer(self, question: Union[str, List[Dict[str, Any]]], history: List[Dict[str, Any]], profile: Dict[str, Any], llm: Optional[BaseLLM] = None) -> Dict[str, Any]:
        weak_areas = profile.get("weak_areas", [])
        style = profile.get("cognitive_style", {}).get("primary", "visual")
        llm = llm or self.llm

        if isinstance(question, list):
            # 图文模式（OpenAI vision 格式）
            prefix_text = (
                f"学生薄弱领域：{weak_areas}\n"
                f"认知风格：{style}\n"
                "请用苏格拉底式提问回应：不直接给答案，而是通过 2-3 个引导性问题，"
                "帮助学生自己思考出答案。最后可以给学生一句简短鼓励。"
            )
            prefixed_content: List[Dict[str, Any]] = [{"type": "text", "text": prefix_text}] + question
            messages = [
                {"role": "system", "content": self.get_system_prompt()},
                *history,
                {"role": "user", "content": prefixed_content},
            ]
        else:
            prompt = (
                f"学生提问：{question}\n"
                f"学生薄弱领域：{weak_areas}\n"
                f"认知风格：{style}\n"
                "请用苏格拉底式提问回应：不直接给答案，而是通过 2-3 个引导性问题，"
                "帮助学生自己思考出答案。最后可以给学生一句简短鼓励。"
            )
            prompt = SafetyGuard.sanitize_prompt(prompt)
            messages = [
                {"role": "system", "content": self.get_system_prompt()},
                *history,
                {"role": "user", "content": prompt},
            ]

        answer = await llm.ainvoke(messages, temperature=0.6, max_tokens=1024)
        # 更新历史
        history.append({"role": "user", "content": question})
        history.append({"role": "assistant", "content": answer})
        # 限制历史长度
        if len(history) > 20:
            history[:] = history[-20:]
        return {"status": "success", "answer": answer, "history_length": len(history)}

    async def _give_hint(self, question: str, history: List[Dict[str, Any]], llm: Optional[BaseLLM] = None) -> Dict[str, Any]:
        llm = llm or self.llm
        prompt = f"学生卡在以下问题上：{question}\n请给出一个不超过两句话的微妙提示，不要直接揭示答案。"
        prompt = SafetyGuard.sanitize_prompt(prompt)
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            *history,
            {"role": "user", "content": prompt},
        ]
        hint = await llm.ainvoke(messages, temperature=0.5)
        return {"status": "success", "answer": hint, "type": "hint"}

    async def _encourage(self, history: List[Dict[str, Any]], llm: Optional[BaseLLM] = None) -> Dict[str, Any]:
        llm = llm or self.llm
        prompt = "根据对话历史，给学生一句真诚的鼓励，肯定他的思考过程。控制在30字以内。"
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            *history,
            {"role": "user", "content": prompt},
        ]
        text = await llm.ainvoke(messages, temperature=0.7)
        return {"status": "success", "answer": text, "type": "encouragement"}

    def clear_session(self, session_id: str):
        """清空指定会话历史"""
        self.session_histories.pop(session_id, None)
