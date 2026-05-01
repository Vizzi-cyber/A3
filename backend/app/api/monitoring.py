"""
系统监控API
- 接口性能监控
- 模型调用监控
- 服务健康监控
- 异常告警
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models.database import get_db
from ..models.monitor import ApiMonitorModel, LlmCallModel, SystemHealthModel
from .auth import require_auth

router = APIRouter()


# ---------- 接口性能监控 ----------

@router.get("/api-stats")
async def get_api_stats(minutes: int = 60, db: Session = Depends(get_db), _current: str = Depends(require_auth)):
    """接口统计"""
    since = datetime.now(timezone.utc) - timedelta(minutes=minutes)
    rows = db.query(ApiMonitorModel).filter(ApiMonitorModel.created_at >= since).all()

    from collections import defaultdict
    stats = defaultdict(lambda: {"count": 0, "avg_duration": 0.0, "errors": 0, "max_duration": 0.0})
    for r in rows:
        key = f"{r.method} {r.endpoint}"
        stats[key]["count"] += 1
        stats[key]["avg_duration"] += r.duration_ms
        stats[key]["max_duration"] = max(stats[key]["max_duration"], r.duration_ms)
        if r.status_code >= 400:
            stats[key]["errors"] += 1

    result = []
    for key, s in stats.items():
        s["avg_duration"] = round(s["avg_duration"] / s["count"], 2) if s["count"] > 0 else 0.0
        s["endpoint"] = key
        result.append(s)

    return {"status": "success", "period_minutes": minutes, "data": result}


# ---------- 模型调用监控 ----------

@router.get("/llm-stats")
async def get_llm_stats(minutes: int = 60, db: Session = Depends(get_db), _current: str = Depends(require_auth)):
    """大模型调用统计"""
    since = datetime.now(timezone.utc) - timedelta(minutes=minutes)
    rows = db.query(LlmCallModel).filter(LlmCallModel.created_at >= since).all()

    from collections import defaultdict
    stats = defaultdict(lambda: {"count": 0, "success": 0, "fail": 0, "avg_duration": 0.0, "total_tokens": 0})
    for r in rows:
        key = r.provider
        stats[key]["count"] += 1
        stats[key]["avg_duration"] += r.duration_ms
        stats[key]["total_tokens"] += r.prompt_tokens + r.completion_tokens
        if r.success:
            stats[key]["success"] += 1
        else:
            stats[key]["fail"] += 1

    result = []
    for key, s in stats.items():
        s["avg_duration"] = round(s["avg_duration"] / s["count"], 2) if s["count"] > 0 else 0.0
        s["provider"] = key
        result.append(s)

    return {"status": "success", "period_minutes": minutes, "data": result}


# ---------- 服务健康 ----------

@router.get("/health")
async def get_system_health(db: Session = Depends(get_db)):
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
