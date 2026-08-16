/**
 * 知识空间悬浮工具条 v2
 * - 右上角悬浮按钮：日历 / 每日练习（本页做题）/ 今日任务 / 课程进度 / 排行榜 / 成就积分 / 图例
 * - 今日任务固定显示在右上角（常驻小卡片）
 * - 每日练习在面板内直接做题（选择→提交→反馈→下一题→得分），不跳转
 * - 全部面板 fixed + zIndex 9999 绝对最顶层
 */
import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Calendar, List, Empty } from "antd";
import {
  CalendarOutlined, EditOutlined, UnorderedListOutlined, TrophyOutlined,
  BarChartOutlined, StarOutlined, QuestionCircleOutlined, ExperimentOutlined, CloseOutlined,
  CheckCircleOutlined, CloseCircleOutlined,
} from "@ant-design/icons";
import api from "../../services/api";
import { HoloData } from "./useHoloData";

interface QuizQuestion {
  q_id: string;
  type: string;
  content: string;
  difficulty: number;
  options?: { id: string; text: string }[];
  correct_answer?: string;
  hint?: string;
}

interface FloatingToolsProps {
  data: HoloData;
}

const FloatingTools: React.FC<FloatingToolsProps> = ({ data }) => {
  const navigate = useNavigate();
  const [open, setOpen] = useState<string | null>(null);
  const [activeDates, setActiveDates] = useState<string[]>([]);
  const [quizQuestions, setQuizQuestions] = useState<QuizQuestion[]>([]);
  const [quizIdx, setQuizIdx] = useState(0);
  const [quizSelected, setQuizSelected] = useState<string | null>(null);
  const [quizShown, setQuizShown] = useState(false);
  const [quizScore, setQuizScore] = useState(0);
  const [quizDone, setQuizDone] = useState(false);
  const [showMore, setShowMore] = useState(false);
  const [gktData, setGktData] = useState<{ bkt: Record<string, number>; gkt: Record<string, number> } | null>(null);
  const [ncdAbility, setNcdAbility] = useState<number | null>(null);
  const [irtAbility, setIrtAbility] = useState<number | null>(null);

  const loadQuiz = async () => {
    try {
      const r = await api.get("/daily-quiz/daily", { params: { count: 5 } });
      setQuizQuestions(r.data?.data?.questions ?? []);
      setQuizIdx(0); setQuizSelected(null); setQuizShown(false); setQuizScore(0); setQuizDone(false);
    } catch { /* ignore */ }
  };

  useEffect(() => {
    if (open === "calendar") {
      api.get("/dashboard/student_001/active-dates")
        .then((r) => setActiveDates(r.data?.data ?? []))
        .catch(() => {});
    }
    if (open === "quiz") {
      loadQuiz();
    }
    if (open === "algorithms") {
      api.get("/algorithms/gkt/mastery/student_001")
        .then((r) => setGktData({ bkt: r.data?.data?.bkt_mastery ?? {}, gkt: r.data?.data?.gkt_mastery ?? {} }))
        .catch(() => {});
      api.post("/algorithms/ncd/fit").then(() =>
        api.get("/algorithms/ncd/ability/student_001")
          .then((r) => setNcdAbility(r.data?.data?.ncd_ability ?? null))
          .catch(() => {})
      ).catch(() => {});
      api.get("/algorithms/irt/ability/student_001")
        .then((r) => setIrtAbility(r.data?.data?.ability_theta ?? null))
        .catch(() => {});
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open]);

  // 每日练习主动弹出：每次进入知识空间 2 秒后自动打开（除非点过"今天不再提醒"）
  useEffect(() => {
    const today = new Date().toISOString().slice(0, 10);
    if (localStorage.getItem("quiz_dismissed_today") === today) return;
    const timer = setTimeout(() => setOpen("quiz"), 2000);
    return () => clearTimeout(timer);
  }, []);

  const submitAnswer = () => {
    if (!quizSelected || quizShown) return;
    const q = quizQuestions[quizIdx];
    setQuizShown(true);
    if (quizSelected === q.correct_answer) setQuizScore((s) => s + 1);
  };

  const nextQuiz = () => {
    if (quizIdx + 1 >= quizQuestions.length) {
      setQuizDone(true);
      return;
    }
    setQuizIdx((i) => i + 1);
    setQuizSelected(null);
    setQuizShown(false);
  };

  const mainTools = [
    { key: "calendar", icon: <CalendarOutlined />, label: "学习日历", color: "#6366f1" },
    { key: "quiz", icon: <EditOutlined />, label: "每日练习", color: "#f97316" },
    { key: "tasks", icon: <UnorderedListOutlined />, label: "今日任务", color: "#0ea5e9" },
    { key: "courses", icon: <BarChartOutlined />, label: "课程进度", color: "#38bdf8" },
  ];
  const moreTools = [
    { key: "rank", icon: <TrophyOutlined />, label: "排行榜", color: "#f59e0b" },
    { key: "honor", icon: <StarOutlined />, label: "成就积分", color: "#fbbf24" },
    { key: "algorithms", icon: <ExperimentOutlined />, label: "算法中心", color: "#8b5cf6" },
    { key: "legend", icon: <QuestionCircleOutlined />, label: "图谱图例", color: "#94a3b8" },
  ];

  const renderPanel = () => {
    switch (open) {
      case "calendar":
        return (
          <div className="w-[440px]">
            <div className="text-sm font-semibold text-slate-700 mb-2">📅 学习日历</div>
            <Calendar
              fullscreen={false}
              cellRender={(date) =>
                activeDates.includes(date.format("YYYY-MM-DD")) ? (
                  <div className="mx-auto w-1.5 h-1.5 rounded-full bg-emerald-500" />
                ) : null
              }
            />
            <div className="text-[10px] text-slate-400 mt-1">绿点 = 学习打卡日（共 {activeDates.length} 天）</div>
          </div>
        );
      case "quiz":
        if (quizDone) {
          return (
            <div className="w-[500px] text-center py-4">
              <div className="text-3xl mb-2">{quizScore >= quizQuestions.length * 0.6 ? "🎉" : "💪"}</div>
              <div className="text-lg font-bold text-slate-800">答对 {quizScore}/{quizQuestions.length} 题</div>
              <div className="text-xs text-slate-400 mt-1">继续练习，巩固知识点</div>
              <div className="flex gap-2 mt-4 justify-center">
                <button onClick={loadQuiz} className="rounded-lg px-4 py-1.5 text-xs font-semibold bg-orange-500 text-white hover:bg-orange-600">再练一次</button>
                <button onClick={() => setOpen(null)} className="rounded-lg px-4 py-1.5 text-xs font-semibold bg-slate-100 text-slate-600 hover:bg-slate-200">收起</button>
              </div>
            </div>
          );
        }
        if (!quizQuestions.length) {
          return (
            <div className="w-[500px]">
              <div className="text-sm font-semibold text-slate-700 mb-2 flex items-center gap-2">
                ✏️ 每日练习
                <span className="text-[9px] px-1.5 py-0.5 rounded-full font-semibold" style={{ background: "#f973161c", color: "#f97316", border: "1px solid #f9731633" }}>
                  AI 自适应选题
                </span>
              </div>
              <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description={<span className="text-[11px] text-slate-400">加载题目中…</span>} />
            </div>
          );
        }
        const q = quizQuestions[quizIdx];
        return (
          <div className="w-[520px]">
            <div className="flex items-center justify-between mb-2">
              <div className="text-sm font-semibold text-slate-700 flex items-center gap-2">
                ✏️ 每日练习
                <span className="text-[9px] px-1.5 py-0.5 rounded-full font-semibold" style={{ background: "#f973161c", color: "#f97316", border: "1px solid #f9731633" }}>
                  AI 自适应选题
                </span>
              </div>
              <div className="text-[10px] text-slate-400">
                第 {quizIdx + 1}/{quizQuestions.length} 题 · 已对 {quizScore}
              </div>
            </div>
            <div className="text-sm text-slate-700 leading-relaxed mb-3">
              <span className="text-orange-500 font-semibold mr-1">Q{quizIdx + 1}.</span>
              {q.content}
            </div>
            <div className="space-y-1.5 mb-3">
              {(q.options ?? []).map((opt) => {
                const isCorrect = quizShown && opt.id === q.correct_answer;
                const isWrongPick = quizShown && quizSelected === opt.id && opt.id !== q.correct_answer;
                return (
                  <button
                    key={opt.id}
                    disabled={quizShown}
                    onClick={() => setQuizSelected(opt.id)}
                    className="w-full text-left rounded-lg px-3 py-2 text-xs transition-all flex items-center gap-2"
                    style={{
                      background: isCorrect ? "#ecfdf5" : isWrongPick ? "#fef2f2" : quizSelected === opt.id ? "#eef2ff" : "#f8fafc",
                      border: `1px solid ${isCorrect ? "#34d399" : isWrongPick ? "#f87171" : quizSelected === opt.id ? "#6366f1" : "#e2e8f0"}`,
                      color: isCorrect ? "#059669" : isWrongPick ? "#dc2626" : "#334155",
                    }}
                  >
                    <span className="font-bold">{opt.id}.</span>
                    <span className="flex-1">{opt.text}</span>
                    {isCorrect && <CheckCircleOutlined />}
                    {isWrongPick && <CloseCircleOutlined />}
                  </button>
                );
              })}
            </div>
            {quizShown ? (
              <div className={`mb-3 rounded-lg p-2 ${quizSelected === q.correct_answer ? "feedback-correct" : "feedback-wrong"}`}>
                <div className={`text-xs font-semibold ${quizSelected === q.correct_answer ? "text-emerald-600" : "text-red-500"}`}>
                  {quizSelected === q.correct_answer ? "✅ 回答正确！" : `❌ 正确答案：${q.correct_answer}`}
                </div>
                {q.hint ? <div className="text-[10px] text-slate-400 mt-1">提示：{q.hint}</div> : null}
              </div>
            ) : null}
            {!quizShown ? (
              <button
                onClick={submitAnswer}
                disabled={!quizSelected}
                className="w-full rounded-lg py-2 text-xs font-semibold text-white transition-colors"
                style={{ background: "#f97316", opacity: quizSelected ? 1 : 0.5 }}
              >
                提交答案
              </button>
            ) : (
              <button
                onClick={nextQuiz}
                className="w-full rounded-lg py-2 text-xs font-semibold text-white bg-indigo-500 hover:bg-indigo-600 transition-colors"
              >
                {quizIdx + 1 >= quizQuestions.length ? "查看成绩" : "下一题"}
              </button>
            )}
            {/* 今天不再提醒（自动弹出场景用） */}
            <button
              onClick={() => {
                localStorage.setItem("quiz_dismissed_today", new Date().toISOString().slice(0, 10));
                setOpen(null);
              }}
              className="w-full mt-2 py-1 text-[10px] text-slate-400 hover:text-slate-600 transition-colors"
            >
              今天不再自动弹出
            </button>
          </div>
        );
      case "tasks":
        return (
          <div className="w-[380px]">
            <div className="text-sm font-semibold text-slate-700 mb-2">📋 今日任务</div>
            {data.tasks.length ? (
              <List
                size="small"
                dataSource={data.tasks}
                renderItem={(t) => (
                  <List.Item className="!px-2">
                    <div className="text-xs text-slate-600 flex items-center gap-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-sky-400 shrink-0" />
                      {t.title}
                    </div>
                  </List.Item>
                )}
              />
            ) : (
              <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description={<span className="text-[11px] text-slate-400">暂无待办</span>} />
            )}
          </div>
        );
      case "courses": {
        const courses = ["C语言", "电路分析", "STM32嵌入式"];
        const colors = ["#3b82f6", "#f97316", "#22c55e"];
        return (
          <div className="w-[400px]">
            <div className="text-sm font-semibold text-slate-700 mb-2">📊 课程进度</div>
            <div className="space-y-3">
              {courses.map((c, i) => {
                const nodes = data.graphNodes.filter((n) => n.course === c);
                const done = nodes.filter((n) => n.status === "completed").length;
                const pct = nodes.length ? Math.round((done / nodes.length) * 100) : 0;
                return (
                  <div key={c}>
                    <div className="flex justify-between text-xs mb-1">
                      <span className="text-slate-600"><span style={{ color: colors[i] }}>●</span> {c}</span>
                      <span className="text-slate-400">{done}/{nodes.length} · {pct}%</span>
                    </div>
                    <div className="h-1.5 rounded-full bg-slate-100 overflow-hidden">
                      <div className="h-full rounded-full" style={{ width: `${pct}%`, background: colors[i] }} />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        );
      }
      case "rank":
        return (
          <div className="w-[380px]">
            <div className="text-sm font-semibold text-slate-700 mb-2">🏆 排行榜</div>
            <List
              size="small"
              dataSource={data.topRankers.length ? data.topRankers : [{ name: "暂无数据", score: 0 }]}
              renderItem={(r, i) => (
                <List.Item className="!px-2">
                  <div className="text-xs flex items-center gap-2 w-full">
                    <span className="text-base">{["🥇", "🥈", "🥉"][i] ?? "·"}</span>
                    <span className="text-slate-700 flex-1 truncate">{r.name}</span>
                    <span className="text-slate-400 font-semibold">{r.score}</span>
                  </div>
                </List.Item>
              )}
            />
          </div>
        );
      case "honor":
        return (
          <div className="w-[380px]">
            <div className="text-sm font-semibold text-slate-700 mb-2">🎖 成就积分</div>
            <div className="grid grid-cols-2 gap-3">
              <div className="rounded-xl p-3 bg-amber-50 border border-amber-100 text-center">
                <div className="text-xl font-bold text-amber-600">{data.achievements}</div>
                <div className="text-[10px] text-slate-400">项成就</div>
              </div>
              <div className="rounded-xl p-3 bg-indigo-50 border border-indigo-100 text-center">
                <div className="text-xl font-bold text-indigo-600">{data.points}</div>
                <div className="text-[10px] text-slate-400">积分</div>
              </div>
              <div className="rounded-xl p-3 bg-emerald-50 border border-emerald-100 text-center">
                <div className="text-xl font-bold text-emerald-600">{data.streakDays}</div>
                <div className="text-[10px] text-slate-400">连续打卡</div>
              </div>
              <div className="rounded-xl p-3 bg-sky-50 border border-sky-100 text-center">
                <div className="text-xl font-bold text-sky-600">{data.totalHours}h</div>
                <div className="text-[10px] text-slate-400">累计学习</div>
              </div>
            </div>
          </div>
        );
      case "algorithms": {
        const gd = gktData ?? { bkt: {}, gkt: {} };
        const kps = Object.keys(gd.bkt).slice(0, 6);
        return (
          <div className="w-[420px]">
            <div className="text-sm font-semibold text-slate-700 mb-2 flex items-center gap-2">
              🧬 高级算法中心
              <span className="text-[9px] px-1.5 py-0.5 rounded-full font-semibold" style={{ background: "#8b5cf61c", color: "#8b5cf6", border: "1px solid #8b5cf633" }}>
                GKT · NCD
              </span>
            </div>

            {/* GKT 图感知掌握度对比 */}
            <div className="mb-3">
              <div className="text-xs font-semibold text-slate-600 mb-1.5">
                🕸️ GKT 图知识追踪（图卷积传播）—— BKT vs 图感知
              </div>
              {kps.length ? (
                <div className="space-y-1.5">
                  {kps.map((kp) => {
                    const b = gd.bkt[kp] ?? 0;
                    const g = gd.gkt[kp] ?? 0;
                    return (
                      <div key={kp} className="flex items-center gap-2 text-[10px]">
                        <span className="w-20 truncate text-slate-500 shrink-0">{kp}</span>
                        <div className="flex-1 h-1.5 rounded-full bg-slate-100 overflow-hidden">
                          <div className="h-full rounded-full" style={{ width: `${b * 100}%`, background: "#6366f1", opacity: 0.6 }} />
                        </div>
                        <div className="flex-1 h-1.5 rounded-full bg-slate-100 overflow-hidden">
                          <div className="h-full rounded-full" style={{ width: `${g * 100}%`, background: "#8b5cf6" }} />
                        </div>
                        <span className="w-12 text-right text-slate-400">{Math.round(b * 100)}→{Math.round(g * 100)}%</span>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className="text-[11px] text-slate-400">加载 GKT 数据…</div>
              )}
              <div className="text-[9px] text-slate-400 mt-1">浅蓝=BKT 单独预测 · 紫=图卷积后（邻居知识点影响）</div>
            </div>

            {/* NCD vs IRT 能力对比 */}
            <div className="pt-2 border-t border-slate-100">
              <div className="text-xs font-semibold text-slate-600 mb-2">🧠 能力诊断对比</div>
              <div className="grid grid-cols-2 gap-2">
                <div className="rounded-xl p-2.5 text-center" style={{ background: "#8b5cf614", border: "1px solid #8b5cf633" }}>
                  <div className="text-[9px] text-slate-400">NCD 神经认知诊断</div>
                  <div className="text-lg font-bold" style={{ color: "#8b5cf6" }}>{ncdAbility != null ? ncdAbility.toFixed(2) : "…"}</div>
                </div>
                <div className="rounded-xl p-2.5 text-center" style={{ background: "#22d3ee14", border: "1px solid #22d3ee33" }}>
                  <div className="text-[9px] text-slate-400">IRT 能力 θ</div>
                  <div className="text-lg font-bold" style={{ color: "#0891b2" }}>{irtAbility != null ? irtAbility.toFixed(2) : "…"}</div>
                </div>
              </div>
              <div className="text-[9px] text-slate-400 mt-1.5">
                NCD = 神经网络 + 单调约束（AAAI 2020）· GKT = 图卷积传播（WI 2019）
              </div>
            </div>
          </div>
        );
      }
      case "legend":
        return (
          <div className="w-[300px]">
            <div className="text-sm font-semibold text-slate-700 mb-2">🧭 图谱图例</div>
            <div className="space-y-1.5 mb-2">
              <div className="flex items-center gap-2 text-xs"><span style={{ color: "#3b82f6" }}>●</span><span className="text-slate-600">C语言 · 计算机</span></div>
              <div className="flex items-center gap-2 text-xs"><span style={{ color: "#f97316" }}>●</span><span className="text-slate-600">电路分析 · 电子</span></div>
              <div className="flex items-center gap-2 text-xs"><span style={{ color: "#22c55e" }}>●</span><span className="text-slate-600">STM32 · 交叉</span></div>
            </div>
            <div className="pt-2 border-t border-slate-100 space-y-1.5">
              <div className="flex items-center gap-2 text-xs"><span style={{ color: "#34d399" }}>◉</span><span className="text-slate-600">已掌握</span></div>
              <div className="flex items-center gap-2 text-xs"><span style={{ color: "#60a5fa" }}>◉</span><span className="text-slate-600">学习中（呼吸光环）</span></div>
              <div className="flex items-center gap-2 text-xs"><span style={{ color: "#94a3b8" }}>◉</span><span className="text-slate-600">待学习</span></div>
              <div className="flex items-center gap-2 text-xs"><span style={{ color: "#64748b" }}>◌</span><span className="text-slate-600">未解锁</span></div>
              <div className="flex items-center gap-2 text-xs"><span style={{ color: "#ef4444" }}>◎</span><span className="text-slate-600">薄弱点（红环）</span></div>
            </div>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <>
      {/* 今日任务：右上角展开显示（常驻完整列表） */}
      <div className="fixed right-4 top-3 z-[9999] pointer-events-none">
        <div
          className="w-[240px] rounded-2xl p-3"
          style={{
            background: "rgba(255,255,255,0.92)",
            border: "1px solid rgba(14,165,233,0.3)",
            boxShadow: "0 8px 28px rgba(15,23,42,0.12)",
            backdropFilter: "blur(10px)",
          }}
        >
          <div className="flex items-center gap-2 text-xs font-semibold mb-2" style={{ color: "#0ea5e9" }}>
            <UnorderedListOutlined />
            今日任务
            <span className="px-1.5 rounded-full text-white text-[10px] ml-auto" style={{ background: "#0ea5e9" }}>
              {data.tasks.length}
            </span>
          </div>
          {data.tasks.length ? (
            <div className="space-y-1.5">
              {data.tasks.slice(0, 4).map((t, i) => (
                <div key={i} className="flex items-start gap-1.5 text-[11px]" style={{ color: "#334155" }}>
                  <span className="mt-0.5 w-1.5 h-1.5 rounded-full shrink-0" style={{ background: "#38bdf8" }} />
                  <span className="leading-snug">{t.title}</span>
                </div>
              ))}
              {data.tasks.length > 4 && (
                <div className="text-[10px] text-slate-400">还有 {data.tasks.length - 4} 项…</div>
              )}
            </div>
          ) : (
            <div className="text-[11px]" style={{ color: "#94a3b8" }}>暂无待办，享受学习吧</div>
          )}
        </div>
      </div>

      {/* 悬浮按钮组（右侧，fixed 绝对顶层） */}
      <div className="fixed right-4 top-1/2 -translate-y-1/2 flex flex-col gap-2" style={{ zIndex: 9999 }}>
        {mainTools.map((t) => (
          <button
            key={t.key}
            onClick={() => setOpen(open === t.key ? null : t.key)}
            title={t.label}
            className="w-10 h-10 rounded-full flex items-center justify-center text-base transition-all hover:scale-110"
            style={{
              background: open === t.key ? t.color : "rgba(255,255,255,0.85)",
              color: open === t.key ? "#fff" : t.color,
              border: `1px solid ${t.color}44`,
              boxShadow: "0 4px 14px rgba(15,23,42,0.1)",
              backdropFilter: "blur(8px)",
            }}
          >
            {t.icon}
          </button>
        ))}
        {/* 更多按钮：收起次要工具 */}
        <button
          onClick={() => setShowMore(!showMore)}
          title="更多"
          className="w-10 h-10 rounded-full flex items-center justify-center text-sm transition-all hover:scale-110"
          style={{
            background: "rgba(255,255,255,0.85)",
            color: "#64748b",
            border: "1px solid rgba(100,116,139,0.3)",
            boxShadow: "0 4px 14px rgba(15,23,42,0.1)",
            backdropFilter: "blur(8px)",
          }}
        >
          {showMore ? "×" : "•••"}
        </button>
        {showMore && (
          <div className="flex flex-col gap-2">
            {moreTools.map((t) => (
              <button
                key={t.key}
                onClick={() => setOpen(open === t.key ? null : t.key)}
                title={t.label}
                className="w-10 h-10 rounded-full flex items-center justify-center text-base transition-all hover:scale-110"
                style={{
                  background: open === t.key ? t.color : "rgba(255,255,255,0.85)",
                  color: open === t.key ? "#fff" : t.color,
                  border: `1px solid ${t.color}44`,
                  boxShadow: "0 4px 14px rgba(15,23,42,0.1)",
                  backdropFilter: "blur(8px)",
                }}
              >
                {t.icon}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* 每日练习：居中大弹窗（带遮罩，进来清晰直接做） */}
      {open === "quiz" && (
        <div
          className="fixed inset-0 flex items-center justify-center z-[9999]"
          style={{ background: "rgba(15,23,42,0.4)", backdropFilter: "blur(4px)" }}
          onClick={() => setOpen(null)}
        >
          <div
            className="relative rounded-3xl p-6"
            style={{
              background: "rgba(255,255,255,0.98)",
              border: "1px solid rgba(148,163,184,0.35)",
              boxShadow: "0 32px 80px rgba(15,23,42,0.35)",
              maxHeight: "82vh",
              overflowY: "auto",
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <button
              onClick={() => setOpen(null)}
              className="absolute -top-2.5 -right-2.5 w-7 h-7 rounded-full bg-slate-700 text-white text-xs flex items-center justify-center hover:bg-slate-600"
              style={{ zIndex: 10000 }}
            >
              <CloseOutlined />
            </button>
            {renderPanel()}
          </div>
        </div>
      )}

      {/* 其他面板（右侧滑出） */}
      {open && open !== "quiz" && (
        <div className="fixed right-16 top-1/2 -translate-y-1/2" style={{ zIndex: 9999 }}>
          <div
            className="relative rounded-2xl p-5"
            style={{
              background: "rgba(255,255,255,0.96)",
              border: "1px solid rgba(148,163,184,0.35)",
              boxShadow: "0 24px 64px rgba(15,23,42,0.25)",
              backdropFilter: "blur(18px)",
              maxHeight: "80vh",
              overflowY: "auto",
            }}
          >
            <button
              onClick={() => setOpen(null)}
              className="absolute -top-2 -right-2 w-6 h-6 rounded-full bg-slate-700 text-white text-[10px] flex items-center justify-center hover:bg-slate-600"
              style={{ zIndex: 10000 }}
            >
              <CloseOutlined />
            </button>
            {renderPanel()}
          </div>
        </div>
      )}
    </>
  );
};

export default FloatingTools;
