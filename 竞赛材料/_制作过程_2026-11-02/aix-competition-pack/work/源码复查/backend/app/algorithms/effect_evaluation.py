"""
学习效果评估与预测算法
- 实时计算：正确率、掌握度、提升速率、薄弱点集中度
- 预测：下次测验得分、潜在失分点、学习效率走势
- 输出：评估报告、数据看板、干预策略
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from collections import Counter
import math


def _safe_float(value: Any, default: float = 0.0) -> float:
    """安全转换为浮点数，处理None和字符串"""
    if value is None:
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def _safe_int(value: Any, default: int = 0) -> int:
    """安全转换为整数，处理None和字符串"""
    if value is None:
        return default
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return default


class LearningEffectEvaluator:
    """学习效果评估器"""

    def evaluate(
        self,
        student_id: str,
        quiz_history: List[Dict[str, Any]],
        learning_records: List[Dict[str, Any]],
        weak_areas: List[str],
        memory_status: Optional[Dict[str, Any]] = None,
        irt_ability: Optional[float] = None,
    ) -> Dict[str, Any]:
        """综合评估入口

        :param memory_status: 可选，FSRS 记忆调度状态
            {"due_kps": [kp_id, ...], "cards": {kp_id: {stability, difficulty, due}},
             "scheduler": "FSRS"}
            提供时输出真实记忆小节（替代"增加间隔重复练习频次"字符串提示）。
        :param irt_ability: 可选，IRT 标定的学生能力 θ（MAP 估计，先验 θ~N(0,1)）。
            提供时掌握度改用 θ 的标准正态百分位 Φ(θ)·100（替代"最近5次加权平均分"），
            mastery_detail 中输出来源与原始 θ，便于复核；未提供时保持原逻辑。
        """
        accuracy = self._calc_accuracy(quiz_history)
        mastery_weighted = self._calc_mastery(quiz_history)
        mastery = mastery_weighted
        mastery_source = "weighted_average"
        if irt_ability is not None:
            mastery = self._theta_to_mastery(irt_ability)
            mastery_source = "irt_theta_percentile"
        improvement_rate = self._calc_improvement_rate(quiz_history)
        weakness_concentration = self._calc_weakness_concentration(quiz_history, weak_areas)

        # 预测
        next_score_prediction = self._predict_next_score(quiz_history, improvement_rate)
        potential_loss_points = self._predict_loss_points(quiz_history, weak_areas)
        efficiency_trend = self._predict_efficiency_trend(learning_records, quiz_history)

        # 干预策略
        intervention = self._generate_intervention(
            accuracy, mastery, improvement_rate, weakness_concentration, weak_areas
        )

        return {
            "student_id": student_id,
            "evaluated_at": datetime.now(timezone.utc).isoformat(),
            "realtime_metrics": {
                "accuracy": round(accuracy, 4),
                "mastery": round(mastery, 4),
                "improvement_rate": round(improvement_rate, 4),
                "weakness_concentration": round(weakness_concentration, 4),
            },
            "mastery_detail": {
                "source": mastery_source,
                "irt_theta": round(float(irt_ability), 4) if irt_ability is not None else None,
                "weighted_average": round(mastery_weighted, 4),
            },
            "predictions": {
                "next_score": round(next_score_prediction, 2),
                "potential_loss_points": potential_loss_points,
                "efficiency_trend": efficiency_trend,
            },
            "intervention": intervention,
            "memory": self._build_memory_section(memory_status),
            "dashboard": {
                "score_history": [_safe_float(q.get("score")) for q in quiz_history],
                "weak_area_distribution": self._weak_area_distribution(quiz_history),
            },
        }

    def _build_memory_section(self, memory_status: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """基于 FSRS 记忆调度状态生成记忆小节（真实复习计划，替代字符串提示）。"""
        if not memory_status:
            return None
        due_kps = list(memory_status.get("due_kps") or [])
        cards = memory_status.get("cards") or {}
        section: Dict[str, Any] = {
            "scheduler": memory_status.get("scheduler", "FSRS"),
            "due_count": len(due_kps),
            "due_kps": due_kps,
            "cards": cards,
            "strategies": [],
        }
        if due_kps:
            section["strategies"].append(
                {"type": "间隔重复复习",
                 "action": f"FSRS 已调度 {len(due_kps)} 个知识点到期复习（{', '.join(due_kps[:5])}），请优先完成复习队列"}
            )
        # 记忆保持预警：可提取性低于阈值的卡片
        low_retention = [
            kp for kp, c in cards.items() if c.get("retrievability", 1.0) < 0.8
        ]
        if low_retention:
            section["strategies"].append(
                {"type": "记忆保持预警",
                 "action": f"以下知识点记忆可提取性低于 0.8，建议加入今日复习：{', '.join(low_retention[:5])}"}
            )
        if not section["strategies"]:
            section["strategies"].append(
                {"type": "记忆状态良好", "action": "暂无到期复习，按 FSRS 计划继续学习"}
            )
        return section

    def _calc_accuracy(self, quiz_history: List[Dict[str, Any]]) -> float:
        """正确率"""
        if not quiz_history:
            return 0.0
        total = sum(_safe_int(q.get("total_questions")) for q in quiz_history)
        correct = sum(_safe_int(q.get("correct_count")) for q in quiz_history)
        return (correct / total * 100) if total > 0 else 0.0

    def _calc_mastery(self, quiz_history: List[Dict[str, Any]]) -> float:
        """掌握度：基于最近5次测验的加权平均（越近权重越高）"""
        if not quiz_history:
            return 0.0
        recent = quiz_history[-5:]
        weights = [0.1, 0.15, 0.2, 0.25, 0.3][-len(recent):]
        scores = [_safe_float(q.get("score")) for q in recent]
        total_weight = sum(weights)
        if total_weight == 0:
            return 0.0
        mastery = sum(s * w for s, w in zip(scores, weights)) / total_weight
        return mastery

    @staticmethod
    def _theta_to_mastery(theta: float) -> float:
        """IRT 能力 θ → 掌握度（0-100）：标准正态百分位 Φ(θ)·100。

        IRT MAP 估计采用先验 θ~N(0,1)，θ=0 即同龄群体中位水平（50 分），
        Φ 变换保证 θ 越高掌握度单调越高，且量纲与加权平均分可比。
        """
        cdf = 0.5 * (1.0 + math.erf(float(theta) / math.sqrt(2.0)))
        return max(0.0, min(100.0, cdf * 100.0))

    def _calc_improvement_rate(self, quiz_history: List[Dict[str, Any]]) -> float:
        """
        提升速率：基于测验历史计算趋势
        - 6次以上：最近3次与之前3次的平均分差异
        - 3-5次：最近n次的线性回归斜率
        - 2次：两次得分差
        - 1次或0次：返回0
        """
        if not quiz_history:
            return 0.0

        scores = [_safe_float(q.get("score")) for q in quiz_history]

        if len(scores) < 2:
            return 0.0

        # 6次以上：使用标准的3对3比较
        if len(scores) >= 6:
            recent_avg = sum(scores[-3:]) / 3.0
            past_avg = sum(scores[-6:-3]) / 3.0
            return recent_avg - past_avg

        # 2-5次：使用线性回归斜率（归一化到每场变化）
        n = len(scores)
        x = list(range(n))
        mean_x = sum(x) / n
        mean_y = sum(scores) / n
        numerator = sum((x[i] - mean_x) * (scores[i] - mean_y) for i in range(n))
        denominator = sum((x[i] - mean_x) ** 2 for i in range(n))
        slope = numerator / denominator if denominator != 0 else 0.0
        # 将斜率转换为每场变化量（与3对3比较的量级相当）
        return slope

    def _calc_weakness_concentration(self, quiz_history: List[Dict[str, Any]], weak_areas: List[str]) -> float:
        """薄弱点集中度：0~1，越高说明薄弱点越集中"""
        if not quiz_history or not weak_areas:
            return 0.0
        # (Counter imported at top level)
        all_weak_tags = []
        for q in quiz_history[-5:]:
            tags = q.get("weak_tags") or []
            all_weak_tags.extend(tags)
        if not all_weak_tags:
            return 0.0
        counts = Counter(all_weak_tags)
        # Herfindahl-like concentration
        total = len(all_weak_tags)
        hhi = sum((c / total) ** 2 for c in counts.values())
        return hhi

    def _predict_next_score(self, quiz_history: List[Dict[str, Any]], improvement_rate: float) -> float:
        """预测下次测验得分：上次得分 + 提升速率的一半，钳位 [0,100]"""
        if not quiz_history:
            return 50.0
        last_score = _safe_float(quiz_history[-1].get("score"), 50.0)
        # 基于提升速率预测：近期上升则给更高预期
        predicted = last_score + improvement_rate * 0.5
        return max(0.0, min(100.0, predicted))

    def _predict_loss_points(self, quiz_history: List[Dict[str, Any]], weak_areas: List[str]) -> List[Dict[str, Any]]:
        """潜在失分点预测"""
        if not quiz_history:
            return []
        # (Counter imported at top level)
        all_weak_tags = []
        for q in quiz_history[-5:]:
            tags = q.get("weak_tags") or []
            all_weak_tags.extend(tags)
        if not all_weak_tags:
            return []
        counts = Counter(all_weak_tags)
        total = len(all_weak_tags)
        loss_points = []
        for tag, count in counts.most_common(5):
            loss_points.append({
                "tag": tag,
                "frequency": count,
                "risk_score": round(count / total, 4),
                "suggestion": f"重点复习 '{tag}' 相关知识点",
            })
        return loss_points

    def _predict_efficiency_trend(self, learning_records: List[Dict[str, Any]], quiz_history: List[Dict[str, Any]]) -> str:
        """学习效率走势预测"""
        improvement = self._calc_improvement_rate(quiz_history)
        if improvement > 5:
            return "上升"
        elif improvement < -5:
            return "下降"
        return "平稳"

    def _weak_area_distribution(self, quiz_history: List[Dict[str, Any]]) -> Dict[str, int]:
        """薄弱点分布"""
        # (Counter imported at top level)
        all_tags = []
        for q in quiz_history:
            tags = q.get("weak_tags") or []
            all_tags.extend(tags)
        return dict(Counter(all_tags).most_common(10))

    def _generate_intervention(
        self,
        accuracy: float,
        mastery: float,
        improvement_rate: float,
        weakness_concentration: float,
        weak_areas: List[str],
    ) -> Dict[str, Any]:
        """生成干预策略"""
        strategies = []
        if accuracy < 60:
            strategies.append({"type": "基础巩固", "action": "回归基础概念，减少高难度练习"})
        if mastery < 50:
            strategies.append({"type": "掌握度提升", "action": "增加间隔重复练习频次"})
        if improvement_rate < -5:
            strategies.append({"type": "趋势干预", "action": "调整学习策略，尝试不同资源类型"})
        if weakness_concentration > 0.6 and weak_areas:
            strategies.append({"type": "薄弱点突破", "action": f"集中攻克: {', '.join(weak_areas[:3])}"})
        if not strategies:
            strategies.append({"type": "保持现状", "action": "当前状态良好，继续按计划学习"})

        return {
            "priority": "high" if (accuracy < 60 or improvement_rate < -10) else "normal",
            "strategies": strategies,
        }
