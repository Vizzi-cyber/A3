# A3 项目需求逐一检查报告

## 检查时间: 2026-04-25
## 检查人: Claude Code
## 项目状态: 后端运行正常 (端口 8000)，前端未启动 (缺 Node.js)

---

## 1. 学生画像构建与管理

### 需求要点
- 至少包含6个维度（知识基础、认知风格、易错点偏好等）
- 画像应动态更新
- 设计数据库/数据结构存储画像，高效读取更新
- 提供API接口

### 检查结果: ✅ 已实现

| 子项 | 状态 | 说明 |
|------|------|------|
| 六维画像 | ✅ | knowledge_base, cognitive_style, weak_areas/error_patterns, interest_areas/learning_goals, learning_tempo, practical_preferences |
| 动态更新 | ✅ | ProfilerAgent + /profile/{id}/analyze-conversation 接口，支持LLM分析对话自动更新画像 |
| 数据库存储 | ✅ | student_profiles 表，SQLite，student_id 为主键，各维度用 JSON 字段存储 |
| 独立可修改 | ✅ | /profile/{id}/update 支持按维度更新；/profile/{id}/initialize 支持重新初始化 |
| API接口 | ✅ | GET /profile/{id}, POST /profile/{id}/update, POST /profile/{id}/initialize, POST /profile/{id}/analyze-conversation, GET /profile/{id}/summary |

### 待完善
- **画像历史版本缺失**: 当前只有最新画像，没有历史版本追踪。建议增加 `profile_history` 表记录每次更新快照。
- **画像更新触发自动化不足**: 目前主要靠前端主动调用 analyze-conversation，建议在学习记录上报、测验完成后自动触发画像更新。

---

## 2. 多智能体协同系统

### 需求要点
- 智能体管理和调度
- 任务分配和调度
- 智能体之间通信协调

### 检查结果: ✅ 已实现

| 子项 | 状态 | 说明 |
|------|------|------|
| 智能体基类 | ✅ | BaseAgent (base.py) 定义统一接口：process, get_system_prompt, send_message, receive_message, run_with_reflection |
| 5个智能体 | ✅ | CourseDesignerAgent(主管), ProfilerAgent(画像), ResourceGeneratorAgent(资源), PathPlannerAgent(路径), TutorAgent(辅导) |
| 任务分解调度 | ✅ | CourseDesignerAgent._create_task_plan / _execute_sub_tasks 支持串行和并行执行 |
| 智能体通信 | ✅ | AgentMessage 消息格式，支持 message_type, priority, requires_response |
| LangGraph工作流 | ✅ | supervisor -> profiler/resource_generator/path_planner/tutor -> assembler -> END |
| 质量把控 | ✅ | BaseAgent.run_with_reflection 支持执行-评估-修正循环；HallucinationGuard 做输出校验 |

### 待完善
- **智能体状态持久化**: 当前智能体状态全部在内存中，服务重启后丢失。建议将智能体运行状态、消息队列持久化到数据库或Redis。
- **智能体间复杂协作**: 当前主要是 CourseDesigner 调用子智能体，子智能体之间缺少直接通信机制。

---

## 3. 个性化学习资源生成

### 需求要点
- 资源生成核心算法
- 多模态资源支持（文本、图像等）
- 资源推送，实时调整推送策略

### 检查结果: ⚠️ 部分实现

| 子项 | 状态 | 说明 |
|------|------|------|
| 文本资源生成 | ✅ | 讲解文档、练习题、思维导图、代码示例 |
| 图像资源生成 | ✅ | /image/generate 文生图接口（基于大模型） |
| OCR识图 | ✅ | /ocr/recognize 支持图片文字识别 |
| 资源生成智能体 | ✅ | ResourceGeneratorAgent 支持 generate_document/questions/code_examples/mindmap/match_resources |
| 内容库优先匹配 | ✅ | content_library.get_content 优先命中，减少LLM调用 |
| 代码执行 | ✅ | /resource/code/execute 支持 Python（AST安全分析）和 C（gcc编译） |
| 视频生成 | ❌ | 未实现 |
| 动画生成 | ❌ | 未实现 |
| 资源推送 | ⚠️ | Dashboard有推荐资源，但未根据学生画像实时动态调整推送策略 |

### 待完善
- **视频/动画资源**: 需求明确要求支持视频、动画，当前缺失。建议接入视频生成API或集成动画库（如Manim、Remotion）。
- **资源推送策略自动化**: 当前推荐资源主要从收藏和兴趣推导，缺少基于实时学习效果的动态权重调整。
- **资源个性化深度不足**: 生成的资源虽支持 cognitive_style 参数，但实际内容库匹配时未充分利用画像差异。

---

## 4. 学习路径规划与调整

### 需求要点
- 个性化学习路径生成
- 根据进度、成绩动态调整
- 路径推送到前端

### 检查结果: ✅ 已实现

| 子项 | 状态 | 说明 |
|------|------|------|
| 路径生成 | ✅ | PathPlannerAgent + /learning-path/generate，支持LLM生成和DAG算法双保险 |
| DAG路径规划 | ✅ | DAGPathPlanner 算法，支持 build_graph, plan_path, detect_cycles, _get_dependency_chain |
| 路径调整 | ✅ | /learning-path/{id}/adjust + /learning-path/dag/adjust |
| 动态路径展示 | ✅ | /learning-path/{id}/current 基于数据库学习记录实时计算节点状态（completed/in-progress/pending/locked） |
| 路径推送 | ✅ | API返回完整路径节点，前端 LearningPath.tsx 可视化展示 |

### 待完善
- **自动化调整触发**: 当前路径调整依赖学生手动反馈或前端调用，建议在学习效果评估检测到掌握度下降时自动触发路径重规划。
- **学习路径历史版本**: 缺少路径变更历史记录。

---

## 5. 智能辅导与答疑

### 需求要点
- 即时答疑，自动生成文本解答、图解说明
- 记录问题和回答，用于后续分析

### 检查结果: ⚠️ 部分实现

| 子项 | 状态 | 说明 |
|------|------|------|
| 即时答疑 | ✅ | /tutor/ask + TutorAgent 苏格拉底式问答 |
| WebSocket流式 | ✅ | /tutor/ws/{session_id} 支持真实LLM流式输出 |
| 多模型切换 | ✅ | 支持 bigmodel/deepseek/openai/spark |
| 图文输入 | ✅ | TutorRequest.question 支持 VisionContentItem[] 数组 |
| 安全过滤 | ✅ | SafetyGuard.check_input / check_output |
| 会话历史 | ✅ | TutorAgent.session_histories 内存维护，支持 get_session_history |
| 图解说明 | ⚠️ | 支持图片输入分析，但未实现"自动生成概念图解"功能 |
| 问答持久化 | ✅ | **TutorQAModel 表 + /tutor/ask 持久化，支持 /tutor/qa-history/{student_id} 查询和 /tutor/qa-feedback/{qa_id} 反馈** |

### 待完善
- **自动生成图解**: 答疑系统目前主要是文本回复，可结合 /image/generate 为复杂概念自动生成示意图。

---

## 6. 学习效果评估与反馈

### 需求要点
- 实时学习数据收集
- 学习效果分析（大模型分析能力）
- 动态调整学习计划和资源推送

### 检查结果: ⚠️ 部分实现

| 子项 | 状态 | 说明 |
|------|------|------|
| 实时数据收集 | ✅ | learning_records, quiz_results 表记录学习行为和测验情况 |
| 效果评估算法 | ✅ | LearningEffectEvaluator：正确率、掌握度、提升速率、薄弱点集中度、预测下次得分、潜在失分点 |
| 趋势分析算法 | ✅ | MultiFactorTrendAnalyzer：掌握度趋势、学习速度、时间效率、薄弱点优先级、稳定性、3天预测 |
| 干预策略生成 | ✅ | 自动生成干预策略（基础巩固、掌握度提升、趋势干预、薄弱点突破） |
| 数据持久化 | ✅ | TrendDataModel 每日持久化趋势数据 |
| 动态调整闭环 | ⚠️ | 评估结果生成干预建议，但未自动化触发资源重推送或路径调整 |
| 大模型参与分析 | ⚠️ | 当前评估主要靠规则算法，未充分调用LLM做深度分析 |

### 待完善
- **评估->调整自动化闭环**: 建议在每日/每次测验后，自动调用路径调整和资源推荐API，实现"检测到薄弱 -> 自动重推资源 -> 调整路径"的闭环。
- **LLM深度评估**: 可将学习记录和测验结果输入LLM，生成更自然语言化的评估报告和学习建议。

---

## 7. 安全与内容过滤

### 需求要点
- 内容安全与防幻觉机制
- 安全验证与权限管理

### 检查结果: ⚠️ 部分实现

| 子项 | 状态 | 说明 |
|------|------|------|
| 敏感词过滤 | ✅ | SafetyGuard 基础敏感词库（中文关键词），支持输入/输出双向检查 |
| Prompt安全约束 | ✅ | SafetyGuard.sanitize_prompt 自动追加安全约束到prompt末尾 |
| JSON结构校验 | ✅ | HallucinationGuard.verify_json_schema |
| 代码语法校验 | ✅ | HallucinationGuard.verify_code_output (Python compile检查) |
| 引用溯源检查 | ✅ | HallucinationGuard.verify_citations |
| 自我纠错接口 | ✅ | HallucinationGuard.self_correct 预留LLM二次校验接口 |
| JWT认证 | ✅ | /auth/login 返回 JWT Token，/auth/me 获取用户信息 |
| 权限控制 | ⚠️ | 有 role 字段（student/teacher/admin），但各API未按角色做权限区分 |
| 密码强度校验 | ✅ | `UserRegisterRequest` 增加 `field_validator`：min_length=8，必须包含至少1个字母和1个数字 |

### 待完善
- **角色权限区分**: 当前所有受保护API统一用 require_auth，未区分 student/teacher/admin 可访问范围。
- **角色权限区分**: 当前所有受保护API统一用 require_auth，未区分 student/teacher/admin 可访问范围。
- **内容审核API**: 当前敏感词库是硬编码列表，建议生产环境接入专业内容审核API。

---

## 8. API设计与数据接口

### 需求要点
- RESTful API：学生画像、资源生成、学习路径、答疑辅导、学习效果评估

### 检查结果: ✅ 已实现

| 接口类别 | 状态 | 说明 |
|----------|------|------|
| 学生画像接口 | ✅ | GET/POST /profile/* |
| 资源生成接口 | ✅ | POST /resource/generate, /resource/document/generate, /resource/questions/generate, /resource/mindmap/generate, /resource/code/generate |
| 学习路径接口 | ✅ | POST /learning-path/generate, GET /learning-path/{id}/current, POST /learning-path/{id}/adjust, POST /learning-path/dag/* |
| 答疑辅导接口 | ✅ | POST /tutor/ask, WS /tutor/ws/{session_id}, GET /tutor/session/{session_id}/history |
| 学习效果评估接口 | ✅ | POST /trend/analyze, GET /trend/{id}/report, GET /trend/{id}/history |
| Dashboard聚合接口 | ✅ | GET /dashboard/{id}/summary |
| 游戏化接口 | ✅ | GET /gamification/{id}/points, /gamification/{id}/achievements, /gamification/{id}/tasks |
| 学习日志接口 | ✅ | GET /log-reflection/{id}/logs, GET /log-reflection/{id}/reflections, POST /log-reflection/* |
| 知识点接口 | ✅ | GET /knowledge/list, /knowledge/{id}, /knowledge/search |
| 系统监控接口 | ✅ | GET /monitoring/api-stats, /monitoring/llm-stats, /monitoring/health |
| 认证接口 | ✅ | POST /auth/register, /auth/login, GET /auth/me |
| 收藏夹接口 | ✅ | GET/POST/DELETE /favorites/* |
| 文生图/OCR接口 | ✅ | POST /image/generate, /ocr/recognize |

| API限流 | ✅ | `RateLimiter` 中间件：登录/注册 10次/分钟，LLM接口 20次/分钟，其他 60次/分钟，返回 429 + Retry-After 头 |

### 待完善
- **API版本管理**: 当前仅 v1，建议规划版本升级策略。

---

## 9. 系统监控与日志管理

### 需求要点
- 实时监控系统性能
- 记录关键操作和异常信息

### 检查结果: ⚠️ 部分实现

| 子项 | 状态 | 说明 |
|------|------|------|
| API性能监控 | ✅ | ApiMonitorModel 表，/monitoring/api-stats 接口 |
| LLM调用监控 | ✅ | LlmCallModel 表，/monitoring/llm-stats 接口 |
| 系统健康监控 | ✅ | SystemHealthModel 表，/monitoring/health 接口 |
| 日志轮转 | ✅ | RotatingFileHandler (10MB, backupCount=5) |
| 自动监控采集 | ❌ | 没有定时任务或中间件自动记录系统健康数据到 SystemHealthModel |
| 异常告警 | ❌ | 没有告警机制（如邮件、Webhook） |

### 待完善
- **自动健康采集**: 建议增加后台定时任务（如 APScheduler）自动采集 CPU/内存/磁盘并写入数据库。
- **异常告警**: 建议增加告警规则（如 API 错误率>5%、LLM调用连续失败等），支持 Webhook/邮件通知。
- **日志结构化**: 当前日志是文本格式，建议增加 JSON 结构化日志便于后续分析。

---

## 10. 游戏化学习与任务驱动

### 需求要点
- 学习进度与成就系统
- 挑战任务
- 社交互动（学生间互动、分享、讨论、合作学习）

### 检查结果: ⚠️ 部分实现

| 子项 | 状态 | 说明 |
|------|------|------|
| 积分系统 | ✅ | PointsModel + /gamification/{id}/points |
| 成就徽章 | ✅ | AchievementModel + 前端徽章展示 |
| 任务系统 | ✅ | TaskModel 支持 daily/weekly/challenge，含进度和完成状态 |
| 排行榜 | ✅ | LeaderboardModel + /gamification/leaderboard/{period} |
| 经验值/等级 | ⚠️ | 前端 Dashboard 显示 Lv.5 和经验条，但后端缺少等级计算逻辑 |
| 挑战任务 | ⚠️ | 前端有 challenges 静态数据，后端 TaskModel 支持 challenge 类型，但缺少动态生成挑战任务的逻辑 |
| **社交互动** | ❌ | **完全缺失** — 没有讨论区、学习小组、成果分享、合作学习功能 |

### 待完善
- **社交互动模块**: 这是本需求的核心缺失项。建议增加：
  - 讨论区/论坛（Topic + Reply 模型）
  - 学习小组（Group + GroupMember 模型）
  - 成果分享（Share + Like/Comment 模型）
  - 同伴学习匹配（基于画像匹配学习伙伴）
- **等级系统后端化**: 将等级和经验值计算逻辑迁移到后端，增加经验值获取规则（完成任务+XP、连续打卡加成等）。
- **动态挑战生成**: 根据学生学习状态自动生成个性化挑战（如"本周攻克指针"、"连续3天每日一题"）。

---

## 11. 自我反思与学习日志

### 需求要点
- 学习日志记录学习路径、难点、任务
- 自我反思模块，引导性问题

### 检查结果: ⚠️ 部分实现

| 子项 | 状态 | 说明 |
|------|------|------|
| 学习日志 | ✅ | LearningLogModel 记录每日时长、知识点数、测验数、平均分、错误、路径进度、时间线 |
| 反思记录 | ✅ | ReflectionModel 支持 content, mood, tags, ai_feedback |
| 复盘聚合 | ✅ | /log-reflection/{id}/review 聚合最近7天日志和反思 |
| 康奈尔笔记 | ✅ | 前端支持，保存到 reflections 表（tag=cornell） |
| 费曼练习 | ✅ | 前端支持，保存到 reflections 表（tag=feynman） |
| 引导式反思 | ❌ | 只有自由输入框，缺少固定引导问题（如"今天学到了什么？""哪些地方还需要提高？"） |
| AI反馈反思 | ⚠️ | ReflectionModel 有 ai_feedback 字段，但当前未调用LLM生成反馈 |

### 待完善
- **引导式反思**: 增加结构化反思模板，定期推送引导问题。
- **AI反馈**: 学生提交反思后，调用 TutorAgent 生成针对性的鼓励和建议，写入 ai_feedback。
- **反思与画像联动**: 将反思中的情绪、自评关键词提取后更新到学生画像（如学习信心度、当前压力状态）。

---

## 总体评估

| 需求模块 | 完成度 | 评级 |
|----------|--------|------|
| 1. 学生画像构建与管理 | 90% | A |
| 2. 多智能体协同系统 | 90% | A |
| 3. 个性化学习资源生成 | 75% | B+ |
| 4. 学习路径规划与调整 | 90% | A |
| 5. 智能辅导与答疑 | 90% | A |
| 6. 学习效果评估与反馈 | 80% | B+ |
| 7. 安全与内容过滤 | 85% | B+ |
| 8. API设计与数据接口 | 95% | A |
| 9. 系统监控与日志管理 | 70% | B |
| 10. 游戏化学习与任务驱动 | 65% | B |
| 11. 自我反思与学习日志 | 80% | B+ |

**综合评级: B+**

---

## 关键缺失项（必须补充）

按优先级排序：

1. **社交互动模块** (P0): 需求10明确要求，当前完全缺失。需要数据库表 + API + 前端页面。
2. **视频/动画资源** (P1): 需求3要求多模态，当前缺失视频和动画生成能力。
3. **引导式反思** (P2): 需求11明确要求固定问题引导。
4. **视频/动画资源** (P1): 需求3要求多模态，当前缺失视频和动画。
5. **API限流** (P1): 防滥用基础能力。
6. **引导式反思** (P2): 需求11明确要求固定问题引导。
7. **自动健康采集** (P2): 需求9要求实时监控。
8. **画像历史版本** (P2): 便于追踪学生成长轨迹。
9. **等级系统后端化** (P2): 游戏化完整性。
10. **评估->调整自动化闭环** (P2): 需求6的核心目标。
