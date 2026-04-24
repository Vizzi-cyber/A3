"""
深入测试 glm-4.6v 模型的完整返回结构
"""
import asyncio, time, sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from openai import AsyncOpenAI
from app.core.config import settings

async def test():
    client = AsyncOpenAI(api_key=settings.BIGMODEL_API_KEY, base_url=settings.BIGMODEL_BASE_URL)
    messages = [
        {"role": "system", "content": "你是一位耐心的学习辅导助手。"},
        {"role": "user", "content": "用一句话解释C语言指针。"},
    ]
    print(f"[TEST] Model: glm-4.6v")
    print(f"[TEST] API Key prefix: {settings.BIGMODEL_API_KEY[:12]}...")
    start = time.time()
    try:
        resp = await client.chat.completions.create(
            model="glm-4.6v",
            messages=messages,
            temperature=0.7,
            max_tokens=256,
            stream=False,
            timeout=30,
        )
        elapsed = time.time() - start
        msg = resp.choices[0].message
        print(f"[PASS] HTTP 200，耗时 {elapsed:.2f}s")
        print(f"[INFO] message.content: '{msg.content}'")
        # 检查是否有 reasoning_content
        reasoning = getattr(msg, 'reasoning_content', None)
        print(f"[INFO] message.reasoning_content: '{reasoning}'")
        # 检查是否有 tool_calls
        tool_calls = getattr(msg, 'tool_calls', None)
        print(f"[INFO] message.tool_calls: {tool_calls}")
        # 完整 message dict
        print(f"[INFO] 完整 message 字段: {list(vars(msg).keys()) if hasattr(msg, '__dict__') else 'N/A'}")
        # 打印原始 response
        print(f"[INFO] raw response: {json.dumps(resp.model_dump(), ensure_ascii=False, indent=2)[:800]}")
    except Exception as e:
        elapsed = time.time() - start
        print(f"[FAIL] 请求失败，耗时 {elapsed:.2f}s")
        print(f"[FAIL] 错误: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(test())
