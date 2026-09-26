"""
从 dotcpp.com / matiji.net 收集的 C 语言练习题写入知识库
题目按知识点分类，用于每日推送练习
运行方式：cd backend && python scripts/seed_practice_problems.py
"""
from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "ai_learning_v2.db"

# ---------------------------------------------------------------------------
# dotcpp.com 零基础入门 + 谭浩强C语言 + matiji.net 整理的 C 语言练习题
# 按知识点分组，每组包含不同难度的题目
# ---------------------------------------------------------------------------

PRACTICE_PROBLEMS = {
    # ===== 输入输出 =====
    "kp_c03": {
        "source": "dotcpp.com 编程零基础入门",
        "problems": [
            {
                "problem_id": "dotcpp_2749",
                "title": "Hello, World!",
                "difficulty": 1,
                "source": "dotcpp",
                "type": "编程题",
                "content": "输出 Hello, World!",
                "hint": "使用 printf 函数",
                "tags": ["输入输出", "入门"],
            },
            {
                "problem_id": "dotcpp_1806",
                "title": "输入输出练习之第二个数字",
                "difficulty": 1,
                "source": "dotcpp",
                "type": "编程题",
                "content": "读入三个整数，输出第二个数字。",
                "hint": "使用 scanf 读入三个整数，输出第二个",
                "tags": ["输入输出", "scanf"],
            },
            {
                "problem_id": "dotcpp_1807",
                "title": "输入输出练习之格式控制",
                "difficulty": 1,
                "source": "dotcpp",
                "type": "编程题",
                "content": "读入两个整数a,b，按格式输出。",
                "hint": "注意 printf 的格式控制符",
                "tags": ["输入输出", "格式控制"],
            },
            {
                "problem_id": "dotcpp_1808",
                "title": "精度控制1",
                "difficulty": 2,
                "source": "dotcpp",
                "type": "编程题",
                "content": "读入一个浮点数，输出保留2位小数的结果。",
                "hint": "使用 %.2f 格式控制",
                "tags": ["输入输出", "精度控制"],
            },
            {
                "problem_id": "dotcpp_1267",
                "title": "A+B Problem",
                "difficulty": 1,
                "source": "dotcpp",
                "type": "编程题",
                "content": "读入两个整数a和b，输出它们的和。",
                "hint": "最基础的输入输出练习",
                "tags": ["输入输出", "入门"],
            },
        ],
    },
    # ===== 数据类型与变量 =====
    "kp_c02": {
        "source": "dotcpp.com 变量定义赋值及转换",
        "problems": [
            {
                "problem_id": "dotcpp_2752",
                "title": "整型数据类型存储空间大小",
                "difficulty": 1,
                "source": "dotcpp",
                "type": "编程题",
                "content": "分别定义short, int, long, long long类型的变量，使用sizeof运算符输出它们的字节大小。",
                "hint": "sizeof(type) 返回字节数",
                "tags": ["数据类型", "sizeof"],
            },
            {
                "problem_id": "dotcpp_2753",
                "title": "浮点型数据类型存储空间大小",
                "difficulty": 1,
                "source": "dotcpp",
                "type": "编程题",
                "content": "定义float和double类型的变量，输出它们的字节大小。",
                "hint": "float通常4字节，double通常8字节",
                "tags": ["数据类型", "浮点"],
            },
            {
                "problem_id": "dotcpp_2755",
                "title": "类型转换1",
                "difficulty": 2,
                "source": "dotcpp",
                "type": "编程题",
                "content": "读入一个整数，将其转换为浮点数输出，保留2位小数。",
                "hint": "使用强制类型转换 (float)",
                "tags": ["数据类型", "类型转换"],
            },
            {
                "problem_id": "matiji_001",
                "title": "变量交换",
                "difficulty": 2,
                "source": "matiji",
                "type": "编程题",
                "content": "读入两个整数a和b，不使用第三个变量，交换它们的值并输出。",
                "hint": "使用加减法或异或运算",
                "tags": ["变量", "交换"],
            },
        ],
    },
    # ===== 运算符与表达式 =====
    "kp_c22": {
        "source": "dotcpp.com 算术表达式与顺序执行",
        "problems": [
            {
                "problem_id": "dotcpp_2762",
                "title": "计算(a+b)*c的值",
                "difficulty": 1,
                "source": "dotcpp",
                "type": "编程题",
                "content": "读入三个整数a,b,c，计算并输出(a+b)*c的值。",
                "hint": "注意运算优先级",
                "tags": ["运算符", "表达式"],
            },
            {
                "problem_id": "dotcpp_2764",
                "title": "带余除法",
                "difficulty": 1,
                "source": "dotcpp",
                "type": "编程题",
                "content": "读入两个整数a,b，输出a除以b的商和余数。",
                "hint": "使用 / 和 % 运算符",
                "tags": ["运算符", "取余"],
            },
            {
                "problem_id": "matiji_002",
                "title": "自增自减运算",
                "difficulty": 2,
                "source": "matiji",
                "type": "选择题",
                "content": "int a=5; int b=a++; 执行后a和b的值分别是？",
                "options": [{"id": "A", "text": "a=5, b=5"}, {"id": "B", "text": "a=6, b=5"}, {"id": "C", "text": "a=6, b=6"}, {"id": "D", "text": "a=5, b=6"}],
                "answer": "B",
                "hint": "a++是后置自增，先赋值再加1",
                "tags": ["运算符", "自增"],
            },
            {
                "problem_id": "matiji_003",
                "title": "复合赋值运算符",
                "difficulty": 2,
                "source": "matiji",
                "type": "编程题",
                "content": "读入整数n，使用 += 运算符计算 1+2+3+...+n 的值。",
                "hint": "sum += i 等价于 sum = sum + i",
                "tags": ["运算符", "复合赋值"],
            },
        ],
    },
    # ===== 选择结构 =====
    "kp_c04": {
        "source": "dotcpp.com 条件分支",
        "problems": [
            {
                "problem_id": "dotcpp_1000",
                "title": "简单的a+b",
                "difficulty": 1,
                "source": "dotcpp",
                "type": "编程题",
                "content": "判断输入的两个数之和是否大于100。",
                "hint": "使用 if-else 语句",
                "tags": ["选择", "if"],
            },
            {
                "problem_id": "dotcpp_1053",
                "title": "成绩等级",
                "difficulty": 2,
                "source": "dotcpp",
                "type": "编程题",
                "content": "读入一个百分制成绩，输出对应的等级：90-100为A，80-89为B，70-79为C，60-69为D，60以下为E。",
                "hint": "使用 if-else if-else 或 switch",
                "tags": ["选择", "if-else"],
            },
            {
                "problem_id": "matiji_004",
                "title": "闰年判断",
                "difficulty": 2,
                "source": "matiji",
                "type": "编程题",
                "content": "读入一个年份，判断它是否是闰年。闰年条件：能被4整除但不能被100整除，或者能被400整除。",
                "hint": "使用逻辑运算符 && 和 ||",
                "tags": ["选择", "逻辑运算"],
            },
            {
                "problem_id": "matiji_005",
                "title": "switch语句应用",
                "difficulty": 2,
                "source": "matiji",
                "type": "编程题",
                "content": "读入一个1-7的整数，输出对应的星期几（Monday-Sunday）。",
                "hint": "使用 switch-case 语句",
                "tags": ["选择", "switch"],
            },
        ],
    },
    # ===== 循环结构 =====
    "kp_c05": {
        "source": "dotcpp.com 循环结构",
        "problems": [
            {
                "problem_id": "dotcpp_1060",
                "title": "求1到N的和",
                "difficulty": 1,
                "source": "dotcpp",
                "type": "编程题",
                "content": "读入正整数N，计算1+2+3+...+N的值。",
                "hint": "使用 for 循环或等差数列公式",
                "tags": ["循环", "for"],
            },
            {
                "problem_id": "dotcpp_1061",
                "title": "阶乘计算",
                "difficulty": 2,
                "source": "dotcpp",
                "type": "编程题",
                "content": "读入正整数n，计算n!（n的阶乘）。",
                "hint": "使用循环累乘",
                "tags": ["循环", "阶乘"],
            },
            {
                "problem_id": "matiji_006",
                "title": "九九乘法表",
                "difficulty": 2,
                "source": "matiji",
                "type": "编程题",
                "content": "输出九九乘法表。",
                "hint": "使用双重for循环",
                "tags": ["循环", "嵌套循环"],
            },
            {
                "problem_id": "matiji_007",
                "title": "水仙花数",
                "difficulty": 3,
                "source": "matiji",
                "type": "编程题",
                "content": "输出所有三位数中的水仙花数（各位数字的立方和等于该数本身）。",
                "hint": "使用循环取出各位数字",
                "tags": ["循环", "数学"],
            },
            {
                "problem_id": "matiji_008",
                "title": "质数判断",
                "difficulty": 3,
                "source": "matiji",
                "type": "编程题",
                "content": "读入一个正整数n，判断n是否为质数。",
                "hint": "从2到sqrt(n)逐一检查能否整除",
                "tags": ["循环", "质数"],
            },
        ],
    },
    # ===== 数组 =====
    "kp_c06": {
        "source": "dotcpp.com 数组",
        "problems": [
            {
                "problem_id": "dotcpp_1070",
                "title": "数组求和",
                "difficulty": 2,
                "source": "dotcpp",
                "type": "编程题",
                "content": "读入n个整数到数组中，计算它们的和与平均值。",
                "hint": "使用循环遍历数组累加",
                "tags": ["数组", "一维数组"],
            },
            {
                "problem_id": "dotcpp_1071",
                "title": "数组最大值",
                "difficulty": 2,
                "source": "dotcpp",
                "type": "编程题",
                "content": "读入n个整数，找出其中的最大值及其下标。",
                "hint": "遍历比较，记录最大值位置",
                "tags": ["数组", "查找"],
            },
            {
                "problem_id": "matiji_009",
                "title": "冒泡排序",
                "difficulty": 3,
                "source": "matiji",
                "type": "编程题",
                "content": "读入n个整数，使用冒泡排序将它们从小到大排序后输出。",
                "hint": "双重循环，相邻元素比较交换",
                "tags": ["数组", "排序"],
            },
            {
                "problem_id": "matiji_010",
                "title": "杨辉三角",
                "difficulty": 3,
                "source": "matiji",
                "type": "编程题",
                "content": "输出杨辉三角的前n行。",
                "hint": "使用二维数组，a[i][j]=a[i-1][j-1]+a[i-1][j]",
                "tags": ["数组", "二维数组"],
            },
        ],
    },
    # ===== 函数 =====
    "kp_c07": {
        "source": "dotcpp.com 函数",
        "problems": [
            {
                "problem_id": "dotcpp_1080",
                "title": "函数求最大值",
                "difficulty": 2,
                "source": "dotcpp",
                "type": "编程题",
                "content": "编写函数int max(int a, int b)，返回两个数中的较大值。在主函数中调用它。",
                "hint": "使用 if-else 比较",
                "tags": ["函数", "基本函数"],
            },
            {
                "problem_id": "matiji_011",
                "title": "递归求阶乘",
                "difficulty": 3,
                "source": "matiji",
                "type": "编程题",
                "content": "使用递归函数计算n!。",
                "hint": "n! = n * (n-1)!，基本情况 n<=1 时返回1",
                "tags": ["函数", "递归"],
            },
            {
                "problem_id": "matiji_012",
                "title": "递归斐波那契",
                "difficulty": 3,
                "source": "matiji",
                "type": "编程题",
                "content": "使用递归计算斐波那契数列第n项。",
                "hint": "f(n) = f(n-1) + f(n-2)，f(1)=f(2)=1",
                "tags": ["函数", "递归", "斐波那契"],
            },
            {
                "problem_id": "matiji_013",
                "title": "素数筛选函数",
                "difficulty": 3,
                "source": "matiji",
                "type": "编程题",
                "content": "编写函数int is_prime(int n)判断n是否为素数，利用该函数输出100以内所有素数。",
                "hint": "函数返回1表示是素数，0表示不是",
                "tags": ["函数", "素数"],
            },
        ],
    },
    # ===== 指针 =====
    "kp_c09": {
        "source": "dotcpp.com 指针",
        "problems": [
            {
                "problem_id": "dotcpp_1100",
                "title": "指针交换",
                "difficulty": 3,
                "source": "dotcpp",
                "type": "编程题",
                "content": "使用指针编写函数void swap(int *a, int *b)交换两个变量的值。",
                "hint": "通过指针解引用修改原始变量",
                "tags": ["指针", "交换"],
            },
            {
                "problem_id": "matiji_014",
                "title": "指针访问数组",
                "difficulty": 3,
                "source": "matiji",
                "type": "编程题",
                "content": "使用指针遍历数组并计算元素之和。",
                "hint": "p++ 移动指针到下一个元素",
                "tags": ["指针", "数组"],
            },
            {
                "problem_id": "matiji_015",
                "title": "动态内存分配",
                "difficulty": 4,
                "source": "matiji",
                "type": "编程题",
                "content": "使用malloc动态分配一个n个元素的int数组，读入数据后计算平均值，最后释放内存。",
                "hint": "malloc返回void*需要强制转换，记得free",
                "tags": ["指针", "动态内存"],
            },
        ],
    },
    # ===== 字符串 =====
    "kp_c31": {
        "source": "dotcpp.com 字符串",
        "problems": [
            {
                "problem_id": "dotcpp_1120",
                "title": "字符串长度",
                "difficulty": 2,
                "source": "dotcpp",
                "type": "编程题",
                "content": "读入一个字符串（不含空格），输出其长度（不使用strlen函数）。",
                "hint": "遍历到 '\\0' 为止",
                "tags": ["字符串", "长度"],
            },
            {
                "problem_id": "matiji_016",
                "title": "字符串逆序",
                "difficulty": 3,
                "source": "matiji",
                "type": "编程题",
                "content": "读入一个字符串，将其逆序输出。",
                "hint": "首尾交换或从后向前遍历",
                "tags": ["字符串", "逆序"],
            },
            {
                "problem_id": "matiji_017",
                "title": "字符串中数字个数",
                "difficulty": 2,
                "source": "matiji",
                "type": "编程题",
                "content": "读入一个字符串，统计其中数字字符的个数。",
                "hint": "判断 ch >= '0' && ch <= '9'",
                "tags": ["字符串", "统计"],
            },
        ],
    },
    # ===== 结构体 =====
    "kp_c10": {
        "source": "dotcpp.com 结构体",
        "problems": [
            {
                "problem_id": "dotcpp_1130",
                "title": "学生成绩管理",
                "difficulty": 3,
                "source": "dotcpp",
                "type": "编程题",
                "content": "定义学生结构体（姓名、学号、三门课成绩），读入n个学生信息，输出平均分最高的学生信息。",
                "hint": "使用struct定义，循环比较",
                "tags": ["结构体", "综合"],
            },
            {
                "problem_id": "matiji_018",
                "title": "结构体排序",
                "difficulty": 3,
                "source": "matiji",
                "type": "编程题",
                "content": "定义点结构体(x,y)，读入n个点，按x坐标从小到大排序后输出。",
                "hint": "结构体数组排序",
                "tags": ["结构体", "排序"],
            },
        ],
    },
    # ===== 文件操作 =====
    "kp_c12": {
        "source": "dotcpp.com 文件",
        "problems": [
            {
                "problem_id": "dotcpp_1140",
                "title": "文件读写",
                "difficulty": 3,
                "source": "dotcpp",
                "type": "编程题",
                "content": "将1-100写入文件data.txt，然后从文件中读取并计算它们的和。",
                "hint": "fopen使用\"w\"和\"r\"模式",
                "tags": ["文件", "读写"],
            },
            {
                "problem_id": "matiji_019",
                "title": "统计文件字符数",
                "difficulty": 3,
                "source": "matiji",
                "type": "编程题",
                "content": "读取一个文本文件，统计其中字母、数字、空格和其他字符的个数。",
                "hint": "使用fgetc逐字符读取",
                "tags": ["文件", "统计"],
            },
        ],
    },
    # ===== 预处理 =====
    "kp_c08": {
        "source": "dotcpp.com 预处理",
        "problems": [
            {
                "problem_id": "matiji_020",
                "title": "宏定义求最大值",
                "difficulty": 2,
                "source": "matiji",
                "type": "编程题",
                "content": "定义宏 MAX(a,b) 求两个数的最大值，测试多组数据。",
                "hint": "使用三元运算符 ?:",
                "tags": ["预处理", "宏"],
            },
            {
                "problem_id": "matiji_021",
                "title": "条件编译",
                "difficulty": 3,
                "source": "matiji",
                "type": "编程题",
                "content": "使用#ifdef DEBUG实现调试信息的条件输出。",
                "hint": "#ifdef ... #endif",
                "tags": ["预处理", "条件编译"],
            },
        ],
    },
    # ===== 位运算 =====
    "kp_c11": {
        "source": "dotcpp.com 位运算",
        "problems": [
            {
                "problem_id": "dotcpp_1150",
                "title": "位运算判断奇偶",
                "difficulty": 2,
                "source": "dotcpp",
                "type": "编程题",
                "content": "使用位运算判断一个整数是奇数还是偶数。",
                "hint": "n & 1 为1是奇数，为0是偶数",
                "tags": ["位运算", "与运算"],
            },
            {
                "problem_id": "matiji_022",
                "title": "统计二进制中1的个数",
                "difficulty": 3,
                "source": "matiji",
                "type": "编程题",
                "content": "读入一个无符号整数，输出其二进制表示中1的个数。",
                "hint": "循环右移并检查最低位",
                "tags": ["位运算", "二进制"],
            },
        ],
    },
}


def seed():
    db_path = DB_PATH.resolve()
    if not db_path.exists():
        print(f"[ERR] 数据库不存在: {db_path}")
        sys.exit(1)

    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()

    # 检查是否有 practice_problems 字段，如果没有则添加
    cur.execute("PRAGMA table_info(knowledge_points)")
    columns = [row[1] for row in cur.fetchall()]

    total_added = 0
    total_updated = 0

    for kp_id, data in PRACTICE_PROBLEMS.items():
        # 检查知识点是否存在
        cur.execute("SELECT kp_id, questions FROM knowledge_points WHERE kp_id = ?", (kp_id,))
        row = cur.fetchone()
        if not row:
            print(f"[WARN] {kp_id} 不存在，跳过")
            continue

        # 合并到现有 questions 字段
        existing_questions = []
        if row[1]:
            try:
                existing_questions = json.loads(row[1])
            except (json.JSONDecodeError, TypeError):
                existing_questions = []

        existing_ids = {q.get("problem_id") or q.get("q_id") for q in existing_questions}

        new_questions = []
        for prob in data["problems"]:
            pid = prob["problem_id"]
            if pid not in existing_ids:
                # 转换为统一格式
                q = {
                    "q_id": pid,
                    "type": prob.get("type", "编程题"),
                    "content": prob["content"],
                    "difficulty": prob.get("difficulty", 2),
                    "source": prob.get("source", "unknown"),
                    "source_url": f"https://www.dotcpp.com/oj/problem{pid.split('_')[1]}.html" if prob.get("source") == "dotcpp" else "",
                    "hint": prob.get("hint", ""),
                    "tags": prob.get("tags", []),
                }
                if "options" in prob:
                    q["options"] = prob["options"]
                if "answer" in prob:
                    q["correct_answer"] = prob["answer"]
                new_questions.append(q)

        if new_questions:
            updated_questions = existing_questions + new_questions
            cur.execute(
                "UPDATE knowledge_points SET questions = ? WHERE kp_id = ?",
                (json.dumps(updated_questions, ensure_ascii=False), kp_id),
            )
            total_added += len(new_questions)
            total_updated += 1
            print(f"[OK] {kp_id}: 新增 {len(new_questions)} 道题目（原 {len(existing_questions)} 道）")
        else:
            print(f"[SKIP] {kp_id}: 题目已存在，无新增")

    conn.commit()
    conn.close()
    print(f"\n[完成] 更新了 {total_updated} 个知识点，新增 {total_added} 道练习题")


if __name__ == "__main__":
    seed()
