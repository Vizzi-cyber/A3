"""
资源种子数据脚本 —— 为 resource_tasks 表填充排版清晰的中文示例数据
覆盖：C语言（讲义/导图/练习/代码）+ 电路分析（讲义/导图/练习）

运行方式：
    cd backend && python scripts/seed_resource_data.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from datetime import datetime, timedelta
import json

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.database import Base
from app.models.knowledge import ResourceTaskModel

engine = create_engine("sqlite:///./ai_learning_v2.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# 清空旧的 resource_tasks
db.query(ResourceTaskModel).delete()
db.commit()
print("已清空旧 resource_tasks 数据")

# =====================================================================
#  种子数据定义
# =====================================================================

SEED_TASKS = [
    # =================================================================
    #  C语言 —— 课程讲义
    # =================================================================
    {
        "title": "C语言指针详解 —— 从入门到精通",
        "resource_type": "document",
        "subject": "C语言",
        "difficulty": "medium",
        "resources": {
            "document": """# C语言指针详解 —— 从入门到精通

## 一、什么是指针？

指针是一个变量，其值是另一个变量的地址。简单来说，指针"指向"内存中的某个位置。

```c
int a = 10;       // 普通变量
int *p = &a;      // 指针变量，存储 a 的地址
printf("%d", *p); // 通过指针访问 a 的值 → 输出 10
```

## 二、指针的声明与初始化

| 语法 | 含义 |
|------|------|
| `int *p` | 声明一个指向 int 的指针 |
| `p = &a` | 将 a 的地址赋给 p |
| `*p` | 解引用，获取 p 指向的值 |

## 三、指针与数组

数组名本身就是首元素的地址，因此数组和指针密切相关：

```c
int arr[] = {1, 2, 3, 4, 5};
int *p = arr;       // p 指向 arr[0]
printf("%d", *(p + 2));  // 输出 arr[2] = 3
```

## 四、指针与函数

### 4.1 指针作为函数参数（传址调用）

```c
void swap(int *a, int *b) {
    int temp = *a;
    *a = *b;
    *b = temp;
}

int main() {
    int x = 5, y = 10;
    swap(&x, &y);
    printf("x=%d, y=%d", x, y);  // x=10, y=5
    return 0;
}
```

### 4.2 函数返回指针

```c
int* find_max(int *arr, int len) {
    int max_idx = 0;
    for (int i = 1; i < len; i++) {
        if (arr[i] > arr[max_idx]) max_idx = i;
    }
    return &arr[max_idx];
}
```

## 五、常见陷阱

1. **野指针**：未初始化的指针，指向随机内存地址
2. **悬挂指针**：指向已释放内存的指针
3. **内存泄漏**：malloc 后未 free

> 💡 **最佳实践**：始终在声明指针时初始化为 NULL，使用前检查是否为 NULL。
"""
        },
    },
    {
        "title": "C语言函数与递归 —— 模块化编程基础",
        "resource_type": "document",
        "subject": "C语言",
        "difficulty": "easy",
        "resources": {
            "document": """# C语言函数与递归 —— 模块化编程基础

## 一、函数的基本概念

函数是一段具有特定功能的代码块，通过函数可以实现代码复用和模块化。

### 函数声明

```c
// 返回类型 函数名(参数列表);
int add(int a, int b);
void print_hello(void);
```

### 函数定义

```c
int add(int a, int b) {
    return a + b;
}
```

## 二、参数传递

C语言只有**值传递**，没有引用传递。要修改外部变量，需要传递指针：

```c
void increment(int *p) {
    (*p)++;
}

int main() {
    int num = 5;
    increment(&num);
    printf("%d", num);  // 输出 6
    return 0;
}
```

## 三、递归

递归是函数调用自身的编程技巧，必须有**终止条件**。

### 经典例子：阶乘

```c
int factorial(int n) {
    if (n <= 1) return 1;       // 终止条件
    return n * factorial(n - 1); // 递归调用
}
```

### 经典例子：斐波那契数列

```c
int fibonacci(int n) {
    if (n == 0) return 0;
    if (n == 1) return 1;
    return fibonacci(n - 1) + fibonacci(n - 2);
}
```

## 四、作用域与生命周期

| 类型 | 作用域 | 生命周期 |
|------|--------|----------|
| 局部变量 | 函数内部 | 函数调用期间 |
| 全局变量 | 整个文件 | 程序运行期间 |
| static 变量 | 函数内部 | 程序运行期间 |

## 五、练习建议

1. 先掌握函数的声明、定义和调用
2. 理解值传递和指针传递的区别
3. 从简单递归开始，逐步理解递归思维
"""
        },
    },
    {
        "title": "C语言数组与字符串 —— 数据组织基础",
        "resource_type": "document",
        "subject": "C语言",
        "difficulty": "easy",
        "resources": {
            "document": """# C语言数组与字符串 —— 数据组织基础

## 一、一维数组

数组是相同类型元素的集合，存储在连续内存空间中。

```c
int arr[5] = {10, 20, 30, 40, 50};
printf("%d", arr[2]);  // 输出 30（下标从0开始）
```

### 数组遍历

```c
for (int i = 0; i < 5; i++) {
    printf("arr[%d] = %d\\n", i, arr[i]);
}
```

## 二、二维数组

```c
int matrix[3][4] = {
    {1,  2,  3,  4},
    {5,  6,  7,  8},
    {9, 10, 11, 12}
};
printf("%d", matrix[1][2]);  // 输出 7
```

## 三、字符串

C语言中没有专门的字符串类型，使用字符数组 + `\\0` 结尾：

```c
char name[] = "Hello";  // 长度为 6（含 \\0）
char greeting[20];
strcpy(greeting, "Hello, World!");
```

### 常用字符串函数（#include <string.h>）

| 函数 | 功能 | 示例 |
|------|------|------|
| `strlen(s)` | 获取长度 | `strlen("Hello")` → 5 |
| `strcpy(dest, src)` | 复制字符串 | `strcpy(a, b)` |
| `strcat(dest, src)` | 拼接字符串 | `strcat(a, b)` |
| `strcmp(s1, s2)` | 比较字符串 | 返回 0 表示相等 |

## 四、数组作为函数参数

```c
void print_array(int arr[], int len) {
    for (int i = 0; i < len; i++) {
        printf("%d ", arr[i]);
    }
}
```

> ⚠️ 数组传参时退化为指针，不会传递数组长度，需要额外参数指定。
"""
        },
    },

    # =================================================================
    #  C语言 —— 知识导图
    # =================================================================
    {
        "title": "C语言指针知识导图",
        "resource_type": "mindmap",
        "subject": "C语言",
        "difficulty": "medium",
        "resources": {
            "mindmap": {
                "root": "C语言指针",
                "children": [
                    {
                        "name": "基础概念",
                        "children": [
                            {"name": "什么是指针"},
                            {"name": "指针的声明与初始化"},
                            {"name": "取地址运算符 &"},
                            {"name": "解引用运算符 *"},
                        ],
                    },
                    {
                        "name": "指针运算",
                        "children": [
                            {"name": "指针加减"},
                            {"name": "指针比较"},
                            {"name": "指针与数组的关系"},
                        ],
                    },
                    {
                        "name": "指针与函数",
                        "children": [
                            {"name": "指针作为参数（传址调用）"},
                            {"name": "指针作为返回值"},
                            {"name": "函数指针"},
                        ],
                    },
                    {
                        "name": "多级指针",
                        "children": [
                            {"name": "二级指针 int **pp"},
                            {"name": "指针数组 int *arr[]"},
                        ],
                    },
                    {
                        "name": "常见陷阱",
                        "children": [
                            {"name": "野指针"},
                            {"name": "悬挂指针"},
                            {"name": "内存泄漏"},
                            {"name": "空指针解引用"},
                        ],
                    },
                ],
            },
        },
    },
    {
        "title": "C语言函数与递归知识导图",
        "resource_type": "mindmap",
        "subject": "C语言",
        "difficulty": "easy",
        "resources": {
            "mindmap": {
                "root": "C语言函数与递归",
                "children": [
                    {
                        "name": "函数基础",
                        "children": [
                            {"name": "函数声明（原型）"},
                            {"name": "函数定义"},
                            {"name": "函数调用"},
                            {"name": "返回值"},
                        ],
                    },
                    {
                        "name": "参数传递",
                        "children": [
                            {"name": "值传递"},
                            {"name": "指针传递（传址）"},
                            {"name": "数组传参"},
                        ],
                    },
                    {
                        "name": "递归",
                        "children": [
                            {"name": "递归三要素"},
                            {"name": "阶乘"},
                            {"name": "斐波那契数列"},
                            {"name": "汉诺塔"},
                        ],
                    },
                    {
                        "name": "作用域",
                        "children": [
                            {"name": "局部变量"},
                            {"name": "全局变量"},
                            {"name": "static 变量"},
                        ],
                    },
                ],
            },
        },
    },

    # =================================================================
    #  C语言 —— 练习题
    # =================================================================
    {
        "title": "C语言指针专项练习",
        "resource_type": "questions",
        "subject": "C语言",
        "difficulty": "medium",
        "resources": {
            "questions": [
                {
                    "q_id": "q_ptr_01",
                    "type": "single_choice",
                    "content": "以下代码的输出结果是什么？\n\nint a = 5;\nint *p = &a;\n*p = 10;\nprintf(\"%d\", a);",
                    "options": [
                        {"id": "A", "text": "5"},
                        {"id": "B", "text": "10"},
                        {"id": "C", "text": "地址值"},
                        {"id": "D", "text": "编译错误"},
                    ],
                    "correct_answer": "B",
                    "explanation": "p 指向 a 的地址，*p = 10 相当于 a = 10，所以输出 10。",
                },
                {
                    "q_id": "q_ptr_02",
                    "type": "single_choice",
                    "content": "以下哪个是正确的指针声明？",
                    "options": [
                        {"id": "A", "text": "int p*;"},
                        {"id": "B", "text": "int *p;"},
                        {"id": "C", "text": "int &p;"},
                        {"id": "D", "text": "pointer<int> p;"},
                    ],
                    "correct_answer": "B",
                    "explanation": "C语言中声明指针使用 int *p; 的语法，* 放在变量名前。",
                },
                {
                    "q_id": "q_ptr_03",
                    "type": "single_choice",
                    "content": "指针变量存储的是什么？",
                    "options": [
                        {"id": "A", "text": "变量的值"},
                        {"id": "B", "text": "变量的地址"},
                        {"id": "C", "text": "变量的类型"},
                        {"id": "D", "text": "变量的大小"},
                    ],
                    "correct_answer": "B",
                    "explanation": "指针变量存储的是另一个变量的内存地址，通过解引用 * 可以访问该地址上的值。",
                },
            ],
        },
    },
    {
        "title": "C语言函数与递归练习",
        "resource_type": "questions",
        "subject": "C语言",
        "difficulty": "easy",
        "resources": {
            "questions": [
                {
                    "q_id": "q_func_01",
                    "type": "single_choice",
                    "content": "C语言中函数参数传递的方式是？",
                    "options": [
                        {"id": "A", "text": "只能值传递"},
                        {"id": "B", "text": "只能引用传递"},
                        {"id": "C", "text": "值传递和引用传递都可以"},
                        {"id": "D", "text": "指针传递"},
                    ],
                    "correct_answer": "A",
                    "explanation": "C语言只有值传递。要实现类似引用传递的效果，需要传递指针。",
                },
                {
                    "q_id": "q_func_02",
                    "type": "single_choice",
                    "content": "递归函数必须包含什么？",
                    "options": [
                        {"id": "A", "text": "循环语句"},
                        {"id": "B", "text": "终止条件"},
                        {"id": "C", "text": "全局变量"},
                        {"id": "D", "text": "指针参数"},
                    ],
                    "correct_answer": "B",
                    "explanation": "递归函数必须有终止条件（也叫基线条件），否则会导致无限递归和栈溢出。",
                },
                {
                    "q_id": "q_func_03",
                    "type": "single_choice",
                    "content": "以下哪个函数声明是正确的？",
                    "options": [
                        {"id": "A", "text": "int add(a, b);"},
                        {"id": "B", "text": "int add(int a, int b)"},
                        {"id": "C", "text": "int add(int, int);"},
                        {"id": "D", "text": "add(int a, int b) int;"},
                    ],
                    "correct_answer": "C",
                    "explanation": "函数声明需要指定参数类型，参数名可选。正确写法：int add(int, int);",
                },
            ],
        },
    },
    {
        "title": "C语言数组与字符串练习",
        "resource_type": "questions",
        "subject": "C语言",
        "difficulty": "easy",
        "resources": {
            "questions": [
                {
                    "q_id": "q_arr_01",
                    "type": "single_choice",
                    "content": "C语言数组的下标从几开始？",
                    "options": [
                        {"id": "A", "text": "1"},
                        {"id": "B", "text": "0"},
                        {"id": "C", "text": "-1"},
                        {"id": "D", "text": "取决于编译器"},
                    ],
                    "correct_answer": "B",
                    "explanation": "C语言数组下标从 0 开始，arr[0] 是第一个元素。",
                },
                {
                    "q_id": "q_arr_02",
                    "type": "single_choice",
                    "content": "以下代码的输出是？\n\nchar s[] = \"Hello\";\nprintf(\"%lu\", strlen(s));",
                    "options": [
                        {"id": "A", "text": "5"},
                        {"id": "B", "text": "6"},
                        {"id": "C", "text": "4"},
                        {"id": "D", "text": "编译错误"},
                    ],
                    "correct_answer": "A",
                    "explanation": "strlen 返回字符串的字符个数，不包含结尾的 \\0，所以是 5。",
                },
                {
                    "q_id": "q_arr_03",
                    "type": "single_choice",
                    "content": "以下哪个能正确定义一个包含 5 个 int 元素的数组？",
                    "options": [
                        {"id": "A", "text": "int arr(5);"},
                        {"id": "B", "text": "int arr[5];"},
                        {"id": "C", "text": "int arr{5};"},
                        {"id": "D", "text": "int[5] arr;"},
                    ],
                    "correct_answer": "B",
                    "explanation": "C语言使用方括号 [] 定义数组：int arr[5];",
                },
            ],
        },
    },

    # =================================================================
    #  C语言 —— 代码示例
    # =================================================================
    {
        "title": "C语言指针实战 —— 交换两个变量的值",
        "resource_type": "code",
        "subject": "C语言",
        "difficulty": "easy",
        "resources": {
            "code": """#include <stdio.h>

// 通过指针交换两个变量的值
void swap(int *a, int *b) {
    int temp = *a;
    *a = *b;
    *b = temp;
}

int main() {
    int x = 10, y = 20;
    printf("交换前: x = %d, y = %d\\n", x, y);

    swap(&x, &y);

    printf("交换后: x = %d, y = %d\\n", x, y);
    return 0;
}

/* 输出：
交换前: x = 10, y = 20
交换后: x = 20, y = 10
*/""",
        },
    },
    {
        "title": "C语言递归 —— 求阶乘和斐波那契数列",
        "resource_type": "code",
        "subject": "C语言",
        "difficulty": "medium",
        "resources": {
            "code": """#include <stdio.h>

// 递归求阶乘
long factorial(int n) {
    if (n <= 1) return 1;
    return n * factorial(n - 1);
}

// 递归求斐波那契数列第 n 项
int fibonacci(int n) {
    if (n == 0) return 0;
    if (n == 1) return 1;
    return fibonacci(n - 1) + fibonacci(n - 2);
}

int main() {
    printf("5! = %ld\\n", factorial(5));
    printf("斐波那契前10项: ");
    for (int i = 0; i < 10; i++) {
        printf("%d ", fibonacci(i));
    }
    printf("\\n");
    return 0;
}

/* 输出：
5! = 120
斐波那契前10项: 0 1 1 2 3 5 8 13 21 34
*/""",
        },
    },
    {
        "title": "C语言数组操作 —— 冒泡排序",
        "resource_type": "code",
        "subject": "C语言",
        "difficulty": "medium",
        "resources": {
            "code": """#include <stdio.h>

// 冒泡排序（升序）
void bubble_sort(int arr[], int len) {
    for (int i = 0; i < len - 1; i++) {
        int swapped = 0;
        for (int j = 0; j < len - 1 - i; j++) {
            if (arr[j] > arr[j + 1]) {
                int temp = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = temp;
                swapped = 1;
            }
        }
        if (!swapped) break;  // 优化：无交换说明已有序
    }
}

void print_array(int arr[], int len) {
    for (int i = 0; i < len; i++) {
        printf("%d ", arr[i]);
    }
    printf("\\n");
}

int main() {
    int arr[] = {64, 34, 25, 12, 22, 11, 90};
    int len = sizeof(arr) / sizeof(arr[0]);

    printf("排序前: ");
    print_array(arr, len);

    bubble_sort(arr, len);

    printf("排序后: ");
    print_array(arr, len);
    return 0;
}

/* 输出：
排序前: 64 34 25 12 22 11 90
排序后: 11 12 22 25 34 64 90
*/""",
        },
    },

    # =================================================================
    #  电路分析 —— 课程讲义
    # =================================================================
    {
        "title": "电路基本定律 —— 欧姆定律与基尔霍夫定律",
        "resource_type": "document",
        "subject": "电路分析",
        "difficulty": "easy",
        "resources": {
            "document": """# 电路基本定律 —— 欧姆定律与基尔霍夫定律

## 一、欧姆定律

欧姆定律描述了电阻两端电压与通过电流的关系：

$$V = IR$$

其中：
- **V** —— 电压（单位：伏特 V）
- **I** —— 电流（单位：安培 A）
- **R** —— 电阻（单位：欧姆 Ω）

### 示例

一个 10Ω 的电阻，两端电压为 5V，则通过的电流为：
$$I = \\frac{V}{R} = \\frac{5}{10} = 0.5A$$

## 二、基尔霍夫电流定律（KCL）

**KCL**：对于任意节点，流入电流之和等于流出电流之和。

$$\\sum I_{in} = \\sum I_{out}$$

> 这是电荷守恒的体现：节点处不会积累电荷。

### 示例

节点处有三条支路，电流分别为 I₁=3A（流入）、I₂=1A（流入）、I₃（流出），则：
$$I_3 = I_1 + I_2 = 3 + 1 = 4A$$

## 三、基尔霍夫电压定律（KVL）

**KVL**：沿任意闭合回路，电压升之和等于电压降之和。

$$\\sum V_{rise} = \\sum V_{drop}$$

> 这是能量守恒的体现：电荷绕闭合回路一周，电势能变化为零。

### 示例

一个回路包含电源 E=12V 和两个电阻 R₁=4Ω、R₂=8Ω 串联，回路电流为：
$$I = \\frac{E}{R_1 + R_2} = \\frac{12}{4 + 8} = 1A$$

## 四、功率计算

$$P = VI = I^2R = \\frac{V^2}{R}$$

- **P > 0**：元件吸收功率（负载）
- **P < 0**：元件发出功率（电源）
"""
        },
    },
    {
        "title": "电路等效变换 —— 串并联与星三角",
        "resource_type": "document",
        "subject": "电路分析",
        "difficulty": "medium",
        "resources": {
            "document": """# 电路等效变换 —— 串并联与星三角

## 一、电阻串联

多个电阻首尾相连，流过同一电流：

$$R_{eq} = R_1 + R_2 + R_3 + ...$$

### 特点
- 流过每个电阻的电流相同
- 总电压等于各电阻电压之和

## 二、电阻并联

多个电阻并列连接，两端电压相同：

$$\\frac{1}{R_{eq}} = \\frac{1}{R_1} + \\frac{1}{R_2} + ...$$

两个电阻并联的简化公式：
$$R_{eq} = \\frac{R_1 \\cdot R_2}{R_1 + R_2}$$

### 特点
- 每个电阻两端电压相同
- 总电流等于各支路电流之和

## 三、星形-三角形（Y-Δ）变换

### Δ → Y 变换

$$R_1 = \\frac{R_{12} \\cdot R_{13}}{R_{12} + R_{23} + R_{13}}$$

$$R_2 = \\frac{R_{12} \\cdot R_{23}}{R_{12} + R_{23} + R_{13}}$$

$$R_3 = \\frac{R_{13} \\cdot R_{23}}{R_{12} + R_{23} + R_{13}}$$

### Y → Δ 变换

$$R_{12} = \\frac{R_1 R_2 + R_2 R_3 + R_3 R_1}{R_3}$$

## 四、等效电源定理

### 戴维南定理
任意线性二端网络可用一个电压源 Vth 和串联电阻 Rth 等效。

### 诺顿定理
任意线性二端网络可用一个电流源 In 和并联电阻 Rn 等效。

$$V_{th} = I_n \\cdot R_n, \\quad R_{th} = R_n$$
"""
        },
    },
    {
        "title": "正弦稳态电路分析 —— 相量法基础",
        "resource_type": "document",
        "subject": "电路分析",
        "difficulty": "hard",
        "resources": {
            "document": """# 正弦稳态电路分析 —— 相量法基础

## 一、正弦信号的基本概念

正弦电压/电流的一般表达式：

$$v(t) = V_m \\cos(\\omega t + \\phi)$$

其中：
- **Vₘ** —— 振幅（峰值）
- **ω** —— 角频率（rad/s），ω = 2πf
- **φ** —— 初相位
- **f** —— 频率（Hz）

## 二、相量表示法

将正弦信号用复数表示，简化稳态分析：

$$\\dot{V} = V_m e^{j\\phi} = V_m \\cos\\phi + jV_m \\sin\\phi$$

### 有效值相量

$$\\dot{V}_{eff} = \\frac{V_m}{\\sqrt{2}} e^{j\\phi}$$

## 三、阻抗与导纳

### 基本元件的阻抗

| 元件 | 阻抗 Z | 特点 |
|------|--------|------|
| 电阻 R | R | 实数，电压电流同相 |
| 电感 L | jωL | 纯虚数，电压超前电流 90° |
| 电容 C | 1/(jωC) | 纯虚数，电流超前电压 90° |

### 串联阻抗

$$Z_{eq} = Z_1 + Z_2 + Z_3 + ...$$

### 并联阻抗

$$\\frac{1}{Z_{eq}} = \\frac{1}{Z_1} + \\frac{1}{Z_2} + ...$$

## 四、功率计算

### 瞬时功率
$$p(t) = v(t) \\cdot i(t)$$

### 平均功率（有功功率）
$$P = V_{eff} I_{eff} \\cos\\phi$$

### 无功功率
$$Q = V_{eff} I_{eff} \\sin\\phi$$

### 视在功率
$$S = V_{eff} I_{eff} = \\sqrt{P^2 + Q^2}$$

### 功率因数
$$\\cos\\phi = \\frac{P}{S}$$

## 五、谐振

串联 RLC 电路谐振条件：ωL = 1/(ωC)，此时阻抗最小，电流最大。
"""
        },
    },

    # =================================================================
    #  电路分析 —— 知识导图
    # =================================================================
    {
        "title": "电路基本定律知识导图",
        "resource_type": "mindmap",
        "subject": "电路分析",
        "difficulty": "easy",
        "resources": {
            "mindmap": {
                "root": "电路基本定律",
                "children": [
                    {
                        "name": "欧姆定律",
                        "children": [
                            {"name": "V = IR"},
                            {"name": "适用条件：线性电阻"},
                            {"name": "功率 P = VI"},
                        ],
                    },
                    {
                        "name": "基尔霍夫定律",
                        "children": [
                            {
                                "name": "KCL（电流定律）",
                                "children": [
                                    {"name": "节点电流守恒"},
                                    {"name": "ΣI_in = ΣI_out"},
                                ],
                            },
                            {
                                "name": "KVL（电压定律）",
                                "children": [
                                    {"name": "回路电压守恒"},
                                    {"name": "ΣV_rise = ΣV_drop"},
                                ],
                            },
                        ],
                    },
                    {
                        "name": "功率",
                        "children": [
                            {"name": "P = VI"},
                            {"name": "P = I²R"},
                            {"name": "P = V²/R"},
                        ],
                    },
                ],
            },
        },
    },
    {
        "title": "电路等效变换知识导图",
        "resource_type": "mindmap",
        "subject": "电路分析",
        "difficulty": "medium",
        "resources": {
            "mindmap": {
                "root": "电路等效变换",
                "children": [
                    {
                        "name": "电阻连接",
                        "children": [
                            {"name": "串联：R_eq = R1 + R2"},
                            {"name": "并联：1/R_eq = 1/R1 + 1/R2"},
                        ],
                    },
                    {
                        "name": "星三角变换",
                        "children": [
                            {"name": "Δ → Y"},
                            {"name": "Y → Δ"},
                            {"name": "对称情况简化"},
                        ],
                    },
                    {
                        "name": "等效电源",
                        "children": [
                            {"name": "戴维南定理"},
                            {"name": "诺顿定理"},
                            {"name": "两者互换"},
                        ],
                    },
                    {
                        "name": "叠加定理",
                        "children": [
                            {"name": "线性电路适用"},
                            {"name": "分别计算各电源贡献"},
                            {"name": "代数求和"},
                        ],
                    },
                ],
            },
        },
    },

    # =================================================================
    #  电路分析 —— 练习题
    # =================================================================
    {
        "title": "电路基本定律练习",
        "resource_type": "questions",
        "subject": "电路分析",
        "difficulty": "easy",
        "resources": {
            "questions": [
                {
                    "q_id": "q_ckt_01",
                    "type": "single_choice",
                    "content": "一个 20Ω 电阻两端电压为 10V，通过的电流为多少？",
                    "options": [
                        {"id": "A", "text": "0.5A"},
                        {"id": "B", "text": "2A"},
                        {"id": "C", "text": "200A"},
                        {"id": "D", "text": "5A"},
                    ],
                    "correct_answer": "A",
                    "explanation": "根据欧姆定律 I = V/R = 10/20 = 0.5A。",
                },
                {
                    "q_id": "q_ckt_02",
                    "type": "single_choice",
                    "content": "基尔霍夫电流定律（KCL）体现了什么守恒？",
                    "options": [
                        {"id": "A", "text": "能量守恒"},
                        {"id": "B", "text": "电荷守恒"},
                        {"id": "C", "text": "动量守恒"},
                        {"id": "D", "text": "质量守恒"},
                    ],
                    "correct_answer": "B",
                    "explanation": "KCL 说明流入节点的电流等于流出节点的电流，体现了电荷守恒。",
                },
                {
                    "q_id": "q_ckt_03",
                    "type": "single_choice",
                    "content": "两个电阻 R₁=6Ω 和 R₂=3Ω 并联，等效电阻为？",
                    "options": [
                        {"id": "A", "text": "9Ω"},
                        {"id": "B", "text": "2Ω"},
                        {"id": "C", "text": "18Ω"},
                        {"id": "D", "text": "4.5Ω"},
                    ],
                    "correct_answer": "B",
                    "explanation": "并联公式：R_eq = (R₁×R₂)/(R₁+R₂) = (6×3)/(6+3) = 18/9 = 2Ω。",
                },
            ],
        },
    },
    {
        "title": "正弦稳态电路练习",
        "resource_type": "questions",
        "subject": "电路分析",
        "difficulty": "hard",
        "resources": {
            "questions": [
                {
                    "q_id": "q_sine_01",
                    "type": "single_choice",
                    "content": "电感的阻抗为 jωL，其物理含义是？",
                    "options": [
                        {"id": "A", "text": "电压与电流同相"},
                        {"id": "B", "text": "电压超前电流 90°"},
                        {"id": "C", "text": "电流超前电压 90°"},
                        {"id": "D", "text": "电压滞后电流 90°"},
                    ],
                    "correct_answer": "B",
                    "explanation": "电感阻抗为纯虚数 jωL，j 表示相位超前 90°，即电压超前电流 90°。",
                },
                {
                    "q_id": "q_sine_02",
                    "type": "single_choice",
                    "content": "串联 RLC 电路谐振时，电路呈什么特性？",
                    "options": [
                        {"id": "A", "text": "阻抗最大"},
                        {"id": "B", "text": "阻抗最小，呈纯电阻性"},
                        {"id": "C", "text": "电流最小"},
                        {"id": "D", "text": "功率因数为 0"},
                    ],
                    "correct_answer": "B",
                    "explanation": "谐振时 ωL = 1/(ωC)，感抗和容抗相互抵消，总阻抗最小且为纯电阻 R。",
                },
                {
                    "q_id": "q_sine_03",
                    "type": "single_choice",
                    "content": "功率因数 cosφ 表示什么？",
                    "options": [
                        {"id": "A", "text": "有功功率与视在功率的比值"},
                        {"id": "B", "text": "无功功率与视在功率的比值"},
                        {"id": "C", "text": "电压与电流的比值"},
                        {"id": "D", "text": "电阻与阻抗的比值"},
                    ],
                    "correct_answer": "A",
                    "explanation": "cosφ = P/S，即有功功率与视在功率的比值，反映电能利用效率。",
                },
            ],
        },
    },

    # =================================================================
    #  C语言 —— 扩展阅读
    # =================================================================
    {
        "title": "C语言发展历史与应用领域",
        "resource_type": "reading",
        "subject": "C语言",
        "difficulty": "easy",
        "resources": {
            "document": """# C语言发展历史与应用领域

## 一、C语言的诞生

1972 年，**Dennis Ritchie** 在贝尔实验室开发了 C 语言，最初目的是为了重写 UNIX 操作系统。C 语言在 B 语言（由 Ken Thompson 开发）的基础上发展而来。

## 二、重要里程碑

| 年份 | 事件 |
|------|------|
| 1972 | C 语言诞生于贝尔实验室 |
| 1978 | 《The C Programming Language》出版（K&R C） |
| 1989 | ANSI C 标准（C89/C90）发布 |
| 1999 | C99 标准发布，引入变长数组等特性 |
| 2011 | C11 标准发布，引入多线程支持 |
| 2018 | C18 标准发布（小幅修订） |

## 三、C语言的应用领域

### 1. 操作系统
- Linux 内核（几乎全部用 C 编写）
- Windows 底层组件
- macOS/XNU 内核

### 2. 嵌入式系统
- 单片机编程（STM32、Arduino）
- 物联网设备
- 汽车电子

### 3. 系统软件
- 数据库引擎（MySQL、SQLite）
- 编译器（GCC、Clang）
- 虚拟机（Python CPython）

### 4. 游戏与图形
- 游戏引擎底层
- 图形库（OpenGL、SDL）

## 四、为什么学习 C 语言？

1. **理解计算机底层**：指针、内存管理让你真正理解计算机如何工作
2. **高效性能**：接近汇编语言的执行效率
3. **广泛基础**：C++、Java、Python 等语言都受 C 影响
4. **就业前景**：嵌入式、系统开发、物联网等领域需求旺盛
"""
        },
    },
]


# =====================================================================
#  写入数据库
# =====================================================================

now = datetime.utcnow()
base_time = now - timedelta(days=30)

for i, task_def in enumerate(SEED_TASKS):
    # 均匀分布在最近 30 天内
    offset = timedelta(days=i * 1.2, hours=i * 3)
    created = base_time + offset

    task = ResourceTaskModel(
        task_id=f"seed_{i:04d}_{task_def['resource_type']}",
        status="completed",
        progress=1.0,
        resources=task_def["resources"],
        message="种子数据",
        title=task_def["title"],
        resource_type=task_def["resource_type"],
        subject=task_def["subject"],
        difficulty=task_def["difficulty"],
        created_at=created,
        updated_at=created,
    )
    db.add(task)

db.commit()
db.close()

print(f"已写入 {len(SEED_TASKS)} 条资源种子数据")
print("  - C语言讲义: 3 篇（指针/函数/数组）")
print("  - C语言导图: 2 张（指针/函数）")
print("  - C语言练习: 3 套（指针/函数/数组，共 9 题）")
print("  - C语言代码: 3 个（swap/递归/冒泡排序）")
print("  - C语言阅读: 1 篇（发展历史）")
print("  - 电路分析讲义: 3 篇（基本定律/等效变换/正弦稳态）")
print("  - 电路分析导图: 2 张（基本定律/等效变换）")
print("  - 电路分析练习: 2 套（基本定律/正弦稳态，共 6 题）")
print("完成！")
