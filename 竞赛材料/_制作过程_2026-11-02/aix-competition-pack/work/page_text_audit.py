# -*- coding: utf-8 -*-
"""图片通道故障时的替代目检：逐页文本+坐标审计"""
import sys, re, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import fitz

P = r"e:\开发\learnlabAI教学平台\AI+X_提交包\马其瑞+202521047080+LearnLab跨学科智能学习平台"
docs = {
    "报告": P + r"\02-作品报告\作品报告.pdf",
    "佐证": P + r"\05-其他材料\佐证材料.pdf",
    "AI说明": P + r"\01-AI工具使用说明\AI工具使用说明.pdf",
    "功能说明": P + r"\05-其他材料\功能说明.pdf",
    "验证清单": P + r"\05-其他材料\功能验证清单.pdf",
    "运行说明": P + r"\05-其他材料\运行说明.pdf",
}

def run(tag, path):
    doc = fitz.open(path)
    print(f"\n===== {tag} ({doc.page_count}页) =====")
    for i, page in enumerate(doc):
        issues = []
        d = page.get_text("dict")
        # 页面内容底界（检测大面积空白：正文底 < 600pt 视为下半页空，封面/末页除外）
        body_bottom = 0
        for b in d["blocks"]:
            for l in b.get("lines", []):
                for s in l.get("spans", []):
                    t = s["text"].strip()
                    if t and s["bbox"][1] < 790:  # 排除页脚
                        body_bottom = max(body_bottom, s["bbox"][3])
        if i > 0 and i < doc.page_count - 1 and body_bottom < 560:
            issues.append(f"下半页空白(正文底 {body_bottom:.0f}pt)")
        # 文本
        txt = page.get_text("text")
        flat = re.sub(r"\s+", "", txt)
        # ASCII 标点夹在中文字符间（排除代码/数字/英文场景：中文,中文 或 中文.中文）
        for mm in re.finditer(r"[\u4e00-\u9fff][,.;:!?][\u4e00-\u9fff]", flat):
            issues.append(f"中文间ASCII标点: …{mm.group(0)}…")
        # 元注解 / AI 味指纹
        for pat in [r"TODO", r"FIXME", r"XXX", r"【待", r"待补", r"占位", r"赋能价值", r"黄金纠错期", r"\"待实现\""]:
            if re.search(pat, flat):
                issues.append(f"指纹词: {pat}")
        print(f"P{i+1:02d} 底={body_bottom:.0f} " + ("| " + "; ".join(issues) if issues else "OK"))
    doc.close()

for tag, p in docs.items():
    run(tag, p)
