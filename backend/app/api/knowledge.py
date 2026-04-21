"""
知识点管理API
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import or_
from ..models.database import get_db
from ..models.knowledge import KnowledgePointModel

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
async def create_kp(request: KnowledgePointCreate, db: Session = Depends(get_db)):
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
    """搜索知识点（按名称、学科、标签模糊匹配）"""
    keyword = f"%{q}%"
    kps = (
        db.query(KnowledgePointModel)
        .filter(
            or_(
                KnowledgePointModel.name.ilike(keyword),
                KnowledgePointModel.subject.ilike(keyword),
                KnowledgePointModel.description.ilike(keyword),
            )
        )
        .limit(limit)
        .all()
    )
    # 再按标签过滤（JSON 字段不同数据库语法不同，这里简化：查出全部再过滤）
    all_kps = (
        db.query(KnowledgePointModel)
        .filter(
            or_(
                KnowledgePointModel.name.ilike(keyword),
                KnowledgePointModel.subject.ilike(keyword),
                KnowledgePointModel.description.ilike(keyword),
            )
        )
        .all()
    )
    tag_kps = [k for k in all_kps if q.lower() in " ".join(k.tags or []).lower()]
    combined = {k.kp_id: k for k in list(all_kps) + tag_kps}
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
