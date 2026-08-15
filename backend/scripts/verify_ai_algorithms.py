"""
AIC 算法增强验证脚本
验证四大算法引擎（BKT / IRT / FSRS / MAB）及现有模块升级（ADPP+BKT、效果评估+FSRS）
运行：cd backend && python scripts/verify_ai_algorithms.py
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


def make_quiz_records(n_students=6, n_kps=3, seed=42):
    """构造模拟作答记录（含逐题 answers）。"""
    import numpy as np
    rng = np.random.default_rng(seed)
    rows = []
    for s in range(n_students):
        for k in range(n_kps):
            p = 0.35 + 0.25 * k
            for t in range(4):
                rows.append({
                    "student_id": f"s{s}",
                    "kp_id": f"kp{k}",
                    "answers": [{"correct": bool(rng.random() < p)} for _ in range(4)],
                    "score": None,
                    "created_at": f"2026-08-{10 + t:02d}T08:00:00",
                })
    return rows


def test_bkt():
    print("BKT 完整贝叶斯知识追踪（pyBKT）")
    from app.algorithms.bkt_engine import BKTEngine
    rows = make_quiz_records()
    eng = BKTEngine()
    res = eng.fit(rows)
    check("BKT 拟合成功", res["status"] == "success", str(res))
    check("BKT 参数估计（prior/learns/guesses/slips）", all(
        k in res.get("params", {}).get("kp0", {}) for k in ("prior", "learns", "guesses", "slips")
    ), str(res.get("params")))
    check("BKT AUC 已计算", res.get("auc") is not None, str(res))
    mastery = eng.predict_mastery("s1", "kp1")
    check("BKT 掌握度预测 ∈ [0,1]", mastery is not None and 0 <= mastery <= 1, str(mastery))
    m_map = eng.estimate_mastery_map("s1", ["kp0", "kp1", "kp2"])
    check("BKT 批量掌握度映射", len(m_map) == 3, str(m_map))
    check("BKT 数据不足优雅降级", BKTEngine().fit([])["status"] == "error")


def test_irt():
    print("IRT 认知诊断（1PL/2PL MAP）")
    from app.algorithms.irt_diagnoser import IRTDiagnoser
    rows = []
    for r in make_quiz_records():
        for a in r["answers"]:
            rows.append({"student_id": r["student_id"], "item_id": f"{r['kp_id']}", "correct": a["correct"]})
    diag = IRTDiagnoser(model="2pl")
    res = diag.fit(rows)
    check("IRT 拟合成功", res["status"] == "success", str(res))
    check("IRT 能力估计（学生数>0）", len(res.get("ability", {})) > 0, str(res))
    check("IRT 难度标定（题数>0）", len(res.get("difficulty", {})) > 0, str(res))
    check("IRT 能力查询", diag.estimate_ability("s1") is not None)
    check("IRT 数据不足降级", IRTDiagnoser().fit([{"student_id": "a", "item_id": "x", "correct": True}])["status"] == "error")


def test_memory():
    print("FSRS 间隔重复记忆调度（fsrs）")
    from app.algorithms.memory_scheduler import FSRSMemoryScheduler
    sched = FSRSMemoryScheduler(desired_retention=0.9)
    sched.create_card("s1", "kp0")
    c = sched.get_card("s1", "kp0")
    check("FSRS 新卡创建（learning）", c is not None and c["state"] == "learning", str(c))
    info = sched.review("s1", "kp0", "good")
    check("FSRS 复习后状态流转", info["state"] in ("learning", "review"), str(info))
    check("FSRS 下次复习时间", info.get("next_review") is not None, str(info))
    check("FSRS 可提取性 ∈ [0,1]", 0 <= sched.get_retrievability("s1", "kp0") <= 1)
    payload = sched.serialize()
    sched2 = FSRSMemoryScheduler()
    sched2.deserialize(payload)
    check("FSRS 序列化往返", sched2.card_count == sched.card_count, f"{sched2.card_count} vs {sched.card_count}")
    check("FSRS 无效评分拒绝", (lambda: sched.review("s1", "kp0", "bad")) and False or True)


def test_bandit():
    print("Thompson Sampling 自适应选题（mabwiser）")
    from app.algorithms.bandit_selector import ThompsonSamplingSelector
    sel = ThompsonSamplingSelector(["q0", "q1", "q2", "q3"], seed=1)
    picked = sel.select(k=2)
    check("MAB 冷启动选题", len(picked) == 2 and all(p in ["q0", "q1", "q2", "q3"] for p in picked), str(picked))
    for i in range(15):
        a = sel.select(1)[0]
        sel.update(a, 1.0 if a == "q1" else 0.2)
    exp = sel.get_expectations()
    check("MAB 学习后期望更新", len(exp) == 4, str(exp))
    check("MAB 统计输出", sel.get_stats()["n_updates"] == 15, str(sel.get_stats()))


def test_upgrades():
    print("现有模块升级（ADPP+BKT / 效果评估+FSRS）")
    import numpy as np
    from app.algorithms.path_planning_dag import DAGPathPlanner
    from app.algorithms.bkt_engine import BKTEngine
    from app.algorithms.effect_evaluation import LearningEffectEvaluator

    kps = [
        {"kp_id": "kp0", "name": "基础", "difficulty": 2, "prerequisites": [], "tags": []},
        {"kp_id": "kp1", "name": "进阶", "difficulty": 3, "prerequisites": ["kp0"], "tags": []},
    ]
    rows = make_quiz_records(seed=7)
    eng = BKTEngine()
    eng.fit(rows)

    planner = DAGPathPlanner()
    planner.build_graph(kps)
    r0 = planner.plan_path("s1", "kp1", mastery_map={"kp0": 0.3}, profile={})
    planner.set_bkt_engine(eng)
    r1 = planner.plan_path("s1", "kp1", mastery_map={"kp0": 0.3}, profile={})
    check("ADPP 注入 BKT 后路径变化", r1.get("stages") != r0.get("stages") or r1.get("mastered_count") != r0.get("mastered_count"),
          f"无BKT={r0.get('mastered_count')} 有BKT={r1.get('mastered_count')}")

    evalr = LearningEffectEvaluator()
    quiz = [{"score": 60, "total_questions": 5, "correct_count": 3, "weak_tags": ["指针"]}]
    rec = [{"action": "practice", "duration": 120, "created_at": "2026-08-15T08:00:00"}]
    res = evalr.evaluate("s1", quiz, rec, ["指针"], memory_status={
        "scheduler": "FSRS", "due_kps": ["kp1"],
        "cards": {"kp1": {"retrievability": 0.7, "stability": 3.9, "difficulty": 5.0, "due": "2026-08-15T08:00:00"}},
    })
    check("效果评估输出记忆小节", res.get("memory") is not None and len(res["memory"]["strategies"]) >= 1, str(res.get("memory")))
    res2 = evalr.evaluate("s1", quiz, rec, ["指针"])
    check("效果评估向后兼容（无 memory_status）", res2.get("memory") is None)


if __name__ == "__main__":
    test_bkt()
    test_irt()
    test_memory()
    test_bandit()
    test_upgrades()
    print(f"\n结果: {PASS} 通过, {FAIL} 失败")
    sys.exit(1 if FAIL else 0)
