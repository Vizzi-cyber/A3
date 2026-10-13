审查问题修复任务清单（按批次逐一修复测试，不影响其他模块）

范围原则：只修「点状缺陷」（bug / 崩溃 / 泄漏 / 契约断裂），每处修复局限在单文件或单一调用点；架构级候选（agent 深入口、上下文构建器、测验事件总线、graph 层决策、api.ts 切分、TutorAgent 三实例统一、status 词表全量统一）本轮不动，记入 06 报告为「架构候选待专项」。

━━━ 第一批：前端 Critical（7 项）━━━
1. pages/Tutor.tsx（两处 ~447/~565）：把 `profileApi.analyzeConversation` 移出 setMessages updater——用 ref 同步最新消息，`complete` 分支在 updater 外触发分析（updater 保持纯函数）
2. services/api.ts apiGet/apiStream 两处 401：改为复用 `tryRefreshToken()`（axios 拦截器同款），成功则换新 token 重发一次 fetch；失败才 `dispatchEvent("auth:expired")` 软通知，删除 `window.location.href` 硬跳转
3. pages/LandingPage.tsx TypeWriter：timerRef 保存 interval id，cleanup 同时 clearTimeout + clearInterval（现清理是死代码）
4. pages/ProjectCollaboration.tsx 成员列表：`key={idx}` → `key={member.student_id}`
5. components/ChatPanel.tsx 附件列表：上传时生成 `crypto.randomUUID()` 存入对象，key 按 uuid
6. pages/circuit/CodeEditor.tsx pinMappings：映射对象加 `id` 字段，key/update/remove 全部按 id 寻址（解耦 index）
7. components/kb/NoteEditor.tsx：useEffect 依赖 `[activeNote]`（对象身份）→ `[activeNote?.note_id]`，仅切换笔记时重置标题，修复自动保存回写覆盖输入
8. pages/ProjectCollaboration.tsx：6 个 `useState<any>` 按实际响应字段定义最小 interface；`catch (error: any)` → unknown 收窄

━━━ 第二批：前端 High（7 项）━━━
9. components/PPTGenerator.tsx：轮询 interval 加 unmount 兜底清理（`useEffect(() => () => stopPolling(), [])`）
10. App.tsx：LandingPage/Login 路由包一层 ErrorBoundary（WebGL 崩溃不再整页白屏）
11. teacher/ClassAnalytics.tsx + StudentManagement.tsx：visibilitychange effect 闭包函数用 useCallback 稳定并列入 deps
12. components/AlgorithmVisualizer.tsx：`setPlaying(false)` 移出 setStepIdx updater，在 effect 内条件判断
13. components/AgentFlowPanel.tsx：轮询加 stale 标志防旧 run 响应覆盖新 run
14. pages/Tutor.tsx：两处 `setTimeout(loadProfile, 2000)` 存 ref 并在 unmount 清理
15. teacher/SystemSettings.tsx：`defaultValue` 改受控 initialValues；密码项补 name 与校验——实现时先确认后端有无改密码接口，无则移除「已保存」假提示改为禁用态（不做假功能）

━━━ 第三批：后端智能体/工作流 bug（8 项）━━━
16. graph/nodes.py `_parallel_agents` 残留死循环地雷：supervisor_node 返回时显式重置为 None；router_edge 构造 Send 后清除该键
17. 14 处 `generate_json` 返回 error 未检查（path_planner._analyze_knowledge、profiler._analyze_profile、resource_generator outline/questions/match_resources、role_matcher×3、collaboration_supervisor×4、result_evaluator×5、project_decomposer._get_project_info）：逐处补 `if data.get("status")=="error": return {"status":"failed", "error": ...}`
18. agents/course_designer.py `_get_student_profile` 恒拿硬编码兜底画像：兼容读 `result.get("profile") or result.get("analysis")`（不改 profiler 返回结构，避免影响其他消费方）
19. agents/knowledge_graph_builder.py：`_process_batch` 失败路径返回 `{"status":"error","message":...}`、成功补 status——接通上轮加了但断线的批次防护
20. cognitive_style str/dict 混型崩溃（nodes.py 3 处无守卫 + agents/tutor.py + resource_generator.py）：加统一 isinstance 守卫 helper，全部换用
21. graph/nodes.py 事件流与边界：(a) `_push("completed")` 按 result.status 推 completed/failed；(b) assembler 失败集合纳入 `partial_failure`；(c) 未知 task_type 返回 error（不再 success 0/0）；(d) tutor session_id 兜底统一为 `{student_id}_default`
22. services/path_adjustment_engine.py：后台任务持引用集防 GC；`db = SessionLocal()` 提到 try 外（finally 判空 close）；`analyze_adjustment_need` 同步 DB 查询包 `asyncio.to_thread`
23. services/llm_factory.py：ainvoke 监控日志任务持引用；FailoverLLM.astream 已 yield 内容后不再切换 fallback（直接 raise，防下游收到重复前半段）

━━━ 第四批：低风险清理（5 项）━━━
24. core/config.py：ARK_*/VOLC_* 字段定义重复两遍（后者静默覆盖前者）→ 删重复块
25. agents/base.py `get_status()` 在子类覆写 str status 后 `status.value` AttributeError → str/Enum 双兼容
26. agents/course_designer.py：`isinstance(result, Exception)` 死分支删除
27. agents/base.py run_with_reflection：不再把 `_previous_result/_feedback` 写进调用方 context（用局部副本传 process），消除副作用污染与死反馈环
28. services/ppt_generator.py：`if any(...): pass` 死代码删除；`add_shape(1)` → MSO_SHAPE 枚举

━━━ 第五批：验证 ━━━
29. verify_ai_algorithms.py 加断言（100→约 104）：kg_builder 批次失败带 status、course_designer 兜底画像兼容读、cognitive_style 守卫
30. 每批修复后即测：第一/二批 → `npm run build`（tsc 类型门禁）；第三/四批 → venv import + TestClient 冒烟
31. 最终全量回归：verify_ai_algorithms / verify_p0_wiring_api / verify_aic_features / verify_all_routes（8001 临时实例）/ test:mna / build，全部须绿
32. 06 报告补第十一节（简短记录）+ memory 更新

━━━ 明确不做（记录口径，避免影响其他模块）━━━
架构候选 1/2/4/5/6（agent 调用深入口、学习上下文构建器、测验事件总线、graph 层归属、api.ts 切分与巨型页面拆分）、TutorAgent 三实例统一、status 词表全量统一、base.py 日志装配合并、llm thinking 签名提升——均属跨模块重构，留待专项。执行中如发现某项与实际代码不符（审计误报），跳过并在汇报中注明。全程不 commit。