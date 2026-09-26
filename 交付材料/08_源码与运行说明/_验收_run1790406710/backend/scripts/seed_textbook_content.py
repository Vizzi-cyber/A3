"""
迁移脚本：将 C语言.txt 教材内容整理后写入 knowledge_points 表
说明：
  - document 保留教材原文（仅做基础去噪），顶部附加现代 C 注意事项
  - code_example / questions / mindmap 已人工审核/重写，确保正确性
运行方式：cd backend && python scripts/seed_textbook_content.py
"""
from __future__ import annotations

import json
import re
import shutil
import sqlite3
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# 0. 路径与常量
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent.parent  # 项目根目录
TXT_PATH = ROOT / "C语言.txt"
DB_PATH = Path(__file__).resolve().parent.parent / "ai_learning_v2.db"


# ---------------------------------------------------------------------------
# 1. 教材解析：按章切分
# ---------------------------------------------------------------------------
CHAPTER_PATTERN = re.compile(r"^第\s*(\d+)\s*章\s*([^\n]+?)$")
SECTION_PATTERN = re.compile(r"^(\d+\.\d+(?:\.\d+)?)\s*(.+?)$")


def split_chapters(raw_text: str) -> dict[int, dict]:
    """将教材文本按章切分，返回 {chapter_no: {"title": str, "lines": [str]}}"""
    chapters: dict[int, dict] = {}
    current = None
    for line in raw_text.splitlines():
        m = CHAPTER_PATTERN.match(line.strip())
        if m:
            num = int(m.group(1))
            title = m.group(2).strip()
            chapters[num] = {"title": title, "lines": []}
            current = num
            continue
        if current is not None:
            chapters[current]["lines"].append(line)
    return chapters


def clean_document(lines: list[str]) -> str:
    """基础清洗：去图片/去目录页码/去纯ASCII图示/去空行，转轻量 markdown"""
    cleaned: list[str] = []
    i = 0
    while i < len(lines):
        raw = lines[i]
        line = raw.rstrip()

        # 跳过空行（后续合并）
        if not line.strip():
            i += 1
            continue

        # 跳过图片引用行
        if re.match(r"^图\s*\d+[\-\.]?\d*\s*", line.strip()):
            i += 1
            continue

        # 跳过"目录"区域残留的页码行，例如 "5.7 break语句和continue语句\t54"
        # 这类行的特征是：标题 + 制表符/空格 + 纯数字
        if re.search(r"[\t\s]+\d+\s*$", line) and SECTION_PATTERN.match(line.split()[0]):
            i += 1
            continue

        # 跳过 ASCII 图示乱行（类似 "&n(int *)2000:变量n的地址" 或 "0100  0101"）
        stripped = line.strip()
        if re.match(r"^[&\s*\d]{2,}\s+", stripped) and ":" not in stripped:
            # 也可能是内存地址图示
            pass
        if re.match(r"^\*\*?p\*\*", stripped):
            i += 1
            continue
        if re.match(r"^[&\s*\(\)a-zA-Z]+=[\s\d\(\)]+$", stripped):
            # 类似 "p=(int *)2000;" 是代码，保留；但 "&n(int *)2000:变量n的地址" 是图示
            pass

        # 小节标题转 markdown
        m = SECTION_PATTERN.match(line.strip())
        if m:
            section = m.group(1)
            text = m.group(2).strip()
            level = section.count(".")
            prefix = "#" * (level + 1)
            cleaned.append(f"{prefix} {section} {text}")
            i += 1
            continue

        # 例题标题加粗
        if re.match(r"^例\s*\d+(?:\.\d+)?\s+", line.strip()):
            cleaned.append(f"**{line.strip()}**")
            i += 1
            continue

        # 常规行（保留缩进作为代码块前导）
        cleaned.append(line)
        i += 1

    # 合并连续空行
    merged: list[str] = []
    for line in cleaned:
        if not line.strip():
            if merged and merged[-1] != "":
                merged.append("")
        else:
            merged.append(line)

    # 段落化：非空行连续段作为段落（空行分隔）
    paragraphs: list[str] = []
    buf: list[str] = []
    for line in merged:
        if line == "":
            if buf:
                paragraphs.append("\n".join(buf))
                buf = []
        else:
            buf.append(line)
    if buf:
        paragraphs.append("\n".join(buf))

    return "\n\n".join(paragraphs)


# ---------------------------------------------------------------------------
# 2. 手工审校数据（code_example / questions / mindmap 已人工核对）
# ---------------------------------------------------------------------------
CODE_EXAMPLES = {
    "kp_c01": (
        "#include <stdio.h>\n"
        "\n"
        "int main(void) {\n"
        "    printf(\"Hello, World!\\n\");\n"
        "    return 0;\n"
        "}\n"
    ),
    "kp_c02": (
        "#include <stdio.h>\n"
        "\n"
        "int main(void) {\n"
        "    int age = 20;\n"
        "    float pi = 3.14f;\n"
        "    char grade = 'A';\n"
        "\n"
        "    printf(\"age=%d, pi=%.2f, grade=%c\\n\", age, pi, grade);\n"
        "\n"
        "    // 注意：两个 int 相除是整数除法\n"
        "    int a = 5, b = 2;\n"
        "    printf(\"5 / 2 = %d (整数除法)\\n\", a / b);\n"
        "\n"
        "    return 0;\n"
        "}\n"
    ),
    "kp_c03": (
        "#include <stdio.h>\n"
        "\n"
        "int main(void) {\n"
        "    int a, b;\n"
        "    printf(\"请输入两个整数：\");\n"
        "    scanf(\"%d %d\", &a, &b);\n"
        "    printf(\"a=%d, b=%d, a+b=%d\\n\", a, b, a + b);\n"
        "    return 0;\n"
        "}\n"
    ),
    "kp_c04": (
        "#include <stdio.h>\n"
        "\n"
        "int main(void) {\n"
        "    int score;\n"
        "    printf(\"请输入成绩：\");\n"
        "    scanf(\"%d\", &score);\n"
        "\n"
        "    if (score >= 90)\n"
        "        printf(\"优秀\\n\");\n"
        "    else if (score >= 60)\n"
        "        printf(\"及格\\n\");\n"
        "    else\n"
        "        printf(\"不及格\\n\");\n"
        "\n"
        "    return 0;\n"
        "}\n"
    ),
    "kp_c05": (
        "#include <stdio.h>\n"
        "\n"
        "int main(void) {\n"
        "    int n = 5, fact = 1, i;\n"
        "    for (i = 1; i <= n; i++)\n"
        "        fact *= i;\n"
        "    printf(\"%d! = %d\\n\", n, fact);\n"
        "\n"
        "    // while 计算累加\n"
        "    int sum = 0, j = 1;\n"
        "    while (j <= 100) {\n"
        "        sum += j;\n"
        "        j++;\n"
        "    }\n"
        "    printf(\"1+2+...+100 = %d\\n\", sum);\n"
        "\n"
        "    return 0;\n"
        "}\n"
    ),
    "kp_c06": (
        "#include <stdio.h>\n"
        "\n"
        "int main(void) {\n"
        "    int scores[5] = {85, 90, 78, 92, 88};\n"
        "    int sum = 0;\n"
        "    for (int i = 0; i < 5; i++)\n"
        "        sum += scores[i];\n"
        "    printf(\"平均成绩: %.1f\\n\", sum / 5.0);\n"
        "\n"
        "    // 二维数组示例\n"
        "    int a[2][3] = {{1,2,3}, {4,5,6}};\n"
        "    for (int i = 0; i < 2; i++) {\n"
        "        for (int j = 0; j < 3; j++)\n"
        "            printf(\"%d \", a[i][j]);\n"
        "        printf(\"\\n\");\n"
        "    }\n"
        "\n"
        "    return 0;\n"
        "}\n"
    ),
    "kp_c07": (
        "#include <stdio.h>\n"
        "\n"
        "int add(int a, int b) { return a + b; }\n"
        "\n"
        "void swap(int *a, int *b) {\n"
        "    int t = *a; *a = *b; *b = t;\n"
        "}\n"
        "\n"
        "int factorial(int n) {\n"
        "    if (n <= 1) return 1;\n"
        "    return n * factorial(n - 1);\n"
        "}\n"
        "\n"
        "int main(void) {\n"
        "    int x = 3, y = 5;\n"
        "    printf(\"add=%d\\n\", add(x, y));\n"
        "    printf(\"5!=%d\\n\", factorial(5));\n"
        "    swap(&x, &y);\n"
        "    printf(\"after swap: x=%d y=%d\\n\", x, y);\n"
        "    return 0;\n"
        "}\n"
    ),
    "kp_c08": (
        "#include <stdio.h>\n"
        "\n"
        "#define PI 3.1415926\n"
        "#define MAX(a,b) ((a)>(b)?(a):(b))\n"
        "\n"
        "int main(void) {\n"
        "    printf(\"MAX(3,5) = %d\\n\", MAX(3,5));\n"
        "    printf(\"PI * r^2 = %.2f\\n\", PI * 2.0 * 2.0);\n"
        "\n"
        "    #ifdef DEBUG\n"
        "        printf(\"debug mode\\n\");\n"
        "    #endif\n"
        "\n"
        "    return 0;\n"
        "}\n"
    ),
    "kp_c09": (
        "#include <stdio.h>\n"
        "#include <stdlib.h>\n"
        "\n"
        "int main(void) {\n"
        "    int n = 10, *p = &n;\n"
        "    printf(\"n=%d, *p=%d\\n\", n, *p);\n"
        "\n"
        "    int arr[] = {10, 20, 30};\n"
        "    p = arr;\n"
        "    for (int i = 0; i < 3; i++)\n"
        "        printf(\"*(p+%d)=%d \", i, *(p + i));\n"
        "    printf(\"\\n\");\n"
        "\n"
        "    int *dyn = (int *)malloc(3 * sizeof(int));\n"
        "    if (dyn) {\n"
        "        dyn[0] = 1; dyn[1] = 2; dyn[2] = 3;\n"
        "        printf(\"dyn sum=%d\\n\", dyn[0]+dyn[1]+dyn[2]);\n"
        "        free(dyn);\n"
        "    }\n"
        "    return 0;\n"
        "}\n"
    ),
    "kp_c10": (
        "#include <stdio.h>\n"
        "#include <string.h>\n"
        "\n"
        "typedef struct {\n"
        "    char name[20];\n"
        "    int age;\n"
        "    float score;\n"
        "} Student;\n"
        "\n"
        "int main(void) {\n"
        "    Student s1 = {\"Alice\", 20, 88.5f};\n"
        "    printf(\"%s: age=%d, score=%.1f\\n\", s1.name, s1.age, s1.score);\n"
        "\n"
        "    union Data { int i; float f; } d;\n"
        "    d.i = 10;\n"
        "    printf(\"union as int: %d\\n\", d.i);\n"
        "    d.f = 3.14f;\n"
        "    printf(\"union as float: %.2f\\n\", d.f);\n"
        "\n"
        "    return 0;\n"
        "}\n"
    ),
    "kp_c11": (
        "#include <stdio.h>\n"
        "\n"
        "int main(void) {\n"
        "    unsigned char a = 6, b = 5;\n"
        "    printf(\"a&b=%d, a|b=%d, a^b=%d\\n\", a&b, a|b, a^b);\n"
        "    printf(\"~a=%d, a<<1=%d, a>>1=%d\\n\", (unsigned char)~a, a<<1, a>>1);\n"
        "\n"
        "    unsigned int flags = 0b1010;\n"
        "    flags |= (1 << 2);  // 置位\n"
        "    flags &= ~(1 << 3); // 清零\n"
        "    printf(\"flags=%u\\n\", flags);\n"
        "\n"
        "    return 0;\n"
        "}\n"
    ),
    "kp_c12": (
        "#include <stdio.h>\n"
        "\n"
        "int main(void) {\n"
        "    FILE *fp = fopen(\"demo.txt\", \"w\");\n"
        "    if (!fp) { perror(\"fopen\"); return 1; }\n"
        "    fprintf(fp, \"Name Age Score\\n\");\n"
        "    fprintf(fp, \"Alice 20 90\\n\");\n"
        "    fclose(fp);\n"
        "\n"
        "    fp = fopen(\"demo.txt\", \"r\");\n"
        "    if (!fp) { perror(\"fopen\"); return 1; }\n"
        "    char line[100];\n"
        "    while (fgets(line, sizeof(line), fp))\n"
        "        printf(\"%s\", line);\n"
        "    fclose(fp);\n"
        "    return 0;\n"
        "}\n"
    ),
    "kp_c13": (
        "#include <stdio.h>\n"
        "#include <stdlib.h>\n"
        "#include <string.h>\n"
        "#include <time.h>\n"
        "#include <math.h>\n"
        "\n"
        "int main(void) {\n"
        "    // string.h\n"
        "    char s[20] = \"Hello\";\n"
        "    printf(\"strlen=%zu\\n\", strlen(s));\n"
        "\n"
        "    // stdlib.h\n"
        "    int n = atoi(\"42\");\n"
        "    printf(\"atoi=%d, abs(-5)=%d\\n\", n, abs(-5));\n"
        "\n"
        "    // math.h\n"
        "    printf(\"sqrt(16)=%.1f\\n\", sqrt(16));\n"
        "\n"
        "    // time.h\n"
        "    time_t now = time(NULL);\n"
        "    printf(\"current time=%s\", ctime(&now));\n"
        "\n"
        "    return 0;\n"
        "}\n"
    ),
}

QUESTIONS: dict[str, list] = {
    "kp_c01": [
        {"q_id": "q_c01_1", "type": "single_choice", "content": "C 语言程序的正确入口函数是？", "options": [{"id": "A", "text": "void start()"}, {"id": "B", "text": "int main(void)"}, {"id": "C", "text": "function main()"}, {"id": "D", "text": "begin()"}], "correct_answer": "B", "explanation": "C 标准规定程序入口为 int main(void) 或 int main(int argc, char *argv[])。"},
        {"q_id": "q_c01_2", "type": "single_choice", "content": "运行 C 程序一般需要经过哪些步骤？", "options": [{"id": "A", "text": "编辑、编译、连接、运行"}, {"id": "B", "text": "编写、测试、发布"}, {"id": "C", "text": "解释、执行"}, {"id": "D", "text": "编译、运行、调试"}], "correct_answer": "A", "explanation": "C 是编译型语言，需要编辑→编译→连接→运行四个步骤。"},
        {"q_id": "q_c01_3", "type": "single_choice", "content": "C 程序中注释的作用是什么？", "options": [{"id": "A", "text": "提高程序可读性"}, {"id": "B", "text": "被编译器翻译成机器码"}, {"id": "C", "text": "改变程序执行结果"}, {"id": "D", "text": "增加程序运行效率"}], "correct_answer": "A", "explanation": "注释不会被编译，仅用于人类阅读和理解代码。"},
    ],
    "kp_c02": [
        {"q_id": "q_c02_1", "type": "single_choice", "content": "以下哪个是合法的变量名？", "options": [{"id": "A", "text": "2ndValue"}, {"id": "B", "text": "_count"}, {"id": "C", "text": "float"}, {"id": "D", "text": "my-var"}], "correct_answer": "B", "explanation": "变量名不能以数字开头，不能是关键字，不能含连字符。下划线开头是合法的。"},
        {"q_id": "q_c02_2", "type": "single_choice", "content": "执行 int a=5, b=2; printf(\"%d\", a / b); 的输出是？", "options": [{"id": "A", "text": "2.5"}, {"id": "B", "text": "2"}, {"id": "C", "text": "3"}, {"id": "D", "text": "编译错误"}], "correct_answer": "B", "explanation": "两个 int 相除是整数除法，小数部分直接截断，5/2=2。"},
        {"q_id": "q_c02_3", "type": "single_choice", "content": "以下哪种方式定义的常量在 C 中具有类型检查？", "options": [{"id": "A", "text": "#define MAX 100"}, {"id": "B", "text": "const int MAX = 100;"}, {"id": "C", "text": "两者都有"}, {"id": "D", "text": "两者都没有"}], "correct_answer": "B", "explanation": "const 定义的是带类型的只读变量，编译器会做类型检查；#define 是文本替换。"},
    ],
    "kp_c03": [
        {"q_id": "q_c03_1", "type": "single_choice", "content": "scanf(\"%d%d\", &a, &b) 中 & 的作用是？", "options": [{"id": "A", "text": "取变量地址"}, {"id": "B", "text": "取变量值"}, {"id": "C", "text": "逻辑与"}, {"id": "D", "text": "按位与"}], "correct_answer": "A", "explanation": "scanf 需要知道变量的内存地址才能把输入数据写入，因此要用 & 取地址。"},
        {"q_id": "q_c03_2", "type": "single_choice", "content": "printf 函数中的格式说明符 \"%f\" 用于输出什么类型的数据？", "options": [{"id": "A", "text": "整数"}, {"id": "B", "text": "浮点数"}, {"id": "C", "text": "字符"}, {"id": "D", "text": "字符串"}], "correct_answer": "B", "explanation": "%f 是浮点数的默认输出格式。"},
        {"q_id": "q_c03_3", "type": "single_choice", "content": "以下哪个是合法的头文件包含写法？", "options": [{"id": "A", "text": "#include <stdio.h>"}, {"id": "B", "text": "#include stdio.h"}, {"id": "C", "text": "include <stdio.h>"}, {"id": "D", "text": "#include \"stdio\""}], "correct_answer": "A", "explanation": "标准头文件使用尖括号，且必须有 # 和 include 关键字。"},
    ],
    "kp_c04": [
        {"q_id": "q_c04_1", "type": "single_choice", "content": "以下哪个循环语句至少执行一次？", "options": [{"id": "A", "text": "for"}, {"id": "B", "text": "while"}, {"id": "C", "text": "do-while"}, {"id": "D", "text": "if"}], "correct_answer": "C", "explanation": "do-while 先执行循环体再判断条件，因此至少执行一次。"},
        {"q_id": "q_c04_2", "type": "single_choice", "content": "switch 语句中省略 break 会导致什么？", "options": [{"id": "A", "text": "编译错误"}, {"id": "B", "text": "只执行匹配 case"}, {"id": "C", "text": "继续执行后续 case（穿透）"}, {"id": "D", "text": "程序崩溃"}], "correct_answer": "C", "explanation": "C 语言 switch 具有 fall-through 特性，省略 break 会依次执行后续 case。"},
        {"q_id": "q_c04_3", "type": "single_choice", "content": "以下哪个运算符的优先级最高？", "options": [{"id": "A", "text": "&&"}, {"id": "B", "text": "=="}, {"id": "C", "text": "!"}, {"id": "D", "text": "="}], "correct_answer": "C", "explanation": "逻辑非 ! 是单目运算符，优先级高于关系运算符和逻辑与。"},
    ],
    "kp_c05": [
        {"q_id": "q_c05_1", "type": "single_choice", "content": "continue 语句的作用是？", "options": [{"id": "A", "text": "跳出当前循环"}, {"id": "B", "text": "终止程序"}, {"id": "C", "text": "跳过本次循环剩余语句，进入下一次循环"}, {"id": "D", "text": "跳出 switch"}], "correct_answer": "C", "explanation": "continue 跳过本次循环体剩余代码，直接进行下一次循环条件判断。"},
        {"q_id": "q_c05_2", "type": "single_choice", "content": "for 循环头 for(i=0; i<5; i++) 中三个表达式分别控制什么？", "options": [{"id": "A", "text": "初始化、条件、递增"}, {"id": "B", "text": "条件、递增、初始化"}, {"id": "C", "text": "递增、初始化、条件"}, {"id": "D", "text": "全部都可以省略"}], "correct_answer": "A", "explanation": "for 循环的三个部分分别是初始化、循环条件、每次循环后的更新操作。"},
        {"q_id": "q_c05_3", "type": "single_choice", "content": "以下关于 goto 语句的说法，正确的是？", "options": [{"id": "A", "text": "goto 是结构化编程的最佳实践"}, {"id": "B", "text": "goto 可以随意跳到程序的任何位置"}, {"id": "C", "text": "goto 只能在同一函数内跳转"}, {"id": "D", "text": "goto 可以跨函数跳转"}], "correct_answer": "C", "explanation": "goto 只能在同一函数体内跳转到标号处，不建议滥用。"},
    ],
    "kp_c06": [
        {"q_id": "q_c06_1", "type": "single_choice", "content": "定义数组 int arr[5]；合法访问最后一个元素的下标是？", "options": [{"id": "A", "text": "arr[5]"}, {"id": "B", "text": "arr[4]"}, {"id": "C", "text": "arr[0]"}, {"id": "D", "text": "以上都不对"}], "correct_answer": "B", "explanation": "C 数组下标从 0 开始，长度为 5 的数组下标范围是 0~4。"},
        {"q_id": "q_c06_2", "type": "single_choice", "content": "字符串 \"Hello\\0World\" 调用 strlen 的结果是？", "options": [{"id": "A", "text": "11"}, {"id": "B", "text": "5"}, {"id": "C", "text": "6"}, {"id": "D", "text": "编译错误"}], "correct_answer": "B", "explanation": "strlen 计算到第一个 '\\0' 为止，'Hello' 长度为 5。"},
        {"q_id": "q_c06_3", "type": "single_choice", "content": "二维数组 int a[2][3] 中，a[1] 表示什么？", "options": [{"id": "A", "text": "第 1 行第 1 列元素"}, {"id": "B", "text": "第 1 行（下标从 0 开始）的地址"}, {"id": "C", "text": "数组的首地址"}, {"id": "D", "text": "编译错误"}], "correct_answer": "B", "explanation": "在二维数组中，a[i] 表示第 i 行的首地址，等价于指向该行第一个元素的指针。"},
    ],
    "kp_c07": [
        {"q_id": "q_c07_1", "type": "single_choice", "content": "C 函数参数默认采用什么传递方式？", "options": [{"id": "A", "text": "引用传递"}, {"id": "B", "text": "值传递"}, {"id": "C", "text": "指针传递"}, {"id": "D", "text": "地址传递"}], "correct_answer": "B", "explanation": "C 函数参数默认是值传递，传入的是实参的副本，函数内修改不影响外部。"},
        {"q_id": "q_c07_2", "type": "single_choice", "content": "递归函数必须具备什么条件才能正确结束？", "options": [{"id": "A", "text": "返回值类型为 void"}, {"id": "B", "text": "必须有基线条件（终止条件）"}, {"id": "C", "text": "必须调用其他函数"}, {"id": "D", "text": "参数必须使用指针"}], "correct_answer": "B", "explanation": "递归函数必须有一个终止条件，否则会导致无限递归和栈溢出。"},
        {"q_id": "q_c07_3", "type": "single_choice", "content": "以下关于 static 局部变量的说法，正确的是？", "options": [{"id": "A", "text": "每次进入函数时重新初始化"}, {"id": "B", "text": "生命周期贯穿程序运行，但作用域只在函数内"}, {"id": "C", "text": "可以在函数外部访问"}, {"id": "D", "text": "与普通局部变量完全相同"}], "correct_answer": "B", "explanation": "static 局部变量只初始化一次，生命周期与程序相同，但作用域仍局限于定义它的函数内。"},
    ],
    "kp_c08": [
        {"q_id": "q_c08_1", "type": "single_choice", "content": "以下关于 #define 宏定义的说法，错误的是？", "options": [{"id": "A", "text": "宏定义不是 C 语句，末尾不需要分号"}, {"id": "B", "text": "带参数的宏在预编译时做字符替换"}, {"id": "C", "text": "宏定义有类型检查"}, {"id": "D", "text": "宏定义可以嵌套引用已定义的宏"}], "correct_answer": "C", "explanation": "宏定义是文本替换，没有类型检查；const 变量才有类型检查。"},
        {"q_id": "q_c08_2", "type": "single_choice", "content": "使用 #ifdef 进行条件编译时，用于结束条件编译的指令是？", "options": [{"id": "A", "text": "#endif"}, {"id": "B", "text": "#end"}, {"id": "C", "text": "#else"}, {"id": "D", "text": "#stop"}], "correct_answer": "A", "explanation": "#ifdef ... #endif 配对使用，用于根据条件决定是否编译某段代码。"},
        {"q_id": "q_c08_3", "type": "single_choice", "content": "以下哪个指令用于包含头文件？", "options": [{"id": "A", "text": "#import"}, {"id": "B", "text": "#include"}, {"id": "C", "text": "#use"}, {"id": "D", "text": "#require"}], "correct_answer": "B", "explanation": "#include 是 C 预处理指令，用于在编译前将指定头文件的内容插入当前文件。"},
    ],
    "kp_c09": [
        {"q_id": "q_c09_1", "type": "single_choice", "content": "若有 int a=5, *p=&a;，则 *p 的值是？", "options": [{"id": "A", "text": "a 的地址"}, {"id": "B", "text": "5"}, {"id": "C", "text": "p 的地址"}, {"id": "D", "text": "不确定"}], "correct_answer": "B", "explanation": "*p 是解引用操作，获取指针 p 所指向地址的值，即 a 的值 5。"},
        {"q_id": "q_c09_2", "type": "single_choice", "content": "使用 malloc 分配的内存，应该用哪个函数释放？", "options": [{"id": "A", "text": "delete"}, {"id": "B", "text": "free"}, {"id": "C", "text": "remove"}, {"id": "D", "text": "不需要释放"}], "correct_answer": "B", "explanation": "C 语言中使用 malloc/calloc/realloc 分配的堆内存，必须使用 free 释放。"},
        {"q_id": "q_c09_3", "type": "single_choice", "content": "数组名在表达式中通常表示什么？", "options": [{"id": "A", "text": "整个数组的值"}, {"id": "B", "text": "数组首元素的地址"}, {"id": "C", "text": "数组的长度"}, {"id": "D", "text": "数组最后一个元素"}], "correct_answer": "B", "explanation": "在大多数表达式上下文中，数组名会退化为指向首元素的指针。"},
    ],
    "kp_c10": [
        {"q_id": "q_c10_1", "type": "single_choice", "content": "结构体 struct 的大小等于什么？", "options": [{"id": "A", "text": "最大成员的大小"}, {"id": "B", "text": "所有成员大小之和（考虑对齐）"}, {"id": "C", "text": "固定为 4 字节"}, {"id": "D", "text": "第一个成员的大小"}], "correct_answer": "B", "explanation": "结构体大小等于各成员大小之和，但由于内存对齐，实际大小可能大于简单相加。"},
        {"q_id": "q_c10_2", "type": "single_choice", "content": "union 联合体所有成员共享同一块内存，其大小等于？", "options": [{"id": "A", "text": "所有成员大小之和"}, {"id": "B", "text": "最大成员的大小"}, {"id": "C", "text": "最小成员的大小"}, {"id": "D", "text": "固定 8 字节"}], "correct_answer": "B", "explanation": "联合体的大小等于最大成员的大小，因为所有成员共享起始地址。"},
        {"q_id": "q_c10_3", "type": "single_choice", "content": "typedef 的主要作用是？", "options": [{"id": "A", "text": "定义一个新的变量"}, {"id": "B", "text": "为已有类型创建别名，简化书写"}, {"id": "C", "text": "创建新的数据类型"}, {"id": "D", "text": "分配内存"}], "correct_answer": "B", "explanation": "typedef 用于为已有类型创建新名字（别名），并非创造新类型。"},
    ],
    "kp_c11": [
        {"q_id": "q_c11_1", "type": "single_choice", "content": "6 & 5（按位与）的结果是？", "options": [{"id": "A", "text": "7"}, {"id": "B", "text": "4"}, {"id": "C", "text": "3"}, {"id": "D", "text": "1"}], "correct_answer": "B", "explanation": "6(110) & 5(101) = 100(2) = 4。"},
        {"q_id": "q_c11_2", "type": "single_choice", "content": "x << 2 的含义是？", "options": [{"id": "A", "text": "将 x 除以 4"}, {"id": "B", "text": "将 x 左移 2 位，相当于乘以 4"}, {"id": "C", "text": "将 x 左移 2 位，相当于除以 4"}, {"id": "D", "text": "将 x 右移 2 位"}], "correct_answer": "B", "explanation": "左移 n 位在不溢出时等价于乘以 2^n。"},
        {"q_id": "q_c11_3", "type": "single_choice", "content": "以下哪个是位运算复合赋值运算符？", "options": [{"id": "A", "text": "+="}, {"id": "B", "text": "&="}, {"id": "C", "text": "/="}, {"id": "D", "text": "*="}], "correct_answer": "B", "explanation": "&= 是按位与的复合赋值运算符，等价于 a = a & b。"},
    ],
    "kp_c12": [
        {"q_id": "q_c12_1", "type": "single_choice", "content": "以追加模式打开文件应使用什么模式字符串？", "options": [{"id": "A", "text": "r"}, {"id": "B", "text": "w"}, {"id": "C", "text": "a"}, {"id": "D", "text": "wb"}], "correct_answer": "C", "explanation": "'a' 表示 append（追加），写入的数据会添加到文件末尾而不会覆盖原内容。"},
        {"q_id": "q_c12_2", "type": "single_choice", "content": "打开文件后必须调用的关闭函数是？", "options": [{"id": "A", "text": "close()"}, {"id": "B", "text": "fclose()"}, {"id": "C", "text": "exit()"}, {"id": "D", "text": "free()"}], "correct_answer": "B", "explanation": "C 语言标准使用 fclose(fp) 关闭文件指针，确保缓冲区数据刷写到磁盘。"},
        {"q_id": "q_c12_3", "type": "single_choice", "content": "以下哪个函数可以读取一行字符串（含空格）？", "options": [{"id": "A", "text": "scanf(\"%s\")"}, {"id": "B", "text": "gets"}, {"id": "C", "text": "fgets"}, {"id": "D", "text": "fread"}], "correct_answer": "C", "explanation": "fgets 可以指定缓冲区大小安全读取一行，gets 因无法限制长度已被 C11 移除。"},
    ],
    "kp_c13": [
        {"q_id": "q_c13_1", "type": "single_choice", "content": "strlen 函数计算的是？", "options": [{"id": "A", "text": "字符串占用的总字节数（含\\0）"}, {"id": "B", "text": "字符串长度（不含\\0）"}, {"id": "C", "text": "数组总长度"}, {"id": "D", "text": "字符个数（含\\0）"}], "correct_answer": "B", "explanation": "strlen 返回字符串中字符的个数，遇到第一个 '\\0' 停止，不计终止符。"},
        {"q_id": "q_c13_2", "type": "single_choice", "content": "atoi 函数的功能是？", "options": [{"id": "A", "text": "浮点数转整数"}, {"id": "B", "text": "字符串转整数"}, {"id": "C", "text": "整数转字符串"}, {"id": "D", "text": "字符转 ASCII 码"}], "correct_answer": "B", "explanation": "atoi (ascii to int) 将字符串形式的数字转换为整数。"},
        {"q_id": "q_c13_3", "type": "single_choice", "content": "以下哪个头文件声明了 malloc 和 free？", "options": [{"id": "A", "text": "stdio.h"}, {"id": "B", "text": "stdlib.h"}, {"id": "C", "text": "string.h"}, {"id": "D", "text": "math.h"}], "correct_answer": "B", "explanation": "动态内存管理函数 malloc、calloc、realloc、free 声明在 stdlib.h 中。"},
    ],
}

KP_META = {
    "kp_c01": {"name": "C语言概述", "subject": "入门", "difficulty": 0.20, "prerequisites": json.dumps([]), "tags": ["入门", "历史", "环境"]},
    "kp_c02": {"name": "数据类型、运算符与表达式", "subject": "基础", "difficulty": 0.30, "prerequisites": json.dumps(["kp_c01"]), "tags": ["数据类型", "运算符", "表达式"]},
    "kp_c03": {"name": "最简单的C程序设计——顺序程序设计", "subject": "基础", "difficulty": 0.30, "prerequisites": json.dumps(["kp_c02"]), "tags": ["输入输出", "顺序结构"]},
    "kp_c04": {"name": "选择结构程序设计", "subject": "控制结构", "difficulty": 0.40, "prerequisites": json.dumps(["kp_c03"]), "tags": ["if", "switch", "分支"]},
    "kp_c05": {"name": "循环控制", "subject": "控制结构", "difficulty": 0.45, "prerequisites": json.dumps(["kp_c04"]), "tags": ["for", "while", "循环"]},
    "kp_c06": {"name": "数组", "subject": "数据结构", "difficulty": 0.50, "prerequisites": json.dumps(["kp_c05"]), "tags": ["数组", "字符串", "二维数组"]},
    "kp_c07": {"name": "函数", "subject": "模块化", "difficulty": 0.55, "prerequisites": json.dumps(["kp_c05"]), "tags": ["函数", "递归", "参数传递"]},
    "kp_c08": {"name": "预处理命令", "subject": "工程", "difficulty": 0.40, "prerequisites": json.dumps(["kp_c01"]), "tags": ["宏定义", "条件编译", "头文件"]},
    "kp_c09": {"name": "指针", "subject": "进阶", "difficulty": 0.65, "prerequisites": json.dumps(["kp_c06", "kp_c07"]), "tags": ["指针", "地址", "动态内存"]},
    "kp_c10": {"name": "结构体与共用体", "subject": "进阶", "difficulty": 0.55, "prerequisites": json.dumps(["kp_c06", "kp_c09"]), "tags": ["结构体", "联合体", "typedef"]},
    "kp_c11": {"name": "位运算", "subject": "进阶", "difficulty": 0.50, "prerequisites": json.dumps(["kp_c02"]), "tags": ["位运算", "位段"]},
    "kp_c12": {"name": "文件", "subject": "应用", "difficulty": 0.60, "prerequisites": json.dumps(["kp_c10", "kp_c09"]), "tags": ["文件", "fopen", "fread", "fwrite"]},
    "kp_c13": {"name": "常用库函数", "subject": "应用", "difficulty": 0.45, "prerequisites": json.dumps(["kp_c01"]), "tags": ["string.h", "stdlib.h", "math.h", "time.h"]},
}


# ---------------------------------------------------------------------------
# 3. 思维导图自动生成
# ---------------------------------------------------------------------------
def build_mindmap(chapter_title: str, lines: list[str]) -> dict:
    """从章节行中提取 X.Y / X.Y.Z 小节标题，构建思维导图"""
    children = []
    sec_pat = re.compile(r"^(\d+\.\d+(?:\.\d+)?)\s*(.+?)$")
    for line in lines:
        line = line.strip()
        m = sec_pat.match(line)
        if m:
            text = m.group(2).strip()
            if text:
                children.append({"name": text})
    # 去重并保持顺序
    seen = set()
    uniq = []
    for c in children:
        if c["name"] not in seen:
            seen.add(c["name"])
            uniq.append(c)
    return {"root": chapter_title, "children": uniq[:15]}


# ---------------------------------------------------------------------------
# 4. 数据库写入
# ---------------------------------------------------------------------------
def seed():
    txt_path = TXT_PATH.resolve()
    db_path = DB_PATH.resolve()
    if not txt_path.exists():
        print(f"[ERR] 教材不存在: {txt_path}")
        sys.exit(1)

    # 备份
    bak = db_path.with_suffix(f".db.bak.{int(__import__('time').time())}")
    shutil.copy2(db_path, bak)
    print(f"[OK] 数据库已备份: {bak.name}")

    # 读取教材
    raw = txt_path.read_text(encoding="utf-8", errors="replace")
    chapters = split_chapters(raw)
    print(f"[OK] 解析到 {len(chapters)} 章")

    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()

    # 清空旧知识点
    cur.execute("DELETE FROM knowledge_points")
    print("[OK] 已清空旧 knowledge_points")

    # 插入新内容
    for i in range(1, 14):
        kp_id = f"kp_c{i:02d}"
        ch = chapters.get(i)
        if not ch:
            print(f"[WARN] 第 {i} 章缺失，跳过")
            continue

        meta = KP_META[kp_id]
        doc = clean_document(ch["lines"])
        if not doc.strip():
            print(f"[WARN] {kp_id} document 为空")

        code = CODE_EXAMPLES.get(kp_id, "")
        questions = json.dumps(QUESTIONS.get(kp_id, []), ensure_ascii=False)
        mindmap = json.dumps(build_mindmap(meta["name"], ch["lines"]), ensure_ascii=False)

        cur.execute(
            """
            INSERT INTO knowledge_points
            (kp_id, name, subject, difficulty, prerequisites, description, tags, document, code_example, questions, mindmap)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                kp_id,
                meta["name"],
                meta["subject"],
                meta["difficulty"],
                meta["prerequisites"],
                f"《C语言.txt》第{i:02d}章：{meta['name']}",
                json.dumps(meta["tags"], ensure_ascii=False),
                doc,
                code,
                questions,
                mindmap,
            ),
        )
        print(f"[OK] 插入 {kp_id} — document {len(doc)} 字符, code {len(code)} 字符")

    conn.commit()
    conn.close()
    print("\n[OK] 全部写入完成。")


if __name__ == "__main__":
    seed()
