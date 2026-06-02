"""
协作督导API
提供团队协作监控、阻塞检测、冲突解决等功能
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from ..agents import CollaborationSupervisionAgent
from ..core.logger import setup_logger
from ..models.database import get_db
from .auth import require_auth

logger = setup_logger()

router = APIRouter()

# 全局协作督导Agent实例
_supervisor_agent = CollaborationSupervisionAgent()


class TeamMember(BaseModel):
    student_id: str
    name: str
    skills: List[str] = []
    current_task: Optional[str] = None


class DailyReportRequest(BaseModel):
    project_id: str
    team_members: List[TeamMember]
    progress_data: Dict[str, Any] = {}


class BlockerDetectionRequest(BaseModel):
    team_members: List[TeamMember]
    progress_data: Dict[str, Any] = {}


class ConflictResolutionRequest(BaseModel):
    conflict_description: str
    involved_members: List[TeamMember]
    project_context: str = ""


class KnowledgeSharingRequest(BaseModel):
    team_members: List[TeamMember]
    project_modules: List[Dict[str, Any]] = []


class ProgressSyncRequest(BaseModel):
    project_id: str
    team_members: List[TeamMember]
    progress_data: Dict[str, Any] = {}


@router.post("/daily-report")
async def generate_daily_report(
    request: DailyReportRequest,
    db: Session = Depends(get_db),
    _current: str = Depends(require_auth)
):
    """生成每日协作报告"""
    try:
        result = await _supervisor_agent.process({
            "task": "daily_report",
            "project_id": request.project_id,
            "team_members": [m.model_dump() for m in request.team_members],
            "progress_data": request.progress_data,
        })
        return result
    except Exception as e:
        logger.error(f"Daily report generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/detect-blockers")
async def detect_blockers(
    request: BlockerDetectionRequest,
    db: Session = Depends(get_db),
    _current: str = Depends(require_auth)
):
    """检测团队阻塞情况"""
    try:
        result = await _supervisor_agent.process({
            "task": "detect_blockers",
            "team_members": [m.model_dump() for m in request.team_members],
            "progress_data": request.progress_data,
        })
        return result
    except Exception as e:
        logger.error(f"Blocker detection failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/resolve-conflict")
async def resolve_conflict(
    request: ConflictResolutionRequest,
    db: Session = Depends(get_db),
    _current: str = Depends(require_auth)
):
    """解决团队冲突"""
    try:
        result = await _supervisor_agent.process({
            "task": "resolve_conflict",
            "conflict_description": request.conflict_description,
            "involved_members": [m.model_dump() for m in request.involved_members],
            "project_context": request.project_context,
        })
        return result
    except Exception as e:
        logger.error(f"Conflict resolution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/knowledge-sharing")
async def knowledge_sharing(
    request: KnowledgeSharingRequest,
    db: Session = Depends(get_db),
    _current: str = Depends(require_auth)
):
    """促进知识共享"""
    try:
        result = await _supervisor_agent.process({
            "task": "knowledge_sharing",
            "team_members": [m.model_dump() for m in request.team_members],
            "project_modules": request.project_modules,
        })
        return result
    except Exception as e:
        logger.error(f"Knowledge sharing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync-progress")
async def sync_progress(
    request: ProgressSyncRequest,
    db: Session = Depends(get_db),
    _current: str = Depends(require_auth)
):
    """同步团队进度"""
    try:
        result = await _supervisor_agent.process({
            "task": "sync_progress",
            "project_id": request.project_id,
            "team_members": [m.model_dump() for m in request.team_members],
            "progress_data": request.progress_data,
        })
        return result
    except Exception as e:
        logger.error(f"Progress sync failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
