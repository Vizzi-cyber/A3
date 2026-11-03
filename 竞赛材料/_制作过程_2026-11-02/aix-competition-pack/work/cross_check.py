# -*- coding: utf-8 -*-
"""六份文档数字口径交叉核对 + 旧值残留扫描"""
import sys, re, io
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
texts = {}
for tag, p in docs.items():
    d = fitz.open(p)
    texts[tag] = re.sub(r"\s+", "", "\n".join(pg.get_text("text") for pg in d))
    d.close()

# 1) 关键正确口径出现位置（应为真）
must = {
    r"59": ["报告", "佐证", "验证清单"],
    r"211": ["报告", "佐证", "验证清单", "AI说明", "功能说明", "运行说明"],
    r"116": ["报告", "佐证", "验证清单", "AI说明"],
    r"12个智能体|12个教育": ["报告", "佐证", "功能说明", "AI说明", "验证清单"],
    r"35个知识点|知识点35|35个": ["报告"],
    r"24个页面|24页": ["报告", "佐证", "验证清单"],
}
for pat, tags in must.items():
    for t in tags:
        print(f"[应有] {t} /{pat}/ : {'有' if re.search(pat, texts[t]) else '!! 缺失'}")

# 2) 旧值/矛盾口径（应为无）
stale = [r"以下三处", r"以上三处", r"针对上述三处", r"学生端核心流程", r"账号体验",
         r"人均日均", r"未出现失败案例", r"正在同步进行", r"32个知识点",
         r"教师端12页", r"22页全部正常", r"49个|49用例|59\+49",
         r"210个路由", r"AIC", r"算法精英大赛", r"21740176", r"第八届"]
for t, txt in texts.items():
    for pat in stale:
        if re.search(pat, txt):
            print(f"[残留] {t} /{pat}/ !!")
print("残留扫描完成")

# 3) 数字出现汇总（人工比对口径）
for t, txt in texts.items():
    nums = {}
    for key, pat in {"E2E59": r"59", "路由211": r"211", "断言116": r"116", "智能体12": r"12个",
                     "页面24": r"24个页面|24页", "接口26": r"26项", "冒烟38": r"38项",
                     "回归29": r"29", "数据流23": r"23", "MNA9": r"9/9|9项"}.items():
        nums[key] = len(re.findall(pat, txt))
    print(t, nums)
