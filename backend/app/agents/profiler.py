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
        schema_example = {
            "knowledge_base": {
                "overall_score": 0.75,
                "academic_level": "大二",
                "subject_strengths": ["高数"],
                "subject_weaknesses": ["数据结构"],
            },
            "cognitive_style": {
                "primary": "visual",
                "scores": {"visual": 0.8, "auditory": 0.4, "reading": 0.6, "kinesthetic": 0.7},
            },
            "weak_areas": ["指针", "内存管理"],
            "error_patterns": [{"type": "概念混淆", "description": "指针与地址混淆"}],
            "learning_goals": [{"topic": "系统学习C语言", "deadline": "3个月", "completed": False}],
            "interest_areas": [{"area": "嵌入式开发", "level": 0.9}],
            "learning_tempo": {
                "study_speed": "moderate",
                "optimal_session_duration": 45,
                "weekly_study_capacity": 10,
                "focus_score": 0.78,
            },
            "practical_preferences": {
                "coding_proficiency": {"C": 0.4, "Python": 0.7},
                "preferred_practice_types": ["实战项目", "算法题"],
                "overall_score": 0.65,
            },
        }
        prompt = (
            "你是一位教育数据分析师。请根据学生的新输入，更新六维学生画像。\n"
            "必须返回完整的六维画像 JSON，不允许省略任何维度。如果某个维度没有新变化，保持原有数据或给出合理默认值。\n\n"
            "六维结构说明：\n"
            "1. knowledge_base - 知识基础（overall_score: 0-1, academic_level, subject_strengths, subject_weaknesses）\n"
            "2. cognitive_style - 认知风格（primary: visual/auditory/reading/kinesthetic, scores: 各维度0-1）\n"
            "3. weak_areas - 薄弱知识点（字符串列表）\n"
            "4. error_patterns - 错误模式（对象列表，含 type/description）\n"
            "5. learning_goals - 学习目标（对象列表，含 topic/deadline/completed）\n"
            "6. interest_areas - 兴趣领域（对象列表，含 area/level）\n"
            "7. learning_tempo - 学习节奏（study_speed, optimal_session_duration, weekly_study_capacity, focus_score: 0-1）\n"
            "8. practical_preferences - 实践偏好（coding_proficiency: 语言->0-1, preferred_practice_types, overall_score: 0-1）\n\n"
            f"当前画像：{current_profile}\n\n"
            f"新输入：{inputs}\n\n"
            f"Schema 示例：{schema_example}\n\n"
            "请严格返回 JSON：{\"profile\": {完整画像}}"
        )
        prompt = SafetyGuard.sanitize_prompt(prompt)
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": prompt},
        ]
        data = await self.llm.generate_json(messages, temperature=0.3)
        profile = data.get("profile", data) if data.get("status") != "error" else current_profile
        # 如果 LLM 返回了不完整画像，做补齐
        profile = self._ensure_complete_profile(profile, current_profile)
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
            "knowledge_base": {"overall_score": 0.5},
            "cognitive_style": {
                "primary": "visual",
                "scores": {"visual": 0.6, "auditory": 0.4, "reading": 0.5, "kinesthetic": 0.5},
            },
            "weak_areas": [],
            "error_patterns": [],
            "learning_goals": [],
            "interest_areas": [],
            "learning_tempo": {
                "study_speed": "moderate",
                "optimal_session_duration": 45,
                "weekly_study_capacity": 10,
                "focus_score": 0.7,
            },
            "practical_preferences": {
                "coding_proficiency": {},
                "preferred_practice_types": [],
                "overall_score": 0.5,
            },
        }

    def _ensure_complete_profile(self, profile: Dict[str, Any], fallback: Dict[str, Any]) -> Dict[str, Any]:
        """确保画像包含所有必要维度，缺失时从 fallback 或默认值补齐"""
        defaults = self._default_profile(profile.get("student_id", ""))
        result = dict(profile)
        for key in defaults:
            if key not in result or result[key] is None:
                result[key] = fallback.get(key, defaults[key])
            elif isinstance(result[key], dict) and isinstance(defaults.get(key), dict):
                # 深度补齐字典内部缺失字段
                for sub_key, sub_default in defaults[key].items():
                    if sub_key not in result[key] or result[key][sub_key] is None:
                        fb_sub = fallback.get(key, {}).get(sub_key)
                        result[key][sub_key] = fb_sub if fb_sub is not None else sub_default
            elif isinstance(result[key], list) and isinstance(defaults.get(key), list):
                if not result[key] and fallback.get(key):
                    result[key] = fallback[key]
        return result
