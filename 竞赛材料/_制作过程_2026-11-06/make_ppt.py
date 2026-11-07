# -*- coding: utf-8 -*-
"""生成 AI+X 校内赛答辩 PPT（16:9，15 页）"""
import os
from PIL import Image
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

BASE = r"C:\Users\Vizzi\Desktop\项目汇总\A3\竞赛材料\_制作过程_2026-11-06\报告"
OUT = r"C:\Users\Vizzi\Desktop\项目汇总\A3\竞赛材料\_制作过程_2026-11-06\答辩PPT.pptx"

NAVY = RGBColor(0x0E, 0x2A, 0x47)
BLUE = RGBColor(0x12, 0x56, 0xB8)
LIGHT = RGBColor(0xF4, 0xF6, 0xF9)
BORDER = RGBColor(0xD9, 0xDF, 0xE8)
GRAY = RGBColor(0x55, 0x61, 0x70)
LIGHTGRAY = RGBColor(0x8A, 0x95, 0xA3)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
ORANGE = RGBColor(0xC2, 0x5A, 0x0B)
TEAL = RGBColor(0x0F, 0x76, 0x6E)
FONT = "微软雅黑"

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]


def new_slide():
    s = prs.slides.add_slide(BLANK)
    bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = WHITE
    bg.line.fill.background()
    bg.shadow.inherit = False
    return s


def rect(s, x, y, w, h, fill=None, line=None, radius=None, line_w=1):
    shape_type = MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE
    sh = s.shapes.add_shape(shape_type, Inches(x), Inches(y), Inches(w), Inches(h))
    if fill is None:
        sh.fill.background()
    else:
        sh.fill.solid()
        sh.fill.fore_color.rgb = fill
    if line is None:
        sh.line.fill.background()
    else:
        sh.line.color.rgb = line
        sh.line.width = Pt(line_w)
    sh.shadow.inherit = False
    if radius:
        try:
            sh.adjustments[0] = radius
        except Exception:
            pass
    return sh


def tb(s, x, y, w, h, paras, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP,
       space_after=6, line_spacing=1.25, margins=(0, 0, 0, 0)):
    box = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = Inches(margins[0])
    tf.margin_right = Inches(margins[1])
    tf.margin_top = Inches(margins[2])
    tf.margin_bottom = Inches(margins[3])
    if isinstance(paras, str):
        paras = [(paras, 14, False, GRAY)]
    for i, item in enumerate(paras):
        text, size, bold, color = item[:4]
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = line_spacing
        p.space_after = Pt(space_after)
        run = p.add_run()
        run.text = text
        run.font.size = Pt(size)
        run.font.bold = bold
        run.font.color.rgb = color
        run.font.name = FONT
        try:
            run.font._element.set("altLang", "zh-CN")
        except Exception:
            pass
    return box


def header(s, title, subtitle=None, num=None):
    tb(s, 0.7, 0.32, 8.6, 0.3, [("AI+X 跨学科智能创新应用  ·  LearnLab", 9.5, False, LIGHTGRAY)])
    tb(s, 0.7, 0.62, 11.9, 0.6, [(title, 27, True, NAVY)])
    rect(s, 0.7, 1.18, 0.85, 0.045, fill=BLUE)
    if subtitle:
        tb(s, 0.7, 1.28, 11.9, 0.35, [(subtitle, 12, False, GRAY)])
    # 页脚
    rect(s, 0.7, 7.03, 11.93, 0.015, fill=BORDER)
    tb(s, 0.7, 7.12, 6.0, 0.25, [("LearnLab  ·  一起搞事情", 8.5, False, LIGHTGRAY)])
    if num is not None:
        tb(s, 11.4, 7.12, 1.23, 0.25, [("%02d" % num, 9, False, LIGHTGRAY)], align=PP_ALIGN.RIGHT)


def fit_pic(s, name, x, y, w, h):
    path = os.path.join(BASE, name)
    iw, ih = Image.open(path).size
    scale = min(w / iw, h / ih)
    pw, ph = iw * scale, ih * scale
    s.shapes.add_picture(path, Inches(x + (w - pw) / 2), Inches(y + (h - ph) / 2),
                         Inches(pw), Inches(ph))


def arrow(s, x1, y1, x2, y2, color=BLUE, width=1.5):
    from pptx.enum.shapes import MSO_CONNECTOR
    from pptx.oxml.ns import qn
    conn = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1),
                                  Inches(x2), Inches(y2))
    conn.line.color.rgb = color
    conn.line.width = Pt(width)
    ln = conn.line._get_or_add_ln()
    tail = ln.makeelement(qn('a:tailEnd'), {'type': 'triangle', 'w': 'med', 'len': 'med'})
    ln.append(tail)


def card(s, x, y, w, h, head, body, head_color=NAVY, fill=LIGHT, head_size=12, body_size=11):
    rect(s, x, y, w, h, fill=fill, line=BORDER, radius=0.06)
    tb(s, x + 0.22, y + 0.16, w - 0.44, 0.3, [(head, head_size, True, head_color)])
    tb(s, x + 0.22, y + 0.52, w - 0.44, h - 0.62,
       [(body, body_size, False, GRAY)], line_spacing=1.3, space_after=4)


def stat(s, x, y, w, h, value, label, color=BLUE, vsize=30):
    rect(s, x, y, w, h, fill=WHITE, line=BORDER, radius=0.05)
    tb(s, x + 0.2, y + 0.12, w - 0.4, 0.55, [(value, vsize, True, color)])
    tb(s, x + 0.2, y + 0.12 + 0.52, w - 0.4, h - 0.62,
       [(label, 9.5, False, GRAY)], line_spacing=1.15)


def bullets(s, x, y, w, items, size=12.5, lead_color=NAVY, gap=0.06, line_spacing=1.28):
    paras = []
    for lead, body in items:
        if body:
            paras.append(("•  " + lead + "  " + body, size, False, GRAY))
        else:
            paras.append(("•  " + lead, size, False, GRAY))
    return tb(s, x, y, w, 4.8, paras, line_spacing=line_spacing, space_after=10)


# ========== 01 封面 ==========
s = new_slide()
rect(s, 0, 0, 13.333, 7.5, fill=NAVY)
rect(s, 0, 0, 13.333, 0.12, fill=BLUE)
tb(s, 0.95, 0.85, 11.5, 0.3,
   [("2026 南京工业大学第七届机器人大赛   ·   “AI+X”跨学科智能创新应用", 11, False, RGBColor(0xB9, 0xC6, 0xD8))])
rect(s, 0.95, 1.75, 0.09, 3.05, fill=BLUE)
tb(s, 1.3, 1.62, 10.8, 0.9, [("LearnLab", 48, True, WHITE)])
tb(s, 1.32, 2.55, 10.8, 0.6, [("跨学科智能学习平台", 30, True, WHITE)])
tb(s, 1.35, 3.25, 10.6, 0.5,
   [("12 个教育智能体  ×  五层教育算法闭环  ×  浏览器端电路实验", 13.5, False, RGBColor(0xB9, 0xC6, 0xD8))])
rect(s, 0.95, 5.95, 11.4, 0.015, fill=RGBColor(0x3C, 0x53, 0x6E))
tb(s, 0.95, 6.15, 11.4, 0.9, [
    ("一起搞事情  ｜  马其瑞（队长，电子信息工程）· 孙雨瑶（数据科学与大数据技术）· 居欣月（遥感科学与技术）", 10.5, False, WHITE),
    ("2026 年 11 月  ·  www.dreamlast.cn", 9.5, False, RGBColor(0x8F, 0xA3, 0xBC)),
], space_after=6)

# ========== 02 三问速览 ==========
s = new_slide()
header(s, "三个问题，一页回答", "竞赛补充说明的核心：发现了什么问题、AI 为什么能解决、创造了什么新方案", 2)
card(s, 0.7, 1.75, 3.85, 4.15, "① 发现的问题",
     "同一门课两种基础，却共用一份教案、一组练习\n\n"
     "实验设备与开放时间受限，接线错误有烧件成本\n\n"
     "C 语言、电路、嵌入式各教各的，链路断开\n\n"
     "教师学情靠期中期末成绩，上百人无法逐人分析\n\n"
     "四类学习环节的 9 条痛点，均无现成手段承接", body_size=10.5)
card(s, 4.75, 1.75, 3.85, 4.15, "② AI 为什么能解决",
     "知识追踪与自适应算法：把“会什么、下一步学什么”算出来\n\n"
     "大模型：把“为什么错、怎么改”讲成学生听得懂的话\n\n"
     "多智能体：把备课、辅导、纠错、协作串成自动流程\n\n"
     "浏览器数值计算：把实验搬到零成本虚拟环境\n\n"
     "知识图谱：把三门课的知识关系建模成图，支撑跨课程编排", body_size=10.5)
card(s, 8.8, 1.75, 3.85, 4.15, "③ 创造的新方案",
     "五层算法闭环（测量→建模→记忆→决策→解释）接入 5 个真实入口\n\n"
     "ADPP 自适应 DAG 路径，9 条跨课程关联编排学习顺序\n\n"
     "MNA + RK4 电路仿真叠加 AI 故障诊断\n\n"
     "统一错误诊断入口贯通三门课，诊断结论回写画像\n\n"
     "教师端：实时学情 + 班级对比 + 试点报告一键导出", body_size=10.5)
rect(s, 0.7, 6.1, 11.95, 0.7, fill=RGBColor(0xEC, 0xF2, 0xFB), line=BORDER, radius=0.06)
tb(s, 0.95, 6.22, 11.5, 0.45,
   [("作品定位：L2 高代码 → L3 创新研发（算法与系统自研并上线）　｜　X 能力：问题发现 · 产品设计 · 展示表达", 11, True, BLUE)])

# ========== 03 问题一 ==========
s = new_slide()
header(s, "问题一：一名老师，一百多种学情", "统一教案 + 统一练习，是当前课堂的默认解，但它对两端的学生都不合适", 3)
bullets(s, 0.7, 1.75, 6.4, [
    ("同一份教案。", "有基础的学生在“炒冷饭”，零基础的学生在追赶，两头都不舒服。"),
    ("传统 LMS 只做分发。", "超星、智慧树把资料挂到网上，不做个性化推荐，也不回答“下一步学什么”。"),
    ("一对一的成本不可规模化。", "Bloom（1984）的 2 Sigma 结论与 VanLehn（2011）的元分析都指向同一件事：效果成立，成本不成立。"),
], size=12.5)
stat(s, 7.5, 1.75, 5.1, 1.35, "60%", "试点前测中学生自陈“知识点零散、不成体系”")
stat(s, 7.5, 3.25, 5.1, 1.35, "1 : 100+", "一名教师面对的学生数量，逐人规划不现实")
stat(s, 7.5, 4.75, 5.1, 1.35, "≈ 2σ", "一对一辅导的成绩增益（Bloom, 1984）")
card(s, 0.7, 4.55, 6.4, 1.4, "为什么必须用 AI",
     "静态目录、题库、LMS 只能“把内容发出去”；个性化路径、即时答疑、学情分析必须由算法承担。",
     head_color=BLUE, head_size=11, body_size=10.5)
rect(s, 0.7, 6.15, 11.95, 0.62, fill=LIGHT, line=BORDER, radius=0.06)
tb(s, 0.95, 6.27, 11.6, 0.4,
   [("要解的不是“内容不够”，而是“效果与成本不可兼得”——这正是算法要接手的部分。", 11, True, NAVY)])

# ========== 04 问题二 ==========
s = new_slide()
header(s, "问题二：实验受设备与成本约束", "电路、嵌入式离不开动手，但真实实验室的时间、设备与试错成本都是刚性约束", 4)
bullets(s, 0.7, 1.75, 6.2, [
    ("排队两小时，上手十分钟。", "实验室有开放时间，设备数量有限，想多练几遍排不上。"),
    ("接错线可能烧件。", "硬件实验的试错有真实成本，学生不敢放开试。"),
    ("传统仿真器只给数值。", "能算出电压电流，却答不了学生那句“为什么不对”。"),
], size=13)
rect(s, 0.7, 4.55, 3.0, 1.35, fill=LIGHT, line=BORDER, radius=0.06)
tb(s, 0.9, 4.66, 2.65, 1.15, [
    ("传统实验室", 10.5, True, GRAY),
    ("受时间与设备约束\n试错有成本\n反馈依赖教师", 9, False, GRAY),
], space_after=3, line_spacing=1.2)
rect(s, 3.9, 4.55, 3.0, 1.35, fill=RGBColor(0xEC, 0xF2, 0xFB), line=BORDER, radius=0.06)
tb(s, 4.1, 4.66, 2.65, 1.15, [
    ("LearnLab 虚拟实验", 10.5, True, BLUE),
    ("随时可做 · 零成本\n可反复试错 · AI 解释", 9, False, GRAY),
], space_after=3, line_spacing=1.2)
stat(s, 7.45, 1.75, 5.2, 1.28, "46 次", "试点期间实验实训参与（故障诊断 30 次 + 仿真 14 次）", vsize=22)
stat(s, 7.45, 3.15, 5.2, 1.28, "9 / 9", "MNA 数值解与 RC / RL / LC 解析解一致", vsize=22)
stat(s, 7.45, 4.55, 5.2, 1.28, "0 硬件依赖", "求解在浏览器端完成，不依赖后端与设备", vsize=22)
rect(s, 0.7, 6.1, 11.95, 0.62, fill=LIGHT, line=BORDER, radius=0.06)
tb(s, 0.95, 6.22, 11.6, 0.4,
   [("实验不该被“排队”和“怕烧件”卡住——这是把实验室搬进浏览器的直接原因。", 10.5, True, NAVY)])

# ========== 05 问题三 ==========
s = new_slide()
header(s, "问题三：三门课各教各的，链路是断的", "新工科要的是“计算机 × 电子信息”，课程体系却把三门课当成三个孤岛", 5)
bullets(s, 0.7, 1.75, 6.0, [
    ("学完 C 语言，不知道位运算能用在寄存器配置上。", ""),
    ("学完电路分析，不清楚分压采样服务的是 ADC 采集。", ""),
    ("“编程思维 → 电路建模 → 嵌入式实现”这条链路，在传统教学里一直没接上。", ""),
], size=13)
card(s, 0.7, 4.55, 6.0, 1.35, "断点的代价",
     "学完就忘、用时接不上；课程设计也说不清先修关系，学生只能自己“悟”。",
     head_color=ORANGE, head_size=11, body_size=10.5)
bx, by, bw = 7.35, 1.75, 4.9
for i, (label, sub, col) in enumerate([
    ("C 语言程序设计", "位运算 · 指针", RGBColor(0x7C, 0x7C, 0xB8)),
    ("电路分析基础", "分压 · 戴维南", ORANGE),
    ("STM32 嵌入式", "寄存器 · PWM", TEAL),
]):
    y = by + i * 1.5
    rect(s, bx, y, bw, 0.95, fill=WHITE, line=col, radius=0.08, line_w=1.5)
    tb(s, bx + 0.25, y + 0.13, bw - 0.5, 0.35, [(label, 13, True, col)])
    tb(s, bx + 0.25, y + 0.52, bw - 0.5, 0.3, [(sub, 9.5, False, GRAY)])
    if i < 2:
        tb(s, bx + bw / 2 - 0.4, y + 0.97, 0.8, 0.45, [("断", 12, True, ORANGE)], align=PP_ALIGN.CENTER)
rect(s, 0.7, 6.12, 11.95, 0.68, fill=LIGHT, line=BORDER, radius=0.06)
tb(s, 0.95, 6.24, 11.6, 0.45,
   [("三门课的缺口不是内容量，而是“关系”：前置知识、跨课依赖与真实作品，没有被建模。", 11, True, NAVY)])

# ========== 06 AI 能力映射 ==========
s = new_slide()
header(s, "AI 为什么能解决：四类能力对准四类缺口", "不是“用了大模型”，而是每一项能力都对应一个具体的教学环节", 6)
rows = [
    ("AI 技术", "解决的学科问题", "落地功能（均已上线）"),
    ("大语言模型", "即时辅导缺失、实验反馈缺失", "苏格拉底式 AI 辅导、AI 电路分析、C 代码错误诊断"),
    ("多智能体（LangGraph）", "教学流程碎片化", "12 个教育角色智能体覆盖备课、学习、纠错、协作全流程"),
    ("知识图谱 + 自适应算法", "个性化缺失、路径模糊", "ADPP 自适应路径、跨课程知识关联、每日个性化练习"),
    ("浏览器数值计算（MNA）", "实验设备受限", "零成本虚拟电路实验，AI 叠加故障诊断"),
]
tbl_shape = s.shapes.add_table(len(rows), 3, Inches(0.7), Inches(1.72), Inches(11.93), Inches(4.0))
table = tbl_shape.table
table.first_row = True
table.horz_banding = False
widths = [2.85, 3.75, 5.33]
for i, w in enumerate(widths):
    table.columns[i].width = Inches(w)
heights = [0.52, 0.88, 0.88, 0.88, 0.88]
for i, h in enumerate(heights):
    table.rows[i].height = Inches(h)
for r, row in enumerate(rows):
    for c, val in enumerate(row):
        cell = table.cell(r, c)
        cell.fill.solid()
        cell.fill.fore_color.rgb = NAVY if r == 0 else (WHITE if r % 2 else LIGHT)
        cell.margin_left = Inches(0.18)
        cell.margin_right = Inches(0.12)
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf = cell.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.LEFT
        run = p.add_run()
        run.text = val
        run.font.name = FONT
        run.font.size = Pt(12 if r == 0 else 11)
        run.font.bold = (r == 0) or (c == 0)
        run.font.color.rgb = WHITE if r == 0 else (NAVY if c == 0 else GRAY)
rect(s, 0.7, 6.05, 11.93, 0.72, fill=RGBColor(0xEC, 0xF2, 0xFB), line=BORDER, radius=0.06)
tb(s, 0.95, 6.18, 11.5, 0.5,
   [("三大环节共 9 条痛点，全部有已上线功能承接，不存在“分析了但没做”的需求。", 11, True, BLUE)])

# ========== 07 架构 ==========
s = new_slide()
header(s, "新方案总览：四层架构，一条学习闭环", "算法层是本作品的重心；展示层与应用层负责把算法结果变成学生和教师愿意用的界面", 7)
fit_pic(s, "架构图.png", 0.65, 1.65, 6.25, 5.0)
items = [
    ("展示层", "React 18 + TypeScript · 学习路径 / 电路仿真 / 故障诊断 / 试点分析"),
    ("应用层", "学习闭环 · 游戏化激励 · 教师备课台 · 试点报告一键导出"),
    ("算法层", "资质五层闭环 · ADPP 路径 · 趋势预警 · 12 智能体（LangGraph）"),
    ("数据层", "SQLite → PostgreSQL · 35 个知识点 · 跨课程关联 · 行为流水"),
]
for i, (name, desc) in enumerate(items):
    y = 1.7 + i * 1.22
    rect(s, 6.95, y, 5.65, 1.0, fill=LIGHT, line=BORDER, radius=0.07)
    tb(s, 7.15, y + 0.1, 1.2, 0.35, [(name, 12, True, BLUE)])
    tb(s, 8.25, y + 0.12, 4.25, 0.78, [(desc, 9.5, False, GRAY)], line_spacing=1.2)
tb(s, 6.95, 6.55, 5.65, 0.3,
   [("FastAPI + SQLAlchemy ｜ 5 家 LLM 统一接口 + 自动降级 ｜ 腾讯云部署", 9, False, LIGHTGRAY)])

# ========== 08 五层算法 ==========
s = new_slide()
header(s, "核心创新 ①：五层教育算法闭环", "测量 → 建模 → 记忆 → 决策 → 解释；每层都有经典文献出处，工程实现全部自研", 8)
fit_pic(s, "fig_loop.png", 0.65, 1.65, 5.55, 4.75)
bullets(s, 6.6, 1.7, 6.1, [
    ("测量 IRT：", "能力 θ 替代加权平均分，题目难度 b 替代人工 1–5 分级。"),
    ("建模 BKT / GKT：", "逐知识点掌握概率，按时间留出评估；图卷积让邻居知识点影响当前点。"),
    ("记忆 FSRS：", "在遗忘临界点前安排复习，到期知识点自动插入路径复习阶段。"),
    ("决策 MAB：", "Thompson Sampling 用于路径调整、每日选题、资源匹配三处。"),
    ("解释 LLM：", "把算法输出转述成学生听得懂的辅导语言。"),
], size=11.5)
rect(s, 6.6, 6.1, 5.85, 0.65, fill=RGBColor(0xEC, 0xF2, 0xFB), line=BORDER, radius=0.06)
tb(s, 6.85, 6.22, 5.4, 0.45,
   [("全部接入答题、路径、复习、选题、解释 5 个真实入口，不是离线演示件。", 10, True, BLUE)])

# ========== 09 ADPP ==========
s = new_slide()
header(s, "核心创新 ②：ADPP 自适应 DAG 路径规划", "把“先学什么”从教师经验判断，变成按依赖关系与掌握度计算的排序", 9)
node = ["C 语言 · 位运算", "指针", "电路 · 电压波形", "STM32 · 定时器 PWM"]
x = 0.75
for i, label in enumerate(node):
    col = RGBColor(0x7C, 0x7C, 0xB8) if i < 2 else (ORANGE if i == 2 else TEAL)
    rect(s, x, 1.95, 2.55, 0.85, fill=WHITE, line=col, radius=0.08, line_w=1.3)
    tb(s, x + 0.12, 2.18, 2.31, 0.5, [(label, 10.5, True, col)], align=PP_ALIGN.CENTER)
    if i < 3:
        tb(s, x + 2.57, 2.1, 0.35, 0.5, [("→", 14, True, BLUE)], align=PP_ALIGN.CENTER)
    x += 2.88
tb(s, 0.75, 2.95, 11.8, 0.35,
   [("示例：目标知识点为 STM32 定时器 PWM，系统向前追前置依赖，生成一条真正跨学科的学习路径。", 10.5, False, GRAY)])
left_items = [
    ("关键路径法（CPM）", "确定必须掌握的前置链"),
    ("BKT 掌握度", "决定从哪一层难度切入"),
    ("IRT 六因子学习成本", "估算每一步的时间成本"),
]
right_items = [
    ("加权拓扑排序", "在满足依赖的前提下排顺序"),
    ("自适应阶段划分", "按掌握度拆成可完成的小阶段"),
    ("Thompson Sampling", "路径调整策略：回炉 / 强化 / 加速 / 维持"),
]
for i, (k, v) in enumerate(left_items):
    y = 3.55 + i * 1.1
    rect(s, 0.75, y, 5.75, 0.92, fill=LIGHT, line=BORDER, radius=0.07)
    tb(s, 0.95, y + 0.13, 5.35, 0.3, [(k, 11.5, True, NAVY)])
    tb(s, 0.95, y + 0.5, 5.35, 0.3, [(v, 9.5, False, GRAY)])
for i, (k, v) in enumerate(right_items):
    y = 3.55 + i * 1.1
    rect(s, 6.75, y, 5.85, 0.92, fill=LIGHT, line=BORDER, radius=0.07)
    tb(s, 6.95, y + 0.13, 5.45, 0.3, [(k, 11.5, True, NAVY)])
    tb(s, 6.95, y + 0.5, 5.45, 0.3, [(v, 9.5, False, GRAY)])

# ========== 10 MNA ==========
s = new_slide()
header(s, "核心创新 ③：浏览器端 MNA 电路仿真 + AI 故障诊断", "把实验从“受设备约束”变成“随时随地、零成本、可反复试错”", 10)
bullets(s, 0.7, 1.72, 7.0, [
    ("求解链路：", "并查集节点合并（路径压缩 + 按秩合并）→ MNA 方程组 → 列主元高斯消元，全部在浏览器端完成。"),
    ("暂态分析：", "电容/电感状态变量法 + 四阶 Runge-Kutta，输出充放电波形与稳态建立时间。"),
    ("数值可信：", "RC 指数充电、RL 升流、LC 振荡幅值与周期，与解析解对照 9/9 通过。"),
    ("故障诊断：", "3 个故障模板（断路 2 / 短路 1），学生观察异常测量后判断原因；本地规则判定 + AI 讲解原理与排查方法。"),
    ("与后端解耦：", "后端不可用时仿真仍在浏览器内完成，课堂不因网络或服务中断。"),
    ("可反复试错：", "故障以极端阻值注入，不损伤任何器件，学生可以放开试。"),
], size=11.5)
stat(s, 8.0, 1.78, 4.65, 1.28, "0 后端", "电路求解完全在浏览器内完成，不依赖服务器", vsize=24)
stat(s, 8.0, 3.03, 4.65, 1.28, "9 / 9", "数值解与 RC / RL / LC 解析解一致", vsize=24)
stat(s, 8.0, 4.28, 4.65, 1.28, "3 类故障", "断路 ×2、短路 ×1，可反复注入与排查", vsize=24)
rect(s, 0.7, 6.1, 11.95, 0.66, fill=LIGHT, line=BORDER, radius=0.06)
tb(s, 0.95, 6.22, 11.6, 0.45,
   [("对照传统实验：不受开放时间限制、不怕烧件、反馈即时，且 AI 回答“为什么异常”。", 10.5, True, NAVY)])

# ========== 11 跨课程 ==========
s = new_slide()
header(s, "核心创新 ④：把三门课接成一条链路", "9 条跨课程知识关联 + 统一错误诊断入口 + 一个跨三门的综合实战项目", 11)
bullets(s, 0.7, 1.72, 5.9, [
    ("9 条关联注入知识图谱：", "位运算 → 寄存器配置；分压采样 → ADC 采集；指针 → 外设地址。"),
    ("路径编排跨课程序列：", "ADPP 排的不是单课目录，而是“编程 → 电路 → 嵌入式”的前置顺序。"),
    ("统一诊断入口：", "按当前学科自动分发到 C 语言分层诊断、电路故障分析、STM32 实训；结论回写画像。"),
    ("综合实战：", "智能温控风扇 —— C 语言采样 → 分压电路 → PWM 调速，三门课知识用在一个作品上。"),
], size=11.5)
# 右侧跨课程关系图（矢量绘制，避免位图遮挡）
purple = RGBColor(0x7C, 0x7C, 0xB8)
green = RGBColor(0x2E, 0x7D, 0x32)
box = [
    (6.95, 1.95, 2.35, 0.95, purple, "C 语言程序设计", "位运算 · 指针"),
    (10.25, 1.95, 2.35, 0.95, ORANGE, "电路分析基础", "分压 · 戴维南"),
    (8.4, 3.22, 2.78, 0.95, green, "综合实战：智能温控风扇", "C 语言采样 → 分压电路 → PWM 调速"),
    (8.5, 4.42, 2.55, 0.95, TEAL, "STM32 嵌入式", "寄存器 · PWM"),
]
for x, y, w, h, col, title, sub in box:
    rect(s, x, y, w, h, fill=WHITE, line=col, radius=0.1, line_w=1.5)
    tb(s, x + 0.12, y + 0.16, w - 0.24, 0.32, [(title, 10.5, True, col)], align=PP_ALIGN.CENTER)
    tb(s, x + 0.12, y + 0.52, w - 0.24, 0.3, [(sub, 8.5, False, GRAY)], align=PP_ALIGN.CENTER)
arrow(s, 8.1, 2.95, 8.85, 3.2, color=purple, width=1.4)
arrow(s, 11.35, 2.95, 10.7, 3.2, color=ORANGE, width=1.4)
arrow(s, 9.79, 4.19, 9.79, 4.4, color=green, width=1.4)
tb(s, 6.7, 3.35, 1.65, 0.6, [("采样编程\n中断控制", 8, False, green)], align=PP_ALIGN.RIGHT, line_spacing=1.15)
tb(s, 11.35, 3.35, 1.35, 0.6, [("分压采样\nADC 采集", 8, False, ORANGE)], line_spacing=1.15)
for i, (v, l) in enumerate([("9 条", "跨课程知识关联"), ("3 门", "课程接成一条链路"), ("1 个", "跨三门综合项目")]):
    x = 0.7 + i * 2.05
    rect(s, x, 5.55, 1.9, 1.1, fill=LIGHT, line=BORDER, radius=0.07)
    tb(s, x + 0.18, 5.66, 1.55, 0.45, [(v, 18, True, BLUE)])
    tb(s, x + 0.18, 6.12, 1.55, 0.35, [(l, 9, False, GRAY)])
rect(s, 6.85, 5.55, 5.75, 1.1, fill=RGBColor(0xEC, 0xF2, 0xFB), line=BORDER, radius=0.06)
tb(s, 7.05, 5.68, 5.35, 0.85,
   [("这是“跨学科”在系统里的具体形态：知识图谱有边、路径有顺序、诊断有统一入口、项目有真实作品。", 9.5, False, BLUE)])

# ========== 12 12 Agent + 防幻觉 ==========
s = new_slide()
header(s, "核心创新 ⑤：12 个教育智能体 + 6 道防幻觉防线", "LangGraph 星型编排，AgentMessage 标准协议 + 反思循环；常驻规则守卫不增加调用成本", 12)
groups = [
    ("主链路（5）", "课程设计师（Supervisor）· 画像师 · 路径规划师 · 资源生成师 · 辅导助手"),
    ("知识支撑（2）", "知识图谱构建师 · 思维溯源师"),
    ("错误诊断（1）", "错误捕捉师（语法 / 逻辑 / 思维误区三层诊断）"),
    ("协作场景（4）", "项目拆解师 · 角色匹配师 · 协作督导 · 成果评估师"),
]
for i, (g, names) in enumerate(groups):
    y = 1.72 + i * 1.0
    rect(s, 0.7, y, 6.15, 0.86, fill=LIGHT, line=BORDER, radius=0.07)
    tb(s, 0.9, y + 0.12, 1.55, 0.3, [(g, 10.5, True, BLUE)])
    tb(s, 2.35, y + 0.12, 4.3, 0.65, [(names, 9.2, False, GRAY)], line_spacing=1.2)
fit_pic(s, "fig_guard.png", 7.0, 1.75, 5.55, 1.95)
bullets(s, 7.0, 3.95, 5.6, [
    ("①–⑤ 常驻主管线：", "输入过滤、Prompt 加固、结构校验、代码校验、引用溯源，规则守卫零成本。"),
    ("⑥ 自我纠错：", "随反思循环生效，执行—评估—修正最多 3 次，可按配置现场开启。"),
], size=10.5)
rect(s, 0.7, 6.25, 11.95, 0.55, fill=LIGHT, line=BORDER, radius=0.06)
tb(s, 0.95, 6.36, 11.5, 0.35,
   [("AgentMessage 标准协议 · 12 个角色可独立替换 · 反思循环执行—评估—修正最多 3 次", 10, True, NAVY)])
s = new_slide()
header(s, "应用效果：真实试点，不是主观描述", "前测 20 份、后测 17 份，全部来自真实学生微信端提交；行为数据自动落库", 13)
stat(s, 0.7, 1.72, 2.85, 1.35, "20 / 17", "前测 / 后测有效问卷（份）", vsize=24)
stat(s, 3.75, 1.72, 2.85, 1.35, "+8 pp", "电路分析（戴维南）80% → 88%", vsize=24)
stat(s, 6.8, 1.72, 2.85, 1.35, "+15.8 分", "配对测验 67.1 → 82.9（约 +23.5%）", vsize=24)
stat(s, 9.85, 1.72, 2.8, 1.35, "100%", "学习内容有帮助（满意度）", vsize=24)
bullets(s, 0.7, 3.35, 6.0, [
    ("真实使用：", "累计注册 39 名学生（含真实学号），AI 生成类调用 600+ 次，零失败记录，平均响应约 8 秒。"),
    ("行为数据：", "近 30 天活跃 15 人、学习行为 424 条、总时长 67.9 小时（人均约 4.5 小时），随堂测验 247 人次。"),
    ("稳定性：", "82% 反馈“完全没有”卡顿，零阻断性故障；生产环境 24 小时零 500 错误。"),
], size=10.5)
card(s, 0.7, 5.35, 5.95, 1.0, "证据来源",
     "问卷（主观感受）+ 行为日志（客观记录）+ 系统实测（工程口径），三类独立证据互相印证。",
     head_color=BLUE, head_size=10.5, body_size=9.5)
rect(s, 6.8, 3.35, 5.85, 3.0, fill=LIGHT, line=BORDER, radius=0.06)
tb(s, 7.0, 3.48, 5.45, 0.3, [("工程验证硬口径", 12, True, NAVY)])
tb(s, 7.0, 3.88, 5.45, 2.35, [
    ("116 项算法专项断言全部通过", 10, False, GRAY),
    ("211 个后端路由冒烟 0 崩溃", 10, False, GRAY),
    ("59 个前端 E2E 用例（7 个文件）通过", 10, False, GRAY),
    ("24 个页面逐页遍历，零 JS 错误、零横向溢出", 10, False, GRAY),
    ("MNA 数值验证 9/9，与解析解一致", 10, False, GRAY),
    ("5 家 LLM 统一接口 + 自动降级 + 6 道防幻觉", 10, False, GRAY),
], line_spacing=1.35, space_after=4)

# ========== 14 价值 ==========
s = new_slide()
header(s, "应用价值：把“一对一辅导”变成可复制的成本结构", "同一套系统，既解决单门课的个性化，也能复制到同类工科课程", 14)
card(s, 0.7, 1.75, 3.8, 3.55, "成本",
     "部署成本约为传统实验室的百分之一\n\n"
     "浏览器端仿真替代硬件工位\n\n"
     "5 家 LLM 自动降级，教学场景成本可控\n\n"
     "学校无需为每个学生配一名辅导教师\n\n"
     "单次实验的边际成本接近于零", body_size=10.5)
card(s, 4.75, 1.75, 3.8, 3.55, "可复制",
     "学科模板库：新接入一门课 2–3 周\n\n"
     "LLM 辅助知识图谱预构建 + 人工审核\n\n"
     "9 条跨课程关联可复用到其他专业组合\n\n"
     "目标：从三门课推广成一套工程范式\n\n"
     "已沉淀讲义规范与学科模板", body_size=10.5)
card(s, 8.8, 1.75, 3.85, 3.55, "已落地",
     "腾讯云上线：www.dreamlast.cn\n\n"
     "真实学号持续注册使用，不是演示环境\n\n"
     "学生端 10 页 + 教师端 14 页全部可用\n\n"
     "试点报告可一键导出，形成过程性数据\n\n"
     "现场可登录、可操作、可复现", body_size=10.5)
rect(s, 0.7, 5.55, 11.95, 1.15, fill=NAVY, radius=0.06)
tb(s, 1.0, 5.72, 11.4, 0.8, [
    ("一句话总结：让每个学生都拥有一条按自己认知状态计算的路径，而学校的成本不随学生人数线性上升。", 13, True, WHITE)
], anchor=MSO_ANCHOR.MIDDLE, line_spacing=1.2)

# ========== 15 团队 ==========
s = new_slide()
header(s, "团队：三个专业，各管一段", "跨专业组队不是标签，而是分工：算法、数据、界面各有人负责", 15)
members = [
    ("马其瑞", "队长 · 电子信息工程", "后端架构与算法引擎\n五层算法接入、12 Agent 编排、MNA 求解器", "211 路由 · 116 算法断言"),
    ("孙雨瑶", "数据科学与大数据技术", "试点数据与质量验证\n前后测设计、问卷回收、算法评估与测试", "前测 20 / 后测 17 · 满意度 100%"),
    ("居欣月", "遥感科学与技术", "前端页面与数据可视化\n学生端 10 页 + 教师端 14 页、知识图谱可视化", "24 页零 JS 错误 · 59 E2E 用例"),
]
for i, (name, major, duty, metric) in enumerate(members):
    x = 0.7 + i * 4.0
    rect(s, x, 1.8, 3.75, 3.3, fill=LIGHT, line=BORDER, radius=0.06)
    tb(s, x + 0.28, 2.0, 3.2, 0.4, [(name, 20, True, NAVY)])
    tb(s, x + 0.28, 2.5, 3.2, 0.35, [(major, 10, False, BLUE)])
    rect(s, x + 0.28, 2.95, 0.55, 0.03, fill=BLUE)
    tb(s, x + 0.28, 3.15, 3.2, 1.5, [(duty, 10, False, GRAY)], line_spacing=1.35)
    tb(s, x + 0.28, 4.55, 3.2, 0.35, [(metric, 9, True, BLUE)])
rect(s, 0.7, 5.45, 11.95, 1.3, fill=RGBColor(0xEC, 0xF2, 0xFB), line=BORDER, radius=0.06)
tb(s, 1.0, 5.6, 11.4, 1.0, [
    ("可现场运行  ·  源码可复现  ·  数据可审计", 15, True, BLUE),
    ("谢谢各位评委，欢迎提问。演示环境：www.dreamlast.cn（账号见《运行说明》）", 10, False, GRAY),
], space_after=8, line_spacing=1.2)

prs.save(OUT)
print("saved", OUT, len(prs.slides.__iter__.__self__._sldIdLst))
