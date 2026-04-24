"""
收藏夹/书签 API
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

from sqlalchemy.orm import Session
from ..models.database import get_db
from ..models.favorites import FavoriteModel

router = APIRouter()


class FavoriteItem(BaseModel):
    title: str
    resource_type: str
    url: Optional[str] = None
    meta: Dict[str, Any] = {}


class AddFavoriteRequest(BaseModel):
    student_id: str
    title: str
    resource_type: str
    url: Optional[str] = None
    meta: Dict[str, Any] = {}


@router.get("/{student_id}")
async def get_favorites(student_id: str, db: Session = Depends(get_db)):
    """获取学生收藏列表"""
    items = (
        db.query(FavoriteModel)
        .filter(FavoriteModel.student_id == student_id)
        .order_by(FavoriteModel.created_at.desc())
        .limit(200)
        .all()
    )
    return {
        "status": "success",
        "data": [
            {
                "id": item.id,
                "title": item.title,
                "resource_type": item.resource_type,
                "url": item.url,
                "meta": item.meta,
                "created_at": item.created_at.isoformat() if item.created_at else None,
            }
            for item in items
        ],
    }


@router.post("/{student_id}")
async def add_favorite(student_id: str, request: FavoriteItem, db: Session = Depends(get_db)):
    """添加收藏"""
    import uuid
    fav = FavoriteModel(
        id=f"fav_{uuid.uuid4().hex[:12]}",
        student_id=student_id,
        title=request.title,
        resource_type=request.resource_type,
        url=request.url,
        meta=request.meta,
    )
    db.add(fav)
    db.commit()
    db.refresh(fav)
    return {"status": "success", "id": fav.id}


@router.delete("/{student_id}/{favorite_id}")
async def remove_favorite(student_id: str, favorite_id: str, db: Session = Depends(get_db)):
    """删除收藏"""
    item = db.query(FavoriteModel).filter(
        FavoriteModel.student_id == student_id,
        FavoriteModel.id == favorite_id,
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Favorite not found")
    db.delete(item)
    db.commit()
    return {"status": "success", "message": "Removed"}
