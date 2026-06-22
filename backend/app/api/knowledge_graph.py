"""
知识图谱 API
提供图谱构建、查询、约束注入等功能
"""
import asyncio
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from ..models.database import get_db
from ..models.knowledge import KnowledgePointModel, KnowledgeGraphModel
from ..agents.knowledge_graph_builder import KnowledgeGraphBuilderAgent
from ..core.logger import setup_logger
from .auth import require_auth

logger = setup_logger()
router = APIRouter()

_builder_agent = KnowledgeGraphBuilderAgent()


class BuildGraphRequest(BaseModel):
    """构建图谱请求"""
    subject: str = Field("C语言", max_length=64)
    graph_name: str = Field("C语言知识图谱", max_length=256)


class GraphNodeResponse(BaseModel):
    """图谱节点响应"""
    id: str
    name: str
    difficulty: int
    prerequisite: List[str]
    question_types: List[str]
    resource_types: List[str]
    learning_objective: str


@router.post("/build")
async def build_knowledge_graph(
    request: BuildGraphRequest,
    db: Session = Depends(get_db),
    _current: str = Depends(require_auth),
):
    """从数据库知识点构建知识图谱（调用 LLM）"""
    # 查询该学科的所有知识点
    kps = (
        db.query(KnowledgePointModel)
        .filter(KnowledgePointModel.subject == request.subject)
        .all()
    )
    if not kps:
        # 如果按 subject 过滤没有结果，尝试获取全部
        kps = db.query(KnowledgePointModel).all()
        if not kps:
            raise HTTPException(status_code=404, detail="No knowledge points found in database")

    kp_list = [
        {
            "kp_id": k.kp_id,
            "name": k.name,
            "difficulty": k.difficulty or 0.5,
            "prerequisites": k.prerequisites or [],
            "tags": k.tags or [],
            "description": k.description or "",
        }
        for k in kps
    ]

    try:
        result = await asyncio.wait_for(
            _builder_agent.process({
                "task": "build_graph",
                "knowledge_points": kp_list,
                "subject": request.subject,
                "graph_name": request.graph_name,
            }),
            timeout=120.0,
        )
    except asyncio.TimeoutError:
        logger.error("Knowledge graph build timed out")
        raise HTTPException(status_code=504, detail="Graph build timed out")
    except Exception as e:
        logger.error(f"Knowledge graph build failed: {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")

    if result.get("status") != "success":
        raise HTTPException(status_code=500, detail=result.get("error", "Build failed"))

    graph_data = result["graph_data"]

    # 存入数据库（更新或插入）
    kg_id = f"kg_{request.subject}"
    existing = db.query(KnowledgeGraphModel).filter(KnowledgeGraphModel.kg_id == kg_id).first()
    if existing:
        existing.graph_data = graph_data
        existing.name = request.graph_name
        existing.version = (existing.version or 0) + 1
    else:
        kg = KnowledgeGraphModel(
            kg_id=kg_id,
            name=request.graph_name,
            subject=request.subject,
            graph_data=graph_data,
            version=1,
        )
        db.add(kg)
    db.commit()

    return {
        "status": "success",
        "data": {
            "kg_id": kg_id,
            "name": request.graph_name,
            "node_count": result["node_count"],
            "edge_count": result["edge_count"],
            "graph_data": graph_data,
        },
    }


@router.get("/")
async def get_knowledge_graph(
    subject: Optional[str] = None,
    db: Session = Depends(get_db),
    _current: str = Depends(require_auth),
):
    """获取知识图谱"""
    query = db.query(KnowledgeGraphModel)
    if subject:
        query = query.filter(KnowledgeGraphModel.subject == subject)
    kg = query.order_by(KnowledgeGraphModel.version.desc()).first()
    if not kg:
        raise HTTPException(status_code=404, detail="Knowledge graph not found. Call /build first.")

    return {
        "status": "success",
        "data": {
            "kg_id": kg.kg_id,
            "name": kg.name,
            "subject": kg.subject,
            "version": kg.version,
            "graph_data": kg.graph_data,
        },
    }


@router.get("/node/{kp_id}")
async def get_graph_node(
    kp_id: str,
    db: Session = Depends(get_db),
    _current: str = Depends(require_auth),
):
    """获取单个节点及其依赖关系"""
    kg = db.query(KnowledgeGraphModel).order_by(KnowledgeGraphModel.version.desc()).first()
    if not kg:
        raise HTTPException(status_code=404, detail="Knowledge graph not found")

    graph = kg.graph_data or {}
    nodes = {n["id"]: n for n in graph.get("nodes", [])}
    edges = graph.get("edges", [])

    if kp_id not in nodes:
        raise HTTPException(status_code=404, detail=f"Node {kp_id} not found in graph")

    node = nodes[kp_id]
    # 找出直接前置和直接后继
    predecessors = [e["from"] for e in edges if e["to"] == kp_id]
    successors = [e["to"] for e in edges if e["from"] == kp_id]

    return {
        "status": "success",
        "data": {
            "node": node,
            "predecessors": [nodes.get(p, {"id": p, "name": "unknown"}) for p in predecessors],
            "successors": [nodes.get(s, {"id": s, "name": "unknown"}) for s in successors],
        },
    }


@router.get("/constraint-prompt")
async def get_constraint_prompt(
    subject: Optional[str] = None,
    db: Session = Depends(get_db),
    _current: str = Depends(require_auth),
):
    """获取用于约束 LLM 的知识图谱 prompt 片段"""
    query = db.query(KnowledgeGraphModel)
    if subject:
        query = query.filter(KnowledgeGraphModel.subject == subject)
    kg = query.order_by(KnowledgeGraphModel.version.desc()).first()
    if not kg:
        raise HTTPException(status_code=404, detail="Knowledge graph not found")

    graph = kg.graph_data or {}
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])

    # 构建紧凑的图谱摘要（用于注入 prompt）
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

    path_constraint_prompt = (
        "你必须严格依据以下知识图谱结构生成学习路径，不能生成图谱外知识点。\n"
        f"知识图谱节点：{node_summary}\n"
        f"依赖关系：{edges}\n"
        "要求：\n"
        "1. 按照前置依赖顺序生成路径\n"
        "2. 从易到难\n"
        "3. 每一步必须对应图谱中的知识点ID\n"
        "4. 不能编造知识\n"
    )

    resource_constraint_prompt = (
        "依据知识图谱生成资源，必须遵守：\n"
        "1. 只能使用图谱内知识点，不能扩展\n"
        "2. 资源类型必须从图谱中选择\n"
        "3. 难度必须匹配图谱中的 difficulty\n"
        "4. 内容必须服务于图谱中的 learning_objective\n"
    )

    return {
        "status": "success",
        "data": {
            "graph_summary": {"node_count": len(nodes), "edge_count": len(edges)},
            "path_constraint_prompt": path_constraint_prompt,
            "resource_constraint_prompt": resource_constraint_prompt,
        },
    }
