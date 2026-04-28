"""
统一大模型调用工厂
当前仅使用智谱AI（BigModel / GLM-4.6v）
为业务层提供一致的调用接口
"""
import json
import re
from abc import ABC, abstractmethod
from typing import AsyncIterator, Dict, Any, List, Optional

from openai import AsyncOpenAI

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
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text, re.IGNORECASE)
        if match:
            try:
                return json.loads(match.group(1).strip())
            except json.JSONDecodeError:
                pass

        match = re.search(r"(\{[\s\S]*\})", text)
        if match:
            try:
                return json.loads(match.group(1).strip())
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
        if not api_key:
            raise ValueError(f"API key is required for model {model}")
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url, timeout=timeout)
        self.model = model
        self._is_bigmodel = "bigmodel" in self.client.base_url.host

    async def ainvoke(self, messages: List[Dict[str, Any]], temperature=0.7, max_tokens=1024, thinking: bool = False) -> str:
        """非流式调用，默认关闭智谱 thinking 以加快响应"""
        kwargs: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }
        # 智谱 GLM-4.6v 支持 thinking 参数：默认禁用深度思考，只有显式开启才启用
        if self._is_bigmodel:
            kwargs["extra_body"] = {"thinking": {"type": "enabled" if thinking else "disabled"}}

        response = await self.client.chat.completions.create(**kwargs)
        msg = response.choices[0].message
        # 只返回正式回答 content，忽略 reasoning_content（思考过程）
        content = msg.content or ""
        return content

    async def astream(self, messages: List[Dict[str, Any]], temperature=0.7, max_tokens=1024, thinking: bool = False) -> AsyncIterator[str]:
        """流式调用，关闭 thinking，只输出正式回答 content"""
        kwargs: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }
        if self._is_bigmodel:
            kwargs["extra_body"] = {"thinking": {"type": "enabled" if thinking else "disabled"}}

        response = await self.client.chat.completions.create(**kwargs)
        async for chunk in response:
            delta = chunk.choices[0].delta
            # 只取 content，不输出 reasoning_content（思考过程）
            content = delta.content
            if content:
                yield content


class LLMFactory:
    """大模型工厂 — 统一支持 spark / deepseek / openai / bigmodel"""

    _cache: Dict[str, BaseLLM] = {}

    # provider -> (settings_api_key, settings_base_url, settings_model, env_var_name)
    _PROVIDER_MAP: Dict[str, tuple] = {
        "bigmodel":  ("BIGMODEL_API_KEY",  "BIGMODEL_BASE_URL",  "BIGMODEL_MODEL"),
        "deepseek":  ("DEEPSEEK_API_KEY",  "DEEPSEEK_BASE_URL",  "DEEPSEEK_MODEL"),
        "openai":    ("OPENAI_API_KEY",    "OPENAI_BASE_URL",    "OPENAI_MODEL"),
        "spark":     ("SPARK_API_KEY",     "SPARK_HTTP_BASE_URL", "SPARK_MODEL"),
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
