# -*- coding: utf-8 -*-
"""从终版 zip 重建隔离环境：解包 backend → seed → 起服务就绪检查"""
import sys, zipfile, os, shutil, subprocess, time, urllib.request

sys.stdout.reconfigure(encoding="utf-8")
base = r"e:\开发\learnlabAI教学平台\2026-11-02\aix-competition-pack"
dst = os.path.join(base, r"work\kp_check2")
if os.path.exists(dst):
    shutil.rmtree(dst)
z = zipfile.ZipFile(os.path.join(base, r"work\LearnLab源代码_final.zip"))
for n in z.namelist():
    if n.startswith("backend/"):
        rel = n[len("backend/"):]
        if not rel:
            continue
        target = os.path.join(dst, rel.replace("/", os.sep))
        if n.endswith("/"):
            os.makedirs(target, exist_ok=True)
        else:
            os.makedirs(os.path.dirname(target), exist_ok=True)
            open(target, "wb").write(z.read(n))
print("解包完成", len(z.namelist()), "条目")

open(os.path.join(dst, ".env"), "w").write("DEBUG=true\nDATABASE_URL=sqlite:///./ai_learning_v2.db\n")
py = r"e:\开发\learnlabAI教学平台\backend\venv\Scripts\python.exe"
r = subprocess.run([py, "seed_data.py"], cwd=dst, capture_output=True, text=True,
                   encoding="utf-8", errors="replace", timeout=300)
print("seed rc:", r.returncode)
