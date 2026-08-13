"""
全链路数据流验证（真实环境，前后端已启动）
学习行为 → 画像更新 → 路径生成 → 测验反馈 → 趋势分析 → 教师端报告
运行：cd backend && python scripts/verify_dataflow.py
"""
import sys
import json
import time
import urllib.request
import urllib.error

BASE = "http://127.0.0.1:8000"
PASS = 0
FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name} {detail}")


def req(method, path, body=None, token=None, timeout=90):
    from urllib.parse import quote
    path = quote(path, safe="/?&=:.%")
    data = json.dumps(body).encode() if body is not None else None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    r = urllib.request.Request(BASE + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(r, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode())
        except Exception:
            return e.code, {}


def main():
    print("=" * 60)
    print("全链路数据流验证（真实环境）")
    print("=" * 60)

    # ---------- 登录 ----------
    print("\n[1] 登录")
    status, data = req("POST", "/api/v1/auth/login", {"student_id": "student_001", "password": "123456"})
    check("学生登录", status == 200, f"{status}")
    student_token = data.get("access_token", "")
    status, data = req("POST", "/api/v1/auth/login", {"student_id": "T001", "password": "Teacher123"})
    teacher_token = data.get("access_token", "")

    # ---------- 学习行为 → 记录+积分 ----------
    print("\n[2] 学习行为数据流")
    total_points_before = 0
    status, data = req("GET", "/api/v1/gamification/student_001/points", token=student_token)
    if status == 200:
        total_points_before = data.get("data", {}).get("total_points", 0)
    check("获取积分", status == 200, f"{status}")

    for action, duration, progress in [
        ("watch", 300, 0.2), ("read", 600, 0.5), ("practice", 300, 0.8),
    ]:
        status, data = req("POST", "/api/v1/learning-data/record", {
            "student_id": "student_001", "kp_id": "kp_c03",
            "action": action, "duration": duration, "progress": progress,
        }, token=student_token)
        check(f"上报{action}", status == 200, f"{status} {str(data)[:80]}")

    status, data = req("GET", "/api/v1/gamification/student_001/points", token=student_token)
    total_points_after = data.get("data", {}).get("total_points", 0) if status == 200 else 0
    check("积分自动增长", total_points_after >= total_points_before, f"{total_points_before}→{total_points_after}")

    # 记录已写入
    status, data = req("GET", "/api/v1/learning-data/student_001/history?limit=5", token=student_token)
    records = data.get("records", []) if status == 200 else []
    check("学习历史可查", status == 200 and len(records) >= 3, f"records={len(records)}")

    # ---------- 测验 → 画像更新 ----------
    print("\n[3] 测验→画像 数据流")
    status, data = req("POST", "/api/v1/learning-data/quiz", {
        "student_id": "student_001", "kp_id": "kp_c10",
        "total_questions": 5, "correct_count": 2, "score": 40,
        "weak_tags": ["指针"],
    }, token=student_token)
    check("上报测验", status == 200, f"{status}")

    status, data = req("GET", "/api/v1/profile/student_001", token=student_token)
    profile = data.get("data", {}) if status == 200 else {}
    kb = profile.get("knowledge_base", {}) if status == 200 else {}
    check("画像knowledge_base更新", "指针" in kb or "kp_c10" in kb, f"kb keys: {list(kb.keys())[:8]}")
    weak = profile.get("weak_areas", []) if status == 200 else []
    check("画像薄弱点更新", "指针" in str(weak), f"weak: {weak}")

    # ---------- DAG 路径生成 ----------
    print("\n[4] 路径生成数据流")
    status, data = req("POST", "/api/v1/learning-path/cross-discipline", {
        "student_id": "student_001", "target_kp_id": "kp_s05",
    }, token=student_token)
    check("跨学科路径", status == 200, f"{status}")
    if status == 200:
        d = data.get("data", {})
        check("路径含阶段", len(d.get("stages", [])) > 0, f"stages={len(d.get('stages', []))}")

    status, data = req("POST", "/api/v1/learning-path/dag/generate", {
        "student_id": "student_001", "target_kp_id": "kp_s05",
    }, token=student_token)
    check("DAG路径", status == 200, f"{status}")

    # ---------- 趋势分析 ----------
    print("\n[5] 趋势数据流")
    status, data = req("POST", "/api/v1/trend/analyze", {"student_id": "student_001"}, token=student_token)
    check("趋势分析", status == 200, f"{status} {str(data)[:100]}")
    status, data = req("GET", "/api/v1/trend/student_001/history", token=student_token)
    check("趋势历史", status == 200, f"{status}")

    # ---------- 教师端数据流 ----------
    print("\n[6] 教师端数据流")
    status, data = req("GET", "/api/v1/teacher/pilot-report?days=30", token=teacher_token)
    check("试点报告(含新数据)", status == 200, f"{status}")
    if status == 200:
        s = data.get("summary", {})
        check("试点报告汇总", s.get("total_records", 0) >= 3, f"records={s.get('total_records')}")

    status, data = req("GET", "/api/v1/teacher/class-comparison?days=30", token=teacher_token)
    check("班级对比", status == 200, f"{status}")
    status, data = req("GET", "/api/v1/teacher/weak-points", token=teacher_token)
    tags = data.get("weak_tags", []) if status == 200 else []
    check("薄弱点统计(含指针)", any("指针" in str(t) for t in tags), f"tags={tags[:4]}")
    status, data = req("GET", "/api/v1/teacher/alerts", token=teacher_token)
    check("学习预警", status == 200, f"{status}")

    # ---------- Agent / LLM 真实链路 ----------
    print("\n[7] Agent + LLM 真实链路（各调用一次真实大模型）")
    status, data = req("POST", "/api/v1/error-catcher/analyze", {
        "code": "int main() { int *p; *p = 10; return 0; }",
        "language": "c",
        "student_level": "beginner",
    }, token=student_token, timeout=120)
    ok = status == 200 and data.get("status") == "success"
    check("错误诊断Agent+LLM", ok, f"{status} {str(data)[:120]}")

    status, data = req("POST", "/api/v1/tutor/ask", {
        "student_id": "student_001",
        "question": "C语言中指针和数组有什么区别？请用一句话回答。",
        "subject": "C语言",
    }, token=student_token, timeout=120)
    check("辅导Agent+LLM", status == 200, f"{status} {str(data)[:120]}")

    # ---------- 前端代理连接 ----------
    print("\n[8] 前端→后端代理连接")
    from urllib.parse import quote
    try:
        proxy_url = "http://127.0.0.1:5173/api/v1/dashboard/student_001/summary"
        r = urllib.request.Request(proxy_url, headers={"Authorization": f"Bearer {student_token}"})
        with urllib.request.urlopen(r, timeout=15) as resp:
            check("前端5173代理→后端", resp.status == 200, str(resp.status))
    except Exception as e:
        check("前端5173代理→后端", False, str(e)[:80])

    print("=" * 60)
    print(f"结果: {PASS} 通过, {FAIL} 失败")
    print("=" * 60)
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
