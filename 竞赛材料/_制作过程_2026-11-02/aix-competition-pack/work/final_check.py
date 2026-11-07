# -*- coding: utf-8 -*-
"""AI+X 提交包终检：页数/残留/吉相如/zip 完整性"""
import os, zipfile, re, sys

pkg = r'e:\开发\learnlabAI教学平台\竞赛材料\AI+X_提交包\马其瑞+202521047080+LearnLab跨学科智能学习平台'
FEATURES = ['aic', 'AIC', '算法创新赛', 'AI+学科交叉', 'AI＋学科交叉', '21740176', '软件杯', '全球校园', '算法精英']

from pypdf import PdfReader

print('== PDF 页数与残留 ==')
pdfs = [
    ('01-AI工具使用说明/AI工具使用说明.pdf', 4),
    ('02-作品报告/作品报告.pdf', 27),
    ('05-其他材料/答辩PPT.pdf', 25),
    ('05-其他材料/运行说明.pdf', 5),
]
for rel, expect in pdfs:
    r = PdfReader(os.path.join(pkg, rel))
    text = ''.join((pg.extract_text() or '') for pg in r.pages)
    hits = {w: text.count(w) for w in FEATURES if text.count(w)}
    jxr = text.count('吉相如')
    flag = 'OK' if len(r.pages) == expect and not hits else '!!'
    print(f'{flag} {rel}: {len(r.pages)}页(期望{expect}) 吉相如x{jxr} 残留={hits if hits else "无"}')

print()
print('== zip 完整性与内部文本残留 ==')
zp = os.path.join(pkg, '03-源代码/LearnLab源代码.zip')
with zipfile.ZipFile(zp) as z:
    bad = z.testzip()
    names = z.namelist()
    print(f'{"OK" if bad is None else "!!"} testzip={bad or "完整"} 条目数={len(names)}')
    inner_hits = {}
    for info in z.infolist():
        if info.file_size > 2_000_000 or info.is_dir():
            continue
        try:
            data = z.read(info).decode('utf-8', errors='ignore')
        except Exception:
            continue
        for w in FEATURES:
            c = data.count(w)
            if c:
                inner_hits.setdefault(w, []).append(f'{info.filename} x{c}')
    print(f'{"OK" if not inner_hits else "!!"} 内部残留={inner_hits if inner_hits else "无"}')
    for need in ['verify_core_features.py', 'verify_all_routes.py', 'e2e/core-features.spec.ts', 'scripts/seed_data.py', '.env.example']:
        found = any(n.endswith(need) or n == need for n in names)
        print(f'{"OK" if found else "!!"} 包内存在 {need}: {found}')
