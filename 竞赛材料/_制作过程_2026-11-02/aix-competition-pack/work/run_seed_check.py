# -*- coding: utf-8 -*-
"""隔离环境实跑 seed_data.py，数知识点/讲义覆盖/课程/用户"""
import sys, subprocess, os

sys.stdout.reconfigure(encoding="utf-8")
dst = r"e:\开发\learnlabAI教学平台\2026-11-02\aix-competition-pack\work\kp_check"
py = r"e:\开发\learnlabAI教学平台\backend\venv\Scripts\python.exe"
r = subprocess.run([py, "seed_data.py"], cwd=dst, capture_output=True, text=True,
                   encoding="utf-8", errors="replace", timeout=300)
print("returncode:", r.returncode)
print((r.stdout or "")[-1500:])
print((r.stderr or "")[-1500:])

# 查库
import sqlite3
db = os.path.join(dst, "ai_learning_v2.db")
if os.path.exists(db):
    c = sqlite3.connect(db)
    for t in ("knowledge_points", "courses", "users", "student_profiles"):
        try:
            n = c.execute(f"select count(*) from {t}").fetchone()[0]
            print(t, "=", n)
        except Exception as e:
            print(t, "ERR", str(e)[:80])
    # 讲义覆盖：knowledge_points 与资源/讲义的关联
    try:
        cols = [x[1] for x in c.execute("pragma table_info(knowledge_points)")]
        print("kp列:", cols)
    except Exception as e:
        print("kp列 ERR", str(e)[:80])
    c.close()
else:
    print("DB 未生成")
