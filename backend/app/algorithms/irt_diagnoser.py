"""
IRT 认知诊断引擎（Item Response Theory Cognitive Diagnosis）

基于项目反应理论（Rasch, 1960; Baker & Kim, 2004《Item Response Theory:
Parameter Estimation Techniques》）实现 1PL/2PL 联合 MAP 估计：

  - 1PL（Rasch）：P(答对) = 1 / (1 + exp(-(θ - b)))
  - 2PL        ：P(答对) = 1 / (1 + exp(-a(θ - b)))

参数：θ 学生能力 / b 题目难度 / a 题目区分度。
先验：θ ~ N(0,1)，b ~ N(0,10)，log a ~ N(0,10)（MAP 估计，解决完美作答
导致的 MLE 无界与 2PL 尺度漂移；与 py-irt 的贝叶斯 IRT 思路一致）。
可识别性约束：学生能力 θ 中心化（均值 0）。

说明：PyPI 上的 py-irt（需 PyTorch+Pyro，且 requires_python <3.12）、lir
（重型贝叶斯框架）在 Python 3.14 环境不可用，故按标准算法自研实现，
公式源自教材，可直接写入技术方案并复核。

输出：学生能力 θ（替代"加权平均分"掌握度）、题目难度 b（替代人工难度
1-5 分级）、区分度 a，供效果评估、加权匹配、ADPP 学习成本模型使用。
"""
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from scipy.optimize import minimize


class IRTDiagnoser:
    """1PL/2PL IRT 认知诊断器（MAP 联合估计）。"""

    def __init__(self, model: str = "2pl", max_iter: int = 300) -> None:
        if model not in ("1pl", "2pl"):
            raise ValueError("model 必须是 '1pl' 或 '2pl'")
        self.model = model
        self.max_iter = max_iter
        self._fitted = False
        self._student_ids: List[str] = []
        self._item_ids: List[str] = []
        self._theta: np.ndarray = np.array([])          # 学生能力
        self._b: np.ndarray = np.array([])              # 题目难度
        self._a: np.ndarray = np.array([])              # 题目区分度
        self._log_likelihood: float = 0.0
        self._n_responses: int = 0

    # ------------------------------------------------------------------ 数据
    @staticmethod
    def build_response_matrix(quiz_results: List[Dict[str, Any]]) -> Tuple[np.ndarray, List[str], List[str]]:
        """
        将作答记录（逐题）构建为学生 × 题目 的 0/1 响应矩阵。

        输入元素：{"student_id", "item_id"(或 kp_id), "correct": bool}
        同一 (学生, 题目) 多次作答取最后一次。
        输出：(X, student_ids, item_ids)，X[i,j] ∈ {0,1}，缺失为 NaN。
        """
        records: Dict[Tuple[str, str], int] = {}
        for r in quiz_results:
            sid = str(r.get("student_id", ""))
            iid = str(r.get("item_id") or r.get("kp_id") or "")
            if not sid or not iid:
                continue
            records[(sid, iid)] = 1 if bool(r.get("correct", False)) else 0

        student_ids = sorted({k[0] for k in records})
        item_ids = sorted({k[1] for k in records})
        X = np.full((len(student_ids), len(item_ids)), np.nan)
        s_idx = {s: i for i, s in enumerate(student_ids)}
        i_idx = {i: j for j, i in enumerate(item_ids)}
        for (sid, iid), correct in records.items():
            X[s_idx[sid], i_idx[iid]] = correct
        return X, student_ids, item_ids

    # ------------------------------------------------------------------ 拟合
    def fit(self, quiz_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        拟合 IRT 模型（MAP 联合估计，scipy BFGS 优化）。

        :param quiz_results: 作答记录（见 build_response_matrix）
        :return: {"status", "model", "students", "items", "ability",
                  "difficulty", "discrimination", "log_likelihood"}
        """
        X, student_ids, item_ids = self.build_response_matrix(quiz_results)
        if X.shape[0] < 2 or X.shape[1] < 2:
            return {"status": "error", "message": "学生或题目数量不足（至少 2×2）"}

        n_students, n_items = X.shape

        # 初始化：θ~N(0,1)，b 用经验 logit，log a = 0（a=1）
        theta0 = np.zeros(n_students)
        b0 = np.zeros(n_items)
        for j in range(n_items):
            col = X[~np.isnan(X[:, j]), j]
            if col.size:
                p = float(np.clip(np.mean(col), 0.05, 0.95))
                b0[j] = -np.log(p / (1.0 - p))
        n_params = n_students + n_items + (n_items if self.model == "2pl" else 0)
        x0 = np.concatenate([theta0, b0, np.zeros(n_items)]) if self.model == "2pl" \
            else np.concatenate([theta0, b0])

        def objective(x: np.ndarray) -> float:
            th = x[:n_students]
            bj = x[n_students:n_students + n_items]
            if self.model == "1pl":
                P = 1.0 / (1.0 + np.exp(-(th[:, None] - bj[None, :])))
            else:
                a = np.exp(x[n_students + n_items:])
                P = 1.0 / (1.0 + np.exp(-a[None, :] * (th[:, None] - bj[None, :])))
            P = np.clip(P, 1e-12, 1 - 1e-12)
            nll = -float(np.nansum(X * np.log(P) + (1.0 - X) * np.log(1.0 - P)))
            # MAP 先验
            prior = 0.5 * float(np.sum(th ** 2)) + 0.05 * float(np.sum(bj ** 2))
            if self.model == "2pl":
                prior += 0.05 * float(np.sum(x[n_students + n_items:] ** 2))
            return nll + prior

        result = minimize(
            objective, x0, method="BFGS",
            options={"maxiter": self.max_iter, "gtol": 1e-5},
        )
        x = result.x
        theta = x[:n_students]
        b = x[n_students:n_students + n_items]
        log_a = x[n_students + n_items:] if self.model == "2pl" else np.zeros(n_items)

        # 可识别性：θ 中心化
        theta = theta - float(np.mean(theta))

        self._fitted = True
        self._student_ids = student_ids
        self._item_ids = item_ids
        self._theta = theta
        self._b = b
        self._a = np.exp(log_a) if self.model == "2pl" else np.ones(n_items)
        self._log_likelihood = result.fun
        self._n_responses = int(np.sum(~np.isnan(X)))

        return {
            "status": "success",
            "model": self.model,
            "converged": bool(result.success),
            "iterations": int(result.nit),
            "students": student_ids,
            "items": item_ids,
            "ability": {s: round(float(theta[i]), 4) for i, s in enumerate(student_ids)},
            "difficulty": {i: round(float(b[j]), 4) for j, i in enumerate(item_ids)},
            "discrimination": {i: round(float(self._a[j]), 4) for j, i in enumerate(item_ids)},
            "log_likelihood": round(self._log_likelihood, 4),
            "n_responses": self._n_responses,
        }

    # ------------------------------------------------------------------ 查询
    def estimate_ability(self, student_id: str) -> Optional[float]:
        """查询学生能力 θ。"""
        if not self._fitted:
            return None
        if student_id in self._student_ids:
            return round(float(self._theta[self._student_ids.index(student_id)]), 4)
        return None

    def get_item_difficulty(self, item_id: str) -> Optional[float]:
        """查询题目难度 b（可替代人工难度分级）。"""
        if not self._fitted:
            return None
        if item_id in self._item_ids:
            return round(float(self._b[self._item_ids.index(item_id)]), 4)
        return None

    def get_item_discrimination(self, item_id: str) -> Optional[float]:
        """查询题目区分度 a。"""
        if not self._fitted:
            return None
        if item_id in self._item_ids:
            return round(float(self._a[self._item_ids.index(item_id)]), 4)
        return None

    @property
    def is_fitted(self) -> bool:
        return self._fitted

    @property
    def ability_map(self) -> Dict[str, float]:
        """{student_id: θ}"""
        return {s: round(float(self._theta[i]), 4) for i, s in enumerate(self._student_ids)}

    @property
    def difficulty_map(self) -> Dict[str, float]:
        """{item_id: b}"""
        return {i: round(float(self._b[j]), 4) for j, i in enumerate(self._item_ids)}
