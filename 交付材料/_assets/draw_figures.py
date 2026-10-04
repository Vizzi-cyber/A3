# -*- coding: utf-8 -*-
"""技术方案全部配图（设计系统：nature-figure NMI pastel + AIC 蓝）
物理尺寸画布：figsize = 插入宽度，字号 = 印刷字号，300dpi。
生成：架构图.png / fig_loop.png / fig_guard.png / fig_fsrs.png /
      fig_cross.png / fig_pilot.png （写入本目录 _assets/）
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

DST = os.path.dirname(os.path.abspath(__file__))

# ---- 设计系统（NMI pastel + AIC 蓝） ----
INK   = '#272727'
SUB   = '#606060'
FAINT = '#A8A8A8'
DEEP  = '#484878'
MID   = '#7884B4'
SOFT  = '#B4C0E4'
LILAC = '#E0E0F0'
AQUA  = '#E0F0F0'
PEACH = '#F0E0D0'
NEU_L = '#D8D8D8'
GREEN = '#2E9E44'
RED   = '#B64342'
GRN, GRN_L = GREEN, '#E7F5EB'
TEALC = '#42949E'
AMBER = '#E28E2C'
VIOL  = '#9A4D8E'
# 五层节点色（深描边/浅填充）
NODE = [
    ('#484878', '#E4E4F0'),   # 测量
    ('#7884B4', '#DCE0EF'),   # 建模
    ('#42949E', '#DFEFF1'),   # 记忆
    ('#E28E2C', '#FBEEDC'),   # 决策
    ('#9A4D8E', '#F2E7F0'),   # 解释
]

def new_ax(w_in, h_in):
    fig = plt.figure(figsize=(w_in, h_in), dpi=300)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, w_in); ax.set_ylim(0, h_in); ax.axis('off')
    return fig, ax

def shadow_box(ax, x, y, w, h, ec, fc, lw=1.0, rounding=0.06, shadow=True):
    if shadow:
        ax.add_patch(FancyBboxPatch((x + 0.022, y - 0.028), w, h,
                     boxstyle=f'round,pad=0,rounding_size={rounding}',
                     fc='#484878', ec='none', alpha=0.10))
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                 boxstyle=f'round,pad=0,rounding_size={rounding}',
                 fc=fc, ec=ec, lw=lw))

def arr(ax, x1, y1, x2, y2, color=SUB, lw=1.0, ms=9):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='-|>', lw=lw, color=color, mutation_scale=ms))

def save(fig, name):
    fig.savefig(os.path.join(DST, name), dpi=300)
    plt.close(fig)
    print(name, 'ok')

# ================= 架构图（四层，层彩底 + 描边层标签 + 白模块） =================
W, H = 5.906, 4.70
fig, ax = new_ax(W, H)
LX, LW = 0.06, 1.06
BX = 1.22
BW = W - BX - 0.05
EC = INK

def band(top, h, name, sub, tint, edge):
    y = top - h
    ax.add_patch(Rectangle((BX, y), BW, h, fc='white', ec=edge, lw=1.0))
    ax.add_patch(Rectangle((BX, y + h - 0.045), BW, 0.045, fc=edge, ec='none'))
    ax.add_patch(Rectangle((LX, y), LW, h, fc=tint, ec=edge, lw=1.0))
    ax.text(LX + LW/2, y + h/2 + (0.10 if sub else 0), name, ha='center', va='center',
            fontsize=9.5, fontweight='bold', color=edge, family='SimHei')
    if sub:
        for k, ln in enumerate(sub.split('\n')):
            ax.text(LX + LW/2, y + h/2 - 0.11 - k*0.17, ln, ha='center', va='center',
                    fontsize=6.8, color=INK, family='SimHei')

def brow(y, h, items, edge, tsize=8.0, ssize=6.8, gap=0.10, pad=0.08):
    n = len(items)
    bw = (BW - pad*2 - gap*(n-1)) / n
    y = y - h
    for k, it in enumerate(items):
        x = BX + pad + k * (bw + gap)
        ax.add_patch(Rectangle((x, y), bw, h, fc='white', ec=edge, lw=0.7))
        if len(it) > 1:
            ax.text(x + bw/2, y + h*0.64, it[0], ha='center', va='center',
                    fontsize=tsize, fontweight='bold', color=INK, family='SimHei')
            ax.text(x + bw/2, y + h*0.28, it[1], ha='center', va='center',
                    fontsize=ssize, color=SUB)
        else:
            ax.text(x + bw/2, y + h/2, it[0], ha='center', va='center',
                    fontsize=tsize, color=INK, family='SimHei')

band(4.65, 0.90, '展示层', '前端 React + TS', LILAC, DEEP)
brow(4.60, 0.78, [('学习路径', '含跨学科视图'), ('电路仿真', 'MNA + RK4 暂态'),
                  ('故障诊断实验', 'STM32 实训'), ('试点数据分析', '班级对比')], DEEP)
band(3.58, 0.90, '应用层', '业务服务', AQUA, TEALC)
brow(3.53, 0.78, [('学习闭环', '测·学·练·修'), ('游戏化激励', '徽章·排行'),
                  ('教师备课工作台', '组卷·学情'), ('试点报告', '一键导出')], TEALC)
band(2.50, 1.44, '算法层', '五层算法闭环\n12 智能体', PEACH, AMBER)
brow(2.43, 0.72, [('① 测量', 'IRT（1PL/2PL）'), ('② 建模', 'BKT / GKT'),
                  ('③ 记忆', 'FSRS'), ('④ 决策', 'MAB'),
                  ('⑤ 解释', 'LLM 数理化')], AMBER, tsize=7.8, ssize=6.6, gap=0.22)
brow(1.62, 0.60, [('ADPP 自适应\nDAG 路径规划', None), ('趋势预警\n（L2 逻辑回归）', None),
                  ('12 个 AI 智能体\nLangGraph 星型拓扑', None)], AMBER, tsize=7.4, gap=0.10)
band(0.92, 0.95, '数据层', 'SQLite / PostgreSQL', '#E4E4F0', DEEP)
brow(0.87, 0.78, [('knowledge_points', '35 个/跨课程关联'), ('courses', '学科元数据'),
                  ('learning_records', '学习行为流水'), ('quiz_results', '测验成绩'),
                  ('experiment_logs', '实验日志')], DEEP, tsize=6.6, ssize=6.6, gap=0.07)
save(fig, '架构图.png')

# ================= 图：五层算法闭环——环形循环图 =================
W, H = 4.724, 3.94
fig, ax = new_ax(W, H)
cx, cy, R = W/2, H/2 + 0.12, 1.32
layers = [('① 测量', 'IRT 认知诊断', '能力参数 θ'),
          ('② 建模', 'BKT / GKT', '掌握概率'),
          ('③ 记忆', 'FSRS 调度', '复习到期日'),
          ('④ 决策', 'MAB 探索利用', '资源与路径'),
          ('⑤ 解释', 'LLM 数理化', '可读反馈')]
angles = [90 - k*72 for k in range(5)]
nw, nh = 1.30, 0.66
for k, ((t, m, o), a) in enumerate(zip(layers, angles)):
    a_rad = np.deg2rad(a)
    nx, ny = cx + R*np.cos(a_rad)*1.28, cy + R*np.sin(a_rad)
    ec, fc = NODE[k]
    shadow_box(ax, nx - nw/2, ny - nh/2, nw, nh, ec, fc, lw=1.0, rounding=0.07, shadow=False)
    ax.text(nx, ny + 0.14, t, ha='center', va='center', fontsize=8.6,
            fontweight='bold', color=ec)
    ax.text(nx, ny - 0.05, m, ha='center', va='center', fontsize=6.6, color=INK)
    ax.text(nx, ny - 0.22, '→ ' + o, ha='center', va='center', fontsize=6.2, color=SUB)
for k in range(5):
    a1 = np.deg2rad(angles[k] - 24)
    a2 = np.deg2rad(angles[k] - 48)
    x1, y1 = cx + R*np.cos(a1)*1.28, cy + R*np.sin(a1)
    x2, y2 = cx + R*np.cos(a2)*1.28, cy + R*np.sin(a2)
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), connectionstyle='arc3,rad=0.30',
                                 arrowstyle='-|>', mutation_scale=10, lw=1.0, color=MID))
a5 = np.deg2rad(90 - 4*72)
x5, y5 = cx + R*np.cos(a5)*1.28, cy + R*np.sin(a5) + nh/2 + 0.06
x1, y1 = cx, cy + R + nh/2 + 0.10
ax.add_patch(FancyArrowPatch((x5, y5), (x1, y1), connectionstyle='arc3,rad=-0.42',
                             arrowstyle='-|>', mutation_scale=10, lw=0.9,
                             linestyle=(0, (4, 2)), color=AMBER))
ax.text(cx + 2.05, cy + 1.52, '行为数据回流', ha='center', va='center',
        fontsize=6.8, color='#B45309')
ax.text(cx + 2.05, cy + 1.34, '回灌模型再训练', ha='center', va='center',
        fontsize=6.8, color='#B45309')
ax.text(cx, cy + 0.10, '五层算法闭环', ha='center', va='center',
        fontsize=9.5, fontweight='bold', color=DEEP)
ax.text(cx, cy - 0.14, '决策产生行为', ha='center', va='center', fontsize=6.6, color=SUB)
ax.text(cx, cy - 0.32, '行为沉淀为数据', ha='center', va='center', fontsize=6.6, color=SUB)
ax.text(cx, cy - 0.50, '数据回灌再训练', ha='center', va='center', fontsize=6.6, color=SUB)
save(fig, 'fig_loop.png')

# ================= 图：防幻觉六道防线——闸门管道 =================
W, H = 5.512, 1.95
fig, ax = new_ax(W, H)
guards = [('输入过滤', '敏感与注入\n规则过滤'),
          ('Prompt 加固', '角色与格式\n约束'),
          ('结构校验', 'JSON 字段\n完整性'),
          ('代码校验', 'AST 语法\n静态解析'),
          ('引用溯源', '知识点来源\n标注'),
          ('自我纠错', '反思循环\n随开关生效')]
n = len(guards)
seg_w, body_h = 0.80, 0.86
x0, y0 = 0.06, 0.66
tip = 0.14
chev_fill = [DEEP, '#5C5C94', MID, '#9AA4C8', SOFT, '#C9D0E8']
for k, (t, s) in enumerate(guards):
    x = x0 + k * (seg_w + 0.03)
    pts = [(x, y0), (x + seg_w - tip, y0), (x + seg_w, y0 + body_h/2),
           (x + seg_w - tip, y0 + body_h), (x, y0 + body_h)]
    if k > 0:
        pts[0] = (x, y0); pts[4] = (x, y0 + body_h)
    tc = 'white' if k < 3 else DEEP
    ax.add_patch(Polygon(pts, closed=True, fc=chev_fill[k], ec='white', lw=0.8))
    ax.text(x + (seg_w - tip)/2 + (tip/2 if k > 0 else 0), y0 + body_h*0.74, t,
            ha='center', va='center', fontsize=7.0, fontweight='bold', color=tc)
    for li, ln in enumerate(s.split('\n')):
        ax.text(x + (seg_w - tip)/2 + (tip/2 if k > 0 else 0),
                y0 + body_h*0.42 - li*0.19, ln, ha='center', va='center',
                fontsize=5.9, color=INK if k >= 3 else '#E8EAF6')
ex = x0 + n * (seg_w + 0.03) - 0.03
ax.add_patch(FancyBboxPatch((ex, y0 + 0.14), 0.46, body_h - 0.28,
                            boxstyle='round,pad=0,rounding_size=0.05',
                            fc='#E7F5EB', ec=GREEN, lw=1.0))
ax.text(ex + 0.25, y0 + body_h/2, '可信\n输出', ha='center', va='center',
        fontsize=6.8, fontweight='bold', color=GREEN)
ax.text(x0 + (ex - x0)/2, y0 - 0.16, '六道防线常驻主管线，逐层拦截幻觉',
        ha='center', va='center', fontsize=7.0, color=SUB)
save(fig, 'fig_guard.png')

# ================= 图：记忆调度机制示意 =================
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
ax.plot(fsrs_x, fsrs_y, color=DEEP, lw=1.5, label='FSRS 个性化调度')
ax.plot(fix_x, fix_y, color=FAINT, lw=1.2, ls='--', label='统一间隔复习')
ax.fill_between(fix_x, fix_y, fsrs_y[:len(fix_y)], color=SOFT, alpha=0.30)
ax.axhline(60, color=NEU_L, lw=0.7, ls=':')
ax.text(29.8, 62.5, '可提取性 60%', ha='right', fontsize=6.2, color=FAINT)
ax.set_xlabel('时间（天）', fontsize=7.2, color=INK)
ax.set_ylabel('可提取性（记忆保留率 %）', fontsize=7.2, color=INK)
ax.set_ylim(35, 103); ax.set_xlim(0, 30.5)
ax.tick_params(labelsize=6.5, colors=SUB)
for sp in ('top', 'right'): ax.spines[sp].set_visible(False)
ax.legend(fontsize=6.6, loc='upper right', frameon=False)
ax.set_title('FSRS 在遗忘临界点前安排复习，稳定性随复习递增（机制示意）',
             fontsize=7.0, color=INK, pad=4)
save(fig, 'fig_fsrs.png')

# ================= 图：跨学科学习链路——三角网络图 =================
W, H = 5.512, 3.55
fig, ax = new_ax(W, H)
nodes = [('C 语言程序设计', '位运算 · 指针', DEEP, LILAC, (1.25, 2.85)),
         ('电路分析基础', '分压 · 戴维南', AMBER, PEACH, (4.26, 2.85)),
         ('STM32 嵌入式', '寄存器 · PWM', TEALC, AQUA, (2.756, 0.62))]
ew, eh = 1.72, 0.86
for t, s2, ec, fc, (nx, ny) in nodes:
    shadow_box(ax, nx - ew/2, ny - eh/2, ew, eh, ec, fc, lw=1.0, rounding=0.30, shadow=False)
    ax.text(nx, ny + 0.13, t, ha='center', va='center', fontsize=7.8, fontweight='bold', color=ec)
    ax.text(nx, ny - 0.15, s2, ha='center', va='center', fontsize=6.3, color=INK)
edges = [(0, 1, '位运算 — 寄存器配置', VIOL, (2.756, 3.42)),
         (1, 2, '分压采样 — ADC 采集', TEALC, (4.90, 1.95)),
         (2, 0, '采样编程 — 中断控制', GRN, (0.62, 1.95))]
for a, b, lbl, col, (lx, ly) in edges:
    (xa, ya), (xb, yb) = nodes[a][4], nodes[b][4]
    ax.add_patch(FancyArrowPatch((xa, ya), (xb, yb), connectionstyle='arc3,rad=0.18',
                                 arrowstyle='<|-|>', mutation_scale=9, lw=0.9, color=col))
    ax.text(lx, ly, lbl, ha='center', va='center', fontsize=6.0, color=col)
pw, ph = 2.5, 0.66
px, py = W/2 - pw/2, 1.55
shadow_box(ax, px, py, pw, ph, GREEN, '#E7F5EB', lw=1.0, rounding=0.08, shadow=False)
ax.text(px + pw/2, py + ph*0.64, '综合实战项目：智能温控风扇', ha='center', va='center',
        fontsize=7.6, fontweight='bold', color='#1E7A38')
ax.text(px + pw/2, py + ph*0.26, 'C 语言采样 → 分压电路 → PWM 调速', ha='center', va='center',
        fontsize=6.2, color=INK)
for t, s2, ec, fc, (nx, ny) in nodes:
    tx = min(max(nx, px + 0.35), px + pw - 0.35)
    if ny > py + ph:
        ax.add_patch(FancyArrowPatch((nx, ny - eh/2 - 0.02), (tx, py + ph + 0.02),
                     connectionstyle='arc3,rad=0.0', arrowstyle='-|>', mutation_scale=8,
                     lw=0.8, linestyle=(0, (3, 2)), color=FAINT))
    else:
        ax.add_patch(FancyArrowPatch((nx, ny + eh/2 + 0.02), (tx, py - 0.02),
                     connectionstyle='arc3,rad=0.0', arrowstyle='-|>', mutation_scale=8,
                     lw=0.8, linestyle=(0, (3, 2)), color=FAINT))
save(fig, 'fig_cross.png')

# ================= 图：试点流程——时间轴 =================
W, H = 5.512, 1.72
fig, ax = new_ax(W, H)
steps = [('前测问卷', '小程序匿名填写', '第 0 天', DEEP, LILAC),
         ('分组', '实验组 SY×4\n对照组 CK×4', '第 1 天', VIOL, '#F2E7F0'),
         ('使用平台', '实验组学习\n对照组自学', '第 1-14 天', TEALC, AQUA),
         ('后测问卷', '同量表同题目', '第 14 天', AMBER, PEACH),
         ('数据分析', '教师端一键导出', '第 15 天', '#1E7A38', '#E7F5EB')]
y_line = 0.92
sx0, sx1 = 0.60, 4.92
ax.annotate('', xy=(sx1 + 0.18, y_line), xytext=(sx0 - 0.14, y_line),
            arrowprops=dict(arrowstyle='-|>', lw=1.4, color=INK))
n = len(steps)
xs = [sx0 + k * (sx1 - sx0) / (n - 1) for k in range(n)]
for k, (item, x) in enumerate(zip(steps, xs)):
    t, s, when, ec, fc = item
    ax.add_patch(Circle((x, y_line), 0.125, fc=fc, ec=ec, lw=1.4))
    ax.text(x, y_line, str(k + 1), ha='center', va='center', fontsize=8.5,
            fontweight='bold', color=ec)
    up = (k % 2 == 0)
    ty = y_line + (0.24 if up else -0.24)
    ax.plot([x, x], [y_line + (0.125 if up else -0.125), ty - (0.05 if up else -0.05)],
            color=SUB, lw=0.6)
    va = 'bottom' if up else 'top'
    ax.text(x, ty + (0.03 if up else -0.03), t, ha='center', va=va,
            fontsize=8.0, fontweight='bold', color=ec)
    for li, ln in enumerate(s.split('\n')):
        ax.text(x, ty + (0.24 if up else -0.24) + (li*0.17 if up else -li*0.17),
                ln, ha='center', va=va, fontsize=6.2, color=SUB)
    ax.text(x, ty + (0.62 if up else -0.62) + (0.17 if up else -0.17) * len(s.split('\n')),
            when, ha='center', va=va, fontsize=6.0, color=FAINT)
ax.text(sx0 - 0.14, y_line - 0.42, '试点周期 1-2 周', ha='left', va='center',
        fontsize=6.8, color=SUB)
ax.text(sx1 + 0.18, y_line - 0.42, '产出：前后测对照 + 行为日志 + 试点报告',
        ha='right', va='center', fontsize=6.8, color=SUB)
save(fig, 'fig_pilot.png')
