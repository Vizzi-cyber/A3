"""
成果评估Agent
评估团队项目成果，包括代码质量、协作效果、学习收获等
"""
from typing import Any, Dict, List, Optional
from .base import BaseAgent
from ..services.llm_factory import BaseLLM, LLMFactory
from ..core.safety import SafetyGuard


class ResultEvaluatorAgent(BaseAgent):
    """成果评估Agent - 多维度评估项目成果"""

    def __init__(self, llm: Optional[BaseLLM] = None):
        super().__init__(
            agent_id="result_evaluator",
            agent_name="成果评估师",
            description="多维度评估项目成果，包括代码质量、协作效果、学习收获"
        )
        self.llm = llm or LLMFactory.get_default_llm()

    def get_system_prompt(self) -> str:
        return (
            "你是一位专业的教育评估专家，专门负责评估学生的项目成果。\n"
            "你的核心能力是：\n"
            "1. 评估代码质量（可读性、结构、规范性）\n"
            "2. 评估团队协作效果（分工合理性、沟通效率）\n"
            "3. 评估项目交付物（功能完整性、创新性）\n"
            "4. 评估学习收获（知识掌握、能力提升）\n"
            "5. 生成综合评估报告\n\n"
            "重要规则：\n"
            "- 评估标准要客观公正\n"
            "- 既要指出不足也要肯定优点\n"
            "- 提供具体的改进建议\n"
            "- 关注学生的成长和进步\n"
        )

    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        context:
        {
            "task": "evaluate_code" | "evaluate_collaboration" | "evaluate_deliverable" | "evaluate_learning" | "full_report",
            "project_id": "xxx",
            "team_members": [...],
            "code_submission": {...},
            "collaboration_data": {...},
            ...
        }
        """
        self.status = "running"
        task = context.get("task", "full_report")

        try:
            if task == "evaluate_code":
                result = await self._evaluate_code(context)
            elif task == "evaluate_collaboration":
                result = await self._evaluate_collaboration(context)
            elif task == "evaluate_deliverable":
                result = await self._evaluate_deliverable(context)
            elif task == "evaluate_learning":
                result = await self._evaluate_learning(context)
            elif task == "full_report":
                result = await self._generate_full_report(context)
            else:
                result = {"status": "failed", "error": f"Unknown task: {task}"}

            self.status = "completed"
            return result
        except Exception as e:
            self.status = "failed"
            self.logger.error(f"ResultEvaluatorAgent error: {e}")
            return {"status": "failed", "error": str(e)}

    async def _evaluate_code(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """评估代码质量"""
        code_submission = context.get("code_submission", {})
        language = context.get("language", "C")

        code_content = code_submission.get("code", "")
        file_name = code_submission.get("file_name", "main.c")

        prompt = (
            f"请评估以下{language}代码的质量：\n\n"
            f"文件名：{file_name}\n"
            f"代码：\n```{language.lower()}\n{code_content}\n```\n\n"
            "请返回 JSON 格式的评估报告：\n"
            "{\n"
            '  "overall_score": 85,\n'
            '  "dimensions": {\n'
            '    "readability": {"score": 80, "comments": "可读性评价"},\n'
            '    "structure": {"score": 85, "comments": "结构评价"},\n'
            '    "naming_convention": {"score": 90, "comments": "命名规范评价"},\n'
            '    "error_handling": {"score": 70, "comments": "错误处理评价"},\n'
            '    "efficiency": {"score": 80, "comments": "效率评价"},\n'
            '    "documentation": {"score": 75, "comments": "注释文档评价"}\n'
            "  },\n"
            '  "strengths": ["优点1", "优点2"],\n'
            '  "improvements": ["改进建议1", "改进建议2"],\n'
            '  "code_quality_level": "good"\n'
            "}"
        )

        prompt = SafetyGuard.sanitize_prompt(prompt)
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": prompt},
        ]

        data = await self.llm.generate_json(messages, temperature=0.3, max_tokens=4096)
        return {
            "status": "success",
            "task": "evaluate_code",
            "evaluation": data,
        }

    async def _evaluate_collaboration(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """评估团队协作效果"""
        collaboration_data = context.get("collaboration_data", {})
        team_members = context.get("team_members", [])

        prompt = (
            f"请评估以下团队的协作效果：\n\n"
            f"团队成员：{', '.join([m.get('name', '') for m in team_members])}\n"
            f"协作数据：{collaboration_data}\n\n"
            "请返回 JSON 格式的评估报告：\n"
            "{\n"
            '  "overall_score": 80,\n'
            '  "dimensions": {\n'
            '    "task_distribution": {"score": 85, "comments": "分工合理性评价"},\n'
            '    "communication": {"score": 75, "comments": "沟通效率评价"},\n'
            '    "contribution_balance": {"score": 80, "comments": "贡献均衡性评价"},\n'
            '    "conflict_resolution": {"score": 70, "comments": "冲突处理评价"},\n'
            '    "timeline_adherence": {"score": 85, "comments": "进度遵守评价"}\n'
            "  },\n"
            '  "team_dynamics": {\n'
            '    "strengths": ["团队优势1"],\n'
            '    "weaknesses": ["团队不足1"],\n'
            '    "recommendations": ["改进建议1"]\n'
            "  },\n"
            '  "member_contributions": [\n'
            "    {\n"
            '      "student_id": "成员ID",\n'
            '      "name": "姓名",\n'
            '      "contribution_score": 85,\n'
            '      "highlights": ["亮点1"],\n'
            '      "areas_to_improve": ["改进点1"]\n'
            "    }\n"
            "  ]\n"
            "}"
        )

        prompt = SafetyGuard.sanitize_prompt(prompt)
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": prompt},
        ]

        data = await self.llm.generate_json(messages, temperature=0.3, max_tokens=4096)
        return {
            "status": "success",
            "task": "evaluate_collaboration",
            "evaluation": data,
        }

    async def _evaluate_deliverable(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """评估项目交付物"""
        project_info = context.get("project_info", {})
        deliverables = context.get("deliverables", [])
        team_level = context.get("team_level", "beginner")

        prompt = (
            f"请评估以下项目交付物：\n\n"
            f"项目信息：{project_info}\n"
            f"团队水平：{team_level}\n"
            f"交付物列表：{deliverables}\n\n"
            "请返回 JSON 格式的评估报告：\n"
            "{\n"
            '  "overall_score": 82,\n'
            '  "dimensions": {\n'
            '    "completeness": {"score": 85, "comments": "功能完整性评价"},\n'
            '    "correctness": {"score": 80, "comments": "功能正确性评价"},\n'
            '    "innovation": {"score": 75, "comments": "创新性评价"},\n'
            '    "usability": {"score": 80, "comments": "易用性评价"},\n'
            '    "robustness": {"score": 78, "comments": "健壮性评价"}\n'
            "  },\n"
            '  "feature_checklist": [\n'
            "    {\n"
            '      "feature": "功能名称",\n'
            '      "status": "completed/partial/missing",\n'
            '      "quality": "good/acceptable/poor"\n'
            "    }\n"
            "  ],\n"
            '  "highlights": ["亮点1"],\n'
            '  "issues": ["问题1"],\n'
            '  "improvement_suggestions": ["建议1"]\n'
            "}"
        )

        prompt = SafetyGuard.sanitize_prompt(prompt)
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": prompt},
        ]

        data = await self.llm.generate_json(messages, temperature=0.3, max_tokens=4096)
        return {
            "status": "success",
            "task": "evaluate_deliverable",
            "evaluation": data,
        }

    async def _evaluate_learning(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """评估学习收获"""
        team_members = context.get("team_members", [])
        project_info = context.get("project_info", {})
        knowledge_points = context.get("knowledge_points", [])

        prompt = (
            f"请评估团队成员的学习收获：\n\n"
            f"项目：{project_info.get('name', '未知项目')}\n"
            f"涉及知识点：{knowledge_points}\n"
            f"团队成员：{', '.join([m.get('name', '') for m in team_members])}\n\n"
            "请返回 JSON 格式的评估报告：\n"
            "{\n"
            '  "overall_learning_score": 80,\n'
            '  "knowledge_mastery": [\n'
            "    {\n"
            '      "knowledge_point": "知识点名称",\n'
            '      "mastery_level": "掌握/了解/未掌握",\n'
            '      "application_quality": "good/acceptable/poor"\n'
            "    }\n"
            "  ],\n"
            '  "skill_development": {\n'
            '    "programming_skills": {"before": "beginner", "after": "intermediate"},\n'
            '    "problem_solving": {"improvement": "significant/moderate/minimal"},\n'
            '    "teamwork": {"improvement": "significant/moderate/minimal"}\n'
            "  },\n"
            '  "individual_assessments": [\n'
            "    {\n"
            '      "student_id": "成员ID",\n'
            '      "name": "姓名",\n'
            '      "learning_score": 85,\n'
            '      "key_achievements": ["成就1"],\n'
            '      "areas_for_growth": ["成长方向1"]\n'
            "    }\n"
            "  ],\n"
            '  "recommendations": ["后续学习建议1"]\n'
            "}"
        )

        prompt = SafetyGuard.sanitize_prompt(prompt)
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": prompt},
        ]

        data = await self.llm.generate_json(messages, temperature=0.3, max_tokens=4096)
        return {
            "status": "success",
            "task": "evaluate_learning",
            "evaluation": data,
        }

    async def _generate_full_report(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """生成综合评估报告"""
        project_info = context.get("project_info", {})
        team_members = context.get("team_members", [])
        code_submissions = context.get("code_submissions", [])
        collaboration_data = context.get("collaboration_data", {})
        deliverables = context.get("deliverables", [])
        knowledge_points = context.get("knowledge_points", [])
        team_level = context.get("team_level", "beginner")

        prompt = (
            f"请为以下项目生成综合评估报告：\n\n"
            f"项目名称：{project_info.get('name', '未知项目')}\n"
            f"项目描述：{project_info.get('description', '')}\n"
            f"团队水平：{team_level}\n"
            f"团队成员：{', '.join([m.get('name', '') for m in team_members])}\n"
            f"涉及知识点：{knowledge_points}\n"
            f"提交代码数：{len(code_submissions)}\n"
            f"交付物数：{len(deliverables)}\n\n"
            "请返回 JSON 格式的综合报告：\n"
            "{\n"
            '  "project_name": "项目名称",\n'
            '  "evaluation_date": "2024-01-01",\n'
            '  "overall_score": 82,\n'
            '  "grade": "B+",\n'
            '  "summary": "项目整体评价摘要",\n'
            '  "dimension_scores": {\n'
            '    "code_quality": 80,\n'
            '    "collaboration": 85,\n'
            '    "deliverable": 78,\n'
            '    "learning": 82\n'
            "  },\n"
            '  "team_performance": [\n'
            "    {\n"
            '      "student_id": "成员ID",\n'
            '      "name": "姓名",\n'
            '      "overall_score": 85,\n'
            '      "code_contribution": 80,\n'
            '      "collaboration_score": 85,\n'
            '      "learning_score": 82,\n'
            '      "strengths": ["优势1"],\n'
            '      "improvements": ["改进点1"]\n'
            "    }\n"
            "  ],\n"
            '  "project_highlights": ["项目亮点1"],\n'
            '  "project_issues": ["项目问题1"],\n'
            '  "final_recommendations": ["最终建议1"]\n'
            "}"
        )

        prompt = SafetyGuard.sanitize_prompt(prompt)
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": prompt},
        ]

        data = await self.llm.generate_json(messages, temperature=0.3, max_tokens=4096)
        return {
            "status": "success",
            "task": "full_report",
            "report": data,
        }
