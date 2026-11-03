# -*- coding: utf-8 -*-
"""zip 注释级残留替换 + 终检（临时脚本）"""
import zipfile, re, sys, os
sys.stdout.reconfigure(encoding="utf-8")

src = r"..\outputs\马其瑞+202521047080+LearnLab跨学科智能学习平台\03-源代码\LearnLab源代码.zip"
dst = r"LearnLab源代码_fix2.zip"
os.chdir(r"e:\开发\learnlabAI教学平台\2026-11-02\aix-competition-pack\work")

repl = {
    "backend/app/api/ai_algorithms.py": [("（核心 算法创新赛核心模块）", "（核心模块）")],
    "backend/app/api/learning_path.py": [("（核心 算法创新赛 · AI+学科交叉）", "")],
    "backend/app/models/course.py": [("支撑\"AI+学科交叉\"定位", "支撑跨学科定位")],
    "backend/app/models/experiment.py": [("（核心 AI+学科交叉赛道）", "")],
    "backend/scripts/seed_cross_discipline.py": [("（核心算法创新赛 · AI+学科交叉）", "")],
    "frontend/src/pages/LearningPath.tsx": [("（核心 AI+学科交叉）", "")],
    "frontend/src/pages/circuit-simulator/fault-templates.ts": [("（核心 算法创新赛 · AI+学科交叉 亮点功能）", "（核心亮点功能）")],
    "frontend/src/pages/circuit-simulator/FaultExperimentDialog.tsx": [("（核心 \"AI+学科交叉\"亮点功能）", "（核心亮点功能）")],
}

zin = zipfile.ZipFile(src)
zout = zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED)
n = 0
for item in zin.infolist():
    data = zin.read(item.filename)
    if item.filename in repl:
        t = data.decode("utf-8")
        for old, new in repl[item.filename]:
            assert old in t, f"NOT FOUND in {item.filename}: {old}"
            t = t.replace(old, new)
        data = t.encode("utf-8")
        n += 1
    zout.writestr(item, data)
zout.close()
zin.close()
print("replaced:", n)

z = zipfile.ZipFile(dst)
pat = re.compile(r"aic|算法创新赛|AI\+学科交叉|21740176", re.I)
bad = []
for name in z.namelist():
    if name.endswith((".py", ".ts", ".tsx", ".js", ".md", ".json", ".txt", ".html", ".css", ".example")):
        t = z.read(name).decode("utf-8", errors="ignore")
        for l in t.splitlines():
            if pat.search(l) and "OpenAICompatible" not in l:
                bad.append((name, l.strip()[:80]))
print("zip 残留行:", len(bad))
for b in bad[:10]:
    print("  ", b)
print("size:", os.path.getsize(dst), "| entries:", len(z.namelist()))
