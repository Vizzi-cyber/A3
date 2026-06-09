"""
从HTML教材中提取SVG电路图，按章节分组输出到JSON文件
"""
import re
import json
import os

HTML_PATH = os.path.join(os.path.dirname(__file__),
    "..", "..", "【水木珞研】2027电气考研零基础课程讲义", "教材.html")

def extract_svgs_from_html(html_content):
    """提取所有SVG元素，按章节分组"""
    # 找到所有chapter div
    chapters = {}
    # 按 <h2 id="chX"> 分割
    chapter_pattern = re.compile(r'<h2 id="ch(\d+)">(.*?)</h2>', re.DOTALL)
    chapter_starts = list(chapter_pattern.finditer(html_content))

    for i, match in enumerate(chapter_starts):
        ch_num = int(match.group(1))
        ch_title = match.group(2).strip()
        start = match.end()
        end = chapter_starts[i+1].start() if i+1 < len(chapter_starts) else len(html_content)
        chapter_html = html_content[start:end]

        # 提取该章节的所有SVG
        svgs = re.findall(r'<svg[^>]*>.*?</svg>', chapter_html, re.DOTALL)
        # 提取该章节的小节标题
        sections = re.findall(r'<h3[^>]*>(.*?)</h3>', chapter_html, re.DOTALL)
        sections = [re.sub(r'<[^>]+>', '', s).strip() for s in sections]

        chapters[ch_num] = {
            "title": ch_title,
            "sections": sections,
            "svgs": svgs,
            "svg_count": len(svgs),
        }

    return chapters


def main():
    with open(HTML_PATH, 'r', encoding='utf-8') as f:
        html = f.read()

    chapters = extract_svgs_from_html(html)

    # 输出摘要
    for ch_num in sorted(chapters.keys()):
        ch = chapters[ch_num]
        print(f"Chapter {ch_num}: {ch['title']}")
        print(f"  Sections: {ch['sections']}")
        print(f"  SVGs: {ch['svg_count']}")
        print()

    # 保存到JSON
    output_path = os.path.join(os.path.dirname(__file__), "circuit_svgs.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(chapters, f, ensure_ascii=False, indent=2)
    print(f"Saved to {output_path}")


if __name__ == "__main__":
    main()
