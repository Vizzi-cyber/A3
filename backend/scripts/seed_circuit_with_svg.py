"""
电路原理课程种子脚本 - 含SVG电路图版本
基于水木珞研2027电气考研零基础课程讲义，为电路原理知识点填充完整的文档、代码示例、练习题和思维导图。
"""
import sqlite3
import os
import json

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "ai_learning_v2.db")

# ============================================================
# kp_e01: 电路模型和电路定律
# ============================================================
KP_E01_DOC = r"""# 电路模型和电路定律

## 一、电路和电路模型

**理想与现实：** 理想模型是将实际电路元件进行抽象简化后得到的数学模型。在电路分析中，我们使用理想电路元件来替代实际元件，这样可以简化分析计算。

**电路的基本构成：** 电路由电源（提供电能）、负载（消耗电能）和导线（连接各元件）三部分组成。

### 四种基本电路元件符号

<svg width="520" height="140" viewBox="0 0 520 140">
  <defs>
    <marker id="arr_e01" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
      <polygon points="0,0 8,3 0,6" fill="#333"/>
    </marker>
  </defs>
  <!-- 独立电压源 -->
  <text x="10" y="15" font-size="11" fill="#666">独立电压源</text>
  <line x1="40" y1="30" x2="40" y2="55" stroke="#333" stroke-width="2"/>
  <circle cx="40" cy="80" r="16" fill="none" stroke="#333" stroke-width="2"/>
  <text x="33" y="77" font-size="11">+</text>
  <text x="33" y="90" font-size="11">−</text>
  <line x1="40" y1="96" x2="40" y2="120" stroke="#333" stroke-width="2"/>

  <!-- 电阻 -->
  <text x="140" y="15" font-size="11" fill="#666">电阻</text>
  <line x1="170" y1="30" x2="170" y2="55" stroke="#333" stroke-width="2"/>
  <rect x="155" y="55" width="30" height="50" fill="none" stroke="#333" stroke-width="2"/>
  <text x="163" y="85" font-size="12" font-weight="bold">R</text>
  <line x1="170" y1="105" x2="170" y2="120" stroke="#333" stroke-width="2"/>

  <!-- 电容 -->
  <text x="270" y="15" font-size="11" fill="#666">电容</text>
  <line x1="300" y1="30" x2="300" y2="65" stroke="#333" stroke-width="2"/>
  <line x1="283" y1="65" x2="317" y2="65" stroke="#333" stroke-width="2.5"/>
  <line x1="283" y1="80" x2="317" y2="80" stroke="#333" stroke-width="2.5"/>
  <line x1="300" y1="80" x2="300" y2="120" stroke="#333" stroke-width="2"/>
  <text x="322" y="77" font-size="12" font-weight="bold">C</text>

  <!-- 电感 -->
  <text x="390" y="15" font-size="11" fill="#666">电感</text>
  <line x1="420" y1="30" x2="420" y2="50" stroke="#333" stroke-width="2"/>
  <path d="M420,50 C435,50 435,62 420,62 C405,62 405,74 420,74 C435,74 435,86 420,86 C405,86 405,98 420,98" fill="none" stroke="#333" stroke-width="2"/>
  <line x1="420" y1="98" x2="420" y2="120" stroke="#333" stroke-width="2"/>
  <text x="435" y="77" font-size="12" font-weight="bold">L</text>
</svg>

## 二、电路的基本物理量

### 电流
- **定义：** 单位时间内通过导体横截面的电荷量
- **公式：** $i = \frac{dq}{dt}$
- **单位：** 安培（A）

### 电压
- **定义：** 单位正电荷从a点移动到b点时电场力所做的功
- **公式：** $u_{ab} = \frac{dw}{dq}$
- **单位：** 伏特（V）

### 电流参考方向示例

<svg width="520" height="100" viewBox="0 0 520 100">
  <defs>
    <marker id="arr_ref" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
      <polygon points="0,0 8,3 0,6" fill="#333"/>
    </marker>
  </defs>
  <!-- 例1: I=2A -->
  <text x="10" y="15" font-size="10" fill="#666">I = 2A</text>
  <line x1="40" y1="25" x2="40" y2="45" stroke="#333" stroke-width="2"/>
  <rect x="25" y="45" width="30" height="30" fill="none" stroke="#333" stroke-width="2"/>
  <line x1="40" y1="75" x2="40" y2="95" stroke="#333" stroke-width="2"/>
  <line x1="50" y1="35" x2="50" y2="65" stroke="#333" stroke-width="1.5" marker-end="url(#arr_ref)"/>
  <text x="55" y="30" font-size="10">a</text>
  <text x="55" y="85" font-size="10">b</text>

  <!-- 例2: i=-5A -->
  <text x="340" y="15" font-size="10" fill="#666">i = −5A</text>
  <line x1="370" y1="25" x2="370" y2="45" stroke="#333" stroke-width="2"/>
  <rect x="355" y="45" width="30" height="30" fill="none" stroke="#333" stroke-width="2"/>
  <line x1="370" y1="75" x2="370" y2="95" stroke="#333" stroke-width="2"/>
  <line x1="380" y1="35" x2="380" y2="65" stroke="#333" stroke-width="1.5" marker-end="url(#arr_ref)"/>

  <!-- 例3: i=5A -->
  <text x="440" y="15" font-size="10" fill="#666">i = 5A</text>
  <line x1="470" y1="25" x2="470" y2="45" stroke="#333" stroke-width="2"/>
  <rect x="455" y="45" width="30" height="30" fill="none" stroke="#333" stroke-width="2"/>
  <line x1="470" y1="75" x2="470" y2="95" stroke="#333" stroke-width="2"/>
  <line x1="480" y1="35" x2="480" y2="65" stroke="#333" stroke-width="1.5" marker-end="url(#arr_ref)"/>
</svg>

## 三、基尔霍夫定律

### 基尔霍夫电流定律（KCL）
**内容：** 任一时刻，对任一节点，所有支路电流的代数和等于零。

$$\sum_{k=1}^{n} i_k = 0$$

### 基尔霍夫电压定律（KVL）
**内容：** 任一时刻，沿任一回路，所有支路电压的代数和等于零。

$$\sum_{k=1}^{n} u_k = 0$$

### KVL应用例题

<svg width="400" height="180" viewBox="0 0 400 180">
  <defs>
    <marker id="arr_kvl" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
      <polygon points="0,0 8,3 0,6" fill="#333"/>
    </marker>
  </defs>
  <!-- 电压源 Us -->
  <circle cx="60" cy="90" r="20" fill="none" stroke="#333" stroke-width="2"/>
  <text x="50" y="86" font-size="10">+</text>
  <text x="50" y="100" font-size="10">−</text>
  <text x="30" y="130" font-size="10">Us</text>

  <!-- 电阻 R1 -->
  <rect x="140" y="75" width="40" height="30" fill="none" stroke="#333" stroke-width="2"/>
  <text x="150" y="95" font-size="10">R1</text>

  <!-- 电阻 R2 -->
  <rect x="220" y="75" width="40" height="30" fill="none" stroke="#333" stroke-width="2"/>
  <text x="230" y="95" font-size="10">R2</text>

  <!-- 连接线 -->
  <line x1="60" y1="70" x2="60" y2="50" stroke="#333" stroke-width="2"/>
  <line x1="60" y1="50" x2="160" y2="50" stroke="#333" stroke-width="2"/>
  <line x1="160" y1="50" x2="160" y2="75" stroke="#333" stroke-width="2"/>
  <line x1="180" y1="90" x2="220" y2="90" stroke="#333" stroke-width="2"/>
  <line x1="260" y1="90" x2="320" y2="90" stroke="#333" stroke-width="2"/>
  <line x1="320" y1="90" x2="320" y2="130" stroke="#333" stroke-width="2"/>
  <line x1="320" y1="130" x2="60" y2="130" stroke="#333" stroke-width="2"/>
  <line x1="60" y1="110" x2="60" y2="130" stroke="#333" stroke-width="2"/>

  <!-- 电流方向 -->
  <line x1="80" y1="45" x2="100" y2="45" stroke="#333" stroke-width="1.5" marker-end="url(#arr_kvl)"/>
  <text x="85" y="40" font-size="10">I</text>
</svg>

## 四、功率计算

**功率公式：** $p = ui$

**关联参考方向下：** 吸收功率 $p = ui$

**能量计算：** $w = \int_{t_0}^{t} p \, dt$
"""

KP_E01_CODE = r"""// ========================================
// 例题1：KCL应用
// ========================================
// 题目：节点a连接4条支路，电流分别为
// i1=2A(流入), i2=3A(流出), i3=1A(流入), i4=?
// 由KCL: i1 - i2 + i3 - i4 = 0
// 2 - 3 + 1 - i4 = 0
// i4 = 0A

// ========================================
// 例题2：功率计算
// ========================================
// 题目：一个元件，电压u=10V，电流i=2A
// 关联参考方向下：p = ui = 10×2 = 20W
// 元件吸收20W功率

// ========================================
// 例题3：KVL应用
// ========================================
// 题目：回路包含电压源Vs=12V，电阻R1=2Ω，R2=4Ω
// 设电流为i(顺时针)
// KVL: -Vs + iR1 + iR2 = 0
// -12 + 2i + 4i = 0
// 6i = 12
// i = 2A
"""

KP_E01_QS = [
    {"q_id": "q_e01_1", "type": "single_choice", "content": "基尔霍夫电流定律（KCL）是指：",
     "options": [{"id": "A", "text": "任一时刻，沿任一回路，所有支路电压的代数和等于零"},
                 {"id": "B", "text": "任一时刻，对任一节点，所有支路电流的代数和等于零"},
                 {"id": "C", "text": "任一时刻，任一支路的电流等于该支路电压除以电阻"},
                 {"id": "D", "text": "任一时刻，电路中各点电位相等"}],
     "correct_answer": "B", "explanation": "KCL描述的是节点处电流的约束关系，流入节点的电流等于流出节点的电流。"},
    {"q_id": "q_e01_2", "type": "single_choice", "content": "在关联参考方向下，一个元件吸收的功率为：",
     "options": [{"id": "A", "text": "p = -ui"}, {"id": "B", "text": "p = ui"}, {"id": "C", "text": "p = u/i"}, {"id": "D", "text": "p = i/u"}],
     "correct_answer": "B", "explanation": "关联参考方向下，电流从电压正极流入，吸收功率p=ui。"},
    {"q_id": "q_e01_3", "type": "single_choice", "content": "理想电压源的特点是：",
     "options": [{"id": "A", "text": "输出电流恒定"}, {"id": "B", "text": "端电压恒定，与外电路无关"},
                 {"id": "C", "text": "内阻为无穷大"}, {"id": "D", "text": "只能提供功率，不能吸收功率"}],
     "correct_answer": "B", "explanation": "理想电压源的端电压恒定不变，与流过的电流和外电路无关。"},
]

KP_E01_MM = {
    "nodes": [
        {"id": "center", "label": "电路模型和电路定律"},
        {"id": "n1", "label": "电路基本概念"},
        {"id": "n2", "label": "基本物理量"},
        {"id": "n3", "label": "基尔霍夫定律"},
        {"id": "n4", "label": "电路元件"},
        {"id": "n5", "label": "功率与能量"},
    ],
    "edges": [
        {"source": "center", "target": "n1"},
        {"source": "center", "target": "n2"},
        {"source": "center", "target": "n3"},
        {"source": "center", "target": "n4"},
        {"source": "center", "target": "n5"},
    ]
}

# ============================================================
# kp_e02: 电阻电路的等效变换
# ============================================================
KP_E02_DOC = r"""# 电阻电路的等效变换

## 一、等效变换的概念

**等效变换的条件：** 两个电路，若具有相同的端口VCR（伏安特性），则它们对外电路是等效的。

**等效变换的目的：** 在不影响分析结果的前提下，简化电路结构。

## 二、电阻的串联和并联

### 电阻串联
<svg width="400" height="100" viewBox="0 0 400 100">
  <line x1="50" y1="50" x2="100" y2="50" stroke="#333" stroke-width="2"/>
  <rect x="100" y="35" width="40" height="30" fill="none" stroke="#333" stroke-width="2"/>
  <text x="110" y="55" font-size="10">R1</text>
  <line x1="140" y1="50" x2="180" y2="50" stroke="#333" stroke-width="2"/>
  <rect x="180" y="35" width="40" height="30" fill="none" stroke="#333" stroke-width="2"/>
  <text x="190" y="55" font-size="10">R2</text>
  <line x1="220" y1="50" x2="260" y2="50" stroke="#333" stroke-width="2"/>
  <rect x="260" y="35" width="40" height="30" fill="none" stroke="#333" stroke-width="2"/>
  <text x="270" y="55" font-size="10">R3</text>
  <line x1="300" y1="50" x2="350" y2="50" stroke="#333" stroke-width="2"/>
  <text x="150" y="85" font-size="10">Req = R1 + R2 + R3</text>
</svg>

**串联分压：** $u_k = \frac{R_k}{R_{eq}} u$

### 电阻并联
<svg width="400" height="120" viewBox="0 0 400 120">
  <line x1="50" y1="30" x2="50" y2="90" stroke="#333" stroke-width="2"/>
  <line x1="50" y1="30" x2="150" y2="30" stroke="#333" stroke-width="2"/>
  <line x1="50" y1="90" x2="150" y2="90" stroke="#333" stroke-width="2"/>

  <rect x="100" y="40" width="30" height="20" fill="none" stroke="#333" stroke-width="2"/>
  <text x="105" y="55" font-size="10">R1</text>
  <rect x="100" y="70" width="30" height="20" fill="none" stroke="#333" stroke-width="2"/>
  <text x="105" y="85" font-size="10">R2</text>

  <line x1="150" y1="30" x2="250" y2="30" stroke="#333" stroke-width="2"/>
  <line x1="150" y1="90" x2="250" y2="90" stroke="#333" stroke-width="2"/>
  <line x1="250" y1="30" x2="250" y2="90" stroke="#333" stroke-width="2"/>

  <text x="100" y="115" font-size="10">Req = (R1×R2)/(R1+R2)</text>
</svg>

**并联分流：** $i_k = \frac{G_k}{G_{eq}} i$

## 三、Y-Δ等效变换

### 变换公式
**Y → Δ：**
$$R_{12} = \frac{R_1R_2 + R_2R_3 + R_3R_1}{R_3}$$

**Δ → Y：**
$$R_1 = \frac{R_{12}R_{13}}{R_{12} + R_{23} + R_{13}}$$

## 四、电源的等效变换

**电压源串联电阻** 与 **电流源并联电阻** 可以相互等效变换。

**变换条件：**
$$I_S = \frac{U_S}{R_S}, \quad R_S = \frac{U_S}{I_S}$$
"""

KP_E02_CODE = r"""// ========================================
// 例题1：电阻串并联化简
// ========================================
// 题目：R1=10Ω与R2=15Ω并联，再与R3=5Ω串联
// 并联部分：R12 = (10×15)/(10+15) = 6Ω
// 总电阻：R = R12 + R3 = 6 + 5 = 11Ω

// ========================================
// 例题2：Y-Δ变换
// ========================================
// 题目：Y形网络 R1=1Ω, R2=2Ω, R3=3Ω
// 变换为Δ形网络：
// R12 = (1×2 + 2×3 + 3×1)/3 = 11/3 Ω

// ========================================
// 例题3：电源等效变换
// ========================================
// 题目：Us=10V电压源串联Rs=2Ω电阻
// 等效为电流源：Is = 10/2 = 5A
// 并联电阻仍为 Rs = 2Ω
"""

KP_E02_QS = [
    {"q_id": "q_e02_1", "type": "single_choice", "content": "两个电阻R1和R2并联的等效电阻为：",
     "options": [{"id": "A", "text": "R1 + R2"}, {"id": "B", "text": "R1 × R2"},
                 {"id": "C", "text": "(R1 × R2)/(R1 + R2)"}, {"id": "D", "text": "1/(R1 + R2)"}],
     "correct_answer": "C", "explanation": "两电阻并联等效电阻为乘积除以和。"},
    {"q_id": "q_e02_2", "type": "single_choice", "content": "Y-Δ等效变换的条件是：",
     "options": [{"id": "A", "text": "端口电流相等"}, {"id": "B", "text": "端口电压相等"},
                 {"id": "C", "text": "端口伏安特性相同"}, {"id": "D", "text": "电阻值相等"}],
     "correct_answer": "C", "explanation": "等效变换的核心是保持端口伏安特性不变。"},
    {"q_id": "q_e02_3", "type": "single_choice", "content": "电压源Us串联电阻Rs，等效为电流源时，电流源的电流Is为：",
     "options": [{"id": "A", "text": "Us × Rs"}, {"id": "B", "text": "Us / Rs"},
                 {"id": "C", "text": "Rs / Us"}, {"id": "D", "text": "Us + Rs"}],
     "correct_answer": "B", "explanation": "根据欧姆定律，Is = Us/Rs。"},
]

KP_E02_MM = {
    "nodes": [
        {"id": "center", "label": "电阻电路的等效变换"},
        {"id": "n1", "label": "等效变换概念"},
        {"id": "n2", "label": "串并联"},
        {"id": "n3", "label": "Y-Δ变换"},
        {"id": "n4", "label": "电源等效"},
    ],
    "edges": [
        {"source": "center", "target": "n1"},
        {"source": "center", "target": "n2"},
        {"source": "center", "target": "n3"},
        {"source": "center", "target": "n4"},
    ]
}

# ============================================================
# kp_e03-kp_e10: 保持原有内容
# ============================================================
# 为了简化，这里复用之前的内容
import sys
sys.path.insert(0, os.path.dirname(__file__))
from seed_circuit_content import (
    KP_E03_DOC, KP_E03_CODE, KP_E03_QS, KP_E03_MM,
    KP_E04_DOC, KP_E04_CODE, KP_E04_QS, KP_E04_MM,
    KP_E05_DOC, KP_E05_CODE, KP_E05_QS, KP_E05_MM,
    KP_E06_DOC, KP_E06_CODE, KP_E06_QS, KP_E06_MM,
    KP_E07_DOC, KP_E07_CODE, KP_E07_QS, KP_E07_MM,
    KP_E08_DOC, KP_E08_CODE, KP_E08_QS, KP_E08_MM,
    KP_E09_DOC, KP_E09_CODE, KP_E09_QS, KP_E09_MM,
    KP_E10_DOC, KP_E10_CODE, KP_E10_QS, KP_E10_MM,
)

# ============================================================
# 所有知识点数据
# ============================================================
ALL_KP = [
    ("kp_e01", "电路模型和电路定律", "电路原理", 0.3, [], "电路基本概念、KCL/KVL、电路元件、功率计算", ["电路", "KCL", "KVL"], KP_E01_DOC, KP_E01_CODE, KP_E01_QS, KP_E01_MM),
    ("kp_e02", "电阻电路的等效变换", "电路原理", 0.4, ["kp_e01"], "串并联、Y-Δ变换、电源等效变换", ["等效变换", "串并联"], KP_E02_DOC, KP_E02_CODE, KP_E02_QS, KP_E02_MM),
    ("kp_e03", "电阻电路的一般分析", "电路原理", 0.5, ["kp_e01", "kp_e02"], "支路电流法、网孔电流法、节点电压法", ["网孔", "节点"], KP_E03_DOC, KP_E03_CODE, KP_E03_QS, KP_E03_MM),
    ("kp_e04", "电路定理", "电路原理", 0.5, ["kp_e01", "kp_e02"], "叠加定理、戴维宁定理、诺顿定理、最大功率传输", ["叠加", "戴维宁"], KP_E04_DOC, KP_E04_CODE, KP_E04_QS, KP_E04_MM),
    ("kp_e05", "一阶电路的暂态分析", "电路原理", 0.55, ["kp_e01"], "换路定则、三要素法、RC/RL电路暂态", ["暂态", "三要素"], KP_E05_DOC, KP_E05_CODE, KP_E05_QS, KP_E05_MM),
    ("kp_e06", "二阶电路的暂态分析", "电路原理", 0.65, ["kp_e05"], "微分方程、过阻尼、欠阻尼、临界阻尼", ["二阶", "阻尼"], KP_E06_DOC, KP_E06_CODE, KP_E06_QS, KP_E06_MM),
    ("kp_e07", "正弦稳态电路分析", "电路原理", 0.6, ["kp_e01"], "相量表示、阻抗导纳、功率计算", ["相量", "阻抗"], KP_E07_DOC, KP_E07_CODE, KP_E07_QS, KP_E07_MM),
    ("kp_e08", "耦合电感和理想变压器", "电路原理", 0.65, ["kp_e07"], "互感、同名端、去耦等效、理想变压器", ["耦合", "变压器"], KP_E08_DOC, KP_E08_CODE, KP_E08_QS, KP_E08_MM),
    ("kp_e09", "三相电路", "电路原理", 0.6, ["kp_e07"], "三相电源、Y/Δ连接、三相功率", ["三相", "功率"], KP_E09_DOC, KP_E09_CODE, KP_E09_QS, KP_E09_MM),
    ("kp_e10", "频率响应", "电路原理", 0.7, ["kp_e07"], "传输函数、滤波器、谐振", ["滤波器", "谐振"], KP_E10_DOC, KP_E10_CODE, KP_E10_QS, KP_E10_MM),
]


def seed():
    db = os.path.abspath(DB_PATH)
    print(f"Database path: {db}")
    conn = sqlite3.connect(db)
    cur = conn.cursor()

    for kp in ALL_KP:
        kp_id, name, subject, diff, prereqs, desc, tags, doc, code, qs, mm = kp
        cur.execute("""
            UPDATE knowledge_points
            SET name=?, subject=?, difficulty=?, prerequisites=?,
                description=?, tags=?, document=?, code_example=?,
                questions=?, mindmap=?
            WHERE kp_id=?
        """, (name, subject, diff, json.dumps(prereqs, ensure_ascii=False),
              desc, json.dumps(tags, ensure_ascii=False),
              doc, code, json.dumps(qs, ensure_ascii=False),
              json.dumps(mm, ensure_ascii=False), kp_id))
        if cur.rowcount == 0:
            cur.execute("""
                INSERT INTO knowledge_points
                (kp_id, name, subject, difficulty, prerequisites, description, tags, document, code_example, questions, mindmap)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (kp_id, name, subject, diff, json.dumps(prereqs, ensure_ascii=False),
                  desc, json.dumps(tags, ensure_ascii=False),
                  doc, code, json.dumps(qs, ensure_ascii=False),
                  json.dumps(mm, ensure_ascii=False)))
        print(f"  [OK] {kp_id}: {name}")

    conn.commit()
    conn.close()
    print(f"\nDone! Updated/inserted {len(ALL_KP)} circuit theory knowledge points.")


if __name__ == "__main__":
    seed()
