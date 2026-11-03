"""
路径调整日志 API
"""
from fastapi import APIRouter, Depends
from typing import Optional
from sqlalchemy.orm import Session

from ..models.database import get_db
from ..models.path_adjustment_log import PathAdjustmentLogModel
from .auth import require_auth

router = APIRouter()


@router.get("/{student_id}/logs")
async def get_adjustment_logs(
    student_id: str,
    limit: int = 20,
    db: Session = Depends(get_db),
    _current: str = Depends(require_auth),
):
    """获取路径调整历史"""
    if student_id != _current:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Cannot view other student's logs")

    logs = (
        db.query(PathAdjustmentLogModel)
        .filter(PathAdjustmentLogModel.student_id == student_id)
        .order_by(PathAdjustmentLogModel.created_at.desc())
        .limit(limit)
        .all()
    )

    return {
        "status": "success",
        "data": [
            {
                "id": log.id,
                "trigger_type": log.trigger_type,
                "trigger_source": log.trigger_source,
                "reason": log.reason,
                "confidence": log.confidence,
                "old_path_snapshot": log.old_path_snapshot,
                "new_path_snapshot": log.new_path_snapshot,
                "created_at": log.created_at.isoformat() if log.created_at else None,
            }
            for log in logs
        ],
    }
