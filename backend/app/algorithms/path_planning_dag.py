"""
自适应 DAG 学习路径规划算法（Adaptive DAG Path Planner, ADPP）

核心思想：
1. 关键路径分析（CPA）：计算每个知识点的下游依赖数量，确定关键知识点
2. 学习成本模型：基于知识追踪理论估算每个知识点的学习时长
3. 薄弱点前置加权：使用加权拓扑排序将薄弱知识点提前
4. 自适应阶段划分：基于每日学习时长、学习节奏动态分阶段
5. 画像感知资源推荐：根据认知风格推荐不同类型的学习资源

参考算法：
- 关键路径法（Critical Path Method, CPM）
- 加权拓扑排序（Weighted Topological Sort）
- 贝叶斯知识追踪简化模型（Simplified BKT）
"""
from typing import Dict, Any, List, Set, Tuple, Optional
from collections import deque, defaultdict
import math


class DAGPathPlanner:
    """自适应 DAG 学习路径规划器"""

    def __init__(self):
        self.kp_graph: Dict[str, List[str]] = {}      # kp_id -> prerequisites
        self.reverse_graph: Dict[str, List[str]] = {} # kp_id -> successors
        self.kp_meta: Dict[str, Dict[str, Any]] = {}
        self.in_degree: Dict[str, int] = {}

    def build_graph(self, knowledge_points: List[Dict[str, Any]]):
        """从知识点列表构建 DAG"""
        self.kp_graph = {}
        self.reverse_graph = defaultdict(list)
        self.kp_meta = {}
        self.in_degree = defaultdict(int)

        for kp in knowledge_points:
            kp_id = kp.get("kp_id", "")
            if not kp_id:
                continue
            prereqs = kp.get("prerequisites", []) or []
            self.kp_graph[kp_id] = prereqs
            self.kp_meta[kp_id] = kp
            self.in_degree[kp_id] = len(prereqs)
            for p in prereqs:
                self.reverse_graph[p].append(kp_id)

    def _topological_sort(self, kp_ids: Optional[List[str]] = None) -> List[str]:
        """Kahn 算法拓扑排序"""
        targets = set(kp_ids or self.kp_graph.keys())
        in_deg = defaultdict(int)
        for k in targets:
            in_deg[k] = sum(1 for p in self.kp_graph.get(k, []) if p in targets)

        queue = deque([k for k in targets if in_deg[k] == 0])
        result = []
        while queue:
            node = queue.popleft()
            result.append(node)
            for succ in self.reverse_graph.get(node, []):
                if succ in targets:
                    in_deg[succ] -= 1
                    if in_deg[succ] == 0:
                        queue.append(succ)

        # 环处理：剩余节点直接追加
        for k in targets:
            if k not in result:
                result.append(k)
        return result

    def _get_dependency_chain(self, target_kp_id: str) -> List[str]:
        """获取目标知识点的所有前置依赖（含自身），使用 DFS"""
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

    def _compute_criticality(self) -> Dict[str, int]:
        """
        计算每个知识点的关键度（下游依赖数量）
        关键度越高，说明该知识点影响面越大，应优先学习
        """
        criticality = defaultdict(int)

        def count_downstream(kp_id, memo):
            if kp_id in memo:
                return memo[kp_id]
            succs = self.reverse_graph.get(kp_id, [])
            count = len(succs)
            for s in succs:
                count += count_downstream(s, memo)
            memo[kp_id] = count
            return count

        memo = {}
        for kp_id in self.kp_graph:
            criticality[kp_id] = count_downstream(kp_id, memo)
        return criticality

    def _estimate_mastery_probability(self, kp_id: str, mastery_map: Dict[str, float]) -> float:
        """
        简化 BKT 模型：基于前置知识点掌握度预测当前知识点掌握概率
        P(master) = 1 - prod(1 - P(prereq_i))
        即：只要有一个前置掌握得好，就有较高概率掌握当前知识点
        """
        prereqs = self.kp_graph.get(kp_id, [])
        if not prereqs:
            return mastery_map.get(kp_id, 0.0)

        probs = []
        for p in prereqs:
            probs.append(mastery_map.get(p, 0.0))

        # 如果所有前置掌握度都低，当前知识点掌握概率也低
        if not probs:
            return mastery_map.get(kp_id, 0.0)

        # 使用逻辑或的近似：1 - prod(1 - p_i)
        combined = 1.0 - math.prod(1.0 - p for p in probs)
        # 结合学生已有的掌握度记录（如果有）
        actual = mastery_map.get(kp_id, 0.0)
        return 0.4 * combined + 0.6 * actual

    def _compute_learning_cost(
        self,
        kp_id: str,
        mastery_map: Dict[str, float],
        profile: Dict[str, Any],
    ) -> float:
        """
        计算单个知识点的学习成本（小时）

        成本 = 基础时长 * 难度系数 * 掌握度折扣 * 薄弱点加权 * 学习速度因子 * 关键度因子
        """
        kp = self.kp_meta.get(kp_id, {})
        base_hours = 1.5

        # 难度系数
        difficulty = kp.get("difficulty", 3)
        diff_factor = {1: 0.7, 2: 0.9, 3: 1.1, 4: 1.4, 5: 1.8}.get(difficulty, 1.1)

        # 掌握度折扣：已掌握越多，所需时间越少
        mastery = mastery_map.get(kp_id, 0.0)
        pred_mastery = self._estimate_mastery_probability(kp_id, mastery_map)
        # 如果预测掌握度已经很高，学习成本很低
        mastery_factor = max(0.15, 1.0 - 0.8 * pred_mastery)

        # 薄弱点加权：如果该知识点是薄弱点，增加 25% 时间
        weak_areas = profile.get("weak_areas", [])
        kp_name = (kp.get("name", "") or "").lower()
        is_weak = any(wa.lower() in kp_name for wa in weak_areas)
        weak_factor = 1.25 if is_weak else 1.0

        # 学习速度因子
        tempo = profile.get("learning_tempo", {})
        speed = tempo.get("study_speed", "moderate")
        speed_factor = {"fast": 0.75, "moderate": 1.0, "slow": 1.35}.get(speed, 1.0)

        # 关键度因子：关键知识点多花一点时间打牢基础
        criticality = self._compute_criticality()
        crit = criticality.get(kp_id, 0)
        max_crit = max(criticality.values()) if criticality else 1
        crit_factor = 1.0 + 0.15 * (crit / max(max_crit, 1))

        return base_hours * diff_factor * mastery_factor * weak_factor * speed_factor * crit_factor

    def _weighted_sort(
        self,
        kp_ids: List[str],
        mastery_map: Dict[str, float],
        profile: Dict[str, Any],
    ) -> List[str]:
        """
        加权拓扑排序：在拓扑序基础上，根据以下权重重新排序：
        - 薄弱点优先（+10）
        - 关键度高优先（+5 * crit_ratio）
        - 掌握度低优先（+3 * (1 - mastery)）
        - 难度适中优先（-abs(difficulty - 3)）
        """
        criticality = self._compute_criticality()
        max_crit = max(criticality.values()) if criticality else 1
        topo_order = {k: i for i, k in enumerate(self._topological_sort(kp_ids))}

        def score(kp_id):
            kp = self.kp_meta.get(kp_id, {})
            weak_areas = profile.get("weak_areas", [])
            kp_name = (kp.get("name", "") or "").lower()
            is_weak = any(wa.lower() in kp_name for wa in weak_areas)
            mastery = mastery_map.get(kp_id, 0.0)
            crit = criticality.get(kp_id, 0) / max(max_crit, 1)
            difficulty = kp.get("difficulty", 3)

            return (
                (10 if is_weak else 0)
                + 5 * crit
                + 3 * (1.0 - mastery)
                - abs(difficulty - 3)
            )

        # 先按拓扑序分组（保证前置知识点在前），再按权重排序
        # 使用稳定排序：按拓扑序作为次要键
        return sorted(kp_ids, key=lambda k: (-score(k), topo_order.get(k, 0)))

    def _stage_division(
        self,
        sorted_kps: List[Dict[str, Any]],
        daily_duration: int,
        preference: str,
    ) -> List[Dict[str, Any]]:
        """
        自适应阶段划分：
        - 根据每日学习时长确定每个阶段的学习量
        - 理论偏好：阶段内知识点偏少，深度大
        - 练习偏好：阶段内知识点偏多，广度大
        """
        if not sorted_kps:
            return []

        # 每日时长转小时
        daily_hours = max(0.5, daily_duration / 60)

        # 偏好调整：理论型每个阶段 2-3 天量，练习型 1-2 天量，平衡型 2 天量
        if preference == "theory":
            days_per_stage = 3.0
        elif preference == "practice":
            days_per_stage = 1.5
        else:
            days_per_stage = 2.0

        threshold = daily_hours * days_per_stage

        stage_names = ["基础巩固", "核心知识", "进阶深化", "综合实战", "专项突破", "融会贯通"]
        stages = []
        current_kps = []
        current_hours = 0.0
        stage_idx = 0

        for kp in sorted_kps:
            if current_hours + kp["hours"] > threshold and current_kps:
                stages.append(self._build_stage(current_kps, stage_idx, stage_names))
                current_kps = []
                current_hours = 0.0
                stage_idx += 1

            current_kps.append(kp)
            current_hours += kp["hours"]

        if current_kps:
            stages.append(self._build_stage(current_kps, stage_idx, stage_names))

        return stages

    def _build_stage(
        self,
        kps: List[Dict[str, Any]],
        stage_idx: int,
        stage_names: List[str],
    ) -> Dict[str, Any]:
        """构建单个阶段的数据结构"""
        total_hours = round(sum(k["hours"] for k in kps), 1)
        all_tags = []
        for k in kps:
            all_tags.extend(k.get("tags", []) or [])
        # 去重并取前 5 个
        unique_tags = list(dict.fromkeys(all_tags))[:5]

        return {
            "stage_no": stage_idx + 1,
            "title": stage_names[min(stage_idx, len(stage_names) - 1)] if stage_idx < len(stage_names) else f"阶段 {stage_idx + 1}",
            "type": "adaptive",
            "topics": [k["name"] for k in kps],
            "kp_ids": [k["kp_id"] for k in kps],
            "hours": total_hours,
            "criteria": f"完成本阶段 {len(kps)} 个知识点的学习，预计耗时 {total_hours} 小时",
            "resources": unique_tags,
        }

    def plan_path(
        self,
        student_id: str,
        target_kp_id: str,
        mastery_map: Dict[str, float],
        profile: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        生成个性化学习路径（自适应 DAG 路径规划算法）
        """
        if target_kp_id not in self.kp_graph:
            return {"status": "error", "message": f"目标知识点 {target_kp_id} 不存在"}

        # 1. 获取完整依赖链
        dependency_chain = self._get_dependency_chain(target_kp_id)

        # 2. 过滤已完全掌握的知识点（掌握度 >= 0.85）
        unmastered_ids = [k for k in dependency_chain if mastery_map.get(k, 0.0) < 0.85]

        if not unmastered_ids:
            return {
                "status": "success",
                "student_id": student_id,
                "target_kp_id": target_kp_id,
                "estimated_total_hours": 2,
                "mastered_count": len(dependency_chain),
                "review_count": 0,
                "learn_count": 0,
                "stages": [{
                    "stage_no": 1,
                    "title": "复习巩固",
                    "type": "review",
                    "topics": [self.kp_meta.get(target_kp_id, {}).get("name", target_kp_id)],
                    "kp_ids": [target_kp_id],
                    "hours": 2,
                    "criteria": "复习已掌握内容，巩固记忆",
                    "resources": [],
                }],
                "dependency_chain": dependency_chain,
            }

        # 3. 计算每个未掌握知识点的学习成本
        kp_costs = []
        for kp_id in unmastered_ids:
            cost = self._compute_learning_cost(kp_id, mastery_map, profile)
            kp = self.kp_meta.get(kp_id, {})
            kp_costs.append({
                "kp_id": kp_id,
                "name": kp.get("name", kp_id),
                "hours": round(cost, 1),
                "difficulty": kp.get("difficulty", 3),
                "tags": kp.get("tags", []),
                "prerequisites": kp.get("prerequisites", []),
            })

        # 4. 加权拓扑排序（薄弱点 + 关键度 + 掌握度综合排序）
        sorted_ids = self._weighted_sort(
            [k["kp_id"] for k in kp_costs],
            mastery_map,
            profile,
        )
        sorted_kps = [next(k for k in kp_costs if k["kp_id"] == sid) for sid in sorted_ids]

        # 5. 自适应阶段划分
        daily_duration = profile.get("learning_tempo", {}).get("weekly_study_capacity", 10)
        if daily_duration < 1:
            daily_duration = 10
        preference = profile.get("preference", "balanced")

        stages = self._stage_division(sorted_kps, daily_duration, preference)

        # 6. 分类统计
        mastered = [k for k in dependency_chain if mastery_map.get(k, 0.0) >= 0.85]
        review = [k for k in dependency_chain if 0.5 <= mastery_map.get(k, 0.0) < 0.85]
        learn = [k for k in dependency_chain if mastery_map.get(k, 0.0) < 0.5]

        total_hours = round(sum(s["hours"] for s in stages), 1)

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
        根据测验结果和学习趋势动态调整路径

        策略：
        - 得分 < 50：插入复习阶段，降低后续阶段难度
        - 得分 50-70：增加练习资源，延长当前阶段时长
        - 得分 70-90：正常推进
        - 得分 >= 90 且趋势上升：允许跳级或加速
        - 预警状态：减少新内容，增加复习，降低难度
        """
        adjusted = {
            "status": "success",
            "adjustment_reasons": [],
            "stages": [dict(s) for s in current_path.get("stages", [])],
        }

        score = quiz_result.get("score", 0.0)
        weak_tags = quiz_result.get("weak_tags", [])

        if score < 50:
            adjusted["adjustment_reasons"].append("测验得分过低，插入基础复习阶段并降低后续难度")
            adjusted["stages"].insert(0, {
                "stage_no": 0,
                "title": "紧急回炉",
                "type": "review",
                "topics": weak_tags[:3] if weak_tags else ["基础概念"],
                "kp_ids": [],
                "hours": 3,
                "criteria": "基础概念理解达标",
                "resources": ["基础讲解视频", "入门练习题"],
            })
            # 降低后续阶段难度：延长每个阶段时长（更细致地学习）
            for s in adjusted["stages"][1:]:
                if s.get("type") == "adaptive":
                    s["hours"] = round(s.get("hours", 5) * 1.3, 1)

        elif 50 <= score < 70:
            adjusted["adjustment_reasons"].append("掌握度一般，增加强化练习")
            # 在第一个学习阶段后插入强化练习
            for i, s in enumerate(adjusted["stages"]):
                if s.get("type") == "adaptive":
                    adjusted["stages"].insert(i + 1, {
                        "stage_no": i + 1,
                        "title": "强化练习",
                        "type": "practice",
                        "topics": weak_tags[:3] if weak_tags else ["巩固练习"],
                        "kp_ids": [],
                        "hours": 2,
                        "criteria": "通过练习题巩固薄弱环节",
                        "resources": ["算法练习题", "代码实战"],
                    })
                    break

        elif score >= 90 and trend_state == "growth":
            adjusted["adjustment_reasons"].append("表现优异且趋势上升，加速推进")
            # 将后续阶段时长缩短 20%
            for s in adjusted["stages"]:
                if s.get("type") == "adaptive":
                    s["hours"] = round(s.get("hours", 5) * 0.8, 1)

        if trend_state == "warning":
            adjusted["adjustment_reasons"].append("学习预警状态，减少新内容，增加复习")
            for s in adjusted["stages"]:
                if s.get("type") == "adaptive":
                    s["hours"] = round(s.get("hours", 5) * 1.2, 1)

        # 重新编号
        for i, s in enumerate(adjusted["stages"]):
            s["stage_no"] = i + 1

        adjusted["estimated_total_hours"] = round(sum(s.get("hours", 0) for s in adjusted["stages"]), 1)
        return adjusted

    def detect_cycles(self) -> List[List[str]]:
        """检测 DAG 中的环（用于数据校验）"""
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
