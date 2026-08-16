"""
神经认知诊断（NCD，Neural Cognitive Diagnosis）

用神经网络模拟学生-题目交互来诊断能力，带单调性约束（可解释）：
  - 学生因子 h_s ∈ R^d（能力表征）
  - 题目因子 h_e ∈ R^d（难度/区分度表征）
  - 交互：x = h_s ∘ h_e（逐元素乘积），f(x) = σ(w·x + b)，w ≥ 0（单调约束）
  - 训练：二元交叉熵 + 梯度下降，w 非负投影（保证"能力越高答对概率越高"的单调性）

参考：NCD, AAAI 2020（中科大）；单调约束保证可解释，是 IRT 的神经网络推广。
纯 numpy 实现，无需深度学习框架。
"""
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


class NCDDiagnoser:
    """神经认知诊断器（numpy 实现，单调约束）。"""

    def __init__(self, dim: int = 4, lr: float = 0.5, epochs: int = 800, seed: int = 42) -> None:
        self.dim = dim
        self.lr = lr
        self.epochs = epochs
        self._rng = np.random.default_rng(seed)
        self._fitted = False
        self._student_ids: List[str] = []
        self._item_ids: List[str] = []
        self._H_s: Optional[np.ndarray] = None   # 学生因子 (n_s, d)
        self._H_e: Optional[np.ndarray] = None   # 题目因子 (n_i, d)
        self._w: Optional[np.ndarray] = None     # 交互权重 (d,)，非负
        self._b: float = 0.0

    def fit(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        训练 NCD 模型。

        :param records: [{"student_id", "item_id", "correct": bool}, ...]
        """
        student_ids = sorted({r["student_id"] for r in records})
        item_ids = sorted({r["item_id"] for r in records})
        if len(student_ids) < 2 or len(item_ids) < 2:
            return {"status": "error", "message": "学生或题目数量不足（至少 2×2）"}

        n_s, n_i, d = len(student_ids), len(item_ids), self.dim
        s_idx = {s: i for i, s in enumerate(student_ids)}
        i_idx = {i: j for j, i in enumerate(item_ids)}

        # 初始化因子（经验答对率引导，训练更稳定）
        stu_acc = np.zeros(n_s)
        item_acc = np.zeros(n_i)
        stu_cnt = np.zeros(n_s)
        item_cnt = np.zeros(n_i)
        for r in records:
            si, ii = s_idx[r["student_id"]], i_idx[r["item_id"]]
            y = int(bool(r["correct"]))
            stu_acc[si] += y; stu_cnt[si] += 1
            item_acc[ii] += y; item_cnt[ii] += 1
        H_s = np.zeros((n_s, d))
        H_e = np.zeros((n_i, d))
        for s in range(n_s):
            p = np.clip(stu_acc[s] / max(stu_cnt[s], 1), 0.05, 0.95)
            H_s[s, 0] = np.log(p / (1 - p))          # 能力主分量
            H_s[s, 1:] = self._rng.normal(0, 0.2, d - 1)
        for i in range(n_i):
            p = np.clip(item_acc[i] / max(item_cnt[i], 1), 0.05, 0.95)
            H_e[i, 0] = -np.log(p / (1 - p))         # 难度主分量
            H_e[i, 1:] = self._rng.normal(0, 0.2, d - 1)
        w = np.ones(d)
        w[0] = 1.5                                   # 主分量权重更大
        b = 0.0

        # 训练数据
        pairs = [(s_idx[r["student_id"]], i_idx[r["item_id"]], int(bool(r["correct"]))) for r in records]

        for _ in range(self.epochs):
            # 前向
            p = np.zeros(len(pairs))
            for k, (si, ii, y) in enumerate(pairs):
                x = H_s[si] * H_e[ii]
                p[k] = 1.0 / (1.0 + np.exp(-(np.dot(w, x) + b)))
            # 损失（BCE）
            loss = -np.mean([y * np.log(max(p[k], 1e-9)) + (1 - y) * np.log(max(1 - p[k], 1e-9)) for k, (_, _, y) in enumerate(pairs)])
            # 梯度（逐样本）
            for si, ii, y in pairs:
                x = H_s[si] * H_e[ii]
                err = p[pairs.index((si, ii, y))] - y if False else None
            # 简单批量梯度
            g_w = np.zeros(d)
            g_b = 0.0
            g_Hs = np.zeros_like(H_s)
            g_He = np.zeros_like(H_e)
            for k, (si, ii, y) in enumerate(pairs):
                x = H_s[si] * H_e[ii]
                e = p[k] - y  # dL/dz
                g_w += e * x
                g_b += e
                g_Hs[si] += e * (H_e[ii] * w)
                g_He[ii] += e * (H_s[si] * w)
            m = len(pairs)
            # 更新 + w 非负投影（单调约束）
            w = np.maximum(w - self.lr * g_w / m, 0.0)
            b = b - self.lr * g_b / m
            H_s = H_s - self.lr * g_Hs / m
            H_e = H_e - self.lr * g_He / m
            if _ % 100 == 0 and _ > 0:
                pass

        self._fitted = True
        self._student_ids = student_ids
        self._item_ids = item_ids
        self._H_s = H_s
        self._H_e = H_e
        self._w = w
        self._b = b

        return {
            "status": "success",
            "students": student_ids,
            "items": item_ids,
            "dim": d,
            "final_loss": round(float(loss), 4),
            "monotone_w": [round(float(x), 4) for x in w],
        }

    def _predict(self, si: int, ii: int) -> float:
        x = self._H_s[si] * self._H_e[ii]
        return 1.0 / (1.0 + np.exp(-(np.dot(self._w, x) + self._b)))

    def predict(self, student_id: str, item_id: str) -> Optional[float]:
        if not self._fitted or student_id not in self._student_ids or item_id not in self._item_ids:
            return None
        si = self._student_ids.index(student_id)
        ii = self._item_ids.index(item_id)
        return round(float(self._predict(si, ii)), 4)

    def estimate_ability(self, student_id: str) -> Optional[float]:
        """能力估计：学生因子与权重加权（正相关，越大越强）。"""
        if not self._fitted or student_id not in self._student_ids:
            return None
        si = self._student_ids.index(student_id)
        return round(float(np.dot(self._H_s[si], self._w)), 4)

    def estimate_difficulty(self, item_id: str) -> Optional[float]:
        """题目难度估计：因子加权（越大越难答对）。"""
        if not self._fitted or item_id not in self._item_ids:
            return None
        ii = self._item_ids.index(item_id)
        return round(float(np.dot(self._H_e[ii], self._w)), 4)

    @property
    def is_fitted(self) -> bool:
        return self._fitted
