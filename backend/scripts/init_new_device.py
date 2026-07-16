"""
新设备一键初始化
运行：cd backend && python scripts/init_new_device.py
"""
import sqlite3, json, os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ai_learning_v2.db")
db = sqlite3.connect(DB_PATH)
cur = db.cursor()

print("=== 1. 检查用户账号 ===")
users = cur.execute("SELECT student_id, role FROM users").fetchall()
if not any(u[0] == "student_001" for u in users):
    print("  创建 student_001...")
    import hashlib, bcrypt
    pw = bcrypt.hashpw("123456".encode(), bcrypt.gensalt()).decode()
    cur.execute("INSERT INTO users (student_id, username, password, role) VALUES (?,?,?,?)",
                ("student_001", "测试学生", pw, "student"))
    cur.execute("INSERT INTO student_profiles (student_id) VALUES (?)", ("student_001",))
if not any(u[0] == "T001" for u in users):
    print("  创建教师 T001...")
    pw2 = bcrypt.hashpw("Teacher123".encode(), bcrypt.gensalt()).decode()
    cur.execute("INSERT INTO users (student_id, username, password, role) VALUES (?,?,?,?)",
                ("T001", "测试教师", pw2, "teacher"))
print(f"  现有用户: {len(users)} 个")

print("\n=== 2. 思维导图格式转换 ===")
rows = cur.execute("SELECT kp_id, mindmap FROM knowledge_points WHERE mindmap IS NOT NULL").fetchall()
converted = 0
for kp_id, mindmap in rows:
    if isinstance(mindmap, str) and mindmap.strip().startswith("#"):
        continue
    try:
        if isinstance(mindmap, str): data = json.loads(mindmap)
        elif isinstance(mindmap, dict): data = mindmap
        else: continue
        def to_mm(d, depth=0):
            p = "#" * (depth + 1)
            n = d.get("name", d.get("root", ""))
            return f"{p} {n}\n" + "".join(to_mm(c, depth+1) for c in d.get("children", [])) if n else ""
        mm = to_mm(data).strip()
        if mm:
            cur.execute("UPDATE knowledge_points SET mindmap=? WHERE kp_id=?", (mm, kp_id))
            converted += 1
    except: pass
print(f"  转换 {converted} 条")

print("\n=== 3. 注入 WikiLink（知识库关联）===")
notes = cur.execute("SELECT note_id, title, content FROM kb_notes").fetchall()
link_count = 0
for note_id, title, content in notes:
    if not content: content = ""
    # 检查内容是否已有关联
    if "关联笔记" in content or "[[" in content:
        continue
    # 找其他笔记标题出现在此内容中的
    links = []
    for other_id, other_title, _ in notes:
        if other_id == note_id or not other_title: continue
        if len(other_title) >= 2 and other_title in content:
            links.append(f"[[{other_title}]]")
    if links:
        new_content = content + f"\n\n**关联笔记**：" + "、".join(links[:5])
        cur.execute("UPDATE kb_notes SET content=? WHERE note_id=?", (new_content, note_id))
        link_count += 1
print(f"  更新 {link_count} 篇笔记的 WikiLink")

db.commit()
db.close()

print(f"\n初始化完成")
print(f"账号：student_001 / 123456(学生)，T001 / Teacher123(教师)")
