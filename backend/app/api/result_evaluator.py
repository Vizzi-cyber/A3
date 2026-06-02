"""
成果评估API
提供代码质量评估、协作效果评估、综合报告生成等功能
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from ..agents import ResultEvaluatorAgent
from ..core.logger import setup_logger
from ..models.database import get_db
from .auth import require_auth

logger = setup_logger()

router = APIRouter()

# 全局成果评估Agent实例
_evaluator_agent = ResultEvaluatorAgent()


class TeamMember(BaseModel):
    student_id: str
    name: str
    skills: List[str] = []


class CodeSubmission(BaseModel):
    file_name: str = "main.c"
    code: str
    student_id: Optional[str] = None


class CodeEvaluationRequest(BaseModel):
    code_submission: CodeSubmission
    language: str = "C"


class CollaborationEvaluationRequest(BaseModel):
    team_members: List[TeamMember]
    collaboration_data: Dict[str, Any] = {}


class DeliverableEvaluationRequest(BaseModel):
    project_info: Dict[str, Any]
    deliverables: List[Dict[str, Any]] = []
    team_level: str = "beginner"


class LearningEvaluationRequest(BaseModel):
    team_members: List[TeamMember]
    project_info: Dict[str, Any] = {}
    knowledge_points: List[str] = []


class FullReportRequest(BaseModel):
    project_info: Dict[str, Any]
    team_members: List[TeamMember]
    code_submissions: List[CodeSubmission] = []
    collaboration_data: Dict[str, Any] = {}
    deliverables: List[Dict[str, Any]] = []
    knowledge_points: List[str] = []
    team_level: str = "beginner"


@router.post("/evaluate-code")
async def evaluate_code(
    request: CodeEvaluationRequest,
    db: Session = Depends(get_db),
    _current: str = Depends(require_auth)
):
    """评估代码质量"""
    try:
        result = await _evaluator_agent.process({
            "task": "evaluate_code",
            "code_submission": request.code_submission.model_dump(),
            "language": request.language,
        })
        return result
    except Exception as e:
        logger.error(f"Code evaluation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/evaluate-collaboration")
async def evaluate_collaboration(
    request: CollaborationEvaluationRequest,
    db: Session = Depends(get_db),
    _current: str = Depends(require_auth)
):
    """评估团队协作效果"""
    try:
        result = await _evaluator_agent.process({
            "task": "evaluate_collaboration",
            "team_members": [m.model_dump() for m in request.team_members],
            "collaboration_data": request.collaboration_data,
        })
        return result
    except Exception as e:
        logger.error(f"Collaboration evaluation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/evaluate-deliverable")
async def evaluate_deliverable(
    request: DeliverableEvaluationRequest,
    db: Session = Depends(get_db),
    _current: str = Depends(require_auth)
):
    """评估项目交付物"""
    try:
        result = await _evaluator_agent.process({
            "task": "evaluate_deliverable",
            "project_info": request.project_info,
            "deliverables": request.deliverables,
            "team_level": request.team_level,
        })
        return result
    except Exception as e:
        logger.error(f"Deliverable evaluation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/evaluate-learning")
async def evaluate_learning(
    request: LearningEvaluationRequest,
    db: Session = Depends(get_db),
    _current: str = Depends(require_auth)
):
    """评估学习收获"""
    try:
        result = await _evaluator_agent.process({
            "task": "evaluate_learning",
            "team_members": [m.model_dump() for m in request.team_members],
            "project_info": request.project_info,
            "knowledge_points": request.knowledge_points,
        })
        return result
    except Exception as e:
        logger.error(f"Learning evaluation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/full-report")
async def generate_full_report(
    request: FullReportRequest,
    db: Session = Depends(get_db),
    _current: str = Depends(require_auth)
):
    """生成综合评估报告"""
    try:
        result = await _evaluator_agent.process({
            "task": "full_report",
            "project_info": request.project_info,
            "team_members": [m.model_dump() for m in request.team_members],
            "code_submissions": [s.model_dump() for s in request.code_submissions],
            "collaboration_data": request.collaboration_data,
            "deliverables": request.deliverables,
            "knowledge_points": request.knowledge_points,
            "team_level": request.team_level,
        })
        return result
    except Exception as e:
        logger.error(f"Full report generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
