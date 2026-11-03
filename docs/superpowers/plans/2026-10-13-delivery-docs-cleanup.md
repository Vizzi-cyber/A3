# 交付材料评审版统一优化实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 按 2026 AIC 赛题规则统一网盘提交材料的命名、表述、事实口径和生成流程，形成内容正确、版式稳定、可复现的评审版交付目录。

**Architecture:** 以 `文档信息/08_源码评审运行说明.md`、`09_功能说明_评审版.md`、`10_功能验证清单.md` 为评审源稿；用现有 Markdown→PDF 工具生成网盘 PDF；用源码包脚本将同一份运行说明写入 ZIP 根目录 README。网盘目录作为唯一对外材料，旧版本继续留在归档目录。

**Tech Stack:** Markdown、Python、pypdf、Playwright/Chrome PDF 打印、ZIP 打包脚本、Git 工作区审计脚本。

---

### Task 1: 统一评审源稿事实与措辞

**Files:**
- Modify: `文档信息/08_源码评审运行说明.md`
- Modify: `文档信息/09_功能说明_评审版.md`
- Modify: `文档信息/10_功能验证清单.md`
- Modify: `交付材料/README_提交说明.md`

- [ ] **Step 1: 修正运行说明**
  - 保留线上地址 `https://www.dreamlast.cn` 和学生/教师演示账号。
  - 统一本地后端端口为 `8001`，前端代理目标为 `http://127.0.0.1:8001`。
  - 把“需配置 API Key”改成客观的能力说明：线上演示已配置；本地未配置时基础功能与离线验证可运行，配置兼容接口密钥后启用实时大模型能力。
  - 删除内部过程、失败场景、维护提醒和不适合评审的风险注解。
  - 将演示路径写成可直接照做的 10 分钟流程。

- [ ] **Step 2: 修正功能说明**
  - 把教师端模块数量由 6 统一为 9。
  - 将学生端 9 个模块、教师端 9 个模块、实验实训能力、算法能力按评审可见功能重新组织。
  - 对“支持/已实现/验证”的表述与源码和验证清单保持一致，不写无法由项目验证的绝对承诺。

- [ ] **Step 3: 修正功能验证清单**
  - 保留已有实际验证数字：116、38、211、29、23、23、59、9、3、22、24 小时。
  - 将“后端全路由冒烟”说明写清楚：211 个接口中 89 个返回 200、72 个返回合法 4xx、50 个动态参数接口按验证脚本规则跳过，不表述为 211 个接口全部返回 200。
  - 增加验证环境、启动顺序、关键脚本名和结果解释。
  - 删除内部测试过程词和不利注解，保留可审计的复现信息。

- [ ] **Step 4: 更新提交说明**
  - 按赛题 PDF 的 7 项提交内容核对根目录材料、网盘材料和命名。
  - 删除“待提交/未完成”式勾选，改成提交前可执行检查表。
  - 明确网盘目录两层结构和内层文件名模板。
  - 将答辩 PPT 转 PDF标记为已完成但不改其内容。

- [ ] **Step 5: 运行源稿静态审查**
  - 搜索源稿中的内部过程词、Markdown/LaTeX 残留、错误端口、错误数量和旧命名。
  - 只保留客观、可验证、对评审有用的说明。

### Task 2: 按规则生成网盘成品 PDF

**Files:**
- Create/Replace: `交付材料/网盘提交/<外层>/<内层>/<内层>-运行说明.pdf`
- Create/Replace: `交付材料/网盘提交/<外层>/<内层>/<内层>-功能说明.pdf`
- Create/Replace: `交付材料/网盘提交/<外层>/<内层>/<内层>-功能验证清单.pdf`

- [ ] **Step 1: 用现有 `scripts/md_to_pdf.py` 生成三份 PDF**
  - 运行说明来自 `文档信息/08_源码评审运行说明.md`。
  - 功能说明来自 `文档信息/09_功能说明_评审版.md`。
  - 功能验证清单来自 `文档信息/10_功能验证清单.md`。
  - 输出文件名严格使用赛题规则规定的内层前缀。

- [ ] **Step 2: 检查 PDF 版式**
  - 确认中文字体正常、标题层级清晰、表格不溢出、代码块可读、页眉页脚正常。
  - 抽取 PDF 文本确认没有 Markdown 标记、乱码、错误端口和内部注解。
  - 记录页数和文件大小，更新 README 中的客观信息。

### Task 3: 同步源码包 README 与网盘 README

**Files:**
- Modify: `文档信息/08_源码评审运行说明.md`
- Modify via packaging: `交付材料/_内部母本勿传/2_源码包.zip`
- Modify via packaging: `交付材料/网盘提交/<外层>/<内层>/<内层>-源代码.zip`
- Modify: `交付材料/网盘提交/<外层>/<内层>/<内层>-README.txt`

- [ ] **Step 1: 重新生成源码包**
  - 执行 `python make_source_package.py`。
  - 确认 ZIP 根目录存在 `README.md`，内容与评审运行说明源稿一致。
  - 确认不打包 `.env`、虚拟环境、缓存、测试产物和个人路径。

- [ ] **Step 2: 复制并规范化网盘源码包**
  - 将母本 ZIP复制到网盘内层并按规则命名。
  - 校验 ZIP 内文件数量、根目录 README、`backend/requirements.txt`、`frontend/package.json`、演示数据库均存在。

- [ ] **Step 3: 更新网盘 README**
  - 列出 5 个网盘成品文件及用途。
  - 明确线上地址、演示账号、源码运行入口和验证脚本入口。
  - 不写内部目录、历史版本、失败记录或待办状态。

### Task 4: 建立提交前统一审计流程

**Files:**
- Modify: `scripts/audit_submission.py`
- Create: `scripts/audit_delivery_docs.py`
- Modify: `交付材料/README_提交说明.md`

- [ ] **Step 1: 修复审计脚本编码兼容**
  - 在 Windows 控制台输出前设置 UTF-8 或使用 ASCII-safe 输出，确保 `python scripts/audit_submission.py` 不因勾号和中文编码崩溃。
  - 保持退出码：全部通过为 0，存在问题为 1。

- [ ] **Step 2: 增加交付文档审计脚本**
  - 检查网盘外层/内层目录名。
  - 检查内层文件是否全部以指定前缀命名。
  - 检查 PDF/ZIP/README 是否齐全。
  - 抽取 PDF 文本检查错误端口、旧数量、内部过程词、Markdown/LaTeX 残留和乱码。
  - 检查网盘 PDF 与源码包 README 的关键事实一致。
  - 检查 ZIP 可打开且包含运行所需目录。

- [ ] **Step 3: 跑完整审计并保存结果**
  - 执行 `python scripts/audit_submission.py`。
  - 执行 `python scripts/audit_delivery_docs.py`。
  - 对失败项先修改源稿或生成流程，再重新生成，禁止手工只改 PDF。

### Task 5: 最终验证与交付目录收口

**Files:**
- Verify: all files under `交付材料/网盘提交/`
- Verify: `交付材料/1_技术方案.pdf`
- Verify: `交付材料/4_佐证材料 .pdf`
- Verify: `交付材料/_待放入_PPT与视频/LearnLab_AIC答辩PPT.pptx`
- Verify: generated PPT PDF and demo MP4 are present

- [ ] **Step 1: 核对主 PDF**
  - 不改 `1_技术方案.pdf` 与 `4_佐证材料 .pdf`，只确认页数、关键数字、标题和项目名称与网盘技术方案/验证口径一致。

- [ ] **Step 2: 核对 PPT 与视频**
  - 不修改用户已确认完成的答辩 PPT/PDF。
  - 检查文件存在、命名清晰、README 不把答辩 PPT PDF误列为技术方案。

- [ ] **Step 3: 运行最终命令**
  - `python scripts/audit_submission.py`
  - `python scripts/audit_delivery_docs.py`
  - `python -m zipfile -t <网盘源码包.zip>`
  - `python -c "from pypdf import PdfReader; ..."` 抽取三份网盘 PDF页数和文本。
  - `cd frontend && npm run build` 仅作项目当前状态的附加验证。

- [ ] **Step 4: 输出交付报告**
  - 列出修改的源稿、重新生成的网盘 PDF、重新打包的源码 ZIP、审计结果和未修改的既有成品。
  - 不提交未经用户授权的 Git commit；保留现有用户工作区改动。
