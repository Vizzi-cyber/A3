# -*- coding: utf-8 -*-
"""官方模板 docx 填充（纯追加版）：旧骨架段全删，内容按 md 流顺序追加文尾，样式用模板 Heading 1/2/3"""
import re, os
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

BASE = os.path.dirname(os.path.abspath(__file__))
MD = os.path.join(BASE, '..', 'AIC技术方案_LearnLab.md')
DOCX = os.path.abspath('交付材料/02_技术方案/模板工作.docx')
OUT = os.path.abspath('交付材料/02_技术方案/模板工作_filled.docx')
IMG = os.path.abspath('交付材料/_assets/架构图.png')
PHOTO = {'马其瑞': os.path.abspath('交付材料/_assets/队照/mqr.jpg'),
         '孙雨瑶': os.path.abspath('交付材料/_assets/队照/syy.jpg'),
         '居欣月': os.path.abspath('交付材料/_assets/队照/jxy.jpg')}

# ---------- md 解析 ----------
lines = open(MD, encoding='utf-8').read().split('\n')
elems, i = [], 0
in_cover = in_toc = False
while i < len(lines):
    ln = lines[i]
    if ln.startswith('<div class="cover">'):
        in_cover = True; i += 1; continue
    if in_cover:
        if ln.startswith('</div>'): in_cover = False
        i += 1; continue
    if ln.startswith('<div class="toc">'):
        in_toc = True; i += 1; continue
    if in_toc:
        if ln == '</div>': in_toc = False
        i += 1; continue
    if ln.startswith('## 目录') or ln == '---' or ln.strip() == '':
        i += 1; continue
    if ln.startswith('## 作品简介'):
        i += 1
        while i < len(lines) and not lines[i].startswith(('## ', '---')):
            if lines[i].strip(): elems.append(('para_intro', lines[i].strip()))
            i += 1
        continue
    m = re.match(r'^## (.+)$', ln)
    if m: elems.append(('h1', m.group(1).strip())); i += 1; continue
    m = re.match(r'^### (.+)$', ln)
    if m: elems.append(('h2', m.group(1).strip())); i += 1; continue
    m = re.match(r'^#### (.+)$', ln)
    if m: elems.append(('h3', m.group(1).strip())); i += 1; continue
    m = re.match(r'^!\[(.*)\]\((.*)\)$', ln)
    if m: elems.append(('img', (m.group(1), IMG))); i += 1; continue
    if ln.startswith('|'):
        rows = []
        while i < len(lines) and lines[i].startswith('|'):
            cells = [c.strip() for c in lines[i].strip().strip('|').split('|')]
            if not re.match(r'^[\s\-:|]+$', lines[i]): rows.append(cells)
            i += 1
        elems.append(('table', rows)); continue
    if ln.startswith('<table class="team-table">'):
        block = []
        while i < len(lines) and not lines[i].startswith('</table>'):
            block.append(lines[i]); i += 1
        i += 1
        block_str = chr(10).join(block)
        rows_data = []
        for tr in re.findall(r'<tr>(.*?)</tr>', block_str, re.S):
            cells = re.findall(r'<t[hd][^>]*>(.*?)</t[hd]>', tr, re.S)
            if cells:
                rows_data.append([re.sub(r'<[^>]+>', ' ', c).replace(chr(10), ' ').strip() for c in cells])
        elems.append(('team_table', rows_data)); continue
    if ln.startswith('- '):
        elems.append(('bullet', ln[2:].strip())); i += 1; continue
    elems.append(('para', ln.strip())); i += 1
print('元素流:', len(elems))

# ---------- 打开模板 ----------
d = Document(DOCX)
body = d.element.body

def ptext_all(el):
    return ''.join(t.text or '' for t in el.iter() if t.tag in (qn('w:t'), qn('w:instrText')))

def ptext(el):
    return ''.join(t.text or '' for t in el.iter(qn('w:t')))

# ---------- 1. 封面填值 ----------
def fill(p, value):
    for r in p.runs:
        if r.font.underline:
            r.text = value; return True
    return False

cover = {'团队名称': '一起搞事情', '参赛编号': 'AIC-2026-21740176',
         '作品名称': 'LearnLab 跨学科智能学习平台'}
for p in d.paragraphs[:22]:
    for label, val in list(cover.items()):
        if p.text.strip().startswith(label) and '：' in p.text:
            if fill(p, val): cover.pop(label)
print('封面未填:', cover if cover else '无（全部成功）')
for p in d.paragraphs[:25]:
    if p.text.strip().startswith('日期：'):
        vals = ['日期：', '2026', ' 年 ', '10', ' 月 ', '', '']
        for r, v in zip(p.runs, vals): r.text = v
        break

# ---------- 2. 删除旧骨架与占位/提示段 ----------
DEL_KEYS = ['提示信息', '不用此信息时', '（鼠标移到此框', '字体:宋体', '目录标题:二号', '一级标题:三号',
            '二级标题:四号', '三级标题:小四', '正文:小四号', '行距:单倍行距', '页边距:上:', '页眉:1.5',
            '页脚:1.5', '纸型:A4', '（五）其他问题', '中国学术期刊（光盘版）', '左:3厘米', '装订线',
            '单击键入正文']
SKELETON = ['一、项目概述', '二、AAAAAAAA', '三、附录', '（一）项目背景与意义', '（二）赛题方向定位']
removed = 0
for p in list(d.paragraphs):
    t = p.text.strip()
    hit = t in SKELETON or any(k in t for k in DEL_KEYS)
    if hit:
        p._element.getparent().remove(p._element); removed += 1
# 深遍历补删：MACROBUTTON 域占位段（instrText 感知，覆盖 sdt 内）
for p in list(body.iter(qn('w:p'))):
    t = ptext_all(p)
    if '单击键入正文' in t:
        p.getparent().remove(p); removed += 1
print('删除旧骨架/占位/提示段:', removed)

# ---------- 3. 追加工具（文尾，顺序天然正确）----------
count = {'h1': 0, 'h2': 0, 'h3': 0, 'para': 0, 'bullet': 0, 'table': 0, 'img': 0, 'intro': 0}

def fmt_para(p, indent=True):
    pf = p.paragraph_format
    pf.line_spacing = 1.0
    pf.space_before = Pt(0); pf.space_after = Pt(0)
    if indent: pf.first_line_indent = Pt(24)
    pPr = p._p.get_or_add_pPr()
    if pPr.find(qn('w:snapToGrid')) is None:
        snap = pPr.makeelement(qn('w:snapToGrid'), {qn('w:val'): '0'})
        pPr.insert(0, snap)

def add_text_runs(para, text, size=12, bold_all=False):
    for part in re.split(r'(\*\*.*?\*\*)', text):
        if not part: continue
        b = part.startswith('**')
        r = para.add_run(part.strip('*') if b else part)
        r.font.name = '宋体'; r.font.size = Pt(size)
        r.font.bold = True if (b or bold_all) else None
        r._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

def ins_team_table(rows):
    # 三张证件照并排一行
    p = d.add_paragraph('')
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for name in ['马其瑞', '孙雨瑶', '居欣月']:
        ph = PHOTO.get(name)
        if ph and os.path.exists(ph):
            r = p.add_run('      ')
            r.font.size = Pt(12)
            p.add_run().add_picture(ph, height=Cm(3.4))
    # 姓名行
    np = d.add_paragraph('')
    np.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_text_runs(np, '马其瑞（队长）　　　　孙雨瑶　　　　居欣月', bold_all=True)
    # 文字表（成员 / 专业方向 / 角色定位 三列）
    t = d.add_table(rows=len(rows), cols=3)
    try: t.style = 'Table Grid'
    except Exception: pass
    t.autofit = False
    for ri, row in enumerate(rows):
        vals = [row[0], row[2], row[3]] if len(row) >= 4 else (row + ['', '', ''])[:3]
        for ci, cell in enumerate(vals):
            c = t.cell(ri, ci); c.text = ''
            add_text_runs(c.paragraphs[0], cell, size=10.5, bold_all=(ri == 0))
    count['table'] += 1

def H(level, text):
    d.add_paragraph(text, style=f'Heading {level}')

def P(text, size=12, indent=True):
    p = d.add_paragraph('', style='Normal')
    add_text_runs(p, text, size=size)
    fmt_para(p, indent)
    count['para'] += 1

def B(text):
    p = d.add_paragraph('', style='Normal')
    add_text_runs(p, '• ' + text)
    fmt_para(p, indent=False)
    p.paragraph_format.left_indent = Pt(24)
    count['bullet'] += 1

def T(rows):
    t = d.add_table(rows=len(rows), cols=len(rows[0]))
    try: t.style = 'Table Grid'
    except Exception: pass
    for ri, row in enumerate(rows):
        for ci, cell in enumerate(row):
            if ci >= len(t.rows[ri].cells): continue
            c = t.cell(ri, ci); c.text = ''
            add_text_runs(c.paragraphs[0], cell, size=10.5, bold_all=(ri == 0))
    count['table'] += 1

def IMG_ADD(path):
    p = d.add_paragraph('')
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(path, width=Cm(15))
    count['img'] += 1

def TEAM(rows):
    t = d.add_table(rows=len(rows), cols=4)
    try: t.style = 'Table Grid'
    except Exception: pass
    widths = [Cm(2.6), Cm(2.8), Cm(3.6), Cm(6.0)]
    for ri, row in enumerate(rows):
        row = (row + ['', '', '', ''])[:4]
        for ci in range(4):
            c = t.cell(ri, ci); c.text = ''; c.width = widths[ci]
            para = c.paragraphs[0]
            if ci == 1 and ri > 0:
                name = row[0].split('队长')[0].split('2025')[0].strip()
                ph = PHOTO.get(name)
                if ph and os.path.exists(ph):
                    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    para.add_run().add_picture(ph, width=Cm(2.2))
            else:
                add_text_runs(para, row[ci], size=10.5, bold_all=(ri == 0))
    count['table'] += 1

# ---------- 4. 按流追加全部内容 ----------
for kind, val in elems:
    if kind == 'para_intro':
        t_title = None
        for p in body.iter(qn('w:p')):
            if ptext(p).strip() == '作品简介': t_title = p; break
        assert t_title is not None
        np = t_title.makeelement(qn('w:p'), {})
        t_title.addnext(np)
        from docx.text.paragraph import Paragraph
        para_obj = Paragraph(np, t_title.getparent())
        add_text_runs(para_obj, val)
        fmt_para(para_obj, True)
        count['intro'] += 1; continue
    if kind == 'h1':
        d.add_paragraph(val, style='Heading 1')
        count['h1'] += 1; continue
    if kind == 'h2':
        d.add_paragraph(val, style='Heading 2'); count['h2'] += 1; continue
    if kind == 'h3':
        d.add_paragraph(val, style='Heading 3'); count['h3'] += 1; continue
    if kind == 'para':
        P(val); continue
    if kind == 'bullet':
        B(val); continue
    if kind == 'table':
        T(val); continue
    if kind == 'team_table':
        ins_team_table(val); continue
    if kind == 'img':
        IMG_ADD(val[1]); continue

# ---------- 7. 全部表格统一加边框（保存前兜底，不依赖样式）----------
for t in d.tables:
    tblPr = t._tbl.tblPr
    borders = tblPr.find(qn('w:tblBorders'))
    if borders is None:
        borders = tblPr.makeelement(qn('w:tblBorders'), {})
        tblPr.append(borders)
    for edge in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        el = borders.find(qn('w:' + edge))
        if el is None:
            el = borders.makeelement(qn('w:' + edge), {})
            borders.append(el)
        el.set(qn('w:val'), 'single'); el.set(qn('w:sz'), '4')
        el.set(qn('w:space'), '0'); el.set(qn('w:color'), '000000')

d.save(OUT)
print('saved:', OUT, os.path.getsize(OUT))
print('统计:', count)
