"""
简易内存限流器
基于客户端IP和路径做速率限制，无需额外依赖
"""
import time
from typing import Dict, Tuple
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class RateLimiter(BaseHTTPMiddleware):
    """
    请求速率限制中间件
    - 全局默认: 60次/分钟
    - 登录/注册: 10次/分钟
    - LLM相关接口: 20次/分钟
    """

    def __init__(self, app, default_limit: int = 60, window_seconds: int = 60):
        super().__init__(app)
        self.default_limit = default_limit
        self.window_seconds = window_seconds
        # 存储结构: {key: [timestamp, ...]}
        self._records: Dict[str, list[float]] = {}
        self._cleanup_counter: int = 0
        self._cleanup_interval: int = 200  # 每 200 次请求做一次全量清理

    def _global_cleanup(self, now: float):
        """全量清理所有过期的 key，防止内存泄漏"""
        expired_keys = []
        for key, records in self._records.items():
            active = [t for t in records if now - t < self.window_seconds]
            if active:
                self._records[key] = active
            else:
                expired_keys.append(key)
        for key in expired_keys:
            del self._records[key]

    async def dispatch(self, request: Request, call_next):
        # 获取客户端标识（优先 X-Forwarded-For 第一个 IP，其次直接IP）
        forwarded = request.headers.get("x-forwarded-for")
        client_ip = "unknown"
        if forwarded:
            client_ip = forwarded.split(",")[0].strip() or "unknown"
        if client_ip == "unknown" and request.client:
            client_ip = request.client.host or "unknown"

        path = request.url.path

        # 根据路径确定限制策略（使用精确路径匹配）
        if path.startswith("/api/v1/auth/login") or path.startswith("/api/v1/auth/register"):
            limit = 10
        elif any(path.startswith(p) for p in ["/api/v1/tutor/", "/api/v1/resource/generate", "/api/v1/image/generate", "/api/v1/learning-path/generate"]):
            limit = 20
        else:
            limit = self.default_limit

        key = f"{client_ip}:{path}"
        now = time.time()

        # 定期全量清理，防止不活跃 key 占用内存
        self._cleanup_counter += 1
        if self._cleanup_counter >= self._cleanup_interval:
            self._cleanup_counter = 0
            self._global_cleanup(now)

        # 清理过期记录
        records = self._records.get(key, [])
        records = [t for t in records if now - t < self.window_seconds]
        if records:
            self._records[key] = records
        else:
            self._records.pop(key, None)

        if len(records) >= limit:
            reset_after = int(self.window_seconds - (now - records[0])) if records else self.window_seconds
            return JSONResponse(
                status_code=429,
                content={
                    "status": "error",
                    "message": f"请求过于频繁，请 {reset_after} 秒后再试",
                },
                headers={"Retry-After": str(reset_after)},
            )

        records.append(now)
        self._records[key] = records

        response = await call_next(request)
        # 添加限流响应头
        remaining = max(0, limit - len(records))
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Window"] = str(self.window_seconds)
        return response
