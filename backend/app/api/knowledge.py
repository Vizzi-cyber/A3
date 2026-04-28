"""
知识点管理API
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_
from ..models.database import get_db
from ..models.knowledge import KnowledgePointModel
from .auth import require_auth

router = APIRouter()


class KnowledgePointCreate(BaseModel):
    kp_id: str
    name: str
    subject: str
    difficulty: float = 0.5
    prerequisites: List[str] = []
    description: Optional[str] = None
    tags: List[str] = []


@router.post("/create")
async def create_kp(request: KnowledgePointCreate, db: Session = Depends(get_db), _current: str = Depends(require_auth)):
    """创建知识点"""
    existing = db.query(KnowledgePointModel).filter(KnowledgePointModel.kp_id == request.kp_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="kp_id already exists")
    kp = KnowledgePointModel(
        kp_id=request.kp_id,
        name=request.name,
        subject=request.subject,
        difficulty=request.difficulty,
        prerequisites=request.prerequisites,
        description=request.description,
        tags=request.tags,
    )
    db.add(kp)
    db.commit()
    db.refresh(kp)
    return {"status": "success", "data": {"kp_id": kp.kp_id, "name": kp.name}}


@router.get("/list")
async def list_kps(subject: Optional[str] = None, db: Session = Depends(get_db)):
    """列出知识点"""
    query = db.query(KnowledgePointModel)
    if subject:
        query = query.filter(KnowledgePointModel.subject == subject)
    kps = query.all()
    return {
        "status": "success",
        "data": [
            {
                "kp_id": k.kp_id,
                "name": k.name,
                "subject": k.subject,
                "difficulty": k.difficulty,
                "prerequisites": k.prerequisites,
                "tags": k.tags,
            }
            for k in kps
        ],
    }


@router.get("/search")
async def search_kps(q: str, limit: int = 10, db: Session = Depends(get_db)):
    """搜索知识点（按名称、学科、描述、标签模糊匹配）—— 单次查询避免重复加载"""
    keyword = f"%{q}%"
    # 放宽 limit 给标签过滤留余量，避免二次查询
    kps = (
        db.query(KnowledgePointModel)
        .filter(
            or_(
                KnowledgePointModel.name.ilike(keyword),
                KnowledgePointModel.subject.ilike(keyword),
                KnowledgePointModel.description.ilike(keyword),
            )
        )
        .limit(limit * 3)
        .all()
    )
    # 补充标签匹配（同一结果集内过滤，无需再次查询数据库）
    tag_kps = [k for k in kps if q.lower() in " ".join(k.tags or []).lower()]
    combined = {k.kp_id: k for k in list(kps) + tag_kps}
    result = list(combined.values())[:limit]
    return {
        "status": "success",
        "data": [
            {
                "kp_id": k.kp_id,
                "name": k.name,
                "subject": k.subject,
                "difficulty": k.difficulty,
                "prerequisites": k.prerequisites,
                "tags": k.tags,
            }
            for k in result
        ],
    }


@router.get("/{kp_id}")
async def get_kp(kp_id: str, db: Session = Depends(get_db)):
    """获取知识点详情"""
    kp = db.query(KnowledgePointModel).filter(KnowledgePointModel.kp_id == kp_id).first()
    if not kp:
        raise HTTPException(status_code=404, detail="Knowledge point not found")
    return {
        "status": "success",
        "data": {
            "kp_id": kp.kp_id,
            "name": kp.name,
            "subject": kp.subject,
            "difficulty": kp.difficulty,
            "prerequisites": kp.prerequisites,
            "description": kp.description,
            "tags": kp.tags,
        },
    }
