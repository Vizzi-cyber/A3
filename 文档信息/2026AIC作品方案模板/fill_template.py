# -*- coding: utf-8 -*-
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

lines = open(MD, encoding='utf-8').read().split('\n')
elems, i = [], 0
in_cover = in_toc = False
while i < len(lines):
    ln = lines[i]
    if ln.startswith('<div class="cover">'): in_cover = True; i += 1; continue
    if in_cover:
        if ln.startswith('</div>'): in_cover = False
        i += 1; continue
    if ln.startswith('<div class="toc">'): in_toc = True; i += 1; continue
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
    if m: elems.append(('h3', m.group(1).strip())); i += 1; continue
    m = re.match(r'^#### (.+)$', ln)
    if m: elems.append(('h4', m.group(1).strip())); i += 1; continue
    m = re.match(r'^!\[(.*)\]\((.*)\)$', ln)
    if m:
        elems.append(('img', (m.group(1), IMG))); i += 1; continue
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
        rows_data = []
        for bl in block:
            cells = re.findall(r'<t[hd][^>]*>(.*?)</t[hd]>', bl)
            if cells:
                rows_data.append([re.sub(r'<[^>]+>', '', c).replace(chr(10), ' ').strip() for c in cells])
        elems.append(('team_table', rows_data)); continue
    if ln.startswith('- '):
        elems.append(('bullet', ln[2:].strip())); i += 1; continue
    elems.append(('para', ln.strip())); i += 1
print('元素流:', len(elems))

d = Document(DOCX)

def fill(p, value):
    for r in p.runs:
        if r.font.underline:
            r.text = value; return True
    return False

cover = {'团队名称': '一起搞事情', '参赛编号': 'AIC-2026-21740176', '作品名称': 'LearnLab 跨学科智能学习平台'}
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

DEL_KEYS = ['提示信息', '不用此信息时', '（鼠标移到此框', '字体:宋体', '目录标题:二号', '一级标题:三号',
            '二级标题:四号', '三级标题:小四', '正文:小四号', '行距:单倍行距', '页边距:上:', '页眉:1.5',
            '页脚:1.5', '纸型:A4', '（五）其他问题', '中国学术期刊（光盘版）', '（一）字体', '（二）字号',
            '（三）行距', '（四）页面设置']
deleted = 0
for p in list(d.paragraphs):
    if any(k in p.text for k in DEL_KEYS):
        p._element.getparent().remove(p._element); deleted += 1
print('删除提示段:', deleted)

def find_h1(prefix):
    for p in d.paragraphs:
        if p.style.name == 'Heading 1' and p.text.strip().startswith(prefix): return p
    return None

def set_text(p, text):
    for r in p.runs: r.text = ''
    if p.runs: p.runs[0].text = text
    else: p.add_run(text)

h1_ch2 = find_h1('二、')
assert h1_ch2, '未找到 Heading1 二、'
set_text(h1_ch2, '二、需求分析')
h1_app = find_h1('三、')
assert h1_app, '未找到 Heading1 三、'
set_text(h1_app, '八、附录')

h3_list = [p for p in d.paragraphs if p.style.name == 'Heading 3']
print('Heading3 段:', [p.text.strip()[:16] for p in h3_list])
h3_1 = h3_list[0]
set_text(h3_1, '1. 行业痛点')
h_2n_cands = [p for p in d.paragraphs
              if (p.text.strip() == '2.' or p.text.strip().startswith('2. '))
              and p.style.name == 'Normal' and len(p.text.strip()) < 8]
print('2. 占位候选:', len(h_2n_cands))
h_2n = h_2n_cands[0]
h_2n.style = d.styles['Heading 3']
set_text(h_2n, '2. 学科发展现状与行业需求')
h2_bg = [p for p in d.paragraphs if p.style.name == 'Heading 2' and '项目背景与意义' in p.text][0]
h2_goal = [p for p in d.paragraphs if p.style.name == 'Heading 2' and '赛题方向定位' in p.text][0]
set_text(h2_goal, '（二）核心目标与赛题方向定位')

def add_text_runs(para, text, size=12, bold_all=False):
    for part in re.split(r'(\*\*.*?\*\*)', text):
        if not part: continue
        b = part.startswith('**')
        r = para.add_run(part.strip('*') if b else part)
        r.font.name = '宋体'; r.font.size = Pt(size)
        r.font.bold = True if (b or bold_all) else None
        r._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

def insert_para(anchor, text, size=12):
    np = anchor.insert_paragraph_before('', style='Normal')
    add_text_runs(np, text, size=size)
    np.paragraph_format.first_line_indent = Pt(24)
    return np

def insert_table(anchor, rows):
    t = d.add_table(rows=len(rows), cols=len(rows[0]))
    try: t.style = 'Table Grid'
    except Exception: pass
    for ri, row in enumerate(rows):
        for ci, cell in enumerate(row):
            if ci >= len(t.rows[ri].cells): continue
            c = t.cell(ri, ci); c.text = ''
            add_text_runs(c.paragraphs[0], cell, size=10.5, bold_all=(ri == 0))
    anchor._p.addprevious(t._tbl)

def insert_img(anchor, path):
    np = anchor.insert_paragraph_before('')
    np.alignment = WD_ALIGN_PARAGRAPH.CENTER
    np.add_run().add_picture(path, width=Cm(15))

count = {'h1new': 0, 'h2': 0, 'h3': 0, 'para': 0, 'bullet': 0, 'table': 0, 'img': 0, 'para_intro': 0}
cursor = h3_1  # 游标段：新内容插在其后，cursor 前移

def ins_after(text='', style=None, size=12, bold_all=False):
    global cursor
    np = cursor.insert_paragraph_before(text if style else '', style=style)
    cursor._p.addnext(np._p)  # 移到游标之后
    if not style:
        add_text_runs(np, text, size=size, bold_all=bold_all)
    cursor = np
    return np

def ins_h1(text):
    global cursor
    np = cursor.insert_paragraph_before(text, style='Heading 1')
    cursor._p.addnext(np._p)
    cursor = np; count['h1new'] += 1

def ins_move(p):
    global cursor
    cursor._p.addnext(p._p)
    cursor = p

def ins_table(rows):
    global cursor
    t = d.add_table(rows=len(rows), cols=len(rows[0]))
    try: t.style = 'Table Grid'
    except Exception: pass
    for ri, row in enumerate(rows):
        for ci, cell in enumerate(row):
            if ci >= len(t.rows[ri].cells): continue
            c = t.cell(ri, ci); c.text = ''
            add_text_runs(c.paragraphs[0], cell, size=10.5, bold_all=(ri == 0))
    cursor._p.addnext(t._tbl)
    np = cursor.insert_paragraph_before('', style='Normal')
    cursor._p.addnext(np._p)
    cursor = np; count['table'] += 1

def ins_img(path):
    global cursor
    np = cursor.insert_paragraph_before('')
    np.alignment = WD_ALIGN_PARAGRAPH.CENTER
    np.add_run().add_picture(path, width=Cm(15))
    cursor._p.addnext(np._p)
    cursor = np; count['img'] += 1

PHOTO = {'马其瑞': os.path.abspath('交付材料/_assets/队照/mqr.jpg'),
         '孙雨瑶': os.path.abspath('交付材料/_assets/队照/syy.jpg'),
         '居欣月': os.path.abspath('交付材料/_assets/队照/jxy.jpg')}

def ins_team_table(rows):
    global cursor
    t = d.add_table(rows=len(rows), cols=4)
    try: t.style = 'Table Grid'
    except Exception: pass
    for ri, row in enumerate(rows):
        row = (row + ['','','',''])[:4]
        for ci in range(4):
            c = t.cell(ri, ci); c.text = ''
            para = c.paragraphs[0]
            if ci == 1 and ri > 0:  # 照片列
                name = row[0].split('队长')[0].split('2025')[0].strip()
                ph = PHOTO.get(name)
                if ph and os.path.exists(ph):
                    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    para.add_run().add_picture(ph, width=Cm(2.2))
            else:
                add_text_runs(para, row[ci], size=10.5, bold_all=(ri == 0))
    for ri, row in enumerate(rows):
        row = (row + ['','','',''])[:4]
        if ri > 0:
            name = row[0].split('队长')[0].split('2025')[0].strip()
            t.cell(ri, 1).width = Cm(2.8)
    # 列宽
    widths = [Cm(2.6), Cm(2.8), Cm(3.6), Cm(6.0)]
    for ri in range(len(t.rows)):
        for ci, w in enumerate(widths):
            t.cell(ri, ci).width = w
    cursor._p.addnext(t._tbl)
    np = cursor.insert_paragraph_before('', style='Normal')
    cursor._p.addnext(np._p)
    cursor = np; count['table'] += 1

for kind, val in elems:
    if kind == 'h1':
        if val.startswith('一、'):
            cursor = h3_1; continue
        if val.startswith('二、'):
            set_text(h1_ch2, '二、需求分析'); ins_move(h1_ch2); continue
        if val.startswith('八、'):
            set_text(h1_app, '八、附录'); ins_move(h1_app); continue
        ins_h1(val); continue
    if kind == 'h3':
        if val.startswith('（一）背景与意义'):
            ins_move(h2_bg); cursor = h2_bg; continue
        if val.startswith('（二）核心目标'):
            ins_move(h2_goal); cursor = h2_goal; continue
        ins_after(val, 'Heading 2'); count['h2'] += 1; continue
    if kind == 'h4':
        if val.startswith('1. 行业痛点'):
            ins_move(h3_1); cursor = h3_1; continue
        if val.startswith('2. 学科发展现状'):
            ins_move(h_2n); cursor = h_2n; continue
        ins_after(val, 'Heading 3'); count['h3'] += 1; continue
    if kind == 'para_intro':
        ins_after(val); count['para_intro'] += 1; continue
    if kind == 'para':
        ins_after(val); count['para'] += 1; continue
    if kind == 'bullet':
        np = ins_after('', style='Normal')
        add_text_runs(np, '• ' + val)
        np.paragraph_format.left_indent = Pt(24)
        count['bullet'] += 1; continue
    if kind == 'team_table':
        ins_team_table(val); continue
    if kind == 'table':
        ins_table(val); continue
    if kind == 'img':
        ins_img(val[1]); continue

d.save(OUT)
print('saved:', OUT, os.path.getsize(OUT))
