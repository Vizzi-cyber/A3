# AI Learning System - 个性化学习平台

## 项目简介

基于大模型的个性化资源生成与学习多智能体系统，第十五届中国软件杯大赛A3赛题作品。

## 技术架构

### 后端 (Python + FastAPI)
- **FastAPI**: 高性能异步Web框架
- **LangGraph**: 多智能体工作流编排
- **大模型接入**: 讯飞星火 / DeepSeek / OpenAI（统一接口，一键切换）
- **SQLite/PostgreSQL**: 主数据库（默认 SQLite）
- **Redis**: 缓存和消息队列（可选）

### 前端 (React + TypeScript)
- **React 18**: UI框架
- **Ant Design**: 组件库
- **Zustand**: 状态管理
- **Recharts**: 数据可视化

## 快速启动

### 1. 环境要求
- Python 3.9+
- Node.js 18+
- PostgreSQL 14+ (可选，默认使用SQLite)
- Redis 7+ (可选)

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

# 前端 (新终端)
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
├── backend/                    # 后端代码
│   ├── app/
│   │   ├── agents/            # 智能体模块
│   │   │   ├── base.py        # 智能体基类
│   │   │   ├── course_designer.py  # 课程设计师（主管）
│   │   │   ├── profiler.py    # 画像师
│   │   │   ├── resource_generator.py  # 资源生成师
│   │   │   ├── path_planner.py        # 路径规划师
│   │   │   ├── tutor.py       # 辅导助手
│   │   │   └── __init__.py
│   │   ├── api/               # API路由
│   │   │   ├── __init__.py
│   │   │   ├── profile.py     # 学生画像API
│   │   │   ├── resource.py    # 资源生成API
│   │   │   ├── learning_path.py  # 学习路径API
│   │   │   └── tutor.py       # 智能辅导API
│   │   ├── core/              # 核心配置
│   │   │   ├── config.py      # 配置管理
│   │   │   ├── logger.py      # 日志配置
│   │   │   └── safety.py      # 安全与防幻觉
│   │   ├── graph/             # LangGraph 工作流
│   │   │   ├── __init__.py
│   │   │   ├── state.py       # 共享状态定义
│   │   │   ├── nodes.py       # 智能体节点
│   │   │   └── graph.py       # 状态图构建器
│   │   ├── services/          # 业务服务层
│   │   │   ├── __init__.py
│   │   │   └── spark_llm.py   # 讯飞星火大模型封装
│   │   └── main.py            # 应用入口
│   ├── .env.example           # 环境变量模板
│   ├── requirements.txt       # Python依赖
│   └── venv/                  # 虚拟环境
├── frontend/                   # 前端代码
│   ├── src/
│   │   ├── components/        # 组件
│   │   ├── pages/             # 页面
│   │   ├── services/          # API服务（axios封装）
│   │   ├── store/             # Zustand 状态管理
│   │   ├── App.tsx            # 主应用
│   │   └── main.tsx           # 入口
│   ├── package.json
│   ├── tsconfig.json
│   └── index.html
├── scripts/                    # 工具脚本
│   └── test_api.py            # API 测试脚本
├── docs/                       # 文档
├── Dockerfile                  # Docker 构建文件
├── docker-compose.yml          # Docker Compose 配置
├── nginx.conf                  # Nginx 反向代理配置
├── requirements.txt            # Python依赖（根目录）
└── README.md                   # 本文件
```

## 核心功能

### 已实现功能
1. ✅ 智能体基类框架
2. ✅ 课程设计师智能体（主管）
3. ✅ 学生画像API（6维度）
4. ✅ 资源生成API（对接 LangGraph + 真实智能体）
5. ✅ 学习路径API
6. ✅ 智能辅导API（苏格拉底式）
7. ✅ WebSocket实时通信
8. ✅ 讯飞星火大模型集成（WebSocket 流式调用）
9. ✅ 画像师智能体完整实现
10. ✅ 资源生成师智能体完整实现
11. ✅ 路径规划师智能体完整实现
12. ✅ 辅导助手智能体完整实现
13. ✅ LangGraph工作流编排
14. ✅ 前端页面完整实现（对接后端 API）
15. ✅ 防幻觉机制（JSON 校验、代码语法检查、引用溯源）
16. ✅ 内容安全过滤（敏感词过滤、Prompt 安全加固）

### 待实现功能
- [ ] 用户认证与权限管理
- [ ] 生产环境部署优化（HTTPS、域名绑定）
- [ ] 更丰富的单元测试与集成测试

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
```

## 测试

```bash
# 启动后端服务后，运行 API 测试脚本
"C:/Users/Vizzi/Desktop/A3_项目框架/backend/venv/Scripts/python.exe" scripts/test_api.py
```

## API接口列表

### 学生画像
- `GET /api/v1/profile/{student_id}` - 获取画像
- `POST /api/v1/profile/{student_id}/update` - 更新画像
- `GET /api/v1/profile/{student_id}/summary` - 获取摘要

### 资源生成
- `POST /api/v1/resource/generate` - 生成资源
- `GET /api/v1/resource/task/{task_id}` - 查询任务状态
- `POST /api/v1/resource/document/generate` - 生成文档
- `POST /api/v1/resource/questions/generate` - 生成题目
- `POST /api/v1/resource/mindmap/generate` - 生成思维导图
- `POST /api/v1/resource/code/generate` - 生成代码

### 学习路径
- `POST /api/v1/learning-path/generate` - 生成路径
- `GET /api/v1/learning-path/{student_id}/current` - 当前路径
- `POST /api/v1/learning-path/{student_id}/adjust` - 调整路径

### 智能辅导
- `POST /api/v1/tutor/ask` - 提问
- `WS /api/v1/tutor/ws/{session_id}` - WebSocket实时辅导

## 开发团队

- 队长: [姓名]
- 后端开发: [姓名]
- 前端开发: [姓名]
- AI算法: [姓名]

## 许可证

MIT License
