# -*- coding: utf-8 -*-
"""排版闸断言（依 [[AI-复查工作流]] ③排版闸）：页码连续/封面无页码/右界溢出/残留字符/标题孤悬"""
import sys, re, glob, os

sys.stdout.reconfigure(encoding="utf-8")
import fitz  # pymupdf

P = r"e:\开发\learnlabAI教学平台\AI+X_提交包\马其瑞+202521047080+LearnLab跨学科智能学习平台"
TARGETS = [
    P + r"\02-作品报告\作品报告.pdf",
    P + r"\05-其他材料\佐证材料.pdf",
    P + r"\01-AI工具使用说明\AI工具使用说明.pdf",
    P + r"\05-其他材料\功能说明.pdf",
    P + r"\05-其他材料\功能验证清单.pdf",
    P + r"\05-其他材料\运行说明.pdf",
]

RIGHT_LIMIT = 522.0  # A4 595pt - 3cm 边距 85pt + 12pt 容差
issues_total = 0

for path in TARGETS:
    doc = fitz.open(path)
    name = os.path.basename(path)
    issues = []
    page_num_re = re.compile(r"^\d{1,3}$")
    footer_nums = []
    for i, page in enumerate(doc):
        # 1) 右界溢出 + 残留字符 + 豆腐块
        for b in page.get_text("dict")["blocks"]:
            for l in b.get("lines", []):
                for s in l.get("spans", []):
                    if s["bbox"][2] > RIGHT_LIMIT and s["text"].strip():
                        issues.append(f"P{i+1} 右界溢出 {s['bbox'][2]:.0f}pt: {s['text'][:24]!r}")
                    if "□" in s["text"] or "�" in s["text"]:
                        issues.append(f"P{i+1} 豆腐块: {s['text'][:30]!r}")
                    txt = s["text"]
                    if re.search(r"(?<!\*)\*(?!\*)|(?<!`)``?(?!`)|^#{1,3}\s", txt):
                        issues.append(f"P{i+1} 残留md字符: {txt[:30]!r}")
        # 2) 页脚页码
        words = page.get_text("words")
        for w in words:
            if w[1] > 780 and page_num_re.match(w[4].strip()):
                footer_nums.append((i + 1, int(w[4])))
    # 封面无页码（LaTeX 类：第 1 页页脚不应有纯页码；小 PDF 无封面不检查）
    if any(p == 1 for p, _ in footer_nums) and ("作品报告" in name or "佐证" in name):
        issues.append("封面(第1页)出现页脚页码")
    # 页码连续
    seq = [n for _, n in footer_nums]
    if len(seq) >= 2:
        diffs = {seq[j + 1] - seq[j] for j in range(len(seq) - 1)}
        if diffs and max(diffs) > 1:
            issues.append(f"页码不连续: {seq[:8]}...")
    doc.close()
    print(f"== {name}: {len(issues)} 项")
    for x in issues[:10]:
        print("  ", x)
    issues_total += len(issues)

print("\n总问题数:", issues_total)
