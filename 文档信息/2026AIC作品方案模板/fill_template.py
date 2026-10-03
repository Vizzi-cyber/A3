# -*- coding: utf-8 -*-
"""官方模板 docx 填充（终版）：封面填值 + 骨架改名 + 占位清理 + 纯追加内容 + 目录尾空段清理"""
import re, os
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.text.paragraph import Paragraph

BASE = os.path.dirname(os.path.abspath(__file__))
MD = os.path.join(BASE, '..', 'AIC技术方案_LearnLab.md')
DOCX = os.path.abspath('交付材料/02_技术方案/模板工作.docx')
OUT = os.path.abspath('交付材料/02_技术方案/模板工作_filled.docx')
IMG = os.path.abspath('交付材料/_assets/架构图.png')
PHOTO_FILE = {'马其瑞': 'mqr.jpg', '孙雨瑶': 'syy.jpg', '居欣月': 'jxy.jpg'}
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

def add_text_runs(para, text, size=12, bold_all=False):
    for part in re.split(r'(\*\*.*?\*\*)', text):
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
            r._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

def fmt_para(p, indent=True):
    pf = p.paragraph_format
    pf.line_spacing = 1.0
    pf.space_before = Pt(0); pf.space_after = Pt(0)
    if indent: pf.first_line_indent = Pt(24)
    pPr = p._p.get_or_add_pPr()
    if pPr.find(qn('w:snapToGrid')) is None:
        snap = pPr.makeelement(qn('w:snapToGrid'), {qn('w:val'): '0'})
        pPr.insert(0, snap)

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

DEL_KEYS = ['提示信息', '不用此信息时', '（鼠标移到此框', '字体:宋体', '目录标题:二号', '一级标题:三号',
            '二级标题:四号', '三级标题:小四', '正文:小四号', '行距:单倍行距', '页边距:上:', '页眉:1.5',
            '页脚:1.5', '纸型:A4', '（五）其他问题', '中国学术期刊（光盘版）', '左:3厘米', '装订线',
            '单击键入正文', 'AAAAAAAA', '错误!未定义书签']
SKELETON_TEXTS = ['一、项目概述', '二、需求分析', '八、附录', '（一）项目背景与意义',
                  '（二）核心目标与赛题方向定位', '1. 行业痛点', '2. 学科发展现状与行业需求',
                  '二、AAAAAAAA', '三、附录', '（二）赛题方向定位', '1.', '2.']
removed = 0
for p in list(body.iter(qn('w:p'))):
    t = ptext_all(p).strip()
    hit = t in SKELETON_TEXTS or any(k in t for k in DEL_KEYS) or t == '2.' or t == '1.'
    if hit:
        p.getparent().remove(p); removed += 1
print('删除骨架/占位/提示段:', removed)

# ---------- 4. toc 样式压缩（防目录溢出空白页）----------
for sn in ('toc 1', 'toc 2', 'toc 3'):
    try:
        st = d.styles[sn]
        st.font.size = Pt(10.5)
        pf = st.paragraph_format
        pf.line_spacing = Pt(11.8)
        pf.space_before = Pt(0); pf.space_after = Pt(0)
    except KeyError: pass

# ---------- 5. 内容插入工具（文尾追加，顺序天然正确）----------
count = {'h1': 0, 'h2': 0, 'h3': 0, 'para': 0, 'bullet': 0, 'table': 0, 'img': 0, 'intro': 0}

def H(level, text):
    d.add_paragraph(text, style=f'Heading {level}')
    count[f'h{level}'] += 1

def P(text):
    p = d.add_paragraph('', style='Normal')
    add_text_runs(p, text)
    fmt_para(p, True)
    count['para'] += 1

def B(text):
    p = d.add_paragraph('', style='Normal')
    add_text_runs(p, '• ' + text)
    p.paragraph_format.left_indent = Pt(24)
    p.paragraph_format.first_line_indent = Pt(0)
    fmt_para(p, False)
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

def TEAM(rows):
    # 4 列表格：成员 / 照片（格内居中 2.4cm）/ 专业方向 / 角色定位
    t = d.add_table(rows=len(rows), cols=4)
    try: t.style = 'Table Grid'
    except Exception: pass
    t.autofit = False
    widths = [Cm(3.2), Cm(3.0), Cm(4.0), Cm(4.8)]
    grid = t._tbl.find(qn('w:tblGrid'))
    if grid is not None:
        for gc, w in zip(grid.findall(qn('w:gridCol')), widths):
            gc.set(qn('w:w'), str(int(w.twips)))
    for ri, row in enumerate(rows):
        row = (row + ['', '', '', ''])[:4]
        member = row[0].replace('·', ' ').replace('・', ' ').replace('  ', ' ')
        for ci in range(4):
            c = t.cell(ri, ci); c.text = ''; c.width = widths[ci]
            para = c.paragraphs[0]
            para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            pf = para.paragraph_format
            pf.line_spacing = 1.0
            pf.space_before = Pt(1); pf.space_after = Pt(1)
            pPr = para._p.get_or_add_pPr()
            if pPr.find(qn('w:snapToGrid')) is None:
                snap = pPr.makeelement(qn('w:snapToGrid'), {qn('w:val'): '0'})
                pPr.insert(0, snap)
            if ci == 1 and ri > 0:
                name = member.split(' ')[0].strip()
                ph = os.path.join(os.path.dirname(os.path.abspath(MD.replace(os.sep + '文档信息' + os.sep, os.sep + '交付材料' + os.sep))), '02_技术方案', 'latex', PHOTO_FILE.get(name, ''))
                if os.path.exists(ph):
                    para.add_run().add_picture(ph, height=Cm(2.4))
                continue
            if ri == 0:
                r = para.add_run(row[ci] if ci != 1 else ''); r.font.bold = True
                r.font.name = '黑体'; r.font.size = Pt(10.5)
                r._element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')
            else:
                add_text_runs(para, member if ci == 0 else row[ci], size=10.5)
    count['table'] += 1

def IMG_ADD(path):
    p = d.add_paragraph('')
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(path, width=Cm(15))
    count['img'] += 1

# ---------- 6. 按流追加全部内容 ----------
for kind, val in elems:
    if kind == 'para_intro': continue  # 简介单独处理
    if kind == 'h1':
        num = val.split('、')[0]
        cn = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8}.get(num, 1)
        H(1 if cn < 8 else 1, val); continue
    if kind == 'h2':
        H(2, val); continue
    if kind == 'h3':
        H(3, val); continue
    if kind == 'para':
        P(val); continue
    if kind == 'bullet':
        B(val); continue
    if kind == 'table':
        T(val); continue
    if kind == 'team_table':
        TEAM(val); continue
    if kind == 'img':
        IMG_ADD(val[1]); continue

# ---------- 7. 简介正文插到"作品简介"标题后 ----------
t_title = None
for p in body.iter(qn('w:p')):
    if ptext(p).strip() == '作品简介': t_title = p; break
assert t_title is not None, '作品简介标题未找到'
intro = [v for k, v in elems if k == 'para_intro'][0]
np = t_title.makeelement(qn('w:p'), {})
t_title.addnext(np)
para_obj = Paragraph(np, t_title.getparent())
add_text_runs(para_obj, intro)
fmt_para(para_obj, True)
count['intro'] = 1

# ---------- 8. 全文空段清理（排除表格内与分节段，防空白页）----------
def in_table(el):
    anc = el.getparent()
    while anc is not None:
        if anc.tag == qn('w:tbl'): return True
        anc = anc.getparent()
    return False

removed_n = 0
for p in list(body.iter(qn('w:p'))):
    if in_table(p): continue
    pPr = p.find(qn('w:pPr'))
    if pPr is not None and pPr.find(qn('w:sectPr')) is not None: continue
    if ptext(p).strip() == '':
        p.getparent().remove(p); removed_n += 1
print('全文空段清理:', removed_n)

d.save(OUT)
print('saved:', OUT, os.path.getsize(OUT))
print('统计:', count)
