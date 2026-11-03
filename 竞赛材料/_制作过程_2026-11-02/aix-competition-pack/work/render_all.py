# -*- coding: utf-8 -*-
"""复查用：把 6 份成品 PDF 全部渲染成 PNG"""
import sys, os, fitz

sys.stdout.reconfigure(encoding="utf-8")
base = r"e:\开发\learnlabAI教学平台\AI+X_提交包\马其瑞+202521047080+LearnLab跨学科智能学习平台"
out = r"e:\开发\learnlabAI教学平台\_制作过程_2026-11-02\aix-competition-pack\work\复查渲染"
pdfs = {
    "报告": base + r"\02-作品报告\作品报告.pdf",
    "佐证": base + r"\05-其他材料\佐证材料.pdf",
    "AI说明": base + r"\01-AI工具使用说明\AI工具使用说明.pdf",
    "功能说明": base + r"\05-其他材料\功能说明.pdf",
    "验证清单": base + r"\05-其他材料\功能验证清单.pdf",
    "运行说明": base + r"\05-其他材料\运行说明.pdf",
}
for tag, p in pdfs.items():
    d = fitz.open(p)
    od = os.path.join(out, tag)
    os.makedirs(od, exist_ok=True)
    for i in range(d.page_count):
        d[i].get_pixmap(dpi=110).save(os.path.join(od, f"p{i+1:02d}.png"))
    print(tag, d.page_count, "页 ->", od)
    d.close()
