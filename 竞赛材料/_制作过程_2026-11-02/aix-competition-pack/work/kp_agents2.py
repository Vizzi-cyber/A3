# -*- coding: utf-8 -*-
"""知识点分课程计数 + playwright.config 排除规则 + 智能体清单确认"""
import sys, re

sys.stdout.reconfigure(encoding="utf-8")
s = open(r"e:\开发\learnlabAI教学平台\backend\seed_data.py", encoding="utf-8").read()
lines = s.splitlines()

# 三个课程段落边界
marks = []
for i, l in enumerate(lines):
    if "知识点（DAG）—— C语言" in l: marks.append(("C语言", i))
    if "电路分析课程" in l and "知识点" not in l: pass
    if "电路分析课程" in l: marks.append(("电路分析", i))
    if "STM32嵌入式开发" in l: marks.append(("STM32", i))
print("段落标记:", [(m[0], m[1] + 1) for m in marks])

kp_idx = [i for i, l in enumerate(lines) if "KnowledgePointModel(" in l and not l.strip().startswith("#")]
bounds = sorted(marks, key=lambda m: m[1])
from collections import Counter
cnt = Counter()
for i in kp_idx:
    sec = None
    for name, start in bounds:
        if i > start:
            sec = name
    cnt[sec] += 1
print("分课程知识点:", dict(cnt), "总计:", sum(cnt.values()))

# playwright.config 排除规则
cfg = open(r"e:\开发\learnlabAI教学平台\frontend\playwright.config.ts", encoding="utf-8").read()
for i, l in enumerate(cfg.splitlines(), 1):
    if re.search(r"testIgnore|testMatch|grep|projects|_shot|image-gen|_page", l):
        print("cfg", i, l.strip()[:100])

# 智能体文件清单
import glob, os
ags = sorted(os.path.basename(f) for f in glob.glob(r"e:\开发\learnlabAI教学平台\backend\app\agents\*.py"))
print("agents 目录:", ags, "除 base 外:", len(ags) - 1)
