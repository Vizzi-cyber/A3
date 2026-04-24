"""
路径规划师智能体
负责分析学生知识状态，生成个性化学习路径
"""
from typing import Any, Dict, List, Optional

from .base import BaseAgent
from ..services.llm_factory import BaseLLM, LLMFactory
from ..core.safety import SafetyGuard, HallucinationGuard


class PathPlannerAgent(BaseAgent):
    """路径规划师智能体"""

    def __init__(self, llm: Optional[BaseLLM] = None):
        super().__init__(
            agent_id="path_planner",
            agent_name="路径规划师",
            description="分析学生知识状态，生成和调整个性化学习路径"
        )
        self.llm = llm or LLMFactory.get_default_llm()

    def get_system_prompt(self) -> str:
        return (
            "你是一位经验丰富的学习路径规划专家，擅长根据学生的知识基础、目标和时间安排，"
            "设计分阶段、可执行的学习路径。路径应包含明确的知识点、预计时长和达成标准。"
            "重要：不要输出思考过程、分析步骤或'让我想想'之类的内心独白，直接输出最终规划结果。"
        )

    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        context:
        {
            "task": "analyze_knowledge_state" | "generate_path" | "adjust_path",
            "student_id": "s123",
            "profile": {...},
            "target": "掌握 Python 面向对象编程",
            "current_path": {...},  # 用于 adjust
            "feedback": "进度太慢，希望加快"  # 用于 adjust
        }
        """
        self.status = "running"
        task = context.get("task", "generate_path")
        target = context.get("target", "")

        safety = SafetyGuard.check_input(target)
        if not safety["safe"]:
            return {"status": "blocked", "reason": safety["message"]}

        try:
            if task == "analyze_knowledge_state":
                result = await self._analyze_knowledge(context)
            elif task == "generate_path":
                result = await self._generate_path(context)
            elif task == "adjust_path":
                result = await self._adjust_path(context)
            else:
                result = {"status": "failed", "error": f"Unknown task: {task}"}

            # 结构校验
            if result.get("status") == "success" and isinstance(result.get("path"), dict):
                schema = HallucinationGuard.verify_json_schema(
                    result["path"], ["stages", "target", "estimated_total_hours"]
                )
                if not schema["valid"]:
                    result["warning"] = schema["message"]

            self.status = "completed"
            return result
        except Exception as e:
            self.status = "failed"
            self.logger.error(f"PathPlannerAgent error: {e}")
            return {"status": "failed", "error": str(e)}

    async def _analyze_knowledge(self, context: Dict[str, Any]) -> Dict[str, Any]:
        profile = context.get("profile", {})
        target = context.get("target", "")
        prompt = (
            "请分析以下学生的知识状态，针对目标技能列出："
            "已掌握的前置知识、存在的知识缺口、建议的补习点。\n"
            f"学生画像：{profile}\n"
            f"目标：{target}\n"
            "返回 JSON：{\"mastered\": [...], \"gaps\": [...], \"remedial\": [...]}"
        )
        prompt = SafetyGuard.sanitize_prompt(prompt)
        data = await self.llm.generate_json([
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": prompt},
        ], temperature=0.4)
        return {"status": "success", "task": "analyze", "analysis": data}

    async def _generate_path(self, context: Dict[str, Any]) -> Dict[str, Any]:
        profile = context.get("profile", {})
        target = context.get("target", "")
        tempo = profile.get("learning_tempo", {})
        weekly_hours = tempo.get("weekly_study_capacity", 10)
        prompt = (
            f"请为学生制定一份学习路径，目标是掌握《{target}》。\n"
            f"学生每周可投入 {weekly_hours} 小时。\n"
            "路径需分阶段（3-5个阶段），每阶段包含：知识点列表、预计时长、达成标准、推荐资源类型。\n"
            "返回 JSON：\n"
            "{\"target\": \"...\", \"estimated_total_hours\": 20, \"stages\": ["
            "  {\"stage_no\": 1, \"title\": \"...\", \"topics\": [...], \"hours\": 5, \"criteria\": \"...\", \"resources\": [...]}"
            "]}"
        )
        prompt = SafetyGuard.sanitize_prompt(prompt)
        data = await self.llm.generate_json([
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": prompt},
        ], temperature=0.4, max_tokens=2048)
        path = data if data.get("status") != "error" else data
        return {"status": "success", "task": "generate_path", "path": path, "raw": data if data.get("status") == "error" else None}

    async def _adjust_path(self, context: Dict[str, Any]) -> Dict[str, Any]:
        current_path = context.get("current_path", {})
        feedback = context.get("feedback", "")
        prompt = (
            "请根据学生反馈，对现有学习路径进行优化调整。\n"
            f"现有路径：{current_path}\n"
            f"学生反馈：{feedback}\n"
            "返回调整后的完整路径 JSON（格式同生成路径）。"
        )
        prompt = SafetyGuard.sanitize_prompt(prompt)
        data = await self.llm.generate_json([
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": prompt},
        ], temperature=0.4)
        return {"status": "success", "task": "adjust_path", "path": data, "raw": data if data.get("status") == "error" else None}
