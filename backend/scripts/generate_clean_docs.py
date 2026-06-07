"""
生成干净的DOC内容，包含inline SVG，无base64图片，无控制字符
"""
import json
import re
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# 读取SVG和映射
with open(os.path.join(SCRIPT_DIR, 'circuit_svgs.json'), 'r', encoding='utf-8') as f:
    all_svgs = json.load(f)

with open(os.path.join(SCRIPT_DIR, 'svg_mapping.json'), 'r', encoding='utf-8') as f:
    svg_mapping = json.load(f)


def get_svgs(chapter, section):
    ch_str = str(chapter)
    if ch_str in svg_mapping and section in svg_mapping[ch_str]:
        indices = svg_mapping[ch_str][section]
        return [all_svgs[ch_str][i] for i in indices]
    return []


def svg_block(svgs):
    if not svgs:
        return ""
    lines = ["\n"]
    for svg in svgs:
        # 清理控制字符
        cleaned = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', svg)
        lines.append('<div class="circuit-diagram">\n%s\n</div>\n' % cleaned)
    return "\n".join(lines)


def clean_text(text):
    """清理文本中的控制字符、乱码和已有的SVG"""
    # 移除控制字符
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', text)
    # 移除base64图片
    text = re.sub(r'!\[.*?\]\(data:image[^)]+\)', '', text)
    # 移除markdown图片引用
    text = re.sub(r'!\[.*?\]\([^)]+\)', '', text)
    # 移除已有的circuit-diagram div和SVG
    text = re.sub(r'<div class="circuit-diagram">.*?</div>', '', text, flags=re.DOTALL)
    # 移除独立的SVG标签
    text = re.sub(r'<svg[^>]*>.*?</svg>', '', text, flags=re.DOTALL)
    # 清理多余的空行
    text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
    return text


def extract_section_from_html(html_path, section_markers):
    """从HTML中提取指定section的文本内容"""
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()

    results = {}
    for marker in section_markers:
        # 找到marker位置
        idx = html.find(marker)
        if idx < 0:
            continue

        # 向前找到section开始
        section_start = html.rfind('<p', 0, idx)
        if section_start < 0:
            section_start = html.rfind('\n', 0, idx)

        # 向后找到section结束（下一个h3或文件结尾）
        next_h3 = html.find('<h3', idx + len(marker))
        if next_h3 < 0:
            next_h3 = len(html)

        section_html = html[section_start:next_h3]

        # 清理HTML
        section_html = re.sub(r'<svg[^>]*>.*?</svg>', '', section_html, flags=re.DOTALL)
        section_html = re.sub(r'<script[^>]*>.*?</script>', '', section_html, flags=re.DOTALL)
        section_html = re.sub(r'<style[^>]*>.*?</style>', '', section_html, flags=re.DOTALL)

        # 转换为简单文本
        section_html = re.sub(r'<p[^>]*>', '\n', section_html)
        section_html = re.sub(r'</p>', '\n', section_html)
        section_html = re.sub(r'<br[^>]*>', '\n', section_html)
        section_html = re.sub(r'<[^>]+>', '', section_html)
        section_html = re.sub(r'\n\s*\n', '\n\n', section_html)

        results[marker] = section_html.strip()

    return results


# ========== 第1章 ==========
print("Processing Chapter 1...")

# 读取已有的clean文件（已经包含正确的inline SVG）
with open(os.path.join(SCRIPT_DIR, 'kp_e01_clean.txt'), 'r', encoding='utf-8') as f:
    ch1_content = f.read()

# 只清理控制字符，不删除SVG
ch1_content = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', ch1_content)

# 验证SVG数量
svg_count = ch1_content.count('<svg')
print(f"Chapter 1: {svg_count} inline SVGs")

# 保存
with open(os.path.join(SCRIPT_DIR, 'kp_e01_final.txt'), 'w', encoding='utf-8') as f:
    f.write(ch1_content)
print(f"Saved kp_e01_final.txt ({len(ch1_content)} chars)")


# ========== 第2章 ==========
print("\nProcessing Chapter 2...")

# 读取当前seed中的KP_E02_DOC
with open(os.path.join(SCRIPT_DIR, 'seed_circuit_content.py'), 'r', encoding='utf-8') as f:
    seed_content = f.read()

pattern = r'KP_E02_DOC = r"""(.*?)"""'
match = re.search(pattern, seed_content, re.DOTALL)
if match:
    ch2_content = match.group(1)
    # 清理
    ch2_content = clean_text(ch2_content)

    # 获取第2章SVG
    ch2_svgs = all_svgs.get('2', [])
    print(f"Chapter 2: {len(ch2_svgs)} available SVGs")

    # 在正确位置插入SVG
    # 根据svg_mapping，第2章的SVG应该在以下位置：
    # 2.2: [0,1,2] - 对偶性之前
    # 2.3: [3] - 三支路电阻相等时之前
    # 2.4: [4,5] - 但等效去掉后之前
    # 2.5: [6] - 诺顿→戴维宁变换之前
    # 2.6: [7] - 注意：含受控源电路之前

    # 插入点标记
    insert_points = {
        '2.2': '### 对偶性',
        '2.3': '**三支路电阻相等时：**',
        '2.4': '但等效去掉后，会影响电压源电流',
        '2.5': '**诺顿→戴维宁变换：**',
        '2.6': '**注意：** 含受控源电路'
    }

    for section, marker in insert_points.items():
        if marker in ch2_content:
            svgs = get_svgs(2, section)
            if svgs:
                block = svg_block(svgs)
                ch2_content = ch2_content.replace(marker, block + '\n' + marker)

    svg_count = ch2_content.count('<svg')
    print(f"Chapter 2 final: {svg_count} inline SVGs")

    with open(os.path.join(SCRIPT_DIR, 'kp_e02_final.txt'), 'w', encoding='utf-8') as f:
        f.write(ch2_content)
    print(f"Saved kp_e02_final.txt ({len(ch2_content)} chars)")


# ========== 第3章 ==========
print("\nProcessing Chapter 3...")

pattern = r'KP_E03_DOC = r"""(.*?)"""'
match = re.search(pattern, seed_content, re.DOTALL)
if match:
    ch3_content = match.group(1)
    # 清理
    ch3_content = clean_text(ch3_content)

    # 获取第3章SVG
    ch3_svgs = all_svgs.get('3', [])
    print(f"Chapter 3: {len(ch3_svgs)} available SVGs")

    # 插入点标记
    insert_points = {
        '3.1': '解得：$I_1 = 3A$，$I_2 = 1.8A$，$I_3 = 1.2A$',
        '3.4': '解得：$I_{m1} = 2A$，$I_{m2} = 0A$',
        '3.5': '4. 联立求解',
        '3.6': '- $I_3 = U_n/R_3 = 6/6 = 1A$'
    }

    for section, marker in insert_points.items():
        if marker in ch3_content:
            svgs = get_svgs(3, section)
            if svgs:
                block = svg_block(svgs)
                ch3_content = ch3_content.replace(marker, marker + block)

    svg_count = ch3_content.count('<svg')
    print(f"Chapter 3 final: {svg_count} inline SVGs")

    with open(os.path.join(SCRIPT_DIR, 'kp_e03_final.txt'), 'w', encoding='utf-8') as f:
        f.write(ch3_content)
    print(f"Saved kp_e03_final.txt ({len(ch3_content)} chars)")


print("\nDone! Generated clean files for all chapters.")
