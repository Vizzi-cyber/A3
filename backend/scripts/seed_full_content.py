"""
完整C语言教材内容种子脚本
基于系统化C语言教学大纲，为16个知识点填充完整的文档、代码示例、练习题和思维导图。
"""
import sqlite3
import os
import json

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "ai_learning_v2.db")

# ============================================================
# kp_c01: C语言概述与开发环境
# ============================================================
KP_C01_DOC = r"""# C语言概述与开发环境

## 一、C语言的发展历史

C语言由**Dennis Ritchie**于1972年在贝尔实验室开发，最初是为了重写UNIX操作系统。C语言是在B语言的基础上发展而来的，而B语言又源自BCPL。

### 发展时间线
- **1969年**：Ken Thompson用汇编语言编写了UNIX雏形
- **1970年**：Thompson开发了B语言
- **1972年**：Ritchie在B语言基础上设计了C语言
- **1978年**：K&R C（《The C Programming Language》出版）
- **1989年**：ANSI C（C89标准）发布
- **1999年**：C99标准发布，支持变长数组、`//`注释等
- **2011年**：C11标准发布，增加多线程、泛型选择等

## 二、C语言的特点

1. **简洁紧凑**：关键字仅32个（C89），语法灵活
2. **贴近硬件**：支持位运算、指针操作，可直接访问内存地址
3. **可移植性**：遵循标准的C程序可在不同平台上编译运行
4. **运算符丰富**：34种运算符，表达力强
5. **结构化编程**：支持函数、选择、循环三种基本结构
6. **高执行效率**：编译后直接生成机器码，运行速度快

## 三、第一个C程序

```c
#include <stdio.h>

int main()
{
    printf("Hello, World!\n");
    return 0;
}
```

### 代码解析
- `#include <stdio.h>`：预处理指令，包含标准输入输出头文件
- `int main()`：主函数，程序执行的入口点
- `printf(...)`：标准输出函数，将内容打印到屏幕
- `\n`：转义字符，表示换行
- `return 0`：返回值0表示程序正常结束

## 四、开发环境搭建

### Windows环境
1. 安装Visual Studio（推荐Community版）或Dev-C++
2. 新建项目 → 控制台应用 → 编写代码 → 编译运行

### 编译过程
```
源代码(.c) → 预处理 → 编译 → 汇编 → 链接 → 可执行程序(.exe)
```

## 五、编译与调试

### 常用编译命令（GCC）
```bash
gcc hello.c -o hello      # 编译
gcc -Wall hello.c -o hello # 开启所有警告
./hello                    # 运行（Linux/Mac）
```

### 调试技巧
- **F9**：设置/取消断点
- **F5**：开始调试（运行到断点处暂停）
- **F10**：单步跳过（Step Over）
- **F11**：单步进入（Step Into）
- 查看变量值：调试时将鼠标悬停在变量上
"""

KP_C01_CODE = r"""// ========================================
// 示例1：Hello World
// ========================================
#include <stdio.h>

int main()
{
    printf("Hello, World!\n");
    printf("欢迎学习C语言！\n");
    return 0;
}

// ========================================
// 示例2：变量与输入输出
// ========================================
#include <stdio.h>

int main()
{
    int age;
    float height;
    char grade;

    printf("请输入年龄: ");
    scanf("%d", &age);
    printf("请输入身高(米): ");
    scanf("%f", &height);
    printf("请输入成绩等级(A/B/C): ");
    scanf(" %c", &grade);  // 前面的空格用于跳过空白字符

    printf("年龄: %d岁\n", age);
    printf("身高: %.2f米\n", height);
    printf("等级: %c\n", grade);
    return 0;
}

// ========================================
// 示例3：变量作用域与生命周期
// ========================================
#include <stdio.h>

int g_val = 2024;  // 全局变量

int main()
{
    int a = 10;     // 局部变量
    {
        int b = 20; // 块作用域局部变量
        printf("a = %d, b = %d\n", a, b);
    }
    // b在此处不可访问

    extern int g_val;  // 使用extern声明外部变量
    printf("g_val = %d\n", g_val);
    return 0;
}
"""

KP_C01_QS = [
    {"q_id": "q_c01_1", "type": "single_choice", "content": "C语言中，程序的执行从哪个函数开始？",
     "options": [{"id": "A", "text": "start()"}, {"id": "B", "text": "main()"}, {"id": "C", "text": "begin()"}, {"id": "D", "text": "init()"}],
     "correct_answer": "B", "explanation": "main()函数是C程序的入口点，操作系统从main函数开始执行程序。"},
    {"q_id": "q_c01_2", "type": "single_choice", "content": "以下哪个是C语言的预处理指令？",
     "options": [{"id": "A", "text": "int main()"}, {"id": "B", "text": "#include <stdio.h>"}, {"id": "C", "text": "printf()"}, {"id": "D", "text": "return 0"}],
     "correct_answer": "B", "explanation": "#include是预处理指令，在编译前由预处理器处理，用于包含头文件。"},
    {"q_id": "q_c01_3", "type": "single_choice", "content": "C语言源代码文件的扩展名通常是？",
     "options": [{"id": "A", "text": ".cpp"}, {"id": "B", "text": ".java"}, {"id": "C", "text": ".c"}, {"id": "D", "text": ".py"}],
     "correct_answer": "C", "explanation": "C语言源文件扩展名为.c，C++为.cpp，Java为.java，Python为.py。"},
    {"q_id": "q_c01_4", "type": "single_choice", "content": "printf函数中，%d用于输出什么类型的数据？",
     "options": [{"id": "A", "text": "浮点数"}, {"id": "B", "text": "整数"}, {"id": "C", "text": "字符"}, {"id": "D", "text": "字符串"}],
     "correct_answer": "B", "explanation": "%d用于输出十进制整数，%f输出浮点数，%c输出字符，%s输出字符串。"},
]

KP_C01_MM = {"root": "C语言概述", "children": [
    {"name": "发展历史"}, {"name": "语言特点"}, {"name": "Hello World"},
    {"name": "开发环境"}, {"name": "编译过程"}, {"name": "调试技巧"}
]}

# ============================================================
# kp_c02: 数据类型与变量
# ============================================================
KP_C02_DOC = r"""# 数据类型与变量

## 一、基本数据类型

| 类型 | 关键字 | 大小(字节) | 范围 | 格式符 |
|------|--------|-----------|------|--------|
| 字符型 | char | 1 | -128~127 | %c |
| 短整型 | short | 2 | -32768~32767 | %hd |
| 整型 | int | 4 | ±21亿 | %d |
| 长整型 | long | 4/8 | 取决于平台 | %ld |
| 无符号整型 | unsigned int | 4 | 0~42亿 | %u |
| 单精度浮点 | float | 4 | ±3.4e38 | %f |
| 双精度浮点 | double | 8 | ±1.7e308 | %lf |

## 二、变量

### 变量的定义
```c
int age = 25;           // 初始化
float height = 1.75f;   // f后缀表示float
char grade = 'A';       // 单引号包裹字符
```

### 变量命名规则
1. 只能由字母、数字、下划线组成
2. 不能以数字开头
3. 区分大小写（`age`和`Age`是不同变量）
4. 不能使用关键字（如int、return等）
5. 命名要有意义（推荐驼峰或下划线命名法）

## 三、常量

### 四种定义常量的方式
```c
// 1. #define宏定义
#define PI 3.14159

// 2. const常变量
const int MAX = 100;

// 3. 枚举常量
enum Color { RED, GREEN, BLUE };  // RED=0, GREEN=1, BLUE=2

// 4. 字面常量
int a = 10;  // 10就是字面常量
```

> **注意**：`const`修饰的变量本质仍是变量，不能用于数组大小；`#define`定义的是真正的常量。

## 四、sizeof操作符

`sizeof`用于计算数据类型或变量所占的字节数：

```c
printf("%zu\n", sizeof(char));     // 1
printf("%zu\n", sizeof(short));    // 2
printf("%zu\n", sizeof(int));      // 4
printf("%zu\n", sizeof(long));     // 4 或 8
printf("%zu\n", sizeof(float));    // 4
printf("%zu\n", sizeof(double));   // 8
```

## 五、转义字符

| 转义字符 | 含义 | ASCII值 |
|---------|------|---------|
| `\n` | 换行 | 10 |
| `\t` | 水平制表符 | 9 |
| `\\` | 反斜杠 | 92 |
| `\'` | 单引号 | 39 |
| `\"` | 双引号 | 34 |
| `\0` | 空字符 | 0 |
| `\ddd` | 八进制表示 | - |
| `\xdd` | 十六进制表示 | - |
"""

KP_C02_CODE = r"""// ========================================
// 示例1：sizeof计算各类型大小
// ========================================
#include <stdio.h>

int main()
{
    printf("char:     %zu 字节\n", sizeof(char));
    printf("short:    %zu 字节\n", sizeof(short));
    printf("int:      %zu 字节\n", sizeof(int));
    printf("long:     %zu 字节\n", sizeof(long));
    printf("long long:%zu 字节\n", sizeof(long long));
    printf("float:    %zu 字节\n", sizeof(float));
    printf("double:   %zu 字节\n", sizeof(double));
    return 0;
}

// ========================================
// 示例2：变量的定义和使用
// ========================================
#include <stdio.h>

int main()
{
    int a = 10;
    int b = 20;
    int sum = a + b;
    printf("%d + %d = %d\n", a, b, sum);

    // 交换两个变量的值
    int tmp = a;
    a = b;
    b = tmp;
    printf("交换后: a=%d, b=%d\n", a, b);
    return 0;
}

// ========================================
// 示例3：常量与枚举
// ========================================
#include <stdio.h>

#define MAX 100

enum Sex
{
    MALE,      // 0
    FEMALE,    // 1
    SECRET     // 2
};

int main()
{
    const int MIN = 0;
    printf("MAX = %d\n", MAX);
    printf("MIN = %d\n", MIN);
    printf("MALE=%d, FEMALE=%d, SECRET=%d\n", MALE, FEMALE, SECRET);
    return 0;
}

// ========================================
// 示例4：sizeof陷阱
// ========================================
#include <stdio.h>

int main()
{
    int a = 5;
    printf("%zu\n", sizeof(a));      // 4 —— 计算变量大小
    printf("%zu\n", sizeof(int));    // 4 —— 计算类型大小
    // sizeof内部表达式不会真正执行
    int b = 10;
    printf("%zu\n", sizeof(b = b + 2)); // 4
    printf("b = %d\n", b);              // b仍然是10，赋值未执行
    return 0;
}
"""

KP_C02_QS = [
    {"q_id": "q_c02_1", "type": "single_choice", "content": "在32位系统中，int类型占多少字节？",
     "options": [{"id": "A", "text": "1字节"}, {"id": "B", "text": "2字节"}, {"id": "C", "text": "4字节"}, {"id": "D", "text": "8字节"}],
     "correct_answer": "C", "explanation": "在大多数平台上，int类型占4字节（32位）。"},
    {"q_id": "q_c02_2", "type": "single_choice", "content": "以下哪个变量名是不合法的？",
     "options": [{"id": "A", "text": "_count"}, {"id": "B", "text": "2name"}, {"id": "C", "text": "myVar"}, {"id": "D", "text": "MAX_SIZE"}],
     "correct_answer": "B", "explanation": "变量名不能以数字开头，2name不符合命名规则。"},
    {"q_id": "q_c02_3", "type": "single_choice", "content": "sizeof操作符的返回值类型是？",
     "options": [{"id": "A", "text": "int"}, {"id": "B", "text": "unsigned int"}, {"id": "C", "text": "size_t"}, {"id": "D", "text": "float"}],
     "correct_answer": "C", "explanation": "sizeof返回size_t类型，是一个无符号整数类型，用%zu格式符打印。"},
    {"q_id": "q_c02_4", "type": "single_choice", "content": "以下哪种方式定义的不是真正的常量？",
     "options": [{"id": "A", "text": "#define PI 3.14"}, {"id": "B", "text": "const int N = 10;"}, {"id": "C", "text": "enum { MAX = 100 };"}, {"id": "D", "text": "以上都是常量"}],
     "correct_answer": "B", "explanation": "const修饰的变量本质仍是变量，只是只读的，不能用于数组大小等需要真正常量的场景。"},
]

KP_C02_MM = {"root": "数据类型与变量", "children": [
    {"name": "基本数据类型"}, {"name": "变量定义"}, {"name": "常量"},
    {"name": "sizeof"}, {"name": "转义字符"}, {"name": "命名规则"}
]}

# ============================================================
# kp_c03: 运算符与表达式
# ============================================================
KP_C03_DOC = r"""# 运算符与表达式

## 一、算术运算符

| 运算符 | 含义 | 示例 | 结果 |
|--------|------|------|------|
| `+` | 加 | 5 + 3 | 8 |
| `-` | 减 | 5 - 3 | 2 |
| `*` | 乘 | 5 * 3 | 15 |
| `/` | 除 | 5 / 3 | 1（整数除法）|
| `%` | 取模 | 5 % 3 | 2 |

> **注意**：整数除法会截断小数部分；取模运算只能用于整数。

## 二、关系运算符

| 运算符 | 含义 | 示例 |
|--------|------|------|
| `==` | 等于 | 5 == 3 → 0 |
| `!=` | 不等于 | 5 != 3 → 1 |
| `>` | 大于 | 5 > 3 → 1 |
| `<` | 小于 | 5 < 3 → 0 |
| `>=` | 大于等于 | 5 >= 5 → 1 |
| `<=` | 小于等于 | 5 <= 3 → 0 |

## 三、逻辑运算符

| 运算符 | 含义 | 说明 |
|--------|------|------|
| `&&` | 逻辑与 | 两边都真则为真 |
| `\|\|` | 逻辑或 | 任一为真则为真 |
| `!` | 逻辑非 | 真变假，假变真 |

**短路求值**：
- `&&`：左边为假时，右边不执行
- `||`：左边为真时，右边不执行

## 四、赋值运算符

```c
a = 10;     // 简单赋值
a += 5;     // 等价于 a = a + 5
a -= 3;     // 等价于 a = a - 3
a *= 2;     // 等价于 a = a * 2
a /= 4;     // 等价于 a = a / 4
a %= 3;     // 等价于 a = a % 3
a &= 0xFF;  // 等价于 a = a & 0xFF
```

## 五、自增自减

```c
int a = 5;
int b = a++;   // 后置：先使用a的值(5)，再a自增 → b=5, a=6
int c = ++a;   // 前置：先a自增(7)，再使用 → c=7, a=7
```

## 六、位运算符

| 运算符 | 含义 | 示例 |
|--------|------|------|
| `&` | 按位与 | 5 & 3 = 1 |
| `\|` | 按位或 | 5 \| 3 = 7 |
| `^` | 按位异或 | 5 ^ 3 = 6 |
| `~` | 按位取反 | ~0 = -1 |
| `<<` | 左移 | 1 << 3 = 8 |
| `>>` | 右移 | 8 >> 2 = 2 |

## 七、运算符优先级

```
单目运算符 > 算术运算符 > 移位运算符 > 关系运算符
> 位运算符 > 逻辑运算符 > 条件运算符 > 赋值运算符
```

> 建议：不确定优先级时，使用括号明确运算顺序。
"""

KP_C03_CODE = r"""// ========================================
// 示例1：算术运算与取模
// ========================================
#include <stdio.h>

int main()
{
    int a = 17, b = 5;
    printf("%d + %d = %d\n", a, b, a + b);
    printf("%d - %d = %d\n", a, b, a - b);
    printf("%d * %d = %d\n", a, b, a * b);
    printf("%d / %d = %d\n", a, b, a / b);   // 3（截断）
    printf("%d %% %d = %d\n", a, b, a % b);  // 2
    return 0;
}

// ========================================
// 示例2：自增自减
// ========================================
#include <stdio.h>

int main()
{
    int a = 5;
    int b = a++;   // 先赋值再自增
    printf("a=%d, b=%d\n", a, b);  // a=6, b=5

    int c = ++a;   // 先自增再赋值
    printf("a=%d, c=%d\n", a, c);  // a=7, c=7
    return 0;
}

// ========================================
// 示例3：位运算实战
// ========================================
#include <stdio.h>

int main()
{
    int a = 13;  // 二进制: 1101
    int b = 11;  // 二进制: 1011

    printf("a & b  = %d\n", a & b);   // 1001 = 9
    printf("a | b  = %d\n", a | b);   // 1111 = 15
    printf("a ^ b  = %d\n", a ^ b);   // 0110 = 6
    printf("a << 2 = %d\n", a << 2);  // 110100 = 52
    printf("a >> 1 = %d\n", a >> 1);  // 110 = 6

    // 异或交换两个数（无需临时变量）
    int x = 10, y = 20;
    x ^= y;
    y ^= x;
    x ^= y;
    printf("交换后: x=%d, y=%d\n", x, y);  // x=20, y=10
    return 0;
}

// ========================================
// 示例4：逻辑运算与短路
// ========================================
#include <stdio.h>

int main()
{
    int a = 0, b = 5;
    // && 短路：a为0（假），右边不执行
    if (a && (b++))
    {
        printf("b=%d\n", b);  // 不会执行
    }
    printf("短路后b=%d\n", b);  // b仍然是5

    // || 短路：a为0（假），右边继续执行
    if (a || (b++))
    {
        printf("短路后b=%d\n", b);  // b=6
    }
    return 0;
}
"""

KP_C03_QS = [
    {"q_id": "q_c03_1", "type": "single_choice", "content": "表达式 17 / 5 的结果是？",
     "options": [{"id": "A", "text": "3.4"}, {"id": "B", "text": "3"}, {"id": "C", "text": "4"}, {"id": "D", "text": "3.0"}],
     "correct_answer": "B", "explanation": "两个整数相除结果仍为整数，小数部分被截断，17/5=3。"},
    {"q_id": "q_c03_2", "type": "single_choice", "content": "若 int a=3, 则表达式 a++ + ++a 的结果是？",
     "options": [{"id": "A", "text": "6"}, {"id": "B", "text": "7"}, {"id": "C", "text": "8"}, {"id": "D", "text": "未定义行为"}],
     "correct_answer": "D", "explanation": "C语言中，对同一变量在同一个表达式中多次自增是未定义行为，不同编译器结果可能不同。"},
    {"q_id": "q_c03_3", "type": "single_choice", "content": "5 & 3 的结果是？",
     "options": [{"id": "A", "text": "7"}, {"id": "B", "text": "6"}, {"id": "C", "text": "1"}, {"id": "D", "text": "15"}],
     "correct_answer": "C", "explanation": "5的二进制101，3的二进制011，按位与得001，即十进制1。"},
    {"q_id": "q_c03_4", "type": "single_choice", "content": "以下表达式中，哪个使用了短路求值？",
     "options": [{"id": "A", "text": "a + b"}, {"id": "B", "text": "a && b"}, {"id": "C", "text": "a = b"}, {"id": "D", "text": "a++"}],
     "correct_answer": "B", "explanation": "逻辑与&&和逻辑或||都使用短路求值：&&左边为假时不计算右边，||左边为真时不计算右边。"},
]

KP_C03_MM = {"root": "运算符与表达式", "children": [
    {"name": "算术运算符"}, {"name": "关系运算符"}, {"name": "逻辑运算符"},
    {"name": "位运算符"}, {"name": "赋值运算符"}, {"name": "优先级"}
]}

# ============================================================
# kp_c04: 输入输出与顺序结构
# ============================================================
KP_C04_DOC = r"""# 输入输出与顺序结构

## 一、printf格式化输出

### 格式符一览
| 格式符 | 含义 | 示例 |
|--------|------|------|
| `%d` | 十进制整数 | printf("%d", 42) |
| `%o` | 八进制 | printf("%o", 10) → 12 |
| `%x` | 十六进制 | printf("%x", 255) → ff |
| `%f` | 浮点数（默认6位小数）| printf("%f", 3.14) |
| `%c` | 字符 | printf("%c", 65) → A |
| `%s` | 字符串 | printf("%s", "hello") |
| `%p` | 地址 | printf("%p", &a) |
| `%%` | 输出%本身 | printf("%%") → % |

### 控制输出宽度和精度
```c
printf("%10d", 42);      // 右对齐，宽度10: "        42"
printf("%-10d", 42);     // 左对齐: "42        "
printf("%05d", 42);      // 前导零填充: "00042"
printf("%.2f", 3.14159); // 保留2位小数: "3.14"
printf("%10.2f", 3.14);  // 宽度10，2位小数: "      3.14"
```

## 二、scanf格式化输入

### 基本用法
```c
int a;
scanf("%d", &a);         // &取地址符是必须的

float b;
scanf("%f", &b);

char c;
scanf(" %c", &c);        // 前面加空格跳过空白字符
```

### 常见陷阱
```c
// 错误：忘记&
scanf("%d", a);    // 运行时崩溃！

// 字符串读取空格问题
char str[20];
scanf("%s", str);  // 遇到空格就停止读取

// 正确读取一行字符串
scanf("%[^\n]", str);  // 读取直到换行符
```

## 三、getchar与putchar

```c
int ch = getchar();   // 读取一个字符
putchar(ch);          // 输出一个字符
putchar('\n');        // 输出换行
```

### getchar的缓冲区问题
```c
// 清空输入缓冲区的正确方式
int c;
while ((c = getchar()) != '\n' && c != EOF);
```

## 四、顺序结构

程序从上到下逐行执行，每条语句按顺序完成：
```c
#include <stdio.h>
int main()
{
    int a = 10;        // 第1步
    int b = 20;        // 第2步
    int sum = a + b;   // 第3步
    printf("sum = %d\n", sum);  // 第4步
    return 0;
}
```
"""

KP_C04_CODE = r"""// ========================================
// 示例1：格式化输出
// ========================================
#include <stdio.h>

int main()
{
    int num = 42;
    float pi = 3.14159;
    char ch = 'A';

    printf("十进制: %d\n", num);
    printf("八进制: %o\n", num);
    printf("十六进制: %x\n", num);
    printf("浮点数: %.2f\n", pi);
    printf("字符: %c\n", ch);
    printf("地址: %p\n", &num);

    // 控制宽度
    printf("[%10d]\n", num);     // [        42]
    printf("[%-10d]\n", num);    // [42        ]
    printf("[%05d]\n", num);     // [00042]
    return 0;
}

// ========================================
// 示例2：scanf输入
// ========================================
#include <stdio.h>

int main()
{
    int age;
    float height;
    char name[50];

    printf("请输入姓名: ");
    scanf("%s", name);  // 字符串不需要&
    printf("请输入年龄: ");
    scanf("%d", &age);  // 整数需要&
    printf("请输入身高: ");
    scanf("%f", &height);

    printf("\n姓名: %s\n年龄: %d岁\n身高: %.2f米\n", name, age, height);
    return 0;
}

// ========================================
// 示例3：getchar清空缓冲区
// ========================================
#include <stdio.h>

int main()
{
    int password;
    printf("请输入密码(4位数字): ");
    scanf("%d", &password);

    // 清空缓冲区中残留的换行符
    int c;
    while ((c = getchar()) != '\n' && c != EOF);

    printf("请按回车键继续...");
    getchar();  // 等待用户按回车
    printf("程序继续执行\n");
    return 0;
}

// ========================================
// 示例4：温度转换
// ========================================
#include <stdio.h>

int main()
{
    float fahrenheit;
    printf("请输入华氏温度: ");
    scanf("%f", &fahrenheit);

    float celsius = (fahrenheit - 32) * 5.0 / 9.0;
    printf("%.1f°F = %.1f°C\n", fahrenheit, celsius);
    return 0;
}
"""

KP_C04_QS = [
    {"q_id": "q_c04_1", "type": "single_choice", "content": "scanf中，读取整数的正确写法是？",
     "options": [{"id": "A", "text": "scanf(\"%d\", a);"}, {"id": "B", "text": "scanf(\"%d\", &a);"}, {"id": "C", "text": "scanf(\"%d\", *a);"}, {"id": "D", "text": "scanf(\"%d\", a&)"}],
     "correct_answer": "B", "explanation": "scanf需要传入变量的地址，使用&取地址符。"},
    {"q_id": "q_c04_2", "type": "single_choice", "content": "printf(\"%05d\", 42)的输出结果是？",
     "options": [{"id": "A", "text": "42"}, {"id": "B", "text": "00042"}, {"id": "C", "text": "00420"}, {"id": "D", "text": "42000"}],
     "correct_answer": "B", "explanation": "%05d表示宽度5，不足部分用0填充。"},
    {"q_id": "q_c04_3", "type": "single_choice", "content": "getchar()函数的返回值类型是？",
     "options": [{"id": "A", "text": "char"}, {"id": "B", "text": "int"}, {"id": "C", "text": "void"}, {"id": "D", "text": "float"}],
     "correct_answer": "B", "explanation": "getchar返回int类型，因为需要表示EOF（通常为-1），char无法表示。"},
]

KP_C04_MM = {"root": "输入输出", "children": [
    {"name": "printf格式化"}, {"name": "scanf输入"}, {"name": "getchar/putchar"},
    {"name": "缓冲区处理"}, {"name": "顺序结构"}
]}

# ============================================================
# kp_c05: 选择结构
# ============================================================
KP_C05_DOC = r"""# 选择结构

## 一、if语句

### 基本形式
```c
if (条件)
{
    // 条件为真时执行
}
```

### if-else形式
```c
if (条件)
{
    // 条件为真
}
else
{
    // 条件为假
}
```

### 多重if-else
```c
if (条件1)
{
    // 条件1为真
}
else if (条件2)
{
    // 条件2为真
}
else
{
    // 所有条件都为假
}
```

> **悬空else问题**：else总是与最近的未匹配if配对。

## 二、switch语句

```c
switch (整型表达式)
{
    case 整型常量1:
        // 语句1
        break;
    case 整型常量2:
        // 语句2
        break;
    default:
        // 默认语句
        break;
}
```

### 注意事项
1. `case`后必须是**整型常量表达式**（不能是变量）
2. 每个`case`后要加`break`，否则会"穿透"执行下一个case
3. `case`的值不能重复
4. 多个case可以共用同一组语句

## 三、条件运算符（三目运算符）

```c
// 表达式1 ? 表达式2 : 表达式3
int max = (a > b) ? a : b;  // 等价于if-else
```

## 四、嵌套选择

```c
// 判断闰年
if (year % 4 == 0)
{
    if (year % 100 == 0)
    {
        if (year % 400 == 0)
            printf("%d是闰年", year);
        else
            printf("%d不是闰年", year);
    }
    else
        printf("%d是闰年", year);
}
else
    printf("%d不是闰年", year);
```

> 可以用逻辑运算符简化：`(year%4==0 && year%100!=0) || (year%400==0)`
"""

KP_C05_CODE = r"""// ========================================
// 示例1：成绩等级判断
// ========================================
#include <stdio.h>

int main()
{
    int score;
    printf("请输入成绩(0-100): ");
    scanf("%d", &score);

    if (score >= 90)
        printf("优秀\n");
    else if (score >= 80)
        printf("良好\n");
    else if (score >= 70)
        printf("中等\n");
    else if (score >= 60)
        printf("及格\n");
    else
        printf("不及格\n");
    return 0;
}

// ========================================
// 示例2：switch实现计算器
// ========================================
#include <stdio.h>

int main()
{
    double a, b;
    char op;
    printf("请输入表达式(如 3 + 5): ");
    scanf("%lf %c %lf", &a, &op, &b);

    switch (op)
    {
    case '+':
        printf("%.2f + %.2f = %.2f\n", a, b, a + b);
        break;
    case '-':
        printf("%.2f - %.2f = %.2f\n", a, b, a - b);
        break;
    case '*':
        printf("%.2f * %.2f = %.2f\n", a, b, a * b);
        break;
    case '/':
        if (b != 0)
            printf("%.2f / %.2f = %.2f\n", a, b, a / b);
        else
            printf("错误：除数不能为0\n");
        break;
    default:
        printf("不支持的运算符: %c\n", op);
        break;
    }
    return 0;
}

// ========================================
// 示例3：判断闰年
// ========================================
#include <stdio.h>

int main()
{
    int year;
    printf("请输入年份: ");
    scanf("%d", &year);

    if ((year % 4 == 0 && year % 100 != 0) || (year % 400 == 0))
        printf("%d年是闰年\n", year);
    else
        printf("%d年不是闰年\n", year);
    return 0;
}

// ========================================
// 示例4：三个数排序
// ========================================
#include <stdio.h>

int main()
{
    int a, b, c, tmp;
    printf("请输入三个整数: ");
    scanf("%d %d %d", &a, &b, &c);

    if (a > b) { tmp = a; a = b; b = tmp; }
    if (a > c) { tmp = a; a = c; c = tmp; }
    if (b > c) { tmp = b; b = c; c = tmp; }

    printf("从小到大: %d %d %d\n", a, b, c);
    return 0;
}
"""

KP_C05_QS = [
    {"q_id": "q_c05_1", "type": "single_choice", "content": "switch语句中，case后面可以是什么类型的常量？",
     "options": [{"id": "A", "text": "浮点数"}, {"id": "B", "text": "字符串"}, {"id": "C", "text": "整型常量"}, {"id": "D", "text": "任意类型"}],
     "correct_answer": "C", "explanation": "case后必须是整型常量表达式，不能是变量、浮点数或字符串。"},
    {"q_id": "q_c05_2", "type": "single_choice", "content": "switch中忘记break会导致什么？",
     "options": [{"id": "A", "text": "编译错误"}, {"id": "B", "text": "程序崩溃"}, {"id": "C", "text": "穿透执行下一个case"}, {"id": "D", "text": "跳过整个switch"}],
     "correct_answer": "C", "explanation": "没有break时，程序会从匹配的case开始，依次执行后面所有case的语句（穿透）。"},
    {"q_id": "q_c05_3", "type": "single_choice", "content": "条件表达式 (a > b) ? a : b 的作用是？",
     "options": [{"id": "A", "text": "求a和b的和"}, {"id": "B", "text": "求a和b中的较大值"}, {"id": "C", "text": "判断a是否大于b"}, {"id": "D", "text": "交换a和b"}],
     "correct_answer": "B", "explanation": "三目运算符：如果a>b为真返回a，否则返回b，即取两者较大值。"},
]

KP_C05_MM = {"root": "选择结构", "children": [
    {"name": "if语句"}, {"name": "if-else"}, {"name": "switch-case"},
    {"name": "三目运算符"}, {"name": "嵌套选择"}
]}

# ============================================================
# kp_c06: 循环结构
# ============================================================
KP_C06_DOC = r"""# 循环结构

## 一、while循环

```c
while (条件)
{
    // 循环体：条件为真时重复执行
}
```

### 执行流程
1. 判断条件 → 为真则执行循环体
2. 执行完循环体后，回到步骤1
3. 条件为假时，跳出循环

## 二、for循环

```c
for (初始化; 条件; 更新)
{
    // 循环体
}
```

### 执行流程
1. 执行初始化（只执行一次）
2. 判断条件 → 为假则跳出
3. 执行循环体
4. 执行更新
5. 回到步骤2

```c
// 经典for循环
for (int i = 0; i < 10; i++)
{
    printf("%d ", i);
}
```

## 三、do-while循环

```c
do
{
    // 循环体（至少执行一次）
} while (条件);  // 注意分号
```

> **与while的区别**：do-while至少执行一次循环体，然后再判断条件。

## 四、循环控制

### break：跳出当前循环
```c
for (int i = 0; i < 100; i++)
{
    if (i == 5) break;  // 当i==5时跳出循环
    printf("%d ", i);   // 输出: 0 1 2 3 4
}
```

### continue：跳过本次循环，进入下一次
```c
for (int i = 0; i < 10; i++)
{
    if (i % 2 == 0) continue;  // 跳过偶数
    printf("%d ", i);           // 输出: 1 3 5 7 9
}
```

## 五、嵌套循环

```c
// 9x9乘法表
for (int i = 1; i <= 9; i++)
{
    for (int j = 1; j <= i; j++)
    {
        printf("%d*%d=%-4d", j, i, i * j);
    }
    printf("\n");
}
```

## 六、goto语句（慎用）

```c
// goto可以跳转到同一函数内的标签处
for (int i = 0; i < 10; i++)
{
    for (int j = 0; j < 10; j++)
    {
        if (i == 5 && j == 5)
            goto end;  // 跳出多层循环
    }
}
end:
printf("跳出嵌套循环\n");
```

> **注意**：goto语句会破坏程序的结构化，应尽量避免使用，用break/continue替代。
"""

KP_C06_CODE = r"""// ========================================
// 示例1：求1到100的和
// ========================================
#include <stdio.h>

int main()
{
    // while循环
    int i = 1, sum = 0;
    while (i <= 100)
    {
        sum += i;
        i++;
    }
    printf("while: 1+2+...+100 = %d\n", sum);

    // for循环
    sum = 0;
    for (int j = 1; j <= 100; j++)
        sum += j;
    printf("for:   1+2+...+100 = %d\n", sum);

    // do-while循环
    sum = 0;
    int k = 1;
    do {
        sum += k;
        k++;
    } while (k <= 100);
    printf("do-while: 1+2+...+100 = %d\n", sum);
    return 0;
}

// ========================================
// 示例2：猜数字游戏
// ========================================
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

int main()
{
    srand((unsigned int)time(NULL));
    int secret = rand() % 100 + 1;  // 1-100的随机数
    int guess, count = 0;

    printf("我想了一个1-100的数字，来猜猜看！\n");
    do {
        printf("请输入你的猜测: ");
        scanf("%d", &guess);
        count++;

        if (guess > secret)
            printf("太大了！\n");
        else if (guess < secret)
            printf("太小了！\n");
        else
            printf("恭喜你猜对了！用了%d次\n", count);
    } while (guess != secret);
    return 0;
}

// ========================================
// 示例3：素数判断
// ========================================
#include <stdio.h>
#include <math.h>

int main()
{
    int n;
    printf("请输入一个正整数: ");
    scanf("%d", &n);

    int is_prime = 1;
    if (n < 2)
        is_prime = 0;
    else
    {
        for (int i = 2; i <= sqrt(n); i++)
        {
            if (n % i == 0)
            {
                is_prime = 0;
                break;
            }
        }
    }

    if (is_prime)
        printf("%d是素数\n", n);
    else
        printf("%d不是素数\n", n);
    return 0;
}

// ========================================
// 示例4：冒泡排序
// ========================================
#include <stdio.h>

int main()
{
    int arr[] = {64, 34, 25, 12, 22, 11, 90};
    int sz = sizeof(arr) / sizeof(arr[0]);

    for (int i = 0; i < sz - 1; i++)
    {
        int swapped = 0;
        for (int j = 0; j < sz - 1 - i; j++)
        {
            if (arr[j] > arr[j + 1])
            {
                int tmp = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = tmp;
                swapped = 1;
            }
        }
        if (!swapped) break;  // 优化：没有交换说明已排好序
    }

    printf("排序结果: ");
    for (int i = 0; i < sz; i++)
        printf("%d ", arr[i]);
    printf("\n");
    return 0;
}
"""

KP_C06_QS = [
    {"q_id": "q_c06_1", "type": "single_choice", "content": "do-while循环至少执行几次？",
     "options": [{"id": "A", "text": "0次"}, {"id": "B", "text": "1次"}, {"id": "C", "text": "2次"}, {"id": "D", "text": "取决于条件"}],
     "correct_answer": "B", "explanation": "do-while先执行循环体再判断条件，所以至少执行一次。"},
    {"q_id": "q_c06_2", "type": "single_choice", "content": "在for循环中，break语句的作用是？",
     "options": [{"id": "A", "text": "跳过本次循环"}, {"id": "B", "text": "结束整个循环"}, {"id": "C", "text": "重新开始循环"}, {"id": "D", "text": "退出程序"}],
     "correct_answer": "B", "explanation": "break用于跳出当前循环（结束整个循环），continue才是跳过本次进入下一次。"},
    {"q_id": "q_c06_3", "type": "single_choice", "content": "以下哪个不是循环语句？",
     "options": [{"id": "A", "text": "while"}, {"id": "B", "text": "for"}, {"id": "C", "text": "switch"}, {"id": "D", "text": "do-while"}],
     "correct_answer": "C", "explanation": "switch是选择（分支）语句，不是循环语句。while、for、do-while是三种循环语句。"},
]

KP_C06_MM = {"root": "循环结构", "children": [
    {"name": "while循环"}, {"name": "for循环"}, {"name": "do-while循环"},
    {"name": "break/continue"}, {"name": "嵌套循环"}, {"name": "goto语句"}
]}

# ============================================================
# kp_c07: 数组
# ============================================================
KP_C07_DOC = r"""# 数组

## 一、一维数组

### 定义与初始化
```c
int arr1[5] = {1, 2, 3, 4, 5};     // 完全初始化
int arr2[5] = {1, 2};               // 部分初始化，其余为0
int arr3[5] = {0};                  // 全部初始化为0
int arr4[] = {1, 2, 3};             // 编译器自动推算大小为3
```

### 数组访问
```c
arr[0]    // 第一个元素（下标从0开始）
arr[4]    // 最后一个元素
arr[i]    // 第i+1个元素
```

### 数组大小
```c
int arr[10];
int sz = sizeof(arr) / sizeof(arr[0]);  // 计算元素个数 = 10
```

## 二、数组越界

C语言**不检查**数组下标是否越界，越界访问是未定义行为：
```c
int arr[5] = {1, 2, 3, 4, 5};
arr[5] = 10;   // 越界！访问了不属于数组的内存
arr[-1] = 0;   // 越界！
```

## 三、二维数组

### 定义与初始化
```c
int arr[3][4] = {
    {1, 2, 3, 4},
    {5, 6, 7, 8},
    {9, 10, 11, 12}
};

int arr2[3][4] = {{1,2}, {5}};  // 部分初始化
```

### 二维数组在内存中是连续存储的
```c
// 二维数组地址连续
for (int i = 0; i < 3; i++)
    for (int j = 0; j < 4; j++)
        printf("&arr[%d][%d] = %p\n", i, j, &arr[i][j]);
```

## 四、数组作为函数参数

数组传参会**退化为指针**：
```c
void printArray(int arr[], int sz)  // arr退化为int*
{
    for (int i = 0; i < sz; i++)
        printf("%d ", arr[i]);
}
```

> **重要**：函数参数中的`int arr[]`等价于`int* arr`，sizeof计算的是指针大小而非数组大小。
"""

KP_C07_CODE = r"""// ========================================
// 示例1：数组遍历与求和
// ========================================
#include <stdio.h>

int main()
{
    int arr[] = {10, 20, 30, 40, 50};
    int sz = sizeof(arr) / sizeof(arr[0]);
    int sum = 0;

    for (int i = 0; i < sz; i++)
        sum += arr[i];

    printf("数组元素: ");
    for (int i = 0; i < sz; i++)
        printf("%d ", arr[i]);
    printf("\n和为: %d\n", sum);
    return 0;
}

// ========================================
// 示例2：二维数组打印
// ========================================
#include <stdio.h>

int main()
{
    int arr[3][4] = {
        {1, 2, 3, 4},
        {5, 6, 7, 8},
        {9, 10, 11, 12}
    };

    for (int i = 0; i < 3; i++)
    {
        for (int j = 0; j < 4; j++)
            printf("%-4d", arr[i][j]);
        printf("\n");
    }
    return 0;
}

// ========================================
// 示例3：数组求最大值
// ========================================
#include <stdio.h>

int main()
{
    int arr[] = {3, 7, 2, 9, 1, 5, 8, 4, 6, 10};
    int sz = sizeof(arr) / sizeof(arr[0]);
    int max = arr[0];

    for (int i = 1; i < sz; i++)
    {
        if (arr[i] > max)
            max = arr[i];
    }

    printf("最大值: %d\n", max);
    return 0;
}

// ========================================
// 示例4：数组逆序
// ========================================
#include <stdio.h>

int main()
{
    int arr[] = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10};
    int sz = sizeof(arr) / sizeof(arr[0]);

    // 双指针逆序
    int left = 0, right = sz - 1;
    while (left < right)
    {
        int tmp = arr[left];
        arr[left] = arr[right];
        arr[right] = tmp;
        left++;
        right--;
    }

    printf("逆序后: ");
    for (int i = 0; i < sz; i++)
        printf("%d ", arr[i]);
    printf("\n");
    return 0;
}
"""

KP_C07_QS = [
    {"q_id": "q_c07_1", "type": "single_choice", "content": "C语言数组的下标从几开始？",
     "options": [{"id": "A", "text": "0"}, {"id": "B", "text": "1"}, {"id": "C", "text": "-1"}, {"id": "D", "text": "取决于定义"}],
     "correct_answer": "A", "explanation": "C语言数组下标从0开始，arr[0]是第一个元素。"},
    {"q_id": "q_c07_2", "type": "single_choice", "content": "int arr[5]={1,2}; 后三个元素的值是？",
     "options": [{"id": "A", "text": "0,0,0"}, {"id": "B", "text": "3,4,5"}, {"id": "C", "text": "随机值"}, {"id": "D", "text": "编译错误"}],
     "correct_answer": "A", "explanation": "部分初始化时，未显式赋值的元素自动初始化为0。"},
    {"q_id": "q_c07_3", "type": "single_choice", "content": "sizeof(arr)/sizeof(arr[0])的作用是？",
     "options": [{"id": "A", "text": "计算数组占用的总字节数"}, {"id": "B", "text": "计算数组的元素个数"}, {"id": "C", "text": "计算单个元素的大小"}, {"id": "D", "text": "计算数组的地址"}],
     "correct_answer": "B", "explanation": "总大小除以单个元素大小得到元素个数。"},
]

KP_C07_MM = {"root": "数组", "children": [
    {"name": "一维数组"}, {"name": "二维数组"}, {"name": "数组初始化"},
    {"name": "数组越界"}, {"name": "数组传参"}, {"name": "常见算法"}
]}

# ============================================================
# kp_c08: 字符串
# ============================================================
KP_C08_DOC = r"""# 字符串

## 一、字符串基础

C语言中没有字符串类型，字符串用**字符数组**表示，以`'\0'`（空字符）结尾：
```c
char str1[] = "hello";      // 长度为6（含\0）
char str2[] = {'h','e','l','l','o','\0'};  // 等价写法
char str3[10] = "hello";    // 剩余位置自动补\0
```

### sizeof vs strlen
```c
char str[] = "hello";
printf("%zu\n", sizeof(str));  // 6（包含\0）
printf("%zu\n", strlen(str));  // 5（不包含\0）
```

## 二、字符串函数（string.h）

| 函数 | 功能 | 注意事项 |
|------|------|---------|
| `strlen` | 计算字符串长度 | 遇到`\0`停止 |
| `strcpy` | 字符串拷贝 | 目标空间要足够大 |
| `strcat` | 字符串追加 | 目标空间要能容纳追加后的内容 |
| `strcmp` | 字符串比较 | 返回0表示相等 |

### 使用示例
```c
char dst[20];
strcpy(dst, "hello");        // 拷贝
strcat(dst, " world");       // 追加
int ret = strcmp("abc", "abd");  // 比较，返回负数
```

## 三、模拟实现字符串函数

### my_strlen
```c
int my_strlen(const char* str)
{
    int count = 0;
    while (*str != '\0')
    {
        count++;
        str++;
    }
    return count;
}
```

### my_strcpy
```c
void my_strcpy(char* dst, const char* src)
{
    while (*dst++ = *src++);
    // 等价于：while(*src != '\0') { *dst = *src; dst++; src++; }
    //          *dst = '\0';
}
```

### my_strcmp
```c
int my_strcmp(const char* s1, const char* s2)
{
    while (*s1 && *s2 && *s1 == *s2)
    {
        s1++;
        s2++;
    }
    return *s1 - *s2;
}
```

## 四、字符串常见陷阱

```c
// 错误：数组不能直接赋值
char str[20];
str = "hello";          // 编译错误！

// 正确：使用strcpy
strcpy(str, "hello");

// 错误：scanf读取字符串遇空格停止
char name[50];
scanf("%s", name);      // 输入"hello world"只会读到"hello"
```
"""

KP_C08_CODE = r"""// ========================================
// 示例1：字符串长度（迭代与递归）
// ========================================
#include <stdio.h>
#include <string.h>

// 迭代方式
int my_strlen(const char* str)
{
    int count = 0;
    while (*str != '\0')
    {
        count++;
        str++;
    }
    return count;
}

// 递归方式
int my_strlen_r(const char* str)
{
    if (*str == '\0')
        return 0;
    return 1 + my_strlen_r(str + 1);
}

int main()
{
    char str[] = "Hello, World!";
    printf("strlen: %zu\n", strlen(str));
    printf("迭代: %d\n", my_strlen(str));
    printf("递归: %d\n", my_strlen_r(str));
    return 0;
}

// ========================================
// 示例2：字符串拷贝与连接
// ========================================
#include <stdio.h>
#include <string.h>

int main()
{
    char dst[50] = {0};

    // 拷贝
    strcpy(dst, "Hello");
    printf("拷贝后: %s\n", dst);

    // 追加
    strcat(dst, ", World!");
    printf("追加后: %s\n", dst);

    // 比较
    int ret = strcmp("abc", "abd");
    printf("比较结果: %d\n", ret);  // 负数
    return 0;
}

// ========================================
// 示例3：字符串反转
// ========================================
#include <stdio.h>
#include <string.h>

void reverse_string(char* str)
{
    int left = 0;
    int right = strlen(str) - 1;
    while (left < right)
    {
        char tmp = str[left];
        str[left] = str[right];
        str[right] = tmp;
        left++;
        right--;
    }
}

int main()
{
    char str[] = "abcdef";
    printf("反转前: %s\n", str);
    reverse_string(str);
    printf("反转后: %s\n", str);
    return 0;
}

// ========================================
// 示例4：查找子串（strstr）
// ========================================
#include <stdio.h>
#include <string.h>

char* my_strstr(const char* haystack, const char* needle)
{
    if (*needle == '\0') return (char*)haystack;
    while (*haystack)
    {
        const char* h = haystack;
        const char* n = needle;
        while (*h && *n && *h == *n)
        {
            h++;
            n++;
        }
        if (*n == '\0')
            return (char*)haystack;
        haystack++;
    }
    return NULL;
}

int main()
{
    char str[] = "hello world";
    char* pos = my_strstr(str, "world");
    if (pos)
        printf("找到子串: %s\n", pos);  // world
    else
        printf("未找到\n");
    return 0;
}
"""

KP_C08_QS = [
    {"q_id": "q_c08_1", "type": "single_choice", "content": "strlen(\"hello\")的返回值是？",
     "options": [{"id": "A", "text": "4"}, {"id": "B", "text": "5"}, {"id": "C", "text": "6"}, {"id": "D", "text": "7"}],
     "correct_answer": "B", "explanation": "strlen计算字符串长度，不包含结束符\\0，所以hello的长度是5。"},
    {"q_id": "q_c08_2", "type": "single_choice", "content": "char str[]=\"abc\"; sizeof(str)的值是？",
     "options": [{"id": "A", "text": "3"}, {"id": "B", "text": "4"}, {"id": "C", "text": "5"}, {"id": "D", "text": "不确定"}],
     "correct_answer": "B", "explanation": "\"abc\"在内存中实际存储为{'a','b','c','\\0'}，sizeof计算的是4个字节。"},
    {"q_id": "q_c08_3", "type": "single_choice", "content": "strcmp返回0表示什么？",
     "options": [{"id": "A", "text": "第一个字符串更长"}, {"id": "B", "text": "两个字符串相等"}, {"id": "C", "text": "第二个字符串更长"}, {"id": "D", "text": "比较出错"}],
     "correct_answer": "B", "explanation": "strcmp返回0表示两个字符串完全相等，返回正数表示第一个更大，负数表示第二个更大。"},
]

KP_C08_MM = {"root": "字符串", "children": [
    {"name": "字符数组"}, {"name": "strlen"}, {"name": "strcpy/strcat"},
    {"name": "strcmp"}, {"name": "字符串反转"}, {"name": "常见陷阱"}
]}

# ============================================================
# kp_c09: 函数与递归
# ============================================================
KP_C09_DOC = r"""# 函数与递归

## 一、函数基础

### 函数定义
```c
返回类型 函数名(参数列表)
{
    函数体;
    return 返回值;
}
```

### 函数声明（原型）
```c
int Add(int x, int y);  // 声明放在main之前或头文件中
```

## 二、传值调用 vs 传址调用

### 传值调用（无法修改实参）
```c
void swap_wrong(int x, int y)
{
    int tmp = x;
    x = y;
    y = tmp;
    // 只交换了形参，实参不变！
}
```

### 传址调用（可以修改实参）
```c
void swap_right(int* x, int* y)
{
    int tmp = *x;
    *x = *y;
    *y = tmp;
    // 通过指针修改了实参的值
}
```

## 三、函数的嵌套调用与链式访问

```c
// 链式访问：将一个函数的返回值作为另一个函数的参数
printf("%d\n", strlen("hello"));     // 链式
int len = strlen("hello");
printf("%d\n", len);                 // 非链式
```

## 四、递归

### 递归的两个必要条件
1. 有**终止条件**（递归出口）
2. 每次递归问题**规模缩小**

### 经典递归示例

**阶乘**：
```c
int factorial(int n)
{
    if (n <= 1) return 1;  // 终止条件
    return n * factorial(n - 1);  // 递归调用
}
```

**斐波那契数列**：
```c
int fib(int n)
{
    if (n <= 2) return 1;
    return fib(n - 1) + fib(n - 2);
}
// 注意：递归实现效率低，有大量重复计算
```

### 递归优化：尾递归 → 迭代
```c
// 迭代版阶乘（更高效）
int factorial_iter(int n)
{
    int result = 1;
    for (int i = 2; i <= n; i++)
        result *= i;
    return result;
}
```

## 五、回调函数

将函数指针作为参数传递给另一个函数：
```c
void qsort(void* base, size_t nmemb, size_t size,
           int (*compar)(const void*, const void*));
```

使用示例：
```c
int compare(const void* a, const void* b)
{
    return (*(int*)a - *(int*)b);
}
int arr[] = {5, 2, 8, 1, 9};
qsort(arr, 5, sizeof(int), compare);
```
"""

KP_C09_CODE = r"""// ========================================
// 示例1：传值 vs 传址
// ========================================
#include <stdio.h>

// 传值调用 —— 无法交换
void swap_wrong(int x, int y)
{
    int tmp = x;
    x = y;
    y = tmp;
    printf("函数内: x=%d, y=%d\n", x, y);
}

// 传址调用 —— 可以交换
void swap_right(int* x, int* y)
{
    int tmp = *x;
    *x = *y;
    *y = tmp;
    printf("函数内: x=%d, y=%d\n", *x, *y);
}

int main()
{
    int a = 10, b = 20;
    swap_wrong(a, b);
    printf("传值后: a=%d, b=%d\n", a, b);  // a=10, b=20

    swap_right(&a, &b);
    printf("传址后: a=%d, b=%d\n", a, b);  // a=20, b=10
    return 0;
}

// ========================================
// 示例2：递归求阶乘
// ========================================
#include <stdio.h>

long long factorial(int n)
{
    if (n <= 1) return 1;
    return n * factorial(n - 1);
}

int main()
{
    for (int i = 1; i <= 10; i++)
        printf("%d! = %lld\n", i, factorial(i));
    return 0;
}

// ========================================
// 示例3：递归求第n个斐波那契数
// ========================================
#include <stdio.h>

// 递归版（效率低）
int fib_r(int n)
{
    if (n <= 2) return 1;
    return fib_r(n - 1) + fib_r(n - 2);
}

// 迭代版（高效）
int fib_i(int n)
{
    if (n <= 2) return 1;
    int a = 1, b = 1, c;
    for (int i = 3; i <= n; i++)
    {
        c = a + b;
        a = b;
        b = c;
    }
    return c;
}

int main()
{
    for (int i = 1; i <= 10; i++)
        printf("fib(%d) = %d (递归), %d (迭代)\n", i, fib_r(i), fib_i(i));
    return 0;
}

// ========================================
// 示例4：递归反转字符串
// ========================================
#include <stdio.h>
#include <string.h>

void reverse(char* str)
{
    int len = strlen(str);
    if (len <= 1) return;

    // 交换首尾字符
    char tmp = str[0];
    str[0] = str[len - 1];
    str[len - 1] = '\0';  // 临时截断
    reverse(str + 1);      // 递归处理中间部分
    str[len - 1] = tmp;    // 恢复
}

int main()
{
    char str[] = "abcdef";
    printf("反转前: %s\n", str);
    reverse(str);
    printf("反转后: %s\n", str);
    return 0;
}
"""

KP_C09_QS = [
    {"q_id": "q_c09_1", "type": "single_choice", "content": "C语言中函数参数的传递方式是？",
     "options": [{"id": "A", "text": "传名调用"}, {"id": "B", "text": "传值调用"}, {"id": "C", "text": "传引用调用"}, {"id": "D", "text": "传址调用"}],
     "correct_answer": "B", "explanation": "C语言默认是传值调用，传递的是实参的副本。要修改实参需要传递地址（传址调用）。"},
    {"q_id": "q_c09_2", "type": "single_choice", "content": "递归必须具备的两个条件是？",
     "options": [{"id": "A", "text": "循环和判断"}, {"id": "B", "text": "终止条件和规模缩小"}, {"id": "C", "text": "返回值和参数"}, {"id": "D", "text": "头文件和源文件"}],
     "correct_answer": "B", "explanation": "递归必须有终止条件（防止无限递归）和每次递归问题规模缩小（最终达到终止条件）。"},
    {"q_id": "q_c09_3", "type": "single_choice", "content": "函数声明（原型）的作用是？",
     "options": [{"id": "A", "text": "定义函数体"}, {"id": "B", "text": "告诉编译器函数的返回类型和参数"}, {"id": "C", "text": "分配内存"}, {"id": "D", "text": "执行函数"}],
     "correct_answer": "B", "explanation": "函数声明告诉编译器函数的名称、返回类型和参数类型，使编译器在调用前知道函数签名。"},
]

KP_C09_MM = {"root": "函数与递归", "children": [
    {"name": "函数定义"}, {"name": "传值传址"}, {"name": "嵌套调用"},
    {"name": "递归思维"}, {"name": "阶乘与斐波那契"}, {"name": "回调函数"}
]}

# ============================================================
# kp_c10: 指针基础
# ============================================================
KP_C10_DOC = r"""# 指针基础

## 一、内存与地址

每个变量在内存中都有一个地址，指针就是存储地址的变量：
```c
int a = 10;
printf("a的值: %d\n", a);        // 10
printf("a的地址: %p\n", &a);     // 如 0x7ffd5e8a
```

## 二、指针变量

```c
int a = 10;
int* p = &a;      // p存储a的地址
printf("%d\n", *p);  // 10，通过解引用访问a的值
*p = 20;              // 通过指针修改a的值
printf("%d\n", a);    // 20
```

### 指针大小
```c
// 32位系统：所有指针占4字节
// 64位系统：所有指针占8字节
printf("%zu\n", sizeof(int*));     // 4或8
printf("%zu\n", sizeof(char*));    // 4或8
printf("%zu\n", sizeof(double*));  // 4或8
```

## 三、野指针

野指针是指向不确定位置的指针，非常危险：

1. **未初始化**：`int* p; *p = 10;`（p指向随机位置）
2. **越界访问**：`int arr[5]; int* p = arr; *(p+10) = 0;`
3. **返回局部变量地址**：`int* f() { int a=10; return &a; }`

### 如何避免野指针
1. 初始化时赋值为`NULL`
2. 小心数组越界
3. 不要返回局部变量的地址
4. 使用前检查是否为`NULL`

## 四、指针运算

### 指针 ± 整数
```c
int arr[] = {10, 20, 30, 40, 50};
int* p = arr;
printf("%d\n", *(p + 2));  // 30（跳过2个int）
```

### 指针 - 指针
```c
int arr[] = {10, 20, 30, 40, 50};
int* p1 = &arr[0];
int* p2 = &arr[4];
printf("%d\n", p2 - p1);  // 4（两个指针之间的元素个数）
```

### 模拟实现strlen（指针方式）
```c
int my_strlen(char* str)
{
    char* start = str;
    while (*str != '\0')
        str++;
    return str - start;  // 指针相减得到长度
}
```

## 五、const修饰指针

```c
int a = 10;

// 1. const修饰指针指向的值 —— 指针可变，值不可变
const int* p1 = &a;
*p1 = 20;    // 编译错误！
p1 = &b;     // 正确

// 2. const修饰指针本身 —— 指针不可变，值可变
int* const p2 = &a;
*p2 = 20;    // 正确
p2 = &b;     // 编译错误！

// 3. 两者都修饰
const int* const p3 = &a;
// 既不能改指针，也不能改值
```

> **记忆口诀**：const在`*`左边修饰值，在`*`右边修饰指针。
"""

KP_C10_CODE = r"""// ========================================
// 示例1：指针基本用法
// ========================================
#include <stdio.h>

int main()
{
    int a = 10;
    int* p = &a;

    printf("a的值: %d\n", a);
    printf("a的地址: %p\n", (void*)&a);
    printf("p的值(地址): %p\n", (void*)p);
    printf("p指向的值: %d\n", *p);

    *p = 20;  // 通过指针修改a
    printf("修改后a = %d\n", a);  // 20
    return 0;
}

// ========================================
// 示例2：指针运算
// ========================================
#include <stdio.h>

int main()
{
    int arr[] = {10, 20, 30, 40, 50};
    int* p = arr;

    // 指针+整数
    for (int i = 0; i < 5; i++)
        printf("*(p+%d) = %d\n", i, *(p + i));

    // 指针-指针
    int* start = &arr[0];
    int* end = &arr[4];
    printf("元素个数: %ld\n", end - start);  // 4
    return 0;
}

// ========================================
// 示例3：const修饰指针
// ========================================
#include <stdio.h>

int main()
{
    int a = 10, b = 20;

    // const在*左边：不能通过指针修改值
    const int* p1 = &a;
    // *p1 = 30;    // 编译错误
    p1 = &b;       // 可以改变指向
    printf("*p1 = %d\n", *p1);

    // const在*右边：指针本身不能改变
    int* const p2 = &a;
    *p2 = 30;      // 可以修改值
    // p2 = &b;    // 编译错误
    printf("a = %d\n", a);

    return 0;
}

// ========================================
// 示例4：指针方式模拟strlen
// ========================================
#include <stdio.h>

int my_strlen(const char* str)
{
    const char* start = str;
    while (*str != '\0')
        str++;
    return str - start;
}

int main()
{
    printf("length of 'hello': %d\n", my_strlen("hello"));       // 5
    printf("length of '': %d\n", my_strlen(""));                 // 0
    printf("length of 'hello world': %d\n", my_strlen("hello world"));  // 11
    return 0;
}
"""

KP_C10_QS = [
    {"q_id": "q_c10_1", "type": "single_choice", "content": "在64位系统中，指针变量占多少字节？",
     "options": [{"id": "A", "text": "4字节"}, {"id": "B", "text": "8字节"}, {"id": "C", "text": "取决于指向的数据类型"}, {"id": "D", "text": "1字节"}],
     "correct_answer": "B", "explanation": "在64位系统中，所有类型的指针都占8字节（64位地址空间）。"},
    {"q_id": "q_c10_2", "type": "single_choice", "content": "const int* p 和 int* const p 的区别是？",
     "options": [{"id": "A", "text": "没有区别"}, {"id": "B", "text": "前者不能改指针指向，后者不能改值"}, {"id": "C", "text": "前者不能改值，后者不能改指针指向"}, {"id": "D", "text": "都是常量指针"}],
     "correct_answer": "C", "explanation": "const int* p：不能通过p修改值（常量指针）；int* const p：p本身不能改变指向（指针常量）。"},
    {"q_id": "q_c10_3", "type": "single_choice", "content": "以下哪种情况会产生野指针？",
     "options": [{"id": "A", "text": "int* p = NULL;"}, {"id": "B", "text": "int* p = &a;"}, {"id": "C", "text": "int* p; *p = 10;"}, {"id": "D", "text": "int a = 10; int* p = &a;"}],
     "correct_answer": "C", "explanation": "未初始化的指针p指向随机地址，解引用写入会导致未定义行为（野指针）。"},
]

KP_C10_MM = {"root": "指针基础", "children": [
    {"name": "内存地址"}, {"name": "指针变量"}, {"name": "解引用"},
    {"name": "野指针"}, {"name": "指针运算"}, {"name": "const指针"}
]}

# ============================================================
# kp_c11: 指针与数组
# ============================================================
KP_C11_DOC = r"""# 指针与数组

## 一、数组名的本质

数组名在大多数情况下等价于**首元素的地址**：
```c
int arr[5] = {10, 20, 30, 40, 50};
printf("%p\n", (void*)arr);        // 等价于 &arr[0]
printf("%p\n", (void*)&arr[0]);    // 首元素地址

// 两种例外：
// 1. sizeof(数组名) → 计算整个数组的大小
printf("%zu\n", sizeof(arr));  // 20（5*sizeof(int)）
// 2. &数组名 → 取整个数组的地址
printf("%p\n", (void*)&arr);   // 类型是int(*)[5]
```

## 二、指针数组 vs 数组指针

### 指针数组（数组，每个元素是指针）
```c
int* arr[3];  // 3个int指针组成的数组
int a = 1, b = 2, c = 3;
arr[0] = &a;
arr[1] = &b;
arr[2] = &c;
```

### 数组指针（指针，指向一个数组）
```c
int arr[5] = {1, 2, 3, 4, 5};
int (*p)[5] = &arr;  // p指向整个数组
```

> **区分方法**：看`*`和谁先结合。`int (*p)[5]`：p先和`*`结合 → 指针；`int* p[5]`：p先和`[5]`结合 → 数组。

## 三、二维数组传参

二维数组传参时，形参可以写成数组形式或指针形式：
```c
// 方式1：数组形式
void print_arr(int arr[][4], int row, int col)
{
    for (int i = 0; i < row; i++)
        for (int j = 0; j < col; j++)
            printf("%d ", arr[i][j]);
}

// 方式2：数组指针形式
void print_arr(int (*p)[4], int row, int col)
{
    for (int i = 0; i < row; i++)
        for (int j = 0; j < col; j++)
            printf("%d ", p[i][j]);
}
```

> **注意**：二维数组传参时，行可以省略，列不能省略。

## 四、二级指针

指针的指针，用于存放指针变量的地址：
```c
int a = 10;
int* p = &a;    // 一级指针
int** pp = &p;  // 二级指针

printf("%d\n", **pp);  // 10，两次解引用
```
"""

KP_C11_CODE = r"""// ========================================
// 示例1：数组名的含义
// ========================================
#include <stdio.h>

int main()
{
    int arr[5] = {1, 2, 3, 4, 5};

    printf("arr    = %p\n", (void*)arr);
    printf("&arr[0]= %p\n", (void*)&arr[0]);
    printf("sizeof(arr) = %zu\n", sizeof(arr));      // 20
    printf("sizeof(arr[0]) = %zu\n", sizeof(arr[0])); // 4
    printf("元素个数: %zu\n", sizeof(arr)/sizeof(arr[0])); // 5
    return 0;
}

// ========================================
// 示例2：指针数组与数组指针
// ========================================
#include <stdio.h>

int main()
{
    // 指针数组
    int a = 10, b = 20, c = 30;
    int* parr[3] = {&a, &b, &c};
    for (int i = 0; i < 3; i++)
        printf("parr[%d] = %d\n", i, *parr[i]);

    // 数组指针
    int arr[5] = {10, 20, 30, 40, 50};
    int (*p)[5] = &arr;
    for (int i = 0; i < 5; i++)
        printf("(*p)[%d] = %d\n", i, (*p)[i]);
    return 0;
}

// ========================================
// 示例3：二级指针
// ========================================
#include <stdio.h>

int main()
{
    int a = 100;
    int* p = &a;
    int** pp = &p;

    printf("a = %d\n", a);       // 100
    printf("*p = %d\n", *p);     // 100
    printf("**pp = %d\n", **pp); // 100

    **pp = 200;  // 通过二级指针修改a
    printf("修改后 a = %d\n", a); // 200
    return 0;
}

// ========================================
// 示例4：用指针遍历二维数组
// ========================================
#include <stdio.h>

int main()
{
    int arr[3][4] = {{1,2,3,4}, {5,6,7,8}, {9,10,11,12}};
    int (*p)[4] = arr;  // 数组指针指向二维数组首行

    for (int i = 0; i < 3; i++)
    {
        for (int j = 0; j < 4; j++)
            printf("%-4d", *(*(p + i) + j));
        printf("\n");
    }
    return 0;
}
"""

KP_C11_QS = [
    {"q_id": "q_c11_1", "type": "single_choice", "content": "int (*p)[5] 中p的类型是？",
     "options": [{"id": "A", "text": "int*"}, {"id": "B", "text": "int[5]"}, {"id": "C", "text": "int(*)[5]（指向含5个int的数组的指针）"}, {"id": "D", "text": "int**"}],
     "correct_answer": "C", "explanation": "p先和*结合，说明p是指针，指向一个含5个int元素的数组。"},
    {"q_id": "q_c11_2", "type": "single_choice", "content": "sizeof(数组名) 与 sizeof(&数组名) 的区别是？",
     "options": [{"id": "A", "text": "没有区别"}, {"id": "B", "text": "前者是数组总大小，后者是指针大小"}, {"id": "C", "text": "前者是指针大小，后者是数组总大小"}, {"id": "D", "text": "编译错误"}],
     "correct_answer": "B", "explanation": "sizeof(数组名)计算整个数组大小；sizeof(&数组名)计算的是指针大小（4或8字节）。"},
    {"q_id": "q_c11_3", "type": "single_choice", "content": "二级指针int** pp中，**pp等价于？",
     "options": [{"id": "A", "text": "pp"}, {"id": "B", "text": "*pp"}, {"id": "C", "text": "a（原始变量）"}, {"id": "D", "text": "&a"}],
     "correct_answer": "C", "explanation": "**pp是对二级指针的两次解引用，第一次得到一级指针，第二次得到原始变量的值。"},
]

KP_C11_MM = {"root": "指针与数组", "children": [
    {"name": "数组名本质"}, {"name": "指针数组"}, {"name": "数组指针"},
    {"name": "二维数组传参"}, {"name": "二级指针"}
]}

# ============================================================
# kp_c12: 结构体与联合体
# ============================================================
KP_C12_DOC = r"""# 结构体与联合体

## 一、结构体定义与使用

### 定义结构体
```c
struct Student
{
    char name[20];
    int age;
    float score;
};
```

### 创建和初始化
```c
struct Student s1 = {"张三", 20, 95.5};
struct Student s2;  // 未初始化
```

### 访问成员
```c
// 用.操作符访问结构体变量的成员
printf("姓名: %s\n", s1.name);
printf("年龄: %d\n", s1.age);

// 用->操作符通过指针访问
struct Student* ps = &s1;
printf("姓名: %s\n", ps->name);
```

## 二、typedef简化结构体

```c
typedef struct
{
    char name[20];
    int age;
} Student;  // 现在可以直接用Student代替struct Student

Student s1 = {"李四", 22};
```

## 三、结构体传值 vs 传址

```c
// 传值：拷贝整个结构体（开销大）
void print_student(struct Student s)
{
    printf("%s %d\n", s.name, s.age);
}

// 传址：只传指针（推荐）
void print_student(const struct Student* ps)
{
    printf("%s %d\n", ps->name, ps->age);
}
```

## 四、结构体内存对齐

结构体成员在内存中的存储不是紧密排列的，需要**内存对齐**：

```c
struct S
{
    char c;    // 1字节 + 3字节填充
    int i;     // 4字节
    double d;  // 8字节
};
printf("%zu\n", sizeof(struct S));  // 16，不是13
```

### 对齐规则
1. 第一个成员放在偏移量为0的位置
2. 其他成员放在对齐数（成员大小与默认对齐数的较小值）的整数倍位置
3. 结构体总大小是最大对齐数的整数倍

### 使用#pragma pack控制对齐
```c
#pragma pack(1)  // 设置默认对齐数为1
struct S
{
    char c;
    int i;
    double d;
};
#pragma pack()   // 恢复默认对齐
// sizeof(struct S) = 13
```

## 五、位段

结构体中可以指定成员占用的位数：
```c
struct Flags
{
    unsigned int a : 1;  // 只占1位
    unsigned int b : 3;  // 只占3位
    unsigned int c : 4;  // 只占4位
};
```

## 六、枚举

```c
enum Color
{
    RED,       // 0
    GREEN,     // 1
    BLUE       // 2
};

enum Week
{
    MON = 1,   // 从1开始
    TUE,       // 2
    WED        // 3
};
```

## 七、联合体（共用体）

所有成员共享同一块内存：
```c
union Data
{
    int i;
    float f;
    char c;
};
printf("%zu\n", sizeof(union Data));  // 4（取最大成员的大小）

// 用于判断大小端
union Endian
{
    int i;
    char c;
};
union Endian e = {1};
printf("%s\n", e.c == 1 ? "小端" : "大端");
```
"""

KP_C12_CODE = r"""// ========================================
// 示例1：结构体定义与使用
// ========================================
#include <stdio.h>
#include <string.h>

struct Student
{
    char name[20];
    int age;
    float score;
};

void print_student(const struct Student* ps)
{
    printf("姓名: %s, 年龄: %d, 成绩: %.1f\n",
           ps->name, ps->age, ps->score);
}

int main()
{
    struct Student s1 = {"张三", 20, 95.5};
    struct Student s2;
    strcpy(s2.name, "李四");
    s2.age = 22;
    s2.score = 88.0;

    print_student(&s1);
    print_student(&s2);
    return 0;
}

// ========================================
// 示例2：结构体内存对齐
// ========================================
#include <stdio.h>
#include <stddef.h>

struct S1
{
    char c;
    int i;
    double d;
};

struct S2
{
    double d;
    int i;
    char c;
};

int main()
{
    printf("struct S1: %zu\n", sizeof(struct S1));  // 16
    printf("struct S2: %zu\n", sizeof(struct S2));  // 12

    printf("S1.c offset: %zu\n", offsetof(struct S1, c));
    printf("S1.i offset: %zu\n", offsetof(struct S1, i));
    printf("S1.d offset: %zu\n", offsetof(struct S1, d));
    return 0;
}

// ========================================
// 示例3：枚举与联合体
// ========================================
#include <stdio.h>

enum Week { MON=1, TUE, WED, THU, FRI, SAT, SUN };

union Endian
{
    int i;
    char c;
};

int main()
{
    // 枚举
    for (int i = MON; i <= SUN; i++)
        printf("%d ", i);
    printf("\n");

    // 联合体判断大小端
    union Endian e = {1};
    if (e.c == 1)
        printf("小端存储\n");
    else
        printf("大端存储\n");
    return 0;
}

// ========================================
// 示例4：位段
// ========================================
#include <stdio.h>

struct Flags
{
    unsigned int a : 1;
    unsigned int b : 3;
    unsigned int c : 4;
    unsigned int d : 24;
};

int main()
{
    printf("sizeof(Flags) = %zu\n", sizeof(struct Flags));  // 4

    struct Flags f = {1, 5, 12, 0};
    printf("a=%u, b=%u, c=%u, d=%u\n", f.a, f.b, f.c, f.d);
    return 0;
}
"""

KP_C12_QS = [
    {"q_id": "q_c12_1", "type": "single_choice", "content": "结构体中，.和->操作符的区别是？",
     "options": [{"id": "A", "text": "没有区别"}, {"id": "B", "text": ".用于变量，->用于指针"}, {"id": "C", "text": ".用于指针，->用于变量"}, {"id": "D", "text": ".用于数组，->用于结构体"}],
     "correct_answer": "B", "explanation": ".操作符用于结构体变量直接访问成员，->用于结构体指针间接访问成员。"},
    {"q_id": "q_c12_2", "type": "single_choice", "content": "联合体所有成员的内存关系是？",
     "options": [{"id": "A", "text": "各自独立"}, {"id": "B", "text": "共享同一块内存"}, {"id": "C", "text": "顺序排列"}, {"id": "D", "text": "随机分配"}],
     "correct_answer": "B", "explanation": "联合体的所有成员共享同一块内存空间，大小为最大成员的大小。"},
    {"q_id": "q_c12_3", "type": "single_choice", "content": "struct S { char c; int i; double d; }; sizeof(struct S) 最可能是？",
     "options": [{"id": "A", "text": "13"}, {"id": "B", "text": "16"}, {"id": "C", "text": "12"}, {"id": "D", "text": "8"}],
     "correct_answer": "B", "explanation": "由于内存对齐，char后填充3字节，总大小为1+3+4+8=16字节。"},
]

KP_C12_MM = {"root": "结构体与联合体", "children": [
    {"name": "结构体定义"}, {"name": "typedef"}, {"name": "内存对齐"},
    {"name": "位段"}, {"name": "枚举enum"}, {"name": "联合体union"}
]}

# ============================================================
# kp_c13: 文件操作
# ============================================================
KP_C13_DOC = r"""# 文件操作

## 一、文件指针

```c
FILE* fp = fopen("test.txt", "r");  // 打开文件
if (fp == NULL)
{
    perror("打开文件失败");
    return 1;
}
// ... 操作文件 ...
fclose(fp);  // 关闭文件
```

## 二、文件打开模式

| 模式 | 含义 | 文件不存在 |
|------|------|-----------|
| `"r"` | 只读 | 打开失败 |
| `"w"` | 只写（清空） | 创建新文件 |
| `"a"` | 追加 | 创建新文件 |
| `"rb"` | 二进制只读 | 打开失败 |
| `"wb"` | 二进制只写 | 创建新文件 |
| `"r+"` | 读写 | 打开失败 |
| `"w+"` | 读写（清空） | 创建新文件 |

## 三、字符读写

```c
// fputc：写一个字符
fputc('A', fp);

// fgetc：读一个字符
int ch = fgetc(fp);  // 返回读取的字符，失败返回EOF
```

## 四、字符串读写

```c
// fputs：写一个字符串
fputs("hello world\n", fp);

// fgets：读一行字符串
char buf[100];
fgets(buf, 100, fp);  // 最多读99个字符，自动加\0
```

## 五、格式化读写

```c
// fprintf：格式化写入
fprintf(fp, "name=%s, age=%d\n", name, age);

// fscanf：格式化读取
fscanf(fp, "name=%s, age=%d", name, &age);
```

## 六、二进制读写

```c
// fwrite：二进制写入
fwrite(&student, sizeof(struct Student), 1, fp);

// fread：二进制读取
fread(&student, sizeof(struct Student), 1, fp);
```

## 七、文件定位

```c
fseek(fp, 0, SEEK_SET);    // 移到文件开头
fseek(fp, 0, SEEK_END);    // 移到文件末尾
fseek(fp, offset, SEEK_CUR); // 从当前位置偏移

long pos = ftell(fp);       // 返回当前位置
rewind(fp);                  // 回到文件开头
```

## 八、错误处理

```c
// feof：判断是否到达文件末尾
if (feof(fp)) printf("文件结束\n");

// ferror：判断是否发生错误
if (ferror(fp)) printf("读写错误\n");

// perror：打印错误信息
perror("fopen");  // 输出: fopen: No such file or directory

// strerror：返回错误描述字符串
#include <errno.h>
printf("%s\n", strerror(errno));
```
"""

KP_C13_CODE = r"""// ========================================
// 示例1：文件写入与读取（文本）
// ========================================
#include <stdio.h>

int main()
{
    // 写入
    FILE* fp = fopen("test.txt", "w");
    if (fp == NULL) { perror("fopen"); return 1; }

    fprintf(fp, "Hello, File!\n");
    fprintf(fp, "name=%s age=%d\n", "张三", 20);
    fclose(fp);

    // 读取
    fp = fopen("test.txt", "r");
    if (fp == NULL) { perror("fopen"); return 1; }

    char buf[100];
    while (fgets(buf, sizeof(buf), fp) != NULL)
        printf("%s", buf);
    fclose(fp);
    return 0;
}

// ========================================
// 示例2：二进制文件读写
// ========================================
#include <stdio.h>
#include <string.h>

struct Student
{
    char name[20];
    int age;
    float score;
};

int main()
{
    // 写入二进制文件
    struct Student students[] = {
        {"张三", 20, 95.5},
        {"李四", 22, 88.0},
        {"王五", 21, 92.0}
    };
    int n = sizeof(students) / sizeof(students[0]);

    FILE* fp = fopen("students.dat", "wb");
    fwrite(students, sizeof(struct Student), n, fp);
    fclose(fp);

    // 读取二进制文件
    struct Student s[3];
    fp = fopen("students.dat", "rb");
    fread(s, sizeof(struct Student), n, fp);
    fclose(fp);

    for (int i = 0; i < n; i++)
        printf("姓名: %s, 年龄: %d, 成绩: %.1f\n",
               s[i].name, s[i].age, s[i].score);
    return 0;
}

// ========================================
// 示例3：文件定位
// ========================================
#include <stdio.h>

int main()
{
    FILE* fp = fopen("test.txt", "w");
    fprintf(fp, "ABCDEFGHIJKLMNOPQRSTUVWXYZ");
    fclose(fp);

    fp = fopen("test.txt", "r");
    fseek(fp, 5, SEEK_SET);  // 跳到第5个字符
    char ch = fgetc(fp);
    printf("第6个字符: %c\n", ch);  // F

    fseek(fp, -3, SEEK_END);  // 从末尾倒数第3个
    ch = fgetc(fp);
    printf("倒数第3个字符: %c\n", ch);  // X

    fclose(fp);
    return 0;
}
"""

KP_C13_QS = [
    {"q_id": "q_c13_1", "type": "single_choice", "content": "fopen返回NULL表示什么？",
     "options": [{"id": "A", "text": "文件为空"}, {"id": "B", "text": "文件打开成功"}, {"id": "C", "text": "文件打开失败"}, {"id": "D", "text": "文件已关闭"}],
     "correct_answer": "C", "explanation": "fopen返回NULL表示文件打开失败，可能是文件不存在或权限不足。"},
    {"q_id": "q_c13_2", "type": "single_choice", "content": "fwrite的返回值是？",
     "options": [{"id": "A", "text": "写入的内容"}, {"id": "B", "text": "写入成功的元素个数"}, {"id": "C", "text": "0或1"}, {"id": "D", "text": "文件大小"}],
     "correct_answer": "B", "explanation": "fwrite返回成功写入的完整元素个数，如果少于请求的数量则出错。"},
    {"q_id": "q_c13_3", "type": "single_choice", "content": "fseek(fp, 0, SEEK_END)的作用是？",
     "options": [{"id": "A", "text": "回到文件开头"}, {"id": "B", "text": "移到文件末尾"}, {"id": "C", "text": "删除文件"}, {"id": "D", "text": "关闭文件"}],
     "correct_answer": "B", "explanation": "SEEK_END表示以文件末尾为基准，偏移量为0就是移到文件末尾。"},
]

KP_C13_MM = {"root": "文件操作", "children": [
    {"name": "文件指针"}, {"name": "打开模式"}, {"name": "字符读写"},
    {"name": "字符串读写"}, {"name": "二进制读写"}, {"name": "文件定位"}
]}

# ============================================================
# kp_c14: 动态内存管理
# ============================================================
KP_C14_DOC = r"""# 动态内存管理

## 一、为什么需要动态内存

```c
// 静态数组：编译时确定大小
int arr[100];  // 固定100个元素，可能浪费或不够用

// 动态内存：运行时决定大小
int n;
scanf("%d", &n);
int* arr = (int*)malloc(n * sizeof(int));  // 按需分配
```

## 二、四个核心函数

### malloc
```c
void* malloc(size_t size);
// 分配size字节的内存，不初始化
// 失败返回NULL
```

### calloc
```c
void* calloc(size_t num, size_t size);
// 分配num个size大小的内存，初始化为0
```

### realloc
```c
void* realloc(void* ptr, size_t new_size);
// 调整已分配内存的大小
// 可能移动内存位置，返回新地址
```

### free
```c
void free(void* ptr);
// 释放动态分配的内存
// 释放后指针应置为NULL
```

## 三、常见错误（6种）

### 1. 对NULL指针解引用
```c
int* p = (int*)malloc(100);
*p = 10;  // 如果malloc失败，p为NULL，这里会崩溃
// 正确做法：先检查
if (p == NULL) { /* 处理错误 */ }
```

### 2. 越界访问
```c
int* p = (int*)malloc(5 * sizeof(int));
p[10] = 0;  // 越界！只分配了5个int的空间
```

### 3. 对非动态内存使用free
```c
int a = 10;
int* p = &a;
free(p);  // 错误！a不是动态分配的
```

### 4. 释放动态内存的一部分
```c
int* p = (int*)malloc(10 * sizeof(int));
free(p + 5);  // 错误！应该释放p
```

### 5. 重复释放
```c
int* p = (int*)malloc(100);
free(p);
free(p);  // 错误！已经释放过了
```

### 6. 内存泄漏
```c
void func()
{
    int* p = (int*)malloc(100);
    // 忘记free(p)，函数结束后p丢失，内存泄漏
}
```

## 四、柔性数组

结构体中最后一个成员是未知大小的数组：
```c
struct FlexArray
{
    int size;
    int data[];  // 柔性数组成员（C99）
};

struct FlexArray* p = malloc(sizeof(struct FlexArray) + 10 * sizeof(int));
p->size = 10;
for (int i = 0; i < 10; i++)
    p->data[i] = i;
free(p);
```
"""

KP_C14_CODE = r"""// ========================================
// 示例1：malloc基本使用
// ========================================
#include <stdio.h>
#include <stdlib.h>

int main()
{
    int n;
    printf("请输入数组大小: ");
    scanf("%d", &n);

    int* arr = (int*)malloc(n * sizeof(int));
    if (arr == NULL)
    {
        printf("内存分配失败\n");
        return 1;
    }

    for (int i = 0; i < n; i++)
        arr[i] = (i + 1) * 10;

    for (int i = 0; i < n; i++)
        printf("arr[%d] = %d\n", i, arr[i]);

    free(arr);
    arr = NULL;
    return 0;
}

// ========================================
// 示例2：calloc与realloc
// ========================================
#include <stdio.h>
#include <stdlib.h>

int main()
{
    // calloc：分配并初始化为0
    int* p = (int*)calloc(5, sizeof(int));
    for (int i = 0; i < 5; i++)
        printf("p[%d] = %d\n", i, p[i]);  // 全部为0

    // realloc：扩容
    int* ptr = (int*)realloc(p, 10 * sizeof(int));
    if (ptr != NULL)
    {
        p = ptr;
        for (int i = 5; i < 10; i++)
            p[i] = i * 100;

        printf("\n扩容后:\n");
        for (int i = 0; i < 10; i++)
            printf("p[%d] = %d\n", i, p[i]);
    }
    free(p);
    return 0;
}

// ========================================
// 示例3：动态二维数组
// ========================================
#include <stdio.h>
#include <stdlib.h>

int main()
{
    int row = 3, col = 4;

    // 分配行指针数组
    int** arr = (int**)malloc(row * sizeof(int*));
    for (int i = 0; i < row; i++)
        arr[i] = (int*)malloc(col * sizeof(int));

    // 赋值
    int count = 1;
    for (int i = 0; i < row; i++)
        for (int j = 0; j < col; j++)
            arr[i][j] = count++;

    // 打印
    for (int i = 0; i < row; i++)
    {
        for (int j = 0; j < col; j++)
            printf("%-4d", arr[i][j]);
        printf("\n");
    }

    // 释放
    for (int i = 0; i < row; i++)
        free(arr[i]);
    free(arr);
    return 0;
}

// ========================================
// 示例4：柔性数组
// ========================================
#include <stdio.h>
#include <stdlib.h>

struct FlexArray
{
    int size;
    int data[];
};

int main()
{
    int n = 5;
    struct FlexArray* p = malloc(sizeof(struct FlexArray) + n * sizeof(int));
    p->size = n;

    for (int i = 0; i < n; i++)
        p->data[i] = (i + 1) * 10;

    printf("size = %d\n", p->size);
    for (int i = 0; i < p->size; i++)
        printf("data[%d] = %d\n", i, p->data[i]);

    free(p);
    return 0;
}
"""

KP_C14_QS = [
    {"q_id": "q_c14_1", "type": "single_choice", "content": "malloc和calloc的区别是？",
     "options": [{"id": "A", "text": "没有区别"}, {"id": "B", "text": "calloc会初始化内存为0"}, {"id": "C", "text": "malloc更慢"}, {"id": "D", "text": "calloc不能分配内存"}],
     "correct_answer": "B", "explanation": "calloc分配的内存会自动初始化为0，而malloc不会初始化（内容随机）。"},
    {"q_id": "q_c14_2", "type": "single_choice", "content": "free(p)之后，应该做什么？",
     "options": [{"id": "A", "text": "什么都不做"}, {"id": "B", "text": "立即将p置为NULL"}, {"id": "C", "text": "再次free(p)"}, {"id": "D", "text": "继续使用p"}],
     "correct_answer": "B", "explanation": "free后p成为悬空指针（指向已释放的内存），应立即置为NULL防止误用。"},
    {"q_id": "q_c14_3", "type": "single_choice", "content": "以下哪种情况会造成内存泄漏？",
     "options": [{"id": "A", "text": "使用free释放内存"}, {"id": "B", "text": "malloc后忘记free"}, {"id": "C", "text": "使用realloc扩容"}, {"id": "D", "text": "使用calloc分配内存"}],
     "correct_answer": "B", "explanation": "内存泄漏是指动态分配的内存没有被释放，导致程序持续占用内存。"},
]

KP_C14_MM = {"root": "动态内存管理", "children": [
    {"name": "malloc"}, {"name": "calloc"}, {"name": "realloc"},
    {"name": "free"}, {"name": "常见错误"}, {"name": "柔性数组"}
]}

# ============================================================
# kp_c15: 预处理指令
# ============================================================
KP_C15_DOC = r"""# 预处理指令

## 一、预定义符号

| 符号 | 含义 | 示例输出 |
|------|------|---------|
| `__FILE__` | 当前源文件名 | "main.c" |
| `__LINE__` | 当前行号 | 15 |
| `__DATE__` | 编译日期 | "Jun 03 2026" |
| `__TIME__` | 编译时间 | "14:30:00" |
| `__FUNCTION__` | 当前函数名 | "main" |
| `__STDC__` | 编译器遵循标准 | 1 |

## 二、#define宏定义

### 宏常量
```c
#define MAX 100
#define PI 3.14159
#define PRINT printf("hello\n")
```

### 宏函数
```c
#define MAX(a, b) ((a) > (b) ? (a) : (b))
#define SQUARE(x) ((x) * (x))
```

> **注意**：宏函数中每个参数都要加括号，防止运算符优先级问题。

### 宏的副作用
```c
#define MAX(a, b) ((a) > (b) ? (a) : (b))
int x = 5, y = 8;
int z = MAX(x++, y++);
// 展开为：((x++) > (y++) ? (x++) : (y++))
// x++和y++可能被多次执行！
```

## 三、#和##操作符

### #：字符串化
```c
#define PRINT(x) printf(#x " = %d\n", x)
int a = 10;
PRINT(a);  // 展开为 printf("a" " = %d\n", a); → 输出: a = 10
```

### ##：拼接
```c
#define CONCAT(a, b) a##b
int class101 = 100;
printf("%d\n", CONCAT(class, 101));  // 输出: 100
```

## 四、条件编译

```c
#ifdef DEBUG
    printf("debug mode\n");
#endif

#ifndef RELEASE
    printf("not release mode\n");
#endif

#if SCORE >= 90
    printf("优秀\n");
#elif SCORE >= 60
    printf("及格\n");
#else
    printf("不及格\n");
#endif
```

### #undef取消宏定义
```c
#define TEMP 10
#undef TEMP   // 取消TEMP宏定义
```

## 五、文件包含

```c
#include <stdio.h>   // 系统头文件，在系统路径中查找
#include "myheader.h" // 自定义头文件，在当前目录中查找
```

### 防止头文件重复包含
```c
// 方式1：#ifndef
#ifndef _MYHEADER_H_
#define _MYHEADER_H_
// 头文件内容
#endif

// 方式2：#pragma once（非标准但广泛支持）
#pragma once
```
"""

KP_C15_CODE = r"""// ========================================
// 示例1：预定义符号
// ========================================
#include <stdio.h>

void debug_print(const char* msg)
{
    printf("[%s:%d] %s in %s\n",
           __FILE__, __LINE__, msg, __FUNCTION__);
}

int main()
{
    printf("文件: %s\n", __FILE__);
    printf("行号: %d\n", __LINE__);
    printf("日期: %s\n", __DATE__);
    printf("时间: %s\n", __TIME__);
    debug_print("测试消息");
    return 0;
}

// ========================================
// 示例2：宏函数
// ========================================
#include <stdio.h>

#define MAX(a, b) ((a) > (b) ? (a) : (b))
#define SQUARE(x) ((x) * (x))
#define PRINT_INT(x) printf(#x " = %d\n", x)

int main()
{
    int a = 10, b = 20;
    printf("max = %d\n", MAX(a, b));
    printf("square(5) = %d\n", SQUARE(5));

    PRINT_INT(a);  // a = 10
    PRINT_INT(b);  // b = 20
    return 0;
}

// ========================================
// 示例3：条件编译
// ========================================
#include <stdio.h>

#define DEBUG

int main()
{
    int result = 42;

#ifdef DEBUG
    printf("[DEBUG] result = %d\n", result);
#endif

    printf("最终结果: %d\n", result);
    return 0;
}

// ========================================
// 示例4：泛型宏MAX
// ========================================
#include <stdio.h>

#define GENERIC_MAX(type) \
type type##_max(type a, type b) { return a > b ? a : b; }

GENERIC_MAX(int)
GENERIC_MAX(float)
GENERIC_MAX(double)

int main()
{
    printf("int_max(3,5) = %d\n", int_max(3, 5));
    printf("float_max(3.14, 2.71) = %f\n", float_max(3.14f, 2.71f));
    return 0;
}
"""

KP_C15_QS = [
    {"q_id": "q_c15_1", "type": "single_choice", "content": "#define SQUARE(x) x*x 中SQUARE(3+1)的结果是？",
     "options": [{"id": "A", "text": "16"}, {"id": "B", "text": "7"}, {"id": "C", "text": "13"}, {"id": "D", "text": "编译错误"}],
     "correct_answer": "C", "explanation": "宏展开为3+1*3+1=3+3+1=7（不是16）。每个参数应加括号：((x)*(x))。"},
    {"q_id": "q_c15_2", "type": "single_choice", "content": "#运算符在宏中的作用是？",
     "options": [{"id": "A", "text": "注释"}, {"id": "B", "text": "字符串化"}, {"id": "C", "text": "拼接"}, {"id": "D", "text": "包含文件"}],
     "correct_answer": "B", "explanation": "#运算符将宏参数转换为字符串字面量。"},
    {"q_id": "q_c15_3", "type": "single_choice", "content": "#ifdef的作用是？",
     "options": [{"id": "A", "text": "定义宏"}, {"id": "B", "text": "判断宏是否已定义"}, {"id": "C", "text": "取消宏定义"}, {"id": "D", "text": "包含头文件"}],
     "correct_answer": "B", "explanation": "#ifdef用于条件编译，判断指定的宏是否已经被定义。"},
]

KP_C15_MM = {"root": "预处理指令", "children": [
    {"name": "预定义符号"}, {"name": "#define宏"}, {"name": "宏函数"},
    {"name": "#和##"}, {"name": "条件编译"}, {"name": "文件包含"}
]}

# ============================================================
# kp_c16: 位运算
# ============================================================
KP_C16_DOC = r"""# 位运算

## 一、位运算符

| 运算符 | 名称 | 规则 | 示例 |
|--------|------|------|------|
| `&` | 按位与 | 两位都为1则为1 | 5&3=1 |
| `\|` | 按位或 | 任一为1则为1 | 5\|3=7 |
| `^` | 按位异或 | 不同为1，相同为0 | 5^3=6 |
| `~` | 按位取反 | 0变1，1变0 | ~0=-1 |
| `<<` | 左移 | 乘以2的n次方 | 1<<3=8 |
| `>>` | 右移 | 除以2的n次方 | 8>>2=2 |

## 二、异或的性质

1. `a ^ a = 0`：相同数异或为0
2. `a ^ 0 = a`：任何数异或0为自身
3. `a ^ b = b ^ a`：交换律
4. `(a ^ b) ^ c = a ^ (b ^ c)`：结合律

### 应用：交换两个数（无需临时变量）
```c
a ^= b;
b ^= a;
a ^= b;
```

## 三、位运算实战

### 统计二进制中1的个数
```c
// 方法1：逐位检查
int count1(int n)
{
    int count = 0;
    while (n)
    {
        count += n & 1;
        n >>= 1;
    }
    return count;
}

// 方法2：n & (n-1) 技巧（更快）
int count2(int n)
{
    int count = 0;
    while (n)
    {
        n = n & (n - 1);  // 每次消除最低位的1
        count++;
    }
    return count;
}
```

### 判断2的幂
```c
int is_power_of_two(int n)
{
    return n > 0 && (n & (n - 1)) == 0;
}
```

### 获取/设置/清除第k位
```c
int get_bit(int n, int k) { return (n >> k) & 1; }
int set_bit(int n, int k) { return n | (1 << k); }
int clear_bit(int n, int k) { return n & ~(1 << k); }
```

## 四、大小端判断

```c
int num = 1;
char* p = (char*)&num;
if (*p == 1)
    printf("小端\n");  // 低位字节存低地址
else
    printf("大端\n");  // 高位字节存低地址
```

## 五、原码、反码、补码

| 类型 | 正数 | 负数 |
|------|------|------|
| 原码 | 符号位0 + 真值 | 符号位1 + 真值 |
| 反码 | 同原码 | 符号位不变，其余取反 |
| 补码 | 同原码 | 反码 + 1 |

- 正数的原码、反码、补码相同
- 负数在内存中以补码形式存储
- 补码的好处：0只有一种表示，且加减法统一
"""

KP_C16_CODE = r"""// ========================================
// 示例1：位运算基础
// ========================================
#include <stdio.h>

int main()
{
    int a = 13;  // 1101
    int b = 11;  // 1011

    printf("a & b  = %d (二进制: ", a & b);
    for (int i = 3; i >= 0; i--)
        printf("%d", (a & b) >> i & 1);
    printf(")\n");

    printf("a | b  = %d\n", a | b);
    printf("a ^ b  = %d\n", a ^ b);
    printf("~a     = %d\n", ~a);
    printf("a << 2 = %d\n", a << 2);
    printf("a >> 1 = %d\n", a >> 1);
    return 0;
}

// ========================================
// 示例2：n & (n-1) 技巧
// ========================================
#include <stdio.h>

// 统计二进制中1的个数
int count_bits(int n)
{
    int count = 0;
    while (n)
    {
        n = n & (n - 1);
        count++;
    }
    return count;
}

// 判断是否为2的幂
int is_power_of_two(int n)
{
    return n > 0 && (n & (n - 1)) == 0;
}

int main()
{
    int num = 13;  // 1101 → 3个1
    printf("%d的二进制中有%d个1\n", num, count_bits(num));

    for (int i = 1; i <= 16; i++)
    {
        if (is_power_of_two(i))
            printf("%d是2的幂\n", i);
    }
    return 0;
}

// ========================================
// 示例3：异或交换与找唯一数
// ========================================
#include <stdio.h>

int main()
{
    // 异或交换
    int a = 10, b = 20;
    a ^= b; b ^= a; a ^= b;
    printf("交换后: a=%d, b=%d\n", a, b);

    // 找唯一数：数组中只有一个数出现1次，其余都出现2次
    int arr[] = {1, 2, 3, 2, 1};
    int sz = sizeof(arr) / sizeof(arr[0]);
    int result = 0;
    for (int i = 0; i < sz; i++)
        result ^= arr[i];
    printf("唯一数: %d\n", result);  // 3
    return 0;
}

// ========================================
// 示例4：原码反码补码演示
// ========================================
#include <stdio.h>

void print_binary(int n)
{
    for (int i = 31; i >= 0; i--)
    {
        printf("%d", (n >> i) & 1);
        if (i % 8 == 0) printf(" ");
    }
}

int main()
{
    int a = 5, b = -5;
    printf(" 5的补码: "); print_binary(a); printf("\n");
    printf("-5的补码: "); print_binary(b); printf("\n");
    printf(" 5 + (-5) = %d\n", a + b);
    return 0;
}
"""

KP_C16_QS = [
    {"q_id": "q_c16_1", "type": "single_choice", "content": "以下哪个运算符表示按位异或？",
     "options": [{"id": "A", "text": "&"}, {"id": "B", "text": "|"}, {"id": "C", "text": "^"}, {"id": "D", "text": "~"}],
     "correct_answer": "C", "explanation": "^ 是按位异或运算符，当两位不同时结果为1。"},
    {"q_id": "q_c16_2", "type": "single_choice", "content": "表达式 5 << 2 的结果是？",
     "options": [{"id": "A", "text": "10"}, {"id": "B", "text": "20"}, {"id": "C", "text": "7"}, {"id": "D", "text": "1"}],
     "correct_answer": "B", "explanation": "5的二进制101，左移2位变为10100，即十进制20。左移n位等于乘以2的n次方。"},
    {"q_id": "q_c16_3", "type": "single_choice", "content": "n & (n-1) 的作用是？",
     "options": [{"id": "A", "text": "n加1"}, {"id": "B", "text": "清除n最低位的1"}, {"id": "C", "text": "n乘2"}, {"id": "D", "text": "判断n是否为偶数"}],
     "correct_answer": "B", "explanation": "n & (n-1)会将n二进制表示中最右边的1变为0，常用于统计1的个数和判断2的幂。"},
]

KP_C16_MM = {"root": "位运算", "children": [
    {"name": "按位与/或"}, {"name": "按位异或"}, {"name": "移位运算"},
    {"name": "n&(n-1)技巧"}, {"name": "原码反码补码"}, {"name": "大小端"}
]}


# ============================================================
# 主函数：写入数据库
# ============================================================
ALL_KP = [
    ("kp_c01", "C语言概述与开发环境", "基础入门", 0.2, [], "C语言的历史、特点、开发环境搭建与第一个程序", ["入门", "环境搭建"], KP_C01_DOC, KP_C01_CODE, KP_C01_QS, KP_C01_MM),
    ("kp_c02", "数据类型与变量", "基础入门", 0.25, [], "基本数据类型、变量声明、命名规则、常量、类型转换", ["基础", "变量"], KP_C02_DOC, KP_C02_CODE, KP_C02_QS, KP_C02_MM),
    ("kp_c03", "运算符与表达式", "基础语法", 0.3, ["kp_c02"], "算术、关系、逻辑、位运算符及优先级", ["运算符", "表达式"], KP_C03_DOC, KP_C03_CODE, KP_C03_QS, KP_C03_MM),
    ("kp_c04", "输入输出与顺序结构", "基础语法", 0.3, ["kp_c02"], "printf、scanf格式控制、getchar/putchar与顺序结构", ["IO", "输入输出"], KP_C04_DOC, KP_C04_CODE, KP_C04_QS, KP_C04_MM),
    ("kp_c05", "选择结构", "控制结构", 0.35, ["kp_c03", "kp_c04"], "if、if-else、switch语句与三目运算符", ["if", "switch", "分支"], KP_C05_DOC, KP_C05_CODE, KP_C05_QS, KP_C05_MM),
    ("kp_c06", "循环结构", "控制结构", 0.4, ["kp_c03", "kp_c04"], "for、while、do-while循环与break/continue", ["for", "while", "循环"], KP_C06_DOC, KP_C06_CODE, KP_C06_QS, KP_C06_MM),
    ("kp_c07", "数组", "数组与字符串", 0.45, ["kp_c06"], "一维数组、二维数组、数组遍历与常见算法", ["数组", "排序"], KP_C07_DOC, KP_C07_CODE, KP_C07_QS, KP_C07_MM),
    ("kp_c08", "字符串", "数组与字符串", 0.45, ["kp_c07"], "字符数组、字符串函数、字符串处理算法", ["字符串", "string.h"], KP_C08_DOC, KP_C08_CODE, KP_C08_QS, KP_C08_MM),
    ("kp_c09", "函数与递归", "函数", 0.5, ["kp_c06"], "函数定义、参数传递、递归算法、回调函数", ["函数", "递归"], KP_C09_DOC, KP_C09_CODE, KP_C09_QS, KP_C09_MM),
    ("kp_c10", "指针基础", "指针", 0.55, ["kp_c02", "kp_c09"], "指针概念、取地址与解引用、野指针、const指针", ["指针", "地址"], KP_C10_DOC, KP_C10_CODE, KP_C10_QS, KP_C10_MM),
    ("kp_c11", "指针与数组", "指针", 0.6, ["kp_c10", "kp_c07"], "数组名本质、指针数组与数组指针、二级指针", ["指针数组", "二级指针"], KP_C11_DOC, KP_C11_CODE, KP_C11_QS, KP_C11_MM),
    ("kp_c12", "结构体与联合体", "结构体与文件", 0.5, ["kp_c02", "kp_c07"], "struct定义、内存对齐、位段、枚举、联合体", ["结构体", "联合体"], KP_C12_DOC, KP_C12_CODE, KP_C12_QS, KP_C12_MM),
    ("kp_c13", "文件操作", "结构体与文件", 0.55, ["kp_c12"], "文件打开关闭、文本与二进制读写、文件定位", ["文件", "fread", "fwrite"], KP_C13_DOC, KP_C13_CODE, KP_C13_QS, KP_C13_MM),
    ("kp_c14", "动态内存管理", "高级主题", 0.6, ["kp_c10"], "malloc、calloc、realloc、free与内存泄漏防范", ["动态内存", "malloc"], KP_C14_DOC, KP_C14_CODE, KP_C14_QS, KP_C14_MM),
    ("kp_c15", "预处理指令", "高级主题", 0.4, ["kp_c01"], "宏定义、条件编译、#和##操作符、文件包含", ["预处理", "宏定义"], KP_C15_DOC, KP_C15_CODE, KP_C15_QS, KP_C15_MM),
    ("kp_c16", "位运算", "高级主题", 0.6, ["kp_c03"], "按位与或异或、移位、n&(n-1)技巧、原码补码", ["位运算", "二进制"], KP_C16_DOC, KP_C16_CODE, KP_C16_QS, KP_C16_MM),
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
        print(f"  ✓ {kp_id}: {name}")

    conn.commit()
    conn.close()
    print(f"\n完成！共更新/插入 {len(ALL_KP)} 个知识点。")


if __name__ == "__main__":
    seed()
