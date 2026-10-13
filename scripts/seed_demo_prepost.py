"""为演示账号补前测/后测配对答题记录，使"进步最快榜"有数据。

背景：进步榜按 quiz_results.assessment_phase 的 pre/post 配对差值计算
（见 gamification_challenge.py 的 improvement 维度），但演示库该字段全为
NULL，导致榜单为空。本脚本为若干演示账号补配对记录，并体现学习进步。

幂等：同一 (student_id, assessment_phase) 已有记录则跳过。

用法：
    python scripts/seed_demo_prepost.py
    python scripts/seed_demo_prepost.py --db <路径>
"""
from __future__ import annotations

import argparse
import json
import random
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB = ROOT / "backend" / "ai_learning_v2.db"

# 学生 → (前测正确率, 后测正确率)。后测普遍提升，体现平台价值。
COHORT = {
    "student_001": (0.40, 0.80),   # 张三：零基础起步，提升明显
    "student_002": (0.85, 0.95),   # 李四：基础好，小幅提升
    "student_003": (0.35, 0.70),   # 王五：提升较大
    "student_004": (0.90, 0.95),   # 陈学霸：已很强，天花板效应
    "student_005": (0.25, 0.65),   # 刘小白：零基础，提升最大
    "student_006": (0.75, 0.90),   # 孙竞赛：竞赛生，稳步提升
    "student_007": (0.55, 0.75),   # 周稳步：中等起点，稳步提升
}
QUESTIONS = 10  # 前后测各 10 题，便于体现差异


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--db", type=Path, default=DEFAULT_DB)
    args = ap.parse_args()

    if not args.db.exists():
        print(f"[错误] 找不到数据库：{args.db}")
        return 1

    conn = sqlite3.connect(args.db)
    cur = conn.cursor()
    rng = random.Random(20261008)

    # 用课程首个知识点承载前后测（代表综合能力测评）
    kp = cur.execute(
        "SELECT kp_id FROM knowledge_points ORDER BY kp_id LIMIT 1"
    ).fetchone()[0]

    added = 0
    pre_day = datetime.now() - timedelta(days=14)  # 前测：两周前
    post_day = datetime.now() - timedelta(days=1)  # 后测：昨天

    for sid, (pre_acc, post_acc) in COHORT.items():
        for phase, acc, day in (("pre", pre_acc, pre_day), ("post", post_acc, post_day)):
            exists = cur.execute(
                "SELECT 1 FROM quiz_results WHERE student_id=? AND assessment_phase=? LIMIT 1",
                (sid, phase),
            ).fetchone()
            if exists:
                continue

            correct = sum(1 for _ in range(QUESTIONS) if rng.random() < acc)
            score = round(correct / QUESTIONS * 100, 1)
            ts = datetime(day.year, day.month, day.day, rng.randint(10, 16), rng.randint(0, 59))
            qid = f"qz_{phase}_{sid}_{rng.randint(10000,99999)}"
            cur.execute(
                "INSERT INTO quiz_results "
                "(quiz_id, student_id, kp_id, total_questions, correct_count, score, "
                " weak_tags, time_spent, answers, created_at, assessment_phase) "
                "VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                (qid, sid, kp, QUESTIONS, correct, score, json.dumps([]),
                 rng.randint(600, 1800),
                 json.dumps([{"q_id": f"q_{i}", "correct": i < correct} for i in range(QUESTIONS)]),
                 ts.isoformat(sep=" "), phase),
            )
            added += 1

    conn.commit()
    conn.close()
    print(f"[OK] 新增 {added} 条前后测记录（{len(COHORT)} 名学生配对）")
    if added == 0:
        print("     （所有学生均已有配对记录，未做改动）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
