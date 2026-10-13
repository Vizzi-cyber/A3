"""Markdown → PDF（A4，中文字体，支持表格/删除线/加粗）。

用法：
    python scripts/md_to_pdf.py <输入.md> <输出.pdf> [标题]

用 markdown 库转 HTML，再交给 Playwright(Chrome) 打印，避免临时管线把
`~~删除线~~`、表格等语法原样漏出。
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

CSS = """
@page { size: A4; margin: 22mm 20mm; }
body { font-family: "Microsoft YaHei", "SimSun", sans-serif; font-size: 10.5pt;
       line-height: 1.7; color: #1a1a1a; }
h1 { font-size: 17pt; border-bottom: 1.5pt solid #1256b8; padding-bottom: 6pt;
     margin: 0 0 14pt; color: #1256b8; }
h2 { font-size: 13pt; margin: 16pt 0 8pt; color: #1e3a5f;
     border-left: 4pt solid #1256b8; padding-left: 8pt; }
h3 { font-size: 11.5pt; margin: 12pt 0 6pt; color: #1e3a5f; }
table { border-collapse: collapse; width: 100%; margin: 8pt 0; font-size: 9.5pt; }
th, td { border: 0.8pt solid #b8c4d4; padding: 5pt 7pt; text-align: left;
         vertical-align: top; }
th { background: #eef4fc; font-weight: bold; }
code { font-family: Consolas, monospace; background: #f4f6f8;
       padding: 1pt 3pt; border-radius: 2pt; font-size: 9pt; }
pre { background: #f6f8fa; border: 0.8pt solid #d8dee6; border-radius: 4pt;
      padding: 8pt; overflow-x: auto; font-size: 9pt; }
pre code { background: none; padding: 0; }
ul { margin: 6pt 0; padding-left: 20pt; }
li { margin: 3pt 0; }
del { color: #8a94a6; }
strong { color: #0b2b52; }
hr { border: none; border-top: 0.8pt solid #d8dee6; margin: 14pt 0; }
blockquote { margin: 8pt 0; padding: 6pt 12pt; border-left: 3pt solid #b8c4d4;
             background: #f8fafc; color: #4a5568; }
"""


def main() -> int:
    if len(sys.argv) < 3:
        print("用法: python scripts/md_to_pdf.py <输入.md> <输出.pdf> [标题]", file=sys.stderr)
        return 1
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    title = sys.argv[3] if len(sys.argv) > 3 else src.stem
    if not src.exists():
        print(f"[错误] 找不到 {src}", file=sys.stderr)
        return 1

    try:
        import markdown
    except ImportError:
        print("[错误] 需要 markdown 库：pip install markdown", file=sys.stderr)
        return 1

    text = src.read_text(encoding="utf-8")
    # 标准 markdown 库不带 GFM 删除线，这里把 ~~x~~ 转成 <del>
    text = re.sub(r"~~([^~\n]+)~~", r"<del>\1</del>", text)
    body = markdown.markdown(
        text,
        extensions=["tables", "fenced_code", "sane_lists"],
    )
    html = (f"<!DOCTYPE html><html lang='zh-CN'><head><meta charset='utf-8'>"
            f"<title>{title}</title><style>{CSS}</style></head><body>{body}</body></html>")

    tmp_html = dst.with_suffix(".tmp.html")
    tmp_html.write_text(html, encoding="utf-8")

    printer = ROOT / "scripts" / "_print_pdf.cjs"
    printer.write_text(
        'const { chromium } = require("playwright");\n'
        '(async () => {\n'
        '  const b = await chromium.launch({ channel: "chrome" });\n'
        '  const p = await b.newPage();\n'
        '  await p.goto("file:///" + process.argv[2].replace(/\\\\/g, "/"), { waitUntil: "load" });\n'
        '  await p.pdf({ path: process.argv[3], format: "A4", printBackground: true,\n'
        '    displayHeaderFooter: true,\n'
        '    headerTemplate: \'<div style="font-size:8pt;font-family:SimHei,serif;width:100%;padding:0 20mm;display:flex;justify-content:space-between;border-bottom:0.5pt solid #999;"><span style="color:#1e5bb8;font-weight:bold;font-style:italic;font-size:12pt;">AIC</span><span style="color:#555;">2026 第八届全球校园人工智能算法精英大赛</span></div>\',\n'
        '    footerTemplate: \'<div style="font-size:9pt;font-family:SimSun,serif;width:100%;text-align:center;"><span class="pageNumber"></span></div>\',\n'
        '    margin: { top: "22mm", bottom: "18mm", left: "20mm", right: "20mm" } });\n'
        '  await b.close();\n'
        '})().catch(e => { console.error("FATAL:", String(e).slice(0,300)); process.exit(1); });\n',
        encoding="utf-8",
    )

    r = subprocess.run(
        ["node", str(printer), str(tmp_html.resolve()), str(dst.resolve())],
        cwd=str(ROOT / "frontend"), capture_output=True, text=True, encoding="utf-8",
    )
    tmp_html.unlink(missing_ok=True)
    printer.unlink(missing_ok=True)
    if r.returncode != 0:
        print(f"[错误] 打印失败：{r.stderr or r.stdout}", file=sys.stderr)
        return 1
    print(f"[OK] 已生成 {dst}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
