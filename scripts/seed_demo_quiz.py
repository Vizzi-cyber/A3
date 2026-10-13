"""为演示账号补知识点答题记录，使 BKT 掌握度可计算、薄弱点识别有意义。

背景：演示账号仅在 5 个知识点有答题记录，其余 30 个无观测数据，BKT 对无观测
知识点输出 0% 掌握度，"薄弱知识点"面板因此全是 0%。本脚本补齐各知识点的
答题记录，并刻意做出梯度：C 语言基础扎实、指针/字符串/文件偏弱、STM32 偏弱
—— 使薄弱点面板能呈现出真实的差异。

幂等：同一 (student_id, kp_id) 已有记录则跳过，重复执行不叠加。

用法：
    python scripts/seed_demo_quiz.py            # 本地库
    python scripts/seed_demo_quiz.py --db <路径>
"""
from __future__ import annotations

import argparse
import json
import random
import sqlite3
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB = ROOT / "backend" / "ai_learning_v2.db"
STUDENT = "student_001"

# 知识点 → 目标正确率（0-1）。数值体现学习画像：C 语言基础好、难点弱、STM32 生疏。
# 未列出的知识点按 0.65 处理。
TARGET = {
    # C 语言：基础扎实，难点薄弱
    "kp_c01": 0.95, "kp_c02": 0.90, "kp_c03": 0.88, "kp_c04": 0.85,
    "kp_c05": 0.82, "kp_c06": 0.70, "kp_c07": 0.62, "kp_c08": 0.35,
    "kp_c09": 0.60, "kp_c10": 0.30, "kp_c11": 0.28, "kp_c12": 0.45,
    "kp_c13": 0.32, "kp_c14": 0.50, "kp_c15": 0.66, "kp_c16": 0.55,
    # 电路分析：中等
    "kp_e01": 0.85, "kp_e02": 0.72, "kp_e03": 0.40, "kp_e04": 0.58,
    "kp_e05": 0.52,
    # STM32：整体生疏
    "kp_s01": 0.55, "kp_s02": 0.70, "kp_s03": 0.62, "kp_s04": 0.35,
    "kp_s05": 0.45, "kp_s06": 0.40, "kp_s07": 0.60, "kp_s08": 0.38,
    "kp_s09": 0.42, "kp_s10": 0.30, "kp_s11": 0.48, "kp_s12": 0.44,
    "kp_s13": 0.36, "kp_s14": 0.46,
}
QUESTIONS_PER_QUIZ = 5
QUIZ_ROUNDS = 6  # 每个知识点来 6 轮，BKT 需要足够样本才能估出 learns 参数


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--db", type=Path, default=DEFAULT_DB)
    ap.add_argument("--overwrite", action="store_true",
                    help="清空该生已有的示例答题记录后重建")
    args = ap.parse_args()

    if not args.db.exists():
        print(f"[错误] 找不到数据库：{args.db}")
        return 1

    conn = sqlite3.connect(args.db)
    cur = conn.cursor()
    rng = random.Random(20261008)

    kp_ids = [r[0] for r in cur.execute("SELECT kp_id FROM knowledge_points ORDER BY kp_id")]

    # 各知识点已有的演示记录数（用于把不足轮数的补齐，已有真实作答的不动）
    have: dict[str, int] = {}
    for kp, n in cur.execute(
        "SELECT kp_id, COUNT(*) FROM quiz_results WHERE student_id=? GROUP BY kp_id",
        (STUDENT,),
    ):
        have[kp] = n

    added, skipped = 0, 0
    # 从 30 天前开始，逐日铺开，形成自然的时间分布
    day = date.today() - timedelta(days=30)

    for kp in kp_ids:
        # 已有真实作答的知识点（如 kp_c01 有 30 条）保持不动
        if have.get(kp, 0) >= QUIZ_ROUNDS * 2:
            skipped += 1
            continue

        target = TARGET.get(kp, 0.65)
        for rnd in range(QUIZ_ROUNDS):
            # 第二轮略微提升（体现学习进步）
            acc = min(0.98, target + rnd * 0.04)
            correct = sum(1 for _ in range(QUESTIONS_PER_QUIZ) if rng.random() < acc)
            score = round(correct / QUESTIONS_PER_QUIZ * 100, 1)
            answers = [{"q_id": f"q_{i}", "correct": i < correct}
                       for i in range(QUESTIONS_PER_QUIZ)]
            ts = datetime(day.year, day.month, day.day, rng.randint(9, 21), rng.randint(0, 59))
            qid = f"qz_demo_{kp}_{rnd}_{rng.randint(1000,9999)}"
            cur.execute(
                "INSERT INTO quiz_results "
                "(quiz_id, student_id, kp_id, total_questions, correct_count, score, "
                " weak_tags, time_spent, answers, created_at) "
                "VALUES (?,?,?,?,?,?,?,?,?,?)",
                (qid, STUDENT, kp, QUESTIONS_PER_QUIZ, correct, score,
                 json.dumps([]), rng.randint(300, 1500), json.dumps(answers),
                 ts.isoformat(sep=" ")),
            )
            added += 1
            day += timedelta(days=1)

    conn.commit()
    conn.close()
    print(f"[OK] 新增 {added} 条答题记录（{len(kp_ids)-skipped} 个知识点 × {QUIZ_ROUNDS} 轮）")
    if skipped:
        print(f"     {skipped} 个知识点已有记录，已跳过")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
