"""
API 性能监控中间件
使用内存缓冲 + 定期批量写入，减少 DB 压力
同时采集功能使用频率数据（按学生），支撑试点效果分析
"""
import asyncio
import time
from collections import deque
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from ..core.logger import setup_logger
from ..core.config import settings

logger = setup_logger()


def _extract_student_id(request: Request):
    """从 Authorization Bearer Token 中提取 student_id（失败返回 None，不阻塞请求）"""
    auth = request.headers.get("authorization", "")
    if not auth.lower().startswith("bearer "):
        return None
    token = auth[7:].strip()
    if not token:
        return None
    try:
        from jose import jwt, JWTError
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload.get("sub")
    except Exception:
        return None


class APIMonitorMiddleware(BaseHTTPMiddleware):
    """
    API 监控中间件（批量写入模式）
    - 请求记录先写入内存缓冲区
    - 每 5 秒或缓冲满 50 条时批量写入数据库
    - 避免每个请求都开 DB session
    - 自动提取 student_id 用于功能使用频率统计（试点数据分析）
    """

    _buffer: deque = deque(maxlen=500)
    _flush_task: asyncio.Task | None = None
    _batch_size: int = 50
    _flush_interval: float = 5.0
    _instance = None

    def __init__(self, app):
        super().__init__(app)
        type(self)._instance = self

    async def dispatch(self, request: Request, call_next):
        start = time.time()
        status_code = 500
        student_id = _extract_student_id(request)
        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        except Exception:
            status_code = 500
            raise
        finally:
            duration_ms = (time.time() - start) * 1000
            self._buffer.append({
                "endpoint": request.url.path,
                "method": request.method,
                "status_code": status_code,
                "duration_ms": round(duration_ms, 2),
                "student_id": student_id,
            })
            # 缓冲满时触发刷新
            if len(self._buffer) >= self._batch_size:
                self._schedule_flush()

    def _schedule_flush(self):
        """调度一次异步刷新（不重复创建任务）"""
        if self._flush_task is None or self._flush_task.done():
            try:
                self._flush_task = asyncio.create_task(self._flush_buffer())
            except RuntimeError:
                pass  # 事件循环未启动

    async def _flush_buffer(self):
        """批量写入数据库，持续排空缓冲区。"""
        while self._buffer:
            batch = []
            while self._buffer and len(batch) < 100:
                batch.append(self._buffer.popleft())
            try:
                from ..models.database import SessionLocal
                from ..models.monitor import ApiMonitorModel

                def _write():
                    db = SessionLocal()
                    try:
                        db.bulk_insert_mappings(ApiMonitorModel, batch)
                        db.commit()
                    finally:
                        db.close()

                await asyncio.to_thread(_write)
            except Exception as e:
                for item in reversed(batch):
                    self._buffer.appendleft(item)
                logger.warning(f"API监控批量写入失败: {e}")
                return

    @classmethod
    async def start_periodic_flush(cls):
        """定期刷新任务（在 lifespan 中调用）"""
        while True:
            await asyncio.sleep(cls._flush_interval)
            instance = cls._get_instance()
            if instance:
                instance._schedule_flush()

    @classmethod
    def _get_instance(cls):
        """获取当前中间件实例"""
        return getattr(cls, "_instance", None)
