"""
文生图 API
对接火山方舟 Seedream 3.0（同步调用）
兼容回退：火山引擎视觉智能 OpenAPI（异步任务）
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from .auth import require_auth
from ..services.image_generation import (
    generate_image_ark,
    submit_image_task,
    get_image_result,
    ImageGenerationError,
)

router = APIRouter()


class ImageGenerateRequest(BaseModel):
    prompt: str
    width: int = 1024
    height: int = 1024
    seed: int = -1
    scale: float = 2.5
    use_pre_llm: bool = False


class ImageGenerateResponse(BaseModel):
    task_id: str
    status: str
    image_urls: Optional[list[str]] = None
    message: str


class ImageResultResponse(BaseModel):
    task_id: str
    status: str
    image_urls: Optional[list[str]] = None
    binary_data: Optional[list[str]] = None
    message: str


# 内存任务状态缓存
_image_tasks: dict[str, dict] = {}


@router.post("/generate", response_model=ImageGenerateResponse)
async def generate_image(
    request: ImageGenerateRequest,
    _current: str = Depends(require_auth),
):
    """提交文生图任务（方舟优先同步返回，OpenAPI 为异步）"""

    # 优先尝试方舟同步调用
    try:
        urls = await generate_image_ark(
            prompt=request.prompt,
            width=request.width,
            height=request.height,
            seed=request.seed,
            scale=request.scale,
        )
        return ImageGenerateResponse(
            task_id="ark_sync",
            status="done",
            image_urls=urls,
            message="Image generated via ARK",
        )
    except ImageGenerationError:
        pass  # 回退到 OpenAPI 异步

    # OpenAPI 异步方式
    try:
        task_id = await submit_image_task(
            prompt=request.prompt,
            width=request.width,
            height=request.height,
            seed=request.seed,
            scale=request.scale,
            use_pre_llm=request.use_pre_llm,
        )
        _image_tasks[task_id] = {
            "task_id": task_id,
            "status": "submitted",
            "created_at": datetime.now().isoformat(),
        }
        return ImageGenerateResponse(
            task_id=task_id,
            status="submitted",
            message="Image generation task submitted (async)",
        )
    except ImageGenerationError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/result/{task_id}", response_model=ImageResultResponse)
async def get_image_result_api(task_id: str, _current: str = Depends(require_auth)):
    """查询文生图任务结果"""
    if task_id == "ark_sync":
        return ImageResultResponse(
            task_id=task_id,
            status="done",
            message="ARK sync task",
        )

    try:
        result = await get_image_result(task_id)
        status = result.get("status", "unknown")
        image_urls = result.get("image_urls") or []
        binary_data = result.get("binary_data_base64") or []

        if task_id in _image_tasks:
            _image_tasks[task_id]["status"] = status

        return ImageResultResponse(
            task_id=task_id,
            status=status,
            image_urls=image_urls if image_urls else None,
            binary_data=binary_data if binary_data else None,
            message="Done" if status == "done" else f"Status: {status}",
        )
    except ImageGenerationError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks")
async def list_image_tasks(_current: str = Depends(require_auth)):
    """列出当前所有文生图任务"""
    return {
        "status": "success",
        "tasks": list(_image_tasks.values()),
    }
