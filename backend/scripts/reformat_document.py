"""
重新格式化 knowledge_points.document，改进教材分段质量。
运行方式：cd backend && python scripts/reformat_document.py
"""
from __future__ import annotations

import re
import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "ai_learning_v2.db"
TXT_PATH = Path(__file__).resolve().parent.parent.parent / "C语言.txt"

CHAPTER_PATTERN = re.compile(r"^第\s*(\d+)\s*章\s*([^\n]+?)$")
SECTION_PATTERN = re.compile(r"^(\d+\.\d+(?:\.\d+)?)\s*(.+?)$")


def split_chapters(raw_text: str) -> dict[int, dict]:
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


def is_section_line(line: str) -> bool:
    return bool(SECTION_PATTERN.match(line.strip()))


def is_chapter_line(line: str) -> bool:
    return bool(CHAPTER_PATTERN.match(line.strip()))


def is_example_line(line: str) -> bool:
    return bool(re.match(r"^例\s*\d+(?:\.\d+)?\s+", line.strip()))


def is_image_line(line: str) -> bool:
    return bool(re.match(r"^图\s*\d+[\-\.]?\d*\s*", line.strip()))


def is_toc_page_line(line: str) -> bool:
    return bool(re.search(r"[\t\s]+\d+\s*$", line) and SECTION_PATTERN.match(line.split()[0]))


def is_code_start(line: str, next_lines: list[str], idx: int) -> bool:
    s = line.strip()
    if s.startswith("#include"):
        return True
    if re.match(r"^(void|int|char|float|double|long|short|unsigned|signed|struct|union|enum|typedef|#define|#ifdef|#ifndef|#endif|#undef)\s", s):
        return True
    if re.match(r"^(void|int)?\s*main\s*\(", s):
        return True
    if line.startswith((" ", "\t")) and re.search(r"[;{}()]", s):
        return True
    return False


def is_ascii_art(line: str) -> bool:
    s = line.strip()
    if not s:
        return False
    # 包含注释的行不当作 ASCII art
    if "/*" in s or "//" in s:
        return False
    # 排除简单的赋值表达式（如 &p=720846, n=10, *p=10）
    if re.match(r"^([\*\u0026]?[a-zA-Z_][a-zA-Z0-9_]*)=[\d,]+$", s):
        return False
    special_chars = set("&*|^~<>+-/\\=:.!@#$%")
    char_count = len(s)
    if char_count == 0:
        return False
    special_count = sum(1 for c in s if c in special_chars)
    chinese_count = len(re.findall(r"[\u4e00-\u9fff]", s))
    if special_count / char_count > 0.3 and chinese_count < 5:
        return True
    if re.search(r"\(int \*\)\d+", s) or re.search(r"^\*\*[\s\d\(\)\*\u0026a-zA-Z]+$", s):
        return True
    if re.match(r"^[\s\d\u0026\|\^\~\u003c\u003e]+$", s):
        return True
    # 指针关系式，但排除含注释的
    if re.match(r"^[\s\*\u0026a-zA-Z_\d\(\)=;]+$", s) and "=" in s and chinese_count < 3 and "/*" not in s:
        return True
    return False


def is_code_continuation(line: str) -> bool:
    s = line.strip()
    if not s:
        return False
    if is_section_line(line) or is_chapter_line(line) or is_example_line(line):
        return False

    chinese_count = len(re.findall(r"[\u4e00-\u9fff]", s))

    if re.match(r"^(运行结果|程序运行后|说明[：:]?|输入[：:]?|输出[：:]?|结果[：:]?|分析[：:]?)", s):
        return False

    if re.match(r"^(void|int)?\s*main\s*\(", s):
        return True

    # 带注释的代码行（如 {int n=10; /* 说明 */）仍然是代码
    if chinese_count > 5 and not s.startswith(("/*", "*", "//")):
        if re.search(r"[;{}]", s) and ("/*" in s or "//" in s):
            return True
        return False

    if is_ascii_art(line):
        return False

    if line.startswith((" ", "\t")):
        return True

    if s.startswith(("/*", "*", "//")):
        return True

    if s.startswith("#"):
        return True

    if re.search(r"[;{}=]", s) and chinese_count < 3:
        return True

    return False


def merge_paragraph_lines(lines: list[str]) -> str:
    if not lines:
        return ""
    result = [lines[0]]
    for i in range(1, len(lines)):
        prev = lines[i - 1].rstrip()
        curr = lines[i].rstrip()
        if prev and prev[-1] in "。！？；：":
            result.append(curr)
        elif curr and curr[0] in "（(【[《〈\"\"'":
            result.append(curr)
        elif len(prev) < 20:
            result.append(curr)
        elif len(curr) < 20:
            result.append(curr)
        else:
            result[-1] = result[-1] + curr
    return "\n".join(result)


def clean_document_v2(lines: list[str]) -> str:
    result: list[str] = []
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        if is_image_line(line):
            i += 1
            continue

        if is_toc_page_line(line):
            i += 1
            continue

        m = CHAPTER_PATTERN.match(stripped)
        if m:
            result.append(f"# 第{m.group(1)}章 {m.group(2).strip()}")
            result.append("")
            i += 1
            continue

        m = SECTION_PATTERN.match(stripped)
        if m:
            section = m.group(1)
            text = m.group(2).strip()
            level = section.count(".")
            prefix = "#" * (level + 1)
            result.append(f"{prefix} {section} {text}")
            result.append("")
            i += 1
            continue

        if is_example_line(line):
            result.append(f"**{stripped}**")
            result.append("")
            i += 1
            continue

        if is_ascii_art(line):
            art_lines = []
            while i < n and (is_ascii_art(lines[i]) or lines[i].strip() == ""):
                if lines[i].strip():
                    art_lines.append(lines[i])
                i += 1
            if art_lines:
                result.append("```")
                result.extend(art_lines)
                result.append("```")
                result.append("")
            continue

        if is_code_start(line, lines, i):
            code_lines = [lines[i]]
            i += 1
            while i < n:
                if not lines[i].strip():
                    if i + 1 < n and is_code_continuation(lines[i + 1]):
                        code_lines.append(lines[i])
                        i += 1
                        continue
                    else:
                        i += 1
                        break
                if is_section_line(lines[i]) or is_chapter_line(lines[i]) or is_example_line(lines[i]):
                    break
                if not is_code_continuation(lines[i]):
                    break
                code_lines.append(lines[i])
                i += 1
            if code_lines:
                result.append("```c")
                result.extend(code_lines)
                result.append("```")
                result.append("")
            continue

        para_lines = []
        while i < n:
            l = lines[i].rstrip()
            if not l:
                i += 1
                break
            if is_chapter_line(l) or is_section_line(l) or is_example_line(l):
                break
            if is_code_start(l, lines, i) or is_ascii_art(l):
                break
            para_lines.append(l)
            i += 1

        if para_lines:
            merged = merge_paragraph_lines(para_lines)
            result.append(merged)
            result.append("")

    final: list[str] = []
    prev_empty = False
    for line in result:
        if line == "":
            if not prev_empty:
                final.append(line)
            prev_empty = True
        else:
            final.append(line)
            prev_empty = False

    return "\n".join(final)


def main():
    txt_path = TXT_PATH.resolve()
    db_path = DB_PATH.resolve()

    if not txt_path.exists():
        print(f"[ERR] 教材不存在: {txt_path}")
        sys.exit(1)

    raw = txt_path.read_text(encoding="utf-8", errors="replace")
    chapters = split_chapters(raw)
    print(f"[OK] 解析到 {len(chapters)} 章")

    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()

    updated = 0
    for i in range(1, 14):
        kp_id = f"kp_c{i:02d}"
        ch = chapters.get(i)
        if not ch:
            print(f"[WARN] 第 {i} 章缺失，跳过")
            continue

        doc = clean_document_v2(ch["lines"])
        if not doc.strip():
            print(f"[WARN] {kp_id} document 为空")
            continue

        cur.execute(
            "UPDATE knowledge_points SET document = ? WHERE kp_id = ?",
            (doc, kp_id),
        )
        updated += 1
        print(f"[OK] 更新 {kp_id} — document {len(doc)} 字符")

    conn.commit()
    conn.close()
    print(f"\n[OK] 共更新 {updated} 条记录。")


if __name__ == "__main__":
    main()
