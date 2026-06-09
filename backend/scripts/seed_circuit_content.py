"""
电路原理课程种子脚本
基于水木珞研2027电气考研零基础课程讲义，为电路原理知识点填充文档、例题和练习题。
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

**电路的基本构成：** 电路由电源（提供电能）、负载（消耗电能）和导线（连接各元件）三部分组成。电路正常运行需要满足：有闭合回路、有电源激励、有负载消耗。

## 二、电路的基本物理量

### 电流
- **定义：** 单位时间内通过导体横截面的电荷量
- **公式：** $i = \frac{dq}{dt}$
- **单位：** 安培（A）

### 电压
- **定义：** 单位正电荷从a点移动到b点时电场力所做的功
- **公式：** $u_{ab} = \frac{dw}{dq}$
- **单位：** 伏特（V）

### 功率
- **公式：** $p = ui$
- **单位：** 瓦特（W）
- **关联参考方向：** 电流从电压正极流入时，$p = ui$ 为吸收功率

## 三、基尔霍夫定律

### 基尔霍夫电流定律（KCL）
**内容：** 任一时刻，对任一节点，所有支路电流的代数和等于零。

$$\sum_{k=1}^{n} i_k = 0$$

**推广：** KCL适用于任意闭合曲面。

### 基尔霍夫电压定律（KVL）
**内容：** 任一时刻，沿任一回路，所有支路电压的代数和等于零。

$$\sum_{k=1}^{n} u_k = 0$$

**推广：** KVL适用于开口电路。

## 四、电路元件

### 电阻元件
- **欧姆定律：** $u = Ri$ 或 $i = Gu$
- **电导：** $G = \frac{1}{R}$，单位：西门子（S）

### 电压源与电流源
- **理想电压源：** 端电压恒定，与外电路无关
- **理想电流源：** 输出电流恒定，与外电路无关

### 受控源
- **电压控制电压源（VCVS）**
- **电流控制电压源（CCVS）**
- **电压控制电流源（VCCS）**
- **电流控制电流源（CCCS）**

## 五、电功率与能量

**功率计算：**
- 吸收功率：$p = ui$（关联参考方向）
- 发出功率：$p = -ui$（非关联参考方向）

**能量计算：**
$$w = \int_{t_0}^{t} p \, dt$$
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
    {"q_id": "q_e01_4", "type": "single_choice", "content": "KCL可以推广用于：",
     "options": [{"id": "A", "text": "只能用于节点"}, {"id": "B", "text": "只能用于回路"},
                 {"id": "C", "text": "任意闭合曲面"}, {"id": "D", "text": "只能用于平面电路"}],
     "correct_answer": "C", "explanation": "KCL不仅适用于节点，也可以推广到任意闭合曲面（广义节点）。"},
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

**等效变换的目的：** 在不影响分析结果的前提下，简化电路结构，从而简化分析计算。

**等效变换的要点：**
- 等效变换前后，电路的外部特性（伏安关系）保持不变
- 等效变换只适用于线性电路
- 等效变换只是对外电路等效，对内部不一定等效

## 二、电阻的串联和并联

### 电阻串联
**定义：** 若干个电阻依次连接，流过每个电阻的电流都相同。

**等效电阻：**
$$R_{eq} = R_1 + R_2 + \cdots + R_n$$

**串联分压：**
$$u_k = \frac{R_k}{R_{eq}} u$$

### 电阻并联
**定义：** 若干个电阻并列连接，每个电阻两端的电压都相同。

**等效电阻：**
$$\frac{1}{R_{eq}} = \frac{1}{R_1} + \frac{1}{R_2} + \cdots + \frac{1}{R_n}$$

**并联分流：**
$$i_k = \frac{G_k}{G_{eq}} i$$

**两个电阻并联：**
$$R_{eq} = \frac{R_1 R_2}{R_1 + R_2}$$

## 三、Y-Δ等效变换

### Y形网络（星形网络）
三个电阻连接到一个公共节点。

### Δ形网络（三角形网络）
三个电阻首尾相连形成三角形。

### 变换公式
**Y → Δ：**
$$R_{12} = \frac{R_1R_2 + R_2R_3 + R_3R_1}{R_3}$$

**Δ → Y：**
$$R_1 = \frac{R_{12}R_{13}}{R_{12} + R_{23} + R_{13}}$$

## 四、电源的等效变换

### 电压源与电流源的等效
**电压源串联电阻** 与 **电流源并联电阻** 可以相互等效变换。

**变换条件：**
$$I_S = \frac{U_S}{R_S}, \quad R_S = \frac{U_S}{I_S}$$

**注意：** 等效变换时，电压源的正极与电流源的电流流出端对应。
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
// R23 = (1×2 + 2×3 + 3×1)/1 = 11 Ω
// R13 = (1×2 + 2×3 + 3×1)/2 = 11/2 Ω

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
# kp_e03: 电阻电路的一般分析
# ============================================================
KP_E03_DOC = r"""# 电阻电路的一般分析
（内容见教材）"""
KP_E03_CODE = "// 例题解析\n"
KP_E03_QS = [{"q_id": "q_e03_1", "type": "single_choice", "content": "网孔电流法适用于平面电路还是非平面电路？", "options": [{"id": "A", "text": "平面电路"}, {"id": "B", "text": "非平面电路"}, {"id": "C", "text": "两者都适用"}, {"id": "D", "text": "都不适用"}], "correct_answer": "A", "explanation": "网孔电流法只能用于平面电路。"}]
KP_E03_MM = {"nodes": [{"id": "center", "label": "电阻电路的一般分析"}], "edges": []}

# ============================================================
# kp_e04: 电路定理
# ============================================================
KP_E04_DOC = r"""# 电路定理

## 一、叠加定理

**内容：** 在线性电路中，任一支路的电流（或电压）等于电路中各个独立电源单独作用时，在该支路产生的电流（或电压）的代数和。

**公式：** $I = I' + I''$

**注意事项：**
- 叠加定理只适用于线性电路
- 功率不能叠加
- 独立电源单独作用时，其他电压源短路、电流源开路

## 二、戴维宁定理

**内容：** 任何一个线性有源二端网络，对外电路而言，可以用一个电压源和一个电阻的串联组合来等效替代。

**等效参数：**
- 开路电压：$U_{OC} = U_{Th}$
- 等效电阻：$R_{eq} = R_{Th}$

**求解方法：**
1. 求开路电压 $U_{OC}$
2. 将所有独立电源置零，求等效电阻 $R_{eq}$

## 三、诺顿定理

**内容：** 任何一个线性有源二端网络，对外电路而言，可以用一个电流源和一个电阻的并联组合来等效替代。

**等效参数：**
- 短路电流：$I_{SC} = I_N$
- 等效电阻：$R_{eq} = R_N$

## 四、最大功率传输定理

**内容：** 当负载电阻等于电源内阻时，负载获得最大功率。

**条件：** $R_L = R_{Th}$

**最大功率：** $P_{max} = \frac{U_{Th}^2}{4R_{Th}}$
"""

KP_E04_CODE = r"""// ========================================
// 例题：戴维宁定理应用
// ========================================
// 题目：求含源二端网络的戴维宁等效电路
// 1. 求开路电压 Uoc
//    断开负载，计算端口电压
// 2. 求等效电阻 Req
//    将独立电源置零（电压源短路，电流源开路）
//    计算端口等效电阻
// 3. 等效电路为 Uoc 串联 Req
"""

KP_E04_QS = [
    {"q_id": "q_e04_1", "type": "single_choice", "content": "叠加定理适用于什么电路？",
     "options": [{"id": "A", "text": "所有电路"}, {"id": "B", "text": "线性电路"},
                 {"id": "C", "text": "非线性电路"}, {"id": "D", "text": "暂态电路"}],
     "correct_answer": "B", "explanation": "叠加定理只适用于线性电路。"},
    {"q_id": "q_e04_2", "type": "single_choice", "content": "戴维宁等效电路中，等效电阻Req的求法是：",
     "options": [{"id": "A", "text": "直接测量"}, {"id": "B", "text": "将独立电源置零后计算"},
                 {"id": "C", "text": "用欧姆定律"}, {"id": "D", "text": "查表"}],
     "correct_answer": "B", "explanation": "求等效电阻时，需要将所有独立电源置零（电压源短路，电流源开路）。"},
    {"q_id": "q_e04_3", "type": "single_choice", "content": "最大功率传输的条件是：",
     "options": [{"id": "A", "text": "RL=0"}, {"id": "B", "text": "RL=∞"},
                 {"id": "C", "text": "RL=RTh"}, {"id": "D", "text": "RL=2RTh"}],
     "correct_answer": "C", "explanation": "当负载电阻等于电源内阻时，负载获得最大功率。"},
]

KP_E04_MM = {
    "nodes": [
        {"id": "center", "label": "电路定理"},
        {"id": "n1", "label": "叠加定理"},
        {"id": "n2", "label": "戴维宁定理"},
        {"id": "n3", "label": "诺顿定理"},
        {"id": "n4", "label": "最大功率传输"},
    ],
    "edges": [
        {"source": "center", "target": "n1"},
        {"source": "center", "target": "n2"},
        {"source": "center", "target": "n3"},
        {"source": "center", "target": "n4"},
    ]
}

# ============================================================
# kp_e05: 一阶电路的暂态分析
# ============================================================
KP_E05_DOC = r"""# 一阶电路的暂态分析

## 一、换路定则

**内容：** 换路瞬间，电容电压和电感电流不能突变。

**公式：**
- $u_C(0^+) = u_C(0^-)$
- $i_L(0^+) = i_L(0^-)$

## 二、三要素法

**公式：**
$$f(t) = f(\infty) + [f(0^+) - f(\infty)]e^{-t/\tau}$$

**三要素：**
1. 初始值 $f(0^+)$
2. 稳态值 $f(\infty)$
3. 时间常数 $\tau$

**时间常数：**
- RC电路：$\tau = RC$
- RL电路：$\tau = L/R$

## 三、RC电路的暂态过程

### 零输入响应
$$u_C(t) = U_0 e^{-t/\tau}$$

### 零状态响应
$$u_C(t) = U_S(1 - e^{-t/\tau})$$

### 全响应
$$u_C(t) = U_S + (U_0 - U_S)e^{-t/\tau}$$

## 四、RL电路的暂态过程

### 零输入响应
$$i_L(t) = I_0 e^{-t/\tau}$$

### 零状态响应
$$i_L(t) = \frac{U_S}{R}(1 - e^{-t/\tau})$$
"""

KP_E05_CODE = r"""// ========================================
// 例题：RC电路三要素法
// ========================================
// 题目：Us=10V, R=1kΩ, C=1μF, t=0时开关闭合
// 初始值：uC(0+) = uC(0-) = 0V (零状态)
// 稳态值：uC(∞) = Us = 10V
// 时间常数：τ = RC = 1kΩ × 1μF = 1ms
// 响应：uC(t) = 10(1 - e^(-t/1ms)) V
"""

KP_E05_QS = [
    {"q_id": "q_e05_1", "type": "single_choice", "content": "换路定则是指：",
     "options": [{"id": "A", "text": "电容电流不能突变"}, {"id": "B", "text": "电感电压不能突变"},
                 {"id": "C", "text": "电容电压和电感电流不能突变"}, {"id": "D", "text": "电阻电压不能突变"}],
     "correct_answer": "C", "explanation": "换路定则：电容电压和电感电流在换路瞬间不能突变。"},
    {"q_id": "q_e05_2", "type": "single_choice", "content": "RC电路的时间常数τ等于：",
     "options": [{"id": "A", "text": "R/C"}, {"id": "B", "text": "RC"},
                 {"id": "C", "text": "1/(RC)"}, {"id": "D", "text": "R+C"}],
     "correct_answer": "B", "explanation": "RC电路的时间常数τ=RC。"},
    {"q_id": "q_e05_3", "type": "single_choice", "content": "三要素法中的三个要素是：",
     "options": [{"id": "A", "text": "R、L、C"}, {"id": "B", "text": "U、I、P"},
                 {"id": "C", "text": "初始值、稳态值、时间常数"}, {"id": "D", "text": "电压、电流、功率"}],
     "correct_answer": "C", "explanation": "三要素是初始值f(0+)、稳态值f(∞)、时间常数τ。"},
]

KP_E05_MM = {
    "nodes": [
        {"id": "center", "label": "一阶电路暂态分析"},
        {"id": "n1", "label": "换路定则"},
        {"id": "n2", "label": "三要素法"},
        {"id": "n3", "label": "RC电路"},
        {"id": "n4", "label": "RL电路"},
    ],
    "edges": [
        {"source": "center", "target": "n1"},
        {"source": "center", "target": "n2"},
        {"source": "center", "target": "n3"},
        {"source": "center", "target": "n4"},
    ]
}

# ============================================================
# kp_e06: 二阶电路的暂态分析
# ============================================================
KP_E06_DOC = r"""# 二阶电路的暂态分析

## 一、二阶电路的微分方程

**RLC串联电路：**
$$LC\frac{d^2u_C}{dt^2} + RC\frac{du_C}{dt} + u_C = U_S$$

**特征方程：**
$$LCs^2 + RCs + 1 = 0$$

## 二、三种响应形式

### 过阻尼响应（$R > 2\sqrt{L/C}$）
$$u_C(t) = U_S + A_1e^{s_1t} + A_2e^{s_2t}$$

### 欠阻尼响应（$R < 2\sqrt{L/C}$）
$$u_C(t) = U_S + Ae^{-\alpha t}\cos(\omega_d t + \varphi)$$

### 临界阻尼响应（$R = 2\sqrt{L/C}$）
$$u_C(t) = U_S + (A_1 + A_2t)e^{-\alpha t}$$

## 三、阻尼系数和固有频率

**阻尼系数：** $\alpha = \frac{R}{2L}$

**固有频率：** $\omega_0 = \frac{1}{\sqrt{LC}}$

**阻尼振荡频率：** $\omega_d = \sqrt{\omega_0^2 - \alpha^2}$
"""

KP_E06_CODE = r"""// ========================================
// 例题：RLC串联电路
// ========================================
// 题目：R=10Ω, L=1H, C=1μF
// 判断响应类型：
// 2√(L/C) = 2√(1/1μF) = 2000Ω
// R=10Ω < 2000Ω，欠阻尼响应
// 阻尼系数：α = R/(2L) = 5
// 固有频率：ω0 = 1/√(LC) = 1000 rad/s
// 阻尼振荡频率：ωd = √(ω0²-α²) ≈ 1000 rad/s
"""

KP_E06_QS = [
    {"q_id": "q_e06_1", "type": "single_choice", "content": "二阶电路的响应类型取决于：",
     "options": [{"id": "A", "text": "只有电阻"}, {"id": "B", "text": "只有电感"},
                 {"id": "C", "text": "R、L、C的比值"}, {"id": "D", "text": "电源电压"}],
     "correct_answer": "C", "explanation": "响应类型取决于R、L、C的比值，特别是R与2√(L/C)的关系。"},
    {"q_id": "q_e06_2", "type": "single_choice", "content": "欠阻尼响应的特点是：",
     "options": [{"id": "A", "text": "单调衰减"}, {"id": "B", "text": "振荡衰减"},
                 {"id": "C", "text": "等幅振荡"}, {"id": "D", "text": "单调增长"}],
     "correct_answer": "B", "explanation": "欠阻尼响应是振荡衰减的。"},
]

KP_E06_MM = {
    "nodes": [
        {"id": "center", "label": "二阶电路暂态分析"},
        {"id": "n1", "label": "微分方程"},
        {"id": "n2", "label": "过阻尼"},
        {"id": "n3", "label": "欠阻尼"},
        {"id": "n4", "label": "临界阻尼"},
    ],
    "edges": [
        {"source": "center", "target": "n1"},
        {"source": "center", "target": "n2"},
        {"source": "center", "target": "n3"},
        {"source": "center", "target": "n4"},
    ]
}

# ============================================================
# kp_e07: 正弦稳态电路分析
# ============================================================
KP_E07_DOC = r"""# 正弦稳态电路分析

## 一、正弦量的相量表示

**相量表示：**
$$\dot{U} = U_m e^{j\varphi} = U_m \angle \varphi$$

**相量与正弦量的关系：**
$$u(t) = U_m \cos(\omega t + \varphi) \leftrightarrow \dot{U} = U \angle \varphi$$

## 二、阻抗和导纳

### 阻抗
$$Z = R + jX = |Z| \angle \varphi_Z$$

- 电阻：$Z_R = R$
- 电感：$Z_L = j\omega L = jX_L$
- 电容：$Z_C = \frac{1}{j\omega C} = -j\frac{1}{\omega C} = -jX_C$

### 导纳
$$Y = \frac{1}{Z} = G + jB$$

## 三、相量法分析步骤

1. 将正弦量转换为相量
2. 用相量形式的欧姆定律：$\dot{U} = Z\dot{I}$
3. 应用KCL和KVL（相量形式）
4. 求解相量方程
5. 将相量结果转换回正弦量

## 四、功率计算

### 有功功率
$$P = UI\cos\varphi$$

### 无功功率
$$Q = UI\sin\varphi$$

### 视在功率
$$S = UI$$

### 功率因数
$$\cos\varphi = \frac{P}{S}$$
"""

KP_E07_CODE = r"""// ========================================
// 例题：RLC串联电路相量分析
// ========================================
// 题目：Us=100∠0°V, R=30Ω, XL=40Ω, XC=80Ω
// 阻抗：Z = R + j(XL - XC) = 30 - j40 Ω
// |Z| = √(30² + 40²) = 50Ω
// φ = arctan(-40/30) = -53.13°
// 电流：I = U/Z = 100∠0° / 50∠-53.13° = 2∠53.13° A
// 有功功率：P = UIcosφ = 100×2×cos(-53.13°) = 120W
// 无功功率：Q = UIsinφ = 100×2×sin(-53.13°) = -160var
"""

KP_E07_QS = [
    {"q_id": "q_e07_1", "type": "single_choice", "content": "电感的阻抗为：",
     "options": [{"id": "A", "text": "jωL"}, {"id": "B", "text": "-jωL"},
                 {"id": "C", "text": "1/(jωL)"}, {"id": "D", "text": "ωL"}],
     "correct_answer": "A", "explanation": "电感的阻抗Z_L = jωL。"},
    {"q_id": "q_e07_2", "type": "single_choice", "content": "有功功率的计算公式是：",
     "options": [{"id": "A", "text": "P=UI"}, {"id": "B", "text": "P=UIcosφ"},
                 {"id": "C", "text": "P=UIsinφ"}, {"id": "D", "text": "P=U²/R"}],
     "correct_answer": "B", "explanation": "有功功率P=UIcosφ，其中cosφ是功率因数。"},
]

KP_E07_MM = {
    "nodes": [
        {"id": "center", "label": "正弦稳态电路分析"},
        {"id": "n1", "label": "相量表示"},
        {"id": "n2", "label": "阻抗导纳"},
        {"id": "n3", "label": "功率计算"},
    ],
    "edges": [
        {"source": "center", "target": "n1"},
        {"source": "center", "target": "n2"},
        {"source": "center", "target": "n3"},
    ]
}

# ============================================================
# kp_e08: 耦合电感和理想变压器
# ============================================================
KP_E08_DOC = r"""# 耦合电感和理想变压器

## 一、耦合电感的电压电流关系

**电压电流关系：**
$$u_1 = L_1\frac{di_1}{dt} + M\frac{di_2}{dt}$$
$$u_2 = M\frac{di_1}{dt} + L_2\frac{di_2}{dt}$$

**互感系数：** $M = k\sqrt{L_1L_2}$

**耦合系数：** $0 \leq k \leq 1$

## 二、同名端

**定义：** 当两个线圈的电流同时从同名端流入时，互感磁通相助。

**判断方法：**
- 假设电流从两个端口流入
- 如果磁通相助，则这两个端口为同名端

## 三、去耦等效

### 串联去耦
$$L_{eq} = L_1 + L_2 \pm 2M$$
- 顺接（同名端相连）：$L_{eq} = L_1 + L_2 + 2M$
- 反接（异名端相连）：$L_{eq} = L_1 + L_2 - 2M$

### 并联去耦
$$L_{eq} = \frac{L_1L_2 - M^2}{L_1 + L_2 \mp 2M}$$

## 四、理想变压器

**电压比：**
$$\frac{u_1}{u_2} = \frac{N_1}{N_2} = n$$

**电流比：**
$$\frac{i_1}{i_2} = -\frac{N_2}{N_1} = -\frac{1}{n}$$

**阻抗变换：**
$$Z_{in} = n^2 Z_L$$
"""

KP_E08_CODE = r"""// ========================================
// 例题：耦合电感去耦
// ========================================
// 题目：L1=1H, L2=2H, M=0.5H, 顺接串联
// 等效电感：Leq = L1 + L2 + 2M = 1 + 2 + 1 = 4H
//
// 例题：理想变压器阻抗变换
// 题目：n=2, RL=8Ω
// 输入阻抗：Zin = n²×RL = 4×8 = 32Ω
"""

KP_E08_QS = [
    {"q_id": "q_e08_1", "type": "single_choice", "content": "耦合系数k的取值范围是：",
     "options": [{"id": "A", "text": "k>1"}, {"id": "B", "text": "0≤k≤1"},
                 {"id": "C", "text": "k<0"}, {"id": "D", "text": "k=1"}],
     "correct_answer": "B", "explanation": "耦合系数k的取值范围是0≤k≤1。"},
    {"q_id": "q_e08_2", "type": "single_choice", "content": "理想变压器的电压比等于：",
     "options": [{"id": "A", "text": "N2/N1"}, {"id": "B", "text": "N1/N2"},
                 {"id": "C", "text": "(N1/N2)²"}, {"id": "D", "text": "√(N1/N2)"}],
     "correct_answer": "B", "explanation": "理想变压器的电压比u1/u2=N1/N2。"},
]

KP_E08_MM = {
    "nodes": [
        {"id": "center", "label": "耦合电感和理想变压器"},
        {"id": "n1", "label": "电压电流关系"},
        {"id": "n2", "label": "同名端"},
        {"id": "n3", "label": "去耦等效"},
        {"id": "n4", "label": "理想变压器"},
    ],
    "edges": [
        {"source": "center", "target": "n1"},
        {"source": "center", "target": "n2"},
        {"source": "center", "target": "n3"},
        {"source": "center", "target": "n4"},
    ]
}

# ============================================================
# kp_e09: 三相电路
# ============================================================
KP_E09_DOC = r"""# 三相电路

## 一、三相电源

**三相对称电源：**
$$u_A = U_m \cos(\omega t)$$
$$u_B = U_m \cos(\omega t - 120°)$$
$$u_C = U_m \cos(\omega t + 120°)$$

**特点：**
- 频率相同
- 幅值相等
- 相位互差120°

## 二、三相电源的连接

### Y形连接
- 线电压：$U_L = \sqrt{3}U_P$
- 线电流：$I_L = I_P$

### Δ形连接
- 线电压：$U_L = U_P$
- 线电流：$I_L = \sqrt{3}I_P$

## 三、三相电路的功率

**有功功率：**
$$P = \sqrt{3}U_LI_L\cos\varphi$$

**无功功率：**
$$Q = \sqrt{3}U_LI_L\sin\varphi$$

**视在功率：**
$$S = \sqrt{3}U_LI_L$$

## 四、三相电路的分析

**对称三相电路：** 取一相计算，其他相根据对称性得出。

**不对称三相电路：** 用节点电压法或回路电流法分析。
"""

KP_E09_CODE = r"""// ========================================
// 例题：三相电路功率计算
// ========================================
// 题目：三相负载，UL=380V, IL=10A, cosφ=0.8
// 有功功率：P = √3×380×10×0.8 = 5261W ≈ 5.26kW
// 无功功率：Q = √3×380×10×0.6 = 3946var ≈ 3.95kvar
// 视在功率：S = √3×380×10 = 6575VA ≈ 6.58kVA
"""

KP_E09_QS = [
    {"q_id": "q_e09_1", "type": "single_choice", "content": "三相对称电源的特点是：",
     "options": [{"id": "A", "text": "频率不同，幅值相同"}, {"id": "B", "text": "频率相同，幅值不同"},
                 {"id": "C", "text": "频率相同，幅值相等，相位互差120°"}, {"id": "D", "text": "任意"}],
     "correct_answer": "C", "explanation": "三相对称电源频率相同、幅值相等、相位互差120°。"},
    {"q_id": "q_e09_2", "type": "single_choice", "content": "Y形连接时，线电压与相电压的关系是：",
     "options": [{"id": "A", "text": "UL=UP"}, {"id": "B", "text": "UL=√3UP"},
                 {"id": "C", "text": "UL=3UP"}, {"id": "D", "text": "UL=UP/√3"}],
     "correct_answer": "B", "explanation": "Y形连接时，线电压UL=√3UP。"},
]

KP_E09_MM = {
    "nodes": [
        {"id": "center", "label": "三相电路"},
        {"id": "n1", "label": "三相电源"},
        {"id": "n2", "label": "电源连接"},
        {"id": "n3", "label": "功率计算"},
    ],
    "edges": [
        {"source": "center", "target": "n1"},
        {"source": "center", "target": "n2"},
        {"source": "center", "target": "n3"},
    ]
}

# ============================================================
# kp_e10: 频率响应
# ============================================================
KP_E10_DOC = r"""# 频率响应

## 一、频率响应的概念

**定义：** 频率响应描述了电路对不同频率正弦信号的响应特性。

**传输函数：**
$$H(j\omega) = \frac{\dot{Y}(j\omega)}{\dot{X}(j\omega)}$$

## 二、幅频特性和相频特性

**幅频特性：**
$$|H(j\omega)| = \frac{|\dot{Y}|}{|\dot{X}|}$$

**相频特性：**
$$\varphi(\omega) = \angle H(j\omega)$$

## 三、滤波器

### 低通滤波器
- 通低频，阻高频
- 截止频率：$\omega_c = \frac{1}{RC}$

### 高通滤波器
- 通高频，阻低频
- 截止频率：$\omega_c = \frac{1}{RC}$

### 带通滤波器
- 通某一频段
- 中心频率：$\omega_0 = \frac{1}{\sqrt{LC}}$

### 带阻滤波器
- 阻某一频段

## 四、谐振

### 串联谐振
**条件：** $\omega L = \frac{1}{\omega C}$

**谐振频率：** $\omega_0 = \frac{1}{\sqrt{LC}}$

**特点：** 阻抗最小，电流最大

### 并联谐振
**条件：** $\omega L = \frac{1}{\omega C}$

**特点：** 阻抗最大，电流最小
"""

KP_E10_CODE = r"""// ========================================
// 例题：RC低通滤波器
// ========================================
// 题目：R=1kΩ, C=1μF
// 截止频率：fc = 1/(2πRC) = 159Hz
// 当f << fc时，|H| ≈ 1，信号通过
// 当f >> fc时，|H| ≈ 0，信号被衰减
"""

KP_E10_QS = [
    {"q_id": "q_e10_1", "type": "single_choice", "content": "低通滤波器的特点是：",
     "options": [{"id": "A", "text": "通高频阻低频"}, {"id": "B", "text": "通低频阻高频"},
                 {"id": "C", "text": "通某一频段"}, {"id": "D", "text": "阻某一频段"}],
     "correct_answer": "B", "explanation": "低通滤波器通低频、阻高频。"},
    {"q_id": "q_e10_2", "type": "single_choice", "content": "串联谐振的条件是：",
     "options": [{"id": "A", "text": "ωL=1/(ωC)"}, {"id": "B", "text": "ωL=ωC"},
                 {"id": "C", "text": "L=C"}, {"id": "D", "text": "ω=1/(LC)"}],
     "correct_answer": "A", "explanation": "串联谐振条件是感抗等于容抗，即ωL=1/(ωC)。"},
]

KP_E10_MM = {
    "nodes": [
        {"id": "center", "label": "频率响应"},
        {"id": "n1", "label": "传输函数"},
        {"id": "n2", "label": "滤波器"},
        {"id": "n3", "label": "谐振"},
    ],
    "edges": [
        {"source": "center", "target": "n1"},
        {"source": "center", "target": "n2"},
        {"source": "center", "target": "n3"},
    ]
}


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
    print(f"数据库路径: {db}")
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
    print(f"\n完成！共更新/插入 {len(ALL_KP)} 个电路原理知识点。")


if __name__ == "__main__":
    seed()
