"""
项目拆解API
提供项目任务拆解、工作量估算等功能
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from ..agents import ProjectDecomposerAgent
from ..core.logger import setup_logger
from ..models.database import get_db
from .auth import require_auth

logger = setup_logger()

router = APIRouter()

# 全局项目拆解Agent实例
_decomposer_agent = ProjectDecomposerAgent()


class DecomposeRequest(BaseModel):
    """项目拆解请求"""
    project_id: Optional[str] = None  # 内置项目ID
    project_name: Optional[str] = None  # 自定义项目名称
    team_size: int = 3
    team_level: str = "beginner"  # beginner / intermediate / advanced
    custom_requirements: Optional[str] = None
    task: str = "decompose"  # decompose / get_project_info / estimate_workload / list_projects


@router.get("/projects")
async def list_projects(
    _current: str = Depends(require_auth)
):
    """列出内置项目库"""
    try:
        result = await _decomposer_agent.process({
            "task": "list_projects",
        })
        return result
    except Exception as e:
        logger.error(f"List projects failed: {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


@router.post("/decompose")
async def decompose_project(
    request: DecomposeRequest,
    db: Session = Depends(get_db),
    _current: str = Depends(require_auth)
):
    """拆解项目为任务树"""
    try:
        result = await _decomposer_agent.process({
            "task": "decompose",
            "project_id": request.project_id,
            "project_name": request.project_name,
            "team_size": request.team_size,
            "team_level": request.team_level,
            "custom_requirements": request.custom_requirements,
        })

        return result

    except Exception as e:
        logger.error(f"Project decomposition failed: {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


@router.post("/project-info")
async def get_project_info(
    request: DecomposeRequest,
    db: Session = Depends(get_db),
    _current: str = Depends(require_auth)
):
    """获取项目信息"""
    try:
        result = await _decomposer_agent.process({
            "task": "get_project_info",
            "project_id": request.project_id,
            "project_name": request.project_name,
        })

        return result

    except Exception as e:
        logger.error(f"Get project info failed: {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


@router.post("/estimate")
async def estimate_workload(
    request: DecomposeRequest,
    db: Session = Depends(get_db),
    _current: str = Depends(require_auth)
):
    """估算工作量"""
    try:
        result = await _decomposer_agent.process({
            "task": "estimate_workload",
            "project_id": request.project_id,
            "team_size": request.team_size,
            "team_level": request.team_level,
        })

        return result

    except Exception as e:
        logger.error(f"Workload estimation failed: {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")
