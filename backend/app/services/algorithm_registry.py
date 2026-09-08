"""
算法引擎共享注册表（进程内单例）

BKT / IRT / GKT / 趋势权重学习器的拟合结果（数据量小、拟合代价高）由
/api/v1/algorithms/* 触发，其他业务模块（学习路径 / 每日练习 / 学情评估 /
资源匹配）通过本注册表读取，实现"算法中心拟合一次，全系统复用"的静默接线。

说明：进程内持有即可满足演示与比赛需求；生产可替换为 Redis 缓存。
"""
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional


_bkt_engine: Any = None
_irt_diagnoser: Any = None
_ncd_diagnoser: Any = None
_gkt_engine: Any = None
_trend_weight_learner: Any = None
_strategy_bandits: Dict[str, Any] = {}  # student_id -> ThompsonSamplingSelector
_resource_bandits: Dict[str, Any] = {}  # student_id -> ThompsonSamplingSelector
_BANDIT_CACHE_MAX = 5000  # 进程内缓存上限（超出时随机淘汰，防长期运行无界增长）


def _evict_bandit_cache(cache: Dict[str, Any]) -> None:
    while len(cache) >= _BANDIT_CACHE_MAX:
        cache.pop(next(iter(cache)))


def set_bkt_engine(engine: Any) -> None:
    global _bkt_engine
    _bkt_engine = engine


def get_bkt_engine() -> Any:
    return _bkt_engine


def set_irt_diagnoser(diagnoser: Any) -> None:
    global _irt_diagnoser
    _irt_diagnoser = diagnoser


def get_irt_diagnoser() -> Any:
    return _irt_diagnoser


def set_ncd_diagnoser(diagnoser: Any) -> None:
    global _ncd_diagnoser
    _ncd_diagnoser = diagnoser


def get_ncd_diagnoser() -> Any:
    return _ncd_diagnoser


def set_gkt_engine(engine: Any) -> None:
    global _gkt_engine
    _gkt_engine = engine


def get_gkt_engine() -> Any:
    return _gkt_engine


def set_trend_weight_learner(learner: Any) -> None:
    global _trend_weight_learner
    _trend_weight_learner = learner


def get_trend_weight_learner() -> Any:
    return _trend_weight_learner


def get_irt_ability(student_id: str) -> Optional[float]:
    """查询学生 IRT 能力 θ（未拟合或无该学生时返回 None，调用方静默降级）。"""
    diagnoser = _irt_diagnoser
    if diagnoser is None or not getattr(diagnoser, "is_fitted", False):
        return None
    try:
        return diagnoser.estimate_ability(student_id)
    except Exception:
        return None


def get_irt_difficulty_map() -> Optional[Dict[str, float]]:
    """查询 IRT 标定的难度 b 值映射 {item_id: b}（未拟合返回 None，静默降级）。

    注意：item_id 可能是 f"{kp_id}:{question_id}" 复合键（启动拟合按作答明细
    构造），按知识点使用时需对前缀聚合。
    """
    diagnoser = _irt_diagnoser
    if diagnoser is None or not getattr(diagnoser, "is_fitted", False):
        return None
    try:
        return dict(diagnoser.difficulty_map)
    except Exception:
        return None


class _KpAggregatedIRT:
    """IRT 诊断器的按知识点聚合视图。

    拟合时作答明细存在则 item_id 为 f"{kp_id}:{question_id}" 复合键，路径规划等
    按 kp_id 查难度的调用方会全部 miss；此处按前缀聚合 b 值（同 api/matching.py
    口径），其余属性透传内部诊断器。
    """

    def __init__(self, inner: Any):
        self._inner = inner
        self.is_fitted = True
        raw = getattr(inner, "difficulty_map", {}) or {}
        agg: Dict[str, List[float]] = {}
        for item_id, b in raw.items():
            try:
                agg.setdefault(str(item_id).split(":")[0], []).append(float(b))
            except (TypeError, ValueError):
                continue
        self._kp_map: Dict[str, float] = {kp: sum(v) / len(v) for kp, v in agg.items() if v}

    def get_item_difficulty(self, item_id: str):
        return self._kp_map.get(item_id)

    @property
    def difficulty_map(self) -> Dict[str, float]:
        return dict(self._kp_map)

    def __getattr__(self, name):
        return getattr(self._inner, name)


def attach_irt_to_planner(planner) -> bool:
    """将已拟合的 IRT 诊断器注入路径规划器（学习成本模型用 b 值）。
    未拟合时不动 planner，返回 False（调用方无需判空）。
    注入的是复合 item_id 按知识点前缀聚合后的视图，保证按 kp_id 查难度可命中。"""
    diagnoser = _irt_diagnoser
    if diagnoser is None or not getattr(diagnoser, "is_fitted", False):
        return False
    planner.set_irt_diagnoser(_KpAggregatedIRT(diagnoser))
    return True


def attach_gkt_to_planner(planner) -> bool:
    """将已训练的 GKT 引擎注入路径规划器（掌握度图卷积传播）。
    未训练时不动 planner，返回 False。"""
    engine = _gkt_engine
    if engine is None or not getattr(engine, "is_fitted", False):
        return False
    planner.set_gkt_engine(engine)
    return True


# ---------------------------------------------------------------- 训练数据构建
def build_mastery_snapshots(db, student_id: str, days: int = 60) -> List[Dict[str, float]]:
    """从学习记录构建该生的每日掌握度快照序列（GKT 自监督训练数据）。

    每日快照：{kp_id: 当日最大 progress}；按日期升序。
    """
    from ..models.knowledge import LearningRecordModel
    since = datetime.now(timezone.utc) - timedelta(days=days)
    rows = (
        db.query(LearningRecordModel)
        .filter(
            LearningRecordModel.student_id == student_id,
            LearningRecordModel.created_at >= since,
        )
        .order_by(LearningRecordModel.created_at.asc())
        .all()
    )
    snapshots: List[Dict[str, float]] = []
    current: Dict[str, float] = {}
    current_date: Optional[str] = None
    for r in rows:
        d = r.created_at.date().isoformat() if r.created_at else None
        if not d:
            continue
        if d != current_date:
            if current:
                snapshots.append(dict(current))
            current_date = d
        try:
            progress = float(r.progress or 0.0)
        except (TypeError, ValueError):
            progress = 0.0
        current[r.kp_id] = max(current.get(r.kp_id, 0.0), min(max(progress, 0.0), 1.0))
    if current:
        snapshots.append(dict(current))
    return snapshots


def build_trend_training_samples(db, days: int = 90, horizon_days: int = 7) -> List[Dict[str, Any]]:
    """从趋势快照表 + 测验/学习记录构建趋势权重训练样本。

    标签（掉队=1）：随后 horizon_days 内平均测验分 < 60，
    或该时段完全无学习记录（学习中断）；无测验成绩但有学习行为 → 0。
    """
    from ..models.trend import TrendDataModel
    from ..models.knowledge import LearningRecordModel, QuizResultModel

    cutoff_date = (datetime.now(timezone.utc) - timedelta(days=days)).date()
    trends = (
        db.query(TrendDataModel)
        .filter(TrendDataModel.date >= cutoff_date.isoformat())
        .all()
    )
    samples: List[Dict[str, Any]] = []
    for t in trends:
        try:
            start = datetime.strptime(t.date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except (TypeError, ValueError):
            continue
        end = start + timedelta(days=horizon_days)
        details = t.details if isinstance(t.details, dict) else {}
        dims = {
            "mastery_trend": t.mastery_trend or 0.0,
            "speed_ratio": t.speed_ratio or 0.0,
            "time_efficiency": t.time_efficiency or 0.0,
            "weakness_priority": t.weakness_priority or 0.0,
            "stability": t.stability or 0.0,
            "completion_rate": details.get("completion_rate", 0.0),
        }
        next_scores = [
            q.score
            for q in db.query(QuizResultModel)
            .filter(
                QuizResultModel.student_id == t.student_id,
                QuizResultModel.created_at > start,
                QuizResultModel.created_at <= end,
                QuizResultModel.score.isnot(None),
            )
            .all()
        ]
        next_study = (
            db.query(LearningRecordModel.record_id)
            .filter(
                LearningRecordModel.student_id == t.student_id,
                LearningRecordModel.created_at > start,
                LearningRecordModel.created_at <= end,
            )
            .first()
        )
        if next_scores:
            label = 1 if (sum(next_scores) / len(next_scores)) < 60 else 0
        elif next_study is None:
            label = 1  # 学习中断
        else:
            label = 0
        samples.append({
            "student_id": t.student_id,
            "date": t.date,
            "dimensions": dims,
            "label": label,
        })
    return samples


# ---------------------------------------------------------------- 路径调整策略 MAB
# 臂集合以 path_planning_dag.STRATEGY_ARMS 为单一来源（含 maintain），
# 按学生维度进程内缓存，与 daily_quiz 的选题器同模式。

def get_strategy_bandit(student_id: str) -> Any:
    """获取（或懒创建）学生的路径调整策略 Thompson Sampling 选择器。"""
    if student_id not in _strategy_bandits:
        from ..algorithms.bandit_selector import ThompsonSamplingSelector
        from ..algorithms.path_planning_dag import STRATEGY_ARMS
        _evict_bandit_cache(_strategy_bandits)
        _strategy_bandits[student_id] = ThompsonSamplingSelector(STRATEGY_ARMS, seed=42)
    return _strategy_bandits[student_id]


def update_strategy_bandit(student_id: str, arm: str, reward: float) -> bool:
    """反馈某轮调整策略的实际收益（0-1）。bandit 不存在时自动创建，
    保证学生的第一条反馈不会因尚未缓存而被丢弃。未知臂返回 False。"""
    try:
        bandit = get_strategy_bandit(student_id)
        bandit.update(arm, reward)
        return True
    except Exception:
        return False


# ---------------------------------------------------------------- 资源匹配探索 MAB
def get_resource_bandit(student_id: str) -> Any:
    """获取（或懒创建）学生的资源类型 Thompson Sampling 选择器
    （加权匹配探索层，臂 = RESOURCE_ARMS 资源类型）。"""
    if student_id not in _resource_bandits:
        from ..algorithms.bandit_selector import ThompsonSamplingSelector
        from ..algorithms.weighted_matching import RESOURCE_ARMS
        _evict_bandit_cache(_resource_bandits)
        _resource_bandits[student_id] = ThompsonSamplingSelector(RESOURCE_ARMS, seed=42)
    return _resource_bandits[student_id]


def update_resource_bandit(student_id: str, arm: str, reward: float) -> bool:
    """反馈某类资源的实际收益（0-1，如点击 0.3 / 完成且好评 1.0），自动创建。"""
    try:
        bandit = get_resource_bandit(student_id)
        bandit.update(arm, reward)
        return True
    except Exception:
        return False


def build_memory_status(db, student_id: str) -> Optional[dict]:
    """从 memory_cards 表构建 FSRS 记忆状态，供效果评估输出真实复习队列。

    无记忆卡片时返回 None（评估保持原逻辑，向后兼容）。
    """
    try:
        from ..algorithms.memory_scheduler import FSRSMemoryScheduler
        from ..models.memory import MemoryCardModel

        scheduler = FSRSMemoryScheduler()
        rows = db.query(MemoryCardModel).filter(
            MemoryCardModel.student_id == student_id
        ).all()
        for r in rows:
            scheduler.restore_card(r.student_id, r.kp_id, r.card_json)
        if scheduler.card_count == 0:
            return None
        return {
            "scheduler": "FSRS",
            "due_kps": scheduler.get_due_kp_ids(student_id),
            "cards": scheduler.get_cards_snapshot(student_id),
        }
    except Exception:
        return None


# ---------------------------------------------------------------- agent prompt 算法上下文
def build_ai_engine_context(db, student_id: str) -> Dict[str, Any]:
    """构建注入 agent prompt 的算法上下文（BKT 薄弱点 + FSRS 到期复习）。

    tutor / error_catcher / resource_generator 三处 agent 共用；任一算法层
    故障都静默降级为空 dict，保证 LLM 主流程不受影响。
    """
    ai_engine: Dict[str, Any] = {}
    try:
        bkt = _bkt_engine
        if bkt is not None and getattr(bkt, "is_fitted", False):
            from ..models.knowledge import KnowledgePointModel
            kp_ids = [k.kp_id for k in db.query(KnowledgePointModel).all()]
            mastery = bkt.estimate_mastery_map(student_id, kp_ids)
            weak = sorted(
                [(k, v) for k, v in mastery.items() if v < 0.5],
                key=lambda x: x[1],
            )[:3]
            if weak:
                ai_engine["bkt"] = {
                    "weak_points": [{"kp": k, "mastery": round(v, 2)} for k, v in weak],
                    "note": "BKT 贝叶斯知识追踪实时掌握度",
                }
    except Exception:
        pass
    try:
        from ..algorithms.memory_scheduler import FSRSMemoryScheduler
        from ..models.memory import MemoryCardModel

        scheduler = FSRSMemoryScheduler()
        rows = db.query(MemoryCardModel).filter(
            MemoryCardModel.student_id == student_id
        ).all()
        for r in rows:
            scheduler.restore_card(r.student_id, r.kp_id, r.card_json)
        if scheduler.card_count:
            due = scheduler.get_due_cards(student_id)
            if due:
                ai_engine["fsrs"] = {
                    "due_count": len(due),
                    "due_kps": [d["kp_id"] for d in due[:3]],
                    "note": "FSRS 间隔重复记忆调度（到期复习）",
                }
    except Exception:
        pass
    return ai_engine


def format_ai_engine_context(ai_engine: Dict[str, Any]) -> str:
    """把 build_ai_engine_context 的输出格式化为 prompt 片段（空输入返回空串）。"""
    if not ai_engine:
        return ""
    parts = []
    bkt = ai_engine.get("bkt") or {}
    if bkt.get("weak_points"):
        wp = "、".join(f"{w['kp']}(掌握{w['mastery']})" for w in bkt["weak_points"])
        parts.append(f"【BKT 算法感知】学生薄弱知识点：{wp}——讲解时优先针对这些，避免泛泛而谈")
    fsrs = ai_engine.get("fsrs") or {}
    if fsrs.get("due_count"):
        parts.append(f"【FSRS 记忆调度】有 {fsrs['due_count']} 个知识点到期复习（{fsrs.get('due_kps', [])}）——可提醒学生先复习再学新内容")
    return "\n".join(parts) + "\n" if parts else ""
