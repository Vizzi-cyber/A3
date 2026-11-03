# -*- coding: utf-8 -*-
"""等后端起来后实跑剩余 verify 脚本"""
import sys, subprocess, os, re, time, urllib.request

sys.stdout.reconfigure(encoding="utf-8")
dst = r"e:\开发\learnlabAI教学平台\2026-11-02\aix-competition-pack\work\kp_check"
py = r"e:\开发\learnlabAI教学平台\backend\venv\Scripts\python.exe"

for i in range(30):
    try:
        urllib.request.urlopen("http://127.0.0.1:8000/docs", timeout=2)
        print("后端已就绪"); break
    except Exception:
        time.sleep(1)
else:
    print("后端 30s 未就绪")

# 从 zip 提取重命名后的 verify_core_features.py
import zipfile
zp = r"e:\开发\learnlabAI教学平台\2026-11-02\aix-competition-pack\outputs\马其瑞+202521047080+LearnLab跨学科智能学习平台\03-源代码\LearnLab源代码.zip"
z = zipfile.ZipFile(zp)
open(os.path.join(dst, "scripts", "verify_core_features.py"), "wb").write(z.read("backend/scripts/verify_core_features.py"))

for sc in ["verify_core_features.py", "verify_dataflow.py", "verify_all_routes.py", "verify_agent_llm.py"]:
    p = os.path.join(dst, "scripts", sc)
    try:
        r = subprocess.run([py, p], cwd=dst, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=420)
        out = (r.stdout or "")
        lines = [l for l in out.splitlines() if l.strip()]
        ok = sum(1 for l in lines if re.search(r"✓|√|PASS|通过|True", l))
        bad = sum(1 for l in lines if re.search(r"✗|×|FAIL|失败|False", l))
        summ = [l for l in lines if re.search(r"结果|总计|total|Total|项", l)][-2:]
        print(f"== {sc}: rc={r.returncode} ✓≈{ok} ✗≈{bad}")
        for l in summ:
            print("   ", l.strip()[:130])
        if r.returncode != 0 and not summ:
            print("   tail:", lines[-1][:130] if lines else "(空)")
    except subprocess.TimeoutExpired:
        print(f"== {sc}: 超时")
