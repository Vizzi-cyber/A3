"""
从菜鸟教程抓取C语言教程内容，补充到 knowledge_points 表
运行方式：cd backend && python scripts/seed_runoob_content.py
"""
from __future__ import annotations

import json
import re
import sqlite3
import sys
import time
from pathlib import Path
from urllib.request import urlopen, Request
from html.parser import HTMLParser

DB_PATH = Path(__file__).resolve().parent.parent / "ai_learning_v2.db"

# 菜鸟教程C语言各章节URL
RUNOOB_PAGES = [
    {"kp_id": "kp_c14", "url": "https://www.runoob.com/cprogramming/c-intro.html", "name": "C 简介", "subject": "入门", "difficulty": 0.15, "tags": ["简介", "历史", "特点"]},
    {"kp_id": "kp_c15", "url": "https://www.runoob.com/cprogramming/c-environment-setup.html", "name": "C 环境设置", "subject": "入门", "difficulty": 0.20, "tags": ["环境", "编译器", "安装"]},
    {"kp_id": "kp_c16", "url": "https://www.runoob.com/cprogramming/c-program-structure.html", "name": "C 程序结构", "subject": "基础", "difficulty": 0.25, "tags": ["结构", "main", "框架"]},
    {"kp_id": "kp_c17", "url": "https://www.runoob.com/cprogramming/c-basic-syntax.html", "name": "C 基础语法", "subject": "基础", "difficulty": 0.25, "tags": ["语法", "语句", "标识符"]},
    {"kp_id": "kp_c18", "url": "https://www.runoob.com/cprogramming/c-data-types.html", "name": "C 数据类型", "subject": "基础", "difficulty": 0.30, "tags": ["int", "float", "char", "类型"]},
    {"kp_id": "kp_c19", "url": "https://www.runoob.com/cprogramming/c-variables.html", "name": "C 变量", "subject": "基础", "difficulty": 0.25, "tags": ["变量", "声明", "定义"]},
    {"kp_id": "kp_c20", "url": "https://www.runoob.com/cprogramming/c-constants.html", "name": "C 常量", "subject": "基础", "difficulty": 0.25, "tags": ["常量", "const", "define"]},
    {"kp_id": "kp_c21", "url": "https://www.runoob.com/cprogramming/c-storage-classes.html", "name": "C 存储类", "subject": "进阶", "difficulty": 0.45, "tags": ["auto", "static", "extern", "register"]},
    {"kp_id": "kp_c22", "url": "https://www.runoob.com/cprogramming/c-operators.html", "name": "C 运算符", "subject": "基础", "difficulty": 0.30, "tags": ["运算符", "优先级", "结合性"]},
    {"kp_id": "kp_c23", "url": "https://www.runoob.com/cprogramming/c-decision.html", "name": "C 判断", "subject": "控制结构", "difficulty": 0.35, "tags": ["if", "switch", "条件"]},
    {"kp_id": "kp_c24", "url": "https://www.runoob.com/cprogramming/c-loops.html", "name": "C 循环", "subject": "控制结构", "difficulty": 0.40, "tags": ["for", "while", "do-while", "循环"]},
    {"kp_id": "kp_c25", "url": "https://www.runoob.com/cprogramming/c-functions.html", "name": "C 函数", "subject": "模块化", "difficulty": 0.45, "tags": ["函数", "参数", "返回值"]},
    {"kp_id": "kp_c26", "url": "https://www.runoob.com/cprogramming/c-scope-rules.html", "name": "C 作用域规则", "subject": "进阶", "difficulty": 0.45, "tags": ["作用域", "局部", "全局"]},
    {"kp_id": "kp_c27", "url": "https://www.runoob.com/cprogramming/c-arrays.html", "name": "C 数组", "subject": "数据结构", "difficulty": 0.45, "tags": ["数组", "一维", "二维"]},
    {"kp_id": "kp_c28", "url": "https://www.runoob.com/cprogramming/c-enum.html", "name": "C enum(枚举)", "subject": "数据结构", "difficulty": 0.40, "tags": ["enum", "枚举"]},
    {"kp_id": "kp_c29", "url": "https://www.runoob.com/cprogramming/c-pointers.html", "name": "C 指针", "subject": "进阶", "difficulty": 0.65, "tags": ["指针", "地址", "解引用"]},
    {"kp_id": "kp_c30", "url": "https://www.runoob.com/cprogramming/c-fun-pointer-callback.html", "name": "C 函数指针与回调函数", "subject": "进阶", "difficulty": 0.60, "tags": ["函数指针", "回调"]},
    {"kp_id": "kp_c31", "url": "https://www.runoob.com/cprogramming/c-strings.html", "name": "C 字符串", "subject": "数据结构", "difficulty": 0.45, "tags": ["字符串", "字符数组", "strlen"]},
    {"kp_id": "kp_c32", "url": "https://www.runoob.com/cprogramming/c-structures.html", "name": "C 结构体", "subject": "进阶", "difficulty": 0.55, "tags": ["struct", "结构体"]},
    {"kp_id": "kp_c33", "url": "https://www.runoob.com/cprogramming/c-unions.html", "name": "C 共用体", "subject": "进阶", "difficulty": 0.50, "tags": ["union", "共用体"]},
    {"kp_id": "kp_c34", "url": "https://www.runoob.com/cprogramming/c-bit-fields.html", "name": "C 位域", "subject": "进阶", "difficulty": 0.50, "tags": ["位域", "位段"]},
    {"kp_id": "kp_c35", "url": "https://www.runoob.com/cprogramming/c-typedef.html", "name": "C typedef", "subject": "进阶", "difficulty": 0.40, "tags": ["typedef", "类型别名"]},
    {"kp_id": "kp_c36", "url": "https://www.runoob.com/cprogramming/c-input-output.html", "name": "C 输入 & 输出", "subject": "基础", "difficulty": 0.35, "tags": ["printf", "scanf", "IO"]},
    {"kp_id": "kp_c37", "url": "https://www.runoob.com/cprogramming/c-file-io.html", "name": "C 文件读写", "subject": "应用", "difficulty": 0.55, "tags": ["文件", "fopen", "fclose", "fread"]},
    {"kp_id": "kp_c38", "url": "https://www.runoob.com/cprogramming/c-preprocessors.html", "name": "C 预处理器", "subject": "工程", "difficulty": 0.45, "tags": ["预处理", "宏", "条件编译"]},
    {"kp_id": "kp_c39", "url": "https://www.runoob.com/cprogramming/c-header-files.html", "name": "C 头文件", "subject": "工程", "difficulty": 0.35, "tags": ["头文件", "include"]},
    {"kp_id": "kp_c40", "url": "https://www.runoob.com/cprogramming/c-type-casting.html", "name": "C 强制类型转换", "subject": "进阶", "difficulty": 0.40, "tags": ["类型转换", "cast"]},
    {"kp_id": "kp_c41", "url": "https://www.runoob.com/cprogramming/c-error-handling.html", "name": "C 错误处理", "subject": "应用", "difficulty": 0.45, "tags": ["错误处理", "errno", "perror"]},
    {"kp_id": "kp_c42", "url": "https://www.runoob.com/cprogramming/c-recursion.html", "name": "C 递归", "subject": "算法", "difficulty": 0.55, "tags": ["递归", "递推"]},
    {"kp_id": "kp_c43", "url": "https://www.runoob.com/cprogramming/c-variable-arguments.html", "name": "C 可变参数", "subject": "进阶", "difficulty": 0.55, "tags": ["可变参数", "stdarg"]},
    {"kp_id": "kp_c44", "url": "https://www.runoob.com/cprogramming/c-memory-management.html", "name": "C 内存管理", "subject": "进阶", "difficulty": 0.60, "tags": ["内存", "malloc", "free", "堆"]},
    {"kp_id": "kp_c45", "url": "https://www.runoob.com/cprogramming/c-command-line-arguments.html", "name": "C 命令行参数", "subject": "应用", "difficulty": 0.40, "tags": ["命令行", "argc", "argv"]},
    {"kp_id": "kp_c46", "url": "https://www.runoob.com/cprogramming/c-sort-algorithm.html", "name": "C 排序算法", "subject": "算法", "difficulty": 0.55, "tags": ["排序", "冒泡", "选择", "快速"]},
]


class RunoobContentParser(HTMLParser):
    """解析菜鸟教程页面，提取文章主体内容"""
    def __init__(self):
        super().__init__()
        self.in_article = False
        self.in_content = False
        self.depth = 0
        self.text_parts = []
        self.current_tag = None

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == "div" and attrs_dict.get("class", "").startswith("article-body"):
            self.in_article = True
            self.depth = 0
        if self.in_article:
            if tag == "div":
                self.depth += 1
            # 提取代码块
            if tag == "div" and "example_code" in attrs_dict.get("class", ""):
                self.in_content = True
                self.text_parts.append("\n```c\n")
            elif tag == "pre":
                self.in_content = True
                self.text_parts.append("\n```\n")
            # 提取标题
            elif tag in ("h1", "h2", "h3", "h4"):
                level = int(tag[1])
                self.text_parts.append("\n" + "#" * level + " ")
            # 提取段落
            elif tag == "p":
                self.text_parts.append("\n")
            # 提取列表
            elif tag == "li":
                self.text_parts.append("\n- ")
            elif tag == "br":
                self.text_parts.append("\n")

    def handle_endtag(self, tag):
        if self.in_article:
            if tag == "div":
                self.depth -= 1
                if self.depth < 0:
                    self.in_article = False
            if tag in ("h1", "h2", "h3", "h4"):
                self.text_parts.append("\n")
            if tag == "pre":
                self.text_parts.append("\n```\n")
                self.in_content = False
            if tag == "div" and self.in_content:
                self.text_parts.append("\n```\n")
                self.in_content = False

    def handle_data(self, data):
        if self.in_article:
            text = data.strip()
            if text:
                self.text_parts.append(text)

    def get_text(self):
        return "\n".join(self.text_parts)


def fetch_page(url: str) -> str:
    """抓取网页内容"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    req = Request(url, headers=headers)
    try:
        with urlopen(req, timeout=15) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"  [ERR] 抓取失败 {url}: {e}")
        return ""


def extract_content(html: str) -> str:
    """从HTML中提取文章主体"""
    parser = RunoobContentParser()
    parser.feed(html)
    text = parser.get_text()

    # 清理多余空行
    lines = text.split("\n")
    cleaned = []
    prev_empty = False
    for line in lines:
        if not line.strip():
            if not prev_empty:
                cleaned.append("")
                prev_empty = True
        else:
            cleaned.append(line)
            prev_empty = False

    return "\n".join(cleaned).strip()


def build_prerequisites(kp_id: str, page_info: dict) -> list:
    """根据知识点ID构建前置依赖"""
    # 简单的前置依赖映射
    prereq_map = {
        "kp_c14": [],  # C 简介
        "kp_c15": ["kp_c14"],  # 环境设置
        "kp_c16": ["kp_c14"],  # 程序结构
        "kp_c17": ["kp_c16"],  # 基础语法
        "kp_c18": ["kp_c17"],  # 数据类型
        "kp_c19": ["kp_c18"],  # 变量
        "kp_c20": ["kp_c19"],  # 常量
        "kp_c21": ["kp_c19"],  # 存储类
        "kp_c22": ["kp_c18"],  # 运算符
        "kp_c23": ["kp_c22"],  # 判断
        "kp_c24": ["kp_c23"],  # 循环
        "kp_c25": ["kp_c24"],  # 函数
        "kp_c26": ["kp_c25"],  # 作用域规则
        "kp_c27": ["kp_c19"],  # 数组
        "kp_c28": ["kp_c18"],  # enum
        "kp_c29": ["kp_c27"],  # 指针
        "kp_c30": ["kp_c29", "kp_c25"],  # 函数指针
        "kp_c31": ["kp_c27"],  # 字符串
        "kp_c32": ["kp_c27"],  # 结构体
        "kp_c33": ["kp_c32"],  # 共用体
        "kp_c34": ["kp_c32"],  # 位域
        "kp_c35": ["kp_c18"],  # typedef
        "kp_c36": ["kp_c17"],  # 输入输出
        "kp_c37": ["kp_c36"],  # 文件读写
        "kp_c38": ["kp_c17"],  # 预处理器
        "kp_c39": ["kp_c38"],  # 头文件
        "kp_c40": ["kp_c18"],  # 强制类型转换
        "kp_c41": ["kp_c25"],  # 错误处理
        "kp_c42": ["kp_c25"],  # 递归
        "kp_c43": ["kp_c25"],  # 可变参数
        "kp_c44": ["kp_c29"],  # 内存管理
        "kp_c45": ["kp_c25"],  # 命令行参数
        "kp_c46": ["kp_c27"],  # 排序算法
    }
    return prereq_map.get(kp_id, [])


def seed():
    db_path = DB_PATH.resolve()
    if not db_path.exists():
        print(f"[ERR] 数据库不存在: {db_path}")
        sys.exit(1)

    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()

    # 检查已有知识点
    cur.execute("SELECT kp_id FROM knowledge_points")
    existing = {r[0] for r in cur.fetchall()}
    print(f"[INFO] 数据库已有 {len(existing)} 个知识点")

    success_count = 0
    skip_count = 0
    fail_count = 0

    for page in RUNOOB_PAGES:
        kp_id = page["kp_id"]

        # 跳过已存在的
        if kp_id in existing:
            print(f"[SKIP] {kp_id} ({page['name']}) 已存在")
            skip_count += 1
            continue

        print(f"[FETCH] {kp_id} - {page['name']} ...")
        html = fetch_page(page["url"])
        if not html:
            fail_count += 1
            continue

        content = extract_content(html)
        if len(content) < 50:
            print(f"  [WARN] 内容过短 ({len(content)} 字符)，跳过")
            fail_count += 1
            continue

        # 构建思维导图
        mindmap = {
            "root": page["name"],
            "children": [{"name": "基本概念"}, {"name": "语法格式"}, {"name": "使用示例"}, {"name": "注意事项"}]
        }

        prerequisites = build_prerequisites(kp_id, page)

        cur.execute(
            """
            INSERT INTO knowledge_points
            (kp_id, name, subject, difficulty, prerequisites, description, tags, document, code_example, questions, mindmap)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                kp_id,
                page["name"],
                page["subject"],
                page["difficulty"],
                json.dumps(prerequisites, ensure_ascii=False),
                f"菜鸟教程C语言：{page['name']}",
                json.dumps(page["tags"], ensure_ascii=False),
                content,  # document
                "",  # code_example (从内容中提取)
                json.dumps([], ensure_ascii=False),  # questions
                json.dumps(mindmap, ensure_ascii=False),  # mindmap
            ),
        )
        print(f"  [OK] 写入 {len(content)} 字符")
        success_count += 1

        # 避免请求过快
        time.sleep(0.5)

    conn.commit()
    conn.close()

    print(f"\n[完成] 新增: {success_count}, 跳过: {skip_count}, 失败: {fail_count}")


if __name__ == "__main__":
    seed()
