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
    auto = IRTDiagnoser(model="auto")
    auto_res = auto.fit(rows)
    check("IRT 小样本自动降级 1PL", auto_res.get("model") == "1pl", str(auto_res))
    check("IRT 自动选择原因可审计",
          auto_res.get("model_selection_reason") == "small_sample_rasch_fallback", str(auto_res))
    large_model, large_reason = IRTDiagnoser._select_model("auto", 100, 10, 1200, 40)
    check("IRT 数据充分时自动启用 2PL",
          (large_model, large_reason) == ("2pl", "sample_supports_2pl"),
          str((large_model, large_reason)))
    check("IRT 标尺中心化", abs(sum(auto_res["ability"].values()) / len(auto_res["ability"])) < 1e-3,
          str(auto_res.get("ability")))
    check("IRT 似然与 MAP 目标语义分离",
          auto_res.get("log_likelihood", 0) <= 0 and auto_res.get("map_objective", 0) >= 0,
          str({k: auto_res.get(k) for k in ("log_likelihood", "map_objective")}))
    check("IRT 数据不足降级", IRTDiagnoser().fit([{"student_id": "a", "item_id": "x", "correct": True}])["status"] == "error")


def test_offline_evaluation():
    print("算法离线评估（按学生时间留出）")
    from app.algorithms.bkt_engine import BKTEngine
    from app.algorithms.offline_evaluation import (
        binary_metrics,
        chronological_student_split,
        evaluate_bkt_time_holdout,
    )

    rows = make_quiz_records(n_students=8, n_kps=3, seed=17)
    frame = BKTEngine.build_dataframe(rows)
    train, test = chronological_student_split(frame, test_fraction=0.25)
    check("离线评估时间切分无交叉", set(train.index).isdisjoint(test.index))
    check("离线评估每生保留训练记录",
          all(len(group) >= 1 for _, group in train.groupby("student_id")))
    metrics = binary_metrics([0, 0, 1, 1], [0.1, 0.2, 0.8, 0.9])
    check("离线评估指标方向正确",
          metrics["auc"] == 1.0 and metrics["brier_score"] < 0.05, str(metrics))
    report = evaluate_bkt_time_holdout(rows, test_fraction=0.25)
    check("BKT 时间留出报告可生成",
          report.get("status") == "success" and report.get("coverage", {}).get("eligible_test_answers", 0) > 0,
          str(report))


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


def test_wiring_round2():
    print("第二轮接线（FSRS→路径复习阶段 / IRT b→匹配难度 / agent 上下文构建）")
    from app.algorithms.path_planning_dag import DAGPathPlanner
    from app.algorithms.weighted_matching import MultiDimWeightedMatcher
    from app.services.algorithm_registry import (
        build_ai_engine_context,
        format_ai_engine_context,
    )

    planner = DAGPathPlanner()
    planner.build_graph([
        {"kp_id": "k1", "name": "K1", "subject": "C", "difficulty": 3,
         "prerequisites": [], "description": "", "tags": []},
        {"kp_id": "k2", "name": "K2", "subject": "C", "difficulty": 3,
         "prerequisites": ["k1"], "description": "", "tags": []},
    ])

    # --- FSRS 到期复习 → 路径头部插入 review 阶段 ---
    r = planner.plan_path("s1", "k2", {"k1": 0.95, "k2": 0.3}, {}, due_kp_ids=["k1"])
    st = r["stages"]
    check("FSRS 到期知识点 → 路径头部插入 review 阶段",
          st[0].get("type") == "review" and st[0].get("review_source") == "fsrs_due"
          and "k1" in st[0].get("kp_ids", []),
          str(st[0]))
    check("插入复习阶段后 stage_no 连续重编号",
          [s["stage_no"] for s in st] == list(range(1, len(st) + 1)), str([s["stage_no"] for s in st]))
    check("总时长包含复习阶段",
          r["estimated_total_hours"] == round(sum(s["hours"] for s in st), 1),
          f"{r['estimated_total_hours']} vs {sum(s['hours'] for s in st)}")

    # 已被学习阶段覆盖的到期知识点去重（不重复既学又复习）
    r2 = planner.plan_path("s1", "k2", {"k1": 0.3, "k2": 0.3}, {}, due_kp_ids=["k1"])
    check("到期知识点已被学习阶段覆盖时去重",
          all(s.get("review_source") != "fsrs_due" for s in r2["stages"]),
          str([s.get("type") for s in r2["stages"]]))

    # 无到期卡行为不变（向后兼容）
    r3 = planner.plan_path("s1", "k2", {"k1": 0.95, "k2": 0.3}, {})
    check("无到期卡时路径无 FSRS 复习阶段",
          all(s.get("type") != "review" for s in r3["stages"]),
          str([s.get("type") for s in r3["stages"]]))

    # 全已掌握 + 到期卡 → 纯复习路径并入到期知识点
    r4 = planner.plan_path("s1", "k2", {"k1": 0.95, "k2": 0.9}, {}, due_kp_ids=["k1"])
    check("全已掌握时到期知识点并入复习阶段",
          r4["stages"][0].get("type") == "review"
          and set(r4["stages"][0].get("kp_ids", [])) == {"k1", "k2"},
          str(r4["stages"][0]))

    # --- IRT b → 匹配难度适配分 ---
    matcher = MultiDimWeightedMatcher()
    check("难度适配三档回退（medium 与中档同义）",
          matcher._difficulty_fit("beginner", "medium") == 0.6,
          str(matcher._difficulty_fit("beginner", "medium")))
    fit_eq = matcher._difficulty_fit("beginner", "medium", irt_b=0.0, irt_theta=0.0)
    fit_hard = matcher._difficulty_fit("beginner", "medium", irt_b=3.0, irt_theta=0.0)
    fit_easy = matcher._difficulty_fit("beginner", "medium", irt_b=-3.0, irt_theta=0.0)
    check("IRT 适配分：θ=b 峰值 1.0，过难/过易对称衰减",
          fit_eq == 1.0 and 0 < fit_hard < 1 and 0 < fit_easy < 1
          and abs(fit_hard - fit_easy) < 1e-9,
          f"eq={fit_eq} hard={fit_hard} easy={fit_easy}")

    profile = {"knowledge_base": {}, "weak_areas": [], "cognitive_style": {},
               "learning_goals": [], "learning_tempo": {}, "knowledge_level": "beginner"}
    resources = [
        {"resource_id": "r_easy", "title": "入门", "type": "document", "kp_id": "kA",
         "kp_tags": [], "content_types": [], "difficulty": "medium", "objectives": [],
         "estimated_duration": 45},
        {"resource_id": "r_match", "title": "匹配", "type": "document", "kp_id": "kB",
         "kp_tags": [], "content_types": [], "difficulty": "medium", "objectives": [],
         "estimated_duration": 45},
    ]
    r_irt = matcher.match_resources(profile, resources, irt_difficulty={"kA": -3.0, "kB": 0.0}, irt_ability=0.0)
    det = {x["resource_id"]: x["details"] for x in r_irt["recommendations"]}
    check("匹配 difficulty_source 标注 irt_b",
          det["r_easy"].get("difficulty_source") == "irt_b"
          and det["r_match"].get("difficulty_source") == "irt_b", str(det["r_easy"]))
    check("IRT b 影响难度适配分（θ=b 的资源拟合分更高）",
          det["r_match"]["difficulty_fit"] > det["r_easy"]["difficulty_fit"],
          f"match={det['r_match']['difficulty_fit']} easy={det['r_easy']['difficulty_fit']}")
    r_plain = matcher.match_resources(profile, resources)
    det_plain = {x["resource_id"]: x["details"] for x in r_plain["recommendations"]}
    check("未标定时 difficulty_source 回退 manual 且行为不变",
          det_plain["r_easy"].get("difficulty_source") == "manual"
          and det_plain["r_easy"]["difficulty_fit"] == det_plain["r_match"]["difficulty_fit"],
          str(det_plain["r_easy"]))

    # --- agent 共享上下文构建/格式化 ---
    check("空算法上下文格式化为空串", format_ai_engine_context({}) == "")
    note = format_ai_engine_context({
        "bkt": {"weak_points": [{"kp": "kp1", "mastery": 0.32}]},
        "fsrs": {"due_count": 2, "due_kps": ["kp1", "kp2"]},
    })
    check("算法上下文含 BKT 薄弱点与 FSRS 到期片段",
          "【BKT 算法感知】" in note and "【FSRS 记忆调度】" in note, note)

    try:
        from app.models.database import SessionLocal
        db = SessionLocal()
        try:
            ctx = build_ai_engine_context(db, "no_such_student_xyz")
            check("build_ai_engine_context 无数据时返回空 dict（静默降级）", ctx == {}, str(ctx))
        finally:
            db.close()
    except Exception as e:  # pragma: no cover - 数据库不可用时跳过该断言
        print(f"  ⏭️ 跳过 build_ai_engine_context 数据库断言: {e}")




def test_robustness_round2():
    print("第三轮修复（难度量纲/IRT 聚合/环防护/is_warm/内容库容错/不可变 mastery）")
    from app.algorithms.path_planning_dag import DAGPathPlanner, _normalize_difficulty_level
    from app.algorithms.bandit_selector import ThompsonSamplingSelector
    from app.services.algorithm_registry import attach_irt_to_planner, set_irt_diagnoser
    from app.services.content_library import _extract_content

    # --- 难度量纲归一化 ---
    check("难度归一化：0-1 比例 → 1-5 级",
          _normalize_difficulty_level(0.2) == 2 and _normalize_difficulty_level(0.65) == 4,
          f"{_normalize_difficulty_level(0.2)}/{_normalize_difficulty_level(0.65)}")
    check("难度归一化：已是级数与非法值兼容",
          _normalize_difficulty_level(3) == 3 and _normalize_difficulty_level(None) == 3,
          f"{_normalize_difficulty_level(3)}/{_normalize_difficulty_level(None)}")
    planner = DAGPathPlanner()
    planner.build_graph([
        {"kp_id": "k1", "name": "K1", "subject": "C", "difficulty": 0.2,
         "prerequisites": [], "description": "", "tags": []},
        {"kp_id": "k2", "name": "K2", "subject": "C", "difficulty": 0.6,
         "prerequisites": ["k1"], "description": "", "tags": []},
    ])
    check("build_graph 入口难度归一化",
          planner.kp_meta["k1"]["difficulty"] == 2 and planner.kp_meta["k2"]["difficulty"] == 3,
          str({k: planner.kp_meta[k]["difficulty"] for k in ("k1", "k2")}))

    # --- IRT 复合键聚合注入 ---
    class FakeIRT:
        is_fitted = True
        difficulty_map = {"kp_c01:q1": 1.0, "kp_c01:q2": 2.0, "kp_c02": 3.0}
        def get_item_difficulty(self, item_id):
            return self.difficulty_map.get(item_id)
    set_irt_diagnoser(FakeIRT())
    planner2 = DAGPathPlanner()
    planner2.build_graph([
        {"kp_id": "kp_c01", "name": "K", "subject": "C", "difficulty": 0.3,
         "prerequisites": [], "description": "", "tags": []},
    ])
    ok_attach = attach_irt_to_planner(planner2)
    _, src = planner2._difficulty_factor("kp_c01", {"difficulty": 0.3})
    check("attach_irt_to_planner 聚合复合 item_id 后按 kp 命中",
          ok_attach is True and src == "irt_b", str(src))

    # --- 环检测防护 ---
    cyc = DAGPathPlanner()
    cyc.build_graph([
        {"kp_id": "a", "name": "A", "subject": "C", "difficulty": 0.3,
         "prerequisites": ["b"], "description": "", "tags": []},
        {"kp_id": "b", "name": "B", "subject": "C", "difficulty": 0.3,
         "prerequisites": ["a"], "description": "", "tags": []},
    ])
    check("成环脏数据：plan_path 入口拒绝（不再递归爆炸）",
          cyc.plan_path("s1", "a", {"a": 0.1, "b": 0.1}, {})["status"] == "error", "ok")

    # --- is_warm 语义（不同臂覆盖） ---
    sel = ThompsonSamplingSelector(["x", "y", "z"], seed=1)
    for _ in range(3):
        sel.update("x", 1.0)
    check("is_warm：累计反馈达臂数即预热（快速预热语义）", sel.is_warm is True)
    check("is_warm：反馈不足臂数保持冷启动", ThompsonSamplingSelector(["x", "y", "z"], seed=1).is_warm is False)

    # --- 内容库单列损坏不连坐 ---
    class FakeKP:
        kp_id = "kx"
        document = "# doc"
        code_example = "int main(){}"
        questions = "{broken json"
        mindmap = "{also broken"
    content = _extract_content(FakeKP())
    check("内容库 JSON 单列损坏只丢该列（document/code 保留）",
          content.get("document") == "# doc" and bool(content.get("code")) and
          "questions" not in content and "mindmap" not in content, str(content.keys()))

    # --- plan_path 不修改调用方 mastery_map ---
    planner3 = DAGPathPlanner()
    planner3.build_graph([
        {"kp_id": "m1", "name": "M1", "subject": "C", "difficulty": 0.3,
         "prerequisites": [], "description": "", "tags": []},
    ])
    src_map = {"m1": 0.5}
    planner3.plan_path("s1", "m1", src_map, {})
    check("plan_path 不再原地修改调用方 mastery_map", src_map == {"m1": 0.5}, str(src_map))




def test_agent_hardening():
    print("第六轮智能体加固（kg 批次防护 / 画像兼容读 / cognitive_style 守卫 / status 兼容）")
    import asyncio
    from app.agents.base import BaseAgent, get_primary_cognitive_style

    # --- cognitive_style 守卫 ---
    check("cognitive_style：dict 形态取 primary",
          get_primary_cognitive_style({"cognitive_style": {"primary": "auditory"}}) == "auditory", "ok")
    check("cognitive_style：字符串形态直接用",
          get_primary_cognitive_style({"cognitive_style": "kinesthetic"}) == "kinesthetic", "ok")
    check("cognitive_style：缺失/None 回退 visual",
          get_primary_cognitive_style({}) == "visual"
          and get_primary_cognitive_style({"cognitive_style": None}) == "visual", "ok")

    # --- get_status str/Enum 双兼容 ---
    class _FakeAgent(BaseAgent):
        def __init__(self):
            super().__init__(agent_id="fake", agent_name="Fake", description="")
            self.status = "running"  # 子类常见覆写
        def get_system_prompt(self):
            return ""
        async def process(self, context):
            return {}
    try:
        st = _FakeAgent().get_status()["status"]
        check("get_status 对字符串 status 不再 AttributeError", st == "running", str(st))
    except AttributeError:
        check("get_status 对字符串 status 不再 AttributeError", False, "AttributeError")

    # --- course_designer 兼容读 profiler analysis ---
    from app.agents.course_designer import CourseDesignerAgent
    cd = CourseDesignerAgent.__new__(CourseDesignerAgent)
    # 不走 LLM：直接验证 _get_student_profile 的提取逻辑（用假 profiler 注入）
    class FakeProfiler:
        async def process(self, ctx):
            return {"status": "success", "analysis": {
                "weak_areas": ["指针"], "cognitive_style": {"primary": "reading"}}}
    cd.sub_agents = {"profiler": FakeProfiler()}
    prof = asyncio.run(cd._get_student_profile("s1"))
    check("course_designer 能读到 profiler analysis 内的真实画像",
          prof.get("weak_areas") == ["指针"], str(prof.get("weak_areas")))

    class EmptyProfiler:
        async def process(self, ctx):
            return {"status": "success", "analysis": {}}
    cd2 = CourseDesignerAgent.__new__(CourseDesignerAgent)
    cd2.sub_agents = {"profiler": EmptyProfiler()}
    prof2 = asyncio.run(cd2._get_student_profile("s1"))
    check("profiler 无画像时回退兜底画像（原行为保留）",
          prof2.get("weak_areas") == ["recursion", "dynamic_programming"], str(prof2.get("weak_areas")))

    # --- kg_builder 批次失败带 status ---
    from app.agents.knowledge_graph_builder import KnowledgeGraphBuilderAgent
    kg = KnowledgeGraphBuilderAgent.__new__(KnowledgeGraphBuilderAgent)
    import types

    class ErrLLM:
        async def generate_json(self, messages, **kw):
            return {"status": "error", "message": "bad json"}
    kg.llm = ErrLLM()
    kg.logger = __import__("logging").getLogger("test")
    batch = asyncio.run(kg._process_batch([{"kp_id": "k1", "name": "K1"}], "C"))
    check("kg_builder 批次失败返回 status=error（外层 failed_batches 防护生效）",
          batch.get("status") == "error", str(batch.get("status")))


if __name__ == "__main__":
    test_bkt()
    test_irt()
    test_offline_evaluation()
    test_memory()
    test_bandit()
    test_upgrades()
    test_gkt()
    test_ncd()
    test_p0_wiring()
    test_robustness()
    test_p1_upgrades()
    test_wiring_round2()
    test_robustness_round2()
    test_agent_hardening()
    print(f"\n结果: {PASS} 通过, {FAIL} 失败")
    sys.exit(1 if FAIL else 0)
