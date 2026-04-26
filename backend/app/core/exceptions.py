"""
全局异常处理
"""
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


import json
from typing import Any


def _safe_jsonify(obj: Any) -> Any:
    """递归清理不可 JSON 序列化的对象"""
    if isinstance(obj, dict):
        return {k: _safe_jsonify(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_safe_jsonify(v) for v in obj]
    if isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    # 其他类型转为字符串
    return str(obj)


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """处理请求参数校验错误"""
    # Pydantic v2 的 exc.errors() 可能包含不可序列化的对象（如 ValueError）
    # 使用 exc.json() 获取安全的字符串，再反序列化
    try:
        raw_errors = json.loads(exc.json())
    except Exception:
        raw_errors = [{"msg": str(exc)}]
    safe_detail = _safe_jsonify(raw_errors)
    return JSONResponse(
        status_code=422,
        content={
            "status": "error",
            "message": "请求参数校验失败",
            "detail": safe_detail,
        },
    )


async def http_exception_handler(request: Request, exc):
    """处理 HTTP 异常"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": exc.detail,
        },
    )


async def global_exception_handler(request: Request, exc: Exception):
    """处理所有未捕获的异常"""
    import os
    debug = os.getenv("DEBUG", "true").lower() == "true"
    # 对不可序列化的异常对象做安全转换
    try:
        detail = str(exc)
    except Exception:
        detail = "不可序列化的异常"
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "服务器内部错误",
            "detail": detail if debug else "请联系管理员",
        },
    )
