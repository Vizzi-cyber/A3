"""
测试 glm-4.6v 启用 thinking 参数后的返回结构
"""
import asyncio, time, sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from openai import AsyncOpenAI
from app.core.config import settings

async def test(thinking_enabled=False, max_tokens=256):
    client = AsyncOpenAI(api_key=settings.BIGMODEL_API_KEY, base_url=settings.BIGMODEL_BASE_URL)
    messages = [
        {"role": "system", "content": "你是一位耐心的学习辅导助手。"},
        {"role": "user", "content": "用一句话解释C语言指针。"},
    ]
    kwargs = {
        "model": "glm-4.6v",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": max_tokens,
        "stream": False,
    }
    if thinking_enabled:
        kwargs["extra_body"] = {"thinking": {"type": "enabled"}}

    print(f"\n[TEST] thinking={thinking_enabled}, max_tokens={max_tokens}")
    start = time.time()
    try:
        resp = await client.chat.completions.create(**kwargs)
        elapsed = time.time() - start
        msg = resp.choices[0].message
        content = msg.content or ""
        reasoning = getattr(msg, "reasoning_content", None)
        print(f"[PASS] HTTP 200，耗时 {elapsed:.2f}s, finish_reason={resp.choices[0].finish_reason}")
        print(f"[INFO] content 长度: {len(content)}")
        print(f"[INFO] reasoning_content 长度: {len(reasoning) if reasoning else 0}")
        if content:
            print(f"[INFO] content 前100字: {content[:100]}")
        if reasoning:
            print(f"[INFO] reasoning 前100字: {reasoning[:100]}")
    except Exception as e:
        elapsed = time.time() - start
        print(f"[FAIL] 请求失败，耗时 {elapsed:.2f}s")
        print(f"[FAIL] 错误: {type(e).__name__}: {e}")

async def main():
    await test(thinking_enabled=False, max_tokens=256)
    await test(thinking_enabled=True, max_tokens=256)
    await test(thinking_enabled=True, max_tokens=1024)
    await test(thinking_enabled=False, max_tokens=1024)

if __name__ == "__main__":
    asyncio.run(main())
