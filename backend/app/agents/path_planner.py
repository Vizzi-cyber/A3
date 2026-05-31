"""
路径规划师智能体
负责分析学生知识状态，生成个性化学习路径
知识图谱约束：所有路径规划必须基于图谱内的知识点，防止幻觉
"""
from typing import Any, Dict, List, Optional

from .base import BaseAgent
from ..services.llm_factory import BaseLLM, LLMFactory
from ..core.safety import SafetyGuard, HallucinationGuard


class PathPlannerAgent(BaseAgent):
    """路径规划师智能体（受知识图谱约束）"""

    def __init__(self, llm: Optional[BaseLLM] = None):
        super().__init__(
            agent_id="path_planner",
            agent_name="路径规划师",
            description="分析学生知识状态，生成和调整个性化学习路径"
        )
        self.llm = llm or LLMFactory.get_default_llm()
        self._knowledge_graph: Optional[Dict[str, Any]] = None

    def set_knowledge_graph(self, graph_data: Dict[str, Any]):
        """注入知识图谱数据，后续路径规划将受此图谱约束"""
        self._knowledge_graph = graph_data

    def _load_knowledge_graph_from_db(self) -> Optional[Dict[str, Any]]:
        """从数据库加载最新知识图谱"""
        try:
            from ..models.database import SessionLocal
            from ..models.knowledge import KnowledgeGraphModel
            db = SessionLocal()
            try:
                kg = db.query(KnowledgeGraphModel).order_by(KnowledgeGraphModel.version.desc()).first()
                if kg and kg.graph_data:
                    return kg.graph_data
            finally:
                db.close()
        except Exception as e:
            self.logger.warning(f"Failed to load knowledge graph: {e}")
        return None

    def _build_graph_constraint_prompt(self) -> str:
        """构建知识图谱约束 prompt 片段"""
        kg = self._knowledge_graph
        if not kg:
            kg = self._load_knowledge_graph_from_db()
        if not kg:
            return ""

        nodes = kg.get("nodes", [])
        edges = kg.get("edges", [])
        if not nodes:
            return ""

        # 构建紧凑的节点摘要
        node_summary = [
            {
                "id": n["id"],
                "name": n["name"],
                "difficulty": n.get("difficulty", 3),
                "prerequisite": n.get("prerequisite", []),
                "learning_objective": n.get("learning_objective", ""),
            }
            for n in nodes
        ]

        return (
            "\n\n【知识图谱约束 - 必须严格遵守】\n"
            f"知识图谱节点（共{len(nodes)}个）：{node_summary}\n"
            f"依赖关系（共{len(edges)}条）：{edges}\n"
            "约束规则：\n"
            "1. 路径中的每一步必须对应图谱中的知识点ID，不能编造图谱外的知识点\n"
            "2. 必须按照前置依赖（prerequisite）顺序安排学习顺序\n"
            "3. 从难度低的知识点到难度高的知识点\n"
            "4. 路径的 topics 字段必须使用图谱中的知识点ID（如 kp_c01）\n"
        )

    def get_system_prompt(self) -> str:
        return (
            "你是一位经验丰富的学习路径规划专家，擅长根据学生的知识基础、目标和时间安排，"
            "设计分阶段、可执行的学习路径。路径应包含明确的知识点、预计时长和达成标准。\n"
            "重要规则：\n"
            "- 不要输出思考过程、分析步骤或'让我想想'之类的内心独白，直接输出最终规划结果\n"
            "- 如果提供了知识图谱约束，你必须严格依据图谱生成路径，不能生成图谱外的知识点\n"
            "- 路径中每个阶段的 topics 必须使用知识图谱中的知识点ID\n"
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
        weak_points = profile.get("weak_areas", [])

        # 构建知识图谱约束
        graph_constraint = self._build_graph_constraint_prompt()

        prompt = (
            f"请为学生制定一份学习路径，目标是掌握《{target}》。\n"
            f"学生每周可投入 {weekly_hours} 小时。\n"
        )
        if weak_points:
            prompt += f"学生薄弱点：{weak_points}\n"
        prompt += (
            "路径需分阶段（3-5个阶段），每阶段包含：知识点列表、预计时长、达成标准、推荐资源类型。\n"
            "返回 JSON：\n"
            "{\"target\": \"...\", \"estimated_total_hours\": 20, \"stages\": ["
            "  {\"stage_no\": 1, \"title\": \"...\", \"topics\": [...], \"hours\": 5, \"criteria\": \"...\", \"resources\": [...]}"
            "]}"
        )
        # 注入图谱约束（必须放在最后，作为强约束）
        if graph_constraint:
            prompt += graph_constraint

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

        # 构建知识图谱约束
        graph_constraint = self._build_graph_constraint_prompt()

        prompt = (
            "请根据学生反馈，对现有学习路径进行优化调整。\n"
            f"现有路径：{current_path}\n"
            f"学生反馈：{feedback}\n"
            "返回调整后的完整路径 JSON（格式同生成路径）。"
        )
        # 注入图谱约束
        if graph_constraint:
            prompt += graph_constraint

        prompt = SafetyGuard.sanitize_prompt(prompt)
        data = await self.llm.generate_json([
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": prompt},
        ], temperature=0.4)
        return {"status": "success", "task": "adjust_path", "path": data, "raw": data if data.get("status") == "error" else None}
