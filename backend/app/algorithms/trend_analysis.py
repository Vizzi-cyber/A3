"""
多因素趋势分析算法
功能：预测掌握度趋势、识别学习瓶颈、掉队预警
5大计算维度：
  1. 知识掌握度趋势（40%）
  2. 学习速度比例（20%）
  3. 学习时间效率（15%）
  4. 薄弱点优先级得分（15%）
  5. 连续学习稳定性（10%）
输出：趋势因子、趋势状态、未来3天掌握度预测、干预建议
"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
import math


class MultiFactorTrendAnalyzer:
    """多因素趋势分析器"""

    # 权重配置
    WEIGHTS = {
        "mastery_trend": 0.40,
        "speed_ratio": 0.20,
        "time_efficiency": 0.15,
        "weakness_priority": 0.15,
        "stability": 0.10,
    }

    def analyze(
        self,
        student_id: str,
        quiz_history: List[Dict[str, Any]],
        learning_records: List[Dict[str, Any]],
        weak_areas: List[str],
        profile: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        主分析入口
        """
        # 1. 知识掌握度趋势
        mastery_trend = self._calc_mastery_trend(quiz_history)

        # 2. 学习速度比例
        speed_ratio = self._calc_speed_ratio(learning_records, profile)

        # 3. 学习时间效率
        time_efficiency = self._calc_time_efficiency(learning_records, quiz_history)

        # 4. 薄弱点优先级得分
        weakness_priority = self._calc_weakness_priority(weak_areas, quiz_history)

        # 5. 连续学习稳定性
        stability = self._calc_stability(learning_records)

        # 综合趋势因子
        trend_factor = (
            mastery_trend * self.WEIGHTS["mastery_trend"]
            + speed_ratio * self.WEIGHTS["speed_ratio"]
            + time_efficiency * self.WEIGHTS["time_efficiency"]
            + weakness_priority * self.WEIGHTS["weakness_priority"]
            + stability * self.WEIGHTS["stability"]
        )

        # 趋势状态判定
        trend_state = self._classify_trend_state(trend_factor, mastery_trend, stability)

        # 未来3天掌握度预测（简单线性外推）
        predicted_mastery_3d = self._predict_mastery_3d(quiz_history, trend_factor)

        # 干预建议生成
        intervention = self._generate_intervention(
            trend_state, mastery_trend, speed_ratio, time_efficiency, weakness_priority, stability, weak_areas
        )

        return {
            "student_id": student_id,
            "trend_factor": round(trend_factor, 4),
            "trend_state": trend_state,
            "dimensions": {
                "mastery_trend": round(mastery_trend, 4),
                "speed_ratio": round(speed_ratio, 4),
                "time_efficiency": round(time_efficiency, 4),
                "weakness_priority": round(weakness_priority, 4),
                "stability": round(stability, 4),
            },
            "predicted_mastery_3d": round(predicted_mastery_3d, 4),
            "intervention": intervention,
            "analyzed_at": datetime.now().isoformat(),
        }

    def _calc_mastery_trend(self, quiz_history: List[Dict[str, Any]]) -> float:
        """知识掌握度趋势：基于最近5次测验得分的线性斜率归一化"""
        if not quiz_history:
            return 0.0
        scores = [q.get("score", 0.0) for q in quiz_history[-5:]]
        if len(scores) < 2:
            return (scores[0] / 100.0 - 0.5) * 2 if scores else 0.0
        n = len(scores)
        x = list(range(n))
        mean_x = sum(x) / n
        mean_y = sum(scores) / n
        numerator = sum((x[i] - mean_x) * (scores[i] - mean_y) for i in range(n))
        denominator = sum((x[i] - mean_x) ** 2 for i in range(n))
        slope = numerator / denominator if denominator != 0 else 0.0
        # 斜率范围大概在 -20 ~ 20，归一化到 -1 ~ 1
        return max(-1.0, min(1.0, slope / 20.0))

    def _calc_speed_ratio(self, learning_records: List[Dict[str, Any]], profile: Dict[str, Any]) -> float:
        """学习速度比例：实际完成量 / 预期完成量"""
        if not learning_records:
            return 0.0
        # 按天统计完成的kp数
        from collections import defaultdict
        daily_kps = defaultdict(int)
        for r in learning_records:
            date = r.get("created_at", "")[:10] if isinstance(r.get("created_at"), str) else ""
            if date:
                daily_kps[date] += 1
        if not daily_kps:
            return 0.0
        avg_daily = sum(daily_kps.values()) / len(daily_kps)
        expected_daily = profile.get("learning_tempo", {}).get("expected_daily_kps", 3)
        if expected_daily <= 0:
            expected_daily = 3
        ratio = avg_daily / expected_daily
        # 归一化：0.5倍预期 -> -1, 1倍 -> 0, 1.5倍 -> 1
        return max(-1.0, min(1.0, (ratio - 1.0) * 2.0))

    def _calc_time_efficiency(self, learning_records: List[Dict[str, Any]], quiz_history: List[Dict[str, Any]]) -> float:
        """学习时间效率：单位时间得分提升率"""
        total_duration = sum(r.get("duration", 0) for r in learning_records)
        if total_duration <= 0:
            return 0.0
        total_duration_hours = total_duration / 3600.0
        if len(quiz_history) >= 2:
            score_diff = quiz_history[-1].get("score", 0) - quiz_history[0].get("score", 0)
            efficiency = score_diff / total_duration_hours if total_duration_hours > 0 else 0.0
        else:
            efficiency = 0.0
        # 归一化：-10 ~ 10 映射到 -1 ~ 1
        return max(-1.0, min(1.0, efficiency / 10.0))

    def _calc_weakness_priority(self, weak_areas: List[str], quiz_history: List[Dict[str, Any]]) -> float:
        """薄弱点优先级得分：薄弱点越多、越集中，得分越低（负向）"""
        if not weak_areas:
            return 0.5  # 没有薄弱点，表现良好
        # 统计薄弱标签在最近测验中的出现频率
        recent_weak_tags = []
        for q in quiz_history[-3:]:
            recent_weak_tags.extend(q.get("weak_tags", []))
        if not recent_weak_tags:
            return 0.0
        # 计算薄弱点集中度（重复出现比例高 -> 更需要关注，得分更低）
        from collections import Counter
        tag_counts = Counter(recent_weak_tags)
        max_count = max(tag_counts.values())
        total_count = len(recent_weak_tags)
        concentration = max_count / total_count if total_count > 0 else 0.0
        # 薄弱点数量惩罚
        num_penalty = min(1.0, len(weak_areas) / 10.0)
        # 综合：concentration高且num多 -> 接近 -1
        score = 0.5 - num_penalty * 0.5 - concentration * 0.5
        return max(-1.0, min(1.0, score))

    def _calc_stability(self, learning_records: List[Dict[str, Any]]) -> float:
        """连续学习稳定性：基于最近7天学习天数占比和标准差"""
        if not learning_records:
            return 0.0
        from collections import defaultdict
        daily_duration = defaultdict(int)
        for r in learning_records:
            date = r.get("created_at", "")[:10] if isinstance(r.get("created_at"), str) else ""
            if date:
                daily_duration[date] += r.get("duration", 0)
        if not daily_duration:
            return 0.0
        # 最近7天
        today = datetime.now().date()
        last_7_days = [(today - timedelta(days=i)).isoformat() for i in range(7)]
        study_days = sum(1 for d in last_7_days if daily_duration.get(d, 0) > 0)
        ratio = study_days / 7.0
        # 每天学习时长的标准差（稳定性）
        durations = [daily_duration.get(d, 0) / 3600.0 for d in last_7_days]
        mean_d = sum(durations) / len(durations)
        variance = sum((d - mean_d) ** 2 for d in durations) / len(durations)
        std = math.sqrt(variance)
        # std小 -> 稳定 -> 高分
        stability_score = ratio * (1.0 - min(1.0, std / 3.0))
        return max(-1.0, min(1.0, stability_score * 2 - 1))

    def _classify_trend_state(self, trend_factor: float, mastery_trend: float, stability: float) -> str:
        """趋势状态分类"""
        if trend_factor >= 0.3 and mastery_trend >= 0.2:
            return "growth"
        if trend_factor <= -0.4 or (mastery_trend <= -0.3 and stability < 0):
            return "warning"
        if trend_factor <= -0.15:
            return "decline"
        return "stable"

    def _predict_mastery_3d(self, quiz_history: List[Dict[str, Any]], trend_factor: float) -> float:
        """预测未来3天掌握度（百分制）"""
        if not quiz_history:
            return 50.0
        last_score = quiz_history[-1].get("score", 50.0)
        # 简单线性预测：每天变化量 = trend_factor * 5
        predicted = last_score + trend_factor * 5 * 3
        return max(0.0, min(100.0, predicted))

    def _generate_intervention(
        self,
        trend_state: str,
        mastery_trend: float,
        speed_ratio: float,
        time_efficiency: float,
        weakness_priority: float,
        stability: float,
        weak_areas: List[str],
    ) -> str:
        """根据各维度得分生成干预建议"""
        suggestions = []
        if trend_state == "warning":
            suggestions.append("学习状态预警：建议立即调整学习计划，重点复习薄弱知识点。")
        elif trend_state == "decline":
            suggestions.append("学习趋势下滑：建议减少新知识摄入，巩固已学内容。")
        elif trend_state == "growth":
            suggestions.append("学习状态良好：可适当加快学习节奏，挑战更高难度内容。")

        if speed_ratio < -0.3:
            suggestions.append("学习速度偏慢：建议将任务拆解为更小的单元，逐步完成。")
        if time_efficiency < -0.3:
            suggestions.append("时间效率较低：建议采用番茄工作法，提高专注度。")
        if weakness_priority < -0.3 and weak_areas:
            suggestions.append(f"薄弱点集中：重点攻克 {'、'.join(weak_areas[:3])}。")
        if stability < -0.3:
            suggestions.append("学习连续性不足：建议制定每日固定学习时段，保持学习节奏。")

        if not suggestions:
            suggestions.append("当前学习状态平稳，请继续保持。")

        return " ".join(suggestions)
