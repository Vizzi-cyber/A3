# AI Learning System - 个性化学习平台

基于大模型的个性化资源生成与学习多智能体系统，第十五届中国软件杯大赛A3赛题作品。

## 技术架构

### 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                    前端 (React + TypeScript)                   │
├─────────────────────────────────────────────────────────────┤
│  React 18 + TypeScript + Ant Design 5 + Zustand + TailwindCSS  │
│  Vite (构建) + Recharts (可视化) + GSAP (动画) + D3.js (图谱)   │
└─────────────────────────────────────────────────────────────┘
                              │
                          REST API / WebSocket
                              │
┌─────────────────────────────────────────────────────────────┐
│              后端 (Python + FastAPI)                           │
├─────────────────────────────────────────────────────────────┤
│  FastAPI + LangGraph (多智能体编排) + SQLAlchemy + SQLite        │
│  12个智能体: 协作式多智能体系统                                   │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    大模型接入层                                │
├─────────────────────────────────────────────────────────────┤
│  统一接口支持: 智谱GLM / 讯飞星火 / DeepSeek / OpenAI / MiMo     │
└─────────────────────────────────────────────────────────────┘
```

### 后端技术栈 (Python + FastAPI)

| 技术 | 用途 |
|------|------|
| **FastAPI** | 高性能异步Web框架，30+ API模块 |
| **LangGraph** | 多智能体工作流编排，状态图驱动 |
| **LangChain** | LLM应用开发框架 |
| **SQLAlchemy** | ORM，支持 SQLite/PostgreSQL |
| **python-pptx** | AI驱动的PPT自动生成 |
| **uvicorn** | ASGI服务器，支持热重载 |
| **python-jose** | JWT 令牌管理 |
| **passlib** | 密码哈希处理 |
| **httpx** | 异步 HTTP 客户端 |
| **websockets** | WebSocket 实时通信 |

### 前端技术栈 (React + TypeScript)

| 技术 | 用途 |
|------|------|
| **React 18 + TypeScript** | UI框架，类型安全 |
| **Ant Design 5** | 企业级组件库 |
| **Zustand** | 轻量级状态管理 |
| **Recharts** | 数据可视化 |
| **D3.js** | 知识图谱可视化 |
| **GSAP** | 高性能动画引擎 |
| **TailwindCSS** | 原子化样式 |
| **Vite** | 构建工具，快速开发 |
| **Monaco Editor** | 代码编辑器 |
| **React Router** | 路由管理 |
| **Axios** | HTTP 客户端 |
| **React Markdown** | Markdown 渲染 |
| **KaTeX** | 数学公式渲染 |
| **Playwright** | E2E 测试 |

## 多智能体系统

### 核心智能体（LangGraph驱动）

| 智能体 | ID | 职责 |
|--------|-----|------|
| **课程设计师** | `course_designer` | 系统中枢，任务分解、流程编排、质量把控，协调其他智能体 |
| **画像师** | `profiler` | 分析学生数据，构建6维学生画像（知识基础/认知风格/薄弱环节/兴趣/习惯/情感） |
| **路径规划师** | `path_planner` | 基于DAG的个性化学习路径规划，受知识图谱约束 |
| **资源生成师** | `resource_generator` | 生成文档/题目/思维导图/代码，受知识图谱约束 |
| **辅导助手** | `tutor` | 苏格拉底式问答，学习状态感知（检测挫败/困惑/自信） |

### 知识体系智能体

| 智能体 | ID | 职责 |
|--------|-----|------|
| **知识图谱构建师** | `kg_builder` | 从知识点构建结构化知识图谱，约束路径规划和资源生成，防止幻觉 |
| **思维溯源师** | `misconception_tracer` | 反向推导学生错误原因，归类错误模型（概念混淆/逻辑缺失/语法惯性/零基础盲区） |

### 代码分析智能体

| 智能体 | ID | 职责 |
|--------|-----|------|
| **错误捕捉师** | `error_catcher` | 抓取代码中的语法错误、逻辑错误和思维误区，给出修复建议 |

### 团队协作智能体

| 智能体 | ID | 职责 |
|--------|-----|------|
| **项目拆解师** | `project_decomposer` | 将C语言项目拆解为可执行的任务树，内置经典项目库 |
| **角色匹配师** | `role_matcher` | 根据学生能力画像匹配最优组队与分工（架构师/开发者/测试员/UI开发/文档员） |
| **协作督导** | `collaboration_supervisor` | 监控团队协作，检测阻塞/冲突，促进知识共享，生成每日协作报告 |
| **成果评估师** | `result_evaluator` | 多维度评估项目成果（代码质量/协作效果/学习收获） |

### 协作架构

```
核心5智能体（LangGraph驱动）：
┌─────────────────┐
│ CourseDesigner   │ ← 任务入口，总控调度
│   ├→ Profiler    │ ← 先分析学生画像
│   ├→ PathPlanner │ ← 再规划学习路径
│   ├→ ResourceGen │ ← 然后生成资源
│   └→ Tutor       │ ← 最后辅导答疑
└─────────────────┘

团队协作4智能体（独立模块）：
┌─────────────────┐
│ ProjectDecomposer│ ← 拆解项目任务
│ RoleMatcher     │ ← 匹配团队角色
│ Collaboration   │ ← 监控协作过程
│ ResultEvaluator │ ← 评估最终成果
└─────────────────┘

知识体系2智能体：
┌─────────────────┐
│ KG Builder      │ ← 构建知识图谱
│ Misconception   │ ← 追溯思维误区
└─────────────────┘

代码分析1智能体：
┌─────────────────┐
│ ErrorCatcher    │ ← 捕捉代码错误
└─────────────────┘
```

## 快速启动

### 1. 环境要求

- Python 3.9+（推荐 3.11）
- Node.js 18+
- PostgreSQL 14+（可选，默认使用 SQLite）

### 2. 配置API密钥

```bash
copy backend\.env.example backend\.env
```

编辑 `backend\.env`，选择并配置大模型提供商：

**方式一：智谱AI（默认）**
```
DEFAULT_LLM_PROVIDER=bigmodel
BIGMODEL_API_KEY=your-bigmodel-key
```

**方式二：讯飞星火**
```
DEFAULT_LLM_PROVIDER=spark
SPARK_API_KEY=your-api-key
```

**方式三：DeepSeek**
```
DEFAULT_LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=your-deepseek-key
```

**方式四：OpenAI**
```
DEFAULT_LLM_PROVIDER=openai
OPENAI_API_KEY=your-openai-key
```

**方式五：小米 MiMo**
```
DEFAULT_LLM_PROVIDER=mimo
MIMO_API_KEY=your-mimo-key
```

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
│   │   ├── api/                   # API路由（30+ 模块，100+ 接口）
│   │   │   ├── auth.py            # JWT 认证（登录/注册/Token刷新）
│   │   │   ├── profile.py         # 学生画像 API
│   │   │   ├── resource.py        # 资源生成 API（含代码安全执行）
│   │   │   ├── learning_path.py   # 学习路径 API（DAG 规划）
│   │   │   ├── tutor.py           # 智能辅导 API（WebSocket 流式）
│   │   │   ├── dashboard.py       # Dashboard 统计 + 成长时间轴
│   │   │   ├── gamification.py    # 游戏化（积分/成就/排行榜）
│   │   │   ├── gamification_tree.py   # 知识树成长系统 + 等级配置
│   │   │   ├── gamification_challenge.py  # 学习挑战 + 六维排行榜
│   │   │   ├── knowledge_graph.py  # 知识图谱管理
│   │   │   ├── knowledge_base.py  # 知识库管理（文件夹/笔记/WikiLink）
│   │   │   ├── agent_flow.py      # Agent 工作流可视化 API
│   │   │   ├── ppt.py             # PPT 自动生成 API
│   │   │   ├── knowledge.py       # 知识点管理
│   │   │   ├── learning_data.py   # 学习数据上报
│   │   │   ├── trend.py           # 趋势分析与预测
│   │   │   ├── image.py           # 文生图
│   │   │   ├── ocr.py             # OCR 识图
│   │   │   ├── log_reflection.py  # 学习日志与反思
│   │   │   ├── favorites.py       # 收藏夹
│   │   │   ├── daily_quiz.py      # 每日测验
│   │   │   ├── error_catcher.py   # 错误捕捉 API
│   │   │   ├── misconception_tracer.py  # 思维溯源 API
│   │   │   ├── project_decomposer.py  # 项目拆解 API
│   │   │   ├── role_matcher.py    # 角色匹配 API
│   │   │   ├── collaboration_supervisor.py  # 协作督导 API
│   │   │   ├── result_evaluator.py  # 成果评估 API
│   │   │   ├── teacher.py         # 教师端 API
│   │   │   ├── onboarding.py      # 新手引导 API
│   │   │   ├── matching.py        # 匹配推荐 API
│   │   │   ├── monitoring.py      # 系统监控 API
│   │   │   ├── path_adjustment_log_api.py  # 路径调整日志 API
│   │   │   └── circuit_analysis.py  # 电路分析 API
│   │   ├── core/                  # 核心配置
│   │   │   ├── config.py          # 配置管理（支持5种LLM提供商）
│   │   │   ├── logger.py          # 日志配置
│   │   │   ├── exceptions.py      # 全局异常处理
│   │   │   ├── safety.py          # 安全与防幻觉（敏感词过滤、JSON校验、代码语法检查、引用溯源）
│   │   │   ├── rate_limiter.py    # 请求限流
│   │   │   └── cache.py           # 缓存管理
│   │   ├── graph/                 # LangGraph 工作流
│   │   │   ├── state.py           # 共享状态定义
│   │   │   ├── nodes.py           # 智能体节点
│   │   │   └── graph.py           # 状态图构建器
│   │   ├── models/                # SQLAlchemy 数据模型（15个）
│   │   │   ├── user.py            # 用户模型
│   │   │   ├── student.py         # 学生画像模型
│   │   │   ├── knowledge.py       # 知识点/学习记录/测验/资源任务模型
│   │   │   ├── trend.py           # 趋势数据模型
│   │   │   ├── gamification.py    # 游戏化模型（积分/成就/任务/排行榜）
│   │   │   ├── log_reflection.py  # 学习日志/反思模型
│   │   │   ├── favorites.py       # 收藏夹模型
│   │   │   ├── monitor.py         # API监控/LLM调用/系统健康模型
│   │   │   ├── tutor_qa.py        # 导师问答模型
│   │   │   ├── kb_note.py         # 知识库文件夹/笔记模型
│   │   │   └── path_adjustment_log.py  # 路径调整日志模型
│   │   ├── schemas/               # Pydantic 请求/响应模型
│   │   ├── algorithms/            # 学习算法（趋势预测、效果评估）
│   │   ├── services/              # 业务服务层
│   │   │   ├── llm_factory.py     # LLM工厂（统一接口，支持5种提供商）
│   │   │   ├── content_library.py # C语言内容库
│   │   │   ├── ppt_generator.py   # PPT 自动生成服务
│   │   │   ├── image_generation.py  # 文生图服务
│   │   │   ├── path_adjustment_engine.py  # 路径调整引擎
│   │   │   └── gamification_service.py  # 游戏化服务
│   │   ├── middleware/            # 中间件
│   │   │   └── api_monitor.py     # API性能监控（批量写入模式）
│   │   └── main.py                # 应用入口
│   ├── .env.example               # 环境变量模板
│   └── requirements.txt           # Python 依赖
├── frontend/                       # 前端代码
│   ├── src/
│   │   ├── components/            # 通用组件
│   │   │   ├── AgentFlowPanel.tsx     # Agent 工作流可视化面板
│   │   │   ├── AlgorithmVisualizer.tsx # 算法动画组件（冒泡/快排/BFS/DFS/链表）
│   │   │   ├── GrowthTimeline.tsx     # 成长时间轴
│   │   │   ├── PPTGenerator.tsx       # PPT 生成器
│   │   │   ├── AppHeader.tsx          # 顶部导航
│   │   │   ├── Sidebar.tsx            # 侧边栏（含今日学习时长）
│   │   │   ├── StatCard.tsx           # 统计卡片
│   │   │   ├── OnboardingQuestionnaire.tsx  # 新手引导问卷
│   │   │   ├── GlobalToast.tsx        # 全局提示
│   │   │   ├── ErrorBoundary.tsx      # 错误边界
│   │   │   ├── ChatPanel.tsx          # 聊天面板
│   │   │   ├── CodeEditor.tsx         # 代码编辑器
│   │   │   ├── DailyChallenge.tsx     # 每日挑战
│   │   │   ├── Leaderboard.tsx        # 排行榜
│   │   │   ├── MarkdownViewer.tsx     # Markdown查看器
│   │   │   ├── MindmapViewer.tsx      # 思维导图查看器
│   │   │   ├── PageCard.tsx           # 页面卡片
│   │   │   ├── SectionCard.tsx        # 区域卡片
│   │   │   ├── StatRow.tsx            # 统计行
│   │   │   ├── StatusIcon.tsx         # 状态图标
│   │   │   ├── StatusTag.tsx          # 状态标签
│   │   │   ├── AdjustmentLogPanel.tsx # 路径调整日志面板
│   │   │   └── kb/                    # 知识库组件
│   │   ├── pages/                 # 页面组件
│   │   │   ├── Dashboard.tsx          # 仪表盘（AgentFlow + 成长时间轴）
│   │   │   ├── LandingPage.tsx        # 落地页
│   │   │   ├── Login.tsx             # 登录/注册
│   │   │   ├── KnowledgeTree.tsx      # 知识树成长系统
│   │   │   ├── LearningChallenge.tsx  # 学习挑战任务地图
│   │   │   ├── LeaderboardPlus.tsx    # 六维排行榜
│   │   │   ├── LearningPath.tsx       # 学习路径（DAG可视化）
│   │   │   ├── ResourceCenter.tsx     # 资源中心（含艾宾浩斯复习提醒）
│   │   │   ├── ResourceDetail.tsx     # 资源详情（含算法可视化Tab）
│   │   │   ├── Tutor.tsx             # AI导师（含学习状态感知）
│   │   │   ├── Profile.tsx           # 学生画像
│   │   │   ├── PersonalSpace.tsx     # 个人空间
│   │   │   ├── KnowledgeBase.tsx     # 知识库管理（文件夹/笔记/WikiLink）
│   │   │   ├── ErrorDiagnosis.tsx    # 错误诊断
│   │   │   ├── ErrorDiagnosisC.tsx   # C语言错误诊断
│   │   │   ├── ProjectCollaboration.tsx  # 项目协作
│   │   │   ├── TeacherDashboard.tsx  # 教师仪表盘
│   │   │   ├── circuit-simulator/    # 电路仿真模块
│   │   │   │   ├── CircuitSimulator.tsx  # 电路仿真主组件
│   │   │   │   ├── Canvas.tsx        # SVG画布（组件拖拽/连线）
│   │   │   │   ├── ComponentPalette.tsx  # 组件面板
│   │   │   │   ├── PropertiesPanel.tsx   # 属性面板
│   │   │   │   ├── AiAnalysisDialog.tsx  # AI分析对话框
│   │   │   │   ├── MeasurementOverlay.tsx # 测量覆盖层
│   │   │   │   ├── ToolBar.tsx       # 工具栏
│   │   │   │   ├── store.ts          # 状态管理
│   │   │   │   ├── types.ts          # 类型定义
│   │   │   │   └── utils/            # 工具函数
│   │   │   │       ├── circuit-utils.ts  # 电路工具
│   │   │   │       ├── constants.ts      # 常量定义
│   │   │   │       ├── drawing-utils.ts  # 绘图工具
│   │   │   │       └── mna-solver.ts     # MNA求解器（节点电压法）
│   │   │   └── NotFound.tsx         # 404页面
│   │   ├── services/              # API服务封装
│   │   │   └── api.ts             # Axios 封装（含Token拦截器）
│   │   ├── store/                 # Zustand 状态管理
│   │   ├── hooks/                 # 自定义Hooks
│   │   ├── types/                 # TypeScript 类型定义
│   │   ├── utils/                 # 工具函数
│   │   │   └── level.ts           # 等级计算工具（统一管理）
│   │   ├── styles/                # 样式文件
│   │   ├── lib/                   # 工具库
│   │   ├── App.tsx                # 应用入口（路由配置）
│   │   └── main.tsx               # React入口
│   ├── e2e/                       # Playwright E2E 测试
│   ├── tailwind.config.js         # TailwindCSS 配置（含自定义动画/渐变）
│   ├── vite.config.ts             # Vite 配置
│   ├── playwright.config.ts       # Playwright 配置
│   └── package.json
├── scripts/                        # 工具脚本
│   └── test_api.py                 # API 测试脚本
├── .gitignore                      # Git忽略配置
├── Dockerfile                      # Docker 构建文件
├── docker-compose.yml              # Docker Compose 配置
├── nginx.conf                      # Nginx 反向代理配置
├── start.bat                       # Windows 一键启动
└── README.md
```

## 核心功能

### 已实现功能（45项）

#### 多智能体协作
1. ✅ 智能体基类框架（消息传递、工具注册、记忆系统、状态管理）
2. ✅ 12个智能体完整实现（4类：核心/知识/代码/协作）
3. ✅ LangGraph 多智能体工作流编排（状态图驱动，条件路由）
4. ✅ Agent 工作流可视化（实时展示智能体协作状态、任务进度、执行日志）

#### 个性化学习
5. ✅ 学生画像 API（6维度：知识基础、认知风格、薄弱环节、兴趣领域、学习习惯、情感状态）
6. ✅ 学习路径 API（DAG 路径规划 + 动态调整 + 依赖链查询）
7. ✅ 智能辅导 API（苏格拉底式问答 + WebSocket 流式 + 学习状态自动检测）
8. ✅ 艾宾浩斯复习提醒（基于遗忘曲线的智能复习推荐）
9. ✅ 新手引导问卷（首次登录个性化配置，支持多学科）

#### 内容生成
10. ✅ 资源生成 API（对接 LangGraph + 真实智能体，文档/题目/思维导图/代码）
11. ✅ PPT 自动生成（AI生成深度学习PPT，含代码、算法步骤、复杂度分析）
12. ✅ 代码在线编译运行（Python AST 安全检查 + C 语言 gcc 沙箱执行）
13. ✅ 文生图（AI 生成学习插图，支持火山引擎/火山方舟）
14. ✅ OCR 识图（图片文字识别，支持文件上传）
15. ✅ 每日测验（智能出题，自动批改，学习统计）

#### 游戏化系统
16. ✅ 知识树成长系统（可视化知识树，学习越多树越茂盛，等级提升动画）
17. ✅ 经验等级系统（后端统一配置 /level-config，10级：初学者 → 传奇）
18. ✅ 学习挑战系统（任务地图，难度递增，完成获得奖励）
19. ✅ 六维排行榜（积分/连续/掌握/测验/AI协作/进步 多维度排名）
20. ✅ 游戏化基础（积分、成就、任务、排行榜，支持增删改查）

#### 数据分析
21. ✅ Dashboard 仪表盘（统计卡片、学习趋势分析、3D 滚动旅程、Agent 工作流面板、成长时间轴）
22. ✅ 趋势分析与预测（算法模型评估学习效果、预测掌握度、预警干预）
23. ✅ 成长时间轴（个性化里程碑展示：能力提升/预警/解锁成就）
24. ✅ 活跃日期统计（学习日历热力图）

#### 算法可视化
25. ✅ 算法动画（冒泡排序、快速排序、BFS/DFS、链表操作的 Canvas 动画）
26. ✅ 伪代码高亮（动画同步高亮当前执行行 + AI 讲解）

#### 电路仿真
27. ✅ 电路仿真器（支持电阻、电压源、电流源、接地等组件）
28. ✅ 电路分析（基尔霍夫定律、MNA节点电压法、网孔电流法）
29. ✅ 电路图可视化（SVG渲染，支持缩放、拖拽、选择）
30. ✅ AI电路分析对话框（智能分析电路特性）

#### 团队协作
31. ✅ 项目拆解（将C语言项目拆解为可执行的任务树，内置经典项目库）
32. ✅ 角色匹配（根据能力画像匹配最优组队与分工）
33. ✅ 协作督导（监控团队协作，检测阻塞/冲突，知识共享，进度同步）
34. ✅ 成果评估（多维度评估代码质量、协作效果、学习收获）

#### 知识管理
35. ✅ 知识图谱（结构化知识关系，约束资源生成和路径规划，防止幻觉）
36. ✅ 知识库管理（文件夹/笔记/WikiLink/反向链接/知识图谱可视化）
37. ✅ 知识点体系（C语言 16 个知识点的内容库）

#### 学习工具
38. ✅ 学习日志与反思（康奈尔笔记、费曼学习法）
39. ✅ 收藏夹（资源收藏管理）
40. ✅ 路径调整日志（记录学习路径调整历史）

#### 教师端
41. ✅ 教师首页（学生统计、积分图表、快捷操作、活跃学生列表）
42. ✅ 作业管理（作业创建、编辑、删除、状态跟踪）
43. ✅ 学生管理（学生列表、搜索、详情查看、趋势分析）
44. ✅ 备课资源（PPT/视频/代码/思维导图生成）
45. ✅ 学情分析（弱项分析、学习洞察、薄弱知识点统计）
46. ✅ 班级学情（雷达图、排名表、多维度分析）
47. ✅ 班级对比（多班对比分析、数据对比）
48. ✅ 报告导出（PDF/Excel/Word导出、自定义导出）
49. ✅ 系统设置（账户信息、通知设置、系统信息）

#### 系统能力
43. ✅ 多模型支持（智谱GLM / 讯飞星火 / DeepSeek / OpenAI / MiMo，统一接口，一键切换）
44. ✅ JWT 认证系统（注册/登录/Token刷新，支持学生/教师/管理员角色）
45. ✅ 防幻觉机制（JSON校验、代码语法检查、引用溯源、知识图谱约束、敏感词过滤）

## 前端页面结构

### 学生端页面 (`/*`)
| 路由 | 页面 | 功能 |
|------|------|------|
| `/` | 学习仪表盘 | 统计卡片、学习趋势、Agent工作流、成长时间轴 |
| `/profile` | 对话画像 | 学生画像展示、认知风格分析 |
| `/learning-path` | 学习路径 | DAG可视化、路径调整、依赖链查询 |
| `/resources` | 学习中心 | 资源生成、代码编辑器、思维导图 |
| `/resource/:kpId` | 资源详情 | 知识点资源、算法可视化、在线编程 |
| `/challenges` | 知识冒险 | 学习挑战任务地图、难度递增 |
| `/tutor` | 智能辅导 | 苏格拉底式问答、学习状态感知 |
| `/error-diagnosis` | 错误诊断 | 代码错误分析、思维误区追溯 |
| `/project-collaboration` | 项目协作 | 项目拆解、角色匹配、协作督导 |
| `/personal` | 个人空间 | 学习日志、反思笔记、康奈尔笔记 |
| `/knowledge-base` | 知识库 | 文件夹管理、笔记编辑、WikiLink、知识图谱 |
| `/leaderboard` | 排行榜 | 六维排行榜、积分排名 |
| `/circuit-simulator` | 电路仿真 | 电路搭建、MNA分析、AI分析 |

### 教师端页面 (`/teacher/*`)
| 路由 | 页面 | 功能 |
|------|------|------|
| `/teacher` | 教师首页 | 学生统计卡片、积分趋势图、快捷操作、活跃学生列表 |
| `/teacher/assignments` | 作业管理 | 作业创建、编辑、删除、提交状态跟踪 |
| `/teacher/students` | 学生管理 | 学生列表、搜索、详情查看、趋势分析 |
| `/teacher/resources` | 备课资源 | PPT/视频/代码/思维导图生成 |
| `/teacher/analytics` | 学情分析 | 弱项分析、学习洞察、薄弱知识点统计 |
| `/teacher/class-analytics` | 班级学情 | 雷达图、排名表、多维度分析 |
| `/teacher/class-comparison` | 班级对比 | 多班对比分析、数据对比 |
| `/teacher/reports` | 报告导出 | PDF/Excel/Word导出、自定义导出 |
| `/teacher/settings` | 系统设置 | 账户信息、通知设置、系统信息 |
| `/teacher/personal` | 个人空间 | 教师个人信息、笔记管理 |

## API接口列表（30+ 模块，100+ 接口）

### 用户认证 (`/api/v1/auth`)
- `POST /register` — 学生注册
- `POST /register-teacher` — 教师注册
- `POST /login` — 登录（返回JWT Token）
- `GET /me` — 获取当前用户信息
- `POST /_debug/validate-password` — 调试：验证密码

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

### Agent 工作流 (`/api/v1/agent-flow`)
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

### PPT 自动生成 (`/api/v1/ppt`)
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
- `GET /leaderboard/{period}` — 排行榜（daily/weekly/monthly/all）

### 知识树成长系统 (`/api/v1/gamification-tree`)
- `GET /level-config` — 获取等级配置
- `GET /{student_id}/tree` — 获取知识树状态

### 学习挑战 (`/api/v1/gamification-challenge`)
- `GET /{student_id}/challenges` — 挑战列表
- `GET /leaderboard/{dimension}` — 六维排行榜（points/streak/mastery/quiz/ai_collab/improvement）

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

### AI 工具 (`/api/v1/image`, `/api/v1/ocr`)
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
- `GET /student/{student_id}/detail` — 学生详情（画像、积分、学习统计）
- `GET /student/{student_id}/progress` — 学生学习进度
- `GET /student/{student_id}/scores` — 学生成绩数据
- `GET /student/{student_id}/trends` — 学生趋势分析
- `GET /student/{student_id}/reflections` — 学生反思记录
- `GET /ranking` — 学生排行榜（支持按积分/学时/分数排序）
- `GET /weak-points` — 薄弱知识点统计（弱项标签+薄弱领域）

### 教师端页面 (`/teacher/*`)
| 路由 | 页面 | 功能 |
|------|------|------|
| `/teacher` | 教师首页 | 学生统计卡片、积分趋势图、快捷操作、活跃学生列表 |
| `/teacher/assignments` | 作业管理 | 作业创建、编辑、删除、提交状态跟踪 |
| `/teacher/students` | 学生管理 | 学生列表、搜索、详情查看、趋势分析 |
| `/teacher/resources` | 备课资源 | PPT/视频/代码/思维导图生成 |
| `/teacher/analytics` | 学情分析 | 弱项分析、学习洞察、薄弱知识点统计 |
| `/teacher/class-analytics` | 班级学情 | 雷达图、排名表、多维度分析 |
| `/teacher/class-comparison` | 班级对比 | 多班对比分析、数据对比 |
| `/teacher/reports` | 报告导出 | PDF/Excel/Word导出、自定义导出 |
| `/teacher/settings` | 系统设置 | 账户信息、通知设置、系统信息 |
| `/teacher/personal` | 个人空间 | 教师个人信息、笔记管理 |

### 匹配推荐 (`/api/v1/matching`)
- `POST /resources` — 资源推荐
- `POST /paths` — 路径推荐

### 系统监控 (`/api/v1/monitoring`)
- `GET /api-stats` — API统计
- `GET /llm-stats` — LLM调用统计
- `GET /health` — 健康检查
- `POST /health/record` — 记录健康数据

### 新手引导 (`/api/v1/onboarding`)
- `GET /check` — 检查是否需要引导
- `POST /submit` — 提交引导问卷

### 路径调整日志 (`/api/v1/path-adjustment`)
- `GET /{student_id}/logs` — 获取调整日志

### 电路分析 (`/api/v1/circuit-analysis`)
- `POST /analyze` — 分析电路

### 收藏夹 (`/api/v1/favorites`)
- `GET /{student_id}` — 获取收藏
- `POST /{student_id}` — 添加收藏
- `DELETE /{student_id}/{favorite_id}` — 删除收藏

## 测试账号

| 角色 | 账号 | 密码 | 说明 |
|------|------|------|------|
| **教师** | T001 | Teacher123 | 教师端所有功能 |
| **学生** | student_001 | 123456 | 学生端所有功能 |
| **学生** | student_002 | 123456 | 学生端所有功能 |
| **学生** | student_003 | 123456 | 学生端所有功能 |

## 测试

```bash
# Playwright API 测试（22个用例）
cd frontend
npx playwright test e2e/api.spec.ts --reporter=list
```

测试覆盖：认证、画像、Dashboard、学习路径、资源生成、辅导、知识点、游戏化（积分/成就/挑战/排行榜/等级配置）、知识树、成长时间轴、Agent工作流、PPT生成、OpenAPI。

## Docker 部署

```bash
# 1. 确保已安装 Docker 和 Docker Compose
# 2. 配置环境变量
copy backend\.env.example backend\.env
# 编辑 backend\.env 填写 API 密钥

# 3. 构建并启动
docker-compose up --build -d

# 4. 访问应用
# 前端: http://localhost
# 后端API: http://localhost:8000
# API文档: http://localhost:8000/docs
```

## 开发说明

### 代码规范
- 后端：Python 3.11+，遵循 PEP 8
- 前端：TypeScript，ESLint + Prettier
- 提交规范：使用 Husky + lint-staged

### 添加新智能体
1. 在 `backend/app/agents/` 下创建新文件
2. 继承 `BaseAgent` 基类
3. 实现 `get_system_prompt()` 和 `process()` 方法
4. 在 `__init__.py` 中导出
5. 在 `api/` 下创建对应的 API 路由

### 添加新页面
1. 在 `frontend/src/pages/` 下创建新组件
2. 在 `App.tsx` 中添加路由
3. 在 `Sidebar.tsx` 中添加导航项

### LLM提供商配置
- 支持5种LLM提供商：智谱GLM、讯飞星火、DeepSeek、OpenAI、小米MiMo
- 通过 `DEFAULT_LLM_PROVIDER` 环境变量切换
- 统一接口：`BaseLLM.ainvoke()` 和 `BaseLLM.astream()`

## 系统验证

### 验证结果（2024-06-15）

| 检查项 | 状态 | 说明 |
|--------|------|------|
| TypeScript编译 | ✅ 通过 | 前端代码无编译错误 |
| API端点 | ✅ 通过 | 135个API端点，30+模块 |
| 学生端API | ✅ 通过 | 30个核心端点全部正常 |
| 教师端API | ✅ 通过 | 10个核心端点全部正常 |
| 数据互通 | ✅ 通过 | 学生数据实时同步到教师端 |
| Agent功能 | ✅ 通过 | 5个核心Agent测试通过 |
| PPT生成 | ✅ 通过 | 异步任务+轮询状态 |
| 前端构建 | ✅ 通过 | 无TypeScript错误 |

### 数据库状态

| 表名 | 记录数 | 说明 |
|------|--------|------|
| users | 20+ | 学生+教师账号 |
| learning_records | 79 | 学习记录 |
| quiz_results | 46 | 测验结果 |
| game_points | 17 | 游戏积分 |
| kb_notes | 20 | 知识库笔记 |
| student_profiles | 3 | 学生画像 |
| student_trends | 3 | 趋势数据 |

### 核心数据流

```
学生学习 → learning_records → Dashboard统计
         → quiz_results → 教师端弱项分析
         → game_points → 排行榜+积分图表
         → kb_notes → 知识库管理
         → reflections → 学习反思
```

## 许可证

MIT License
