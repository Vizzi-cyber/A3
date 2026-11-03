"""
C语言课程完整内容种子脚本
为16个C语言知识点创建详细的教材内容
"""
import sqlite3
import os
import json

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "ai_learning_v2.db")

# ============================================================
# C语言完整教材内容
# ============================================================

DOCUMENTS = {
    "kp_c01": """# C语言概述与开发环境

## 一、C语言的发展历史

C语言由**Dennis Ritchie**于1972年在贝尔实验室开发，最初是为了重写UNIX操作系统。C语言是在B语言的基础上发展起来的，而B语言则源自BCPL。

### 发展时间线
- **1969年**：Ken Thompson用汇编语言编写了UNIX操作系统
- **1970年**：Thompson开发了B语言
- **1972年**：Ritchie在B语言基础上开发了C语言
- **1978年**：K&R C（《The C Programming Language》第一版）
- **1989年**：ANSI C（C89）标准发布
- **1999年**：C99标准发布，支持变长数组、`//`注释等
- **2011年**：C11标准发布，增加多线程、原子操作等

## 二、C语言的特点

1. **简洁紧凑**：关键字仅32个（C89），语法简洁
2. **接近硬件**：支持位运算、指针操作，可直接访问内存地址
3. **可移植性**：遵循标准的C程序可在不同平台上编译运行
4. **库函数丰富**：34个标准库函数，功能强大
5. **结构化**：支持函数、选择、循环等基本结构
6. **执行效率高**：编译后直接生成机器码，运行速度快

## 三、第一个C程序

```c
#include <stdio.h>

int main()
{
    printf("Hello, World!\\n");
    return 0;
}
```

### 代码解析
- `#include <stdio.h>`：预处理指令，包含标准输入输出头文件
- `int main()`：主函数，程序执行的入口点
- `printf(...)`：标准库函数，用于将数据打印到屏幕
- `\\n`：转义字符，表示换行
- `return 0`：返回值0表示程序正常结束

## 四、开发环境搭建

### Windows环境
1. 安装Visual Studio（推荐Community版）或Dev-C++
2. 新建项目 → 控制台应用 → 编写代码 → 编译运行

### 编译流程
```
源代码(.c) → 预处理 → 编译 → 链接 → 运行 → 可执行程序(.exe)
```

## 五、编码规范建议

### 命名规范
- 变量名、函数名：小写字母+下划线，如 `student_count`
- 常量名：全大写+下划线，如 `MAX_SIZE`
- 宏名：全大写，如 `PI`

### 代码风格
```c
// 缩进使用4个空格
int main()
{
    int count = 0;  // 变量声明后加空行

    if (count > 0)
    {
        printf("正数\\n");
    }

    return 0;
}
```

## 六、常见问题

1. **Q：为什么main函数返回int而不是void？**
   A：返回int可以让操作系统了解程序的退出状态，0通常表示成功。

2. **Q：#include <stdio.h>和#include "stdio.h"有什么区别？**
   A：尖括号从系统目录查找，双引号先从当前目录查找。

3. **Q：C语言和C++有什么关系？**
   A：C++是C语言的超集，兼容C语言语法，增加了面向对象等特性。
""",

    "kp_c02": """# 数据类型与变量

## 一、基本数据类型

### 整数类型
| 类型 | 关键字 | 字节范围 | 示例 |
|------|--------|----------|------|
| 短整型 | short | 2字节 | -32768 ~ 32767 |
| 整型 | int | 4字节 | -2^31 ~ 2^31-1 |
| 长整型 | long | 4/8字节 | 依平台而定 |
| 长长整型 | long long | 8字节 | -2^63 ~ 2^63-1 |

### 浮点类型
| 类型 | 关键字 | 字节 | 精度 |
|------|--------|------|------|
| 单精度 | float | 4字节 | 6-7位有效数字 |
| 双精度 | double | 8字节 | 15-16位有效数字 |

### 字符类型
```c
char ch = 'A';      // 字符变量
char str[] = "Hello"; // 字符串（字符数组）
```

## 二、变量的声明与初始化

```c
// 声明变量
int age;
float salary;
char grade;

// 初始化
age = 20;
salary = 3500.50;
grade = 'A';

// 声明时初始化（推荐）
int count = 0;
double pi = 3.14159;
```

## 三、常量的定义

```c
// 使用const关键字
const int MAX_SIZE = 100;
const double PI = 3.14159;

// 使用#define宏定义
#define MAX_SIZE 100
#define PI 3.14159
```

### const与#define的区别
- const有类型检查，#define只是文本替换
- const在编译期处理，#define在预编译期处理
- const可以调试，#define不可以

## 四、类型转换

### 隐式类型转换
```c
int a = 5;
double b = 2.5;
double result = a + b;  // int自动转为double
```

### 显式类型转换（强制转换）
```c
int a = 5, b = 2;
double result = (double)a / b;  // 先将a转为double再除
```

## 五、sizeof运算符

```c
printf("int: %zu bytes\\n", sizeof(int));      // 4
printf("double: %zu bytes\\n", sizeof(double)); // 8
printf("char: %zu bytes\\n", sizeof(char));     // 1
```

## 六、变量的作用域

### 局部变量
```c
void func()
{
    int x = 10;  // 只在func内有效
    printf("%d\\n", x);
}
```

### 全局变量
```c
int global_var = 100;  // 所有函数都可访问

void func1()
{
    global_var = 200;  // 可以修改
}
```

### static静态变量
```c
void func()
{
    static int count = 0;  // 只初始化一次
    count++;
    printf("调用次数: %d\\n", count);
}
```

## 七、常见错误

1. **未初始化变量**
```c
int x;  // 未初始化，值不确定
printf("%d\\n", x);  // 危险！
```

2. **类型溢出**
```c
short big = 40000;  // 溢出，short最大32767
```

3. **整数除法**
```c
int a = 5, b = 2;
printf("%d\\n", a / b);  // 输出2，不是2.5
```
""",

    "kp_c03": """# 运算符与表达式

## 一、算术运算符

| 运算符 | 含义 | 示例 | 结果 |
|--------|------|------|------|
| + | 加法 | 5 + 3 | 8 |
| - | 减法 | 5 - 3 | 2 |
| * | 乘法 | 5 * 3 | 15 |
| / | 除法 | 5 / 3 | 1 |
| % | 取模 | 5 % 3 | 2 |

### 注意事项
```c
// 整数除法
5 / 3 = 1      // 整数部分
5.0 / 3 = 1.6667  // 浮点除法

// 取模运算只能用于整数
7 % 3 = 1
-7 % 3 = -1    // 结果符号与被除数相同
```

## 二、关系运算符

| 运算符 | 含义 | 示例 |
|--------|------|------|
| == | 等于 | a == b |
| != | 不等于 | a != b |
| > | 大于 | a > b |
| < | 小于 | a < b |
| >= | 大于等于 | a >= b |
| <= | 小于等于 | a <= b |

```c
int a = 5, b = 3;
printf("%d\\n", a > b);   // 1（真）
printf("%d\\n", a == b);  // 0（假）
```

## 三、逻辑运算符

| 运算符 | 含义 | 示例 |
|--------|------|------|
| && | 逻辑与 | a && b |
| \|\| | 逻辑或 | a \|\| b |
| ! | 逻辑非 | !a |

### 短路求值
```c
// && 短路：左边为假，右边不执行
int x = 0;
if (x != 0 && 10/x > 2)
{
    // 不会执行到10/x，避免除零错误
}

// || 短路：左边为真，右边不执行
if (x == 0 || 10/x > 2)
{
    // x==0为真时，不执行10/x
}
```

## 四、位运算符

| 运算符 | 含义 | 示例 |
|--------|------|------|
| & | 按位与 | 6 & 5 = 4 |
| \| | 按位或 | 6 \| 5 = 7 |
| ^ | 按位异或 | 6 ^ 5 = 3 |
| ~ | 按位取反 | ~6 = -7 |
| << | 左移 | 1 << 3 = 8 |
| >> | 右移 | 8 >> 2 = 2 |

```c
// 位运算应用
unsigned int flags = 0;

// 设置第3位
flags |= (1 << 3);

// 清除第3位
flags &= ~(1 << 3);

// 检查第3位是否设置
if (flags & (1 << 3))
{
    printf("第3位已设置\\n");
}
```

## 五、赋值运算符

| 运算符 | 等价形式 |
|--------|----------|
| += | a += b → a = a + b |
| -= | a -= b → a = a - b |
| *= | a *= b → a = a * b |
| /= | a /= b → a = a / b |
| %= | a %= b → a = a % b |

## 六、自增自减运算符

```c
int a = 5;
int b = a++;  // b=5, a=6（后置：先用后加）
int c = ++a;  // c=7, a=7（前置：先加后用）

// 注意：避免在复杂表达式中使用
int x = 5;
int y = x++ + ++x;  // 未定义行为，不要这样写！
```

## 七、运算符优先级

从高到低：
1. 括号 `()`
2. 单目运算符 `! ~ ++ -- + - * & (type) sizeof`
3. 算术运算符 `* / %` → `+ -`
4. 移位运算符 `<< >>`
5. 关系运算符 `< <= > >=` → `== !=`
6. 位运算符 `&` → `^` → `|`
7. 逻辑运算符 `&&` → `||`
8. 条件运算符 `?:`
9. 赋值运算符 `= += -= ...`
10. 逗号运算符 `,`

## 八、类型转换规则

```c
// 自动类型转换（隐式）
int a = 5;
double b = 2.5;
double c = a + b;  // a自动转为double

// 强制类型转换（显式）
int a = 5, b = 2;
double result = (double)a / b;  // 先转再除
```
""",

    "kp_c04": """# 输入输出与顺序结构

## 一、格式化输出 printf

### 格式说明符
| 格式符 | 说明 | 示例 |
|--------|------|------|
| %d | 十进制整数 | printf("%d", 100) |
| %o | 八进制 | printf("%o", 100) → 144 |
| %x | 十六进制 | printf("%x", 100) → 64 |
| %f | 浮点数 | printf("%f", 3.14) |
| %e | 科学计数法 | printf("%e", 3.14) |
| %c | 字符 | printf("%c", 'A') |
| %s | 字符串 | printf("%s", "Hello") |
| %p | 指针地址 | printf("%p", &a) |
| %% | 输出%本身 | printf("100%%") |

### 宽度与精度控制
```c
int num = 42;
printf("%10d\\n", num);     // "        42"（右对齐，宽度10）
printf("%-10d\\n", num);    // "42        "（左对齐）
printf("%010d\\n", num);    // "0000000042"（前导零）

double pi = 3.14159;
printf("%.2f\\n", pi);      // "3.14"（保留2位小数）
printf("%10.2f\\n", pi);    // "      3.14"
```

## 二、格式化输入 scanf

```c
int age;
float score;
char grade;

// 基本用法
scanf("%d", &age);        // 注意取地址符&
scanf("%f", &score);
scanf(" %c", &grade);     // 前面加空格跳过空白字符

// 读取多个值
scanf("%d %f %c", &age, &score, &grade);

// 读取字符串（遇空格停止）
char name[50];
scanf("%s", name);  // 数组名就是地址，不需要&
```

### scanf注意事项
1. 必须使用变量地址（加&）
2. 数组名不需要加&
3. 输入时要用空格分隔多个值
4. `%c`会读取空白字符，前面加空格可跳过

## 三、字符输入输出

```c
// getchar()和putchar()
char ch = getchar();  // 读取一个字符
putchar(ch);          // 输出一个字符

// 示例：统计字符个数
int count = 0;
char ch;
while ((ch = getchar()) != '\\n')
{
    count++;
}
printf("字符个数: %d\\n", count);
```

## 四、顺序结构程序设计

### 示例1：交换两个数
```c
#include <stdio.h>

int main()
{
    int a = 5, b = 10;
    int temp;

    // 交换
    temp = a;
    a = b;
    b = temp;

    printf("a=%d, b=%d\\n", a, b);  // a=10, b=5
    return 0;
}
```

### 示例2：计算圆的面积和周长
```c
#include <stdio.h>

#define PI 3.14159

int main()
{
    double radius, area, circumference;

    printf("请输入半径: ");
    scanf("%lf", &radius);

    area = PI * radius * radius;
    circumference = 2 * PI * radius;

    printf("面积: %.2f\\n", area);
    printf("周长: %.2f\\n", circumference);

    return 0;
}
```

### 示例3：华氏温度转摄氏温度
```c
#include <stdio.h>

int main()
{
    float fahrenheit, celsius;

    printf("请输入华氏温度: ");
    scanf("%f", &fahrenheit);

    celsius = (fahrenheit - 32) * 5.0 / 9.0;

    printf("摄氏温度: %.1f\\n", celsius);

    return 0;
}
```

## 五、常见错误

1. **忘记取地址符**
```c
int x;
scanf("%d", x);  // 错误！应该是 &x
```

2. **格式符不匹配**
```c
float f = 3.14;
printf("%d\\n", f);  // 错误！应该用%f
```

3. **getchar()读取换行符**
```c
char ch;
scanf("%d", &x);  // 输入后按回车
ch = getchar();   // 读到的是换行符'\\n'，不是期望的字符
```
""",

    "kp_c05": """# 选择结构

## 一、if语句

### 基本形式
```c
if (条件)
{
    语句块;
}
```

### if-else形式
```c
if (条件)
{
    语句块1;
}
else
{
    语句块2;
}
```

### else-if形式
```c
if (条件1)
{
    语句块1;
}
else if (条件2)
{
    语句块2;
}
else
{
    语句块3;
}
```

### 示例：成绩等级判断
```c
#include <stdio.h>

int main()
{
    int score;

    printf("请输入成绩: ");
    scanf("%d", &score);

    if (score >= 90)
    {
        printf("优秀\\n");
    }
    else if (score >= 80)
    {
        printf("良好\\n");
    }
    else if (score >= 70)
    {
        printf("中等\\n");
    }
    else if (score >= 60)
    {
        printf("及格\\n");
    }
    else
    {
        printf("不及格\\n");
    }

    return 0;
}
```

## 二、switch语句

### 基本语法
```c
switch (表达式)
{
    case 常量1:
        语句块1;
        break;
    case 常量2:
        语句块2;
        break;
    default:
        语句块n;
        break;
}
```

### 示例：简易计算器
```c
#include <stdio.h>

int main()
{
    double num1, num2, result;
    char op;

    printf("请输入表达式 (如: 3 + 5): ");
    scanf("%lf %c %lf", &num1, &op, &num2);

    switch (op)
    {
        case '+':
            result = num1 + num2;
            break;
        case '-':
            result = num1 - num2;
            break;
        case '*':
            result = num1 * num2;
            break;
        case '/':
            if (num2 != 0)
                result = num1 / num2;
            else
            {
                printf("错误：除数不能为0\\n");
                return 1;
            }
            break;
        default:
            printf("错误：未知运算符\\n");
            return 1;
    }

    printf("结果: %.2f\\n", result);
    return 0;
}
```

### switch注意事项
1. case后必须是常量表达式
2. 每个case后要加break
3. case的值不能重复
4. switch只能用于整型、字符型

## 三、条件运算符（三目运算符）

```c
// 语法：条件 ? 表达式1 : 表达式2
int max = (a > b) ? a : b;
```

### 示例：求三个数的最大值
```c
int a = 10, b = 20, c = 30;
int max = (a > b) ? ((a > c) ? a : c) : ((b > c) ? b : c);
```

## 四、嵌套if语句

```c
if (条件1)
{
    if (条件2)
    {
        // 条件1和条件2都为真
    }
    else
    {
        // 条件1为真，条件2为假
    }
}
else
{
    // 条件1为假
}
```

### 注意悬空else问题
```c
// 这个else与哪个if配对？
if (a > 0)
    if (b > 0)
        printf("both positive\\n");
else  // 与最近的if配对，不是最外层的！
    printf("not both positive\\n");
```

## 五、常见错误

1. **if后加分号**
```c
if (x > 0);  // 分号导致if语句为空
{
    printf("正数\\n");  // 这行总是执行
}
```

2. **赋值与比较混淆**
```c
if (x = 5)  // 这是赋值，总是为真！
{
    printf("x是5\\n");
}

// 正确写法
if (x == 5)
{
    printf("x是5\\n");
}
```

3. **switch忘记break**
```c
switch (ch)
{
    case 'A':
        printf("优\\n");
        // 忘记break，会继续执行下面的case
    case 'B':
        printf("良\\n");
        break;
}
```
""",

    "kp_c06": """# 循环结构

## 一、for循环

### 基本语法
```c
for (初始化; 条件; 更新)
{
    循环体;
}
```

### 示例
```c
// 打印1到10
for (int i = 1; i <= 10; i++)
{
    printf("%d ", i);
}

// 计算1+2+...+100
int sum = 0;
for (int i = 1; i <= 100; i++)
{
    sum += i;
}
printf("sum = %d\\n", sum);  // 5050
```

### for循环变体
```c
// 死循环
for (;;)
{
    // 无限循环
}

// 多个初始化和更新
for (int i = 0, j = 10; i < j; i++, j--)
{
    printf("i=%d, j=%d\\n", i, j);
}
```

## 二、while循环

### 基本语法
```c
while (条件)
{
    循环体;
}
```

### 示例
```c
// 计算阶乘
int n = 5;
long long fact = 1;
int i = 1;

while (i <= n)
{
    fact *= i;
    i++;
}
printf("%d! = %lld\\n", n, fact);  // 120
```

### do-while循环
```c
// 至少执行一次
do
{
    循环体;
}
while (条件);
```

### 示例：输入验证
```c
int num;
do
{
    printf("请输入1-100的数字: ");
    scanf("%d", &num);
}
while (num < 1 || num > 100);
```

## 三、循环控制语句

### break语句
```c
// 查找第一个能被7整除的数
for (int i = 1; i <= 100; i++)
{
    if (i % 7 == 0)
    {
        printf("第一个能被7整除的数是: %d\\n", i);
        break;  // 跳出循环
    }
}
```

### continue语句
```c
// 打印1-10中所有奇数
for (int i = 1; i <= 10; i++)
{
    if (i % 2 == 0)
        continue;  // 跳过偶数
    printf("%d ", i);
}
// 输出: 1 3 5 7 9
```

### goto语句（不推荐使用）
```c
// 仅用于多层循环跳出
for (...)
{
    for (...)
    {
        for (...)
        {
            if (条件)
                goto end;  // 跳出所有循环
        }
    }
}
end:
// 继续执行
```

## 四、嵌套循环

### 示例：打印九九乘法表
```c
#include <stdio.h>

int main()
{
    for (int i = 1; i <= 9; i++)
    {
        for (int j = 1; j <= i; j++)
        {
            printf("%d×%d=%-4d", j, i, i * j);
        }
        printf("\\n");
    }
    return 0;
}
```

### 示例：打印菱形
```c
#include <stdio.h>

int main()
{
    int n = 5;

    // 上半部分
    for (int i = 1; i <= n; i++)
    {
        for (int j = 1; j <= n - i; j++)
            printf(" ");
        for (int j = 1; j <= 2 * i - 1; j++)
            printf("*");
        printf("\\n");
    }

    // 下半部分
    for (int i = n - 1; i >= 1; i--)
    {
        for (int j = 1; j <= n - i; j++)
            printf(" ");
        for (int j = 1; j <= 2 * i - 1; j++)
            printf("*");
        printf("\\n");
    }

    return 0;
}
```

## 五、常见循环模式

### 计数器模式
```c
int count = 0;
for (int i = 0; i < n; i++)
{
    if (条件)
        count++;
}
```

### 累加器模式
```c
int sum = 0;
for (int i = 1; i <= n; i++)
{
    sum += i;
}
```

### 查找模式
```c
int found = 0;
for (int i = 0; i < n; i++)
{
    if (arr[i] == target)
    {
        found = 1;
        break;
    }
}
```

## 六、常见错误

1. **无限循环**
```c
int i = 0;
while (i < 10)
{
    printf("%d\\n", i);
    // 忘记i++，导致死循环
}
```

2. **循环边界错误**
```c
// 打印1到10，但写成了<=10
for (int i = 1; i < 10; i++)  // 只打印1-9
```

3. **在循环内修改循环变量**
```c
for (int i = 0; i < 10; i++)
{
    if (i == 5)
        i += 2;  // 可能导致逻辑错误
}
```
""",

    "kp_c07": """# 数组

## 一、一维数组

### 定义与初始化
```c
// 定义数组
int arr[5];  // 未初始化

// 初始化方式
int arr1[5] = {1, 2, 3, 4, 5};  // 完全初始化
int arr2[5] = {1, 2, 3};  // 部分初始化，其余为0
int arr3[] = {1, 2, 3, 4, 5};  // 自动确定大小为5
int arr4[5] = {0};  // 全部初始化为0
```

### 数组访问
```c
int arr[5] = {10, 20, 30, 40, 50};

// 访问元素
printf("%d\\n", arr[0]);  // 10（第一个元素）
printf("%d\\n", arr[4]);  // 50（最后一个元素）

// 修改元素
arr[2] = 300;

// 数组长度
int len = sizeof(arr) / sizeof(arr[0]);  // 5
```

### 示例：求平均值
```c
#include <stdio.h>

int main()
{
    int scores[10];
    int sum = 0;

    printf("请输入10个成绩: ");
    for (int i = 0; i < 10; i++)
    {
        scanf("%d", &scores[i]);
        sum += scores[i];
    }

    printf("平均成绩: %.1f\\n", sum / 10.0);

    return 0;
}
```

## 二、二维数组

### 定义与初始化
```c
// 定义二维数组
int arr[3][4];  // 3行4列

// 初始化方式
int arr1[2][3] = {{1, 2, 3}, {4, 5, 6}};
int arr2[2][3] = {1, 2, 3, 4, 5, 6};  // 按行存储
int arr3[][3] = {{1, 2, 3}, {4, 5, 6}};  // 可省略行数
```

### 二维数组访问
```c
int arr[2][3] = {{1, 2, 3}, {4, 5, 6}};

// 访问元素
printf("%d\\n", arr[0][0]);  // 1
printf("%d\\n", arr[1][2]);  // 6

// 遍历
for (int i = 0; i < 2; i++)
{
    for (int j = 0; j < 3; j++)
    {
        printf("%d ", arr[i][j]);
    }
    printf("\\n");
}
```

### 示例：矩阵转置
```c
#include <stdio.h>

int main()
{
    int a[2][3] = {{1, 2, 3}, {4, 5, 6}};
    int b[3][2];

    // 转置
    for (int i = 0; i < 2; i++)
    {
        for (int j = 0; j < 3; j++)
        {
            b[j][i] = a[i][j];
        }
    }

    // 输出转置后的矩阵
    for (int i = 0; i < 3; i++)
    {
        for (int j = 0; j < 2; j++)
        {
            printf("%d ", b[i][j]);
        }
        printf("\\n");
    }

    return 0;
}
```

## 三、字符数组与字符串

### 字符串的表示
```c
// 字符数组
char str1[6] = {'H', 'e', 'l', 'l', 'o', '\\0'};

// 字符串（自动添加'\\0'）
char str2[] = "Hello";

// 指针方式
char *str3 = "Hello";
```

### 字符串函数（string.h）
```c
#include <string.h>

char str[] = "Hello";

// 求长度（不含'\\0'）
int len = strlen(str);  // 5

// 拼接
char dest[20] = "Hello";
strcat(dest, " World");  // "Hello World"

// 复制
char src[] = "Hello";
char dst[20];
strcpy(dst, src);

// 比较
int cmp = strcmp("abc", "abd");  // 负数（a < b）

// 查找
char *pos = strchr(str, 'l');  // 第一次出现'l'的位置
```

### 示例：字符串反转
```c
#include <stdio.h>
#include <string.h>

void reverse(char *str)
{
    int len = strlen(str);
    for (int i = 0; i < len / 2; i++)
    {
        char temp = str[i];
        str[i] = str[len - 1 - i];
        str[len - 1 - i] = temp;
    }
}

int main()
{
    char str[] = "Hello";
    reverse(str);
    printf("反转后: %s\\n", str);  // olleH
    return 0;
}
```

## 四、常见错误

1. **数组越界**
```c
int arr[5] = {1, 2, 3, 4, 5};
printf("%d\\n", arr[5]);  // 越界！下标0-4有效
```

2. **数组作为函数参数**
```c
// 错误：无法在函数内获取数组长度
void printArray(int arr[])
{
    int len = sizeof(arr) / sizeof(arr[0]);  // 错误！
}

// 正确：传递长度参数
void printArray(int arr[], int len)
{
    for (int i = 0; i < len; i++)
        printf("%d ", arr[i]);
}
```

3. **字符串未留'\0'空间**
```c
char str[5] = "Hello";  // 错误！需要6个字节存放'\\0'
```
""",

    "kp_c08": """# 函数与递归

## 一、函数的定义与调用

### 函数定义
```c
// 返回类型 函数名(参数列表)
// {
//     函数体;
//     return 返回值;
// }

int add(int a, int b)
{
    return a + b;
}

void printHello()
{
    printf("Hello!\\n");
}
```

### 函数调用
```c
int result = add(3, 5);  // result = 8
printHello();
```

## 二、函数参数传递

### 值传递
```c
void swap(int a, int b)  // 无法交换！
{
    int temp = a;
    a = b;
    b = temp;
}

int x = 5, y = 10;
swap(x, y);  // x和y不会改变
```

### 指针传递（地址传递）
```c
void swap(int *a, int *b)  // 可以交换
{
    int temp = *a;
    *a = *b;
    *b = temp;
}

int x = 5, y = 10;
swap(&x, &y);  // x=10, y=5
```

### 数组作为参数
```c
// 数组传递的是地址，可以直接修改
void modifyArray(int arr[], int size)
{
    for (int i = 0; i < size; i++)
    {
        arr[i] *= 2;  // 直接修改原数组
    }
}
```

## 三、递归函数

### 基本概念
递归函数是直接或间接调用自身的函数。

### 示例：阶乘
```c
long long factorial(int n)
{
    if (n <= 1)  // 基线条件
        return 1;
    return n * factorial(n - 1);  // 递归调用
}

printf("%d! = %lld\\n", 5, factorial(5));  // 120
```

### 示例：斐波那契数列
```c
int fibonacci(int n)
{
    if (n <= 2)
        return 1;
    return fibonacci(n - 1) + fibonacci(n - 2);
}

// 优化：使用记忆化
int fib_cache[100] = {0};
int fibonacci_opt(int n)
{
    if (n <= 2)
        return 1;
    if (fib_cache[n] != 0)
        return fib_cache[n];
    fib_cache[n] = fibonacci_opt(n - 1) + fibonacci_opt(n - 2);
    return fib_cache[n];
}
```

## 四、变量的作用域与生命周期

### 局部变量
```c
void func()
{
    int x = 10;  // 只在func内有效
    static int count = 0;  // 静态局部变量，只初始化一次
    count++;
}
```

### 全局变量
```c
int global = 100;  // 所有函数都可访问

void func1()
{
    global = 200;  // 可以修改
}

void func2()
{
    printf("%d\\n", global);  // 200
}
```

### extern关键字
```c
// file1.c
int global = 100;

// file2.c
extern int global;  // 声明外部变量
printf("%d\\n", global);
```

## 五、内部函数与外部函数

### static内部函数
```c
// 只能在当前文件使用
static int helper(int x)
{
    return x * x;
}
```

### extern外部函数
```c
// 可以在其他文件使用
extern int public_func(int x);
```

## 六、常见错误

1. **递归没有终止条件**
```c
void infinite()
{
    infinite();  // 无限递归，栈溢出
}
```

2. **函数声明与定义不匹配**
```c
int add(int a, int b);  // 声明
double add(double a, double b)  // 定义：返回类型不同
{
    return a + b;
}
```

3. **返回局部变量的地址**
```c
int* func()
{
    int x = 10;
    return &x;  // 错误！x在函数结束后被销毁
}
```
""",

    "kp_c09": """# 字符串

## 一、字符串基础

### 字符串的表示
```c
// 字符数组
char str1[] = {'H', 'e', 'l', 'l', 'o', '\\0'};

// 字符串字面量（自动添加'\\0'）
char str2[] = "Hello";

// 指针方式（不可修改）
char *str3 = "Hello";
```

### 字符串长度
```c
char str[] = "Hello";
int len = strlen(str);  // 5（不含'\\0'）
int size = sizeof(str);  // 6（含'\\0'）
```

## 二、字符串输入输出

### 输入函数
```c
// gets() - 不安全，已弃用
char str[100];
gets(str);  // 可能导致缓冲区溢出

// fgets() - 安全
char str[100];
fgets(str, sizeof(str), stdin);  // 包含换行符

// scanf() - 遇空格停止
char str[100];
scanf("%99s", str);  // 限制长度防止溢出
```

### 输出函数
```c
// puts() - 自动添加换行
puts("Hello");

// printf()
printf("%s\\n", str);
```

## 三、字符串处理函数（string.h）

### 求长度
```c
size_t strlen(const char *s);
// 返回字符串长度（不含'\\0'）

char str[] = "Hello";
printf("长度: %zu\\n", strlen(str));  // 5
```

### 复制字符串
```c
char *strcpy(char *dest, const char *src);
char *strncpy(char *dest, const char *src, size_t n);

char src[] = "Hello";
char dst[20];
strcpy(dst, src);  // dst = "Hello"
strncpy(dst, src, 3);  // dst = "Hel"
```

### 拼接字符串
```c
char *strcat(char *dest, const char *src);
char *strncat(char *dest, const char *src, size_t n);

char str[20] = "Hello";
strcat(str, " World");  // str = "Hello World"
strncat(str, "!!!", 1);  // str = "Hello World!"
```

### 比较字符串
```c
int strcmp(const char *s1, const char *s2);
int strncmp(const char *s1, const char *s2, size_t n);

// 返回值：<0 s1<s2, =0 相等, >0 s1>s2
if (strcmp(str1, str2) == 0)
{
    printf("字符串相等\\n");
}
```

### 查找字符
```c
char *strchr(const char *s, int c);
char *strrchr(const char *s, int c);

char str[] = "Hello";
char *pos = strchr(str, 'l');  // 第一次出现'l'的位置
char *pos2 = strrchr(str, 'l');  // 最后一次出现'l'的位置
```

### 查找子串
```c
char *strstr(const char *haystack, const char *needle);

char str[] = "Hello World";
char *pos = strstr(str, "World");  // "World"的起始位置
```

### 字符串转数字
```c
int atoi(const char *s);  // 字符串转整数
double atof(const char *s);  // 字符串转浮点数

char str[] = "123";
int num = atoi(str);  // 123

char str2[] = "3.14";
double pi = atof(str2);  // 3.14
```

## 四、安全的字符串操作

### 使用snprintf
```c
char str[20];
snprintf(str, sizeof(str), "Number: %d", 123);
```

### 使用strncpy确保终止符
```c
char dst[10];
strncpy(dst, src, sizeof(dst) - 1);
dst[sizeof(dst) - 1] = '\\0';
```

## 五、示例程序

### 示例1：统计单词个数
```c
#include <stdio.h>
#include <string.h>

int countWords(const char *str)
{
    int count = 0;
    int inWord = 0;

    while (*str)
    {
        if (*str == ' ' || *str == '\\t' || *str == '\\n')
        {
            inWord = 0;
        }
        else if (!inWord)
        {
            inWord = 1;
            count++;
        }
        str++;
    }

    return count;
}

int main()
{
    char str[] = "  Hello   World  ";
    printf("单词个数: %d\\n", countWords(str));  // 2
    return 0;
}
```

### 示例2：字符串分割
```c
#include <stdio.h>
#include <string.h>

int main()
{
    char str[] = "apple,banana,cherry";
    char *token;

    token = strtok(str, ",");
    while (token != NULL)
    {
        printf("%s\\n", token);
        token = strtok(NULL, ",");
    }

    return 0;
}
```

## 六、常见错误

1. **缓冲区溢出**
```c
char str[5];
strcpy(str, "Hello World");  // 溢出！
```

2. **字符串比较错误**
```c
char str[] = "Hello";
if (str == "Hello")  // 错误！比较的是地址
{
    printf("相等\\n");
}

// 正确写法
if (strcmp(str, "Hello") == 0)
{
    printf("相等\\n");
}
```

3. **修改字符串字面量**
```c
char *str = "Hello";
str[0] = 'h';  // 错误！字符串字面量不可修改
```
""",

    "kp_c10": """# 指针基础

## 一、指针的概念

### 什么是指针
指针是存储内存地址的变量。每个变量都有自己的内存地址，通过指针可以间接访问变量的值。

```c
int x = 10;
int *p = &x;  // p存储x的地址

printf("x的值: %d\\n", x);      // 10
printf("x的地址: %p\\n", &x);   // 地址
printf("p的值: %p\\n", p);      // 与&x相同
printf("p指向的值: %d\\n", *p); // 10
```

### 指针的声明
```c
int *p;      // 指向int的指针
double *dp;  // 指向double的指针
char *cp;    // 指向char的指针
```

### 地址和指针的概念
- **地址**：内存单元的编号，用`&`获取
- **指针**：存放地址的变量
- **解引用**：通过`*`获取指针指向的值

## 二、指针变量的定义与初始化

### 定义指针变量
```c
// 方式1：定义时初始化
int n = 10;
int *p = &n;

// 方式2：先定义后赋值
int n = 10;
int *p;
p = &n;
```

### 指针变量的引用
```c
int n = 10, *p = &n;

// 通过指针修改值
*p = 20;
printf("%d\\n", n);  // 20

// 指针的指针
int **pp = &p;
printf("%d\\n", **pp);  // 20
```

### 指针变量作为函数参数
```c
// 交换两个变量的值
void swap(int *a, int *b)
{
    int t = *a;
    *a = *b;
    *b = t;
}

int x = 3, y = 4;
swap(&x, &y);  // x=4, y=3
```

## 三、指针的运算

### 指针加减整数
```c
int a[5] = {10, 20, 30, 40, 50};
int *p = a;

printf("%d\\n", *p);      // 10
printf("%d\\n", *(p + 1)); // 20
printf("%d\\n", *(p + 2)); // 30

// 指针自增
p++;  // 指向下一个int元素
```

### 指针的关系运算
```c
int arr[5] = {10, 20, 30, 40, 50};
int *p1 = &arr[0];
int *p2 = &arr[4];

if (p1 < p2)
{
    printf("p1在p2前面\\n");
}
```

## 四、指针与数组

### 数组名是指针
```c
int arr[5] = {10, 20, 30, 40, 50};
int *p = arr;  // 数组名就是首元素地址

printf("%d\\n", arr[0]);  // 10
printf("%d\\n", *p);      // 10

printf("%d\\n", arr[1]);  // 20
printf("%d\\n", *(p + 1)); // 20
```

### 通过指针引用数组元素
```c
int a[5] = {1, 3, 5, 7, 9};
int *p = a;

// 四种等价方式
for (int i = 0; i < 5; i++)
{
    printf("%d,%d,%d,%d\\n", a[i], *(a + i), p[i], *(p + i));
}
```

### 指针遍历数组
```c
int arr[] = {10, 20, 30, 40, 50};
int len = sizeof(arr) / sizeof(arr[0]);

int *p;
for (p = arr; p < arr + len; p++)
{
    printf("%d ", *p);
}
```

## 五、指针与字符串

### 字符指针
```c
char str[] = "Hello";
char *p = str;

printf("%c\\n", *p);      // 'H'
printf("%s\\n", p);        // "Hello"
printf("%s\\n", p + 1);    // "ello"
```

### 字符串的表示形式
```c
// 方法1：字符数组
char s[80] = "Good!";

// 方法2：字符指针
char *s = "OK";
```

## 六、常见错误

1. **野指针**
```c
int *p;  // 未初始化，指向随机地址
*p = 10;  // 危险！
```

2. **空指针**
```c
int *p = NULL;
*p = 10;  // 段错误
```

3. **指针越界**
```c
int arr[5] = {1, 2, 3, 4, 5};
int *p = arr;
printf("%d\\n", *(p + 10));  // 越界访问
```

4. **指针类型不匹配**
```c
int n = 10;
short *p = (short *)&n;  // 类型不匹配可能导致问题
```
""",

    "kp_c11": """# 指针基础

## 一、指针的概念

### 什么是指针
指针是存储内存地址的变量。

```c
int x = 10;
int *p = &x;  // p存储x的地址

printf("x的值: %d\\n", x);      // 10
printf("x的地址: %p\\n", &x);   // 地址
printf("p的值: %p\\n", p);      // 与&x相同
printf("p指向的值: %d\\n", *p); // 10
```

### 指针的声明
```c
int *p;      // 指向int的指针
double *dp;  // 指向double的指针
char *cp;    // 指向char的指针
```

## 二、指针的运算

### 解引用运算符 *
```c
int x = 10;
int *p = &x;

*p = 20;  // 修改x的值为20
printf("%d\\n", x);  // 20
```

### 地址运算符 &
```c
int x = 10;
printf("%p\\n", &x);  // x的内存地址
```

### 指针算术
```c
int arr[] = {10, 20, 30, 40, 50};
int *p = arr;

printf("%d\\n", *p);      // 10
printf("%d\\n", *(p + 1)); // 20
printf("%d\\n", *(p + 2)); // 30

// 指针递增
p++;  // 指向下一个int元素
```

## 三、指针与数组

### 数组名是指针
```c
int arr[5] = {10, 20, 30, 40, 50};
int *p = arr;  // 数组名就是首元素地址

printf("%d\\n", arr[0]);  // 10
printf("%d\\n", *p);      // 10

printf("%d\\n", arr[1]);  // 20
printf("%d\\n", *(p + 1)); // 20
```

### 指针遍历数组
```c
int arr[] = {10, 20, 30, 40, 50};
int *p;

for (p = arr; p < arr + 5; p++)
{
    printf("%d ", *p);
}
```

## 四、指针与字符串

### 字符指针
```c
char str[] = "Hello";
char *p = str;

printf("%c\\n", *p);      // 'H'
printf("%s\\n", p);        // "Hello"
printf("%s\\n", p + 1);    // "ello"
```

### 字符串复制
```c
void strCopy(char *dest, const char *src)
{
    while (*src != '\\0')
    {
        *dest = *src;
        dest++;
        src++;
    }
    *dest = '\\0';
}
```

## 五、指针与函数

### 指针作为参数
```c
void swap(int *a, int *b)
{
    int temp = *a;
    *a = *b;
    *b = temp;
}

int x = 5, y = 10;
swap(&x, &y);  // x=10, y=5
```

### 指针作为返回值
```c
int* findMax(int *arr, int size)
{
    int *max = &arr[0];
    for (int i = 1; i < size; i++)
    {
        if (arr[i] > *max)
        {
            max = &arr[i];
        }
    }
    return max;
}
```

## 六、常见错误

1. **野指针**
```c
int *p;  // 未初始化，指向随机地址
*p = 10;  // 危险！
```

2. **空指针**
```c
int *p = NULL;
*p = 10;  // 段错误
```

3. **指针越界**
```c
int arr[5] = {1, 2, 3, 4, 5};
int *p = arr;
printf("%d\\n", *(p + 10));  // 越界访问
```
""",

    "kp_c12": """# 指针与数组

## 一、指针与一维数组

### 数组名的本质
```c
int arr[5] = {10, 20, 30, 40, 50};

// 数组名在大多数表达式中退化为指针
int *p = arr;  // 等价于 int *p = &arr[0];

// 访问元素
printf("%d\\n", arr[0]);  // 10
printf("%d\\n", *p);      // 10

printf("%d\\n", arr[1]);  // 20
printf("%d\\n", *(p + 1)); // 20
```

### 指针遍历数组
```c
int arr[] = {10, 20, 30, 40, 50};
int len = sizeof(arr) / sizeof(arr[0]);

// 方式1：下标访问
for (int i = 0; i < len; i++)
{
    printf("%d ", arr[i]);
}

// 方式2：指针访问
int *p;
for (p = arr; p < arr + len; p++)
{
    printf("%d ", *p);
}
```

## 二、指针与二维数组

### 二维数组的存储
```c
int arr[2][3] = {{1, 2, 3}, {4, 5, 6}};

// arr[i][j] 等价于 *(*(arr + i) + j)
printf("%d\\n", arr[1][2]);  // 6
printf("%d\\n", *(*(arr + 1) + 2));  // 6
```

### 指针数组
```c
int arr1[] = {1, 2, 3};
int arr2[] = {4, 5, 6};
int arr3[] = {7, 8, 9};

int *parr[3] = {arr1, arr2, arr3};

// 访问元素
printf("%d\\n", parr[0][1]);  // 2
printf("%d\\n", *(*(parr + 1) + 0));  // 4
```

## 三、指针与函数

### 指针作为参数
```c
void modifyArray(int *arr, int size)
{
    for (int i = 0; i < size; i++)
    {
        arr[i] *= 2;  // 直接修改原数组
    }
}

int arr[] = {1, 2, 3, 4, 5};
modifyArray(arr, 5);  // arr变为{2, 4, 6, 8, 10}
```

### 函数指针
```c
// 函数指针声明
int (*funcPtr)(int, int);

// 指向函数
funcPtr = add;

// 通过指针调用函数
int result = funcPtr(3, 5);  // result = 8
```

## 四、动态内存分配

### malloc和free
```c
#include <stdlib.h>

// 分配内存
int *arr = (int *)malloc(5 * sizeof(int));
if (arr == NULL)
{
    printf("内存分配失败\\n");
    return 1;
}

// 使用内存
for (int i = 0; i < 5; i++)
{
    arr[i] = (i + 1) * 10;
}

// 释放内存
free(arr);
arr = NULL;  // 防止野指针
```

### calloc
```c
// 分配并初始化为0
int *arr = (int *)calloc(5, sizeof(int));
```

### realloc
```c
// 重新分配内存
int *arr = (int *)malloc(5 * sizeof(int));
arr = (int *)realloc(arr, 10 * sizeof(int));  // 扩展到10个元素
```

## 五、常见错误

1. **内存泄漏**
```c
int *p = (int *)malloc(sizeof(int));
p = NULL;  // 忘记free，内存泄漏
```

2. **野指针**
```c
int *p = (int *)malloc(sizeof(int));
free(p);
*p = 10;  // 错误！p已释放
```

3. **数组越界**
```c
int arr[5] = {1, 2, 3, 4, 5};
int *p = arr;
printf("%d\\n", *(p + 10));  // 越界
```
""",

    "kp_c13": """# 结构体与联合体

## 一、结构体的定义

### 定义结构体
```c
struct Student
{
    char name[50];
    int age;
    float score;
};

// 或使用typedef简化
typedef struct
{
    char name[50];
    int age;
    float score;
} Student;
```

### 声明结构体变量
```c
// 方式1
struct Student s1;

// 方式2（使用typedef）
Student s2;

// 初始化
Student s3 = {"张三", 20, 95.5};
```

## 二、结构体成员访问

### 使用点运算符
```c
Student s1 = {"李四", 19, 88.0};

printf("姓名: %s\\n", s1.name);
printf("年龄: %d\\n", s1.age);
printf("成绩: %.1f\\n", s1.score);

// 修改成员
s1.age = 20;
s1.score = 92.5;
```

## 三、结构体数组

```c
Student class[3] = {
    {"张三", 20, 95.5},
    {"李四", 19, 88.0},
    {"王五", 21, 92.0}
};

// 遍历
for (int i = 0; i < 3; i++)
{
    printf("%s: %.1f\\n", class[i].name, class[i].score);
}
```

## 四、结构体指针

### 指针访问成员
```c
Student s1 = {"张三", 20, 95.5};
Student *p = &s1;

// 方式1：(*p).member
printf("%s\\n", (*p).name);

// 方式2：p->member（推荐）
printf("%s\\n", p->name);
printf("%d\\n", p->age);
```

### 结构体作为函数参数
```c
// 值传递（效率低）
void printStudent(Student s)
{
    printf("%s: %.1f\\n", s.name, s.score);
}

// 指针传递（推荐）
void printStudent(Student *s)
{
    printf("%s: %.1f\\n", s->name, s->score);
}
```

## 五、联合体

### 定义与使用
```c
union Data
{
    int i;
    float f;
    char str[20];
};

Data d;
d.i = 10;
printf("%d\\n", d.i);  // 10

d.f = 3.14;  // 覆盖之前的值
printf("%.2f\\n", d.f);  // 3.14
```

### 联合体大小
```c
printf("union大小: %zu\\n", sizeof(union Data));  // 最大成员的大小
```

## 六、枚举类型

```c
enum Color { RED, GREEN, BLUE };
enum Color c = RED;

// 或指定值
enum Weekday { MON=1, TUE, WED, THU, FRI, SAT, SUN };
enum Weekday today = WED;  // 3
```

## 七、位域

```c
struct Flags
{
    unsigned int bold : 1;
    unsigned int italic : 1;
    unsigned int underline : 1;
};

struct Flags f;
f.bold = 1;
f.italic = 0;
f.underline = 1;
```

## 八、常见错误

1. **结构体比较错误**
```c
Student s1 = {"张三", 20, 95.5};
Student s2 = {"张三", 20, 95.5};

if (s1 == s2)  // 错误！不能直接比较
{
    printf("相等\\n");
}

// 正确：逐个成员比较
if (strcmp(s1.name, s2.name) == 0 && s1.age == s2.age)
```

2. **结构体赋值**
```c
Student s1 = {"张三", 20, 95.5};
Student s2;
s2 = s1;  // 正确，结构体支持赋值
```
""",

    "kp_c14": """# 位运算

## 一、位运算符

### 按位与 &
```c
// 两个位都为1时结果为1
int a = 6;   // 0110
int b = 5;   // 0101
int c = a & b;  // 0100 = 4
```

### 按位或 |
```c
// 任一位为1时结果为1
int a = 6;   // 0110
int b = 5;   // 0101
int c = a | b;  // 0111 = 7
```

### 按位异或 ^
```c
// 两位不同时结果为1
int a = 6;   // 0110
int b = 5;   // 0101
int c = a ^ b;  // 0011 = 3
```

### 按位取反 ~
```c
// 0变1，1变0
int a = 6;   // 0000 0000 0000 0110
int b = ~a;  // 1111 1111 1111 1001 = -7
```

### 左移 <<
```c
// 左移n位相当于乘以2^n
int a = 3;   // 0011
int b = a << 2;  // 1100 = 12
```

### 右移 >>
```c
// 右移n位相当于除以2^n（向下取整）
int a = 12;  // 1100
int b = a >> 2;  // 0011 = 3
```

## 二、位运算应用

### 设置位
```c
unsigned int flags = 0;

// 设置第3位
flags |= (1 << 3);

// 设置第0、2、5位
flags |= (1 << 0) | (1 << 2) | (1 << 5);
```

### 清除位
```c
// 清除第3位
flags &= ~(1 << 3);

// 清除第0、2位
flags &= ~((1 << 0) | (1 << 2));
```

### 切换位
```c
// 切换第3位
flags ^= (1 << 3);
```

### 检查位
```c
// 检查第3位是否设置
if (flags & (1 << 3))
{
    printf("第3位已设置\\n");
}
```

### 交换两个数（不使用临时变量）
```c
void swap(int *a, int *b)
{
    *a ^= *b;
    *b ^= *a;
    *a ^= *b;
}
```

### 判断奇偶
```c
if (n & 1)
{
    printf("奇数\\n");
}
else
{
    printf("偶数\\n");
}
```

## 三、位域

```c
struct BitField
{
    unsigned int bold : 1;
    unsigned int italic : 1;
    unsigned int underline : 1;
    unsigned int color : 4;
};

struct BitField f;
f.bold = 1;
f.color = 15;
```

## 四、常见错误

1. **移位位数超出范围**
```c
int a = 1;
int b = a << 32;  // 未定义行为（int通常32位）
```

2. **有符号数右移**
```c
int a = -8;
int b = a >> 2;  // 实现定义（可能是-2或大数）
```

3. **位运算优先级错误**
```c
if (flags & 1 == 0)  // 错误！==优先级高于&
{
    // ...
}

// 正确写法
if ((flags & 1) == 0)
{
    // ...
}
```
""",

    "kp_c15": """# 文件操作

## 一、文件的基本概念

### 文件指针
```c
FILE *fp;
```

### 文件打开模式
| 模式 | 说明 |
|------|------|
| "r" | 只读（文件必须存在） |
| "w" | 只写（创建新文件或清空） |
| "a" | 追加（文件不存在则创建） |
| "rb" | 二进制只读 |
| "wb" | 二进制只写 |
| "r+" | 读写（文件必须存在） |
| "w+" | 读写（创建新文件或清空） |
| "a+" | 读写（追加模式） |

## 二、文件的打开与关闭

### 打开文件
```c
FILE *fp = fopen("data.txt", "r");
if (fp == NULL)
{
    printf("文件打开失败\\n");
    return 1;
}
```

### 关闭文件
```c
fclose(fp);
```

## 三、文件的读写

### 字符读写
```c
// 写入字符
fputc('A', fp);

// 读取字符
char ch = fgetc(fp);
```

### 字符串读写
```c
// 写入字符串
fputs("Hello\\n", fp);

// 读取字符串
char str[100];
fgets(str, sizeof(str), fp);
```

### 格式化读写
```c
// 格式化写入
fprintf(fp, "Name: %s, Age: %d\\n", name, age);

// 格式化读取
char name[50];
int age;
fscanf(fp, "Name: %s, Age: %d", name, &age);
```

### 二进制读写
```c
// 写入二进制数据
int arr[] = {1, 2, 3, 4, 5};
fwrite(arr, sizeof(int), 5, fp);

// 读取二进制数据
int arr2[5];
fread(arr2, sizeof(int), 5, fp);
```

## 四、文件定位

```c
// 获取当前位置
long pos = ftell(fp);

// 移动到文件开头
rewind(fp);

// 定位到指定位置
fseek(fp, 0, SEEK_SET);  // 文件开头
fseek(fp, 10, SEEK_CUR);  // 当前位置+10
fseek(fp, -5, SEEK_END);  // 文件末尾-5
```

## 五、错误处理

```c
// 检查文件结束
if (feof(fp))
{
    printf("已到达文件末尾\\n");
}

// 检查错误
if (ferror(fp))
{
    printf("文件操作错误\\n");
}
```

## 六、示例程序

### 示例1：复制文件
```c
#include <stdio.h>

int main()
{
    FILE *src = fopen("source.txt", "r");
    FILE *dst = fopen("dest.txt", "w");

    if (src == NULL || dst == NULL)
    {
        printf("文件打开失败\\n");
        return 1;
    }

    char ch;
    while ((ch = fgetc(src)) != EOF)
    {
        fputc(ch, dst);
    }

    fclose(src);
    fclose(dst);

    printf("文件复制完成\\n");
    return 0;
}
```

### 示例2：统计文件行数
```c
#include <stdio.h>

int main()
{
    FILE *fp = fopen("text.txt", "r");
    if (fp == NULL)
    {
        printf("文件打开失败\\n");
        return 1;
    }

    int lines = 0;
    char ch;
    while ((ch = fgetc(fp)) != EOF)
    {
        if (ch == '\\n')
            lines++;
    }

    fclose(fp);
    printf("行数: %d\\n", lines);
    return 0;
}
```

## 七、常见错误

1. **忘记关闭文件**
```c
FILE *fp = fopen("data.txt", "r");
// 使用文件...
// 忘记 fclose(fp)，可能导致资源泄漏
```

2. **文件指针未检查**
```c
FILE *fp = fopen("data.txt", "r");
fprintf(fp, "Hello");  // 如果文件打开失败，fp为NULL
```

3. **二进制模式混用**
```c
FILE *fp = fopen("data.bin", "r");  // 应该用"rb"
```
""",

    "kp_c16": """# 动态内存管理

## 一、内存分区

### 栈区（Stack）
- 存放局部变量、函数参数
- 自动分配和释放
- 空间有限（通常1-8MB）

### 堆区（Heap）
- 存放动态分配的内存
- 需要手动分配和释放
- 空间较大

### 全局区
- 存放全局变量、静态变量
- 程序运行期间一直存在

### 常量区
- 存放字符串常量等

## 二、动态内存分配函数

### malloc
```c
#include <stdlib.h>

// 分配指定字节数的内存
void *malloc(size_t size);

// 示例
int *arr = (int *)malloc(5 * sizeof(int));
if (arr == NULL)
{
    printf("内存分配失败\\n");
    return 1;
}
```

### calloc
```c
// 分配并初始化为0
void *calloc(size_t num, size_t size);

// 示例
int *arr = (int *)calloc(5, sizeof(int));  // 5个int，全部为0
```

### realloc
```c
// 重新分配内存
void *realloc(void *ptr, size_t new_size);

// 示例
int *arr = (int *)malloc(5 * sizeof(int));
arr = (int *)realloc(arr, 10 * sizeof(int));  // 扩展到10个
```

### free
```c
// 释放内存
void free(void *ptr);

// 示例
free(arr);
arr = NULL;  // 防止野指针
```

## 三、常见内存问题

### 内存泄漏
```c
void func()
{
    int *p = (int *)malloc(sizeof(int));
    // 忘记free，函数返回后p丢失，内存泄漏
}
```

### 野指针
```c
int *p = (int *)malloc(sizeof(int));
free(p);
*p = 10;  // 错误！p已释放
```

### 重复释放
```c
int *p = (int *)malloc(sizeof(int));
free(p);
free(p);  // 错误！重复释放
```

### 内存越界
```c
int *arr = (int *)malloc(5 * sizeof(int));
arr[10] = 100;  // 越界！只分配了5个int的空间
```

## 四、安全编程实践

### 检查分配结果
```c
int *arr = (int *)malloc(5 * sizeof(int));
if (arr == NULL)
{
    fprintf(stderr, "内存分配失败\\n");
    exit(1);
}
```

### 释放后置空
```c
free(arr);
arr = NULL;
```

### 使用内存检测工具
- Valgrind（Linux）
- Visual Studio 内存诊断工具

## 五、示例程序

### 示例1：动态数组
```c
#include <stdio.h>
#include <stdlib.h>

int main()
{
    int n;
    printf("请输入数组大小: ");
    scanf("%d", &n);

    int *arr = (int *)malloc(n * sizeof(int));
    if (arr == NULL)
    {
        printf("内存分配失败\\n");
        return 1;
    }

    // 使用数组
    for (int i = 0; i < n; i++)
    {
        arr[i] = i * 10;
    }

    // 输出
    for (int i = 0; i < n; i++)
    {
        printf("%d ", arr[i]);
    }
    printf("\\n");

    free(arr);
    arr = NULL;

    return 0;
}
```

### 示例2：链表
```c
#include <stdio.h>
#include <stdlib.h>

typedef struct Node
{
    int data;
    struct Node *next;
} Node;

// 创建新节点
Node* createNode(int data)
{
    Node *newNode = (Node *)malloc(sizeof(Node));
    if (newNode == NULL)
    {
        printf("内存分配失败\\n");
        exit(1);
    }
    newNode->data = data;
    newNode->next = NULL;
    return newNode;
}

// 释放链表
void freeList(Node *head)
{
    Node *temp;
    while (head != NULL)
    {
        temp = head;
        head = head->next;
        free(temp);
    }
}

int main()
{
    Node *head = createNode(1);
    head->next = createNode(2);
    head->next->next = createNode(3);

    // 遍历
    Node *current = head;
    while (current != NULL)
    {
        printf("%d -> ", current->data);
        current = current->next;
    }
    printf("NULL\\n");

    freeList(head);

    return 0;
}
```

## 六、常见错误

1. **malloc后未检查NULL**
2. **忘记释放内存**
3. **free后继续使用指针**
4. **在循环中重复分配未释放**
""",

    "kp_c15": """# 预处理指令

## 一、宏定义

### 简单宏
```c
#define PI 3.14159
#define MAX_SIZE 100

double area = PI * r * r;
int arr[MAX_SIZE];
```

### 带参数的宏
```c
#define SQUARE(x) ((x) * (x))
#define MAX(a, b) ((a) > (b) ? (a) : (b))

int result = SQUARE(5);  // 25
int maximum = MAX(3, 7);  // 7
```

### 宏的注意事项
```c
// 错误：未加括号
#define SQUARE(x) x * x
int result = SQUARE(3 + 2);  // 3 + 2 * 3 + 2 = 11，不是25

// 正确：加括号
#define SQUARE(x) ((x) * (x))
int result = SQUARE(3 + 2);  // ((3 + 2) * (3 + 2)) = 25
```

### 字符串化 #
```c
#define PRINT(x) printf(#x " = %d\\n", x)

int a = 10;
PRINT(a);  // 输出: a = 10
```

### 连接 ##
```c
#define CONCAT(a, b) a##b

int xy = 100;
int result = CONCAT(x, y);  // 等价于 xy
```

## 二、文件包含

### #include <stdio.h>
从系统目录查找头文件。

### #include "myfile.h"
先从当前目录查找，再从系统目录查找。

## 三、条件编译

### #ifdef / #ifndef
```c
#ifdef DEBUG
    printf("调试信息: x = %d\\n", x);
#endif

#ifndef RELEASE
    printf("非发布版本\\n");
#endif
```

### #if / #elif / #else / #endif
```c
#define VERSION 3

#if VERSION == 1
    printf("版本1\\n");
#elif VERSION == 2
    printf("版本2\\n");
#else
    printf("其他版本\\n");
#endif
```

### 头文件保护（防止重复包含）
```c
#ifndef MYHEADER_H
#define MYHEADER_H

// 头文件内容

#endif
```

## 四、其他预处理指令

### #pragma
```c
#pragma once  // 只包含一次

#pragma pack(1)  // 设置对齐方式
```

### #error / #warning
```c
#ifndef __cplusplus
#error "此文件只能在C++中使用"
#endif
```

### 预定义宏
```c
printf("文件: %s\\n", __FILE__);
printf("行号: %d\\n", __LINE__);
printf("日期: %s\\n", __DATE__);
printf("时间: %s\\n", __TIME__);
printf("函数: %s\\n", __func__);
```

## 五、常见错误

1. **宏定义末尾加分号**
```c
#define PI 3.14;  // 错误！
double area = PI * r * r;  // 展开为 3.14; * r * r
```

2. **宏参数未加括号**
```c
#define DOUBLE(x) x + x
int result = DOUBLE(3) * 2;  // 3 + 3 * 2 = 9，不是12
```

3. **宏定义中的副作用**
```c
#define MAX(a, b) ((a) > (b) ? (a) : (b))

int x = 5, y = 3;
int result = MAX(x++, y++);  // x和y都被递增两次
```
""",

    "kp_c16": """# 位运算

## 一、位运算符

### 按位与 &
```c
// 两个位都为1时结果为1
int a = 6;   // 0110
int b = 5;   // 0101
int c = a & b;  // 0100 = 4
```

### 按位或 |
```c
// 任一位为1时结果为1
int a = 6;   // 0110
int b = 5;   // 0101
int c = a | b;  // 0111 = 7
```

### 按位异或 ^
```c
// 两位不同时结果为1
int a = 6;   // 0110
int b = 5;   // 0101
int c = a ^ b;  // 0011 = 3
```

### 按位取反 ~
```c
// 0变1，1变0
int a = 6;   // 0000 0000 0000 0110
int b = ~a;  // 1111 1111 1111 1001 = -7
```

### 左移 <<
```c
// 左移n位相当于乘以2^n
int a = 3;   // 0011
int b = a << 2;  // 1100 = 12
```

### 右移 >>
```c
// 右移n位相当于除以2^n（向下取整）
int a = 12;  // 1100
int b = a >> 2;  // 0011 = 3
```

## 二、位运算应用

### 设置位
```c
unsigned int flags = 0;

// 设置第3位
flags |= (1 << 3);

// 设置第0、2、5位
flags |= (1 << 0) | (1 << 2) | (1 << 5);
```

### 清除位
```c
// 清除第3位
flags &= ~(1 << 3);

// 清除第0、2位
flags &= ~((1 << 0) | (1 << 2));
```

### 切换位
```c
// 切换第3位
flags ^= (1 << 3);
```

### 检查位
```c
// 检查第3位是否设置
if (flags & (1 << 3))
{
    printf("第3位已设置\\n");
}
```

### 交换两个数（不使用临时变量）
```c
void swap(int *a, int *b)
{
    *a ^= *b;
    *b ^= *a;
    *a ^= *b;
}
```

### 判断奇偶
```c
if (n & 1)
{
    printf("奇数\\n");
}
else
{
    printf("偶数\\n");
}
```

## 三、位域

```c
struct BitField
{
    unsigned int bold : 1;
    unsigned int italic : 1;
    unsigned int underline : 1;
    unsigned int color : 4;
};

struct BitField f;
f.bold = 1;
f.color = 15;
```

## 四、常见错误

1. **移位位数超出范围**
```c
int a = 1;
int b = a << 32;  // 未定义行为（int通常32位）
```

2. **有符号数右移**
```c
int a = -8;
int b = a >> 2;  // 实现定义（可能是-2或大数）
```

3. **位运算优先级错误**
```c
if (flags & 1 == 0)  // 错误！==优先级高于&
{
    // ...
}

// 正确写法
if ((flags & 1) == 0)
{
    // ...
}
```
"""
}

# ============================================================
# 数据库写入
# ============================================================
def seed():
    db_path = os.path.join(os.path.dirname(__file__), "..", "ai_learning_v2.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("开始更新C语言知识点内容...")

    for kp_id, doc in DOCUMENTS.items():
        # 更新document字段
        cursor.execute(
            "UPDATE knowledge_points SET document = ? WHERE kp_id = ?",
            (doc, kp_id)
        )
        if cursor.rowcount > 0:
            print(f"  [OK] {kp_id}: {len(doc)} chars")
        else:
            print(f"  [WARN] {kp_id} 不存在，跳过")

    conn.commit()
    conn.close()

    print(f"\n完成！更新了 {len(DOCUMENTS)} 个C语言知识点")


if __name__ == "__main__":
    seed()
