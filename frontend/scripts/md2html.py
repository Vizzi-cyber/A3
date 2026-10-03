# -*- coding: utf-8 -*-
"""Markdown → 带样式 HTML（交付 PDF 转排用：黑框表格+粗表头，朴素学术风）
用法: backend venv python frontend/scripts/md2html.py <输入.md> <输出.html>
"""
import markdown
import os
import sys

src = sys.argv[1] if len(sys.argv) > 1 else None
out = sys.argv[2] if len(sys.argv) > 2 else None
if not src or not out:
    print("用法: md2html.py <输入.md> <输出.html>")
    sys.exit(1)

md = open(src, encoding="utf-8").read()
body = markdown.markdown(md, extensions=["tables", "fenced_code", "sane_lists"])
html = """<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><style>

body { font-family: "SimSun","Songti SC",serif; font-size: 11.5pt; line-height: 2.0; color:#000; margin: 0; padding: 0; line-break: strict; }
h1 { font-family: "SimHei","Heiti SC",sans-serif; font-size: 20pt; text-align: center; margin: 10mm 0 8mm; }
h2 { font-family: "SimHei","Heiti SC",sans-serif; font-size: 15pt; margin: 10mm 0 4.5mm; border-bottom: 1.5pt solid #000; padding-bottom: 2.5mm; page-break-after: avoid; }
h3 { font-family: "SimHei","Heiti SC",sans-serif; font-size: 13pt; margin: 7mm 0 3.5mm; page-break-after: avoid; }
h4 { font-family: "SimHei","Heiti SC",sans-serif; font-size: 12pt; margin: 5.5mm 0 2.5mm; page-break-after: avoid; }
p { margin: 0 0 3mm; text-align: justify; }
table { width: 100%; border-collapse: collapse; font-size: 10pt; margin: 4.5mm 0; page-break-inside: avoid; }
th, td { border: 1pt solid #000; padding: 5px 9px; text-align: left; vertical-align: top; }
th { font-family: "SimHei","Heiti SC",sans-serif; font-weight: bold; background: #fff; }
tr { page-break-inside: avoid; }
pre { background: #f6f6f6; border: 0.75pt solid #000; padding: 2.5mm; font-size: 9.5pt; line-height: 1.5; white-space: pre-wrap; page-break-inside: avoid; }
code { font-family: Consolas, monospace; font-size: 10pt; }
ul, ol { margin: 0 0 3.5mm; padding-left: 2em; }
li { margin-bottom: 1.8mm; text-align: justify; overflow-wrap: break-word; }
hr { border: none; border-top: 1pt solid #000; margin: 7mm 0; }
img { max-width: 100%; height: auto; }
.team-table td { vertical-align: middle; }
.team-table .photo { width: 64px; height: 85px; object-fit: cover; border: 0.75pt solid #000; display: block; }
.team-table .sub { font-size: 8.5pt; color: #555; }
</style></head><body>""" + body + "</body></html>"

# ---- 按内容权重自动列宽：防止短标签列被长描述列挤压成一字宽 ----
import re as _re

def _add_colgroups(html: str) -> str:
    def fix_table(m: "_re.Match") -> str:
        table = m.group(0)
        if "<colgroup" in table:
            return table
        rows = _re.findall(r"<tr>(.*?)</tr>", table, _re.S)
        if not rows:
            return table
        ncols = max(len(_re.findall(r"<t[hd][ >]", r)) for r in rows)
        if ncols < 2:
            return table
        weights = [1.0] * ncols
        for r in rows:
            cells = _re.findall(r"<t[hd][ >](.*?)</t[hd]>", r, _re.S)
            for i, c in enumerate(cells[:ncols]):
                weights[i] += len(_re.sub(r"<[^>]+>", "", c).strip())
        total = sum(weights)
        pcts = [max(9.0, w / total * 100) for w in weights]
        scale = 100.0 / sum(pcts)
        pcts = [round(x * scale, 2) for x in pcts]
        colgroup = "<colgroup>" + "".join(
            f'<col style="width:{x}%">' for x in pcts) + "</colgroup>"
        return table.replace("<thead>", colgroup + "<thead>", 1)             if "<thead>" in table else table.replace(">", ">" + colgroup, 1)
    return _re.sub(r"<table>.*?</table>", fix_table, html, flags=_re.S)

body = _add_colgroups(body)

os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
open(out, "w", encoding="utf-8", newline="\n").write(html)
print("HTML_OK:", out)
