# AIC 算法创新赛 · 项目进度同步

> 实时同步 LearnLab 备战第八届 AIC"算法创新赛"· AI+学科交叉赛道的项目进度
> 最后更新：2026-08-13（深夜）
> 提交截止：2026-09-10（剩余约 4 周）

---

## 一、总体进度

| 阶段 | 内容 | 状态 |
|---|---|---|
| 阶段一 | 代码完善（跨学科/试点/实验实训/可靠性/降级） | ✅ 全部完成（含补漏项） |
| 阶段二 | 试点运行收集数据 | ⏳ 待启动（计划 9/1-9/9） |
| 阶段三 | 参赛文档材料 | ⏳ 待启动（计划 8/27-9/8） |
| 阶段四 | PPT 调整 + 演示视频 | ⏳ 待启动（计划 9/5-9/9） |

---

## 二、代码完善阶段完成明细（8/13 完成）

### ✅ 已交付功能（8 项，全部通过测试）

| # | 功能 | 对应评分项 | 状态 | 验证 |
|---|---|---|---|---|
| 1 | **D1 多模型注册+自动降级**：5家provider（星火/DeepSeek/智谱/OpenAI/MiMo）、FailoverLLM降级链、无Key清晰报错 | 方案可行性 20 | ✅ | TestClient 场景ABC + 应用冒烟 |
| 2 | **B1 功能使用频率采集**：api_monitor 补记 student_id、/monitoring/feature-usage（38项功能映射） | 应用效果 20 | ✅ | 权限4场景 |
| 3 | **A1-A3 跨学科数据层**：9条跨课程依赖注入（迁移脚本幂等）、courses 学科元数据表、/learning-path/courses、/learning-path/cross-discipline | 创新性 20 | ✅ | 依赖链跨3门课无环 |
| 4 | **C1 故障诊断实验**：3个故障模板、本地判定+AI诊断评估（后端诊断模式） | 需求分析 15 | ✅ | 真实LLM调用验证 |
| 5 | **C3 STM32 仿真器 AI 分析**（此前仅模拟电路有） | 创新性 20 | ✅ | Playwright |
| 6 | **B2 实验行为采集**：experiment_logs 表、上报/统计接口、三处前端埋点 | 应用效果 20 | ✅ | 权限4场景 |
| 7 | **B3/B4 试点报告**：/teacher/pilot-report 聚合5维度、教师端"试点数据分析"页面 | 应用效果 20 | ✅ | 教师200/学生403 |
| 8 | **A4 跨学科 DAG 可视化**：学习路径页折叠卡片、学科着色依赖图 | 创新性 20 | ✅ | Playwright |

### 测试验证记录

| 测试 | 范围 | 结果 | 脚本 |
|---|---|---|---|
| TestClient 回归 | 29 项断言（新功能+核心接口） | ✅ 29/29 | `backend/scripts/verify_aic_features.py` |
| 真实环境 HTTP | 33 项（学生端12+教师端6+新增15+前端） | ✅ 33/33 | `backend/scripts/verify_live.py` |
| 全路由冒烟 | 177 个路由 | ✅ 0 崩溃（55过+58合法4xx+64跳过） | `backend/scripts/verify_all_routes.py` |
| Playwright E2E | 4 项新功能浏览器测试 | ✅ 4/4 | `frontend/e2e/aic-features.spec.ts` |
| 前端构建 | TypeScript + vite build | ✅ 零错误 | — |

---

## 三、待办任务（按优先级）

### 🔴 P0 — 必须完成

| # | 任务 | 类型 | 计划时间 | 说明 |
|---|---|---|---|---|
| 1 | **组织小规模试点收集数据** | 操作 | 9/1-9/9 | 10-20名学生前后测+问卷（方案见差距分析5.1） |
| 2 | **团队信息确认** | 文档 | 待办 | 成员：马其瑞、孙雨瑶、居欣月；专业/年级/分工待确认 |
| 3 | **DeepSeek API Key 配置** | 配置 | 待办 | 配置后降级链 spark→deepseek 自动生效 |
| 4 | **按 AIC 八大部分重构技术方案文档** | 文档 | 8/27-9/8 | 整合系统开发说明书+补充项 |

### 🟡 P1 — 强烈建议

| # | 任务 | 类型 | 说明 |
|---|---|---|---|
| 5 | 创新点包装为"学科交叉三大新模式" | 文档 | ①AI个性化教学 ②AI虚拟实验实训 ③跨学科辅导 |
| 6 | 经济可行性分析 | 文档 | 套用差距分析 5.3 模板 |
| 7 | 学科专业界定 | 文档 | 计算机+电子信息新工科定位 |
| 8 | 实施计划时间线+资源保障 | 文档 | 甘特图+资源清单 |
| 9 | 参考文献列表 | 文档 | 15-20篇（BKT/学习科学/教育政策） |
| 10 | PPT 调整（25页→22-24页） | 演示 | 按差距分析第六部分 |

### 🟢 P2 — 增强项（代码已完成，文档侧跟进）

| # | 任务 | 说明 |
|---|---|---|
| 11 | 实验实训需求深度分析（写文档） | 电路故障实验/STM32仿真已具备，写入需求分析 |
| 12 | AI赋能必要性论证 | 传统LMS对比 |
| 13 | 演示视频录制 | 5-8分钟，突出跨学科链路+故障实验 |
| 14 | 总结展望结合政策趋势 | 教育数字化+AI趋势+三阶段推广 |

---

### ✅ 优化批次（8/13 深夜完成，commit `ebc8ec8`，13文件+898行）

| # | 优化项 | 说明 |
|---|---|---|
| 1 | **班级维度+班级对比** | users加class_id（seed_classes.py幂等迁移）、/teacher/classes、/teacher/class-comparison、试点报告按班级过滤（实验组vs对照组） |
| 2 | **试点报告Markdown导出** | pilot-report?format=markdown，前端"导出报告"按钮，参赛文档素材一键生成 |
| 3 | **STM32实验报告** | 实验实训卡片加"生成实验报告"（目标/元件/步骤/原理→下载.md） |
| 4 | **存量E2E测试修复** | frontend.spec.ts 8/8全过（登录placeholder、/profile→/personal路由、onboarding Modal拦截） |
| 5 | **LandingPage学科交叉展示** | 三学科卡片（计算机/电子信息/交叉）+跨学科链路图 |
| 6 | **README数据修正** | 数据库状态表与DB对齐（含新表courses/experiment_logs） |
| 7 | **A5跨学科综合实战项目** | 智能温控风扇/呼吸灯2个实战项目（任务勾选+完成上报cross_project） |

### 测试回归（优化批次后）

| 测试 | 结果 |
|---|---|
| TestClient（verify_aic_features.py） | ✅ 29/29 |
| Playwright AIC（aic-features.spec.ts） | ✅ 6/6 |
| Playwright 存量（frontend.spec.ts） | ✅ 8/8（首次全绿） |
| 前端构建 | ✅ TS零错误+build通过 |

## 三·补充、功能串联验证（与原有功能无冲突）

**全链路数据流验证 `verify_dataflow.py`（23/23）**：登录 → 学习行为上报 → 积分自动增长 → 测验 → 画像 knowledge_base/薄弱点实时更新 → 跨学科/DAG 路径生成 → 趋势分析 → 教师端试点报告/班级对比/薄弱点/预警 → 真实 LLM Agent 调用 → 前端 5173 代理

**Agent/LLM 专项验证 `verify_agent_llm.py`（23/23）**：反思循环迭代修正、Agent 缓存命中、JSON 解析 5 种乱格式、FailoverLLM 降级链 3 场景、防幻觉守卫（结构/代码/引用）

**Playwright**：AIC suite 6/6 + 存量 suite 8/8（分 suite 运行全绿；连跑偶发为 Windows 高负载时序问题，已加 retries=2）

**与原有功能联动关系**（已验证无冲突）：
- 学习记录/测验（原有）→ 画像/薄弱点（原有）→ 路径生成（原有+跨学科新模式叠加，兼容）
- 游戏化积分（原有）↔ 学习行为上报（原有，新增实验行为并行写入独立表）
- 教师端（原有 14 接口）↔ 新增（classes/class-comparison/pilot-report/feature-usage/experiment-stats）独立路由不冲突
- 学科切换（原有）→ 跨学科视图/实验实训（新增，按当前学科展示）
- api_monitor（原有）新增 student_id 字段（向后兼容，旧数据 NULL 不影响统计）

## 四、已发现问题的处理状态

| 问题 | 状态 |
|---|---|
| 多模型"5家实为1家"诚信风险 | ✅ 已修复（D1） |
| 防幻觉 self_correct/verify_citations 死代码 | ✅ 已挂接（D2：apply_guards规则守卫+低质量LLM自我纠错，接入反思循环与缓存流程） |
| 电路分析/知识图谱 LLM 故障 500 | ✅ 已修复（D6：电路降级引导提示、知识图谱降级本地图谱兜底16节点） |
| 无班级维度（教师端班级对比不可用） | ⏳ 待决策（新增模型或文档弱化） |
| PRODUCT.md 滞后（只写C语言） | ⏳ 待更新 |
| 原有 E2E 测试 frontend.spec.ts 首个用例失败 | ℹ️ 存量问题（登录页默认Tab与旧测试预期不符，Login.tsx 未改动） |

### ✅ 补漏项（8/13 晚完成，commit `83c6a19`）

| # | 任务 | 说明 |
|---|---|---|
| 9 | **D6 LLM 业务降级** | 电路分析失败→引导提示（degraded标记）；知识图谱超时→数据库prerequisites本地图谱兜底 |
| 10 | **D2 防幻觉挂接** | apply_guards（引用核查+结果合并）挂 cached_process/run_with_reflection；低质量输出触发 LLM 自我纠错 |
| 11 | **C4 STM32 实验任务化** | 学习中心新增"实验实训"Tab：7个实验（目标/元件/步骤勾选/原理）+完成度采集 |
| 12 | **C2 实验报告生成** | 故障实验报告：Markdown 预览/下载(.md)/复制 |

---

## 五、文件清单（本次改动）

**后端**（11 改 + 4 新）：
- 修改：`app/core/config.py`、`app/services/llm_factory.py`、`app/middleware/api_monitor.py`、`app/api/monitoring.py`、`app/api/learning_path.py`、`app/api/circuit_analysis.py`、`app/api/learning_data.py`、`app/api/teacher.py`、`app/algorithms/path_planning_dag.py`、`app/models/__init__.py`、`.env.example`
- 新增：`app/models/course.py`、`app/models/experiment.py`、`scripts/seed_cross_discipline.py`、`scripts/verify_aic_features.py`、`scripts/verify_live.py`、`scripts/verify_all_routes.py`

**前端**（5 改 + 3 新）：
- 修改：`services/api.ts`、`pages/LearningPath.tsx`、`pages/circuit/CircuitSimulatorPage.tsx`、`pages/circuit-simulator/store.ts`、`pages/circuit-simulator/ToolBar.tsx`、`pages/circuit-simulator/CircuitSimulator.tsx`
- 新增：`components/CrossDisciplineView.tsx`、`pages/circuit-simulator/FaultExperimentDialog.tsx`、`pages/circuit-simulator/fault-templates.ts`、`pages/teacher/PilotReport.tsx`、`e2e/aic-features.spec.ts`

**文档**：
- `README.md`（新增 AIC 功能章节）、`文档信息/AIC比赛项目完善计划书.md`、本文件

---

## 六、当前 Git 状态

- 分支：main，已与远程同步
- ✅ commit `39d6685`（首轮8项功能+文档，39文件）已推送
- ✅ commit `83c6a19`（补漏4项：D6/D2/C4/C2，6文件）已推送
- 工作区干净
