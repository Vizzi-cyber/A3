"""
本地真实环境全面验证（后端必须已启动在 8000 端口）
覆盖：原有功能 + AIC 新增功能，验证无冲突
运行：cd backend && python scripts/verify_live.py
"""
import sys
import json
import urllib.request
import urllib.error

BASE = "http://127.0.0.1:8000"
PASS = 0
FAIL = 0
FAILURES = []


def check(name: str, cond: bool, detail: str = ""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        FAILURES.append(f"{name}: {detail}")
        print(f"  ❌ {name} {detail}")


def req(method: str, path: str, body: dict = None, token: str = None, timeout: int = 60, parse_json: bool = True):
    from urllib.parse import quote
    # 路径中的中文（如 subject=C语言）需要 URL 编码
    path = quote(path, safe="/?&=:.%")
    url = BASE + path
    data = json.dumps(body).encode() if body is not None else None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    r = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(r, timeout=timeout) as resp:
            raw = resp.read()
            if not parse_json:
                return resp.status, raw
            return resp.status, json.loads(raw.decode())
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode())
        except Exception:
            return e.code, {}


def main():
    print("=" * 60)
    print("本地真实环境全面验证 (原有功能 + AIC新增功能)")
    print("=" * 60)

    # ---------- 登录（原有功能） ----------
    print("\n[1] 登录认证")
    status, data = req("POST", "/api/v1/auth/login", {"student_id": "student_001", "password": "123456"})
    check("学生登录", status == 200 and data.get("access_token"), f"{status} {str(data)[:100]}")
    student_token = data.get("access_token", "")
    status, data = req("POST", "/api/v1/auth/login", {"student_id": "T001", "password": "Teacher123"})
    check("教师登录", status == 200 and data.get("access_token"), f"{status} {str(data)[:100]}")
    teacher_token = data.get("access_token", "")

    # ---------- 原有功能回归 ----------
    print("\n[2] 原有学生端功能")
    for name, path in [
        ("dashboard", "/api/v1/dashboard/student_001/summary"),
        ("knowledge列表", "/api/v1/knowledge/list?subject=C语言"),
        ("每日练习", "/api/v1/daily-quiz/daily?count=3&subject=C语言"),
        ("学习画像", "/api/v1/profile/student_001"),
        ("知识库文件夹", "/api/v1/kb/folders"),
        ("游戏化积分", "/api/v1/gamification/student_001/points"),
        ("知识树", "/api/v1/gamification-tree/student_001/tree"),
        ("趋势分析", "/api/v1/trend/student_001/history"),
        ("反思日志", "/api/v1/log-reflection/student_001/reflections"),
        ("收藏", "/api/v1/favorites/student_001"),
        ("监控统计", "/api/v1/monitoring/api-stats?minutes=60"),
        ("LLM统计", "/api/v1/monitoring/llm-stats?minutes=60"),
    ]:
        try:
            status, data = req("GET", path, token=student_token)
            check(name, status == 200, f"{status}")
        except Exception as e:
            check(name, False, str(e)[:80])

    print("\n[3] 原有教师端功能")
    for name, path in [
        ("教师总览", "/api/v1/teacher/overview"),
        ("学生列表", "/api/v1/teacher/students"),
        ("薄弱点", "/api/v1/teacher/weak-points"),
        ("排行榜", "/api/v1/teacher/ranking"),
        ("学习预警", "/api/v1/teacher/alerts"),
        ("成绩导出CSV", None),
    ]:
        if path is None:
            continue
        try:
            status, data = req("GET", path, token=teacher_token)
            check(name, status == 200, f"{status}")
        except Exception as e:
            check(name, False, str(e)[:80])

    # 成绩导出（POST，响应为 CSV 不解析 JSON）
    try:
        status, data = req("POST", "/api/v1/teacher/export", {
            "report_type": "scores", "format": "csv", "student_ids": ["student_001"],
        }, token=teacher_token, parse_json=False)
        check("成绩导出CSV", status == 200 and len(data) > 100, f"{status}")
    except Exception as e:
        check("成绩导出CSV", False, str(e)[:80])

    # ---------- AIC 新增功能 ----------
    print("\n[4] D1 多模型注册（系统级验证）")
    status, data = req("GET", "/api/v1/teacher/system-info", token=teacher_token)
    check("系统信息", status == 200, f"{status}")

    print("\n[5] B1 功能使用频率")
    status, data = req("GET", "/api/v1/monitoring/feature-usage?student_id=student_001&days=7", token=student_token)
    check("学生查自己", status == 200, f"{status}")
    status, data = req("GET", "/api/v1/monitoring/feature-usage?days=7", token=student_token)
    check("学生查全班403", status == 403, f"{status}")
    status, data = req("GET", "/api/v1/monitoring/feature-usage?days=7", token=teacher_token)
    check("教师查全班", status == 200, f"{status}")

    print("\n[6] A2 学科元数据 + A3 跨学科路径")
    status, data = req("GET", "/api/v1/learning-path/courses", token=student_token)
    check("学科元数据", status == 200 and len(data.get("data", [])) == 3, f"{status}")
    status, data = req("POST", "/api/v1/learning-path/cross-discipline", {
        "student_id": "student_001", "target_kp_id": "kp_s05",
    }, token=student_token)
    ok = status == 200 and data.get("data", {}).get("cross_discipline", {}).get("is_cross_discipline") is True
    check("跨学科综合路径", ok, f"{status} {str(data)[:150]}")
    status, data = req("GET", "/api/v1/learning-path/dag/dependency-chain/kp_s06", token=student_token)
    check("依赖链", status == 200, f"{status}")

    print("\n[7] B2 实验行为采集")
    status, data = req("POST", "/api/v1/learning-data/experiment", {
        "student_id": "student_001", "experiment_type": "stm32_simulate",
        "action": "run", "detail": {"live_test": True}, "duration": 5,
    }, token=student_token)
    check("上报实验", status == 200, f"{status}")
    status, data = req("GET", "/api/v1/learning-data/experiment-stats?student_id=student_001", token=student_token)
    check("实验统计", status == 200, f"{status}")
    status, data = req("GET", "/api/v1/learning-data/experiment-stats", token=teacher_token)
    check("教师全班实验统计", status == 200, f"{status}")

    print("\n[8] B4 试点报告")
    status, data = req("GET", "/api/v1/teacher/pilot-report?days=30", token=teacher_token)
    ok = status == 200 and "summary" in data
    check("试点报告", ok, f"{status} {str(data)[:120]}")

    print("\n[9] C1 电路故障诊断（真实 LLM 调用一次验证链路）")
    status, data = req("POST", "/api/v1/circuit-analysis/analyze", {
        "netlist": [
            {"name": "V1", "type": "voltage_source", "node1": 0, "node2": 1, "value": 5},
            {"name": "R1", "type": "resistor", "node1": 1, "node2": 2, "value": 1000},
            {"name": "R2", "type": "resistor", "node1": 2, "node2": 3, "value": 1000000000},
        ],
        "node_voltages": {"n1": 5.0, "n2": 5.0},
        "is_diagnosis": True,
        "fault_description": "分压电路实测中间节点5V，怀疑R2断路",
        "student_answer": "A. R2 断路",
        "expected_answer": "A. R2 断路",
    }, token=student_token, timeout=90)
    ok = status == 200 and data.get("mode") == "diagnosis" and data.get("analysis")
    check("诊断模式真实调用", ok, f"{status} {str(data)[:120]}")

    # ---------- 前端 ----------
    print("\n[10] 前端页面")
    import urllib.request as u
    try:
        with u.urlopen("http://127.0.0.1:5173/", timeout=10) as resp:
            check("前端首页", resp.status == 200, str(resp.status))
    except Exception as e:
        check("前端首页", False, str(e)[:80])

    print("=" * 60)
    print(f"结果: {PASS} 通过, {FAIL} 失败")
    if FAILURES:
        print("失败项:")
        for f in FAILURES:
            print(f"  - {f}")
    print("=" * 60)
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
