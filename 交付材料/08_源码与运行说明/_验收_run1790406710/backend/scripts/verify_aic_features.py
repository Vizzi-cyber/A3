"""
AIC 竞赛功能综合验证脚本
验证 D1/B1/A1-A3/C1/C3/B2 全部新增功能 + 核心接口回归
（LLM 相关用 mock，不消耗真实 API 额度）
运行：cd backend && python scripts/verify_aic_features.py
"""
import sys
import os
import asyncio
from unittest.mock import patch, AsyncMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PASS = 0
FAIL = 0


def check(name: str, cond: bool, detail: str = ""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name} {detail}")


# ---------- mock LLM（避免真实调用） ----------
class FakeLLM:
    async def ainvoke(self, messages, temperature=0.7, max_tokens=1024, thinking=False):
        return "## 模拟分析结果\n这是测试用的模拟响应，验证链路正常。"

    async def astream(self, messages, temperature=0.7, max_tokens=1024, thinking=False):
        yield "模拟流式响应"

    async def generate_json(self, messages, temperature=0.3, max_tokens=1024):
        return {"status": "success", "data": {"test": True}}


def main():
    from fastapi.testclient import TestClient
    from app.main import app
    from app.api.auth import _create_access_token

    print("=" * 60)
    print("AIC 功能综合验证")
    print("=" * 60)

    with TestClient(app) as client:
        student_token = _create_access_token({"sub": "student_001"})
        teacher_token = _create_access_token({"sub": "T001"})
        h_s = {"Authorization": f"Bearer {student_token}"}
        h_t = {"Authorization": f"Bearer {teacher_token}"}

        # ---------- 1. 基础回归 ----------
        print("\n[1] 核心接口回归")
        r = client.get("/api/v1/dashboard/student_001/summary", headers=h_s)
        check("dashboard summary", r.status_code == 200, str(r.status_code))
        r = client.get("/api/v1/knowledge/list?subject=C语言", headers=h_s)
        check("knowledge list", r.status_code == 200, str(r.status_code))
        r = client.get("/api/v1/daily-quiz/daily?count=3&subject=C语言", headers=h_s)
        check("daily quiz", r.status_code == 200, str(r.status_code))

        # ---------- 2. D1: 多模型注册 ----------
        print("\n[2] D1 多模型注册")
        from app.services.llm_factory import LLMFactory
        providers = sorted(LLMFactory._PROVIDER_MAP.keys())
        check("5家provider注册", providers == ["bigmodel", "deepseek", "mimo", "openai", "spark"], str(providers))
        try:
            LLMFactory.get_llm("unknown")
            check("未注册provider报错", False)
        except ValueError:
            check("未注册provider报错", True)

        # ---------- 3. B1: 功能使用频率 ----------
        print("\n[3] B1 功能使用频率")
        r = client.get("/api/v1/monitoring/feature-usage?student_id=student_001", headers=h_s)
        check("学生查自己 200", r.status_code == 200, str(r.status_code))
        r = client.get("/api/v1/monitoring/feature-usage?student_id=student_002", headers=h_s)
        check("学生查他人 403", r.status_code == 403, str(r.status_code))
        r = client.get("/api/v1/monitoring/feature-usage", headers=h_s)
        check("学生查全班 403", r.status_code == 403, str(r.status_code))
        r = client.get("/api/v1/monitoring/feature-usage?days=7", headers=h_t)
        check("教师查全班 200", r.status_code == 200, str(r.status_code))

        # ---------- 4. A2: 学科元数据 ----------
        print("\n[4] A2 学科元数据")
        r = client.get("/api/v1/learning-path/courses", headers=h_s)
        d = r.json()
        check("courses 接口 200", r.status_code == 200, str(r.status_code))
        if r.status_code == 200:
            names = [c["course_id"] for c in d["data"]]
            check("3门课程元数据", names == ["C语言", "电路分析", "STM32嵌入式"], str(names))
            stm32 = next((c for c in d["data"] if c["course_id"] == "STM32嵌入式"), None)
            check("STM32 跨课程关联8条", stm32 and stm32["cross_count"] == 8, str(stm32 and stm32["cross_count"]))

        # ---------- 5. A1/A3: 跨学科路径 ----------
        print("\n[5] A1/A3 跨学科路径")
        r = client.post("/api/v1/learning-path/cross-discipline", headers=h_s, json={
            "student_id": "student_001", "target_kp_id": "kp_s05",
        })
        check("cross-discipline 200", r.status_code == 200, str(r.status_code))
        if r.status_code == 200:
            data = r.json()["data"]
            cd = data["cross_discipline"]
            check("跨3门课", cd["cross_courses"] == ["C语言", "STM32嵌入式", "电路分析"] or len(cd["cross_courses"]) == 3, str(cd["cross_courses"]))
            check("is_cross_discipline=True", cd["is_cross_discipline"] is True)
            chain = data["dependency_chain"]
            check("依赖链含跨课节点", any(k.startswith("kp_e") for k in chain), str(chain))

        # 无环检测
        r = client.post("/api/v1/learning-path/cross-discipline", headers=h_s, json={
            "student_id": "student_001", "target_kp_id": "kp_s14",
        })
        check("kp_s14 路径无环", r.status_code == 200, str(r.status_code))

        # 依赖链接口
        r = client.get("/api/v1/learning-path/dag/dependency-chain/kp_s06", headers=h_s)
        check("依赖链 kp_s06", r.status_code == 200, str(r.status_code))

        # ---------- 6. B2: 实验行为采集 ----------
        print("\n[6] B2 实验行为采集")
        r = client.post("/api/v1/learning-data/experiment", headers=h_s, json={
            "student_id": "student_001", "experiment_type": "stm32_simulate",
            "action": "run", "detail": {"component_count": 5}, "duration": 30,
        })
        check("上报实验 200", r.status_code == 200, str(r.status_code))
        r = client.get("/api/v1/learning-data/experiment-stats?student_id=student_001", headers=h_s)
        check("学生查实验统计 200", r.status_code == 200, str(r.status_code))
        r = client.get("/api/v1/learning-data/experiment-stats", headers=h_s)
        check("学生查全班实验 403", r.status_code == 403, str(r.status_code))
        r = client.get("/api/v1/learning-data/experiment-stats", headers=h_t)
        d = r.json()
        check("教师查全班实验 200", r.status_code == 200 and d.get("total_experiments", 0) >= 1, str(r.status_code))

        # ---------- 7. C1: 电路诊断模式（mock LLM） ----------
        print("\n[7] C1 电路故障诊断")
        with patch("app.api.circuit_analysis.LLMFactory.get_default_llm", return_value=FakeLLM()):
            r = client.post("/api/v1/circuit-analysis/analyze", headers=h_s, json={
                "netlist": [
                    {"name": "V1", "type": "voltage_source", "node1": 0, "node2": 1, "value": 5},
                    {"name": "R1", "type": "resistor", "node1": 1, "node2": 2, "value": 1000},
                    {"name": "R2", "type": "resistor", "node1": 2, "node2": 3, "value": 1000000000},
                ],
                "node_voltages": {"n1": 5.0, "n2": 5.0},
                "is_diagnosis": True,
                "fault_description": "分压电路实测中间节点5V",
                "student_answer": "A. R2 断路",
                "expected_answer": "A. R2 断路",
            })
            check("诊断模式 200", r.status_code == 200, str(r.status_code))
            if r.status_code == 200:
                check("诊断模式标记", r.json().get("mode") == "diagnosis", str(r.json()))
            # 常规模式回归
            r = client.post("/api/v1/circuit-analysis/analyze", headers=h_s, json={
                "netlist": [{"name": "V1", "type": "voltage_source", "node1": 0, "node2": 1, "value": 5}],
            })
            check("常规分析 200", r.status_code == 200, str(r.status_code))

        # ---------- 8. 数据库完整性 ----------
        print("\n[8] 数据库完整性")
        import sqlite3
        conn = sqlite3.connect("ai_learning_v2.db")
        tables = [t[0] for t in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        check("新表存在", all(t in tables for t in ["courses", "experiment_logs"]), str(len(tables)))
        cross = 0
        for r in conn.execute("SELECT kp_id, prerequisites FROM knowledge_points").fetchall():
            import json
            pre = json.loads(r[1]) if r[1] else []
            for p in pre:
                if p[3] != r[0][3]:
                    cross += 1
        check("跨课程依赖9条", cross == 9, str(cross))
        conn.close()

        # ---------- 9. LLM 降级链（patch settings 字段模拟未配置场景） ----------
        print("\n[9] LLM 降级链")
        from app.core.config import settings as _settings
        LLMFactory.clear_cache()
        _orig_spark = _settings.SPARK_API_KEY
        _orig_deepseek = _settings.DEEPSEEK_API_KEY
        try:
            object.__setattr__(_settings, "SPARK_API_KEY", "")   # 主提供商未配置
            object.__setattr__(_settings, "DEEPSEEK_API_KEY", "test-key")  # 备用已配置
            llm = LLMFactory.get_default_llm()
            check("key缺失自动切换", getattr(llm, "provider", "") == "deepseek", str(llm))
            object.__setattr__(_settings, "SPARK_API_KEY", "test-key")
            object.__setattr__(_settings, "DEEPSEEK_API_KEY", "test-key")
            LLMFactory.clear_cache()
            llm = LLMFactory.get_default_llm()
            check("双key降级链", "FailoverLLM" in str(llm) and "deepseek" in str(llm), str(llm))
        finally:
            object.__setattr__(_settings, "SPARK_API_KEY", _orig_spark)
            object.__setattr__(_settings, "DEEPSEEK_API_KEY", _orig_deepseek)
            LLMFactory.clear_cache()

    print("=" * 60)
    print(f"结果: {PASS} 通过, {FAIL} 失败")
    print("=" * 60)
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
