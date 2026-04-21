"""
多维度加权匹配算法
场景1：学生 <-> 学习资源匹配（知识点、难度、风格、目标）
场景2：学生 <-> 学习路径匹配（基础水平、薄弱点、节奏、目标）
输出：匹配度得分、优先级排序、推荐列表
联动机制：趋势预警触发 -> 自动重新匹配
"""
from typing import Dict, Any, List, Tuple
import math


class MultiDimWeightedMatcher:
    """多维度加权匹配器"""

    # 资源匹配维度权重
    RESOURCE_WEIGHTS = {
        "knowledge_match": 0.30,
        "difficulty_fit": 0.25,
        "style_match": 0.20,
        "goal_match": 0.15,
        "tempo_match": 0.10,
    }

    # 路径匹配维度权重
    PATH_WEIGHTS = {
        "base_level_fit": 0.25,
        "weakness_coverage": 0.25,
        "tempo_fit": 0.20,
        "goal_alignment": 0.20,
        "prerequisite_ready": 0.10,
    }

    def match_resources(
        self,
        student_profile: Dict[str, Any],
        resources: List[Dict[str, Any]],
        top_k: int = 5,
    ) -> Dict[str, Any]:
        """
        学生-学习资源匹配
        """
        scored = []
        for res in resources:
            score, details = self._score_resource(student_profile, res)
            scored.append({
                "resource_id": res.get("resource_id", ""),
                "title": res.get("title", ""),
                "match_score": round(score, 4),
                "details": details,
                "resource": res,
            })

        scored.sort(key=lambda x: x["match_score"], reverse=True)
        return {
            "type": "resource_matching",
            "student_id": student_profile.get("student_id", ""),
            "recommendations": scored[:top_k],
            "total_candidates": len(resources),
        }

    def match_learning_paths(
        self,
        student_profile: Dict[str, Any],
        path_candidates: List[Dict[str, Any]],
        top_k: int = 3,
    ) -> Dict[str, Any]:
        """
        学生-学习路径匹配
        """
        scored = []
        for path in path_candidates:
            score, details = self._score_path(student_profile, path)
            scored.append({
                "path_id": path.get("path_id", ""),
                "title": path.get("title", ""),
                "match_score": round(score, 4),
                "details": details,
                "path": path,
            })

        scored.sort(key=lambda x: x["match_score"], reverse=True)
        return {
            "type": "path_matching",
            "student_id": student_profile.get("student_id", ""),
            "recommendations": scored[:top_k],
            "total_candidates": len(path_candidates),
        }

    def _score_resource(
        self,
        profile: Dict[str, Any],
        resource: Dict[str, Any],
    ) -> Tuple[float, Dict[str, float]]:
        """为单个资源计算匹配分"""
        # 1. 知识点匹配
        kp_match = self._knowledge_match(
            profile.get("knowledge_base", {}),
            resource.get("kp_tags", []),
            profile.get("weak_areas", []),
        )

        # 2. 难度适配
        diff_fit = self._difficulty_fit(
            profile.get("knowledge_level", "intermediate"),
            resource.get("difficulty", "medium"),
        )

        # 3. 认知风格匹配
        style_match = self._cognitive_style_match(
            profile.get("cognitive_style", {}),
            resource.get("content_types", []),
        )

        # 4. 学习目标匹配
        goal_match = self._goal_match(
            profile.get("learning_goals", []),
            resource.get("objectives", []),
        )

        # 5. 学习节奏匹配
        tempo_match = self._tempo_match(
            profile.get("learning_tempo", {}),
            resource.get("estimated_duration", 30),
        )

        total = (
            kp_match * self.RESOURCE_WEIGHTS["knowledge_match"]
            + diff_fit * self.RESOURCE_WEIGHTS["difficulty_fit"]
            + style_match * self.RESOURCE_WEIGHTS["style_match"]
            + goal_match * self.RESOURCE_WEIGHTS["goal_match"]
            + tempo_match * self.RESOURCE_WEIGHTS["tempo_match"]
        )

        return total, {
            "knowledge_match": round(kp_match, 4),
            "difficulty_fit": round(diff_fit, 4),
            "style_match": round(style_match, 4),
            "goal_match": round(goal_match, 4),
            "tempo_match": round(tempo_match, 4),
        }

    def _score_path(
        self,
        profile: Dict[str, Any],
        path: Dict[str, Any],
    ) -> Tuple[float, Dict[str, float]]:
        """为单条路径计算匹配分"""
        # 1. 基础水平适配
        base_fit = self._base_level_fit(
            profile.get("knowledge_level", "intermediate"),
            path.get("required_level", "intermediate"),
        )

        # 2. 薄弱点覆盖度
        weak_coverage = self._weakness_coverage(
            profile.get("weak_areas", []),
            path.get("covered_kps", []),
        )

        # 3. 节奏适配
        tempo_fit = self._tempo_fit(
            profile.get("learning_tempo", {}),
            path.get("estimated_hours", 10),
        )

        # 4. 目标对齐
        goal_align = self._goal_alignment(
            profile.get("learning_goals", []),
            path.get("objectives", []),
        )

        # 5. 前置准备度
        prereq_ready = self._prerequisite_ready(
            profile.get("knowledge_base", {}),
            path.get("prerequisites", []),
        )

        total = (
            base_fit * self.PATH_WEIGHTS["base_level_fit"]
            + weak_coverage * self.PATH_WEIGHTS["weakness_coverage"]
            + tempo_fit * self.PATH_WEIGHTS["tempo_fit"]
            + goal_align * self.PATH_WEIGHTS["goal_alignment"]
            + prereq_ready * self.PATH_WEIGHTS["prerequisite_ready"]
        )

        return total, {
            "base_level_fit": round(base_fit, 4),
            "weakness_coverage": round(weak_coverage, 4),
            "tempo_fit": round(tempo_fit, 4),
            "goal_alignment": round(goal_align, 4),
            "prerequisite_ready": round(prereq_ready, 4),
        }

    # ---------- 子评分函数 ----------

    def _knowledge_match(self, knowledge_base: Dict, kp_tags: List[str], weak_areas: List[str]) -> float:
        if not kp_tags:
            return 0.5
        mastered = set(knowledge_base.keys())
        weak_set = set(weak_areas)
        tags_set = set(kp_tags)
        # 匹配到薄弱点加分，匹配到已掌握点减分（重复学习）
        weak_match = len(tags_set & weak_set) / len(tags_set) if tags_set else 0.0
        master_match = len(tags_set & mastered) / len(tags_set) if tags_set else 0.0
        return 0.3 + weak_match * 0.7 - master_match * 0.2

    def _difficulty_fit(self, student_level: str, resource_difficulty: str) -> float:
        levels = {"beginner": 1, "intermediate": 2, "advanced": 3}
        s = levels.get(student_level, 2)
        r = levels.get(resource_difficulty, 2)
        diff = abs(s - r)
        if diff == 0:
            return 1.0
        elif diff == 1:
            return 0.6
        return 0.2

    def _cognitive_style_match(self, cognitive_style: Dict, content_types: List[str]) -> float:
        primary = cognitive_style.get("primary", "visual") if isinstance(cognitive_style, dict) else "visual"
        type_map = {
            "visual": ["video", "diagram", "mindmap", "image"],
            "auditory": ["audio", "podcast", "lecture"],
            "reading": ["document", "article", "textbook"],
            "kinesthetic": ["interactive", "code", "quiz", "lab"],
        }
        preferred = set(type_map.get(primary, []))
        if not content_types:
            return 0.5
        matched = len(preferred & set(content_types)) / len(content_types)
        return 0.3 + matched * 0.7

    def _goal_match(self, learning_goals: List[Dict], resource_objectives: List[str]) -> float:
        if not learning_goals or not resource_objectives:
            return 0.5
        goal_texts = [g.get("title", "") for g in learning_goals if isinstance(g, dict)]
        goal_texts += [str(g) for g in learning_goals if not isinstance(g, dict)]
        matched = 0
        for obj in resource_objectives:
            for gt in goal_texts:
                if obj in gt or gt in obj:
                    matched += 1
                    break
        return 0.2 + (matched / len(resource_objectives)) * 0.8

    def _tempo_match(self, learning_tempo: Dict, estimated_duration: int) -> float:
        optimal = learning_tempo.get("optimal_session_duration", 45) if isinstance(learning_tempo, dict) else 45
        if optimal <= 0:
            optimal = 45
        ratio = estimated_duration / optimal
        if 0.5 <= ratio <= 1.5:
            return 1.0 - abs(ratio - 1.0)
        return 0.3

    def _base_level_fit(self, student_level: str, required_level: str) -> float:
        return self._difficulty_fit(student_level, required_level)

    def _weakness_coverage(self, weak_areas: List[str], covered_kps: List[str]) -> float:
        if not weak_areas:
            return 0.8  # 没有薄弱点，路径匹配度默认较高
        if not covered_kps:
            return 0.2
        covered = len(set(weak_areas) & set(covered_kps))
        return 0.2 + (covered / len(weak_areas)) * 0.8

    def _goal_alignment(self, learning_goals: List[Dict], path_objectives: List[str]) -> float:
        return self._goal_match(learning_goals, path_objectives)

    def _prerequisite_ready(self, knowledge_base: Dict, prerequisites: List[str]) -> float:
        if not prerequisites:
            return 1.0
        mastered = set(knowledge_base.keys())
        ready = len(set(prerequisites) & mastered)
        return ready / len(prerequisites)

    def _tempo_fit(self, learning_tempo: Dict, estimated_hours: int) -> float:
        weekly_capacity = learning_tempo.get("weekly_study_capacity", 10) if isinstance(learning_tempo, dict) else 10
        if weekly_capacity <= 0:
            weekly_capacity = 10
        ratio = estimated_hours / weekly_capacity
        if ratio <= 1.0:
            return 1.0
        elif ratio <= 1.5:
            return 0.7
        elif ratio <= 2.0:
            return 0.4
        return 0.2
