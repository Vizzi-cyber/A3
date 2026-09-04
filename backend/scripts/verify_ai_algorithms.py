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
    try:
        sched.review("s1", "kp0", "bad")
        raised = False
    except ValueError:
        raised = True
    check("FSRS 无效评分拒绝（抛 ValueError）", raised)
    sched2.deserialize("{corrupted json")
    check("FSRS 反序列化损坏负载不崩溃", sched2.card_count == sched.card_count)


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


def test_gkt():
    print("GKT 图知识追踪（图卷积掌握度传播）")
    from app.algorithms.gkt_engine import GKTEngine
    kps = ["kp0", "kp1", "kp2"]
    edges = [("kp0", "kp1"), ("kp1", "kp2")]
    gkt = GKTEngine(alpha=0.6, hops=2)
    gkt.build_graph(kps, edges)
    check("GKT 建图后可传播（未训练 is_fitted=False）",
          gkt.is_fitted is False and gkt.propagate({"kp0": 0.5, "kp1": 0.5, "kp2": 0.5}) is not None)
    base = {"kp0": 0.8, "kp1": 0.5, "kp2": 0.2}
    out = gkt.propagate(base)
    check("GKT 传播输出 ∈ [0,1]", all(0 <= v <= 1 for v in out.values()), str(out))
    # 单调性：邻居 kp0 掌握度升高 → 相邻 kp1 的图感知掌握度升高
    boosted = dict(base, kp0=1.0)
    out_boost = gkt.propagate(boosted)
    check("GKT 传播单调性（邻居提升→目标提升）", out_boost["kp1"] > out["kp1"],
          f"{out['kp1']} → {out_boost['kp1']}")
    # α 融合：alpha=1 时保持自身掌握度（图影响权重为 0）
    gkt3 = GKTEngine(alpha=1.0, hops=1)
    gkt3.build_graph(kps, edges)
    out3 = gkt3.propagate(base)
    check("GKT α=1 时保持自身值", all(abs(out3[k] - base[k]) < 1e-6 for k in kps), str(out3))
    # 未拟合引擎回退：原样返回输入
    same = GKTEngine().propagate(base)
    check("GKT 未拟合回退原掌握度", same == base, str(same))


def test_ncd():
    print("NCD 神经认知诊断（numpy 单调约束）")
    import numpy as np
    from app.algorithms.ncd_diagnoser import NCDDiagnoser
    rng = np.random.default_rng(3)
    # 构造强/弱学生 × 易/难题（能力与难度均单调）
    records = []
    for s, ability in [("strong", 0.95), ("weak", 0.15)]:
        for it, diff in [("easy", 0.95), ("hard", 0.2)]:
            p = 0.1 + 0.85 * (0.6 * ability + 0.4 * diff)
            for _ in range(40):
                records.append({"student_id": s, "item_id": it,
                                "correct": bool(rng.random() < p)})
    diag = NCDDiagnoser(dim=4, epochs=600, seed=42)
    res = diag.fit(records)
    check("NCD 拟合成功", res.get("status") == "success", str(res))
    check("NCD loss 收敛（优于随机 0.693）", res.get("final_loss", 1.0) < 0.65, str(res.get("final_loss")))
    check("NCD 单调约束（w ≥ 0）", res.get("monotone_w_ok") is True
          and all(x >= 0 for x in res.get("monotone_w", [])), str(res.get("monotone_w")))
    p_easy = diag.predict("strong", "easy")
    p_hard = diag.predict("strong", "hard")
    check("NCD 难度排序（同学生：易题>难题）", p_easy is not None and p_hard is not None and p_easy > p_hard,
          f"{p_easy} vs {p_hard}")
    p_strong = diag.predict("strong", "easy")
    p_weak = diag.predict("weak", "easy")
    check("NCD 能力排序（同题目：强生>弱生）", p_strong is not None and p_weak is not None and p_strong > p_weak,
          f"{p_strong} vs {p_weak}")
    a_s, a_w = diag.estimate_ability("strong"), diag.estimate_ability("weak")
    check("NCD 能力估计排序", a_s is not None and a_w is not None and a_s > a_w, f"{a_s} vs {a_w}")
    check("NCD 未知查询返回 None", diag.predict("ghost", "easy") is None
          and diag.estimate_difficulty("ghost") is None)
    check("NCD 数据不足降级", NCDDiagnoser().fit(
        [{"student_id": "a", "item_id": "x", "correct": True}])["status"] == "error")


def test_p0_wiring():
    print("P0 算法接线（IRT→效果评估 / IRT→学习成本 / MAB→路径调整）")
    import math
    import numpy as np
    from app.algorithms.effect_evaluation import LearningEffectEvaluator
    from app.algorithms.irt_diagnoser import IRTDiagnoser
    from app.algorithms.path_planning_dag import DAGPathPlanner
    from app.algorithms.bandit_selector import ThompsonSamplingSelector

    # --- IRT θ → effect_evaluation ---
    evalr = LearningEffectEvaluator()
    quiz = [{"score": 60, "total_questions": 5, "correct_count": 3, "weak_tags": []}]
    r_plain = evalr.evaluate("s1", quiz, [], [])
    check("效果评估默认掌握度来源=weighted_average",
          r_plain["mastery_detail"]["source"] == "weighted_average", str(r_plain["mastery_detail"]))
    theta = 1.0
    r_irt = evalr.evaluate("s1", quiz, [], [], irt_ability=theta)
    expected = 0.5 * (1 + math.erf(theta / math.sqrt(2))) * 100
    check("IRT θ 接管掌握度（Φ(θ)·100）",
          r_irt["mastery_detail"]["source"] == "irt_theta_percentile"
          and abs(r_irt["realtime_metrics"]["mastery"] - expected) < 0.01,
          str(r_irt["mastery_detail"]))
    check("mastery_detail 保留原始 θ 与加权平均对照",
          r_irt["mastery_detail"]["irt_theta"] == 1.0
          and r_irt["mastery_detail"]["weighted_average"] == 60.0, str(r_irt["mastery_detail"]))
    check("θ 单调性（θ↑ → 掌握度↑）",
          evalr.evaluate("s1", quiz, [], [], irt_ability=0.0)["realtime_metrics"]["mastery"]
          < r_irt["realtime_metrics"]["mastery"])

    # --- IRT b → path_planning_dag 学习成本 ---
    kps = [
        {"kp_id": "kpA", "name": "易", "difficulty": 3, "prerequisites": [], "tags": []},
        {"kp_id": "kpB", "name": "难", "difficulty": 3, "prerequisites": [], "tags": []},
    ]
    diag = IRTDiagnoser(model="1pl")
    rng = np.random.default_rng(5)
    # 注意：build_response_matrix 对每对（学生,题目）只保留最后一次作答，
    # 故每个学生每题只构造一条记录，保证题目正确率差异可被标定
    rows = []
    for s in range(12):
        rows.append({"student_id": f"s{s}", "item_id": "kpA", "correct": bool(rng.random() < 0.85)})
        rows.append({"student_id": f"s{s}", "item_id": "kpB", "correct": bool(rng.random() < 0.25)})
    fit_res = diag.fit(rows)
    check("IRT 拟合用于成本模型", fit_res.get("status") == "success", str(fit_res))
    b_a, b_b = diag.get_item_difficulty("kpA"), diag.get_item_difficulty("kpB")
    check("IRT b 排序（易题 b < 难题 b）", b_a is not None and b_b is not None and b_a < b_b,
          f"{b_a} vs {b_b}")

    profile = {"weak_areas": [], "learning_tempo": {"study_speed": "moderate"}}
    planner = DAGPathPlanner()
    planner.build_graph(kps)
    zero_mastery = {"kpA": 0.0, "kpB": 0.0}
    c0a = planner._compute_learning_cost("kpA", zero_mastery, profile)
    c0b = planner._compute_learning_cost("kpB", zero_mastery, profile)
    check("无 IRT 时同级知识点成本相等（人工3级）", abs(c0a - c0b) < 1e-9, f"{c0a} vs {c0b}")
    planner.set_irt_diagnoser(diag)
    c1a = planner._compute_learning_cost("kpA", zero_mastery, profile)
    c1b = planner._compute_learning_cost("kpB", zero_mastery, profile)
    check("注入 IRT 后易题（b<0）成本下降", c1a < c0a, f"{c0a} → {c1a}")
    check("注入 IRT 后难题（b>0）成本上升", c1b > c0b, f"{c0b} → {c1b}")
    plan_res = planner.plan_path("s1", "kpB", zero_mastery, profile)
    check("plan_path 在 IRT 注入下正常出路径",
          plan_res.get("status") == "success" and plan_res.get("stages"), str(plan_res.get("status")))

    # --- MAB → adjust_path ---
    from app.algorithms.path_planning_dag import STRATEGY_ARMS
    path = {"stages": [{"stage_no": 1, "title": "核心", "type": "adaptive", "hours": 5}]}
    quiz60 = {"score": 60, "weak_tags": ["指针"]}
    planner2 = DAGPathPlanner()
    r_rule = planner2.adjust_path(path, quiz60, "stable")
    check("adjust_path 输出策略与来源（规则先验）",
          r_rule.get("strategy") == "practice_boost" and r_rule.get("strategy_source") == "rule_fallback"
          and set(r_rule.get("strategy_candidates", [])) == {"practice_boost", "review_boost"},
          str(r_rule.get("strategy")))
    bandit = ThompsonSamplingSelector(STRATEGY_ARMS, seed=1)
    check("MAB 选择器 is_warm 冷启动判定", bandit.is_warm is False)
    r_cold = planner2.adjust_path(path, quiz60, "stable", bandit_selector=bandit)
    check("MAB 冷启动回退规则先验", r_cold.get("strategy_source") == "rule_fallback",
          str(r_cold.get("strategy_source")))
    # 反馈收益（回炉策略收益最高）达到臂数后 MAB 接管
    for _ in range(4):
        bandit.update("review_boost", 0.9)
        bandit.update("practice_boost", 0.2)
    check("MAB 预热后 is_warm 置位", bandit.is_warm is True)
    r_mab = planner2.adjust_path(path, quiz60, "stable", bandit_selector=bandit)
    check("MAB 接管策略选择", r_mab.get("strategy_source") == "thompson_sampling",
          str(r_mab.get("strategy_source")))
    check("MAB 期望排序选中高收益策略", r_mab.get("strategy") == "review_boost",
          str(r_mab.get("strategy")))
    # ≥90 且趋势上升档：MAB 可在 accelerate/maintain 间决策（maintain 必须是臂）
    quiz95 = {"score": 95, "weak_tags": []}
    for _ in range(4):
        bandit.update("accelerate", 0.1)
        bandit.update("maintain", 0.9)
    r_top = planner2.adjust_path(path, quiz95, "growth", bandit_selector=bandit)
    check("高分档 MAB 可选中 maintain（候选集不退化）",
          r_top.get("strategy") == "maintain" and r_top.get("strategy_source") == "thompson_sampling",
          f"{r_top.get('strategy')}/{r_top.get('strategy_source')}")
    # 分数段保底：<50 强制回炉（无采样空间）
    r_low = planner2.adjust_path(path, {"score": 30, "weak_tags": []}, "stable", bandit_selector=bandit)
    check("低分强制回炉（候选集保底）",
          r_low.get("strategy") == "review_boost" and r_low.get("strategy_candidates") == ["review_boost"],
          str(r_low.get("strategy_candidates")))
    check("record_strategy_reward 未注入时安全返回 False",
          planner2.record_strategy_reward("accelerate", 0.8) is False)
    p3 = DAGPathPlanner()
    p3.set_strategy_bandit(bandit)
    check("record_strategy_reward 注入后反馈生效", p3.record_strategy_reward("accelerate", 0.8) is True)
    # 非法 score 类型不崩溃（回退 0 分 → 强制回炉）
    r_bad = planner2.adjust_path(path, {"score": "abc", "weak_tags": []}, "stable")
    check("非法 score 类型安全回退", r_bad.get("strategy") == "review_boost", str(r_bad.get("strategy")))


def test_robustness():
    print("算法加固（None 容忍 / 空串守卫 / registry 闭环）")
    from app.algorithms.trend_analysis import MultiFactorTrendAnalyzer
    from app.algorithms.weighted_matching import MultiDimWeightedMatcher
    from app.services.algorithm_registry import (
        update_strategy_bandit, get_strategy_bandit, attach_irt_to_planner,
    )
    from app.algorithms.path_planning_dag import DAGPathPlanner

    # 趋势分析：None 分数 / 缺失字段不崩溃
    analyzer = MultiFactorTrendAnalyzer()
    res = analyzer.analyze(
        "s1",
        quiz_history=[{"score": None, "weak_tags": None}, {"score": "75"}, {"score": 80}],
        learning_records=[{"duration": None, "created_at": "2026-09-01T10:00:00"},
                          {"action": "complete", "kp_id": "kp0", "progress": None,
                           "created_at": "2026-09-02T10:00:00"}],
        weak_areas=["指针"],
        profile={},
    )
    check("趋势分析容忍 None/字符串分值",
          -1 <= res["trend_factor"] <= 1
          and res["trend_state"] in ("growth", "stable", "warning", "decline")
          and -1 <= res["dimensions"]["speed_ratio"] <= 1,
          str(res.get("dimensions")))

    # 加权匹配：空串目标不虚增匹配数（修复前 "" in "" 恒真会把 goal_match 推到 1.0）
    matcher = MultiDimWeightedMatcher()
    _, details = matcher._score_resource(
        {"learning_goals": [{"title": ""}], "knowledge_base": {}, "weak_areas": [], "cognitive_style": {}, "learning_tempo": {}},
        {"resource_id": "r0", "objectives": ["", "指针"], "kp_tags": [], "content_types": [], "estimated_duration": 45},
    )
    check("加权匹配空串目标守卫（matched 不虚增）", abs(details["goal_match"] - 0.2) < 1e-9,
          str(details["goal_match"]))

    # registry 收益闭环：未缓存学生首条反馈自动建 bandit（不再被丢弃）
    ok = update_strategy_bandit("_verify_new_student_", "review_boost", 0.9)
    bandit = get_strategy_bandit("_verify_new_student_")
    check("registry 首条收益反馈自动建 bandit", ok is True and bandit.get_stats()["n_updates"] == 1,
          str(bandit.get_stats()))

    # attach helper：未拟合时返回 False 且不注入
    planner = DAGPathPlanner()
    check("attach_irt_to_planner 未拟合返回 False", attach_irt_to_planner(planner) is False)


def test_p1_upgrades():
    print("P1 算法补全（GKT 可学习 / 趋势权重学习化 / 匹配 MAB 探索层）")
    import numpy as np
    from app.algorithms.gkt_engine import GKTEngine
    from app.algorithms.trend_analysis import TrendWeightLearner, MultiFactorTrendAnalyzer
    from app.algorithms.weighted_matching import MultiDimWeightedMatcher
    from app.algorithms.bandit_selector import ThompsonSamplingSelector

    # --- GKT：自监督训练降低预测误差，且保留单调性与边界 ---
    kps = ["kp0", "kp1", "kp2"]
    gkt = GKTEngine()
    gkt.build_graph(kps, [("kp0", "kp1"), ("kp1", "kp2")])
    rng = np.random.default_rng(7)
    seqs = []
    for _ in range(5):
        snaps = []
        v = 0.1
        for _t in range(10):
            v = min(0.95, v + 0.08)
            snaps.append({"kp0": min(0.95, v + 0.05), "kp1": v, "kp2": max(0.05, v - 0.1)})
        seqs.append(snaps)
    res = gkt.fit(seqs)
    check("GKT 可训练：拟合成功", res.get("status") == "success", str(res))
    check("GKT 训练降低预测误差",
          res.get("final_loss", 1) < res.get("initial_loss", 0), 
          f"{res.get('initial_loss')} -> {res.get('final_loss')}")
    check("GKT 单调约束（w ≥ 0）与门控范围",
          res.get("params", {}).get("w", -1) >= 0
          and 0 < res.get("params", {}).get("alpha", -1) < 1, str(res.get("params")))
    check("GKT is_fitted 置位", gkt.is_fitted is True)
    out = gkt.propagate({"kp0": 0.9, "kp1": 0.5, "kp2": 0.1})
    check("GKT 训练后传播仍 ∈ [0,1]", all(0 <= v <= 1 for v in out.values()), str(out))
    # 样本不足优雅降级
    gkt2 = GKTEngine()
    gkt2.build_graph(kps, [("kp0", "kp1")])
    check("GKT 快照序列不足降级", gkt2.fit([[{"kp0": 0.5}]])["status"] == "error")

    # --- 趋势权重学习器：可分样本上训练准确率 > 0.9，权重极性与人工先验一致 ---
    learner = TrendWeightLearner()
    samples = []
    rng = np.random.default_rng(8)
    for i in range(80):
        drop = rng.random() < 0.5
        dims = {"mastery_trend": -0.8 if drop else 0.8, "speed_ratio": -0.5 if drop else 0.5,
                "time_efficiency": float(rng.normal(0, 0.1)), "weakness_priority": -0.4 if drop else 0.2,
                "stability": -0.6 if drop else 0.6, "completion_rate": -0.5 if drop else 0.5}
        samples.append({"dimensions": dims, "label": 1 if drop else 0})
    res_l = learner.fit(samples)
    check("趋势学习器训练成功且准确率 > 0.9",
          res_l.get("status") == "success" and res_l.get("train_accuracy", 0) > 0.9, str(res_l))
    w = learner.convex_weights
    check("学习权重极性与'越大越好'语义一致（积极维度权重为正）",
          w["mastery_trend"] > 0 and w["stability"] > 0, str(w))
    check("预警概率 ∈ [0,1] 且极值方向正确",
          0 <= learner.predict_proba({k: 0.8 for k in w}) < 0.5
          and learner.predict_proba({k: -0.8 for k in w}) > 0.5,
          f"good={learner.predict_proba({k: 0.8 for k in w})} bad={learner.predict_proba({k: -0.8 for k in w})}")
    # 序列化往返
    learner2 = TrendWeightLearner()
    check("趋势学习器序列化往返", learner2.deserialize(learner.serialize())
          and abs(learner2.predict_proba(samples[0]["dimensions"]) 
                  - learner.predict_proba(samples[0]["dimensions"])) < 1e-6)
    # 分析器接入：learned / manual_prior 双模式
    analyzer = MultiFactorTrendAnalyzer()
    r_learned = analyzer.analyze("s1", [{"score": 70}], 
                                 [{"action": "read", "duration": 100, "created_at": "2026-09-01T10:00:00"}],
                                 [], {}, weight_learner=learner)
    r_manual = analyzer.analyze("s1", [{"score": 70}], 
                                [{"action": "read", "duration": 100, "created_at": "2026-09-01T10:00:00"}],
                                [], {})
    check("分析器双模式标注（learned / manual_prior）",
          r_learned["weights_source"] == "learned" and r_manual["weights_source"] == "manual_prior",
          f"{r_learned['weights_source']}/{r_manual['weights_source']}")
    check("双模式均输出预警概率 ∈ [0,1]",
          0 <= r_learned["warning_probability"] <= 1 and 0 <= r_manual["warning_probability"] <= 1,
          f"{r_learned['warning_probability']}/{r_manual['warning_probability']}")

    # --- 匹配 MAB 探索层：冷启动不改变排序，预热后高收益类型提前 ---
    matcher = MultiDimWeightedMatcher()
    profile = {"knowledge_base": {}, "weak_areas": [], "cognitive_style": {}, 
               "learning_goals": [], "learning_tempo": {}}
    resources = [
        {"resource_id": "doc1", "title": "讲义", "type": "document", "kp_tags": ["指针"],
         "content_types": [], "difficulty": "intermediate", "objectives": [], "estimated_duration": 45},
        {"resource_id": "vid1", "title": "视频", "type": "video", "kp_tags": ["指针"],
         "content_types": [], "difficulty": "intermediate", "objectives": [], "estimated_duration": 45},
    ]
    r_plain = matcher.match_resources(profile, resources)
    sel = ThompsonSamplingSelector(["video", "document", "quiz", "interactive", "audio", "image", "code", "mindmap"], seed=1)
    r_cold = matcher.match_resources(profile, resources, bandit_selector=sel)
    check("匹配探索冷启动排序与纯打分一致",
          [x["resource_id"] for x in r_plain["recommendations"]]
          == [x["resource_id"] for x in r_cold["recommendations"]],
          f"{[x['resource_id'] for x in r_cold['recommendations']]}")
    for _ in range(8):
        sel.update("video", 1.0)
        sel.update("document", 0.1)
    r_warm = matcher.match_resources(profile, resources, bandit_selector=sel)
    order = {x["resource_id"]: x["match_score"] for x in r_warm["recommendations"]}
    check("匹配探索预热后高收益类型提分",
          order.get("vid1", 0) > order.get("doc1", 0), str(order))
    check("匹配结果标注探索状态",
          r_cold["exploration"]["enabled"] is False and r_warm["exploration"]["enabled"] is True,
          str(r_warm["exploration"]["enabled"]))


if __name__ == "__main__":
    test_bkt()
    test_irt()
    test_memory()
    test_bandit()
    test_upgrades()
    test_gkt()
    test_ncd()
    test_p0_wiring()
    test_robustness()
    test_p1_upgrades()
    print(f"\n结果: {PASS} 通过, {FAIL} 失败")
    sys.exit(1 if FAIL else 0)
