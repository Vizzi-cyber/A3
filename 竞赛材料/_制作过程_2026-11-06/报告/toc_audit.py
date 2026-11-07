# -*- coding: utf-8 -*-
"""基于 main.toc 的精确目录断言"""
import sys, re

sys.stdout.reconfigure(encoding="utf-8")
import fitz

toc = open("main.toc", encoding="utf-8").read()
entries = re.findall(r"contentsline \{(section|subsection|subsubsection)\}\{(.+?)\}\{(\d+)\}", toc)
doc = fitz.open("main.pdf")
pages = [re.sub(r"\s+", "", p.get_text("text")) for p in doc]


def clean(s):
    s = re.sub(r"\\textbf\s*", "", s)
    s = re.sub(r"\\numberline\s*\{([\d.]*)\}", r"\1", s)  # 保留编号（含 1.1.1 形式）
    s = re.sub(r"[{}\\~$]", "", s)
    s = re.sub(r"\s+", "", s)  # 只去空白，保留点号与正文渲染一致
    return s


bad = checked = 0
for typ, title, num in entries:
    t = clean(title)
    if len(t) < 3:
        continue
    n = int(num)
    if n + 1 >= len(pages):
        continue
    ok = t in pages[n]  # 印刷页 n = PDF 索引 n（封面无页码，PDF第2页印刷1）
    if not ok:
        found = [k for k in range(2, len(pages)) if t in pages[k]]
        bad += 1
        print(f"[{typ}] {title[:36]!r} TOC={n} 实际印刷页={found[:3]}")
    checked += 1
print(f"检查 {checked} 条, 不一致 {bad} 条")
doc.close()
