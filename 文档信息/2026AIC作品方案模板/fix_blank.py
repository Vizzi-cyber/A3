# -*- coding: utf-8 -*-
"""COM 修复：删除目录节尾到简介标题之间的空段/分节段（节合并消除空白页），重导出"""
import win32com.client, os

src = os.path.abspath('交付材料/02_技术方案/模板工作_filled.docx')
pdf = os.path.abspath('交付材料/02_技术方案/模板工作_filled.pdf')

app = win32com.client.Dispatch('Word.Application')
doc = app.Documents.Open(src)

paras = list(doc.Paragraphs)
intro_i = last_i = None
for i, p in enumerate(paras):
    t = p.Range.Text.strip()
    if intro_i is None and t == '作品简介':
        intro_i = i
    if '知识产权、学术伦理与其他材料' in t:
        last_i = i
print('目录尾条目 idx:', last_i, '| 简介 Title idx:', intro_i)
if last_i is None or intro_i is None:
    print('定位失败，退出'); doc.Close(False); app.Quit(); exit(1)

# 倒序删除区间内段落（不含两端）：空段与分节符段一并删（节合并）
n = 0
for i in range(intro_i - 1, last_i, -1):
    try:
        paras[i].Range.Delete(); n += 1
    except Exception: pass
print('删除区间段数:', n)

# 重导出
for toc in doc.TablesOfContents: toc.Update()
doc.Fields.Update()
doc.Save()
doc.ExportAsFixedFormat(pdf, 17)
pages = doc.ComputeStatistics(2)
blank = 0
for p in doc.Paragraphs: pass
doc.Close(False); app.Quit()

import pymupdf
d = pymupdf.open(pdf)
print('终验: %d 页 %.2fMB' % (len(d), os.path.getsize(pdf) / 1048576))
for i, p in enumerate(d):
    t = p.get_text().strip()
    if len(t) < 60 and i > 0: print('  近空页:', i + 1, len(t))
print('团队照片表页:', [i+1 for i,p in enumerate(d) if '专业方向' in p.get_text() and '队长' in p.get_text() and i > 5])
