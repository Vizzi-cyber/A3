"""为演示账号补最近 7 天连续学习记录（供演示"连续打卡/本周时长"展示）。

背景：演示库 student_001 的记录日期不连续（6 月有 7 天，之后是孤立单天 10/02、
10/08），仪表盘的「连续打卡」算出来只有 1 天，演示时说服力不足。

本脚本在最近 7 天内补齐每日学习记录，使 streak_days = 7、本周时长有数。
幂等：同一天已有记录则跳过，重复执行不会叠加。

用法：
    python scripts/seed_demo_activity.py            # 本地库
    python scripts/seed_demo_activity.py --db <路径>
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

STUDENT = "student_001"
# 每日学习的知识点（按课程顺序推进，体现"在学"的过程）
KP_POOL = ["kp_c01", "kp_c02", "kp_c03", "kp_c04", "kp_c05", "kp_c06", "kp_c07"]
ACTIONS = [
    ("read", "阅读讲义", (300, 900)),
    ("watch", "观看讲解", (240, 600)),
    ("practice", "练习题", (300, 1200)),
    ("quiz", "小测", (180, 600)),
]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--db", type=Path, default=DEFAULT_DB)
    ap.add_argument("--days", type=int, default=7, help="补齐最近 N 天（含今天）")
    args = ap.parse_args()

    if not args.db.exists():
        print(f"[错误] 找不到数据库：{args.db}")
        return 1

    conn = sqlite3.connect(args.db)
    cur = conn.cursor()

    today = date.today()
    # 固定随机种子 → 同一脚本在任何机器上生成同样的数据（避免每次跑出不同结果）
    rng = random.Random(20261008)

    added_days, added_rows, added_min = 0, 0, 0
    for offset in range(args.days):
        day = today - timedelta(days=args.days - 1 - offset)
        day_str = day.isoformat()

        cur.execute(
            "SELECT COUNT(*) FROM learning_records WHERE student_id=? AND DATE(created_at)=?",
            (STUDENT, day_str),
        )
        if cur.fetchone()[0] > 0:
            continue  # 该日已有记录，跳过（幂等）

        # 当天学习 3-5 条记录，覆盖 2-3 个知识点
        n_records = rng.randint(3, 5)
        kps = rng.sample(KP_POOL, rng.randint(2, 3))
        base_hour = rng.randint(19, 21)  # 晚间学习

        for i in range(n_records):
            kp = kps[i % len(kps)]
            action, _label, (lo, hi) = rng.choice(ACTIONS)
            duration = rng.randint(lo, hi)
            # 每天至少一条"完成"记录（progress=1.0）：
            # 掌握度榜按 progress>=1.0 统计，缺了会让该生在各周期榜单上都为空
            if i == 0:
                action = "complete"
                progress = 1.0
            else:
                progress = round(rng.uniform(0.3, 0.99), 2)
            ts = datetime(day.year, day.month, day.day,
                          base_hour, rng.randint(0, 59), rng.randint(0, 59))
            rid = f"lr_demo_{day.strftime('%Y%m%d')}_{uuid.uuid4().hex[:8]}"
            cur.execute(
                "INSERT INTO learning_records "
                "(record_id, student_id, kp_id, action, duration, progress, score, meta, created_at) "
                "VALUES (?,?,?,?,?,?,?,?,?)",
                (rid, STUDENT, kp, action, duration,
                 progress, None, json.dumps({}),
                 ts.isoformat(sep=" ")),
            )
            added_rows += 1
            added_min += duration // 60

        added_days += 1

    conn.commit()
    conn.close()

    print(f"[OK] 补齐 {added_days} 天 / {added_rows} 条记录 / 约 {added_min} 分钟")
    if added_days == 0:
        print("      （最近 7 天均已有记录，未做改动）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
