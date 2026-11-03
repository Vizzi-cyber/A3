# -*- coding: utf-8 -*-
"""终检：E2E 用例数回数、.env.example 密钥扫描、配套 txt/说明一致性"""
import zipfile, re, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

zp = r"e:\开发\learnlabAI教学平台\AI+X_提交包\马其瑞+202521047080+LearnLab跨学科智能学习平台\03-源代码\LearnLab源代码.zip"
z = zipfile.ZipFile(zp)
# 1) E2E 用例数（test( / test.describe 计数近似；以 test( 为准）
total = 0
for n in z.namelist():
    if n.startswith("frontend/e2e/") and n.endswith(".spec.ts"):
        t = z.read(n).decode("utf-8", errors="replace")
        c = len(re.findall(r"\btest\(", t))
        total += c
        print(f"{os.path.basename(n)}: {c} 用例")
print("E2E 用例合计:", total)
# 2) .env.example 密钥扫描
env = z.read("backend/.env.example").decode("utf-8", errors="replace")
suspicious = [(m.start(), env[max(0,m.start()-30):m.end()+10]) for m in re.finditer(r"(sk-\w{20,}|api[_-]?key\s*=\s*\S{20,})", env, re.I)]
print(".env.example 可疑长密钥:", len(suspicious))
for _, c in suspicious[:3]:
    print("   …", c)
# 3) requirements/package.json 存在
for f in ["backend/requirements.txt", "frontend/package.json", "README.md"]:
    print(f, "存在" if f in z.namelist() else "!!缺失")
z.close()

# 4) 配套材料
base = r"e:\开发\learnlabAI教学平台\AI+X_提交包"
d = os.path.join(base, r"马其瑞+202521047080+LearnLab跨学科智能学习平台")
for f in [os.path.join(d, "网盘链接说明.txt"), os.path.join(d, r"05-其他材料\参赛作品简介.txt")]:
    print("\n----", os.path.basename(f), "----")
    print(open(f, encoding="utf-8").read()[:600])
# 5) README 与 AI说明 关键内容
ai = open(r"e:\开发\learnlabAI教学平台\_制作过程_2026-11-02\aix-competition-pack\work\AI工具使用说明.md", encoding="utf-8").read()
flat = re.sub(r"\s+", "", ai)
print("\n---- AI说明 四要素检查 ----")
for k, pat in {"工具选择及作用": r"工具选择|选用了哪些|使用的AI工具", "使用方式与频率": r"使用方式|使用频率|如何使用",
               "具体应用": r"具体|应用环节|应用场景", "自主创作声明": r"自主|原创|本人完成|自行完成"}.items():
    print(k, "有" if re.search(pat, flat) else "!!缺")
print("检索实现表述(应为BM25/jieba):", "BM25" in flat and "jieba" in flat, "| 失实'向量化':", bool(re.search(r"向量化模型|向量模型", flat)))
