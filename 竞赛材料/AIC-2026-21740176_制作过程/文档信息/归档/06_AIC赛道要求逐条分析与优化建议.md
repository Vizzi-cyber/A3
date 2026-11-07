# LearnLab 项目对照 AIC 算法创新赛要求 · 逐条分析报告

> 赛道要求核对 · 评分机制分析 · 算法实现程度 · 优化建议
>
> - **赛道**：第八届 AIC 算法创新赛 · AI+学科交叉赛道（tracks-2 / 3806）
> - **项目**：LearnLab —— 基于大模型的个性化资源生成与学习多智能体系统
> - **分析日期**：2026-09-03

---

## 〇、说明与依据

本报告基于项目仓库内已有的官方材料（《参赛要求说明.pdf》《AIC算法升级方案_LearnLab.md》《AIC技术方案_LearnLab.md》《挑战赛申请及优化亮点.docx》等）与当前代码实况撰写。评分机制与「八大部分」要求取自项目方已整理的参赛要求，线上赛道页因网络限制未能直接抓取、PDF 为扫描件，故以项目自身文档为准。核心算法结论均对照 `backend/app/algorithms/` 与 `backend/app/api/ai_algorithms.py` 实际源码，并实际运行 `verify_ai_algorithms.py`（结果 23/23 通过）。

---

## 一、赛道评分机制分析（总 100 分）

本项目参加的「算法创新赛 · AI+学科交叉」赛道，评分标准为六大维度、满分 100 分：

| 评分维度 | 分值 | 评审关注点 | 项目对应抓手 |
|---|---|---|---|
| 创新性 | 20 | 算法/方法是否有学术含量与原创点，能否给出「出处+公式+对照」 | BKT/IRT/FSRS/MAB/GKT/NCD 五层算法闭环 + 跨学科链路 |
| 需求分析 | 15 | 学科痛点是否真实、AI 赋能是否必要 | 新工科三大矛盾 + 传统 LMS 对比 |
| 方案可行性 | 20 | 技术/经济/推广可行性、可靠性 | 5 家 LLM 降级、防幻觉、自研算法可复现 |
| 项目实施 | 20 | 实施计划、资源保障、团队协作、代码/测试 | 分阶段计划 + 23 项算法验证 + 177 路由 0 崩溃 |
| 应用效果 | 20 | 效果验证（对照实验、量化对比） | 算法层已具备对照实验设计，真实试点数据待补充 |
| 总结与展望 | 5 | 总结深度、政策趋势结合、推广规划 | 三阶段推广 + 新工科/教育数字化政策 |

**补充说明**：项目早前还按「挑战赛」口径整理过另一套权重（创新价值与实践性 35% + 技术实现与功能要求 45% + 测试文档 10% + 演示视频/PPT 10%），用于《挑战赛申请及优化亮点》。本报告以「算法创新赛」六维评分为主口径，因其为当前参赛赛道且覆盖算法评分核心。

技术方案要求按「八大部分」组织，与评分维度基本一一对应：

| 部分 | 标题 | 对应评分维度 |
|---|---|---|
| （一） | 项目概述（背景/目标） | 需求分析（铺垫） |
| （二） | 需求分析（学科界定/痛点/AI 切入点） | 需求分析 15 |
| （三） | 解决方案设计（架构/算法/多智能体） | 创新性 20 + 方案可行性 20 |
| （四） | 方案可行性（技术/经济/推广） | 方案可行性 20 |
| （五） | 项目实施（计划/资源/团队） | 项目实施 20 |
| （六） | 应用效果（预期/试点/验证数据） | 应用效果 20 |
| （七） | 总结与展望 | 总结与展望 5 |
| （八） | 附录（代码/参考文献/材料） | 佐证全维度 |

---

## 二、算法实现程度盘点（重点）

**算法层现状**：从「5 大算法资产」已升级为「BKT / IRT / FSRS / MAB 四引擎 + GKT / NCD 两扩展 + 四个旧业务算法」。逐项评估如下：

| 算法模块 | 文件 | 升级状态 | 实现程度与依据 |
|---|---|---|---|
| BKT 知识追踪 | `bkt_engine.py` | ✅ 完整 | pyBKT 完整 EM 估计（prior/learns/guesses/slips/forgets），带 AUC 验证，含 numpy2.x 兼容补丁 |
| IRT 认知诊断 | `irt_diagnoser.py` | ✅ 完整 | 1PL/2PL 自研 MAP 联合估计（scipy BFGS），输出 θ/b/a，替代加权平均分 |
| FSRS 记忆调度 | `memory_scheduler.py` | ✅ 完整 | py-fsrs 三变量 D/S/R，复习队列 + 可提取性，持久化到 memory_cards 表 |
| Thompson Sampling | `bandit_selector.py` | ✅ 完整 | mabwiser MAB，冷启动 + 探索-利用 + 期望收益统计 |
| GKT 图知识追踪 | `gkt_engine.py` | ⚠️ 简化版 | 仅图卷积平滑 A_hat^k·X（拉普拉斯归一化），非完整 GCN+GRU 可学习模型 |
| NCD 神经认知诊断 | `ncd_diagnoser.py` | ⚠️ 有缺陷 | numpy 单调约束实现，但训练循环存在死代码（line 87/106）、未纳入验证脚本 |
| ADPP 路径规划 | `path_planning_dag.py` | ⚠️ 部分升级 | 已支持注入 BKT 引擎；但学习成本仍用人工难度表、adjust_path 仍为 50/70/90 规则阈值 |
| 效果评估 | `effect_evaluation.py` | ⚠️ 部分升级 | 已接 FSRS 记忆状态；但掌握度仍为加权平均（未接 IRT θ）、预测仍为线性外推 |
| 趋势分析 | `trend_analysis.py` | ❌ 未升级 | 仍为 6 因子人工权重（0.35/0.15/…）+ 线性外推 + 规则阈值，权重未学习化 |
| 加权匹配 | `weighted_matching.py` | ❌ 未升级 | 仍为 5 维人工权重线性加权，未叠加 MAB 探索层 |
| MNA 电路仿真 | `mna-solver.ts`（前端） | ✅ 学科亮点 | 并查集 + MNA 方程组 + 列主元高斯消元；暂态分析（RK4）仍待增强 |

**算法验证现状**：`backend/scripts/verify_ai_algorithms.py` 共 23 项断言，实际运行结果为 23 通过 / 0 失败，覆盖 BKT(6)、IRT(5)、FSRS(6)、MAB(3)、ADPP+BKT 与效果评估+FSRS 升级(3)。**注意：GKT 与 NCD 未纳入该验证脚本。**

---

## 三、评分维度逐条对照（符合项 vs 缺口）

### 3.1 创新性（20 分）—— 总体达标，算法层叙事已补齐

- ✅ **符合**：五层算法闭环（IRT 测量 → BKT/GKT 建模 → FSRS 记忆 → MAB 决策 → LLM 解释），每层均有经典/前沿出处（Corbett & Anderson、Rasch、KDD FSRS、ZPDES 等）。
- ✅ **符合**：跨学科学习链路（9 条跨课程依赖 + 跨学科路径算法 + 综合实战项目），为「AI+学科交叉」差异化亮点。
- ⚠️ **缺口**：GKT 为简化图平滑、NCD 有死代码，二者作为「前沿叙事」名不副实，需补全或降级定位，避免评审质疑。

### 3.2 需求分析（15 分）—— 文档已充分，代码侧无缺口

- ✅ **符合**：新工科三大结构性矛盾 + 传统 LMS 对比 + AI 赋能必要性论证，已在技术方案（二）成稿。
- ✅ **符合**：学科界定（计算机 × 电子信息）、三门课程（C 语言/电路分析/STM32）清晰。

### 3.3 方案可行性（20 分）—— 代码已就绪，需文档对齐

- ✅ **符合**：技术可行性（全栈开源框架 + 自研算法可复现 + 测试完备）。
- ✅ **符合**：可靠性工程（5 家 LLM 自动降级、6 道防幻觉、LLM 故障业务降级）。
- ⚠️ **缺口**：算法「接线不彻底」会削弱「方案自洽性」观感（详见第四节）——引擎实现了却没在业务链路里用上，评审顺藤摸瓜会发现断层。

### 3.4 项目实施（20 分）—— 代码与测试已达标

- ✅ **符合**：分阶段实施计划、资源保障、跨专业组队（待补充专业/年级）。
- ✅ **符合**：23 项算法专项验证、177 路由 0 崩溃、前端 E2E、数据流验证等可复现脚本齐全。
- ⚠️ **缺口**：团队成员专业/年级/分工仍待补充；演示视频与 PPT 待录制/调整。

### 3.5 应用效果（20 分）—— 最大短板

- ✅ **符合**：对照实验「设计」已就绪（BKT vs 简化 BKT 的 AUC、FSRS vs 固定间隔的记忆保持率、IRT 效度、MAB 选题效果）。
- ❌ **缺口**：真实试点数据缺失。目前只有代码级验证（verify 脚本），尚无 10-20 名学生的前测/后测/问卷量化结果，直接导致「应用效果 20 分」缺乏实据。
- ⚠️ **缺口**：算法接线未完成，导致部分对照实验（如 IRT 替换加权平均、MAB 替换规则选题）在业务链路里还跑不出「传统 vs 算法」的对比数据。

### 3.6 总结与展望（5 分）—— 基本达标

- ✅ **符合**：三阶段推广规划 + 教育数字化/新工科政策结合。
- ⚠️ **缺口**：需补 15-20 篇参考文献成册（目前为「待补充」状态）。

---

## 四、算法接线现状与优化建议（重点）

**核心判断**：算法引擎已「造好」，但「接入」不彻底——BKT 接入了路径规划，FSRS 接入了效果评估，而 IRT、Thompson Sampling、GKT、NCD 大多停留在 API 层「能独立调用」，尚未回写进业务链路。这是当前性价比最高、最能提升「应用效果 20 分」与「方案可行性 20 分」的优化方向。

### 4.1 P0 —— 高价值接线（直接补应用效果/方案可行性，约 2-3 天）

| # | 优化项 | 现状 | 建议 | 对应得分 |
|---|---|---|---|---|
| 1 | IRT θ 接入效果评估 | 效果评估掌握度仍是「最近5次加权平均」 | `evaluate()` 增加 irt_ability 参数，mastery 改用 IRT θ（标定后） | 应用效果/创新性 20 |
| 2 | IRT b 接入学习成本模型 | `path_planning_dag` 难度系数仍是 `{1:0.7,2:0.9…}` 人工表 | `_compute_learning_cost` 的 difficulty 改用 IRT 标定的 b 值 | 创新性/方案可行性 20 |
| 3 | Thompson Sampling 接入路径调整 | `adjust_path` 仍是 50/70/90 规则分档 | 每个调整策略(回炉/强化/加速)一个 Beta 臂，按历史收益采样 | 创新性/应用效果 20 |

### 4.2 P1 —— 补齐创新性叙事（约 2-4 天）

| # | 优化项 | 现状 | 建议 |
|---|---|---|---|
| 4 | 加权匹配叠加 MAB | `weighted_matching` 纯 5 维人工权重 | 保留打分作先验，叠加 Thompson Sampling/LinUCB 探索层 |
| 5 | 趋势分析权重学习化 | `trend_analysis` 6 因子人工权重 | 用历史数据训练逻辑回归/GBDT（标签=是否掉队），输出预警概率 |
| 6 | GKT 补全或降级定位 | `gkt_engine` 仅图平滑 | 改为可学习 GCN 层，或在文档中明确定位为「图卷积掌握度传播」（避免与真 GKT 混淆） |

### 4.3 P2 —— 工程收尾（约 1-2 天）

| # | 优化项 | 现状 | 建议 |
|---|---|---|---|
| 7 | 修复 NCD 死代码 | `ncd_diagnoser.py` line 87 有 `if False` 死代码、line 106 空 if | 清理死代码；训练循环向量化；补 monotone 校验 |
| 8 | 验证脚本覆盖 GKT/NCD | `verify_ai_algorithms.py` 未测 GKT/NCD | 补 GKT 传播单调性、NCD 拟合与预测断言，确保 23→30+ 项全绿 |
| 9 | 对照实验量化数据 | 仅有代码级验证，无真实对照 | 小规模试点 10-20 人前测/后测/问卷，产出「传统 vs 算法」量化表 |
| 10 | MNA 暂态分析(RK4) | 电路仿真仅直流稳态 | 补 RK4 暂态求解（电容/电感充放电波形），强化学科算法深度 |

---

## 五、结论

1. **评分机制清晰**：六维 100 分（创新性 20 / 需求分析 15 / 方案可行性 20 / 项目实施 20 / 应用效果 20 / 总结与展望 5），技术方案按「八大部分」组织，与评分维度基本对齐。
2. **算法层已「质变」**：从最初的 4 个规则式算法升级为 BKT/IRT/FSRS/MAB 四引擎完整实现（23 项验证全绿）+ GKT/NCD 两扩展，学术含量已达标。
3. **最大短板是「应用效果 20 分」**：真实试点数据缺失，且算法接线不彻底导致部分对照实验在业务链路中无法闭环产出量化对比。
4. **最优先动作**：完成 P0 三项接线（IRT→效果评估、IRT→成本模型、MAB→路径调整），即可同时强化「创新性」「方案可行性」「应用效果」三个高权重维度，性价比最高。

---

## 六、执行记录（2026-09-04）

P0 三项接线与 P2 工程收尾已全部完成并通过验证，本文第四节建议 1/2/3/7/8 落地。

### 6.1 改动清单

| # | 文件 | 改动 |
|---|---|---|
| 1 | `backend/app/algorithms/effect_evaluation.py` | **P0-1**：`evaluate()` 新增 `irt_ability` 参数，提供 θ 时掌握度改用标准正态百分位 Φ(θ)·100（θ~N(0,1) 先验，math.erf 实现），新增 `mastery_detail`（source / irt_theta / weighted_average）输出；未提供 θ 时行为不变 |
| 2 | `backend/app/algorithms/path_planning_dag.py` | **P0-2**：新增 `set_irt_diagnoser()` 与 `_difficulty_factor()`——IRT 标定 b 优先（`level = clip(3+0.8·b, 1, 5)` 对人工系数表线性插值），无标定记录回退人工分级，kp_costs 输出 `difficulty_source`。**P0-3**：`adjust_path()` 新增 `bandit_selector` 参数与三策略臂（review_boost / practice_boost / accelerate），分数段决定候选集（安全保底）、累计收益反馈达臂数后 MAB 接管（冷启动回退规则先验），输出 `strategy / strategy_source / strategy_candidates`，新增 `record_strategy_reward()` |
| 3 | `backend/app/services/algorithm_registry.py` | 新增 `get_irt_ability()`（未拟合返回 None 静默降级）、`get_strategy_bandit()`（按学生进程内缓存）、`update_strategy_bandit()`、`STRATEGY_ARMS` |
| 4 | `backend/app/api/dashboard.py`、`backend/app/api/trend.py` | 接线 P0-1：两处 `evaluate()` 调用传入 `get_irt_ability(student_id)` |
| 5 | `backend/app/api/learning_path.py` | 接线 P0-2（两处 planner 注入 IRT）与 P0-3（`/dag/adjust` 支持 `quiz_result.prev_strategy + reward` 收益闭环回传并传入 bandit）。**附带修复**：`/{student_id}/adjust` 通配路由遮蔽 `/dag/adjust` 的声明顺序 bug（该端点此前实际不可达），已调整注册顺序并注释说明 |
| 6 | `backend/app/api/onboarding.py` | 接线 P0-2：引导问卷 DAG 降级路径同样注入 IRT |
| 7 | `backend/app/algorithms/ncd_diagnoser.py` | **P2-7**：删除 line 87 死代码（`if False`）与 line 106-107 空 if；训练循环 numpy 向量化（SI/II/Y 索引 + np.add.at，消除逐样本 Python 循环与 O(n²) 的 `pairs.index`）；返回值新增 `monotone_w_ok` 校验 |
| 8 | `backend/scripts/verify_ai_algorithms.py` | **P2-8**：新增 GKT（5 项）、NCD（8 项）、P0 接线（17 项）断言，23 → **53 项** |
| 9 | `backend/scripts/verify_p0_wiring_api.py` | 新增 API 级冒烟脚本（11 项）：注册表 → dashboard/trend mastery_detail → dag/adjust 规则先验 / MAB 接管 / 收益闭环 / 低分保底 |

### 6.2 验证结果

| 验证 | 范围 | 结果 |
|---|---|---|
| `verify_ai_algorithms.py` | 算法层断言（BKT 6 / IRT 5 / FSRS 6 / MAB 3 / 升级 3 / GKT 5 / NCD 8 / P0 接线 17） | ✅ **53/53** |
| `verify_p0_wiring_api.py` | TestClient 全链路（演示库自动拟合 IRT：8 学生 × 162 题） | ✅ **11/11** |
| `verify_aic_features.py` | AIC 功能回归 | ✅ **29/29** |
| `verify_all_routes.py` | 全路由冒烟 | ✅ **206 路由 0 崩溃**（86 过 / 70 合法 4xx / 50 跳过） |

### 6.3 接线后的可验证收益（可写入技术方案「应用效果」）

- **掌握度口径升级**：仪表盘与趋势报告的 mastery 从「最近 5 次加权平均」升级为 IRT θ 百分位（`mastery_detail.source = irt_theta_percentile`），且保留加权平均作对照——同一学生两种口径的差值即「IRT 替代规则评分」的对照数据点。
- **学习成本模型升级**：路径规划难度系数由人工 1-5 分级升级为 IRT 标定 b 值连续插值（`difficulty_source = irt_b / manual` 可区分），同一知识点两种来源的耗时差即「IRT 成本模型 vs 人工分级」对照数据点。
- **路径调整策略升级**：`adjust_path` 由纯 50/70/90 规则分档升级为「分数段候选集保底 + Thompson Sampling 候选集内决策 + 收益闭环反馈」，`strategy_source` 可区分 `thompson_sampling / rule_fallback`，配合 `prev_strategy + reward` 回传即可在试点中积累「MAB vs 规则」的策略收益数据。

### 6.4 遗留事项（更新至第四节优先级）

- P1-4 加权匹配叠加 MAB、P1-5 趋势分析权重学习化、P1-6 GKT 补全或降级定位（文档侧可先做「图卷积掌握度传播」的明确定位）
- P2-9 真实试点数据（10-20 人前测/后测/问卷，需组织）
- P2-10 MNA 暂态分析 RK4（前端 `mna-solver.ts`）

---

## 七、全量算法审计与修复（2026-09-04 第二轮）

以算法评审视角对 `backend/app/algorithms/` 全部 10 个模块 + 相关 API 接线做了双轴审查（代码标准轴 + 规格符合轴）与逐文件人工审计，修复如下。

### 7.1 审查发现并修复的真问题

| # | 级别 | 位置 | 问题 | 修复 |
|---|---|---|---|---|
| 1 | 🔴 bug | `algorithm_registry.py` | 收益闭环首反馈丢失：`update_strategy_bandit` 对未缓存学生直接丢弃（`bandit is None → return False`），每个学生/每次重启后的第一条 `prev_strategy+reward` 被静默吞掉 | 改为自动创建 bandit 后再反馈 |
| 2 | 🔴 bug | `path_planning_dag.py` | ≥90 且趋势上升档 MAB 决策退化：候选集 `["accelerate","maintain"]` 中 `maintain` 不在臂集里，MAB 在该档退化为必选 accelerate（即使其历史收益差） | `STRATEGY_ARMS` 增加第 4 臂 `maintain`（单一来源在 path_planning_dag，registry 导入），高分档可在「加速/维持」间真实决策 |
| 3 | 🔴 数据缺口 | `api/trend.py` | `learning_history` 只传 `duration/progress`，导致趋势分析的学习速度、连续稳定性、完成率三个维度因子恒为 0（算法无错、数据饿死） | 补传 `action/kp_id/created_at` |
| 4 | 🟡 健壮性 | `trend_analysis.py` | 分数/时长直接算术运算，`None`/字符串分值会 TypeError 崩溃（测验 `score` 列可空） | 增加 `_safe_float/_safe_int` 全量防御 |
| 5 | 🟡 健壮性 | `bkt_engine.py` | 无逐题数据时 `score` 为字符串会崩溃 | float 容忍转换 |
| 6 | 🟡 健壮性 | `weighted_matching.py` | 空串目标 `"" in ""` 恒真，会把 goal_match 虚增到 1.0 | 空串过滤守卫 |
| 7 | 🟡 健壮性 | `memory_scheduler.py` | `deserialize` 对损坏 JSON 直接崩溃 | try/except + 类型校验，损坏条目跳过 |
| 8 | 🟡 健壮性 | `path_planning_dag.py adjust_path` | HTTP 传入的 `score` 为字符串时 500 | float 容忍 + 回退 0 分 |
| 9 | 🟡 隐藏缺陷 | `verify_ai_algorithms.py` | 「FSRS 无效评分拒绝」断言是恒真表达式（`lambda and False or True`），从未真正校验异常 | 改为真正捕获 ValueError 断言 |
| 10 | ⚪ 死代码 | `path_planning_dag.py _weighted_sort` | `topo_order` 计算后从未使用（且白做一次拓扑排序） | 删除 |
| 11 | ⚪ 可读性 | `gkt_engine.py` | `not self.adj_norm is not None` 双重否定 | 改为 `self.adj_norm is None` |

### 7.2 优化项

- **NCD 训练早停**：损失改进 < 1e-7 时提前收敛，避免固定跑满 800 轮（拟合结果不变，训练更快）。
- **效果评估去重复算**：`_calc_mastery` 原在 IRT 接管时被计算两次（mastery + mastery_detail），现复用一次结果。
- **MAB 冷启动判定封装**：`ThompsonSamplingSelector` 新增 `is_warm` 属性，`adjust_path` 不再伸手读取选择器内部统计（Feature Envy 消除）。
- **IRT 注入去重**：registry 新增 `attach_irt_to_planner(planner)`，learning_path 两处 + onboarding 一处的重复注入块收敛为一个 helper（Duplicated Code 消除）。
- **PEP 8**：NCD 向量化变量 `SI/II/Y/E` 改小写命名；verify 脚本超长 lambda 重写。

### 7.3 审计后验证结果（全部重跑）

| 验证 | 结果 |
|---|---|
| `verify_ai_algorithms.py`（新增加固/守卫/闭环断言） | ✅ **62/62** |
| `verify_p0_wiring_api.py`（同步 4 臂预热条件） | ✅ **11/11** |
| `verify_aic_features.py`（回归） | ✅ **29/29** |
| `verify_all_routes.py`（全路由冒烟） | ✅ **206 路由 0 崩溃**；我改动的端点逐一探测均 200 |

**审计结论**：BKT/IRT/FSRS/MAB/GKT/NCD/ADPP/效果评估/趋势分析/加权匹配十个模块现在全部通过数值边界、None 容忍、空值守卫、类型防御与业务闭环的检查；策略臂候选集、收益反馈闭环、路由可达性三处链路级缺陷已修复并有回归断言覆盖。

---

## 八、算法补全执行记录（2026-09-04 第三轮）

本节对应第四节遗留的 P1 全部三项与 P2-10，至此除「P2-9 真实试点数据」（需真人组织）外，报告提出的算法优化项全部落地。

### 8.1 P1-6 GKT：简化图平滑 → 可学习门控图卷积

`gkt_engine.py` 重写：
- 传播公式升级为 `final = α·X + (1−α)·(w·A_hat^k·X + b)`，新增可学习参数：邻居传播增益 w（**非负投影保持单调可解释**）、偏置 b、融合门 α = σ(g)；
- **自监督训练**：以「t 日掌握度快照 → t+1 日快照」为样本做 MSE 拟合（无需人工标注），全批梯度下降 + 早停；训练数据由 `build_mastery_snapshots`（学习记录每日最大进度）自动构建；
- 未训练时退化为确定性平滑（w=1, b=0, α=0.6），完全向后兼容；`is_fitted` 语义改为「已训练」；
- 接线：教师端 `POST /algorithms/gkt/train`（演示库实测多学生快照训练成功）、`/algorithms/status` 增加 gkt 字段；路径规划 `plan_path` 在 BKT 掌握度覆盖后叠加 GKT 图感知传播（learning_path 两处 + registry `attach_gkt_to_planner`）。

### 8.2 P1-5 趋势分析：6 因子人工权重 → 数据学习权重 + 掉队预警概率

`trend_analysis.py` 新增 `TrendWeightLearner`：
- numpy 手写 **L2 正则逻辑回归**（BCE 数值稳定梯度 + 早停），无需新增依赖；
- 标签自动构建（`build_trend_training_samples`）：趋势快照 + 测验/学习记录 → 「随后一周平均分 < 60 或学习中断」= 掉队（1）；
- 输出两层：① **符号归一化融合权重**（−coef/Σ|coef|，极性与"越大越好"语义对齐，替代人工 0.35/0.15/…）；② **掉队预警概率** `σ(w·x+b)`；
- `analyze()` 增加 `weight_learner` 参数：已训练用学习权重 + 预警概率（`weights_source: "learned"`），未训练回退人工权重 + 状态映射概率（`manual_prior`）；输出增加 `weights / weights_source / warning_probability`；
- 接线：教师端 `POST /algorithms/trend/train`、trend 报告与 dashboard 学情分析两处调用全部接入。

### 8.3 P1-4 加权匹配：纯人工权重 → 先验打分 + Thompson Sampling 探索层

- `weighted_matching.py`：`match_resources()` 新增可选 `bandit_selector`（臂 = 8 类资源类型，`RESOURCE_ARMS` 单一来源 + `resource_arm()` 提取器）；混合公式 `final = score + explore_weight·(E[arm] − 0.5)`——**冷启动 E=0.5 时排序与纯打分完全一致**（零扰动），预热后高收益资源类型被提升；结果标注 `exploration` 元数据与逐项 `exploration_adjust`；
- 闭环：`POST /matching/feedback`（student_id + resource_type + reward 0-1）→ registry 按学生缓存的资源 MAB 更新 → 下次匹配调序；`/matching/resources` 已接入；
- 路径匹配保持纯打分（无自然反馈信号，不过度设计）。

### 8.4 P2-10 MNA 电路仿真：直流稳态 → 直流修复 + RK4 暂态分析

`mna-solver.ts` 重构升级：
- **修复直流缺陷**：电感在直流稳态下此前被完全忽略（等效开路，错误），现正确 stamp 为 0V 电压源（短路），支路电流可读；电容开路（原本正确，补注释说明）；
- **新增 `runTransientAnalysis`（状态变量法 + RK4）**：电容替换为电压源 vc、电感替换为电流源 il，每阶段一次 MNA 直流求解读回 `dvc/dt = iC/C`、`dil/dt = vL/L`，四阶 Runge-Kutta 推进；导出 `TransientResult` 波形（时间轴 + 各电容电压/电感电流序列），步数上限保护前端性能；
- 架构上抽出 `buildNetlist` / `solveMNA` 共享内核，直流与暂态复用同一套并查集建图 + 列主元高斯消元；
- 接线：`solveCircuit` 检测到电容/电感时**自动附带**暂态结果；`MeasurementOverlay` 新增「暂态分析（RK4）」面板（各动态元件终值 + 稳态建立时间）；
- **数值验证**（`frontend/scripts/mna-numeric-test.ts`，`npm run test:mna`，esbuild 打包 node 运行）：RC 充电对照解析解 `V(1−e^(−t/RC))`、RL 升流对照 `V/R(1−e^(−tR/L))`、LC 振荡峰值 2V 出现在 T/2（RK4 幅值保持）、电感直流短路、自动附带波形，**9/9 通过**。

### 8.5 补全后验证结果（全部重跑）

| 验证 | 范围 | 结果 |
|---|---|---|
| `verify_ai_algorithms.py` | 算法层断言（新增 GKT 可学习 6 / 趋势学习器 7 / 匹配探索 3） | ✅ **77/77** |
| `verify_p0_wiring_api.py` | API 全链路（新增训练端点 + 匹配闭环 5 项，演示库真实数据训练） | ✅ **16/16** |
| `verify_aic_features.py` | AIC 功能回归 | ✅ **29/29** |
| `verify_all_routes.py` | 全路由冒烟（含 3 个新端点） | ✅ **209 路由 0 崩溃** |
| `npm run test:mna` | MNA 数值对照（RC/RL/LC 解析解） | ✅ **9/9** |
| `npm run build`（tsc + vite） | 前端类型与构建 | ✅ 零错误，43s 构建成功 |

### 8.6 结论更新

报告第四节提出的 10 项优化建议中，9 项（P0-1/2/3、P1-4/5/6、P2-7/8/10）已全部实现并通过验证；唯一遗留 **P2-9 真实试点数据**需组织 10-20 名学生开展前测/后测/问卷（方案见差距分析 5.1），属于运营动作而非代码工作。至此算法层的「接线 + 补全」阶段收官，可进入试点数据收集与比赛材料冲刺。

---

## 九、文档-代码对齐修复执行记录（2026-09-05 第四轮）

对仓库全部 16 份 md + 2 份 docx 做了「文档声明 vs 代码实况」全量对照核查（约 260 条可验证声明），对发现的 A 类缺口（文档声明已实现但代码缺失）逐项修复：能补代码的补代码，成本过高或低价值的改文档口径。

### 9.1 代码修复清单（8 项）

| # | 文件 | 改动 |
|---|---|---|
| 1 | `algorithms/path_planning_dag.py` + `api/learning_path.py` | **FSRS→路径**：`plan_path` 新增 `due_kp_ids` 可选参数，到期知识点插入路径头部 review 阶段（`review_source=fsrs_due` 可溯源，stage_no 重编号、总时长重算、已覆盖知识点去重）；`/dag/generate` 经 `build_memory_status` 注入；`/generate` 转换保留 `type/kp_ids` 字段 |
| 2 | `services/algorithm_registry.py` + `agents/error_catcher.py` + `agents/resource_generator.py` + `api/error_catcher.py` + `api/resource.py` | **KT 注入三处智能体**：抽出共享 `build_ai_engine_context` / `format_ai_engine_context`（tutor 原逻辑上收）；error_catcher 四端点 + full-diagnosis、resource_generator 四类生成任务全部注入 BKT 薄弱点+FSRS 到期上下文（`ErrorCatchRequest` 增 `student_id`）。**顺带修复 tutor 两处既有 bug**：图文模式 `_format_ai_engine` 重复注入两次、纯文本模式漏注入 |
| 3 | `algorithms/weighted_matching.py` + `api/matching.py` | **IRT b→匹配难度**：`match_resources` 新增 `irt_difficulty/irt_ability` 参数，`_difficulty_fit` 支持 logistic(θ−b) 连续拟合分（`difficulty_source=irt_b/manual` 可区分）；API 侧复合 item_id 按 kp 前缀聚合。**顺带修复难度因子恒 1.0 的真 bug**（profile 缺 `knowledge_level` 键 + 档位表缺 `medium`，现从 `knowledge_base.overall_score` 推导三档） |
| 4 | `api/auth.py` + `frontend/src/services/api.ts` | **JWT Token 刷新**：新增 `POST /auth/refresh` 滑动续期（验签 + 查库 `is_active`，禁用账号无法续期）；前端 401 拦截器改为静默刷新+重放原请求（并发 401 合并等待同一次刷新，认证接口 401 直接登出） |
| 5 | `api/result_evaluator.py` | **反思循环接线**：`/evaluate-code` 在 `REFLECTION_ENABLED=true` 时走 `run_with_reflection`（quality_threshold 显式 0.7，规避规则评估无 confidence 字段时的空转满轮），防幻觉第⑥道自我纠错随此路径生效；默认关闭保持原行为 |
| 6 | `api/gamification_challenge.py` + `pages/LeaderboardPlus.tsx` | **六维排行榜真实化**：后端新增 `ai_collab`（tutor_qa_records 问答次数）与 `improvement`（前测/后测配对差值）两维真实计算；前端删除「AI协作榜→points、进步榜→mastery」的别名假映射；mastery 维度 metric 由 % 改为「个」（后端语义为掌握个数） |
| 7 | `components/AlgorithmVisualizer.tsx` | **BFS/DFS 图遍历动画**：新增 GraphStep 帧模型 + 2 张预设图 + BFS（队列）/DFS（递归栈）帧生成器，复用既有播放控制/伪代码高亮框架；控制栏图模式切换预设图，图例按模式切换 |
| 8 | `store/kbStore.ts` | **500ms 防抖自动保存**（兑现 README 声明）：setContent/setTitle 走模块级防抖窗口（标题+内容合并一次 PATCH），置 `isDirty`（修复脏标记圆点从未生效的 bug），切换/删除笔记前 flush 防丢尾字 |

### 9.2 文档勘误清单

- **README**：报告导出 PDF/Excel/Word→「CSV(Excel兼容)/Markdown」；`Profile.tsx` 页面行改为 PersonalSpace 承接；艾宾浩斯→FSRS 口径；E2E 三处矛盾数字统一为「7 文件 49 用例」；模块计数更新为实测（39 API 模块 / 210+ 接口 / 14 敏感词）；结构树 Dockerfile/compose 按实况修正（Dockerfile 位于 frontend/）；数据库快照数字刷新
- **技术方案**：反思循环与防幻觉第⑥道标注「`REFLECTION_ENABLED` 配置启用，默认关闭」；算法接线段落补 FSRS→路径复习阶段、IRT b→匹配难度、三处智能体注入；故障模板措辞改为「断路×2/短路×1，错值以极端阻值注入」
- **进度同步**：清理 3 处过期状态（班级维度已实现、PRODUCT.md 已移除、未提交改动已入库）+ LandingPage 展示位置变更说明

### 9.3 明确不改代码、维持文档口径的项

- PDF/Word 导出：实现成本高、比赛演示价值低，README 已改为实际能力
- Token 黑名单/jti：refresh 已带 is_active 校验，满足单机演示场景
- DKT 家族 / EduQate / LinUCB / AKT / SAINT+ 等高级算法：《高级算法精选》中本就定位为后续批次/展望，不虚构落地
- profiler 画像 θ 升级、测验评分难度加权：涉及评分语义变更，维持「IRT 标定已完成、画像接入为后续迭代」口径

### 9.4 本轮验证结果（全部重跑）

| 验证 | 范围 | 结果 |
|---|---|---|
| `verify_ai_algorithms.py` | 算法层断言（新增第二轮接线 14 项） | ✅ **91/91** |
| `verify_p0_wiring_api.py` | API 全链路（新增 refresh/FSRS 路径/排行榜六维/反思循环 10 项） | ✅ **26/26** |
| `verify_aic_features.py` | AIC 功能回归 | ✅ **29/29** |
| `verify_all_routes.py` | 全路由冒烟（含 /auth/refresh） | ✅ **210 路由 0 崩溃** |
| `npm run test:mna` | MNA 数值对照 | ✅ **9/9** |
| `npm run build`（tsc + vite） | 前端类型与构建 | ✅ 零错误 |

### 9.5 结论

至此，全部文档中「声明已实现」的功能与代码实况对齐：文档侧不再存在失实的✅条目，算法叙事（五层闭环 + 三处智能体注入 + FSRS 全链路）均有对应实现与验证断言背书。遗留待办不变：P2-9 真实试点数据（需组织 10-20 名学生）、演示视频、PPT 重排、团队信息回填，均为材料/运营动作。

---

## 十、全量后端审计与修复执行记录（2026-09-05 第五轮）

以「整个项目开发情况 + 后端逻辑」为对象做三路并行代码审计（API 路由层 24 项 / 算法服务层 20 项 / 智能体与图编排层 17 项，合计约 58 个真问题，其中 🔴 22 个），逐项核实后修复；同时按复查结论对全部 md 做终版数字对齐。

### 10.1 🔴 用户可见故障与越权（全部修复）

| # | 位置 | 问题 | 修复 |
|---|---|---|---|
| 1 | `api/gamification_challenge.py` | quiz_score 排行榜 `count(QuizResultModel.id)` 引用不存在列，恒 500 | 改 `quiz_id` |
| 2-4 | `api/tutor.py` | /ask、/session/history、WS 三处缺归属校验（可冒用他人画像/代答/读他人会话） | 全部补 sub 校验/本人过滤/会话前缀校验 |
| 5 | `api/tutor.py` qa-feedback | 必填 query 参数 + 与前端 body 字段不一致，恒 422（点赞功能从未落库） | 改 body 模型 `{rating}` + 归属校验 |
| 6 | `api/log_reflection.py` | 日期正则 `r"^\d..."` 双反斜杠永不匹配，反思/日志创建整体失效 | 改单反斜杠 |
| 7 | `api/assignment.py` | 学生读作业详情可见 correct_answer | 学生视图剥离答案/解析，教师保留 |
| 8 | `api/gamification.py` | /points/add、/achievements/unlock 允许学生自铸积分成就 | 收紧为 require_teacher（前端零调用） |
| 9 | `api/analytics.py` | 无测验学生调预测 IndexError 500 | 空分数兜底 |
| 10 | `api/knowledge_base.py` | analyze-and-save 调用包装器不存在的 `.chat` 方法，LLM 分析从未生效 | 改 `await llm.ainvoke(...)` |
| 11 | `api/trend.py` | 历史趋势升序+limit 取到最旧 N 天 | 取最近 N 天后升序返回 |

### 10.2 🔴 算法/服务/编排层（全部修复）

| # | 位置 | 问题 | 修复 |
|---|---|---|---|
| 12 | `path_planning_dag.py` | 难度量纲错位：DB 存 0-1 比例（0.2~0.65），算法按 1-5 查表恒默认值 | build_graph 入口归一化（`_normalize_difficulty_level`） |
| 13 | `algorithm_registry.py` | IRT item_id 为 `{kp}:{qid}` 复合键时 planner 按 kp 查难度恒 miss | 注入 `_KpAggregatedIRT` 前缀聚合视图 |
| 14 | `services/path_adjustment_engine.py` | 后台任务复用请求级 Session（请求返回后已关闭） | 任务内自建 SessionLocal |
| 15 | `path_planning_dag.py` | /generate 主链路无环检测，成环数据递归爆炸 | plan_path 入口拒绝 + 两个递归函数加 in-progress 防护 |
| 16 | `services/content_library.py` | `_FALLBACK_LIBRARY` 空壳 + 单列 JSON 损坏连坐整体 | 删空壳、按列容错部分降级，README 口径同步 |
| 17 | `graph/nodes.py` | assembler 失败集合不含 "error"（全挂仍报 success） | 纳入 error |
| 18 | `agents/tutor.py` | 全局单锁包住整个 LLM 调用，全站辅导串行化 | 每会话独立锁 |
| 19 | `api/tutor.py` WS | 连接泄漏（无 finally）、同 session 覆盖死 socket、可连他人会话 | try/finally + 旧连接关闭 + 归属校验 + 历史读写加锁 |
| 20 | `agents/path_planner.py` | `data if status!="error" else data` 死条件，错误 JSON 伪装成功 | 显式 failed |
| 21 | `graph/nodes.py` | 三处缓存 key 漏画像/认知风格（资源串号、画像回退） | key 纳入个性化字段 |
| 22 | NCD 孤立引擎 | 不进注册表、重启后 /ncd/ability 恒 409 | 进 algorithm_registry + 启动自动拟合 + /algorithms/status 暴露 |

### 10.3 🟡/⚪ 健壮性与清理（要点）

- 数据健壮性：teacher 导出分数 None 防护、dashboard trend_factor falsy-zero、daily_quiz overall_score 类型防护 + count 参数约束、learning_data 画像失败回滚、prerequisites 短串防护、kg_builder 批次失败不静默
- 权限收紧：/knowledge/create、/knowledge-graph/build、/monitoring/health/record → require_teacher
- 并发/性能：main.py 启动拟合包 to_thread（不再阻塞事件循环）、agent_flow 持任务引用防 GC + 归属校验、_load_knowledge_graph_from_db 包 to_thread + 回填缓存、bandit 缓存容量上限
- 行为修正：llm_factory astream 首 chunk 后不再重试（防内容重复）、image_generation 网络异常统一包业务异常（可回退）、反思循环规则评估认得 evaluation/report 键、course_designer 无 parallel_groups 时按依赖序兜底执行子任务 + full-diagnosis 透传 ai_engine、图文模式补 sanitize、tutor 图文/文本双模式口径统一
- 清理：删除零调用文件 `services/agent_tools.py`、course_designer 未用 import、daily_quiz 死变量、onboarding DAG 终点加稳定排序、冷却时间戳改分析成功后写入、plan_path 拷贝 mastery_map 消除副作用
- 误报澄清：bandit `is_warm` 审计称与注释不符——实现是「快速预热」的产品语义且全部测试/文档基于它，改注释而非改代码

### 10.4 文档终版对齐（数字以 10.5 实测为准）

- 过期数字 24+ 处：77→100、16→38、209→210、53→49、23→100、verify_live「33 项」→ 实测 22 项（03/02/04/技术方案/进度同步/README/计划书/文档信息README）
- README 补 `/auth/refresh` 接口条目与 `verify_p0_wiring_api.py` 脚本行
- 根目录《AIC算法升级方案》§0 加「过程存档勿作现状引用」说明，置信区间/LU 分解/12 智能体注入等未实现条目补「后续批次」标注；《教育算法分析报告》画像 θ、测验难度加权两条补「后续迭代」标注
- 进度同步补第四/五轮记录行、更新日期

### 10.5 本轮验证结果（全部重跑）

| 验证 | 范围 | 结果 |
|---|---|---|
| `verify_ai_algorithms.py` | 算法层断言（新增第三轮修复 8 项） | ✅ **100/100** |
| `verify_p0_wiring_api.py` | API 全链路（新增安全/越权/契约/NCD 12 项） | ✅ **38/38** |
| `verify_aic_features.py` | AIC 功能回归 | ✅ **29/29** |
| `verify_all_routes.py` | 全路由冒烟 | ✅ **210 路由 0 崩溃**（88 过 / 72 合法 4xx / 50 跳过） |
| `npm run test:mna` | MNA 数值对照 | ✅ **9/9** |
| `npm run build` | 前端类型与构建 | ✅ 零错误 |

### 10.6 结论

三轮文档-代码对齐（九）+ 一轮全量后端审计（本节）后：文档中不再存在失实声明或过期数字；后端三层（API/算法服务/智能体编排）已按审计清单完成全部 🔴 与高价值 🟡 修复，用户可稳定触发的确定性故障（quiz_score 榜、辅导越权、点赞失效、反思日志 422、答案泄漏）全部消除并有回归断言背书。缓做项（bandit 收益持久化、状态词表全量统一、streak 时区、DKT 家族等）均已在文档中如实标注口径。

---

## 十一、三维专项审查修复执行记录（2026-09-05 第六轮）

以三种审查方法论对「功能层 + 工作流层 + 智能体层」做专项审查：前端按 TypeScript/React 审查清单（Critical/High 分级）、智能体层按代码坏味道基线（Fowler ch.3 十二项逐条对照 + 正确性专项）、全库按架构深化方法论（浅模块/接缝/局部性/删除测试）。审查发现前端 7 Critical + 8 High、智能体层 13 项新缺陷、架构候选 7 项。本轮修复全部**点状缺陷**（27 项），架构级候选留待专项（见 11.4）。

### 11.1 前端 Critical 修复（7 项，tsc + build 门禁零错误）

| # | 位置 | 问题 | 修复 |
|---|---|---|---|
| 1 | `pages/Tutor.tsx` 两处 | `profileApi.analyzeConversation` 副作用写进 setMessages updater（StrictMode/并发重放下重复分析、重复扣配额） | 消息镜像 ref + `triggerConversationAnalysis()` 在 updater 外触发；两处 setTimeout(loadProfile) 一并纳入 ref 清理 |
| 2 | `services/api.ts` | apiGet/apiStream（fetch 通道）401 直接硬跳转 /login，绕过 axios 通道的静默刷新 | 抽 `fetchWithAuth`：复用 tryRefreshToken 换新 token 重发一次，失败才派发 auth:expired 软通知 |
| 3 | `pages/LandingPage.tsx` | TypeWriter 清理函数写在 setTimeout 回调 return 里（死代码），interval 泄漏 | timer 变量提升，cleanup 同时清 timeout + interval |
| 4 | `pages/ProjectCollaboration.tsx` | 可增删成员列表 `key={idx}` + 按 index 删除 | key 与删除均按 student_id 寻址 |
| 5 | `components/ChatPanel.tsx` | 附件列表 `key={i}` + 按 index 删除 | key 与删除按 dataURL 值寻址 |
| 6 | `pages/circuit/CodeEditor.tsx` | pinMappings 可增删改却全按 index 寻址 | PinMapping 加 `id` 字段，key/update/remove 全部按 id |
| 7 | `components/kb/NoteEditor.tsx` | 标题重置 effect 依赖 activeNote 对象身份，自动保存回写覆盖输入（丢字） | 依赖改 `activeNote?.note_id` |
| 8 | `pages/ProjectCollaboration.tsx` | 6 个 `useState<any>` + 8 处 `catch (error: any)` | 定义 6 个最小 interface（team_health 四分数字段、team_performance 数组等按实际消费形状）；error 收窄 unknown + `extractErrorMessage` helper |

### 11.2 前端 High 修复（7 项）

PPTGenerator 轮询 unmount 兜底清理；LandingPage/Login 路由包 ErrorBoundary（WebGL 崩溃不再白屏）；两个教师页 visibilitychange 闭包经 ref 调最新函数；AlgorithmVisualizer setPlaying 移出 updater（新增独立 effect 判停）；AgentFlowPanel 轮询 stale 标志防旧 run 响应覆盖；SystemSettings 移除「假保存」（后端无改密码接口，validateFields 恒过 + 密码三项无 name，改为只读展示与禁用说明——不做假功能）。

### 11.3 后端智能体/工作流修复（13 项）

| # | 位置 | 问题 | 修复 |
|---|---|---|---|
| 9 | `graph/nodes.py` | `_parallel_agents` 置位后永不复位：启用并行路由即无限 fan-out（潜伏地雷） | router_edge 构造 Send 时显式置 None |
| 10 | 7 个 agent 文件 18 处 | `generate_json` 返回 error 未检查，错误 dict 被当成功数据透出 | 按括号平衡定位语句逐处补 failed 检查（collaboration_supervisor 的 llm_analysis 为降级语义置 {}） |
| 11 | `agents/course_designer.py` | `_get_student_profile` 恒拿硬编码兜底画像（profiler 返回无 profile 键），个性化全失效 | 兼容读 `analysis.profile / analysis`，无数据保留兜底 |
| 12 | `agents/knowledge_graph_builder.py` | 上轮批次防护断线：`_process_batch` 从不返回 status，failed_batches 恒 0 | 失败/空产出返回 `status:"error"`，成功补 success |
| 13 | 3 个 agent + nodes.py | cognitive_style str/dict 混型 `.get` AttributeError（LLM 返回字符串即崩） | `get_primary_cognitive_style` 统一守卫，4 处调用点全换 |
| 14 | `graph/nodes.py` | 事件流不看 result.status 恒推 completed；未知 task_type 输出「success 0/0」；assembler 漏 partial_failure | 按 status 推 completed/failed；未知类型直接输出 error final_output；失败集合纳入 partial_failure |
| 15 | `services/path_adjustment_engine.py` | 后台任务不持引用（GC 回收）；db 在 try 内赋值（finally 可能 NameError）；同步 DB 查询阻塞事件循环 | 引用集持任务；SessionLocal 提到 try 外；分析包 to_thread |
| 16 | `services/llm_factory.py` | ainvoke 日志任务不持引用；FailoverLLM.astream 已 yield 后降级导致下游收到重复前半段 | `_spawn_logged` 持引用；yielded 后直接 raise 不再切 fallback |
| 17 | `core/config.py` | ARK_*/VOLC_* 字段定义重复两遍（后者静默覆盖，改前一组即埋雷） | 删重复块 |
| 18 | `agents/base.py` | get_status 在子类覆写字符串 status 后 `.value` AttributeError；run_with_reflection 向调用方 context 原地写入死反馈键 | str/Enum 双兼容；改写局部副本 |
| 19 | `agents/course_designer.py` | `isinstance(result, Exception)` 死分支 | 删除 |
| 20 | `services/ppt_generator.py` | `if any(...): pass` 死代码；`add_shape(1)` 魔法数字 | 删除；MSO_SHAPE.RECTANGLE |

### 11.4 架构候选（审查产出，留待专项，本轮不动）

1. **Agent 调用深入口**（Strong）：6 文件 27 个同构路由 + base.py 深机制（cached_process/guards/reflection）被主调用方绕过；18 处 error 检查的复制块应由基类模板方法收口
2. **学生学习上下文构建器**（Strong）：掌握度聚合×4、COURSE_NAMES×5、planner 算法注入三处漂移（adjustment 零注入、onboarding 缺 BKT）
3. **归属/角色校验收口**（Strong）：47 处内联 403 校验收敛到 auth.py 既有依赖
4. **测验提交事件显性化**（Worth）：record_quiz 为隐藏编排器，调用链 12 文件
5. **graph 层归属决策**（Worth）：V1 路由死配置可删；LangGraph 仅服务 1 端点，真实编排散在路由内联
6. **前端 api.ts 收口与巨型页面拆分**（Worth）：res.data.data 泄漏 20 处；3 个 2000+ 行页面
7. **status 词表收口**（Speculative）：251 处字面量，依赖候选 1 落地

### 11.5 本轮验证结果（全部重跑）

| 验证 | 范围 | 结果 |
|---|---|---|
| `verify_ai_algorithms.py` | 算法层断言（新增智能体加固 7 项） | ✅ **107/107** |
| `verify_p0_wiring_api.py` | API 全链路 | ✅ **38/38** |
| `verify_aic_features.py` | AIC 功能回归 | ✅ **29/29** |
| `verify_all_routes.py` | 全路由冒烟 | ✅ **210 路由 0 崩溃** |
| `npm run test:mna` | MNA 数值对照 | ✅ **9/9** |
| `npm run build`（tsc + vite） | 前端类型与构建门禁 | ✅ 零错误 |

### 11.6 结论

功能层（前端页面/组件）、工作流层（LangGraph 编排与事件流）、智能体层（12 agent 与基类契约）的点状缺陷已全部修复并有断言背书：前端不再有 updater 副作用/泄漏/契约断裂，智能体层不再有错误伪装成功/混型崩溃/死防护，工作流层不再有并行死循环地雷与事件失真。架构级候选 7 项留待专项推进（其中候选 1/3 建议比赛后立即启动，比赛期间不动——当前链路功能正确，重构收益是长期可维护性而非演示效果）。
