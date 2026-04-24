"""
全功能 API 测试脚本
测试所有后端接口，确保功能正常
"""
import requests
import json
import sys

BASE = "http://localhost:8000/api/v1"
TOKEN = None
STUDENT_ID = f"test_{__import__('time').time():.0f}"
PASS = 0
FAIL = 0

def log(msg, level="INFO"):
    print(f"[{level}] {msg}")

def call(method, path, data=None, headers=None, auth=True):
    global TOKEN
    h = headers or {}
    if auth and TOKEN:
        h["Authorization"] = f"Bearer {TOKEN}"
    url = f"{BASE}{path}"
    try:
        if method == "GET":
            r = requests.get(url, headers=h, timeout=15)
        elif method == "POST":
            r = requests.post(url, json=data, headers=h, timeout=30)
        elif method == "DELETE":
            r = requests.delete(url, headers=h, timeout=15)
        else:
            return None, f"Unsupported method {method}"
        return r, None
    except Exception as e:
        return None, str(e)

def check(name, resp, err, expect_code=200, check_fn=None):
    global PASS, FAIL
    if err:
        log(f"{name}: 请求失败 - {err}", "FAIL")
        FAIL += 1
        return False
    if resp.status_code != expect_code:
        log(f"{name}: 状态码异常 {resp.status_code} (期望 {expect_code})", "FAIL")
        log(f"  响应: {resp.text[:200]}", "DEBUG")
        FAIL += 1
        return False
    try:
        data = resp.json()
    except:
        data = resp.text
    if check_fn and not check_fn(data):
        log(f"{name}: 内容校验失败", "FAIL")
        log(f"  响应: {str(data)[:200]}", "DEBUG")
        FAIL += 1
        return False
    log(f"{name}: 通过", "PASS")
    PASS += 1
    return True

# ==================== 1. 认证 ====================
log("\n========== 1. 认证模块 ==========")

# 注册
resp, err = call("POST", "/auth/register", {
    "student_id": STUDENT_ID,
    "username": "Test User",
    "password": "TestPass123!"
}, auth=False)
check("注册", resp, err, 200, lambda d: d.get("status") == "success")

# 登录
resp, err = call("POST", "/auth/login", {
    "student_id": STUDENT_ID,
    "password": "TestPass123!"
}, auth=False)
if resp and resp.status_code == 200:
    TOKEN = resp.json().get("access_token")
    log(f"获取 Token: {TOKEN[:20]}...", "INFO")
check("登录", resp, err, 200, lambda d: "access_token" in d)

# 获取当前用户
resp, err = call("GET", "/auth/me")
check("获取当前用户", resp, err, 200, lambda d: d.get("data", {}).get("student_id") == STUDENT_ID)

# ==================== 2. 学生画像 ====================
log("\n========== 2. 学生画像 ==========")

# 获取画像（自动创建）
resp, err = call("GET", f"/profile/{STUDENT_ID}")
check("获取画像", resp, err, 200, lambda d: d.get("status") == "success" and "data" in d)

# 更新画像
resp, err = call("POST", f"/profile/{STUDENT_ID}/update", {
    "dimension": "knowledge",
    "updates": {"overall_score": 0.7, "subject_strengths": ["math"]}
})
check("更新画像(knowledge)", resp, err, 200)

# 分析对话
resp, err = call("POST", f"/profile/{STUDENT_ID}/analyze-conversation", {
    "conversation": "学生：我是大二计算机专业，擅长数学，但数据结构比较薄弱。喜欢通过代码实践来学习。"
})
check("分析对话", resp, err, 200, lambda d: d.get("status") == "success")

# 获取画像摘要
resp, err = call("GET", f"/profile/{STUDENT_ID}/summary")
check("画像摘要", resp, err, 200)

# ==================== 3. 学习路径 ====================
log("\n========== 3. 学习路径 ==========")

# 生成路径
resp, err = call("POST", "/learning-path/generate", {
    "student_id": STUDENT_ID,
    "target_topic": "掌握 C语言程序设计",
    "daily_duration": 90,
    "difficulty": 3,
    "preference": "balanced"
})
check("生成路径", resp, err, 200, lambda d: d.get("data", {}).get("path", {}).get("stages") is not None)

# 获取当前路径
resp, err = call("GET", f"/learning-path/{STUDENT_ID}/current")
check("获取当前路径", resp, err, 200)

# 调整路径
resp, err = call("POST", f"/learning-path/{STUDENT_ID}/adjust", {
    "feedback": "指针部分太难，多加点基础练习"
})
check("调整路径", resp, err, 200)

# ==================== 4. 资源生成 ====================
log("\n========== 4. 资源生成 ==========")

# 生成文档
resp, err = call("POST", "/resource/document/generate", {
    "student_id": STUDENT_ID,
    "topic": "C语言指针",
    "difficulty": "medium"
})
check("生成文档", resp, err, 200)

# 生成题目
resp, err = call("POST", "/resource/questions/generate", {
    "student_id": STUDENT_ID,
    "topic": "C语言数组",
    "count": 3
})
check("生成题目", resp, err, 200, lambda d: len(d.get("questions", [])) > 0)

# 生成思维导图
resp, err = call("POST", "/resource/mindmap/generate", {
    "student_id": STUDENT_ID,
    "topic": "C语言控制结构"
})
check("生成思维导图", resp, err, 200)

# 生成代码
resp, err = call("POST", "/resource/code/generate", {
    "student_id": STUDENT_ID,
    "topic": "冒泡排序",
    "language": "C"
})
check("生成代码", resp, err, 200)

# 执行代码（Python）
resp, err = call("POST", "/resource/code/execute", {
    "code": "print('Hello, World!')",
    "language": "Python"
})
check("执行Python代码", resp, err, 200, lambda d: "Hello, World!" in d.get("output", ""))

# 执行代码（C）
resp, err = call("POST", "/resource/code/execute", {
    "code": "#include <stdio.h>\nint main() { printf(\"Hello C!\"); return 0; }",
    "language": "C"
})
check("执行C代码", resp, err, 200)

# ==================== 5. 智能辅导 ====================
log("\n========== 5. 智能辅导 ==========")

resp, err = call("POST", "/tutor/ask", {
    "student_id": STUDENT_ID,
    "question": "什么是C语言的指针？",
    "session_id": f"{STUDENT_ID}_test"
})
check("智能辅导", resp, err, 200, lambda d: "response" in d)

# ==================== 6. 文生图 ====================
log("\n========== 6. 文生图 ==========")

resp, err = call("POST", "/image/generate", {
    "prompt": "一只可爱的猫在编程",
    "width": 1024,
    "height": 1024
})
check("文生图", resp, err, 200)

# ==================== 7. Dashboard ====================
log("\n========== 7. Dashboard ==========")

resp, err = call("GET", f"/dashboard/{STUDENT_ID}/summary")
check("Dashboard摘要", resp, err, 200)

# ==================== 8. 知识点 ====================
log("\n========== 8. 知识点 ==========")

resp, err = call("GET", "/knowledge/list")
check("知识点列表", resp, err, 200)

# ==================== 9. 学习数据 ====================
log("\n========== 9. 学习数据 ==========")

resp, err = call("POST", "/learning-data/record", {
    "student_id": STUDENT_ID,
    "kp_id": "kp_c_basics",
    "action": "study",
    "duration": 30,
    "progress": 0.5
})
check("记录学习数据", resp, err, 200)

resp, err = call("GET", f"/learning-data/{STUDENT_ID}/history")
check("学习历史", resp, err, 200)

# ==================== 10. 趋势 ====================
log("\n========== 10. 趋势分析 ==========")

resp, err = call("POST", "/trend/analyze", {
    "student_id": STUDENT_ID
})
check("趋势分析", resp, err, 200)

# ==================== 11. 收藏 ====================
log("\n========== 11. 收藏 ==========")

resp, err = call("POST", f"/favorites/{STUDENT_ID}", {
    "title": "C语言指针教程",
    "resource_type": "doc",
    "url": "http://example.com"
})
fav_id = None
if resp and resp.status_code == 200:
    fav_id = resp.json().get("id")
check("添加收藏", resp, err, 200)

if fav_id:
    resp, err = call("DELETE", f"/favorites/{STUDENT_ID}/{fav_id}")
    check("删除收藏", resp, err, 200)

# ==================== 12. 游戏化 ====================
log("\n========== 12. 游戏化 ==========")

resp, err = call("GET", f"/gamification/{STUDENT_ID}/points")
check("积分查询", resp, err, 200)

resp, err = call("GET", f"/gamification/{STUDENT_ID}/achievements")
check("成就查询", resp, err, 200)

# ==================== 13. 日志反思 ====================
log("\n========== 13. 日志反思 ==========")

resp, err = call("POST", "/log-reflection/reflections/create", {
    "student_id": STUDENT_ID,
    "date": "2026-04-24",
    "content": "今天学习了指针，感觉理解得不错",
    "mood": "happy",
    "tags": ["指针", "C语言"]
})
check("创建反思", resp, err, 200)

resp, err = call("GET", f"/log-reflection/{STUDENT_ID}/reflections")
check("反思列表", resp, err, 200)

# ==================== 总结 ====================
log("\n========== 测试总结 ==========")
total = PASS + FAIL
log(f"总计: {total} 项", "INFO")
log(f"通过: {PASS} 项", "PASS")
log(f"失败: {FAIL} 项", "FAIL" if FAIL > 0 else "PASS")

if FAIL > 0:
    sys.exit(1)
else:
    log("所有测试通过！", "PASS")
    sys.exit(0)
