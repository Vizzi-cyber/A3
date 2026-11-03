"""Leakage-resistant offline evaluation helpers for education algorithms."""

from __future__ import annotations

import math
from collections import defaultdict, deque
from typing import Any, Dict, Iterable, List, Tuple

import numpy as np
import pandas as pd
from scipy.stats import rankdata

from .bkt_engine import BKTEngine


def binary_metrics(y_true: Iterable[int], y_prob: Iterable[float]) -> Dict[str, float | None]:
    """Return calibration and ranking metrics without fitting on evaluation data."""
    y = np.asarray(list(y_true), dtype=np.int64)
    p = np.clip(np.asarray(list(y_prob), dtype=np.float64), 1e-7, 1 - 1e-7)
    if y.size == 0 or y.size != p.size:
        raise ValueError("y_true and y_prob must be non-empty and have equal length")

    positives = int(y.sum())
    negatives = int(y.size - positives)
    auc = None
    if positives and negatives:
        ranks = rankdata(p, method="average")
        auc = float((ranks[y == 1].sum() - positives * (positives + 1) / 2) / (positives * negatives))

    log_loss = -float(np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))
    brier = float(np.mean((p - y) ** 2))
    accuracy = float(np.mean((p >= 0.5) == y))
    return {
        "auc": None if auc is None else round(auc, 4),
        "log_loss": round(log_loss, 4),
        "brier_score": round(brier, 4),
        "accuracy": round(accuracy, 4),
    }


def bootstrap_auc_interval(
    y_true: Iterable[int],
    y_prob: Iterable[float],
    iterations: int = 1000,
    seed: int = 42,
) -> List[float] | None:
    """Estimate a deterministic percentile interval; skip one-class resamples."""
    y = np.asarray(list(y_true), dtype=np.int64)
    p = np.asarray(list(y_prob), dtype=np.float64)
    if y.size < 2 or len(np.unique(y)) < 2:
        return None
    rng = np.random.default_rng(seed)
    values: List[float] = []
    for _ in range(iterations):
        idx = rng.integers(0, y.size, y.size)
        if len(np.unique(y[idx])) < 2:
            continue
        auc = binary_metrics(y[idx], p[idx])["auc"]
        if auc is not None:
            values.append(float(auc))
    if not values:
        return None
    low, high = np.percentile(values, [2.5, 97.5])
    return [round(float(low), 4), round(float(high), 4)]


def chronological_student_split(
    frame: pd.DataFrame,
    test_fraction: float = 0.3,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Hold out the latest answers for every student with at least two answers."""
    if not 0 < test_fraction < 1:
        raise ValueError("test_fraction must be between 0 and 1")
    train_indices: List[int] = []
    test_indices: List[int] = []
    ordered = frame.sort_values(["student_id", "order_id"], kind="stable")
    for _, group in ordered.groupby("student_id", sort=False):
        if len(group) < 2:
            train_indices.extend(group.index.tolist())
            continue
        n_test = min(len(group) - 1, max(1, math.ceil(len(group) * test_fraction)))
        train_indices.extend(group.index[:-n_test].tolist())
        test_indices.extend(group.index[-n_test:].tolist())
    return frame.loc[train_indices].copy(), frame.loc[test_indices].copy()


def evaluate_bkt_time_holdout(
    quiz_results: List[Dict[str, Any]],
    test_fraction: float = 0.3,
    min_train_answers: int = 4,
) -> Dict[str, Any]:
    """Evaluate BKT and simple baselines on each student's future answers."""
    frame = BKTEngine.build_dataframe(quiz_results)
    if frame.empty:
        return {"status": "error", "message": "no valid answers"}

    train, test = chronological_student_split(frame, test_fraction)
    train_records = [
        {
            "student_id": row.student_id,
            "kp_id": row.skill_name,
            "answers": [{"correct": bool(row.correct)}],
            "created_at": f"{int(row.order_id):012d}",
        }
        for row in train.itertuples()
    ]
    engine = BKTEngine()
    fit_result = engine.fit(train_records, min_answers=min_train_answers)
    if fit_result.get("status") != "success":
        return {"status": "error", "message": fit_result.get("message", "BKT fit failed")}

    eligible = set(engine.skills)
    combined = frame[frame["skill_name"].isin(eligible)].sort_values("order_id", kind="stable").copy()
    test_indices = set(test[test["skill_name"].isin(eligible)].index.tolist())
    if not test_indices:
        return {"status": "error", "message": "no holdout answers for fitted skills"}

    predictions = engine.predict_dataframe(combined)
    bkt_by_index = {
        int(idx): float(prob)
        for idx, prob in predictions["correct_predictions"].items()
        if int(idx) in test_indices
    }

    global_rate = float(train["correct"].mean()) if not train.empty else 0.5
    skill_rates = train.groupby("skill_name")["correct"].mean().to_dict()
    histories: Dict[Tuple[str, str], deque[int]] = defaultdict(lambda: deque(maxlen=5))
    for row in train.sort_values("order_id", kind="stable").itertuples():
        histories[(str(row.student_id), str(row.skill_name))].append(int(row.correct))

    y_true: List[int] = []
    bkt_prob: List[float] = []
    majority_prob: List[float] = []
    recent_prob: List[float] = []
    for idx, row in test.sort_values("order_id", kind="stable").iterrows():
        if idx not in test_indices or idx not in bkt_by_index:
            continue
        key = (str(row["student_id"]), str(row["skill_name"]))
        history = histories[key]
        fallback = float(skill_rates.get(row["skill_name"], global_rate))
        y_true.append(int(row["correct"]))
        bkt_prob.append(bkt_by_index[idx])
        majority_prob.append(global_rate)
        recent_prob.append(float(np.mean(history)) if history else fallback)
        history.append(int(row["correct"]))

    model_metrics = {
        "bkt": binary_metrics(y_true, bkt_prob),
        "recent_5_correctness": binary_metrics(y_true, recent_prob),
        "train_majority_rate": binary_metrics(y_true, majority_prob),
    }
    for name, probabilities in (
        ("bkt", bkt_prob),
        ("recent_5_correctness", recent_prob),
        ("train_majority_rate", majority_prob),
    ):
        model_metrics[name]["auc_ci_95"] = bootstrap_auc_interval(y_true, probabilities)

    warnings: List[str] = []
    if len(y_true) < 100:
        warnings.append("holdout_below_100_answers")
    if model_metrics["bkt"]["log_loss"] >= model_metrics["train_majority_rate"]["log_loss"]:
        warnings.append("bkt_calibration_worse_than_majority_baseline")

    return {
        "status": "success",
        "method": "per_student_chronological_holdout",
        "test_fraction": test_fraction,
        "coverage": {
            "all_answers": int(len(frame)),
            "train_answers": int(len(train)),
            "all_test_answers": int(len(test)),
            "eligible_test_answers": int(len(y_true)),
            "students": int(frame["student_id"].nunique()),
            "fitted_skills": len(eligible),
            "positive_rate_test": round(float(np.mean(y_true)), 4),
        },
        "models": model_metrics,
        "warnings": warnings,
        "fit": {
            "train_auc": fit_result.get("auc"),
            "note": "train_auc is diagnostic only; use holdout metrics for claims",
        },
    }
