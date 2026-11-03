"""
通用 LRU + TTL 内存缓存，用于 Agent 结果去重
"""
import asyncio
import hashlib
import json
import time
from typing import Any, Optional


class PromptCache:
    """基于 prompt hash 的结果缓存（LRU + TTL）"""

    def __init__(self, max_size: int = 512, ttl_seconds: int = 600):
        self._cache: dict[str, tuple[Any, float]] = {}
        self._max_size = max_size
        self._ttl = ttl_seconds

    @staticmethod
    def hash_prompt(data: Any, extra_salt: str = "") -> str:
        """对数据做 SHA256 生成缓存 key"""
        raw = json.dumps(data, sort_keys=True, ensure_ascii=False, default=str) + extra_salt
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:32]

    async def get(self, key: str) -> Optional[Any]:
        if key in self._cache:
            value, ts = self._cache[key]
            if time.time() - ts < self._ttl:
                return value
            del self._cache[key]
        return None

    async def set(self, key: str, value: Any):
        if len(self._cache) >= self._max_size:
            oldest_key = min(self._cache, key=lambda k: self._cache[k][1])
            del self._cache[oldest_key]
        self._cache[key] = (value, time.time())

    def clear(self):
        self._cache.clear()

    def clear_by_prefix(self, prefix: str):
        """清除所有 key 以 prefix 开头的缓存"""
        keys_to_remove = [k for k in self._cache if k.startswith(prefix)]
        for k in keys_to_remove:
            del self._cache[k]


# 全局单例（启动时创建，TTL/size 可通过 config 覆盖）
prompt_cache = PromptCache(max_size=512, ttl_seconds=600)


def init_cache():
    """根据配置重新初始化缓存参数"""
    try:
        from .config import settings
        prompt_cache._max_size = settings.CACHE_MAX_SIZE
        prompt_cache._ttl = settings.CACHE_TTL_SECONDS
    except Exception:
        pass
