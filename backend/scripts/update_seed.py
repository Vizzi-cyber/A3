"""
更新seed script，使用base64编码的SVG DOC
"""
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# 读取新生成的DOC文件
with open(os.path.join(SCRIPT_DIR, 'kp_e01_doc.txt'), 'r', encoding='utf-8') as f:
    new_kp_e01_doc = f.read()

with open(os.path.join(SCRIPT_DIR, 'kp_e02_doc.txt'), 'r', encoding='utf-8') as f:
    new_kp_e02_doc = f.read()

with open(os.path.join(SCRIPT_DIR, 'kp_e03_doc.txt'), 'r', encoding='utf-8') as f:
    new_kp_e03_doc = f.read()

# 读取当前seed script
seed_path = os.path.join(SCRIPT_DIR, 'seed_circuit_content.py')
with open(seed_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 替换函数
def replace_var(content, var_name, new_value):
    marker_start = '%s = r"""' % var_name
    marker_end = '"""'

    start_idx = content.find(marker_start)
    if start_idx < 0:
        print("ERROR: Could not find %s" % var_name)
        return content

    # 找到结束的 r"""
    search_start = start_idx + len(marker_start)
    end_idx = content.find(marker_end, search_start)
    if end_idx < 0:
        print("ERROR: Could not find end of %s" % var_name)
        return content

    new_section = '%s = r"""%s"""' % (var_name, new_value)
    content = content[:start_idx] + new_section + content[end_idx + len(marker_end):]
    print("Replaced %s (%d chars)" % (var_name, len(new_value)))
    return content


content = replace_var(content, 'KP_E01_DOC', new_kp_e01_doc)
content = replace_var(content, 'KP_E02_DOC', new_kp_e02_doc)
content = replace_var(content, 'KP_E03_DOC', new_kp_e03_doc)

# 保存更新后的seed script
with open(seed_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("\nSeed script updated successfully!")
