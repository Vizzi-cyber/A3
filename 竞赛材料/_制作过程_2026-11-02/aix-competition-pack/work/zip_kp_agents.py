# -*- coding: utf-8 -*-
"""核对：zip 内 spec 文件清单 / 知识点实数 / 智能体实数"""
import sys, re, zipfile

sys.stdout.reconfigure(encoding="utf-8")
zp = r"e:\开发\learnlabAI教学平台\2026-11-02\aix-competition-pack\outputs\马其瑞+202521047080+LearnLab跨学科智能学习平台\03-源代码\LearnLab源代码.zip"
z = zipfile.ZipFile(zp)
names = z.namelist()

print("== zip 内 .spec 文件 ==")
specs = [n for n in names if n.endswith(".spec.ts")]
for n in specs:
    print(" ", n)

print("== zip 内 verify/seed 脚本 ==")
for n in names:
    b = n.rsplit("/", 1)[-1]
    if ("verify" in b or "seed" in b) and b.endswith(".py"):
        print(" ", n)

# 知识点实数（从项目 backend/seed_data.py 统计实际构造）
s = open(r"e:\开发\learnlabAI教学平台\backend\seed_data.py", encoding="utf-8").read()
kp_lines = [l for l in s.splitlines()
            if "KnowledgePointModel(" in l and not l.strip().startswith("#")]
print("== seed_data.py KnowledgePointModel 构造行:", len(kp_lines))
ids = re.findall(r'KnowledgePointModel\(\s*(?:\n\s*)?id="([^"]+)"', s)
print("   id= 形式:", len(ids), "唯一:", len(set(ids)))
# 无 id= 的构造（可能用 name=）
noid = [l for l in kp_lines if "id=" not in l]
print("   无 id= 的构造行:", len(noid))
for l in noid[:8]:
    print("    ", l.strip()[:90])

# 智能体：找 12 个的定义处
print("== 智能体定义检索 ==")
import glob, os
hits = []
for f in glob.glob(r"e:\开发\learnlabAI教学平台\backend\app\**\*.py", recursive=True):
    t = open(f, encoding="utf-8").read()
    for pat in (r"class \w*Agent\w*", r"^\s*AGENT\w*\s*=", r'"name":\s*"[^"]{2,8}(?:师|员|家|手)"'):
        m = re.findall(pat, t, re.M)
        if m:
            hits.append((os.path.relpath(f, r"e:\开发\learnlabAI教学平台\backend"), pat, len(m)))
for h in hits[:20]:
    print(" ", h)
