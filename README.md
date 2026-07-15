# LearnLab - 个性化学习平台

基于大模型的个性化资源生成与学习多智能体系统，第十五届中国软件杯大赛A3赛题作品。

---

## 目录

- [项目背景](#项目背景)
- [项目概述](#项目概述)
- [核心功能](#核心功能)
- [核心创新点](#核心创新点)
- [总结与展望](#总结与展望)
- [技术架构](#技术架构)
- [多智能体系统（12个Agent）](#多智能体系统12个agent)
- [智能体基类特色](#智能体基类特色)
- [防幻觉机制](#防幻觉机制)
- [核心算法详解](#核心算法详解)
- [C语言内容库](#c语言内容库)
- [电路仿真系统](#电路仿真系统)
- [后端模块详解](#后端模块详解)
- [前端模块详解](#前端模块详解)
- [数据库设计](#数据库设计)
- [API接口列表](#api接口列表)
- [前端页面结构](#前端页面结构)
- [快速启动](#快速启动)
- [Docker部署](#docker部署)
- [E2E测试](#e2e测试)
- [开发指南](#开发指南)
- [系统验证](#系统验证)

---

## 项目背景

在高等教育学习过程中，学生普遍面临学习资源繁杂无序、难以精准匹配自身需求且缺乏智能化、个性化学习指导的核心问题。不同专业、不同学历水平的学生在面对海量课程资料、学术文献、学习辅助工具时，难以快速筛选出契合自身学习进度和能力的资源；同时课堂集体讲授模式无法兼顾每位学生的学习节奏与特点，导致学生在知识掌握和能力提升上存在明显差距。传统学习模式及基础的智能辅助系统，因缺乏多模态生成、多智能体协同等前沿AI技术的支撑，难以满足现代高等教育对培养创新型、个性化人才的要求。

**LearnLab** 正是为解决这一问题而生——通过12个AI智能体协作，覆盖「预习—听课—练习—答疑—纠错—实战—复盘」完整学习闭环，实现从知识获取到能力内化的全链路智能化。

---

## 项目概述

覆盖「预习 - 听课 - 练习 - 答疑 - 纠错 - 实战 - 复盘」完整学习闭环

### 产品定位

第十五届中国软件杯 A3 赛题作品，定位为"基于大模型的个性化资源生成与学习多智能体系统"。

### 核心学习闭环

```
构建画像 → 规划路径 → 生成资源 → 智能辅导 → 效果评估 → 动态调整
    ↑                                                          │
    └──────────────────── 持续优化 ←────────────────────────────┘
```

### 六维学习画像

知识基础、认知风格、薄弱环节、兴趣领域、学习习惯、情感状态

### 兼容大模型

讯飞星火、DeepSeek、OpenAI GPT-4、智谱 AI GLM-4、小米 MiMo（一键切换，统一接口封装）

### 核心特性

- **12个AI智能体协作**：LangGraph驱动的多智能体工作流，覆盖学习全场景
- **个性化学习路径**：基于DAG的知识图谱驱动，贝叶斯知识追踪，自适应调整
- **苏格拉底式辅导**：多模态交互（文字+图片），WebSocket实时流式输出
- **游戏化激励**：知识树成长、学习挑战、六维排行榜、成就系统
- **5种大模型支持**：智谱GLM / 讯飞星火 / DeepSeek / OpenAI / 小米MiMo，统一接口一键切换
- **多层防幻觉机制**：输入过滤→Prompt加固→输出校验→代码语法检查→引用溯源→LLM自我纠错
- **前端电路仿真**：浏览器端完整MNA电路求解（并查集+高斯消元），AI分析集成
- **教师端学情分析**：班级学情、薄弱知识点、学生排名、报告导出

---

## 核心功能

### 学习仪表盘

本周学习进度卡片、课程完成进度、月度打卡日历
数据统计：学习时长、连续打卡、掌握知识点、待办任务
每日练习模块：实时刷题，即时检验基础语法
全局学情概览，快速定位待完成学习任务

### AI 智能辅导

RAG 本地知识库问答，不直接给答案、引导独立思考
学情雷达图：知识基础 / 专注度 / 薄弱点可视化
薄弱知识点自动识别，配套举一反三、薄弱诊断工具
专属对话会话管理，留存答疑历史

### 个性化学习路径

基于艾宾浩斯遗忘曲线生成复习提醒
分阶段 C 语言学习大纲（16 个学习节点）
AI 自动生成薄弱点定向学习资源
可视化学习进度，智能调整学习难度

### 学习中心

分章节结构化图文讲义（C 语言完整课程目录）
配套辅助 AI 助手，边看课边提问
资源工具：OCR 识图、一键生成 PPT、标记课程完成状态

### 知识冒险

闯关挑战体系、积分等级成长系统
知识树可视化掌握程度，7 天学习趋势分析
学情 AI 评语，自动预警下滑学习状态
排行榜、挑战关卡提升学习趣味性

### 错误诊断系统

C 语言代码粘贴自动捕获语法 / 逻辑 / 思维错误
编译器报错解析、思维溯源分析
错题诊断记录存档，建立个人错题库

### 项目协作学习

内置分级 C 语言实战项目（入门 / 基础 / 中等 / 进阶 / 挑战）
自定义项目、AI 自动任务拆解、智能组队匹配
团队协作进度监控、代码提交评估，贴合课程设计 / 软件竞赛

### 个人空间

累计学习时长、专注度趋势、每日时长折线图
完整学习历史记录、笔记 / 收藏 / 成长历程管理
番茄专注钟、学习画像深度分析

### 知识库

分录结构化管理 C 语言笔记（基础语法 / 指针 / 数组 / 结构体）
双向链接、图谱关联知识点，快速检索语法笔记
支持新建、分类、归档个人学习总结

---

## 核心创新点

### AI 苏格拉底式引导教学

区别普通问答，引导思考而非直接输出答案

### 遗忘曲线个性化复习机制

自动推送需要复习的薄弱知识点

### 全链路代码错误智能诊断

从语法到底层思维溯源定位错题

### 学情多维数据可视化

仪表盘、雷达图、趋势曲线、知识树多维度展示

### 游戏化 + 项目制双实战模式

轻量化闯关 + 团队工程项目结合

### RAG 本地知识库课程体系

讲义、习题、笔记打通联动检索

### 一站式闭环

从预习听课、AI 答疑、刷题纠错、项目实战到数据复盘全覆盖

### 多智能体协同架构（LangGraph星型拓扑）

基于 LangGraph 的 `StateGraph` 构建星型拓扑多智能体系统：

```
                    ┌─────────────┐
                    │ Supervisor  │ ← 课程设计师（总控调度）
                    │  (Router)   │
                    └──────┬──────┘
           ┌───────┬───────┼───────┬───────┐
           ▼       ▼       ▼       ▼       ▼
       ┌──────┐┌──────┐┌──────┐┌──────┐┌──────┐
       │Profil││PathPl││Resour││Tutor ││Assembler│
       │  er  ││anner ││ceGen ││      ││  (汇总) │
       └──────┘└──────┘└──────┘└──────┘└──────┘
```

- **动态条件路由**：supervisor 根据任务类型（画像/路径/资源/辅导）动态分配给对应子智能体
- **轮询式协作**：子智能体执行完后回到supervisor，支持多轮迭代
- **并行fan-out**：V2路由支持依赖检查和并行执行
- **延迟初始化**：lifespan中延迟创建，避免阻塞应用启动

### 自适应DAG学习路径规划（ADPP算法）

融合多种经典算法的自适应路径规划：

```
知识点DAG → 拓扑排序 → 关键度计算 → 贝叶斯掌握度预测
    → 多因子学习成本 → 加权拓扑排序 → 自适应阶段划分 → 个性化路径
```

**核心公式**：
```
学习成本 = 基础时长 × 难度系数(0.7~1.8) × 掌握度折扣(最低15%)
         × 薄弱点加权(+25%) × 速度因子(0.75~1.35) × 关键度因子(+15%)
```

**动态调整策略**：
- 得分 < 50：插入"紧急回炉"阶段，后续延长30%
- 得分 50-70：插入强化练习阶段
- 得分 ≥ 90 且趋势上升：允许加速，后续缩短20%
- 预警状态：全局增加20%学习时间

### 智能体反思循环（Self-Reflection Loop）

`BaseAgent.run_with_reflection()` 实现 **执行-评估-修正** 循环：

```
┌─────────────────────────────────────────────┐
│  执行 → 质量评估 → 达标? → 输出最佳结果      │
│    ↑         │                               │
│    │        否                               │
│    │         │                               │
│    └── 注入反馈，重新执行（最多3次）           │
└─────────────────────────────────────────────┘
```

- **双重评估**：规则评估（快速fallback）+ LLM自评（准确性/完整性/可用性）
- **最佳结果保留**：即使后续迭代失败，也能返回最优解
- **超时控制**：每次迭代60秒超时，避免无限循环

### 多层防幻觉机制（7道防线）

```
用户输入 → ①敏感词检测 → ②Prompt安全加固 → ③LLM生成
    → ④JSON/代码校验 → ⑤引用溯源检查 → ⑥LLM自我纠错 → 输出过滤
```

| 防线 | 机制 | 实现 |
|------|------|------|
| ① 输入过滤 | `SafetyGuard.check_input()` | 预编译正则匹配15个敏感词 |
| ② Prompt加固 | `SafetyGuard.sanitize_prompt()` | 自动追加安全约束，未成年人额外保护 |
| ③ 输出过滤 | `SafetyGuard.check_output()` | 同样敏感词检测 |
| ④ 结构校验 | `HallucinationGuard.verify_json_schema()` | JSON必要字段验证 |
| ⑤ 代码校验 | `HallucinationGuard.verify_code_output()` | Python AST编译检查，精确到行号 |
| ⑥ 引用溯源 | `HallucinationGuard.verify_citations()` | 6种正则模式检测引用标注 |
| ⑦ 自我纠错 | `HallucinationGuard.self_correct()` | LLM以"事实核查专家"角色自我修正（温度0.2） |

### 前端电路仿真（浏览器端MNA求解）

在浏览器端实现完整的电路仿真，无需后端计算：

**核心技术**：
- **并查集节点合并**：带路径压缩和按秩合并，自动处理等电位节点
- **MNA方程组构建**：电阻→导纳矩阵，电压源→额外方程行，电流源→RHS向量
- **高斯消元求解**：带部分主元选取，奇异矩阵检测
- **结果提取**：节点电压、支路电流、功率耗散

**AI集成**：将网表+仿真结果发送给后端，获取AI电路分析、元件作用解释、优化建议

### 数据库驱动的结构化内容库

- **四维内容结构**：每个知识点包含文档(document)、代码示例(code_example)、练习题(questions)、思维导图(mindmap)
- **数据库优先策略**：动态读取，支持热更新
- **防SQL注入**：LIKE通配符转义处理
- **延迟加载**：fallback数据按需加载，避免启动内存占用

### 游戏化学习体系

- **知识树成长**：D3.js SVG动画，5种状态（种子→成长→开花→结果→传说）
- **经验等级系统**：10级（初学者→传奇），后端统一配置，前端统一计算
- **六维排行榜**：积分/连续/掌握/测验/AI协作/进步 × 日/周/月
- **学习挑战**：游戏化任务地图，"数据结构大陆"世界观，分区域（数组村庄、栈峡谷、树之森林等）

### UI/UX设计亮点

- **GSAP + ScrollTrigger**：滚动触发动画（标题渐入、卡片错落入场、3D tilt卡片效果）
- **浏览器Mockup组件**：落地页模拟真实应用界面
- **浮动通知卡片**：AI辅导消息、成就通知带CSS动画
- **响应式设计**：移动端菜单、自适应栅格
- **环境噪声纹理**：noise-overlay和渐变网格背景

---

## 总结与展望

**LearnLab** 是一套完整的 AI 个性化学习解决方案，从项目背景出发精准切中高教学习痛点，通过 12 个 AI 智能体的协同工作、前沿大模型技术的灵活接入和丰富的功能矩阵，构建了一个覆盖学习全链路的智能化平台。

### 已实现

- ✅ 12 个 AI 智能体完整实现，LangGraph 工作流编排
- ✅ 28 个前端页面 + 36 个后端 API 模块（167+ 接口）
- ✅ 学生端 + 教师端双角色完整功能
- ✅ 浏览器端电路仿真（MNA 求解器）
- ✅ 39 个 E2E 测试用例全部通过
- ✅ Docker 一键部署

### 展望

- **多学科扩展**：从 C 语言和电路分析扩展到更多学科（Python、数据结构、算法等）
- **移动端适配**：React Native 或小程序端，实现随时随地学习
- **学习社区**：学生间互助问答、笔记共享、项目组队社区
- **更深度个性化**：引入强化学习，根据学生实时反馈动态调整教学策略
- **离线模式**：PWA 支持，部分核心功能离线可用

---

## 技术亮点总结

| 维度 | 亮点 | 技术实现 |
|------|------|----------|
| **智能体架构** | 12个智能体协作，星型拓扑 | LangGraph StateGraph + 条件路由 |
| **路径规划** | 自适应DAG，6因子成本模型 | 关键路径法 + BKT + 加权拓扑排序 |
| **质量保障** | 智能体反思循环 | 执行-评估-修正，LLM自评+规则评估 |
| **安全防护** | 6道防幻觉防线 | 输入过滤→Prompt加固→输出校验→语法检查→引用溯源→自我纠错 |
| **电路仿真** | 浏览器端完整MNA求解 | 并查集 + 高斯消元 + AI分析集成 |
| **内容体系** | 16个C语言知识点，四维内容 | 数据库驱动，文档+代码+练习+导图 |
| **游戏化** | 知识树+等级+挑战+排行榜 | D3.js动画 + 10级系统 + 6维排名 |
| **多模型** | 5种LLM一键切换 | LLMFactory统一接口 + 指数退避重试 |
| **教师端** | 学情分析+班级对比+报告导出 | 雷达图 + 排名表 + PDF/Excel导出 |
| **工程化** | 167+API，39个E2E测试 | FastAPI + Playwright + Docker部署 |

---

## 技术架构

### 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                    前端 (React + TypeScript)                   │
├─────────────────────────────────────────────────────────────┤
│  React 18 + TypeScript + Ant Design 5 + Zustand + TailwindCSS  │
│  Vite (构建) + Recharts (可视化) + GSAP (动画) + D3.js (图谱)   │
│  Monaco Editor (代码) + Playwright (E2E测试)                     │
└─────────────────────────────────────────────────────────────┘
                              │
                          REST API / WebSocket
                              │
┌─────────────────────────────────────────────────────────────┐
│              后端 (Python + FastAPI)                           │
├─────────────────────────────────────────────────────────────┤
│  FastAPI + LangGraph (多智能体编排) + SQLAlchemy + SQLite        │
│  12个智能体 + 36个API路由模块 + 23个数据模型 + 4个学习算法         │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    大模型接入层                                │
├─────────────────────────────────────────────────────────────┤
│  LLMFactory统一接口: 智谱GLM / 讯飞星火 / DeepSeek / OpenAI / MiMo │
│  火山引擎文生图 / OCR识图 / PPT自动生成                           │
└─────────────────────────────────────────────────────────────┘
```

### 后端技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| **FastAPI** | >=0.115.0 | 高性能异步Web框架，36个API路由模块 |
| **LangGraph** | 0.2~0.4 | 多智能体工作流编排，状态图驱动 |
| **LangChain** | 0.2~0.4 | LLM应用开发框架 |
| **SQLAlchemy** | >=2.0.25 | ORM，支持SQLite/PostgreSQL |
| **Python** | 3.9+ (推荐3.11) | 后端语言 |
| **uvicorn** | >=0.27.0 | ASGI服务器，支持热重载 |
| **python-pptx** | >=0.6.23 | AI驱动的PPT自动生成 |
| **python-jose** | >=3.3.0 | JWT令牌管理 |
| **passlib** | >=1.7.4 | 密码哈希处理 |
| **httpx** | >=0.26.0 | 异步HTTP客户端 |
| **websockets** | >=12.0 | WebSocket实时通信 |
| **aiosqlite** | >=0.19.0 | 异步SQLite驱动 |

### 前端技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| **React 18 + TypeScript** | ^18.2.0 | UI框架，类型安全 |
| **Ant Design 5** | ^5.12.0 | 企业级组件库 |
| **Zustand** | ^4.4.0 | 轻量级状态管理（持久化到localStorage） |
| **Recharts** | ^2.10.0 | 数据可视化（折线图/柱状图/雷达图/饼图） |
| **D3.js** | ^7.9.0 | 知识图谱/思维导图/知识树/电路模拟可视化 |
| **GSAP** | ^3.15.0 | 高性能动画引擎（ScrollTrigger/SplitText） |
| **TailwindCSS** | ^3.3.0 | 原子化样式 |
| **Vite** | ^5.0.0 | 构建工具，代码分割，快速开发 |
| **Monaco Editor** | ^4.7.0 | 代码编辑器（C/Python语法高亮） |
| **React Router** | ^6.21.0 | 路由管理（懒加载） |
| **Axios** | ^1.6.0 | HTTP客户端（Token拦截器、请求去重） |
| **React Markdown** | ^9.0.0 | Markdown渲染（GFM/数学公式/代码高亮） |
| **KaTeX** | ^0.17.0 | 数学公式渲染 |
| **Playwright** | ^1.59.1 | E2E测试（39个测试用例） |
| **Sentry** | ^10.50.0 | 错误监控 |

---

## 多智能体系统（12个Agent）

### 智能体总览

| # | 智能体 | 类名 | 分类 | 职责 |
|---|--------|------|------|------|
| 1 | **课程设计师** | `CourseDesignerAgent` | 核心 | 系统中枢，任务分解、流程编排、质量把控 |
| 2 | **画像师** | `ProfilerAgent` | 核心 | 分析学生数据，构建6维画像 |
| 3 | **路径规划师** | `PathPlannerAgent` | 核心 | 基于DAG的个性化学习路径规划 |
| 4 | **资源生成师** | `ResourceGeneratorAgent` | 核心 | 生成文档/题目/思维导图/代码 |
| 5 | **辅导助手** | `TutorAgent` | 核心 | 苏格拉底式问答，学习状态感知 |
| 6 | **知识图谱构建师** | `KnowledgeGraphBuilderAgent` | 知识 | 构建结构化知识图谱 |
| 7 | **思维溯源师** | `MisconceptionTracerAgent` | 知识 | 反向推导学生错误原因 |
| 8 | **错误捕捉师** | `ErrorCatcherAgent` | 代码 | 抓取代码中的语法/逻辑错误 |
| 9 | **项目拆解师** | `ProjectDecomposerAgent` | 协作 | 将C语言项目拆解为任务树 |
| 10 | **角色匹配师** | `RoleMatcherAgent` | 协作 | 根据能力画像匹配最优组队 |
| 11 | **协作督导** | `CollaborationSupervisionAgent` | 协作 | 监控团队协作，检测阻塞/冲突 |
| 12 | **成果评估师** | `ResultEvaluatorAgent` | 协作 | 多维度评估项目成果 |

### 核心智能体（LangGraph驱动）

| 智能体 | 职责 | 特色功能 |
|--------|------|----------|
| **课程设计师** | 系统中枢，任务分解、流程编排、质量把控 | 协调其他智能体工作 |
| **画像师** | 分析学生数据，构建6维学生画像 | 知识基础/认知风格/薄弱环节/兴趣/习惯/情感 |
| **路径规划师** | 基于DAG的个性化学习路径规划 | 受知识图谱约束，防止幻觉 |
| **资源生成师** | 生成多模态学习资源 | 文档/题目/思维导图/代码，受知识图谱约束 |
| **辅导助手** | 苏格拉底式问答 | 学习状态自动检测（挫败/困惑/自信） |

### 知识体系智能体

| 智能体 | 职责 | 特色功能 |
|--------|------|----------|
| **知识图谱构建师** | 从知识点构建结构化知识图谱 | 约束路径规划和资源生成，防止幻觉 |
| **思维溯源师** | 反向推导学生错误原因 | 归类：概念混淆/逻辑缺失/语法惯性/零基础盲区 |

### 代码分析智能体

| 智能体 | 职责 | 特色功能 |
|--------|------|----------|
| **错误捕捉师** | 抓取代码中的错误 | 语法错误、逻辑错误、思维误区分析 |

### 团队协作智能体

| 智能体 | 职责 | 特色功能 |
|--------|------|----------|
| **项目拆解师** | 将C语言项目拆解为可执行的任务树 | 内置经典项目库 |
| **角色匹配师** | 根据学生能力画像匹配最优组队 | 架构师/开发者/测试员/UI开发/文档员 |
| **协作督导** | 监控团队协作，检测阻塞/冲突 | 促进知识共享，生成每日协作报告 |
| **成果评估师** | 多维度评估项目成果 | 代码质量/协作效果/学习收获 |

### Agent协作架构

```
┌─────────────────────────────────────────────────────────────┐
│                    12个智能体协作架构                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  核心5智能体（LangGraph驱动）：                                │
│  ┌─────────────────┐                                        │
│  │ CourseDesigner   │ ← 任务入口，总控调度                    │
│  │   ├→ Profiler    │ ← 先分析学生画像                       │
│  │   ├→ PathPlanner │ ← 再规划学习路径                       │
│  │   ├→ ResourceGen │ ← 然后生成资源                         │
│  │   └→ Tutor       │ ← 最后辅导答疑                         │
│  └─────────────────┘                                        │
│                                                             │
│  团队协作4智能体（独立模块）：                                  │
│  ┌─────────────────┐                                        │
│  │ ProjectDecomposer│ ← 拆解项目任务                         │
│  │ RoleMatcher     │ ← 匹配团队角色                         │
│  │ Collaboration   │ ← 监控协作过程                         │
│  │ ResultEvaluator │ ← 评估最终成果                         │
│  └─────────────────┘                                        │
│                                                             │
│  知识体系2智能体：                                            │
│  ┌─────────────────┐                                        │
│  │ KG Builder      │ ← 构建知识图谱                         │
│  │ Misconception   │ ← 追溯思维误区                         │
│  └─────────────────┘                                        │
│                                                             │
│  代码分析1智能体：                                            │
│  ┌─────────────────┐                                        │
│  │ ErrorCatcher    │ ← 捕捉代码错误                         │
│  └─────────────────┘                                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Agent API端点

| Agent | API端点 | 功能 |
|-------|---------|------|
| 课程设计师 | `POST /api/v1/agent-flow/run` | 启动智能体工作流 |
| 辅导助手 | `POST /api/v1/tutor/ask` | 提问问答 |
| 错误捕捉 | `POST /api/v1/error-catcher/analyze` | 分析代码错误 |
| 思维溯源 | `POST /api/v1/misconception-tracer/trace` | 追溯思维误区 |
| 项目拆解 | `POST /api/v1/project-decomposer/decompose` | 拆解项目 |
| 角色匹配 | `POST /api/v1/role-matcher/match` | 匹配角色 |
| 协作督导 | `POST /api/v1/collaboration-supervisor/daily-report` | 生成协作报告 |
| 成果评估 | `POST /api/v1/result-evaluator/full-report` | 生成评估报告 |

---

## 智能体基类特色

`BaseAgent`（`backend/app/agents/base.py`）为所有12个智能体提供统一的基础能力：

### 1. 智能体通信机制

```python
AgentMessage(
    from_agent="profiler",
    to_agent="path_planner",
    message_type="task_assignment",  # task_assignment/query/response/notification
    priority="high",                 # low/normal/high/urgent
    requires_response=True
)
```

- 标准化消息格式，支持4种消息类型和4种优先级
- 消息队列异步通信，智能体间松耦合

### 2. 工具注册与调用

```python
agent.register_tool("search_knowledge", search_func)
result = agent.use_tool("search_knowledge", query="递归")
```

- 动态注册工具函数，类似 function calling 范式
- 运行时按名称调用，灵活扩展智能体能力

### 3. 记忆系统

```python
agent.update_memory("student_weakness", ["指针", "递归"])
weakness = agent.get_memory("student_weakness")
agent.clear_memory()
```

- 每个智能体独立维护上下文记忆
- 支持读写和清除操作

### 4. 反思循环（Reflection Loop）— 核心创新

```python
result = await agent.run_with_reflection(
    context=input_data,
    max_iterations=3,        # 最多3次迭代
    quality_threshold=0.8,   # 质量阈值80%
    timeout_per_iteration=60 # 每次60秒超时
)
```

**执行流程**：
1. 执行 `process()` 获取初始结果
2. 调用 `_self_evaluate()` 或 `_rule_based_evaluate()` 评估质量
3. 分数 ≥ 0.8 → 提前终止，返回结果
4. 分数 < 0.8 → 将结果+反馈注入context，重新执行
5. 保留 `best_result`，即使后续失败也能返回最优解

**双重评估**：
- `_rule_based_evaluate()`：检查是否包含 content/output、confidence、status 字段（快速fallback）
- `_self_evaluate()`：LLM作为教育内容质量评估专家，从准确性、完整性、可用性三维度打分

### 5. 结果缓存

```python
result = await agent.cached_process(context)
```

- 使用 context 的 JSON SHA256 哈希作为缓存 key
- 仅缓存 `status=="success"` 的结果
- 避免重复计算相同输入

---

## 防幻觉机制

### SafetyGuard（内容安全守卫）

**输入检查** `check_input(text)`：
- 支持纯文本和图文数组两种输入格式
- 预编译正则匹配15个敏感词（政治敏感、暴力恐怖等）
- 返回 `{safe: bool, messages: []}`

**Prompt安全加固** `sanitize_prompt(prompt, student_age)`：
- 自动在prompt末尾追加安全约束
- 未成年人（age < 18）额外追加更温和的表达要求
- 约束内容：禁止违法内容、要求不确定时明确说明、适龄化表达

### HallucinationGuard（防幻觉守卫）

**四种防幻觉策略层层递进**：

| 策略 | 方法 | 实现细节 |
|------|------|----------|
| JSON Schema校验 | `verify_json_schema()` | 验证LLM输出的JSON是否包含所有必要字段 |
| 代码语法校验 | `verify_code_output()` | 对Python输出调用`compile()`做AST静态语法检查，精确报错到行号 |
| 引用溯源检查 | `verify_citations()` | 6种正则模式检测引用标注：`[1]`、`《》`、`来源：`、`参考`、`引用`、`according to` |
| 自我纠错 | `self_correct()` | 构造二次Prompt，以"严格的事实核查专家"角色进行自我修正 |

**自我纠错流程**：
1. 构造事实核查Prompt（检查事实不符、前后矛盾、过度推断、编造内容）
2. 以低温度（0.2）调用LLM，确保修正的确定性
3. 返回修正后的文本

### 结果合并

`combine_guard_results()` 将多个安全检查结果合并为统一的 `{safe, messages, details}` 结构

---

## 核心算法详解

### 1. 自适应DAG学习路径规划（ADPP）

**文件**：`backend/app/algorithms/path_planning_dag.py`
**类名**：`DAGPathPlanner`

#### 1.1 关键路径分析（Critical Path Method）

```python
def count_downstream(kp_id, memo):
    """递归计算每个知识点的下游依赖数量"""
    downstream = prerequisites_map.get(kp_id, [])
    count = len(downstream)
    for d in downstream:
        count += count_downstream(d, memo)
    memo[kp_id] = count
    return count
```

- 关键度越高的知识点影响面越大，优先学习
- 结果带缓存（`_criticality_cache`），避免重复计算

#### 1.2 学习成本模型

```
成本 = 基础时长 × 难度系数 × 掌握度折扣 × 薄弱点加权 × 速度因子 × 关键度因子
```

| 因子 | 范围 | 说明 |
|------|------|------|
| 难度系数 | 0.7 ~ 1.8 | 1级=0.7x, 5级=1.8x |
| 掌握度折扣 | 0.15 ~ 1.0 | 预测掌握概率越高，成本越低 |
| 薄弱点加权 | 1.0 / 1.25 | 匹配薄弱领域则+25% |
| 速度因子 | 0.75 / 1.0 / 1.35 | fast/moderate/slow |
| 关键度因子 | 1.0 / 1.15 | 关键知识点额外+15% |

#### 1.3 简化BKT（贝叶斯知识追踪）模型

```python
def _estimate_mastery_probability(kp_id, student_profile):
    """逻辑或近似：只要有一个前置掌握得好，就有较高概率掌握当前"""
    P_master = 1 - prod(1 - P(prereq_i))
    # 结合实际掌握度：0.4 * 预测值 + 0.6 * 实际值
    return 0.4 * P_master + 0.6 * actual_mastery
```

#### 1.4 加权拓扑排序

在严格保证拓扑序的前提下，每个层级内按综合权重排序：

```
权重 = 薄弱点优先(+10) + 关键度(+5×比率) + 掌握度低优先(+3×(1-mastery))
       - 难度偏离(-abs(difficulty-3))
```

#### 1.5 自适应阶段划分

| 学习偏好 | 每阶段量 | 阶段名称序列 |
|----------|----------|--------------|
| 理论型 | 3天量 | 基础巩固→核心知识→进阶深化→综合实战 |
| 练习型 | 1.5天量 | 基础巩固→核心知识→进阶深化→综合实战→专项突破→融会贯通 |
| 平衡型 | 2天量 | 同上 |

#### 1.6 动态路径调整

| 条件 | 策略 |
|------|------|
| 得分 < 50 | 插入"紧急回炉"阶段，后续延长30% |
| 得分 50-70 | 插入强化练习阶段 |
| 得分 ≥ 90 且趋势上升 | 允许加速，后续缩短20% |
| 预警状态 | 全局增加20%学习时间，更注重复习 |

### 2. 多因素趋势分析

**文件**：`backend/app/algorithms/trend_analysis.py`
**类名**：`MultiFactorTrendAnalyzer`

6大维度加权计算（总和=1.0）：

| 维度 | 权重 | 算法 | 公式 |
|------|------|------|------|
| 知识掌握度趋势 | 35% | 最近5次测验线性斜率 | `slope = Σ(x-x̄)(y-ȳ) / Σ(x-x̄)²` |
| 学习速度比例 | 15% | 按action类型加权 | `speed = Σ(count_i × weight_i) / expected` |
| 学习时间效率 | 15% | 单位时间得分提升率 | `efficiency = score_gain / time_spent` |
| 薄弱点优先级 | 15% | 薄弱点集中度+数量惩罚 | `H = Σ(p_i²)` (Herfindahl指数) |
| 连续学习稳定性 | 5% | 最近7天学习天数占比 | `stability = active_days / 7` |
| 知识点完成率 | 15% | complete动作占比+quiz质量 | `completion = completed / total` |

**趋势状态分类**：
- `growth`：掌握度趋势上升 + 完成率高
- `decline`：掌握度趋势下降
- `warning`：薄弱点多 + 连续性差
- `stable`：其他情况

**预测**：线性回归预测未来3天掌握度

### 3. 多维度加权匹配

**文件**：`backend/app/algorithms/weighted_matching.py`
**类名**：`MultiDimWeightedMatcher`

**资源匹配**（5因子）：
| 因子 | 权重 | 说明 |
|------|------|------|
| 知识点匹配 | 30% | 资源知识点与学生需求的匹配度 |
| 难度适配 | 25% | 资源难度与学生水平的匹配 |
| 认知风格匹配 | 20% | 视觉/听觉/动手偏好 |
| 学习目标匹配 | 15% | 与学生目标的对齐度 |
| 学习节奏匹配 | 10% | 与学生速度的匹配 |

**路径匹配**（5因子）：
| 因子 | 权重 | 说明 |
|------|------|------|
| 基础水平适配 | 25% | 路径起点与学生水平 |
| 薄弱点覆盖度 | 25% | 路径对薄弱点的覆盖 |
| 节奏适配 | 20% | 路径强度与学生承受力 |
| 目标对齐 | 20% | 路径终点与学生目标 |
| 前置准备度 | 10% | 学生对前置知识的掌握 |

### 4. 学习效果评估

**文件**：`backend/app/algorithms/effect_evaluation.py`
**类名**：`LearningEffectEvaluator`

| 指标 | 算法 | 说明 |
|------|------|------|
| 正确率 | `correct / total` | 基础正确率 |
| 掌握度 | 最近5次加权平均 | 权重递增（最近一次权重最高） |
| 提升速率 | 3对3比较或线性回归 | 前3次 vs 后3次 |
| 薄弱点集中度 | Herfindahl指数 | `H = Σ(p_i²)`，越集中越严重 |
| 下次测验预测 | 线性回归 | 预测下次得分 |
| 潜在失分点 | 薄弱点×难度权重 | 预测可能失分的知识点 |
| 干预策略 | 规则引擎 | 自动生成针对性建议 |

---

## C语言内容库

### 内容架构

采用 **"数据库优先 + 本地fallback"** 双层架构：

```
请求知识点内容
    │
    ├─ 数据库有 → 从 knowledge_points 表读取
    │
    └─ 数据库无 → 从本地 fallback 数据读取（延迟加载）
```

### 知识点结构

每个知识点（kp_id）包含四维内容：

| 内容类型 | 字段名 | 说明 |
|----------|--------|------|
| **讲解文档** | `document` | Markdown格式的知识点讲解 |
| **代码示例** | `code_example` | 可运行的代码示例 |
| **练习题** | `questions` | JSON数组，含选择/判断/填空题 |
| **思维导图** | `mindmap` | JSON对象，D3.js可视化 |

### 知识点列表（C语言16个）

| kp_id | 名称 | 难度 | 前置知识 |
|-------|------|------|----------|
| `kp_c01` | 数据类型与变量 | 1 | 无 |
| `kp_c02` | 运算符与表达式 | 1 | kp_c01 |
| `kp_c03` | 控制结构 | 2 | kp_c01, kp_c02 |
| `kp_c04` | 函数 | 2 | kp_c03 |
| `kp_c05` | 数组 | 2 | kp_c01, kp_c03 |
| `kp_c06` | 字符串 | 2 | kp_c05 |
| `kp_c07` | 指针基础 | 3 | kp_c01, kp_c04 |
| `kp_c08` | 指针与数组 | 3 | kp_c05, kp_c07 |
| `kp_c09` | 指针进阶 | 3 | kp_c07, kp_c08 |
| `kp_c10` | 结构体 | 3 | kp_c01, kp_c04 |
| `kp_c11` | 动态内存 | 3 | kp_c07, kp_c10 |
| `kp_c12` | 文件操作 | 3 | kp_c04, kp_c06 |
| `kp_c13` | 预处理 | 2 | kp_c04 |
| `kp_c14` | 位运算 | 3 | kp_c02 |
| `kp_c15` | 数据结构基础 | 3 | kp_c07, kp_c10 |
| `kp_c16` | 算法基础 | 3 | kp_c05, kp_c15 |

### 安全特性

- **防SQL注入**：LIKE通配符（`%`、`_`、`\`）自动转义
- **延迟加载**：fallback数据按需加载，避免启动内存占用
- **Session复用**：支持外部传入db session，避免重复创建连接

---

## 电路仿真系统

### 系统架构

```
┌─────────────────────────────────────────────┐
│              电路仿真器前端                    │
├─────────────────────────────────────────────┤
│  CircuitSimulator (主入口)                    │
│    ├─ ComponentPalette (元件面板)             │
│    ├─ Canvas (SVG画布)                       │
│    ├─ PropertiesPanel (属性面板)              │
│    ├─ ToolBar (工具栏)                       │
│    ├─ MeasurementOverlay (测量浮层)           │
│    └─ AiAnalysisDialog (AI分析)              │
├─────────────────────────────────────────────┤
│  utils/                                     │
│    ├─ mna-solver.ts (MNA求解器核心)           │
│    ├─ circuit-utils.ts (电路工具)             │
│    ├─ drawing-utils.ts (绘图工具)             │
│    └─ constants.ts (常量定义)                │
└─────────────────────────────────────────────┘
```

### 支持的元件类型

| 元件 | 类型标识 | 参数 |
|------|----------|------|
| 电阻 | `resistor` | 阻值 R (Ω) |
| 电容 | `capacitor` | 容值 C (F) |
| 电感 | `inductor` | 感值 L (H) |
| 电压源 | `voltage_source` | 电压 V (V) |
| 电流源 | `current_source` | 电流 I (A) |
| 接地 | `ground` | 0V参考点 |

### MNA求解器核心算法

#### 并查集节点合并（Union-Find）

```typescript
class UnionFind {
  parent: number[];
  rank: number[];
  
  find(x: number): number {
    // 路径压缩
    if (this.parent[x] !== x) {
      this.parent[x] = this.find(this.parent[x]);
    }
    return this.parent[x];
  }
  
  union(x: number, y: number): void {
    // 按秩合并
    const px = this.find(x), py = this.find(y);
    if (px === py) return;
    if (this.rank[px] < this.rank[py]) this.parent[px] = py;
    else if (this.rank[px] > this.rank[py]) this.parent[py] = px;
    else { this.parent[py] = px; this.rank[px]++; }
  }
}
```

**合并规则**：
- 导线连接的端点自动合并为同一节点
- 不同元件在同一栅格点的端子自动合并
- 所有接地元件的端子统一合并到节点0

#### MNA方程组构建

矩阵规模：`(N+M) × (N+M)`，N=节点数，M=电压源数量

| 元件 | 矩阵贡献 |
|------|----------|
| 电阻 | G[i][i] += 1/R, G[j][j] += 1/R, G[i][j] -= 1/R, G[j][i] -= 1/R |
| 电压源 | 增加额外方程行和列（未知量为支路电流） |
| 电流源 | RHS[i] += I, RHS[j] -= I |

#### 高斯消元求解

```typescript
function gaussianElimination(matrix: number[][], vector: number[]): number[] {
  const n = matrix.length;
  // 列主元选取
  for (let col = 0; col < n; col++) {
    let maxRow = col;
    for (let row = col + 1; row < n; row++) {
      if (Math.abs(matrix[row][col]) > Math.abs(matrix[maxRow][col])) {
        maxRow = row;
      }
    }
    // 奇异矩阵检测
    if (Math.abs(matrix[maxRow][col]) < 1e-12) {
      throw new Error("奇异矩阵：电路可能开路或短路");
    }
    // 交换行
    [matrix[col], matrix[maxRow]] = [matrix[maxRow], matrix[col]];
    [vector[col], vector[maxRow]] = [vector[maxRow], vector[col]];
    // 消元
    for (let row = col + 1; row < n; row++) {
      const factor = matrix[row][col] / matrix[col][col];
      for (let j = col; j < n; j++) {
        matrix[row][j] -= factor * matrix[col][j];
      }
      vector[row] -= factor * vector[col];
    }
  }
  // 回代
  const x = new Array(n).fill(0);
  for (let i = n - 1; i >= 0; i--) {
    x[i] = vector[i];
    for (let j = i + 1; j < n; j++) {
      x[i] -= matrix[i][j] * x[j];
    }
    x[i] /= matrix[i][i];
  }
  return x;
}
```

#### 结果提取

求解后自动计算：
- **节点电压**：直接从解向量获取
- **支路电流**：电阻用欧姆定律 `I = V/R`，电压源用电流变量
- **功率耗散**：`P = I²×R` 或 `P = V×I`

### AI电路分析集成

`AiAnalysisDialog` 将电路的网表（netlist）和仿真结果发送给后端 `/circuit-analysis/analyze` 接口，获取：
- 电路功能分析
- 元件作用解释
- 优化建议
- 潜在问题诊断

提供4个快捷问题模板，支持自定义提问。

### 实时测量浮层

`MeasurementOverlay` 在画布右上角实时显示：
- 各节点电压值
- 各支路电流值（自动选择单位：uA/mA/A）
- 功率耗散

---

## 后端模块详解

### 核心基础模块 (`app/core/`)

| 文件 | 类/函数 | 功能 |
|------|---------|------|
| `config.py` | `Settings(BaseSettings)` | 应用配置：5种LLM供应商、数据库、Redis、火山引擎、LangSmith |
| `logger.py` | `setup_logger(name)` | 双通道日志（控制台+文件轮转10MB×5） |
| `exceptions.py` | 异常处理器 | 请求校验错误(422)、HTTP异常、全局异常(500) |
| `safety.py` | `SafetyGuard` + `HallucinationGuard` | 敏感词过滤(15个)、JSON校验、代码语法检查、引用溯源、LLM自我修正 |
| `rate_limiter.py` | `RateLimiter` | 滑动窗口限流：全局60次/分钟，登录10次/分钟，LLM 20次/分钟 |
| `cache.py` | `PromptCache` | LRU+TTL内存缓存，512条，600秒过期 |

### 数据模型 (`app/models/`) — 23个ORM模型

| 文件 | 模型类 | 表名 | 说明 |
|------|--------|------|------|
| `user.py` | `UserModel` | `users` | 用户（学生/教师/管理员） |
| `student.py` | `StudentProfileModel` | `student_profiles` | 6维学生画像 |
| `knowledge.py` | `KnowledgePointModel` | `knowledge_points` | 知识点（含文档/代码/题目/思维导图） |
| `knowledge.py` | `LearningRecordModel` | `learning_records` | 学习记录 |
| `knowledge.py` | `QuizResultModel` | `quiz_results` | 测验结果 |
| `knowledge.py` | `ResourceFeedbackModel` | `resource_feedback` | 资源反馈 |
| `knowledge.py` | `ResourceTaskModel` | `resource_tasks` | 资源生成任务 |
| `knowledge.py` | `KnowledgeGraphModel` | `knowledge_graph` | 知识图谱 |
| `trend.py` | `TrendDataModel` | `student_trends` | 学习趋势数据 |
| `gamification.py` | `PointsModel` | `game_points` | 游戏积分 |
| `gamification.py` | `AchievementModel` | `game_achievements` | 成就徽章 |
| `gamification.py` | `TaskModel` | `game_tasks` | 学习任务 |
| `gamification.py` | `LeaderboardModel` | `leaderboard` | 排行榜 |
| `log_reflection.py` | `LearningLogModel` | `learning_logs` | 学习日志 |
| `log_reflection.py` | `ReflectionModel` | `reflections` | 反思记录 |
| `favorites.py` | `FavoriteModel` | `favorites` | 收藏夹 |
| `monitor.py` | `ApiMonitorModel` | `api_monitor` | API性能监控 |
| `monitor.py` | `LlmCallModel` | `llm_calls` | LLM调用记录 |
| `monitor.py` | `SystemHealthModel` | `system_health` | 系统健康 |
| `tutor_qa.py` | `TutorQAModel` | `tutor_qa_records` | 辅导问答记录 |
| `kb_note.py` | `KBFolderModel` | `kb_folders` | 知识库文件夹 |
| `kb_note.py` | `KBNoteModel` | `kb_notes` | 知识库笔记 |
| `path_adjustment_log.py` | `PathAdjustmentLogModel` | `path_adjustment_logs` | 路径调整日志 |

### Pydantic Schema (`app/schemas/`)

`resource.py` 定义了资源生成相关的请求/响应模型：
- `DocumentGenerateRequest/Response` — 文档生成
- `QuestionsGenerateRequest/Response` — 题目生成
- `MindmapGenerateRequest/Response` — 思维导图生成
- `CodeGenerateRequest/Response` — 代码生成
- `CodeExecuteRequest/Response` — 代码执行

### 学习算法 (`app/algorithms/`)

| 文件 | 类名 | 核心算法 |
|------|------|----------|
| `path_planning_dag.py` | `DAGPathPlanner` | 自适应DAG学习路径规划（ADPP）：关键路径分析 + 贝叶斯知识追踪 + 加权拓扑排序 + 自适应阶段划分 |
| `trend_analysis.py` | `MultiFactorTrendAnalyzer` | 多因素趋势分析：6维度加权（掌握度35%+速度15%+效率15%+薄弱点15%+稳定性5%+完成率15%） |
| `weighted_matching.py` | `MultiDimWeightedMatcher` | 多维度加权匹配：资源匹配（5因子）+ 路径匹配（5因子） |
| `effect_evaluation.py` | `LearningEffectEvaluator` | 学习效果评估：正确率/掌握度/提升速率/薄弱集中度/预测/干预 |

### 服务层 (`app/services/`)

| 文件 | 类/函数 | 功能 |
|------|---------|------|
| `llm_factory.py` | `BaseLLM` + `OpenAICompatibleLLM` + `LLMFactory` | 统一LLM工厂：5供应商、流式/非流式/JSON输出、指数退避重试、调用监控 |
| `gamification_service.py` | `award_points` / `sync_leaderboard` | 游戏化服务：积分管理、排行榜同步、成就解锁 |
| `content_library.py` | `get_content` | C语言课程内容库（16个知识点） |
| `image_generation.py` | `generate_image_ark` | 火山引擎文生图（ARK优先，视觉智能回退） |
| `ppt_generator.py` | `generate_ppt` | PPT自动生成：LLM生成大纲 + python-pptx构建（支持10种幻灯片类型） |
| `path_adjustment_engine.py` | `analyze_adjustment_need` | 路径自动调整：测验趋势(40%)+反思分析(30%)+辅导频率(30%) |

### LangGraph工作流 (`app/graph/`)

| 文件 | 功能 |
|------|------|
| `state.py` | 共享状态定义：`AgentState`（messages/student_id/task_type/results等） |
| `graph.py` | 状态图构建：supervisor → profiler/path_planner/resource_generator/tutor → assembler |
| `nodes.py` | 节点实现：6个节点函数 + 声明式路由配置（V1串行 + V2并行fan-out） |

### API路由 (`app/api/`) — 36个模块

| 文件 | 路由前缀 | 功能 |
|------|----------|------|
| `auth.py` | `/auth` | JWT认证（登录/注册/Token刷新） |
| `profile.py` | `/profile` | 学生画像（6维分析） |
| `resource.py` | `/resource` | 资源生成（文档/题目/思维导图/代码） |
| `learning_path.py` | `/learning-path` | 学习路径（DAG规划+动态调整） |
| `tutor.py` | `/tutor` | 智能辅导（WebSocket流式） |
| `knowledge.py` | `/knowledge` | 知识点管理 |
| `learning_data.py` | `/learning-data` | 学习数据上报 |
| `trend.py` | `/trend` | 趋势分析与预测 |
| `matching.py` | `/matching` | 匹配推荐 |
| `gamification.py` | `/gamification` | 游戏化（积分/成就/任务/排行榜） |
| `gamification_tree.py` | `/gamification-tree` | 知识树成长系统 |
| `gamification_challenge.py` | `/gamification-challenge` | 学习挑战+六维排行榜 |
| `log_reflection.py` | `/log-reflection` | 学习日志与反思（康奈尔笔记/费曼学习法） |
| `monitoring.py` | `/monitoring` | 系统监控（API/LLM/健康检查） |
| `dashboard.py` | `/dashboard` | 仪表盘统计+成长时间轴 |
| `knowledge_graph.py` | `/knowledge-graph` | 知识图谱构建与查询 |
| `knowledge_base.py` | `/kb` | 知识库管理（文件夹/笔记/WikiLink/反向链接） |
| `agent_flow.py` | `/agent-flow` | Agent工作流可视化 |
| `ppt.py` | `/ppt` | PPT自动生成 |
| `image.py` | `/image` | 文生图 |
| `ocr.py` | `/ocr` | OCR识图 |
| `daily_quiz.py` | `/daily-quiz` | 每日测验 |
| `favorites.py` | `/favorites` | 收藏夹 |
| `error_catcher.py` | `/error-catcher` | 错误捕捉 |
| `misconception_tracer.py` | `/misconception-tracer` | 思维溯源 |
| `project_decomposer.py` | `/project-decomposer` | 项目拆解 |
| `role_matcher.py` | `/role-matcher` | 角色匹配 |
| `collaboration_supervisor.py` | `/collaboration-supervisor` | 协作督导 |
| `result_evaluator.py` | `/result-evaluator` | 成果评估 |
| `teacher.py` | `/teacher` | 教师端API |
| `onboarding.py` | `/onboarding` | 新手引导问卷 |
| `path_adjustment_log_api.py` | `/path-adjustment` | 路径调整日志 |
| `circuit_analysis.py` | `/circuit-analysis` | 电路分析 |

### 中间件 (`app/middleware/`)

| 文件 | 类 | 功能 |
|------|-----|------|
| `api_monitor.py` | `APIMonitorMiddleware` | API性能监控：内存缓冲(deque, 500条) + 定期批量写入(每5秒/满50条) |

---

## 前端模块详解

### 页面组件 (`src/pages/`) — 28个路由页面

#### 学生端页面

| 文件 | 路由 | 功能 |
|------|------|------|
| `Dashboard.tsx` | `/` | 学习仪表盘：统计卡片、学习趋势图、任务进度、推荐资源、知识树、每日练习、排行榜 |
| `Login.tsx` | `/login` | 登录/注册：三Tab（登录/学生注册/教师注册），GSAP动画 |
| `LandingPage.tsx` | `/`（未登录） | 落地页：功能特性展示、使用流程、统计数据、FAQ |
| `Profile.tsx` | `/profile` | 对话式学习画像：AI对话评估6维画像，雷达图可视化 |
| `LearningPath.tsx` | `/learning-path` | 学习路径：DAG可视化、路径调整、依赖链查询、调整日志 |
| `ResourceCenter.tsx` | `/resources` | 学习资源中心：课程目录树+多标签内容（文档/代码/练习/思维导图/算法可视化） |
| `ResourceDetail.tsx` | `/resource/:kpId` | 资源详情：Markdown讲义、Monaco代码编辑器、练习题、AI辅导 |
| `Tutor.tsx` | `/tutor` | AI辅导：多模态交互、WebSocket实时、模型切换、RAG增强 |
| `LearningChallenge.tsx` | `/challenges` | 知识冒险：游戏化任务地图、成就徽章、知识树动画 |
| `LeaderboardPlus.tsx` | `/leaderboard` | 增强排行榜：6维度（积分/连续/掌握/测验/AI协作/进步）× 3周期（日/周/月） |
| `ErrorDiagnosis.tsx` | `/error-diagnosis` | 错误诊断入口：根据学科智能切换（C语言/电路分析） |
| `ErrorDiagnosisC.tsx` | — | C语言错误诊断：语法错误、逻辑错误分析，雷达图能力评估 |
| `ProjectCollaboration.tsx` | `/project-collaboration` | 项目协作：拆解→匹配→督导→评估完整工作流 |
| `PersonalSpace.tsx` | `/personal` | 个人空间：学习统计、反思日志、成就徽章、收藏夹 |
| `KnowledgeBase.tsx` | `/knowledge-base` | 知识库：三栏布局（文件夹树+笔记编辑器+反向链接/图谱） |
| `KnowledgeTree.tsx` | — | 知识树成长动画：D3.js绘制，5种状态（种子→传说） |

#### 教师端页面

| 文件 | 路由 | 功能 |
|------|------|------|
| `TeacherHome.tsx` | `/teacher` | 教师首页：统计卡片、学生积分趋势图、快捷操作、活跃学生列表 |
| `AssignmentManagement.tsx` | `/teacher/assignments` | 作业管理：创建/编辑/删除/状态跟踪 |
| `StudentManagement.tsx` | `/teacher/students` | 学生管理：列表/搜索/详情/趋势分析 |
| `TeachingResources.tsx` | `/teacher/resources` | 备课资源：PPT在线生成 |
| `LearningAnalytics.tsx` | `/teacher/analytics` | 学情分析：薄弱知识点、薄弱领域、学习洞察 |
| `ClassAnalytics.tsx` | `/teacher/class-analytics` | 班级学情：雷达图、排名表、多维度分析 |
| `ClassComparison.tsx` | `/teacher/class-comparison` | 班级对比：多班数据对比分析 |
| `ReportExport.tsx` | `/teacher/reports` | 报告导出：PDF/Excel/Word |
| `SystemSettings.tsx` | `/teacher/settings` | 系统设置：账户/密码/通知/语言 |

#### 电路模拟器

| 文件 | 功能 |
|------|------|
| `CircuitSimulator.tsx` | 电路模拟器入口 |
| `Canvas.tsx` | SVG画布（组件拖拽/连线） |
| `ComponentPalette.tsx` | 电路元件面板（电阻/电压源/电流源/接地） |
| `PropertiesPanel.tsx` | 元件属性面板 |
| `AiAnalysisDialog.tsx` | AI电路分析对话框 |
| `MeasurementOverlay.tsx` | 测量覆盖层 |
| `ToolBar.tsx` | 工具栏 |
| `store.ts` / `types.ts` | 状态管理/类型定义 |
| `utils/mna-solver.ts` | MNA节点电压法求解器 |

### 通用组件 (`src/components/`) — 24个组件

| 组件 | 功能 |
|------|------|
| `AppHeader` | 顶部导航：全局搜索、通知、帮助、学科切换、用户菜单 |
| `Sidebar` | 侧边栏：学生10项/教师10项菜单，今日学习时长，折叠/展开 |
| `ChatPanel` | 通用AI对话面板：Markdown、图片上传、建议问题、多模态 |
| `AgentFlowPanel` | Agent工作流面板：6个智能体执行状态/日志/时间线 |
| `AlgorithmVisualizer` | 算法可视化：冒泡/快速/插入排序动画+伪代码高亮 |
| `OnboardingQuestionnaire` | 新手引导：5步问卷（水平/难度/时长/目标/风格） |
| `PPTGenerator` | PPT生成弹窗：主题输入+进度+下载 |
| `MarkdownViewer` | Markdown渲染：GFM/数学公式/代码高亮/复制 |
| `MindmapViewer` | 思维导图：D3.js力导向布局，拖拽交互 |
| `CodeEditor` | 代码编辑器：Monaco Editor，C/Python语法 |
| `GrowthTimeline` | 成长时间轴：里程碑节点+每日学习曲线 |
| `Leaderboard` | 排行榜：日/周/月切换，奖牌/排名/积分 |
| `DailyChallenge` | 每日挑战：任务列表/进度条/奖励 |
| `AdjustmentLogPanel` | 路径调整日志：触发类型/原因/时间 |
| `ErrorBoundary` | 全局错误边界：Sentry集成，重试/返回首页 |
| `GlobalToast` | 全局Toast通知 |
| `PageCard` / `SectionCard` | 卡片容器 |
| `StatCard` / `StatRow` | 统计展示 |
| `StatusIcon` / `StatusTag` | 状态图标/标签 |

#### 知识库子组件 (`src/components/kb/`)

| 组件 | 功能 |
|------|------|
| `FileTree` | 文件夹树（创建/重命名/删除） |
| `NoteList` | 笔记列表（标题+预览） |
| `NoteEditor` | 笔记编辑器（Markdown+WikiLink） |
| `BacklinksPanel` | 反向链接面板 |
| `SearchPanel` | 全文搜索 |
| `KnowledgeGraph` | D3.js力导向知识图谱 |
| `WikiLinkMarkdown` | WikiLink语法渲染（`[[笔记名]]`→链接） |

### API服务封装 (`src/services/`)

| 文件 | API对象 | 功能模块 |
|------|---------|----------|
| `api.ts` | `authApi` | 登录/注册/获取用户 |
| | `profileApi` | 画像获取/更新/摘要/初始化/对话分析 |
| | `resourceApi` | 资源生成/任务查询/文档/题目/思维导图/代码/执行 |
| | `pathApi` | 路径生成/当前路径/调整/DAG生成 |
| | `tutorApi` | 提问/历史 |
| | `dashboardApi` | 统计/时间轴/活跃日期 |
| | `gamificationApi` | 积分/成就/任务/排行榜 |
| | `knowledgeTreeApi` | 知识树状态 |
| | `challengeApi` | 挑战列表 |
| | `leaderboardPlusApi` | 增强排行榜 |
| | `pptApi` | PPT生成/状态/下载 |
| | `learningDataApi` | 学习记录/测验/历史/反馈 |
| | `logReflectionApi` | 反思CRUD/日志/回顾 |
| | `trendApi` | 趋势历史/分析 |
| | `knowledgeApi` | 知识点列表/详情/搜索 |
| | `dailyQuizApi` | 每日测验/统计 |
| | `agentFlowApi` | 工作流启动/状态 |
| | `collaborationApi` | 协作督导全部接口 |
| | `projectDecomposerApi` | 项目拆解 |
| | `roleMatcherApi` | 角色匹配 |
| | `evaluationApi` | 成果评估 |
| | `teacherApi` | 教师端全部接口 |
| | `onboardingApi` | 引导问卷 |
| | `adjustmentLogApi` | 路径调整日志 |
| | `circuitApi` | 电路分析 |
| | `imageApi` | 文生图 |
| | `ocrApi` | OCR识图 |
| | `favoritesApi` | 收藏管理 |
| `knowledgeBaseApi.ts` | `kbApi` | 知识库全部接口 |
| **特性** | | 请求拦截器（Token注入）、响应拦截器（错误处理）、请求去重 |

### 状态管理 (`src/store/`)

| 文件 | Store | 功能 |
|------|-------|------|
| `index.ts` | `useAppStore` | 全局状态：studentId/token/isLoggedIn/userInfo/currentSubject/toast/sidebarCollapsed，持久化到localStorage |
| `kbStore.ts` | `kbStore` | 知识库状态：文件夹/笔记/搜索/反向链接，500ms防抖自动保存 |

### 工具函数 (`src/utils/`)

| 文件 | 函数 | 功能 |
|------|------|------|
| `error.ts` | `extractApiError()` | 从错误对象提取可读消息 |
| `level.ts` | `fetchLevelConfig()` / `calcLevel()` | 等级系统：从后端获取配置，计算等级/进度/升级XP |
| `profile.ts` | `buildRadarData()` | 画像→雷达图数据转换（6维归一化） |

### 自定义Hooks (`src/hooks/`)

| Hook | 功能 |
|------|------|
| `useElapsedTime` | 追踪页面停留时长（用于学习数据上报） |

### TypeScript类型 (`src/types/`)

| 文件 | 内容 |
|------|------|
| `index.ts` | 450+行：API通用/画像/路径/资源/辅导/仪表盘/算法/游戏化/引导/Agent等全部类型 |
| `knowledgeBase.ts` | 知识库专用类型：文件夹/笔记/反向链接/图节点/图边 |

---

## 数据库设计

### 数据库状态

| 表名 | 记录数 | 说明 |
|------|--------|------|
| `users` | 20+ | 学生+教师账号 |
| `learning_records` | 79 | 学习记录 |
| `quiz_results` | 46 | 测验结果 |
| `game_points` | 17 | 游戏积分 |
| `kb_notes` | 20 | 知识库笔记 |
| `student_profiles` | 3 | 学生画像 |
| `student_trends` | 3 | 趋势数据 |

### 核心数据流

```
学生学习 → learning_records → Dashboard统计
         → quiz_results → 教师端弱项分析
         → game_points → 排行榜+积分图表
         → kb_notes → 知识库管理
         → reflections → 学习反思
         → student_trends → 趋势预测
         → path_adjustment_logs → 路径调整历史
```

---

## 核心算法

> 详见上方 [核心算法详解](#核心算法详解) 章节，包含完整的公式、代码实现和参数说明。

---

## API接口列表（36个模块，167+接口）

### 用户认证 (`/api/v1/auth`)
- `POST /register` — 学生注册
- `POST /register-teacher` — 教师注册
- `POST /login` — 登录（返回JWT Token）
- `GET /me` — 获取当前用户信息

### 学生画像 (`/api/v1/profile`)
- `GET /{student_id}` — 获取画像
- `POST /{student_id}/update` — 更新画像
- `GET /{student_id}/summary` — 获取摘要
- `POST /{student_id}/initialize` — 初始化画像
- `POST /{student_id}/analyze-conversation` — 对话分析

### Dashboard (`/api/v1/dashboard`)
- `GET /{student_id}/summary` — 仪表盘统计
- `GET /{student_id}/timeline` — 成长时间轴
- `GET /{student_id}/active-dates` — 活跃日期统计

### Agent工作流 (`/api/v1/agent-flow`)
- `POST /run` — 启动智能体工作流
- `GET /{run_id}/status` — 查询工作流状态

### 学习路径 (`/api/v1/learning-path`)
- `POST /generate` — 生成路径
- `GET /{student_id}/current` — 当前路径
- `POST /{student_id}/adjust` — 调整路径
- `POST /dag/generate` — DAG路径生成
- `POST /dag/adjust` — DAG路径调整
- `GET /dag/dependency-chain/{target_kp_id}` — 获取依赖链

### 资源生成 (`/api/v1/resource`)
- `POST /generate` — 生成资源（异步任务）
- `GET /task/{task_id}` — 查询任务状态
- `POST /document/generate` — 生成文档
- `POST /questions/generate` — 生成题目
- `POST /mindmap/generate` — 生成思维导图
- `POST /code/generate` — 生成代码
- `POST /code/execute` — 在线运行代码（安全沙箱）

### PPT自动生成 (`/api/v1/ppt`)
- `POST /generate` — 生成PPT（异步任务）
- `GET /{task_id}/status` — 查询生成状态
- `GET /{task_id}/download` — 下载PPT

### 智能辅导 (`/api/v1/tutor`)
- `POST /ask` — 提问（同步响应）
- `WS /ws/{session_id}` — WebSocket实时辅导（流式输出）
- `GET /session/{session_id}/history` — 会话历史
- `GET /qa-history/{student_id}` — 学生问答历史
- `POST /qa-feedback/{qa_id}` — 问答反馈

### 游戏化 (`/api/v1/gamification`)
- `GET /{student_id}/points` — 获取积分
- `POST /points/add` — 添加积分
- `GET /{student_id}/achievements` — 获取成就
- `POST /achievements/unlock` — 解锁成就
- `GET /{student_id}/tasks` — 获取任务
- `POST /tasks/create` — 创建任务
- `POST /tasks/progress` — 更新任务进度
- `GET /leaderboard/{period}` — 排行榜

### 知识树成长 (`/api/v1/gamification-tree`)
- `GET /level-config` — 获取等级配置
- `GET /{student_id}/tree` — 获取知识树状态

### 学习挑战 (`/api/v1/gamification-challenge`)
- `GET /{student_id}/challenges` — 挑战列表
- `GET /leaderboard/{dimension}` — 六维排行榜

### 知识图谱 (`/api/v1/knowledge-graph`)
- `POST /build` — 构建知识图谱
- `GET /` — 获取最新图谱
- `GET /node/{kp_id}` — 获取节点信息
- `GET /constraint-prompt` — 获取约束Prompt

### 知识库 (`/api/v1/kb`)
- `POST /folders` — 创建文件夹
- `GET /folders` — 文件夹列表
- `PUT /folders/{folder_id}` — 更新文件夹
- `DELETE /folders/{folder_id}` — 删除文件夹
- `POST /notes` — 创建笔记
- `GET /notes` — 笔记列表
- `GET /notes/search` — 搜索笔记
- `GET /notes/{note_id}` — 笔记详情
- `PUT /notes/{note_id}` — 更新笔记
- `DELETE /notes/{note_id}` — 删除笔记
- `GET /wikilink/backlinks/{note_id}` — 反向链接
- `GET /wikilink/graph` — 知识图谱可视化
- `POST /auto-organize` — 自动整理
- `POST /batch-organize` — 批量整理
- `POST /analyze-and-save` — AI分析并保存

### 知识点 (`/api/v1/knowledge`)
- `POST /create` — 创建知识点
- `GET /list` — 知识点列表
- `GET /search` — 搜索
- `GET /{kp_id}` — 知识点详情

### 学习数据 (`/api/v1/learning-data`)
- `POST /record` — 上报学习记录
- `POST /quiz` — 提交测验结果
- `GET /{student_id}/history` — 学习历史
- `GET /{student_id}/completed` — 已完成知识点
- `POST /feedback` — 学习反馈

### 趋势分析 (`/api/v1/trend`)
- `POST /analyze` — 趋势预测分析
- `GET /{student_id}/report` — 获取报告
- `GET /{student_id}/history` — 历史趋势

### 学习日志与反思 (`/api/v1/log-reflection`)
- `GET /{student_id}/logs` — 学习日志
- `POST /logs/upsert` — 创建/更新日志
- `POST /reflections/create` — 创建反思
- `PUT /reflections/{reflection_id}` — 更新反思
- `DELETE /reflections/{reflection_id}` — 删除反思
- `GET /{student_id}/reflections` — 反思记录
- `GET /{student_id}/review` — 学习回顾

### AI工具 (`/api/v1/image`, `/api/v1/ocr`)
- `POST /image/generate` — 文生图
- `GET /image/result/{task_id}` — 图片结果
- `GET /image/tasks` — 任务列表
- `POST /ocr/recognize` — OCR识图（URL）
- `POST /ocr/upload` — OCR识图（文件上传）

### 每日测验 (`/api/v1/daily-quiz`)
- `GET /daily` — 获取每日测验
- `GET /stats` — 学习统计

### 错误捕捉 (`/api/v1/error-catcher`)
- `POST /analyze` — 分析代码错误
- `POST /catch-error` — 捕捉错误
- `POST /analyze-misconception` — 分析思维误区
- `POST /validate-code` — 验证代码

### 思维溯源 (`/api/v1/misconception-tracer`)
- `POST /trace` — 追溯思维误区
- `POST /classify` — 分类误区
- `POST /correct` — 生成纠正策略
- `POST /full-analysis` — 完整分析

### 项目拆解 (`/api/v1/project-decomposer`)
- `GET /projects` — 项目列表
- `POST /decompose` — 拆解项目
- `POST /project-info` — 项目详情
- `POST /estimate` — 工作量估算

### 角色匹配 (`/api/v1/role-matcher`)
- `GET /roles` — 角色列表
- `POST /match` — 匹配角色
- `POST /suggest` — 建议分工
- `POST /rebalance` — 重新平衡

### 协作督导 (`/api/v1/collaboration-supervisor`)
- `POST /daily-report` — 生成每日协作报告
- `POST /detect-blockers` — 检测协作阻塞
- `POST /resolve-conflict` — 解决冲突
- `POST /knowledge-sharing` — 知识共享建议
- `POST /sync-progress` — 同步进度

### 成果评估 (`/api/v1/result-evaluator`)
- `POST /evaluate-code` — 评估代码质量
- `POST /evaluate-collaboration` — 评估协作效果
- `POST /evaluate-deliverable` — 评估交付物
- `POST /evaluate-learning` — 评估学习收获
- `POST /full-report` — 生成综合评估报告

### 教师端 (`/api/v1/teacher`)
- `GET /students` — 学生列表（含积分、趋势状态）
- `GET /overview` — 教师概览（学生数、活跃数、平均分、学习记录）
- `GET /student/{student_id}/detail` — 学生详情
- `GET /student/{student_id}/progress` — 学生学习进度
- `GET /student/{student_id}/scores` — 学生成绩数据
- `GET /student/{student_id}/trends` — 学生趋势分析
- `GET /student/{student_id}/reflections` — 学生反思记录
- `GET /ranking` — 学生排行榜（支持按积分/学时/分数排序）
- `GET /weak-points` — 薄弱知识点统计

### 其他接口
- `POST /api/v1/matching/resources` — 资源推荐
- `POST /api/v1/matching/paths` — 路径推荐
- `GET /api/v1/monitoring/api-stats` — API统计
- `GET /api/v1/monitoring/llm-stats` — LLM调用统计
- `GET /api/v1/monitoring/health` — 健康检查
- `GET /api/v1/onboarding/check` — 检查引导
- `POST /api/v1/onboarding/submit` — 提交引导问卷
- `GET /api/v1/path-adjustment/{student_id}/logs` — 路径调整日志
- `POST /api/v1/circuit-analysis/analyze` — 电路分析
- `GET /api/v1/favorites/{student_id}` — 获取收藏
- `POST /api/v1/favorites/{student_id}` — 添加收藏
- `DELETE /api/v1/favorites/{student_id}/{favorite_id}` — 删除收藏

---

## 前端页面结构

### 学生端菜单（10项）
| 路由 | 页面 | 图标 |
|------|------|------|
| `/` | 学习仪表盘 | DashboardOutlined |
| `/profile` | 对话画像 | PieChartOutlined |
| `/learning-path` | 学习路径 | NodeIndexOutlined |
| `/resources` | 学习中心 | ReadOutlined |
| `/challenges` | 知识冒险 | ThunderboltOutlined |
| `/tutor` | 智能辅导 | RobotOutlined |
| `/error-diagnosis` | 错误诊断 | BugOutlined |
| `/project-collaboration` | 项目协作 | ProjectOutlined |
| `/personal` | 个人空间 | UserOutlined |
| `/knowledge-base` | 知识库 | BookOutlined |

### 教师端菜单（10项）
| 路由 | 页面 | 图标 |
|------|------|------|
| `/teacher` | 首页 | DashboardOutlined |
| `/teacher/assignments` | 作业管理 | FileTextOutlined |
| `/teacher/students` | 学生管理 | TeamOutlined |
| `/teacher/resources` | 备课资源 | BookOutlined |
| `/teacher/analytics` | 学情分析 | BarChartOutlined |
| `/teacher/class-analytics` | 班级学情 | LineChartOutlined |
| `/teacher/class-comparison` | 班级对比 | ExperimentOutlined |
| `/teacher/reports` | 报告导出 | FileExcelOutlined |
| `/teacher/settings` | 系统设置 | SettingOutlined |
| `/teacher/personal` | 个人空间 | UserOutlined |

---

## 快速启动

### 1. 环境要求

- Python 3.9+（推荐 3.11）
- Node.js 18+

### 2. 配置API密钥

```bash
copy backend\.env.example backend\.env
```

编辑 `backend\.env`，选择并配置大模型提供商：

| 提供商 | 配置 |
|--------|------|
| **智谱AI（默认）** | `DEFAULT_LLM_PROVIDER=bigmodel` + `BIGMODEL_API_KEY=xxx` |
| **讯飞星火** | `DEFAULT_LLM_PROVIDER=spark` + `SPARK_API_KEY=xxx` |
| **DeepSeek** | `DEFAULT_LLM_PROVIDER=deepseek` + `DEEPSEEK_API_KEY=xxx` |
| **OpenAI** | `DEFAULT_LLM_PROVIDER=openai` + `OPENAI_API_KEY=xxx` |
| **小米MiMo** | `DEFAULT_LLM_PROVIDER=mimo` + `MIMO_API_KEY=xxx` |

### 3. 启动服务

**Windows（一键启动）：**
```bash
start.bat
```

**手动启动：**
```bash
# 后端
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload

# 前端（新终端）
cd frontend
npm install
npm run dev
```

### 4. 访问应用

- 前端: http://localhost:5173
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

### 测试账号

| 角色 | 账号 | 密码 |
|------|------|------|
| **教师** | T001 | Teacher123 |
| **学生** | student_001 | 123456 |
| **学生** | student_002 | 123456 |
| **学生** | student_003 | 123456 |

---

## Docker部署

```bash
# 1. 配置环境变量
copy backend\.env.example backend\.env
# 编辑 backend\.env 填写 API 密钥

# 2. 构建并启动
docker-compose up --build -d

# 3. 访问应用
# 前端: http://localhost
# 后端API: http://localhost:8000
# API文档: http://localhost:8000/docs
```

### Docker配置说明

| 文件 | 说明 |
|------|------|
| `Dockerfile` | 多阶段构建：backend(python:3.11-slim) + frontend-build(node:18-alpine) + frontend(nginx:alpine) |
| `docker-compose.yml` | 两个服务：backend(端口8000) + frontend(端口80)，含健康检查、数据持久化 |
| `nginx.conf` | SPA路由支持、静态资源缓存(1年)、API反向代理、WebSocket 24小时超时 |
| `.dockerignore` | 排除.git/node_modules/dist/venv/.env/*.db |

---

## E2E测试

### 测试框架

- **Playwright** (v1.59.1)
- 串行执行（`workers: 1`）
- 超时60秒，重试1次（CI重试2次）

### 测试文件（4个，39个用例）

| 文件 | 用例数 | 测试内容 |
|------|--------|----------|
| `api.spec.ts` | 21 | 后端API集成：认证、画像、路径、资源、辅导、游戏化、知识树、Agent工作流、PPT生成 |
| `frontend.spec.ts` | 9 | 前端UI：登录、页面导航、侧边栏、登出 |
| `knowledge-base.spec.ts` | 7 | 知识库：页面布局、笔记CRUD、编辑器、反向链接、图谱、搜索、文件树 |
| `markdown-render.spec.ts` | 1 | Markdown渲染：中文内容、代码块、无错误 |

### 运行测试

```bash
cd frontend
npx playwright test e2e/api.spec.ts --reporter=list
```

---

## 项目结构

```
A3_项目框架/
├── backend/                        # 后端代码
│   ├── app/
│   │   ├── agents/                # 12个智能体模块
│   │   │   ├── base.py            # 智能体基类（消息传递、工具注册、记忆系统）
│   │   │   ├── course_designer.py # 课程设计师（主管）
│   │   │   ├── profiler.py        # 画像师
│   │   │   ├── path_planner.py    # 路径规划师
│   │   │   ├── resource_generator.py  # 资源生成师
│   │   │   ├── tutor.py           # 辅导助手（含学习状态感知）
│   │   │   ├── knowledge_graph_builder.py  # 知识图谱构建师
│   │   │   ├── misconception_tracer.py  # 思维溯源师
│   │   │   ├── error_catcher.py   # 错误捕捉师
│   │   │   ├── project_decomposer.py  # 项目拆解师
│   │   │   ├── role_matcher.py    # 角色匹配师
│   │   │   ├── collaboration_supervisor.py  # 协作督导
│   │   │   └── result_evaluator.py  # 成果评估师
│   │   ├── api/                   # 36个API路由模块（167+接口）
│   │   ├── core/                  # 核心配置（config/logger/exceptions/safety/rate_limiter/cache）
│   │   ├── graph/                 # LangGraph工作流（state/nodes/graph）
│   │   ├── models/                # 23个ORM数据模型
│   │   ├── schemas/               # Pydantic请求/响应模型
│   │   ├── algorithms/            # 4个学习算法
│   │   ├── services/              # 7个业务服务
│   │   ├── middleware/            # API性能监控中间件
│   │   └── main.py                # 应用入口
│   ├── .env.example               # 环境变量模板（30+配置项）
│   ├── requirements.txt           # Python依赖（32个包）
│   └── ai_learning_v2.db          # SQLite数据库
├── frontend/                       # 前端代码
│   ├── src/
│   │   ├── pages/                 # 28个路由页面
│   │   │   ├── teacher/           # 9个教师端页面
│   │   │   └── circuit-simulator/ # 电路模拟器（9个文件）
│   │   ├── components/            # 24个通用组件
│   │   │   └── kb/                # 知识库子组件（7个）
│   │   ├── services/              # API服务封装（30+服务对象）
│   │   ├── store/                 # Zustand状态管理（2个Store）
│   │   ├── hooks/                 # 自定义Hooks
│   │   ├── types/                 # TypeScript类型定义（450+行）
│   │   ├── utils/                 # 工具函数（等级/画像/错误）
│   │   ├── lib/                   # WikiLink解析器
│   │   ├── styles/                # Markdown样式
│   │   ├── App.tsx                # 路由配置（React Router v6）
│   │   └── main.tsx               # React入口
│   ├── e2e/                       # Playwright E2E测试（4个文件，39个用例）
│   ├── tailwind.config.js         # TailwindCSS配置（自定义颜色/动画/阴影）
│   ├── vite.config.ts             # Vite配置（代码分割/代理）
│   ├── playwright.config.ts       # Playwright配置
│   └── package.json               # 前端依赖
├── scripts/                        # 工具脚本
│   ├── test_api.py                 # API冒烟测试
│   └── test_llm.py                 # LLM调用测试
├── .gitignore
├── .dockerignore
├── .husky/pre-commit               # Git提交前钩子
├── Dockerfile                      # 多阶段Docker构建
├── docker-compose.yml              # Docker Compose配置
├── nginx.conf                      # Nginx反向代理配置
├── start.bat                       # Windows一键启动
└── README.md
```

---

## 开发指南

### 代码规范

- 后端：Python 3.11+，遵循PEP 8
- 前端：TypeScript，ESLint + Prettier
- Git：Husky + lint-staged（提交前自动检查）

### 添加新智能体

1. 在 `backend/app/agents/` 下创建新文件
2. 继承 `BaseAgent` 基类
3. 实现 `get_system_prompt()` 和 `process()` 方法
4. 在 `__init__.py` 中导出
5. 在 `api/` 下创建对应的API路由

### 添加新页面

1. 在 `frontend/src/pages/` 下创建新组件
2. 在 `App.tsx` 中添加路由（React.lazy懒加载）
3. 在 `Sidebar.tsx` 中添加导航项

### 添加新数据模型

1. 在 `backend/app/models/` 下创建或修改文件
2. 定义ORM模型类
3. 在 `main.py` 的lifespan中自动创建表
4. 在 `api/` 下创建对应的CRUD接口

### LLM提供商配置

- 通过 `DEFAULT_LLM_PROVIDER` 环境变量切换
- 统一接口：`LLMFactory.get_default_llm()`
- 支持 `ainvoke()`（非流式）、`astream()`（流式）、`generate_json()`（JSON输出）

---

## 系统验证

### 验证结果

| 检查项 | 状态 | 说明 |
|--------|------|------|
| TypeScript编译 | ✅ 通过 | 前端代码无编译错误 |
| API端点 | ✅ 通过 | 167+个API端点，36个模块 |
| 学生端API | ✅ 通过 | 30个核心端点全部正常 |
| 教师端API | ✅ 通过 | 10个核心端点全部正常 |
| 数据互通 | ✅ 通过 | 学生数据实时同步到教师端 |
| Agent功能 | ✅ 通过 | 12个智能体测试通过 |
| PPT生成 | ✅ 通过 | 异步任务+轮询状态 |
| E2E测试 | ✅ 通过 | 39个测试用例全部通过 |
| 前端构建 | ✅ 通过 | 无TypeScript错误 |

### 已实现功能清单（55项）

<details>
<summary>点击展开完整功能清单</summary>

#### 多智能体协作
1. ✅ 智能体基类框架（消息传递、工具注册、记忆系统、状态管理）
2. ✅ 12个智能体完整实现（4类：核心/知识/代码/协作）
3. ✅ LangGraph多智能体工作流编排（状态图驱动，条件路由，并行fan-out）
4. ✅ Agent工作流可视化（实时展示智能体协作状态、任务进度、执行日志）

#### 个性化学习
5. ✅ 学生画像（6维度：知识基础、认知风格、薄弱环节、兴趣领域、学习习惯、情感状态）
6. ✅ 学习路径（DAG路径规划+动态调整+依赖链查询）
7. ✅ 智能辅导（苏格拉底式问答+WebSocket流式+学习状态自动检测）
8. ✅ 艾宾浩斯复习提醒（基于遗忘曲线的智能复习推荐）
9. ✅ 新手引导问卷（首次登录个性化配置，支持多学科）

#### 内容生成
10. ✅ 资源生成（文档/题目/思维导图/代码，对接LangGraph真实智能体）
11. ✅ PPT自动生成（AI生成深度教学PPT，10种幻灯片类型）
12. ✅ 代码在线编译运行（Python AST安全检查+C语言gcc沙箱执行）
13. ✅ 文生图（火山引擎Seedream 3.0）
14. ✅ OCR识图（图片文字识别）
15. ✅ 每日测验（智能出题，自动批改）

#### 游戏化系统
16. ✅ 知识树成长系统（D3.js可视化，5种状态，等级提升动画）
17. ✅ 经验等级系统（10级：初学者→传奇，后端统一配置）
18. ✅ 学习挑战系统（游戏化任务地图，难度递增）
19. ✅ 六维排行榜（积分/连续/掌握/测验/AI协作/进步）
20. ✅ 游戏化基础（积分、成就、任务、排行榜）

#### 数据分析
21. ✅ Dashboard仪表盘（统计卡片、学习趋势、Agent工作流面板、成长时间轴）
22. ✅ 趋势分析与预测（6维度算法模型）
23. ✅ 成长时间轴（个性化里程碑展示）
24. ✅ 活跃日期统计（学习日历热力图）

#### 算法可视化
25. ✅ 算法动画（冒泡排序、快速排序、BFS/DFS、链表操作）
26. ✅ 伪代码高亮（动画同步+AI讲解）

#### 电路仿真
27. ✅ 电路仿真器（电阻、电压源、电流源、接地等组件）
28. ✅ 电路分析（基尔霍夫定律、MNA节点电压法）
29. ✅ 电路图可视化（SVG渲染，缩放、拖拽）
30. ✅ AI电路分析对话框

#### 团队协作
31. ✅ 项目拆解（C语言项目→任务树，内置经典项目库）
32. ✅ 角色匹配（能力画像→最优组队）
33. ✅ 协作督导（监控协作、检测阻塞/冲突、知识共享）
34. ✅ 成果评估（代码质量/协作效果/学习收获）

#### 知识管理
35. ✅ 知识图谱（结构化知识关系，约束资源生成和路径规划）
36. ✅ 知识库管理（文件夹/笔记/WikiLink/反向链接/知识图谱可视化）
37. ✅ 知识点体系（C语言16个知识点的内容库）

#### 学习工具
38. ✅ 学习日志与反思（康奈尔笔记、费曼学习法）
39. ✅ 收藏夹
40. ✅ 路径调整日志

#### 教师端
41. ✅ 教师首页（统计卡片、积分趋势图、快捷操作、活跃学生列表）
42. ✅ 作业管理（创建/编辑/删除/状态跟踪）
43. ✅ 学生管理（列表/搜索/详情/趋势分析）
44. ✅ 备课资源（PPT在线生成）
45. ✅ 学情分析（薄弱知识点、薄弱领域、学习洞察）
46. ✅ 班级学情（雷达图、排名表、多维度分析）
47. ✅ 班级对比（多班数据对比）
48. ✅ 报告导出（PDF/Excel/Word）

#### 系统能力
49. ✅ 多模型支持（5种LLM供应商，统一接口，一键切换）
50. ✅ JWT认证系统（注册/登录/Token刷新，学生/教师/管理员角色）
51. ✅ 防幻觉机制（JSON校验、代码语法检查、引用溯源、知识图谱约束、敏感词过滤）
52. ✅ 请求限流（滑动窗口，分级限流）
53. ✅ API性能监控（批量写入，异步持久化）
54. ✅ 全局错误边界（Sentry集成）
55. ✅ 新手引导（5步问卷，多学科支持）

</details>

---

## 许可证

MIT License
