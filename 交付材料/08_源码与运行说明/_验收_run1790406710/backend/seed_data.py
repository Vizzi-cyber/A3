"""
数据库测试数据填充脚本 —— C语言程序设计教材体系
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
import bcrypt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.database import Base
from app.models.user import UserModel

if not settings.DEBUG:
    raise RuntimeError("seed_data.py 只能在 DEBUG 模式下运行，生产环境禁止执行！")
from app.models.student import StudentProfileModel
from app.models.knowledge import KnowledgePointModel, LearningRecordModel, QuizResultModel
from app.models.trend import TrendDataModel
from app.models.gamification import PointsModel, AchievementModel, TaskModel, LeaderboardModel
from app.models.log_reflection import LearningLogModel, ReflectionModel


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


engine = create_engine("sqlite:///./ai_learning_v2.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

db = SessionLocal()

STUDENT_ID = "student_001"
STUDENT2 = "student_002"
STUDENT3 = "student_003"
TEST_USER = "test_001"
TEACHER = "teacher_001"
TOP_STUDENT = "student_004"
BEGINNER = "student_005"
COMPETITOR = "student_006"
STEADY = "student_007"

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
              hashed_password=_hash_password("123456"), is_active=True, role="student"),
    UserModel(student_id=STUDENT2, username="李四", email="lisi@example.com",
              hashed_password=_hash_password("123456"), is_active=True, role="student"),
    UserModel(student_id=STUDENT3, username="王五", email="wangwu@example.com",
              hashed_password=_hash_password("123456"), is_active=True, role="student"),
    UserModel(student_id=TEST_USER, username="测试用户", email="test@example.com",
              hashed_password=_hash_password("123456"), is_active=True, role="student"),
    UserModel(student_id=TEACHER, username="赵老师", email="teacher@example.com",
              hashed_password=_hash_password("123456"), is_active=True, role="teacher"),
    UserModel(student_id=TOP_STUDENT, username="陈学霸", email="chenxueba@example.com",
              hashed_password=_hash_password("123456"), is_active=True, role="student"),
    UserModel(student_id=BEGINNER, username="刘小白", email="liuxiaobai@example.com",
              hashed_password=_hash_password("123456"), is_active=True, role="student"),
    UserModel(student_id=COMPETITOR, username="孙竞赛", email="sunjingsai@example.com",
              hashed_password=_hash_password("123456"), is_active=True, role="student"),
    UserModel(student_id=STEADY, username="周稳步", email="zhouwenbu@example.com",
              hashed_password=_hash_password("123456"), is_active=True, role="student"),
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
    # teacher_001 赵老师 — 教师账号，全面掌握
    StudentProfileModel(
        student_id=TEACHER,
        knowledge_base={"overall_score": 98, "C语言概述": 0.99, "数据类型与变量": 0.98, "控制结构": 0.97, "指针": 0.96, "结构体": 0.95, "文件操作": 0.94},
        cognitive_style={"primary": "reading", "scores": {"visual": 0.8, "auditory": 0.9, "reading": 0.95, "kinesthetic": 0.7}},
        weak_areas=[],
        error_patterns=[],
        learning_goals=[{"goal": "监督学生学习进度并提供指导", "deadline": "2026-12-01"}],
        interest_areas=["教学研究", "课程设计", "学生评估"],
        learning_tempo={"study_speed": "fast", "optimal_session_duration": 90, "weekly_study_capacity": 30, "focus_score": 95},
        practical_preferences={"overall_score": 98, "coding_proficiency": {"c": 0.98, "python": 0.9, "java": 0.85}, "preferred_practice_types": ["项目实战", "教学案例"]},
    ),
    # student_004 陈学霸 — 高水平快速学习者
    StudentProfileModel(
        student_id=TOP_STUDENT,
        knowledge_base={"overall_score": 95, "C语言概述": 0.98, "数据类型与变量": 0.95, "控制结构": 0.93, "指针": 0.9, "结构体": 0.88, "文件操作": 0.85},
        cognitive_style={"primary": "reading", "scores": {"visual": 0.7, "auditory": 0.5, "reading": 0.95, "kinesthetic": 0.6}},
        weak_areas=[],
        error_patterns=[],
        learning_goals=[{"goal": "精通C语言并参加程序设计竞赛", "deadline": "2026-05-01"}],
        interest_areas=["算法竞赛", "操作系统", "编译原理"],
        learning_tempo={"study_speed": "fast", "optimal_session_duration": 90, "weekly_study_capacity": 25, "focus_score": 95},
        practical_preferences={"overall_score": 96, "coding_proficiency": {"c": 0.95, "python": 0.9, "rust": 0.6}, "preferred_practice_types": ["算法竞赛", "项目实战"]},
    ),
    # student_005 刘小白 — 零基础挣扎初学者
    StudentProfileModel(
        student_id=BEGINNER,
        knowledge_base={"overall_score": 20, "C语言概述": 0.3, "数据类型与变量": 0.15, "控制结构": 0.05},
        cognitive_style={"primary": "kinesthetic", "scores": {"visual": 0.6, "auditory": 0.5, "reading": 0.3, "kinesthetic": 0.9}},
        weak_areas=["数学基础", "编程语法", "逻辑思维", "英语阅读"],
        error_patterns=[{"type": "语法错误", "desc": "分号括号经常遗漏"}, {"type": "逻辑错误", "desc": "if条件判断方向写反"}, {"type": "概念混淆", "desc": "变量和常量分不清"}],
        learning_goals=[{"goal": "能独立编写Hello World程序", "deadline": "2026-09-01"}],
        interest_areas=["游戏开发"],
        learning_tempo={"study_speed": "slow", "optimal_session_duration": 20, "weekly_study_capacity": 5, "focus_score": 35},
        practical_preferences={"overall_score": 15, "coding_proficiency": {"c": 0.1}, "preferred_practice_types": ["视频教程", "互动练习", "拖拽编程"]},
    ),
    # student_006 孙竞赛 — 竞赛型选手，算法强但基础有盲区
    StudentProfileModel(
        student_id=COMPETITOR,
        knowledge_base={"overall_score": 88, "C语言概述": 0.8, "数据类型与变量": 0.85, "控制结构": 0.95, "指针": 0.92, "结构体": 0.9, "文件操作": 0.6},
        cognitive_style={"primary": "kinesthetic", "scores": {"visual": 0.5, "auditory": 0.3, "reading": 0.6, "kinesthetic": 0.95}},
        weak_areas=["文件操作", "预处理器"],
        error_patterns=[{"type": "粗心错误", "desc": "边界条件经常遗漏"}],
        learning_goals=[{"goal": "获得蓝桥杯C/C++组省一等奖", "deadline": "2026-04-01"}],
        interest_areas=["算法竞赛", "数据结构", "动态规划", "图论"],
        learning_tempo={"study_speed": "fast", "optimal_session_duration": 120, "weekly_study_capacity": 30, "focus_score": 90},
        practical_preferences={"overall_score": 92, "coding_proficiency": {"c": 0.92, "cpp": 0.95}, "preferred_practice_types": ["算法竞赛", "限时挑战"]},
    ),
    # student_007 周稳步 — 中等水平稳步前进
    StudentProfileModel(
        student_id=STEADY,
        knowledge_base={"overall_score": 62, "C语言概述": 0.75, "数据类型与变量": 0.7, "控制结构": 0.6, "指针": 0.4},
        cognitive_style={"primary": "visual", "scores": {"visual": 0.85, "auditory": 0.6, "reading": 0.65, "kinesthetic": 0.5}},
        weak_areas=["指针", "动态内存"],
        error_patterns=[{"type": "概念模糊", "desc": "指针与数组的关系理解不深"}],
        learning_goals=[{"goal": "通过C语言期末考试拿到85分以上", "deadline": "2026-06-15"}],
        interest_areas=["Web开发", "移动应用"],
        learning_tempo={"study_speed": "moderate", "optimal_session_duration": 50, "weekly_study_capacity": 12, "focus_score": 72},
        practical_preferences={"overall_score": 65, "coding_proficiency": {"c": 0.55, "python": 0.5, "javascript": 0.4}, "preferred_practice_types": ["代码实操", "图文讲义"]},
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


# ---------- 知识点（DAG）—— C语言课程 ----------
kps = [
    KnowledgePointModel(
        kp_id="kp_c01", name="C语言概述与开发环境", subject="基础入门", course="C语言", difficulty=0.2,
        prerequisites=[], description="C语言的历史、特点、开发环境搭建与第一个程序",
        tags=["入门", "环境搭建"],
        document=KP_C01_DOC, code_example=KP_C01_CODE, questions=KP_C01_QS, mindmap=KP_C01_MM,
    ),
    KnowledgePointModel(
        kp_id="kp_c02", name="数据类型与变量", subject="基础入门", course="C语言", difficulty=0.25,
        prerequisites=[], description="基本数据类型、变量声明、命名规则、常量、类型转换",
        tags=["基础", "变量"],
        document=KP_C02_DOC, code_example=KP_C02_CODE, questions=KP_C02_QS, mindmap=KP_C02_MM,
    ),
    KnowledgePointModel(
        kp_id="kp_c03", name="运算符与表达式", subject="基础语法", course="C语言", difficulty=0.3,
        prerequisites=["kp_c02"], description="算术、关系、逻辑、赋值运算符及优先级",
        tags=["运算符", "表达式"],
        document=KP_C03_DOC, code_example=KP_C03_CODE, questions=KP_C03_QS, mindmap=KP_C03_MM,
    ),
    KnowledgePointModel(
        kp_id="kp_c04", name="输入输出与顺序结构", subject="基础语法", course="C语言", difficulty=0.3,
        prerequisites=["kp_c02"], description="printf、scanf格式控制与顺序结构程序设计",
        tags=["IO", "顺序结构"],
        document=KP_C04_DOC, code_example=KP_C04_CODE, questions=KP_C04_QS, mindmap=KP_C04_MM,
    ),
    KnowledgePointModel(
        kp_id="kp_c05", name="选择结构", subject="控制结构", course="C语言", difficulty=0.35,
        prerequisites=["kp_c03", "kp_c04"], description="if、if-else、switch语句与多分支程序设计",
        tags=["if", "switch", "分支"],
        document=KP_C05_DOC, code_example=KP_C05_CODE, questions=KP_C05_QS, mindmap=KP_C05_MM,
    ),
    KnowledgePointModel(
        kp_id="kp_c06", name="循环结构", subject="控制结构", course="C语言", difficulty=0.4,
        prerequisites=["kp_c03", "kp_c04"], description="for、while、do-while循环与嵌套循环",
        tags=["for", "while", "循环"],
        document=KP_C06_DOC, code_example=KP_C06_CODE, questions=KP_C06_QS, mindmap=KP_C06_MM,
    ),
    KnowledgePointModel(
        kp_id="kp_c07", name="数组", subject="数组与字符串", course="C语言", difficulty=0.45,
        prerequisites=["kp_c06"], description="一维数组、二维数组、数组遍历与常见算法",
        tags=["数组", "排序"],
        document=KP_C07_DOC, code_example=KP_C07_CODE, questions=KP_C07_QS, mindmap=KP_C07_MM,
    ),
    KnowledgePointModel(
        kp_id="kp_c08", name="字符串", subject="数组与字符串", course="C语言", difficulty=0.45,
        prerequisites=["kp_c07"], description="字符数组、字符串函数、字符串处理",
        tags=["字符串", "string.h"],
        document=KP_C08_DOC, code_example=KP_C08_CODE, questions=KP_C08_QS, mindmap=KP_C08_MM,
    ),
    KnowledgePointModel(
        kp_id="kp_c09", name="函数与递归", subject="函数", course="C语言", difficulty=0.5,
        prerequisites=["kp_c06"], description="函数定义、参数传递、递归算法、变量作用域",
        tags=["函数", "递归"],
        document=KP_C09_DOC, code_example=KP_C09_CODE, questions=KP_C09_QS, mindmap=KP_C09_MM,
    ),
    KnowledgePointModel(
        kp_id="kp_c10", name="指针基础", subject="指针", course="C语言", difficulty=0.55,
        prerequisites=["kp_c02", "kp_c09"], description="指针概念、取地址与解引用、指针运算",
        tags=["指针", "地址"],
        document=KP_C10_DOC, code_example=KP_C10_CODE, questions=KP_C10_QS, mindmap=KP_C10_MM,
    ),
    KnowledgePointModel(
        kp_id="kp_c11", name="指针与数组", subject="指针", course="C语言", difficulty=0.6,
        prerequisites=["kp_c10", "kp_c07"], description="数组名与指针关系、指针数组、多级指针",
        tags=["指针数组", "多级指针"],
        document=KP_C11_DOC, code_example=KP_C11_CODE, questions=KP_C11_QS, mindmap=KP_C11_MM,
    ),
    KnowledgePointModel(
        kp_id="kp_c12", name="结构体与联合体", subject="结构体与文件", course="C语言", difficulty=0.5,
        prerequisites=["kp_c02", "kp_c07"], description="struct定义、typedef、结构体数组与嵌套、union",
        tags=["结构体", "联合体"],
        document=KP_C12_DOC, code_example=KP_C12_CODE, questions=KP_C12_QS, mindmap=KP_C12_MM,
    ),
    KnowledgePointModel(
        kp_id="kp_c13", name="文件操作", subject="结构体与文件", course="C语言", difficulty=0.55,
        prerequisites=["kp_c12"], description="文件打开关闭、文本与二进制读写、文件定位",
        tags=["文件", "fread", "fwrite"],
        document=KP_C13_DOC, code_example=KP_C13_CODE, questions=KP_C13_QS, mindmap=KP_C13_MM,
    ),
    KnowledgePointModel(
        kp_id="kp_c14", name="动态内存管理", subject="高级主题", course="C语言", difficulty=0.6,
        prerequisites=["kp_c10"], description="malloc、calloc、realloc、free与内存泄漏防范",
        tags=["动态内存", "malloc"],
        document=KP_C14_DOC, code_example=KP_C14_CODE, questions=KP_C14_QS, mindmap=KP_C14_MM,
    ),
    KnowledgePointModel(
        kp_id="kp_c15", name="预处理指令", subject="高级主题", course="C语言", difficulty=0.4,
        prerequisites=["kp_c01"], description="宏定义、条件编译、文件包含与预处理原理",
        tags=["预处理", "宏定义"],
        document=KP_C15_DOC, code_example=KP_C15_CODE, questions=KP_C15_QS, mindmap=KP_C15_MM,
    ),
    KnowledgePointModel(
        kp_id="kp_c16", name="位运算", subject="高级主题", course="C语言", difficulty=0.55,
        prerequisites=["kp_c03", "kp_c06"], description="位运算符、位掩码、位域与底层数据操作",
        tags=["位运算", "位掩码"],
        document=KP_C16_DOC, code_example=KP_C16_CODE, questions=KP_C16_QS, mindmap=KP_C16_MM,
    ),
    # ---------- 电路分析课程 ----------
    KnowledgePointModel(
        kp_id="kp_e01", name="电路基本概念", subject="基础理论", course="电路分析", difficulty=0.2,
        prerequisites=[], description="电流、电压、功率、电阻的基本概念与欧姆定律",
        tags=["电流", "电压", "欧姆定律"],
        document="""# 电路基本概念

## 1.1 电流与电压

**电流（I）** 是电荷的定向移动，单位为安培（A）。
- 直流电流：大小和方向都不随时间变化
- 交流电流：大小和方向随时间周期性变化

**电压（V）** 是两点之间的电位差，单位为伏特（V）。
- 电压的方向：从高电位指向低电位
- 参考方向：假设的电压正方向

## 1.2 电阻与欧姆定律

**电阻（R）** 是导体对电流的阻碍作用，单位为欧姆（Ω）。

**欧姆定律**：$$V = I \\times R$$

其中：
- V 为电压（V）
- I 为电流（A）
- R 为电阻（Ω）

## 1.3 功率与能量

**电功率**：$$P = V \\times I = I^2 \\times R = \\frac{V^2}{R}$$

单位为瓦特（W）。

**电能量**：$$W = P \\times t$$

单位为焦耳（J）或千瓦时（kWh）。

## 1.4 电路模型

实际电路可以用理想电路元件来建模：
- **电阻**：消耗电能
- **电感**：储存磁场能量
- **电容**：储存电场能量
- **电源**：提供电能（电压源、电流源）

## 1.5 基尔霍夫定律

### KCL（基尔霍夫电流定律）
流入任一节点的电流之和等于流出该节点的电流之和：
$$\\sum I_{in} = \\sum I_{out}$$

### KVL（基尔霍夫电压定律）
沿任一闭合回路，电压升之和等于电压降之和：
$$\\sum V_{rise} = \\sum V_{drop}$$

> **学习建议**：理解电流、电压、电阻的基本概念是学习电路分析的基础，务必掌握欧姆定律和功率计算。""",
        code_example="""# 电路基本计算示例

# 欧姆定律计算
R = 100  # 电阻 (Ω)
V = 5    # 电压 (V)
I = V / R  # 电流 (A)
print(f'电流: {I}A')

# 功率计算
P = V * I  # 功率 (W)
print(f'功率: {P}W')

# 已知功率和电阻求电压
P_known = 25  # W
R_known = 25  # Ω
V_calc = (P_known * R_known) ** 0.5
print(f'电压: {V_calc}V')

# 已知功率和电压求电流
I_calc = P_known / V_calc
print(f'电流: {I_calc}A')

# KCL验证
# 节点A有三条支路，流入2A和3A，流出应该是5A
I1, I2 = 2, 3  # 流入电流
I3 = I1 + I2   # 流出电流
print(f'KCL验证: 流入{I1}+{I2}={I1+I2}A, 流出{I3}A -> {I1+I2 == I3}')

# KVL验证
# 闭合回路：电源12V，电阻压降5V和7V
V_source = 12
V_drop1, V_drop2 = 5, 7
kvl_ok = V_source == V_drop1 + V_drop2
print(f'KVL验证: 电源{V_source}V = 压降{V_drop1}+{V_drop2}={V_drop1+V_drop2}V -> {kvl_ok}')""",
        questions=[
            {"q_id": "q_e01_1", "type": "single_choice", "content": "欧姆定律的表达式是？", "options": [{"id": "A", "text": "V = I + R"}, {"id": "B", "text": "V = I × R"}, {"id": "C", "text": "V = I / R"}, {"id": "D", "text": "V = I - R"}], "correct_answer": "B", "explanation": "欧姆定律：V = I × R，电压等于电流乘以电阻。"},
            {"q_id": "q_e01_2", "type": "single_choice", "content": "一个10Ω电阻两端加5V电压，流过的电流是？", "options": [{"id": "A", "text": "0.5A"}, {"id": "B", "text": "2A"}, {"id": "C", "text": "50A"}, {"id": "D", "text": "5A"}], "correct_answer": "A", "explanation": "根据欧姆定律 I = V/R = 5/10 = 0.5A。"},
            {"q_id": "q_e01_3", "type": "single_choice", "content": "KCL定律描述的是？", "options": [{"id": "A", "text": "回路电压关系"}, {"id": "B", "text": "节点电流关系"}, {"id": "C", "text": "功率守恒"}, {"id": "D", "text": "电阻串联"}], "correct_answer": "B", "explanation": "KCL（基尔霍夫电流定律）描述的是节点处电流的守恒关系。"},
        ],
        mindmap={"root": "电路基本概念", "children": [{"name": "电流"}, {"name": "电压"}, {"name": "电阻"}, {"name": "功率"}, {"name": "欧姆定律"}, {"name": "KCL"}, {"name": "KVL"}]},
    ),
    KnowledgePointModel(
        kp_id="kp_e02", name="电阻串联与并联", subject="基础理论", course="电路分析", difficulty=0.22,
        prerequisites=["kp_e01"], description="串联电阻、并联电阻的等效计算与分压分流公式",
        tags=["串联", "并联", "等效电阻", "分压", "分流"],
        document="""# 电阻串联与并联

## 2.1 电阻串联

多个电阻首尾相连，电流相同。

**等效电阻**：$$R_{eq} = R_1 + R_2 + ... + R_n$$

**分压公式**：$$V_k = V_{total} \\times \\frac{R_k}{R_{eq}}$$

## 2.2 电阻并联

多个电阻并列连接，电压相同。

**等效电阻**：$$\\frac{1}{R_{eq}} = \\frac{1}{R_1} + \\frac{1}{R_2} + ... + \\frac{1}{R_n}$$

两个电阻并联简化：$$R_{eq} = \\frac{R_1 \\times R_2}{R_1 + R_2}$$

**分流公式**：$$I_k = I_{total} \\times \\frac{R_{total}}{R_k}$$

## 2.3 混联电路

既有串联又有并联的电路，需要逐步化简：
1. 先计算并联部分的等效电阻
2. 再计算串联部分的总电阻

## 2.4 实际应用

- **分压器**：从高电压获得低电压
- **电流表扩程**：并联分流电阻
- **电压表扩程**：串联分压电阻

> **学习建议**：熟练掌握串并联等效计算和分压分流公式是分析复杂电路的关键。""",
        code_example="""# 电阻串并联计算示例

# 串联电阻计算
R1, R2, R3 = 10, 20, 30  # Ω
R_series = R1 + R2 + R3
print(f'串联等效电阻: {R_series}Ω')

# 并联电阻计算（两个电阻）
R_a, R_b = 100, 200  # Ω
R_parallel = (R_a * R_b) / (R_a + R_b)
print(f'两电阻并联: {R_parallel:.2f}Ω')

# 并联电阻计算（多个电阻）
R_vals = [10, 20, 30]
R_multi = 1 / sum(1/r for r in R_vals)
print(f'三电阻并联: {R_multi:.2f}Ω')

# 分压计算
V_source = 12  # V
R_top, R_bottom = 100, 200  # Ω
V_out = V_source * R_bottom / (R_top + R_bottom)
print(f'分压输出: {V_out}V')

# 分流计算
I_total = 3  # A
R1, R2 = 20, 30  # Ω
I1 = I_total * R2 / (R1 + R2)
I2 = I_total * R1 / (R1 + R2)
print(f'分流: I1={I1}A, I2={I2}A, 合计={I1+I2}A')

# 混联电路计算
# R1串联(R2并联R3)
R1 = 10
R2, R3 = 20, 20
R_parallel_23 = (R2 * R3) / (R2 + R3)
R_total = R1 + R_parallel_23
print(f'混联等效: {R_total}Ω')""",
        questions=[
            {"q_id": "q_e02_1", "type": "single_choice", "content": "两个10Ω电阻并联后的等效电阻是？", "options": [{"id": "A", "text": "20Ω"}, {"id": "B", "text": "10Ω"}, {"id": "C", "text": "5Ω"}, {"id": "D", "text": "15Ω"}], "correct_answer": "C", "explanation": "两个相同电阻并联，等效电阻为原电阻的一半：10/2 = 5Ω。"},
            {"q_id": "q_e02_2", "type": "single_choice", "content": "12V电源串联100Ω和200Ω电阻，200Ω电阻上的电压是？", "options": [{"id": "A", "text": "4V"}, {"id": "B", "text": "6V"}, {"id": "C", "text": "8V"}, {"id": "D", "text": "12V"}], "correct_answer": "C", "explanation": "分压公式：V = 12 × 200/(100+200) = 12 × 2/3 = 8V。"},
        ],
        mindmap={"root": "电阻串并联", "children": [{"name": "串联"}, {"name": "并联"}, {"name": "等效电阻"}, {"name": "分压公式"}, {"name": "分流公式"}, {"name": "混联电路"}]},
    ),
    KnowledgePointModel(
        kp_id="kp_e03", name="支路电流法与网孔电流法", subject="电路分析方法", course="电路分析", difficulty=0.3,
        prerequisites=["kp_e02"], description="基于KCL和KVL的系统化电路分析方法",
        tags=["支路电流法", "网孔电流法", "节点电压法"],
        document="""# 支路电流法与网孔电流法

## 3.1 支路电流法

以各支路电流为未知量，直接应用KCL和KVL列方程。

**步骤**：
1. 标注各支路电流参考方向
2. 对每个节点应用KCL，列电流方程
3. 对每个网孔应用KVL，列电压方程
4. 联立求解

## 3.2 网孔电流法

以假想的网孔电流为未知量，仅需列KVL方程。

**步骤**：
1. 选择网孔，假设网孔电流方向
2. 对每个网孔列KVL方程
3. 互电阻项：相邻网孔电流方向相同时取正
4. 联立求解

**网孔方程**：$$R_{11}I_1 - R_{12}I_2 = V_{S1}$$
$$-R_{21}I_1 + R_{22}I_2 = V_{S2}$$

## 3.3 节点电压法

以节点电压为未知量，仅需列KCL方程。

**步骤**：
1. 选择参考节点（接地）
2. 对每个独立节点列KCL方程
3. 用电导表示：$$G_{11}V_1 - G_{12}V_2 = I_{S1}$$
4. 联立求解

## 3.4 方法比较

| 方法 | 方程数 | 适用场景 |
|------|--------|----------|
| 支路电流法 | 支路数 | 简单电路 |
| 网孔电流法 | 网孔数 | 平面电路 |
| 节点电压法 | 节点数-1 | 非平面电路 |

> **学习建议**：网孔电流法和节点电压法是最常用的方法，选择方程数少的方法更高效。""",
        code_example="""# 网孔电流法示例
# 双网孔电路：
# 网孔1: Vs1=10V, R11=100Ω, R12=50Ω(公共)
# 网孔2: Vs2=5V, R22=80Ω, R12=50Ω(公共)

import numpy as np

# 系数矩阵
R = np.array([[150, -50],   # R11+R12, -R12
              [-50, 130]])  # -R12, R22+R12

# 右侧向量
V = np.array([10, 5])

# 求解网孔电流
I = np.linalg.solve(R, V)
print(f'网孔电流: I1={I[0]*1000:.2f}mA, I2={I[1]*1000:.2f}mA')

# 计算各支路电流
I_R1 = I[0]  # R1上的电流
I_R2 = I[1]  # R2上的电流
I_R12 = I[0] - I[1]  # 公共电阻上的电流
print(f'支路电流: R1={I_R1*1000:.2f}mA, R2={I_R2*1000:.2f}mA, 公共={I_R12*1000:.2f}mA')

# 节点电压法示例
# 两个节点: V1和参考节点(地)
# G11*V1 = Is
G11 = 1/100 + 1/200  # 电导之和
Is = 0.1  # 流入电流源
V1 = Is / G11
print(f'节点电压: V1={V1:.2f}V')""",
        questions=[
            {"q_id": "q_e03_1", "type": "single_choice", "content": "网孔电流法需要列什么方程？", "options": [{"id": "A", "text": "KCL方程"}, {"id": "B", "text": "KVL方程"}, {"id": "C", "text": "功率方程"}, {"id": "D", "text": "欧姆定律"}], "correct_answer": "B", "explanation": "网孔电流法是对每个网孔应用KVL列写电压方程。"},
        ],
        mindmap={"root": "电路分析方法", "children": [{"name": "支路电流法"}, {"name": "网孔电流法"}, {"name": "节点电压法"}, {"name": "叠加定理"}, {"name": "等效变换"}]},
    ),
    KnowledgePointModel(
        kp_id="kp_e04", name="叠加定理与等效变换", subject="电路分析方法", course="电路分析", difficulty=0.3,
        prerequisites=["kp_e03"], description="线性电路的叠加原理与电源等效变换",
        tags=["叠加定理", "等效变换", "电压源", "电流源"],
        document="""# 叠加定理与等效变换

## 4.1 叠加定理

**定理内容**：在线性电路中，任一支路的电流（或电压）等于各个独立电源单独作用时在该支路产生的电流（或电压）的代数和。

**使用步骤**：
1. 保留一个电源，其余电压源短路、电流源开路
2. 计算该电源单独作用时的响应
3. 对所有电源重复上述步骤
4. 将各响应代数相加

**注意事项**：
- 仅适用于线性电路
- 功率不能叠加（功率与电流/电压是平方关系）
- 叠加时注意参考方向

## 4.2 电源等效变换

### 电压源与电流源互换

**电压源 → 电流源**：$$I_S = \\frac{V_S}{R_S}$$
内阻不变，电流源与内阻并联

**电流源 → 电压源**：$$V_S = I_S \\times R_S$$
内阻不变，电压源与内阻串联

### 实际电源模型

**理想电压源**：内阻为零，输出电压恒定
**理想电流源**：内阻无穷大，输出电流恒定

**实际电源**：$$V = V_S - I \\times R_S$$

## 4.3 最大功率传输定理

当负载电阻等于电源内阻时，负载获得最大功率：
$$R_L = R_S$$
$$P_{max} = \\frac{V_S^2}{4R_S}$$

> **学习建议**：叠加定理是分析多电源电路的利器，电源等效变换可以简化电路结构。""",
        code_example="""# 叠加定理示例
# 双电源电路
V1, V2 = 10, 5  # V
R1, R2, R3 = 100, 200, 150  # Ω

# V1单独作用（V2短路）
# R2和R3并联后与R1串联
R23_parallel = (R2 * R3) / (R2 + R3)
I_total_1 = V1 / (R1 + R23_parallel)
I_R3_1 = I_total_1 * R2 / (R2 + R3)

# V2单独作用（V1短路）
# R1和R3并联后与R2串联
R13_parallel = (R1 * R3) / (R1 + R3)
I_total_2 = V2 / (R2 + R13_parallel)
I_R3_2 = I_total_2 * R1 / (R1 + R3)

# 叠加（注意方向）
I_R3 = I_R3_1 + I_R3_2
print(f'叠加定理: I_R3 = {I_R3*1000:.2f}mA')

# 电源等效变换
# 10V电压源串联100Ω → 电流源并联100Ω
V_S = 10  # V
R_S = 100  # Ω
I_S = V_S / R_S
print(f'等效电流源: Is={I_S*1000:.2f}mA, Rs={R_S}Ω')

# 最大功率传输
V_source = 12  # V
R_internal = 50  # Ω
R_load = R_internal  # 匹配条件
P_max = V_source**2 / (4 * R_internal)
print(f'最大功率: Pmax={P_max}W (当RL={R_load}Ω)')""",
        questions=[
            {"q_id": "q_e04_1", "type": "single_choice", "content": "叠加定理适用于哪种电路？", "options": [{"id": "A", "text": "非线性电路"}, {"id": "B", "text": "线性电路"}, {"id": "C", "text": "交流电路"}, {"id": "D", "text": "所有电路"}], "correct_answer": "B", "explanation": "叠加定理仅适用于线性电路，因为非线性元件不满足叠加性。"},
            {"q_id": "q_e04_2", "type": "single_choice", "content": "最大功率传输的条件是？", "options": [{"id": "A", "text": "负载电阻最大"}, {"id": "B", "text": "负载电阻最小"}, {"id": "C", "text": "负载电阻等于内阻"}, {"id": "D", "text": "负载电阻为零"}], "correct_answer": "C", "explanation": "当负载电阻等于电源内阻时，负载获得最大功率。"},
        ],
        mindmap={"root": "叠加定理与等效变换", "children": [{"name": "叠加定理"}, {"name": "电源等效变换"}, {"name": "电压源→电流源"}, {"name": "电流源→电压源"}, {"name": "最大功率传输"}]},
    ),
    KnowledgePointModel(
        kp_id="kp_e05", name="戴维南定理与诺顿定理", subject="电路分析方法", course="电路分析", difficulty=0.35,
        prerequisites=["kp_e03", "kp_e04"], description="将复杂二端网络等效为简单电源模型",
        tags=["戴维南", "诺顿", "等效电路", "开路电压", "等效电阻"],
        document="""# 戴维南定理与诺顿定理

## 5.1 戴维南定理

**定理内容**：任何一个线性含源二端网络，对外电路而言，可以用一个电压源和一个电阻的串联组合来等效替代。

**等效参数**：
- **开路电压** $V_{th}$：端口开路时的电压
- **等效电阻** $R_{th}$：将独立源置零后端口的等效电阻

## 5.2 求解戴维南等效电路

### 方法一：开路电压/短路电流法
1. 求开路电压 $V_{th}$（端口开路时的电压）
2. 求短路电流 $I_{sc}$（端口短路时的电流）
3. $R_{th} = V_{th} / I_{sc}$

### 方法二：外加电源法
1. 将所有独立源置零（电压源短路，电流源开路）
2. 在端口外加测试电压 $V_T$
3. 计算流入电流 $I_T$
4. $R_{th} = V_T / I_T$

## 5.3 诺顿定理

**定理内容**：任何一个线性含源二端网络，对外电路而言，可以用一个电流源和一个电阻的并联组合来等效替代。

**等效参数**：
- **短路电流** $I_N = V_{th}/R_{th}$
- **等效电阻** $R_N = R_{th}$

## 5.4 戴维南-诺顿互换

$$V_{th} = I_N \\times R_{th}$$
$$I_N = V_{th} / R_{th}$$

## 5.5 应用场景

- 分析负载变化时的电路响应
- 求解最大功率传输问题
- 简化复杂电路分析

**例题**：求下图的戴维南等效电路

```
    R1=100Ω     R2=200Ω
Vs1 ──┤├──A──┤├──B
10V              │
                 RL=50Ω
                 │
GND ─────────────┘
```

解：
1. 开路电压：$V_{th} = V_{AB} = V_{s1} \\times \\frac{R_2}{R_1+R_2} = 10 \\times \\frac{200}{300} = 6.67V$
2. 等效电阻：$R_{th} = R_1 // R_2 = \\frac{100 \\times 200}{100+200} = 66.67Ω$
3. 负载电流：$I_L = \\frac{V_{th}}{R_{th}+R_L} = \\frac{6.67}{66.67+50} = 57.1mA$

> **学习建议**：戴维南定理是电路分析中最重要的定理之一，务必掌握两种求解方法。""",
        code_example="""# 戴维南等效计算示例

def thevenin_equivalent(Vs1, R1, R2, RL=None):
    \"\"\"计算含源二端网络的戴维南等效\"\"\"
    # 开路电压（去掉负载RL）
    Vth = Vs1 * R2 / (R1 + R2)
    # 等效电阻（电源短路）
    Rth = (R1 * R2) / (R1 + R2)
    # 负载电流
    if RL:
        IL = Vth / (Rth + RL)
    else:
        IL = None
    return Vth, Rth, IL

# 例题计算
Vs1 = 10  # V
R1, R2 = 100, 200  # Ω
RL = 50  # Ω

Vth, Rth, IL = thevenin_equivalent(Vs1, R1, R2, RL)
print(f'戴维南等效:')
print(f'  开路电压 Vth = {Vth:.2f}V')
print(f'  等效电阻 Rth = {Rth:.2f}Ω')
print(f'  负载电流 IL = {IL*1000:.2f}mA')

# 诺顿等效
IN = Vth / Rth
print(f'\\n诺顿等效:')
print(f'  短路电流 IN = {IN*1000:.2f}mA')
print(f'  等效电阻 RN = {Rth:.2f}Ω')

# 验证：用诺顿等效计算负载电流
IL_norton = IN * Rth / (Rth + RL)
print(f'  负载电流 IL = {IL_norton*1000:.2f}mA (与戴维南结果一致)')

# 最大功率传输
P_max = Vth**2 / (4 * Rth)
R_load_optimal = Rth
print(f'\\n最大功率传输:')
print(f'  最优负载 RL = {R_load_optimal:.2f}Ω')
print(f'  最大功率 Pmax = {P_max*1000:.2f}mW')""",
        questions=[
            {"q_id": "q_e05_1", "type": "single_choice", "content": "戴维南等效中的Vth是什么？", "options": [{"id": "A", "text": "短路电流"}, {"id": "B", "text": "开路电压"}, {"id": "C", "text": "等效电阻"}, {"id": "D", "text": "负载电压"}], "correct_answer": "B", "explanation": "Vth是戴维南等效电压，即端口开路时的电压。"},
            {"q_id": "q_e05_2", "type": "single_choice", "content": "戴维南等效电阻Rth的求法是？", "options": [{"id": "A", "text": "端口开路电阻"}, {"id": "B", "text": "端口短路电阻"}, {"id": "C", "text": "独立源置零后的端口电阻"}, {"id": "D", "text": "负载电阻"}], "correct_answer": "C", "explanation": "等效电阻是将所有独立源置零（电压源短路、电流源开路）后，从端口看进去的等效电阻。"},
            {"q_id": "q_e05_3", "type": "single_choice", "content": "诺顿定理的等效电流源等于？", "options": [{"id": "A", "text": "开路电压"}, {"id": "B", "text": "短路电流"}, {"id": "C", "text": "等效电阻"}, {"id": "D", "text": "负载电流"}], "correct_answer": "B", "explanation": "诺顿等效电流源等于端口短路时的电流。"},
        ],
        mindmap={"root": "戴维南与诺顿定理", "children": [{"name": "戴维南定理"}, {"name": "诺顿定理"}, {"name": "开路电压"}, {"name": "等效电阻"}, {"name": "短路电流"}, {"name": "互换关系"}, {"name": "最大功率传输"}]},
    ),
    # ============================================================
    # STM32嵌入式开发 知识点
    # ============================================================
    KnowledgePointModel(
        kp_id="kp_s01", name="STM32基础入门", subject="基础入门", course="STM32嵌入式", difficulty=0.2,
        prerequisites=[], description="芯片架构、开发环境搭建、工程模板创建、GPIO基础",
        tags=["STM32", "ARM", "Cortex-M3", "Keil", "工程模板"],
        document="""# STM32基础入门

## 1. STM32芯片概述

STM32是意法半导体（ST）推出的基于ARM Cortex-M3内核的32位微控制器系列。STM32F103是入门级经典型号。

### 核心参数
| 参数 | 数值 |
|------|------|
| 内核 | ARM Cortex-M3 |
| 主频 | 72MHz |
| Flash | 64KB/128KB/256KB/512KB |
| SRAM | 20KB/48KB/64KB/96KB |
| GPIO | 37~112个 |

## 2. 开发环境搭建

### Keil MDK 安装
1. 安装 Keil MDK-ARM
2. 安装 STM32F10x 器件支持包（DFP）
3. 安装 ST-Link 驱动

### 工程模板创建
```
Project/
├── User/          # 用户代码（main.c, stm32f10x_it.c）
├── StdPeriph_Driver/  # 标准外设库
├── CMSIS/         # ARM内核支持文件
├── Output/        # 编译输出
└── Listings/      # 编译列表
```

## 3. GPIO基础

GPIO（General Purpose Input/Output）是通用输入输出端口，STM32每个GPIO引脚可配置为：
- **输入模式**：上拉输入、下拉输入、浮空输入、模拟输入
- **输出模式**：推挽输出、开漏输出、复用推挽、复用开漏

### GPIO初始化步骤
```c
RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOA, ENABLE);  // 开启时钟
GPIO_InitTypeDef GPIO_InitStructure;
GPIO_InitStructure.GPIO_Pin = GPIO_Pin_0;
GPIO_InitStructure.GPIO_Mode = GPIO_Mode_Out_PP;  // 推挽输出
GPIO_InitStructure.GPIO_Speed = GPIO_Speed_50MHz;
GPIO_Init(GPIOA, &GPIO_InitStructure);
```

> **重点**：操作GPIO前必须先开启对应GPIO端口的时钟！
""",
        code_example="""#include "stm32f10x.h"
#include "Delay.h"

int main(void)
{
    RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOA, ENABLE);
    GPIO_InitTypeDef GPIO_InitStructure;
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_Out_PP;
    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_0;
    GPIO_InitStructure.GPIO_Speed = GPIO_Speed_50MHz;
    GPIO_Init(GPIOA, &GPIO_InitStructure);
    while (1)
    {
        GPIO_ResetBits(GPIOA, GPIO_Pin_0);
        Delay_ms(500);
        GPIO_SetBits(GPIOA, GPIO_Pin_0);
        Delay_ms(500);
    }
}""",
        questions=[
            {"q_id": "q_s01_1", "type": "single_choice", "content": "STM32F103的内核架构是？", "options": [{"id": "A", "text": "ARM Cortex-M0"}, {"id": "B", "text": "ARM Cortex-M3"}, {"id": "C", "text": "ARM Cortex-M4"}, {"id": "D", "text": "ARM Cortex-A9"}], "correct_answer": "B", "explanation": "STM32F103系列采用ARM Cortex-M3内核，主频72MHz。"},
            {"q_id": "q_s01_2", "type": "single_choice", "content": "操作GPIO前必须先做什么？", "options": [{"id": "A", "text": "配置引脚模式"}, {"id": "B", "text": "开启GPIO端口时钟"}, {"id": "C", "text": "设置输出速度"}, {"id": "D", "text": "初始化中断"}], "correct_answer": "B", "explanation": "STM32外设默认时钟关闭，操作前必须先使能对应GPIO端口的时钟。"},
            {"q_id": "q_s01_3", "type": "single_choice", "content": "推挽输出的特点是？", "options": [{"id": "A", "text": "只能输出低电平"}, {"id": "B", "text": "只能输出高电平"}, {"id": "C", "text": "可以输出高电平和低电平"}, {"id": "D", "text": "只能输入"}], "correct_answer": "C", "explanation": "推挽输出可以主动驱动高电平和低电平，驱动能力较强。"},
        ],
        mindmap={"root": "STM32基础入门", "children": [{"name": "芯片架构"}, {"name": "开发环境"}, {"name": "Keil MDK"}, {"name": "工程模板"}, {"name": "GPIO基础"}, {"name": "引脚模式"}]},
    ),
    KnowledgePointModel(
        kp_id="kp_s02", name="GPIO输出控制", subject="GPIO与外设", course="STM32嵌入式", difficulty=0.25,
        prerequisites=["kp_s01"], description="通用输入输出端口输出模式，驱动LED、蜂鸣器、舵机等外设",
        tags=["GPIO", "LED", "蜂鸣器", "推挽输出", "输出控制"],
        document="""# GPIO输出控制

## 1. GPIO输出模式

### 推挽输出（Push-Pull）
- 可输出高电平（VDD）和低电平（VSS）
- 驱动能力强，适合驱动LED、蜂鸣器等
- 最常用输出模式

### 开漏输出（Open-Drain）
- 只能主动拉低，高电平需外部上拉
- 适合电平转换和线与逻辑
- I2C通信常用此模式

## 2. 驱动LED

### 接线方式
- LED正极 → GPIO引脚（通过限流电阻）
- LED负极 → GND
- 限流电阻：220Ω~1kΩ

### 代码实现
```c
// 点亮LED（低电平有效）
GPIO_ResetBits(GPIOA, GPIO_Pin_0);
// 熄灭LED
GPIO_SetBits(GPIOA, GPIO_Pin_0);
// 翻转LED
GPIO_WriteBit(GPIOA, GPIO_Pin_0,
    (BitAction)(1 - GPIO_ReadOutputDataBit(GPIOA, GPIO_Pin_0)));
```

## 3. 驱动蜂鸣器

有源蜂鸣器：给电即响，用GPIO直接驱动
无源蜂鸣器：需要PWM信号驱动

## 4. 驱动舵机

舵机通过50Hz PWM信号控制角度：
- 0.5ms脉宽 → 0°
- 1.5ms脉宽 → 90°
- 2.5ms脉宽 → 180°
""",
        code_example="""#include "stm32f10x.h"
#include "Delay.h"

int main(void)
{
    RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOA, ENABLE);
    GPIO_InitTypeDef GPIO_InitStructure;
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_Out_PP;
    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_0;
    GPIO_InitStructure.GPIO_Speed = GPIO_Speed_50MHz;
    GPIO_Init(GPIOA, &GPIO_InitStructure);
    while (1)
    {
        GPIO_ResetBits(GPIOA, GPIO_Pin_0);  // LED亮
        Delay_ms(500);
        GPIO_SetBits(GPIOA, GPIO_Pin_0);    // LED灭
        Delay_ms(500);
    }
}""",
        questions=[
            {"q_id": "q_s02_1", "type": "single_choice", "content": "驱动LED通常使用哪种GPIO输出模式？", "options": [{"id": "A", "text": "开漏输出"}, {"id": "B", "text": "推挽输出"}, {"id": "C", "text": "浮空输入"}, {"id": "D", "text": "模拟输入"}], "correct_answer": "B", "explanation": "推挽输出驱动能力强，适合驱动LED等外设。"},
            {"q_id": "q_s02_2", "type": "single_choice", "content": "LED限流电阻的典型值是？", "options": [{"id": "A", "text": "10Ω"}, {"id": "B", "text": "100Ω"}, {"id": "C", "text": "220Ω"}, {"id": "D", "text": "10kΩ"}], "correct_answer": "C", "explanation": "220Ω是常用限流电阻值，可将LED电流限制在约10mA。"},
        ],
        mindmap={"root": "GPIO输出控制", "children": [{"name": "推挽输出"}, {"name": "开漏输出"}, {"name": "LED驱动"}, {"name": "蜂鸣器驱动"}, {"name": "舵机控制"}]},
    ),
    KnowledgePointModel(
        kp_id="kp_s03", name="GPIO输入检测", subject="GPIO与外设", course="STM32嵌入式", difficulty=0.25,
        prerequisites=["kp_s01"], description="通用输入输出端口输入模式，按键检测、传感器接口",
        tags=["GPIO", "按键", "传感器", "输入检测", "消抖"],
        document="""# GPIO输入检测

## 1. GPIO输入模式

### 上拉输入（Input Pull-Up）
- 内部上拉电阻，默认高电平
- 按键接地，按下时低电平
- 最常用的按键检测方式

### 下拉输入（Input Pull-Down）
- 内部下拉电阻，默认低电平
- 按键接VCC，按下时高电平

### 浮空输入（Input Floating）
- 无内部上下拉，电平由外部决定
- 适合外部已有上下拉的场景

## 2. 按键检测

### 硬件消抖
- 并联100nF电容滤除抖动

### 软件消抖
```c
if (GPIO_ReadInputDataBit(GPIOA, GPIO_Pin_1) == 0)  // 按下
{
    Delay_ms(20);  // 等待消抖
    if (GPIO_ReadInputDataBit(GPIOA, GPIO_Pin_1) == 0)  // 确认按下
    {
        // 执行操作
        while (GPIO_ReadInputDataBit(GPIOA, GPIO_Pin_1) == 0);  // 等待松开
    }
}
```

## 3. 传感器接口

### 数字传感器
- 输出高低电平，直接用GPIO读取
- 如：光敏传感器、红外避障传感器

### 模拟传感器
- 输出模拟电压，需要用ADC采集
- 如：温度传感器、电位器
""",
        code_example="""#include "stm32f10x.h"
#include "Delay.h"

int main(void)
{
    RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOA, ENABLE);
    // PA0: LED输出
    GPIO_InitTypeDef GPIO_InitStructure;
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_Out_PP;
    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_0;
    GPIO_Init(GPIOA, &GPIO_InitStructure);
    // PA1: 按键输入（上拉）
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_IPU;
    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_1;
    GPIO_Init(GPIOA, &GPIO_InitStructure);
    while (1)
    {
        if (GPIO_ReadInputDataBit(GPIOA, GPIO_Pin_1) == 0)
        {
            Delay_ms(20);
            if (GPIO_ReadInputDataBit(GPIOA, GPIO_Pin_1) == 0)
            {
                GPIO_WriteBit(GPIOA, GPIO_Pin_0,
                    (BitAction)(1 - GPIO_ReadOutputDataBit(GPIOA, GPIO_Pin_0)));
                while (GPIO_ReadInputDataBit(GPIOA, GPIO_Pin_1) == 0);
            }
        }
    }
}""",
        questions=[
            {"q_id": "q_s03_1", "type": "single_choice", "content": "按键检测通常使用哪种输入模式？", "options": [{"id": "A", "text": "浮空输入"}, {"id": "B", "text": "上拉输入"}, {"id": "C", "text": "模拟输入"}, {"id": "D", "text": "下拉输入"}], "correct_answer": "B", "explanation": "上拉输入默认高电平，按键接地后按下为低电平，是最常用的按键检测方式。"},
            {"q_id": "q_s03_2", "type": "single_choice", "content": "软件消抖的延时时间通常为？", "options": [{"id": "A", "text": "1ms"}, {"id": "B", "text": "5ms"}, {"id": "C", "text": "20ms"}, {"id": "D", "text": "100ms"}], "correct_answer": "C", "explanation": "按键机械抖动通常在5~20ms，延时20ms可有效消除抖动。"},
        ],
        mindmap={"root": "GPIO输入检测", "children": [{"name": "上拉输入"}, {"name": "下拉输入"}, {"name": "浮空输入"}, {"name": "按键检测"}, {"name": "软件消抖"}, {"name": "传感器接口"}]},
    ),
    KnowledgePointModel(
        kp_id="kp_s04", name="OLED显示模块", subject="通信协议", course="STM32嵌入式", difficulty=0.4,
        prerequisites=["kp_s01"], description="I2C通信协议、SSD1306驱动、文字图形显示",
        tags=["OLED", "SSD1306", "I2C", "显示", "0.96寸"],
        document="""# OLED显示模块

## 1. OLED简介

0.96寸OLED显示屏，分辨率128×64，驱动芯片SSD1306，支持I2C和SPI接口。

## 2. I2C通信协议

I2C使用两根线通信：
- **SCL**：时钟线
- **SDA**：数据线

### 时序
1. 起始信号：SCL高电平时，SDA由高变低
2. 停止信号：SCL高电平时，SDA由低变高
3. 数据传输：SCL低电平时改变SDA，高电平时读取

### 设备地址
- SSD1306默认地址：0x3C（7位）/ 0x78（8位）

## 3. SSD1306初始化

```c
// 关闭显示
SSD1306_WriteCmd(0xAE);
// 设置对比度
SSD1306_WriteCmd(0x81);
SSD1306_WriteCmd(0x7F);
// 正常显示
SSD1306_WriteCmd(0xA6);
// 开启显示
SSD1306_WriteCmd(0xAF);
```

## 4. 显示文字

使用字模库将字符转换为点阵数据，通过I2C发送到OLED。
""",
        code_example="""#include "stm32f10x.h"
#include "OLED.h"

int main(void)
{
    OLED_Init();
    OLED_Clear();
    OLED_ShowString(0, 0, "Hello STM32!");
    OLED_ShowNum(0, 2, 12345, 5);
    OLED_ShowSignedNum(0, 4, -67);
    while (1) {}
}""",
        questions=[
            {"q_id": "q_s04_1", "type": "single_choice", "content": "SSD1306 OLED的默认I2C地址是？", "options": [{"id": "A", "text": "0x3C"}, {"id": "B", "text": "0x50"}, {"id": "C", "text": "0xA0"}, {"id": "D", "text": "0xD0"}], "correct_answer": "A", "explanation": "SSD1306的7位I2C地址默认为0x3C。"},
            {"q_id": "q_s04_2", "type": "single_choice", "content": "I2C通信使用几根数据线？", "options": [{"id": "A", "text": "1根"}, {"id": "B", "text": "2根"}, {"id": "C", "text": "3根"}, {"id": "D", "text": "4根"}], "correct_answer": "B", "explanation": "I2C使用SCL（时钟）和SDA（数据）两根线通信。"},
        ],
        mindmap={"root": "OLED显示模块", "children": [{"name": "SSD1306"}, {"name": "I2C协议"}, {"name": "SCL/SDA"}, {"name": "设备地址"}, {"name": "字模库"}, {"name": "显示文字"}]},
    ),
    KnowledgePointModel(
        kp_id="kp_s05", name="定时器与PWM", subject="高级外设", course="STM32嵌入式", difficulty=0.45,
        prerequisites=["kp_s02"], description="定时中断、PWM输出、输入捕获、编码器接口",
        tags=["定时器", "TIM", "PWM", "输入捕获", "编码器"],
        document="""# 定时器与PWM

## 1. 定时器概述

STM32F103有多个定时器：
- **TIM1**：高级控制定时器
- **TIM2~TIM4**：通用定时器
- **TIM5~TIM7**：基本定时器

## 2. 定时中断

### 配置步骤
1. 开启定时器时钟
2. 配置时基单元（PSC预分频、ARR自动重装载）
3. 配置NVIC中断
4. 使能更新中断
5. 启动定时器

```c
TIM_TimeBaseInitTypeDef TIM_TimeBaseStructure;
TIM_TimeBaseStructure.TIM_Period = 999;      // ARR
TIM_TimeBaseStructure.TIM_Prescaler = 7199;  // PSC
TIM_TimeBaseStructure.TIM_ClockDivision = 0;
TIM_TimeBaseInit(TIM2, &TIM_TimeBaseStructure);
TIM_ITConfig(TIM2, TIM_IT_Update, ENABLE);
TIM_Cmd(TIM2, ENABLE);
```

## 3. PWM输出

PWM（脉冲宽度调制）通过改变占空比控制输出：
- **占空比** = CCR / (ARR+1) × 100%
- 频率 = 时钟 / ((PSC+1) × (ARR+1))

### 应用
- LED亮度调节
- 舵机角度控制
- 电机速度控制

## 4. 输入捕获

测量外部信号的频率和脉宽，常用于红外接收、超声波测距等。
""",
        code_example="""#include "stm32f10x.h"
#include "Delay.h"

void PWM_Init(void)
{
    RCC_APB1PeriphClockCmd(RCC_APB1Periph_TIM2, ENABLE);
    RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOA, ENABLE);
    GPIO_InitTypeDef GPIO_InitStructure;
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_AF_PP;
    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_0;
    GPIO_Init(GPIOA, &GPIO_InitStructure);
    TIM_TimeBaseInitTypeDef TIM_TimeBaseStructure;
    TIM_TimeBaseStructure.TIM_Period = 100 - 1;
    TIM_TimeBaseStructure.TIM_Prescaler = 0;
    TIM_TimeBaseInit(TIM2, &TIM_TimeBaseStructure);
    TIM_OCInitTypeDef TIM_OCInitStructure;
    TIM_OCInitStructure.TIM_OCMode = TIM_OCMode_PWM1;
    TIM_OCInitStructure.TIM_OutputState = TIM_OutputState_Enable;
    TIM_OC1Init(TIM2, &TIM_OCInitStructure);
    TIM_Cmd(TIM2, ENABLE);
}
int main(void)
{
    PWM_Init();
    uint8_t i;
    while (1)
    {
        for (i = 0; i <= 100; i++) { TIM_SetCompare1(TIM2, i); Delay_ms(10); }
        for (i = 0; i <= 100; i++) { TIM_SetCompare1(TIM2, 100 - i); Delay_ms(10); }
    }
}""",
        questions=[
            {"q_id": "q_s05_1", "type": "single_choice", "content": "PWM占空比的计算公式是？", "options": [{"id": "A", "text": "CCR / ARR × 100%"}, {"id": "B", "text": "ARR / CCR × 100%"}, {"id": "C", "text": "PSC / ARR × 100%"}, {"id": "D", "text": "CCR / PSC × 100%"}], "correct_answer": "A", "explanation": "占空比 = CCR / (ARR+1) × 100%，CCR越大占空比越高。"},
            {"q_id": "q_s05_2", "type": "single_choice", "content": "舵机控制需要多少频率的PWM信号？", "options": [{"id": "A", "text": "1Hz"}, {"id": "B", "text": "10Hz"}, {"id": "C", "text": "50Hz"}, {"id": "D", "text": "1000Hz"}], "correct_answer": "C", "explanation": "舵机标准控制信号为50Hz（周期20ms），脉宽0.5~2.5ms对应0°~180°。"},
        ],
        mindmap={"root": "定时器与PWM", "children": [{"name": "定时中断"}, {"name": "PWM输出"}, {"name": "占空比"}, {"name": "输入捕获"}, {"name": "编码器接口"}, {"name": "LED呼吸灯"}, {"name": "舵机控制"}]},
    ),
    KnowledgePointModel(
        kp_id="kp_s06", name="ADC模数转换", subject="高级外设", course="STM32嵌入式", difficulty=0.45,
        prerequisites=["kp_s05"], description="模拟信号采集、电压测量、多通道扫描",
        tags=["ADC", "模数转换", "电压采集", "模拟信号"],
        document="""# ADC模数转换

## 1. ADC概述

STM32F103内置2个12位逐次逼近型ADC（ADC1、ADC2），共16个通道。

### 关键参数
| 参数 | 数值 |
|------|------|
| 分辨率 | 12位（0~4095） |
| 转换时间 | 最短1μs（72MHz/12=6MHz） |
| 输入范围 | 0~3.3V |
| 通道数 | 16个外部通道 |

## 2. ADC配置

### 单次转换
```c
ADC_InitTypeDef ADC_InitStructure;
ADC_InitStructure.ADC_Mode = ADC_Mode_Independent;
ADC_InitStructure.ADC_ScanConvMode = DISABLE;
ADC_InitStructure.ADC_ContinuousConvMode = DISABLE;
ADC_InitStructure.ADC_DataAlign = ADC_DataAlign_Right;
ADC_Init(ADC1, &ADC_InitStructure);
ADC_Cmd(ADC1, ENABLE);
```

### 读取电压
```c
uint16_t adc_value = ADC_GetConversionValue(ADC1);
float voltage = adc_value * 3.3f / 4095;
```

## 3. 多通道扫描

按顺序采集多个通道的数据，适合多传感器场景。

## 4. 应用场景
- 电位器电压检测
- 温度传感器读取
- 光敏传感器采集
- 电池电压监测
""",
        code_example="""#include "stm32f10x.h"

uint16_t ADC_Read(uint8_t channel)
{
    ADC_RegularChannelConfig(ADC1, channel, 1, ADC_SampleTime_55Cycles5);
    ADC_SoftwareStartConvCmd(ADC1, ENABLE);
    while (!ADC_GetFlagStatus(ADC1, ADC_FLAG_EOC));
    return ADC_GetConversionValue(ADC1);
}
int main(void)
{
    // ADC初始化代码...
    while (1)
    {
        uint16_t adc_val = ADC_Read(ADC_Channel_0);
        float voltage = adc_val * 3.3f / 4095;
    }
}""",
        questions=[
            {"q_id": "q_s06_1", "type": "single_choice", "content": "STM32F103 ADC的分辨率是？", "options": [{"id": "A", "text": "8位"}, {"id": "B", "text": "10位"}, {"id": "C", "text": "12位"}, {"id": "D", "text": "16位"}], "correct_answer": "C", "explanation": "STM32F103内置12位ADC，转换结果范围0~4095。"},
            {"q_id": "q_s06_2", "type": "single_choice", "content": "ADC输入电压范围是？", "options": [{"id": "A", "text": "0~5V"}, {"id": "B", "text": "0~3.3V"}, {"id": "C", "text": "0~1.8V"}, {"id": "D", "text": "0~12V"}], "correct_answer": "B", "explanation": "STM32的ADC输入范围为0~3.3V，超过可能损坏芯片。"},
        ],
        mindmap={"root": "ADC模数转换", "children": [{"name": "12位分辨率"}, {"name": "单次转换"}, {"name": "连续转换"}, {"name": "多通道扫描"}, {"name": "电压计算"}, {"name": "传感器采集"}]},
    ),
    KnowledgePointModel(
        kp_id="kp_s07", name="DMA数据转运", subject="高级外设", course="STM32嵌入式", difficulty=0.6,
        prerequisites=["kp_s06"], description="直接内存访问、高效数据传输、DMA+ADC",
        tags=["DMA", "直接内存访问", "数据传输", "高效"],
        document="""# DMA数据转运

## 1. DMA概述

DMA（Direct Memory Access）直接内存访问，可在不占用CPU的情况下传输数据。

### STM32F103 DMA特性
- 2个DMA控制器（DMA1、DMA2）
- DMA1有7个通道，DMA2有5个通道
- 支持存储器↔外设、存储器↔存储器传输

## 2. DMA工作原理

```
外设 → DMA → 存储器（无需CPU干预）
```

### 传输参数
- **源地址**：数据来源（外设数据寄存器或内存）
- **目标地址**：数据去向
- **传输数量**：传输多少个数据
- **传输方向**：外设到内存 / 内存到外设 / 内存到内存

## 3. DMA+ADC

使用DMA自动将ADC转换结果搬运到数组，无需CPU逐个读取：

```c
uint16_t adc_buffer[10];
DMA_InitTypeDef DMA_InitStructure;
DMA_InitStructure.DMA_PeripheralBaseAddr = (uint32_t)&ADC1->DR;
DMA_InitStructure.DMA_MemoryBaseAddr = (uint32_t)adc_buffer;
DMA_InitStructure.DMA_DIR = DMA_DIR_PeripheralSRC;
DMA_InitStructure.DMA_BufferSize = 10;
DMA_InitStructure.DMA_PeripheralInc = DMA_PeripheralInc_Disable;
DMA_InitStructure.DMA_MemoryInc = DMA_MemoryInc_Enable;
DMA_Init(DMA1_Channel1, &DMA_InitStructure);
```

## 4. 应用场景
- ADC连续采集
- 串口数据接收
- SPI/I2C批量传输
""",
        code_example="""#include "stm32f10x.h"

uint16_t adc_buffer[10];

void DMA_ADC_Init(void)
{
    DMA_InitTypeDef DMA_InitStructure;
    DMA_InitStructure.DMA_PeripheralBaseAddr = (uint32_t)&ADC1->DR;
    DMA_InitStructure.DMA_MemoryBaseAddr = (uint32_t)adc_buffer;
    DMA_InitStructure.DMA_DIR = DMA_DIR_PeripheralSRC;
    DMA_InitStructure.DMA_BufferSize = 10;
    DMA_InitStructure.DMA_PeripheralInc = DMA_PeripheralInc_Disable;
    DMA_InitStructure.DMA_MemoryInc = DMA_MemoryInc_Enable;
    DMA_InitStructure.DMA_PeripheralDataSize = DMA_PeripheralDataSize_HalfWord;
    DMA_InitStructure.DMA_MemoryDataSize = DMA_MemoryDataSize_HalfWord;
    DMA_InitStructure.DMA_Mode = DMA_Mode_Circular;
    DMA_Init(DMA1_Channel1, &DMA_InitStructure);
    DMA_Cmd(DMA1_Channel1, ENABLE);
}""",
        questions=[
            {"q_id": "q_s07_1", "type": "single_choice", "content": "DMA的主要优势是？", "options": [{"id": "A", "text": "提高CPU运算速度"}, {"id": "B", "text": "不占用CPU进行数据传输"}, {"id": "C", "text": "增加内存容量"}, {"id": "D", "text": "降低功耗"}], "correct_answer": "B", "explanation": "DMA可以在不占用CPU的情况下进行数据传输，提高系统效率。"},
        ],
        mindmap={"root": "DMA数据转运", "children": [{"name": "DMA1"}, {"name": "DMA2"}, {"name": "传输方向"}, {"name": "DMA+ADC"}, {"name": "循环模式"}, {"name": "高效传输"}]},
    ),
    KnowledgePointModel(
        kp_id="kp_s08", name="UART串口通信", subject="通信协议", course="STM32嵌入式", difficulty=0.4,
        prerequisites=["kp_s01"], description="串口发送接收、中断处理、数据包协议",
        tags=["UART", "USART", "串口", "通信", "波特率"],
        document="""# UART串口通信

## 1. UART概述

UART（Universal Asynchronous Receiver/Transmitter）通用异步收发器，是最常用的串行通信接口。

### 关键参数
| 参数 | 说明 |
|------|------|
| 波特率 | 每秒传输的位数，常用9600/115200 |
| 数据位 | 5/6/7/8位，常用8位 |
| 停止位 | 1/1.5/2位，常用1位 |
| 校验位 | 无/奇/偶校验 |

## 2. 硬件连接

STM32 USART1：
- **PA9** → TX（发送）
- **PA10** → RX（接收）

USB-TTL模块：
- TXD → STM32 RXD
- RXD → STM32 TXD
- GND → GND（必须共地）

## 3. 串口配置

```c
USART_InitTypeDef USART_InitStructure;
USART_InitStructure.USART_BaudRate = 115200;
USART_InitStructure.USART_WordLength = USART_WordLength_8b;
USART_InitStructure.USART_StopBits = USART_StopBits_1;
USART_InitStructure.USART_Parity = USART_Parity_No;
USART_InitStructure.USART_Mode = USART_Mode_Tx | USART_Mode_Rx;
USART_Init(USART1, &USART_InitStructure);
USART_Cmd(USART1, ENABLE);
```

## 4. printf重定向

```c
int fputc(int ch, FILE *f)
{
    USART_SendData(USART1, ch);
    while (USART_GetFlagStatus(USART1, USART_FLAG_TXE) == RESET);
    return ch;
}
```
""",
        code_example="""#include "stm32f10x.h"
#include <stdio.h>

void USART_Init(void)
{
    RCC_APB2PeriphClockCmd(RCC_APB2Periph_USART1 | RCC_APB2Periph_GPIOA, ENABLE);
    GPIO_InitTypeDef GPIO_InitStructure;
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_AF_PP;
    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_9;
    GPIO_Init(GPIOA, &GPIO_InitStructure);
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_IN_FLOATING;
    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_10;
    GPIO_Init(GPIOA, &GPIO_InitStructure);
    USART_InitTypeDef USART_InitStructure;
    USART_InitStructure.USART_BaudRate = 115200;
    USART_InitStructure.USART_WordLength = USART_WordLength_8b;
    USART_InitStructure.USART_StopBits = USART_StopBits_1;
    USART_InitStructure.USART_Parity = USART_Parity_No;
    USART_InitStructure.USART_Mode = USART_Mode_Tx | USART_Mode_Rx;
    USART_Init(USART1, &USART_InitStructure);
    USART_Cmd(USART1, ENABLE);
}
int fputc(int ch, FILE *f)
{
    USART_SendData(USART1, ch);
    while (USART_GetFlagStatus(USART1, USART_FLAG_TXE) == RESET);
    return ch;
}
int main(void)
{
    USART_Init();
    printf("Hello STM32!\\r\\n");
    while (1) {}
}""",
        questions=[
            {"q_id": "q_s08_1", "type": "single_choice", "content": "STM32 USART1的TX引脚是？", "options": [{"id": "A", "text": "PA9"}, {"id": "B", "text": "PA10"}, {"id": "C", "text": "PA11"}, {"id": "D", "text": "PA12"}], "correct_answer": "A", "explanation": "USART1的TX引脚为PA9，RX引脚为PA10。"},
            {"q_id": "q_s08_2", "type": "single_choice", "content": "串口通信中TX和RX应该如何连接？", "options": [{"id": "A", "text": "TX接TX，RX接RX"}, {"id": "B", "text": "TX接RX，RX接TX"}, {"id": "C", "text": "随意连接"}, {"id": "D", "text": "只需要接TX"}], "correct_answer": "B", "explanation": "串口通信是交叉连接：设备A的TX接设备B的RX，反之亦然。"},
        ],
        mindmap={"root": "UART串口通信", "children": [{"name": "波特率"}, {"name": "TX/RX"}, {"name": "数据格式"}, {"name": "printf重定向"}, {"name": "中断接收"}, {"name": "数据包协议"}]},
    ),
    KnowledgePointModel(
        kp_id="kp_s09", name="I2C通信协议", subject="通信协议", course="STM32嵌入式", difficulty=0.55,
        prerequisites=["kp_s04"], description="I2C时序、软件/硬件I2C、MPU6050六轴传感器",
        tags=["I2C", "SCL", "SDA", "MPU6050", "传感器"],
        document="""# I2C通信协议

## 1. I2C概述

I2C（Inter-Integrated Circuit）是飞利浦公司开发的两线式串行通信协议。

### 特点
- 只需2根线：SCL（时钟）、SDA（数据）
- 支持多主多从
- 标准模式100kHz，快速模式400kHz

## 2. I2C时序

### 起始信号
SCL为高电平时，SDA由高电平变为低电平

### 停止信号
SCL为高电平时，SDA由低电平变为高电平

### 数据传输
- SCL低电平时，发送方改变SDA
- SCL高电平时，接收方读取SDA
- 每传输8位，接收方发送ACK（第9个时钟）

## 3. 软件I2C实现

```c
void I2C_Start(void)
{
    SDA_OUT();
    SDA_HIGH();
    SCL_HIGH();
    Delay_us(5);
    SDA_LOW();  // 起始
    Delay_us(5);
    SCL_LOW();
}
```

## 4. MPU6050六轴传感器

MPU6050通过I2C输出加速度和陀螺仪数据：
- 设备地址：0xD0（写）/ 0xD1（读）
- 加速度寄存器：0x3B~0x40
- 陀螺仪寄存器：0x43~0x48
""",
        code_example="""#include "stm32f10x.h"
#include "Delay.h"

#define MPU6050_ADDR 0xD0
void I2C_Start(void) { /* 起始信号 */ }
void I2C_Stop(void) { /* 停止信号 */ }
void MPU6050_WriteReg(uint8_t reg, uint8_t data)
{
    I2C_Start();
    I2C_SendByte(MPU6050_ADDR);
    I2C_SendByte(reg);
    I2C_SendByte(data);
    I2C_Stop();
}
void MPU6050_Init(void)
{
    MPU6050_WriteReg(0x6B, 0x80);  // 复位
    Delay_ms(100);
    MPU6050_WriteReg(0x6B, 0x00);  // 唤醒
}
int main(void)
{
    MPU6050_Init();
    while (1) { /* 读取传感器数据 */ }
}""",
        questions=[
            {"q_id": "q_s09_1", "type": "single_choice", "content": "I2C通信使用几根线？", "options": [{"id": "A", "text": "1根"}, {"id": "B", "text": "2根"}, {"id": "C", "text": "3根"}, {"id": "D", "text": "4根"}], "correct_answer": "B", "explanation": "I2C使用SCL（时钟线）和SDA（数据线）两根线。"},
            {"q_id": "q_s09_2", "type": "single_choice", "content": "MPU6050的I2C设备地址是？", "options": [{"id": "A", "text": "0x3C"}, {"id": "B", "text": "0x50"}, {"id": "C", "text": "0xD0"}, {"id": "D", "text": "0xA0"}], "correct_answer": "C", "explanation": "MPU6050的7位地址为0x68，8位写地址为0xD0。"},
        ],
        mindmap={"root": "I2C通信协议", "children": [{"name": "SCL/SDA"}, {"name": "起始信号"}, {"name": "停止信号"}, {"name": "ACK应答"}, {"name": "软件I2C"}, {"name": "MPU6050"}]},
    ),
    KnowledgePointModel(
        kp_id="kp_s10", name="SPI通信协议", subject="通信协议", course="STM32嵌入式", difficulty=0.55,
        prerequisites=["kp_s01"], description="SPI时序、软件/硬件SPI、W25Q64 Flash存储器",
        tags=["SPI", "全双工", "W25Q64", "Flash", "高速"],
        document="""# SPI通信协议

## 1. SPI概述

SPI（Serial Peripheral Interface）串行外设接口，是全双工高速通信协议。

### 特点
- 4根线：SCK（时钟）、MOSI（主出从入）、MISO（主入从出）、CS（片选）
- 全双工：可同时收发数据
- 高速：可达数十MHz
- 一主多从：每个从机需要独立CS

## 2. SPI模式

| 模式 | CPOL | CPHA | 空闲时钟 | 采样边沿 |
|------|------|------|---------|---------|
| Mode 0 | 0 | 0 | 低 | 上升沿 |
| Mode 1 | 0 | 1 | 低 | 下降沿 |
| Mode 2 | 1 | 0 | 高 | 下降沿 |
| Mode 3 | 1 | 1 | 高 | 上升沿 |

## 3. W25Q64 Flash

W25Q64是8MB SPI Flash存储器：
- 读ID：0x9F
- 读数据：0x03 + 地址
- 页编程：0x02 + 地址 + 数据
- 扇区擦除：0x20 + 地址

## 4. 硬件SPI配置

```c
SPI_InitTypeDef SPI_InitStructure;
SPI_InitStructure.SPI_Mode = SPI_Mode_Master;
SPI_InitStructure.SPI_DataSize = SPI_DataSize_8b;
SPI_InitStructure.SPI_CPOL = SPI_CPOL_Low;
SPI_InitStructure.SPI_CPHA = SPI_CPHA_1Edge;
SPI_InitStructure.SPI_NSS = SPI_NSS_Soft;
SPI_InitStructure.SPI_BaudRatePrescaler = SPI_BaudRatePrescaler_256;
SPI_Init(SPI1, &SPI_InitStructure);
```
""",
        code_example="""#include "stm32f10x.h"

uint8_t SPI_ReadID(void)
{
    uint8_t id;
    CS_LOW();
    SPI_SendData(SPI1, 0x9F);
    while (SPI_I2S_GetFlagStatus(SPI1, SPI_I2S_FLAG_RXNE) == RESET);
    SPI_ReceiveData(SPI1);  // dummy
    SPI_SendData(SPI1, 0xFF);
    while (SPI_I2S_GetFlagStatus(SPI1, SPI_I2S_FLAG_RXNE) == RESET);
    id = SPI_ReceiveData(SPI1);
    CS_HIGH();
    return id;
}
int main(void)
{
    // SPI初始化...
    uint8_t flash_id = SPI_ReadID();
    while (1) {}
}""",
        questions=[
            {"q_id": "q_s10_1", "type": "single_choice", "content": "SPI通信是全双工还是半双工？", "options": [{"id": "A", "text": "半双工"}, {"id": "B", "text": "全双工"}, {"id": "C", "text": "单工"}, {"id": "D", "text": "以上都可以"}], "correct_answer": "B", "explanation": "SPI使用独立的MOSI和MISO线，支持全双工通信。"},
        ],
        mindmap={"root": "SPI通信协议", "children": [{"name": "SCK"}, {"name": "MOSI"}, {"name": "MISO"}, {"name": "CS片选"}, {"name": "SPI模式"}, {"name": "W25Q64"}]},
    ),
    KnowledgePointModel(
        kp_id="kp_s11", name="RTC实时时钟", subject="高级外设", course="STM32嵌入式", difficulty=0.4,
        prerequisites=["kp_s01"], description="备份寄存器、RTC配置、日历功能",
        tags=["RTC", "实时时钟", "日历", "备份域", "闹钟"],
        document="""# RTC实时时钟

## 1. RTC概述

RTC（Real-Time Clock）实时时钟，可在掉电后通过备用电池继续运行。

### STM32F103 RTC特性
- 32位计数器，可记录约136年
- 使用LSE（32.768kHz）外部晶振
- 支持闹钟中断
- 位于备份域，VBAT供电可保持运行

## 2. RTC配置

### 启用备份域访问
```c
RCC_APB1PeriphClockCmd(RCC_APB1Periph_PWR | RCC_APB1Periph_BKP, ENABLE);
PWR_BackupAccessCmd(ENABLE);
```

### 配置LSE晶振
```c
RCC_LSEConfig(RCC_LSE_ON);
while (RCC_GetFlagStatus(RCC_FLAG_LSERDY) == RESET);
RCC_RTCCLKConfig(RCC_RTCCLKSource_LSE);
RCC_RTCCLKCmd(ENABLE);
```

### 设置时间
```c
RTC_SetCounter(hours * 3600 + minutes * 60 + seconds);
```

## 3. 日历功能

将秒数转换为年月日时分秒：
```c
uint32_t time = RTC_GetCounter();
uint8_t hours = time / 3600 % 24;
uint8_t minutes = time / 60 % 60;
uint8_t seconds = time % 60;
```

## 4. 闹钟中断

设置闹钟值，到达时触发中断，可用于定时唤醒。
""",
        code_example="""#include "stm32f10x.h"

void RTC_Init(void)
{
    RCC_APB1PeriphClockCmd(RCC_APB1Periph_PWR | RCC_APB1Periph_BKP, ENABLE);
    PWR_BackupAccessCmd(ENABLE);
    if (BKP_ReadBackupRegister(BKP_DR1) != 0xA5A5)
    {
        RCC_LSEConfig(RCC_LSE_ON);
        while (RCC_GetFlagStatus(RCC_FLAG_LSERDY) == RESET);
        RCC_RTCCLKConfig(RCC_RTCCLKSource_LSE);
        RCC_RTCCLKCmd(ENABLE);
        RTC_WaitForSynchro();
        RTC_WaitForLastTask();
        RTC_SetPrescaler(32767);
        RTC_WaitForLastTask();
        RTC_SetCounter(0);
        BKP_WriteBackupRegister(BKP_DR1, 0xA5A5);
    }
}
int main(void)
{
    RTC_Init();
    while (1)
    {
        uint32_t time = RTC_GetCounter();
    }
}""",
        questions=[
            {"q_id": "q_s11_1", "type": "single_choice", "content": "RTC的时钟源通常使用？", "options": [{"id": "A", "text": "HSI内部高速时钟"}, {"id": "B", "text": "HSE外部高速晶振"}, {"id": "C", "text": "LSE 32.768kHz晶振"}, {"id": "D", "text": "LSI内部低速时钟"}], "correct_answer": "C", "explanation": "RTC通常使用LSE 32.768kHz晶振，精度高且功耗低。"},
        ],
        mindmap={"root": "RTC实时时钟", "children": [{"name": "备份域"}, {"name": "LSE晶振"}, {"name": "计数器"}, {"name": "日历功能"}, {"name": "闹钟中断"}, {"name": "VBAT供电"}]},
    ),
    KnowledgePointModel(
        kp_id="kp_s12", name="低功耗模式", subject="高级外设", course="STM32嵌入式", difficulty=0.55,
        prerequisites=["kp_s08", "kp_s11"], description="睡眠、停止、待机模式配置与唤醒",
        tags=["低功耗", "睡眠", "停止", "待机", "唤醒"],
        document="""# 低功耗模式

## 1. 低功耗模式概述

STM32提供3种低功耗模式：

| 模式 | 唤醒方式 | 功耗 | 保持内容 |
|------|---------|------|---------|
| 睡眠 | 任何中断 | 较高 | 全部 |
| 停止 | 外部中断/WKUP | 极低 | SRAM和寄存器 |
| 待机 | WKUP引脚/复位 | 最低 | 仅备份域 |

## 2. 睡眠模式

CPU停止运行，但外设继续工作：
```c
SCB->SCR |= SCB_SCR_SLEEPDEEP_Msk;
__WFI();  // 等待中断唤醒
```

## 3. 停止模式

所有时钟停止，SRAM和寄存器内容保持：
```c
PWR_EnterSTOPMode(PWR_Regulator_LowPower, PWR_STOPEntry_WFI);
```

## 4. 待机模式

最低功耗，仅备份域保持：
```c
PWR_EnterSTANDBYMode();
```

## 5. 唤醒方式
- **睡眠**：任意中断
- **停止**：EXTI中断、WKUP引脚
- **待机**：WKUP引脚上升沿、复位、IWDG复位

## 6. 应用场景
- 电池供电设备：待机模式
- 定时采集：停止+RTC闹钟唤醒
- 低功耗传感器：睡眠+外部中断唤醒
""",
        code_example="""#include "stm32f10x.h"

void EnterStandbyMode(void)
{
    RCC_APB1PeriphClockCmd(RCC_APB1Periph_PWR, ENABLE);
    PWR_WakeUpPinCmd ENABLE);
    PWR_EnterSTANDBYMode();
}
int main(void)
{
    // 初始化...
    Delay_ms(5000);  // 工作5秒
    EnterStandbyMode();  // 进入待机
    // 唤醒后从头执行
}""",
        questions=[
            {"q_id": "q_s12_1", "type": "single_choice", "content": "哪种低功耗模式功耗最低？", "options": [{"id": "A", "text": "睡眠模式"}, {"id": "B", "text": "停止模式"}, {"id": "C", "text": "待机模式"}, {"id": "D", "text": "三种一样"}], "correct_answer": "C", "explanation": "待机模式功耗最低，仅备份域保持，SRAM和寄存器内容丢失。"},
        ],
        mindmap={"root": "低功耗模式", "children": [{"name": "睡眠模式"}, {"name": "停止模式"}, {"name": "待机模式"}, {"name": "WKUP唤醒"}, {"name": "EXTI唤醒"}, {"name": "应用场景"}]},
    ),
    KnowledgePointModel(
        kp_id="kp_s13", name="看门狗", subject="高级外设", course="STM32嵌入式", difficulty=0.4,
        prerequisites=["kp_s05"], description="独立看门狗、窗口看门狗配置与应用",
        tags=["看门狗", "IWDG", "WWDG", "复位", "程序监控"],
        document="""# 看门狗

## 1. 看门狗概述

看门狗（Watchdog）用于监控程序运行，防止程序跑飞或死锁。

### 两种看门狗
| 类型 | 时钟源 | 特点 |
|------|--------|------|
| IWDG独立看门狗 | LSI 40kHz | 简单，独立运行 |
| WWDG窗口看门狗 | APB1时钟 | 精确，可设窗口 |

## 2. 独立看门狗（IWDG）

### 工作原理
- 递减计数器，从重装载值递减到0时产生复位
- 必须在计数器归零前"喂狗"（重装载）
- 如果程序跑飞未喂狗，系统自动复位

### 配置
```c
IWDG_WriteAccessCmd(IWDG_WriteAccess_Enable);
IWDG_SetPrescaler(IWDG_Prescaler_64);
IWDG_SetReload(625);  // 超时时间 = 64/40000 * 625 = 1秒
IWDG_ReloadCounter();
IWDG_Enable();
```

### 喂狗
```c
IWDG_ReloadCounter();  // 在主循环中定期调用
```

## 3. 窗口看门狗（WWDG）

- 必须在窗口范围内喂狗
- 太早或太晚都会复位
- 适合对时序要求严格的场景

## 4. 应用场景
- 工业控制系统
- 汽车电子
- 任何需要高可靠性的场景
""",
        code_example="""#include "stm32f10x.h"

void IWDG_Init(void)
{
    IWDG_WriteAccessCmd(IWDG_WriteAccess_Enable);
    IWDG_SetPrescaler(IWDG_Prescaler_64);
    IWDG_SetReload(625);
    IWDG_ReloadCounter();
    IWDG_Enable();
}
int main(void)
{
    // 系统初始化...
    IWDG_Init();
    while (1)
    {
        // 正常工作...
        IWDG_ReloadCounter();  // 喂狗
        Delay_ms(500);
    }
}""",
        questions=[
            {"q_id": "q_s13_1", "type": "single_choice", "content": "看门狗的作用是？", "options": [{"id": "A", "text": "提高运算速度"}, {"id": "B", "text": "监控程序防止跑飞"}, {"id": "C", "text": "节省功耗"}, {"id": "D", "text": "增加存储空间"}], "correct_answer": "B", "explanation": "看门狗用于监控程序运行，程序跑飞未喂狗时自动复位系统。"},
        ],
        mindmap={"root": "看门狗", "children": [{"name": "IWDG"}, {"name": "WWDG"}, {"name": "喂狗"}, {"name": "重装载值"}, {"name": "系统复位"}, {"name": "程序监控"}]},
    ),
    KnowledgePointModel(
        kp_id="kp_s14", name="Flash操作", subject="高级外设", course="STM32嵌入式", difficulty=0.4,
        prerequisites=["kp_s01"], description="内部Flash读写、芯片ID读取",
        tags=["Flash", "存储器", "读写", "芯片ID", "擦除"],
        document="""# Flash操作

## 1. Flash概述

STM32F103内置Flash存储器，用于存储程序代码和数据。

### Flash特性
| 参数 | 数值 |
|------|------|
| 编程粒度 | 半字（16位） |
| 擦除粒度 | 扇区（1KB~2KB） |
| 编程时间 | 40~70μs |
| 擦写次数 | 10万次 |

## 2. 读取Flash

Flash可像内存一样直接读取：
```c
uint32_t data = *(volatile uint32_t*)0x08000000;
```

## 3. 写入Flash

### 写入步骤
1. 解锁Flash（写入密钥）
2. 擦除目标扇区
3. 逐半字写入数据
4. 锁定Flash

```c
FLASH_Unlock();
FLASH_ErasePage(FLASH_START_ADDR);
FLASH_ProgramHalfWord(FLASH_START_ADDR, 0x1234);
FLASH_Lock();
```

## 4. 读取芯片ID

每个STM32有唯一96位芯片ID：
```c
uint32_t id0 = *(uint32_t*)(0x1FFFF7E8);  // 低32位
uint32_t id1 = *(uint32_t*)(0x1FFFF7EC);  // 中32位
uint32_t id2 = *(uint32_t*)(0x1FFFF7F0);  // 高32位
```

## 5. 应用场景
- 存储配置参数
- 在线升级（IAP）
- 数据记录
- 唯一设备标识
""",
        code_example="""#include "stm32f10x.h"

#define FLASH_START_ADDR 0x08000000 + 60 * 1024  // 最后一页

void Flash_Write(uint32_t addr, uint16_t data)
{
    FLASH_Unlock();
    FLASH_ErasePage(addr);
    FLASH_ProgramHalfWord(addr, data);
    FLASH_Lock();
}
uint16_t Flash_Read(uint32_t addr)
{
    return *(volatile uint16_t*)addr;
}
void ReadChipID(void)
{
    uint32_t id0 = *(uint32_t*)(0x1FFFF7E8);
    uint32_t id1 = *(uint32_t*)(0x1FFFF7EC);
    uint32_t id2 = *(uint32_t*)(0x1FFFF7F0);
}
int main(void)
{
    ReadChipID();
    Flash_Write(FLASH_START_ADDR, 0xABCD);
    uint16_t val = Flash_Read(FLASH_START_ADDR);
    while (1) {}
}""",
        questions=[
            {"q_id": "q_s14_1", "type": "single_choice", "content": "STM32 Flash的编程粒度是？", "options": [{"id": "A", "text": "字节（8位）"}, {"id": "B", "text": "半字（16位）"}, {"id": "C", "text": "字（32位）"}, {"id": "D", "text": "扇区"}], "correct_answer": "B", "explanation": "STM32F103 Flash编程粒度为半字（16位），擦除粒度为扇区。"},
        ],
        mindmap={"root": "Flash操作", "children": [{"name": "读取Flash"}, {"name": "写入Flash"}, {"name": "擦除扇区"}, {"name": "芯片ID"}, {"name": "IAP升级"}, {"name": "参数存储"}]},
    ),
]
db.add_all(kps)
db.commit()


# ---------- 学习记录 ----------
actions = ["watch", "read", "practice", "review"]
ALL_USERS = [STUDENT_ID, STUDENT2, STUDENT3, TEST_USER, TEACHER, TOP_STUDENT, BEGINNER, COMPETITOR, STEADY]
records = []
now = datetime.now()

# 为 student_001 创建最近 7 天的学习记录（确保有连续打卡数据）
for day_offset in range(7):
    day = now - timedelta(days=day_offset)
    # 每天 2-3 条记录
    for j in range(2 + (day_offset % 2)):
        kp = kps[(day_offset * 3 + j) % len(kps)].kp_id
        records.append(LearningRecordModel(
            record_id=f"lr_day{day_offset}_{j:03d}",
            student_id=STUDENT_ID,
            kp_id=kp,
            action=actions[j % len(actions)],
            duration=1800 + j * 600,  # 30-50 分钟
            progress=min(1.0, 0.5 + j * 0.25),
            score=70 + (j % 4) * 7,
            meta={"device": "pc"},
            created_at=day.replace(hour=10 + j * 2, minute=30),
        ))

# 其他用户的记录
for i in range(60):
    sid = ALL_USERS[i % len(ALL_USERS)]
    if sid == STUDENT_ID:
        continue  # 跳过 student_001，已经单独处理
    kp = kps[i % len(kps)].kp_id
    day_offset = i % 14
    records.append(LearningRecordModel(
        record_id=f"lr_{i:03d}",
        student_id=sid,
        kp_id=kp,
        action=actions[i % len(actions)],
        duration=(i + 1) * 120,
        progress=min(1.0, (i + 1) * 0.06),
        score=60 + (i % 5) * 8,
        meta={"device": "pc"},
        created_at=now - timedelta(days=day_offset, hours=i % 12),
    ))
db.add_all(records)
db.commit()

# ---------- 测验结果 ----------
quizzes = []
for i in range(45):
    sid = ALL_USERS[i % len(ALL_USERS)]
    kp = kps[i % len(kps)].kp_id
    correct = 3 + (i % 3)
    total = 5
    day_offset = i % 14
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
        created_at=now - timedelta(days=day_offset, hours=14 + i % 8),
    ))
db.add_all(quizzes)
db.commit()

# ---------- 趋势数据 ----------
trends = []
base_date = datetime.now() - timedelta(days=14)

# 每个学生的趋势参数：(base_mastery, growth_rate, base_speed, base_efficiency, base_stability, base_factor, growth_day, intervention_msg)
trend_profiles = {
    STUDENT_ID:    (0.50, 0.020, 0.60, 0.70, 0.80, -0.20, 8, "建议加强薄弱点练习"),
    STUDENT2:      (0.70, 0.015, 0.75, 0.82, 0.88, -0.10, 5, "可以尝试更高难度题目"),
    STUDENT3:      (0.25, 0.025, 0.40, 0.50, 0.60, -0.30, 10, "建议从基础语法重新学习"),
    TEST_USER:     (0.45, 0.018, 0.55, 0.65, 0.75, -0.15, 7, "建议复习指针与内存"),
    TEACHER:       (0.95, 0.003, 0.90, 0.92, 0.95, 0.01, 0, None),
    TOP_STUDENT:   (0.85, 0.010, 0.82, 0.88, 0.92, -0.05, 3, "已超越大部分同学，保持节奏"),
    BEGINNER:      (0.10, 0.015, 0.25, 0.30, 0.40, -0.35, 12, "建议放慢节奏，多做基础练习"),
    COMPETITOR:    (0.80, 0.012, 0.85, 0.85, 0.88, -0.08, 4, "算法能力突出，注意补全基础知识"),
    STEADY:        (0.40, 0.022, 0.55, 0.62, 0.72, -0.18, 9, "稳步提升中，建议增加练习量"),
}

for i in range(14):
    d = (base_date + timedelta(days=i)).strftime("%Y-%m-%d")
    for sid, (bm, gr, bs, be, bst, bf, gi, itv) in trend_profiles.items():
        trends.append(TrendDataModel(
            student_id=sid,
            date=d,
            mastery_trend=bm + i * gr,
            speed_ratio=bs + (i % 3) * 0.03,
            time_efficiency=be - (i % 5) * 0.01,
            weakness_priority=0.4 + (i % 3) * 0.1,
            stability=bst - (i % 7) * 0.02,
            trend_factor=bf + i * 0.02,
            trend_state="growth" if i > gi else "stable",
            predicted_mastery_3d=bm + i * (gr + 0.005),
            intervention=itv if itv and i % 4 == 0 else None,
        ))
db.add_all(trends)
db.commit()

# ---------- 游戏化积分 ----------
points = [
    PointsModel(student_id=STUDENT_ID, total_points=1250, daily_points=120, weekly_points=450),
    PointsModel(student_id=STUDENT2, total_points=2100, daily_points=200, weekly_points=800),
    PointsModel(student_id=STUDENT3, total_points=350, daily_points=50, weekly_points=150),
    PointsModel(student_id=TEST_USER, total_points=880, daily_points=90, weekly_points=320),
    PointsModel(student_id=TEACHER, total_points=5000, daily_points=300, weekly_points=1200),
    PointsModel(student_id=TOP_STUDENT, total_points=4200, daily_points=250, weekly_points=1000),
    PointsModel(student_id=BEGINNER, total_points=80, daily_points=10, weekly_points=40),
    PointsModel(student_id=COMPETITOR, total_points=3800, daily_points=220, weekly_points=900),
    PointsModel(student_id=STEADY, total_points=650, daily_points=80, weekly_points=280),
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
    # 赵老师 — 教师成就
    AchievementModel(student_id=TEACHER, achievement_id="ach_001", name="初出茅庐", description="完成首个学习模块", icon="trophy"),
    AchievementModel(student_id=TEACHER, achievement_id="ach_002", name="持之以恒", description="连续打卡7天", icon="fire"),
    AchievementModel(student_id=TEACHER, achievement_id="ach_004", name="学霸", description="测验平均分超过90", icon="star"),
    AchievementModel(student_id=TEACHER, achievement_id="ach_006", name="全栈大师", description="掌握所有知识点", icon="crown"),
    AchievementModel(student_id=TEACHER, achievement_id="ach_007", name="教学先锋", description="创建10个教学案例", icon="book"),
    # 陈学霸 — 高水平成就
    AchievementModel(student_id=TOP_STUDENT, achievement_id="ach_001", name="初出茅庐", description="完成首个学习模块", icon="trophy"),
    AchievementModel(student_id=TOP_STUDENT, achievement_id="ach_002", name="持之以恒", description="连续打卡7天", icon="fire"),
    AchievementModel(student_id=TOP_STUDENT, achievement_id="ach_003", name="代码高手", description="完成10次代码练习", icon="code"),
    AchievementModel(student_id=TOP_STUDENT, achievement_id="ach_004", name="学霸", description="测验平均分超过90", icon="star"),
    AchievementModel(student_id=TOP_STUDENT, achievement_id="ach_008", name="算法王者", description="完成50道算法题", icon="crown"),
    # 刘小白 — 初学者成就
    AchievementModel(student_id=BEGINNER, achievement_id="ach_001", name="初出茅庐", description="完成首个学习模块", icon="trophy"),
    AchievementModel(student_id=BEGINNER, achievement_id="ach_009", name="勇敢迈出第一步", description="完成第一次编程练习", icon="rocket"),
    # 孙竞赛 — 竞赛成就
    AchievementModel(student_id=COMPETITOR, achievement_id="ach_001", name="初出茅庐", description="完成首个学习模块", icon="trophy"),
    AchievementModel(student_id=COMPETITOR, achievement_id="ach_002", name="持之以恒", description="连续打卡7天", icon="fire"),
    AchievementModel(student_id=COMPETITOR, achievement_id="ach_003", name="代码高手", description="完成10次代码练习", icon="code"),
    AchievementModel(student_id=COMPETITOR, achievement_id="ach_004", name="学霸", description="测验平均分超过90", icon="star"),
    AchievementModel(student_id=COMPETITOR, achievement_id="ach_008", name="算法王者", description="完成50道算法题", icon="crown"),
    AchievementModel(student_id=COMPETITOR, achievement_id="ach_010", name="竞赛达人", description="获得竞赛奖项", icon="medal"),
    # 周稳步 — 稳步前进成就
    AchievementModel(student_id=STEADY, achievement_id="ach_001", name="初出茅庐", description="完成首个学习模块", icon="trophy"),
    AchievementModel(student_id=STEADY, achievement_id="ach_002", name="持之以恒", description="连续打卡7天", icon="fire"),
    AchievementModel(student_id=STEADY, achievement_id="ach_005", name="C语言学徒", description="完成C语言概述学习", icon="code"),
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
    # 赵老师 — 教师任务
    TaskModel(student_id=TEACHER, task_id="t_010", title="审查学生进度", description="检查本周学生学习报告", task_type="daily", reward_points=100, progress=1.0, completed=True, completed_at=datetime.now()),
    TaskModel(student_id=TEACHER, task_id="t_011", title="设计期中测验", description="编写C语言期中考试题目", task_type="weekly", reward_points=200, progress=0.7, completed=False),
    # 陈学霸 — 高水平任务
    TaskModel(student_id=TOP_STUDENT, task_id="t_012", title="完成高级指针练习", description="多级指针与函数指针专项", task_type="daily", reward_points=80, progress=1.0, completed=True, completed_at=datetime.now()),
    TaskModel(student_id=TOP_STUDENT, task_id="t_013", title="LeetCode每日一题", description="完成今日LeetCode挑战", task_type="daily", reward_points=60, progress=1.0, completed=True, completed_at=datetime.now()),
    TaskModel(student_id=TOP_STUDENT, task_id="t_014", title="实现链表库", description="用C实现通用双向链表", task_type="challenge", reward_points=300, progress=0.6, completed=False),
    # 刘小白 — 初学者任务
    TaskModel(student_id=BEGINNER, task_id="t_015", title="看C语言入门视频", description="观看第一章教学视频", task_type="daily", reward_points=15, progress=0.8, completed=False),
    TaskModel(student_id=BEGINNER, task_id="t_016", title="练习Hello World", description="成功运行第一个程序", task_type="daily", reward_points=10, progress=0.0, completed=False),
    # 孙竞赛 — 竞赛任务
    TaskModel(student_id=COMPETITOR, task_id="t_017", title="每日算法训练", description="完成3道中等难度算法题", task_type="daily", reward_points=90, progress=1.0, completed=True, completed_at=datetime.now()),
    TaskModel(student_id=COMPETITOR, task_id="t_018", title="备战蓝桥杯", description="完成蓝桥杯历年真题一套", task_type="challenge", reward_points=500, progress=0.4, completed=False),
    TaskModel(student_id=COMPETITOR, task_id="t_019", title="学习动态规划", description="完成DP专题训练", task_type="weekly", reward_points=200, progress=0.7, completed=False),
    # 周稳步 — 稳步学习任务
    TaskModel(student_id=STEADY, task_id="t_020", title="阅读控制结构讲义", description="完成if/switch/循环章节", task_type="daily", reward_points=40, progress=1.0, completed=True, completed_at=datetime.now()),
    TaskModel(student_id=STEADY, task_id="t_021", title="完成指针入门练习", description="理解指针基本概念", task_type="daily", reward_points=50, progress=0.3, completed=False),
    TaskModel(student_id=STEADY, task_id="t_022", title="本周学习12小时", description="累计学习时长目标", task_type="weekly", reward_points=100, progress=0.55, completed=False),
]
db.add_all(tasks)
db.commit()

# ---------- 排行榜 ----------
leaderboard = [
    # weekly 排名（不含教师）
    LeaderboardModel(student_id=TOP_STUDENT, period="weekly", score=4200, rank=1),
    LeaderboardModel(student_id=COMPETITOR, period="weekly", score=3800, rank=2),
    LeaderboardModel(student_id=STUDENT2, period="weekly", score=2100, rank=3),
    LeaderboardModel(student_id=STUDENT_ID, period="weekly", score=1250, rank=4),
    LeaderboardModel(student_id=TEST_USER, period="weekly", score=880, rank=5),
    LeaderboardModel(student_id=STEADY, period="weekly", score=650, rank=6),
    LeaderboardModel(student_id=STUDENT3, period="weekly", score=350, rank=7),
    LeaderboardModel(student_id=BEGINNER, period="weekly", score=80, rank=8),
    # monthly 排名
    LeaderboardModel(student_id=TOP_STUDENT, period="monthly", score=16800, rank=1),
    LeaderboardModel(student_id=COMPETITOR, period="monthly", score=15200, rank=2),
    LeaderboardModel(student_id=STUDENT2, period="monthly", score=8500, rank=3),
    LeaderboardModel(student_id=STUDENT_ID, period="monthly", score=5200, rank=4),
    LeaderboardModel(student_id=TEST_USER, period="monthly", score=3200, rank=5),
    LeaderboardModel(student_id=STEADY, period="monthly", score=2600, rank=6),
    LeaderboardModel(student_id=STUDENT3, period="monthly", score=1200, rank=7),
    LeaderboardModel(student_id=BEGINNER, period="monthly", score=280, rank=8),
]
db.add_all(leaderboard)
db.commit()

# ---------- 学习日志 ----------
logs = []
# 每个学生的日志参数：(base_duration, duration_inc, base_kp, base_quiz, base_score, mistakes_key, base_progress, start_hour)
log_profiles = {
    STUDENT_ID:    (3600, 300, 2, 1, 70, "概念混淆", 0.10, "10:00"),
    STUDENT2:      (5400, 200, 4, 2, 88, "动态内存", 0.30, "09:00"),
    STUDENT3:      (1800, 150, 1, 1, 45, "语法错误", 0.05, "15:00"),
    TEST_USER:     (2400, 200, 1, 1, 65, "指针错误", 0.15, "14:00"),
    TEACHER:       (7200, 100, 6, 3, 96, None, 0.50, "08:00"),
    TOP_STUDENT:   (6000, 250, 5, 2, 92, "边界遗漏", 0.40, "08:30"),
    BEGINNER:      (900, 100, 1, 0, 30, "语法错误", 0.02, "16:00"),
    COMPETITOR:    (5400, 300, 3, 2, 85, "粗心错误", 0.35, "09:30"),
    STEADY:        (2700, 200, 2, 1, 62, "概念模糊", 0.12, "13:00"),
}
for i in range(7):
    d = (datetime.now() - timedelta(days=6 - i)).strftime("%Y-%m-%d")
    for sid, (bd, di, bk, bq, bs, mk, bp, sh) in log_profiles.items():
        logs.append(LearningLogModel(
            log_id=f"log_{sid}_{d}",
            student_id=sid,
            date=d,
            total_duration=bd + i * di,
            kp_count=bk + (i % 3),
            quiz_count=bq + (i % 2),
            avg_score=bs + i * 2,
            mistakes=[mk] if mk and i % 3 == 0 else [],
            path_progress=bp + i * 0.04,
            completed_tasks=[f"task_{j}" for j in range(max(0, i - 1))],
            timeline=[{"time": sh, "action": "read" if i % 2 == 0 else "practice", "kp_id": f"kp_c{(i % 8) + 1:02d}", "duration": 1200 + i * 200}],
        ))
db.add_all(logs)
db.commit()

# ---------- 反思记录 ----------
reflections = [
    # 张三 — 中等水平学生
    ReflectionModel(reflection_id=f"ref_{STUDENT_ID}_2026-04-14", student_id=STUDENT_ID, date="2026-04-14",
                    content="今天复习了指针的概念，对解引用运算符*的理解更深入了，但多级指针还是有点晕。",
                    mood="neutral", tags=["指针", "学习感悟"], ai_feedback="建议从简单的单级指针开始，逐步过渡到二级指针。"),
    ReflectionModel(reflection_id=f"ref_{STUDENT_ID}_2026-04-15", student_id=STUDENT_ID, date="2026-04-15",
                    content="完成了结构体的学习，发现 typedef 真的很方便，代码可读性提高了很多。",
                    mood="excited", tags=["结构体", "进步"], ai_feedback="可以尝试用结构体实现一个简单的学生管理系统。"),
    ReflectionModel(reflection_id=f"ref_{STUDENT_ID}_2026-04-16", student_id=STUDENT_ID, date="2026-04-16",
                    content="动态内存管理好难，malloc 和 free 总是配对出错，漏掉了 free 导致内存泄漏。",
                    mood="frustrated", tags=["内存管理", "困难"], ai_feedback="养成良好的习惯：malloc 后立即写下对应的 free，或者使用 RAII 思想。"),
    # 李四 — 高水平学生
    ReflectionModel(reflection_id=f"ref_{STUDENT2}_2026-04-17", student_id=STUDENT2, date="2026-04-17",
                    content="今天用文件操作实现了一个简单的日志系统，fwrite 和 fread 真的很好用！",
                    mood="happy", tags=["文件操作", "项目实战"], ai_feedback="可以尝试加入错误处理和文件加密功能。"),
    # 测试用户
    ReflectionModel(reflection_id=f"ref_{TEST_USER}_2026-04-20", student_id=TEST_USER, date="2026-04-20",
                    content="今天学习了C语言的数据类型，对int和float的精度区别有了更深的理解。",
                    mood="happy", tags=["C语言", "基础"], ai_feedback="可以尝试编写几个类型转换的小程序加深理解。"),
    ReflectionModel(reflection_id=f"ref_{TEST_USER}_2026-04-21", student_id=TEST_USER, date="2026-04-21",
                    content="指针好难啊，今天花了两个小时才搞明白指针和数组的关系。",
                    mood="neutral", tags=["C语言", "指针"], ai_feedback="指针是C语言的核心，建议多画图辅助理解内存布局。"),
    # 赵老师 — 教师反思
    ReflectionModel(reflection_id=f"ref_{TEACHER}_2026-04-18", student_id=TEACHER, date="2026-04-18",
                    content="本周批改了30份作业，发现大部分学生在指针部分存在共性问题，需要调整教学策略。",
                    mood="neutral", tags=["教学反思", "指针"], ai_feedback="建议在下周增加指针专题辅导课，配合可视化工具演示内存模型。"),
    ReflectionModel(reflection_id=f"ref_{TEACHER}_2026-04-20", student_id=TEACHER, date="2026-04-20",
                    content="新设计的C语言实验课效果不错，学生们通过实际操作理解了变量的内存布局。",
                    mood="happy", tags=["实验课", "教学改进"], ai_feedback="可以将这个实验课的设计思路推广到其他章节。"),
    # 陈学霸 — 高水平反思
    ReflectionModel(reflection_id=f"ref_{TOP_STUDENT}_2026-04-19", student_id=TOP_STUDENT, date="2026-04-19",
                    content="今天用递归实现了快速排序，时间复杂度分析已经很熟练了。接下来挑战红黑树。",
                    mood="excited", tags=["排序算法", "递归", "数据结构"], ai_feedback="红黑树的旋转操作是关键，建议先画图理解左旋和右旋。"),
    ReflectionModel(reflection_id=f"ref_{TOP_STUDENT}_2026-04-21", student_id=TOP_STUDENT, date="2026-04-21",
                    content="函数指针和回调函数终于搞懂了，qsort的实现原理比想象中优雅。",
                    mood="happy", tags=["函数指针", "回调", "标准库"], ai_feedback="可以尝试用函数指针实现一个简单的事件系统。"),
    # 刘小白 — 零基础挣扎
    ReflectionModel(reflection_id=f"ref_{BEGINNER}_2026-04-20", student_id=BEGINNER, date="2026-04-20",
                    content="第一个程序终于跑起来了！虽然只是Hello World，但看到屏幕输出的那一刻好开心。",
                    mood="excited", tags=["Hello World", "第一步"], ai_feedback="恭喜迈出第一步！接下来尝试修改程序输出自己的名字。"),
    ReflectionModel(reflection_id=f"ref_{BEGINNER}_2026-04-21", student_id=BEGINNER, date="2026-04-21",
                    content="变量好难理解啊，为什么int a = 5;后面还要加分号？总是忘。",
                    mood="frustrated", tags=["变量", "语法", "困惑"], ai_feedback="分号是C语言语句结束的标志，就像中文的句号。多写几遍就记住了。"),
    ReflectionModel(reflection_id=f"ref_{BEGINNER}_2026-04-22", student_id=BEGINNER, date="2026-04-22",
                    content="今天终于理解了if语句，原来程序可以自己做判断！写了猜数字的小程序。",
                    mood="happy", tags=["条件判断", "进步"], ai_feedback="很棒的进步！可以尝试加入else if实现更多的判断分支。"),
    # 孙竞赛 — 竞赛反思
    ReflectionModel(reflection_id=f"ref_{COMPETITOR}_2026-04-19", student_id=COMPETITOR, date="2026-04-19",
                    content="今天的动态规划训练做了一道背包问题，状态转移方程想了很久才想通。DP还是我的弱项。",
                    mood="neutral", tags=["动态规划", "背包问题", "训练"], ai_feedback="背包问题是DP的经典入门，建议从01背包开始，画表格理解状态转移过程。"),
    ReflectionModel(reflection_id=f"ref_{COMPETITOR}_2026-04-21", student_id=COMPETITOR, date="2026-04-21",
                    content="蓝桥杯省赛拿了二等奖，离一等奖差了2道题。最后两题的边界条件没处理好。",
                    mood="frustrated", tags=["蓝桥杯", "竞赛", "边界条件"], ai_feedback="边界条件是竞赛中最容易丢分的地方，建议写完代码后专门用极端数据测试。"),
    # 周稳步 — 稳步学习反思
    ReflectionModel(reflection_id=f"ref_{STEADY}_2026-04-20", student_id=STEADY, date="2026-04-20",
                    content="for循环终于搞懂了，原来循环变量的初始化、条件、递增三部分缺一不可。",
                    mood="happy", tags=["循环", "for", "进步"], ai_feedback="建议多练习不同类型的循环题目，熟练掌握循环的执行流程。"),
    ReflectionModel(reflection_id=f"ref_{STEADY}_2026-04-22", student_id=STEADY, date="2026-04-22",
                    content="指针的概念还是不太清楚，int *p = &a;这里的&和*到底是什么意思？",
                    mood="neutral", tags=["指针", "困惑"], ai_feedback="&是取地址运算符，*是解引用运算符。建议画一个内存示意图来理解。"),
]
db.add_all(reflections)
db.commit()

db.close()
print("[DONE] Seed data inserted successfully!")
print(f"   users: {len(users)}")
print(f"   profiles: {len(profiles)}")
print(f"   knowledge_points: {len(kps)}")
print(f"   learning_records: {len(records)}")
print(f"   quiz_results: {len(quizzes)}")
print(f"   trend_data: {len(trends)}")
print(f"   points: {len(points)}")
print(f"   achievements: {len(achievements)}")
print(f"   tasks: {len(tasks)}")
print(f"   leaderboard: {len(leaderboard)}")
print(f"   learning_logs: {len(logs)}")
print(f"   reflections: {len(reflections)}")
