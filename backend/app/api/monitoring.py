"""
系统监控API
- 接口性能监控
- 模型调用监控
- 服务健康监控
- 异常告警
"""
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session
from sqlalchemy import func, case
from ..models.database import get_db
from ..models.monitor import ApiMonitorModel, LlmCallModel, SystemHealthModel
from .auth import require_auth

router = APIRouter()


# ---------- 接口性能监控 ----------

@router.get("/api-stats")
async def get_api_stats(minutes: int = Query(60, ge=1, le=1440), db: Session = Depends(get_db), _current: str = Depends(require_auth)):
    """接口统计（使用 SQL 聚合避免全量加载）"""
    since = datetime.now(timezone.utc) - timedelta(minutes=minutes)
    rows = db.query(
        ApiMonitorModel.method,
        ApiMonitorModel.endpoint,
        func.count().label("count"),
        func.avg(ApiMonitorModel.duration_ms).label("avg_duration"),
        func.max(ApiMonitorModel.duration_ms).label("max_duration"),
        func.sum(case((ApiMonitorModel.status_code >= 400, 1), else_=0)).label("errors"),
    ).filter(
        ApiMonitorModel.created_at >= since,
    ).group_by(
        ApiMonitorModel.method, ApiMonitorModel.endpoint,
    ).all()

    result = []
    for r in rows:
        result.append({
            "endpoint": f"{r.method} {r.endpoint}",
            "count": r.count,
            "avg_duration": round(float(r.avg_duration or 0), 2),
            "max_duration": round(float(r.max_duration or 0), 2),
            "errors": r.errors or 0,
        })

    return {"status": "success", "period_minutes": minutes, "data": result}


# ---------- 模型调用监控 ----------

@router.get("/llm-stats")
async def get_llm_stats(minutes: int = Query(60, ge=1, le=1440), db: Session = Depends(get_db), _current: str = Depends(require_auth)):
    """大模型调用统计（使用 SQL 聚合）"""
    since = datetime.now(timezone.utc) - timedelta(minutes=minutes)
    rows = db.query(
        LlmCallModel.provider,
        func.count().label("count"),
        func.avg(LlmCallModel.duration_ms).label("avg_duration"),
        func.sum(LlmCallModel.prompt_tokens + LlmCallModel.completion_tokens).label("total_tokens"),
        func.sum(case((LlmCallModel.success == True, 1), else_=0)).label("success"),
        func.sum(case((LlmCallModel.success == False, 1), else_=0)).label("fail"),
    ).filter(
        LlmCallModel.created_at >= since,
    ).group_by(
        LlmCallModel.provider,
    ).all()

    result = []
    for r in rows:
        result.append({
            "provider": r.provider,
            "count": r.count,
            "avg_duration": round(float(r.avg_duration or 0), 2),
            "total_tokens": r.total_tokens or 0,
            "success": r.success or 0,
            "fail": r.fail or 0,
        })

    return {"status": "success", "period_minutes": minutes, "data": result}


# ---------- 服务健康 ----------

@router.get("/health")
async def get_system_health(db: Session = Depends(get_db), _current: str = Depends(require_auth)):
    """系统健康状态"""
    latest = db.query(SystemHealthModel).order_by(SystemHealthModel.recorded_at.desc()).first()
    if not latest:
        return {"status": "success", "data": {"message": "No health data recorded yet"}}
    return {
        "status": "success",
        "data": {
            "cpu_percent": latest.cpu_percent,
            "memory_percent": latest.memory_percent,
            "disk_percent": latest.disk_percent,
            "active_connections": latest.active_connections,
            "queue_size": latest.queue_size,
            "recorded_at": latest.recorded_at.isoformat() if latest.recorded_at else None,
        },
    }


class RecordHealthRequest(BaseModel):
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    active_connections: int = 0
    queue_size: int = 0


@router.post("/health/record")
async def record_system_health(request: RecordHealthRequest, db: Session = Depends(get_db), _current: str = Depends(require_auth)):
    """记录系统健康数据"""
    health = SystemHealthModel(
        cpu_percent=request.cpu_percent,
        memory_percent=request.memory_percent,
        disk_percent=request.disk_percent,
        active_connections=request.active_connections,
        queue_size=request.queue_size,
    )
    db.add(health)
    db.commit()
    return {"status": "success"}
