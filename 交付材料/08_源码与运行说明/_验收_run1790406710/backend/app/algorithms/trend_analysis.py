"""
多因素趋势分析算法
功能：预测掌握度趋势、识别学习瓶颈、掉队预警
6大计算维度：
  1. 知识掌握度趋势（35%）
  2. 学习速度比例（15%，按 action 类型加权）
  3. 学习时间效率（15%）
  4. 薄弱点优先级得分（15%）
  5. 连续学习稳定性（5%）
  6. 知识点完成率（15%，complete 动作占比 + 完成质量）
输出：趋势因子、趋势状态、未来3天掌握度预测、干预建议

AIC 算法增强（TrendWeightLearner）：
  - 6 因子权重可由历史数据学习（L2 正则逻辑回归，标签=随后一周掉队/中断）
  - 已训练时用学习到的符号归一化权重计算趋势因子，并输出掉队预警概率
    warning_probability = σ(w·x + b)；未训练时回退人工先验权重（weight_source 标注）
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, timezone
from collections import defaultdict, Counter
import math

import numpy as np


def _safe_float(value: Any, default: float = 0.0) -> float:
    """安全转换为浮点数（容忍 None / 字符串 / 非法值）。"""
    if value is None:
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def _safe_int(value: Any, default: int = 0) -> int:
    if value is None:
        return default
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return default


class TrendWeightLearner:
    """趋势掉队预警学习器（numpy 逻辑回归，L2 正则，符号归一化权重输出）。

    样本：{"dimensions": {6 维因子（各 ∈ [-1,1]）}, "label": 0/1}
    标签语义：1 = 随后一周平均分下滑或学习中断（掉队），0 = 正常推进。
    """

    FEATURE_ORDER = [
        "mastery_trend", "speed_ratio", "time_efficiency",
        "weakness_priority", "stability", "completion_rate",
    ]

    def __init__(self, lr: float = 0.3, epochs: int = 600, l2: float = 1e-3) -> None:
        self.lr = lr
        self.epochs = epochs
        self.l2 = l2
        self._coef: Optional[np.ndarray] = None   # (6,)
        self._intercept: float = 0.0
        self._train_info: Dict[str, Any] = {}

    # ------------------------------------------------------------------ 训练
    def fit(self, samples: List[Dict[str, Any]]) -> Dict[str, Any]:
        X_list, y_list = [], []
        for s in samples or []:
            dims = s.get("dimensions") or {}
            if not isinstance(dims, dict):
                continue
            X_list.append([_safe_float(dims.get(k)) for k in self.FEATURE_ORDER])
            y_list.append(1 if s.get("label") else 0)
        if len(X_list) < 10:
            return {"status": "error", "message": f"训练样本不足（{len(X_list)} < 10）"}
        X = np.clip(np.array(X_list, dtype=np.float64), -1.0, 1.0)
        y = np.array(y_list, dtype=np.float64)
        # 类别不均衡保护：两类都至少要有 2 个样本
        if len(set(y.tolist())) < 2 or min(y.mean(), 1 - y.mean()) * len(y) < 2:
            return {"status": "error", "message": "正负样本过少，无法训练（需两类均有 ≥2 样本）"}

        coef = np.zeros(X.shape[1])
        intercept = 0.0
        prev_loss = float("inf")
        epochs_run = 0
        n = len(y)
        for epoch in range(self.epochs):
            z = X @ coef + intercept
            p = 1.0 / (1.0 + np.exp(-np.clip(z, -30, 30)))
            # 交叉熵 + L2（数值稳定版 BCE 梯度：p - y）
            loss = (-np.mean(y * np.log(np.clip(p, 1e-9, None))
                             + (1 - y) * np.log(np.clip(1 - p, 1e-9, None)))
                    + self.l2 * float(np.sum(coef ** 2)))
            if prev_loss - loss < 1e-8:
                break
            prev_loss = loss
            epochs_run = epoch + 1
            resid = p - y
            g_coef = X.T @ resid / n + 2.0 * self.l2 * coef
            g_int = float(np.mean(resid))
            coef = coef - self.lr * g_coef
            intercept = intercept - self.lr * g_int

        self._coef = coef
        self._intercept = float(intercept)
        proba = self.predict_proba_batch(X)
        accuracy = float(np.mean((proba >= 0.5) == (y == 1)))
        self._train_info = {
            "n_samples": int(n),
            "positive_ratio": round(float(y.mean()), 4),
            "epochs_run": epochs_run,
            "final_loss": round(float(loss), 6),
            "train_accuracy": round(accuracy, 4),
        }
        return {"status": "success", **self._train_info}

    # ------------------------------------------------------------------ 预测
    def predict_proba_batch(self, X: np.ndarray) -> np.ndarray:
        z = X @ self._coef + self._intercept
        return 1.0 / (1.0 + np.exp(-np.clip(z, -30, 30)))

    def predict_proba(self, dimensions: Dict[str, Any]) -> float:
        """掉队预警概率（0-1，越大越可能掉队）。未训练时返回 0.5。"""
        if self._coef is None:
            return 0.5
        x = np.array([_safe_float(dimensions.get(k)) for k in self.FEATURE_ORDER])
        return round(float(self.predict_proba_batch(x[None, :])[0]), 4)

    # ------------------------------------------------------------------ 输出
    @property
    def convex_weights(self) -> Dict[str, float]:
        """趋势因子融合权重：-coef_i / Σ|coef_j|。

        逻辑回归系数 β 指向"掉队"方向（β<0 的维度越积极越安全），而趋势因子
        语义是"越大越好"，故取负号后按绝对值归一化，与人工先验权重的极性一致。
        """
        if self._coef is None:
            return {k: 0.0 for k in self.FEATURE_ORDER}
        total = float(np.sum(np.abs(self._coef)))
        if total < 1e-12:
            return {k: 0.0 for k in self.FEATURE_ORDER}
        return {k: round(float(-c) / total, 4) for k, c in zip(self.FEATURE_ORDER, self._coef)}

    @property
    def is_fitted(self) -> bool:
        return self._coef is not None

    def serialize(self) -> Dict[str, Any]:
        coef = [] if self._coef is None else [round(float(c), 6) for c in self._coef]
        return {
            "coef": coef,
            "intercept": round(self._intercept, 6),
            "feature_order": self.FEATURE_ORDER,
        }

    def deserialize(self, data: Dict[str, Any]) -> bool:
        try:
            coef = [float(c) for c in (data.get("coef") or [])]
            if len(coef) != len(self.FEATURE_ORDER):
                return False
            self._coef = np.array(coef)
            self._intercept = float(data.get("intercept") or 0.0)
            return True
        except (TypeError, ValueError):
            return False


class MultiFactorTrendAnalyzer:
    """多因素趋势分析器"""

    # 权重配置（总和 = 1.0）
    WEIGHTS = {
        "mastery_trend": 0.35,
        "speed_ratio": 0.15,
        "time_efficiency": 0.15,
        "weakness_priority": 0.15,
        "stability": 0.05,
        "completion_rate": 0.15,
    }

    # action 强度权重：标记完成是最强信号
    ACTION_WEIGHTS = {
        "complete": 1.0,
        "practice": 0.6,
        "quiz": 0.7,
        "review": 0.5,
        "read": 0.3,
        "watch": 0.3,
    }

    def analyze(
        self,
        student_id: str,
        quiz_history: List[Dict[str, Any]],
        learning_records: List[Dict[str, Any]],
        weak_areas: List[str],
        profile: Dict[str, Any],
        weight_learner: Optional[TrendWeightLearner] = None,
    ) -> Dict[str, Any]:
        """
        主分析入口

        :param weight_learner: 可选，已训练的 TrendWeightLearner。提供且已拟合时
            用学习权重替代人工权重并输出掉队预警概率；否则回退人工先验。
        """
        # 1. 知识掌握度趋势
        mastery_trend = self._calc_mastery_trend(quiz_history)

        # 2. 学习速度比例（按 action 类型加权）
        speed_ratio = self._calc_speed_ratio(learning_records, profile)

        # 3. 学习时间效率
        time_efficiency = self._calc_time_efficiency(learning_records, quiz_history)

        # 4. 薄弱点优先级得分
        weakness_priority = self._calc_weakness_priority(weak_areas, quiz_history)

        # 5. 连续学习稳定性
        stability = self._calc_stability(learning_records)

        # 6. 知识点完成率（complete 动作占比 + 完成质量）
        completion_rate = self._calc_completion_rate(learning_records, quiz_history)

        dimensions = {
            "mastery_trend": mastery_trend,
            "speed_ratio": speed_ratio,
            "time_efficiency": time_efficiency,
            "weakness_priority": weakness_priority,
            "stability": stability,
            "completion_rate": completion_rate,
        }

        # 综合趋势因子（学习权重优先，人工权重兜底）
        if weight_learner is not None and weight_learner.is_fitted:
            weights = weight_learner.convex_weights
            weight_source = "learned"
        else:
            weights = dict(self.WEIGHTS)
            weight_source = "manual_prior"
        trend_factor = sum(dimensions[k] * weights[k] for k in weights)

        # 趋势状态判定
        trend_state = self._classify_trend_state(trend_factor, mastery_trend, stability)
        if weight_source == "learned":
            warning_probability = weight_learner.predict_proba(dimensions)
        else:
            # 规则兜底预警概率：状态映射（无训练数据时的可解释回退）
            warning_probability = {"warning": 0.9, "decline": 0.7, "stable": 0.35, "growth": 0.1}.get(
                trend_state, 0.5)

        # 未来3天掌握度预测（简单线性外推）
        predicted_mastery_3d = self._predict_mastery_3d(quiz_history, trend_factor)

        # 干预建议生成
        intervention = self._generate_intervention(
            trend_state, mastery_trend, speed_ratio, time_efficiency,
            weakness_priority, stability, completion_rate, weak_areas
        )

        return {
            "student_id": student_id,
            "trend_factor": round(trend_factor, 4),
            "trend_state": trend_state,
            "dimensions": {k: round(v, 4) for k, v in dimensions.items()},
            "weights_source": weight_source,
            "weights": {k: round(v, 4) for k, v in weights.items()},
            "warning_probability": warning_probability,
            "predicted_mastery_3d": round(predicted_mastery_3d, 4),
            "intervention": intervention,
            "analyzed_at": datetime.now(timezone.utc).isoformat(),
        }

    def _calc_mastery_trend(self, quiz_history: List[Dict[str, Any]]) -> float:
        """知识掌握度趋势：基于最近5次测验得分的线性斜率归一化"""
        if not quiz_history:
            return 0.0
        scores = [_safe_float(q.get("score")) for q in quiz_history[-5:]]
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
        """学习速度比例：按 action 类型加权后的实际/预期完成量"""
        if not learning_records:
            return 0.0
        # 按天累计加权动作数（complete 计 1.0，practice 0.6，read/watch 0.3）
        # (defaultdict imported at top level)
        daily_weight = defaultdict(float)
        for r in learning_records:
            date = r.get("created_at", "")[:10] if isinstance(r.get("created_at"), str) else ""
            if not date:
                continue
            action = str(r.get("action") or "").lower()
            w = self.ACTION_WEIGHTS.get(action, 0.3)
            daily_weight[date] += w
        if not daily_weight:
            return 0.0
        avg_daily = sum(daily_weight.values()) / len(daily_weight)
        expected_daily = profile.get("learning_tempo", {}).get("expected_daily_kps", 3)
        if expected_daily <= 0:
            expected_daily = 3
        ratio = avg_daily / expected_daily
        # 归一化：0.5倍预期 -> -1, 1倍 -> 0, 1.5倍 -> 1
        return max(-1.0, min(1.0, (ratio - 1.0) * 2.0))

    def _calc_time_efficiency(self, learning_records: List[Dict[str, Any]], quiz_history: List[Dict[str, Any]]) -> float:
        """学习时间效率：单位时间得分提升率"""
        total_duration = sum(_safe_float(r.get("duration")) for r in learning_records)
        if total_duration <= 0:
            return 0.0
        total_duration_hours = total_duration / 3600.0
        if len(quiz_history) >= 2:
            score_diff = _safe_float(quiz_history[-1].get("score")) - _safe_float(quiz_history[0].get("score"))
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
            recent_weak_tags.extend(q.get("weak_tags") or [])
        if not recent_weak_tags:
            return 0.0
        # 计算薄弱点集中度（重复出现比例高 -> 更需要关注，得分更低）
        # (Counter imported at top level)
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
        # (defaultdict imported at top level)
        daily_duration = defaultdict(int)
        for r in learning_records:
            date = r.get("created_at", "")[:10] if isinstance(r.get("created_at"), str) else ""
            if date:
                daily_duration[date] += _safe_int(r.get("duration"))
        if not daily_duration:
            return 0.0
        # 最近7天
        today = datetime.now(timezone.utc).date()
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

    def _calc_completion_rate(
        self,
        learning_records: List[Dict[str, Any]],
        quiz_history: List[Dict[str, Any]],
    ) -> float:
        """
        知识点完成率：
          - completed_kp = action='complete' 的去重 kp_id 数
          - touched_kp   = 出现过的所有 kp_id 数
          - 完成率 = completed_kp / max(touched_kp, 1)
          - 完成质量 = 这些 kp 在 quiz 中的平均分（若有）
          - 综合：0.7 * 完成率 + 0.3 * 质量；归一化到 -1~1
        """
        if not learning_records:
            return 0.0
        completed_kps = set()
        touched_kps = set()
        for r in learning_records:
            kp_id = r.get("kp_id")
            if not kp_id:
                continue
            touched_kps.add(kp_id)
            if str(r.get("action") or "").lower() == "complete" or _safe_float(r.get("progress")) >= 1.0:
                completed_kps.add(kp_id)
        if not touched_kps:
            return 0.0
        completion_ratio = len(completed_kps) / len(touched_kps)

        # 完成质量：已完成 kp 在 quiz 中的平均分
        quality = 0.0
        if completed_kps and quiz_history:
            scores = [
                _safe_float(q.get("score"))
                for q in quiz_history
                if q.get("kp_id") in completed_kps
            ]
            if scores:
                quality = sum(scores) / len(scores) / 100.0  # 0~1
        else:
            # 没 quiz 数据时，给完成率本身一个基线 0.6
            quality = 0.6

        score = 0.7 * completion_ratio + 0.3 * quality
        # 归一化：0.5 -> 0, 1.0 -> 1, 0.0 -> -1
        return max(-1.0, min(1.0, (score - 0.5) * 2.0))

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
        last_score = _safe_float(quiz_history[-1].get("score"), 50.0)
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
        completion_rate: float,
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
        if completion_rate < -0.3:
            suggestions.append("知识点完成率偏低：浏览过的章节请尽量点击「标记完成」并配合练习。")
        elif completion_rate > 0.4:
            suggestions.append("完成率出色：保持当前节奏，可挑战更高难度的综合题。")

        if not suggestions:
            suggestions.append("当前学习状态平稳，请继续保持。")

        return " ".join(suggestions)
