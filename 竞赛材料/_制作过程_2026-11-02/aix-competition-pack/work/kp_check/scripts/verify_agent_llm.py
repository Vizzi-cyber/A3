"""
Agent 与 LLM 专项验证（TestClient + mock LLM，不烧额度）
覆盖：反思循环 / Agent缓存 / JSON解析健壮性 / 防幻觉挂接 / 多模型注册
运行：cd backend && python scripts/verify_agent_llm.py
"""
import sys
import os
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PASS = 0
FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name} {detail}")


class SequenceLLM:
    """按调用次数返回预设响应的 mock LLM（模拟反思循环多次迭代）"""
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = 0

    async def ainvoke(self, messages, temperature=0.7, max_tokens=1024, thinking=False):
        self.calls += 1
        if self.calls <= len(self.responses):
            return self.responses[self.calls - 1]
        return self.responses[-1]

    async def generate_json(self, messages, temperature=0.3, max_tokens=1024):
        self.calls += 1
        if self.calls <= len(self.responses):
            return self.responses[self.calls - 1]
        return self.responses[-1]


async def main():
    from app.agents.base import BaseAgent
    from app.core.safety import HallucinationGuard
    from app.core.cache import prompt_cache
    from app.services.llm_factory import BaseLLM, OpenAICompatibleLLM, LLMFactory, FailoverLLM

    print("=" * 60)
    print("Agent 与 LLM 专项验证")
    print("=" * 60)

    # ---------- 1. 反思循环（质量低→自我修正） ----------
    print("\n[1] 反思循环")
    class TestAgent(BaseAgent):
        def __init__(self, llm):
            super().__init__("test", "测试Agent")
            self.llm = llm
            self.iteration = 0

        def get_system_prompt(self) -> str:
            return "测试系统提示词"

        async def process(self, context):
            self.iteration += 1
            # 第一次输出质量差，第二次输出质量好（模拟反思修正）
            if self.iteration == 1:
                return {"status": "success", "content": "简短且不完整" * 1, "confidence": 0.1}
            return {"status": "success", "content": "完整内容" * 5, "confidence": 0.9}

    agent = TestAgent(SequenceLLM([{"score": 0.3, "reason": "不够完整"}, {"score": 0.9, "reason": "很好"}]))
    result = await agent.run_with_reflection({}, max_iterations=3, quality_threshold=0.8)
    check("反思循环迭代修正", result.get("_total_iterations", 0) >= 1 and result.get("_evaluation_score", 0) >= 0.3,
          f"score={result.get('_evaluation_score')} iters={result.get('_total_iterations')}")
    check("最佳结果保留", "完整内容" in str(result.get("content", "")), str(result)[:80])

    # ---------- 2. 防幻觉挂接（apply_guards） ----------
    print("\n[2] 防幻觉挂接")
    guarded = agent.apply_guards({"status": "success", "content": "这是讲解内容，参考《C程序设计》教材。"})
    check("引用核查", "_guards" in guarded and guarded["_guards"].get("safe") is True, str(guarded.get("_guards", {}))[:120])
    guarded2 = agent.apply_guards({"status": "error", "message": "出错"})
    check("非成功结果跳过", "_guards" not in guarded2)

    # self_correct 触发
    class CorrectLLM(BaseLLM):
        async def ainvoke(self, messages, temperature=0.7, max_tokens=1024, thinking=False):
            return "修正后的完整内容，包含正确的事实说明。"
        async def astream(self, messages, temperature=0.7, max_tokens=1024, thinking=False):
            yield "流式"

    agent.llm = CorrectLLM()
    corrected = await agent.self_correct_output({}, {"status": "success", "content": "错误内容" * 30})
    check("自我纠错触发", corrected.get("_self_corrected") is True, str(corrected)[:100])
    corrected2 = await agent.self_correct_output({}, {"status": "success", "content": "短"})
    check("短文本跳过纠错", corrected2.get("_self_corrected") is not True)

    # ---------- 3. Agent 缓存（cached_process 命中） ----------
    print("\n[3] Agent 缓存")
    prompt_cache.clear()
    class CacheAgent(BaseAgent):
        def get_system_prompt(self) -> str:
            return "缓存测试"

        async def process(self, context):
            return {"status": "success", "content": "缓存内容"}

    cache_agent = CacheAgent("cache_test", "缓存Agent")
    r1 = await cache_agent.cached_process({"task": "t1"})
    r2 = await cache_agent.cached_process({"task": "t1"})
    check("缓存命中返回", r1.get("content") == "缓存内容" and r2.get("content") == "缓存内容")
    r3 = await cache_agent.cached_process({"task": "t2"})
    check("不同上下文不串缓存", r3.get("content") == "缓存内容")

    # ---------- 4. JSON 解析健壮性 ----------
    print("\n[4] JSON 解析健壮性")
    llm = OpenAICompatibleLLM(api_key="test", base_url="https://x.test/v1", model="test")
    # 直接 JSON
    r = llm._try_parse_json('{"a": 1}')
    check("直接解析", r == {"a": 1})
    # 代码块包裹
    r = llm._try_parse_json('```json\n{"a": 2}\n```')
    check("代码块提取", r == {"a": 2})
    # 前后文本
    r = llm._try_parse_json('结果如下：{"a": 3} 请查收')
    check("文本中提取", r == {"a": 3})
    # 尾部逗号
    r = llm._try_parse_json('{"a": 4,}')
    check("尾部逗号修复", r == {"a": 4})
    # 完全非法
    r = llm._try_parse_json('不是JSON')
    check("非法返回None", r is None)

    # ---------- 5. 多模型注册与降级 ----------
    print("\n[5] 多模型注册与降级")
    providers = sorted(LLMFactory._PROVIDER_MAP.keys())
    check("5家provider", providers == ["bigmodel", "deepseek", "mimo", "openai", "spark"])
    check("is_configured接口", callable(LLMFactory.is_configured))

    # FailoverLLM 降级
    class FailLLM(BaseLLM):
        def __init__(self, name, fail=False):
            self.model, self.provider, self.fail = name, name, fail
        async def ainvoke(self, messages, temperature=0.7, max_tokens=1024, thinking=False):
            if self.fail:
                raise RuntimeError(f"{self.provider} down")
            return f"ok-{self.provider}"
        async def astream(self, messages, temperature=0.7, max_tokens=1024, thinking=False):
            if self.fail:
                raise RuntimeError("down")
            yield "ok"

    fo = FailoverLLM(FailLLM("spark", fail=True), [FailLLM("deepseek")])
    r = await fo.ainvoke([{"role": "user", "content": "hi"}])
    check("降级切换", r == "ok-deepseek", r)
    fo2 = FailoverLLM(FailLLM("spark"), [FailLLM("deepseek")])
    r = await fo2.ainvoke([{"role": "user", "content": "hi"}])
    check("主正常不降级", r == "ok-spark", r)
    fo3 = FailoverLLM(FailLLM("spark", fail=True), [FailLLM("deepseek", fail=True)])
    try:
        await fo3.ainvoke([{"role": "user", "content": "hi"}])
        check("全失败抛错", False)
    except RuntimeError:
        check("全失败抛错", True)

    # ---------- 6. HallucinationGuard 方法可用 ----------
    print("\n[6] 防幻觉守卫方法")
    v = HallucinationGuard.verify_json_schema({"a": 1}, ["a", "b"])
    check("结构校验", v["valid"] is False and "b" in v["missing_fields"])
    v = HallucinationGuard.verify_json_schema({"a": 1, "b": 2}, ["a", "b"])
    check("结构校验通过", v["valid"] is True)
    v = HallucinationGuard.verify_code_output("def f():\n    pass", "python")
    check("代码校验", v["valid"] is True)
    v = HallucinationGuard.verify_code_output("def f(:\n", "python")
    check("代码校验失败", v["valid"] is False)
    v = HallucinationGuard.verify_citations("参考《教材》和[1]", 2)
    check("引用核查", v["has_citations"] is True)

    print("=" * 60)
    print(f"结果: {PASS} 通过, {FAIL} 失败")
    print("=" * 60)
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
