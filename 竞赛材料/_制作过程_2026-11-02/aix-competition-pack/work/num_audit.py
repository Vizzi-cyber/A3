# -*- coding: utf-8 -*-
"""内容复查：抽取各 PDF 中关键数字出现处，交叉比对一致性"""
import sys, re, fitz

sys.stdout.reconfigure(encoding="utf-8")
base = r"e:\开发\learnlabAI教学平台\2026-11-02\aix-competition-pack\outputs\马其瑞+202521047080+LearnLab跨学科智能学习平台"
pdfs = {
    "报告": base + r"\02-作品报告\作品报告.pdf",
    "佐证": base + r"\05-其他材料\佐证材料.pdf",
    "AI说明": base + r"\01-AI工具使用说明\AI工具使用说明.pdf",
    "功能说明": base + r"\05-其他材料\功能说明.pdf",
    "验证清单": base + r"\05-其他材料\功能验证清单.pdf",
    "运行说明": base + r"\05-其他材料\运行说明.pdf",
}

# 关键指标：正则 -> 标签
metrics = {
    "E2E": re.compile(r"E2E[^。；\n]{0,30}?(\d+)\s*(?:条|个|项|条用例|条测试)?"),
    "路由": re.compile(r"(\d+)\s*(?:条|个)?(?:后端)?路由"),
    "接口": re.compile(r"(\d+)\s*(?:条|个)?(?:REST)?接口"),
    "智能体": re.compile(r"(\d+)\s*(?:个|名)?(?:教育)?智能体"),
    "知识点": re.compile(r"(\d+)\s*(?:个|条)?知识点"),
    "课程": re.compile(r"(\d+)\s*(?:门|个)课程"),
    "学生规模": re.compile(r"(\d+)\s*(?:名|个)?学生"),
    "题目": re.compile(r"(\d+)\s*(?:道|条|个)题目"),
    "单元测试": re.compile(r"(\d+)\s*(?:条|个)?(?:单元测试|pytest|后端测试)"),
    "召回": re.compile(r"召回率[^。；\n]{0,20}?(\d+(?:\.\d+)?)\s*%?"),
    "准确": re.compile(r"准确率[^。；\n]{0,20}?(\d+(?:\.\d+)?)\s*%?"),
    "响应时间": re.compile(r"响应时间[^。；\n]{0,30}?(\d+(?:\.\d+)?)\s*(?:ms|毫秒|秒)"),
    "并发": re.compile(r"(\d+)\s*(?:路|个)?并发"),
    "覆盖率": re.compile(r"覆盖率[^。；\n]{0,20}?(\d+(?:\.\d+)?)\s*%?"),
}

texts = {}
for tag, p in pdfs.items():
    doc = fitz.open(p)
    texts[tag] = "\n".join(pg.get_text("text") for pg in doc)
    doc.close()

for tag, t in texts.items():
    print("=" * 20, tag)
    for name, pat in metrics.items():
        hits = pat.findall(t)
        if hits:
            # 去重保序
            seen, uniq = set(), []
            for h in hits:
                if h not in seen:
                    seen.add(h); uniq.append(h)
            print(f"  {name}: {uniq}")
