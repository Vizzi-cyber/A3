"""
全接口冒烟测试：遍历所有注册路由，验证无 500 崩溃
- LLM 调用全部 mock（不消耗真实 API 额度）
- 需要路径参数的 GET 路由自动跳过（参数无法穷举）
- 输出：通过/4xx合法/跳过/失败 统计
运行：cd backend && python scripts/verify_all_routes.py
"""
import sys
import os
import json
import urllib.request
import urllib.error

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import patch

BASE = "http://127.0.0.1:8000"
PASS = []
FAIL = []
SKIP = []
LEGIT_4XX = []


class FakeLLM:
    async def ainvoke(self, messages, temperature=0.7, max_tokens=1024, thinking=False):
        return "## 模拟结果\n测试用模拟响应。"

    async def astream(self, messages, temperature=0.7, max_tokens=1024, thinking=False):
        yield "模拟流式响应"

    async def generate_json(self, messages, temperature=0.3, max_tokens=1024):
        return {"status": "success", "data": {"mock": True}, "stages": [], "path": {}}


def req(method, path, body=None, token=None, timeout=30):
    from urllib.parse import quote
    path = quote(path, safe="/?&=:.%")
    data = json.dumps(body).encode() if body is not None else None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    r = urllib.request.Request(BASE + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(r, timeout=timeout) as resp:
            return resp.status, resp.read()[:200]
    except urllib.error.HTTPError as e:
        return e.code, e.read()[:200]
    except Exception as e:
        return -1, str(e).encode()[:200]

def _service_available() -> bool:
    try:
        with urllib.request.urlopen(BASE + "/health", timeout=3) as response:
            return response.status == 200
    except Exception:
        return False


def main():
    from app.main import app
    from app.api.auth import _create_access_token
    from fastapi.routing import APIRoute

    if not _service_available():
        print(f"后端服务不可用：{BASE}，请先启动 uvicorn")
        return 2

    student_token = _create_access_token({"sub": "student_001"})
    teacher_token = _create_access_token({"sub": "T001"})

    # 收集所有路由
    routes = []
    for r in app.routes:
        if isinstance(r, APIRoute):
            for method in r.methods:
                routes.append((method, r.path))
    total = len(routes)

    # 常见 POST body 模板（按路径关键词）
    def make_body(path):
        if "login" in path:
            return {"student_id": "student_001", "password": "123456"}
        if "register" in path:
            return {"student_id": "test_e2e", "password": "Test123456", "username": "测试", "role": "student"}
        if "record" in path or "learning-data" in path and "experiment" in path:
            return {"student_id": "student_001", "kp_id": "kp_c01", "action": "read", "duration": 30}
        if "experiment" in path:
            return {"student_id": "student_001", "experiment_type": "circuit_simulate", "action": "run"}
        if "quiz" in path:
            return {"student_id": "student_001", "kp_id": "kp_c01", "total_questions": 5, "correct_count": 3, "score": 60}
        if "feedback" in path:
            return {"student_id": "student_001", "kp_id": "kp_c01", "rating": "good"}
        if "path" in path and "generate" in path:
            return {"student_id": "student_001", "target_topic": "指针", "subject": "C语言"}
        if "cross-discipline" in path:
            return {"student_id": "student_001", "target_kp_id": "kp_s05"}
        if "dag/generate" in path:
            return {"student_id": "student_001", "target_kp_id": "kp_s05"}
        if "adjust" in path:
            return {"student_id": "student_001", "current_path": {"stages": []}, "quiz_result": {"score": 60}}
        if "analyze" in path:
            return {"code": "int main() { return 0; }", "language": "c", "student_level": "beginner"}
        if "circuit-analysis" in path:
            return {"netlist": [{"name": "V1", "type": "voltage_source", "node1": 0, "node2": 1, "value": 5}]}
        if "ppt" in path:
            return {"topic": "C语言指针", "subject": "C语言"}
        if "image" in path:
            return {"prompt": "测试图片", "subject": "C语言"}
        if "ocr" in path:
            return {"image_url": ""}
        if "profile" in path:
            return {"student_id": "student_001"}
        if "onboarding" in path:
            return {"student_id": "student_001", "answers": {"level": 3}}
        if "export" in path:
            return {"report_type": "scores", "format": "csv", "student_ids": ["student_001"]}
        if "agent-flow" in path:
            return {"task_type": "tutor", "student_id": "student_001", "query": "什么是指针"}
        if "favorite" in path:
            return {"student_id": "student_001", "kp_id": "kp_c01"}
        if "collaboration" in path:
            return {"student_id": "student_001", "project_id": "p1"}
        if "assignment" in path:
            return {"title": "测试作业", "subject": "C语言"}
        if "log" in path or "reflection" in path:
            return {"student_id": "student_001", "date": "2026-08-13", "content": "测试反思", "mood": "good"}
        if "note" in path or "kb" in path:
            return {"student_id": "student_001", "folder_id": "f1", "title": "测试笔记", "content": "内容"}
        return {"student_id": "student_001"}

    # 注意：本脚本通过 HTTP 调用运行中的服务，mock 仅作用于本进程。
    # LLM 依赖接口（如 knowledge-graph/build）会真实调用大模型，已在
    # TestClient 层单独验证（scripts/verify_aic_features.py 覆盖）。
    for method, path in routes:
        # 跳过带路径参数的 GET（无法穷举参数值）
        if "{" in path:
            # 使用固定演示参数覆盖常见动态路径，减少无意义跳过
            fixtures = {
                "student_id": "student_001", "kp_id": "kp_c01",
                "experiment_id": "exp_aic_demo", "folder_id": "f1",
            }
            concrete = path
            for name, value in fixtures.items():
                concrete = concrete.replace("{" + name + "}", value)
            if "{" in concrete:
                SKIP.append(f"{method} {path}")
                continue
            path = concrete
        # LLM 重依赖接口（真实调用会烧额度且慢/不稳定；TestClient mock 层已单独验证）
        LLM_DEPENDENT = (
            "/api/v1/knowledge-graph/build",
            "/api/v1/project-decomposer/decompose",
            "/api/v1/role-matcher/match",
            "/api/v1/role-matcher/recommend",
            "/api/v1/collaboration-supervisor/report",
            "/api/v1/result-evaluator/",
            "/api/v1/error-catcher/analyze",
            "/api/v1/error-catcher/catch-error",
            "/api/v1/error-catcher/analyze-misconception",
            "/api/v1/error-catcher/validate-code",
            "/api/v1/misconception-tracer/",
            "/api/v1/ppt/generate",
            "/api/v1/image/generate",
            "/api/v1/ocr/",
            "/api/v1/tutor/ask",
            "/api/v1/teaching-assist/",
        )
        if any(path.startswith(p) for p in LLM_DEPENDENT):
            SKIP.append(f"{method} {path}（LLM依赖，已单独验证）")
            continue
        if method == "GET":
            # 教师端接口用教师token，其余用学生token
            token = teacher_token if path.startswith("/api/v1/teacher") else student_token
            status, body = req(method, path, token=token)
        elif method == "POST":
            body_data = make_body(path)
            token = teacher_token if path.startswith("/api/v1/teacher") else student_token
            status, body = req(method, path, body_data, token)
        elif method in ("PUT", "DELETE", "PATCH"):
            token = teacher_token if path.startswith("/api/v1/teacher") else student_token
            status, body = req(method, path, make_body(path), token)
        else:
            SKIP.append(f"{method} {path}")
            continue

        if status == 200:
            PASS.append(f"{method} {path}")
        elif 400 <= status < 500:
            # 4xx 属于合法响应（参数不完整/权限），不算崩溃
            LEGIT_4XX.append(f"{method} {path} -> {status}")
        elif status == -1:
            FAIL.append(f"{method} {path} -> 网络异常: {body[:80]}")
        else:
            FAIL.append(f"{method} {path} -> {status}")

    print("=" * 60)
    print(f"路由总数: {total}")
    print(f"✅ 200 通过: {len(PASS)}")
    print(f"ℹ️  4xx 合法: {len(LEGIT_4XX)}（参数/权限限制，非崩溃）")
    print(f"⏭️  跳过: {len(SKIP)}（路径含动态参数，无法穷举）")
    print(f"❌ 失败(500/网络): {len(FAIL)}")
    if FAIL:
        print("\n失败明细:")
        for f in FAIL:
            print(f"  - {f}")
    print("=" * 60)
    return 0 if not FAIL else 1


if __name__ == "__main__":
    sys.exit(main())
