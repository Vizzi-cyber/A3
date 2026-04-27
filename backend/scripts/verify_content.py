import sys
sys.path.insert(0, '.')
from app.services.content_library import get_content

test_kps = ['kp_c01', 'kp_c09', 'kp_c11', 'kp_c13']
for kp_id in test_kps:
    d = get_content(kp_id)
    doc_len = len(d.get('document', ''))
    code_len = len(d.get('code', ''))
    qs_count = len(d.get('questions', []))
    mm_children = len(d.get('mindmap', {}).get('children', []))
    print(f'{kp_id}: doc={doc_len} code={code_len} qs={qs_count} mindmap_children={mm_children}')
    doc = d.get('document', '')
    fence_count = doc.count('```')
    if fence_count % 2 != 0:
        print(f'  [WARN] 未闭合代码块! fence_count={fence_count}')
    else:
        print(f'  代码块闭合正常 ({fence_count//2} 对)')
