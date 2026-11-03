# -*- coding: utf-8 -*-
"""AI+X 成品：用用户自己的管线（frontend/scripts/md2html.py + print_pdf.cjs）重出 4 份 md 类 PDF"""
import subprocess, sys, pathlib, re

sys.stdout.reconfigure(encoding="utf-8")
WORK = pathlib.Path(__file__).parent
MD2HTML = r"e:\开发\learnlabAI教学平台\frontend\scripts\md2html.py"
PY = r"e:\开发\learnlabAI教学平台\backend\.venv\Scripts\python.exe"

JOBS = [
    ("AI工具使用说明.md", "AI工具使用说明"),
    ("小PDF/08_源码评审运行说明.md", "运行说明"),
    ("小PDF/09_功能说明_评审版.md", "功能说明"),
    ("小PDF/10_功能验证清单.md", "功能验证清单"),
]
if not pathlib.Path(PY).exists():
    PY = sys.executable

for md_rel, name in JOBS:
    md = WORK / md_rel
    html = WORK / (name + "_his.html")
    pdf = WORK / (name + "_his.pdf")
    subprocess.run([PY, MD2HTML, str(md), str(html)], check=True)
    subprocess.run(["node", str(WORK / "print_pdf.cjs"), str(html), str(pdf)],
                   check=True, cwd=str(WORK))
    from pypdf import PdfReader
    r = PdfReader(str(pdf))
    t = re.sub(r"\s+", "", "".join(p.extract_text() or "" for p in r.pages))
    print(f"{name}_his.pdf: {len(r.pages)} 页, 残留:",
          {p: t.count(p) for p in ["AIC", "21740176", "AI+X"]})
