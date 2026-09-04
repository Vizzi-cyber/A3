"""
FSRS 间隔重复记忆调度器（Free Spaced Repetition Scheduler）

基于 fsrs 包（open-spaced-repetition/py-fsrs，Anki 现行调度算法的 Python 实现）
为每个学生 × 知识点维护记忆卡片：
  - 难度 D（Difficulty）、稳定性 S（Stability）、可提取性 R（Retrievability）
  - 复习后更新三变量并计算下次最优复习时刻（目标可提取性由 desired_retention 控制）

替代原 effect_evaluation.py 中"增加间隔重复练习频次"的字符串提示——
本调度器输出真实的复习队列与记忆保持概率。

参考文献：
- Ye et al. (2022). A Stochastic Shortest Path Algorithm for Optimizing
  Spaced Repetition Scheduling. KDD.
- Liu et al. (2023). Optimizing Spaced Repetition Schedule by Capturing the
  Dynamics of Memory. TKDE.
"""
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fsrs import Card, Rating, ReviewLog, Scheduler, State

# 前端/API 可读的评分名 -> fsrs Rating
RATING_MAP: Dict[str, Rating] = {
    "again": Rating.Again,   # 忘记
    "hard": Rating.Hard,     # 费力回忆
    "good": Rating.Good,     # 犹豫后回忆
    "easy": Rating.Easy,     # 轻松回忆
}
RATING_LABELS = {r.value: r.name.lower() for r in Rating}

STATE_LABELS = {
    State.Learning: "learning",
    State.Review: "review",
    State.Relearning: "relearning",
}


class FSRSMemoryScheduler:
    """FSRS 间隔重复调度器（内存态 + JSON 序列化）。"""

    def __init__(self, desired_retention: float = 0.9, params: Optional[tuple] = None) -> None:
        """
        :param desired_retention: 目标记忆保持率（0-1，默认 0.9，复习越频繁越保守）
        :param params:            可选的 21 维 FSRS 参数（默认使用社区校准值）
        """
        self.desired_retention = desired_retention
        if params is not None:
            self._scheduler = Scheduler(parameters=params, desired_retention=desired_retention)
        else:
            self._scheduler = Scheduler(desired_retention=desired_retention)
        # key: f"{student_id}:{kp_id}"
        self._cards: Dict[str, Card] = {}
        self._review_logs: List[ReviewLog] = []

    # ------------------------------------------------------------------ 内部
    @staticmethod
    def _key(student_id: str, kp_id: str) -> str:
        return f"{student_id}:{kp_id}"

    @staticmethod
    def _card_to_dict(card: Card) -> Dict[str, Any]:
        """卡片 -> 可读 dict（含可提取性需外部计算）。"""
        return {
            "card_id": card.card_id,
            "state": STATE_LABELS.get(card.state, str(card.state)),
            "due": card.due.isoformat() if card.due else None,
            "last_review": card.last_review.isoformat() if card.last_review else None,
            "stability": round(card.stability, 4) if card.stability is not None else None,
            "difficulty": round(card.difficulty, 4) if card.difficulty is not None else None,
            "step": card.step,
        }

    # ------------------------------------------------------------------ 卡片
    def create_card(self, student_id: str, kp_id: str) -> Dict[str, Any]:
        """为新知识点创建记忆卡片（新卡立即到期）。"""
        card = Card()
        self._cards[self._key(student_id, kp_id)] = card
        return self._card_to_dict(card)

    def get_card(self, student_id: str, kp_id: str) -> Optional[Dict[str, Any]]:
        card = self._cards.get(self._key(student_id, kp_id))
        if card is None:
            return None
        info = self._card_to_dict(card)
        info["retrievability"] = round(self.get_retrievability(student_id, kp_id), 4)
        return info

    def ensure_card(self, student_id: str, kp_id: str) -> Dict[str, Any]:
        """不存在则创建，返回卡片。"""
        if self._key(student_id, kp_id) not in self._cards:
            return self.create_card(student_id, kp_id)
        return self.get_card(student_id, kp_id) or {}

    # ------------------------------------------------------------------ 复习
    def review(self, student_id: str, kp_id: str, rating: str) -> Dict[str, Any]:
        """
        执行一次复习并更新记忆状态。

        :param rating: "again" / "hard" / "good" / "easy"
        :return: 更新后的卡片信息 + 下次复习时间
        """
        key = self._key(student_id, kp_id)
        card = self._cards.get(key)
        if card is None:
            card = Card()
            self._cards[key] = card

        r = RATING_MAP.get(str(rating).lower())
        if r is None:
            raise ValueError(f"无效评分: {rating}，可选 again/hard/good/easy")

        new_card, review_log = self._scheduler.review_card(card, r)
        self._cards[key] = new_card
        self._review_logs.append(review_log)

        info = self._card_to_dict(new_card)
        info["rating"] = RATING_LABELS.get(r.value, str(r.value))
        info["retrievability"] = round(
            self._scheduler.get_card_retrievability(new_card), 4
        )
        info["next_review"] = new_card.due.isoformat() if new_card.due else None
        return info

    # ------------------------------------------------------------------ 查询
    def get_retrievability(self, student_id: str, kp_id: str) -> float:
        """当前记忆可提取性 R（0-1，越低越需要复习）。"""
        card = self._cards.get(self._key(student_id, kp_id))
        if card is None:
            return 0.0
        return float(self._scheduler.get_card_retrievability(card))

    def get_due_cards(self, student_id: str, kp_ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        到期复习队列（按到期时间排序）。

        :param kp_ids: 可选，只在该子集中筛选（如 ADPP 路径上的知识点）
        """
        now = datetime.now(timezone.utc)
        due = []
        for key, card in self._cards.items():
            sid, kp = key.split(":", 1)
            if sid != student_id:
                continue
            if kp_ids is not None and kp not in kp_ids:
                continue
            if card.due is None or card.due <= now:
                due.append({
                    "kp_id": kp,
                    **self._card_to_dict(card),
                    "retrievability": round(self.get_retrievability(student_id, kp), 4),
                })
        due.sort(key=lambda x: x.get("due") or "")
        return due

    def get_due_kp_ids(self, student_id: str, kp_ids: Optional[List[str]] = None) -> List[str]:
        """到期知识点的 kp_id 列表（供路径规划插入复习阶段）。"""
        return [d["kp_id"] for d in self.get_due_cards(student_id, kp_ids)]

    # ------------------------------------------------------------------ 持久化
    def serialize(self) -> str:
        """导出全部卡片（JSON 字符串），供数据库存储。"""
        return json.dumps(
            {key: card.to_json() for key, card in self._cards.items()},
            ensure_ascii=False,
        )

    def deserialize(self, payload: str) -> None:
        """从 JSON 字符串恢复卡片状态（损坏的卡片条目跳过，不中断恢复）。"""
        if not payload:
            return
        try:
            data = json.loads(payload)
        except (ValueError, TypeError):
            return
        if not isinstance(data, dict):
            return
        for key, card_json in data.items():
            try:
                self._cards[key] = Card.from_json(card_json)
            except Exception:
                continue

    def get_card_json(self, student_id: str, kp_id: str) -> Optional[str]:
        """导出单张卡片的 fsrs 序列化 JSON（无卡片返回 None）。"""
        card = self._cards.get(self._key(student_id, kp_id))
        return card.to_json() if card is not None else None

    def restore_card(self, student_id: str, kp_id: str, card_json: str) -> bool:
        """从 fsrs 序列化 JSON 恢复单张卡片（用于数据库持久化恢复）。"""
        if not card_json:
            return False
        try:
            self._cards[self._key(student_id, kp_id)] = Card.from_json(card_json)
            return True
        except Exception:
            return False

    def get_cards_snapshot(self, student_id: str, kp_ids: Optional[List[str]] = None) -> Dict[str, Dict[str, Any]]:
        """导出某学生全部记忆卡片的快照（含未到期卡片，供记忆保持预警）。"""
        result: Dict[str, Dict[str, Any]] = {}
        for key, card in self._cards.items():
            sid, kp = key.split(":", 1)
            if sid != student_id:
                continue
            if kp_ids is not None and kp not in kp_ids:
                continue
            info = self._card_to_dict(card)
            info["retrievability"] = round(self.get_retrievability(student_id, kp), 4)
            result[kp] = info
        return result

    @property
    def card_count(self) -> int:
        return len(self._cards)

    @property
    def scheduler_config(self) -> Dict[str, Any]:
        return {"desired_retention": self.desired_retention}
