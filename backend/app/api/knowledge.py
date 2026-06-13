"""
知识点管理API
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_
from ..models.database import get_db
from ..models.knowledge import KnowledgePointModel
from .auth import require_auth, get_current_student_id

router = APIRouter()


class KnowledgePointCreate(BaseModel):
    kp_id: str = Field(..., max_length=64)
    name: str = Field(..., max_length=256)
    subject: str = Field(..., max_length=64)
    difficulty: float = Field(0.5, ge=0.0, le=1.0)
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
async def list_kps(
    subject: Optional[str] = None,
    limit: int = Query(200, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    _current: str = Depends(get_current_student_id),
):
    """列出知识点（分页）—— subject 支持课程级别（C语言、电路分析）或章节级别"""
    query = db.query(KnowledgePointModel)
    if subject:
        # 课程级别筛选：C语言、电路分析等
        COURSE_NAMES = {"C语言", "电路分析"}
        if subject in COURSE_NAMES:
            query = query.filter(KnowledgePointModel.course == subject)
        else:
            query = query.filter(KnowledgePointModel.subject == subject)
    total = query.count()
    kps = query.order_by(KnowledgePointModel.created_at.asc()).offset(offset).limit(limit).all()
    return {
        "status": "success",
        "total": total,
        "offset": offset,
        "limit": limit,
        "data": [
            {
                "kp_id": k.kp_id,
                "name": k.name,
                "subject": k.subject,
                "course": k.course,
                "difficulty": k.difficulty,
                "prerequisites": k.prerequisites,
                "tags": k.tags,
                "document": k.document,
                "code_example": k.code_example,
                "questions": k.questions,
                "mindmap": k.mindmap,
            }
            for k in kps
        ],
    }


@router.get("/search")
async def search_kps(q: str = Query(..., min_length=1, max_length=200), limit: int = Query(10, ge=1, le=100), db: Session = Depends(get_db), _current: str = Depends(get_current_student_id)):
    """搜索知识点（按名称、学科、描述、标签模糊匹配）—— 单次查询避免重复加载"""
    # 转义 LIKE 通配符防止注入
    escaped = q.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    keyword = f"%{escaped}%"
    # 放宽 limit 给标签过滤留余量，避免二次查询
    kps = (
        db.query(KnowledgePointModel)
        .filter(
            or_(
                KnowledgePointModel.name.ilike(keyword, escape="\\"),
                KnowledgePointModel.subject.ilike(keyword, escape="\\"),
                KnowledgePointModel.description.ilike(keyword, escape="\\"),
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
async def get_kp(kp_id: str, db: Session = Depends(get_db), _current: str = Depends(require_auth)):
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
            "document": kp.document,
            "code_example": kp.code_example,
            "questions": kp.questions,
            "mindmap": kp.mindmap,
        },
    }
