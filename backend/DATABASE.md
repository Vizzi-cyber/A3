# 数据库文档

## 1. 数据库概述

- **数据库类型**：SQLite
- **数据库文件路径**：`ai_learning.db`
- **ORM 框架**：SQLAlchemy（declarative_base）
- **连接方式**：通过 `backend/app/models/database.py` 创建引擎与会话，支持通过环境变量切换为 PostgreSQL
- **时区处理**：DateTime 字段均使用 `timezone=True`，默认服务器时间为 `func.now()`

---

## 2. 表结构总览

| 序号 | 表名 | 说明 |
|------|------|------|
| 1 | `users` | 用户认证信息 |
| 2 | `student_profiles` | 学生画像 |
| 3 | `knowledge_points` | 知识点（含课程内容） |
| 4 | `learning_records` | 学习记录 |
| 5 | `quiz_results` | 测验结果 |
| 6 | `student_trends` | 学习趋势与评估数据 |
| 7 | `game_points` | 游戏化积分 |
| 8 | `game_achievements` | 成就徽章 |
| 9 | `game_tasks` | 学习任务与挑战 |
| 10 | `leaderboard` | 排行榜快照 |
| 11 | `learning_logs` | 学习日志 |
| 12 | `reflections` | 反思记录 |
| 13 | `favorites` | 收藏夹/书签 |
| 14 | `api_monitor` | API 接口监控 |
| 15 | `llm_calls` | 大模型调用监控 |
| 16 | `system_health` | 系统健康监控 |

---

## 3. 各表详细说明

### 3.1 users（用户表）

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | Integer | PK, 自增, index | 内部主键 |
| student_id | String(64) | unique, index, not null | 学生唯一标识 |
| username | String(128) | not null | 用户名 |
| email | String(128) | unique, nullable | 邮箱 |
| hashed_password | String(256) | nullable | 哈希密码 |
| is_active | Boolean | default=True | 是否启用 |
| role | String(32) | default="student" | 角色：student / teacher / admin |
| created_at | DateTime(tz) | server_default=now() | 创建时间 |
| updated_at | DateTime(tz) | onupdate=now() | 更新时间 |

**索引**：`id`, `student_id`, `email`

---

### 3.2 student_profiles（学生画像表）

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| student_id | String(64) | PK, index | 学生唯一标识 |
| knowledge_base | JSON | default=dict | 知识基础 |
| cognitive_style | JSON | default=dict | 认知风格 |
| weak_areas | JSON | default=list | 薄弱领域 |
| error_patterns | JSON | default=list | 错误模式 |
| learning_goals | JSON | default=list | 学习目标 |
| interest_areas | JSON | default=list | 兴趣领域 |
| learning_tempo | JSON | default=dict | 学习节奏 |
| practical_preferences | JSON | default=dict | 实践偏好 |
| created_at | DateTime(tz) | server_default=now() | 创建时间 |
| updated_at | DateTime(tz) | onupdate=now() | 更新时间 |

**索引**：`student_id`

---

### 3.3 knowledge_points（知识点表）

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| kp_id | String(64) | PK, index | 知识点唯一标识 |
| name | String(256) | not null | 知识点名称 |
| subject | String(64) | not null | 所属学科 |
| difficulty | Float | default=0.5 | 难度系数（0.0 ~ 1.0） |
| prerequisites | JSON | default=list | 前置知识点 ID 列表（支持 DAG 依赖） |
| description | Text | nullable | 知识点描述 |
| tags | JSON | default=list | 标签列表 |
| created_at | DateTime(tz) | server_default=now() | 创建时间 |
| document | Text | nullable | Markdown 图文讲义 |
| code_example | Text | nullable | 代码示例 |
| questions | JSON | nullable | 练习题列表 |
| mindmap | JSON | nullable | 思维导图 JSON |

**索引**：`kp_id`

**特别说明**：
- `document`：用于存储该知识点的 Markdown 格式图文讲义，替代硬编码的 content_library。
- `code_example`：存储与该知识点相关的可运行代码示例，便于学生边学边练。
- `questions`：以 JSON 数组形式存储配套练习题，支持动态组卷与自适应测验。
- `mindmap`：以 JSON 形式存储思维导图节点数据，用于前端可视化展示知识脉络。

---

### 3.4 learning_records（学习记录表）

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| record_id | String(64) | PK, index | 记录唯一标识 |
| student_id | String(64) | index, not null | 学生标识 |
| kp_id | String(64) | index, not null | 知识点标识 |
| action | String(64) | not null | 动作类型：watch / read / practice / review |
| duration | Integer | default=0 | 学习时长（秒） |
| progress | Float | default=0.0 | 进度（0.0 ~ 1.0） |
| score | Float | nullable | 练习得分 |
| meta | JSON | default=dict | 扩展信息 |
| created_at | DateTime(tz) | server_default=now() | 创建时间 |

**索引**：`record_id`, `student_id`, `kp_id`

---

### 3.5 quiz_results（测验结果表）

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| quiz_id | String(64) | PK, index | 测验唯一标识 |
| student_id | String(64) | index, not null | 学生标识 |
| kp_id | String(64) | index, not null | 知识点标识 |
| total_questions | Integer | default=0 | 总题数 |
| correct_count | Integer | default=0 | 正确题数 |
| score | Float | default=0.0 | 百分制得分 |
| weak_tags | JSON | default=list | 薄弱标签 |
| time_spent | Integer | default=0 | 用时（秒） |
| answers | JSON | default=list | 答题详情 |
| created_at | DateTime(tz) | server_default=now() | 创建时间 |

**索引**：`quiz_id`, `student_id`, `kp_id`

---

### 3.6 student_trends（学生趋势数据表）

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | Integer | PK, 自增 | 内部主键 |
| student_id | String(64) | index, not null | 学生标识 |
| date | String(10) | index, not null | 日期（YYYY-MM-DD） |
| mastery_trend | Float | default=0.0 | 知识掌握度趋势（权重 40%） |
| speed_ratio | Float | default=0.0 | 学习速度比例（权重 20%） |
| time_efficiency | Float | default=0.0 | 学习时间效率（权重 15%） |
| weakness_priority | Float | default=0.0 | 薄弱点优先级得分（权重 15%） |
| stability | Float | default=0.0 | 连续学习稳定性（权重 10%） |
| trend_factor | Float | default=0.0 | 综合趋势因子（-1.0 ~ 1.0） |
| trend_state | String(16) | default="stable" | 趋势状态：growth / decline / warning / stable |
| predicted_mastery_3d | Float | default=0.0 | 3 天后预测掌握度 |
| intervention | String(256) | nullable | 干预建议 |
| details | JSON | default=dict | 详细数据 |
| created_at | DateTime(tz) | server_default=now() | 创建时间 |

**索引**：`id`, `student_id`, `date`

---

### 3.7 game_points（积分表）

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | Integer | PK, 自增 | 内部主键 |
| student_id | String(64) | index, not null | 学生标识 |
| total_points | Integer | default=0 | 总积分 |
| daily_points | Integer | default=0 | 当日积分 |
| weekly_points | Integer | default=0 | 本周积分 |
| updated_at | DateTime(tz) | onupdate=now() | 更新时间 |

**索引**：`id`, `student_id`

---

### 3.8 game_achievements（成就徽章表）

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | Integer | PK, 自增 | 内部主键 |
| student_id | String(64) | index, not null | 学生标识 |
| achievement_id | String(64) | not null | 成就唯一标识 |
| name | String(128) | not null | 成就名称 |
| description | String(512) | nullable | 成就描述 |
| icon | String(256) | nullable | 图标地址 |
| unlocked_at | DateTime(tz) | server_default=now() | 解锁时间 |

**索引**：`id`, `student_id`

---

### 3.9 game_tasks（学习任务与挑战任务表）

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | Integer | PK, 自增 | 内部主键 |
| student_id | String(64) | index, not null | 学生标识 |
| task_id | String(64) | not null | 任务唯一标识 |
| title | String(256) | not null | 任务标题 |
| description | String(512) | nullable | 任务描述 |
| task_type | String(32) | default="daily" | 任务类型：daily / weekly / challenge |
| reward_points | Integer | default=0 | 奖励积分 |
| progress | Float | default=0.0 | 完成进度（0.0 ~ 1.0） |
| completed | Boolean | default=False | 是否完成 |
| completed_at | DateTime(tz) | nullable | 完成时间 |
| deadline | DateTime(tz) | nullable | 截止时间 |
| created_at | DateTime(tz) | server_default=now() | 创建时间 |

**索引**：`id`, `student_id`

---

### 3.10 leaderboard（排行榜快照表）

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | Integer | PK, 自增 | 内部主键 |
| student_id | String(64) | index, not null | 学生标识 |
| period | String(16) | default="weekly" | 统计周期：daily / weekly / monthly |
| score | Integer | default=0 | 得分 |
| rank | Integer | default=0 | 排名 |
| updated_at | DateTime(tz) | server_default=now() | 更新时间 |

**索引**：`id`, `student_id`

---

### 3.11 learning_logs（学习日志自动记录表）

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| log_id | String(64) | PK, index | 日志唯一标识 |
| student_id | String(64) | index, not null | 学生标识 |
| date | String(10) | index, not null | 日期（YYYY-MM-DD） |
| total_duration | Integer | default=0 | 当日总学习时长（秒） |
| kp_count | Integer | default=0 | 当日学习知识点数量 |
| quiz_count | Integer | default=0 | 当日测验次数 |
| avg_score | Float | default=0.0 | 当日平均得分 |
| mistakes | JSON | default=list | 当日错题记录 |
| path_progress | Float | default=0.0 | 路径进度 |
| completed_tasks | JSON | default=list | 已完成任务列表 |
| timeline | JSON | default=list | 时间线明细：[{time, action, kp_id, duration}] |
| created_at | DateTime(tz) | server_default=now() | 创建时间 |

**索引**：`log_id`, `student_id`, `date`

---

### 3.12 reflections（反思记录表）

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| reflection_id | String(64) | PK, index | 反思唯一标识 |
| student_id | String(64) | index, not null | 学生标识 |
| date | String(10) | index, not null | 日期（YYYY-MM-DD） |
| content | Text | not null | 反思内容 |
| mood | String(32) | default="neutral" | 心情：happy / neutral / frustrated / excited |
| tags | JSON | default=list | 标签 |
| ai_feedback | Text | nullable | AI 反馈 |
| created_at | DateTime(tz) | server_default=now() | 创建时间 |

**索引**：`reflection_id`, `student_id`, `date`

---

### 3.13 favorites（收藏夹/书签表）

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | String(64) | PK, index | 收藏唯一标识 |
| student_id | String(64) | index, not null | 学生标识 |
| title | String(256) | not null | 资源标题 |
| resource_type | String(32) | not null | 资源类型：doc / video / code / tool / article |
| url | Text | nullable | 资源链接 |
| meta | JSON | default=dict | 扩展信息：icon, color, description, tags 等 |
| created_at | DateTime(tz) | server_default=now() | 创建时间 |

**索引**：`id`, `student_id`

---

### 3.14 api_monitor（API 接口监控表）

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | Integer | PK, 自增 | 内部主键 |
| endpoint | String(256) | not null | 接口路径 |
| method | String(16) | not null | HTTP 方法 |
| status_code | Integer | default=200 | 响应状态码 |
| duration_ms | Float | default=0.0 | 响应耗时（毫秒） |
| student_id | String(64) | nullable | 关联学生标识 |
| error_msg | Text | nullable | 错误信息 |
| created_at | DateTime(tz) | server_default=now() | 创建时间 |

**索引**：`id`

---

### 3.15 llm_calls（大模型调用监控表）

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | Integer | PK, 自增 | 内部主键 |
| provider | String(32) | not null | 提供商 |
| model | String(64) | nullable | 模型名称 |
| prompt_tokens | Integer | default=0 | 提示 token 数 |
| completion_tokens | Integer | default=0 | 补全 token 数 |
| duration_ms | Float | default=0.0 | 调用耗时（毫秒） |
| success | Boolean | default=True | 是否成功 |
| error_msg | Text | nullable | 错误信息 |
| created_at | DateTime(tz) | server_default=now() | 创建时间 |

**索引**：`id`

---

### 3.16 system_health（系统健康监控表）

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | Integer | PK, 自增 | 内部主键 |
| cpu_percent | Float | default=0.0 | CPU 使用率 |
| memory_percent | Float | default=0.0 | 内存使用率 |
| disk_percent | Float | default=0.0 | 磁盘使用率 |
| active_connections | Integer | default=0 | 活跃连接数 |
| queue_size | Integer | default=0 | 队列长度 |
| recorded_at | DateTime(tz) | server_default=now() | 记录时间 |

**索引**：`id`

---

## 4. 表之间的关系

本项目采用**逻辑关联**设计，未在数据库层面设置外键约束（ForeignKey），关系通过业务字段（如 `student_id`、`kp_id`）在应用层维护。主要关系如下：

| 主表 | 关联表 | 关联字段 | 关系类型 |
|------|--------|----------|----------|
| `users` | `student_profiles` | `student_id` | 1 对 1 |
| `users` | `learning_records` | `student_id` | 1 对多 |
| `users` | `quiz_results` | `student_id` | 1 对多 |
| `users` | `student_trends` | `student_id` | 1 对多 |
| `users` | `game_points` | `student_id` | 1 对 1 |
| `users` | `game_achievements` | `student_id` | 1 对多 |
| `users` | `game_tasks` | `student_id` | 1 对多 |
| `users` | `leaderboard` | `student_id` | 1 对多 |
| `users` | `learning_logs` | `student_id` | 1 对多 |
| `users` | `reflections` | `student_id` | 1 对多 |
| `users` | `favorites` | `student_id` | 1 对多 |
| `knowledge_points` | `learning_records` | `kp_id` | 1 对多 |
| `knowledge_points` | `quiz_results` | `kp_id` | 1 对多 |
| `knowledge_points` | `knowledge_points` | `prerequisites` | DAG 自引用（前置依赖） |

---

## 5. 特别说明

### 5.1 knowledge_points 表新增字段用途

在 `knowledge_points` 表中，除基础知识点信息外，还设计了以下四个课程内容字段，用于替代传统的硬编码 content_library，实现课程内容的数据库化与动态管理：

- **`document`**（Text，nullable）
  - 用途：存储该知识点的 Markdown 格式图文讲义。
  - 优势：支持富文本、公式、图片，便于前端直接渲染为学习文档。

- **`code_example`**（Text，nullable）
  - 用途：存储与该知识点相关的代码示例。
  - 优势：学生可在学习页面直接查看、复制、运行代码，提升实践体验。

- **`questions`**（JSON，nullable）
  - 用途：以 JSON 数组形式存储配套练习题。
  - 格式示例：`[{"question": "...", "options": [...], "answer": "...", "type": "choice"}]`
  - 优势：支持动态组卷、自适应难度调整、即时批改。

- **`mindmap`**（JSON，nullable）
  - 用途：以 JSON 形式存储思维导图的节点与连接数据。
  - 格式示例：`{"nodes": [{"id": "1", "label": "根节点"}], "edges": [...]}`
  - 优势：前端可基于该数据直接渲染交互式思维导图，帮助学生梳理知识脉络。

---

## 6. 索引汇总

| 表名 | 索引字段 | 说明 |
|------|----------|------|
| users | id, student_id, email | 主键 + 唯一标识 + 登录 |
| student_profiles | student_id | 主键 |
| knowledge_points | kp_id | 主键 |
| learning_records | record_id, student_id, kp_id | 主键 + 学生/知识点查询 |
| quiz_results | quiz_id, student_id, kp_id | 主键 + 学生/知识点查询 |
| student_trends | id, student_id, date | 主键 + 学生/日期查询 |
| game_points | id, student_id | 主键 + 学生查询 |
| game_achievements | id, student_id | 主键 + 学生查询 |
| game_tasks | id, student_id | 主键 + 学生查询 |
| leaderboard | id, student_id | 主键 + 学生查询 |
| learning_logs | log_id, student_id, date | 主键 + 学生/日期查询 |
| reflections | reflection_id, student_id, date | 主键 + 学生/日期查询 |
| favorites | id, student_id | 主键 + 学生查询 |
| api_monitor | id | 主键 |
| llm_calls | id | 主键 |
| system_health | id | 主键 |

---

## 7. 备注

- 所有 JSON 字段在 Python 层通过 SQLAlchemy 自动序列化/反序列化，存储为 SQLite 的 JSON 类型（实际为 TEXT）。
- 时间字段统一使用 `DateTime(timezone=True)`，确保跨时区一致性。
- 监控类表（`api_monitor`、`llm_calls`、`system_health`）主要用于运维与审计，建议配合定时清理策略防止数据膨胀。
