"""
统一大模型调用工厂
当前使用讯飞星火
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
    """OpenAI 兼容接口（智谱AI/DeepSeek/讯飞星火 等）"""

    def __init__(
        self,
        api_key: str,
        base_url: str,
        model: str,
        provider: str = "openai",
        timeout: float = _DEFAULT_TIMEOUT,
    ):
        if AsyncOpenAI is None:
            raise ImportError("openai package is not installed. Please install it to use LLM features.")
        if not api_key:
            raise ValueError(f"API key is required for model {model}")
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url, timeout=timeout)
        self.model = model
        self.provider = provider
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
                    self._log_llm_call, self.provider, self.model,
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
                    self._log_llm_call, self.provider, self.model,
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
                    self._log_llm_call, self.provider, self.model,
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
                    self._log_llm_call, self.provider, self.model,
                    0, 0, duration_ms, False, str(e)[:500],
                ))
                raise
        raise last_exception


class FailoverLLM(BaseLLM):
    """多提供商自动降级包装器：主提供商调用失败后，自动切换到备用提供商重试。

    使用场景：单一 LLM 服务商故障/限流/Key 失效时，系统不中断，自动降级到备用模型。
    每个提供商内部仍有指数退避重试，降级链只在其彻底失败后触发。
    """

    def __init__(self, primary: BaseLLM, fallbacks: List[BaseLLM]):
        self._providers = [primary] + fallbacks

    @property
    def model(self) -> str:
        return self._providers[0].model

    @property
    def provider(self) -> str:
        return self._providers[0].provider

    def __repr__(self):
        chain = " -> ".join(f"{llm.provider}({llm.model})" for llm in self._providers)
        return f"FailoverLLM[{chain}]"

    async def ainvoke(self, messages, temperature=0.7, max_tokens=1024, thinking: bool = False) -> str:
        last_error = None
        for llm in self._providers:
            try:
                return await llm.ainvoke(messages, temperature, max_tokens, thinking)
            except Exception as e:
                last_error = e
                logger.warning(f"LLM provider {llm.provider}({llm.model}) 调用失败，自动降级: {str(e)[:200]}")
        raise last_error

    async def astream(self, messages, temperature=0.7, max_tokens=1024, thinking: bool = False) -> AsyncIterator[str]:
        last_error = None
        for llm in self._providers:
            try:
                async for chunk in llm.astream(messages, temperature, max_tokens, thinking):
                    yield chunk
                return
            except Exception as e:
                last_error = e
                logger.warning(f"LLM provider {llm.provider}({llm.model}) 流式调用失败，自动降级: {str(e)[:200]}")
        raise last_error


class LLMFactory:
    """大模型工厂 — 支持多家提供商注册与自动降级"""

    _cache: Dict[str, BaseLLM] = {}

    # provider -> (settings_api_key, settings_base_url, settings_model)
    _PROVIDER_MAP: Dict[str, tuple] = {
        "spark":     ("SPARK_API_KEY",     "SPARK_HTTP_BASE_URL", "SPARK_MODEL"),
        "deepseek":  ("DEEPSEEK_API_KEY",  "DEEPSEEK_BASE_URL",  "DEEPSEEK_MODEL"),
        "bigmodel":  ("BIGMODEL_API_KEY",  "BIGMODEL_BASE_URL",  "BIGMODEL_MODEL"),
        "openai":    ("OPENAI_API_KEY",    "OPENAI_BASE_URL",    "OPENAI_MODEL"),
        "mimo":      ("MIMO_API_KEY",      "MIMO_BASE_URL",      "MIMO_MODEL"),
    }

    @classmethod
    def is_configured(cls, provider: str) -> bool:
        """该提供商是否已配置 API Key（未配置的不会进入降级链）"""
        mapping = cls._PROVIDER_MAP.get(provider)
        if not mapping:
            return False
        return bool(getattr(settings, mapping[0], None))

    @classmethod
    def get_llm(cls, provider: Optional[str] = None) -> BaseLLM:
        """获取指定提供商的 LLM 实例（不做降级，显式指定提供商时使用）"""
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
            provider=provider,
        )

        cls._cache[provider] = llm
        logger.info(f"LLM provider initialized: {provider} (model={llm.model})")
        return llm

    @classmethod
    def get_default_llm(cls) -> BaseLLM:
        """获取默认 LLM 实例（自动降级链：主提供商 + 所有已配置 Key 的备用提供商）"""
        primary_name = (settings.DEFAULT_LLM_PROVIDER or "spark").lower().strip()
        if primary_name not in cls._PROVIDER_MAP:
            logger.warning(f"DEFAULT_LLM_PROVIDER={primary_name} 未注册，回退到 spark")
            primary_name = "spark"

        if not cls.is_configured(primary_name):
            # 主提供商未配置 Key 时，自动选择第一个已配置的提供商
            configured = [n for n in cls._PROVIDER_MAP if cls.is_configured(n)]
            if not configured:
                raise ValueError(
                    "未配置任何 LLM API Key。请在 .env 中至少配置一项："
                    "SPARK_API_KEY / DEEPSEEK_API_KEY / BIGMODEL_API_KEY / OPENAI_API_KEY / MIMO_API_KEY"
                )
            logger.warning(f"主提供商 {primary_name} 未配置 API Key，自动切换为 {configured[0]}")
            primary_name = configured[0]

        cache_key = f"failover:{primary_name}"
        if cache_key in cls._cache:
            return cls._cache[cache_key]

        primary = cls.get_llm(primary_name)
        fallbacks: List[BaseLLM] = []
        for name in cls._PROVIDER_MAP:
            if name == primary_name:
                continue
            if not cls.is_configured(name):
                logger.info(f"LLM 备用提供商 {name} 未配置 API Key，跳过降级链")
                continue
            try:
                fallbacks.append(cls.get_llm(name))
            except Exception as e:
                logger.warning(f"备用提供商 {name} 初始化失败: {e}")

        llm: BaseLLM
        if fallbacks:
            llm = FailoverLLM(primary, fallbacks)
            logger.info(f"LLM 降级链就绪: {llm}")
        else:
            llm = primary
            logger.info(f"LLM 单提供商模式（无备用）: {primary_name}({primary.model})")

        cls._cache[cache_key] = llm
        return llm

    @classmethod
    def clear_cache(cls):
        cls._cache.clear()


# 便捷导出
__all__ = ["BaseLLM", "LLMFactory", "OpenAICompatibleLLM", "FailoverLLM"]
