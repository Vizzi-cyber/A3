# -*- coding: utf-8 -*-
"""md → LaTeX（按 AIC 官方模板规范）→ xelatex 编译 → PDF
模板规范：宋体小四正文/一级三号粗体/二级四号粗体/三级小四粗体/单倍行距/
页边距上下2.5左右3.0cm/页眉 AIC+大赛名/页脚页码/A4 纵向
"""
import re, os, shutil, subprocess

BASE = os.path.dirname(os.path.abspath(__file__))
MD = os.path.abspath('文档信息/AIC技术方案_LearnLab.md')
WORK = os.path.abspath('交付材料/02_技术方案/latex')
OUT_PDF = os.path.abspath('交付材料/1_技术方案.pdf')

# 图片复制到英文路径
os.makedirs(WORK, exist_ok=True)
for f in ['mqr.jpg', 'syy.jpg', 'jxy.jpg']:
    shutil.copy(os.path.abspath(f'交付材料/_assets/队照/{f}'), os.path.join(WORK, f))
shutil.copy(os.path.abspath('交付材料/_assets/架构图.png'), os.path.join(WORK, 'arch.png'))

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
    if m: elems.append(('img', (m.group(1), 'arch.png'))); i += 1; continue
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
    m_ol = re.match(r'^(\d+)\.\s+(.*)$', ln.strip())
    if m_ol:
        elems.append(('olitem', (m_ol.group(1), m_ol.group(2).strip()))); i += 1; continue
    elems.append(('para', ln.strip())); i += 1
print('元素流:', len(elems))

# ---------- LaTeX 转义与内联 ----------
def tex_escape(s):
    s = s.replace('\\', r'\textbackslash{}')
    for ch in '&%$#_{}':
        s = s.replace(ch, '\\' + ch)
    s = s.replace('~', r'\textasciitilde{}')
    s = s.replace('^', r'\textasciicircum{}')
    return s

def tex_inline(s):
    # 直引号成对转中文引号（XeLaTeX 西文字体把 " 渲染成两个右引号）
    s = re.sub(r'"([^"]*?)"', '\u201c\\1\u201d', s)
    out = []
    for part in re.split(r'(\*\*.+?\*\*|\*[^*]+?\*)', s):
        if not part: continue
        b = part.startswith('**')
        it = (not b) and part.startswith('*') and part.endswith('*') and len(part) > 2
        clean = part.strip('*') if (b or it) else part
        for seg in re.split(r'(`[^`]+`)', clean):
            if not seg: continue
            code = seg.startswith('`')
            body = seg.strip('`') if code else seg
            body = tex_escape(body)
            if code: body = r'\texttt{' + body + '}'
            if it: body = r'\textit{' + body + '}'
            if b: body = r'\textbf{' + body + '}'
            out.append(body)
    return ''.join(out)

# ---------- 生成 tex ----------
TEX = r'''\documentclass[zihao=-4,a4paper,UTF8,fontset=windows]{ctexart}
\usepackage[top=2.5cm,bottom=2.5cm,left=3cm,right=3cm]{geometry}
\usepackage{fancyhdr}
\usepackage{longtable}
\usepackage{array}
\usepackage{graphicx}
\usepackage{xcolor}
\usepackage{enumitem}
\definecolor{aicblue}{RGB}{18,86,184}
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\includegraphics[height=0.55cm]{aic_logo.png}}
\fancyhead[R]{\zihao{-5} 2026 第八届全球校园人工智能算法精英大赛}
\renewcommand{\headrulewidth}{0.5pt}
\fancyfoot[C]{\zihao{5}\thepage}
% 封面页样式：页眉同正文（官方 logo + 大赛名），页脚无页码（对照官方模板封面）
\fancypagestyle{cover}{%
  \fancyhf{}%
  \fancyhead[L]{\includegraphics[height=0.55cm]{aic_logo.png}}%
  \fancyhead[R]{\zihao{-5} 2026 第八届全球校园人工智能算法精英大赛}%
  \renewcommand{\headrulewidth}{0.5pt}%
  \fancyfoot[C]{}%
}
% 列表符号用中文间隔号（降 AI 味，不用英文圆点）
\renewcommand{\labelitemi}{\textperiodcentered}
\renewcommand{\labelitemii}{--}
% 标题层级：一级三号粗体 / 二级四号粗体 / 三级小四粗体（模板规范）
\setcounter{secnumdepth}{-1}
\usepackage{titlesec}
% 标题字体：黑体承担粗体（Windows 中文惯例），字号按模板 三号/四号/小四
\titleformat{\section}{\heiti\zihao{3}}{}{0em}{}
\titleformat{\subsection}{\heiti\zihao{4}}{}{0em}{}
\titleformat{\subsubsection}{\heiti\zihao{-4}}{}{0em}{}
\titlespacing*{\section}{0pt}{1.2em}{0.6em}
\titlespacing*{\subsection}{0pt}{0.8em}{0.4em}
\titlespacing*{\subsubsection}{0pt}{0.6em}{0.3em}
% 西文 Times New Roman（fontspec）
\usepackage{fontspec}
\setmainfont{Times New Roman}
% 行距：单倍（模板要求）
\linespread{1.0}
\setlength{\parindent}{2em}
% 标题后的首段也缩进（中文排版惯例，模板正文全部段首空两格）
\usepackage{indentfirst}
\setlength{\parskip}{0pt}
\renewcommand{\arraystretch}{1.15}
\begin{document}
% ===== 封面 =====（对照官方模板：标题群上 1/4 起、团队信息中部左对齐下划线、日期底部、无页码）
\begin{titlepage}
\thispagestyle{cover}
\vspace*{2.8cm}
\begin{center}
{\bfseries\zihao{1} 2026 年第八届}\\[0.8em]
{\bfseries\zihao{1} 全球校园人工智能算法精英大赛}\\[3em]
{\bfseries\zihao{3} 算法创新赛}\\[1em]
{\bfseries\zihao{3}（AI+学科交叉）}\\[1em]
{\bfseries\zihao{3} 技术报告}\\
\end{center}
\vspace{5em}
\begin{flushleft}
\hspace*{4em}\zihao{4}
团队名称：\underline{\makebox[7cm][c]{一起搞事情}}\\[0.8em]
\hspace*{4em}参赛编号：\underline{\makebox[7cm][c]{AIC-2026-21740176}}\\[0.8em]
\hspace*{4em}作品名称：\underline{\makebox[7cm][c]{LearnLab 跨学科智能学习平台}}\\
\end{flushleft}
\vfill
\begin{center}\zihao{4} 日期：2026 年 10 月\end{center}
\vspace*{1.5cm}
\end{titlepage}
\setcounter{page}{1}
% ===== 目录 =====
\renewcommand{\contentsname}{目\quad 录}
\setcounter{tocdepth}{3}
\tableofcontents
\newpage
% ===== 作品简介 =====
\section*{作品简介}
\addcontentsline{toc}{section}{作品简介}
'''

# ---------- 元素流转 LaTeX ----------
cur = []
for kind, val in elems:
    if kind == 'para_intro':
        TEX += tex_inline(val) + '\n\n'; continue
    if kind == 'h1':
        TEX += '\\section{' + tex_inline(val) + '}\n'; continue
    if kind == 'h2':
        TEX += '\\subsection{' + tex_inline(val) + '}\n'; continue
    if kind == 'h3':
        TEX += '\\subsubsection{' + tex_inline(val) + '}\n'; continue
    if kind == 'para':
        TEX += tex_inline(val) + '\n\n'; continue
    if kind == 'bullet':
        TEX += '\\begin{itemize}[leftmargin=2em,itemsep=0pt,topsep=0pt]\n\\item ' + tex_inline(val) + '\n\\end{itemize}\n'; continue
    if kind == 'olitem':
        num, otxt = val
        TEX += '\n\n\\noindent\\hangindent=2em ' + num + '.~' + tex_inline(otxt) + '\n\n'; continue
    if kind == 'table':
        rows = val
        ncol = max(len(r) for r in rows)
        if ncol == 4:
            colspec = '|p{2.6cm}|p{2.6cm}|p{4.2cm}|p{4.6cm}|'
        elif ncol == 3:
            colspec = '|p{3.2cm}|p{4.8cm}|p{6.4cm}|'
        elif ncol == 5:
            colspec = '|p{2.2cm}|p{2.2cm}|p{2.6cm}|p{3.4cm}|p{3.0cm}|'
        else:
            colspec = '|' + '|'.join([f'p{{{round(15.0/ncol,2)}cm}}'] * ncol) + '|'
        TEX += '\\begin{longtable}{' + colspec + '}\n\\hline\n'
        for ri, row in enumerate(rows):
            cells = []
            for ci in range(ncol):
                cell = row[ci] if ci < len(row) else ''
                ct = tex_inline(cell)
                if ri == 0: ct = '\\textbf{' + ct + '}'
                cells.append(ct)
            TEX += ' & '.join(cells) + r' \\ \hline' + '\n'
        TEX += '\\end{longtable}\n'; continue
    if kind == 'team_table':
        rows = val
        TEX += '\\begin{longtable}{|p{2.6cm}|p{3.0cm}|p{4.4cm}|p{5.0cm}|}\n\\hline\n'
        TEX += r'\textbf{成员} & \textbf{照片} & \textbf{专业方向} & \textbf{角色定位} \\ \hline' + '\n'
        for row in rows:
            row = (row + ['', '', '', ''])[:4]
            name = row[0].split('队长')[0].split('2025')[0].strip()
            PHOTO_FILE = {'马其瑞': 'mqr.jpg', '孙雨瑶': 'syy.jpg', '居欣月': 'jxy.jpg'}
            ph = os.path.join(WORK.replace('latex',''), 'latex', name + '.jpg')
            ph2 = os.path.join('交付材料/02_技术方案/latex', name + '.jpg')
            ph = ph2 if os.path.exists(ph2) else ph
            photo_tex = (r'\includegraphics[height=3.2cm]{' + PHOTO_FILE.get(name, '') + '}') if PHOTO_FILE.get(name) else ''
            c0 = tex_inline(re.sub(r'\s+', ' ', row[0].replace('·', ' '))); c2 = tex_inline(row[2]); c3 = tex_inline(row[3])
            TEX += c0 + ' & ' + photo_tex + ' & ' + c2 + ' & ' + c3 + r' \\ \hline' + '\n'
        TEX += '\\end{longtable}\n'; continue
    if kind == 'img':
        TEX += '\\begin{center}\\includegraphics[width=15cm]{arch.png}\\end{center}\n'; continue

TEX += '\\end{document}\n'

os.makedirs(WORK, exist_ok=True)
tex_path = os.path.join(WORK, 'main.tex')
open(tex_path, 'w', encoding='utf-8').write(TEX)
print('tex 生成:', tex_path, len(TEX), '字符')
