"""
角色匹配Agent
根据学生能力画像和项目任务，自动匹配最优组队与分工方案
"""
from typing import Any, Dict, List, Optional
from .base import BaseAgent
from ..services.llm_factory import BaseLLM, LLMFactory
from ..core.safety import SafetyGuard


class RoleMatcherAgent(BaseAgent):
    """角色匹配Agent"""

    # 角色定义
    ROLES = {
        "architect": {
            "name": "架构师",
            "description": "负责整体设计和核心算法",
            "required_skills": ["逻辑思维", "算法设计", "系统设计"],
            "preferred_traits": ["analytical", "systematic"],
        },
        "developer": {
            "name": "开发者",
            "description": "负责核心功能实现",
            "required_skills": ["编程能力", "调试能力", "代码阅读"],
            "preferred_traits": ["detail-oriented", "problem-solver"],
        },
        "tester": {
            "name": "测试员",
            "description": "负责测试和质量保证",
            "required_skills": ["细心", "逻辑思维", "文档能力"],
            "preferred_traits": ["careful", "methodical"],
        },
        "ui_developer": {
            "name": "界面开发者",
            "description": "负责用户界面设计和实现",
            "required_skills": ["界面设计", "用户体验", "交互逻辑"],
            "preferred_traits": ["creative", "user-focused"],
        },
        "documenter": {
            "name": "文档员",
            "description": "负责文档编写和代码注释",
            "required_skills": ["写作能力", "代码理解", "组织能力"],
            "preferred_traits": ["organized", "communicative"],
        },
    }

    def __init__(self, llm: Optional[BaseLLM] = None):
        super().__init__(
            agent_id="role_matcher",
            agent_name="角色匹配师",
            description="根据学生能力画像和项目任务，自动匹配最优组队与分工方案"
        )
        self.llm = llm or LLMFactory.get_default_llm()

    def get_system_prompt(self) -> str:
        return (
            "你是一位资深的人力资源专家，专门负责团队组建和任务分配。\n"
            "你的核心能力是：\n"
            "1. 分析每个学生的技能和特长\n"
            "2. 根据项目需求匹配最合适的角色\n"
            "3. 确保团队能力互补，避免强者包揽\n"
            "4. 考虑学生的学习成长需求\n\n"
            "重要规则：\n"
            "- 优先考虑能力互补，而不是简单的能力排序\n"
            "- 要给每个成员成长的机会\n"
            "- 避免让一个人承担过多任务\n"
            "- 考虑学生的兴趣和偏好\n"
        )

    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        context:
        {
            "task": "match_team" | "suggest_role" | "rebalance",
            "students": [
                {
                    "student_id": "s1",
                    "name": "张三",
                    "profile": {...},  # 六维画像
                    "skills": ["C语言基础", "逻辑思维"],
                    "preferences": ["算法", "后端"]
                }
            ],
            "project_tasks": {...},  # 项目任务树
            "current_assignments": {...}  # 当前分配（用于rebalance）
        }
        """
        self.status = "running"
        task = context.get("task", "match_team")

        try:
            if task == "match_team":
                result = await self._match_team(context)
            elif task == "suggest_role":
                result = await self._suggest_role(context)
            elif task == "rebalance":
                result = await self._rebalance(context)
            elif task == "get_roles":
                result = self._get_roles()
            else:
                result = {"status": "failed", "error": f"Unknown task: {task}"}

            self.status = "completed"
            return result
        except Exception as e:
            self.status = "failed"
            self.logger.error(f"RoleMatcherAgent error: {e}")
            return {"status": "failed", "error": str(e)}

    def _get_roles(self) -> Dict[str, Any]:
        """获取角色定义"""
        return {
            "status": "success",
            "task": "get_roles",
            "roles": self.ROLES,
        }

    async def _match_team(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """匹配团队和分工"""
        students = context.get("students", [])
        project_tasks = context.get("project_tasks", {})

        if not students:
            return {"status": "failed", "error": "没有提供学生信息"}

        prompt = (
            f"请为以下团队匹配最优分工方案：\n\n"
            f"团队成员（{len(students)}人）：\n"
        )

        for i, student in enumerate(students, 1):
            profile = student.get("profile", {})
            prompt += (
                f"\n成员{i}：{student.get('name', f'学生{i}')}\n"
                f"  - ID: {student.get('student_id', '')}\n"
                f"  - 技能: {', '.join(student.get('skills', []))}\n"
                f"  - 偏好: {', '.join(student.get('preferences', []))}\n"
                f"  - 画像摘要: {profile}\n"
            )

        if project_tasks:
            prompt += f"\n项目任务树：{project_tasks}\n"

        prompt += (
            "\n可用角色：\n"
            "1. 架构师：负责整体设计和核心算法\n"
            "2. 开发者：负责核心功能实现\n"
            "3. 测试员：负责测试和质量保证\n"
            "4. 界面开发者：负责用户界面\n"
            "5. 文档员：负责文档编写\n\n"
            "请返回 JSON 格式的分工方案：\n"
            "{\n"
            '  "team_assignments": [\n'
            "    {\n"
            '      "student_id": "学生ID",\n'
            '      "student_name": "学生姓名",\n'
            '      "primary_role": "主要角色",\n'
            '      "secondary_role": "辅助角色（可选）",\n'
            '      "assigned_tasks": ["任务ID列表"],\n'
            '      "reason": "分配理由",\n'
            '      "growth_areas": ["该学生可以发展的能力"]\n'
            "    }\n"
            "  ],\n"
            '  "team_dynamics": {\n'
            '    "strengths": ["团队优势"],\n'
            '    "potential_issues": ["潜在问题"],\n'
            '    "suggestions": ["团队协作建议"]\n'
            "  },\n"
            '  "collaboration_plan": {\n'
            '    "communication_frequency": "沟通频率建议",\n'
            '    "code_review_pairs": [["学生A", "学生B"]],\n'
            '    "knowledge_sharing": ["知识分享建议"]\n'
            "  }\n"
            "}"
        )

        prompt = SafetyGuard.sanitize_prompt(prompt)
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": prompt},
        ]

        data = await self.llm.generate_json(messages, temperature=0.4)
        return {
            "status": "success",
            "task": "match_team",
            "assignments": data,
        }

    async def _suggest_role(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """为单个学生建议角色"""
        student = context.get("student", {})
        project_tasks = context.get("project_tasks", {})

        prompt = (
            f"请为以下学生建议最适合的团队角色：\n\n"
            f"学生信息：\n"
            f"  - 姓名: {student.get('name', '')}\n"
            f"  - 技能: {', '.join(student.get('skills', []))}\n"
            f"  - 偏好: {', '.join(student.get('preferences', []))}\n"
            f"  - 画像: {student.get('profile', {})}\n\n"
        )

        if project_tasks:
            prompt += f"项目任务：{project_tasks}\n\n"

        prompt += (
            "请返回 JSON 格式的角色建议：\n"
            "{\n"
            '  "recommended_role": "推荐角色",\n'
            '  "match_score": 0.0-1.0,\n'
            '  "reasons": ["推荐理由"],\n'
            '  "alternative_roles": ["备选角色"],\n'
            '  "skill_gaps": ["需要补充的技能"],\n'
            '  "growth_path": ["成长路径建议"]\n'
            "}"
        )

        prompt = SafetyGuard.sanitize_prompt(prompt)
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": prompt},
        ]

        data = await self.llm.generate_json(messages, temperature=0.4)
        return {
            "status": "success",
            "task": "suggest_role",
            "suggestion": data,
        }

    async def _rebalance(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """重新平衡任务分配"""
        students = context.get("students", [])
        current_assignments = context.get("current_assignments", {})
        project_tasks = context.get("project_tasks", {})
        issues = context.get("issues", [])  # 当前存在的问题

        prompt = (
            f"请重新平衡以下团队的任务分配：\n\n"
            f"当前分配：{current_assignments}\n\n"
            f"存在的问题：{issues}\n\n"
            f"团队成员：\n"
        )

        for student in students:
            prompt += (
                f"  - {student.get('name', '')}: "
                f"技能={student.get('skills', [])}, "
                f"当前任务={student.get('current_tasks', [])}\n"
            )

        prompt += (
            "\n请返回调整后的分配方案：\n"
            "{\n"
            '  "adjustments": [\n'
            "    {\n"
            '      "student_id": "学生ID",\n'
            '      "action": "add/remove/swap",\n'
            '      "tasks": ["任务ID"],\n'
            '      "reason": "调整原因"\n'
            "    }\n"
            "  ],\n"
            '  "new_assignments": {...},\n'
            '  "expected_improvements": ["预期改进"]\n'
            "}"
        )

        prompt = SafetyGuard.sanitize_prompt(prompt)
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": prompt},
        ]

        data = await self.llm.generate_json(messages, temperature=0.4)
        return {
            "status": "success",
            "task": "rebalance",
            "rebalanced": data,
        }
