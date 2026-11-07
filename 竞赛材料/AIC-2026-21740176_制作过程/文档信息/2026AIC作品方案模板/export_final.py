# -*- coding: utf-8 -*-
"""COM 终极后处理：删旧目录域+占位域 → 重建目录 → 表格布局 → 导出 PDF"""
import win32com.client, os

src = os.path.abspath('交付材料/02_技术方案/模板工作_filled.docx')
pdf = os.path.abspath('交付材料/02_技术方案/模板工作_filled.pdf')

app = win32com.client.Dispatch('Word.Application')
doc = app.Documents.Open(src)

# 1. 删除全部旧目录域（含损坏的缓存与嵌套域）
while doc.TablesOfContents.Count > 0:
    doc.TablesOfContents(1).Delete()
print('旧目录域删除')

# 2. 删除全部 MACROBUTTON 域（倒序遍历 main story Fields）
i = doc.Fields.Count
removed_f = 0
while i > 0:
    try:
        fld = doc.Fields(i)
        if 'MACROBUTTON' in fld.Code.Text:
            fld.Delete(); removed_f += 1
    except Exception: pass
    i -= 1
print('MACROBUTTON 域删除:', removed_f)

# 3. 正文文本级清理（占位/错误文本，Find 全局替换）
for txt in ['［单击键入正文］', '错误!未定义书签', '错误!未定义书签。']:
    r = doc.Content
    fr = r.Find
    fr.Text = txt
    fr.Replacement.Text = ''
    fr.Execute(Replace=2, Forward=True)

# 4. 找"目 录"标题段，段尾重建目录域（Heading 1-3）
rng = doc.Content
fr = rng.Find
fr.Text = '目  录'
found = fr.Execute()
if not found:
    fr.Text = '目 录'
    found = fr.Execute()
print('找到目录标题:', bool(found))
if found:
    rng.Collapse(0)  # wdCollapseEnd：收缩到标题段末
    # 移过段落标记
    rng.Move(4, 1)  # wdParagraph=4, 移 1 段
    doc.TablesOfContents.Add(
        Range=rng, UseHeadingStyles=True,
        UpperHeadingLevel=1, LowerHeadingLevel=3,
        UseFieldsStyle=False, UseHyperlinks=True)

# 5. 表格统一布局：固定+版心全宽+列宽分配
CM = 28.35
for ti in range(1, doc.Tables.Count + 1):
    tbl = doc.Tables(ti)
    tbl.AutoFitBehavior(2)  # wdAutoFitFixed
    tbl.PreferredWidthType = 3
    tbl.PreferredWidth = 425.25  # 15cm
    tbl.Columns.PreferredWidthType = 3
    head = tbl.Cell(1, 1).Range.Text.strip()
    ncol = tbl.Columns.Count
    if '照片' in head:
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
            tbl.Columns(ci).Width = widths[ci - 1] * CM

# 6. 赛题名替换
f = doc.Content.Find
f.Text = '（赛题名称）'
if f.Execute(): f.Parent.Text = '（AI+学科交叉）'

# 7. 删浮动框
for i in range(doc.Shapes.Count, 0, -1):
    try: doc.Shapes(i).Delete()
    except Exception: pass

# 8. 最终更新域并导出
doc.Fields.Update()
doc.Save()
doc.ExportAsFixedFormat(pdf, 17)
pages = doc.ComputeStatistics(2)
doc.Close(False); app.Quit()
print('PDF %.2fMB | %d 页' % (os.path.getsize(pdf) / 1048576, pages))
