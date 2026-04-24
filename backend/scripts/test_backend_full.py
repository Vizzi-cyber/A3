"""
后端全量接口测试
覆盖：auth、profile、tutor、dashboard、learning-path、resource、algorithm 等
"""
import requests, json, sys

BASE = "http://127.0.0.1:8001/api/v1"
STUDENT_ID = "student_001"
HEADERS = {"Content-Type": "application/json"}
TOKEN = None

def req(method, path, json_data=None, auth=True, timeout=10):
    url = f"{BASE}{path}"
    h = HEADERS.copy()
    if auth and TOKEN:
        h["Authorization"] = f"Bearer {TOKEN}"
    try:
        if method == "GET":
            return requests.get(url, headers=h, timeout=timeout)
        return requests.post(url, headers=h, json=json_data, timeout=timeout)
    except Exception as e:
        class FakeRes:
            status_code = 0
            def json(self): return {"error": str(e)}
            def text(self): return str(e)
        return FakeRes()

def log(title, r, key_checks=None):
    ok = r.status_code == 200
    status = "PASS" if ok else "FAIL"
    print(f"\n[{status}] {title}")
    if not ok:
        try:
            print(f"       Status: {r.status_code}, Body: {r.text[:200]}")
        except:
            print(f"       Status: {r.status_code}")
        return
    try:
        d = r.json()
        for k in (key_checks or []):
            val = d
            for part in k.split("."):
                val = val.get(part, {}) if isinstance(val, dict) else None
            if val is None or val == {} or val == []:
                print(f"       [WARN] 缺少字段: {k}")
            else:
                print(f"       [OK] {k}: {str(val)[:80]}")
    except Exception as e:
        print(f"       [WARN] JSON解析失败: {e}")

# ---------- 1. 登录 ----------
print("=" * 60)
print("[TEST SUITE] 后端全量接口测试")
print("=" * 60)

r = req("POST", "/auth/login", {"student_id": STUDENT_ID, "password": "123456"}, auth=False)
if r.status_code == 200:
    TOKEN = r.json().get("access_token")
    print(f"\n[PASS] 登录成功，获取 token")
else:
    print(f"\n[WARN] 登录失败 ({r.status_code})，后续需要认证的接口可能 401")

# ---------- 2. Profile ----------
log("GET /profile/{student_id}", req("GET", f"/profile/{STUDENT_ID}"), ["data.student_id", "data.weak_areas"])

# ---------- 3. Dashboard ----------
log("GET /dashboard/{student_id}/summary", req("GET", f"/dashboard/{STUDENT_ID}/summary"),
    ["status", "stats.weekly_hours", "algorithm_analysis.trend_analysis.trend_state", "algorithm_analysis.effect_evaluation.realtime_metrics.accuracy"])

# ---------- 4. Tutor (AI 辅导，耗时较长) ----------
print("\n[TEST] POST /tutor/ask (glm-4.6v，预计 5~12s)...")
r = req("POST", "/tutor/ask", {"student_id": STUDENT_ID, "question": "C语言指针是什么？", "session_id": f"{STUDENT_ID}_tutor"}, timeout=65)
log("POST /tutor/ask", r, ["response"])
if r.status_code == 200:
    reply = r.json().get("response", "")
    if reply and len(reply) > 10:
        print(f"       [OK] AI 回复长度: {len(reply)}")
    elif "思考时间" in reply:
        print(f"       [WARN] AI 返回思考时间提示")
    else:
        print(f"       [WARN] AI 回复为空或极短")

# ---------- 5. Learning Path ----------
log("GET /learning-path/{student_id}/current", req("GET", f"/learning-path/{STUDENT_ID}/current"), ["status", "nodes"])
log("POST /learning-path/generate", req("POST", "/learning-path/generate", {
    "student_id": STUDENT_ID, "target_topic": "掌握C语言基础", "daily_duration": 60, "difficulty": 3
}, timeout=20), ["status", "data.path.stages"])

# ---------- 6. Knowledge Points ----------
log("GET /knowledge/list", req("GET", "/knowledge/list"), ["status", "data"])

# ---------- 7. Resource Generation ----------
log("POST /resource/document/generate", req("POST", "/resource/document/generate", {
    "student_id": STUDENT_ID, "topic": "C语言指针", "kp_id": "kp_c04"
}, timeout=15), ["status", "document"])
log("POST /resource/code/generate", req("POST", "/resource/code/generate", {
    "student_id": STUDENT_ID, "topic": "C语言指针", "language": "C", "kp_id": "kp_c04"
}, timeout=15), ["status", "code"])

# ---------- 8. Gamification ----------
log("GET /gamification/{student_id}/points", req("GET", f"/gamification/{STUDENT_ID}/points"), ["status", "data.total_points"])
log("GET /gamification/{student_id}/tasks", req("GET", f"/gamification/{STUDENT_ID}/tasks"), ["status", "data"])
log("GET /gamification/{student_id}/achievements", req("GET", f"/gamification/{STUDENT_ID}/achievements"), ["status", "data"])

# ---------- 9. Learning Data ----------
log("GET /learning-data/{student_id}/history", req("GET", f"/learning-data/{STUDENT_ID}/history"), ["status", "data"])

# ---------- 10. Trend ----------
log("GET /trend/{student_id}/report", req("GET", f"/trend/{STUDENT_ID}/report"), ["status", "data.trend_state"])

# ---------- 11. Monitoring ----------
log("GET /monitoring/health", req("GET", "/monitoring/health", auth=False), ["status"])
log("GET /monitoring/api-stats", req("GET", "/monitoring/api-stats"), ["status", "data"])

# ---------- 12. Image Generation (ARK) ----------
print("\n[TEST] POST /image/generate (ARK/即梦，预计 3~8s)...")
r = req("POST", "/image/generate", {"prompt": "一只可爱的橘猫在草地上玩耍，插画风格", "width": 512, "height": 512}, timeout=15)
log("POST /image/generate", r, ["status", "task_id"])

print("\n" + "=" * 60)
print("[TEST SUITE COMPLETE]")
print("=" * 60)
