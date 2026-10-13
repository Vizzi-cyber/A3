# -*- coding: utf-8 -*-
"""技术方案配图（差异化视觉语言版，物理尺寸画布，字号=印刷字号，300dpi）
fig_loop.png   五层算法闭环——环形循环图（曲线箭头+中心标注+外环回流）  → 三（三）2，宽 12cm
fig_cross.png  跨学科学习链路——三角网络图（课程圆节点+关联边+中心项目）→ 三（三）5，宽 14cm
fig_guard.png  防幻觉六道防线——闸门管道图（雪佛龙段+红到绿渐变）      → 三（三）6，宽 14cm
fig_pilot.png  试点流程——时间轴（圆点里程碑+上下交错标注）            → 六（二），宽 14cm
fig_fsrs.png   记忆调度曲线对比（数据曲线图）                          → 三（三）2 记忆段后，宽 11cm
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Ellipse, Polygon, Rectangle
from matplotlib import font_manager
import numpy as np
import os

for f in (r'C:\Windows\Fonts\simhei.ttf',):
    font_manager.fontManager.addfont(f)
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

DST = r'E:\开发\learnlabAI教学平台\交付材料\_assets'
INK, SUB = '#1F2937', '#4B5563'
BLUE, BLUE_L = '#1256B8', '#E8F0FB'
TEAL, TEAL_L = '#0E9888', '#E5F4F1'
ORG, ORG_L = '#D97706', '#FDF0E1'
PUR, PUR_L = '#6D4AC7', '#EFEAFB'
GRN, GRN_L = '#2E9E4F', '#E7F5EB'
RED, RED_L = '#B91C1C', '#FDEAEA'

def new_ax(w_in, h_in):
    fig = plt.figure(figsize=(w_in, h_in), dpi=300)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, w_in); ax.set_ylim(0, h_in); ax.axis('off')
    return fig, ax

def save(fig, name):
    fig.savefig(os.path.join(DST, name), dpi=300)
    plt.close(fig)
    print(name, 'ok')

# ============ 图 1：五层算法闭环——环形循环图 ============
W, H = 4.724, 3.94                     # 12cm × 10cm
fig, ax = new_ax(W, H)
cx, cy, R = W/2, H/2 + 0.12, 1.32
layers = [('① 测量', 'IRT 认知诊断', '能力参数 θ', BLUE, BLUE_L),
          ('② 建模', 'BKT / GKT', '掌握概率', TEAL, TEAL_L),
          ('③ 记忆', 'FSRS 调度', '复习到期日', GRN, GRN_L),
          ('④ 决策', 'MAB 探索利用', '资源与路径', ORG, ORG_L),
          ('⑤ 解释', 'LLM 数理化', '可读反馈', PUR, PUR_L)]
angles = [90 - k*72 for k in range(5)]          # 顺时针
nw, nh = 1.30, 0.66
pos = []
for (t, m, o, ec, fc), a in zip(layers, angles):
    a_rad = np.deg2rad(a)
    nx, ny = cx + R*np.cos(a_rad)*1.28, cy + R*np.sin(a_rad)
    pos.append((nx, ny))
    rbox = FancyBboxPatch((nx-nw/2, ny-nh/2), nw, nh,
                          boxstyle='round,pad=0,rounding_size=0.07',
                          fc=fc, ec=ec, lw=1.0)
    ax.add_patch(rbox)
    ax.text(nx, ny + 0.14, t, ha='center', va='center', fontsize=8.6,
            fontweight='bold', color=ec)
    ax.text(nx, ny - 0.05, m, ha='center', va='center', fontsize=6.6, color=INK)
    ax.text(nx, ny - 0.22, '→ ' + o, ha='center', va='center', fontsize=6.2, color=SUB)
# 顺时针曲线箭头（前 4 段沿环）
for k in range(5):
    a1 = np.deg2rad(angles[k] - 24)
    a2 = np.deg2rad(angles[k] - 48)
    x1, y1 = cx + R*np.cos(a1)*1.28, cy + R*np.sin(a1)
    x2, y2 = cx + R*np.cos(a2)*1.28, cy + R*np.sin(a2)
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), connectionstyle='arc3,rad=0.30',
                                 arrowstyle='-|>', mutation_scale=10, lw=1.0, color=SUB))
# 外环回流（⑤ → ①，虚线大弧）
a5 = np.deg2rad(90 - 4*72)
x5, y5 = cx + R*np.cos(a5)*1.28, cy + R*np.sin(a5) + nh/2 + 0.06
x1, y1 = cx, cy + R + nh/2 + 0.10
ax.add_patch(FancyArrowPatch((x5, y5), (x1, y1), connectionstyle='arc3,rad=-0.42',
                             arrowstyle='-|>', mutation_scale=10, lw=0.9,
                             linestyle=(0, (4, 2)), color=ORG))
ax.text(cx + 2.05, cy + 1.52, '行为数据回流', ha='center', va='center',
        fontsize=6.8, color='#B45309')
ax.text(cx + 2.05, cy + 1.34, '回灌模型再训练', ha='center', va='center',
        fontsize=6.8, color='#B45309')
# 中心标注
ax.text(cx, cy + 0.10, '五层算法闭环', ha='center', va='center',
        fontsize=9.5, fontweight='bold', color=INK)
ax.text(cx, cy - 0.14, '决策产生行为', ha='center', va='center', fontsize=6.6, color=SUB)
ax.text(cx, cy - 0.32, '行为沉淀为数据', ha='center', va='center', fontsize=6.6, color=SUB)
ax.text(cx, cy - 0.50, '数据回灌再训练', ha='center', va='center', fontsize=6.6, color=SUB)
save(fig, 'fig_loop.png')

# ============ 图 2：跨学科学习链路——三角网络图 ============
W, H = 5.512, 3.15                    # 14cm × 8cm
fig, ax = new_ax(W, H)
nodes = [('C 语言程序设计', '位运算 · 指针', BLUE, BLUE_L, (1.30, 2.50)),
         ('电路分析基础', '分压 · 戴维南', ORG, ORG_L, (4.21, 2.50)),
         ('STM32 嵌入式', '寄存器 · PWM', TEAL, TEAL_L, (2.756, 0.68))]
ew, eh = 1.72, 0.86
for t, s2, ec, fc, (nx, ny) in nodes:
    ax.add_patch(Ellipse((nx, ny), ew, eh, fc=fc, ec=ec, lw=1.0))
    ax.text(nx, ny + 0.13, t, ha='center', va='center', fontsize=7.8, fontweight='bold', color=ec)
    ax.text(nx, ny - 0.15, s2, ha='center', va='center', fontsize=6.3, color=INK)
edges = [(0, 1, '位运算 — 寄存器配置', '#8B5CF6', (2.756, 3.02)),
         (1, 2, '分压采样 — ADC 采集', '#0EA5E9', (4.72, 1.62)),
         (2, 0, '采样编程 — 中断控制', '#10B981', (0.80, 1.62))]
for a, b, lbl, col, (lx, ly) in edges:
    (xa, ya), (xb, yb) = nodes[a][4], nodes[b][4]
    ax.add_patch(FancyArrowPatch((xa, ya), (xb, yb), connectionstyle='arc3,rad=0.18',
                                 arrowstyle='<|-|>', mutation_scale=9, lw=0.9, color=col))
    ax.text(lx, ly, lbl, ha='center', va='center', fontsize=6.0, color=col)
pw, ph = 2.5, 0.66
px, py = W/2 - pw/2, 1.52
ax.add_patch(FancyBboxPatch((px, py), pw, ph, boxstyle='round,pad=0,rounding_size=0.06',
                            fc='#F0FDF4', ec=GRN, lw=1.0))
ax.text(px + pw/2, py + ph*0.64, '综合实战项目：智能温控风扇', ha='center', va='center',
        fontsize=7.6, fontweight='bold', color='#1E7A38')
ax.text(px + pw/2, py + ph*0.26, 'C 语言采样 → 分压电路 → PWM 调速', ha='center', va='center',
        fontsize=6.2, color=INK)
for t, s2, ec, fc, (nx, ny) in nodes:
    tx = min(max(nx, px + 0.35), px + pw - 0.35)
    if ny > py + ph:
        ax.add_patch(FancyArrowPatch((nx, ny - eh/2 - 0.02), (tx, py + ph + 0.02),
                     connectionstyle='arc3,rad=0.0', arrowstyle='-|>', mutation_scale=8,
                     lw=0.8, linestyle=(0, (3, 2)), color='#9CA3AF'))
    else:
        ax.add_patch(FancyArrowPatch((nx, ny + eh/2 + 0.02), (tx, py - 0.02),
                     connectionstyle='arc3,rad=0.0', arrowstyle='-|>', mutation_scale=8,
                     lw=0.8, linestyle=(0, (3, 2)), color='#9CA3AF'))
save(fig, 'fig_cross.png')

# ============ 图 3：防幻觉六道防线——闸门管道（雪佛龙） ============
W, H = 5.512, 1.95                    # 14cm × 5cm
fig, ax = new_ax(W, H)
guards = [('输入过滤', '敏感与注入\n规则过滤', RED, RED_L),
          ('Prompt 加固', '角色与格式\n约束', ORG, ORG_L),
          ('结构校验', 'JSON 字段\n完整性', '#B45309', '#FEF3C7'),
          ('代码校验', 'AST 语法\n静态解析', TEAL, TEAL_L),
          ('引用溯源', '知识点来源\n标注', BLUE, BLUE_L),
          ('自我纠错', '反思循环\n随开关生效', GRN, GRN_L)]
n = len(guards)
seg_w, body_h = 0.80, 0.86
x0, y0 = 0.06, 0.66
tip = 0.14                             # 雪佛龙尖角
for k, (t, s, ec, fc) in enumerate(guards):
    x = x0 + k * (seg_w + 0.03)
    pts = [(x, y0), (x + seg_w - tip, y0), (x + seg_w, y0 + body_h/2),
           (x + seg_w - tip, y0 + body_h), (x, y0 + body_h)]
    if k > 0:
        pts[0] = (x, y0); pts[4] = (x, y0 + body_h)
    ax.add_patch(Polygon(pts, closed=True, fc=fc, ec=ec, lw=0.8))
    ax.text(x + (seg_w - tip)/2 + (tip/2 if k > 0 else 0), y0 + body_h*0.72, t,
            ha='center', va='center', fontsize=7.0, fontweight='bold', color=ec)
    for li, ln in enumerate(s.split('\n')):
        ax.text(x + (seg_w - tip)/2 + (tip/2 if k > 0 else 0),
                y0 + body_h*0.40 - li*0.19, ln, ha='center', va='center',
                fontsize=5.9, color=INK)
# 末端可信输出
ex = x0 + n * (seg_w + 0.03)
ax.add_patch(FancyBboxPatch((ex, y0 + 0.16), 0.44, body_h - 0.32,
                            boxstyle='round,pad=0,rounding_size=0.05',
                            fc=GRN_L, ec=GRN, lw=1.0))
ax.text(ex + 0.22, y0 + body_h/2, '可信\n输出', ha='center', va='center',
        fontsize=6.8, fontweight='bold', color='#1E7A38')
ax.text(x0 + (ex - x0)/2, y0 - 0.16, '六道防线常驻主管线，逐层拦截幻觉',
        ha='center', va='center', fontsize=7.0, color=SUB)
save(fig, 'fig_guard.png')

# ============ 图 4：试点流程——时间轴 ============
W, H = 5.512, 1.72                    # 14cm × 4.4cm
fig, ax = new_ax(W, H)
steps = [('前测问卷', '小程序匿名填写', '第 0 天', BLUE),
         ('分组', '实验组 SY×4\n对照组 CK×4', '第 1 天', PUR),
         ('使用平台', '实验组学习\n对照组自学', '第 1-14 天', TEAL),
         ('后测问卷', '同量表同题目', '第 14 天', ORG),
         ('数据分析', '教师端一键导出', '第 15 天', GRN)]
y_line = 0.92
sx0, sx1 = 0.60, 4.92
ax.annotate('', xy=(sx1 + 0.18, y_line), xytext=(sx0 - 0.14, y_line),
            arrowprops=dict(arrowstyle='-|>', lw=1.4, color=INK))
n = len(steps)
xs = [sx0 + k * (sx1 - sx0) / (n - 1) for k in range(n)]
for k, (item, x) in enumerate(zip(steps, xs)):
    t, s, when, ec = item
    ax.add_patch(Circle((x, y_line), 0.115, fc='white', ec=ec, lw=1.4))
    ax.text(x, y_line, str(k + 1), ha='center', va='center', fontsize=8.5,
            fontweight='bold', color=ec)
    up = (k % 2 == 0)
    ty = y_line + (0.24 if up else -0.24)
    ax.plot([x, x], [y_line + (0.115 if up else -0.115), ty - (0.05 if up else -0.05)],
            color=SUB, lw=0.6)
    va = 'bottom' if up else 'top'
    ax.text(x, ty + (0.03 if up else -0.03), t, ha='center', va=va,
            fontsize=8.0, fontweight='bold', color=ec)
    for li, ln in enumerate(s.split('\n')):
        ax.text(x, ty + (0.24 if up else -0.24) + (li*0.17 if up else -li*0.17),
                ln, ha='center', va=va, fontsize=6.2, color=SUB)
    ax.text(x, ty + (0.62 if up else -0.62) + (0.17 if up else -0.17) * len(s.split('\n')),
            when, ha='center', va=va, fontsize=6.0, color='#9CA3AF')
ax.text(sx0 - 0.14, y_line - 0.42, '试点周期 1-2 周', ha='left', va='center',
        fontsize=6.8, color=SUB)
ax.text(sx1 + 0.18, y_line - 0.42, '产出：前后测对照 + 行为日志 + 试点报告',
        ha='right', va='center', fontsize=6.8, color=SUB)
save(fig, 'fig_pilot.png')

# ============ 图 5：记忆调度曲线（保留，微调图例位置） ============
fig = plt.figure(figsize=(4.0, 2.45), dpi=300)
ax = fig.add_axes([0.13, 0.20, 0.84, 0.72])
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
fsrs_x, fsrs_y = curve([1, 3.2, 8, 18.6], 9.5, 2.2)
fix_x, fix_y = curve([7, 14, 21, 28], 12.0, 1.0)
ax.plot(fsrs_x, fsrs_y, color=BLUE, lw=1.5, label='FSRS 个性化调度')
ax.plot(fix_x, fix_y, color='#9CA3AF', lw=1.2, ls='--', label='统一间隔复习')
ax.fill_between(fix_x, fix_y, fsrs_y[:len(fix_y)] if len(fsrs_y) >= len(fix_y) else fix_y,
                color=BLUE, alpha=0.06)
ax.axhline(60, color='#D1D5DB', lw=0.7, ls=':')
ax.text(29.8, 62.5, '可提取性 60%', ha='right', fontsize=6.2, color='#9CA3AF')
ax.set_xlabel('时间（天）', fontsize=7.2, color=INK)
ax.set_ylabel('可提取性（记忆保留率 %）', fontsize=7.2, color=INK)
ax.set_ylim(35, 103); ax.set_xlim(0, 30.5)
ax.tick_params(labelsize=6.5, colors=SUB)
for sp in ('top', 'right'): ax.spines[sp].set_visible(False)
ax.legend(fontsize=6.6, loc='upper right', frameon=False)
ax.set_title('FSRS 在遗忘临界点前安排复习，稳定性随复习递增（机制示意）',
             fontsize=7.0, color=INK, pad=4)
save(fig, 'fig_fsrs.png')
