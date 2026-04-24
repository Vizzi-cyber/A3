"""
直接测试智谱 GLM 大模型 API 连通性
"""
import asyncio, time, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from openai import AsyncOpenAI
from app.core.config import settings

async def test():
    client = AsyncOpenAI(
        api_key=settings.BIGMODEL_API_KEY,
        base_url=settings.BIGMODEL_BASE_URL,
    )
    messages = [
        {"role": "system", "content": "你是一位耐心的学习辅导助手。"},
        {"role": "user", "content": "用一句话解释C语言指针是什么。"},
    ]
    print(f"[TEST] Calling {settings.BIGMODEL_MODEL} at {settings.BIGMODEL_BASE_URL}")
    start = time.time()
    try:
        resp = await client.chat.completions.create(
            model=settings.BIGMODEL_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=256,
            stream=False,
            timeout=30,  # openai 内部超时
        )
        elapsed = time.time() - start
        content = resp.choices[0].message.content or ""
        print(f"[PASS] 请求成功，耗时 {elapsed:.2f}s")
        print(f"[PASS] 回复: {content[:200]}")
    except Exception as e:
        elapsed = time.time() - start
        print(f"[FAIL] 请求失败，耗时 {elapsed:.2f}s")
        print(f"[FAIL] 错误: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(test())
