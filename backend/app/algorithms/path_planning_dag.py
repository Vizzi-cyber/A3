"""
学习路径规划算法（基于知识点DAG）
- 按掌握度自动：跳级、回炉复习、插入强化训练
- 动态调整：随趋势与匹配结果实时更新
"""
from typing import Dict, Any, List, Set, Tuple
from collections import deque, defaultdict
import math


class DAGPathPlanner:
    """基于DAG的学习路径规划器"""

    def __init__(self):
        self.kp_graph: Dict[str, List[str]] = {}  # kp_id -> list of prerequisite kp_ids
        self.kp_meta: Dict[str, Dict[str, Any]] = {}

    def build_graph(self, knowledge_points: List[Dict[str, Any]]):
        """从知识点列表构建DAG"""
        self.kp_graph = {}
        self.kp_meta = {}
        for kp in knowledge_points:
            kp_id = kp.get("kp_id", "")
            if not kp_id:
                continue
            self.kp_graph[kp_id] = kp.get("prerequisites", [])
            self.kp_meta[kp_id] = kp

    def plan_path(
        self,
        student_id: str,
        target_kp_id: str,
        mastery_map: Dict[str, float],  # kp_id -> 0.0~1.0
        profile: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        规划从当前状态到目标知识点的学习路径
        """
        if target_kp_id not in self.kp_graph:
            return {"status": "error", "message": f"目标知识点 {target_kp_id} 不存在"}

        # 1. 拓扑排序获取完整依赖链
        dependency_chain = self._get_dependency_chain(target_kp_id)

        # 2. 根据掌握度分类节点
        mastered = []
        review = []
        learn = []
        for kp_id in dependency_chain:
            m = mastery_map.get(kp_id, 0.0)
            if m >= 0.85:
                mastered.append(kp_id)
            elif m >= 0.5:
                review.append(kp_id)
            else:
                learn.append(kp_id)

        # 3. 生成学习阶段
        stages = []
        stage_no = 1

        # 阶段1：回炉复习（掌握度50%~85%）
        if review:
            stages.append({
                "stage_no": stage_no,
                "title": "回炉复习",
                "type": "review",
                "topics": [self.kp_meta.get(k, {}).get("name", k) for k in review],
                "kp_ids": review,
                "hours": max(1, len(review) * 2),
                "criteria": "掌握度提升至85%以上",
            })
            stage_no += 1

        # 阶段2：新知学习（掌握度<50%）
        if learn:
            # 按依赖关系排序
            sorted_learn = self._topological_sort_subgraph(learn)
            # 每3个知识点为一个子阶段
            batch_size = 3
            for i in range(0, len(sorted_learn), batch_size):
                batch = sorted_learn[i:i+batch_size]
                stages.append({
                    "stage_no": stage_no,
                    "title": f"新知学习 {i//batch_size + 1}",
                    "type": "learn",
                    "topics": [self.kp_meta.get(k, {}).get("name", k) for k in batch],
                    "kp_ids": batch,
                    "hours": max(1, len(batch) * 3),
                    "criteria": "掌握度达到50%以上",
                })
                stage_no += 1

        # 阶段3：强化训练（薄弱点）
        weak_areas = profile.get("weak_areas", [])
        weak_in_path = [k for k in weak_areas if k in dependency_chain]
        if weak_in_path:
            stages.append({
                "stage_no": stage_no,
                "title": "薄弱点强化",
                "type": "strengthen",
                "topics": [self.kp_meta.get(k, {}).get("name", k) for k in weak_in_path],
                "kp_ids": weak_in_path,
                "hours": max(1, len(weak_in_path) * 2),
                "criteria": "薄弱点消除",
            })
            stage_no += 1

        # 阶段4：目标达成
        stages.append({
            "stage_no": stage_no,
            "title": "目标达成",
            "type": "target",
            "topics": [self.kp_meta.get(target_kp_id, {}).get("name", target_kp_id)],
            "kp_ids": [target_kp_id],
            "hours": 2,
            "criteria": "掌握度达到85%以上",
        })

        total_hours = sum(s["hours"] for s in stages)

        return {
            "status": "success",
            "student_id": student_id,
            "target_kp_id": target_kp_id,
            "estimated_total_hours": total_hours,
            "mastered_count": len(mastered),
            "review_count": len(review),
            "learn_count": len(learn),
            "stages": stages,
            "dependency_chain": dependency_chain,
        }

    def adjust_path(
        self,
        current_path: Dict[str, Any],
        quiz_result: Dict[str, Any],
        trend_state: str,
    ) -> Dict[str, Any]:
        """
        根据测验结果和趋势动态调整路径
        """
        adjusted = {
            "status": "success",
            "adjustment_reasons": [],
            "stages": current_path.get("stages", []),
        }

        score = quiz_result.get("score", 0.0)
        weak_tags = quiz_result.get("weak_tags", [])

        # 触发调整条件
        if score < 50:
            adjusted["adjustment_reasons"].append("测验得分过低，插入基础复习阶段")
            # 在开头插入复习阶段
            adjusted["stages"].insert(0, {
                "stage_no": 0,
                "title": "紧急回炉",
                "type": "review",
                "topics": weak_tags[:3] if weak_tags else ["基础概念"],
                "kp_ids": weak_tags[:3] if weak_tags else [],
                "hours": 3,
                "criteria": "基础概念理解达标",
            })
        elif score >= 90 and trend_state == "growth":
            adjusted["adjustment_reasons"].append("表现优异且趋势上升，允许跳级")
            # 移除第一个学习阶段（跳级）
            if adjusted["stages"] and adjusted["stages"][0].get("type") == "learn":
                skipped = adjusted["stages"].pop(0)
                adjusted["adjustment_reasons"].append(f"跳级跳过: {skipped.get('title', '')}")

        if trend_state == "warning":
            adjusted["adjustment_reasons"].append("学习预警状态，减少新内容，增加复习")
            # 将学习阶段时长减半，增加复习
            for s in adjusted["stages"]:
                if s.get("type") == "learn":
                    s["hours"] = max(1, s["hours"] // 2)

        # 重新编号
        for i, s in enumerate(adjusted["stages"]):
            s["stage_no"] = i + 1

        adjusted["estimated_total_hours"] = sum(s["hours"] for s in adjusted["stages"])
        return adjusted

    def _get_dependency_chain(self, target_kp_id: str) -> List[str]:
        """获取目标知识点的所有前置依赖（含自身）"""
        visited = set()
        chain = []

        def dfs(kp_id):
            if kp_id in visited or kp_id not in self.kp_graph:
                return
            visited.add(kp_id)
            for prereq in self.kp_graph.get(kp_id, []):
                dfs(prereq)
            chain.append(kp_id)

        dfs(target_kp_id)
        return chain

    def _topological_sort_subgraph(self, kp_ids: List[str]) -> List[str]:
        """对子图进行拓扑排序"""
        subgraph = {k: [p for p in self.kp_graph.get(k, []) if p in kp_ids] for k in kp_ids}
        in_degree = {k: 0 for k in kp_ids}
        for k, prereqs in subgraph.items():
            for p in prereqs:
                if p in in_degree:
                    in_degree[k] += 1

        queue = deque([k for k, d in in_degree.items() if d == 0])
        result = []
        while queue:
            node = queue.popleft()
            result.append(node)
            for k, prereqs in subgraph.items():
                if node in prereqs:
                    in_degree[k] -= 1
                    if in_degree[k] == 0:
                        queue.append(k)

        # 如果有环，剩下的直接追加
        for k in kp_ids:
            if k not in result:
                result.append(k)
        return result

    def detect_cycles(self) -> List[List[str]]:
        """检测DAG中的环（用于数据校验）"""
        cycles = []
        visited = set()
        rec_stack = set()

        def dfs(node, path):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            for prereq in self.kp_graph.get(node, []):
                if prereq not in visited:
                    dfs(prereq, path)
                elif prereq in rec_stack:
                    cycle_start = path.index(prereq)
                    cycles.append(path[cycle_start:] + [prereq])
            path.pop()
            rec_stack.remove(node)

        for node in self.kp_graph:
            if node not in visited:
                dfs(node, [])
        return cycles
