"""
大模型调用测试脚本
支持测试：讯飞星火、DeepSeek、OpenAI

用法:
    cd backend
    python ../scripts/test_llm.py

确保已在 backend/.env 中配置好对应的 API 密钥。
"""
import asyncio
import sys

sys.path.insert(0, "backend")

from app.services.llm_factory import LLMFactory
from app.core.config import settings


async def test_llm():
    provider = settings.DEFAULT_LLM_PROVIDER
    print(f"Current LLM provider: {provider}")

    # 检查密钥是否已配置
    if provider == "spark":
        if not all([settings.SPARK_APP_ID, settings.SPARK_API_KEY, settings.SPARK_API_SECRET]):
            print("[SKIP] 讯飞星火 API 密钥未配置，请在 backend/.env 中填写")
            return
    elif provider == "deepseek":
        if not settings.DEEPSEEK_API_KEY:
            print("[SKIP] DeepSeek API 密钥未配置，请在 backend/.env 中填写")
            return
    elif provider == "openai":
        if not settings.OPENAI_API_KEY:
            print("[SKIP] OpenAI API 密钥未配置，请在 backend/.env 中填写")
            return
    else:
        print(f"[ERROR] 未知的 LLM 提供商: {provider}")
        return

    llm = LLMFactory.get_llm(provider)

    messages = [
        {"role": "system", "content": "你是一位有帮助的教育 AI 助手。"},
        {"role": "user", "content": "请用一句话介绍递归的概念"},
    ]

    print("\n[Test 1] 非流式调用")
    try:
        result = await llm.ainvoke(messages, temperature=0.7)
        print(f"Response: {result[:200]}...")
    except Exception as e:
        print(f"[FAIL] {e}")
        return

    print("\n[Test 2] 流式调用")
    try:
        chunks = []
        async for chunk in llm.astream(messages, temperature=0.7):
            chunks.append(chunk)
            print(chunk, end="", flush=True)
        print("\n")
        print(f"Stream total length: {len(''.join(chunks))}")
    except Exception as e:
        print(f"[FAIL] {e}")
        return

    print("\n[Test 3] JSON 结构化输出")
    json_messages = [
        {"role": "system", "content": "你是一个 JSON 生成器，只输出合法 JSON，不输出任何解释。"},
        {"role": "user", "content": "请生成一个关于递归的学习大纲，返回格式：{\"outline\": [\"...\", \"...\"]}"},
    ]
    try:
        data = await llm.generate_json(json_messages, temperature=0.3)
        print(f"JSON: {data}")
    except Exception as e:
        print(f"[FAIL] {e}")
        return

    print("\n[OK] All LLM tests passed!")


if __name__ == "__main__":
    asyncio.run(test_llm())
