"""
迁移脚本：将数据库中所有 JSON 格式的思维导图转为 markmap 缩进文本
运行：cd backend && python scripts/migrate_mindmap_format.py
"""
import sqlite3, json, os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ai_learning_v2.db")

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

rows = cur.execute("""
    SELECT kp_id, name, mindmap FROM knowledge_points
    WHERE mindmap IS NOT NULL AND mindmap != ''
""").fetchall()

converted = 0
skipped = 0

for kp_id, name, mindmap in rows:
    # 已经是 markmap 格式
    if isinstance(mindmap, str) and mindmap.strip().startswith("#"):
        skipped += 1
        continue

    try:
        # 尝试解析 JSON
        if isinstance(mindmap, str):
            data = json.loads(mindmap)
        elif isinstance(mindmap, dict):
            data = mindmap
        else:
            skipped += 1
            continue

        def to_markmap(d, depth=0):
            prefix = "#" * (depth + 1)
            n = d.get("name", d.get("root", ""))
            if not n: return ""
            text = f"{prefix} {n}\n"
            for c in d.get("children", []):
                text += to_markmap(c, depth + 1)
            return text

        mm_text = to_markmap(data).strip()
        if mm_text:
            cur.execute("UPDATE knowledge_points SET mindmap=? WHERE kp_id=?", (mm_text, kp_id))
            converted += 1
            print(f"  [OK] {kp_id} {name}")
    except Exception:
        skipped += 1

conn.commit()
conn.close()
print(f"\n完成：转换 {converted} 条，跳过 {skipped} 条（已是 markmap 或无数据）")
