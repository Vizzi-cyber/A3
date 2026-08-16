"""
图知识追踪引擎（GKT，Graph-based Knowledge Tracing）

用图卷积（GCN）在知识点前置依赖图上传播掌握度：
  - 将 BKT/IRT 的逐点掌握度作为节点特征 X
  - 图卷积传播：H = A_hat^k · X（拉普拉斯归一化邻接矩阵，k 跳聚合）
  - 输出图感知掌握度：邻居知识点的掌握状态影响当前知识点

算法（可写进技术方案）：
  - 邻接矩阵 A（前置依赖边，对称化 + 自环）
  - A_hat = D^(-1/2) · (A + I) · D^(-1/2)（拉普拉斯归一化，GCN 标准做法）
  - 传播：X_k = A_hat^k · X（k 跳平滑）
  - 融合：mastery_final = α·X + (1-α)·X_k（保留自身 + 邻居影响）

参考：GKT, IEEE/WIC/ACM WI 2019（无 arXiv 预印本）；Kipf & Welling, ICLR 2017（GCN）。
"""
from typing import Any, Dict, List, Optional

import numpy as np


class GKTEngine:
    """图知识追踪：BKT 掌握度 + 图卷积传播 → 图感知掌握度。"""

    def __init__(self, alpha: float = 0.6, hops: int = 2) -> None:
        """
        :param alpha: 自身掌握度权重（0-1，越大越保留 BKT 原值）
        :param hops:   图卷积传播跳数（邻居影响范围）
        """
        self.alpha = alpha
        self.hops = hops
        self.kp_ids: List[str] = []
        self.adj_norm: Optional[np.ndarray] = None  # 归一化邻接矩阵
        self._fitted = False

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
        self._fitted = True

    def propagate(self, mastery_map: Dict[str, float]) -> Dict[str, float]:
        """
        图卷积传播掌握度。

        :param mastery_map: {kp_id: mastery 0-1}
        :return: {kp_id: 图感知掌握度}
        """
        if not self._fitted or not self.adj_norm is not None or not self.kp_ids:
            return dict(mastery_map)

        n = len(self.kp_ids)
        X = np.zeros(n)
        for i, kp in enumerate(self.kp_ids):
            X[i] = np.clip(mastery_map.get(kp, 0.0), 0.0, 1.0)

        # k 跳传播（图卷积平滑）
        H = X.copy()
        for _ in range(self.hops):
            H = self.adj_norm @ H

        # 融合：自身 + 邻居影响
        final = self.alpha * X + (1 - self.alpha) * H
        return {
            kp: round(float(np.clip(v, 0.0, 1.0)), 4)
            for kp, v in zip(self.kp_ids, final)
        }

    @property
    def is_fitted(self) -> bool:
        return self._fitted
