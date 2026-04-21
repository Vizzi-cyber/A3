"""
API 快速测试脚本
用于验证后端各接口是否正常工作
"""
import sys
import requests

BASE_URL = "http://localhost:8000/api/v1"
STUDENT_ID = "test_student_001"


def test_health():
    r = requests.get("http://localhost:8000/health")
    assert r.status_code == 200
    print("[OK] Health check passed")


def test_profile():
    # 获取画像
    r = requests.get(f"{BASE_URL}/profile/{STUDENT_ID}")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "success"
    print("[OK] Get profile passed")

    # 更新画像
    r = requests.post(
        f"{BASE_URL}/profile/{STUDENT_ID}/update",
        json={"dimension": "knowledge", "updates": {"python": 0.8}},
    )
    assert r.status_code == 200
    print("[OK] Update profile passed")

    # 获取摘要
    r = requests.get(f"{BASE_URL}/profile/{STUDENT_ID}/summary")
    assert r.status_code == 200
    print("[OK] Profile summary passed")


def test_learning_path():
    # 生成路径
    r = requests.post(
        f"{BASE_URL}/learning-path/generate",
        json={"student_id": STUDENT_ID, "target_topic": "Python 递归"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "success"
    print("[OK] Generate learning path passed")

    # 当前路径
    r = requests.get(f"{BASE_URL}/learning-path/{STUDENT_ID}/current")
    assert r.status_code == 200
    print("[OK] Get current path passed")


def test_resource():
    # 生成文档
    r = requests.post(
        f"{BASE_URL}/resource/document/generate",
        json={"student_id": STUDENT_ID, "topic": "递归算法"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "success"
    print("[OK] Generate document passed")

    # 生成题目
    r = requests.post(
        f"{BASE_URL}/resource/questions/generate",
        json={"student_id": STUDENT_ID, "topic": "递归算法", "count": 3},
    )
    assert r.status_code == 200
    print("[OK] Generate questions passed")


def test_tutor():
    r = requests.post(
        f"{BASE_URL}/tutor/ask",
        json={"student_id": STUDENT_ID, "question": "什么是递归？"},
    )
    assert r.status_code == 200
    data = r.json()
    assert "response" in data
    print("[OK] Tutor ask passed")


def main():
    print(f"Testing API at {BASE_URL}...\n")
    try:
        test_health()
        test_profile()
        test_learning_path()
        test_resource()
        test_tutor()
        print("\nAll tests passed!")
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
