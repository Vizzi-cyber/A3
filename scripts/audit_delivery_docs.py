"""审计网盘提交目录的文件名、文档事实和源码包完整性。"""
from __future__ import annotations

import re
import sys
import zipfile
from pathlib import Path

import pypdf

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
OUTER = "AIC-2026-21740176-省赛-一起搞事情-马其瑞"
PREFIX = "AIC-2026-21740176-AI+学科交叉-LearnLab跨学科智能学习平台"
NETDISK = ROOT / "交付材料" / "网盘提交" / OUTER / PREFIX
EXPECTED = {
    f"{PREFIX}-技术方案.pdf",
    f"{PREFIX}-功能说明.pdf",
    f"{PREFIX}-功能验证清单.pdf",
    f"{PREFIX}-运行说明.pdf",
    f"{PREFIX}-源代码.zip",
    f"{PREFIX}-README.txt",
}
PHOTO_DIR = NETDISK / "检录照片"


def pdf_text(path: Path) -> str:
    return "\n".join((page.extract_text() or "") for page in pypdf.PdfReader(str(path)).pages)


def main() -> int:
    errors: list[str] = []
    print("交付材料网盘目录审计")
    print(f"目录：{NETDISK}")

    if not NETDISK.is_dir():
        print("❌ 找不到网盘内层目录")
        return 1

    files = {p.name for p in NETDISK.iterdir() if p.is_file()}
    missing = sorted(EXPECTED - files)
    extra = sorted(files - EXPECTED)
    if missing:
        errors.extend(f"缺少文件：{name}" for name in missing)
    if extra:
        errors.extend(f"多余文件：{name}" for name in extra)
    if missing or extra:
        print("❌ 文件清单不一致")
        for item in errors:
            print(f"  - {item}")
    else:
        print(f"✅ 文件清单完整：{len(EXPECTED)} 项")

    if not PHOTO_DIR.is_dir() or not list(PHOTO_DIR.glob("*.jpg")):
        errors.append("缺少检录照片")
        print("❌ 检录照片目录为空")
    else:
        print(f"✅ 检录照片：{len(list(PHOTO_DIR.glob('*.jpg')))} 张")

    documents = {}
    for name in sorted(EXPECTED):
        path = NETDISK / name
        if path.suffix.lower() == ".pdf":
            try:
                reader = pypdf.PdfReader(str(path))
                documents[name] = pdf_text(path)
                print(f"✅ PDF：{name}（{len(reader.pages)} 页）")
            except Exception as exc:
                errors.append(f"PDF 无法读取：{name}：{exc}")
        elif path.suffix.lower() == ".txt":
            documents[name] = path.read_text(encoding="utf-8", errors="replace")

    text = "\n".join(documents[name] for name in documents if any(
        key in name for key in ["运行说明", "功能说明", "功能验证清单", "README"]
    ))
    forbidden = ["仍需人工验收", "仍未完成", "待录制", "本轮迭代", "评分复核", "GBK"]
    for word in forbidden:
        if word in text:
            errors.append(f"对外文档包含内部过程词：{word}")
    for word in ["8000", "教师端 6 个", "…源代码.zip", "…运行说明.pdf"]:
        if word in text:
            # PDF 正文可使用“源码包/运行说明”等省略称呼，不视为错误文件名。
            if word.startswith("…") and "…" in text:
                continue
            errors.append(f"对外文档包含旧口径或占位符：{word}")
    if "8001" not in text or "www.dreamlast.cn" not in text:
        errors.append("运行入口未完整包含线上地址或后端 8001 端口")
    if errors:
        print("⚠️ 文档关键词检查发现问题")
    else:
        print("✅ 对外文档事实关键词检查完成")

    source_zip = NETDISK / f"{PREFIX}-源代码.zip"
    if source_zip.is_file():
        try:
            with zipfile.ZipFile(source_zip) as archive:
                names = set(archive.namelist())
                required = {"README.md", "backend/app/main.py", "backend/requirements.txt", "frontend/package.json"}
                missing_zip = sorted(required - names)
                if missing_zip:
                    errors.extend(f"源码包缺少：{name}" for name in missing_zip)
                else:
                    readme = archive.read("README.md").decode("utf-8", errors="replace")
                    if "8001" not in readme or "www.dreamlast.cn" not in readme:
                        errors.append("源码包 README 与运行说明入口不一致")
                    print(f"✅ 源码包完整性通过：{len(names)} 个条目")
        except Exception as exc:
            errors.append(f"源码包无法读取：{exc}")

    if errors:
        print("\n审计发现：")
        for error in errors:
            print(f"  - {error}")
        print("\n结论：存在需处理项 ❌")
        return 1
    print("\n结论：网盘提交材料通过 ✅")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
