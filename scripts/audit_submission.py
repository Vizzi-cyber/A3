"""提交材料统一审计（评委可见内容的最终关卡）。

检查项：
  1. 内部信息     —— 待办/调试/私有资源/过程信息/清洗说明
  2. 数字一致性   —— 关键数字在各文档中是否与实测基准一致
  3. 交叉引用     —— 引用的文件是否真实存在于提交材料中
  4. 命名规范     —— 是否符合「编号-赛题名-作品名-XX」
  5. 公平性       —— 是否含学校名称/Logo/指导教师
  6. 格式残留     —— Markdown 标记、LaTeX 命令、乱码等

用法：python scripts/audit_submission.py
"""
from __future__ import annotations

import os
import re
import sys
import zipfile
from pathlib import Path

import pypdf

ROOT = Path(__file__).resolve().parent.parent
NETDISK = ROOT / "交付材料" / "网盘提交" / "AIC-2026-21740176-AI+学科交叉-LearnLab跨学科智能学习平台"
PREFIX = "AIC-2026-21740176-AI+学科交叉-LearnLab跨学科智能学习平台"
ZIP = ROOT / "交付材料" / "_内部母本勿传" / "2_源码包.zip"

# 实测基准值（跑过验证脚本得到的真实数字）
TRUTH = {"116": "算法断言", "211": "路由总数", "59": "E2E 用例",
         "39": "路由模块", "20": "问卷前测", "17": "问卷后测"}

INTERNAL = {
    "内部待办": ["仍需人工验收", "仍未完成", "待录制", "待补充", "人工视觉走查", "暂不收录"],
    "内部调试": ["GBK", "不代表功能验证失败"],
    "私有资源": ["GitHub", "Vizzi", "随仓库"],
    "过期口径": ["实验组", "对照组", "一键登录", "3-5分钟"],
    "过程信息": ["队友", "国庆", "答辩PPT", "评分复核", "六维评分", "本轮迭代", "剔除教师"],
}

# 语境豁免：命中关键词但属于正当用法的片段
EXEMPT = [
    "以编号SY01", "以试点编号SY01", "作答记录的8名学生",
]

# 格式残留：不应出现在成品 PDF 里的标记
FORMAT_LEAK = [
    (r"\*\*", "Markdown 加粗标记"),
    (r"~~", "Markdown 删除线标记"),
    (r"\\textbf", "LaTeX 命令"),
    (r"\\item", "LaTeX 命令"),
    (r"\\dots", "LaTeX 命令"),
    (r"\\allowbreak", "LaTeX 命令"),
]

SCHOOL_NAMES = ["大学", "学院", "校徽", "教务处", "指导教师", "指导老师"]

ok_all = True


def flat(s: str) -> str:
    return re.sub(r"\s", "", s)


def read_pdf(p: Path) -> str:
    return "".join((pg.extract_text() or "") for pg in pypdf.PdfReader(str(p)).pages)


def main() -> int:
    global ok_all
    if not NETDISK.is_dir():
        print(f"[错误] 找不到网盘目录：{NETDISK}", file=sys.stderr)
        return 1

    docs: dict[str, str] = {}
    for f in sorted(NETDISK.iterdir()):
        if f.suffix == ".pdf":
            docs[f.name.replace(PREFIX + "-", "")] = read_pdf(f)
        elif f.suffix == ".txt":
            docs[f.name.replace(PREFIX + "-", "")] = f.read_text(encoding="utf-8")

    # 表单直传件
    for name in ["1_技术方案.pdf", "4_佐证材料.pdf"]:
        p = ROOT / "交付材料" / name
        if p.is_file():
            docs[name] = read_pdf(p)
    intro = ROOT / "交付材料" / "参赛作品简介_300字.txt"
    if intro.is_file():
        docs["参赛作品简介.txt"] = intro.read_text(encoding="utf-8")

    # 源码包内文档
    zip_docs: dict[str, str] = {}
    if ZIP.is_file():
        z = zipfile.ZipFile(ZIP)
        for n in z.namelist():
            if n.lower().endswith((".md", ".txt")):
                zip_docs[n] = z.read(n).decode("utf-8", "ignore")

    print("=" * 74)
    print("提交材料审计")
    print("=" * 74)

    # 1 内部信息
    print("\n【一、内部信息检查】")
    bad = False
    for label, kws in INTERNAL.items():
        hits = []
        for n, t in docs.items():
            f = flat(t)
            for ex in EXEMPT:
                f = f.replace(flat(ex), "")
            hits += [f"{n}→{k}" for k in kws if k in f]
        if hits:
            print(f"  ❌ {label}: {hits[:3]}")
            bad = True
    if not bad:
        print("  ✅ 全部文档无内部信息")
    else:
        ok_all = False

    # 2 数字一致性
    print("\n【二、关键数字一致性】")
    print(f"  {'文档':<22}" + "".join(f"{v:<9}" for v in TRUTH.values()))
    for n, t in sorted(docs.items()):
        f = flat(t)
        row = f"  {n:<22}" + "".join(f"{'✔' if k in f else '·':<9}" for k in TRUTH)
        print(row)

    # 3 交叉引用
    print("\n【三、交叉引用检查】")
    exist = {x.name for x in NETDISK.iterdir()}
    refs = {"源代码.zip": f"{PREFIX}-源代码.zip", "运行说明.pdf": f"{PREFIX}-运行说明.pdf",
            "功能说明.pdf": f"{PREFIX}-功能说明.pdf", "功能验证清单.pdf": f"{PREFIX}-功能验证清单.pdf"}
    ref_bad = False
    for n, t in sorted(docs.items()):
        f = flat(t)
        for label, fn in refs.items():
            if flat(label) in f and fn not in exist:
                print(f"  ❌ {n} 引用了不存在的 {label}")
                ref_bad = True
    if not ref_bad:
        print("  ✅ 全部引用均指向存在的文件")
    else:
        ok_all = False

    # 4 命名规范
    print("\n【四、命名规范】")
    if NETDISK.name == PREFIX:
        print("  ✅ 根目录名合规")
    else:
        print(f"  ❌ 根目录名不合规: {NETDISK.name}")
        ok_all = False
    nbad = [f.name for f in NETDISK.iterdir() if f.is_file() and not f.name.startswith(PREFIX + "-")]
    print("  ✅ 文件名全部合规" if not nbad else f"  ❌ 不合规: {nbad}")
    if nbad:
        ok_all = False

    # 5 公平性
    print("\n【五、公平性检查】")
    fbad = []
    for n, t in {**docs, **zip_docs}.items():
        f = flat(t)
        for k in SCHOOL_NAMES:
            if k in f:
                fbad.append(f"{n}→{k}")
    if fbad:
        print(f"  ⚠️ 需人工确认: {fbad[:6]}")
    else:
        print("  ✅ 未发现学校名称/校徽/指导教师信息")

    # 6 格式残留
    print("\n【六、格式残留检查】")
    fbad = []
    for n, t in docs.items():
        if not n.endswith(".pdf"):
            continue
        for pat, desc in FORMAT_LEAK:
            if re.search(pat, t):
                fbad.append(f"{n}→{desc}")
    if fbad:
        print(f"  ❌ {fbad[:5]}")
        ok_all = False
    else:
        print("  ✅ 无 Markdown/LaTeX 标记残留")

    print("\n" + "=" * 74)
    print("结论：" + ("全部通过 ✅" if ok_all else "存在需处理项 ❌"))
    return 0 if ok_all else 1


if __name__ == "__main__":
    raise SystemExit(main())
