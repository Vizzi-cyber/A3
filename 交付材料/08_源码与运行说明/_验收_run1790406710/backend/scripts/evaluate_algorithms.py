"""Generate reproducible holdout metrics for the competition report."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.algorithms.offline_evaluation import evaluate_bkt_time_holdout
from app.models.database import SessionLocal
from app.models.knowledge import QuizResultModel


def load_quiz_results() -> list[dict]:
    db = SessionLocal()
    try:
        rows = db.query(QuizResultModel).order_by(QuizResultModel.created_at, QuizResultModel.quiz_id).all()
        return [
            {
                "student_id": row.student_id,
                "kp_id": row.kp_id,
                "answers": row.answers or [],
                "score": row.score,
                "created_at": row.created_at.isoformat() if row.created_at else "",
            }
            for row in rows
        ]
    finally:
        db.close()


def markdown_report(report: dict) -> str:
    if report.get("status") != "success":
        return f"# Algorithm Evaluation\n\nEvaluation failed: {report.get('message', 'unknown error')}\n"
    coverage = report["coverage"]
    lines = [
        "# 算法离线评估",
        "",
        "## 方法",
        "",
        "按学生时间顺序留出最近作答；模型参数仅使用更早作答拟合。",
        "",
        "## 数据覆盖",
        "",
        f"- 作答：共 {coverage['all_answers']}，训练 {coverage['train_answers']}，留出集 {coverage['all_test_answers']} 中有 {coverage['eligible_test_answers']} 条可评估",
        f"- 学生：{coverage['students']}",
        f"- 已拟合知识点：{coverage['fitted_skills']}",
        f"- 留出集答对率：{coverage['positive_rate_test']:.4f}",
        "",
        "## 结果",
        "",
        "| 模型 | AUC（95% bootstrap CI） | LogLoss | Brier | 准确率 |",
        "|---|---:|---:|---:|---:|",
    ]
    for name, metrics in report["models"].items():
        if metrics["auc"] is None:
            auc = "N/A"
        else:
            interval = metrics.get("auc_ci_95")
            auc = f"{metrics['auc']:.4f}"
            if interval:
                auc += f" ({interval[0]:.4f}-{interval[1]:.4f})"
        lines.append(
            f"| {name} | {auc} | {metrics['log_loss']:.4f} | "
            f"{metrics['brier_score']:.4f} | {metrics['accuracy']:.4f} |"
        )
    warning_labels = {
        "holdout_below_100_answers": "留出作答少于 100，区间较宽，结论仅作初步证据。",
        "bkt_calibration_worse_than_majority_baseline": "BKT LogLoss 差于多数类基线，需继续做概率校准。",
    }
    lines.extend([
        "",
        "## 风险提示",
        "",
        *(f"- {warning_labels.get(warning, warning)}" for warning in report.get("warnings", [])),
        "",
        "> 训练集 AUC 只用于拟合诊断，不得作为泛化效果对外表述。",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "reports")
    parser.add_argument("--test-fraction", type=float, default=0.3)
    args = parser.parse_args()

    report = evaluate_bkt_time_holdout(load_quiz_results(), args.test_fraction)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "algorithm_evaluation.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (args.output_dir / "algorithm_evaluation.md").write_text(markdown_report(report), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report.get("status") == "success" else 1


if __name__ == "__main__":
    raise SystemExit(main())
