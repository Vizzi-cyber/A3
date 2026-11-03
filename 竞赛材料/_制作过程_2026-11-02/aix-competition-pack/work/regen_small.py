# -*- coding: utf-8 -*-
"""四份小 PDF 重出：md -> html -> 带页脚 PDF"""
import subprocess, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
base = r"e:\开发\learnlabAI教学平台\_制作过程_2026-11-02\aix-competition-pack\work"
py = r"e:\开发\learnlabAI教学平台\backend\venv\Scripts\python.exe"
md2 = r"e:\开发\learnlabAI教学平台\frontend\scripts\md2html.py"
jobs = [
    (base + r"\AI工具使用说明.md",   base + r"\AI工具使用说明.html",   base + r"\AI工具使用说明_f.pdf"),
    (base + r"\小PDF\09_功能说明_评审版.md", base + r"\小PDF\09_功能说明_评审版.html", base + r"\功能说明_f.pdf"),
    (base + r"\小PDF\10_功能验证清单.md",   base + r"\小PDF\10_功能验证清单.html",   base + r"\验证清单_f.pdf"),
    (base + r"\小PDF\08_源码评审运行说明.md", base + r"\小PDF\08_源码评审运行说明.html", base + r"\运行说明_f.pdf"),
]
for md, html, pdf in jobs:
    r = subprocess.run([py, md2, md, html], capture_output=True, text=True, encoding="utf-8", errors="replace")
    if "HTML_OK" not in (r.stdout or ""):
        print("MD2HTML_FAIL:", md, r.stdout, r.stderr); sys.exit(1)
    r = subprocess.run(["node", base + r"\print_pdf.cjs", html, pdf], capture_output=True, text=True, encoding="utf-8", errors="replace")
    if "PDF_OK" not in (r.stdout or ""):
        print("PRINT_FAIL:", md, r.stdout[-300:], r.stderr[-300:]); sys.exit(1)
    print("OK:", os.path.basename(pdf), os.path.getsize(pdf))
