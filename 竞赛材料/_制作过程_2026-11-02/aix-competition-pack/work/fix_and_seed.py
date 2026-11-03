# -*- coding: utf-8 -*-
"""修 kp_check 副本的 seed：mindmap json.dumps；实跑并统计"""
import sys, re, os, subprocess, sqlite3

sys.stdout.reconfigure(encoding="utf-8")
dst = r"e:\开发\learnlabAI教学平台\2026-11-02\aix-competition-pack\work\kp_check"
p = os.path.join(dst, "seed_data.py")
s = open(p, encoding="utf-8").read()

if "import json" not in s[:800]:
    s = s.replace("from datetime import datetime, timedelta",
                  "import json\nfrom datetime import datetime, timedelta", 1)
n = len(re.findall(r"mindmap=(KP_\w+),", s))
s = re.sub(r"mindmap=(KP_\w+),", r"mindmap=json.dumps(\1, ensure_ascii=False),", s)
# 内联 dict 形式：mindmap={...},  （单行）
n2 = len(re.findall(r"mindmap=(\{[^\n]+\})(,)\n", s))
s = re.sub(r"mindmap=(\{[^\n]+\})(,)\n", r"mindmap=json.dumps(\1, ensure_ascii=False)\2\n", s)
open(p, "w", encoding="utf-8").write(s)
print("patched mindmap 变量:", n, " 内联dict:", n2)

db = os.path.join(dst, "ai_learning_v2.db")
if os.path.exists(db):
    os.remove(db)

py = r"e:\开发\learnlabAI教学平台\backend\venv\Scripts\python.exe"
r = subprocess.run([py, "seed_data.py"], cwd=dst, capture_output=True, text=True,
                   encoding="utf-8", errors="replace", timeout=300)
print("seed returncode:", r.returncode)
if r.returncode != 0:
    print((r.stderr or "")[-800:])
else:
    c = sqlite3.connect(db)
    kps = c.execute("select count(*), sum(case when document is not null and length(document)>10 then 1 else 0 end) from knowledge_points").fetchone()
    print("knowledge_points 总数/有讲义:", kps)
    print("courses:", c.execute("select distinct course from knowledge_points").fetchall())
    print("users:", c.execute("select count(*) from users").fetchone()[0])
    c.close()
