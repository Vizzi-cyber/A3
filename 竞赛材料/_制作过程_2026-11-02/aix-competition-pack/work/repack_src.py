# -*- coding: utf-8 -*-
"""重打源码包 v2：清除全部 AIC 残留（注释/日志文案/脚本文件名）"""
import sys, zipfile, re, os

sys.stdout.reconfigure(encoding="utf-8")
SRC = r"e:\开发\learnlabAI教学平台\交付材料\2_源码包.zip"
DST = r"e:\开发\learnlabAI教学平台\2026-11-02\aix-competition-pack\work\LearnLab源代码.zip"

# AIC 后跟中文/空白/冒号的才是真残留；OpenAICompatible 属误报
PAT = re.compile(r"AIC(?=[\u4e00-\u9fff\s：（“\"'])")
RENAME = {
    "backend/scripts/verify_aic_features.py": "backend/scripts/verify_core_features.py",
    "frontend/e2e/aic-features.spec.ts": "frontend/e2e/core-features.spec.ts",
}

def patch_text(t):
    t = t.replace(
        "LearnLab 跨学科智能学习平台（AIC 算法创新赛·AI+学科交叉）",
        "LearnLab 跨学科智能学习平台（“AI+X”跨学科智能创新应用竞赛）",
    )
    t = t.replace("# AIC 算法增强（知识追踪 / 间隔重复 / 多臂老虎机）",
                  "# 核心算法依赖（知识追踪 / 间隔重复 / 多臂老虎机）")
    t = t.replace("verify_aic_features", "verify_core_features")
    t = t.replace("aic-features", "core-features")
    t = t.replace("aic_features", "core_features")
    t = PAT.sub("核心", t)
    return t

TEXT_EXT = (".py", ".md", ".txt", ".json", ".html", ".js", ".ts", ".tsx", ".css", ".cfg", ".ini", ".yml", ".yaml", ".sql")

zin = zipfile.ZipFile(SRC)
zout = zipfile.ZipFile(DST, "w", zipfile.ZIP_DEFLATED)
ref_hits = []
for item in zin.infolist():
    name = item.filename
    data = zin.read(name)
    if name.lower().endswith(TEXT_EXT):
        t = patch_text(data.decode("utf-8", "ignore"))
        if "verify_aic_features" in t:
            ref_hits.append(name)
            t = t.replace("verify_aic_features", "verify_core_features")
        data = t.encode("utf-8")
    if name in RENAME:
        name = RENAME[name]
    zi = zipfile.ZipInfo(name, date_time=item.date_time)
    zi.compress_type = zipfile.ZIP_DEFLATED
    zout.writestr(zi, data)
zout.close()

# ---- 验证 ----
z2 = zipfile.ZipFile(DST)
bad = []
for n in z2.namelist():
    if n.lower().endswith(TEXT_EXT):
        t = z2.read(n).decode("utf-8", "ignore")
        for m in re.finditer(r"AIC", t):
            ctx = t[max(0, m.start() - 12): m.start() + 16]
            if "OpenAICompatible" not in ctx:
                bad.append((n, ctx.replace("\n", " ")))
    if re.search(r"aic|21740176", n, re.I):
        bad.append((n, "文件名"))
print("残留数:", len(bad))
for b in bad[:15]:
    print("  ", b[0], "|", b[1])
print("verify_aic_features 引用文件:", ref_hits)
print("条目数:", len(z2.namelist()), "大小:", os.path.getsize(DST))
