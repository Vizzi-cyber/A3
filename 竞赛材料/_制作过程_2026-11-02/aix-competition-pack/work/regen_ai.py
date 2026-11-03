# -*- coding: utf-8 -*-
"""只重出 AI 说明一份"""
import subprocess, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
base = r"e:\开发\learnlabAI教学平台\_制作过程_2026-11-02\aix-competition-pack\work"
py = r"e:\开发\learnlabAI教学平台\backend\venv\Scripts\python.exe"
md2 = r"e:\开发\learnlabAI教学平台\frontend\scripts\md2html.py"
md, html, pdf = base + r"\AI工具使用说明.md", base + r"\AI工具使用说明.html", base + r"\AI工具使用说明_f.pdf"
r = subprocess.run([py, md2, md, html], capture_output=True, text=True, encoding="utf-8", errors="replace")
assert "HTML_OK" in r.stdout, r.stdout + r.stderr
r = subprocess.run(["node", base + r"\print_pdf.cjs", html, pdf], capture_output=True, text=True, encoding="utf-8", errors="replace")
assert "PDF_OK" in r.stdout, r.stdout[-300:] + r.stderr[-300:]
print("OK", os.path.getsize(pdf))
import fitz
print("页数:", fitz.open(pdf).page_count)
