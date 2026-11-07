# -*- coding: utf-8 -*-
"""COM 后处理+导出：表格统一布局列宽（Word 原生）+ 赛题名替换 + 删浮动框 + 更新目录 + 导出 PDF"""
import win32com.client, os

src = os.path.abspath('交付材料/02_技术方案/模板工作_filled.docx')
pdf = os.path.abspath('交付材料/02_技术方案/模板工作_filled.pdf')
TEAM_MARK = '照片'  # 团队表表头第 2 格

app = win32com.client.Dispatch('Word.Application')
doc = app.Documents.Open(src)

# 1. 赛题名称占位替换
f = doc.Content.Find
f.Text = '（赛题名称）'
if f.Execute():
    f.Parent.Text = '（AI+学科交叉）'
    print('赛题名替换')

# 2. 删浮动提示框
for i in range(doc.Shapes.Count, 0, -1):
    try: doc.Shapes(i).Delete()
    except Exception: pass

# 3. 全部表格：固定布局 + 版心全宽 + 列宽分配（Word 原生 API，顺序无忧）
CM = 28.35  # 1cm≈28.35pt
for ti in range(1, doc.Tables.Count + 1):
    tbl = doc.Tables(ti)
    tbl.AutoFitBehavior(2)  # wdAutoFitFixed
    tbl.PreferredWidthType = 3  # wdPreferredWidthPoints
    tbl.PreferredWidth = 425.25  # 15cm
    tbl.Columns.PreferredWidthType = 3
    head = tbl.Cell(1, 1).Range.Text.strip()
    ncol = tbl.Columns.Count
    if TEAM_MARK in head:  # 团队照片表：成员/照片/专业/角色
        widths = [2.6, 3.0, 4.4, 5.0]
    elif ncol == 4:
        widths = [3.2, 2.2, 4.6, 5.0]
    elif ncol == 3:
        widths = [3.4, 5.0, 6.6]
    elif ncol == 2:
        widths = [5.0, 10.0]
    else:
        widths = None
    if widths:
        for ci in range(1, ncol + 1):
            tbl.Columns(ci).Width = widths[ci - 1] * 28.35  # cm→pt

# 4. 更新目录与域
for toc in doc.TablesOfContents: toc.Update()
doc.Fields.Update()

# 5. 导出
doc.Save()
doc.ExportAsFixedFormat(pdf, 17)
pages = doc.ComputeStatistics(2)
doc.Close(False); app.Quit()
print('PDF %.2fMB | %d 页' % (os.path.getsize(pdf) / 1048576, pages))
