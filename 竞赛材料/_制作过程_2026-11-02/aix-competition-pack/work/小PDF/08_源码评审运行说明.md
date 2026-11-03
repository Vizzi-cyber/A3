# LearnLab 评审运行说明

> LearnLab 跨学科智能学习平台（“AI+X”跨学科智能创新应用竞赛）
>
> 本说明面向评审人员，提供线上体验入口和本地源码运行方法。

## 1. 体验入口

平台线上环境：**https://www.dreamlast.cn**

线上环境已部署学生端和教师端功能，可直接用于功能体验。登录页提供“体验学生账号”和“体验教师账号”快捷入口，也可以使用以下演示账号：

| 角色 | 账号 | 密码 |
|---|---|---|
| 学生 | `student_001` | `123456` |
| 教师 | `T001` | `Teacher123` |

## 2. 运行环境

| 组件 | 版本要求 | 用途 |
|---|---|---|
| 操作系统 | Windows 10/11 或 Linux | 开发与运行环境 |
| Python | 3.11 及以上 | 后端服务与算法验证 |
| Node.js | 18 及以上 | 前端依赖与构建 |
| 浏览器 | Chrome 或 Edge | 平台访问与功能体验 |

系统默认使用 SQLite 演示数据库，源码包已包含演示数据，不需要额外安装 MySQL 或 PostgreSQL。

## 3. 源码目录

```text
learnlab/
├─ backend/
│  ├─ app/                    # FastAPI 接口、算法与智能体源码
│  ├─ ai_learning_v2.db      # SQLite 演示数据库
│  ├─ requirements.txt        # Python 依赖清单
│  ├─ requirements-lock.txt   # 锁定版本依赖清单
│  └─ seed_data.py            # 演示数据初始化脚本
└─ frontend/
   ├─ src/                    # React + TypeScript 前端源码
   ├─ e2e/                    # Playwright 端到端测试
   └─ package.json            # 前端依赖与脚本
```

## 4. 本地启动

### 4.1 启动后端

在第一个终端执行：

```bash
cd backend
python -m venv venv
```

Windows：

```bash
venv\Scripts\activate
```

Linux 或 macOS：

```bash
source venv/bin/activate
```

安装依赖并启动服务：

```bash
pip install -r requirements-lock.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001
```

启动成功后，访问 `http://127.0.0.1:8001/health`，返回 `{"status":"healthy"}` 即表示后端已就绪。

### 4.2 启动前端

新开第二个终端执行：

```bash
cd frontend
npm install
```

Windows：

```bash
set VITE_PROXY_TARGET=http://127.0.0.1:8001
```

Linux 或 macOS：

```bash
export VITE_PROXY_TARGET=http://127.0.0.1:8001
```

启动前端：

```bash
npm run dev
```

启动成功后，浏览器访问 `http://localhost:5173/`。

## 5. 大模型能力配置

线上环境已配置可用的大模型能力。本地运行时，在 `backend/.env` 中配置兼容接口密钥后，可以体验智能辅导、AI 备课、AI 学情洞察和 AI 智能组卷等实时生成能力。系统支持多 Provider 注册与切换，配置项示例见 `backend/.env.example`。

未配置外部模型密钥时，平台的课程浏览、学习路径、知识图谱、练习、实验仿真、数据看板及离线算法验证仍可运行；需要实时生成的功能会按照系统配置返回相应提示。

## 6. 推荐评审路径

1. 进入线上环境或本地前端，登录学生账号。
2. 查看学习仪表盘，了解学习时长、掌握度、任务和成长信息。
3. 进入学习路径，查看跨 C 语言、电路分析、STM32 的知识依赖关系与个性化学习顺序。
4. 进入学习中心，阅读知识点讲义，体验 Cornell 笔记栏、思维导图和 AI 辅导助手。
5. 进入智能辅导，输入学习问题，体验苏格拉底式引导和流式回复。
6. 进入错误诊断，提交含有错误的 C 代码，查看语法、逻辑和概念层面的诊断结果。
7. 进入知识冒险和排行榜，体验闯关练习、知识树和多维成长记录。
8. 退出学生账号，登录教师账号，查看教师工作台、学生管理和学情分析。
9. 进入 AI 智能组卷，选择知识点和难度，生成多题型试卷。
10. 进入试点数据分析，查看学习行为、测验、掌握度和实验参与等数据的汇总报告。

## 7. 算法验证

源码包中的 `backend/scripts/` 提供算法、接口和功能验证脚本，`backend/reports/algorithm_evaluation.md` 提供算法评估结果记录。常用验证命令如下：

```bash
cd backend
python -X utf8 scripts/verify_ai_algorithms.py
python -X utf8 scripts/verify_core_features.py
python -X utf8 scripts/verify_dataflow.py
python -X utf8 scripts/verify_agent_llm.py
```

后端服务启动后，可运行全路由验证：

```bash
python -X utf8 scripts/verify_all_routes.py
```

前端端到端验证：

```bash
cd frontend
npx playwright test e2e/core-features.spec.ts --reporter=list
npx playwright test e2e/frontend.spec.ts --reporter=list
```

## 8. 常用端口

| 服务 | 默认地址 |
|---|---|
| 后端 API | `http://127.0.0.1:8001` |
| 后端健康检查 | `http://127.0.0.1:8001/health` |
| 前端开发服务 | `http://localhost:5173/` |

端口可在启动命令中按实际环境调整；前端代理目标应与后端地址保持一致。
