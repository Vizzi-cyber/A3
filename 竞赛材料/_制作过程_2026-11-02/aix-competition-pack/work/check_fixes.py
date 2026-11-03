# -*- coding: utf-8 -*-
"""核对 13 条文字修正是否落在改写版 tex/md 中"""
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
base = r"e:\开发\learnlabAI教学平台\2026-11-02\aix-competition-pack\work"
m = open(base + r"\技术报告\main.tex", encoding="utf-8").read()
z = open(base + r"\佐证材料\zz.tex", encoding="utf-8").read()
q = open(base + r"\小PDF\10_功能验证清单.md", encoding="utf-8").read()
ai = open(base + r"\AI工具使用说明.md", encoding="utf-8").read()

def show(tag, pat, text, ctx=60):
    hits = [(mm.start(), text[max(0, mm.start()-20):mm.end()+ctx].replace("\n", "⏎")) for mm in re.finditer(pat, text)]
    print(f"[{tag}] /{pat}/ -> {len(hits)} hit(s)")
    for _, h in hits[:6]:
        print("    …" + h + "…")

print("========== 报告 main.tex ==========")
for p in [r"三处|五处", r"67\.9", r"人均日均", r"15\.7|15\.8", r"未出现失败|未记录到失败",
          r"正在同步进行|已逐项落实", r"AI 赋能价值", r"黄金纠错期", r"”待实现|待实现”",
          r"38项|38 项", r"26项|26 项"]:
    show("报告", p, m)
print("========== 佐证 zz.tex ==========")
for p in [r"账号体验", r"体验账号", r"分类准确率见", r"学生端核心流程 59", r"学生端与教师端", r"59/59"]:
    show("佐证", p, z)
print("========== 验证清单 ==========")
for p in [r"12\s*页", r"22\s*页", r"24\s*页", r"14\s*页"]:
    show("清单", p, q)
print("========== AI说明（残留检查） ==========")
for p in [r"向量化|向量模型", r"本地向量化"]:
    show("AI说明", p, ai)
