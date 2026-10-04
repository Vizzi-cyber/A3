# -*- coding: utf-8 -*-
"""技术方案配图三张（物理尺寸画布：figsize=插入宽度，字号=印刷字号，300dpi）
fig_loop.png  五层算法闭环与数据回流   → 插入 三（三）2，宽 14cm
fig_cross.png 跨学科学习链路          → 插入 三（三）5，宽 14cm
fig_pilot.png 试点流程                → 插入 六（二），宽 14cm
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
from matplotlib import font_manager
import os

for f in (r'C:\Windows\Fonts\simhei.ttf',):
    font_manager.fontManager.addfont(f)
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

DST = r'E:\开发\learnlabAI教学平台\交付材料\_assets'
EC = 'black'

def new_ax(w_in, h_in):
    fig = plt.figure(figsize=(w_in, h_in), dpi=300)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, w_in); ax.set_ylim(0, h_in); ax.axis('off')
    return fig, ax

def rbox(ax, x, y, w, h, fc='white'):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0,rounding_size=0.04',
                                fc=fc, ec=EC, lw=0.8))

def arr(ax, x1, y1, x2, y2, lw=0.9):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', lw=lw, color='black'))

def save(fig, name):
    fig.savefig(os.path.join(DST, name), dpi=300)
    plt.close(fig)
    print(name, 'ok')

# ============ 图 2：五层算法闭环与数据回流 ============
fig, ax = new_ax(5.512, 2.55)          # 14cm × 6.5cm
layers = [('① 测量', 'IRT 认知诊断', '能力参数 θ'),
          ('② 建模', 'BKT / GKT', '掌握概率'),
          ('③ 记忆', 'FSRS 调度', '复习到期日'),
          ('④ 决策', 'MAB 探索利用', '资源与路径'),
          ('⑤ 解释', 'LLM 数理化', '可读反馈')]
bw, bh, gap = 0.92, 0.86, 0.16
x0 = (5.512 - (5 * bw + 4 * gap)) / 2
ytop = 1.52
for k, (t, m, o) in enumerate(layers):
    x = x0 + k * (bw + gap)
    rbox(ax, x, ytop, bw, bh)
    ax.text(x + bw/2, ytop + bh*0.72, t, ha='center', va='center', fontsize=8.2, fontweight='bold')
    ax.text(x + bw/2, ytop + bh*0.44, m, ha='center', va='center', fontsize=6.8, color='#333333')
    ax.text(x + bw/2, ytop + bh*0.16, '→ ' + o, ha='center', va='center', fontsize=6.4, color='#333333')
    if k < 4:
        arr(ax, x + bw + 0.015, ytop + bh/2, x + bw + gap - 0.015, ytop + bh/2)
# 数据回流：⑤ 底部 → ① 底部
ymid = ytop - 0.34
arr(ax, x0 + 4*(bw+gap) + bw/2, ytop - 0.02, x0 + 4*(bw+gap) + bw/2, ymid, lw=0.8)
ax.plot([x0 + bw/2, x0 + 4*(bw+gap) + bw/2], [ymid, ymid], color='black', lw=0.8)
arr(ax, x0 + bw/2, ymid, x0 + bw/2, ytop - 0.02, lw=0.8)
ax.text(5.512/2, ymid - 0.16, '行为数据自动落库 → 回灌模型再训练（决策产生行为，行为沉淀为数据）',
        ha='center', va='center', fontsize=6.8, color='#333333')
ax.text(5.512/2, 0.12, '业务入口：答题 · 路径 · 复习 · 选题 · 解释（五层全部接进真实链路）',
        ha='center', va='center', fontsize=7.2)
save(fig, 'fig_loop.png')

# ============ 图 3：跨学科学习链路 ============
fig, ax = new_ax(5.512, 2.35)          # 14cm × 6cm
courses = [('C 语言程序设计', '位运算 · 指针 · 采样编程'),
           ('电路分析基础', '分压采样 · 戴维南等效'),
           ('STM32 嵌入式', '寄存器配置 · PWM 调速')]
cw, ch, cgap = 1.52, 0.72, 0.24
cx0 = (5.512 - (3 * cw + 2 * cgap)) / 2
cy = 1.28
for k, (t, s) in enumerate(courses):
    x = cx0 + k * (cw + cgap)
    rbox(ax, x, cy, cw, ch)
    ax.text(x + cw/2, cy + ch*0.66, t, ha='center', va='center', fontsize=8.0, fontweight='bold')
    ax.text(x + cw/2, cy + ch*0.26, s, ha='center', va='center', fontsize=6.5, color='#333333')
    if k < 2:
        arr(ax, x + cw + 0.02, cy + ch/2, x + cw + cgap - 0.02, cy + ch/2)
        ax.text(x + cw + cgap/2, cy + ch/2 + 0.10, '知识关联', ha='center', va='center',
                fontsize=6.0, color='#333333')
# 底部：综合实战项目
pw = 4.3
px = (5.512 - pw) / 2
rbox(ax, px, 0.18, pw, 0.62, fc='#efefef')
ax.text(px + pw/2, 0.49, '综合实战项目：智能温控风扇', ha='center', va='center',
        fontsize=8.0, fontweight='bold')
ax.text(px + pw/2, 0.30, 'C 语言采样 → 分压电路 → PWM 调速（三门课知识贯通一个作品）',
        ha='center', va='center', fontsize=6.6, color='#333333')
arr(ax, 5.512/2, cy - 0.02, 5.512/2, 0.82)
ax.text(5.512/2 + 0.12, 0.92, '9 条跨课程知识关联支撑', ha='left', va='center',
        fontsize=6.4, color='#333333')
save(fig, 'fig_cross.png')

# ============ 图 4：试点流程 ============
fig, ax = new_ax(5.512, 1.75)          # 14cm × 4.4cm
steps = [('前测问卷', '小程序匿名填写'),
         ('分组', '实验组 SY×4\n对照组 CK×4'),
         ('1-2 周使用', '实验组用平台\n对照组传统自学'),
         ('后测问卷', '同量表同题目'),
         ('数据分析报告', '教师端一键导出')]
sw, sh, sgap = 0.98, 0.78, 0.14
sx0 = (5.512 - (5 * sw + 4 * sgap)) / 2
sy = (1.75 - sh) / 2 + 0.06
for k, (t, s) in enumerate(steps):
    x = sx0 + k * (sw + sgap)
    rbox(ax, x, sy, sw, sh, fc='#efefef' if k == 1 else 'white')
    lines = s.split('\n')
    ax.text(x + sw/2, sy + sh*0.68, t, ha='center', va='center', fontsize=7.8, fontweight='bold')
    for li, ln in enumerate(lines):
        ax.text(x + sw/2, sy + sh*0.36 - li*0.155, ln, ha='center', va='center',
                fontsize=6.2, color='#333333')
    if k < 4:
        arr(ax, x + sw + 0.01, sy + sh/2, x + sw + sgap - 0.01, sy + sh/2)
save(fig, 'fig_pilot.png')
