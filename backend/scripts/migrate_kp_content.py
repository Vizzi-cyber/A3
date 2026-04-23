"""
迁移脚本：将 content_library 中的硬编码内容写入 knowledge_points 表
运行方式：cd backend && python scripts/migrate_kp_content.py
"""
import sys, os, json, sqlite3

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ai_learning.db")

CONTENTS = {
    "kp_c01": {
        "document": "## C语言概述\n\nC语言由丹尼斯·里奇于1972年在贝尔实验室开发，是系统级编程的基石。\n\n### 核心特点\n- **高效性**：直接映射到机器指令，运行效率接近汇编\n- **可移植性**：ANSI C标准保证代码跨平台编译\n- **底层控制**：指针和内存管理让程序员直接操作硬件\n- **广泛应用**：Linux内核、嵌入式、数据库（MySQL/Redis）均用C编写\n\n### Hello World\n```c\n#include <stdio.h>\n\nint main() {\n    printf(\"Hello, World!\\n\");\n    return 0;\n}\n```\n\n### 程序结构\n| 部分 | 说明 |\n|------|------|\n| 预处理 | `#include`、`#define` 在编译前处理 |\n| 主函数 | `int main()` 是唯一入口 |\n| 语句 | 以分号 `;` 结尾 |\n| 返回值 | `return 0` 表示程序正常结束 |\n\n> 关键洞察：C语言的本质是**直接操作内存**。理解地址与值的关系，是掌握指针和高效编程的前提。\n",
        "code_example": "#include <stdio.h>\n\nint main() {\n    printf(\"=== C语言概述示例 ===\\n\");\n\n    // 基本数据类型的大小（与平台相关）\n    printf(\"char  占 %zu 字节\\n\", sizeof(char));\n    printf(\"int   占 %zu 字节\\n\", sizeof(int));\n    printf(\"float 占 %zu 字节\\n\", sizeof(float));\n    printf(\"double占 %zu 字节\\n\", sizeof(double));\n\n    return 0;\n}",
        "questions": json.dumps([
            {"q_id": "q_c01_1", "type": "single_choice", "content": "C语言的发明者和发明时间分别是？", "options": [{"id": "A", "text": "Dennis Ritchie，1972年"}, {"id": "B", "text": "Ken Thompson，1969年"}, {"id": "C", "text": "Bjarne Stroustrup，1979年"}, {"id": "D", "text": "James Gosling，1995年"}], "correct_answer": "A", "explanation": "C语言由丹尼斯·里奇（Dennis Ritchie）于1972年在贝尔实验室开发。"},
            {"q_id": "q_c01_2", "type": "single_choice", "content": "C语言程序的正确入口函数是？", "options": [{"id": "A", "text": "void start()"}, {"id": "B", "text": "int main()"}, {"id": "C", "text": "function main()"}, {"id": "D", "text": "begin()"}], "correct_answer": "B", "explanation": "C语言标准规定程序入口为 int main(void) 或 int main(int argc, char *argv[])。"}
        ]),
        "mindmap": json.dumps({"root": "C语言概述", "children": [{"name": "发展历史"}, {"name": "语言特点"}, {"name": "程序结构"}, {"name": "开发环境"}, {"name": "应用领域"}]}),
    },
    "kp_c02": {
        "document": "## 数据类型与变量\n\nC语言是**强类型语言**，每个变量必须先声明类型再使用。\n\n### 基本数据类型\n| 类型 | 说明 | 典型大小 |\n|------|------|---------|\n| `char` | 字符型 | 1字节 |\n| `short`| 短整型 | 2字节 |\n| `int`  | 整型 | 4字节 |\n| `long` | 长整型 | 4/8字节 |\n| `float`| 单精度浮点 | 4字节 |\n| `double`| 双精度浮点 | 8字节 |\n\n### 变量声明与初始化\n```c\nint age = 20;          // 声明并初始化\nfloat pi = 3.14159;    // 浮点数\nchar grade = 'A';      // 单引号表示字符\n```\n\n### 常量\n- `#define MAX 100` —— 宏常量，编译时替换\n- `const int MIN = 0;` —— 只读变量，有类型检查\n\n> 注意事项：变量未初始化时值为**垃圾值**（不确定），务必在首次使用前赋值。\n",
        "code_example": "#include <stdio.h>\n\nint main() {\n    // 变量声明与初始化\n    int age = 20;\n    float score = 85.5;\n    char grade = 'A';\n\n    printf(\"年龄: %d\\n\", age);\n    printf(\"成绩: %.1f\\n\", score);\n    printf(\"等级: %c\\n\", grade);\n\n    // 基本运算\n    int a = 10, b = 3;\n    printf(\"a + b = %d\\n\", a + b);\n    printf(\"a - b = %d\\n\", a - b);\n    printf(\"a * b = %d\\n\", a * b);\n    printf(\"a / b = %d\\n\", a / b);   // 整数除法，结果为 3\n    printf(\"a %% b = %d\\n\", a % b);  // 取模运算，结果为 1\n\n    return 0;\n}",
        "questions": json.dumps([
            {"q_id": "q_c02_1", "type": "single_choice", "content": "在C语言中，以下哪个是合法的变量名？", "options": [{"id": "A", "text": "2ndValue"}, {"id": "B", "text": "_count"}, {"id": "C", "text": "float"}, {"id": "D", "text": "my-var"}], "correct_answer": "B", "explanation": "变量名不能以数字开头，不能是关键字，不能包含连字符。下划线开头是合法的。"},
            {"q_id": "q_c02_2", "type": "single_choice", "content": "执行 int a = 5, b = 2; printf(\"%d\", a / b); 的输出是？", "options": [{"id": "A", "text": "2.5"}, {"id": "B", "text": "2"}, {"id": "C", "text": "3"}, {"id": "D", "text": "编译错误"}], "correct_answer": "B", "explanation": "两个 int 相除执行整数除法，小数部分直接截断，5/2 = 2。"}
        ]),
        "mindmap": json.dumps({"root": "数据类型与变量", "children": [{"name": "基本类型"}, {"name": "变量声明"}, {"name": "常量定义"}, {"name": "类型转换"}, {"name": "格式化输出"}]}),
    },
    "kp_c03": {
        "document": "## 运算符与表达式\n\nC语言提供丰富的运算符，用于算术、比较、逻辑和位运算。\n\n### 算术运算符\n`+` `-` `*` `/` `%`\n> 整数除法截断小数；取模 `%` 要求两边都是整数。\n\n### 关系与逻辑运算符\n| 运算符 | 含义 | 示例 |\n|--------|------|------|\n| `==` | 等于 | `a == b` |\n| `!=` | 不等于 | `a != b` |\n| `&&` | 逻辑与 | `a > 0 && b > 0` |\n| `||` | 逻辑或 | `a > 0 || b > 0` |\n| `!`  | 逻辑非 | `!(a == b)` |\n\n### 赋值运算符\n```c\na += 5;   // 等价于 a = a + 5;\na *= 2;   // 等价于 a = a * 2;\n```\n\n### 优先级\n括号 `()` > 单目 `!` > 算术 `*` `/` > 关系 `>` `==` > 逻辑 `&&` > 赋值 `=`\n\n> 建议：复杂表达式多用括号，避免依赖优先级记忆。\n",
        "code_example": "#include <stdio.h>\n\nint main() {\n    int a = 10, b = 3;\n\n    printf(\"算术运算:\\n\");\n    printf(\"a + b = %d\\n\", a + b);\n    printf(\"a - b = %d\\n\", a - b);\n    printf(\"a * b = %d\\n\", a * b);\n    printf(\"a / b = %d\\n\", a / b);\n    printf(\"a %% b = %d\\n\", a % b);\n\n    printf(\"\\n关系与逻辑:\\n\");\n    printf(\"a > b  : %d\\n\", a > b);    // 1 (真)\n    printf(\"a == b : %d\\n\", a == b);   // 0 (假)\n    printf(\"a>5 && b>5 : %d\\n\", a>5 && b>5); // 0\n\n    printf(\"\\n赋值运算:\\n\");\n    int c = 5;\n    c += 3;\n    printf(\"c += 3 后 c = %d\\n\", c);\n\n    return 0;\n}",
        "questions": json.dumps([
            {"q_id": "q_c03_1", "type": "single_choice", "content": "表达式 `5 % 3` 的结果是？", "options": [{"id": "A", "text": "1"}, {"id": "B", "text": "2"}, {"id": "C", "text": "1.6"}, {"id": "D", "text": "编译错误"}], "correct_answer": "B", "explanation": "5 除以 3 商 1 余 2，取模运算返回余数 2。"},
            {"q_id": "q_c03_2", "type": "single_choice", "content": "以下逻辑表达式中，当 a=0, b=5 时结果为真（1）的是？", "options": [{"id": "A", "text": "a && b"}, {"id": "B", "text": "a || b"}, {"id": "C", "text": "!b"}, {"id": "D", "text": "a == b"}], "correct_answer": "B", "explanation": "|| 是逻辑或，只要一侧为真即为真。b=5 为非零值，视为真。"}
        ]),
        "mindmap": json.dumps({"root": "运算符与表达式", "children": [{"name": "算术运算符"}, {"name": "关系运算符"}, {"name": "逻辑运算符"}, {"name": "赋值运算符"}, {"name": "位运算符"}, {"name": "优先级"}]}),
    },
    "kp_c04": {
        "document": "## 控制结构\n\n控制结构决定程序的执行流程，包括分支和循环两大类。\n\n### 分支结构\n```c\n// if-else\nif (score >= 90) {\n    printf(\"优秀\");\n} else if (score >= 60) {\n    printf(\"及格\");\n} else {\n    printf(\"不及格\");\n}\n\n// switch\nswitch (grade) {\n    case 'A': printf(\"优秀\"); break;\n    case 'B': printf(\"良好\"); break;\n    default:  printf(\"其他\"); break;\n}\n```\n\n### 循环结构\n```c\n// for 循环：已知次数\nfor (int i = 0; i < 5; i++) {\n    printf(\"%d \", i);\n}\n\n// while 循环：条件驱动\nwhile (n > 0) {\n    n--;\n}\n\n// do-while 循环：至少执行一次\ndo {\n    scanf(\"%d\", &n);\n} while (n < 0);\n```\n\n### 跳转\n- `break`：立即退出当前循环或 switch\n- `continue`：跳过本次循环剩余代码，进入下一次\n\n> 最佳实践：循环嵌套不超过3层，过深的嵌套会降低可读性。\n",
        "code_example": "#include <stdio.h>\n\nint main() {\n    // for 循环打印九九乘法表的一行\n    int n = 5;\n    printf(\"%d 的乘法表: \", n);\n    for (int i = 1; i <= 9; i++) {\n        printf(\"%d*%d=%-2d \", n, i, n * i);\n    }\n    printf(\"\\n\");\n\n    // while 计算阶乘\n    int fact = 1, m = 5;\n    int temp = m;\n    while (temp > 1) {\n        fact *= temp;\n        temp--;\n    }\n    printf(\"%d! = %d\\n\", m, fact);\n\n    // switch 判断等级\n    char grade = 'B';\n    switch (grade) {\n        case 'A': printf(\"等级: 优秀\\n\"); break;\n        case 'B': printf(\"等级: 良好\\n\"); break;\n        case 'C': printf(\"等级: 中等\\n\"); break;\n        default:  printf(\"等级: 其他\\n\"); break;\n    }\n\n    return 0;\n}",
        "questions": json.dumps([
            {"q_id": "q_c04_1", "type": "single_choice", "content": "以下哪个循环语句至少会执行一次循环体？", "options": [{"id": "A", "text": "for"}, {"id": "B", "text": "while"}, {"id": "C", "text": "do-while"}, {"id": "D", "text": "if"}], "correct_answer": "C", "explanation": "do-while 先执行循环体，再判断条件，因此至少执行一次。"},
            {"q_id": "q_c04_2", "type": "single_choice", "content": "在 switch 语句中，若省略 break，会发生什么？", "options": [{"id": "A", "text": "编译错误"}, {"id": "B", "text": "只执行匹配的 case"}, {"id": "C", "text": "继续执行后续所有 case（穿透）"}, {"id": "D", "text": "程序崩溃"}], "correct_answer": "C", "explanation": "C语言 switch 具有 fall-through 特性，省略 break 会依次执行后续 case。"}
        ]),
        "mindmap": json.dumps({"root": "控制结构", "children": [{"name": "if-else"}, {"name": "switch"}, {"name": "for循环"}, {"name": "while循环"}, {"name": "do-while"}, {"name": "break/continue"}]}),
    },
    "kp_c05": {
        "document": "## 数组与字符串\n\n数组是**相同类型数据的连续内存集合**。字符串在C语言中本质是以 `'\\0'` 结尾的字符数组。\n\n### 一维数组\n```c\nint nums[5] = {1, 2, 3, 4, 5};\nprintf(\"%d\", nums[0]);  // 访问第一个元素，输出 1\n```\n\n### 二维数组\n```c\nint matrix[2][3] = {\n    {1, 2, 3},\n    {4, 5, 6}\n};\n```\n\n### 字符串处理\n```c\nchar s1[20] = \"Hello\";\nchar s2[20] = \"World\";\nstrlen(s1);      // 求长度（不含\\0）\nstrcpy(s1, s2);  // 复制字符串\nstrcat(s1, s2);  // 拼接字符串\nstrcmp(s1, s2);  // 比较字符串\n```\n\n> 注意：C语言**不会检查数组越界**。访问 `nums[10]` 可能导致不可预知的错误，这是C语言高效但危险的代价。\n",
        "code_example": "#include <stdio.h>\n#include <string.h>\n\nint main() {\n    // 一维数组：求平均值\n    int scores[5] = {85, 90, 78, 92, 88};\n    int sum = 0;\n    for (int i = 0; i < 5; i++) {\n        sum += scores[i];\n    }\n    printf(\"平均成绩: %.1f\\n\", sum / 5.0);\n\n    // 二维数组：矩阵转置\n    int a[2][3] = {{1, 2, 3}, {4, 5, 6}};\n    printf(\"原矩阵:\\n\");\n    for (int i = 0; i < 2; i++) {\n        for (int j = 0; j < 3; j++) {\n            printf(\"%d \", a[i][j]);\n        }\n        printf(\"\\n\");\n    }\n\n    // 字符串操作\n    char str1[30] = \"C语言\";\n    char str2[30] = \"程序设计\";\n    strcat(str1, str2);\n    printf(\"拼接结果: %s\\n\", str1);\n    printf(\"长度: %zu\\n\", strlen(str1));\n\n    return 0;\n}",
        "questions": json.dumps([
            {"q_id": "q_c05_1", "type": "single_choice", "content": "定义数组 int arr[5]；合法访问最后一个元素的下标是？", "options": [{"id": "A", "text": "arr[5]"}, {"id": "B", "text": "arr[4]"}, {"id": "C", "text": "arr[0]"}, {"id": "D", "text": "以上都不对"}], "correct_answer": "B", "explanation": "C语言数组下标从0开始，长度为5的数组下标范围是 0~4。"},
            {"q_id": "q_c05_2", "type": "single_choice", "content": "字符串 \"Hello\\0World\" 调用 strlen 的结果是？", "options": [{"id": "A", "text": "11"}, {"id": "B", "text": "5"}, {"id": "C", "text": "6"}, {"id": "D", "text": "编译错误"}], "correct_answer": "B", "explanation": "strlen 计算到第一个 '\\0' 为止，'Hello' 长度为 5。"}
        ]),
        "mindmap": json.dumps({"root": "数组与字符串", "children": [{"name": "一维数组"}, {"name": "二维数组"}, {"name": "数组初始化"}, {"name": "字符串本质"}, {"name": "string.h函数"}]}),
    },
    "kp_c06": {
        "document": "## 函数\n\n函数是C语言模块化编程的基础，将复杂问题分解为可复用的代码块。\n\n### 函数定义\n```c\nint add(int a, int b) {\n    return a + b;\n}\n```\n\n### 参数传递\n- **值传递**：传递变量的副本，函数内部修改不影响外部\n- **地址传递**：传递指针，函数内部可修改外部变量\n\n### 递归函数\n函数调用自身的编程技巧，必须有明确的终止条件。\n```c\nint factorial(int n) {\n    if (n <= 1) return 1;\n    return n * factorial(n - 1);\n}\n```\n\n### 作用域\n- 局部变量：在函数/块内定义，离开即销毁\n- 全局变量：在所有函数外定义，整个文件可见\n- `static`：静态变量，生命周期贯穿程序运行，作用域不变\n\n> 建议：优先使用值传递保证数据安全；需要修改外部数据时使用指针显式传递地址。\n",
        "code_example": "#include <stdio.h>\n\n// 函数声明\nint add(int a, int b);\nint factorial(int n);\nvoid swap(int *a, int *b);\n\nint main() {\n    printf(\"3 + 5 = %d\\n\", add(3, 5));\n    printf(\"5! = %d\\n\", factorial(5));\n\n    int x = 10, y = 20;\n    printf(\"交换前: x=%d, y=%d\\n\", x, y);\n    swap(&x, &y);\n    printf(\"交换后: x=%d, y=%d\\n\", x, y);\n\n    return 0;\n}\n\nint add(int a, int b) {\n    return a + b;\n}\n\nint factorial(int n) {\n    if (n <= 1) return 1;\n    return n * factorial(n - 1);\n}\n\nvoid swap(int *a, int *b) {\n    int temp = *a;\n    *a = *b;\n    *b = temp;\n}",
        "questions": json.dumps([
            {"q_id": "q_c06_1", "type": "single_choice", "content": "C语言函数参数默认采用什么传递方式？", "options": [{"id": "A", "text": "引用传递"}, {"id": "B", "text": "值传递"}, {"id": "C", "text": "指针传递"}, {"id": "D", "text": "地址传递"}], "correct_answer": "B", "explanation": "C语言函数参数默认是值传递，传入的是实参的副本。"},
            {"q_id": "q_c06_2", "type": "single_choice", "content": "递归函数必须具备什么条件才能正确结束？", "options": [{"id": "A", "text": "返回值类型为 void"}, {"id": "B", "text": "必须有基线条件（终止条件）"}, {"id": "C", "text": "必须调用其他函数"}, {"id": "D", "text": "参数必须使用指针"}], "correct_answer": "B", "explanation": "递归必须有终止条件，否则会导致无限递归和栈溢出。"}
        ]),
        "mindmap": json.dumps({"root": "函数", "children": [{"name": "函数定义"}, {"name": "参数传递"}, {"name": "返回值"}, {"name": "递归"}, {"name": "作用域"}, {"name": "static变量"}]}),
    },
    "kp_c07": {
        "document": "## 指针\n\n指针是C语言的灵魂，也是最难掌握的概念。指针即**内存地址**。\n\n### 基本概念\n```c\nint a = 10;\nint *p = &a;   // p 存储 a 的地址\nprintf(\"%d\", *p);  // 解引用，输出 10\n```\n\n### 指针与数组\n数组名本质是首元素地址。\n```c\nint arr[3] = {10, 20, 30};\nint *p = arr;\nprintf(\"%d\", *(p + 1));  // 等价于 arr[1]，输出 20\n```\n\n### 指针与函数\n通过指针可以实现\"按引用传递\"，让函数修改外部变量。\n\n### 动态内存分配\n```c\nint *p = (int *)malloc(5 * sizeof(int));\nfree(p);  // 用完必须释放，防止内存泄漏\n```\n\n> 关键洞察：`*` 在声明中表示\"指针\"，在表达式中表示\"解引用\"；`&` 表示\"取地址\"。\n",
        "code_example": "#include <stdio.h>\n#include <stdlib.h>\n\nint main() {\n    int a = 100;\n    int *p = &a;\n\n    printf(\"a 的值: %d\\n\", a);\n    printf(\"a 的地址: %p\\n\", (void*)&a);\n    printf(\"p 的值（即a的地址）: %p\\n\", (void*)p);\n    printf(\"p 指向的值: %d\\n\", *p);\n\n    // 指针与数组\n    int arr[] = {10, 20, 30};\n    int *pa = arr;\n    printf(\"\\n通过指针遍历数组:\\n\");\n    for (int i = 0; i < 3; i++) {\n        printf(\"arr[%d] = %d\\n\", i, *(pa + i));\n    }\n\n    // 动态内存\n    int *dyn = (int *)malloc(3 * sizeof(int));\n    if (dyn) {\n        dyn[0] = 1; dyn[1] = 2; dyn[2] = 3;\n        printf(\"\\n动态数组求和: %d\\n\", dyn[0] + dyn[1] + dyn[2]);\n        free(dyn);\n    }\n\n    return 0;\n}",
        "questions": json.dumps([
            {"q_id": "q_c07_1", "type": "single_choice", "content": "若有 int a=5, *p=&a;，则 *p 的值是？", "options": [{"id": "A", "text": "a 的地址"}, {"id": "B", "text": "5"}, {"id": "C", "text": "p 的地址"}, {"id": "D", "text": "不确定"}], "correct_answer": "B", "explanation": "*p 是解引用操作，获取指针 p 所指向地址的值，即 a 的值 5。"},
            {"q_id": "q_c07_2", "type": "single_choice", "content": "使用 malloc 分配的内存，应该使用什么函数释放？", "options": [{"id": "A", "text": "delete"}, {"id": "B", "text": "free"}, {"id": "C", "text": "remove"}, {"id": "D", "text": "不需要释放"}], "correct_answer": "B", "explanation": "C语言中使用 malloc/calloc/realloc 分配的堆内存，必须使用 free 释放。"}
        ]),
        "mindmap": json.dumps({"root": "指针", "children": [{"name": "地址与解引用"}, {"name": "指针与数组"}, {"name": "指针与函数"}, {"name": "动态内存"}, {"name": "指针运算"}]}),
    },
    "kp_c08": {
        "document": "## 结构体与联合体\n\n结构体（struct）允许将不同类型的数据组合成一个整体，是面向对象思想的雏形。\n\n### 结构体定义与使用\n```c\nstruct Student {\n    char name[20];\n    int age;\n    float score;\n};\n\nstruct Student s1 = {\"Alice\", 20, 90.5};\nprintf(\"%s: %.1f\", s1.name, s1.score);\n```\n\n### typedef 简化\n```c\ntypedef struct Student {\n    char name[20];\n    int age;\n} Stu;\n\nStu s1;  // 无需再写 struct\n```\n\n### 联合体（union）\n所有成员共享同一块内存，大小等于最大成员的大小。\n```c\nunion Data {\n    int i;\n    float f;\n};\n```\n\n### 枚举（enum）\n```c\nenum Color { RED, GREEN, BLUE };\nenum Color c = RED;\n```\n\n> 应用场景：结构体用于描述实体记录（学生、商品）；联合体用于节省内存的互斥数据；枚举用于状态标识。\n",
        "code_example": "#include <stdio.h>\n#include <string.h>\n\ntypedef struct {\n    char name[20];\n    int age;\n    float score;\n} Student;\n\nunion Data {\n    int i;\n    float f;\n};\n\nint main() {\n    Student s1;\n    strcpy(s1.name, \"张三\");\n    s1.age = 21;\n    s1.score = 88.5;\n    printf(\"学生: %s, 年龄: %d, 成绩: %.1f\\n\", s1.name, s1.age, s1.score);\n\n    union Data d;\n    d.i = 10;\n    printf(\"union 作为 int: %d\\n\", d.i);\n    d.f = 3.14;\n    printf(\"union 作为 float: %.2f\\n\", d.f);\n    printf(\"union 大小: %zu（等于最大成员大小）\\n\", sizeof(d));\n\n    return 0;\n}",
        "questions": json.dumps([
            {"q_id": "q_c08_1", "type": "single_choice", "content": "结构体 struct 的大小等于什么？", "options": [{"id": "A", "text": "最大成员的大小"}, {"id": "B", "text": "所有成员大小之和（考虑对齐）"}, {"id": "C", "text": "固定为 4 字节"}, {"id": "D", "text": "第一个成员的大小"}], "correct_answer": "B", "explanation": "结构体大小等于各成员大小之和，但由于内存对齐，实际大小可能大于简单相加。"},
            {"q_id": "q_c08_2", "type": "single_choice", "content": "union 联合体所有成员共享同一块内存，其大小等于？", "options": [{"id": "A", "text": "所有成员大小之和"}, {"id": "B", "text": "最大成员的大小"}, {"id": "C", "text": "最小成员的大小"}, {"id": "D", "text": "固定 8 字节"}], "correct_answer": "B", "explanation": "联合体的大小等于最大成员的大小，因为所有成员共享起始地址。"}
        ]),
        "mindmap": json.dumps({"root": "结构体与联合体", "children": [{"name": "struct定义"}, {"name": "typedef"}, {"name": "嵌套结构体"}, {"name": "union共享内存"}, {"name": "enum枚举"}]}),
    },
    "kp_c09": {
        "document": "## 文件操作\n\nC语言通过标准库函数实现文件的读写，核心概念是**文件指针（FILE*）**。\n\n### 打开与关闭\n```c\nFILE *fp = fopen(\"data.txt\", \"r\");  // r读 w写 a追加\nif (fp == NULL) {\n    printf(\"打开失败\");\n    return 1;\n}\nfclose(fp);\n```\n\n### 读写方式\n| 函数 | 功能 | 示例 |\n|------|------|------|\n| `fscanf` / `fprintf` | 格式化读写 | 类似 scanf/printf |\n| `fgets` / `fputs` | 按行读写 | 读取一行字符串 |\n| `fread` / `fwrite` | 二进制块读写 | 读写结构体数组 |\n| `fgetc` / `fputc` | 字符读写 | 逐个字符处理 |\n\n### 文件定位\n```c\nfseek(fp, 0, SEEK_SET);  // 定位到文件开头\nftell(fp);               // 获取当前位置\nrewind(fp);              // 回到开头\n```\n\n> 注意：文件操作后必须 `fclose`，否则数据可能只留在缓冲区而未写入磁盘。\n",
        "code_example": "#include <stdio.h>\n\nint main() {\n    // 写入文件\n    FILE *fp = fopen(\"demo.txt\", \"w\");\n    if (!fp) {\n        printf(\"无法创建文件\\n\");\n        return 1;\n    }\n    fprintf(fp, \"姓名 年龄 成绩\\n\");\n    fprintf(fp, \"Alice 20 90.5\\n\");\n    fprintf(fp, \"Bob 21 85.0\\n\");\n    fclose(fp);\n    printf(\"写入完成\\n\");\n\n    // 读取文件\n    fp = fopen(\"demo.txt\", \"r\");\n    if (!fp) {\n        printf(\"无法打开文件\\n\");\n        return 1;\n    }\n    char line[100];\n    printf(\"\\n文件内容:\\n\");\n    while (fgets(line, sizeof(line), fp)) {\n        printf(\"%s\", line);\n    }\n    fclose(fp);\n\n    return 0;\n}",
        "questions": json.dumps([
            {"q_id": "q_c09_1", "type": "single_choice", "content": "以追加模式打开文件应使用什么模式字符串？", "options": [{"id": "A", "text": "r"}, {"id": "B", "text": "w"}, {"id": "C", "text": "a"}, {"id": "D", "text": "wb"}], "correct_answer": "C", "explanation": "'a' 表示 append（追加），写入的数据会添加到文件末尾而不会覆盖原内容。"},
            {"q_id": "q_c09_2", "type": "single_choice", "content": "打开文件后必须调用的关闭函数是？", "options": [{"id": "A", "text": "close()"}, {"id": "B", "text": "fclose()"}, {"id": "C", "text": "exit()"}, {"id": "D", "text": "free()"}], "correct_answer": "B", "explanation": "C语言标准使用 fclose(fp) 关闭文件指针，确保缓冲区数据刷写到磁盘。"}
        ]),
        "mindmap": json.dumps({"root": "文件操作", "children": [{"name": "打开关闭"}, {"name": "格式化读写"}, {"name": "二进制读写"}, {"name": "字符/行读写"}, {"name": "文件定位"}]}),
    },
    "kp_c10": {
        "document": "## 预处理与内存管理\n\n预处理指令在编译前由预处理器处理，内存管理则涉及堆空间的申请与释放。\n\n### 宏定义\n```c\n#define PI 3.14159\n#define MAX(a,b) ((a)>(b)?(a):(b))  // 带参数的宏，注意括号\n```\n\n### 条件编译\n```c\n#ifdef DEBUG\n    printf(\"调试信息\");\n#endif\n```\n\n### 动态内存管理\n| 函数 | 功能 |\n|------|------|\n| `malloc(n)` | 分配 n 字节，不初始化 |\n| `calloc(n,size)` | 分配 n*size 字节，初始化为 0 |\n| `realloc(ptr,new_size)` | 重新分配内存大小 |\n| `free(ptr)` | 释放 malloc 申请的内存 |\n\n### 常见错误\n- **内存泄漏**：malloc 后未 free\n- **野指针**：free 后未置 NULL，再次使用\n- **越界访问**：写入超出分配范围的地址\n\n> 原则：谁申请谁释放；释放后置空；申请后检查返回值是否为 NULL。\n",
        "code_example": "#include <stdio.h>\n#include <stdlib.h>\n\n#define SQUARE(x) ((x) * (x))\n\nint main() {\n    // 宏定义示例\n    int a = 5;\n    printf(\"SQUARE(%d) = %d\\n\", a, SQUARE(a));\n\n    // 动态内存管理\n    int n = 5;\n    int *arr = (int *)calloc(n, sizeof(int));  // 初始化为0\n    if (arr == NULL) {\n        printf(\"内存分配失败\\n\");\n        return 1;\n    }\n\n    printf(\"calloc 初始化后的数组:\");\n    for (int i = 0; i < n; i++) {\n        printf(\" %d\", arr[i]);\n    }\n    printf(\"\\n\");\n\n    // 重新分配\n    int *new_arr = (int *)realloc(arr, 10 * sizeof(int));\n    if (new_arr) {\n        arr = new_arr;\n        printf(\"realloc 后容量扩大到 10\\n\");\n    }\n\n    free(arr);\n    arr = NULL;  // 避免野指针\n    printf(\"内存已释放并置空\\n\");\n\n    return 0;\n}",
        "questions": json.dumps([
            {"q_id": "q_c10_1", "type": "single_choice", "content": "malloc 与 calloc 的主要区别是什么？", "options": [{"id": "A", "text": "malloc 可以分配更大内存"}, {"id": "B", "text": "calloc 会初始化内存为0，malloc不会"}, {"id": "C", "text": "malloc 是标准函数，calloc不是"}, {"id": "D", "text": "没有区别"}], "correct_answer": "B", "explanation": "calloc 在分配内存后会将所有位初始化为 0，而 malloc 分配的内存值为未定义（垃圾值）。"},
            {"q_id": "q_c10_2", "type": "single_choice", "content": "以下哪种情况会导致内存泄漏？", "options": [{"id": "A", "text": "malloc 后调用了 free"}, {"id": "B", "text": "使用局部变量数组"}, {"id": "C", "text": "malloc 后未调用 free，且指针丢失"}, {"id": "D", "text": "使用 const 变量"}], "correct_answer": "C", "explanation": "内存泄漏指动态分配的内存不再被任何指针引用，且未被释放，导致系统内存浪费。"}
        ]),
        "mindmap": json.dumps({"root": "预处理与内存管理", "children": [{"name": "宏定义"}, {"name": "条件编译"}, {"name": "头文件包含"}, {"name": "malloc/calloc"}, {"name": "realloc/free"}, {"name": "内存泄漏"}]}),
    },
}


def migrate():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # 检查列是否存在（SQLite 不直接支持 IF NOT EXISTS）
    cur.execute("PRAGMA table_info(knowledge_points)")
    cols = [c[1] for c in cur.fetchall()]

    # 增加新列
    new_cols = ["document", "code_example", "questions", "mindmap"]
    for col in new_cols:
        if col not in cols:
            cur.execute(f'ALTER TABLE knowledge_points ADD COLUMN {col} TEXT')
            print(f"[+] 添加列: {col}")
        else:
            print(f"[*] 列已存在: {col}")

    # 插入/更新内容
    for kp_id, data in CONTENTS.items():
        cur.execute("SELECT 1 FROM knowledge_points WHERE kp_id = ?", (kp_id,))
        if cur.fetchone():
            cur.execute(
                "UPDATE knowledge_points SET document=?, code_example=?, questions=?, mindmap=? WHERE kp_id=?",
                (data["document"], data["code_example"], data.get("questions"), data.get("mindmap"), kp_id)
            )
            print(f"[OK] 更新 {kp_id}")
        else:
            # 如果知识点不存在，插入基础记录
            cur.execute(
                "INSERT INTO knowledge_points (kp_id, name, subject, difficulty, prerequisites, description, tags, document, code_example, questions, mindmap) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (kp_id, f"知识点 {kp_id}", "编程基础", 0.3, '[]', '', '[]', data["document"], data["code_example"], data.get("questions"), data.get("mindmap"))
            )
            print(f"[+] 插入 {kp_id}")

    conn.commit()
    conn.close()
    print("\n[OK] 迁移完成。")


if __name__ == "__main__":
    migrate()
