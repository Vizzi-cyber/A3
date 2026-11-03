# -*- coding: utf-8 -*-
"""终版 zip 验证：条目数/spec 数/seed 修复/残留/命名"""
import zipfile, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
zp = r"e:\开发\learnlabAI教学平台\AI+X_提交包\马其瑞+202521047080+LearnLab跨学科智能学习平台\03-源代码\LearnLab源代码.zip"
z = zipfile.ZipFile(zp)
names = z.namelist()
print("条目数:", len(names))
specs = [n for n in names if n.startswith("frontend/e2e/") and n.endswith(".spec.ts")]
print("spec 文件:", len(specs), specs)
# seed 修复
seed = z.read("backend/seed_data.py").decode("utf-8", errors="replace")
print("seed import json:", "import json" in seed)
print("seed json.dumps mindmap 次数:", len(re.findall(r"json\.dumps\((?:\{\s*\"root\"|KP_\w+_MM)", seed)))
# 残留扫描（与 repack 规则一致：AIC 后跟 CJK/标点视为残留）
pat = re.compile(r"AIC(?=[\u4e00-\u9fff\s：（“\"'])")
hits = []
for n in names:
    if n.endswith((".py", ".ts", ".tsx", ".md", ".txt", ".json", ".html", ".js", ".cjs", ".css", ".tex")):
        try:
            t = z.read(n).decode("utf-8", errors="replace")
        except Exception:
            continue
        for mm in pat.finditer(t):
            hits.append((n, t[max(0,mm.start()-25):mm.end()+25].replace("\n"," ")))
print("文本残留 AIC:", len(hits))
for n, c in hits[:5]:
    print("   ", n, "…", c, "…")
# 二进制/其他文件名级残留
name_hits = [n for n in names if "aic" in n.lower() or "AIC" in n]
print("文件名 AIC:", len(name_hits), name_hits[:5])
# 旧命名残留
old = [n for n in names if "verify_aic_features" in n or "aic-features" in n]
print("旧文件名残留:", old)
# 大文件检查
big = [(n, i.file_size) for n in names for i in [z.getinfo(n)] if i.file_size > 3_000_000]
print(">3MB 文件:", big)
# .env / 密钥
envs = [n for n in names if n.endswith(".env") or n == "backend/.env"]
print("真 .env:", envs)
log_dirs = [n for n in names if "__pycache__" in n or n.endswith(".log") or "node_modules" in n]
print("缓存/日志/node_modules 条目:", len(log_dirs), log_dirs[:8])
