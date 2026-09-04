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

AIC 算法增强（可选注入，未注入时保持原逻辑）：
- set_bkt_engine：完整 BKT（pyBKT）替代简化掌握度合并
- set_irt_diagnoser：IRT 标定难度 b 替代人工 1-5 分级（Rasch, 1960 / 2PL）
- set_strategy_bandit：Thompson Sampling 在分数段候选策略中选择调整动作
  （回炉复习 / 强化练习 / 加速推进），替代纯 50/70/90 规则分档
"""
from typing import Dict, Any, List, Set, Tuple, Optional
from collections import deque, defaultdict
import math

# 难度 1-5 级 → 时间系数（人工先验表；IRT b 标定后按级插值查此表）
DIFFICULTY_FACTOR_TABLE = {1: 0.7, 2: 0.9, 3: 1.1, 4: 1.4, 5: 1.8}
# adjust_path 策略臂（Thompson Sampling）：回炉复习 / 强化练习 / 加速推进 / 维持现状
# maintain 必须是臂而非仅默认值：≥90 且趋势上升档的候选集为 accelerate+maintain，
# 若 maintain 不在臂中，MAB 期望排序会在该档退化为必选 accelerate
STRATEGY_ARMS = ["review_boost", "practice_boost", "accelerate", "maintain"]


class DAGPathPlanner:
    """自适应 DAG 学习路径规划器"""

    def __init__(self):
        self.kp_graph: Dict[str, List[str]] = {}      # kp_id -> prerequisites
        self.reverse_graph: Dict[str, List[str]] = {} # kp_id -> successors
        self.kp_meta: Dict[str, Dict[str, Any]] = {}
        self.in_degree: Dict[str, int] = {}
        self._criticality_cache: Optional[Dict[str, int]] = None
        self._bkt_engine = None                        # 可选：完整 BKT 引擎（pyBKT）
        self._irt_diagnoser = None                     # 可选：IRT 诊断器（难度 b 标定）
        self._gkt_engine = None                        # 可选：GKT 引擎（图卷积掌握度传播）
        self._strategy_bandit = None                   # 可选：路径调整策略 MAB

    def set_bkt_engine(self, engine) -> None:
        """注入完整贝叶斯知识追踪引擎（pyBKT），掌握度预测由"简化 BKT 概率合并"
        升级为带 EM 参数估计的完整 BKT（Corbett & Anderson, 1995）。"""
        self._bkt_engine = engine

    def set_gkt_engine(self, engine) -> None:
        """注入 GKT 引擎（可学习门控图卷积）：对 BKT 覆盖后的掌握度做
        图感知传播（前置依赖邻居影响），需 engine.build_graph 与本图同构图。"""
        self._gkt_engine = engine

    def set_irt_diagnoser(self, diagnoser) -> None:
        """注入 IRT 诊断器：学习成本模型的难度系数优先使用标定 b 值
        （1PL/2PL MAP 估计），替代人工 1-5 分级；无标定记录的知识点回退人工分级。"""
        self._irt_diagnoser = diagnoser

    def set_strategy_bandit(self, selector) -> None:
        """注入路径调整策略 Thompson Sampling 选择器（臂见 STRATEGY_ARMS）。
        冷启动（收益反馈不足，见 selector.is_warm）时回退规则先验。"""
        self._strategy_bandit = selector

    def record_strategy_reward(self, arm: str, reward: float) -> bool:
        """反馈某次调整策略的实际收益（0-1，如下次测验提分比例），驱动 MAB 学习。"""
        if self._strategy_bandit is None:
            return False
        try:
            self._strategy_bandit.update(arm, reward)
            return True
        except Exception:
            return False

    def build_graph(self, knowledge_points: List[Dict[str, Any]]):
        """从知识点列表构建 DAG"""
        self.kp_graph = {}
        self.reverse_graph = defaultdict(list)
        self.kp_meta = {}
        self.in_degree = defaultdict(int)
        self._criticality_cache = None

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

    def _difficulty_factor(self, kp_id: str, kp: Dict[str, Any]) -> Tuple[float, str]:
        """难度系数与来源。

        优先使用 IRT 标定的题目难度 b（连续 logit 尺度，MAP 估计）：
          level = clip(3 + 0.8·b, 1, 5)，即 b=0 → 3 级（中等）、b=±2.5 → 5/1 级，
          再对人工先验系数表线性插值，保证与原量纲可比且单调。
        IRT 未拟合 / 该知识点无标定记录时回退人工 1-5 分级。
        """
        irt = self._irt_diagnoser
        if irt is not None and getattr(irt, "is_fitted", False):
            try:
                b = irt.get_item_difficulty(kp_id)
            except Exception:
                b = None
            if b is not None:
                level = min(5.0, max(1.0, 3.0 + 0.8 * float(b)))
                lower, upper = int(math.floor(level)), int(math.ceil(level))
                if lower == upper:
                    factor = DIFFICULTY_FACTOR_TABLE[lower]
                else:
                    frac = level - lower
                    factor = (DIFFICULTY_FACTOR_TABLE[lower] * (1.0 - frac)
                              + DIFFICULTY_FACTOR_TABLE[upper] * frac)
                return factor, "irt_b"
        difficulty = kp.get("difficulty", 3)
        return DIFFICULTY_FACTOR_TABLE.get(difficulty, 1.1), "manual"

    def _compute_learning_cost(
        self,
        kp_id: str,
        mastery_map: Dict[str, float],
        profile: Dict[str, Any],
    ) -> float:
        """
        计算单个知识点的学习成本（小时）

        成本 = 基础时长 * 难度系数 * 掌握度折扣 * 薄弱点加权 * 学习速度因子 * 关键度因子
        难度系数：IRT 标定 b 值优先（_difficulty_factor），回退人工分级
        """
        kp = self.kp_meta.get(kp_id, {})
        base_hours = 1.5

        # 难度系数（IRT b 标定 → 人工分级）
        diff_factor, _diff_source = self._difficulty_factor(kp_id, kp)

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

        # 关键度因子：关键知识点多花一点时间打牢基础（缓存结果）
        if self._criticality_cache is None:
            self._criticality_cache = self._compute_criticality()
        criticality = self._criticality_cache
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

        # 严格保证拓扑序：前置知识点一定排在后续知识点之前
        # 在每个拓扑层级内部按权重排序
        topo_sorted = self._topological_sort(kp_ids)
        kp_set = set(kp_ids)

        # 计算每个节点的拓扑层级（最长前置链长度）
        level_cache: Dict[str, int] = {}
        def topo_level(kp_id: str) -> int:
            if kp_id in level_cache:
                return level_cache[kp_id]
            prereqs = [p for p in self.kp_graph.get(kp_id, []) if p in kp_set]
            if not prereqs:
                level_cache[kp_id] = 0
                return 0
            lv = max(topo_level(p) for p in prereqs) + 1
            level_cache[kp_id] = lv
            return lv

        for k in kp_ids:
            topo_level(k)

        # 先按拓扑层级排序，层级内按权重降序排序（稳定排序）
        return sorted(kp_ids, key=lambda k: (level_cache.get(k, 0), -score(k)))

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
            "courses": list(dict.fromkeys(k.get("course", "") for k in kps if k.get("course"))),
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

        # 0. BKT 增强：注入完整 BKT 引擎时，用参数化估计的掌握度
        #    覆盖画像快照掌握度（预测概率 > 0 才覆盖，保持向后兼容）
        if getattr(self, "_bkt_engine", None) is not None:
            try:
                bkt_map = self._bkt_engine.estimate_mastery_map(
                    student_id,
                    list(mastery_map.keys()) + [target_kp_id],
                )
                for kp, prob in bkt_map.items():
                    if prob > 0:
                        mastery_map[kp] = prob
            except Exception:
                pass  # BKT 不可用时回退画像掌握度

        # 0.5 GKT 增强：图卷积掌握度传播（可学习门控；前置依赖邻居影响当前点）
        if getattr(self, "_gkt_engine", None) is not None:
            try:
                gkt_map = self._gkt_engine.propagate(mastery_map)
                for kp, prob in gkt_map.items():
                    if kp in mastery_map:
                        mastery_map[kp] = prob
            except Exception:
                pass  # GKT 不可用时保持原掌握度

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
            _, diff_source = self._difficulty_factor(kp_id, kp)
            kp_costs.append({
                "kp_id": kp_id,
                "name": kp.get("name", kp_id),
                "course": kp.get("course", ""),
                "hours": round(cost, 1),
                "difficulty": kp.get("difficulty", 3),
                "difficulty_source": diff_source,
                "tags": kp.get("tags", []),
                "prerequisites": kp.get("prerequisites", []),
            })

        # 4. 加权拓扑排序（薄弱点 + 关键度 + 掌握度综合排序）
        sorted_ids = self._weighted_sort(
            [k["kp_id"] for k in kp_costs],
            mastery_map,
            profile,
        )
        kp_costs_map = {k["kp_id"]: k for k in kp_costs}
        sorted_kps = [kp_costs_map[sid] for sid in sorted_ids if sid in kp_costs_map]

        # 5. 自适应阶段划分
        weekly_capacity = profile.get("learning_tempo", {}).get("weekly_study_capacity", 10)
        if weekly_capacity < 1:
            weekly_capacity = 10
        # 转换为每日学习时长（分钟），假设每周学习 5 天
        daily_duration = max(15, int(weekly_capacity * 60 / 5))
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
        bandit_selector=None,
    ) -> Dict[str, Any]:
        """
        根据测验结果和学习趋势动态调整路径（Thompson Sampling 增强）

        策略选择 = 分数段候选集（规则保底） + MAB 候选集内决策：
        - <50  ：候选 ["review_boost"]（基础未过，强制回炉，无采样空间）
        - 50-70：候选 ["practice_boost", "review_boost"]，规则先验取强化练习
        - 70-90：候选 ["maintain"]，正常推进
        - >=90 且趋势上升：候选 ["accelerate", "maintain"]，规则先验取加速
        - 注入 bandit_selector 且其已预热（累计收益反馈达到臂数，is_warm）后，
          由 Thompson Sampling 期望排序在候选集内接管决策（冷启动回退规则先验，
          避免随机扰动覆盖合理先验）
        - trend_state == "warning"：叠加预警规则（减少新内容，增加复习），不受 MAB 影响

        输出附带 strategy / strategy_source / strategy_candidates，便于前端
        在下一轮测验后回传该策略的实际收益（record_strategy_reward），形成闭环。
        """
        adjusted = {
            "status": "success",
            "adjustment_reasons": [],
            "stages": [dict(s) for s in current_path.get("stages", [])],
        }

        try:
            score = float(quiz_result.get("score") or 0.0)
        except (TypeError, ValueError):
            score = 0.0
        weak_tags = quiz_result.get("weak_tags", []) or []

        # 1. 候选策略集（分数段安全保底）与规则先验默认
        if score < 50:
            candidates = ["review_boost"]
            default_strategy = "review_boost"
        elif score < 70:
            candidates = ["practice_boost", "review_boost"]
            default_strategy = "practice_boost"
        elif score < 90:
            candidates = ["maintain"]
            default_strategy = "maintain"
        else:
            candidates = ["accelerate", "maintain"] if trend_state == "growth" else ["maintain"]
            default_strategy = "accelerate" if trend_state == "growth" else "maintain"

        strategy, strategy_source = default_strategy, "rule_fallback"
        if bandit_selector is not None and len(candidates) > 1 and getattr(bandit_selector, "is_warm", False):
            try:
                exclude = [a for a in bandit_selector.arms if a not in candidates]
                picked = bandit_selector.select(1, exclude=exclude)
                if picked:
                    strategy, strategy_source = picked[0], "thompson_sampling"
            except Exception:
                pass  # MAB 异常时回退规则先验

        # 2. 执行所选策略
        if strategy == "review_boost":
            adjusted["adjustment_reasons"].append(
                "测验得分过低，插入基础复习阶段并降低后续难度" if score < 50
                else "掌握度偏低，插入回炉复习并放慢后续进度"
            )
            adjusted["stages"].insert(0, {
                "stage_no": 0,
                "title": "紧急回炉" if score < 50 else "回炉复习",
                "type": "review",
                "topics": weak_tags[:3] if weak_tags else ["基础概念"],
                "kp_ids": [],
                "hours": 3,
                "criteria": "基础概念理解达标",
                "resources": ["基础讲解视频", "入门练习题"],
            })
            # 降低后续阶段难度：延长每个阶段时长（更细致地学习）
            slow_factor = 1.3 if score < 50 else 1.2
            for s in adjusted["stages"][1:]:
                if s.get("type") == "adaptive":
                    s["hours"] = round(s.get("hours", 5) * slow_factor, 1)

        elif strategy == "practice_boost":
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

        elif strategy == "accelerate":
            adjusted["adjustment_reasons"].append("表现优异且趋势上升，加速推进")
            # 将后续阶段时长缩短 20%
            for s in adjusted["stages"]:
                if s.get("type") == "adaptive":
                    s["hours"] = round(s.get("hours", 5) * 0.8, 1)

        # maintain：结构不变

        if trend_state == "warning":
            adjusted["adjustment_reasons"].append("学习预警状态，减少新内容，增加复习")
            for s in adjusted["stages"]:
                if s.get("type") == "adaptive":
                    s["hours"] = round(s.get("hours", 5) * 1.2, 1)

        # 重新编号
        for i, s in enumerate(adjusted["stages"]):
            s["stage_no"] = i + 1

        adjusted["estimated_total_hours"] = round(sum(s.get("hours", 0) for s in adjusted["stages"]), 1)
        adjusted["strategy"] = strategy
        adjusted["strategy_source"] = strategy_source
        adjusted["strategy_candidates"] = candidates
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
