"""
系统监控API
- 接口性能监控
- 模型调用监控
- 服务健康监控
- 异常告警
- 功能使用频率统计（试点数据分析）
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session
from sqlalchemy import func, case
from ..models.database import get_db
from ..models.monitor import ApiMonitorModel, LlmCallModel, SystemHealthModel
from ..models.user import UserModel
from .auth import require_auth

router = APIRouter()


# ---------- 功能使用频率统计 ----------

# endpoint 前缀 -> 功能名（按顺序匹配，先命中优先）
FEATURE_PATTERNS: List[tuple] = [
    ("/tutor", "智能辅导"),
    ("/resource", "学习资源"),
    ("/learning-path", "学习路径"),
    ("/daily-quiz", "每日练习"),
    ("/kb/", "知识库"),
    ("/knowledge-base", "知识库"),
    ("/knowledge-graph", "知识图谱"),
    ("/knowledge/", "知识点"),
    ("/error-catcher", "错误诊断"),
    ("/misconception-tracer", "思维溯源"),
    ("/circuit-analysis", "电路AI分析"),
    ("/circuit", "电路仿真"),
    ("/gamification-tree", "知识树"),
    ("/gamification-challenge", "学习挑战"),
    ("/gamification", "游戏化"),
    ("/ppt", "PPT生成"),
    ("/image", "文生图"),
    ("/ocr", "OCR识别"),
    ("/profile", "学习画像"),
    ("/dashboard", "学习仪表盘"),
    ("/learning-data", "学习记录"),
    ("/trend", "趋势分析"),
    ("/log-reflection", "反思日志"),
    ("/project-decomposer", "项目拆解"),
    ("/role-matcher", "角色匹配"),
    ("/collaboration-supervisor", "协作督导"),
    ("/result-evaluator", "成果评估"),
    ("/agent-flow", "Agent工作流"),
    ("/stm32", "STM32内容"),
    ("/assignment", "作业管理"),
    ("/teaching-assist", "教学辅助"),
    ("/teacher", "教师端"),
    ("/auth", "认证"),
    ("/onboarding", "新人引导"),
    ("/path-adjustment", "路径调整"),
    ("/favorites", "收藏"),
    ("/matching", "资源匹配"),
    ("/monitoring", "系统监控"),
]


def _map_feature(endpoint: str) -> str:
    for prefix, name in FEATURE_PATTERNS:
        if endpoint.startswith(prefix):
            return name
    return "其他"


@router.get("/feature-usage")
async def get_feature_usage(
    days: int = Query(7, ge=1, le=90),
    student_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current: str = Depends(require_auth),
):
    """功能使用频率统计（试点数据分析核心接口）

    - 不传 student_id：返回全班功能使用汇总（需教师权限）
    - 传 student_id：返回该学生的功能使用统计（教师可查任意学生；学生只能查自己）
    """
    # 权限：学生只能看自己的数据；全班汇总或查看其他学生需教师权限
    if not student_id or student_id != current:
        user = db.query(UserModel).filter(UserModel.student_id == current).first()
        if not user or user.role not in ("teacher", "admin"):
            raise HTTPException(status_code=403, detail="教师权限不足")

    since = datetime.now(timezone.utc) - timedelta(days=days)
    q = db.query(
        ApiMonitorModel.endpoint,
        func.count().label("count"),
        func.avg(ApiMonitorModel.duration_ms).label("avg_duration"),
        func.sum(case((ApiMonitorModel.status_code >= 400, 1), else_=0)).label("errors"),
    ).filter(
        ApiMonitorModel.created_at >= since,
        ApiMonitorModel.student_id.isnot(None),
    )
    if student_id:
        q = q.filter(ApiMonitorModel.student_id == student_id)
    rows = q.group_by(ApiMonitorModel.endpoint).all()

    # 按功能聚合
    feature_map: Dict[str, dict] = {}
    total_requests = 0
    for r in rows:
        feature = _map_feature(r.endpoint)
        entry = feature_map.setdefault(feature, {"feature": feature, "count": 0, "avg_duration_ms": 0.0, "errors": 0, "endpoints": []})
        entry["count"] += r.count
        entry["avg_duration_ms"] = round((entry["avg_duration_ms"] * (entry["count"] - r.count) + float(r.avg_duration or 0) * r.count) / entry["count"], 2)
        entry["errors"] += r.errors or 0
        entry["endpoints"].append(r.endpoint)
        total_requests += r.count

    features = sorted(feature_map.values(), key=lambda x: -x["count"])
    return {
        "status": "success",
        "days": days,
        "student_id": student_id,
        "total_requests": total_requests,
        "data": features,
    }


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
