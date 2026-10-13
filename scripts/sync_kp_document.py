"""把 seed_data.py 里某个知识点的讲义同步到数据库（只 UPDATE 单条，不重建）。

背景：seed_data.py 是全量重建脚本（db.add_all + commit），重跑会清空现有
数据 —— 包括真实学生的注册记录。因此内容修订必须走这条路：改源头脚本，
再用本脚本把改动 UPDATE 进库。

用法：
    python scripts/sync_kp_document.py kp_e02

不带参数时列出库里所有知识点的 kp_id / name，便于确认目标。
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEED = ROOT / "backend" / "seed_data.py"
DB = ROOT / "backend" / "ai_learning_v2.db"


def load_documents_from_seed() -> dict[str, str]:
    """从 seed_data.py 解析出 {kp_id: document}。

    用 AST 解析而非 import —— seed_data.py 顶层会连库写数据，import 即触发。
    这里只读取 KnowledgePointModel(...) 调用的关键字参数，无副作用。
    """
    tree = ast.parse(SEED.read_text(encoding="utf-8"))
    docs: dict[str, str] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not (isinstance(func, ast.Name) and func.id == "KnowledgePointModel"):
            continue
        kwargs = {kw.arg: kw.value for kw in node.keywords if kw.arg}
        kp_id_node = kwargs.get("kp_id")
        doc_node = kwargs.get("document")
        if not isinstance(kp_id_node, ast.Constant) or not isinstance(doc_node, ast.Constant):
            continue
        if isinstance(kp_id_node.value, str) and isinstance(doc_node.value, str):
            docs[kp_id_node.value] = doc_node.value
    return docs


def main() -> int:
    import sqlite3

    docs = load_documents_from_seed()
    if not docs:
        print("[错误] 未能从 seed_data.py 解析出任何知识点讲义", file=sys.stderr)
        return 1

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    if len(sys.argv) < 2:
        print(f"seed_data.py 中解析到 {len(docs)} 个知识点讲义。")
        print("库里现有知识点：")
        for kp_id, name in cur.execute(
            "SELECT kp_id, name FROM knowledge_points ORDER BY kp_id"
        ):
            print(f"  {kp_id:<12} {name}")
        print("\n用法：python scripts/sync_kp_document.py <kp_id>")
        return 0

    target = sys.argv[1]
    if target not in docs:
        print(f"[错误] seed_data.py 中找不到 kp_id={target}", file=sys.stderr)
        return 1

    cur.execute("SELECT name, LENGTH(COALESCE(document,'')) FROM knowledge_points WHERE kp_id=?", (target,))
    row = cur.fetchone()
    if not row:
        print(f"[错误] 数据库中没有 kp_id={target}", file=sys.stderr)
        return 1

    name, old_len = row
    new_doc = docs[target]
    cur.execute("UPDATE knowledge_points SET document=? WHERE kp_id=?", (new_doc, target))
    conn.commit()
    print(f"[OK] {target} 《{name}》讲义已更新")
    print(f"     {old_len} 字 -> {len(new_doc)} 字")
    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
