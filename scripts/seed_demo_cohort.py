"""为全体演示学生补近期学习活动，使六维排行榜有真实竞争数据。

背景：演示库中仅 student_001 有本周活动，其余学生最后活跃在 6 月，
导致「连续学习榜 / 知识掌握榜 / AI 协作榜」等维度只有 1 人上榜。
本脚本按各生人设补近期记录，形成合理梯度（谁更活跃、谁更弱），
使排行榜呈现出真实的分布。

幂等：同一 (student_id, 某一天) 已有记录则跳过该天。

用法：
    python scripts/seed_demo_cohort.py
    python scripts/seed_demo_cohort.py --db <路径> --days 14
"""
from __future__ import annotations

import argparse
import json
import random
import sqlite3
import uuid
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB = ROOT / "backend" / "ai_learning_v2.db"

# 学生 → (连续学习天数, 每天记录数, 描述)
# 梯度设计：学霸/竞赛生最活跃，小白最少，体现真实差异
COHORT = {
    "student_001": (14, (3, 5)),   # 张三   —— 我补过 7 天，这里补齐到 14 天
    "student_002": (12, (4, 6)),   # 李四   —— 基础好，稳定
    "student_003": (10, (3, 5)),   # 王五
    "student_004": (14, (5, 7)),   # 陈学霸 —— 最活跃
    "student_005": (6, (2, 4)),    # 刘小白 —— 零基础，断续
    "student_006": (13, (4, 6)),   # 孙竞赛 —— 竞赛生
    "student_007": (11, (3, 5)),   # 周稳步
}
KP_POOL = ["kp_c01", "kp_c02", "kp_c03", "kp_c04", "kp_c05", "kp_c06", "kp_c07", "kp_c08"]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--db", type=Path, default=DEFAULT_DB)
    args = ap.parse_args()

    if not args.db.exists():
        print(f"[错误] 找不到数据库：{args.db}")
        return 1

    conn = sqlite3.connect(args.db)
    cur = conn.cursor()
    rng = random.Random(20261009)

    today = date.today()
    added_days, added_rows = 0, 0

    for sid, (streak, (lo, hi)) in COHORT.items():
        for offset in range(streak):
            day = today - timedelta(days=offset)
            day_str = day.isoformat()

            exists = cur.execute(
                "SELECT 1 FROM learning_records WHERE student_id=? AND DATE(created_at)=? LIMIT 1",
                (sid, day_str),
            ).fetchone()
            if exists:
                continue

            n = rng.randint(lo, hi)
            kps = rng.sample(KP_POOL, min(len(KP_POOL), rng.randint(2, 4)))
            hour = rng.randint(8, 22)

            for i in range(n):
                kp = kps[i % len(kps)]
                # 每天首条为"完成"，满足掌握度榜的 progress>=1.0 统计口径
                if i == 0:
                    action, progress = "complete", 1.0
                else:
                    action = rng.choice(["read", "watch", "practice", "quiz"])
                    progress = round(rng.uniform(0.3, 0.99), 2)
                duration = rng.randint(180, 1200)
                ts = datetime(day.year, day.month, day.day, hour,
                              rng.randint(0, 59), rng.randint(0, 59))
                cur.execute(
                    "INSERT INTO learning_records "
                    "(record_id, student_id, kp_id, action, duration, progress, score, meta, created_at) "
                    "VALUES (?,?,?,?,?,?,?,?,?)",
                    (f"lr_cohort_{uuid.uuid4().hex[:12]}", sid, kp, action,
                     duration, progress, None, json.dumps({}), ts.isoformat(sep=" ")),
                )
                added_rows += 1
            added_days += 1

    conn.commit()
    conn.close()
    print(f"[OK] 新增 {added_days} 人日 / {added_rows} 条学习记录")
    if added_days == 0:
        print("     （全部学生近期均已有记录，未做改动）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
