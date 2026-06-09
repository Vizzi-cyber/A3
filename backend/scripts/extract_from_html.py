"""
从HTML教材提取干净的markdown内容，保留inline SVG
"""
import re
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
HTML_PATH = r'C:\Users\15722\Desktop\开发\软件杯A3\【水木珞研】2027电气考研零基础课程讲义\教材.html'


def html_to_markdown(html_content):
    """将HTML转换为markdown格式，保留SVG"""
    text = html_content

    # 移除DOCTYPE, head, style, script
    text = re.sub(r'<!DOCTYPE[^>]*>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'<head>.*?</head>', '', text, flags=re.DOTALL)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL)

    # 处理标题
    text = re.sub(r'<h1[^>]*>(.*?)</h1>', r'# \1\n', text, flags=re.DOTALL)
    text = re.sub(r'<h2[^>]*>(.*?)</h2>', r'\n## \1\n', text, flags=re.DOTALL)
    text = re.sub(r'<h3[^>]*>(.*?)</h3>', r'\n### \1\n', text, flags=re.DOTALL)
    text = re.sub(r'<h4[^>]*>(.*?)</h4>', r'\n#### \1\n', text, flags=re.DOTALL)

    # 处理段落 - 保留内容
    text = re.sub(r'<p[^>]*>(.*?)</p>', r'\1\n', text, flags=re.DOTALL)

    # 处理加粗
    text = re.sub(r'<strong>(.*?)</strong>', r'**\1**', text, flags=re.DOTALL)
    text = re.sub(r'<b>(.*?)</b>', r'**\1**', text, flags=re.DOTALL)

    # 处理斜体
    text = re.sub(r'<em>(.*?)</em>', r'*\1*', text, flags=re.DOTALL)
    text = re.sub(r'<i>(.*?)</i>', r'*\1*', text, flags=re.DOTALL)

    # 处理行内代码
    text = re.sub(r'<code>(.*?)</code>', r'`\1`', text, flags=re.DOTALL)

    # 处理链接
    text = re.sub(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', r'[\2](\1)', text, flags=re.DOTALL)

    # 处理图片
    text = re.sub(r'<img[^>]*src="([^"]*)"[^>]*/?>', r'![](\1)', text)

    # 处理列表
    text = re.sub(r'<ul[^>]*>', '', text)
    text = re.sub(r'</ul>', '\n', text)
    text = re.sub(r'<ol[^>]*>', '', text)
    text = re.sub(r'</ol>', '\n', text)
    text = re.sub(r'<li[^>]*>(.*?)</li>', r'- \1\n', text, flags=re.DOTALL)

    # 处理引用块
    text = re.sub(r'<blockquote[^>]*>(.*?)</blockquote>', r'> \1\n', text, flags=re.DOTALL)

    # 处理代码块
    text = re.sub(r'<pre[^>]*><code[^>]*>(.*?)</code></pre>', r'```\n\1\n```\n', text, flags=re.DOTALL)
    text = re.sub(r'<pre[^>]*>(.*?)</pre>', r'```\n\1\n```\n', text, flags=re.DOTALL)

    # 保留SVG（不处理）
    # SVG已经在HTML中，保持原样

    # 处理div标签（移除非circuit的）
    text = re.sub(r'<div class="circuit"[^>]*>(.*?)</div>', r'\1\n', text, flags=re.DOTALL)
    text = re.sub(r'<div class="note"[^>]*>(.*?)</div>', r'> **注意：** \1\n', text, flags=re.DOTALL)
    text = re.sub(r'<div class="important"[^>]*>(.*?)</div>', r'> **重要：** \1\n', text, flags=re.DOTALL)
    text = re.sub(r'<div class="tip"[^>]*>(.*?)</div>', r'> **提示：** \1\n', text, flags=re.DOTALL)
    text = re.sub(r'<div class="example"[^>]*>(.*?)</div>', r'> **例题：** \1\n', text, flags=re.DOTALL)
    text = re.sub(r'<div class="section"[^>]*>(.*?)</div>', r'\1\n', text, flags=re.DOTALL)

    # 移除其他div标签
    text = re.sub(r'<div[^>]*>', '', text)
    text = re.sub(r'</div>', '\n', text)

    # 移除span标签
    text = re.sub(r'<span[^>]*>(.*?)</span>', r'\1', text, flags=re.DOTALL)

    # 移除br标签
    text = re.sub(r'<br[^>]*>', '\n', text)

    # 移除hr标签
    text = re.sub(r'<hr[^>]*/?>', '\n---\n', text)

    # 移除剩余HTML标签（但保留SVG）
    # 先保护SVG
    svg_pattern = r'(<svg[^>]*>.*?</svg>)'
    svgs = re.findall(svg_pattern, text, re.DOTALL)
    for i, svg in enumerate(svgs):
        text = text.replace(svg, f'__SVG_{i}__')

    # 移除其他标签
    text = re.sub(r'<[^>]+>', '', text)

    # 恢复SVG
    for i, svg in enumerate(svgs):
        text = text.replace(f'__SVG_{i}__', svg)

    # 清理多余空行
    text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)

    # 清理行首行尾空格
    lines = text.split('\n')
    lines = [line.strip() for line in lines]
    text = '\n'.join(lines)

    return text.strip()


def extract_chapter(html_content, chapter_num):
    """提取指定章节的内容"""
    # 找到章节开始
    chapter_pattern = f'<h2[^>]*id="ch{chapter_num}"[^>]*>.*?</h2>'
    chapter_match = re.search(chapter_pattern, html_content, re.DOTALL | re.IGNORECASE)

    if not chapter_match:
        print(f"Chapter {chapter_num} not found")
        return None

    start_pos = chapter_match.start()

    # 找到下一章或文件结尾
    next_chapter_pattern = f'<h2[^>]*id="ch{chapter_num + 1}"[^>]*>'
    next_chapter_match = re.search(next_chapter_pattern, html_content[start_pos + 100:], re.IGNORECASE)

    if next_chapter_match:
        end_pos = start_pos + 100 + next_chapter_match.start()
    else:
        end_pos = len(html_content)

    chapter_html = html_content[start_pos:end_pos]

    # 移除章末标记
    chapter_html = re.sub(r'<div class="chapter-end">.*?</div>', '', chapter_html, flags=re.DOTALL)

    return chapter_html


# 读取HTML
print(f"Reading HTML from: {HTML_PATH}")
with open(HTML_PATH, 'r', encoding='utf-8') as f:
    html_content = f.read()

print(f"HTML size: {len(html_content)} chars")

# 提取各章节
for chapter_num in [1, 2, 3]:
    print(f"\n=== Chapter {chapter_num} ===")

    chapter_html = extract_chapter(html_content, chapter_num)
    if not chapter_html:
        continue

    print(f"Chapter HTML size: {len(chapter_html)} chars")

    # 转换为markdown
    markdown = html_to_markdown(chapter_html)

    # 统计SVG数量
    svg_count = markdown.count('<svg')
    print(f"SVG count: {svg_count}")

    # 保存
    output_path = os.path.join(SCRIPT_DIR, f'kp_e{chapter_num:02d}_from_html.txt')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown)

    print(f"Saved to: {output_path}")
    print(f"Size: {len(markdown)} chars")

print("\nDone!")
