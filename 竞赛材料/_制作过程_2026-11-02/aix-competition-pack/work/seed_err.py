# -*- coding: utf-8 -*-
"""重跑种子，只取异常首行定位原因"""
import sys, subprocess, os, re

sys.stdout.reconfigure(encoding="utf-8")
dst = r"e:\开发\learnlabAI教学平台\2026-11-02\aix-competition-pack\work\kp_check"
py = r"e:\开发\learnlabAI教学平台\backend\venv\Scripts\python.exe"
r = subprocess.run([py, "seed_data.py"], cwd=dst, capture_output=True, text=True,
                   encoding="utf-8", errors="replace", timeout=300)
err = r.stderr or ""
lines = [l for l in err.splitlines() if l.strip()]
keep = [l for l in lines if re.search(r"Error|error|constraint|NOT NULL|UNIQUE|f4|e20", l)][:6]
for l in keep:
    print(l[:220])
