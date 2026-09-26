# -*- coding: utf-8 -*-
"""LearnLab AIC 源码包打包脚本

用法（仓库根目录执行）：
    python make_source_package.py

输出：交付材料/2_源码包.zip（zip 内 README.md 为 AIC 评审运行说明）
- 只含评审运行所需源码与演示数据库
- 排除虚拟环境/依赖目录/一次性开发脚本/个人路径文件
"""
import os
import zipfile

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(ROOT, "交付材料")
OUT = os.path.join(OUT_DIR, "2_源码包.zip")

INCLUDE = [
    "backend/app",
    "backend/alembic",
    "backend/alembic.ini",
    "backend/requirements.txt",
    "backend/requirements-lock.txt",
    "backend/seed_data.py",
    "backend/reports",
    "backend/scripts",
    "backend/static",
    "backend/ai_learning_v2.db",
    "backend/.env.example",
    "backend/image_tasks.json",
    "frontend/src",
    "frontend/public",
    "frontend/package.json",
    "frontend/package-lock.json",
    "frontend/vite.config.ts",
    "frontend/tailwind.config.js",
    "frontend/postcss.config.js",
    "frontend/tsconfig.json",
    "frontend/tsconfig.node.json",
    "frontend/eslint.config.js",
    "frontend/index.html",
]

# 目录级排除（虚拟环境/构建产物/缓存）
EXCLUDE_DIRS = {
    "__pycache__", "venv", "env", "node_modules", ".git", "dist",
    "logs", "test-results", "shots-local", "shots-audit", ".pytest_cache",
}
EXCLUDE_EXT = {".pyc", ".bak", ".log", ".db-shm", ".db-wal"}

# 一次性开发脚本不进评审包（含历史个人路径或已被 verify_* 取代）
EXCLUDE_NAMES = {
    "update_test_notes.py",
    "extract_from_html.py",
    "extract_svg.py",
    "import_pengge_code.py",
    "import_board_notes.py",
    "migrate_kp_content.py",
    "migrate_mindmap_format.py",
    "reformat_document.py",
    "fix_mindmap_seeds.py",
    "generate_clean_docs.py",
    "generate_doc_with_svg.py",
    "update_seed.py",
    "update_seed_with_clean.py",
    "svg_mapping.json",
    "test_ai_features.py",
    "verify_live.py",
}
EXCLUDE_PREFIXES = ("kp_e0",)


def excluded(rel: str, name: str) -> bool:
    if name in EXCLUDE_NAMES:
        return True
    if name.startswith(EXCLUDE_PREFIXES):
        return True
    if os.path.splitext(name)[1].lower() in EXCLUDE_EXT:
        return True
    parts = rel.replace("\\", "/").split("/")
    return bool(EXCLUDE_DIRS & set(parts))


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    count = 0
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for item in INCLUDE:
            full = os.path.join(ROOT, item)
            if os.path.isfile(full):
                z.write(full, item)
                count += 1
            elif os.path.isdir(full):
                for dirpath, dirnames, filenames in os.walk(full):
                    rel_dir = os.path.relpath(dirpath, ROOT)
                    dirnames[:] = [d for d in dirnames if not excluded(os.path.join(rel_dir, d), d)]
                    for fn in filenames:
                        rel = os.path.normpath(os.path.join(rel_dir, fn))
                        if excluded(rel, fn):
                            continue
                        z.write(os.path.join(dirpath, fn), rel)
                        count += 1
        # zip 内 README 用 AIC 评审运行说明（仓库根 README 是软件杯口吻，评审包不适用）
        readme_src = os.path.join(ROOT, "文档信息", "08_源码评审运行说明.md")
        z.write(readme_src, "README.md")
        count += 1
    print(f"打包完成: {count} 个文件, {os.path.getsize(OUT) / 1048576:.1f} MB -> {OUT}")


if __name__ == "__main__":
    main()
