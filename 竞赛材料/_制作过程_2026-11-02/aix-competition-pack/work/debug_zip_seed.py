# -*- coding: utf-8 -*-
"""debug 终版 zip 种子：报错行 + mindmap 形式统计"""
import sys, re, zipfile, os, subprocess

sys.stdout.reconfigure(encoding="utf-8")
base = r"e:\开发\learnlabAI教学平台\2026-11-02\aix-competition-pack"
z = zipfile.ZipFile(os.path.join(base, r"work\LearnLab源代码_final.zip"))
s = z.read("backend/seed_data.py").decode("utf-8")

allm = re.findall(r"mindmap\s*=\s*([^\n]{0,50})", s)
print("zip seed mindmap 总数:", len(allm))
for m in allm:
    if "json.dumps" not in m:
        print("  未序列化:", repr(m[:60]))

chk = os.path.join(base, r"work\seed_final_check")
py = r"e:\开发\learnlabAI教学平台\backend\venv\Scripts\python.exe"
r = subprocess.run([py, "seed_data.py"], cwd=chk, capture_output=True, text=True,
                   encoding="utf-8", errors="replace", timeout=300)
err = (r.stderr or "").splitlines()
keep = [l for l in err if re.search(r"Error|error", l)][:3]
for l in keep:
    print(l[:200])
