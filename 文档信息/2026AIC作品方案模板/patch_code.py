# -*- coding: utf-8 -*-
p = '文档信息/2026AIC作品方案模板/fill_template.py'
s = open(p, encoding='utf-8').read()
a = """def add_text_runs(para, text, size=12, bold_all=False):
    for part in re.split(r'(\\*\\*.*?\\*\\*)', text):
        if not part: continue
        b = part.startswith('**')
        r = para.add_run(part.strip('*') if b else part)
        r.font.name = '宋体'; r.font.size = Pt(size)
        r.font.bold = True if (b or bold_all) else None
        r._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')"""
b = """def add_text_runs(para, text, size=12, bold_all=False):
    for part in re.split(r'(\\*\\*.*?\\*\\*)', text):
        if not part: continue
        b = part.startswith('**')
        clean = part.strip('*') if b else part
        for seg in re.split(r'(`[^`]+`)', clean):
            if not seg: continue
            code = seg.startswith('`')
            r = para.add_run(seg.strip('`') if code else seg)
            r.font.name = 'Consolas' if code else '宋体'
            r.font.size = Pt(size - 1.5 if code else size)
            r.font.bold = True if (b or bold_all) else None
            r._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')"""
assert a in s, 'anchor miss'
open(p, 'w', encoding='utf-8').write(s.replace(a, b, 1))
print('patch ok')
