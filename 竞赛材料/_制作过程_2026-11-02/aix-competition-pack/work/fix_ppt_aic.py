# -*- coding: utf-8 -*-
"""将 LearnLab_AIC答辩PPT.pptx 去除 AIC 痕迹，另存为 AI+X 版本"""
from pptx import Presentation

SRC = r'e:\开发\learnlabAI教学平台\竞赛材料\AIC-2026-21740176_制作过程\交付材料\_待放入_PPT与视频\LearnLab_AIC答辩PPT.pptx'
DST = r'e:\开发\learnlabAI教学平台\竞赛材料\AI+X_提交包\LearnLab_AI+X答辩PPT.pptx'

MAP = [
    ('AIC 算法创新赛  /  AI + 学科交叉', '\u201cAI+X\u201d跨学科智能创新应用竞赛'),
    ('LEARNLAB  /  AIC 算法创新赛  /  谢谢各位评委',
     'LEARNLAB  /  \u201cAI+X\u201d跨学科创新应用竞赛  /  谢谢各位评委'),
    ('LEARNLAB  /  AIC 算法创新赛', 'LEARNLAB  /  \u201cAI+X\u201d跨学科创新应用竞赛'),
    ('AIC 回归', '功能回归'),
]

def fix_para(para):
    full = ''.join(r.text for r in para.runs)
    if not full.strip():
        return 0
    changed = False
    for old, new in MAP:
        if old in full:
            full = full.replace(old, new)
            changed = True
    if 'AIC' in full:  # 兜底：任何残留 AIC 字样
        full = full.replace('AIC', 'AI+X')
        changed = True
    if changed and para.runs:
        para.runs[0].text = full
        for r in para.runs[1:]:
            r.text = ''
    return 1 if changed else 0

p = Presentation(SRC)

# 母版/版式检查
extra = 0
for m in p.slide_masters:
    for s in m.shapes:
        if s.has_text_frame and 'AIC' in s.text_frame.text:
            extra += 1
    for lay in m.slide_layouts:
        for s in lay.shapes:
            if s.has_text_frame and 'AIC' in s.text_frame.text:
                extra += 1
print('母版/版式 AIC 形状数:', extra)

n = 0
for slide in p.slides:
    for shape in slide.shapes:
        if shape.has_text_frame:
            for para in shape.text_frame.paragraphs:
                n += fix_para(para)
print('替换段落数:', n)
p.save(DST)
print('已保存:', DST)

# 复检
p2 = Presentation(DST)
leftover = []
for idx, slide in enumerate(p2.slides, 1):
    for shape in slide.shapes:
        if shape.has_text_frame and ('AIC' in shape.text_frame.text or '学科交叉' in shape.text_frame.text):
            leftover.append((idx, shape.text_frame.text[:60]))
print('残留:', leftover if leftover else '无')
