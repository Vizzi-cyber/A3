"""
火山引擎文生图服务
支持火山方舟（ARK）优先，回退到视觉智能 OpenAPI
"""
import json
import httpx
from typing import Dict, Any

from ..core.config import settings
from .volc_signature import sign_request


class ImageGenerationError(Exception):
    pass


# ---------- ARK (火山方舟) 方式 ----------

async def _ark_generate(
    prompt: str,
    width: int = 1024,
    height: int = 1024,
    seed: int = -1,
    scale: float = 2.5,
) -> list[str]:
    """通过方舟 invoke endpoint 生成图像，返回图片 URL 列表"""
    if not settings.ARK_API_KEY:
        raise ImageGenerationError("Missing ARK_API_KEY in config")

    endpoint_id = settings.ARK_IMAGE_ENDPOINT
    url = f"{settings.ARK_BASE_URL}/{endpoint_id}"

    payload = {
        "prompt": prompt,
        "width": width,
        "height": height,
        "seed": seed,
        "scale": scale,
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.ARK_API_KEY}",
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(url, headers=headers, json=payload)
        data = resp.json()

    # 方舟返回格式可能包含 images 数组
    images = data.get("images") or data.get("data", {}).get("images", [])
    if not images:
        raise ImageGenerationError(f"No images returned: {data}")

    urls = []
    for img in images:
        if isinstance(img, str):
            urls.append(img)
        elif isinstance(img, dict):
            if "url" in img:
                urls.append(img["url"])
            elif "base64" in img:
                urls.append(f"data:image/jpeg;base64,{img['base64']}")
    return urls


# ---------- 视觉智能 OpenAPI 方式（异步） ----------

_BASE_URL = settings.VOLC_VISUAL_ENDPOINT
_REGION = settings.VOLC_REGION
_SERVICE = settings.VOLC_SERVICE
_REQ_KEY = "high_aes_general_v30l_zt2i"


def _ensure_chinese_prompt(prompt: str) -> str:
    """如果用户输入包含中文，追加约束强制图片内文字使用中文"""
    # 简单检测是否包含中文字符
    has_chinese = any("\u4e00" <= ch <= "\u9fff" for ch in prompt)
    if has_chinese:
        # 避免重复追加
        suffix = "图片内所有文字必须使用中文，不得出现任何英文字母或英文单词。"
        if suffix not in prompt:
            prompt = f"{prompt}，{suffix}"
    return prompt


async def submit_image_task(
    prompt: str,
    width: int = 1328,
    height: int = 1328,
    seed: int = -1,
    scale: float = 2.5,
    use_pre_llm: bool = False,
) -> str:
    """提交文生图异步任务，返回 task_id"""
    if not settings.VOLC_ACCESS_KEY or not settings.VOLC_SECRET_KEY:
        raise ImageGenerationError("Missing VOLC_ACCESS_KEY or VOLC_SECRET_KEY in config")

    prompt = _ensure_chinese_prompt(prompt)

    uri = "/"
    query = "Action=CVSync2AsyncSubmitTask&Version=2022-08-31"
    body_dict = {
        "req_key": _REQ_KEY,
        "prompt": prompt,
        "width": width,
        "height": height,
        "seed": seed,
        "scale": scale,
        "use_pre_llm": use_pre_llm,
    }
    body = json.dumps(body_dict, separators=(",", ":"), ensure_ascii=False)

    headers = {
        "Content-Type": "application/json",
        "host": "visual.volcengineapi.com",
    }
    signed_headers = sign_request(
        access_key=settings.VOLC_ACCESS_KEY,
        secret_key=settings.VOLC_SECRET_KEY,
        method="POST",
        uri=uri,
        query=query,
        body=body,
        region=_REGION,
        service=_SERVICE,
    )

    url = f"{_BASE_URL}?{query}"
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(url, headers=signed_headers, content=body.encode("utf-8"))
        data = resp.json()

    if data.get("code") != 10000:
        raise ImageGenerationError(f"Submit failed: {data.get('message')} (code={data.get('code')})")

    task_id = data.get("data", {}).get("task_id")
    if not task_id:
        raise ImageGenerationError("No task_id returned")
    return task_id


async def get_image_result(task_id: str) -> Dict[str, Any]:
    """查询文生图任务结果"""
    if not settings.VOLC_ACCESS_KEY or not settings.VOLC_SECRET_KEY:
        raise ImageGenerationError("Missing VOLC_ACCESS_KEY or VOLC_SECRET_KEY in config")

    uri = "/"
    query = "Action=CVSync2AsyncGetResult&Version=2022-08-31"
    body_dict = {
        "req_key": _REQ_KEY,
        "task_id": task_id,
        "req_json": json.dumps({"return_url": True, "logo_info": {"add_logo": False}}, ensure_ascii=False),
    }
    body = json.dumps(body_dict, separators=(",", ":"), ensure_ascii=False)

    headers = {
        "Content-Type": "application/json",
        "host": "visual.volcengineapi.com",
    }
    signed_headers = sign_request(
        access_key=settings.VOLC_ACCESS_KEY,
        secret_key=settings.VOLC_SECRET_KEY,
        method="POST",
        uri=uri,
        query=query,
        body=body,
        region=_REGION,
        service=_SERVICE,
    )

    url = f"{_BASE_URL}?{query}"
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(url, headers=signed_headers, content=body.encode("utf-8"))
        data = resp.json()

    if data.get("code") != 10000:
        raise ImageGenerationError(f"Query failed: {data.get('message')} (code={data.get('code')})")

    return data.get("data", {})


# ---------- 统一入口 ----------

async def generate_image_ark(
    prompt: str,
    width: int = 1024,
    height: int = 1024,
    seed: int = -1,
    scale: float = 2.5,
) -> list[str]:
    """
    统一文生图入口：优先使用方舟（同步直接返回 URL），
    若未配置 ARK_API_KEY 则抛出错误提示用户。
    """
    if settings.ARK_API_KEY:
        return await _ark_generate(prompt, width, height, seed, scale)
    raise ImageGenerationError(
        "Missing ARK_API_KEY. Please set it in backend/.env"
    )
