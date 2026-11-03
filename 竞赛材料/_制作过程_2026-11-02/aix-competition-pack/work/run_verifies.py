# -*- coding: utf-8 -*-
"""隔离环境实跑 verify 脚本，核对文档断言数"""
import sys, subprocess, os, re

sys.stdout.reconfigure(encoding="utf-8")
dst = r"e:\开发\learnlabAI教学平台\2026-11-02\aix-competition-pack\work\kp_check"
py = r"e:\开发\learnlabAI教学平台\backend\venv\Scripts\python.exe"
scripts = ["verify_core_features.py", "verify_dataflow.py", "verify_agent_llm.py",
           "verify_ai_algorithms.py", "verify_all_routes.py"]
for sc in scripts:
    p = os.path.join(dst, "scripts", sc)
    if not os.path.exists(p):
        print(sc, "不存在"); continue
    try:
        r = subprocess.run([py, p], cwd=dst, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=420)
        out = (r.stdout or "") + (r.stderr or "")
        # 统计通过/总数
        pass_n = len(re.findall(r"✓|√|PASS|通过", out))
        fail_n = len(re.findall(r"✗|×|FAIL|失败", out))
        total = re.findall(r"[Tt]otal[^\n]{0,40}|共\s*\d+\s*项|\d+\s*/\s*(\d+)", out)
        print(f"== {sc}: rc={r.returncode} ✓{pass_n} ✗{fail_n}")
        tail = [l for l in out.splitlines() if l.strip()][-3:]
        for l in tail:
            print("   ", l.strip()[:120])
    except subprocess.TimeoutExpired:
        print(f"== {sc}: 超时(420s) 跳过")
