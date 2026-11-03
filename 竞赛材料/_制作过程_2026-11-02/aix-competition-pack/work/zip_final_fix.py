# -*- coding: utf-8 -*-
"""终版 zip 修复：seed mindmap 序列化 + 移除 4 个辅助 spec → 复验"""
import sys, re, zipfile, os, shutil, subprocess, sqlite3

sys.stdout.reconfigure(encoding="utf-8")
base = r"e:\开发\learnlabAI教学平台\_制作过程_2026-11-02\aix-competition-pack"
src = r"e:\开发\learnlabAI教学平台\AI+X_提交包\马其瑞+202521047080+LearnLab跨学科智能学习平台\03-源代码\LearnLab源代码.zip"
out = os.path.join(base, r"work\LearnLab源代码_final.zip")

DROP = {
    "frontend/e2e/_shot.spec.ts",
    "frontend/e2e/_shot_teacher.spec.ts",
    "frontend/e2e/_page-review.spec.ts",
    "frontend/e2e/image-gen.spec.ts",
}

zin = zipfile.ZipFile(src)
zout = zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED)
n_seed = 0
n_drop = 0
for item in zin.infolist():
    if item.filename in DROP:
        n_drop += 1
        continue
    data = zin.read(item.filename)
    if item.filename == "backend/seed_data.py":
        t = data.decode("utf-8")
        if "import json" not in t[:800]:
            t = t.replace("from datetime import datetime, timedelta",
                          "import json\nfrom datetime import datetime, timedelta", 1)
        a = len(re.findall(r"mindmap=(KP_\w+),", t))
        t = re.sub(r"mindmap=(KP_\w+),", r"mindmap=json.dumps(\1, ensure_ascii=False),", t)
        b = len(re.findall(r"mindmap=(\{[^\n]+\})(,)\r?\n", t))
        t = re.sub(r"mindmap=(\{[^\n]+\})(,)\r?\n", r"mindmap=json.dumps(\1, ensure_ascii=False)\2\n", t)
        n_seed = a + b
        data = t.encode("utf-8")
    zi = zipfile.ZipInfo(item.filename, date_time=item.date_time)
    zi.compress_type = zipfile.ZIP_DEFLATED
    zi.external_attr = item.external_attr
    zout.writestr(zi, data)
zout.close(); zin.close()
print(f"seed patch: {n_seed} 处, drop spec: {n_drop} 个")

# ---- 复验 1：zip 内 seed 提取实跑 ----
chk = os.path.join(base, r"work\seed_final_check")
if os.path.exists(chk):
    shutil.rmtree(chk)
z = zipfile.ZipFile(out)
os.makedirs(chk)
open(os.path.join(chk, "seed_data.py"), "wb").write(z.read("backend/seed_data.py"))
# app 包从 kp_check 复用（同一份源）
shutil.copytree(os.path.join(base, r"work\kp_check\app"), os.path.join(chk, "app"))
shutil.copy(os.path.join(base, r"work\kp_check\.env"), os.path.join(chk, ".env"))
# 排除 kp_check 的 app 内已 patch 内容？app 未改，无碍
py = r"e:\开发\learnlabAI教学平台\backend\venv\Scripts\python.exe"
r = subprocess.run([py, "seed_data.py"], cwd=chk, capture_output=True, text=True,
                   encoding="utf-8", errors="replace", timeout=300)
print("final zip seed rc:", r.returncode)
c = sqlite3.connect(os.path.join(chk, "ai_learning_v2.db"))
print("KP总数/有讲义:", c.execute(
    "select count(*), sum(case when document is not null and length(document)>10 then 1 else 0 end) from knowledge_points").fetchone())
c.close()

# ---- 复验 2：残留与 spec 清单 ----
pat = re.compile(r"aic|算法创新赛|AI\+学科交叉|21740176", re.I)
bad = 0
specs = []
for name in z.namelist():
    if name.endswith(".spec.ts"):
        specs.append(name)
    if name.endswith((".py", ".ts", ".tsx", ".js", ".md", ".json", ".txt", ".html", ".css", ".example")):
        t = z.read(name).decode("utf-8", errors="ignore")
        for l in t.splitlines():
            if pat.search(l) and "OpenAICompatible" not in l:
                bad += 1
print("残留行:", bad, "| spec 文件:", len(specs), "| 总条目:", len(z.namelist()),
      "| 大小: %.2fMB" % (os.path.getsize(out) / 1048576))
z.close()
