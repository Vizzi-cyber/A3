"""
图知识追踪引擎（GKT，Graph-based Knowledge Tracing）

在知识点前置依赖图上做图卷积传播掌握度，并提供可学习的门控参数：
  - 将 BKT/IRT 的逐点掌握度作为节点特征 X
  - 图卷积传播：H = A_hat^k · X（拉普拉斯归一化邻接矩阵，k 跳聚合）
  - 门控融合：mastery_final = α·X + (1-α)·(w·H + b)
  - 可学习参数：传播增益 w（非负投影，保持单调可解释）、偏置 b、
    融合门 α = σ(g)（sigmoid 门控），以「今日掌握度 → 明日掌握度」的
    自监督 MSE 训练（无需标注，历史快照即训练数据）

算法（可写进技术方案）：
  - 邻接矩阵 A（前置依赖边，对称化 + 自环）
  - A_hat = D^(-1/2) · (A + I) · D^(-1/2)（拉普拉斯归一化，GCN 标准做法）
  - 传播：X_k = A_hat^k · X（k 跳平滑）
  - 融合：mastery_final = α·X + (1-α)·(w·X_k + b)
  - 训练：min Σ‖f(X_t) − X_{t+1}‖²（全批梯度下降 + 早停，w ≥ 0 投影）

参考：GKT, IEEE/WIC/ACM WI 2019（无 arXiv 预印本）；Kipf & Welling, ICLR 2017（GCN）。
未训练时 w=1、b=0、α 取构造参数，退化为确定性图卷积平滑（向后兼容）。
"""
from typing import Any, Dict, List, Optional

import numpy as np


def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + np.exp(-x))


class GKTEngine:
    """图知识追踪：可学习门控图卷积（掌握度传播）。"""

    def __init__(self, alpha: float = 0.6, hops: int = 2, lr: float = 0.3, epochs: int = 400) -> None:
        """
        :param alpha: 未训练时的自身掌握度权重（0-1，越大越保留原值）
        :param hops:   图卷积传播跳数（邻居影响范围）
        :param lr:     训练学习率
        :param epochs: 训练最大轮数（早停可提前结束）
        """
        self.alpha = alpha
        self.hops = hops
        self.lr = lr
        self.epochs = epochs
        self.kp_ids: List[str] = []
        self.adj_norm: Optional[np.ndarray] = None  # 归一化邻接矩阵
        self._fitted = False
        # 可学习参数（未训练时退化为恒等传播）
        self._w = 1.0                       # 邻居传播增益（w ≥ 0，单调约束）
        self._b = 0.0                       # 传播偏置
        self._alpha_learned: Optional[float] = None  # 训练后的融合门

    def build_graph(self, kp_ids: List[str], edges: List[tuple]) -> None:
        """
        构建知识点依赖图并归一化。

        :param kp_ids: 全部知识点 ID（顺序固定，特征向量按此序）
        :param edges:  前置依赖边 [(pre_kp, cur_kp), ...]
        """
        self.kp_ids = list(kp_ids)
        n = len(kp_ids)
        idx = {k: i for i, k in enumerate(kp_ids)}
        A = np.zeros((n, n))
        for pre, cur in edges:
            if pre in idx and cur in idx:
                A[idx[pre], idx[cur]] = 1.0
                A[idx[cur], idx[pre]] = 1.0  # 对称化（双向影响）
        A += np.eye(n)  # 自环
        # 拉普拉斯归一化：D^-1/2 (A+I) D^-1/2
        deg = A.sum(axis=1)
        d_inv_sqrt = np.diag(1.0 / np.sqrt(np.maximum(deg, 1e-8)))
        self.adj_norm = d_inv_sqrt @ A @ d_inv_sqrt
        self._fitted = False

    def _smooth(self, X: np.ndarray) -> np.ndarray:
        """k 跳图卷积平滑（结构部分，不含可学习参数）。"""
        H = X.copy()
        for _ in range(self.hops):
            H = self.adj_norm @ H
        return H

    # ------------------------------------------------------------------ 训练
    def fit(self, sequences: List[List[Dict[str, float]]]) -> Dict[str, Any]:
        """
        自监督训练门控参数：以「t 日掌握度快照 → t+1 日快照」为样本。

        :param sequences: 每个学生一条时间有序快照序列 [{kp_id: mastery 0-1}, ...]
                          （快照键 ⊆ build_graph 的 kp_ids；序列长度 ≥ 2 才产生样本）
        :return: {"status", "n_pairs", "epochs_run", "initial_loss", "final_loss",
                  "params": {w, b, alpha}}
        """
        if not self._fitted_graph():
            return {"status": "error", "message": "请先 build_graph 构建知识点依赖图"}

        pairs: List[tuple] = []
        for snaps in sequences or []:
            valid = [s for s in snaps if s]
            for x_t, x_next in zip(valid[:-1], valid[1:]):
                x_vec = np.array([np.clip(x_t.get(k, 0.0), 0.0, 1.0) for k in self.kp_ids])
                y_vec = np.array([np.clip(x_next.get(k, 0.0), 0.0, 1.0) for k in self.kp_ids])
                pairs.append((x_vec, y_vec))
        if len(pairs) < 2:
            return {"status": "error", "message": f"训练样本不足（{len(pairs)} 对，至少 2 对）"}

        X = np.stack([p[0] for p in pairs])          # (n_pairs, n_kp)
        Y = np.stack([p[1] for p in pairs])
        H = np.stack([self._smooth(x) for x in X])   # (n_pairs, n_kp)
        n = len(pairs)

        # 参数初始化：w=1, b=0, g=logit(alpha)（未训练语义）
        w, b = 1.0, 0.0
        g = float(np.log(max(self.alpha, 1e-4) / max(1.0 - self.alpha, 1e-4)))
        prev_loss = float("inf")
        initial_loss = None
        epochs_run = 0

        for epoch in range(self.epochs):
            a = _sigmoid(g)
            pred = a * X + (1.0 - a) * (w * H + b)
            resid = pred - Y
            loss = float(np.mean(resid ** 2))
            if initial_loss is None:
                initial_loss = loss
            if prev_loss - loss < 1e-8:
                break
            prev_loss = loss
            epochs_run = epoch + 1

            # 梯度（MSE 对各参数）
            d_pred = 2.0 * resid / resid.size
            g_w = float(np.sum(d_pred * (1.0 - a) * H))
            g_b = float(np.sum(d_pred) * (1.0 - a))
            g_g = float(np.sum(d_pred * (a * (1.0 - a)) * (X - (w * H + b))))
            # 更新 + w 非负投影（保持"邻居掌握度高 → 传播值高"的单调可解释性）
            w = max(w - self.lr * g_w, 0.0)
            b = b - self.lr * g_b
            g = g - self.lr * g_g

        self._w = float(w)
        self._b = float(b)
        self._alpha_learned = float(_sigmoid(g))
        return {
            "status": "success",
            "n_pairs": int(n),
            "epochs_run": epochs_run,
            "initial_loss": round(float(initial_loss), 6),
            "final_loss": round(float(np.mean((self._forward(X, H) - Y) ** 2)), 6),
            "params": {
                "w": round(self._w, 4),
                "b": round(self._b, 4),
                "alpha": round(self._alpha_learned, 4),
            },
        }

    def _forward(self, X: np.ndarray, H: np.ndarray) -> np.ndarray:
        a = self._alpha_learned if self._alpha_learned is not None else self.alpha
        return a * X + (1.0 - a) * (self._w * H + self._b)

    def _fitted_graph(self) -> bool:
        return self.adj_norm is not None and bool(self.kp_ids)

    # ------------------------------------------------------------------ 传播
    def propagate(self, mastery_map: Dict[str, float]) -> Dict[str, float]:
        """
        图卷积传播掌握度。

        :param mastery_map: {kp_id: mastery 0-1}
        :return: {kp_id: 图感知掌握度}（训练后使用可学习 w/b/α，未训练时确定性平滑）
        """
        if not self._fitted_graph() or self.adj_norm is None:
            return dict(mastery_map)

        n = len(self.kp_ids)
        X = np.zeros(n)
        for i, kp in enumerate(self.kp_ids):
            X[i] = np.clip(mastery_map.get(kp, 0.0), 0.0, 1.0)

        H = self._smooth(X)
        final = np.clip(self._forward(X, H), 0.0, 1.0)
        return {
            kp: round(float(v), 4)
            for kp, v in zip(self.kp_ids, final)
        }

    def get_params(self) -> Dict[str, Any]:
        """当前门控参数（未训练时返回退化默认值）。"""
        a = self._alpha_learned if self._alpha_learned is not None else self.alpha
        return {"w": round(self._w, 4), "b": round(self._b, 4),
                "alpha": round(float(a), 4), "learned": self._alpha_learned is not None}

    @property
    def is_fitted(self) -> bool:
        return self._fitted_graph() and self._alpha_learned is not None
