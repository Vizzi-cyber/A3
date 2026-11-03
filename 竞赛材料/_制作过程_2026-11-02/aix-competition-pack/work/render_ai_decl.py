# -*- coding: utf-8 -*-
"""渲染 AI工具使用说明.md → PDF（与 render.py 同一 CSS）"""
import subprocess, sys, pathlib, re
import markdown

sys.stdout.reconfigure(encoding="utf-8")
BASE = pathlib.Path(__file__).parent
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
css = (BASE / "小PDF" / "render.py").read_text(encoding="utf-8").split('CSS = """')[1].split('"""')[0]
md = (BASE / "AI工具使用说明.md").read_text(encoding="utf-8")
body = markdown.markdown(md, extensions=["tables", "fenced_code", "sane_lists"])
html = f"<!DOCTYPE html><html><head><meta charset='utf-8'><style>{css}</style></head><body>{body}</body></html>"
html_file = BASE / "AI工具使用说明.html"
html_file.write_text(html, encoding="utf-8")
pdf_file = BASE / "AI工具使用说明.pdf"
subprocess.run(
    [EDGE, "--headless", "--disable-gpu", "--no-pdf-header-footer",
     f"--print-to-pdf={pdf_file}", html_file.resolve().as_uri()],
    check=True, capture_output=True, timeout=120,
)
from pypdf import PdfReader
r = PdfReader(str(pdf_file))
t = re.sub(r"\s+", "", "".join(pg.extract_text() or "" for pg in r.pages))
print("AI工具使用说明.pdf", len(r.pages), "页",
      {k: t.count(k) for k in ["AIC", "AI+X", "星火", "DeepSeek", "智谱", "MiMo", "Seedream", "BM25"]})
