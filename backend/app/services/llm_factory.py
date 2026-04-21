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
        max_tokens: int = 4096,
    ) -> str:
        pass

    @abstractmethod
    async def astream(
        self,
        messages: List[Dict[str, Any]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> AsyncIterator[str]:
        pass

    async def generate_json(
        self,
        messages: List[Dict[str, Any]],
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> Dict[str, Any]:
        """强制 JSON 输出"""
        text = await self.ainvoke(messages, temperature, max_tokens)
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

        logger.warning(f"JSON parse failed, returning raw text. Raw: {text[:200]}")
        return {"status": "error", "raw_text": text, "message": "模型未返回合法 JSON"}

    def bind_tools(self, tools: List[Any]):
        return self


class OpenAICompatibleLLM(BaseLLM):
    """OpenAI 兼容接口（智谱AI 等）"""

    def __init__(
        self,
        api_key: str,
        base_url: str,
        model: str,
    ):
        if not api_key:
            raise ValueError(f"API key is required for model {model}")
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self.model = model

    async def ainvoke(self, messages: List[Dict[str, Any]], temperature=0.7, max_tokens=4096, thinking: bool = False) -> str:
        """非流式调用，支持智谱 thinking 深度思考"""
        kwargs: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }
        # 智谱 GLM-4.6v 支持 thinking 参数
        if thinking and "bigmodel" in self.client.base_url.host:
            kwargs["extra_body"] = {"thinking": {"type": "enabled"}}

        response = await self.client.chat.completions.create(**kwargs)
        msg = response.choices[0].message
        # 只返回正式回答内容，隐藏 reasoning_content 思考过程
        return msg.content or ""

    async def astream(self, messages: List[Dict[str, Any]], temperature=0.7, max_tokens=4096, thinking: bool = False) -> AsyncIterator[str]:
        """流式调用，只输出正式回答内容，不输出 reasoning_content"""
        kwargs: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }
        if thinking and "bigmodel" in self.client.base_url.host:
            kwargs["extra_body"] = {"thinking": {"type": "enabled"}}

        response = await self.client.chat.completions.create(**kwargs)
        async for chunk in response:
            delta = chunk.choices[0].delta
            # 过滤掉智谱特有的 reasoning_content，只输出正式回答
            content = delta.content
            if content:
                yield content


class LLMFactory:
    """大模型工厂 — 当前仅支持智谱AI"""

    _cache: Dict[str, BaseLLM] = {}

    @classmethod
    def get_llm(cls, provider: Optional[str] = None) -> BaseLLM:
        """获取指定提供商的 LLM 实例（当前固定 bigmodel）"""
        provider = (provider or settings.DEFAULT_LLM_PROVIDER).lower().strip()

        # 强制映射到 bigmodel
        if provider in ("spark", "deepseek", "openai"):
            logger.warning(f"Provider '{provider}' is not available, falling back to bigmodel")
            provider = "bigmodel"

        # 强制清除任何残留的 spark 缓存
        if "spark" in cls._cache:
            del cls._cache["spark"]

        if provider in cls._cache:
            return cls._cache[provider]

        if provider == "bigmodel":
            llm = OpenAICompatibleLLM(
                api_key=settings.BIGMODEL_API_KEY or "",
                base_url=settings.BIGMODEL_BASE_URL,
                model=settings.BIGMODEL_MODEL,
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

        cls._cache[provider] = llm
        logger.info(f"LLM provider initialized: {provider}")
        return llm

    @classmethod
    def get_default_llm(cls) -> BaseLLM:
        return cls.get_llm(settings.DEFAULT_LLM_PROVIDER)

    @classmethod
    def clear_cache(cls):
        cls._cache.clear()


# 便捷导出
__all__ = ["BaseLLM", "LLMFactory", "OpenAICompatibleLLM"]
