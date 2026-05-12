# AI Learning System - 个性化学习平台

基于大模型的个性化资源生成与学习多智能体系统，第十五届中国软件杯大赛A3赛题作品。

## 技术架构

### 后端 (Python + FastAPI)
- **FastAPI**: 高性能异步Web框架
- **LangGraph**: 多智能体工作流编排（5个智能体协作）
- **大模型接入**: 讯飞星火 / DeepSeek / OpenAI（统一接口，一键切换）
- **SQLite/PostgreSQL**: 主数据库（默认 SQLite）
- **python-pptx**: AI驱动的PPT自动生成

### 前端 (React + TypeScript)
- **React 18** + **TypeScript**: UI框架
- **Ant Design 5**: 组件库
- **Zustand**: 状态管理
- **Recharts**: 数据可视化
- **GSAP**: 高性能动画引擎
- **TailwindCSS**: 原子化样式

### 多智能体系统
| 智能体 | 职责 |
|--------|------|
| Supervisor（课程设计师） | 总控调度，协调其他智能体 |
| Profiler（画像师） | 分析学习数据，构建6维学生画像 |
| PathPlanner（路径规划师） | 基于DAG的个性化学习路径规划 |
| ResourceGen（资源生成师） | 自适应难度的资源生成（文档/题目/思维导图/代码） |
| Tutor（辅导助手） | 苏格拉底式问答，学习状态感知 |

## 快速启动

### 1. 环境要求
- Python 3.9+（推荐 3.11）
- Node.js 18+
- PostgreSQL 14+（可选，默认使用 SQLite）
- Redis 7+（可选）

### 2. 配置API密钥

```bash
copy backend\.env.example backend\.env
```

编辑 `backend\.env`，选择并配置大模型提供商：

**方式一：讯飞星火（默认）**
```
DEFAULT_LLM_PROVIDER=spark
SPARK_APP_ID=your-app-id
SPARK_API_KEY=your-api-key
SPARK_API_SECRET=your-api-secret
```

**方式二：DeepSeek**
```
DEFAULT_LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=your-deepseek-key
```

**方式三：OpenAI**
```
DEFAULT_LLM_PROVIDER=openai
OPENAI_API_KEY=your-openai-key
```

### 3. 启动服务

**Windows:**
```bash
start.bat
```

**手动启动:**
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
│   │   ├── agents/                # 智能体模块
│   │   │   ├── base.py            # 智能体基类
│   │   │   ├── course_designer.py # 课程设计师（主管）
│   │   │   ├── profiler.py        # 画像师
│   │   │   ├── resource_generator.py  # 资源生成师
│   │   │   ├── path_planner.py    # 路径规划师
│   │   │   └── tutor.py           # 辅导助手（含学习状态感知）
│   │   ├── api/                   # API路由（20+ 模块）
│   │   │   ├── auth.py            # JWT 认证
│   │   │   ├── profile.py         # 学生画像 API
│   │   │   ├── resource.py        # 资源生成 API（含代码安全执行）
│   │   │   ├── learning_path.py   # 学习路径 API（DAG 规划）
│   │   │   ├── tutor.py           # 智能辅导 API（WebSocket 流式）
│   │   │   ├── dashboard.py       # Dashboard 统计 + 成长时间轴
│   │   │   ├── gamification.py    # 游戏化（积分/成就/排行榜）
│   │   │   ├── gamification_tree.py   # 知识树成长系统 + 等级配置
│   │   │   ├── gamification_challenge.py  # 学习挑战 + 六维排行榜
│   │   │   ├── agent_flow.py      # Agent 工作流可视化 API
│   │   │   ├── ppt.py             # PPT 自动生成 API
│   │   │   ├── knowledge.py       # 知识点管理
│   │   │   ├── learning_data.py   # 学习数据上报
│   │   │   ├── trend.py           # 趋势分析与预测
│   │   │   ├── image.py           # 文生图
│   │   │   ├── ocr.py             # OCR 识图
│   │   │   ├── log_reflection.py  # 学习日志与反思
│   │   │   └── favorites.py       # 收藏夹
│   │   ├── core/                  # 核心配置
│   │   ├── graph/                 # LangGraph 工作流（含事件推送）
│   │   │   ├── state.py           # 共享状态定义
│   │   │   ├── nodes.py           # 智能体节点（含AgentFlow事件推送）
│   │   │   └── graph.py           # 状态图构建器
│   │   ├── models/                # SQLAlchemy 数据模型
│   │   ├── schemas/               # Pydantic 请求/响应模型
│   │   ├── algorithms/            # 学习算法（趋势预测、效果评估）
│   │   ├── services/
│   │   │   ├── spark_llm.py       # 讯飞星火大模型封装
│   │   │   ├── content_library.py # C语言内容库
│   │   │   └── ppt_generator.py   # PPT 自动生成服务
│   │   └── main.py
│   └── requirements.txt
├── frontend/                       # 前端代码
│   ├── src/
│   │   ├── components/
│   │   │   ├── AgentFlowPanel.tsx     # Agent 工作流可视化面板
│   │   │   ├── AlgorithmVisualizer.tsx# 算法动画组件
│   │   │   ├── GrowthTimeline.tsx     # 成长时间轴
│   │   │   ├── PPTGenerator.tsx       # PPT 生成器
│   │   │   ├── AppHeader.tsx          # 顶部导航
│   │   │   ├── Sidebar.tsx            # 侧边栏
│   │   │   ├── StatCard.tsx           # 统计卡片
│   │   │   └── ...
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx          # 仪表盘（AgentFlow + 成长时间轴）
│   │   │   ├── KnowledgeTree.tsx      # 知识树成长系统
│   │   │   ├── LearningChallenge.tsx  # 学习挑战任务地图
│   │   │   ├── LeaderboardPlus.tsx    # 六维排行榜
│   │   │   ├── LearningPath.tsx       # 学习路径
│   │   │   ├── ResourceCenter.tsx     # 学习中心（含艾宾浩斯复习提醒）
│   │   │   ├── ResourceDetail.tsx     # 资源详情（含算法可视化Tab）
│   │   │   ├── Tutor.tsx             # AI导师（含学习状态感知）
│   │   │   ├── Profile.tsx           # 学生画像
│   │   │   ├── PersonalSpace.tsx     # 个人空间
│   │   │   └── Login.tsx            # 登录/注册
│   │   ├── services/api.ts          # API 服务（axios 封装）
│   │   ├── store/                   # Zustand 状态管理
│   │   ├── utils/level.ts           # 等级计算工具（统一管理）
│   │   └── types/                   # TypeScript 类型定义
│   ├── e2e/api.spec.ts             # Playwright E2E 测试（22个用例）
│   ├── tailwind.config.js
│   └── package.json
├── scripts/
├── docs/
└── README.md
```

## 核心功能

### 多智能体协作
1. **Agent工作流可视化** — 实时展示5个智能体的协作状态、任务进度、执行日志
2. **LangGraph编排** — Supervisor调度 → Profiler画像 → PathPlanner规划 → ResourceGen生成 → Tutor辅导

### 个性化学习
3. **6维学生画像** — 知识基础、认知风格、薄弱环节、兴趣领域、学习习惯、情感状态
4. **DAG学习路径** — 基于知识图谱的有向无环图路径规划，动态调整
5. **AI导师** — 苏格拉底式问答，自动检测学习状态（挫败/困惑/自信），自适应语气
6. **艾宾浩斯复习** — 基于遗忘曲线的智能复习提醒

### 内容生成
7. **PPT自动生成** — 输入主题，AI生成深度学习PPT（含代码、算法步骤、复杂度分析）
8. **资源生成** — 文档、题目、思维导图、代码，自适应难度
9. **代码在线运行** — Python AST安全检查 + C语言gcc沙箱执行
10. **文生图/OCR** — AI插图生成、图片文字识别

### 游戏化系统
11. **知识树成长** — 可视化知识树，学习越多树越茂盛，等级提升动画
12. **等级系统** — 后端统一配置（/level-config），10级：初学者 → 传奇
13. **学习挑战** — 任务地图，难度递增，完成获得奖励
14. **六维排行榜** — 积分/连续/掌握/测验/AI协作/进步 多维度排名
15. **成就系统** — 学习里程碑解锁，积分奖励

### 数据分析
16. **Dashboard仪表盘** — 统计卡片、学习趋势、Agent工作流、成长时间轴
17. **趋势分析** — 算法模型评估学习效果，预测掌握度，预警干预
18. **成长时间轴** — 个性化里程碑展示，能力提升/预警/成就事件

### 算法可视化
19. **算法动画** — 冒泡排序、快速排序、BFS/DFS、链表操作的Canvas动画
20. **伪代码高亮** — 动画同步高亮当前执行行

### 系统能力
21. **JWT认证** — 注册/登录/Token刷新
22. **防幻觉机制** — JSON校验、代码语法检查、引用溯源
23. **内容安全过滤** — 敏感词过滤、Prompt安全加固
24. **学习日志与反思** — 康奈尔笔记、费曼学习法

## 测试

```bash
# Playwright API 测试（22个用例，全量通过）
cd frontend
npx playwright test e2e/api.spec.ts --reporter=list
```

测试覆盖：认证、画像、Dashboard、学习路径、资源生成、辅导、知识点、游戏化（积分/成就/挑战/排行榜/等级配置）、知识树、成长时间轴、Agent工作流、PPT生成、OpenAPI。

## API接口列表

### 用户认证
- `POST /api/v1/auth/login` — 登录
- `POST /api/v1/auth/register` — 注册
- `GET /api/v1/auth/me` — 获取当前用户

### 学生画像
- `GET /api/v1/profile/{student_id}` — 获取画像
- `POST /api/v1/profile/{student_id}/update` — 更新画像
- `GET /api/v1/profile/{student_id}/summary` — 获取摘要
- `POST /api/v1/profile/{student_id}/initialize` — 初始化画像
- `POST /api/v1/profile/{student_id}/analyze-conversation` — 对话分析

### Dashboard
- `GET /api/v1/dashboard/{student_id}/summary` — 仪表盘统计
- `GET /api/v1/dashboard/{student_id}/timeline` — 成长时间轴

### Agent 工作流
- `POST /api/v1/agent-flow/run` — 启动智能体工作流
- `GET /api/v1/agent-flow/{run_id}/status` — 查询工作流状态

### 学习路径
- `POST /api/v1/learning-path/generate` — 生成路径
- `GET /api/v1/learning-path/{student_id}/current` — 当前路径
- `POST /api/v1/learning-path/{student_id}/adjust` — 调整路径
- `POST /api/v1/learning-path/dag/generate` — DAG路径生成

### 资源生成
- `POST /api/v1/resource/generate` — 生成资源
- `GET /api/v1/resource/task/{task_id}` — 查询任务状态
- `POST /api/v1/resource/document/generate` — 生成文档
- `POST /api/v1/resource/questions/generate` — 生成题目
- `POST /api/v1/resource/mindmap/generate` — 生成思维导图
- `POST /api/v1/resource/code/generate` — 生成代码
- `POST /api/v1/resource/code/execute` — 在线运行代码

### PPT 自动生成
- `POST /api/v1/ppt/generate` — 生成PPT
- `GET /api/v1/ppt/{task_id}/status` — 查询生成状态
- `GET /api/v1/ppt/{task_id}/download` — 下载PPT

### 智能辅导
- `POST /api/v1/tutor/ask` — 提问
- `GET /api/v1/tutor/session/{session_id}/history` — 会话历史
- `WS /api/v1/tutor/ws/{session_id}` — WebSocket实时辅导

### 游戏化
- `GET /api/v1/gamification/{student_id}/points` — 积分
- `GET /api/v1/gamification/{student_id}/achievements` — 成就
- `GET /api/v1/gamification/{student_id}/tasks` — 任务
- `GET /api/v1/gamification/leaderboard/{period}` — 排行榜

### 知识树成长系统
- `GET /api/v1/gamification-tree/level-config` — 等级配置
- `GET /api/v1/gamification-tree/{student_id}/tree` — 知识树状态

### 学习挑战
- `GET /api/v1/gamification-challenge/{student_id}/challenges` — 挑战列表
- `GET /api/v1/gamification-challenge/leaderboard/{dimension}` — 六维排行榜

### 知识点
- `GET /api/v1/knowledge/list` — 知识点列表
- `GET /api/v1/knowledge/{kp_id}` — 知识点详情
- `GET /api/v1/knowledge/search` — 搜索

### 学习数据
- `GET /api/v1/learning-data/{student_id}/history` — 学习历史
- `POST /api/v1/learning-data/record` — 上报学习记录
- `GET /api/v1/learning-data/{student_id}/completed` — 已完成知识点

### 趋势分析
- `GET /api/v1/trend/{student_id}/history` — 历史趋势
- `POST /api/v1/trend/analyze` — 趋势预测分析

### 学习日志与反思
- `GET /api/v1/log-reflection/{student_id}/logs` — 学习日志
- `GET /api/v1/log-reflection/{student_id}/reflections` — 反思记录
- `POST /api/v1/log-reflection/reflections/create` — 创建反思
- `GET /api/v1/log-reflection/{student_id}/review` — 学习回顾

### AI 工具
- `POST /api/v1/image/generate` — 文生图
- `GET /api/v1/image/result/{task_id}` — 图片结果
- `POST /api/v1/ocr/recognize` — OCR 识图
- `POST /api/v1/ocr/upload` — 图片上传识别

### 收藏夹
- `GET /api/v1/favorites/{student_id}` — 获取收藏
- `POST /api/v1/favorites/{student_id}` — 添加收藏
- `DELETE /api/v1/favorites/{student_id}/{favorite_id}` — 删除收藏

## Docker 部署（可选）

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

## 许可证

MIT License
