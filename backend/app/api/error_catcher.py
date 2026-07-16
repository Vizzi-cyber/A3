"""
错误捕捉API
提供代码错误分析、思维误区诊断等功能
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from ..agents import ErrorCatcherAgent, CourseDesignerAgent
from ..core.logger import setup_logger
from ..models.database import get_db
from .auth import require_auth

logger = setup_logger()

router = APIRouter()

# 全局错误捕捉Agent实例
_error_catcher_agent = ErrorCatcherAgent()


class ErrorCatchRequest(BaseModel):
    """错误捕捉请求"""
    code: str
    language: str = "C"
    task: str = "catch_error"  # catch_error / analyze_misconception / validate_code
    student_level: str = "beginner"  # beginner / intermediate / advanced
    error_output: Optional[str] = None  # 编译器错误信息


class ErrorCatchResponse(BaseModel):
    """错误捕捉响应"""
    status: str
    analysis: Optional[Dict[str, Any]] = None
    misconceptions: Optional[List[Dict[str, Any]]] = None
    learning_suggestions: Optional[List[str]] = None
    validation: Optional[Dict[str, Any]] = None


@router.post("/analyze", response_model=ErrorCatchResponse)
async def analyze_code_error(
    request: ErrorCatchRequest,
    db: Session = Depends(get_db),
    _current: str = Depends(require_auth)
):
    """分析代码中的错误"""
    try:
        result = await _error_catcher_agent.process({
            "task": request.task,
            "code": request.code,
            "language": request.language,
            "student_level": request.student_level,
            "error_output": request.error_output,
        })

        if result.get("status") == "success":
            return ErrorCatchResponse(
                status="success",
                analysis=result.get("analysis"),
                misconceptions=result.get("misconceptions"),
                learning_suggestions=result.get("learning_suggestions"),
                validation=result.get("validation"),
            )
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "分析失败"))

    except Exception as e:
        logger.error(f"Error analysis failed: {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


@router.post("/catch-error")
async def catch_error(
    request: ErrorCatchRequest,
    db: Session = Depends(get_db),
    _current: str = Depends(require_auth)
):
    """捕捉代码错误（简化接口）"""
    try:
        result = await _error_catcher_agent.process({
            "task": "catch_error",
            "code": request.code,
            "language": request.language,
            "student_level": request.student_level,
            "error_output": request.error_output,
        })

        return result

    except Exception as e:
        logger.error(f"Error catching failed: {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


@router.post("/analyze-misconception")
async def analyze_misconception(
    request: ErrorCatchRequest,
    db: Session = Depends(get_db),
    _current: str = Depends(require_auth)
):
    """分析思维误区"""
    try:
        result = await _error_catcher_agent.process({
            "task": "analyze_misconception",
            "code": request.code,
            "language": request.language,
            "student_level": request.student_level,
        })

        return result

    except Exception as e:
        logger.error(f"Misconception analysis failed: {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


@router.post("/validate-code")
async def validate_code(
    request: ErrorCatchRequest,
    db: Session = Depends(get_db),
    _current: str = Depends(require_auth)
):
    """验证代码正确性"""
    try:
        result = await _error_catcher_agent.process({
            "task": "validate_code",
            "code": request.code,
            "language": request.language,
            "student_level": request.student_level,
        })

        return result

    except Exception as e:
        logger.error(f"Code validation failed: {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


# 全局课程设计师实例（编排错误诊断全流程）
_designer_agent = CourseDesignerAgent()


class FullDiagnosisRequest(BaseModel):
    """全流程诊断请求"""
    code: str
    language: str = "C"
    student_level: str = "beginner"
    error_output: str = ""
    error_type: str = "逻辑错误"
    student_id: str


@router.post("/full-diagnosis")
async def full_diagnosis(
    request: FullDiagnosisRequest,
    _current: str = Depends(require_auth),
):
    """课程设计师Agent编排的全流程错误诊断"""
    try:
        result = await _designer_agent.process({
            "task_type": "error_diagnosis",
            "code": request.code,
            "language": request.language,
            "student_level": request.student_level,
            "error_output": request.error_output,
            "error_type": request.error_type,
            "student_id": request.student_id,
        })
        return {"status": "success", "data": result}
    except Exception as e:
        logger.error(f"Full diagnosis failed: {e}")
        raise HTTPException(status_code=500, detail="全流程诊断失败，请稍后重试")
