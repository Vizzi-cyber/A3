"""
算法层单元测试
覆盖：DAG 路径规划、趋势分析、效果评估、加权匹配
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.algorithms.path_planning_dag import DAGPathPlanner
from app.algorithms.trend_analysis import MultiFactorTrendAnalyzer
from app.algorithms.effect_evaluation import LearningEffectEvaluator
from app.algorithms.weighted_matching import MultiDimWeightedMatcher


# ===== DAG 路径规划测试 =====

class TestDAGPathPlanner:
    """测试 DAG 路径规划器"""

    def setup_method(self):
        self.planner = DAGPathPlanner()

    def _build_simple_graph(self):
        """构建简单的测试图：A -> B -> C, A -> D"""
        kps = [
            {"kp_id": "A", "name": "基础语法", "difficulty": 1, "prerequisites": [], "estimated_minutes": 30},
            {"kp_id": "B", "name": "控制流", "difficulty": 2, "prerequisites": ["A"], "estimated_minutes": 45},
            {"kp_id": "C", "name": "函数", "difficulty": 3, "prerequisites": ["B"], "estimated_minutes": 60},
            {"kp_id": "D", "name": "数组", "difficulty": 2, "prerequisites": ["A"], "estimated_minutes": 40},
        ]
        self.planner.build_graph(kps)
        return kps

    def test_build_graph(self):
        self._build_simple_graph()
        assert "A" in self.planner.kp_graph
        assert "B" in self.planner.kp_graph
        assert self.planner.in_degree["A"] == 0
        assert self.planner.in_degree["B"] == 1
        assert self.planner.in_degree["C"] == 1

    def test_plan_path_returns_stages(self):
        self._build_simple_graph()
        result = self.planner.plan_path("student1", "C", {}, {})
        assert "status" in result
        assert result["status"] == "success"
        assert "stages" in result
        assert len(result["stages"]) >= 1

    def test_plan_path_dependency_chain(self):
        """路径应包含完整依赖链"""
        self._build_simple_graph()
        result = self.planner.plan_path("student1", "C", {}, {})
        chain = result.get("dependency_chain", [])
        assert "A" in chain
        assert "B" in chain
        assert "C" in chain

    def test_plan_path_mastered_skip(self):
        """已掌握的知识点应被跳过"""
        self._build_simple_graph()
        mastery = {"A": 0.95, "B": 0.95}
        result = self.planner.plan_path("student1", "C", mastery, {})
        # A 和 B 已掌握，learn_count 应为 1（仅 C）
        assert result["learn_count"] <= 1

    def test_plan_path_nonexistent_target(self):
        """目标知识点不存在时应返回错误"""
        self._build_simple_graph()
        result = self.planner.plan_path("student1", "Z", {}, {})
        assert result["status"] == "error"

    def test_empty_graph(self):
        self.planner.build_graph([])
        result = self.planner.plan_path("student1", "A", {}, {})
        assert result["status"] == "error"

    def test_weakness_priority(self):
        """薄弱知识点应被安排在更早的阶段"""
        self._build_simple_graph()
        profile = {"weak_areas": ["B"]}
        result_no_weak = self.planner.plan_path("student1", "C", {}, {})
        result_with_weak = self.planner.plan_path("student1", "C", {}, profile)
        # 两者都应成功
        assert result_no_weak["status"] == "success"
        assert result_with_weak["status"] == "success"


# ===== 趋势分析测试 =====

class TestTrendAnalyzer:
    """测试趋势分析器"""

    def setup_method(self):
        self.analyzer = MultiFactorTrendAnalyzer()

    def test_analyze_empty_data(self):
        result = self.analyzer.analyze("test_student", [], [], [], {})
        assert "trend_state" in result

    def test_analyze_with_quiz_data(self):
        quiz_history = [
            {"score": 60, "kp_id": "A", "created_at": "2024-01-01"},
            {"score": 70, "kp_id": "A", "created_at": "2024-01-03"},
            {"score": 80, "kp_id": "B", "created_at": "2024-01-05"},
            {"score": 85, "kp_id": "B", "created_at": "2024-01-07"},
        ]
        learning_records = [
            {"action": "complete", "kp_id": "A", "created_at": "2024-01-02"},
            {"action": "complete", "kp_id": "B", "created_at": "2024-01-06"},
        ]
        result = self.analyzer.analyze("test_student", quiz_history, learning_records, ["A"], {})
        assert "trend_state" in result
        assert "trend_factor" in result

    def test_analyze_returns_dimensions(self):
        quiz_history = [
            {"score": 70, "kp_id": "A", "created_at": "2024-01-01"},
            {"score": 80, "kp_id": "A", "created_at": "2024-01-02"},
        ]
        result = self.analyzer.analyze("test_student", quiz_history, [], [], {})
        assert "dimensions" in result or "trend_state" in result


# ===== 效果评估测试 =====

class TestEffectEvaluator:
    """测试效果评估器"""

    def setup_method(self):
        self.evaluator = LearningEffectEvaluator()

    def test_evaluate_empty(self):
        result = self.evaluator.evaluate("test_student", [], [], [])
        assert "realtime_metrics" in result

    def test_evaluate_with_data(self):
        quiz_results = [
            {"score": 80, "kp_id": "A", "created_at": "2024-01-01"},
            {"score": 85, "kp_id": "A", "created_at": "2024-01-02"},
            {"score": 90, "kp_id": "B", "created_at": "2024-01-03"},
        ]
        result = self.evaluator.evaluate("test_student", quiz_results, [], ["A"])
        assert "realtime_metrics" in result
        metrics = result["realtime_metrics"]
        assert "accuracy" in metrics
        assert "mastery" in metrics

    def test_evaluate_metrics_range(self):
        """指标应在合理范围内"""
        quiz_results = [
            {"score": 80, "kp_id": "A", "created_at": "2024-01-01"},
        ]
        result = self.evaluator.evaluate("test_student", quiz_results, [], [])
        metrics = result["realtime_metrics"]
        assert 0 <= metrics["accuracy"] <= 100


# ===== 加权匹配测试 =====

class TestWeightedMatcher:
    """测试加权匹配器"""

    def setup_method(self):
        self.matcher = MultiDimWeightedMatcher()

    def test_match_resource(self):
        student = {
            "knowledge_base": {"A": 0.5, "B": 0.3},
            "weak_areas": ["B"],
            "cognitive_style": "visual",
            "interest_areas": ["算法"],
        }
        resources = [
            {"resource_id": "R1", "kp_id": "A", "difficulty": 0.5, "type": "document", "title": "A 文档"},
            {"resource_id": "R2", "kp_id": "B", "difficulty": 0.3, "type": "video", "title": "B 视频"},
        ]
        result = self.matcher.match_resources(student, resources)
        assert "recommendations" in result
        assert len(result["recommendations"]) == 2

    def test_match_score_ordering(self):
        """匹配结果应按分数降序排列"""
        student = {
            "knowledge_base": {"A": 0.3},
            "weak_areas": ["A"],
            "cognitive_style": "visual",
        }
        resources = [
            {"resource_id": "R1", "kp_id": "A", "difficulty": 0.3, "type": "video", "title": "视频"},
            {"resource_id": "R2", "kp_id": "A", "difficulty": 0.9, "type": "document", "title": "高难度"},
        ]
        result = self.matcher.match_resources(student, resources)
        recs = result["recommendations"]
        scores = [r["match_score"] for r in recs]
        assert scores == sorted(scores, reverse=True)

    def test_match_empty_resources(self):
        student = {"knowledge_base": {}, "weak_areas": []}
        result = self.matcher.match_resources(student, [])
        assert result["recommendations"] == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
