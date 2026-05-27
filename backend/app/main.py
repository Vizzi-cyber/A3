"""
FastAPI 主应用入口
"""
import asyncio
import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

from .api import router as api_router
from .core.config import settings
from .core.logger import setup_logger
from .core.rate_limiter import RateLimiter
from .core.exceptions import validation_exception_handler, http_exception_handler, global_exception_handler

# 设置日志
logger = setup_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    """
    # 启动时执行
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")

    # 先创建所有表
    from .models.database import engine, Base
    import app.models as models
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")

    # 跳过 Alembic 迁移（表已通过 create_all 创建）
    # from alembic.config import Config
    # from alembic.command import upgrade
    # alembic_cfg = Config("alembic.ini")
    # await asyncio.to_thread(upgrade, alembic_cfg, "head")
    # logger.info("Database migrations applied")

    yield

    # 关闭时执行
    logger.info("Shutting down application")


# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="基于大模型的个性化资源生成与学习多智能体系统",
    lifespan=lifespan
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 请求限流
app.add_middleware(RateLimiter, default_limit=60, window_seconds=60)


# API 性能监控中间件
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import time

class APIMonitorMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        status_code = 500
        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        except Exception:
            status_code = 500
            raise
        finally:
            duration_ms = (time.time() - start) * 1000
            # 异步写入，不阻塞事件循环
            try:
                from .models.database import SessionLocal
                from .models.monitor import ApiMonitorModel

                def _write_monitor():
                    db = SessionLocal()
                    try:
                        db.add(ApiMonitorModel(
                            endpoint=request.url.path,
                            method=request.method,
                            status_code=status_code,
                            duration_ms=round(duration_ms, 2),
                        ))
                        db.commit()
                    finally:
                        db.close()

                asyncio.create_task(asyncio.to_thread(_write_monitor))
            except Exception as e:
                logger.warning(f"API监控写入失败: {e}")

app.add_middleware(APIMonitorMiddleware)

# 注册异常处理器
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# 注册路由
app.include_router(api_router, prefix="/api/v1")

# 静态文件（用于存储生成的资源）
os.makedirs("static/resources", exist_ok=True)
os.makedirs("static/uploads", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    """根路径 - 服务状态检查"""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs_url": "/docs"
    }


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }



if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
