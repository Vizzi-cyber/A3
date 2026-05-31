"""
知识图谱构建智能体
从数据库知识点出发，调用 LLM 解析为结构化知识图谱
图谱用于约束路径规划和资源生成，防止幻觉
"""
from typing import Any, Dict, List, Optional

from .base import BaseAgent
from ..services.llm_factory import BaseLLM, LLMFactory
from ..core.safety import SafetyGuard


# 每批发送给 LLM 的知识点数量（避免 token 超限）
BATCH_SIZE = 15


class KnowledgeGraphBuilderAgent(BaseAgent):
    """知识图谱构建智能体"""

    def __init__(self, llm: Optional[BaseLLM] = None):
        super().__init__(
            agent_id="kg_builder",
            agent_name="知识图谱构建师",
            description="从课程知识点中构建结构化知识图谱，用于约束学习路径和资源生成"
        )
        self.llm = llm or LLMFactory.get_default_llm()

    def get_system_prompt(self) -> str:
        return (
            "你是知识图谱构建专家。你的任务是将课程文档解析成严格的JSON格式知识图谱。\n"
            "输出必须是标准JSON，不能有多余文字、不能有注释、不能有省略。\n"
            "每个知识点必须包含：id, name, difficulty(1-5), prerequisite(前置依赖ID列表), "
            "question_types(关联题型列表), resource_types(推荐资源类型列表), learning_objective(学习目标)。"
        )

    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        context:
        {
            "task": "build_graph",
            "knowledge_points": [{"kp_id": "...", "name": "...", "document": "...", ...}],
            "subject": "C语言",
            "graph_name": "C语言知识图谱"
        }
        """
        self.status = "running"
        task = context.get("task", "build_graph")

        try:
            if task == "build_graph":
                result = await self._build_graph(context)
            else:
                result = {"status": "failed", "error": f"Unknown task: {task}"}
            self.status = "completed"
            return result
        except Exception as e:
            self.status = "failed"
            self.logger.error(f"KnowledgeGraphBuilderAgent error: {e}")
            return {"status": "failed", "error": str(e)}

    async def _build_graph(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """分批调用 LLM 构建知识图谱"""
        kps = context.get("knowledge_points", [])
        if not kps:
            return {"status": "failed", "error": "No knowledge points provided"}

        subject = context.get("subject", "未知学科")
        graph_name = context.get("graph_name", f"{subject}知识图谱")

        # 分批处理
        all_nodes = []
        all_edges = []
        for i in range(0, len(kps), BATCH_SIZE):
            batch = kps[i:i + BATCH_SIZE]
            self.logger.info(f"Processing batch {i // BATCH_SIZE + 1}: {len(batch)} knowledge points")
            batch_result = await self._process_batch(batch, subject)
            if batch_result.get("nodes"):
                all_nodes.extend(batch_result["nodes"])
            if batch_result.get("edges"):
                all_edges.extend(batch_result["edges"])

        # 去重
        seen_ids = set()
        unique_nodes = []
        for node in all_nodes:
            if node["id"] not in seen_ids:
                seen_ids.add(node["id"])
                unique_nodes.append(node)

        seen_edges = set()
        unique_edges = []
        for edge in all_edges:
            key = (edge["from"], edge["to"])
            if key not in seen_edges:
                seen_edges.add(key)
                unique_edges.append(edge)

        graph_data = {
            "nodes": unique_nodes,
            "edges": unique_edges,
        }

        return {
            "status": "success",
            "graph_name": graph_name,
            "subject": subject,
            "graph_data": graph_data,
            "node_count": len(unique_nodes),
            "edge_count": len(unique_edges),
        }

    async def _process_batch(self, kps: List[Dict], subject: str) -> Dict[str, Any]:
        """处理一批知识点，调用 LLM 解析为图谱节点和边"""
        # 构建知识点摘要（只发名称和标签，不发完整文档避免 token 超限）
        kp_summaries = []
        for kp in kps:
            summary = {
                "kp_id": kp["kp_id"],
                "name": kp["name"],
                "difficulty": kp.get("difficulty", 0.5),
                "prerequisites": kp.get("prerequisites", []),
                "tags": kp.get("tags", []),
                "description": (kp.get("description") or "")[:200],
            }
            kp_summaries.append(summary)

        prompt = (
            f"请将以下 {subject} 知识点解析为知识图谱的节点和边。\n\n"
            f"知识点列表：\n{kp_summaries}\n\n"
            "要求：\n"
            "1. 每个知识点对应一个节点\n"
            "2. difficulty 从 1-5（1最简单，5最难），根据知识点内容判断\n"
            "3. prerequisite 是前置依赖知识点ID列表，必须引用上面列表中的 kp_id\n"
            "4. question_types 是该知识点适合的题型，从以下选择："
            '["选择题","判断题","填空题","编程题","简答题","分析题"]\n'
            "5. resource_types 是推荐的学习资源类型，从以下选择："
            '["文档","视频","思维导图","代码示例","练习题库","实操案例"]\n'
            "6. learning_objective 是该知识点的学习目标，一句话描述\n"
            "7. edges 列出所有前置依赖关系\n\n"
            '返回严格JSON格式：\n'
            '{"nodes": [{"id": "kp_c01", "name": "...", "difficulty": 1, '
            '"prerequisite": [], "question_types": ["..."], "resource_types": ["..."], '
            '"learning_objective": "..."}], '
            '"edges": [{"from": "kp_c01", "to": "kp_c02", "type": "prerequisite"}]}'
        )

        prompt = SafetyGuard.sanitize_prompt(prompt)
        data = await self.llm.generate_json([
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": prompt},
        ], temperature=0.3, max_tokens=4096)

        return {
            "nodes": data.get("nodes", []),
            "edges": data.get("edges", []),
        }
