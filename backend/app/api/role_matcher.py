"""
角色匹配API
提供团队组建、角色建议、任务分配等功能
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from ..agents import RoleMatcherAgent
from ..core.logger import setup_logger
from ..models.database import get_db
from .auth import require_auth

logger = setup_logger()

router = APIRouter()

# 全局角色匹配Agent实例
_role_matcher_agent = RoleMatcherAgent()


class StudentInfo(BaseModel):
    """学生信息"""
    student_id: str
    name: str
    profile: Optional[Dict[str, Any]] = None
    skills: List[str] = []
    preferences: List[str] = []
    current_tasks: Optional[List[str]] = None


class MatchRequest(BaseModel):
    """角色匹配请求"""
    task: str = "match_team"  # match_team / suggest_role / rebalance / get_roles
    students: Optional[List[StudentInfo]] = None
    student: Optional[StudentInfo] = None
    project_tasks: Optional[Dict[str, Any]] = None
    current_assignments: Optional[Dict[str, Any]] = None
    issues: Optional[List[str]] = None


@router.get("/roles")
async def get_roles(
    _current: str = Depends(require_auth)
):
    """获取可用角色定义"""
    try:
        result = await _role_matcher_agent.process({
            "task": "get_roles",
        })
        return result
    except Exception as e:
        logger.error(f"Get roles failed: {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


@router.post("/match")
async def match_team(
    request: MatchRequest,
    db: Session = Depends(get_db),
    _current: str = Depends(require_auth)
):
    """匹配团队和分工"""
    try:
        students_data = None
        if request.students:
            students_data = [s.dict() for s in request.students]

        result = await _role_matcher_agent.process({
            "task": "match_team",
            "students": students_data or [],
            "project_tasks": request.project_tasks,
        })

        return result

    except Exception as e:
        logger.error(f"Team matching failed: {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


@router.post("/suggest")
async def suggest_role(
    request: MatchRequest,
    db: Session = Depends(get_db),
    _current: str = Depends(require_auth)
):
    """为单个学生建议角色"""
    try:
        if not request.student:
            raise HTTPException(status_code=400, detail="请提供学生信息")

        result = await _role_matcher_agent.process({
            "task": "suggest_role",
            "student": request.student.dict(),
            "project_tasks": request.project_tasks,
        })

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Role suggestion failed: {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


@router.post("/rebalance")
async def rebalance(
    request: MatchRequest,
    db: Session = Depends(get_db),
    _current: str = Depends(require_auth)
):
    """重新平衡任务分配"""
    try:
        students_data = None
        if request.students:
            students_data = [s.dict() for s in request.students]

        result = await _role_matcher_agent.process({
            "task": "rebalance",
            "students": students_data or [],
            "current_assignments": request.current_assignments,
            "project_tasks": request.project_tasks,
            "issues": request.issues,
        })

        return result

    except Exception as e:
        logger.error(f"Rebalance failed: {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")
