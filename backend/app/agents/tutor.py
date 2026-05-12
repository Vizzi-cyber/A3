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

    MAX_SESSIONS = 100  # 最大内存会话数

    def __init__(self, llm: Optional[BaseLLM] = None):
        super().__init__(
            agent_id="tutor",
            agent_name="辅导助手",
            description="通过苏格拉底式提问引导学生独立思考"
        )
        self.llm = llm or LLMFactory.get_default_llm()
        self.session_histories: Dict[str, List[Dict[str, Any]]] = {}
        self._session_last_access: Dict[str, float] = {}  # 记录会话最后访问时间
        self._student_summaries: Dict[str, str] = {}  # 跨session记忆，keyed by student_id

    def _detect_learning_state(self, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        分析最近对话，检测学习状态
        返回: {state: "confident"|"confused"|"frustrated"|"neutral", hint: str}
        """
        if len(history) < 2:
            return {"state": "neutral", "hint": ""}

        recent = history[-6:]  # 最近3轮对话
        user_msgs = [m for m in recent if m.get("role") == "user"]
        if not user_msgs:
            return {"state": "neutral", "hint": ""}

        # 检测挫败感：短回答、否定词
        frustration_words = ["不会", "不懂", "太难", "放弃", "算了", "不知道", "很难", "搞不懂"]
        short_count = sum(1 for m in user_msgs if len(str(m.get("content", ""))) < 10)
        frustration_count = sum(
            1 for m in user_msgs
            if any(w in str(m.get("content", "")) for w in frustration_words)
        )

        if frustration_count >= 2 or (short_count >= 2 and frustration_count >= 1):
            return {
                "state": "frustrated",
                "hint": "学生似乎感到挫败，用更鼓励的语气，给出更简单的解释，避免过多追问。",
            }

        # 检测困惑：回退话题、重复提问
        confusion_words = ["还是", "可是", "但是", "为什么", "不太", "没明白"]
        confusion_count = sum(
            1 for m in user_msgs
            if any(w in str(m.get("content", "")) for w in confusion_words)
        )
        if confusion_count >= 2:
            return {
                "state": "confused",
                "hint": "学生可能感到困惑，尝试换一种解释方式，用更具体的例子。",
            }

        # 检测自信：长回答、主动思考
        long_count = sum(1 for m in user_msgs if len(str(m.get("content", ""))) > 50)
        if long_count >= 2:
            return {
                "state": "confident",
                "hint": "学生思考积极，可以适当增加难度，引导更深入的探讨。",
            }

        return {"state": "neutral", "hint": ""}

    def _evict_old_sessions(self):
        """当会话数超过上限时，淘汰最久未访问的会话"""
        if len(self.session_histories) <= self.MAX_SESSIONS:
            return
        # 按最后访问时间排序，淘汰最旧的
        sorted_sessions = sorted(
            self._session_last_access.items(),
            key=lambda x: x[1],
        )
        to_remove = len(sorted_sessions) - self.MAX_SESSIONS + 1
        for session_id, _ in sorted_sessions[:to_remove]:
            self.session_histories.pop(session_id, None)
            self._session_last_access.pop(session_id, None)

    def get_system_prompt(self) -> str:
        return (
            "你是一位耐心的学习辅导助手，笃信苏格拉底式教学法。"
            "当学生提问时，你不应直接给出完整答案，而是通过循序渐进的提问，"
            "引导学生发现自己的知识盲区，并自主推导出结论。"
            "你的语气应温和、鼓励，避免批评。"
            "重要：不要输出思考过程、分析步骤或'让我想想'之类的内心独白，直接给出对学生的回复内容。"
            "每次回复要有所不同，不要重复相同的引导问题或句式。"
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

        # 更新会话访问时间
        from time import time as _time
        self._session_last_access[session_id] = _time()

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
            # 维护会话历史（带 LRU 淘汰）
            self._evict_old_sessions()
            history = self.session_histories.setdefault(session_id, [])
            if task == "answer_question":
                result = await self._socratic_answer(question, history, context.get("profile", {}), llm)
            elif task == "hint":
                result = await self._give_hint(question, history, llm)
            elif task == "encourage":
                result = await self._encourage(history, llm)
            elif task == "explain_code":
                result = await self._explain_code(question, context.get("language", "C"), llm)
            elif task == "explain_error":
                result = await self._explain_error(question, context.get("language", "C"), llm)
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

        # 学习状态检测
        learning_state = self._detect_learning_state(history)

        if isinstance(question, list):
            # 图文模式（OpenAI vision 格式）
            prefix_text = (
                f"学生薄弱领域：{weak_areas}\n"
                f"认知风格：{style}\n"
                f"学习状态：{learning_state['state']}\n"
                f"{'教学建议：' + learning_state['hint'] if learning_state['hint'] else ''}\n"
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
                f"学习状态：{learning_state['state']}\n"
                f"{'教学建议：' + learning_state['hint'] if learning_state['hint'] else ''}\n"
                "请用苏格拉底式提问回应：不直接给答案，而是通过 2-3 个引导性问题，"
                "帮助学生自己思考出答案。最后可以给学生一句简短鼓励。"
            )
            prompt = SafetyGuard.sanitize_prompt(prompt)
            messages = [
                {"role": "system", "content": self.get_system_prompt()},
                *history,
                {"role": "user", "content": prompt},
            ]

        answer = await llm.ainvoke(messages, temperature=0.8, max_tokens=1024)
        # 更新历史
        user_content = prefixed_content if isinstance(question, list) else prompt
        history.append({"role": "user", "content": user_content})
        history.append({"role": "assistant", "content": answer})
        # 限制历史长度
        if len(history) > 20:
            history[:] = history[-20:]
        return {
            "status": "success",
            "answer": answer,
            "history_length": len(history),
            "learning_state": learning_state,
        }

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

    async def _explain_code(self, code: str, language: str = "C", llm: Optional[BaseLLM] = None) -> Dict[str, Any]:
        llm = llm or self.llm
        prompt = (
            f"以下是学生编写的一段 {language} 代码，请逐行解释它的功能和逻辑：\n\n"
            f"```{language.lower()}\n{code}\n```\n\n"
            "要求：\n"
            "1. 先用一句话概括这段代码做了什么\n"
            "2. 逐行或逐块解释关键逻辑\n"
            "3. 指出可能的改进点或常见错误（如果有）\n"
            "4. 语言简洁，适合初学者理解"
        )
        prompt = SafetyGuard.sanitize_prompt(prompt)
        messages = [
            {"role": "system", "content": "你是一位专业的编程教师，善于用清晰简洁的语言解释代码。"},
            {"role": "user", "content": prompt},
        ]
        answer = await llm.ainvoke(messages, temperature=0.4, max_tokens=1500)
        return {"status": "success", "answer": answer, "type": "code_explanation"}

    async def _explain_error(self, error_output: str, language: str = "C", llm: Optional[BaseLLM] = None) -> Dict[str, Any]:
        llm = llm or self.llm
        prompt = (
            f"学生运行了一段 {language} 代码，遇到了以下错误：\n\n"
            f"```\n{error_output}\n```\n\n"
            "请：\n"
            "1. 解释这个错误是什么意思\n"
            "2. 分析最可能的原因\n"
            "3. 给出修复建议\n"
            "4. 用初学者能理解的语言"
        )
        prompt = SafetyGuard.sanitize_prompt(prompt)
        messages = [
            {"role": "system", "content": "你是一位专业的编程教师，善于帮助初学者理解和修复代码错误。"},
            {"role": "user", "content": prompt},
        ]
        answer = await llm.ainvoke(messages, temperature=0.4, max_tokens=1000)
        return {"status": "success", "answer": answer, "type": "error_explanation"}

    def clear_session(self, session_id: str):
        """清空指定会话历史"""
        self.session_histories.pop(session_id, None)
        self._session_last_access.pop(session_id, None)
