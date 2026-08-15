"""
Thompson Sampling 自适应选题器（多臂老虎机 MAB）

基于 mabwiser（Fidelity AI Center of Excellence，ICTAI 2019 / IJAIT 2021）
实现 Thompson Sampling 选题策略，解决"下一题/下一资源选什么"的
探索-利用（exploration-exploitation）权衡：
  - 探索：给未充分练习的题目机会，发现学生薄弱点
  - 利用：多选历史收益高的题目，维持学习效率

教育场景实证：ZPDES（arXiv:2402.01669）用 MAB 做选题，265 名儿童
随机对照实验验证优于人工课程。

用于：每日练习选题（daily_quiz）、资源推荐多样性（weighted_matching）、
路径调整决策（path_planning_dag.adjust_path）。
"""
from typing import Any, Dict, List, Optional

import numpy as np
from mabwiser.mab import MAB, LearningPolicy


class ThompsonSamplingSelector:
    """Thompson Sampling 选题器（mabwiser 封装）。"""

    def __init__(self, arms: List[str], seed: int = 42) -> None:
        """
        :param arms: 候选臂（题目/资源/策略的标识符列表）
        :param seed: 随机种子（可复现）
        """
        self._arms = [str(a) for a in arms]
        self._rng = np.random.default_rng(seed)
        self._mab = MAB(
            self._arms,
            LearningPolicy.ThompsonSampling(
                binarizer=lambda arm, reward: 1 if float(reward) >= 0.5 else 0
            ),
            seed=seed,
        )
        self._decisions: List[str] = []
        self._rewards: List[float] = []
        self._trained = False

    # ------------------------------------------------------------------ 选择
    def select(self, k: int = 1, exclude: Optional[List[str]] = None) -> List[str]:
        """
        选择 k 个候选臂（按期望收益降序）。

        :param k: 返回数量（默认 1）
        :param exclude: 排除的臂（如已选过的题目）
        """
        if not self._arms:
            return []
        exclude = set(exclude or [])
        candidates = [a for a in self._arms if a not in exclude]
        if not candidates:
            return []

        if not self._trained or len(self._decisions) < len(set(self._arms)):
            # 冷启动：均匀随机采样（保证每个臂都被探索）
            picked = [str(a) for a in self._rng.choice(candidates, size=min(k, len(candidates)), replace=False)]
            return picked

        try:
            expectations = self._mab.predict_expectations()
            ranked = sorted(candidates, key=lambda a: -float(expectations.get(a, 0.0)))
            return ranked[:k]
        except Exception:
            # 兜底：随机
            picked = [str(a) for a in self._rng.choice(candidates, size=min(k, len(candidates)), replace=False)]
            return picked

    # ------------------------------------------------------------------ 反馈
    def update(self, arm: str, reward: float) -> None:
        """
        反馈一个臂的收益并更新策略。

        :param arm:    被选中的臂
        :param reward: 收益（0-1，如答对=1 / 答错=0，或完成度）
        """
        arm = str(arm)
        if arm not in self._arms:
            return
        self._decisions.append(arm)
        self._rewards.append(float(np.clip(reward, 0.0, 1.0)))
        try:
            self._mab.partial_fit([arm], [float(np.clip(reward, 0.0, 1.0))])
        except Exception:
            # 不支持 partial_fit 时退化为全量重训（数据量小，开销可忽略）
            self._mab = MAB(
                self._arms,
                LearningPolicy.ThompsonSampling(
                    binarizer=lambda arm, reward: 1 if float(reward) >= 0.5 else 0
                ),
                seed=42,
            )
            self._mab.fit(self._decisions, self._rewards)
        self._trained = True

    # ------------------------------------------------------------------ 状态
    def get_expectations(self) -> Dict[str, float]:
        """各臂的期望收益（0-1）。"""
        if not self._trained:
            return {a: 0.5 for a in self._arms}
        try:
            raw = self._mab.predict_expectations()
            return {a: round(float(raw.get(a, 0.5)), 4) for a in self._arms}
        except Exception:
            return {a: 0.5 for a in self._arms}

    def get_stats(self) -> Dict[str, Any]:
        """统计信息（试炼次数、收益、期望）。"""
        counts: Dict[str, int] = {}
        rewards: Dict[str, float] = {}
        for arm, reward in zip(self._decisions, self._rewards):
            counts[arm] = counts.get(arm, 0) + 1
            rewards[arm] = rewards.get(arm, 0.0) + reward
        return {
            "arms": self._arms,
            "trained": self._trained,
            "n_updates": len(self._decisions),
            "arm_counts": counts,
            "arm_avg_reward": {
                a: round(rewards.get(a, 0.0) / counts[a], 4) for a in counts
            },
            "expectations": self.get_expectations(),
        }

    @property
    def arms(self) -> List[str]:
        return list(self._arms)
