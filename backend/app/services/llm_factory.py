"""
统一大模型调用工厂
当前仅使用智谱AI（BigModel / GLM-4.6v）
为业务层提供一致的调用接口
"""
import asyncio
import json
import re
import time
from abc import ABC, abstractmethod
from typing import AsyncIterator, Dict, Any, List, Optional

try:
    from openai import AsyncOpenAI
except ImportError:
    AsyncOpenAI = None

from ..core.config import settings
from ..core.logger import setup_logger

logger = setup_logger()


class BaseLLM(ABC):
    """统一 LLM 接口（messages 支持 vision 格式）"""

    @abstractmethod
    async def ainvoke(
        self,
        messages: List[Dict[str, Any]],
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> str:
        pass

    @abstractmethod
    async def astream(
        self,
        messages: List[Dict[str, Any]],
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> AsyncIterator[str]:
        pass

    @staticmethod
    def _try_parse_json(text: str) -> Optional[Dict[str, Any]]:
        """尝试多种方式解析 JSON，成功返回 dict，失败返回 None"""
        if not text or not text.strip():
            return None

        # 1. 直接解析
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # 2. 提取 markdown 代码块中的 JSON（支持各种 backtick 变体）
        # 匹配 ```json ... ``` 或 ``` ... ```
        match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text, re.IGNORECASE)
        if match:
            try:
                return json.loads(match.group(1).strip())
            except json.JSONDecodeError:
                pass

        # 3. 从 { 到最后一个 } 提取 JSON（处理 LLM 输出带前后文本的情况）
        match = re.search(r"(\{[\s\S]*\})", text)
        if match:
            try:
                return json.loads(match.group(1).strip())
            except json.JSONDecodeError:
                # 尝试修复常见问题：移除尾部逗号
                fixed = re.sub(r",\s*([}\]])", r"\1", match.group(1).strip())
                try:
                    return json.loads(fixed)
                except json.JSONDecodeError:
                    pass

        # 4. 尝试找到最外层 {} 并解析（处理截断或编码问题）
        start = text.find("{")
        if start >= 0:
            # 从最后一个 } 向前找
            end = text.rfind("}")
            if end > start:
                try:
                    return json.loads(text[start:end + 1])
                except json.JSONDecodeError:
                    pass

        return None

    async def generate_json(
        self,
        messages: List[Dict[str, Any]],
        temperature: float = 0.3,
        max_tokens: int = 1024,
    ) -> Dict[str, Any]:
        """强制 JSON 输出"""
        text = await self.ainvoke(messages, temperature, max_tokens)
        parsed = self._try_parse_json(text)
        if parsed is not None:
            return parsed

        logger.warning(f"JSON parse failed, returning raw text. Raw: {text[:200]}")
        return {"status": "error", "raw_text": text, "message": "模型未返回合法 JSON"}

    def bind_tools(self, tools: List[Any]):
        return self


_DEFAULT_TIMEOUT = 60.0  # 秒


class OpenAICompatibleLLM(BaseLLM):
    """OpenAI 兼容接口（智谱AI 等）"""

    def __init__(
        self,
        api_key: str,
        base_url: str,
        model: str,
        timeout: float = _DEFAULT_TIMEOUT,
    ):
        if AsyncOpenAI is None:
            raise ImportError("openai package is not installed. Please install it to use LLM features.")
        if not api_key:
            raise ValueError(f"API key is required for model {model}")
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url, timeout=timeout)
        self.model = model
        self._is_bigmodel = "bigmodel" in self.client.base_url.host

    def _log_llm_call(self, provider: str, model: str, prompt_tokens: int, completion_tokens: int,
                       duration_ms: float, success: bool, error_msg: str = None):
        """异步记录 LLM 调用到监控表（同步方法，供 to_thread 调用）"""
        try:
            from ..models.database import SessionLocal
            from ..models.monitor import LlmCallModel
            db = SessionLocal()
            try:
                db.add(LlmCallModel(
                    provider=provider, model=model,
                    prompt_tokens=prompt_tokens, completion_tokens=completion_tokens,
                    duration_ms=round(duration_ms, 2), success=success, error_msg=error_msg,
                ))
                db.commit()
            finally:
                db.close()
        except Exception as e:
            logger.warning(f"LLM调用记录持久化失败: {e}")

    async def ainvoke(self, messages: List[Dict[str, Any]], temperature=0.7, max_tokens=1024, thinking: bool = False) -> str:
        """非流式调用，默认关闭智谱 thinking 以加快响应，含指数退避重试"""
        kwargs: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }
        if self._is_bigmodel:
            kwargs["extra_body"] = {"thinking": {"type": "enabled" if thinking else "disabled"}}

        max_retries = 3
        last_exception = None
        for attempt in range(max_retries):
            start = time.time()
            try:
                response = await self.client.chat.completions.create(**kwargs)
                msg = response.choices[0].message
                content = msg.content or ""
                duration_ms = (time.time() - start) * 1000
                usage = getattr(response, 'usage', None)
                asyncio.create_task(asyncio.to_thread(
                    self._log_llm_call, "bigmodel" if self._is_bigmodel else "openai", self.model,
                    getattr(usage, 'prompt_tokens', 0) if usage else 0,
                    getattr(usage, 'completion_tokens', 0) if usage else 0,
                    duration_ms, True,
                ))
                return content
            except Exception as e:
                last_exception = e
                duration_ms = (time.time() - start) * 1000
                error_str = str(e).lower()
                is_transient = any(k in error_str for k in ["timeout", "429", "503", "connection", "rate limit"])
                if is_transient and attempt < max_retries - 1:
                    wait = 2 ** attempt
                    logger.warning(f"LLM transient error (attempt {attempt+1}/{max_retries}), retrying in {wait}s: {e}")
                    await asyncio.sleep(wait)
                    continue
                asyncio.create_task(asyncio.to_thread(
                    self._log_llm_call, "bigmodel" if self._is_bigmodel else "openai", self.model,
                    0, 0, duration_ms, False, str(e)[:500],
                ))
                raise
        raise last_exception

    async def astream(self, messages: List[Dict[str, Any]], temperature=0.7, max_tokens=1024, thinking: bool = False) -> AsyncIterator[str]:
        """流式调用，关闭 thinking，只输出正式回答 content，含指数退避重试"""
        kwargs: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }
        if self._is_bigmodel:
            kwargs["extra_body"] = {"thinking": {"type": "enabled" if thinking else "disabled"}}

        max_retries = 3
        last_exception = None
        for attempt in range(max_retries):
            start = time.time()
            try:
                response = await self.client.chat.completions.create(**kwargs)
                async for chunk in response:
                    if not chunk or not chunk.choices:
                        continue
                    choice = chunk.choices[0]
                    if not choice or not choice.delta:
                        continue
                    content = choice.delta.content
                    if content:
                        yield content
                duration_ms = (time.time() - start) * 1000
                asyncio.create_task(asyncio.to_thread(
                    self._log_llm_call, "bigmodel" if self._is_bigmodel else "openai", self.model,
                    0, 0, duration_ms, True,
                ))
                return
            except Exception as e:
                last_exception = e
                duration_ms = (time.time() - start) * 1000
                error_str = str(e).lower()
                is_transient = any(k in error_str for k in ["timeout", "429", "503", "connection", "rate limit"])
                if is_transient and attempt < max_retries - 1:
                    wait = 2 ** attempt
                    logger.warning(f"LLM stream transient error (attempt {attempt+1}/{max_retries}), retrying in {wait}s: {e}")
                    await asyncio.sleep(wait)
                    continue
                asyncio.create_task(asyncio.to_thread(
                    self._log_llm_call, "bigmodel" if self._is_bigmodel else "openai", self.model,
                    0, 0, duration_ms, False, str(e)[:500],
                ))
                raise
        raise last_exception


class LLMFactory:
    """大模型工厂 — 统一支持 spark / deepseek / openai / bigmodel / mimo"""

    _cache: Dict[str, BaseLLM] = {}

    # provider -> (settings_api_key, settings_base_url, settings_model)
    _PROVIDER_MAP: Dict[str, tuple] = {
        "bigmodel":  ("BIGMODEL_API_KEY",  "BIGMODEL_BASE_URL",  "BIGMODEL_MODEL"),
        "deepseek":  ("DEEPSEEK_API_KEY",  "DEEPSEEK_BASE_URL",  "DEEPSEEK_MODEL"),
        "openai":    ("OPENAI_API_KEY",    "OPENAI_BASE_URL",    "OPENAI_MODEL"),
        "spark":     ("SPARK_API_KEY",     "SPARK_HTTP_BASE_URL", "SPARK_MODEL"),
        "mimo":      ("MIMO_API_KEY",      "MIMO_BASE_URL",      "MIMO_MODEL"),
    }

    @classmethod
    def get_llm(cls, provider: Optional[str] = None) -> BaseLLM:
        """获取指定提供商的 LLM 实例"""
        provider = (provider or settings.DEFAULT_LLM_PROVIDER).lower().strip()

        if provider in cls._cache:
            return cls._cache[provider]

        mapping = cls._PROVIDER_MAP.get(provider)
        if not mapping:
            raise ValueError(f"Unsupported LLM provider: {provider}. Supported: {', '.join(cls._PROVIDER_MAP.keys())}")

        api_key_attr, base_url_attr, model_attr = mapping
        api_key = getattr(settings, api_key_attr, None) or ""
        if not api_key:
            logger.warning(f"{api_key_attr} is not configured. LLM calls will fail.")

        llm = OpenAICompatibleLLM(
            api_key=api_key,
            base_url=getattr(settings, base_url_attr),
            model=getattr(settings, model_attr),
        )

        cls._cache[provider] = llm
        logger.info(f"LLM provider initialized: {provider} (model={llm.model})")
        return llm

    @classmethod
    def get_default_llm(cls) -> BaseLLM:
        return cls.get_llm(settings.DEFAULT_LLM_PROVIDER)

    @classmethod
    def clear_cache(cls):
        cls._cache.clear()


# 便捷导出
__all__ = ["BaseLLM", "LLMFactory", "OpenAICompatibleLLM"]
