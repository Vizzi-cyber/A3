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

        # ---------- 7. 第二轮接线：auth/refresh、FSRS→路径、排行榜六维、反思循环 ----------
        print("\n[7] 第二轮接线（auth/refresh + FSRS→路径复习阶段 + 排行榜六维 + 反思循环）")

        # 7.1 JWT 滑动续期
        r = client.post("/api/v1/auth/refresh", headers=h_s)
        new_token = (r.json() or {}).get("access_token")
        check("POST /auth/refresh 换发新 token",
              r.status_code == 200 and bool(new_token), str(r.status_code))
        r2 = client.get("/api/v1/auth/me",
                        headers={"Authorization": f"Bearer {new_token}"} if new_token else {})
        check("刷新后的 token 可通过认证",
              r2.status_code == 200 and r2.json().get("data", {}).get("student_id") == "student_001",
              str(r2.status_code))
        r3 = client.post("/api/v1/auth/refresh")
        check("无凭据调用 refresh 返回 401", r3.status_code == 401, str(r3.status_code))

        # 7.2 FSRS 到期复习 → DAG 路径头部复习阶段
        from app.models.database import SessionLocal
        from app.models.memory import MemoryCardModel
        from app.models.knowledge import KnowledgePointModel
        from app.algorithms.memory_scheduler import FSRSMemoryScheduler

        db = SessionLocal()
        inserted = False
        try:
            all_kps = [k.kp_id for k in db.query(KnowledgePointModel.kp_id).all()]
            existing_kps = {
                r[0] for r in db.query(MemoryCardModel.kp_id)
                .filter(MemoryCardModel.student_id == "student_001").all()
            }
            # 选一个该生还没有记忆卡的知识点做到期卡，避免撞 (student_id, kp_id) 唯一约束
            free_kps = [k for k in all_kps if k not in existing_kps]
            if len(free_kps) >= 1 and len(all_kps) >= 2:
                due_kp = free_kps[0]
                target_kp = next(k for k in all_kps if k != due_kp)
                sched = FSRSMemoryScheduler()
                sched.create_card("student_001", due_kp)  # 新卡立即到期
                db.add(MemoryCardModel(
                    student_id="student_001", kp_id=due_kp,
                    card_json=sched.get_card_json("student_001", due_kp) or "{}",
                ))
                db.commit()
                inserted = True

                payload = {
                    "student_id": "student_001",
                    "target_kp_id": target_kp,
                    # 除目标外全部标记已掌握 → 学习阶段不含 due_kp，复习阶段应出现在头部
                    "mastery_map": {k: 0.95 for k in all_kps if k != target_kp} | {target_kp: 0.3},
                }
                r = client.post("/api/v1/learning-path/dag/generate", headers=h_s, json=payload)
                stages = ((r.json().get("data", {}) or {}).get("stages", []))
                check("FSRS 到期卡 → /dag/generate 路径头部含复习阶段",
                      r.status_code == 200 and stages
                      and stages[0].get("type") == "review"
                      and stages[0].get("review_source") == "fsrs_due"
                      and due_kp in stages[0].get("kp_ids", []),
                      f"status={r.status_code} stages={[s.get('type') for s in stages]}")
                check("复习阶段后各阶段 stage_no 重编号连续",
                      [s.get("stage_no") for s in stages] == list(range(1, len(stages) + 1)),
                      str([s.get("stage_no") for s in stages]))
        finally:
            if inserted:
                db.query(MemoryCardModel).filter(
                    MemoryCardModel.student_id == "student_001", MemoryCardModel.kp_id == due_kp
                ).delete()
                db.commit()
            db.close()

        # 7.3 排行榜六维真实计算
        for dim in ("ai_collab", "improvement"):
            r = client.get(f"/api/v1/gamification-challenge/leaderboard/{dim}?period=all", headers=h_s)
            body = r.json() or {}
            check(f"排行榜维度 {dim} 后端真实计算",
                  body.get("status") == "success"
                  and body.get("data", {}).get("dimension") == dim
                  and isinstance(body.get("data", {}).get("entries"), list),
                  f"status={r.status_code} body={str(body)[:120]}")
        r = client.get("/api/v1/gamification-challenge/leaderboard/unknown_dim?period=all", headers=h_s)
        check("未知排行榜维度返回 error", r.json().get("status") == "error", str(r.json().get("status")))

        # 7.4 反思循环（REFLECTION_ENABLED 开启时 evaluate-code 走 run_with_reflection）
        from unittest.mock import patch as mock_patch
        from app.core.config import settings as app_settings
        from app.api import result_evaluator as re_mod

        orig_llm = re_mod._evaluator_agent.llm
        re_mod._evaluator_agent.llm = None  # 冒烟不消耗真实 LLM 额度，规则评估兜底
        try:
            payload = {
                "code_submission": {"file_name": "main.c", "code": "int main(){return 0;}",
                                    "student_id": "student_001"},
                "language": "C",
            }
            r = client.post("/api/v1/result-evaluator/evaluate-code", headers=h_s, json=payload)
            check("REFLECTION_ENABLED=false 时 evaluate-code 走原路径（无反思字段）",
                  r.status_code == 200 and "_iteration" not in r.json(), str(r.status_code))
            with mock_patch.object(app_settings, "REFLECTION_ENABLED", True):
                r = client.post("/api/v1/result-evaluator/evaluate-code", headers=h_s, json=payload)
                body = r.json() or {}
                check("REFLECTION_ENABLED=true 时走反思循环（跑满迭代并输出总轮数）",
                      r.status_code == 200
                      and body.get("_total_iterations") == app_settings.REFLECTION_MAX_ITERATIONS,
                      f"total={body.get('_total_iterations')} keys={sorted(list(body.keys()))[:8]}")
        finally:
            re_mod._evaluator_agent.llm = orig_llm

        # ---------- 8. 第三轮修复：安全/越权/契约 ----------
        print()
        print("[8] 第三轮修复（排行榜quiz_score/越权防护/契约对齐/答案剥离/NCD/反思日志）")

        # 8.1 quiz_score 排行榜（原 QuizResultModel.id 引用不存在列恒 500）
        r = client.get("/api/v1/gamification-challenge/leaderboard/quiz_score?period=all", headers=h_s)
        body = r.json() or {}
        check("quiz_score 排行榜修复（原 count(id) 500）",
              r.status_code == 200 and body.get("status") == "success"
              and isinstance(body.get("data", {}).get("entries"), list),
              f"status={r.status_code}")

        # 8.2 tutor 越权提问防护
        r = client.post("/api/v1/tutor/ask", headers=h_s,
                        json={"student_id": "student_002", "question": "test", "rag_active": False})
        check("tutor /ask 代他人提问返回 403", r.status_code == 403, str(r.status_code))

        # 8.3 tutor 会话历史本人过滤
        r = client.get("/api/v1/tutor/session/student_002_default/history", headers=h_s)
        msgs = ((r.json() or {}).get("messages", []))
        check("tutor 会话历史只返回本人记录", r.status_code == 200 and msgs == [], str(len(msgs)))

        # 8.4 qa-feedback 契约（原必填 query 参数 + 字段不一致恒 422）
        r = client.post("/api/v1/tutor/qa-feedback/999999", headers=h_s, json={})
        check("qa-feedback 缺 rating 返回 422（body 契约生效）", r.status_code == 422, str(r.status_code))
        r = client.post("/api/v1/tutor/qa-feedback/999999", headers=h_s, json={"rating": "meh"})
        check("qa-feedback rating 非法值返回 422", r.status_code == 422, str(r.status_code))

        # 8.5 assignment 答案剥离
        questions = [{"q_id": "q1", "text": "1+1=?", "options": ["1", "2"], "correct_answer": "2"}]
        r = client.post("/api/v1/assignment/create", headers=h_t,
                        json={"title": "验证作业", "subject": "C语言", "questions": questions})
        aid = (r.json() or {}).get("assignment_id")
        r_s = client.get("/api/v1/assignment/" + aid, headers=h_s)
        qs_s = ((r_s.json() or {}).get("assignment", {}).get("questions", []))
        check("学生读作业不见 correct_answer", bool(qs_s) and "correct_answer" not in qs_s[0], str(qs_s))
        r_t = client.get("/api/v1/assignment/" + aid, headers=h_t)
        qs_t = ((r_t.json() or {}).get("assignment", {}).get("questions", []))
        check("教师读作业可见 correct_answer", bool(qs_t) and qs_t[0].get("correct_answer") == "2", str(qs_t))

        # 8.6 自我加分入口关闭
        r = client.post("/api/v1/gamification/points/add", headers=h_s,
                        json={"student_id": "student_001", "points": 100, "reason": "cheat"})
        check("学生调用 /points/add 返回 403", r.status_code == 403, str(r.status_code))

        # 8.7 NCD 接线
        r = client.post("/api/v1/algorithms/ncd/fit", headers=h_t)
        check("NCD /ncd/fit 训练成功（演示库真实作答）",
              r.status_code == 200 and r.json().get("status") == "success", str(r.status_code))
        r = client.get("/api/v1/algorithms/status", headers=h_t)
        check("算法状态总览含 ncd 且已拟合",
              (r.json().get("data", {}).get("ncd", {}) or {}).get("fitted") is True,
              str(r.json().get("data", {}).get("ncd")))
        r = client.get("/api/v1/algorithms/ncd/ability/student_001", headers=h_t)
        check("NCD 能力查询端点可用（原重启后恒 409）", r.status_code == 200, str(r.status_code))

        # 8.8 学习日志日期正则修复（原双反斜杠正则永不匹配，创建整体 422）
        import datetime as _dt
        today = _dt.date.today().isoformat()
        r = client.post("/api/v1/log-reflection/logs/upsert", headers=h_s,
                        json={"student_id": "student_001", "date": today, "total_duration": 30,
                              "kp_count": 1, "quiz_count": 0, "avg_score": 0,
                              "mistakes": [], "path_progress": 0.1,
                              "completed_tasks": [], "timeline": []})
        check("学习日志创建（日期正则修复）", r.status_code == 200, str(r.status_code) + " " + str(r.json())[:80])


    print(f"\n结果: {PASS} 通过, {FAIL} 失败")
    sys.exit(1 if FAIL else 0)



if __name__ == "__main__":
    main()
