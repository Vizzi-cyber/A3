"""
思维溯源API
提供错误根源追溯、思维误区分类、纠正策略生成等功能
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from ..agents import MisconceptionTracerAgent
from ..core.logger import setup_logger
from ..models.database import get_db
from .auth import require_auth

logger = setup_logger()

router = APIRouter()

# 全局思维溯源Agent实例
_tracer_agent = MisconceptionTracerAgent()


class TraceRequest(BaseModel):
    """思维溯源请求"""
    code: str
    error_type: str = ""  # 语法错误/逻辑错误/思维误区
    error_description: str = ""
    task: str = "trace_error"  # trace_error / classify_misconception / generate_correction
    student_history: Optional[Dict[str, Any]] = None
    profile: Optional[Dict[str, Any]] = None
    misconception_type: Optional[str] = None


@router.post("/trace")
async def trace_error(
    request: TraceRequest,
    db: Session = Depends(get_db),
    _current: str = Depends(require_auth)
):
    """追溯错误根源"""
    try:
        result = await _tracer_agent.process({
            "task": "trace_error",
            "code": request.code,
            "error_type": request.error_type,
            "error_description": request.error_description,
            "student_history": request.student_history,
            "profile": request.profile,
        })

        return result

    except Exception as e:
        logger.error(f"Error tracing failed: {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


@router.post("/classify")
async def classify_misconception(
    request: TraceRequest,
    db: Session = Depends(get_db),
    _current: str = Depends(require_auth)
):
    """分类思维误区"""
    try:
        result = await _tracer_agent.process({
            "task": "classify_misconception",
            "code": request.code,
            "error_description": request.error_description,
        })

        return result

    except Exception as e:
        logger.error(f"Misconception classification failed: {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


@router.post("/correct")
async def generate_correction(
    request: TraceRequest,
    db: Session = Depends(get_db),
    _current: str = Depends(require_auth)
):
    """生成纠正策略"""
    try:
        result = await _tracer_agent.process({
            "task": "generate_correction",
            "code": request.code,
            "error_type": request.error_type,
            "misconception_type": request.misconception_type,
            "profile": request.profile,
        })

        return result

    except Exception as e:
        logger.error(f"Correction generation failed: {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


@router.post("/full-analysis")
async def full_analysis(
    request: TraceRequest,
    db: Session = Depends(get_db),
    _current: str = Depends(require_auth)
):
    """完整分析流程：追溯 -> 分类 -> 纠正"""
    try:
        # Step 1: 追溯错误根源
        trace_result = await _tracer_agent.process({
            "task": "trace_error",
            "code": request.code,
            "error_type": request.error_type,
            "error_description": request.error_description,
            "student_history": request.student_history,
            "profile": request.profile,
        })

        # Step 2: 分类思维误区
        classify_result = await _tracer_agent.process({
            "task": "classify_misconception",
            "code": request.code,
            "error_description": request.error_description,
        })

        # Step 3: 生成纠正策略
        correction_result = await _tracer_agent.process({
            "task": "generate_correction",
            "code": request.code,
            "error_type": request.error_type,
            "misconception_type": classify_result.get("classification", {}).get("primary_category", ""),
            "profile": request.profile,
        })

        return {
            "status": "success",
            "trace": trace_result.get("trace_result"),
            "classification": classify_result.get("classification"),
            "correction": correction_result.get("correction"),
        }

    except Exception as e:
        logger.error(f"Full analysis failed: {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")
