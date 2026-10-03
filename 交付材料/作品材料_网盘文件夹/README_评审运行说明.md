# LearnLab 评审运行说明

> LearnLab：AI 赋能新工科跨学科学习平台（AIC 算法创新赛·AI+学科交叉）
> 本文面向评审人员，说明如何在本地从源码运行完整的 LearnLab 系统。

## 1. 环境要求

| 组件 | 版本要求 | 说明 |
|---|---|---|
| 操作系统 | Windows 10/11 或 Linux | Windows 已验证 |
| Python | 3.11+ | 后端 |
| Node.js | 18+ | 前端构建 |
| 浏览器 | Chrome / Edge | 访问前端 |

无需安装 MySQL/PostgreSQL：系统默认使用 SQLite（随源码附带演示数据库），开箱即运行。

## 2. 目录结构

```text
learnlab/
├─ backend/               # FastAPI 后端
│  ├─ app/                # 应用源码（API/算法/智能体/模型）
│  ├─ ai_learning_v2.db   # SQLite 演示数据库（含演示账号与课程数据）
│  ├─ requirements.txt    # 依赖清单
│  └─ seed_data.py        # 演示数据初始化脚本（可选）
└─ frontend/              # React + Vite 前端
   ├─ src/                # 前端源码
   └─ package.json
```

## 3. 后端启动（约 2 分钟）

```bash
cd backend
python -m venv venv                      # 创建虚拟环境
venv\Scripts\activate                    # Windows 激活（Linux: source venv/bin/activate）
pip install -r requirements-lock.txt    # 安装锁定版本依赖（含传递依赖）
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001
```

启动成功标志：控制台输出 `Uvicorn running on http://127.0.0.1:8001`，
访问 `http://127.0.0.1:8001/health` 返回 `{"status": "healthy"}`。

> 若需 AI 辅导/组卷等大模型功能生效，在 `backend/.env` 中配置讯飞星火
> `SPARK_API_KEY`（OpenAI 兼容接口）。未配置时系统其余功能均正常运行，
> AI 功能返回友好降级提示。评分所用离线算法验证（`backend/reports/`）
> 不依赖任何外部 API。

## 4. 前端启动（约 2 分钟）

新开一个终端：

```bash
cd frontend
npm install                              # 安装依赖（首次约 2-5 分钟）
set VITE_PROXY_TARGET=http://127.0.0.1:8001   # Linux: export VITE_PROXY_TARGET=...
npm run dev                              # 开发模式启动
```

启动成功标志：控制台输出 `Local: http://localhost:5173/`。

## 5. 访问与演示账号

浏览器打开 `http://localhost:5173`：

| 角色 | 账号 | 密码 |
|---|---|---|
| 学生 | student_001 | 123456 |
| 教师 | T001 | Teacher123 |

（登录页也可自行注册新学生账号。）

## 6. 建议的评审演示路径（约 10 分钟）

1. **学生端**：登录 student_001 → 学习仪表盘 → 学习路径（16 阶段个性化计划）→ 学习中心（图文讲义 + 康奈尔线索栏 + AI 助手三栏阅读视图，正文区滚动阅读，右上角「标记完成」触发知识库自动整理与成就解锁）
2. **AI 能力**：智能辅导（提问后 AI 苏格拉底式流式回复）→ 错误诊断（粘贴含错误 C 代码，自动语法/逻辑/思维误区分析）
3. **游戏化**：知识冒险（挑战地图）→ 多维排行榜（6 维度）
4. **教师端**：退出后以 T001 登录 → 教师工作台（全班学情）→ AI 智能组卷（输入主题自动生成试卷）→ 试点数据分析（AIC 应用效果验证数据）

## 7. 常见问题

- **端口占用**：后端默认 8001、前端默认 5173，可在启动命令中修改 `--port` / `--port`。
- **npm install 缓慢**：可切换国内镜像 `npm config set registry https://registry.npmmirror.com`。
- **AI 功能无响应**：检查 `.env` 中 SPARK_API_KEY 是否配置；未配置属预期降级，不影响其他功能评分。
- **数据库重置**：删除 `backend/ai_learning_v2.db` 后运行 `python seed_data.py` 可重建演示数据。

## 8. 离线算法验证（可选）

`backend/reports/algorithm_evaluation.md` 记录了 AIC 算法增强（BKT/GKT/IRT/NCD/FSRS/MAB）的
离线评估结果与复现方式；`backend/scripts/verify_ai_algorithms.py` 可一键重新验证。
