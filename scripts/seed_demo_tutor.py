"""为演示学生补辅导问答记录，使「AI 协作榜」有数据。

背景：AI 协作榜按 tutor_qa_records 的交互次数统计，演示库仅 4 名学生
有记录，榜单数据单薄。本脚本按各生活跃度补问答记录。

幂等：同一 (student_id, session_id) 已有记录则跳过。

用法：
    python scripts/seed_demo_tutor.py
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

# 学生 → 本周问答次数（体现活跃度差异）
COHORT = {
    "student_001": 8, "student_002": 12, "student_003": 5,
    "student_004": 15, "student_005": 3, "student_006": 11,
    "student_007": 7,
}

# 示范问答（贴近真实使用场景）
QA_PAIRS = [
    ("指针和数组有什么区别？", "可以从内存布局的角度来想：数组名在多数场合会退化为首元素地址，但它本身不是变量，不能被赋值；指针是独立变量，存放的是地址，可以重新指向别处。你先说说，a[i] 和 *(a+i) 这两种写法你觉得等价吗？"),
    ("循环里的 break 和 continue 有什么不同？", "break 是直接跳出整个循环，continue 是跳过本轮剩下的语句、进入下一轮。想一个场景：遍历数组时遇到负数就跳过、遇到 0 就停止，这两种需求分别该用哪个？"),
    ("结构体和联合体的区别是什么？", "关键在内存：结构体各成员各占一块空间、大小相加（含对齐）；联合体所有成员共用同一块空间，大小取最大成员。所以联合体同一时刻只能存一个成员的值。想想什么时候该用联合体？"),
    ("为什么我的程序会段错误？", "段错误通常是访问了不属于自己的内存。最常见的三种：解引用了空指针、数组越界、访问已释放的内存。你把出错的代码贴出来，我们一起看是哪一类。"),
    ("递归一定要有终止条件吗？", "是的，否则会无限递归直到栈溢出。终止条件负责把问题规模缩到最小、直接给出答案；递归步骤负责把大问题拆小。你能说出求阶乘时，终止条件该写什么吗？"),
    ("GPIO 的推挽输出和开漏输出有什么不同？", "推挽输出能主动输出高电平和低电平，驱动能力强；开漏输出只能拉低，高电平需要外部上拉电阻，好处是能做电平转换和线与。I2C 总线为什么必须用开漏？"),
]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--db", type=Path, default=DEFAULT_DB)
    args = ap.parse_args()

    if not args.db.exists():
        print(f"[错误] 找不到数据库：{args.db}")
        return 1

    conn = sqlite3.connect(args.db)
    cur = conn.cursor()
    rng = random.Random(20261010)

    today = datetime.now()
    added = 0

    for sid, count in COHORT.items():
        session = f"sess_{sid}_recent"
        exists = cur.execute(
            "SELECT 1 FROM tutor_qa_records WHERE student_id=? AND session_id=? LIMIT 1",
            (sid, session),
        ).fetchone()
        if exists:
            continue

        for i in range(count):
            q, a = QA_PAIRS[i % len(QA_PAIRS)]
            ts = today - timedelta(days=rng.randint(0, 6), hours=rng.randint(0, 20))
            cur.execute(
                "INSERT INTO tutor_qa_records "
                "(student_id, session_id, question, answer, question_meta, "
                " profile_snapshot, response_type, blocked, created_at) "
                "VALUES (?,?,?,?,?,?,?,?,?)",
                (sid, session, q, a, json.dumps({"rag_active": True}),
                 json.dumps({"weak_areas": [], "cognitive_style": {"primary": "visual"}}),
                 "explanation", 0, ts.isoformat(sep=" ")),
            )
            added += 1

    conn.commit()
    conn.close()
    print(f"[OK] 新增 {added} 条辅导问答记录（{len(COHORT)} 名学生）")
    if added == 0:
        print("     （均已有记录，未做改动）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
