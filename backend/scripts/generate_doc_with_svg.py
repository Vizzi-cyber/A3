"""
生成包含base64编码SVG的DOC内容
"""
import json
import base64
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


def svg_block(svgs, label):
    if not svgs:
        return ""
    lines = ["\n\n**电路图示：**\n"]
    for i, svg in enumerate(svgs):
        # 使用HTML div包裹SVG，确保rehype-raw能正确处理
        lines.append('\n<div class="circuit-diagram">\n%s\n</div>\n' % svg)
    return "\n".join(lines)


def read_template(var_name):
    """从seed script读取模板内容（不含SVG）"""
    seed_path = os.path.join(SCRIPT_DIR, 'seed_circuit_content.py')
    with open(seed_path, 'r', encoding='utf-8') as f:
        content = f.read()

    pattern = r'%s = r"""(.*?)"""' % var_name
    match = re.search(pattern, content, re.DOTALL)
    if match:
        return match.group(1)
    return None


def write_doc(var_name, doc_content):
    """将生成的DOC写入文件"""
    output_path = os.path.join(SCRIPT_DIR, '%s.txt' % var_name.lower())
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(doc_content)
    print("Wrote %s: %d chars" % (var_name, len(doc_content)))


# ========== KP_E01 ==========
e01_s1 = get_svgs(1, "1.1")
e01_s2 = get_svgs(1, "1.2")
e01_s3 = get_svgs(1, "1.3")
e01_s4 = get_svgs(1, "1.5") + get_svgs(1, "1.6") + get_svgs(1, "1.7")
e01_s5 = get_svgs(1, "1.8")

template = read_template('KP_E01_DOC')
if template:
    # 在各节后插入SVG
    # 一、电路和电路模型
    template = template.replace(
        '- **分布参数元件：** 尺寸与信号波长可比拟',
        '- **分布参数元件：** 尺寸远小于信号波长可比拟' + svg_block(e01_s1, "图1.1")
    )
    # 二、电流和电压的参考方向
    template = template.replace(
        '3. $i_{ab}=5A$ 与 $i_{ba}=-5A$ 完全等价，没有区别',
        '3. $i_{ab}=5A$ 与 $i_{ba}=-5A$ 完全等价，没有区别' + svg_block(e01_s2, "图1.2")
    )
    # 三、电功率和能量
    template = template.replace(
        '**SI单位词头：**',
        svg_block(e01_s3, "图1.3") + '\n\n**SI单位词头：**'
    )
    # 四、电路元件
    template = template.replace(
        '含受控源电路的等效电阻',
        svg_block(e01_s4, "图1.4-1.7") + '\n\n含受控源电路的等效电阻'
    )
    # 五、基尔霍夫定律
    template = template.replace(
        '**推广：** KVL适用于开口电路。',
        '**推广：** KVL适用于开口电路。' + svg_block(e01_s5, "图1.8")
    )
    write_doc('KP_E01_DOC', template)

# ========== KP_E02 ==========
e02_s2 = get_svgs(2, "2.2")
e02_s3 = get_svgs(2, "2.3")
e02_s4 = get_svgs(2, "2.4")
e02_s5 = get_svgs(2, "2.5")
e02_s6 = get_svgs(2, "2.6")

template = read_template('KP_E02_DOC')
if template:
    template = template.replace(
        '### 对偶性',
        svg_block(e02_s2, "图2.2") + '\n\n### 对偶性'
    )
    template = template.replace(
        '**三支路电阻相等时：**',
        svg_block(e02_s3, "图2.3") + '\n\n**三支路电阻相等时：**'
    )
    template = template.replace(
        '但等效去掉后，会影响电压源电流',
        svg_block(e02_s4, "图2.4") + '\n\n但等效去掉后，会影响电压源电流'
    )
    template = template.replace(
        '**诺顿→戴维宁变换：**',
        svg_block(e02_s5, "图2.5") + '\n\n**诺顿→戴维宁变换：**'
    )
    template = template.replace(
        '**注意：** 含受控源电路',
        svg_block(e02_s6, "图2.6") + '\n\n**注意：** 含受控源电路'
    )
    write_doc('KP_E02_DOC', template)

# ========== KP_E03 ==========
e03_s1 = get_svgs(3, "3.1")
e03_s2 = get_svgs(3, "3.4")
e03_s3 = get_svgs(3, "3.6")
e03_s4 = get_svgs(3, "3.5")

template = read_template('KP_E03_DOC')
if template:
    template = template.replace(
        '解得：$I_1 = 3A$，$I_2 = 1.8A$，$I_3 = 1.2A$',
        '解得：$I_1 = 3A$，$I_2 = 1.8A$，$I_3 = 1.2A$' + svg_block(e03_s1, "图3.1")
    )
    template = template.replace(
        '解得：$I_{m1} = 2A$，$I_{m2} = 0A$',
        '解得：$I_{m1} = 2A$，$I_{m2} = 0A$' + svg_block(e03_s2, "图3.4")
    )
    template = template.replace(
        '- $I_3 = U_n/R_3 = 6/6 = 1A$',
        '- $I_3 = U_n/R_3 = 6/6 = 1A$' + svg_block(e03_s3, "图3.6")
    )
    template = template.replace(
        '4. 联立求解\n',
        '4. 联立求解' + svg_block(e03_s4, "图3.5") + '\n'
    )
    write_doc('KP_E03_DOC', template)

print("\nDone!")
