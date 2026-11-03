# -*- coding: utf-8 -*-
"""把 work/小PDF 下的三份 markdown 渲染成 PDF（Edge headless 打印）"""
import subprocess, sys, pathlib
import markdown

sys.stdout.reconfigure(encoding="utf-8")
BASE = pathlib.Path(__file__).parent
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

CSS = """
@page { size: A4; margin: 18mm 16mm; }
* { box-sizing: border-box; }
body { font-family: "Microsoft YaHei", "SimSun", sans-serif; font-size: 10.5pt;
       line-height: 1.65; color: #1a1a1a; margin: 0; }
h1 { font-size: 17pt; border-bottom: 2px solid #1256b8; padding-bottom: 6px; margin: 0 0 14px; }
h2 { font-size: 13.5pt; color: #1256b8; margin: 18px 0 8px; }
blockquote { margin: 10px 0; padding: 6px 12px; background: #f2f6fc;
             border-left: 3px solid #1256b8; color: #333; }
blockquote p { margin: 2px 0; }
table { border-collapse: collapse; width: 100%; margin: 10px 0; font-size: 9.5pt; }
th, td { border: 1px solid #b9c4d6; padding: 5px 8px; text-align: left; vertical-align: top; }
th { background: #e8eefb; }
code { font-family: Consolas, monospace; background: #f4f4f4; padding: 1px 4px;
       border-radius: 3px; font-size: 9pt; }
pre { background: #f4f4f4; padding: 8px 10px; border-radius: 4px; overflow-x: hidden; }
hr { border: none; border-top: 1px solid #ccc; margin: 14px 0; }
li { margin: 2px 0; }
"""

for md_file in sorted(BASE.glob("*.md")):
    html_body = markdown.markdown(
        md_file.read_text(encoding="utf-8"),
        extensions=["tables", "fenced_code", "sane_lists"],
    )
    html = f"<!DOCTYPE html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{html_body}</body></html>"
    html_file = md_file.with_suffix(".html")
    html_file.write_text(html, encoding="utf-8")
    pdf_file = md_file.with_suffix(".pdf")
    subprocess.run(
        [EDGE, "--headless", "--disable-gpu", "--no-pdf-header-footer",
         f"--print-to-pdf={pdf_file}", html_file.as_uri()],
        check=True, capture_output=True, timeout=120,
    )
    print("OK", pdf_file.name, pdf_file.stat().st_size, "bytes")
