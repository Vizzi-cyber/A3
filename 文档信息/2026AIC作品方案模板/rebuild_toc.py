# -*- coding: utf-8 -*-
"""COM 重建目录域：删残域 → 清占位 → 定位目录标题 → 新建 TOC → 表格布局 → 导出"""
import win32com.client, os

src = os.path.abspath('交付材料/02_技术方案/模板工作_filled.docx')
pdf = os.path.abspath('交付材料/02_技术方案/模板工作_filled.pdf')

app = win32com.client.Dispatch('Word.Application')
doc = app.Documents.Open(src)

# 1. 删全部残域（HYPERLINK/PAGEREF/MACROBUTTON 倒序）
i = doc.Fields.Count
removed = 0
while i > 0:
    try:
        doc.Fields(i).Delete(); removed += 1
    except Exception: pass
    i -= 1
print('残域删除:', removed)

# 2. 文本级清理（域代码字面/错误书签/占位）
for txt in ['TOC \\o "1-3"', 'TOC \\h \\z \\u', '［单击键入正文］',
            '错误!未定义书签', '错误!未定义书签。']:
    r = doc.Content
    fr = r.Find
    fr.Text = txt
    fr.Replacement.Text = ''
    if fr.Execute(): fr.Execute(Replace=2, Forward=True)

# 3. 定位"目 录"标题段（规范化匹配）
target = None
for para in doc.Paragraphs:
    t = para.Range.Text.strip().replace('　', '').replace(' ', '')
    if t == '目录':
        target = para
        break
print('找到目录标题段:', bool(target))

# 4. 段末重建目录域（Heading 1-3）
if target is not None:
    rng = target.Range
    rng.Collapse(0)   # wdCollapseEnd
    rng.Move(4, -1)   # wdParagraph 回退段落标记，TOC 插段内末尾
    doc.TablesOfContents.Add(
        Range=rng, UseHeadingStyles=True,
        UpperHeadingLevel=1, LowerHeadingLevel=3,
        UseFieldsStyle=False, UseHyperlinks=True)

# 5. 表格统一布局
CM = 28.35
for ti in range(1, doc.Tables.Count + 1):
    tbl = doc.Tables(ti)
    tbl.AutoFitBehavior(2)
    tbl.PreferredWidthType = 3
    tbl.PreferredWidth = 425.25
    tbl.Columns.PreferredWidthType = 3
    head = tbl.Cell(1, 1).Range.Text.strip()
    ncol = tbl.Columns.Count
    if '照片' in head: widths = [2.6, 3.0, 4.4, 5.0]
    elif ncol == 4: widths = [3.2, 2.2, 4.6, 5.0]
    elif ncol == 3: widths = [3.4, 5.0, 6.6]
    elif ncol == 2: widths = [5.0, 10.0]
    else: widths = None
    if widths:
        for ci in range(1, ncol + 1):
            tbl.Columns(ci).Width = widths[ci - 1] * CM

# 6. 赛题名替换+删浮动框
f = doc.Content.Find
f.Text = '（赛题名称）'
if f.Execute(): f.Parent.Text = '（AI+学科交叉）'
for i in range(doc.Shapes.Count, 0, -1):
    try: doc.Shapes(i).Delete()
    except Exception: pass

# 7. 更新域并导出
doc.Fields.Update()
for toc in doc.TablesOfContents: toc.Update()
doc.Save()
doc.ExportAsFixedFormat(pdf, 17)
pages = doc.ComputeStatistics(2)
doc.Close(False); app.Quit()
print('PDF %.2fMB | %d 页' % (os.path.getsize(pdf) / 1048576, pages))
