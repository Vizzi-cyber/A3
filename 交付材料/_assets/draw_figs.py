# -*- coding: utf-8 -*-
"""技术方案配图（彩色版，物理尺寸画布：figsize=插入宽度，字号=印刷字号，300dpi）
fig_loop.png   五层算法闭环与数据回流   → 三（三）2，宽 14cm
fig_guard.png  防幻觉六道防线管道      → 三（三）6，宽 14cm
fig_fsrs.png   记忆调度机制示意曲线    → 三（三）2 记忆段后，宽 11cm
fig_cross.png  跨学科学习链路          → 三（三）5，宽 14cm
fig_pilot.png  试点流程                → 六（二），宽 14cm
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
from matplotlib import font_manager
import numpy as np
import os

for f in (r'C:\Windows\Fonts\simhei.ttf',):
    font_manager.fontManager.addfont(f)
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

DST = r'E:\开发\learnlabAI教学平台\交付材料\_assets'
INK = '#1F2937'
SUB = '#4B5563'
# AIC 蓝 + 分层功能色（深色描边 / 浅色填充）
BLUE, BLUE_L = '#1256B8', '#E8F0FB'
TEAL, TEAL_L = '#0E9888', '#E5F4F1'
ORG, ORG_L = '#D97706', '#FDF0E1'
PUR, PUR_L = '#6D4AC7', '#EFEAFB'
GRN, GRN_L = '#2E9E4F', '#E7F5EB'
GRAY, GRAY_L = '#6B7280', '#F3F4F6'

def new_ax(w_in, h_in):
    fig = plt.figure(figsize=(w_in, h_in), dpi=300)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, w_in); ax.set_ylim(0, h_in); ax.axis('off')
    return fig, ax

def cbox(ax, x, y, w, h, ec, fc, lw=0.9):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0,rounding_size=0.045',
                                fc=fc, ec=ec, lw=lw))

def arr(ax, x1, y1, x2, y2, color=SUB, lw=1.0):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='-|>', lw=lw, color=color, mutation_scale=9))

def save(fig, name):
    fig.savefig(os.path.join(DST, name), dpi=300)
    plt.close(fig)
    print(name, 'ok')

# ============ 图：五层算法闭环与数据回流（彩色） ============
fig, ax = new_ax(5.512, 2.25)
layers = [('① 测量', 'IRT 认知诊断', '能力参数 θ', BLUE, BLUE_L),
          ('② 建模', 'BKT / GKT', '掌握概率', TEAL, TEAL_L),
          ('③ 记忆', 'FSRS 调度', '复习到期日', GRN, GRN_L),
          ('④ 决策', 'MAB 探索利用', '资源与路径', ORG, ORG_L),
          ('⑤ 解释', 'LLM 数理化', '可读反馈', PUR, PUR_L)]
bw, bh, gap = 0.92, 0.86, 0.16
x0 = (5.512 - (5 * bw + 4 * gap)) / 2
ytop = 1.26
for k, (t, m, o, ec, fc) in enumerate(layers):
    x = x0 + k * (bw + gap)
    cbox(ax, x, ytop, bw, bh, ec, fc)
    ax.text(x + bw/2, ytop + bh*0.72, t, ha='center', va='center', fontsize=8.2,
            fontweight='bold', color=ec)
    ax.text(x + bw/2, ytop + bh*0.44, m, ha='center', va='center', fontsize=6.8, color=INK)
    ax.text(x + bw/2, ytop + bh*0.16, '→ ' + o, ha='center', va='center', fontsize=6.4, color=SUB)
    if k < 4:
        arr(ax, x + bw + 0.015, ytop + bh/2, x + bw + gap - 0.015, ytop + bh/2, color=ec)
ymid = ytop - 0.34
arr(ax, x0 + 4*(bw+gap) + bw/2, ytop - 0.02, x0 + 4*(bw+gap) + bw/2, ymid, color=PUR)
ax.plot([x0 + bw/2, x0 + 4*(bw+gap) + bw/2], [ymid, ymid], color=SUB, lw=0.8)
arr(ax, x0 + bw/2, ymid, x0 + bw/2, ytop - 0.02, color=SUB)
ax.text(5.512/2, ymid - 0.15, '行为数据自动落库 → 回灌模型再训练（决策产生行为，行为沉淀为数据）',
        ha='center', va='center', fontsize=6.8, color=SUB)
ax.text(5.512/2, 0.22, '业务入口：答题 · 路径 · 复习 · 选题 · 解释（五层全部接进真实链路）',
        ha='center', va='center', fontsize=7.2, color=INK)
save(fig, 'fig_loop.png')

# ============ 图：防幻觉六道防线管道（新） ============
fig, ax = new_ax(5.512, 1.62)
guards = [('输入过滤', '敏感与注入\n规则过滤', BLUE, BLUE_L),
          ('Prompt 加固', '角色与格式\n约束', TEAL, TEAL_L),
          ('结构校验', 'JSON 字段\n完整性', GRN, GRN_L),
          ('代码校验', 'AST 语法\n静态解析', ORG, ORG_L),
          ('引用溯源', '知识点来源\n标注', PUR, PUR_L),
          ('自我纠错', '反思循环\n随开关生效', '#B91C1C', '#FDEAEA')]
bw, bh, gap = 0.78, 0.92, 0.115
x0 = (5.512 - (6 * bw + 5 * gap)) / 2
y0 = 0.42
for k, (t, s, ec, fc) in enumerate(guards):
    x = x0 + k * (bw + gap)
    cbox(ax, x, y0, bw, bh, ec, fc)
    ax.text(x + bw/2, y0 + bh*0.70, t, ha='center', va='center', fontsize=7.0,
            fontweight='bold', color=ec)
    for li, ln in enumerate(s.split('\n')):
        ax.text(x + bw/2, y0 + bh*0.38 - li*0.175, ln, ha='center', va='center',
                fontsize=6.0, color=INK)
    if k < 5:
        arr(ax, x + bw + 0.01, y0 + bh/2, x + bw + gap - 0.01, y0 + bh/2)
ax.text(5.512/2, 0.16, '六道防线常驻主管线，输出到达学生之前逐层拦截幻觉',
        ha='center', va='center', fontsize=7.0, color=SUB)
save(fig, 'fig_guard.png')

# ============ 图：记忆调度机制示意（新，曲线图） ============
fig = plt.figure(figsize=(4.0, 2.45), dpi=300)
ax = fig.add_axes([0.13, 0.20, 0.84, 0.74])
days = np.arange(0, 30.5, 0.05)
def curve(reviews, S0, growth, horizon=30.5):
    xs, ys = [0.0], [100.0]
    t, S, base = 0.0, S0, 100.0
    for rp in reviews:
        tt = np.arange(t, rp + 1e-9, 0.05)
        xs.extend(tt.tolist()); ys.extend((base * np.exp(-(tt - t) / S)).tolist())
        base = float(base * np.exp(-(rp - t) / S)); S *= growth; t = rp
    tt = np.arange(t, horizon, 0.05)
    xs.extend(tt.tolist()); ys.extend((base * np.exp(-(tt - t) / S)).tolist())
    return np.array(xs), np.array(ys)
# FSRS：复习设在可提取性降至 ~90% 的临界点，稳定性每次复习成倍增长
fsrs_x, fsrs_y = curve([1, 3.2, 8, 18.6], 9.5, 2.2)
# 统一间隔：固定每 7 天复习，稳定性不增长，遗忘已明显发生
fix_x, fix_y = curve([7, 14, 21, 28], 12.0, 1.0)
ax.plot(fsrs_x, fsrs_y, color=BLUE, lw=1.4, label='FSRS 个性化调度')
ax.plot(fix_x, fix_y, color='#9CA3AF', lw=1.2, ls='--', label='统一间隔复习')
ax.axhline(60, color='#D1D5DB', lw=0.7, ls=':')
ax.text(29.8, 62, '可提取性 60%', ha='right', fontsize=6.2, color='#9CA3AF')
ax.set_xlabel('时间（天）', fontsize=7.2, color=INK)
ax.set_ylabel('可提取性（记忆保留率 %）', fontsize=7.2, color=INK)
ax.set_ylim(40, 103); ax.set_xlim(0, 30.5)
ax.tick_params(labelsize=6.5, colors=SUB)
for sp in ('top', 'right'): ax.spines[sp].set_visible(False)
ax.legend(fontsize=6.6, loc='lower left', frameon=False)
ax.set_title('FSRS 在遗忘临界点前安排复习，稳定性随复习递增（机制示意）',
             fontsize=7.0, color=INK, pad=4)
save(fig, 'fig_fsrs.png')

# ============ 图：跨学科学习链路（彩色） ============
fig, ax = new_ax(5.512, 2.35)
courses = [('C 语言程序设计', '位运算 · 指针 · 采样编程', BLUE, BLUE_L),
           ('电路分析基础', '分压采样 · 戴维南等效', ORG, ORG_L),
           ('STM32 嵌入式', '寄存器配置 · PWM 调速', TEAL, TEAL_L)]
cw, ch, cgap = 1.52, 0.72, 0.24
cx0 = (5.512 - (3 * cw + 2 * cgap)) / 2
cy = 1.28
for k, (t, s, ec, fc) in enumerate(courses):
    x = cx0 + k * (cw + cgap)
    cbox(ax, x, cy, cw, ch, ec, fc)
    ax.text(x + cw/2, cy + ch*0.66, t, ha='center', va='center', fontsize=8.0,
            fontweight='bold', color=ec)
    ax.text(x + cw/2, cy + ch*0.26, s, ha='center', va='center', fontsize=6.5, color=INK)
    if k < 2:
        arr(ax, x + cw + 0.02, cy + ch/2, x + cw + cgap - 0.02, cy + ch/2)
        ax.text(x + cw + cgap/2, cy + ch/2 + 0.10, '知识关联', ha='center', va='center',
                fontsize=6.0, color=SUB)
pw = 4.3
px = (5.512 - pw) / 2
cbox(ax, px, 0.18, pw, 0.62, GRN, GRN_L)
ax.text(px + pw/2, 0.49, '综合实战项目：智能温控风扇', ha='center', va='center',
        fontsize=8.0, fontweight='bold', color='#1E7A38')
ax.text(px + pw/2, 0.30, 'C 语言采样 → 分压电路 → PWM 调速（三门课知识贯通一个作品）',
        ha='center', va='center', fontsize=6.6, color=INK)
arr(ax, 5.512/2, cy - 0.02, 5.512/2, 0.82)
ax.text(5.512/2 + 0.12, 0.92, '9 条跨课程知识关联支撑', ha='left', va='center',
        fontsize=6.4, color=SUB)
save(fig, 'fig_cross.png')

# ============ 图：试点流程（彩色） ============
fig, ax = new_ax(5.512, 1.75)
steps = [('前测问卷', '小程序匿名填写', BLUE, BLUE_L),
         ('分组', '实验组 SY×4\n对照组 CK×4', PUR, PUR_L),
         ('1-2 周使用', '实验组用平台\n对照组传统自学', TEAL, TEAL_L),
         ('后测问卷', '同量表同题目', ORG, ORG_L),
         ('数据分析报告', '教师端一键导出', GRN, GRN_L)]
sw, sh, sgap = 0.98, 0.78, 0.14
sx0 = (5.512 - (5 * sw + 4 * sgap)) / 2
sy = (1.75 - sh) / 2 + 0.06
for k, (t, s, ec, fc) in enumerate(steps):
    x = sx0 + k * (sw + sgap)
    cbox(ax, x, sy, sw, sh, ec, fc)
    lines = s.split('\n')
    ax.text(x + sw/2, sy + sh*0.68, t, ha='center', va='center', fontsize=7.8,
            fontweight='bold', color=ec)
    for li, ln in enumerate(lines):
        ax.text(x + sw/2, sy + sh*0.36 - li*0.155, ln, ha='center', va='center',
                fontsize=6.2, color=INK)
    if k < 4:
        arr(ax, x + sw + 0.01, sy + sh/2, x + sw + sgap - 0.01, sy + sh/2)
save(fig, 'fig_pilot.png')
