# -*- coding: utf-8 -*-
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
base = r"e:\开发\learnlabAI教学平台\2026-11-02\aix-competition-pack\work"
m = open(base + r"\技术报告\main.tex", encoding="utf-8").read()
lines = m.split("\n")
pats = ["以下三处", "以上三处", "针对上述三处", "67.9", "15.7", "未出现失败", "正在同步进行",
        "AI 赋能价值", "黄金纠错期", "全接口 26", "全链路冒烟 38"]
for i, ln in enumerate(lines, 1):
    if any(p in ln for p in pats):
        print(f"L{i}: {ln[:150]}")
# 编号断裂区域：打印 以下三处 前后 40 行
for i, ln in enumerate(lines, 1):
    if "以下三处" in ln:
        for j in range(i-1, min(i+45, len(lines))):
            print(f">> {j+1}: {lines[j][:160]}")
        break
# 引号审计：右弯引号不左配对
print("== 引号审计 main.tex ==")
for mm in re.finditer(r"”[^””]{1,40}”", m):
    s = mm.start()
    if s == 0 or m[s-1] not in "“\"":
        print("右引号开头:", m[max(0,s-15):mm.end()+5].replace("\n","⏎"))
print("== 引号审计 zz.tex ==")
z = open(base + r"\佐证材料\zz.tex", encoding="utf-8").read()
for mm in re.finditer(r"”[^””]{1,40}”", z):
    s = mm.start()
    if s == 0 or z[s-1] not in "“\"":
        print("右引号开头:", z[max(0,s-15):mm.end()+5].replace("\n","⏎"))
