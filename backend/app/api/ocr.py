"""
OCR 图片识别 API
利用 GLM-4.6v 等支持 vision 的模型进行图片内容识别
支持纸质笔记、错题、公式识别
"""
import base64
import io
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from pydantic import BaseModel

from ..services.llm_factory import LLMFactory
from ..core.safety import SafetyGuard
from .auth import require_auth

router = APIRouter()


class OCRRequest(BaseModel):
    image_base64: str
    prompt: str = "请识别这张图片中的所有文字内容，保持原有的段落和格式。如果是数学公式，请用 LaTeX 表示。"
    provider: Optional[str] = None


class OCRResponse(BaseModel):
    status: str
    text: str
    note_type: Optional[str] = None  # note / error_question / formula / mixed


@router.post("/recognize", response_model=OCRResponse)
async def ocr_recognize(
    request: OCRRequest,
    _current: str = Depends(require_auth),
):
    """识别图片中的文字内容（基于 LLM Vision）"""
    image_b64 = request.image_base64
    if image_b64.startswith("data:"):
        image_b64 = image_b64.split(",", 1)[-1]

    # 安全校验：限制大小（base64 长度约等于 4/3 * 字节数）
    if len(image_b64) > 20_000_000:  # 约 15MB
        raise HTTPException(status_code=413, detail="Image too large")

    try:
        # 解码验证是否为合法图片
        raw = base64.b64decode(image_b64)
        io.BytesIO(raw)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image data")

    provider = request.provider or "bigmodel"
    try:
        llm = LLMFactory.get_llm(provider)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM provider error: {e}")

    vision_content = [
        {"type": "text", "text": request.prompt},
        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}},
    ]

    messages = [
        {"role": "system", "content": "你是一位精准的 OCR 识别助手。请只输出图片中的文字内容，不要添加额外解释。保持原有排版。"},
        {"role": "user", "content": vision_content},
    ]

    try:
        text = await llm.ainvoke(messages, temperature=0.2, max_tokens=2048)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recognition failed: {e}")

    # 输出安全过滤
    safety = SafetyGuard.check_output(text)
    if not safety["safe"]:
        raise HTTPException(status_code=400, detail="识别结果包含敏感内容，已拦截")

    return OCRResponse(status="success", text=text)


@router.post("/upload", response_model=OCRResponse)
async def ocr_upload(
    file: UploadFile = File(...),
    prompt: str = "请识别这张图片中的所有文字内容，保持原有的段落和格式。如果是数学公式，请用 LaTeX 表示。",
    provider: Optional[str] = None,
    _current: str = Depends(require_auth),
):
    """上传图片文件进行 OCR 识别"""
    content = await file.read()
    if len(content) > 15 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Image too large (max 15MB)")

    image_b64 = base64.b64encode(content).decode("utf-8")
    request = OCRRequest(
        image_base64=image_b64,
        prompt=prompt,
        provider=provider,
    )
    return await ocr_recognize(request, _current)
