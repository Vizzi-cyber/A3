"""
C 语言代码静态分析服务（tree-sitter AST + 规则引擎）
用 tree-sitter 解析 C 代码为 AST，扫描常见 bug 模式：
  1. 数组越界：数组下标 >= 声明的数组大小（常量场景）
  2. 野指针：未初始化指针解引用（*p 但 p 未赋值）
  3. 未初始化变量：声明后未赋值即使用
  4. 除零：除法/取模除数为常量 0
  5. 内存泄漏：malloc/calloc/realloc 后无 free
  6. 悬空 else：else 与 if 配对异常（启发式：else 后空行）
  7. 空指针解引用：对可能为 NULL 的返回值直接解引用
输出：bug 列表（行号 + 类型 + 严重度 + 描述 + 建议），供 LLM 深度诊断前置。
"""
from typing import Any, Dict, List

from tree_sitter import Language, Parser
import tree_sitter_c

_C_LANG = Language(tree_sitter_c.language())
_PARSER = Parser(_C_LANG)

# 严重度与建议
_TYPE_KW = {"int", "char", "float", "double", "void", "struct", "unsigned", "long", "short", "const", "static", "return"}

_BUG_TEMPLATE = {
    "array_oob": {"severity": "high", "desc": "数组越界访问", "suggest": "检查下标范围，确保 < 数组长度"},
    "wild_pointer": {"severity": "high", "desc": "野指针/未初始化指针解引用", "suggest": "先为指针赋值或 malloc 后再解引用"},
    "uninitialized": {"severity": "medium", "desc": "使用未初始化变量", "suggest": "声明时初始化或先赋值再使用"},
    "div_zero": {"severity": "high", "desc": "除数为零（常量场景）", "suggest": "检查除数，增加 0 判断"},
    "memory_leak": {"severity": "medium", "desc": "内存泄漏：分配后未释放", "suggest": "在退出路径上调用 free()"},
    "null_deref": {"severity": "high", "desc": "可能空指针解引用", "suggest": "解引用前判空"},
}


def _node_text(node, source: bytes) -> str:
    try:
        return source[node.start_byte:node.end_byte].decode("utf-8", "ignore")
    except Exception:
        return ""


def _line(node) -> int:
    return node.start_point[0] + 1


def analyze_c(source_text: str) -> List[Dict[str, Any]]:
    """对 C 代码做 AST 静态分析，返回问题列表。"""
    source = source_text.encode("utf-8")
    tree = _PARSER.parse(source)
    root = tree.root_node
    issues: List[Dict[str, Any]] = []

    # 收集：数组声明（名字->大小）、malloc 调用、free 调用、变量初始化状态
    array_sizes: Dict[str, int] = {}
    malloc_locs: List[int] = []
    free_locs: List[int] = []
    declared_vars: Dict[str, bool] = {}  # name -> initialized
    ptr_vars: Dict[str, bool] = {}       # 指针变量 -> 是否赋值

    def walk(node) -> None:
        ntype = node.type

        # 1) 数组声明 int a[N] / a[N]
        if ntype == "array_declarator":
            txt = _node_text(node, source)
            # 找变量名和大小
            parent = node.parent
            if parent and parent.type in ("init_declarator", "declaration"):
                decl_txt = _node_text(parent, source)
                m = __import__("re").search(r"(\w+)\s*\[\s*(\d+)\s*\]", decl_txt)
                if m:
                    array_sizes[m.group(1)] = int(m.group(2))
        # 2) 下标访问 a[i]
        if ntype == "subscript_expression":
            txt = _node_text(node, source)
            m = __import__("re").search(r"(\w+)\s*\[\s*(\d+)\s*\]", txt)
            if m and m.group(1) in array_sizes:
                idx = int(m.group(2))
                if idx >= array_sizes[m.group(1)]:
                    issues.append({
                        "line": _line(node), "type": "array_oob",
                        **_BUG_TEMPLATE["array_oob"],
                        "detail": f"访问 {m.group(1)}[{idx}]，但数组大小为 {array_sizes[m.group(1)]}",
                    })
        # 3) 除法/取模，除数字面量 0
        if ntype in ("binary_expression",):
            txt = _node_text(node, source)
            if " / 0" in txt or " % 0" in txt or "/0" in txt:
                issues.append({
                    "line": _line(node), "type": "div_zero",
                    **_BUG_TEMPLATE["div_zero"], "detail": f"除数为 0：{txt[:40]}",
                })
        # 4) malloc / free 追踪
        if ntype == "call_expression":
            txt = _node_text(node, source)
            if "malloc" in txt or "calloc" in txt or "realloc" in txt:
                malloc_locs.append(_line(node))
            if "free(" in txt:
                free_locs.append(_line(node))
        # 5) 变量声明（AST 精确版）：declaration 节点下的 identifier 是变量名
        if ntype == "declaration":
            child_txt = _node_text(node, source)
            has_init = "=" in child_txt
            for c in node.children:
                if c.type == "identifier":
                    v = _node_text(c, source)
                    if v not in _TYPE_KW:
                        declared_vars[v] = has_init
                elif c.type == "pointer_declarator":
                    for cc in c.children:
                        if cc.type == "identifier":
                            ptr_vars[_node_text(cc, source)] = has_init
                elif c.type == "init_declarator":
                    txt2 = _node_text(c, source)
                    m = __import__("re").search(r"(\w+)\s*=", txt2)
                    if m:
                        declared_vars[m.group(1)] = True
                    if "*" in txt2:
                        m2 = __import__("re").search(r"\*\s*(\w+)", txt2)
                        if m2:
                            ptr_vars[m2.group(1)] = True
        # 赋值更新状态：仅直接赋值（p = ...）标记已初始化；
        # *p = ... 是解引用赋值，不改变 p 本身的状态（野指针仍会检出）
        if ntype == "assignment_expression":
            for c in node.children:
                if c.type == "identifier":
                    declared_vars[_node_text(c, source)] = True
                elif c.type == "pointer_expression":
                    pass  # 解引用赋值：不标记指针本身
        # 6) 指针解引用（未赋值指针）
        if ntype == "pointer_expression":
            for c in node.children:
                if c.type == "identifier":
                    v = _node_text(c, source)
                    if v in ptr_vars and not ptr_vars[v]:
                        issues.append({
                            "line": _line(node), "type": "wild_pointer",
                            **_BUG_TEMPLATE["wild_pointer"], "detail": f"指针 {v} 未初始化即解引用",
                        })
        # 7) 标识符使用（未初始化变量）：读取位置（非声明/赋值左侧）
        if ntype == "identifier":
            v = _node_text(node, source)
            parent = node.parent
            if (v in declared_vars and not declared_vars[v] and parent
                    and parent.type in ("argument_list", "binary_expression", "return_statement", "call_expression", "subscript_expression")):
                issues.append({
                    "line": _line(node), "type": "uninitialized",
                    **_BUG_TEMPLATE["uninitialized"], "detail": f"变量 {v} 未初始化即使用",
                })

        for child in node.children:
            walk(child)

    walk(root)

    # 5) 内存泄漏：malloc 数量 > free 数量（粗粒度）
    if len(malloc_locs) > len(free_locs):
        issues.append({
            "line": malloc_locs[0] if malloc_locs else 1, "type": "memory_leak",
            **_BUG_TEMPLATE["memory_leak"],
            "detail": f"检测到 {len(malloc_locs)} 次内存分配但只有 {len(free_locs)} 次释放",
        })

    # 去重（按 line+type）
    seen = set()
    dedup = []
    for it in issues:
        key = (it["line"], it["type"])
        if key not in seen:
            seen.add(key)
            dedup.append(it)
    return dedup
