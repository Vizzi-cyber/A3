# -*- coding: utf-8 -*-
"""成品终检：页数 + AIC/占位残留"""
import sys, re, glob, os

sys.stdout.reconfigure(encoding="utf-8")
import fitz

base = r"e:\开发\learnlabAI教学平台\2026-11-02\aix-competition-pack\outputs\马其瑞+202521047080+LearnLab跨学科智能学习平台"
pats = re.compile(r"AIC(?=[\u4e00-\u9fff\s：（\"'])|学号待补")

for f in sorted(glob.glob(base + r"\**\*.pdf", recursive=True)):
    doc = fitz.open(f)
    hits = sum(1 for p in doc for m in [p.get_text("text")] if pats.search(m))
    print(f"{os.path.basename(f):24s} {doc.page_count:>3d} 页  残留: {hits}")
    doc.close()
