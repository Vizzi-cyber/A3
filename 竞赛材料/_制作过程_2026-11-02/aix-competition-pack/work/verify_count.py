# -*- coding: utf-8 -*-
"""zip 内 verify 脚本断言计数，核对 29/23/23/116 口径"""
import sys, re, zipfile

sys.stdout.reconfigure(encoding="utf-8")
zp = r"e:\开发\learnlabAI教学平台\2026-11-02\aix-competition-pack\outputs\马其瑞+202521047080+LearnLab跨学科智能学习平台\03-源代码\LearnLab源代码.zip"
z = zipfile.ZipFile(zp)
for n in sorted(z.namelist()):
    b = n.rsplit("/", 1)[-1]
    if b.startswith("verify_") and b.endswith(".py"):
        t = z.read(n).decode("utf-8", errors="ignore")
        cnt_assert = len(re.findall(r"\bassert\b", t))
        cnt_ok = len(re.findall(r"\bok\s*\(|passes|PASS", t))
        cnt_def = len(re.findall(r"^def ", t, re.M))
        print(f"{b:34s} def={cnt_def:3d} assert={cnt_assert:3d} ok/ PASS≈{cnt_ok:3d}")
