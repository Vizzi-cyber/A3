"""
资源生成师智能体
负责生成多模态学习资源：文档、练习题、代码示例、思维导图
知识图谱约束：所有资源生成必须基于图谱内的知识点，防止幻觉和超纲
"""
from typing import Any, Dict, List, Optional

from .base import BaseAgent
from ..services.llm_factory import BaseLLM, LLMFactory
from ..core.safety import SafetyGuard, HallucinationGuard


class ResourceGeneratorAgent(BaseAgent):
    """资源生成师智能体（受知识图谱约束）"""

    def __init__(self, llm: Optional[BaseLLM] = None):
        super().__init__(
            agent_id="resource_generator",
            agent_name="资源生成师",
            description="根据学习主题和学生画像生成个性化学习资源"
        )
        self.llm = llm or LLMFactory.get_default_llm()
        self._knowledge_graph: Optional[Dict[str, Any]] = None

    def set_knowledge_graph(self, graph_data: Dict[str, Any]):
        """注入知识图谱数据，后续资源生成将受此图谱约束"""
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

    def _get_node_info(self, topic: str) -> Optional[Dict[str, Any]]:
        """根据主题名或ID查找图谱节点信息"""
        kg = self._knowledge_graph or self._load_knowledge_graph_from_db()
        if not kg:
            return None
        for node in kg.get("nodes", []):
            if node["id"] == topic or node["name"] == topic:
                return node
        return None

    def _build_profile_snippet(self, context: Dict[str, Any]) -> str:
        """从 context 提取画像信息构建个性化 prompt 片段"""
        profile = context.get("profile", {})
        style = context.get("cognitive_style", profile.get("cognitive_style", {}).get("primary", "visual"))
        weak_areas = profile.get("weak_areas", [])
        knowledge_level = profile.get("knowledge_base", {}).get("overall_score", 0.5)
        interest_areas = profile.get("interest_areas", [])

        parts = []
        parts.append(f"学生认知风格：{style}")
        if weak_areas:
            parts.append(f"薄弱知识点：{', '.join(weak_areas[:5])}")
        level_map = {0: "基础", 0.3: "初等", 0.5: "中等", 0.7: "中高等", 0.9: "高等"}
        level_label = "中等"
        for threshold, label in sorted(level_map.items()):
            if knowledge_level >= threshold:
                level_label = label
        parts.append(f"学生知识水平：{level_label}")
        if interest_areas:
            interests = [a.get("area", str(a))[:20] for a in interest_areas[:3]]
            parts.append(f"兴趣领域：{', '.join(interests)}")
        return "\n".join(parts)

    def _build_resource_constraint_prompt(self, topic: str) -> str:
        """构建资源生成约束 prompt 片段"""
        node = self._get_node_info(topic)
        if not node:
            return ""

        return (
            "\n\n【知识图谱约束 - 必须严格遵守】\n"
            f"当前知识点：{node['name']}（ID: {node['id']}）\n"
            f"难度等级：{node.get('difficulty', 3)}/5\n"
            f"学习目标：{node.get('learning_objective', '无')}\n"
            f"推荐资源类型：{node.get('resource_types', ['文档', '练习题库'])}\n"
            f"关联题型：{node.get('question_types', ['选择题', '编程题'])}\n"
            "约束规则：\n"
            "1. 只能围绕该知识点生成内容，不能扩展到图谱外的知识点\n"
            "2. 难度必须匹配上述难度等级\n"
            "3. 内容必须服务于上述学习目标\n"
            "4. 不要编造超出该知识点范围的内容\n"
        )

    def get_system_prompt(self) -> str:
        return (
            "你是一位资深的教育内容设计师，精通教学设计、习题编写和代码示例撰写。"
            "你能根据学生的学习风格和知识水平，生成难度适中、结构清晰的学习资源。\n"
            "重要规则：\n"
            "- 不要输出思考过程、分析步骤或'让我想想'之类的内心独白，直接输出最终生成的内容\n"
            "- 如果提供了知识图谱约束，你必须严格依据图谱生成资源，不能生成图谱外的内容\n"
            "- 难度和资源类型必须匹配图谱中的定义\n"
        )

    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        context:
        {
            "task": "generate_outline" | "generate_document" | "generate_questions"
                   | "generate_code_examples" | "generate_mindmap",
            "topic": "Python 递归",
            "difficulty": "intermediate",
            "cognitive_style": "visual",
            "profile": {...},
            "constraints": {"count": 5, "language": "Python"}
        }
        """
        self.status = "running"
        task = context.get("task", "generate_document")
        topic = context.get("topic", "")

        # 输入安全检查
        safety = SafetyGuard.check_input(topic)
        if not safety["safe"]:
            return {"status": "blocked", "reason": safety["message"]}

        try:
            if task == "generate_outline":
                result = await self._generate_outline(context)
            elif task == "generate_document":
                result = await self._generate_document(context)
            elif task == "generate_questions":
                result = await self._generate_questions(context)
            elif task == "generate_code_examples":
                result = await self._generate_code_examples(context)
            elif task == "generate_mindmap":
                result = await self._generate_mindmap(context)
            elif task == "match_resources":
                result = await self._match_resources(context)
            else:
                result = {"status": "failed", "error": f"Unknown task: {task}"}

            # 输出安全校验
            if result.get("status") == "success" and isinstance(result.get("content"), str):
                out_safety = SafetyGuard.check_output(result["content"])
                if not out_safety["safe"]:
                    result["status"] = "blocked"
                    result["reason"] = out_safety["message"]
                    result["content"] = "[内容已拦截] 生成结果包含敏感信息。"

            self.status = "completed"
            return result
        except Exception as e:
            self.status = "failed"
            self.logger.error(f"ResourceGeneratorAgent error: {e}")
            return {"status": "failed", "error": str(e)}

    async def _generate_outline(self, context: Dict[str, Any]) -> Dict[str, Any]:
        profile_snippet = self._build_profile_snippet(context)
        prompt = (
            f"请为主题《{context['topic']}》生成一份教学大纲。\n"
            f"难度：{context.get('difficulty', 'medium')}\n"
            f"学生画像参考：\n{profile_snippet}\n"
            "请贴合学生的知识水平和薄弱点来调整大纲的侧重点。\n"
            "返回 JSON：{\"outline\": [\"1. 引言\", \"2. ...\"]}"
        )
        prompt = SafetyGuard.sanitize_prompt(prompt)
        data = await self.llm.generate_json([
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": prompt},
        ], temperature=0.4)
        # 防幻觉校验
        schema_check = HallucinationGuard.verify_json_schema(data, ["outline"])
        if not schema_check["valid"]:
            self.logger.warning(f"Outline JSON schema check: {schema_check['message']}")
        return {"status": "success", "task": "outline", "content": data.get("outline", [])}

    async def _generate_document(self, context: Dict[str, Any]) -> Dict[str, Any]:
        style = context.get("cognitive_style", "visual")
        topic = context["topic"]
        profile_snippet = self._build_profile_snippet(context)

        # 知识图谱约束
        graph_constraint = self._build_resource_constraint_prompt(topic)

        prompt = (
            f"请为主题《{topic}》撰写一份面向{style}型学习者的学习文档。\n"
            f"学生画像参考：\n{profile_snippet}\n"
            "要求：结构清晰、有具体例子、适合该认知风格，重点讲解学生的薄弱知识点。"
        )
        if graph_constraint:
            prompt += graph_constraint

        prompt = SafetyGuard.sanitize_prompt(prompt)
        text = await self.llm.ainvoke([
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": prompt},
        ], temperature=0.5, max_tokens=4096)  # 增加 max_tokens 避免内容截断
        return {"status": "success", "task": "document", "content": text, "format": "markdown"}

    async def _generate_questions(self, context: Dict[str, Any]) -> Dict[str, Any]:
        count = context.get("constraints", {}).get("count", 5)
        topic = context["topic"]
        subject = context.get("subject") or context.get("constraints", {}).get("subject", "C语言")
        profile_snippet = self._build_profile_snippet(context)

        # 知识图谱约束
        graph_constraint = self._build_resource_constraint_prompt(topic)

        prompt = (
            f"请为{subject}课程主题《{topic}》生成 {count} 道练习题。\n"
            f"学生画像参考：\n{profile_snippet}\n"
            "请针对学生的薄弱知识点多出题，题目难度匹配学生的知识水平。\n"
            f"重要：所有题目必须与{subject}课程内容相关，不要出其他学科题目。\n"
            "要求：题目准确无歧义，代码示例完整可运行，填空题不要求填写关键字而是直接填写语法或表达式。\n"
            "包含选择题、填空题或简答题，并提供答案与解析。\n"
            "返回 JSON：{\"questions\": [{\"type\": \"choice\", \"question\": \"...\", \"answer\": \"...\", \"explanation\": \"...\"}]}"
        )
        if graph_constraint:
            prompt += graph_constraint

        prompt = SafetyGuard.sanitize_prompt(prompt)
        data = await self.llm.generate_json([
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": prompt},
        ], temperature=0.5)
        return {"status": "success", "task": "questions", "content": data.get("questions", [])}

    async def _generate_code_examples(self, context: Dict[str, Any]) -> Dict[str, Any]:
        language = context.get("constraints", {}).get("language", "Python")
        topic = context["topic"]

        # 知识图谱约束
        graph_constraint = self._build_resource_constraint_prompt(topic)

        prompt = (
            f"请为主题《{topic}》提供 2-3 个 {language} 代码示例。\n"
            "每个示例需包含：问题描述、完整可运行代码、逐行注释、运行结果。"
        )
        if graph_constraint:
            prompt += graph_constraint

        prompt = SafetyGuard.sanitize_prompt(prompt)
        text = await self.llm.ainvoke([
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": prompt},
        ], temperature=0.4, max_tokens=4096)  # 增加 max_tokens 避免内容截断
        # 代码语法校验
        code_check = HallucinationGuard.verify_code_output(text, language)
        return {"status": "success", "task": "code_examples", "content": text, "syntax_check": code_check}

    async def _generate_mindmap(self, context: Dict[str, Any]) -> Dict[str, Any]:
        topic = context["topic"]

        # 知识图谱约束
        graph_constraint = self._build_resource_constraint_prompt(topic)

        prompt = (
            f"请为主题《{topic}》生成思维导图的大纲。\n"
            "只输出缩进格式文本，不要输出JSON，不要有任何额外说明。例如：\n"
            "# 主题\n"
            "## 分支1\n"
            "### 子项1\n"
            "### 子项2\n"
            "## 分支2\n"
            "### 子项3\n"
        )
        if graph_constraint:
            prompt += graph_constraint

        prompt = SafetyGuard.sanitize_prompt(prompt)
        text = await self.llm.ainvoke([
            {"role": "system", "content": "你只输出 markmap 兼容的缩进格式文本，不要输出JSON，不要输出任何说明。"},
            {"role": "user", "content": prompt},
        ], temperature=0.3, max_tokens=4096)
        # 清理可能的 JSON 包裹
        cleaned = text.strip().strip("```").strip()
        if cleaned.startswith("{"):
            cleaned = f"# {topic}\n"
        return {"status": "success", "task": "mindmap", "content": cleaned}

    async def _match_resources(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """根据路径节点匹配资源（用于 path_planner 后续步骤）"""
        path_nodes = context.get("path_nodes", [])
        profile = context.get("profile", {})
        prompt = (
            f"请为以下学习路径节点推荐匹配的学习资源类型（视频/文档/练习/代码示例）。\n"
            f"路径：{path_nodes}\n"
            f"学生画像：{profile}\n"
            "返回 JSON：{\"matches\": [{\"node\": \"...\", \"resource_types\": [\"video\", \"doc\"]}]}"
        )
        prompt = SafetyGuard.sanitize_prompt(prompt)
        data = await self.llm.generate_json([
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": prompt},
        ], temperature=0.5)
        return {"status": "success", "task": "match_resources", "content": data.get("matches", [])}
