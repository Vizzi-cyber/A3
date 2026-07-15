"""
更新测试笔记内容（替换数据库中的占位/敷衍内容）
"""
import sqlite3

db = sqlite3.connect("E:/开发/软件杯A3/A3_项目框架/backend/ai_learning_v2.db")
cur = db.cursor()

updates = {
    "kb_note_student_001_1780762094663": (
        "C语言基础：变量与数据类型",
        """## 学习笔记

**记录时间**: 2026-06-06 16:08

### 变量声明与初始化

在C语言中，所有变量必须先声明后使用。声明时需指定数据类型：

```c
int age = 20;           // 整型变量
float score = 95.5;     // 浮点型变量
char grade = 'A';       // 字符型变量
double pi = 3.14159;    // 双精度浮点型
```

### 基本数据类型

| 类型 | 大小 | 范围 | 格式化符号 |
|------|------|------|-----------|
| char | 1字节 | -128~127 | %c |
| short | 2字节 | -32768~32767 | %hd |
| int | 4字节 | -21亿~21亿 | %d |
| long | 4/8字节 | 依平台而定 | %ld |
| float | 4字节 | ~6-7位精度 | %f |
| double | 8字节 | ~15-16位精度 | %lf |

### 命名规则

1. 变量名只能包含字母、数字和下划线
2. 不能以数字开头
3. 不能使用C语言关键字（如 int, float, return 等）
4. 区分大小写

### 示例

```c
#include <stdio.h>

int main() {
    int a = 10;
    int b = 20;
    int sum = a + b;

    printf("a = %d, b = %d\\n", a, b);
    printf("sum = %d\\n", sum);
    return 0;
}
```

总结：理解数据类型和变量声明是学习C语言的第一步，掌握好这些基础对后续学习指针、结构体等概念至关重要。
""",
    ),
    "kb_note_student_001_1780761969929": (
        "指针基础",
        """## 学习笔记

**记录时间**: 2026-06-06 16:06

### 什么是指针？

指针是C语言的精髓——它是一个存储内存地址的变量。通过指针可以间接访问和修改内存中的数据。

### 指针的声明与使用

```c
int a = 42;
int *p = &a;     // p 存储 a 的地址
printf("%d", *p); // 42，解引用：通过地址取值
*p = 100;         // 通过指针修改 a 的值，a 变为 100
```

- `&`：取地址运算符，获取变量的内存地址
- `*`：解引用运算符，通过地址访问对应的值

### 指针与函数参数

指针常用于函数参数传递，实现"传引用"效果：

```c
void swap(int *x, int *y) {
    int temp = *x;
    *x = *y;
    *y = temp;
}

int main() {
    int a = 5, b = 10;
    swap(&a, &b);  // 传递地址
    // 现在 a=10, b=5
    return 0;
}
```

### 注意事项

1. 指针必须初始化后才能使用，否则会成为野指针
2. NULL 指针表示不指向任何地址
3. 指针的大小在32位系统中是4字节，64位系统中是8字节
4. 不同类型的指针不能直接赋值（void* 除外）

### 总结

指针是C语言最强大也最容易出错的概念。理解指针就是理解内存地址，掌握好指针才能写出高效、灵活的C程序。
""",
    ),
    "kb_note_student_001_1780762010973": (
        "循环结构：for 循环详解",
        """## 学习笔记

**记录时间**: 2026-06-06 16:06

### for 循环语法

```c
for (初始化表达式; 条件表达式; 循环后操作) {
    // 循环体
}
```

### 执行流程

1. **初始化表达式**：只执行一次，用于声明循环变量
2. **条件表达式**：每次循环前判断，为真则执行循环体
3. **循环体**：执行需要重复的代码
4. **循环后操作**：每次循环体执行完后执行，通常用于更新变量

### 示例

```c
// 打印 1 到 10
for (int i = 1; i <= 10; i++) {
    printf("%d ", i);
}
// 输出：1 2 3 4 5 6 7 8 9 10

// 遍历数组
int arr[5] = {10, 20, 30, 40, 50};
for (int i = 0; i < 5; i++) {
    printf("arr[%d] = %d\\n", i, arr[i]);
}

// 倒序遍历
for (int i = 10; i > 0; i--) {
    printf("%d ", i);
}
// 输出：10 9 8 7 6 5 4 3 2 1
```

### 常见陷阱

1. 忘记写花括号导致循环体只有第一条语句
2. 循环条件写成赋值 `=` 而非比较 `==`
3. 死循环：条件永远为真

### 总结

for 循环是C语言中最常用的循环结构，熟练掌握 for 循环的三种表达式对编写高效代码至关重要。
""",
    ),
    "kb_note_student_001_1780569670591_82ceddc2": (
        "C语言基础语法",
        """## 学习笔记

### 基本数据类型

C语言提供以下基本数据类型：

| 类型 | 大小 | 范围 |
|------|------|------|
| char | 1字节 | -128~127 |
| short | 2字节 | -32768~32767 |
| int | 4字节 | 约±21亿 |
| long | 4/8字节 | 依平台而定 |
| float | 4字节 | 6-7位精度 |
| double | 8字节 | 15-16位精度 |

### 输入输出

```c
#include <stdio.h>

int main() {
    int num;
    printf("请输入一个整数：");
    scanf("%d", &num);
    printf("你输入的是：%d\\n", num);
    return 0;
}
```

### 运算符

- 算术运算符：`+` `-` `*` `/` `%`
- 关系运算符：`==` `!=` `>` `<` `>=` `<=`
- 逻辑运算符：`&&` `||` `!`
- 赋值运算符：`=` `+=` `-=` `*=` `/=` `%=`

### 注意事项

1. 整数除法会截断小数部分：`5 / 2 = 2`
2. `%` 运算符要求两个操作数都是整数
3. 自增自减：`i++` 先取值后自增，`++i` 先自增后取值
""",
    ),
    "kb_note_test001_1780588972620": (
        "C语言入门指南",
        """## 学习笔记

**记录时间**: 2026-06-04 16:02

### C语言概述

C语言是一门通用、面向过程的编程语言，广泛应用于系统软件、嵌入式开发等领域。学习C语言是理解计算机系统和内存管理的绝佳途径。

### 第一个程序

```c
#include <stdio.h>

int main() {
    printf("Hello, World!\\n");
    return 0;
}
```

### 编译运行

1. 编写源代码（.c文件）
2. 使用编译器编译：`gcc hello.c -o hello`
3. 运行可执行文件：`./hello`

### 学习路线

1. 基础语法（变量、数据类型、运算符）
2. 控制结构（if、switch、for、while）
3. 函数与模块化
4. 数组与字符串
5. 指针（重点难点）
6. 结构体与联合体
7. 动态内存管理
8. 文件操作
""",
    ),
    "kb_note_test001_1780590167321": (
        "后端集成指南",
        """# 后端集成指南

## 模块说明

LearnLab 后端基于 FastAPI 构建，采用模块化架构。每个功能模块由 API 路由 + Agent 智能体 + Service 服务三层组成。

## 知识库模块结构

```
backend/
├── app/api/knowledge_base.py    # 知识库路由（文件夹/笔记CRUD）
├── app/models/kb_note.py        # 数据模型（KBFolderModel, KBNoteModel）
└── app/core/database.py         # 数据库连接
```

## 注册路由

在 `backend/app/api/__init__.py` 中注册：

```python
from .knowledge_base import router as kb_router
router.include_router(kb_router, prefix="/kb", tags=["知识库"])
```

## 数据模型

### 文件夹 (KBFolderModel)
| 字段 | 类型 | 说明 |
|------|------|------|
| folder_id | VARCHAR(64) | 主键 |
| student_id | VARCHAR(64) | 所属学生 |
| name | VARCHAR(255) | 文件夹名称 |
| parent_id | VARCHAR(64) | 父文件夹ID |

### 笔记 (KBNoteModel)
| 字段 | 类型 | 说明 |
|------|------|------|
| note_id | VARCHAR(64) | 主键 |
| title | VARCHAR(255) | 笔记标题 |
| content | TEXT | Markdown内容 |
| folder_id | VARCHAR(64) | 所属文件夹 |

## API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /kb/folders | 创建文件夹 |
| GET | /kb/folders | 文件夹列表 |
| POST | /kb/notes | 创建笔记 |
| GET | /kb/notes | 笔记列表 |
| GET | /kb/notes/{id} | 笔记详情 |
| PUT | /kb/notes/{id} | 更新笔记 |
| DELETE | /kb/notes/{id} | 删除笔记 |
""",
    ),
    "kb_note_test001_1780590167597": (
        "前端集成指南",
        """# 前端集成指南

## 模块说明

LearnLab 前端基于 React 18 + TypeScript 构建，使用 Ant Design 5 作为 UI 组件库。

## 知识库前端结构

```
frontend/src/
├── pages/KnowledgeBase.tsx        # 知识库主页面
├── components/kb/
│   ├── FileTree.tsx               # 文件夹树组件
│   ├── NoteList.tsx               # 笔记列表组件
│   ├── NoteEditor.tsx             # 笔记编辑器（Markdown+WikiLink）
│   ├── BacklinksPanel.tsx         # 反向链接面板
│   ├── SearchPanel.tsx            # 全文搜索
│   └── KnowledgeGraph.tsx         # D3.js知识图谱
├── store/kbStore.ts               # Zustand状态管理
└── services/knowledgeBaseApi.ts   # API封装
```

## 安装依赖

```bash
npm install zustand antd @ant-design/icons
```

## 状态管理

使用 Zustand 管理知识库状态，包括：
- 文件夹列表和当前选中
- 笔记列表和当前编辑
- 搜索状态和结果
- 反向链接和图谱数据

## 路由配置

在 `App.tsx` 中添加：

```tsx
const KnowledgeBase = React.lazy(() => import("./pages/KnowledgeBase"));
// 路由: /knowledge-base
```
""",
    ),
    "kb_note_test001_1780590167864": (
        "API 参考文档",
        """# API 参考文档

## 知识库 API

### 文件夹管理

| 方法 | 路径 | 说明 |
|--------|------|-------------|
| POST | /kb/folders | 创建文件夹 |
| GET | /kb/folders | 文件夹列表 |
| PUT | /kb/folders/{id} | 更新文件夹 |
| DELETE | /kb/folders/{id} | 删除文件夹 |

### 笔记管理

| 方法 | 路径 | 说明 |
|--------|------|-------------|
| POST | /kb/notes | 创建笔记 |
| GET | /kb/notes | 笔记列表 |
| GET | /kb/notes/search | 搜索笔记 |
| GET | /kb/notes/{id} | 笔记详情 |
| PUT | /kb/notes/{id} | 更新笔记 |
| DELETE | /kb/notes/{id} | 删除笔记 |

### WikiLink 与图谱

| 方法 | 路径 | 说明 |
|--------|------|-------------|
| GET | /kb/wikilink/backlinks/{id} | 反向链接 |
| GET | /kb/wikilink/graph | 知识图谱 |

## 认证

所有 API 需要在 Header 中携带 JWT Token：

```
Authorization: Bearer <token>
```
""",
    ),
    "kb_note_test001_1780590176922": (
        "知识库模块概览",
        """# 知识库模块概览

## 功能描述

Obsidian 风格的知识库系统，支持文件夹管理、Markdown 笔记编辑、WikiLink 双向链接、反向链接面板和知识图谱可视化。

## 核心特性

- **文件夹树**：多级文件夹组织笔记，支持拖拽
- **Markdown 编辑器**：支持 GFM、代码高亮、数学公式
- **WikiLink 语法**：`[[笔记名]]` 快速创建链接
- **反向链接**：自动检测哪些笔记引用了当前笔记
- **知识图谱**：D3.js 力导向图展示笔记关联关系
- **全文搜索**：按标题和内容快速检索

## 模块结构

```
backend/api/knowledge_base.py   - FastAPI 路由
frontend/src/pages/KnowledgeBase.tsx - 主页面
frontend/src/store/kbStore.ts   - 状态管理
frontend/src/services/knowledgeBaseApi.ts - API 调用
```
""",
    ),
    "kb_note_student_001_1780569670605_2a5c59b1": (
        "指针进阶",
        """## 学习笔记

### 指针基础概念

指针是存储内存地址的变量。声明格式：`类型 *指针名;`

```c
int a = 42;
int *p = &a;     // p 存储 a 的地址
printf("%d", *p); // 42，解引用：通过地址取值
*p = 100;         // 通过指针修改 a 的值，a 变为 100
```

`&` 取地址运算符，`*` 解引用运算符。

### 指针的运算

指针支持算术运算：`p++` 使指针向前移动一个元素大小。

```c
int arr[5] = {1, 2, 3, 4, 5};
int *p = arr;        // p 指向 arr[0]
p++;                  // 现在指向 arr[1]
printf("%d", *p);     // 2
```

### 指针数组与数组指针

- `int *p[5]`：指针数组，包含5个int指针
- `int (*p)[5]`：数组指针，指向包含5个int的数组
""",
    ),
    "kb_note_student_001_1780569670616_48c14eb1": (
        "数组与字符串",
        """## 学习笔记

### 数组基础

数组是相同类型元素的连续集合。声明时大小必须是编译期常量（C99 VLAs 除外）：

```c
int arr[5] = {1, 2, 3};          // 未初始化元素为0
int arr2[] = {1, 2, 3, 4, 5};    // 编译器自动推断大小为5
int arr3[3][4];                   // 二维数组，3行4列
```

### 数组与指针

数组名在大多数表达式中退化为指向首元素的指针：

```c
int arr[5] = {1, 2, 3, 4, 5};
int *p = arr;      // 等效于 int *p = &arr[0];
arr[2] == *(arr+2); // 两者等价
```

### 字符串

C语言中没有专门的字符串类型，字符串以字符数组存储，以 `\\0` 结尾：

```c
char str[] = "Hello";          // 实际占用6字节（含\\0）
char *str2 = "World";          // 字符串常量，不可修改
printf("%s", str);             // 输出：Hello
```
""",
    ),
    "kb_note_student_001_1780569670626_b290f461": (
        "函数与模块化",
        """## 学习笔记

### 函数定义与声明

```c
// 函数定义
返回值类型 函数名(参数列表) {
    // 函数体
    return 返回值;
}

// 函数原型（放在头文件中）
int add(int a, int b);
```

### 模块化设计

C语言的模块化通常通过头文件(.h)和源文件(.c)分离来实现：

- 头文件(.h)：声明函数原型、宏定义、类型定义
- 源文件(.c)：实现函数定义

### 示例

```c
// add.h
int add(int a, int b);

// add.c
#include "add.h"
int add(int a, int b) {
    return a + b;
}

// main.c
#include <stdio.h>
#include "add.h"
int main() {
    printf("%d\\n", add(3, 5));  // 8
    return 0;
}
```

### 作用域与存储类别

- `auto`：局部变量（默认）
- `static`：静态变量，保持值在函数调用间持久
- `extern`：外部变量，引用其他文件的全局变量
- `register`：建议编译器存储在寄存器中
""",
    ),
    "kb_note_student_001_1780569670636_648ba85a": (
        "结构体与联合体",
        """## 学习笔记

### 结构体定义

结构体将不同类型的变量组合成一个整体：

```c
struct Student {
    char name[50];
    int age;
    float gpa;
};

// 定义并初始化
struct Student s1 = {"张三", 20, 3.8};
struct Student s2;
strcpy(s2.name, "李四");
s2.age = 21;
s2.gpa = 3.5;
```

### 结构体指针

```c
struct Student *p = &s1;
printf("%s", p->name);   // 通过指针访问成员
printf("%s", (*p).name); // 等效写法
```

### 联合体

联合体所有成员共享同一块内存，大小由最大成员决定：

```c
union Data {
    int i;
    float f;
    char str[20];
};
```
""",
    ),
}

count = 0
for note_id, (title, content) in updates.items():
    cur.execute("UPDATE kb_notes SET title = ?, content = ? WHERE note_id = ?", (title, content, note_id))
    if cur.rowcount > 0:
        count += 1
        print(f"  [OK] {note_id} -> {title[:30]}")
    else:
        print(f"  [NOT FOUND] {note_id}")

db.commit()
db.close()
print(f"\n共更新 {count} 条笔记")
