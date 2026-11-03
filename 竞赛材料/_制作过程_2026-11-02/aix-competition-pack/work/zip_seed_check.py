# -*- coding: utf-8 -*-
"""检查 zip 内 seed_data.py 的 mindmap 处理 + spec 引用关系"""
import sys, re, zipfile

sys.stdout.reconfigure(encoding="utf-8")
zp = r"e:\开发\learnlabAI教学平台\2026-11-02\aix-competition-pack\outputs\马其瑞+202521047080+LearnLab跨学科智能学习平台\03-源代码\LearnLab源代码.zip"
z = zipfile.ZipFile(zp)

seed = z.read("backend/seed_data.py").decode("utf-8")
print("zip seed mindmap= 形式：")
forms = re.findall(r"mindmap\s*=\s*([^,\n]{0,50})", seed)
from collections import Counter
print(Counter(forms).most_common(8))
print("json.dumps mindmap 次数:", len(re.findall(r"mindmap\s*=\s*json\.dumps", seed)))
print("import json:", "import json" in seed.split("from datetime")[0] or "import json" in seed[:800])

model = z.read("backend/app/models/knowledge.py").decode("utf-8")
m = re.search(r"mindmap\s*=\s*Column\([^)]*\)", model)
print("zip 模型 mindmap 列:", m.group(0) if m else "未找到")

# 前端对 _shot/_page-review/image-gen 的引用
for spec in ("_shot.spec.ts", "_shot_teacher.spec.ts", "_page-review.spec.ts", "image-gen.spec.ts"):
    refs = []
    for n in z.namelist():
        if n.endswith((".ts", ".js", ".json", ".cjs", ".mjs")) and "node_modules" not in n:
            try:
                t = z.read(n).decode("utf-8", errors="ignore")
            except Exception:
                continue
            if spec.replace(".spec.ts", "") in t and not n.endswith(spec):
                refs.append(n)
    print(spec, "被引用于:", refs[:5] if refs else "无")
