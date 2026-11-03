# -*- coding: utf-8 -*-
"""视觉替代闸：页眉/图注/编号/字号层级/图文同页"""
import sys, re, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import fitz

P = r"e:\开发\learnlabAI教学平台\AI+X_提交包\马其瑞+202521047080+LearnLab跨学科智能学习平台"
REPORT = P + r"\02-作品报告\作品报告.pdf"
ZZ = P + r"\05-其他材料\佐证材料.pdf"

def spans(page):
    out = []
    for b in page.get_text("dict")["blocks"]:
        for l in b.get("lines", []):
            for s in l.get("spans", []):
                if s["text"].strip():
                    out.append(s)
    return out

# 1) 报告：每页页眉（logo 图 + 文字）与页脚页码
doc = fitz.open(REPORT)
print("== 报告 页眉/页脚 ==")
for i, page in enumerate(doc):
    imgs = page.get_images(full=True)
    head = "".join(s["text"] for s in spans(page) if s["bbox"][1] < 60)
    ok_head = ("跨学科智能创新应用竞赛" in re.sub(r"\s", "", head)) and len(imgs) >= 1
    foot = [s["text"].strip() for s in spans(page) if s["bbox"][1] > 790]
    if i == 0:
        print(f"P{i+1} 封面: 页眉{'OK' if len(imgs)>=1 else '!!缺logo'} 页脚={foot}")
    elif not ok_head or not foot:
        print(f"P{i+1} !! 页眉文字={'OK' if '跨学科' in re.sub(chr(92)+'s','',head) else head[:30]} 图={len(imgs)} 页脚={foot}")
print("（未打印的页 = 页眉页脚正常）")

# 2) 报告 P22-23 边界编号 1-5 序列
flat23 = re.sub(r"\s+", "", doc[22].get_text("text"))
flat22 = re.sub(r"\s+", "", doc[21].get_text("text"))
both = flat22 + flat23
seq = re.findall(r"[^\d]([1-5])\.[~～]?(?:知识追踪|趋势预警|电路仿真|学习内容|学科扩展)", both)
print("\n边界条目编号序列:", seq, "应为 1,2,3,4,5")
print("以下五处:", "以下五处" in flat22 or "以下五处" in flat23, "| 以上五处:", "以上五处" in both, "| 针对上述五处:", "针对上述五处" in both)

# 3) 字号层级：正文 span 主字号 & 标题字号
sizes = {}
for page in doc:
    for s in spans(page):
        if 70 < s["bbox"][1] < 780:
            sizes[round(s["size"], 1)] = sizes.get(round(s["size"], 1), 0) + len(s["text"])
main = sorted(sizes.items(), key=lambda x: -x[1])[:6]
print("\n正文字号分布(top6 字号:字符数):", main)

# 4) 图注与图同页：架构图 p? 与 fig_pilot、佐证 13 张截图
print("\n== 图与图注同页检查 ==")
for pi, page in enumerate(doc):
    txt = re.sub(r"\s+", "", page.get_text("text"))
    n_img = len(page.get_images(full=True))
    if n_img >= 1 and pi > 0:
        caps = re.findall(r"(系统总体架构图|试点流程|五层算法|防幻觉|FSRS|跨学科|前测后测)", txt)
        print(f"P{pi+1}: 图{n_img} 文字含图注关键词:{bool(caps)}")
doc.close()

# 5) 佐证：13 张截图与图注同页
doc = fitz.open(ZZ)
print("\n== 佐证 截图页 ==")
missing = []
for pi, page in enumerate(doc):
    n_img = len(page.get_images(full=True))
    txt = re.sub(r"\s+", "", page.get_text("text"))
    figs = set(re.findall(r"图(\d{1,2})", txt))
    if n_img and not figs:
        missing.append((pi + 1, n_img))
    elif n_img:
        print(f"P{pi+1}: 图{n_img}张 图号{sorted(figs, key=int)}")
print("有图无图注页:", missing if missing else "无")
doc.close()
