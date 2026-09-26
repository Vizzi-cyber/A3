"""
PPT 自动生成 API
"""
import asyncio
import os
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, Query, Request, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from ..core.logger import setup_logger
from .auth import require_auth, verify_token

logger = setup_logger()

router = APIRouter()

# 内存任务存储
_ppt_tasks: Dict[str, Dict[str, Any]] = {}
_MAX_PPT_TASKS = 100


def _cleanup_old_tasks():
    """清理过期 PPT 任务，防止内存无限增长"""
    if len(_ppt_tasks) <= _MAX_PPT_TASKS:
        return
    sorted_tasks = sorted(
        _ppt_tasks.items(),
        key=lambda x: x[1].get("status") == "pending",
    )
    to_remove = len(sorted_tasks) - _MAX_PPT_TASKS
    for key, _ in sorted_tasks[:to_remove]:
        del _ppt_tasks[key]


class PPTGenerateRequest(BaseModel):
    topic: str = Field(..., max_length=500)
    subject: str = Field("C语言数据结构", max_length=200)


class PPTTaskStatus(BaseModel):
    task_id: str
    status: str  # pending | generating_outline | building_pptx | completed | failed
    progress: int  # 0-100
    filename: Optional[str] = None
    slide_count: Optional[int] = None
    message: str = ""


async def _generate_task(task_id: str, topic: str, subject: str):
    """后台 PPT 生成任务"""
    try:
        _ppt_tasks[task_id]["status"] = "generating_outline"
        _ppt_tasks[task_id]["progress"] = 15
        _ppt_tasks[task_id]["message"] = "AI正在分析主题，生成深度大纲..."

        from ..services.ppt_generator import generate_ppt

        _ppt_tasks[task_id]["status"] = "building_pptx"
        _ppt_tasks[task_id]["progress"] = 50
        _ppt_tasks[task_id]["message"] = "正在构建PPT文件（含代码示例、算法步骤）..."

        result = await generate_ppt(topic, subject)

        _ppt_tasks[task_id]["status"] = "completed"
        _ppt_tasks[task_id]["progress"] = 100
        _ppt_tasks[task_id]["filename"] = result["filename"]
        _ppt_tasks[task_id]["slide_count"] = result["slide_count"]
        _ppt_tasks[task_id]["message"] = f"PPT生成完成，共{result['slide_count']}页"
        _ppt_tasks[task_id]["path"] = result["path"]

    except Exception as e:
        logger.error(f"PPT生成失败: {e}")
        _ppt_tasks[task_id]["status"] = "failed"
        _ppt_tasks[task_id]["progress"] = 0
        _ppt_tasks[task_id]["message"] = "PPT生成失败，请稍后重试"


@router.post("/generate")
async def generate_ppt_endpoint(req: PPTGenerateRequest, bg: BackgroundTasks, _current: str = Depends(require_auth)):
    """启动PPT生成任务"""
    import uuid
    task_id = str(uuid.uuid4())[:8]

    _cleanup_old_tasks()
    _ppt_tasks[task_id] = {
        "task_id": task_id,
        "status": "pending",
        "progress": 0,
        "message": "任务已创建，等待生成...",
        "filename": None,
        "slide_count": None,
        "path": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    bg.add_task(_generate_task, task_id, req.topic, req.subject)

    return {
        "status": "success",
        "task_id": task_id,
        "message": "PPT生成任务已启动",
    }


@router.get("/{task_id}/status")
async def get_ppt_status(task_id: str, _current: str = Depends(require_auth)):
    """查询PPT生成状态"""
    task = _ppt_tasks.get(task_id)
    if not task:
        return {"status": "error", "message": "任务不存在"}
    return {
        "status": "success",
        "data": {
            "task_id": task["task_id"],
            "status": task["status"],
            "progress": task["progress"],
            "filename": task["filename"],
            "slide_count": task["slide_count"],
            "message": task["message"],
        },
    }


@router.get("/{task_id}/download")
async def download_ppt(task_id: str, request: Request, token: str = Query(None, description="JWT token (alternative to Authorization header)")):
    """下载生成的PPT文件 - 支持 Authorization header 或 token query param"""
    auth_header = request.headers.get("authorization", "")
    token_to_verify = None

    if auth_header.startswith("Bearer "):
        token_to_verify = auth_header[7:]
    elif token:
        token_to_verify = token

    if not token_to_verify:
        raise HTTPException(status_code=401, detail="未提供认证信息")

    try:
        student_id = verify_token(token_to_verify)
        if not student_id:
            raise HTTPException(status_code=401, detail="认证失败")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail="认证失败")

    task = _ppt_tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    if task["status"] == "failed":
        raise HTTPException(status_code=400, detail="PPT生成失败，请重新生成")
    if task["status"] != "completed":
        raise HTTPException(status_code=400, detail="PPT尚未生成完成")

    file_path = task.get("path")
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")

    return FileResponse(
        path=file_path,
        filename=task["filename"],
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
    )
