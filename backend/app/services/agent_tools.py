"""
Agent 工具注册表（Agentic 工具化）
把本地算法能力封装为 Agent 可调用的工具：
  - knowledge_search : 知识库 RAG 检索（BM25+jieba，返回相关笔记片段）
  - static_analyze   : C 代码 AST 静态分析（tree-sitter 规则引擎）
  - calc             : 表达式计算（安全求值）
这些工具不依赖 LLM API——Agent 决策层（LLM）只需选择工具并传参，
工具本身纯本地算法，可独立测试，也方便后续接 LangGraph ToolNode。
"""
from typing import Any, Callable, Dict, List, Optional


def _calc(expr: str) -> Dict[str, Any]:
    """安全表达式计算（仅允许数字/运算符/括号）。"""
    import ast
    import operator

    ops = {
        ast.Add: operator.add, ast.Sub: operator.sub,
        ast.Mult: operator.mul, ast.Div: operator.truediv,
        ast.Mod: operator.mod, ast.Pow: operator.pow,
        ast.USub: operator.neg, ast.UAdd: operator.pos,
    }

    def _eval(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in ops:
            return ops[type(node.op)](_eval(node.left), _eval(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in ops:
            return ops[type(node.op)](_eval(node.operand))
        raise ValueError("不支持的表达式")

    try:
        tree = ast.parse(expr, mode="eval")
        result = _eval(tree.body)
        return {"success": True, "result": round(float(result), 6)}
    except Exception as e:
        return {"success": False, "error": str(e)}


_TOOLS: Dict[str, Dict[str, Any]] = {
    "knowledge_search": {
        "description": "检索知识库笔记（RAG/BM25），返回与查询相关的笔记片段",
        "params": {"query": "搜索关键词", "top_k": "返回数量(默认5)"},
        "handler": None,  # 运行时注入（需 db + student_id）
    },
    "static_analyze": {
        "description": "C 语言代码静态分析（AST 规则引擎），扫描越界/野指针/未初始化/除零/内存泄漏",
        "params": {"code": "C 代码文本"},
        "handler": "static",
    },
    "calc": {
        "description": "计算数学表达式（如 2*3+4）",
        "params": {"expr": "数学表达式"},
        "handler": _calc,
    },
}


def list_tools() -> List[Dict[str, Any]]:
    """列出全部工具（含描述与参数说明）。"""
    return [
        {"name": name, **{k: v for k, v in meta.items() if k != "handler"}}
        for name, meta in _TOOLS.items()
    ]


def call_tool(name: str, args: Dict[str, Any],
              rag_search: Optional[Callable[[str, int], List[Dict[str, Any]]]] = None,
              analyzer: Optional[Callable[[str], List[Dict[str, Any]]]] = None) -> Dict[str, Any]:
    """
    调用工具。
    :param rag_search: 注入的 RAG 检索函数 (query, top_k) -> results（由调用方绑定 db/student）
    :param analyzer:   注入的静态分析函数 (code) -> issues
    """
    meta = _TOOLS.get(name)
    if not meta:
        return {"success": False, "error": f"未知工具: {name}"}

    if name == "knowledge_search":
        if rag_search is None:
            return {"success": False, "error": "RAG 检索工具未注入"}
        results = rag_search(str(args.get("query", "")), int(args.get("top_k", 5)))
        return {"success": True, "results": results[:8]}
    if name == "static_analyze":
        if analyzer is None:
            return {"success": False, "error": "静态分析工具未注入"}
        issues = analyzer(str(args.get("code", "")))
        return {"success": True, "issues": issues, "total": len(issues)}
    if name == "calc":
        return _calc(str(args.get("expr", "")))
    return {"success": False, "error": "工具调用失败"}
