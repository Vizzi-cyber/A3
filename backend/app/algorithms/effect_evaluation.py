"""
学习效果评估与预测算法
- 实时计算：正确率、掌握度、提升速率、薄弱点集中度
- 预测：下次测验得分、潜在失分点、学习效率走势
- 输出：评估报告、数据看板、干预策略
"""
from typing import Dict, Any, List
from datetime import datetime, timezone
import math


class LearningEffectEvaluator:
    """学习效果评估器"""

    def evaluate(
        self,
        student_id: str,
        quiz_history: List[Dict[str, Any]],
        learning_records: List[Dict[str, Any]],
        weak_areas: List[str],
    ) -> Dict[str, Any]:
        """综合评估入口"""
        accuracy = self._calc_accuracy(quiz_history)
        mastery = self._calc_mastery(quiz_history)
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
            "predictions": {
                "next_score": round(next_score_prediction, 2),
                "potential_loss_points": potential_loss_points,
                "efficiency_trend": efficiency_trend,
            },
            "intervention": intervention,
            "dashboard": {
                "score_history": [q.get("score", 0) for q in quiz_history],
                "weak_area_distribution": self._weak_area_distribution(quiz_history),
            },
        }

    def _calc_accuracy(self, quiz_history: List[Dict[str, Any]]) -> float:
        """正确率"""
        if not quiz_history:
            return 0.0
        total = sum(q.get("total_questions", 0) for q in quiz_history)
        correct = sum(q.get("correct_count", 0) for q in quiz_history)
        return (correct / total * 100) if total > 0 else 0.0

    def _calc_mastery(self, quiz_history: List[Dict[str, Any]]) -> float:
        """掌握度：基于最近5次测验的加权平均（越近权重越高）"""
        if not quiz_history:
            return 0.0
        recent = quiz_history[-5:]
        weights = [0.1, 0.15, 0.2, 0.25, 0.3][-len(recent):]
        scores = [q.get("score", 0) for q in recent]
        total_weight = sum(weights)
        if total_weight == 0:
            return 0.0
        mastery = sum(s * w for s, w in zip(scores, weights)) / total_weight
        return mastery

    def _calc_improvement_rate(self, quiz_history: List[Dict[str, Any]]) -> float:
        """提升速率：最近3次与之前3次的平均分差异"""
        if len(quiz_history) < 6:
            return 0.0
        recent_avg = sum(q.get("score", 0) for q in quiz_history[-3:]) / 3.0
        past_avg = sum(q.get("score", 0) for q in quiz_history[-6:-3]) / 3.0
        return recent_avg - past_avg

    def _calc_weakness_concentration(self, quiz_history: List[Dict[str, Any]], weak_areas: List[str]) -> float:
        """薄弱点集中度：0~1，越高说明薄弱点越集中"""
        if not quiz_history or not weak_areas:
            return 0.0
        from collections import Counter
        all_weak_tags = []
        for q in quiz_history[-5:]:
            all_weak_tags.extend(q.get("weak_tags", []))
        if not all_weak_tags:
            return 0.0
        counts = Counter(all_weak_tags)
        # Herfindahl-like concentration
        total = len(all_weak_tags)
        hhi = sum((c / total) ** 2 for c in counts.values())
        return hhi

    def _predict_next_score(self, quiz_history: List[Dict[str, Any]], improvement_rate: float) -> float:
        """预测下次测验得分"""
        if not quiz_history:
            return 50.0
        last_score = quiz_history[-1].get("score", 50.0)
        # 基于提升速率预测
        predicted = last_score + improvement_rate * 0.5
        # 添加一点随机波动模拟
        return max(0.0, min(100.0, predicted))

    def _predict_loss_points(self, quiz_history: List[Dict[str, Any]], weak_areas: List[str]) -> List[Dict[str, Any]]:
        """潜在失分点预测"""
        if not quiz_history:
            return []
        from collections import Counter
        all_weak_tags = []
        for q in quiz_history[-5:]:
            all_weak_tags.extend(q.get("weak_tags", []))
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
        from collections import Counter
        all_tags = []
        for q in quiz_history:
            all_tags.extend(q.get("weak_tags", []))
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
