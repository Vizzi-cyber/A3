# -*- coding: utf-8 -*-
import sys, re, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import fitz
doc = fitz.open(r"e:\开发\learnlabAI教学平台\AI+X_提交包\马其瑞+202521047080+LearnLab跨学科智能学习平台\02-作品报告\作品报告.pdf")
txt = doc[25].get_text("text")
flat = re.sub(r"\s+", "", txt)
for mm in re.finditer(r"[\u4e00-\u9fff][,.;:!?][\u4e00-\u9fff]", flat):
    s = mm.start()
    print("…" + flat[max(0,s-40):s+40] + "…")
doc.close()
