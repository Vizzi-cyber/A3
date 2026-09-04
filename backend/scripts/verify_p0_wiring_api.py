"""
P0 算法接线 API 冒烟验证
验证 IRT θ→效果评估、IRT b→学习成本、Thompson Sampling→路径调整 在
真实 FastAPI 链路（注册表 → 依赖注入 → 响应字段）中的表现。
（不消耗真实 LLM 额度；IRT 若因演示库数据不足无法拟合则注入合成引擎兜底）
运行：cd backend && python scripts/verify_p0_wiring_api.py
"""
import sys
import os

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


def main():
    import numpy as np
    from fastapi.testclient import TestClient
    from app.main import app
    from app.api.auth import _create_access_token
    from app.services.algorithm_registry import (
        get_irt_diagnoser, set_irt_diagnoser, get_irt_ability,
    )
    from app.algorithms.irt_diagnoser import IRTDiagnoser

    print("=" * 60)
    print("P0 算法接线 API 冒烟验证")
    print("=" * 60)

    with TestClient(app) as client:
        h_s = {"Authorization": f"Bearer {_create_access_token({'sub': 'student_001'})}"}
        h_t = {"Authorization": f"Bearer {_create_access_token({'sub': 'T001'})}"}

        # ---------- 1. IRT 拟合（教师端，真实演示库；数据不足则注入合成引擎） ----------
        print("\n[1] IRT 拟合与注册表")
        r = client.post("/api/v1/algorithms/irt/fit", headers=h_t, json={"model": "1pl"})
        fit_ok = r.status_code == 200 and r.json().get("status") == "success"
        n_students = 0
        if fit_ok:
            n_students = len(r.json().get("data", {}).get("ability", {}))
            print(f"  演示库拟合: {r.json().get('data', {}).get('n_responses')} 条作答, {n_students} 名学生")
        if not fit_ok or "student_001" not in r.json().get("data", {}).get("ability", {}):
            # 合成数据兜底：保证 student_001 在能力表中，使 IRT 链路可被冒烟
            rng = np.random.default_rng(11)
            rows = []
            for s in ["student_001", "student_002", "student_003", "student_004"]:
                ability = 0.9 if s == "student_001" else 0.4
                for kp, diff in [("kp0", 0.85), ("kp1", 0.55), ("kp2", 0.25)]:
                    p = 0.1 + 0.85 * (0.6 * ability + 0.4 * diff)
                    for _ in range(6):
                        rows.append({"student_id": s, "item_id": kp,
                                     "correct": bool(rng.random() < p)})
            diag = IRTDiagnoser(model="1pl")
            res = diag.fit(rows)
            if res["status"] == "success":
                set_irt_diagnoser(diag)
                fit_ok = True
                print("  演示库数据不足，已注入合成 IRT 引擎（含 student_001）")
        check("IRT 引擎就绪且注册表可读",
              fit_ok and get_irt_diagnoser() is not None and get_irt_diagnoser().is_fitted)
        check("get_irt_ability(student_001) 返回 θ",
              get_irt_ability("student_001") is not None, str(get_irt_ability("student_001")))

        # ---------- 2. 仪表盘：掌握度改用 IRT θ ----------
        print("\n[2] 仪表盘效果评估（dashboard/summary）")
        r = client.get("/api/v1/dashboard/student_001/summary", headers=h_s)
        eff = (r.json().get("algorithm_analysis", {}) or {}).get("effect_evaluation", {}) or {}
        md = eff.get("mastery_detail", {}) or {}
        check("dashboard 返回 mastery_detail", bool(md), str(md))
        check("掌握度来源 = irt_theta_percentile",
              md.get("source") == "irt_theta_percentile", str(md.get("source")))
        check("原始 θ 与加权平均同时输出",
              md.get("irt_theta") is not None and "weighted_average" in md, str(md))

        # ---------- 3. 趋势报告 ----------
        print("\n[3] 趋势报告（trend/report）")
        r = client.get("/api/v1/trend/student_001/report", headers=h_s)
        rep_md = ((r.json().get("data", {}) or {}).get("mastery_detail", {}) or {})
        check("trend report 返回 mastery_detail",
              rep_md.get("source") in ("irt_theta_percentile", "weighted_average"), str(rep_md))

        # ---------- 4. DAG 路径调整：规则先验 → MAB 接管 ----------
        print("\n[4] 路径调整（learning-path/dag/adjust）")
        path = {"stages": [{"stage_no": 1, "title": "核心知识", "type": "adaptive", "hours": 5}]}
        payload = {
            "student_id": "student_001",
            "current_path": path,
            "quiz_result": {"score": 60, "weak_tags": ["指针"]},
            "trend_state": "stable",
        }
        r = client.post("/api/v1/learning-path/dag/adjust", headers=h_s, json=payload)
        data = r.json().get("data", {}) or {}
        check("首轮调整：规则先验选择强化练习",
              data.get("strategy") == "practice_boost" and data.get("strategy_source") == "rule_fallback",
              f"{data.get('strategy')}/{data.get('strategy_source')}")

        # 闭环反馈：连续 4 轮回传「回炉复习」策略高收益 → MAB 预热（4 臂）后接管
        for _ in range(4):
            fb = dict(payload)
            fb["quiz_result"] = {"score": 60, "weak_tags": ["指针"],
                                 "prev_strategy": "review_boost", "reward": 0.9}
            r = client.post("/api/v1/learning-path/dag/adjust", headers=h_s, json=fb)
            assert r.status_code == 200
        fb_free = dict(payload)
        fb_free["quiz_result"] = {"score": 60, "weak_tags": ["指针"]}
        r = client.post("/api/v1/learning-path/dag/adjust", headers=h_s, json=fb_free)
        data = r.json().get("data", {}) or {}
        check("收益反馈后 MAB 接管决策",
              data.get("strategy_source") == "thompson_sampling", str(data.get("strategy_source")))
        check("MAB 选中高收益策略（回炉复习）",
              data.get("strategy") == "review_boost", str(data.get("strategy")))
        check("调整结果含候选集与重编号 stages",
              set(data.get("strategy_candidates", [])) == {"practice_boost", "review_boost"}
              and [s.get("stage_no") for s in data.get("stages", [])] == sorted(
                  s.get("stage_no") for s in data.get("stages", [])), str(data.get("strategy_candidates")))

        # 低分保底：score<50 强制回炉（忽略 MAB）
        low = dict(payload)
        low["quiz_result"] = {"score": 30, "weak_tags": []}
        r = client.post("/api/v1/learning-path/dag/adjust", headers=h_s, json=low)
        data = r.json().get("data", {}) or {}
        check("低分强制回炉（候选集保底）",
              data.get("strategy") == "review_boost"
              and data.get("strategy_candidates") == ["review_boost"],
              str(data.get("strategy_candidates")))

        # ---------- 5. P1 训练端点：GKT / 趋势权重 ----------
        print("\n[5] P1 训练端点（algorithms/gkt/train + trend/train）")
        r = client.post("/api/v1/algorithms/gkt/train", headers=h_t)
        gkt_data = r.json().get("data", {}) or {}
        check("GKT 训练端点（演示库真实快照）",
              r.json().get("status") == "success" and gkt_data.get("students", 0) > 0,
              f"students={gkt_data.get('students')} err={gkt_data.get('message')}")
        r = client.post("/api/v1/algorithms/trend/train", headers=h_t)
        trend_data = r.json().get("data", {}) or {}
        check("趋势权重训练端点（含权重输出）",
              r.json().get("status") == "success" and trend_data.get("weights"),
              f"msg={trend_data.get('message')}")
        r = client.get("/api/v1/algorithms/status", headers=h_t)
        status = (r.json().get("data", {}) or {})
        check("算法状态总览含 gkt/trend_learner",
              "gkt" in status and "trend_learner" in status
              and status["gkt"].get("trained") is True and status["trend_learner"].get("trained") is True,
              str({k: status.get(k) for k in ("gkt", "trend_learner")}))

        # ---------- 6. 匹配探索层 + 收益反馈闭环 ----------
        print("\n[6] 匹配探索（match/resources + feedback）")
        resources = [
            {"resource_id": "doc1", "title": "图文讲义", "type": "document", "kp_tags": ["指针"],
             "content_types": [], "difficulty": "intermediate", "objectives": [], "estimated_duration": 45},
            {"resource_id": "vid1", "title": "视频讲解", "type": "video", "kp_tags": ["指针"],
             "content_types": [], "difficulty": "intermediate", "objectives": [], "estimated_duration": 45},
        ]
        r = client.post("/api/v1/matching/resources", headers=h_s,
                        json={"student_id": "student_001", "resources": resources, "top_k": 5})
        recs = ((r.json().get("data", {}) or {}).get("recommendations", []))
        check("匹配接口返回探索元数据与排序",
              len(recs) == 2 and (r.json().get("data", {}).get("exploration") or {}).get("weight") == 0.15,
              str(r.json().get("data", {}).get("exploration")))
        # 闭环：反馈 video 高收益 ×8 → 预热后 video 排名/得分应被提升
        for _ in range(8):
            client.post("/api/v1/matching/feedback", headers=h_s,
                        json={"student_id": "student_001", "resource_type": "video", "reward": 1.0})
            client.post("/api/v1/matching/feedback", headers=h_s,
                        json={"student_id": "student_001", "resource_type": "document", "reward": 0.1})
        r = client.post("/api/v1/matching/resources", headers=h_s,
                        json={"student_id": "student_001", "resources": resources, "top_k": 5})
        data_m = r.json().get("data", {}) or {}
        score_by_id = {x["resource_id"]: x["match_score"] for x in data_m.get("recommendations", [])}
        check("收益反馈预热后 video 类型得分被提升",
              data_m.get("exploration", {}).get("enabled") is True
              and score_by_id.get("vid1", 0) > score_by_id.get("doc1", 0),
              str(score_by_id))

    print(f"\n结果: {PASS} 通过, {FAIL} 失败")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
