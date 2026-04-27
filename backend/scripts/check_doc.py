import sqlite3
conn = sqlite3.connect('ai_learning_v2.db')
cur = conn.cursor()

for kp_id in ['kp_c03', 'kp_c11', 'kp_c13']:
    cur.execute('SELECT document FROM knowledge_points WHERE kp_id=?', (kp_id,))
    doc = cur.fetchone()[0]
    lines = doc.split('\n')
    print(f'\n=== {kp_id} ===')
    print(f'长度: {len(doc)}, 行数: {len(lines)}')
    code_blocks = sum(1 for l in lines if l == '```c')
    print(f'代码块: {code_blocks}')
    for i, line in enumerate(lines[:30]):
        print(f'{i+1:3d}: {line}')

conn.close()
