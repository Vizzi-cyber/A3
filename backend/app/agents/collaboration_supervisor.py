"""
协作督导Agent
监控团队协作状态，检测阻塞、冲突，提供协作建议
"""
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from .base import BaseAgent
from ..services.llm_factory import BaseLLM, LLMFactory
from ..core.safety import SafetyGuard


class CollaborationSupervisionAgent(BaseAgent):
    """协作督导Agent - 监控团队协作、检测阻塞与冲突"""

    def __init__(self, llm: Optional[BaseLLM] = None):
        super().__init__(
            agent_id="collaboration_supervisor",
            agent_name="协作督导",
            description="监控团队协作状态，检测阻塞、冲突，提供协作建议"
        )
        self.llm = llm or LLMFactory.get_default_llm()

    def get_system_prompt(self) -> str:
        return (
            "你是一位经验丰富的团队协作督导专家，专门负责监控和指导学生团队的项目协作。\n"
            "你的核心能力是：\n"
            "1. 实时监控团队成员的进度同步情况\n"
            "2. 检测成员是否遇到阻塞（超过30分钟无进展）\n"
            "3. 识别团队成员间的接口分歧和冲突\n"
            "4. 促进跨成员的知识共享\n"
            "5. 生成每日协作报告\n\n"
            "重要规则：\n"
            "- 及时发现并提醒潜在风险\n"
            "- 提供具体可执行的解决建议\n"
            "- 保持客观公正的督导态度\n"
            "- 关注团队整体协作效率\n"
        )

    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        context:
        {
            "task": "daily_report" | "detect_blockers" | "resolve_conflict" | "knowledge_sharing" | "sync_progress",
            "project_id": "xxx",
            "team_members": [...],
            "progress_data": {...},
            ...
        }
        """
        self.status = "running"
        task = context.get("task", "daily_report")

        try:
            if task == "daily_report":
                result = await self._generate_daily_report(context)
            elif task == "detect_blockers":
                result = await self._detect_blockers(context)
            elif task == "resolve_conflict":
                result = await self._resolve_conflict(context)
            elif task == "knowledge_sharing":
                result = await self._knowledge_sharing(context)
            elif task == "sync_progress":
                result = await self._sync_progress(context)
            else:
                result = {"status": "failed", "error": f"Unknown task: {task}"}

            self.status = "completed"
            return result
        except Exception as e:
            self.status = "failed"
            self.logger.error(f"CollaborationSupervisionAgent error: {e}")
            return {"status": "failed", "error": str(e)}

    async def _generate_daily_report(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """生成每日协作报告"""
        project_id = context.get("project_id", "")
        team_members = context.get("team_members", [])
        progress_data = context.get("progress_data", {})

        prompt = (
            f"请为以下团队生成每日协作报告：\n\n"
            f"项目ID：{project_id}\n"
            f"团队成员：{', '.join([m.get('name', m.get('student_id', '')) for m in team_members])}\n"
            f"进度数据：{progress_data}\n\n"
            "请返回 JSON 格式的报告：\n"
            "{\n"
            '  "report_date": "2024-01-01",\n'
            '  "summary": "今日协作概况",\n'
            '  "member_status": [\n'
            "    {\n"
            '      "student_id": "成员ID",\n'
            '      "name": "姓名",\n'
            '      "tasks_completed": 2,\n'
            '      "tasks_in_progress": 1,\n'
            '      "blockers": [],\n'
            '      "contribution_score": 85\n'
            "    }\n"
            "  ],\n"
            '  "team_health": {\n'
            '    "collaboration_score": 80,\n'
            '    "communication_score": 75,\n'
            '    "progress_score": 70,\n'
            '    "overall_score": 75\n'
            "  },\n"
            '  "risks": ["风险1"],\n'
            '  "recommendations": ["建议1"],\n'
            '  "action_items": ["待办事项1"]\n'
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
            "task": "daily_report",
            "report": data,
        }

    async def _detect_blockers(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """检测成员阻塞情况"""
        team_members = context.get("team_members", [])
        progress_data = context.get("progress_data", {})

        # 分析每个成员的阻塞状态
        blockers = []
        for member in team_members:
            member_id = member.get("student_id", "")
            member_progress = progress_data.get(member_id, {})
            last_update = member_progress.get("last_update", "")
            current_task = member_progress.get("current_task", "")

            # 检查是否超过30分钟无进展
            if last_update:
                try:
                    last_time = datetime.fromisoformat(last_update.replace("Z", "+00:00"))
                    now = datetime.now(timezone.utc)
                    minutes_since = (now - last_time).total_seconds() / 60

                    if minutes_since > 30:
                        blockers.append({
                            "student_id": member_id,
                            "name": member.get("name", ""),
                            "current_task": current_task,
                            "minutes_stuck": int(minutes_since),
                            "severity": "high" if minutes_since > 120 else "medium",
                            "suggestion": self._get_blocker_suggestion(member, member_progress),
                        })
                except (ValueError, TypeError):
                    pass

        # 使用LLM分析潜在阻塞
        prompt = (
            f"请分析以下团队成员的进度数据，识别可能的阻塞风险：\n\n"
            f"成员列表：{team_members}\n"
            f"进度数据：{progress_data}\n\n"
            "返回 JSON 格式：\n"
            "{\n"
            '  "potential_blockers": [\n'
            "    {\n"
            '      "student_id": "成员ID",\n'
            '      "risk_level": "low/medium/high",\n'
            '      "reason": "阻塞原因分析",\n'
            '      "suggestion": "解决建议"\n'
            "    }\n"
            "  ],\n"
            '  "team_risk_summary": "团队整体风险评估"\n'
            "}"
        )

        prompt = SafetyGuard.sanitize_prompt(prompt)
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": prompt},
        ]

        llm_analysis = await self.llm.generate_json(messages, temperature=0.3, max_tokens=4096)

        return {
            "status": "success",
            "task": "detect_blockers",
            "blockers": blockers,
            "analysis": llm_analysis,
        }

    def _get_blocker_suggestion(self, member: Dict, progress: Dict) -> str:
        """根据成员情况生成阻塞解决建议"""
        task = progress.get("current_task", "未知任务")
        return f"建议{member.get('name', '该成员')}暂停当前任务「{task}」，先与团队讨论或寻求帮助"

    async def _resolve_conflict(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """解决团队冲突"""
        conflict_description = context.get("conflict_description", "")
        involved_members = context.get("involved_members", [])
        project_context = context.get("project_context", "")

        prompt = (
            f"请帮助解决以下团队协作冲突：\n\n"
            f"冲突描述：{conflict_description}\n"
            f"涉及成员：{', '.join([m.get('name', '') for m in involved_members])}\n"
            f"项目背景：{project_context}\n\n"
            "请返回 JSON 格式的解决方案：\n"
            "{\n"
            '  "conflict_type": "interface_disagreement / task_allocation / technical_choice / communication",\n'
            '  "root_cause": "冲突根本原因",\n'
            '  "solutions": [\n'
            "    {\n"
            '      "option": "方案描述",\n'
            '      "pros": ["优点1"],\n'
            '      "cons": ["缺点1"],\n'
            '      "recommended": true\n'
            "    }\n"
            "  ],\n"
            '  "mediation_steps": ["调解步骤1", "调解步骤2"],\n'
            '  "prevention_tips": ["预防建议1"]\n'
            "}"
        )

        prompt = SafetyGuard.sanitize_prompt(prompt)
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": prompt},
        ]

        data = await self.llm.generate_json(messages, temperature=0.4, max_tokens=4096)
        return {
            "status": "success",
            "task": "resolve_conflict",
            "resolution": data,
        }

    async def _knowledge_sharing(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """促进知识共享"""
        team_members = context.get("team_members", [])
        project_modules = context.get("project_modules", [])

        # 分析每个成员的技能分布
        skills_map = {}
        for member in team_members:
            for skill in member.get("skills", []):
                if skill not in skills_map:
                    skills_map[skill] = []
                skills_map[skill].append(member.get("name", ""))

        prompt = (
            f"请为以下团队制定知识共享计划：\n\n"
            f"团队成员及技能：\n"
        )
        for member in team_members:
            prompt += f"- {member.get('name', '')}: 技能={member.get('skills', [])}, 当前任务={member.get('current_task', '无')}\n"

        prompt += (
            f"\n项目模块：{[m.get('name', '') for m in project_modules]}\n\n"
            "请返回 JSON 格式的知识共享计划：\n"
            "{\n"
            '  "skill_gaps": [\n'
            "    {\n"
            '      "member": "成员名",\n'
            '      "missing_skills": ["技能1"],\n'
            '      "recommended_mentor": "导师成员名"\n'
            "    }\n"
            "  ],\n"
            '  "sharing_sessions": [\n'
            "    {\n"
            '      "topic": "分享主题",\n'
            '      "presenter": "主讲人",\n'
            '      "audience": ["听众1"],\n'
            '      "duration_minutes": 30\n'
            "    }\n"
            "  ],\n"
            '  "documentation_needed": ["需要文档化的知识点1"]\n'
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
            "task": "knowledge_sharing",
            "plan": data,
        }

    async def _sync_progress(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """同步进度"""
        team_members = context.get("team_members", [])
        progress_data = context.get("progress_data", {})
        project_id = context.get("project_id", "")

        # 计算总体进度
        total_tasks = 0
        completed_tasks = 0
        for member_id, member_progress in progress_data.items():
            total_tasks += member_progress.get("total_tasks", 0)
            completed_tasks += member_progress.get("completed_tasks", 0)

        overall_progress = round(completed_tasks / total_tasks * 100, 1) if total_tasks > 0 else 0

        return {
            "status": "success",
            "task": "sync_progress",
            "project_id": project_id,
            "overall_progress": overall_progress,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "member_progress": [
                {
                    "student_id": member.get("student_id", ""),
                    "name": member.get("name", ""),
                    "progress": progress_data.get(member.get("student_id", ""), {}),
                    "status": self._get_member_status(progress_data.get(member.get("student_id", ""), {})),
                }
                for member in team_members
            ],
            "sync_time": datetime.now(timezone.utc).isoformat(),
        }

    def _get_member_status(self, progress: Dict) -> str:
        """判断成员状态"""
        if not progress:
            return "inactive"
        completed = progress.get("completed_tasks", 0)
        total = progress.get("total_tasks", 0)
        if total == 0:
            return "no_tasks"
        ratio = completed / total
        if ratio >= 0.8:
            return "on_track"
        elif ratio >= 0.5:
            return "slightly_behind"
        else:
            return "behind"
