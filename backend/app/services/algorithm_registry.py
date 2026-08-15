"""
算法引擎共享注册表（进程内单例）

BKT / IRT 引擎的拟合结果（数据量小、拟合代价高）由 /api/v1/algorithms/* 触发，
其他业务模块（学习路径 / 每日练习 / 学情评估）通过本注册表读取，实现
"算法中心拟合一次，全系统复用"的静默接线。

说明：进程内持有即可满足演示与比赛需求；生产可替换为 Redis 缓存。
"""
from typing import Any, Optional


_bkt_engine: Any = None
_irt_diagnoser: Any = None


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
