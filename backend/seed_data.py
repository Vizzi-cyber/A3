"""
数据库测试数据填充脚本 —— C语言程序设计教材体系
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from passlib.context import CryptContext
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.database import Base
from app.models.user import UserModel
from app.models.student import StudentProfileModel
from app.models.knowledge import KnowledgePointModel, LearningRecordModel, QuizResultModel
from app.models.trend import TrendDataModel
from app.models.gamification import PointsModel, AchievementModel, TaskModel, LeaderboardModel
from app.models.log_reflection import LearningLogModel, ReflectionModel

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
engine = create_engine("sqlite:///./ai_learning_v2.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

db = SessionLocal()

STUDENT_ID = "student_001"
STUDENT2 = "student_002"
STUDENT3 = "student_003"
TEST_USER = "test_001"

# ---------- 清空旧数据（保留表结构） ----------
for tbl in [
    ReflectionModel, LearningLogModel, LeaderboardModel, TaskModel,
    AchievementModel, PointsModel, TrendDataModel, QuizResultModel,
    LearningRecordModel, KnowledgePointModel, StudentProfileModel, UserModel,
]:
    db.query(tbl).delete()
db.commit()

# ---------- 用户表 ----------
users = [
    UserModel(student_id=STUDENT_ID, username="张三", email="zhangsan@example.com",
              hashed_password=pwd_context.hash("123456"), is_active=True, role="student"),
    UserModel(student_id=STUDENT2, username="李四", email="lisi@example.com",
              hashed_password=pwd_context.hash("123456"), is_active=True, role="student"),
    UserModel(student_id=STUDENT3, username="王五", email="wangwu@example.com",
              hashed_password=pwd_context.hash("123456"), is_active=True, role="student"),
    UserModel(student_id=TEST_USER, username="测试用户", email="test@example.com",
              hashed_password=pwd_context.hash("123456"), is_active=True, role="student"),
]
db.add_all(users)
db.commit()

# ---------- 学生画像 ----------
profiles = [
    StudentProfileModel(
        student_id=STUDENT_ID,
        knowledge_base={"overall_score": 72, "C语言概述": 0.8, "数据类型与变量": 0.75, "控制结构": 0.6, "指针": 0.3},
        cognitive_style={"primary": "visual", "scores": {"visual": 0.8, "auditory": 0.5, "reading": 0.7, "kinesthetic": 0.6}},
        weak_areas=["指针与内存", "结构体"],
        error_patterns=[{"type": "概念混淆", "desc": "经常混淆指针与地址"}],
        learning_goals=[{"goal": "掌握C语言程序设计与数据结构基础", "deadline": "2026-06-01"}],
        interest_areas=["编程基础", "算法"],
        learning_tempo={"study_speed": "moderate", "optimal_session_duration": 45, "weekly_study_capacity": 10, "focus_score": 75},
        practical_preferences={"overall_score": 80, "coding_proficiency": {"c": 0.6, "python": 0.5}, "preferred_practice_types": ["代码实操", "算法练习"]},
    ),
    StudentProfileModel(
        student_id=STUDENT2,
        knowledge_base={"overall_score": 85, "C语言概述": 0.9, "数据类型与变量": 0.85, "控制结构": 0.8, "指针": 0.7},
        cognitive_style={"primary": "reading", "scores": {"visual": 0.6, "auditory": 0.4, "reading": 0.9, "kinesthetic": 0.5}},
        weak_areas=["动态内存管理"],
        error_patterns=[],
        learning_goals=[{"goal": "精通C语言系统编程", "deadline": "2026-07-01"}],
        interest_areas=["系统编程", "嵌入式"],
        learning_tempo={"study_speed": "fast", "optimal_session_duration": 60, "weekly_study_capacity": 20, "focus_score": 85},
        practical_preferences={"overall_score": 95, "coding_proficiency": {"c": 0.9, "java": 0.7}, "preferred_practice_types": ["项目实战", "算法竞赛"]},
    ),
    StudentProfileModel(
        student_id=STUDENT3,
        knowledge_base={"overall_score": 45, "C语言概述": 0.5, "数据类型与变量": 0.4, "控制结构": 0.3},
        cognitive_style={"primary": "kinesthetic", "scores": {"visual": 0.5, "auditory": 0.6, "reading": 0.4, "kinesthetic": 0.85}},
        weak_areas=["数学基础", "编程语法"],
        error_patterns=[{"type": "语法错误", "desc": "经常遗漏分号"}],
        learning_goals=[{"goal": "入门C语言编程", "deadline": "2026-08-01"}],
        interest_areas=["游戏开发", "物联网"],
        learning_tempo={"study_speed": "slow", "optimal_session_duration": 30, "weekly_study_capacity": 8, "focus_score": 55},
        practical_preferences={"overall_score": 40, "coding_proficiency": {"c": 0.3, "python": 0.2}, "preferred_practice_types": ["视频教程", "互动练习"]},
    ),
    StudentProfileModel(
        student_id=TEST_USER,
        knowledge_base={"overall_score": 68, "C语言概述": 0.85, "数据类型与变量": 0.8, "控制结构": 0.65, "指针": 0.35},
        cognitive_style={"primary": "visual", "scores": {"visual": 0.85, "auditory": 0.5, "reading": 0.6, "kinesthetic": 0.7}},
        weak_areas=["指针与内存", "文件操作"],
        error_patterns=[{"type": "概念混淆", "desc": "指针和地址概念不清"}],
        learning_goals=[{"goal": "掌握C语言程序设计与数据结构基础", "deadline": "2026-06-01"}],
        interest_areas=["编程基础", "算法"],
        learning_tempo={"study_speed": "moderate", "optimal_session_duration": 45, "weekly_study_capacity": 10, "focus_score": 70},
        practical_preferences={"overall_score": 75, "coding_proficiency": {"c": 0.55, "python": 0.4}, "preferred_practice_types": ["代码实操", "算法练习"]},
    ),
]
db.add_all(profiles)
db.commit()


# ============================================================
# C语言程序设计教材内容
# ============================================================

KP_C01_DOC = """# C语言概述与开发环境搭建

## 1.1 什么是C语言

C语言是由丹尼斯·里奇（Dennis Ritchie）于1972年在贝尔实验室开发的一种通用、过程式编程语言。它被设计用于编写操作系统（如Unix），因此具有底层操作能力。

### C语言的特点
- **高效性**：接近底层硬件，执行效率高
- **可移植性**：标准化程度高，跨平台能力强
- **灵活性**：提供丰富的底层操作能力（指针、内存管理）
- **广泛应用**：操作系统、嵌入式、驱动程序等领域

## 1.2 第一个C程序

每个C程序都包含一个 `main` 函数，这是程序的入口点。

```c
#include <stdio.h>

int main() {
    printf("Hello, World!\\n");
    return 0;
}
```

### 代码解析
1. `#include <stdio.h>` —— 引入标准输入输出库
2. `int main()` —— 主函数，程序从这里开始执行
3. `printf()` —— 输出函数，将内容打印到控制台
4. `return 0` —— 表示程序正常结束

## 1.3 开发环境搭建

### Windows 推荐方案
- **MinGW-w64**：GCC编译器的Windows版本
- **VS Code + C/C++插件**：轻量级编辑器方案
- **Dev-C++**：适合初学者的IDE

### 编译与运行
```bash
gcc hello.c -o hello.exe
hello.exe
```

## 1.4 程序结构总结

| 组成部分 | 说明 | 是否必需 |
|---------|------|---------|
| 预处理指令 | #include, #define 等 | 按需 |
| 全局声明 | 全局变量、函数声明 | 按需 |
| main函数 | 程序入口 | 必需 |
| 用户函数 | 自定义功能模块 | 按需 |
| 注释 | // 单行, /* 多行 */ | 建议 |

> **学习建议**：刚开始不必深究每个细节，先让程序跑起来，建立成就感后再深入理解。
"""

KP_C01_CODE = '''#include <stdio.h>

int main() {
    // 输出个人信息
    printf("===== 我的第一个C程序 =====\\n");
    printf("姓名: 学习者\\n");
    printf("学习目标: 掌握C语言\\n");
    printf("==========================\\n");

    // 简单的计算
    int a = 10, b = 20;
    printf("%d + %d = %d\\n", a, b, a + b);

    return 0;
}'''

KP_C01_QS = [
    {"q_id": "q_c01_1", "type": "single_choice", "content": "C语言中，程序的执行从哪个函数开始？", "options": [{"id": "A", "text": "start()"}, {"id": "B", "text": "main()"}, {"id": "C", "text": "begin()"}, {"id": "D", "text": "run()"}], "correct_answer": "B", "explanation": "main() 函数是C程序的入口点，程序从这里开始执行。"},
    {"q_id": "q_c01_2", "type": "single_choice", "content": "以下哪个是标准的C语言输出函数？", "options": [{"id": "A", "text": "print()"}, {"id": "B", "text": "cout <<"}, {"id": "C", "text": "printf()"}, {"id": "D", "text": "console.log()"}], "correct_answer": "C", "explanation": "printf() 是C标准库 <stdio.h> 中的格式化输出函数。"},
    {"q_id": "q_c01_3", "type": "single_choice", "content": "C源程序编译后生成的可执行文件扩展名在Windows下通常是？", "options": [{"id": "A", "text": ".java"}, {"id": "B", "text": ".py"}, {"id": "C", "text": ".exe"}, {"id": "D", "text": ".html"}], "correct_answer": "C", "explanation": "Windows下C程序编译后的可执行文件扩展名为 .exe。"},
]

KP_C01_MM = {"root": "C语言概述", "children": [{"name": "发展历史"}, {"name": "语言特点"}, {"name": "开发环境"}, {"name": "HelloWorld"}, {"name": "编译运行"}]}


KP_C02_DOC = """# 数据类型与变量

## 2.1 变量的概念

变量是程序中用于存储数据的容器。在C语言中，使用变量前必须先**声明**（指定类型和名称）。

```c
int age = 20;       // 整型变量
float price = 19.99; // 单精度浮点
char grade = 'A';   // 字符变量
```

## 2.2 基本数据类型

| 类型 | 关键字 | 占用字节 | 取值范围（大致） | 示例 |
|-----|--------|---------|-----------------|------|
| 整型 | `int` | 4 | -21亿 ~ 21亿 | `int a = 100;` |
| 短整型 | `short` | 2 | -32768 ~ 32767 | `short s = 10;` |
| 长整型 | `long` | 4/8 | 更大范围 | `long l = 1000000L;` |
| 字符型 | `char` | 1 | -128 ~ 127 | `char c = 'A';` |
| 单精度浮点 | `float` | 4 | 约6位有效数字 | `float f = 3.14f;` |
| 双精度浮点 | `double` | 8 | 约15位有效数字 | `double d = 3.14159;` |

## 2.3 变量命名规则

- 只能由字母、数字、下划线组成
- 不能以数字开头
- 区分大小写
- 不能使用C语言关键字（如 int, return, if 等）

### 良好命名示例
```c
int studentAge;      // 驼峰命名
int student_age;     // 下划线命名
float averageScore;  // 有意义的名称
```

## 2.4 常量

```c
const int MAX_SIZE = 100;  // const常量
#define PI 3.14159        // 宏定义常量
```

## 2.5 类型转换

```c
int a = 5, b = 2;
float result = (float)a / b;  // 强制类型转换，result = 2.5
```

> **注意**：不进行强制转换时，`a / b` 结果为 `2`（整数除法会截断小数部分）。
"""

KP_C02_CODE = '''#include <stdio.h>

int main() {
    // 声明不同类型的变量
    int age = 20;
    float height = 175.5;
    double pi = 3.1415926535;
    char grade = 'A';

    // 输出变量值
    printf("年龄: %d 岁\\n", age);
    printf("身高: %.1f cm\\n", height);
    printf("圆周率: %.10f\\n", pi);
    printf("成绩等级: %c\\n", grade);

    // 整数除法 vs 浮点除法
    int a = 5, b = 2;
    printf("\\n整数除法: %d / %d = %d\\n", a, b, a / b);
    printf("浮点除法: %d / %d = %.2f\\n", a, b, (float)a / b);

    // 类型大小
    printf("\\n各类型占用字节数:\\n");
    printf("char: %zu\\n", sizeof(char));
    printf("int: %zu\\n", sizeof(int));
    printf("float: %zu\\n", sizeof(float));
    printf("double: %zu\\n", sizeof(double));

    return 0;
}'''

KP_C02_QS = [
    {"q_id": "q_c02_1", "type": "single_choice", "content": "在C语言中，int类型变量通常占用多少字节？", "options": [{"id": "A", "text": "1字节"}, {"id": "B", "text": "2字节"}, {"id": "C", "text": "4字节"}, {"id": "D", "text": "8字节"}], "correct_answer": "C", "explanation": "在32位和64位系统中，int类型通常占用4字节（32位）。"},
    {"q_id": "q_c02_2", "type": "single_choice", "content": "以下哪个是合法的变量名？", "options": [{"id": "A", "text": "2name"}, {"id": "B", "text": "int"}, {"id": "C", "text": "_score"}, {"id": "D", "text": "my-name"}], "correct_answer": "C", "explanation": "变量名不能以数字开头，不能是关键字，不能包含连字符。_score 是合法的。"},
    {"q_id": "q_c02_3", "type": "single_choice", "content": "表达式 5 / 2 的结果是多少？", "options": [{"id": "A", "text": "2.5"}, {"id": "B", "text": "2"}, {"id": "C", "text": "3"}, {"id": "D", "text": "2.0"}], "correct_answer": "B", "explanation": "整数除法会截断小数部分，5/2 的结果是 2。要得到2.5需要至少一个操作数是浮点数。"},
    {"q_id": "q_c02_4", "type": "single_choice", "content": "下列哪个常量定义是正确的？", "options": [{"id": "A", "text": "const MAX = 100;"}, {"id": "B", "text": "const int MAX = 100;"}, {"id": "C", "text": "int const MAX = 100;"}, {"id": "D", "text": "define MAX 100"}], "correct_answer": "B", "explanation": "const 常量必须指定数据类型，正确写法是 const int MAX = 100;"},
]

KP_C02_MM = {"root": "数据类型与变量", "children": [{"name": "变量声明"}, {"name": "基本类型"}, {"name": "命名规则"}, {"name": "常量"}, {"name": "类型转换"}]}


KP_C03_DOC = """# 运算符与表达式

## 3.1 算术运算符

| 运算符 | 含义 | 示例 | 结果 |
|-------|------|------|------|
| `+` | 加法 | `5 + 3` | 8 |
| `-` | 减法 | `5 - 3` | 2 |
| `*` | 乘法 | `5 * 3` | 15 |
| `/` | 除法 | `5 / 2` | 2（整数） |
| `%` | 取模（求余） | `5 % 2` | 1 |

## 3.2 关系运算符

用于比较两个值，结果为真(1)或假(0)。

| 运算符 | 含义 | 示例 | 结果 |
|-------|------|------|------|
| `==` | 等于 | `5 == 5` | 1（真） |
| `!=` | 不等于 | `5 != 3` | 1（真） |
| `>` | 大于 | `5 > 3` | 1（真） |
| `<` | 小于 | `5 < 3` | 0（假） |
| `>=` | 大于等于 | `5 >= 5` | 1（真） |
| `<=` | 小于等于 | `5 <= 3` | 0（假） |

## 3.3 逻辑运算符

| 运算符 | 含义 | 说明 |
|-------|------|------|
| `&&` | 逻辑与 | 两边都为真，结果才为真 |
| `||` | 逻辑或 | 只要一边为真，结果就为真 |
| `!` | 逻辑非 | 取反 |

```c
int a = 5, b = 10;
if (a > 0 && b > 0) {
    printf("两个数都为正数\\n");
}
```

## 3.4 赋值与复合赋值运算符

```c
int a = 10;
a += 5;   // 等价于 a = a + 5; 结果 a = 15
a -= 3;   // 等价于 a = a - 3; 结果 a = 12
a *= 2;   // 等价于 a = a * 2; 结果 a = 24
a /= 4;   // 等价于 a = a / 4; 结果 a = 6
a %= 4;   // 等价于 a = a % 4; 结果 a = 2
```

## 3.5 自增自减运算符

```c
int i = 5;
int a = ++i;  // 前置++：先加1，再赋值。a=6, i=6
int b = i++;  // 后置++：先赋值，再加1。b=6, i=7
```

> **优先级口诀**：括号 > 单目 > 算术 > 关系 > 逻辑 > 赋值
"""

KP_C03_CODE = '''#include <stdio.h>

int main() {
    int a = 17, b = 5;

    printf("算术运算:\\n");
    printf("%d + %d = %d\\n", a, b, a + b);
    printf("%d - %d = %d\\n", a, b, a - b);
    printf("%d * %d = %d\\n", a, b, a * b);
    printf("%d / %d = %d\\n", a, b, a / b);
    printf("%d %% %d = %d\\n", a, b, a % b);

    printf("\\n关系运算:\\n");
    printf("%d > %d ? %d\\n", a, b, a > b);
    printf("%d == %d ? %d\\n", a, b, a == b);

    printf("\\n逻辑运算:\\n");
    printf("(%d > 10) && (%d < 10) ? %d\\n", a, b, (a > 10) && (b < 10));
    printf("(%d > 20) || (%d < 10) ? %d\\n", a, b, (a > 20) || (b < 10));

    printf("\\n自增运算:\\n");
    int x = 5;
    printf("x = %d\\n", x);
    printf("++x = %d, x = %d\\n", ++x, x);
    printf("x++ = %d, x = %d\\n", x++, x);

    return 0;
}'''

KP_C03_QS = [
    {"q_id": "q_c03_1", "type": "single_choice", "content": "表达式 10 % 3 的结果是？", "options": [{"id": "A", "text": "3"}, {"id": "B", "text": "1"}, {"id": "C", "text": "0"}, {"id": "D", "text": "3.33"}], "correct_answer": "B", "explanation": "% 是取模运算符，10 除以 3 商 3 余 1，所以结果是 1。"},
    {"q_id": "q_c03_2", "type": "single_choice", "content": "设 int a = 5; 则执行 a += 3 后，a 的值是？", "options": [{"id": "A", "text": "3"}, {"id": "B", "text": "5"}, {"id": "C", "text": "8"}, {"id": "D", "text": "15"}], "correct_answer": "C", "explanation": "a += 3 等价于 a = a + 3，即 5 + 3 = 8。"},
    {"q_id": "q_c03_3", "type": "single_choice", "content": "设 int i = 5; int j = i++; 则 i 和 j 的值分别是？", "options": [{"id": "A", "text": "5, 5"}, {"id": "B", "text": "6, 5"}, {"id": "C", "text": "6, 6"}, {"id": "D", "text": "5, 6"}], "correct_answer": "B", "explanation": "i++ 是后置自增，先将 i 的值(5)赋给 j，然后 i 自增为 6。所以 i=6, j=5。"},
]

KP_C03_MM = {"root": "运算符与表达式", "children": [{"name": "算术运算符"}, {"name": "关系运算符"}, {"name": "逻辑运算符"}, {"name": "赋值运算符"}, {"name": "自增自减"}]}


KP_C04_DOC = """# 输入输出与顺序结构

## 4.1 格式化输出 printf

`printf` 是C语言最常用的输出函数，支持多种格式控制符。

| 格式符 | 说明 | 示例 |
|-------|------|------|
| `%d` | 输出十进制整数 | `printf("%d", 100);` |
| `%f` | 输出浮点数 | `printf("%f", 3.14);` |
| `%c` | 输出单个字符 | `printf("%c", 'A');` |
| `%s` | 输出字符串 | `printf("%s", "Hello");` |
| `%p` | 输出指针地址 | `printf("%p", &a);` |
| `%%` | 输出百分号 | `printf("%%");` |

### 格式控制
```c
printf("%.2f\\n", 3.14159);   // 保留2位小数: 3.14
printf("%5d\\n", 42);         // 占5个字符宽度: __42
printf("%-5d\\n", 42);        // 左对齐: 42__
```

## 4.2 格式化输入 scanf

```c
int age;
float score;
printf("请输入年龄和成绩: ");
scanf("%d %f", &age, &score);
printf("年龄: %d, 成绩: %.1f\\n", age, score);
```

> **重要**：`scanf` 中变量前必须加 `&`（取地址符），表示将输入的数据存入该地址对应的内存空间。

## 4.3 字符输入输出

```c
char ch;
ch = getchar();     // 读取一个字符
putchar(ch);        // 输出一个字符
```

## 4.4 顺序结构程序设计

顺序结构是程序最基本的结构，语句按照书写顺序依次执行。

```c
#include <stdio.h>

int main() {
    // 计算长方形面积
    float length, width, area;

    printf("请输入长方形的长: ");
    scanf("%f", &length);

    printf("请输入长方形的宽: ");
    scanf("%f", &width);

    area = length * width;
    printf("长方形的面积为: %.2f\\n", area);

    return 0;
}
```
"""

KP_C04_CODE = '''#include <stdio.h>

int main() {
    // 计算圆的周长和面积
    float radius;
    const float PI = 3.14159;

    printf("请输入圆的半径: ");
    scanf("%f", &radius);

    float circumference = 2 * PI * radius;
    float area = PI * radius * radius;

    printf("半径为 %.2f 的圆:\\n", radius);
    printf("周长 = %.2f\\n", circumference);
    printf("面积 = %.2f\\n", area);

    // 温度转换：华氏度转摄氏度
    float fahrenheit;
    printf("\\n请输入华氏温度: ");
    scanf("%f", &fahrenheit);
    float celsius = (fahrenheit - 32) * 5.0 / 9.0;
    printf("%.1f°F = %.1f°C\\n", fahrenheit, celsius);

    return 0;
}'''

KP_C04_QS = [
    {"q_id": "q_c04_1", "type": "single_choice", "content": "使用 scanf 读取整数变量 a 的正确语句是？", "options": [{"id": "A", "text": "scanf(\"%d\", a);"}, {"id": "B", "text": "scanf(\"%d\", &a);"}, {"id": "C", "text": "scanf(\"%f\", &a);"}, {"id": "D", "text": "scanf(\"%d\", *a);"}], "correct_answer": "B", "explanation": "scanf 需要传入变量的地址，因此必须加 & 取地址符。整数用 %d。"},
    {"q_id": "q_c04_2", "type": "single_choice", "content": "printf(\"%.2f\", 3.14159) 的输出结果是？", "options": [{"id": "A", "text": "3.14"}, {"id": "B", "text": "3.14159"}, {"id": "C", "text": "3.141"}, {"id": "D", "text": "3.15"}], "correct_answer": "A", "explanation": "%.2f 表示保留2位小数，对第3位四舍五入，3.14159 保留两位是 3.14。"},
    {"q_id": "q_c04_3", "type": "single_choice", "content": "以下哪个函数用于从键盘读取一个字符？", "options": [{"id": "A", "text": "printf()"}, {"id": "B", "text": "scanf()"}, {"id": "C", "text": "getchar()"}, {"id": "D", "text": "putchar()"}], "correct_answer": "C", "explanation": "getchar() 函数专门用于从标准输入读取一个字符。"},
]

KP_C04_MM = {"root": "输入输出与顺序结构", "children": [{"name": "printf输出"}, {"name": "scanf输入"}, {"name": "格式控制符"}, {"name": "getchar/putchar"}, {"name": "顺序结构"}]}


KP_C05_DOC = """# 选择结构（if、switch）

## 5.1 if 语句

### 单分支
```c
if (条件表达式) {
    // 条件为真时执行
}
```

### 双分支
```c
if (条件表达式) {
    // 条件为真时执行
} else {
    // 条件为假时执行
}
```

### 多分支
```c
if (score >= 90) {
    printf("优秀\\n");
} else if (score >= 80) {
    printf("良好\\n");
} else if (score >= 60) {
    printf("及格\\n");
} else {
    printf("不及格\\n");
}
```

## 5.2 嵌套 if

```c
if (a > b) {
    if (a > c) {
        printf("最大数是 a\\n");
    } else {
        printf("最大数是 c\\n");
    }
}
```

## 5.3 switch 语句

适用于多分支等值判断，结构比 if-else if 更清晰。

```c
switch (表达式) {
    case 常量1:
        // 语句
        break;
    case 常量2:
        // 语句
        break;
    default:
        // 默认语句
}
```

### 示例：根据数字输出星期
```c
int day = 3;
switch (day) {
    case 1: printf("星期一\\n"); break;
    case 2: printf("星期二\\n"); break;
    case 3: printf("星期三\\n"); break;
    case 4: printf("星期四\\n"); break;
    case 5: printf("星期五\\n"); break;
    case 6: printf("星期六\\n"); break;
    case 7: printf("星期日\\n"); break;
    default: printf("无效输入\\n");
}
```

> **注意**：每个 case 末尾不要忘记 `break`，否则会"穿透"到下一个 case 继续执行。
"""

KP_C05_CODE = '''#include <stdio.h>

int main() {
    int score;
    printf("请输入成绩 (0-100): ");
    scanf("%d", &score);

    // if-else 判断等级
    if (score < 0 || score > 100) {
        printf("成绩输入无效!\\n");
    } else if (score >= 90) {
        printf("等级: A (优秀)\\n");
    } else if (score >= 80) {
        printf("等级: B (良好)\\n");
    } else if (score >= 70) {
        printf("等级: C (中等)\\n");
    } else if (score >= 60) {
        printf("等级: D (及格)\\n");
    } else {
        printf("等级: F (不及格)\\n");
    }

    // switch 判断月份天数
    int month;
    printf("\\n请输入月份 (1-12): ");
    scanf("%d", &month);

    switch (month) {
        case 1: case 3: case 5: case 7: case 8: case 10: case 12:
            printf("%d月有31天\\n", month);
            break;
        case 4: case 6: case 9: case 11:
            printf("%d月有30天\\n", month);
            break;
        case 2:
            printf("%d月有28或29天\\n", month);
            break;
        default:
            printf("无效的月份!\\n");
    }

    return 0;
}'''

KP_C05_QS = [
    {"q_id": "q_c05_1", "type": "single_choice", "content": "以下关于 if 语句的说法，正确的是？", "options": [{"id": "A", "text": "if 后面可以没有括号"}, {"id": "B", "text": "if 后面的条件表达式必须用圆括号包裹"}, {"id": "C", "text": "else 可以单独使用"}, {"id": "D", "text": "if 后面只能跟一条语句"}], "correct_answer": "B", "explanation": "if 后面的条件表达式必须用圆括号 () 包裹，这是C语言的语法要求。"},
    {"q_id": "q_c05_2", "type": "single_choice", "content": "switch 语句中，case 分支末尾通常使用什么关键字防止穿透？", "options": [{"id": "A", "text": "continue"}, {"id": "B", "text": "return"}, {"id": "C", "text": "break"}, {"id": "D", "text": "exit"}], "correct_answer": "C", "explanation": "break 用于跳出 switch 语句，防止程序继续执行下一个 case（穿透效应）。"},
    {"q_id": "q_c05_3", "type": "single_choice", "content": "表达式 (5 > 3) && (2 > 4) || (6 > 1) 的结果是？", "options": [{"id": "A", "text": "0"}, {"id": "B", "text": "1"}, {"id": "C", "text": "编译错误"}, {"id": "D", "text": "不确定"}], "correct_answer": "B", "explanation": "&& 优先级高于 ||。(5>3)&&(2>4) 为假(0)，但 || (6>1) 为真(1)，所以整体为真(1)。"},
]

KP_C05_MM = {"root": "选择结构", "children": [{"name": "if单分支"}, {"name": "if-else双分支"}, {"name": "if-else if多分支"}, {"name": "嵌套if"}, {"name": "switch语句"}, {"name": "break穿透"}]}


KP_C06_DOC = """# 循环结构（for、while、do-while）

## 6.1 for 循环

适用于已知循环次数的场景。

```c
for (初始化; 条件判断; 迭代操作) {
    // 循环体
}
```

### 示例：计算1到100的和
```c
int sum = 0;
for (int i = 1; i <= 100; i++) {
    sum += i;
}
printf("1+2+...+100 = %d\\n", sum);  // 输出 5050
```

## 6.2 while 循环

适用于不确定循环次数，但已知循环条件的场景。

```c
while (条件表达式) {
    // 循环体
}
```

### 示例：猜数字游戏
```c
int target = 7, guess;
while (1) {
    printf("猜一个数字: ");
    scanf("%d", &guess);
    if (guess == target) {
        printf("猜对了!\\n");
        break;
    } else if (guess < target) {
        printf("太小了\\n");
    } else {
        printf("太大了\\n");
    }
}
```

## 6.3 do-while 循环

至少执行一次循环体，然后再判断条件。

```c
do {
    // 循环体
} while (条件表达式);
```

## 6.4 循环控制语句

| 语句 | 作用 |
|-----|------|
| `break` | 立即跳出当前循环 |
| `continue` | 跳过当前迭代，进入下一次循环 |

## 6.5 嵌套循环

```c
// 打印九九乘法表
for (int i = 1; i <= 9; i++) {
    for (int j = 1; j <= i; j++) {
        printf("%d*%d=%-2d ", j, i, i * j);
    }
    printf("\\n");
}
```
"""

KP_C06_CODE = '''#include <stdio.h>

int main() {
    // for循环：计算阶乘
    int n;
    printf("请输入一个正整数: ");
    scanf("%d", &n);

    long long factorial = 1;
    for (int i = 1; i <= n; i++) {
        factorial *= i;
    }
    printf("%d! = %lld\\n", n, factorial);

    // while循环：计算斐波那契数列前10项
    printf("\\n斐波那契数列前10项:\\n");
    int a = 0, b = 1, count = 0;
    while (count < 10) {
        printf("%d ", a);
        int temp = a + b;
        a = b;
        b = temp;
        count++;
    }
    printf("\\n");

    // do-while：输入验证
    int num;
    printf("\\n请输入1-10之间的数字: ");
    do {
        scanf("%d", &num);
        if (num < 1 || num > 10) {
            printf("输入无效，请重新输入: ");
        }
    } while (num < 1 || num > 10);
    printf("你输入了: %d\\n", num);

    // 嵌套循环：打印直角三角形
    printf("\\n直角三角形:\\n");
    for (int i = 1; i <= 5; i++) {
        for (int j = 1; j <= i; j++) {
            printf("* ");
        }
        printf("\\n");
    }

    return 0;
}'''

KP_C06_QS = [
    {"q_id": "q_c06_1", "type": "single_choice", "content": "以下哪种循环至少会执行一次循环体？", "options": [{"id": "A", "text": "for"}, {"id": "B", "text": "while"}, {"id": "C", "text": "do-while"}, {"id": "D", "text": "都一样"}], "correct_answer": "C", "explanation": "do-while 先执行循环体，再判断条件，因此至少执行一次。"},
    {"q_id": "q_c06_2", "type": "single_choice", "content": "在循环中，continue 语句的作用是？", "options": [{"id": "A", "text": "终止整个程序"}, {"id": "B", "text": "跳出当前循环"}, {"id": "C", "text": "跳过本次循环剩余部分，进入下一次迭代"}, {"id": "D", "text": "暂停程序执行"}], "correct_answer": "C", "explanation": "continue 用于跳过当前迭代的剩余语句，直接进入下一次循环条件判断。"},
    {"q_id": "q_c06_3", "type": "single_choice", "content": "for (int i=0; i<10; i++) 循环会执行多少次？", "options": [{"id": "A", "text": "9次"}, {"id": "B", "text": "10次"}, {"id": "C", "text": "11次"}, {"id": "D", "text": "无限次"}], "correct_answer": "B", "explanation": "i 从 0 开始，到 9 结束（i<10），共 10 次迭代。"},
]

KP_C06_MM = {"root": "循环结构", "children": [{"name": "for循环"}, {"name": "while循环"}, {"name": "do-while循环"}, {"name": "break"}, {"name": "continue"}, {"name": "嵌套循环"}]}


KP_C07_DOC = """# 数组

## 7.1 一维数组

数组是相同类型数据的集合，在内存中连续存放。

```c
// 声明与初始化
int scores[5] = {85, 92, 78, 90, 88};
int numbers[] = {1, 2, 3, 4, 5};  // 编译器自动计算长度
float temps[7];  // 声明后逐个赋值
```

### 数组访问
```c
printf("第一个元素: %d\\n", scores[0]);  // 下标从0开始
scores[2] = 95;  // 修改第三个元素
```

> **注意**：C语言不检查数组越界！访问 `scores[10]` 不会报错，但可能导致程序崩溃或数据损坏。

## 7.2 数组遍历

```c
int arr[5] = {10, 20, 30, 40, 50};
for (int i = 0; i < 5; i++) {
    printf("arr[%d] = %d\\n", i, arr[i]);
}
```

## 7.3 数组常见算法

### 求最大值
```c
int max = arr[0];
for (int i = 1; i < n; i++) {
    if (arr[i] > max) {
        max = arr[i];
    }
}
```

### 冒泡排序
```c
for (int i = 0; i < n - 1; i++) {
    for (int j = 0; j < n - 1 - i; j++) {
        if (arr[j] > arr[j + 1]) {
            int temp = arr[j];
            arr[j] = arr[j + 1];
            arr[j + 1] = temp;
        }
    }
}
```

## 7.4 二维数组

```c
int matrix[3][4] = {
    {1, 2, 3, 4},
    {5, 6, 7, 8},
    {9, 10, 11, 12}
};

// 遍历二维数组
for (int i = 0; i < 3; i++) {
    for (int j = 0; j < 4; j++) {
        printf("%d ", matrix[i][j]);
    }
    printf("\\n");
}
```
"""

KP_C07_CODE = '''#include <stdio.h>

int main() {
    // 一维数组：学生成绩
    int scores[5] = {78, 85, 92, 67, 88};
    int n = 5;

    printf("原始成绩: ");
    for (int i = 0; i < n; i++) {
        printf("%d ", scores[i]);
    }
    printf("\\n");

    // 求和与平均值
    int sum = 0;
    for (int i = 0; i < n; i++) {
        sum += scores[i];
    }
    printf("总分: %d, 平均分: %.1f\\n", sum, (float)sum / n);

    // 找最大值和最小值
    int max = scores[0], min = scores[0];
    for (int i = 1; i < n; i++) {
        if (scores[i] > max) max = scores[i];
        if (scores[i] < min) min = scores[i];
    }
    printf("最高分: %d, 最低分: %d\\n", max, min);

    // 冒泡排序
    for (int i = 0; i < n - 1; i++) {
        for (int j = 0; j < n - 1 - i; j++) {
            if (scores[j] > scores[j + 1]) {
                int temp = scores[j];
                scores[j] = scores[j + 1];
                scores[j + 1] = temp;
            }
        }
    }
    printf("排序后: ");
    for (int i = 0; i < n; i++) {
        printf("%d ", scores[i]);
    }
    printf("\\n");

    // 二维数组：矩阵相加
    int a[2][3] = {{1, 2, 3}, {4, 5, 6}};
    int b[2][3] = {{7, 8, 9}, {10, 11, 12}};
    printf("\\n矩阵相加结果:\\n");
    for (int i = 0; i < 2; i++) {
        for (int j = 0; j < 3; j++) {
            printf("%2d ", a[i][j] + b[i][j]);
        }
        printf("\\n");
    }

    return 0;
}'''

KP_C07_QS = [
    {"q_id": "q_c07_1", "type": "single_choice", "content": "在C语言中，数组下标从几开始？", "options": [{"id": "A", "text": "0"}, {"id": "B", "text": "1"}, {"id": "C", "text": "-1"}, {"id": "D", "text": "任意值"}], "correct_answer": "A", "explanation": "C语言数组下标从0开始，第一个元素是 arr[0]。"},
    {"q_id": "q_c07_2", "type": "single_choice", "content": "声明 int arr[5] 后，以下哪个访问是安全的？", "options": [{"id": "A", "text": "arr[5]"}, {"id": "B", "text": "arr[-1]"}, {"id": "C", "text": "arr[4]"}, {"id": "D", "text": "arr[10]"}], "correct_answer": "C", "explanation": "arr[5] 的有效下标是 0~4，arr[4] 是最后一个合法元素。"},
    {"q_id": "q_c07_3", "type": "single_choice", "content": "二维数组 int a[3][4] 有多少个元素？", "options": [{"id": "A", "text": "7"}, {"id": "B", "text": "12"}, {"id": "C", "text": "16"}, {"id": "D", "text": "3"}], "correct_answer": "B", "explanation": "3行4列，共 3 * 4 = 12 个元素。"},
]

KP_C07_MM = {"root": "数组", "children": [{"name": "一维数组"}, {"name": "数组初始化"}, {"name": "数组遍历"}, {"name": "求最值"}, {"name": "排序"}, {"name": "二维数组"}]}


KP_C08_DOC = """# 字符串

## 8.1 字符串的本质

C语言中没有专门的字符串类型，字符串本质上是**以 \\0 结尾的字符数组**。

```c
char str1[] = "Hello";      // 自动包含 \\0，实际长度为6
char str2[20] = "World";    // 预留空间
char str3[] = {'H', 'i', '\\0'};  // 手动定义
```

## 8.2 字符串输入输出

```c
char name[50];
printf("请输入你的名字: ");
scanf("%s", name);          // 读取一个单词（遇空格停止）
printf("你好, %s\\n", name);

// 读取一行（含空格）
char line[100];
getchar();  // 吃掉换行符
fgets(line, sizeof(line), stdin);
```

## 8.3 常用字符串函数（string.h）

| 函数 | 功能 | 示例 |
|-----|------|------|
| `strlen(s)` | 求字符串长度（不含\\0） | `strlen("abc")` → 3 |
| `strcpy(dest, src)` | 复制字符串 | `strcpy(a, b)` |
| `strcat(dest, src)` | 拼接字符串 | `strcat(a, b)` |
| `strcmp(s1, s2)` | 比较字符串 | 相等返回0 |
| `strchr(s, c)` | 查找字符 | 返回首次出现位置 |
| `strstr(s1, s2)` | 查找子串 | 返回首次出现位置 |

## 8.4 字符串操作示例

```c
#include <stdio.h>
#include <string.h>

int main() {
    char s1[50] = "Hello";
    char s2[50] = "World";

    printf("s1长度: %zu\\n", strlen(s1));

    strcat(s1, " ");
    strcat(s1, s2);
    printf("拼接后: %s\\n", s1);  // Hello World

    if (strcmp(s1, s2) > 0) {
        printf("s1 大于 s2\\n");
    }

    return 0;
}
```

> **注意**：使用 strcpy 和 strcat 时要确保目标数组有足够的空间，否则会造成缓冲区溢出！
"""

KP_C08_CODE = '''#include <stdio.h>
#include <string.h>

int main() {
    char str1[50] = "C Language";
    char str2[50] = "Programming";

    // 字符串长度
    printf("\"%s\" 的长度是: %zu\\n", str1, strlen(str1));

    // 字符串复制
    char copy[50];
    strcpy(copy, str1);
    printf("复制结果: %s\\n", copy);

    // 字符串拼接
    strcat(copy, " ");
    strcat(copy, str2);
    printf("拼接结果: %s\\n", copy);

    // 字符串比较
    int cmp = strcmp(str1, str2);
    if (cmp == 0) {
        printf("两个字符串相等\\n");
    } else if (cmp < 0) {
        printf("\"%s\" < \"%s\"\\n", str1, str2);
    } else {
        printf("\"%s\" > \"%s\"\\n", str1, str2);
    }

    // 查找字符和子串
    char *p = strchr(str1, 'L');
    if (p) {
        printf("'L' 在 \"%s\" 中的位置: %ld\\n", str1, p - str1);
    }

    // 手动遍历字符串
    printf("\\n逐个字符输出:\\n");
    for (int i = 0; str1[i] != '\\0'; i++) {
        printf("str1[%d] = '%c'\\n", i, str1[i]);
    }

    return 0;
}'''

KP_C08_QS = [
    {"q_id": "q_c08_1", "type": "single_choice", "content": "C语言中，字符串 \"abc\" 实际占用的字节数是？", "options": [{"id": "A", "text": "3"}, {"id": "B", "text": "4"}, {"id": "C", "text": "2"}, {"id": "D", "text": "不确定"}], "correct_answer": "B", "explanation": "字符串末尾自动添加 '\\0' 结束符，所以 \"abc\" 实际占用4字节。"},
    {"q_id": "q_c08_2", "type": "single_choice", "content": "以下哪个函数用于计算字符串长度（不含结束符）？", "options": [{"id": "A", "text": "sizeof()"}, {"id": "B", "text": "strlen()"}, {"id": "C", "text": "length()"}, {"id": "D", "text": "size()"}], "correct_answer": "B", "explanation": "strlen() 来自 string.h，计算字符串实际长度（不含 '\\0'）。"},
    {"q_id": "q_c08_3", "type": "single_choice", "content": "char s[10] = \"Hello\"; strcpy(s, \"HelloWorld\"); 这段代码？", "options": [{"id": "A", "text": "正常运行"}, {"id": "B", "text": "编译错误"}, {"id": "C", "text": "缓冲区溢出，可能导致程序异常"}, {"id": "D", "text": "自动扩展数组大小"}], "correct_answer": "C", "explanation": "目标数组 s 只有10字节，HelloWorld 加上结束符需要11字节，会导致缓冲区溢出。"},
]

KP_C08_MM = {"root": "字符串", "children": [{"name": "字符数组"}, {"name": "字符串输入"}, {"name": "strlen"}, {"name": "strcpy"}, {"name": "strcat"}, {"name": "strcmp"}]}


KP_C09_DOC = """# 函数与递归

## 9.1 函数的定义与调用

函数是完成特定任务的代码块，可以被重复调用。

```c
// 函数定义
返回值类型 函数名(参数列表) {
    // 函数体
    return 返回值;
}
```

### 示例
```c
// 函数声明（放在main之前）
int add(int a, int b);

int main() {
    int result = add(3, 5);
    printf("3 + 5 = %d\\n", result);
    return 0;
}

// 函数定义
int add(int a, int b) {
    return a + b;
}
```

## 9.2 参数传递方式

C语言函数参数采用**值传递**：函数内部修改参数不会影响外部变量。

```c
void swap_wrong(int a, int b) {
    int temp = a;
    a = b;
    b = temp;  // 这里的交换不会影响到外部
}

void swap_correct(int *a, int *b) {
    int temp = *a;
    *a = *b;
    *b = temp;  // 通过指针修改外部变量
}
```

## 9.3 递归函数

函数调用自身的过程称为递归。递归必须有一个**终止条件**。

### 计算阶乘
```c
int factorial(int n) {
    if (n <= 1) return 1;        // 终止条件
    return n * factorial(n - 1); // 递归调用
}
```

### 斐波那契数列
```c
int fib(int n) {
    if (n <= 1) return n;
    return fib(n - 1) + fib(n - 2);
}
```

> **注意**：递归虽然简洁，但过深的递归会导致栈溢出。实际工程中要考虑迭代方案或尾递归优化。

## 9.4 变量的作用域与生命周期

| 类型 | 声明位置 | 作用域 | 生命周期 |
|-----|---------|--------|---------|
| 局部变量 | 函数内部 | 所在函数 | 函数执行期间 |
| 全局变量 | 函数外部 | 整个文件 | 程序运行期间 |
| 静态变量 | 加static关键字 | 同局部/全局 | 程序运行期间 |

```c
void counter() {
    static int count = 0;  // 静态局部变量，只初始化一次
    count++;
    printf("调用次数: %d\\n", count);
}
```
"""

KP_C09_CODE = '''#include <stdio.h>

// 函数声明
int add(int a, int b);
int factorial(int n);
int fib(int n);
void swap(int *a, int *b);

int main() {
    // 基本函数调用
    printf("3 + 5 = %d\\n", add(3, 5));

    // 阶乘
    printf("\\n阶乘:\\n");
    for (int i = 1; i <= 7; i++) {
        printf("%d! = %d\\n", i, factorial(i));
    }

    // 斐波那契
    printf("\\n斐波那契数列前10项:\\n");
    for (int i = 0; i < 10; i++) {
        printf("%d ", fib(i));
    }
    printf("\\n");

    // 指针交换
    int x = 10, y = 20;
    printf("\\n交换前: x=%d, y=%d\\n", x, y);
    swap(&x, &y);
    printf("交换后: x=%d, y=%d\\n", x, y);

    return 0;
}

int add(int a, int b) {
    return a + b;
}

int factorial(int n) {
    if (n <= 1) return 1;
    return n * factorial(n - 1);
}

int fib(int n) {
    if (n <= 1) return n;
    return fib(n - 1) + fib(n - 2);
}

void swap(int *a, int *b) {
    int temp = *a;
    *a = *b;
    *b = temp;
}'''

KP_C09_QS = [
    {"q_id": "q_c09_1", "type": "single_choice", "content": "C语言函数参数默认采用什么传递方式？", "options": [{"id": "A", "text": "引用传递"}, {"id": "B", "text": "值传递"}, {"id": "C", "text": "指针传递"}, {"id": "D", "text": "地址传递"}], "correct_answer": "B", "explanation": "C语言函数参数默认是值传递，函数内修改参数不会影响外部变量。"},
    {"q_id": "q_c09_2", "type": "single_choice", "content": "以下关于递归的说法，错误的是？", "options": [{"id": "A", "text": "递归函数必须有一个终止条件"}, {"id": "B", "text": "递归就是自己调用自己"}, {"id": "C", "text": "递归一定比迭代效率高"}, {"id": "D", "text": "递归过深可能导致栈溢出"}], "correct_answer": "C", "explanation": "递归通常比迭代效率低，因为涉及大量的函数调用开销和栈空间占用。"},
    {"q_id": "q_c09_3", "type": "single_choice", "content": "static 局部变量的特点是？", "options": [{"id": "A", "text": "每次函数调用都重新初始化"}, {"id": "B", "text": "只初始化一次，生命周期贯穿整个程序"}, {"id": "C", "text": "可以被其他文件访问"}, {"id": "D", "text": "存储在栈区"}], "correct_answer": "B", "explanation": "static 局部变量只初始化一次，其生命周期与全局变量相同，但作用域仍限于所在函数。"},
]

KP_C09_MM = {"root": "函数与递归", "children": [{"name": "函数定义"}, {"name": "参数传递"}, {"name": "返回值"}, {"name": "递归原理"}, {"name": "阶乘与斐波那契"}, {"name": "作用域"}]}


KP_C10_DOC = """# 指针基础

## 10.1 什么是指针

指针是**存储内存地址的变量**。通过指针，我们可以直接访问和操作内存。

```c
int a = 10;
int *p = &a;   // p 存储了 a 的地址

printf("a 的值: %d\\n", a);      // 10
printf("a 的地址: %p\\n", &a);   // 0x7ff...
printf("p 的值: %p\\n", p);       // 0x7ff...（与&a相同）
printf("p 指向的值: %d\\n", *p);  // 10（解引用）
```

### 指针声明语法
```c
int *p1;     // 指向int的指针
float *p2;   // 指向float的指针
char *p3;    // 指向char的指针
```

## 10.2 取地址与解引用

| 运算符 | 名称 | 作用 |
|-------|------|------|
| `&` | 取地址符 | 获取变量的内存地址 |
| `*` | 解引用符 | 通过地址访问对应的值 |

```c
int x = 100;
int *p = &x;

*p = 200;  // 通过指针修改 x 的值
printf("x = %d\\n", x);  // 输出 200
```

## 10.3 指针与函数

通过指针，函数可以修改外部变量的值（模拟引用传递）。

```c
void increment(int *p) {
    (*p)++;  // 注意括号！*p++ 的含义不同
}

int main() {
    int a = 5;
    increment(&a);
    printf("a = %d\\n", a);  // 输出 6
    return 0;
}
```

## 10.4 空指针与野指针

```c
int *p = NULL;  // 空指针，不指向任何有效地址

// 使用前先检查
if (p != NULL) {
    printf("%d\\n", *p);
}
```

> **野指针**是指向已释放内存或未初始化地址的指针，使用野指针会导致不可预知的错误。

## 10.5 指针的运算

```c
int arr[5] = {10, 20, 30, 40, 50};
int *p = arr;

printf("*p = %d\\n", *p);       // 10
printf("*(p+1) = %d\\n", *(p+1)); // 20
printf("p[2] = %d\\n", p[2]);    // 30（等价于 *(p+2)）
```
"""

KP_C10_CODE = '''#include <stdio.h>

void swap(int *a, int *b);
void printArray(int *arr, int size);

int main() {
    // 指针基础
    int num = 42;
    int *p = &num;

    printf("num = %d\\n", num);
    printf("&num = %p\\n", (void*)&num);
    printf("p = %p\\n", (void*)p);
    printf("*p = %d\\n", *p);

    // 通过指针修改值
    *p = 100;
    printf("\\n修改后 num = %d\\n", num);

    // 指针与函数
    int x = 10, y = 20;
    printf("\\n交换前: x=%d, y=%d\\n", x, y);
    swap(&x, &y);
    printf("交换后: x=%d, y=%d\\n", x, y);

    // 指针运算
    int arr[] = {10, 20, 30, 40, 50};
    printf("\\n数组元素通过指针访问:\\n");
    printArray(arr, 5);

    return 0;
}

void swap(int *a, int *b) {
    int temp = *a;
    *a = *b;
    *b = temp;
}

void printArray(int *arr, int size) {
    for (int i = 0; i < size; i++) {
        printf("*(arr+%d) = %d\\n", i, *(arr + i));
    }
}'''

KP_C10_QS = [
    {"q_id": "q_c10_1", "type": "single_choice", "content": "若有 int a = 5; int *p = &a; 则 *p 的值是？", "options": [{"id": "A", "text": "a的地址"}, {"id": "B", "text": "5"}, {"id": "C", "text": "p的地址"}, {"id": "D", "text": "不确定"}], "correct_answer": "B", "explanation": "*p 是解引用操作，获取指针 p 所指向地址的值，即 a 的值 5。"},
    {"q_id": "q_c10_2", "type": "single_choice", "content": "以下哪个表示指针 p 指向的值加1？", "options": [{"id": "A", "text": "*p++"}, {"id": "B", "text": "(*p)++"}, {"id": "C", "text": "*p+1"}, {"id": "D", "text": "++*p"}], "correct_answer": "B", "explanation": "由于 ++ 的优先级高于 *，*p++ 等价于 *(p++)，会移动指针。要修改指向的值，必须用 (*p)++。"},
    {"q_id": "q_c10_3", "type": "single_choice", "content": "空指针在C语言中通常用哪个宏表示？", "options": [{"id": "A", "text": "VOID"}, {"id": "B", "text": "NIL"}, {"id": "C", "text": "NULL"}, {"id": "D", "text": "ZERO"}], "correct_answer": "C", "explanation": "NULL 是C语言标准定义的空指针常量，表示指针不指向任何有效地址。"},
]

KP_C10_MM = {"root": "指针基础", "children": [{"name": "地址与指针"}, {"name": "取地址&"}, {"name": "解引用*"}, {"name": "指针与函数"}, {"name": "空指针"}, {"name": "指针运算"}]}


KP_C11_DOC = """# 指针与数组、字符串

## 11.1 数组名即指针

在C语言中，**数组名本质上是一个指向数组首元素的常量指针**。

```c
int arr[5] = {10, 20, 30, 40, 50};
int *p = arr;  // 等价于 p = &arr[0]

// 以下四种访问方式等价
printf("%d\\n", arr[2]);
printf("%d\\n", *(arr + 2));
printf("%d\\n", p[2]);
printf("%d\\n", *(p + 2));
```

## 11.2 指针遍历数组

```c
int arr[] = {1, 2, 3, 4, 5};
int n = sizeof(arr) / sizeof(arr[0]);

// 方式1：下标法
for (int i = 0; i < n; i++) {
    printf("%d ", arr[i]);
}

// 方式2：指针法
for (int *p = arr; p < arr + n; p++) {
    printf("%d ", *p);
}
```

## 11.3 字符指针与字符串

```c
char str1[] = "Hello";       // 字符数组，内容可修改
char *str2 = "Hello";        // 字符串常量，内容不可修改

str1[0] = 'h';   // 合法
// str2[0] = 'h'; // 非法！可能导致程序崩溃
```

## 11.4 指针数组

```c
char *names[] = {"Alice", "Bob", "Charlie"};
for (int i = 0; i < 3; i++) {
    printf("%s\\n", names[i]);
}
```

## 11.5 多级指针

```c
int a = 10;
int *p = &a;
int **pp = &p;  // 指向指针的指针

printf("a = %d\\n", a);       // 10
printf("*p = %d\\n", *p);     // 10
printf("**pp = %d\\n", **pp); // 10
```
"""

KP_C11_CODE = '''#include <stdio.h>

int main() {
    // 数组名即指针
    int arr[] = {10, 20, 30, 40, 50};
    int *p = arr;

    printf("数组访问方式对比:\\n");
    printf("arr[2] = %d\\n", arr[2]);
    printf("*(arr+2) = %d\\n", *(arr + 2));
    printf("p[2] = %d\\n", p[2]);
    printf("*(p+2) = %d\\n", *(p + 2));

    // 指针遍历数组
    printf("\\n指针遍历数组:\\n");
    int n = sizeof(arr) / sizeof(arr[0]);
    for (int *ptr = arr; ptr < arr + n; ptr++) {
        printf("%d ", *ptr);
    }
    printf("\\n");

    // 指针数组
    char *names[] = {"Alice", "Bob", "Charlie", "David"};
    printf("\\n指针数组:\\n");
    for (int i = 0; i < 4; i++) {
        printf("names[%d] = %s\\n", i, names[i]);
    }

    // 多级指针
    int num = 42;
    int *p1 = &num;
    int **p2 = &p1;
    printf("\\n多级指针:\\n");
    printf("num = %d\\n", num);
    printf("*p1 = %d\\n", *p1);
    printf("**p2 = %d\\n", **p2);

    return 0;
}'''

KP_C11_QS = [
    {"q_id": "q_c11_1", "type": "single_choice", "content": "若有 int arr[5]; int *p = arr; 则 arr[2] 等价于？", "options": [{"id": "A", "text": "p + 2"}, {"id": "B", "text": "*(p + 2)"}, {"id": "C", "text": "*p + 2"}, {"id": "D", "text": "p[1]"}], "correct_answer": "B", "explanation": "arr[i] 等价于 *(arr + i)，也等价于 *(p + i) 或 p[i]。"},
    {"q_id": "q_c11_2", "type": "single_choice", "content": "char *s = \"Hello\"; s[0] = 'h'; 这段代码？", "options": [{"id": "A", "text": "正常运行"}, {"id": "B", "text": "编译错误"}, {"id": "C", "text": "可能运行错误，因为字符串常量不可修改"}, {"id": "D", "text": "自动分配新内存"}], "correct_answer": "C", "explanation": "char *s = \"Hello\" 指向字符串常量，存储在只读数据区，修改它会导致未定义行为。"},
    {"q_id": "q_c11_3", "type": "single_choice", "content": "二级指针 int **pp 中，**pp 表示？", "options": [{"id": "A", "text": "pp的地址"}, {"id": "B", "text": "pp指向的指针的地址"}, {"id": "C", "text": "pp指向的指针所指向的int值"}, {"id": "D", "text": "pp的值"}], "correct_answer": "C", "explanation": "*pp 得到 pp 指向的指针，**pp 再解引用一次，得到最终指向的整数值。"},
]

KP_C11_MM = {"root": "指针与数组", "children": [{"name": "数组名即指针"}, {"name": "指针遍历"}, {"name": "字符指针"}, {"name": "指针数组"}, {"name": "多级指针"}]}


KP_C12_DOC = """# 结构体与联合体

## 12.1 结构体的定义

结构体允许将不同类型的数据组合成一个整体。

```c
struct Student {
    char name[50];
    int age;
    float score;
};

// 声明变量
struct Student stu1 = {"张三", 20, 85.5};

// 使用 typedef 简化
typedef struct {
    char name[50];
    int age;
} Student;

Student stu2 = {"李四", 21};
```

## 12.2 结构体成员的访问

```c
// 结构体变量用 .
printf("姓名: %s\\n", stu1.name);
printf("年龄: %d\\n", stu1.age);

// 结构体指针用 ->
struct Student *p = &stu1;
printf("姓名: %s\\n", p->name);
printf("年龄: %d\\n", p->age);
```

## 12.3 结构体数组

```c
struct Student class[3] = {
    {"张三", 20, 85},
    {"李四", 21, 90},
    {"王五", 19, 78}
};

for (int i = 0; i < 3; i++) {
    printf("%s: %.1f\\n", class[i].name, class[i].score);
}
```

## 12.4 结构体嵌套

```c
struct Date {
    int year, month, day;
};

struct Person {
    char name[50];
    struct Date birthday;
};

struct Person p = {"张三", {2000, 5, 15}};
printf("出生日期: %d-%d-%d\\n", p.birthday.year, p.birthday.month, p.birthday.day);
```

## 12.5 联合体（union）

联合体所有成员共享同一块内存，大小等于最大成员的大小。

```c
union Data {
    int i;
    float f;
    char str[20];
};

union Data d;
d.i = 10;       // 使用整数成员
d.f = 3.14;     // 现在浮点成员有效，整数成员被破坏
```

> **适用场景**：当多个数据互斥使用时，用联合体节省内存。
"""

KP_C12_CODE = '''#include <stdio.h>
#include <string.h>

// 定义结构体
typedef struct {
    char name[50];
    int age;
    float score;
} Student;

typedef struct {
    int year;
    int month;
    int day;
} Date;

typedef struct {
    char title[100];
    Date publishDate;
    float price;
} Book;

int main() {
    // 结构体变量
    Student stu = {"张三", 20, 85.5};
    printf("学生: %s, 年龄: %d, 成绩: %.1f\\n", stu.name, stu.age, stu.score);

    // 结构体指针
    Student *p = &stu;
    p->score = 92.0;
    printf("修改后成绩: %.1f\\n", p->score);

    // 结构体数组
    Student class[3] = {
        {"李四", 21, 88},
        {"王五", 20, 91},
        {"赵六", 19, 76}
    };
    printf("\\n班级成绩:\\n");
    float total = 0;
    for (int i = 0; i < 3; i++) {
        printf("%s: %.1f\\n", class[i].name, class[i].score);
        total += class[i].score;
    }
    printf("平均分: %.1f\\n", total / 3);

    // 嵌套结构体
    Book book = {"C语言程序设计", {2024, 3, 15}, 59.0};
    printf("\\n书名: %s\\n", book.title);
    printf("出版日期: %d-%02d-%02d\\n", book.publishDate.year, book.publishDate.month, book.publishDate.day);
    printf("价格: %.2f元\\n", book.price);

    return 0;
}'''

KP_C12_QS = [
    {"q_id": "q_c12_1", "type": "single_choice", "content": "结构体指针 p 访问成员的正确方式是？", "options": [{"id": "A", "text": "p.name"}, {"id": "B", "text": "p->name"}, {"id": "C", "text": "p::name"}, {"id": "D", "text": "p-name"}], "correct_answer": "B", "explanation": "结构体指针使用 -> 运算符访问成员，如 p->name。变量使用 . 运算符。"},
    {"q_id": "q_c12_2", "type": "single_choice", "content": "联合体 union 的所有成员？", "options": [{"id": "A", "text": "各自占有独立的内存"}, {"id": "B", "text": "共享同一块内存"}, {"id": "C", "text": "按顺序排列在内存中"}, {"id": "D", "text": "大小相加"}], "correct_answer": "B", "explanation": "联合体的所有成员共享同一块内存空间，同一时间只有一个成员有效。"},
    {"q_id": "q_c12_3", "type": "single_choice", "content": "以下关于 typedef 的说法，正确的是？", "options": [{"id": "A", "text": "创建新的数据类型"}, {"id": "B", "text": "为已有类型创建别名"}, {"id": "C", "text": "定义宏常量"}, {"id": "D", "text": "声明变量"}], "correct_answer": "B", "explanation": "typedef 用于为已有的数据类型创建一个新的名字（别名），不会创建新类型。"},
]

KP_C12_MM = {"root": "结构体与联合体", "children": [{"name": "结构体定义"}, {"name": "typedef"}, {"name": "成员访问"}, {"name": "结构体数组"}, {"name": "嵌套结构体"}, {"name": "联合体"}]}


KP_C13_DOC = """# 文件操作

## 13.1 文件指针

C语言通过 `FILE*` 类型的指针来操作文件。

```c
FILE *fp;  // 文件指针
```

## 13.2 打开与关闭文件

```c
FILE *fp = fopen("data.txt", "r");  // 以只读方式打开
if (fp == NULL) {
    printf("打开文件失败\\n");
    return 1;
}
// ... 读写操作
fclose(fp);  // 关闭文件
```

### 打开模式

| 模式 | 含义 |
|-----|------|
| `"r"` | 只读，文件必须存在 |
| `"w"` | 只写，文件不存在则创建，存在则清空 |
| `"a"` | 追加，文件不存在则创建 |
| `"r+"` | 读写，文件必须存在 |
| `"w+"` | 读写，不存在则创建，存在则清空 |
| `"a+"` | 读追加，不存在则创建 |
| `"rb"`, `"wb"` | 二进制模式 |

## 13.3 文本文件读写

### 字符读写
```c
char ch;
ch = fgetc(fp);        // 读一个字符
fputc(ch, fp);         // 写一个字符
```

### 字符串读写
```c
char buffer[100];
fgets(buffer, 100, fp);   // 读一行
fputs("Hello\\n", fp);    // 写字符串
```

### 格式化读写
```c
fprintf(fp, "%s %d\\n", "张三", 85);  // 格式化写入
fscanf(fp, "%s %d", name, &score);   // 格式化读取
```

## 13.4 二进制文件读写

```c
// 写入结构体数组
Student students[3] = {...};
fwrite(students, sizeof(Student), 3, fp);

// 读取
Student read_stu[3];
fread(read_stu, sizeof(Student), 3, fp);
```

## 13.5 文件定位

```c
fseek(fp, 0, SEEK_SET);  // 定位到文件开头
fseek(fp, 0, SEEK_END);  // 定位到文件末尾
long size = ftell(fp);   // 获取当前位置（可用来计算文件大小）
rewind(fp);              // 回到文件开头
```
"""

KP_C13_CODE = '''#include <stdio.h>
#include <stdlib.h>

typedef struct {
    char name[50];
    int age;
    float score;
} Student;

int main() {
    // 写入文本文件
    FILE *fp = fopen("students.txt", "w");
    if (fp == NULL) {
        printf("无法创建文件\\n");
        return 1;
    }

    fprintf(fp, "张三 20 85.5\\n");
    fprintf(fp, "李四 21 92.0\\n");
    fprintf(fp, "王五 19 78.5\\n");
    fclose(fp);
    printf("文本文件写入完成\\n");

    // 读取文本文件
    fp = fopen("students.txt", "r");
    printf("\\n读取文本文件:\\n");
    char line[100];
    while (fgets(line, sizeof(line), fp) != NULL) {
        printf("%s", line);
    }
    fclose(fp);

    // 二进制文件读写
    Student students[3] = {
        {"张三", 20, 85.5},
        {"李四", 21, 92.0},
        {"王五", 19, 78.5}
    };

    fp = fopen("students.dat", "wb");
    fwrite(students, sizeof(Student), 3, fp);
    fclose(fp);
    printf("\\n二进制文件写入完成\\n");

    // 读取二进制文件
    Student readStu[3];
    fp = fopen("students.dat", "rb");
    fread(readStu, sizeof(Student), 3, fp);
    printf("\\n读取二进制文件:\\n");
    for (int i = 0; i < 3; i++) {
        printf("%s %d %.1f\\n", readStu[i].name, readStu[i].age, readStu[i].score);
    }
    fclose(fp);

    return 0;
}'''

KP_C13_QS = [
    {"q_id": "q_c13_1", "type": "single_choice", "content": "fopen(\"test.txt\", \"w\") 中 \"w\" 模式的特点是？", "options": [{"id": "A", "text": "只读打开"}, {"id": "B", "text": "追加写入"}, {"id": "C", "text": "只写打开，存在则清空"}, {"id": "D", "text": "读写打开"}], "correct_answer": "C", "explanation": "\"w\" 模式以只写方式打开，如果文件已存在，其内容会被清空。"},
    {"q_id": "q_c13_2", "type": "single_choice", "content": "fread(buffer, size, count, fp) 中各参数的含义是？", "options": [{"id": "A", "text": "读取count个size大小的数据块到buffer"}, {"id": "B", "text": "读取size个count大小的数据块到buffer"}, {"id": "C", "text": "读取buffer到fp"}, {"id": "D", "text": "读取size字节到buffer"}], "correct_answer": "A", "explanation": "fread 从文件中读取 count 个大小为 size 的数据块，存入 buffer。"},
    {"q_id": "q_c13_3", "type": "single_choice", "content": "将文件指针移到文件开头的函数是？", "options": [{"id": "A", "text": "fseek(fp, 0, SEEK_END)"}, {"id": "B", "text": "fseek(fp, 0, SEEK_SET)"}, {"id": "C", "text": "ftell(fp)"}, {"id": "D", "text": "fclose(fp)"}], "correct_answer": "B", "explanation": "fseek(fp, 0, SEEK_SET) 将文件指针定位到文件开头。SEEK_SET 表示从文件起始位置计算偏移量。"},
]

KP_C13_MM = {"root": "文件操作", "children": [{"name": "fopen/fclose"}, {"name": "打开模式"}, {"name": "文本读写"}, {"name": "二进制读写"}, {"name": "fseek定位"}]}


KP_C14_DOC = """# 动态内存管理

## 14.1 为什么需要动态内存

- 数组大小必须在编译时确定，不够灵活
- 动态内存允许在运行时根据需要申请内存
- 可以创建可变大小的数据结构（如链表、动态数组）

## 14.2 malloc 与 free

```c
#include <stdlib.h>

// 申请能存放5个int的内存
int *arr = (int *)malloc(5 * sizeof(int));
if (arr == NULL) {
    printf("内存分配失败\\n");
    return 1;
}

// 使用内存...
for (int i = 0; i < 5; i++) {
    arr[i] = i + 1;
}

// 释放内存
free(arr);
arr = NULL;  // 避免野指针
```

### 相关函数

| 函数 | 功能 |
|-----|------|
| `malloc(n)` | 申请 n 字节内存，不初始化 |
| `calloc(n, size)` | 申请 n * size 字节内存，初始化为0 |
| `realloc(p, n)` | 重新调整已分配内存的大小 |
| `free(p)` | 释放 malloc/calloc/realloc 申请的内存 |

## 14.3 calloc 与 malloc 的区别

```c
int *a = (int *)malloc(5 * sizeof(int));     // 内容不确定
int *b = (int *)calloc(5, sizeof(int));      // 内容全为0
```

## 14.4 realloc 调整内存大小

```c
int *arr = (int *)malloc(5 * sizeof(int));
// ... 后续发现5个不够
arr = (int *)realloc(arr, 10 * sizeof(int));
// 现在可以存放10个int
```

## 14.5 内存泄漏与野指针

### 内存泄漏
申请了内存但没有释放，导致可用内存越来越少。

```c
void leak() {
    int *p = (int *)malloc(100);
    // 没有 free(p) —— 内存泄漏！
}
```

### 常见错误
1. **使用已释放的内存**（悬空指针）
2. **重复释放同一块内存**
3. **释放非动态分配的内存**
4. **malloc 后没有检查返回值是否为 NULL**

## 14.6 动态数组示例

```c
#include <stdio.h>
#include <stdlib.h>

int main() {
    int n;
    printf("请输入元素个数: ");
    scanf("%d", &n);

    int *arr = (int *)calloc(n, sizeof(int));

    printf("请输入 %d 个整数:\\n", n);
    for (int i = 0; i < n; i++) {
        scanf("%d", &arr[i]);
    }

    printf("输入的数据: ");
    for (int i = 0; i < n; i++) {
        printf("%d ", arr[i]);
    }
    printf("\\n");

    free(arr);
    return 0;
}
```

> **黄金法则**：谁 malloc，谁 free；malloc 和 free 要成对出现。
"""

KP_C14_CODE = '''#include <stdio.h>
#include <stdlib.h>

int main() {
    // malloc 动态分配数组
    int n = 5;
    int *arr = (int *)malloc(n * sizeof(int));

    if (arr == NULL) {
        printf("内存分配失败\\n");
        return 1;
    }

    printf("malloc分配的数组:\\n");
    for (int i = 0; i < n; i++) {
        arr[i] = (i + 1) * 10;
        printf("arr[%d] = %d\\n", i, arr[i]);
    }

    // realloc 扩展数组
    int *newArr = (int *)realloc(arr, 8 * sizeof(int));
    if (newArr != NULL) {
        arr = newArr;
        printf("\\nrealloc扩展到8个元素:\\n");
        for (int i = 5; i < 8; i++) {
            arr[i] = (i + 1) * 10;
        }
        for (int i = 0; i < 8; i++) {
            printf("arr[%d] = %d\\n", i, arr[i]);
        }
    }

    // calloc 分配并初始化
    int *zeroArr = (int *)calloc(5, sizeof(int));
    printf("\\ncalloc分配的数组(已初始化为0):\\n");
    for (int i = 0; i < 5; i++) {
        printf("zeroArr[%d] = %d\\n", i, zeroArr[i]);
    }

    // 释放内存
    free(arr);
    free(zeroArr);
    arr = NULL;
    zeroArr = NULL;

    printf("\\n内存已释放\\n");
    return 0;
}'''

KP_C14_QS = [
    {"q_id": "q_c14_1", "type": "single_choice", "content": "malloc 申请的内存使用完毕后应该用什么函数释放？", "options": [{"id": "A", "text": "delete"}, {"id": "B", "text": "free"}, {"id": "C", "text": "release"}, {"id": "D", "text": "clear"}], "correct_answer": "B", "explanation": "C语言中使用 free() 函数释放 malloc/calloc/realloc 动态分配的内存。"},
    {"q_id": "q_c14_2", "type": "single_choice", "content": "calloc(5, sizeof(int)) 与 malloc(5 * sizeof(int)) 的主要区别是？", "options": [{"id": "A", "text": "分配的内存大小不同"}, {"id": "B", "text": "calloc 会初始化内存为0"}, {"id": "C", "text": "malloc 更安全"}, {"id": "D", "text": "没有区别"}], "correct_answer": "B", "explanation": "calloc 在分配内存后会将所有字节初始化为0，而 malloc 分配的内存内容是未定义的。"},
    {"q_id": "q_c14_3", "type": "single_choice", "content": "以下哪种情况会导致内存泄漏？", "options": [{"id": "A", "text": "free 后立即将指针置为 NULL"}, {"id": "B", "text": "malloc 后没有调用 free"}, {"id": "C", "text": "使用 calloc 分配内存"}, {"id": "D", "text": "使用 static 变量"}], "correct_answer": "B", "explanation": "malloc/calloc/realloc 申请的内存如果不调用 free 释放，就会造成内存泄漏。"},
]

KP_C14_MM = {"root": "动态内存管理", "children": [{"name": "malloc"}, {"name": "calloc"}, {"name": "realloc"}, {"name": "free"}, {"name": "内存泄漏"}, {"name": "动态数组"}]}

# ---------- kp_c15: 预处理指令 ----------
KP_C15_DOC = """# 预处理指令

## 15.1 什么是预处理

C语言的预处理发生在编译之前，由预处理器完成。所有以 `#` 开头的行都是预处理指令。

## 15.2 文件包含 #include

`#include` 用于将头文件的内容插入到当前位置。

```c
#include <stdio.h>   // 系统头文件，在标准库目录查找
#include "myheader.h" // 用户头文件，先在当前目录查找
```

## 15.3 宏定义 #define

宏分为不带参数的宏和带参数的宏。

### 不带参数的宏
```c
#define PI 3.14159
#define MAX_SIZE 100
```

### 带参数的宏（宏函数）
```c
#define SQUARE(x) ((x) * (x))
#define MAX(a, b) ((a) > (b) ? (a) : (b))
```

> **注意**：宏展开只是简单的文本替换，务必多加括号避免优先级错误。

## 15.4 条件编译

条件编译让代码可以根据条件选择性编译。

```c
#ifdef DEBUG
    printf("Debug mode\\n");
#else
    printf("Release mode\\n");
#endif
```

常用指令：
- `#ifdef` / `#ifndef` —— 判断是否定义了某个宏
- `#if` / `#elif` / `#else` / `#endif` —— 根据表达式条件编译
- `#undef` —— 取消宏定义

## 15.5 预定义宏

C标准预定义了一些有用的宏：

| 宏 | 含义 |
|---|---|
| `__FILE__` | 当前源文件名 |
| `__LINE__` | 当前行号 |
| `__DATE__` | 编译日期 |
| `__TIME__` | 编译时间 |
| `__func__` | 当前函数名 |

> **学习建议**：善用条件编译可以实现跨平台代码和调试信息的灵活控制。
"""

KP_C15_CODE = '''#include <stdio.h>

#define PI 3.14159
#define SQUARE(x) ((x) * (x))
#define MAX(a, b) ((a) > (b) ? (a) : (b))

// 条件编译示例
#ifdef DEBUG
    #define LOG(msg) printf("[DEBUG] %s:%d %s\\n", __FILE__, __LINE__, msg)
#else
    #define LOG(msg) // 空实现
#endif

int main() {
    printf("编译日期: %s %s\\n", __DATE__, __TIME__);
    printf("PI = %f\\n", PI);
    printf("SQUARE(5) = %d\\n", SQUARE(5));
    printf("MAX(3, 7) = %d\\n", MAX(3, 7));
    LOG("程序启动");
    return 0;
}'''

KP_C15_QS = [
    {"q_id": "q_c15_1", "type": "single_choice", "content": "以下哪个预处理指令用于包含头文件？", "options": [{"id": "A", "text": "#define"}, {"id": "B", "text": "#include"}, {"id": "C", "text": "#ifdef"}, {"id": "D", "text": "#pragma"}], "correct_answer": "B", "explanation": "#include 用于将指定头文件的内容插入到当前源文件中。"},
    {"q_id": "q_c15_2", "type": "single_choice", "content": "宏定义 #define SQUARE(x) x * x 调用 SQUARE(2+3) 的结果是多少？", "options": [{"id": "A", "text": "25"}, {"id": "B", "text": "11"}, {"id": "C", "text": "13"}, {"id": "D", "text": "编译错误"}], "correct_answer": "B", "explanation": "不加括号时，宏展开为 2+3*2+3 = 2+6+3 = 11，因此宏参数必须加括号。"},
    {"q_id": "q_c15_3", "type": "single_choice", "content": "以下哪个预定义宏表示当前源文件名？", "options": [{"id": "A", "text": "__LINE__"}, {"id": "B", "text": "__FILE__"}, {"id": "C", "text": "__DATE__"}, {"id": "D", "text": "__TIME__"}], "correct_answer": "B", "explanation": "__FILE__ 是编译器预定义的宏，表示当前正在编译的源文件名称。"},
]

KP_C15_MM = {"root": "预处理指令", "children": [{"name": "#include"}, {"name": "#define"}, {"name": "宏函数"}, {"name": "条件编译"}, {"name": "预定义宏"}]}

# ---------- kp_c16: 位运算 ----------
KP_C16_DOC = """# 位运算

## 16.1 位运算概述

位运算直接对整数的二进制位进行操作，是C语言接近底层的重要特性，常用于嵌入式、图像处理、权限控制等领域。

## 16.2 位运算符

| 运算符 | 名称 | 示例 | 说明 |
|---|---|---|---|
| `&` | 按位与 | `a & b` | 两位都为1时结果为1 |
| `\|` | 按位或 | `a \| b` | 两位至少一个为1时结果为1 |
| `^` | 按位异或 | `a ^ b` | 两位不同时结果为1 |
| `~` | 按位取反 | `~a` | 0变1，1变0 |
| `<<` | 左移 | `a << 2` | 各位左移，右侧补0 |
| `>>` | 右移 | `a >> 2` | 各位右移，左侧补符号位或0 |

## 16.3 常见应用

### 掩码操作（清零/置位）
```c
int flags = 0b1010;
flags = flags | 0b0100;  // 置第2位为1
flags = flags & ~0b0010; // 清第1位为0
```

### 判断奇偶
```c
if (n & 1) {
    printf("奇数\\n");
} else {
    printf("偶数\\n");
}
```

### 交换两个数（不用临时变量）
```c
a = a ^ b;
b = a ^ b;
a = a ^ b;
```

## 16.4 注意事项

- 位运算只适用于整数类型
- 右移时，有符号数的算术右移与逻辑右移结果可能不同
- 避免移位超过数据类型的位数

> **学习建议**：位运算在系统编程和算法优化中非常重要，建议多练习掩码操作。
"""

KP_C16_CODE = '''#include <stdio.h>

int main() {
    unsigned char a = 0b1010; // 10
    unsigned char b = 0b1100; // 12

    printf("a & b  = %d\\n", a & b);   // 8
    printf("a | b  = %d\\n", a | b);   // 14
    printf("a ^ b  = %d\\n", a ^ b);   // 6
    printf("~a     = %d\\n", ~a);      // 按位取反
    printf("a << 1 = %d\\n", a << 1); // 20
    printf("a >> 1 = %d\\n", a >> 1); // 5

    // 判断奇偶
    int n = 7;
    printf("%d 是%s\\n", n, (n & 1) ? "奇数" : "偶数");

    // 交换两个数
    int x = 5, y = 9;
    printf("交换前: x=%d, y=%d\\n", x, y);
    x = x ^ y;
    y = x ^ y;
    x = x ^ y;
    printf("交换后: x=%d, y=%d\\n", x, y);

    return 0;
}'''

KP_C16_QS = [
    {"q_id": "q_c16_1", "type": "single_choice", "content": "以下哪个运算符表示按位异或？", "options": [{"id": "A", "text": "&"}, {"id": "B", "text": "|"}, {"id": "C", "text": "^"}, {"id": "D", "text": "~"}], "correct_answer": "C", "explanation": "^ 是按位异或运算符，当两位不同时结果为1。"},
    {"q_id": "q_c16_2", "type": "single_choice", "content": "表达式 5 << 2 的结果是多少？", "options": [{"id": "A", "text": "10"}, {"id": "B", "text": "20"}, {"id": "C", "text": "7"}, {"id": "D", "text": "1"}], "correct_answer": "B", "explanation": "5 的二进制为 101，左移2位后为 10100，即十进制的 20。"},
    {"q_id": "q_c16_3", "type": "single_choice", "content": "利用位运算判断整数 n 是否为奇数，正确的表达式是？", "options": [{"id": "A", "text": "n | 1"}, {"id": "B", "text": "n & 1"}, {"id": "C", "text": "n ^ 1"}, {"id": "D", "text": "n ~ 1"}], "correct_answer": "B", "explanation": "n & 1 用于判断最低位是否为1，若为1则是奇数。"},
]

KP_C16_MM = {"root": "位运算", "children": [{"name": "按位与"}, {"name": "按位或"}, {"name": "按位异或"}, {"name": "取反与移位"}, {"name": "掩码操作"}]}


# ---------- 知识点（DAG）----------
kps = [
    KnowledgePointModel(
        kp_id="kp_c01", name="C语言概述与开发环境", subject="基础入门", difficulty=0.2,
        prerequisites=[], description="C语言的历史、特点、开发环境搭建与第一个程序",
        tags=["入门", "环境搭建"],
        document=KP_C01_DOC, code_example=KP_C01_CODE, questions=KP_C01_QS, mindmap=KP_C01_MM,
    ),
    KnowledgePointModel(
        kp_id="kp_c02", name="数据类型与变量", subject="基础入门", difficulty=0.25,
        prerequisites=[], description="基本数据类型、变量声明、命名规则、常量、类型转换",
        tags=["基础", "变量"],
        document=KP_C02_DOC, code_example=KP_C02_CODE, questions=KP_C02_QS, mindmap=KP_C02_MM,
    ),
    KnowledgePointModel(
        kp_id="kp_c03", name="运算符与表达式", subject="基础语法", difficulty=0.3,
        prerequisites=["kp_c02"], description="算术、关系、逻辑、赋值运算符及优先级",
        tags=["运算符", "表达式"],
        document=KP_C03_DOC, code_example=KP_C03_CODE, questions=KP_C03_QS, mindmap=KP_C03_MM,
    ),
    KnowledgePointModel(
        kp_id="kp_c04", name="输入输出与顺序结构", subject="基础语法", difficulty=0.3,
        prerequisites=["kp_c02"], description="printf、scanf格式控制与顺序结构程序设计",
        tags=["IO", "顺序结构"],
        document=KP_C04_DOC, code_example=KP_C04_CODE, questions=KP_C04_QS, mindmap=KP_C04_MM,
    ),
    KnowledgePointModel(
        kp_id="kp_c05", name="选择结构", subject="控制结构", difficulty=0.35,
        prerequisites=["kp_c03", "kp_c04"], description="if、if-else、switch语句与多分支程序设计",
        tags=["if", "switch", "分支"],
        document=KP_C05_DOC, code_example=KP_C05_CODE, questions=KP_C05_QS, mindmap=KP_C05_MM,
    ),
    KnowledgePointModel(
        kp_id="kp_c06", name="循环结构", subject="控制结构", difficulty=0.4,
        prerequisites=["kp_c03", "kp_c04"], description="for、while、do-while循环与嵌套循环",
        tags=["for", "while", "循环"],
        document=KP_C06_DOC, code_example=KP_C06_CODE, questions=KP_C06_QS, mindmap=KP_C06_MM,
    ),
    KnowledgePointModel(
        kp_id="kp_c07", name="数组", subject="数组与字符串", difficulty=0.45,
        prerequisites=["kp_c06"], description="一维数组、二维数组、数组遍历与常见算法",
        tags=["数组", "排序"],
        document=KP_C07_DOC, code_example=KP_C07_CODE, questions=KP_C07_QS, mindmap=KP_C07_MM,
    ),
    KnowledgePointModel(
        kp_id="kp_c08", name="字符串", subject="数组与字符串", difficulty=0.45,
        prerequisites=["kp_c07"], description="字符数组、字符串函数、字符串处理",
        tags=["字符串", "string.h"],
        document=KP_C08_DOC, code_example=KP_C08_CODE, questions=KP_C08_QS, mindmap=KP_C08_MM,
    ),
    KnowledgePointModel(
        kp_id="kp_c09", name="函数与递归", subject="函数", difficulty=0.5,
        prerequisites=["kp_c06"], description="函数定义、参数传递、递归算法、变量作用域",
        tags=["函数", "递归"],
        document=KP_C09_DOC, code_example=KP_C09_CODE, questions=KP_C09_QS, mindmap=KP_C09_MM,
    ),
    KnowledgePointModel(
        kp_id="kp_c10", name="指针基础", subject="指针", difficulty=0.55,
        prerequisites=["kp_c02", "kp_c09"], description="指针概念、取地址与解引用、指针运算",
        tags=["指针", "地址"],
        document=KP_C10_DOC, code_example=KP_C10_CODE, questions=KP_C10_QS, mindmap=KP_C10_MM,
    ),
    KnowledgePointModel(
        kp_id="kp_c11", name="指针与数组", subject="指针", difficulty=0.6,
        prerequisites=["kp_c10", "kp_c07"], description="数组名与指针关系、指针数组、多级指针",
        tags=["指针数组", "多级指针"],
        document=KP_C11_DOC, code_example=KP_C11_CODE, questions=KP_C11_QS, mindmap=KP_C11_MM,
    ),
    KnowledgePointModel(
        kp_id="kp_c12", name="结构体与联合体", subject="结构体与文件", difficulty=0.5,
        prerequisites=["kp_c02", "kp_c07"], description="struct定义、typedef、结构体数组与嵌套、union",
        tags=["结构体", "联合体"],
        document=KP_C12_DOC, code_example=KP_C12_CODE, questions=KP_C12_QS, mindmap=KP_C12_MM,
    ),
    KnowledgePointModel(
        kp_id="kp_c13", name="文件操作", subject="结构体与文件", difficulty=0.55,
        prerequisites=["kp_c12"], description="文件打开关闭、文本与二进制读写、文件定位",
        tags=["文件", "fread", "fwrite"],
        document=KP_C13_DOC, code_example=KP_C13_CODE, questions=KP_C13_QS, mindmap=KP_C13_MM,
    ),
    KnowledgePointModel(
        kp_id="kp_c14", name="动态内存管理", subject="高级主题", difficulty=0.6,
        prerequisites=["kp_c10"], description="malloc、calloc、realloc、free与内存泄漏防范",
        tags=["动态内存", "malloc"],
        document=KP_C14_DOC, code_example=KP_C14_CODE, questions=KP_C14_QS, mindmap=KP_C14_MM,
    ),
    KnowledgePointModel(
        kp_id="kp_c15", name="预处理指令", subject="高级主题", difficulty=0.4,
        prerequisites=["kp_c01"], description="宏定义、条件编译、文件包含与预处理原理",
        tags=["预处理", "宏定义"],
        document=KP_C15_DOC, code_example=KP_C15_CODE, questions=KP_C15_QS, mindmap=KP_C15_MM,
    ),
    KnowledgePointModel(
        kp_id="kp_c16", name="位运算", subject="高级主题", difficulty=0.55,
        prerequisites=["kp_c03", "kp_c06"], description="位运算符、位掩码、位域与底层数据操作",
        tags=["位运算", "位掩码"],
        document=KP_C16_DOC, code_example=KP_C16_CODE, questions=KP_C16_QS, mindmap=KP_C16_MM,
    ),
]
db.add_all(kps)
db.commit()


# ---------- 学习记录 ----------
actions = ["watch", "read", "practice", "review"]
records = []
for i in range(40):
    sid = STUDENT_ID if i % 4 == 0 else (STUDENT2 if i % 4 == 1 else (STUDENT3 if i % 4 == 2 else TEST_USER))
    kp = kps[i % len(kps)].kp_id
    records.append(LearningRecordModel(
        record_id=f"lr_{i:03d}",
        student_id=sid,
        kp_id=kp,
        action=actions[i % len(actions)],
        duration=(i + 1) * 120,
        progress=min(1.0, (i + 1) * 0.06),
        score=60 + (i % 5) * 8,
        meta={"device": "pc"},
    ))
db.add_all(records)
db.commit()

# ---------- 测验结果 ----------
quizzes = []
for i in range(28):
    sid = STUDENT_ID if i % 4 == 0 else (STUDENT2 if i % 4 == 1 else (STUDENT3 if i % 4 == 2 else TEST_USER))
    kp = kps[i % len(kps)].kp_id
    correct = 3 + (i % 3)
    total = 5
    quizzes.append(QuizResultModel(
        quiz_id=f"qz_{i:03d}",
        student_id=sid,
        kp_id=kp,
        total_questions=total,
        correct_count=correct,
        score=correct / total * 100,
        weak_tags=["概念混淆"] if i % 4 == 0 else [],
        time_spent=300 + i * 60,
        answers=[{"q_id": f"q_{j}", "correct": j < correct} for j in range(total)],
    ))
db.add_all(quizzes)
db.commit()

# ---------- 趋势数据 ----------
trends = []
base_date = datetime.now() - timedelta(days=14)
for i in range(14):
    d = (base_date + timedelta(days=i)).strftime("%Y-%m-%d")
    trends.append(TrendDataModel(
        student_id=STUDENT_ID,
        date=d,
        mastery_trend=0.5 + i * 0.02,
        speed_ratio=0.6 + (i % 3) * 0.05,
        time_efficiency=0.7 - (i % 5) * 0.02,
        weakness_priority=0.4 + (i % 2) * 0.1,
        stability=0.8 - (i % 7) * 0.03,
        trend_factor=-0.2 + i * 0.03,
        trend_state="growth" if i > 7 else "stable",
        predicted_mastery_3d=0.5 + i * 0.025,
        intervention="建议加强薄弱点练习" if i % 3 == 0 else None,
    ))
    trends.append(TrendDataModel(
        student_id=TEST_USER,
        date=d,
        mastery_trend=0.45 + i * 0.018,
        speed_ratio=0.55 + (i % 4) * 0.04,
        time_efficiency=0.65 - (i % 6) * 0.015,
        weakness_priority=0.5 + (i % 3) * 0.08,
        stability=0.75 - (i % 5) * 0.02,
        trend_factor=-0.15 + i * 0.025,
        trend_state="growth" if i > 6 else "stable",
        predicted_mastery_3d=0.45 + i * 0.022,
        intervention="建议复习指针与内存" if i % 4 == 0 else None,
    ))
db.add_all(trends)
db.commit()

# ---------- 游戏化积分 ----------
points = [
    PointsModel(student_id=STUDENT_ID, total_points=1250, daily_points=120, weekly_points=450),
    PointsModel(student_id=STUDENT2, total_points=2100, daily_points=200, weekly_points=800),
    PointsModel(student_id=STUDENT3, total_points=350, daily_points=50, weekly_points=150),
    PointsModel(student_id=TEST_USER, total_points=880, daily_points=90, weekly_points=320),
]
db.add_all(points)
db.commit()

# ---------- 成就 ----------
achievements = [
    AchievementModel(student_id=STUDENT_ID, achievement_id="ach_001", name="初出茅庐", description="完成首个学习模块", icon="trophy"),
    AchievementModel(student_id=STUDENT_ID, achievement_id="ach_002", name="持之以恒", description="连续打卡7天", icon="fire"),
    AchievementModel(student_id=STUDENT_ID, achievement_id="ach_003", name="代码高手", description="完成10次代码练习", icon="code"),
    AchievementModel(student_id=STUDENT2, achievement_id="ach_001", name="初出茅庐", description="完成首个学习模块", icon="trophy"),
    AchievementModel(student_id=STUDENT2, achievement_id="ach_004", name="学霸", description="测验平均分超过90", icon="star"),
    AchievementModel(student_id=STUDENT3, achievement_id="ach_001", name="初出茅庐", description="完成首个学习模块", icon="trophy"),
    AchievementModel(student_id=TEST_USER, achievement_id="ach_001", name="初出茅庐", description="完成首个学习模块", icon="trophy"),
    AchievementModel(student_id=TEST_USER, achievement_id="ach_005", name="C语言学徒", description="完成C语言概述学习", icon="code"),
]
db.add_all(achievements)
db.commit()

# ---------- 任务 ----------
tasks = [
    TaskModel(student_id=STUDENT_ID, task_id="t_001", title="阅读C语言概述", description="完成第一章图文讲义", task_type="daily", reward_points=50, progress=1.0, completed=True, completed_at=datetime.now()),
    TaskModel(student_id=STUDENT_ID, task_id="t_002", title="完成数据类型练习", description="完成3道相关练习题", task_type="daily", reward_points=30, progress=0.6, completed=False),
    TaskModel(student_id=STUDENT_ID, task_id="t_003", title="本周学习15小时", description="累计学习时长目标", task_type="weekly", reward_points=100, progress=0.4, completed=False),
    TaskModel(student_id=STUDENT2, task_id="t_004", title="完成指针练习", description="指针与内存专项训练", task_type="weekly", reward_points=150, progress=0.8, completed=False),
    TaskModel(student_id=STUDENT2, task_id="t_005", title="算法竞赛", description="参加一场线上算法赛", task_type="challenge", reward_points=300, progress=0.0, completed=False),
    TaskModel(student_id=STUDENT3, task_id="t_006", title="C语言基础练习", description="完成C语言入门教程", task_type="daily", reward_points=20, progress=0.3, completed=False),
    TaskModel(student_id=TEST_USER, task_id="t_007", title="阅读C语言概述", description="完成C语言概述章节", task_type="daily", reward_points=30, progress=1.0, completed=True, completed_at=datetime.now()),
    TaskModel(student_id=TEST_USER, task_id="t_008", title="完成指针练习", description="完成3道指针相关习题", task_type="daily", reward_points=40, progress=0.5, completed=False),
    TaskModel(student_id=TEST_USER, task_id="t_009", title="本周学习10小时", description="累计学习时长目标", task_type="weekly", reward_points=80, progress=0.6, completed=False),
]
db.add_all(tasks)
db.commit()

# ---------- 排行榜 ----------
leaderboard = [
    LeaderboardModel(student_id=STUDENT2, period="weekly", score=2100, rank=1),
    LeaderboardModel(student_id=STUDENT_ID, period="weekly", score=1250, rank=2),
    LeaderboardModel(student_id=TEST_USER, period="weekly", score=880, rank=3),
    LeaderboardModel(student_id=STUDENT3, period="weekly", score=350, rank=4),
    LeaderboardModel(student_id=STUDENT2, period="monthly", score=8500, rank=1),
    LeaderboardModel(student_id=STUDENT_ID, period="monthly", score=5200, rank=2),
    LeaderboardModel(student_id=TEST_USER, period="monthly", score=3200, rank=3),
    LeaderboardModel(student_id=STUDENT3, period="monthly", score=1200, rank=4),
]
db.add_all(leaderboard)
db.commit()

# ---------- 学习日志 ----------
logs = []
for i in range(7):
    d = (datetime.now() - timedelta(days=6 - i)).strftime("%Y-%m-%d")
    logs.append(LearningLogModel(
        log_id=f"log_{STUDENT_ID}_{d}",
        student_id=STUDENT_ID,
        date=d,
        total_duration=3600 + i * 300,
        kp_count=2 + i,
        quiz_count=1 + (i % 2),
        avg_score=70 + i * 2,
        mistakes=["概念混淆"] if i % 3 == 0 else [],
        path_progress=0.1 + i * 0.05,
        completed_tasks=[f"task_{j}" for j in range(i)],
        timeline=[{"time": "10:00", "action": "read", "kp_id": "kp_c01", "duration": 1800}],
    ))
    logs.append(LearningLogModel(
        log_id=f"log_{TEST_USER}_{d}",
        student_id=TEST_USER,
        date=d,
        total_duration=2400 + i * 200,
        kp_count=1 + (i % 3),
        quiz_count=1 if i % 2 == 0 else 0,
        avg_score=65 + i * 3,
        mistakes=["指针错误"] if i % 4 == 0 else [],
        path_progress=0.15 + i * 0.04,
        completed_tasks=[f"task_{j}" for j in range(max(0, i - 1))],
        timeline=[{"time": "14:00", "action": "practice", "kp_id": "kp_c02", "duration": 1200}],
    ))
db.add_all(logs)
db.commit()

# ---------- 反思记录 ----------
reflections = [
    ReflectionModel(reflection_id=f"ref_{STUDENT_ID}_2026-04-14", student_id=STUDENT_ID, date="2026-04-14",
                    content="今天复习了指针的概念，对解引用运算符*的理解更深入了，但多级指针还是有点晕。",
                    mood="neutral", tags=["指针", "学习感悟"], ai_feedback="建议从简单的单级指针开始，逐步过渡到二级指针。"),
    ReflectionModel(reflection_id=f"ref_{STUDENT_ID}_2026-04-15", student_id=STUDENT_ID, date="2026-04-15",
                    content="完成了结构体的学习，发现 typedef 真的很方便，代码可读性提高了很多。",
                    mood="excited", tags=["结构体", "进步"], ai_feedback="可以尝试用结构体实现一个简单的学生管理系统。"),
    ReflectionModel(reflection_id=f"ref_{STUDENT_ID}_2026-04-16", student_id=STUDENT_ID, date="2026-04-16",
                    content="动态内存管理好难，malloc 和 free 总是配对出错，漏掉了 free 导致内存泄漏。",
                    mood="frustrated", tags=["内存管理", "困难"], ai_feedback="养成良好的习惯：malloc 后立即写下对应的 free，或者使用 RAII 思想。"),
    ReflectionModel(reflection_id=f"ref_{STUDENT2}_2026-04-17", student_id=STUDENT2, date="2026-04-17",
                    content="今天用文件操作实现了一个简单的日志系统，fwrite 和 fread 真的很好用！",
                    mood="happy", tags=["文件操作", "项目实战"], ai_feedback="可以尝试加入错误处理和文件加密功能。"),
    ReflectionModel(reflection_id=f"ref_{TEST_USER}_2026-04-20", student_id=TEST_USER, date="2026-04-20",
                    content="今天学习了C语言的数据类型，对int和float的精度区别有了更深的理解。",
                    mood="happy", tags=["C语言", "基础"], ai_feedback="可以尝试编写几个类型转换的小程序加深理解。"),
    ReflectionModel(reflection_id=f"ref_{TEST_USER}_2026-04-21", student_id=TEST_USER, date="2026-04-21",
                    content="指针好难啊，今天花了两个小时才搞明白指针和数组的关系。",
                    mood="neutral", tags=["C语言", "指针"], ai_feedback="指针是C语言的核心，建议多画图辅助理解内存布局。"),
]
db.add_all(reflections)
db.commit()

db.close()
print("[DONE] Seed data inserted successfully!")
print(f"   users: 4")
print(f"   profiles: 4")
print(f"   knowledge_points: {len(kps)}")
print(f"   learning_records: {len(records)}")
print(f"   quiz_results: {len(quizzes)}")
print(f"   trend_data: {len(trends)}")
print(f"   points: 4")
print(f"   achievements: {len(achievements)}")
print(f"   tasks: {len(tasks)}")
print(f"   leaderboard: {len(leaderboard)}")
print(f"   learning_logs: {len(logs)}")
print(f"   reflections: {len(reflections)}")
