"""
AI 功能自动化测试脚本
测试项：
1. 智能辅导 /tutor/ask
2. Dashboard 聚合数据（含算法分析）
3. 学习路径生成 /learning-path/generate
4. 画像获取 /profile/{student_id}
5. 学习路径当前状态 /learning-path/{student_id}/current
"""
import requests, json, time, sys

BASE = "http://127.0.0.1:8001/api/v1"
STUDENT_ID = "student_001"
HEADERS = {"Content-Type": "application/json"}

# 使用预生成的测试 token（secret 需与后端一致）
TEST_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdHVkZW50XzAwMSIsImV4cCI6MTc3NzU1MDAzNX0.tahpZb-5x88DRrGQkRf7XNKepFzTYV7vjMCNJIrFp-c"
AUTH_HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {TEST_TOKEN}"
}

def log(title, res):
    print(f"\n{'='*60}")
    print(f"[TEST] {title}")
    print(f"Status: {res.status_code}")
    try:
        data = res.json()
        pretty = json.dumps(data, ensure_ascii=False, indent=2)
        if len(pretty) > 2000:
            pretty = pretty[:2000] + "\n... (truncated)"
        print(pretty)
    except Exception as e:
        print("Response:", res.text[:500])
    print(f"{'='*60}\n")

# ---------- 0. 登录获取真实 token ----------
print("[0/5] 尝试登录获取真实 token ...")
try:
    r = requests.post(
        f"{BASE}/auth/login",
        headers=HEADERS,
        json={"student_id": STUDENT_ID, "password": "123456"},
        timeout=5
    )
    if r.status_code == 200:
        real_token = r.json().get("access_token")
        if real_token:
            AUTH_HEADERS["Authorization"] = f"Bearer {real_token}"
            print(f"[PASS] 登录成功，获取到真实 token")
    else:
        print(f"[INFO] 登录失败（可能密码不对），使用预生成 token 继续测试")
except Exception as e:
    print(f"[INFO] 登录异常: {e}，使用预生成 token 继续测试")

# ---------- 1. 智能辅导 ----------
print("[1/5] 测试智能辅导 /tutor/ask ...")
try:
    r = requests.post(
        f"{BASE}/tutor/ask",
        headers=AUTH_HEADERS,
        json={"student_id": STUDENT_ID, "question": "C语言指针是什么？", "session_id": f"{STUDENT_ID}_test"},
        timeout=20
    )
    log("智能辅导 /tutor/ask", r)
    if r.status_code == 200:
        reply = r.json().get("response", "")
        if reply and "思考时间" not in reply:
            print(f"[PASS] AI 回复正常，长度: {len(reply)}")
        elif "思考时间" in reply:
            print(f"[WARN] AI 回复为思考时间提示")
        else:
            print(f"[WARN] AI 回复为空")
    elif r.status_code == 401:
        print("[FAIL] 未认证，无法测试 AI 辅导")
except Exception as e:
    print(f"[FAIL] 智能辅导请求异常: {e}\n")

# ---------- 2. Dashboard 聚合数据 ----------
print("[2/5] 测试 Dashboard 聚合数据 /dashboard/{student_id}/summary ...")
try:
    r = requests.get(f"{BASE}/dashboard/{STUDENT_ID}/summary", timeout=10)
    log("Dashboard Summary", r)
    d = r.json()
    algo = d.get("algorithm_analysis")
    if algo:
        print("[PASS] algorithm_analysis 存在")
        trend = algo.get("trend_analysis", {})
        effect = algo.get("effect_evaluation", {})
        print(f"       - trend_state: {trend.get('trend_state')}")
        print(f"       - trend_factor: {trend.get('trend_factor')}")
        print(f"       - predicted_mastery_3d: {trend.get('predicted_mastery_3d')}")
        print(f"       - accuracy: {effect.get('realtime_metrics',{}).get('accuracy')}")
        print(f"       - mastery: {effect.get('realtime_metrics',{}).get('mastery')}")
        print(f"       - next_score: {effect.get('predictions',{}).get('next_score')}")
        print(f"       - intervention: {effect.get('intervention',{}).get('priority')}")
    else:
        print("[FAIL] algorithm_analysis 不存在，后端代码可能没有更新")
except Exception as e:
    print(f"[FAIL] Dashboard 请求异常: {e}\n")

# ---------- 3. 学习路径生成 ----------
print("[3/5] 测试学习路径生成 /learning-path/generate ...")
try:
    r = requests.post(
        f"{BASE}/learning-path/generate",
        headers=AUTH_HEADERS,
        json={
            "student_id": STUDENT_ID,
            "target_topic": "掌握 C语言程序设计与数据结构基础",
            "daily_duration": 60,
            "difficulty": 3,
            "preference": "balanced"
        },
        timeout=20
    )
    log("学习路径生成", r)
    if r.status_code == 200:
        d = r.json()
        stages = d.get("data", {}).get("path", {}).get("stages", [])
        print(f"[PASS] 生成路径阶段数: {len(stages)}")
        for s in stages:
            print(f"       Stage {s.get('stage_no')}: {s.get('title')} ({s.get('hours')}h)")
    elif r.status_code == 401:
        print("[FAIL] 未认证，无法测试路径生成")
except Exception as e:
    print(f"[FAIL] 路径生成请求异常: {e}\n")

# ---------- 4. 画像获取 ----------
print("[4/5] 测试画像获取 /profile/{student_id} ...")
try:
    r = requests.get(f"{BASE}/profile/{STUDENT_ID}", headers=AUTH_HEADERS, timeout=10)
    log("画像获取", r)
    if r.status_code == 200:
        d = r.json()
        profile = d.get("data", {})
        print(f"[PASS] weak_areas: {profile.get('weak_areas', [])}")
        print(f"[PASS] interest_areas: {profile.get('interest_areas', [])}")
    elif r.status_code == 404:
        print("[FAIL] 画像接口 404，路由可能错误")
except Exception as e:
    print(f"[FAIL] 画像获取请求异常: {e}\n")

# ---------- 5. 学习路径当前状态 ----------
print("[5/5] 测试学习路径当前状态 /learning-path/{student_id}/current ...")
try:
    r = requests.get(f"{BASE}/learning-path/{STUDENT_ID}/current", timeout=10)
    log("学习路径当前状态", r)
    if r.status_code == 200:
        d = r.json()
        nodes = d.get("nodes", [])
        print(f"[PASS] 节点数: {len(nodes)}")
        # 检查是否是C语言内容
        first_title = nodes[0].get("title", "") if nodes else ""
        if "C" in first_title or "语言" in first_title or "概述" in first_title:
            print(f"[PASS] 路径内容已更新为 C语言课程: {first_title}")
        else:
            print(f"[WARN] 路径内容可能仍是旧数据: {first_title}")
        for n in nodes[:5]:
            print(f"       {n.get('title')}: {n.get('status')}")
except Exception as e:
    print(f"[FAIL] 当前路径请求异常: {e}\n")

print("\n[TEST COMPLETE]")
