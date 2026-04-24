"""
画像师智能体
负责分析学生行为、测试、交互数据，生成和更新六维画像
"""
from typing import Any, Dict, List, Optional

from .base import BaseAgent
from ..services.llm_factory import BaseLLM, LLMFactory
from ..core.safety import SafetyGuard, HallucinationGuard


class ProfilerAgent(BaseAgent):
    """画像师智能体"""

    def __init__(self, llm: Optional[BaseLLM] = None):
        super().__init__(
            agent_id="profiler",
            agent_name="画像师",
            description="分析学生数据，生成和更新六维学生画像"
        )
        self.llm = llm or LLMFactory.get_default_llm()

    def get_system_prompt(self) -> str:
        return (
            "你是一位专业的教育数据分析师，擅长从学生的学习行为、测试表现和交互记录中"
            "提取特征，构建精准的学生画像。"
            "重要：不要输出思考过程、分析步骤或'让我想想'之类的内心独白，直接输出最终分析结果。"
        )

    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        context 示例:
        {
            "action": "update" | "analyze" | "initialize",
            "student_id": "s123",
            "inputs": ["最近测试只对了3道递归题", "喜欢看视频学习"],
            "current_profile": {...}  # 可选
        }
        """
        self.status = "running"
        action = context.get("action", "analyze")
        inputs = context.get("inputs", [])
        current_profile = context.get("current_profile", {})

        try:
            # 输入安全检查
            for text in inputs:
                if isinstance(text, str):
                    check = SafetyGuard.check_input(text)
                    if not check["safe"]:
                        return {"status": "blocked", "reason": check["message"], "hits": check["hits"]}

            if action == "initialize":
                result = await self._initialize_profile(context)
            elif action == "update":
                result = await self._update_profile(inputs, current_profile)
            else:
                result = await self._analyze_profile(inputs, current_profile)

            # 输出校验
            if isinstance(result.get("profile"), dict):
                schema_check = HallucinationGuard.verify_json_schema(
                    result["profile"],
                    ["student_id", "cognitive_style", "knowledge_base", "weak_areas", "learning_tempo"]
                )
                if not schema_check["valid"]:
                    result["warning"] = schema_check["message"]

            self.status = "completed"
            return result
        except Exception as e:
            self.status = "failed"
            self.logger.error(f"ProfilerAgent error: {e}")
            return {"status": "failed", "error": str(e)}

    async def _initialize_profile(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """初始化画像"""
        prompt = (
            "请根据以下学生信息，生成一个结构化的六维学生画像。\n"
            "六维：知识基础、认知风格、易错点、兴趣动机、学习节奏、实践偏好。\n"
            "请严格返回 JSON 格式，不要包含 Markdown 代码块标记。\n"
            f"输入信息：{context}\n"
            "返回格式：{\"profile\": {\"student_id\": \"...\", \"knowledge_base\": {...}, ...}}"
        )
        prompt = SafetyGuard.sanitize_prompt(prompt)
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": prompt},
        ]
        data = await self.llm.generate_json(messages, temperature=0.3)
        if data.get("status") == "error":
            return {"status": "partial_failure", "llm_output": data, "profile": self._default_profile(context.get("student_id", ""))}
        profile = data.get("profile", data)
        return {"status": "success", "profile": profile}

    async def _update_profile(self, inputs: List[str], current_profile: Dict[str, Any]) -> Dict[str, Any]:
        """增量更新画像"""
        prompt = (
            "请根据以下新的学习行为和反馈，更新现有学生画像。\n"
            "仅对明显变化的维度进行更新，保持未变化维度的原有数据。\n"
            "请严格返回 JSON 格式的完整更新后画像。\n\n"
            f"当前画像：{current_profile}\n\n"
            f"新输入：{inputs}\n\n"
            "返回格式：{\"profile\": {完整画像JSON}}"
        )
        prompt = SafetyGuard.sanitize_prompt(prompt)
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": prompt},
        ]
        data = await self.llm.generate_json(messages, temperature=0.3)
        profile = data.get("profile", data) if data.get("status") != "error" else current_profile
        return {"status": "success", "profile": profile, "llm_output": data if data.get("status") == "error" else None}

    async def _analyze_profile(self, inputs: List[str], current_profile: Dict[str, Any]) -> Dict[str, Any]:
        """分析画像并给出教育建议"""
        prompt = (
            "请基于以下学生画像和最新输入，分析学生的当前状态，并给出3条针对性的教学建议。\n"
            f"画像：{current_profile}\n"
            f"输入：{inputs}\n"
            "返回格式：{\"analysis\": \"...\", \"suggestions\": [\"...\", \"...\", \"...\"]}"
        )
        prompt = SafetyGuard.sanitize_prompt(prompt)
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": prompt},
        ]
        data = await self.llm.generate_json(messages, temperature=0.4)
        return {"status": "success", "analysis": data}

    def _default_profile(self, student_id: str) -> Dict[str, Any]:
        return {
            "student_id": student_id,
            "knowledge_base": {},
            "cognitive_style": {"primary": "visual", "scores": {}},
            "weak_areas": [],
            "error_patterns": [],
            "learning_goals": [],
            "interest_areas": [],
            "learning_tempo": {"study_speed": "moderate", "optimal_session_duration": 45},
            "practical_preferences": {"coding_proficiency": {}, "preferred_practice_types": []},
        }
