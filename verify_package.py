# -*- coding: utf-8 -*-
"""源码包完整验收：解压 → 绝对路径/隐私扫描 → 后端启动测试"""
import os
import sys
import time
import tempfile
import zipfile
import urllib.request
import urllib.error

ZIP = os.path.join("交付材料", "2_源码包.zip")
EXTRACT = tempfile.mkdtemp(prefix="learnlab_verify_")

# 1. 解压
if os.path.exists(EXTRACT):
    import shutil
    shutil.rmtree(EXTRACT)
with zipfile.ZipFile(ZIP) as z:
    z.extractall(EXTRACT)
print("解压 OK:", EXTRACT)

# 2. 扫描：绝对路径 / 个人信息 / 内部代号
BAD_PATTERNS = [
    "E:/开发", "E:\\开发", "C:/Users", "C:\\Users", "E:/软件杯",
    "软件杯A3", "鹏哥", "水木珞研", "15722", "dreamlast",
    "马其瑞", "孙雨瑶", "居欣月", "Vizzi-cyber", "D:/开发",
]
hits = []
scanned = 0
for dirpath, dirnames, filenames in os.walk(EXTRACT):
    dirnames[:] = [d for d in dirnames if d not in ("node_modules", "__pycache__")]
    for fn in filenames:
        if os.path.splitext(fn)[1].lower() not in (
            ".py", ".ts", ".tsx", ".js", ".json", ".md", ".ini",
            ".example", ".html", ".css", ".txt",
        ):
            continue
        fp = os.path.join(dirpath, fn)
        try:
            text = open(fp, encoding="utf-8").read()
        except (UnicodeDecodeError, PermissionError):
            continue
        scanned += 1
        for pat in BAD_PATTERNS:
            if pat in text:
                rel = os.path.relpath(fp, EXTRACT)
                hits.append(f"{rel}: 含 '{pat}'")
print(f"扫描文件数: {scanned}")
print("命中:", hits if hits else "无")

# 3. 后端启动测试（用本地 venv 的 python，cwd=解压目录）
venv_python = os.path.abspath("backend/venv/Scripts/python.exe")
backend_dir = os.path.join(EXTRACT, "backend")
import subprocess
proc = subprocess.Popen(
    [venv_python, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8765"],
    cwd=backend_dir,
    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
)
ok = False
for i in range(60):
    time.sleep(2)
    try:
        with urllib.request.urlopen("http://127.0.0.1:8765/health", timeout=3) as resp:
            ok = resp.status == 200
            break
    except Exception:
        if i % 15 == 14:
            print(f"  仍在等待启动... ({(i + 1) * 2}s)")
        continue
print("后端启动(独立目录):", "OK /health=200" if ok else "FAIL")
if not ok:
    sys.exit(1)
proc.terminate()
try:
    proc.wait(timeout=10)
except Exception:
    proc.kill()

if hits:
    print("\n".join(hits[:10]))
    sys.exit(1)
print("验收通过")
