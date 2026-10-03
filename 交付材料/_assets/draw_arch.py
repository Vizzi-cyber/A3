# -*- coding: utf-8 -*-
"""系统架构图（四层）——按成品物理尺寸绘制，matplotlib 字号 = 印刷字号。
画布 15cm 宽 = PDF 中 width=15cm 原尺寸插入，图内 9pt 即印出 9pt。
输出：交付材料/02_技术方案/latex/arch.png（300dpi）+ _assets/架构图.png
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
from matplotlib import font_manager

for f in (r'C:\Windows\Fonts\simhei.ttf',):
    font_manager.fontManager.addfont(f)
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

W, H = 5.906, 4.70          # 15cm × 11.9cm
fig = plt.figure(figsize=(W, H), dpi=300)
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis('off')

LX, LW = 0.05, 1.08          # 层标签列
BX, BW = 1.23, W - 1.23 - 0.05   # 内容区
EC, LW_BODY = 'black', 0.8

def band(top, h, name, sub):
    y = top - h
    ax.add_patch(FancyBboxPatch((LX, y), LW, h, boxstyle='round,pad=0,rounding_size=0.04',
                                fc='#efefef', ec=EC, lw=LW_BODY))
    cy = y + h / 2
    lines = sub.split('\n')
    ax.text(LX + LW / 2, cy + 0.09 * (2 - len(lines)), name,
            ha='center', va='center', fontsize=9.5, fontweight='bold', family='SimHei')
    for k, ln in enumerate(lines):
        ax.text(LX + LW / 2, cy - 0.12 - 0.17 * k + 0.09 * (2 - len(lines)), ln,
                ha='center', va='center', fontsize=6.8, color='#333333', family='SimHei')

def box(x, w, y, h, title, sub=None, tsize=8.3, ssize=6.9):
    ax.add_patch(Rectangle((x, y), w, h, fc='white', ec=EC, lw=0.7))
    if sub:
        ax.text(x + w / 2, y + h * 0.62, title, ha='center', va='center',
                fontsize=tsize, fontweight='bold', family='SimHei')
        ax.text(x + w / 2, y + h * 0.28, sub, ha='center', va='center',
                fontsize=ssize, color='#333333')
    else:
        ax.text(x + w / 2, y + h / 2, title, ha='center', va='center',
                fontsize=tsize, fontweight='bold', family='SimHei')

def row(top, h, items, tsize=8.3, ssize=6.9, gap=0.10, pad=0.08):
    y = top - h
    n = len(items)
    bw = (BW - pad * 2 - gap * (n - 1)) / n
    for k, it in enumerate(items):
        box(BX + pad + k * (bw + gap), bw, y, h, it[0], it[1] if len(it) > 1 else None,
            tsize=tsize, ssize=ssize)
    return y, bw

def arrow(x, y):
    ax.annotate('', xy=(x + 0.09, y), xytext=(x - 0.09, y),
                arrowprops=dict(arrowstyle='->', lw=0.9, color='black'))

# ---- 展示层 ----
band(4.67, 0.87, '展示层', '前端 React + TS')
row(4.62, 0.76, [('学习路径', '含跨学科视图'), ('电路仿真', 'MNA + RK4 暂态'),
                 ('故障诊断实验', 'STM32 实训'), ('试点数据分析', '班级对比')])

# ---- 应用层 ----
band(3.67, 0.87, '应用层', '业务服务')
row(3.62, 0.76, [('学习闭环', '测 · 学 · 练 · 修'), ('游戏化激励', '徽章 · 排行'),
                 ('教师备课工作台', '组卷 · 学情'), ('试点报告', '一键导出')])

# ---- 算法层（两行）----
band(2.67, 1.47, '算法层', '五层算法闭环\n12 智能体')
y5, bw5 = row(2.60, 0.68, [('① 测量', 'IRT（1PL/2PL）'), ('② 建模', 'BKT / GKT'),
                           ('③ 记忆', 'FSRS'), ('④ 决策', 'MAB'), ('⑤ 解释', 'LLM 数理化')], gap=0.24)
step = (BW - 0.16 - 0.24 * 4) / 5 + 0.24
for k in range(4):   # 五层闭环箭头
    arrow(BX + 0.08 + (k + 1) * step - 0.12 + 0.02, 2.26)
row(1.76, 0.62, [('ADPP 自适应\nDAG 路径规划', None), ('趋势预警\n（L2 逻辑回归）', None),
                 ('12 个 AI 智能体\nLangGraph 星型拓扑', None)], tsize=7.4, gap=0.10)

# ---- 数据层 ----
band(1.13, 0.92, '数据层', 'SQLite / PostgreSQL')
row(1.08, 0.82, [('knowledge_points', '35 个/跨课程关联'), ('courses', '学科元数据'),
                 ('learning_records', '学习行为流水'), ('quiz_results', '测验成绩'),
                 ('experiment_logs', '实验日志')], tsize=6.6, ssize=6.6, gap=0.07)

fig.savefig(r'E:\开发\learnlabAI教学平台\交付材料\02_技术方案\latex\arch.png', dpi=300)
fig.savefig(r'E:\开发\learnlabAI教学平台\交付材料\_assets\架构图.png', dpi=300)
print('arch.png 已生成')
