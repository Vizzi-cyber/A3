"""
测试智谱不同模型名称的可用性
"""
import asyncio, time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from openai import AsyncOpenAI
from app.core.config import settings

MODELS = ["glm-4", "glm-4-plus", "glm-4v", "glm-4v-plus", "glm-4-flash", "glm-4.6v"]

async def test_model(client, model):
    messages = [
        {"role": "system", "content": "你是一位耐心的学习辅导助手。"},
        {"role": "user", "content": "用一句话解释C语言指针。"},
    ]
    start = time.time()
    try:
        resp = await client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7,
            max_tokens=128,
            stream=False,
            timeout=25,
        )
        elapsed = time.time() - start
        content = resp.choices[0].message.content or ""
        return model, True, elapsed, content[:100]
    except Exception as e:
        elapsed = time.time() - start
        return model, False, elapsed, str(e)[:100]

async def main():
    client = AsyncOpenAI(api_key=settings.BIGMODEL_API_KEY, base_url=settings.BIGMODEL_BASE_URL)
    print(f"[TEST] Base URL: {settings.BIGMODEL_BASE_URL}\n")
    tasks = [test_model(client, m) for m in MODELS]
    results = await asyncio.gather(*tasks)
    for model, ok, elapsed, info in results:
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] {model:20s} 耗时:{elapsed:5.2f}s  回复:{info}")

if __name__ == "__main__":
    asyncio.run(main())
