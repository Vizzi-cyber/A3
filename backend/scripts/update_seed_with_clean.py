"""
使用从HTML提取的干净内容更新seed文件
"""
import re
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def wrap_svg_with_div(content):
    """将SVG包裹在circuit-diagram div中"""
    # 匹配SVG标签（包括多行）
    svg_pattern = r'(<svg[^>]*>.*?</svg>)'

    def replace_svg(match):
        svg = match.group(1)
        # 检查是否已经在div中
        return f'\n<div class="circuit-diagram">\n{svg}\n</div>\n'

    # 使用DOTALL标志匹配多行SVG
    content = re.sub(svg_pattern, replace_svg, content, flags=re.DOTALL)

    # 清理多余的div嵌套
    content = re.sub(r'<div class="circuit-diagram">\s*<div class="circuit-diagram">', '<div class="circuit-diagram">', content)
    content = re.sub(r'</div>\s*</div>', '</div>', content)

    return content


def update_seed_variable(seed_content, var_name, new_value):
    """更新seed文件中的变量"""
    marker_start = f'{var_name} = r"""'
    marker_end = '"""'

    start_idx = seed_content.find(marker_start)
    if start_idx < 0:
        print(f"ERROR: Could not find {var_name}")
        return seed_content

    # 找到结束的 r"""
    search_start = start_idx + len(marker_start)
    end_idx = seed_content.find(marker_end, search_start)
    if end_idx < 0:
        print(f"ERROR: Could not find end of {var_name}")
        return seed_content

    new_section = f'{var_name} = r"""{new_value}"""'
    seed_content = seed_content[:start_idx] + new_section + seed_content[end_idx + len(marker_end):]
    print(f"Updated {var_name} ({len(new_value)} chars)")
    return seed_content


# 读取干净的提取内容
print("Reading extracted content...")

with open(os.path.join(SCRIPT_DIR, 'kp_e01_from_html.txt'), 'r', encoding='utf-8') as f:
    ch1_content = f.read()

with open(os.path.join(SCRIPT_DIR, 'kp_e02_from_html.txt'), 'r', encoding='utf-8') as f:
    ch2_content = f.read()

with open(os.path.join(SCRIPT_DIR, 'kp_e03_from_html.txt'), 'r', encoding='utf-8') as f:
    ch3_content = f.read()

# 包裹SVG
print("Wrapping SVGs with circuit-diagram div...")
ch1_content = wrap_svg_with_div(ch1_content)
ch2_content = wrap_svg_with_div(ch2_content)
ch3_content = wrap_svg_with_div(ch3_content)

# 验证
for name, content in [("Chapter 1", ch1_content), ("Chapter 2", ch2_content), ("Chapter 3", ch3_content)]:
    svg_count = content.count('<svg')
    div_count = content.count('<div class="circuit-diagram">')
    b64_count = content.count('data:image')
    ctrl_count = len(re.findall(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', content))
    print(f"{name}: {svg_count} SVGs, {div_count} divs, {b64_count} base64, {ctrl_count} ctrl chars")

# 读取当前seed文件
seed_path = os.path.join(SCRIPT_DIR, 'seed_circuit_content.py')
with open(seed_path, 'r', encoding='utf-8') as f:
    seed_content = f.read()

# 更新各章节
print("\nUpdating seed file...")
seed_content = update_seed_variable(seed_content, 'KP_E01_DOC', ch1_content)
seed_content = update_seed_variable(seed_content, 'KP_E02_DOC', ch2_content)
seed_content = update_seed_variable(seed_content, 'KP_E03_DOC', ch3_content)

# 保存更新后的seed文件
with open(seed_path, 'w', encoding='utf-8') as f:
    f.write(seed_content)

print("\nSeed file updated successfully!")

# 保存最终版本供参考
for name, content in [("e01", ch1_content), ("e02", ch2_content), ("e03", ch3_content)]:
    output_path = os.path.join(SCRIPT_DIR, f'kp_{name}_final_clean.txt')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Saved {output_path}")
