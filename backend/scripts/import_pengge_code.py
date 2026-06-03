"""
将鹏哥C语言文件夹中的所有代码文件导入到数据库。
按日期映射到知识点，追加到 code_example 字段。
"""
import sqlite3
import os
import glob
from pathlib import Path

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "ai_learning_v2.db")
CODE_ROOT = r"C:\Users\15722\Desktop\开发\软件杯A3\鹏哥C语言【代码及板书】2020年版本\鹏哥C语言84版代码及板书"

# 日期 -> 知识点映射（根据课程进度）
DATE_KP_MAP = {
    # 2月 - C语言概述、数据类型
    "2_27": "kp_c01",   # 初始C语言
    "2_29": "kp_c01",   # 初始C语言2
    # 3月上旬 - 数据类型、运算符、输入输出
    "3_3": "kp_c02",    # 数据类型
    "3_5": "kp_c02",    # 数据类型
    "3_7": "kp_c03",    # 运算符
    "3_10": "kp_c03",   # 运算符
    "3_14": "kp_c04",   # 输入输出
    "3_15": "kp_c04",   # 输入输出
    # 3月中旬 - 选择结构、循环结构
    "3_17": "kp_c05",   # 选择结构
    "3_21": "kp_c05",   # 选择结构
    "3_21_2": "kp_c05", # 选择结构
    "3_22": "kp_c06",   # 循环结构
    "3_26": "kp_c06",   # 循环结构
    "3_28": "kp_c06",   # 循环结构
    "3_29": "kp_c06",   # 循环结构
    "3_30": "kp_c06",   # 循环结构
    # 4月上旬 - 数组、字符串
    "4_2": "kp_c07",    # 数组
    "4_6": "kp_c07",    # 数组
    "4_8": "kp_c07",    # 数组
    "4_10": "kp_c08",   # 字符串
    "4_13": "kp_c08",   # 字符串
    "4_15": "kp_c09",   # 函数
    "4_17": "kp_c09",   # 函数
    # 4月下旬 - 函数递归、指针
    "4_20": "kp_c09",   # 函数递归
    "4_22": "kp_c10",   # 指针基础
    "4_24": "kp_c10",   # 指针基础
    "4_27": "kp_c10",   # 指针基础
    "4_29": "kp_c11",   # 指针与数组
    # 5月 - 结构体、文件、动态内存
    "5_6": "kp_c12",    # 结构体
    "5_9": "kp_c12",    # 结构体
    "5_11": "kp_c13",   # 文件操作
    "5_13": "kp_c14",   # 动态内存
}

# 项目文件夹 -> 知识点映射
PROJECT_KP_MAP = {
    "Contact": "kp_c12",      # 通讯录(结构体)
    "Contact2": "kp_c12",     # 通讯录2
    "ContactFile": "kp_c13",  # 通讯录文件版
    "Contact_Dynamic": "kp_c14",  # 通讯录动态版(动态内存)
    "game1": "kp_c06",        # 游戏(循环)
}


def read_file(path):
    """读取文件内容，处理编码问题"""
    encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1']
    for enc in encodings:
        try:
            with open(path, 'r', encoding=enc) as f:
                return f.read()
        except (UnicodeDecodeError, UnicodeError):
            continue
    return None


def format_code_example(folder_name, files_content):
    """将多个代码文件格式化为一个 code_example 字符串"""
    parts = []
    for fname, content in files_content:
        if content and content.strip():
            # 过滤掉全注释的文件
            lines = [l for l in content.split('\n') if l.strip() and not l.strip().startswith('//')]
            if len(lines) > 2:  # 至少有2行非注释代码
                parts.append(f"// ===== {folder_name}/{fname} =====\n{content.strip()}")
    return "\n\n".join(parts)


def collect_code_files():
    """收集所有代码文件，按知识点分组"""
    kp_codes = {}  # kp_id -> [(folder_name, file_name, content)]

    # 处理日期命名的文件夹
    for date_key, kp_id in DATE_KP_MAP.items():
        folder_pattern = os.path.join(CODE_ROOT, f"test_{date_key}", f"test_{date_key}")
        if os.path.isdir(folder_pattern):
            files = []
            for f in glob.glob(os.path.join(folder_pattern, "*.c")):
                content = read_file(f)
                if content:
                    files.append((os.path.basename(f), content))
            if files:
                kp_codes.setdefault(kp_id, []).append((f"test_{date_key}", files))

    # 处理项目文件夹
    for project_name, kp_id in PROJECT_KP_MAP.items():
        # 查找项目中的.c文件
        project_dir = os.path.join(CODE_ROOT, project_name)
        if os.path.isdir(project_dir):
            c_files = glob.glob(os.path.join(project_dir, "**", "*.c"), recursive=True)
            files = []
            for f in c_files:
                content = read_file(f)
                if content:
                    files.append((os.path.basename(f), content))
            if files:
                kp_codes.setdefault(kp_id, []).append((project_name, files))

    return kp_codes


def import_to_database():
    """将收集的代码导入数据库"""
    kp_codes = collect_code_files()

    db = os.path.abspath(DB_PATH)
    print(f"数据库路径: {db}")
    conn = sqlite3.connect(db)
    cur = conn.cursor()

    total_files = 0
    total_kp = 0

    for kp_id, groups in sorted(kp_codes.items()):
        # 获取现有的 code_example
        cur.execute("SELECT code_example FROM knowledge_points WHERE kp_id=?", (kp_id,))
        row = cur.fetchone()
        existing_code = row[0] if row and row[0] else ""

        # 构建新的代码内容
        new_parts = []
        for group_name, files in groups:
            formatted = format_code_example(group_name, files)
            if formatted:
                new_parts.append(formatted)
                total_files += len(files)

        if new_parts:
            # 合并：保留现有内容 + 追加新内容
            separator = "\n\n// ========================================\n// 课堂实践代码\n// ========================================\n\n"
            combined = existing_code + separator + "\n\n".join(new_parts)

            cur.execute(
                "UPDATE knowledge_points SET code_example=? WHERE kp_id=?",
                (combined, kp_id)
            )
            total_kp += 1
            file_count = sum(len(files) for _, files in groups)
            print(f"  [OK] {kp_id}: 追加 {file_count} 个代码文件")
        else:
            print(f"  [SKIP] {kp_id}: 无有效代码")

    conn.commit()
    conn.close()
    print(f"\n完成！更新了 {total_kp} 个知识点，共导入 {total_files} 个代码文件。")


if __name__ == "__main__":
    import_to_database()
