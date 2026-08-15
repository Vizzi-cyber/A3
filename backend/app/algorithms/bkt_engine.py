"""
完整贝叶斯知识追踪引擎（Full BKT Engine）

基于 pyBKT（Badrinath, Wang & Pardos, EDM 2021）的完整贝叶斯知识追踪：
对每个知识点独立拟合隐马尔可夫模型，EM 算法估计 4 类参数：
  - prior   : 先验掌握概率 P(L0)
  - learns  : 学习率 P(T)（未掌握 -> 掌握 的转移概率）
  - guesses : 猜测率 P(G)（未掌握但答对）
  - slips   : 失误率 P(S)（已掌握但答错）
  - forgets : 遗忘率（可选变体）

替代原 path_planning_dag.py 中的"简化 BKT"（概率合并公式 1-Π(1-pᵢ)，
无参数估计）。本引擎输出带参数估计的掌握度概率，可计算 AUC 验证预测质量。

参考文献：
- Corbett & Anderson (1995). Knowledge Tracing: Modeling the Acquisition of
  Procedural Knowledge. UMUAI.
- Badrinath, Wang & Pardos (2021). pyBKT: An Accessible Python Library of
  Bayesian Knowledge Tracing Models. EDM 2021.
"""
import importlib.util
import sys
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# pyBKT 1.4.3 与 numpy 2.x / sklearn 1.9+ 的兼容补丁（源码级、幂等）
# 1) pyBKT.util.metrics.fetch_supported_metrics 只捕获 TypeError，而 sklearn 新版
#    的 log_loss 等函数抛 AttributeError/ValueError，导致 import 时崩溃；
# 2) pyBKT.fit.EM_fit 中 log_likelihoods 赋值在 numpy 2.x 下形状不兼容。
# ---------------------------------------------------------------------------


def _patch_pybkt_compat() -> None:
    """对 pyBKT 打源码级兼容补丁（不动第三方文件，进程内生效，幂等）。"""
    if getattr(sys, "_LEARNLAB_PYBKT_PATCHED", False):
        return

    patches = []

    # 补丁 1：metrics 模块捕获所有异常（而非仅 TypeError）
    spec = importlib.util.find_spec("pyBKT.util.metrics")
    if spec is not None:
        src = spec.loader.get_source("pyBKT.util.metrics")
        patched = src.replace("except TypeError:", "except Exception:")
        if patched != src:
            patches.append(("pyBKT.util.metrics", spec, patched))

    # 补丁 2：EM_fit 的 log-likelihood 标量赋值（numpy 2.x 形状兼容）
    spec = importlib.util.find_spec("pyBKT.fit.EM_fit")
    if spec is not None:
        src = spec.loader.get_source("pyBKT.fit.EM_fit")
        old = "log_likelihoods[i][0] = result['total_loglike']"
        new = "log_likelihoods[i][0] = float(np.asarray(result['total_loglike']).reshape(-1)[0])"
        if old in src and new not in src:
            patches.append(("pyBKT.fit.EM_fit", spec, src.replace(old, new)))

    for mod_name, spec, patched_src in patches:
        module = importlib.util.module_from_spec(spec)
        exec(compile(patched_src, spec.origin, "exec"), module.__dict__)
        sys.modules[mod_name] = module

    sys._LEARNLAB_PYBKT_PATCHED = True  # type: ignore[attr-defined]


_patch_pybkt_compat()

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from pyBKT.models import Model, Roster  # noqa: E402


class BKTEngine:
    """完整贝叶斯知识追踪引擎（pyBKT 封装）。"""

    # pyBKT 期望的 DataFrame 列名映射
    DEFAULTS = {
        "order_id": "order_id",
        "user_id": "student_id",
        "skill_name": "skill_name",
        "correct": "correct",
    }

    def __init__(self, seed: int = 42, num_fits: int = 1, parallel: bool = False) -> None:
        # Windows 下 multiprocessing spawn 易失败且会显著拖慢拟合，默认禁用并行
        self._model = Model(seed=seed, num_fits=num_fits, parallel=parallel)
        self._fitted: bool = False
        self._skills: List[str] = []
        self._train_df: Optional[pd.DataFrame] = None
        self._fit_info: Dict[str, Any] = {}

    # ------------------------------------------------------------------ 数据
    @staticmethod
    def build_dataframe(quiz_results: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        将 quiz_results（含逐题作答）展开为 pyBKT 的训练序列。

        输入元素：{
            "student_id": str, "kp_id": str,
            "answers": [{"correct": bool}, ...],   # 逐题作答（优先）
            "score": float,                        # 无逐题时退化为整卷一次作答
            "created_at": str,
        }
        输出 DataFrame 列：order_id / student_id / skill_name / correct
        """
        rows: List[Dict[str, Any]] = []
        order = 0
        for q in sorted(quiz_results, key=lambda x: str(x.get("created_at") or "")):
            student_id = str(q.get("student_id", ""))
            kp_id = str(q.get("kp_id", ""))
            if not student_id or not kp_id:
                continue
            answers = q.get("answers") or []
            if answers:
                for a in answers:
                    rows.append({
                        "order_id": order,
                        "student_id": student_id,
                        "skill_name": kp_id,
                        "correct": int(bool(a.get("correct", False))),
                    })
                    order += 1
            else:
                # 无逐题数据：以整卷得分 >= 60 视为一次正确作答
                correct = 1 if (q.get("score") or 0) >= 60 else 0
                rows.append({
                    "order_id": order,
                    "student_id": student_id,
                    "skill_name": kp_id,
                    "correct": correct,
                })
                order += 1
        return pd.DataFrame(rows, columns=["order_id", "student_id", "skill_name", "correct"])

    # ------------------------------------------------------------------ 拟合
    def fit(self, quiz_results: List[Dict[str, Any]], min_answers: int = 4) -> Dict[str, Any]:
        """
        拟合完整 BKT 模型（EM 参数估计）。

        :param quiz_results: 作答记录（见 build_dataframe）
        :param min_answers:  每个知识点最少作答数，不足则跳过该知识点
        :return: {"status", "skills", "params", "auc", "total_answers", "skipped"}
        """
        df = self.build_dataframe(quiz_results)
        if df.empty or len(df) < min_answers:
            return {"status": "error", "message": "作答数据不足，无法拟合 BKT 模型"}

        # 按知识点统计，过滤作答数不足的知识点
        counts = df.groupby("skill_name").size()
        skills = [s for s in counts.index if counts[s] >= min_answers]
        skipped = [s for s in counts.index if counts[s] < min_answers]

        fit_df = df[df["skill_name"].isin(skills)].copy()
        if fit_df.empty:
            return {"status": "error", "message": "没有作答数达标的知识点"}

        self._model.fit(data=fit_df, defaults=self.DEFAULTS)
        self._fitted = True
        self._skills = skills
        self._train_df = fit_df
        self._fit_info = {
            "total_answers": int(len(fit_df)),
            "students": int(fit_df["student_id"].nunique()),
            "skills": skills,
            "skipped": skipped,
        }
        return {
            "status": "success",
            "skills": skills,
            "params": self.get_params(),
            "auc": self.evaluate_auc(),
            "total_answers": int(len(fit_df)),
            "skipped": skipped,
        }

    # ------------------------------------------------------------------ 评估
    def evaluate_auc(self) -> Optional[float]:
        """预测 AUC（对比简化 BKT / 随机基线用）。"""
        if not self._fitted or self._train_df is None:
            return None
        try:
            return round(float(self._model.evaluate(data=self._train_df, metric="auc")), 4)
        except Exception:
            return None

    def get_params(self) -> Dict[str, Dict[str, float]]:
        """输出每个知识点的 BKT 参数（prior/learns/guesses/slips/forgets）。"""
        if not self._fitted:
            return {}
        raw = self._model.params()  # pyBKT 1.4.3 返回 MultiIndex DataFrame
        result: Dict[str, Dict[str, float]] = {}
        try:
            for (skill, param, _cls), row in raw.iterrows():
                result.setdefault(str(skill), {})[str(param)] = round(float(row["value"]), 4)
        except Exception:
            return {}
        return result

    # ------------------------------------------------------------------ 预测
    def predict_mastery(
        self,
        student_id: str,
        kp_id: str,
        sequence: Optional[List[int]] = None,
    ) -> Optional[float]:
        """
        预测学生对某知识点的当前掌握概率 P(mastery)。

        使用 pyBKT Roster 重放该生作答序列做前向传播：
        - sequence 提供时按其重放；
        - 否则取训练数据中该生该知识点的历史作答（按时间序）。
        无作答历史时返回先验掌握概率；未拟合时返回 None（调用方降级）。
        """
        if not self._fitted:
            return None
        try:
            roster = Roster(students=[student_id], skills=[kp_id], model=self._model)
            if sequence is None and self._train_df is not None:
                hist = self._train_df[
                    (self._train_df["student_id"] == student_id)
                    & (self._train_df["skill_name"] == kp_id)
                ].sort_values("order_id")
                sequence = [int(c) for c in hist["correct"].tolist()]
            for c in (sequence or []):
                roster.update_state(kp_id, student_id, correct=int(c))
            prob = float(roster.get_mastery_prob(kp_id, student_id))
            return round(min(1.0, max(0.0, prob)), 4)
        except Exception:
            return None

    def estimate_mastery_map(self, student_id: str, kp_ids: List[str]) -> Dict[str, float]:
        """
        批量预测掌握度映射 {kp_id: mastery}，供 ADPP 路径规划等模块使用。
        预测失败的知识点回退为 0（表示未知，交给学习成本模型处理）。
        """
        result: Dict[str, float] = {}
        for kp in kp_ids:
            p = self.predict_mastery(student_id, kp)
            result[kp] = p if p is not None else 0.0
        return result

    @property
    def is_fitted(self) -> bool:
        return self._fitted

    @property
    def skills(self) -> List[str]:
        return list(self._skills)

    @property
    def fit_info(self) -> Dict[str, Any]:
        return dict(self._fit_info)
