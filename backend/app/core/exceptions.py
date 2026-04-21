"""
全局异常处理
"""
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """处理请求参数校验错误"""
    return JSONResponse(
        status_code=422,
        content={
            "status": "error",
            "message": "请求参数校验失败",
            "detail": exc.errors(),
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
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "服务器内部错误",
            "detail": str(exc) if debug else "请联系管理员",
        },
    )
