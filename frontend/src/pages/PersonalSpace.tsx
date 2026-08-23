import React, { useEffect, useState, useMemo, useRef } from "react";
import {
  Typography,
  Tabs,
  List,
  Avatar,
  Tag,
  Space,
  Button,
  Progress,
  Row,
  Col,
  message,
} from "antd";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
} from "recharts";
import { useNavigate, useSearchParams } from "react-router-dom";
import {
  FileTextOutlined,
  VideoCameraOutlined,
  CodeOutlined,
  StarOutlined,
  HeartOutlined,
  HistoryOutlined,
  EditOutlined,
  TrophyOutlined,
  FireOutlined,
  ClockCircleOutlined,
  BarChartOutlined,
  LineChartOutlined,
  CrownOutlined,
  ThunderboltOutlined,
  BulbOutlined,
  MessageOutlined,
  ApartmentOutlined,
  CheckCircleOutlined,
  PlayCircleOutlined,
  PauseCircleOutlined,
} from "@ant-design/icons";
import type {
  ReflectionEntry,
  StudentProfile,
  // DashboardStats,
  Achievement,
} from "../types";
import { useAppStore } from "../store";

interface FavoriteItem {
  id?: string;
  title: string;
  resource_type: string;
  url?: string;
}

interface HistoryItem {
  title: string;
  time: string;
  type: string;
}

interface FocusItem {
  day: string;
  focus: number;
  duration: number;
}

interface ReviewTopic {
  topic: string;
  retention: number;
  nextReview: string;
}

interface BadgeItemLocal {
  id: string;
  name: string;
  desc: string;
  icon: React.ReactNode;
  color: string;
  unlocked: boolean;
  unlocked_at?: string;
}
import {
  profileApi,
  dashboardApi,
  gamificationApi,
  learningDataApi,
  favoritesApi,
  logReflectionApi,
  trendApi,
} from "../services/api";
import { buildRadarData } from "../utils/profile";
import { StatCard } from "../components/StatCard";
import Leaderboard from "../components/Leaderboard";
import GrowthTimeline from "../components/GrowthTimeline";
import { Input, Collapse, Drawer, Popconfirm } from "antd";
import {
  CaretRightOutlined,
  AlertOutlined,
  RiseOutlined,
  FallOutlined,
  DeleteOutlined,
} from "@ant-design/icons";

const typeMeta: Record<
  string,
  { icon: React.ReactNode; color: string; bg: string; label: string }
> = {
  video: {
    icon: <VideoCameraOutlined />,
    color: "#ef4444",
    bg: "#fef2f2",
    label: "视频",
  },
  quiz: {
    icon: <TrophyOutlined />,
    color: "#f59e0b",
    bg: "#fffbeb",
    label: "练习",
  },
  code: {
    icon: <CodeOutlined />,
    color: "#3b82f6",
    bg: "#eff6ff",
    label: "代码",
  },
  profile: {
    icon: <EditOutlined />,
    color: "#8b5cf6",
    bg: "#f5f3ff",
    label: "画像",
  },
  doc: {
    icon: <FileTextOutlined />,
    color: "#10b981",
    bg: "#ecfdf5",
    label: "文档",
  },
  document: {
    icon: <FileTextOutlined />,
    color: "#10b981",
    bg: "#ecfdf5",
    label: "文档",
  },
  mindmap: {
    icon: <ApartmentOutlined />,
    color: "#8b5cf6",
    bg: "#f5f3ff",
    label: "思维导图",
  },
};

const defaultBadges = [
  {
    id: "1",
    name: "初出茅庐",
    desc: "完成首次学习",
    icon: <StarOutlined />,
    color: "#f59e0b",
  },
  {
    id: "2",
    name: "代码能手",
    desc: "完成5次代码实操",
    icon: <CodeOutlined />,
    color: "#3b82f6",
  },
  {
    id: "3",
    name: "学习王者",
    desc: "连续打卡30天",
    icon: <CrownOutlined />,
    color: "#ef4444",
  },
  {
    id: "4",
    name: "全勤标兵",
    desc: "连续7天完成每日挑战",
    icon: <FireOutlined />,
    color: "#10b981",
  },
  {
    id: "5",
    name: "思维导图",
    desc: "生成10张思维导图",
    icon: <ApartmentOutlined />,
    color: "#8b5cf6",
  },
  {
    id: "6",
    name: "提问达人",
    desc: "向AI辅导提问50次",
    icon: <MessageOutlined />,
    color: "#0ea5e9",
  },
  {
    id: "7",
    name: "知识探索者",
    desc: "完成全部基础章节",
    icon: <BulbOutlined />,
    color: "#f59e0b",
  },
  {
    id: "8",
    name: "完美通过",
    desc: "测验全部满分",
    icon: <CheckCircleOutlined />,
    color: "#10b981",
  },
];

// 番茄钟组件
const POMODORO_FOCUS = 25 * 60;
const POMODORO_BREAK = 5 * 60;

const PomodoroTimer: React.FC = () => {
  const [pomodoroTime, setPomodoroTime] = useState(() => {
    try {
      const saved = sessionStorage.getItem("pomodoro_state");
      if (saved) {
        const s = JSON.parse(saved);
        return s.time ?? POMODORO_FOCUS;
      }
    } catch {}
    return POMODORO_FOCUS;
  });
  const pomodoroEndRef = useRef<number | null>(null);
  const [isPomodoroRunning, setIsPomodoroRunning] = useState(() => {
    try {
      const saved = sessionStorage.getItem("pomodoro_state");
      if (saved) {
        const s = JSON.parse(saved);
        if (s.running && s.endTime) pomodoroEndRef.current = s.endTime;
        return s.running ?? false;
      }
    } catch {}
    return false;
  });
  const isBreakRef = useRef(false);
  const [isBreak, setIsBreak] = useState(() => {
    try {
      const saved = sessionStorage.getItem("pomodoro_state");
      if (saved) {
        const s = JSON.parse(saved);
        isBreakRef.current = s.isBreak ?? false;
        return s.isBreak ?? false;
      }
    } catch {}
    return false;
  });
  const [pomodoroCount, setPomodoroCount] = useState(() => {
    try {
      const saved = sessionStorage.getItem("pomodoro_state");
      if (saved) return JSON.parse(saved).count ?? 0;
    } catch {}
    return 0;
  });

  // Pomodoro timer
  useEffect(() => {
    if (!isPomodoroRunning) {
      pomodoroEndRef.current = null;
      return;
    }
    if (pomodoroEndRef.current == null) {
      pomodoroEndRef.current = Date.now() + pomodoroTime * 1000;
    }
    const tick = () => {
      const end = pomodoroEndRef.current;
      if (end == null) return;
      const remain = Math.max(0, Math.round((end - Date.now()) / 1000));
      setPomodoroTime(remain);
      if (remain <= 0) {
        setIsPomodoroRunning(false);
        pomodoroEndRef.current = null;
        if (!isBreakRef.current) {
          setPomodoroCount((c: number) => c + 1);
          message.success("专注时间结束！休息一下吧");
          isBreakRef.current = true;
          setIsBreak(true);
          setPomodoroTime(POMODORO_BREAK);
        } else {
          message.success("休息结束，继续专注！");
          isBreakRef.current = false;
          setIsBreak(false);
          setPomodoroTime(POMODORO_FOCUS);
        }
      }
    };
    const timer = setInterval(tick, 1000);
    return () => clearInterval(timer);
  }, [isPomodoroRunning]);

  // 持久化番茄钟状态到 sessionStorage
  useEffect(() => {
    const state = {
      time: pomodoroTime,
      running: isPomodoroRunning,
      isBreak: isBreak,
      count: pomodoroCount,
      endTime: pomodoroEndRef.current,
    };
    sessionStorage.setItem("pomodoro_state", JSON.stringify(state));
  }, [pomodoroTime, isPomodoroRunning, isBreak, pomodoroCount]);

  return (
    <div className="bg-white rounded-2xl border border-slate-100 p-6">
      <div className="flex items-center justify-between mb-5">
        <div className="flex items-center gap-2">
          <ClockCircleOutlined className="text-primary text-lg" />
          <span className="font-semibold text-slate-800">番茄专注钟</span>
        </div>
        <Tag className="rounded-full border-0 bg-primary-50 text-primary text-xs font-medium">
          {pomodoroCount} 个番茄
        </Tag>
      </div>
      <div className="text-center py-4">
        <div
          className={`text-7xl font-bold tracking-tight mb-4 ${isBreak ? "text-emerald-500" : "text-primary"}`}
        >
          {Math.floor(pomodoroTime / 60)
            .toString()
            .padStart(2, "0")}
          :{(pomodoroTime % 60).toString().padStart(2, "0")}
        </div>
        <div className="text-sm text-slate-400 mb-6">
          {isBreak ? "休息时间 · 恢复精力" : "专注时间 · 保持高效"}
        </div>
        <Space>
          <Button
            type="primary"
            shape="round"
            size="large"
            icon={
              isPomodoroRunning ? (
                <PauseCircleOutlined />
              ) : (
                <PlayCircleOutlined />
              )
            }
            onClick={() => setIsPomodoroRunning(!isPomodoroRunning)}
            className="bg-primary"
          >
            {isPomodoroRunning ? "暂停" : "开始"}
          </Button>
          <Button
            shape="round"
            size="large"
            onClick={() => {
              setIsPomodoroRunning(false);
              setPomodoroTime(isBreak ? POMODORO_BREAK : POMODORO_FOCUS);
            }}
          >
            重置
          </Button>
        </Space>
      </div>
    </div>
  );
};

const PersonalSpace: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const initialTab = searchParams.get("tab") || "history";
  const [activeTab, setActiveTab] = useState<string>(initialTab);
  const [profile, setProfile] = useState<StudentProfile | null>(null);
  const [profileData, setProfileData] = useState(buildRadarData(null));
  const [dashboardStats, setDashboardStats] = useState<Record<
    string,
    unknown
  > | null>(null);
  const [_points, setPoints] = useState<Record<string, unknown> | null>(null);
  const [achievements, setAchievements] = useState<Achievement[]>([]);
  const [reflections, setReflections] = useState<ReflectionEntry[]>([]);
  const [newReflection, setNewReflection] = useState("");
  const [favorites, setFavorites] = useState<FavoriteItem[]>([]); // 保留状态但不再有UI入口
  const [learningHistory, setLearningHistory] = useState<HistoryItem[]>([]);
  const [focusData, setFocusData] = useState<FocusItem[]>([]);
  const [pomodoroStats, setPomodoroStats] = useState({
    total: 0,
    today: 0,
    streak: 0,
  });
  const [cornellNotes, setCornellNotes] = useState({
    cues: "",
    notes: "",
    summary: "",
  });
  const [feynmanInput, setFeynmanInput] = useState("");
  const [reviewTopics, setReviewTopics] = useState<ReviewTopic[]>([]);
  const [trendInfo, setTrendInfo] = useState<{
    state: string;
    factor: number;
    dimensions: Record<string, number>;
    intervention: string;
  } | null>(null);
  const [notesHistory, setNotesHistory] = useState<
    Array<{
      id: string;
      date: string;
      type: "cornell" | "notes" | "feynman" | "other";
      title: string;
      content: string;
      rawContent?: string;
    }>
  >([]);
  // 笔记编辑抽屉
  const [editingNote, setEditingNote] = useState<{
    id: string;
    date: string;
    type: "cornell" | "notes" | "feynman" | "other";
    title: string;
    cues?: string;
    notes?: string;
    summary?: string;
    content?: string;
  } | null>(null);
  const [editDrawerOpen, setEditDrawerOpen] = useState(false);
  const [savingEdit, setSavingEdit] = useState(false);
  // 画像维度详情 & 遗忘曲线补充数据
  const [dimensions, setDimensions] = useState<
    { label: string; value: number; color: string }[]
  >([]);
  const [retentionItems, setRetentionItems] = useState<
    { topic: string; retention: number; nextReview: string }[]
  >([]);
  const [historyData, setHistoryData] = useState<
    { date: string; value: number }[]
  >([]);
  const studentId = useAppStore((s) => s.studentId);
  const loadedTabs = useRef<Set<string>>(new Set());

  // 同步 URL 中的 tab 参数到激活 Tab
  useEffect(() => {
    const t = searchParams.get("tab");
    if (t && t !== activeTab) setActiveTab(t);
  }, [searchParams]);

  // 页面重新可见时刷新数据（从其他页面返回时同步更新）
  useEffect(() => {
    const handleVisibility = () => {
      if (document.visibilityState === "visible" && studentId) {
        loadedTabs.current.clear();
      }
    };
    document.addEventListener("visibilitychange", handleVisibility);
    return () =>
      document.removeEventListener("visibilitychange", handleVisibility);
  }, [studentId]);

  useEffect(() => {
    const load = async () => {
      if (!studentId) return;
      if (loadedTabs.current.has(activeTab)) return;

      const safe = <T,>(p: Promise<T>): Promise<T | null> =>
        p.catch(() => null);

      // 按 Tab 分组：只拉取当前 Tab 需要的接口
      const needsHistory = activeTab === "history";
      const needsBadges = activeTab === "profile";
      const needsLeaderboard = activeTab === "profile";
      const needsFavorites = activeTab === "favorites";
      const needsReflections = activeTab === "notes";

      // profile 总是拉取（多个 Tab 依赖 weak_areas 等字段）
      const [pRes, dRes, ptRes, aRes, hRes, thRes, fRes, rRes] =
        await Promise.all([
          safe(profileApi.get(studentId)),
          needsHistory || needsLeaderboard
            ? safe(dashboardApi.getSummary(studentId))
            : Promise.resolve(null),
          needsBadges
            ? safe(gamificationApi.getPoints(studentId))
            : Promise.resolve(null),
          needsBadges
            ? safe(gamificationApi.getAchievements(studentId))
            : Promise.resolve(null),
          needsHistory
            ? safe(learningDataApi.getHistory(studentId, 200))
            : Promise.resolve(null),
          needsHistory
            ? safe(trendApi.getHistory(studentId, 7))
            : Promise.resolve(null),
          needsFavorites
            ? safe(favoritesApi.get(studentId))
            : Promise.resolve(null),
          needsReflections
            ? safe(logReflectionApi.getReflections(studentId, 100))
            : Promise.resolve(null),
        ]);

      loadedTabs.current.add(activeTab);

      try {
        if (pRes?.data?.data) {
          setProfile(pRes.data.data);
          const radar = buildRadarData(pRes.data.data);
          setProfileData(radar);
          // 维度详情
          setDimensions(
            radar.map((item) => ({
              label: item.subject,
              value: Math.round(item.A),
              color:
                item.subject === "知识基础"
                  ? "#4f46e5"
                  : item.subject === "认知风格"
                    ? "#0ea5e9"
                    : item.subject === "学习偏好"
                      ? "#10b981"
                      : item.subject === "薄弱点"
                        ? "#f59e0b"
                        : item.subject === "学习进度"
                          ? "#8b5cf6"
                          : "#ec4899",
            })),
          );
          // 遗忘曲线数据：从API获取
          const retentionRes = await safe(profileApi.getRetention(studentId));
          if (retentionRes?.data?.data) {
            setRetentionItems(retentionRes.data.data);
          }
        }
        if (dRes?.data)
          setDashboardStats(dRes.data as unknown as Record<string, unknown>);
        if (ptRes?.data?.data) setPoints(ptRes.data.data);
        if (aRes?.data?.data) setAchievements(aRes.data.data);

        const recordsRaw =
          (hRes?.data?.records as unknown as Record<string, unknown>[]) || [];
        const quizzesRaw =
          (hRes?.data?.quizzes as unknown as Record<string, unknown>[]) || [];

        // 最近列表（前 5 条）展示 — 精确到小节
        if (recordsRaw.length) {
          const mapped = recordsRaw.slice(0, 5).map((r) => {
            const actionLabel =
              r.action === "complete"
                ? "已完成"
                : r.action === "watch"
                  ? "观看视频"
                  : r.action === "read"
                    ? "阅读文档"
                    : r.action === "practice"
                      ? "练习代码"
                      : r.action || "学习";
            const kpName = r.kp_name || r.kp_id || "";
            return {
              title: `${actionLabel} · ${kpName}`,
              time: r.created_at
                ? new Date(String(r.created_at)).toLocaleString()
                : "近期",
              type: String(r.action || "").includes("代码")
                ? "code"
                : String(r.action || "").includes("测验")
                  ? "quiz"
                  : "doc",
            };
          });
          setLearningHistory(mapped);
        }

        // ---- 周专注度&时长聚合（最近 7 天）----
        const dayKeys: string[] = [];
        const today = new Date();
        for (let i = 6; i >= 0; i--) {
          const d = new Date(today);
          d.setDate(today.getDate() - i);
          dayKeys.push(d.toISOString().slice(0, 10));
        }
        const dayLabels = [
          "周日",
          "周一",
          "周二",
          "周三",
          "周四",
          "周五",
          "周六",
        ];
        const focusAgg: Record<
          string,
          {
            progressSum: number;
            count: number;
            durationSum: number;
            quizScoreSum: number;
            quizCount: number;
            pomodoros: number;
          }
        > = {};
        dayKeys.forEach((d) => {
          focusAgg[d] = {
            progressSum: 0,
            count: 0,
            durationSum: 0,
            quizScoreSum: 0,
            quizCount: 0,
            pomodoros: 0,
          };
        });
        let totalPomodoros = 0;
        recordsRaw.forEach((r) => {
          const dateStr = String(r.created_at || "").slice(0, 10);
          const dur = Number(r.duration) || 0;
          const action = String(r.action || "");
          const isPomodoro =
            dur >= 20 * 60 ||
            action === "complete" ||
            action === "practice" ||
            action === "quiz";
          if (isPomodoro) totalPomodoros += 1;
          if (focusAgg[dateStr]) {
            focusAgg[dateStr].progressSum += Number(r.progress) || 0;
            focusAgg[dateStr].count += 1;
            focusAgg[dateStr].durationSum += dur;
            if (isPomodoro) focusAgg[dateStr].pomodoros += 1;
          }
        });
        quizzesRaw.forEach((q) => {
          const dateStr = String(q.created_at || "").slice(0, 10);
          if (focusAgg[dateStr]) {
            focusAgg[dateStr].quizScoreSum += Number(q.score) || 0;
            focusAgg[dateStr].quizCount += 1;
          }
        });

        // ---- 趋势历史（驱动专注度折线）----
        const trendByDate: Record<string, number> = {};
        const trendList =
          (thRes?.data?.data as
            | Array<{ date: string; trend_factor: number }>
            | undefined) || [];
        // 画像历史变化（近7天）
        if (trendList.length) {
          setHistoryData(
            trendList.slice(-7).map((d) => ({
              date: d.date.slice(5),
              value: Math.round(d.trend_factor * 100),
            })),
          );
        }
        trendList.forEach((tp) => {
          const f = Math.max(-1, Math.min(1, Number(tp.trend_factor) || 0));
          trendByDate[String(tp.date).slice(0, 10)] = Math.round((f + 1) * 50);
        });

        const aggregated: FocusItem[] = dayKeys.map((d) => {
          const agg = focusAgg[d];
          let focus = 0;
          if (trendByDate[d] !== undefined) {
            focus = trendByDate[d];
          } else if (agg.quizCount > 0) {
            focus = Math.round(agg.quizScoreSum / agg.quizCount);
          } else if (agg.count > 0) {
            focus = Math.round((agg.progressSum / agg.count) * 100);
          }
          return {
            day: dayLabels[new Date(d).getDay()],
            focus: Math.max(0, Math.min(100, focus)),
            duration: Math.round(agg.durationSum / 6) / 10,
          };
        });
        if (aggregated.some((a) => a.focus > 0 || a.duration > 0)) {
          setFocusData(aggregated);
        }

        // ---- 番茄钟统计 ----
        const todayKey = dayKeys[dayKeys.length - 1];
        const todayPomos = focusAgg[todayKey]?.pomodoros || 0;
        let streak = 0;
        for (let i = dayKeys.length - 1; i >= 0; i--) {
          if ((focusAgg[dayKeys[i]]?.pomodoros || 0) > 0) streak += 1;
          else break;
        }
        setPomodoroStats({ total: totalPomodoros, today: todayPomos, streak });

        // ---- 待复习知识点 ----
        const weakList: string[] =
          (pRes?.data?.data?.weak_areas as string[] | undefined) || [];
        const tagScoreMap: Record<string, { sum: number; n: number }> = {};
        quizzesRaw.forEach((q) => {
          const tags = (q.weak_tags as string[] | undefined) || [];
          const score = Number(q.score) || 0;
          tags.forEach((t) => {
            if (!tagScoreMap[t]) tagScoreMap[t] = { sum: 0, n: 0 };
            tagScoreMap[t].sum += score;
            tagScoreMap[t].n += 1;
          });
        });
        if (weakList.length) {
          const reviews: ReviewTopic[] = weakList.slice(0, 6).map((w, i) => {
            const stat = tagScoreMap[w];
            const baseRetention =
              stat && stat.n > 0
                ? Math.round(stat.sum / stat.n)
                : Math.max(30, 70 - i * 8);
            const retention = Math.max(20, Math.min(95, baseRetention));
            const nextReview =
              retention < 50 ? "今天" : retention < 70 ? "明天" : "3天后";
            return { topic: w, retention, nextReview };
          });
          setReviewTopics(reviews);
        }

        // Favorites
        if (fRes?.data?.data) setFavorites(fRes.data.data as FavoriteItem[]);

        // Reflections
        if (rRes?.data?.data) {
          const all = rRes.data.data as Record<string, unknown>[];
          const refs = all
            .filter((r) => {
              const tags = String(r.tags || "");
              return (
                !tags.includes("cornell") &&
                !tags.includes("feynman") &&
                !tags.includes("notes")
              );
            })
            .map((r) => ({
              id: String(r.reflection_id || `ref_${Date.now()}`),
              date: String(r.date || ""),
              content: String(r.content || ""),
              topic: (r.tags as string[])?.[0] || "今日学习",
            }));
          setReflections(refs);

          const cornellList = all.filter((r) =>
            (r.tags as string[] | undefined)?.includes("cornell"),
          );
          const cornell = cornellList[0];
          if (cornell) {
            try {
              setCornellNotes(JSON.parse(String(cornell.content)));
            } catch {
              setCornellNotes({
                cues: String(cornell.content),
                notes: "",
                summary: "",
              });
            }
          }
          const feynman = all.find((r) =>
            (r.tags as string[] | undefined)?.includes("feynman"),
          );
          if (feynman) setFeynmanInput(String(feynman.content));

          const noteEntries = all
            .filter((r) => {
              const tags = (r.tags as string[] | undefined) || [];
              return (
                tags.includes("cornell") ||
                tags.includes("notes") ||
                tags.includes("feynman")
              );
            })
            .map((r) => {
              const tags = (r.tags as string[] | undefined) || [];
              const isCornell = tags.includes("cornell");
              const isFeynman = tags.includes("feynman");
              const kpTag = tags.find(
                (t) => t && t !== "cornell" && t !== "notes" && t !== "feynman",
              );
              const rawContent = String(r.content || "");
              let preview = rawContent;
              let title = isCornell
                ? "康奈尔笔记"
                : isFeynman
                  ? "费曼练习"
                  : "学习笔记";
              if (isCornell) {
                try {
                  const parsed = JSON.parse(rawContent) as {
                    cues?: string;
                    notes?: string;
                    summary?: string;
                  };
                  preview = [parsed.summary, parsed.notes, parsed.cues]
                    .filter(Boolean)
                    .join("\n");
                } catch {
                  // 保留原文
                }
              }
              if (kpTag) title += ` · ${kpTag}`;
              const type: "cornell" | "notes" | "feynman" = isCornell
                ? "cornell"
                : isFeynman
                  ? "feynman"
                  : "notes";
              return {
                id: String(
                  r.reflection_id || `note_${Date.now()}_${Math.random()}`,
                ),
                date: String(r.date || ""),
                type,
                title,
                content: preview,
                rawContent,
              };
            })
            .sort((a, b) => (a.date > b.date ? -1 : 1));
          setNotesHistory(noteEntries);
        }

        // ---- 趋势分析（POST /trend/analyze 是写操作，不并发，放在最后单独跑）----
        try {
          const tRes = await trendApi.analyze(studentId);
          const td = tRes.data?.data as Record<string, unknown> | undefined;
          if (td) {
            setTrendInfo({
              state: String(td.trend_state || "stable"),
              factor: Number(td.trend_factor) || 0,
              dimensions: (td.dimensions as Record<string, number>) || {},
              intervention: String(td.intervention || ""),
            });
          }
        } catch {
          // 趋势分析失败时静默
        }
      } catch {
        // 静默处理聚合错误
      }
    };
    load();
  }, [studentId, activeTab]);

  const weakAreas = profile?.weak_areas || [];
  const cognitivePrimary = profile?.cognitive_style?.primary || "visual";
  const studySpeed = profile?.learning_tempo?.study_speed || "moderate";

  const handleAddReflection = async () => {
    if (!newReflection.trim()) return;
    try {
      const today = new Date().toISOString().slice(0, 10);
      await logReflectionApi.createReflection({
        student_id: studentId,
        date: today,
        content: newReflection.trim(),
        mood: "neutral",
        tags: ["今日学习"],
      });
      const entry: ReflectionEntry = {
        id: `ref_${studentId}_${today}_${Date.now()}`,
        date: today,
        content: newReflection.trim(),
        topic: "今日学习",
      };
      setReflections([entry, ...reflections]);
      setNewReflection("");
      message.success("反思已保存");
      // 同步到画像
      const conversationContext = `学生写了今日反思：${newReflection.trim()}`;
      profileApi
        .analyzeConversation(studentId, conversationContext)
        .catch(() => {});
    } catch (_e) {
      message.error("保存失败");
    }
  };

  const handleSaveCornell = async () => {
    try {
      const today = new Date().toISOString().slice(0, 10);
      const rawContent = JSON.stringify(cornellNotes);
      const res = await logReflectionApi.createReflection({
        student_id: studentId,
        date: today,
        content: rawContent,
        tags: ["cornell"],
      });
      const newId = String(res.data?.reflection_id || `note_${Date.now()}`);
      const preview = [
        cornellNotes.summary,
        cornellNotes.notes,
        cornellNotes.cues,
      ]
        .filter(Boolean)
        .join("\n");
      setNotesHistory((prev) => [
        {
          id: newId,
          date: today,
          type: "cornell",
          title: "康奈尔笔记",
          content: preview,
          rawContent,
        },
        ...prev,
      ]);
      message.success("康奈尔笔记已保存");

      // 同步到画像
      const conversationContext = `学生记录了康奈尔笔记：线索栏：${cornellNotes.cues}；笔记栏：${cornellNotes.notes}；总结：${cornellNotes.summary}`;
      profileApi
        .analyzeConversation(studentId, conversationContext)
        .catch(() => {});
    } catch (_e) {
      message.error("保存失败");
    }
  };

  // 康奈尔笔记自动保存（防抖 2 秒）
  const cornellAutoSaveTimer = useRef<ReturnType<typeof setTimeout> | null>(
    null,
  );
  const cornellDirtyRef = useRef(false);

  useEffect(() => {
    cornellDirtyRef.current = true;
    if (cornellAutoSaveTimer.current)
      clearTimeout(cornellAutoSaveTimer.current);
    cornellAutoSaveTimer.current = setTimeout(() => {
      if (
        cornellDirtyRef.current &&
        (cornellNotes.cues || cornellNotes.notes || cornellNotes.summary)
      ) {
        cornellDirtyRef.current = false;
        handleSaveCornell();
      }
    }, 2000);
    return () => {
      if (cornellAutoSaveTimer.current)
        clearTimeout(cornellAutoSaveTimer.current);
    };
  }, [cornellNotes.cues, cornellNotes.notes, cornellNotes.summary]);

  const handleSaveFeynman = async () => {
    if (!feynmanInput.trim()) return;
    try {
      const today = new Date().toISOString().slice(0, 10);
      const res = await logReflectionApi.createReflection({
        student_id: studentId,
        date: today,
        content: feynmanInput.trim(),
        tags: ["feynman"],
      });
      const newId = String(res.data?.reflection_id || `note_${Date.now()}`);
      setNotesHistory((prev) => [
        {
          id: newId,
          date: today,
          type: "feynman",
          title: "费曼练习",
          content: feynmanInput.trim(),
        },
        ...prev,
      ]);
      message.success("费曼练习已保存");
      // 同步到画像
      const conversationContext = `学生进行了费曼练习，用自己的话解释：${feynmanInput.trim()}`;
      profileApi
        .analyzeConversation(studentId, conversationContext)
        .catch(() => {});
      setFeynmanInput("");
    } catch (_e) {
      message.error("保存失败");
    }
  };

  // 打开笔记编辑抽屉
  const handleOpenNoteEdit = (n: {
    id: string;
    date: string;
    type: "cornell" | "notes" | "feynman" | "other";
    title: string;
    content: string;
    rawContent?: string;
  }) => {
    if (n.type === "cornell") {
      // 优先用 rawContent 解析三段
      let cues = "";
      let notes = n.content;
      let summary = "";
      if (n.rawContent) {
        try {
          const parsed = JSON.parse(n.rawContent) as {
            cues?: string;
            notes?: string;
            summary?: string;
          };
          cues = parsed.cues || "";
          notes = parsed.notes || "";
          summary = parsed.summary || "";
        } catch {
          notes = n.rawContent;
        }
      }
      setEditingNote({
        id: n.id,
        date: n.date,
        type: "cornell",
        title: n.title,
        cues,
        notes,
        summary,
      });
    } else {
      setEditingNote({
        id: n.id,
        date: n.date,
        type: n.type,
        title: n.title,
        content: n.content,
      });
    }
    setEditDrawerOpen(true);
  };

  // 保存笔记编辑
  const handleSaveNoteEdit = async () => {
    if (!editingNote) return;
    setSavingEdit(true);
    try {
      let content = "";
      let preview = "";
      if (editingNote.type === "cornell") {
        const obj = {
          cues: editingNote.cues || "",
          notes: editingNote.notes || "",
          summary: editingNote.summary || "",
        };
        content = JSON.stringify(obj);
        preview = [obj.summary, obj.notes, obj.cues].filter(Boolean).join("\n");
      } else {
        content = editingNote.content || "";
        preview = content;
      }
      await logReflectionApi.updateReflection(editingNote.id, { content });
      setNotesHistory((prev) =>
        prev.map((it) =>
          it.id === editingNote.id
            ? { ...it, content: preview, rawContent: content }
            : it,
        ),
      );
      // 同步反思列表（若编辑的是反思项）
      if (editingNote.type === "other") {
        setReflections((prev) =>
          prev.map((it) =>
            it.id === editingNote.id ? { ...it, content: preview } : it,
          ),
        );
      }
      // 若编辑的是当前最新 cornell，同步更新主编辑器
      if (editingNote.type === "cornell") {
        setCornellNotes({
          cues: editingNote.cues || "",
          notes: editingNote.notes || "",
          summary: editingNote.summary || "",
        });
      } else if (editingNote.type === "feynman") {
        setFeynmanInput(editingNote.content || "");
      }
      message.success("已更新");
      setEditDrawerOpen(false);
      setEditingNote(null);
    } catch (_e) {
      message.error("更新失败");
    } finally {
      setSavingEdit(false);
    }
  };

  // 删除笔记
  const handleDeleteNote = async () => {
    if (!editingNote) return;
    setSavingEdit(true);
    try {
      await logReflectionApi.deleteReflection(editingNote.id);
      setNotesHistory((prev) => prev.filter((it) => it.id !== editingNote.id));
      // 同步从反思列表移除（如果在反思列表里）
      setReflections((prev) => prev.filter((it) => it.id !== editingNote.id));
      message.success("已删除");
      setEditDrawerOpen(false);
      setEditingNote(null);
    } catch (_e) {
      message.error("删除失败");
    } finally {
      setSavingEdit(false);
    }
  };

  // 打开反思编辑（复用同一抽屉，type='other'）
  const handleOpenReflectionEdit = (r: ReflectionEntry) => {
    setEditingNote({
      id: r.id,
      date: r.date,
      type: "other",
      title: r.topic || "反思",
      content: r.content,
    });
    setEditDrawerOpen(true);
  };

  const handleFavoriteClick = (item: FavoriteItem) => {
    if (
      item.resource_type === "code" ||
      item.resource_type === "document" ||
      item.resource_type === "doc"
    ) {
      navigate(`/resources?topic=${encodeURIComponent(item.title)}`);
    } else {
      message.info("该资源暂无详情页");
    }
  };

  const statsRecord = (dashboardStats?.stats || {}) as Record<string, unknown>;
  const statCardsData = useMemo(
    () => [
      {
        title: "累计学习时长",
        value: Math.round((Number(statsRecord.total_hours) || 0) * 10) / 10,
        suffix: "h",
        color: "#4f46e5",
        icon: <ClockCircleOutlined />,
      },
      {
        title: "最长连续打卡",
        value: Number(statsRecord.streak_days) || 0,
        suffix: "天",
        color: "#f59e0b",
        icon: <FireOutlined />,
      },
      {
        title: "获得勋章",
        value: achievements.filter((a) => a.unlocked_at).length,
        suffix: "枚",
        color: "#10b981",
        icon: <TrophyOutlined />,
      },
      {
        title: "收藏资源",
        value: favorites.length,
        suffix: "个",
        color: "#ec4899",
        icon: <HeartOutlined />,
      },
    ],
    [dashboardStats, achievements, favorites],
  );

  const badgeList = useMemo(
    () =>
      defaultBadges.map((db) => {
        const unlocked = achievements.find((a) => a.name === db.name);
        return {
          ...db,
          unlocked: !!unlocked,
          unlocked_at: unlocked?.unlocked_at,
        };
      }),
    [achievements],
  );

  const weekFocus = useMemo(() => {
    if (focusData.length) return focusData;
    // 没数据时也铺满 7 天（按今天往前推），全部 0，避免出现假数据
    const labels = ["周日", "周一", "周二", "周三", "周四", "周五", "周六"];
    const out: FocusItem[] = [];
    const t = new Date();
    for (let i = 6; i >= 0; i--) {
      const d = new Date(t);
      d.setDate(t.getDate() - i);
      out.push({ day: labels[d.getDay()], focus: 0, duration: 0 });
    }
    return out;
  }, [focusData]);

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-5">
        {statCardsData.map((stat, idx) => (
          <StatCard
            key={idx}
            icon={stat.icon}
            color={stat.color}
            title={stat.title}
            value={stat.value}
            suffix={stat.suffix}
          />
        ))}
        <StatCard
          icon={<ClockCircleOutlined />}
          color="#ef4444"
          title="今日番茄钟"
          value={pomodoroStats.today}
          suffix="个"
        />
      </div>

      <Tabs
        activeKey={activeTab}
        onChange={(k) => {
          setActiveTab(k);
          if (k === "history") {
            searchParams.delete("tab");
          } else {
            searchParams.set("tab", k);
          }
          setSearchParams(searchParams, { replace: true });
        }}
        className="custom-tabs"
        items={[
          {
            key: "history",
            label: (
              <span className="flex items-center gap-1.5">
                <HistoryOutlined /> 学习历史与分析
              </span>
            ),
            children: (
              <div className="space-y-5">
                <Row gutter={[20, 20]}>
                  <Col xs={24} lg={12}>
                    <div className="bg-white rounded-2xl border border-slate-100 p-6">
                      <div className="flex items-center gap-2 mb-4">
                        <LineChartOutlined className="text-primary" />
                        <span className="font-semibold text-slate-800">
                          专注度趋势
                        </span>
                      </div>
                      <div className="h-60">
                        <ResponsiveContainer width="100%" height="100%">
                          <LineChart data={weekFocus}>
                            <CartesianGrid
                              strokeDasharray="3 3"
                              stroke="#f1f5f9"
                            />
                            <XAxis
                              dataKey="day"
                              tick={{ fill: "#64748b" }}
                              axisLine={false}
                              tickLine={false}
                            />
                            <YAxis
                              domain={[0, 100]}
                              tick={{ fill: "#64748b" }}
                              axisLine={false}
                              tickLine={false}
                            />
                            <Tooltip
                              contentStyle={{
                                borderRadius: 12,
                                border: "none",
                                boxShadow: "0 4px 12px rgba(0,0,0,0.06)",
                              }}
                              cursor={{ stroke: "#e2e8f0", strokeWidth: 2 }}
                            />
                            <Line
                              type="monotone"
                              dataKey="focus"
                              stroke="#4f46e5"
                              strokeWidth={3}
                              dot={{ fill: "#4f46e5", r: 4 }}
                              activeDot={{
                                r: 6,
                                fill: "#fff",
                                stroke: "#4f46e5",
                                strokeWidth: 2,
                              }}
                            />
                          </LineChart>
                        </ResponsiveContainer>
                      </div>
                    </div>
                  </Col>
                  <Col xs={24} lg={12}>
                    <div className="bg-white rounded-2xl border border-slate-100 p-6">
                      <div className="flex items-center gap-2 mb-4">
                        <BarChartOutlined className="text-secondary" />
                        <span className="font-semibold text-slate-800">
                          每日学习时长
                        </span>
                      </div>
                      <div className="h-60">
                        <ResponsiveContainer width="100%" height="100%">
                          <BarChart data={weekFocus}>
                            <CartesianGrid
                              strokeDasharray="3 3"
                              stroke="#f1f5f9"
                              vertical={false}
                            />
                            <XAxis
                              dataKey="day"
                              tick={{ fill: "#64748b" }}
                              axisLine={false}
                              tickLine={false}
                            />
                            <YAxis
                              tick={{ fill: "#64748b" }}
                              axisLine={false}
                              tickLine={false}
                            />
                            <Tooltip
                              contentStyle={{
                                borderRadius: 12,
                                border: "none",
                                boxShadow: "0 4px 12px rgba(0,0,0,0.06)",
                              }}
                              cursor={{ fill: "#f8fafc" }}
                            />
                            <Bar
                              dataKey="duration"
                              fill="url(#colorDuration)"
                              radius={[8, 8, 0, 0]}
                            />
                            <defs>
                              <linearGradient
                                id="colorDuration"
                                x1="0"
                                y1="0"
                                x2="0"
                                y2="1"
                              >
                                <stop
                                  offset="5%"
                                  stopColor="#4f46e5"
                                  stopOpacity={0.9}
                                />
                                <stop
                                  offset="95%"
                                  stopColor="#0ea5e9"
                                  stopOpacity={0.7}
                                />
                              </linearGradient>
                            </defs>
                          </BarChart>
                        </ResponsiveContainer>
                      </div>
                    </div>
                  </Col>
                </Row>

                <div className="bg-white rounded-2xl border border-slate-100 p-6">
                  <div className="font-semibold text-slate-800 mb-4">
                    最近学习记录
                  </div>
                  <List
                    itemLayout="horizontal"
                    dataSource={
                      learningHistory.length
                        ? learningHistory
                        : [{ title: "暂无学习记录", time: "-", type: "doc" }]
                    }
                    renderItem={(item: HistoryItem) => {
                      const meta = typeMeta[item.type] || typeMeta.doc;
                      return (
                        <List.Item className="hover:bg-slate-50 rounded-xl transition-colors px-2">
                          <List.Item.Meta
                            avatar={
                              <Avatar
                                icon={meta.icon}
                                style={{
                                  background: meta.bg,
                                  color: meta.color,
                                  border: `1px solid ${meta.color}15`,
                                }}
                              />
                            }
                            title={
                              <Typography.Text className="text-slate-700 font-medium text-sm">
                                {item.title}
                              </Typography.Text>
                            }
                            description={
                              <Space>
                                <Tag className="rounded-full text-xs border-0 bg-slate-100 text-slate-500">
                                  {meta.label}
                                </Tag>
                                <span className="text-slate-400 text-xs">
                                  {item.time}
                                </span>
                              </Space>
                            }
                          />
                        </List.Item>
                      );
                    }}
                  />
                </div>

                {/* 笔记记录 */}
                <div className="mt-6 bg-white rounded-2xl border border-slate-100 p-6">
                  <div className="font-semibold text-slate-800 mb-4">
                    笔记记录
                  </div>
                  <List
                    itemLayout="horizontal"
                    dataSource={
                      notesHistory.length
                        ? notesHistory.filter((n) =>
                            ["notes", "cornell", "cues"].includes(n.type),
                          )
                        : [
                            {
                              id: "empty",
                              date: "",
                              type: "notes" as const,
                              title: "暂无笔记记录",
                              content: "在学习中心记录笔记后，这里会自动同步",
                            },
                          ]
                    }
                    renderItem={(n) => {
                      const typeMeta: Record<
                        string,
                        { label: string; color: string; bg: string }
                      > = {
                        cornell: {
                          label: "康奈尔笔记",
                          color: "#0ea5e9",
                          bg: "#e0f2fe",
                        },
                        cues: {
                          label: "线索栏",
                          color: "#10b981",
                          bg: "#d1fae5",
                        },
                        notes: {
                          label: "普通笔记",
                          color: "#f59e0b",
                          bg: "#fef3c7",
                        },
                      };
                      const meta = typeMeta[n.type] || typeMeta.notes;
                      return (
                        <List.Item className="hover:bg-slate-50 rounded-xl transition-colors px-2">
                          <List.Item.Meta
                            title={
                              <Typography.Text className="text-slate-700 font-medium text-sm">
                                {n.title}
                              </Typography.Text>
                            }
                            description={
                              <div className="space-y-1">
                                <div className="text-xs text-slate-500 line-clamp-2">
                                  {n.content}
                                </div>
                                <Space>
                                  <Tag
                                    className="rounded-full text-xs border-0"
                                    style={{
                                      color: meta.color,
                                      background: meta.bg,
                                    }}
                                  >
                                    {meta.label}
                                  </Tag>
                                  {n.date && (
                                    <span className="text-slate-400 text-xs">
                                      {n.date}
                                    </span>
                                  )}
                                </Space>
                              </div>
                            }
                          />
                        </List.Item>
                      );
                    }}
                  />
                </div>
              </div>
            ),
          },
          {
            key: "growth",
            label: (
              <span className="flex items-center gap-1.5">
                <RiseOutlined /> 成长旅程
              </span>
            ),
            children: (
              <div className="bg-white rounded-2xl border border-slate-100 p-6">
                <GrowthTimeline />
              </div>
            ),
          },
          {
            key: "notes",
            label: (
              <span className="flex items-center gap-1.5">
                <EditOutlined /> 笔记与反思
              </span>
            ),
            children: (
              <div className="space-y-5">
                {/* 康奈尔笔记 */}
                <div className="bg-white rounded-2xl border border-slate-100 p-6">
                  <div className="font-semibold text-slate-800 mb-4">
                    康奈尔笔记法
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="md:col-span-1 space-y-2">
                      <div className="text-xs font-medium text-slate-500">
                        线索栏 (Cues)
                      </div>
                      <Input.TextArea
                        rows={10}
                        placeholder="记录关键词、问题..."
                        value={cornellNotes.cues}
                        onChange={(e) =>
                          setCornellNotes({
                            ...cornellNotes,
                            cues: e.target.value,
                          })
                        }
                        className="rounded-xl bg-slate-50 border-slate-200"
                      />
                    </div>
                    <div className="md:col-span-2 space-y-2">
                      <div className="text-xs font-medium text-slate-500">
                        笔记栏 (Notes)
                      </div>
                      <Input.TextArea
                        rows={10}
                        placeholder="记录课堂/阅读笔记..."
                        value={cornellNotes.notes}
                        onChange={(e) =>
                          setCornellNotes({
                            ...cornellNotes,
                            notes: e.target.value,
                          })
                        }
                        className="rounded-xl bg-slate-50 border-slate-200"
                      />
                    </div>
                  </div>
                  <div className="mt-4 space-y-2">
                    <div className="text-xs font-medium text-slate-500">
                      总结栏 (Summary)
                    </div>
                    <Input.TextArea
                      rows={3}
                      placeholder="用一句话总结本页核心内容..."
                      value={cornellNotes.summary}
                      onChange={(e) =>
                        setCornellNotes({
                          ...cornellNotes,
                          summary: e.target.value,
                        })
                      }
                      className="rounded-xl bg-slate-50 border-slate-200"
                    />
                  </div>
                  <Button
                    type="primary"
                    className="rounded-lg bg-primary mt-4"
                    onClick={handleSaveCornell}
                  >
                    <CheckCircleOutlined /> 保存康奈尔笔记
                  </Button>
                </div>

                {/* 费曼练习 */}
                <div className="bg-white rounded-2xl border border-slate-100 p-6">
                  <div className="font-semibold text-slate-800 mb-4">
                    费曼学习法
                  </div>
                  <div className="p-4 rounded-xl bg-amber-50 border border-amber-100 text-sm text-amber-800 mb-4">
                    <strong>费曼技巧：</strong>
                    选择你要学习的概念，尝试用最简单的语言向一个"小孩"解释它。如果你卡住了，就回到材料中重新学习，然后再次尝试简化。
                  </div>
                  <Input.TextArea
                    rows={6}
                    placeholder="用你自己的话，尝试向一个外行解释最近学到的知识点..."
                    value={feynmanInput}
                    onChange={(e) => setFeynmanInput(e.target.value)}
                    className="rounded-xl bg-slate-50 border-slate-200 mb-3"
                  />
                  <Button
                    type="primary"
                    className="rounded-lg bg-primary"
                    onClick={handleSaveFeynman}
                  >
                    <ThunderboltOutlined /> 提交费曼练习
                  </Button>
                </div>

                {/* 自由反思 */}
                <div className="bg-white rounded-2xl border border-slate-100 p-6">
                  <div className="font-semibold text-slate-800 mb-4">
                    写今日反思
                  </div>
                  <Input.TextArea
                    rows={4}
                    placeholder="今天学到了什么？有哪些地方还需要提高？记录下来，帮助你加深记忆..."
                    value={newReflection}
                    onChange={(e) => setNewReflection(e.target.value)}
                    className="rounded-xl bg-slate-50 border-slate-200 mb-3"
                  />
                  <Button
                    type="primary"
                    className="rounded-lg bg-primary"
                    onClick={handleAddReflection}
                  >
                    保存反思
                  </Button>
                </div>

                {/* 笔记时间线 */}
                <div className="bg-white rounded-2xl border border-slate-100 p-2">
                  <Collapse
                    ghost
                    expandIcon={({ isActive }) => (
                      <CaretRightOutlined rotate={isActive ? 90 : 0} />
                    )}
                    items={[
                      {
                        key: "notes-timeline",
                        label: (
                          <div className="flex items-center justify-between w-full pr-4">
                            <span className="font-semibold text-slate-800">
                              <FileTextOutlined className="mr-2 text-primary" />
                              我的笔记时间线
                            </span>
                            <Tag className="rounded-full border-0 bg-primary-50 text-primary text-xs">
                              {notesHistory.length} 条
                            </Tag>
                          </div>
                        ),
                        children: (
                          <div className="space-y-3 max-h-[480px] overflow-y-auto px-2 pb-2">
                            {notesHistory.length ? (
                              notesHistory.map((n) => (
                                <div
                                  key={n.id}
                                  className="p-4 rounded-xl bg-slate-50 border border-slate-100 hover:border-primary/30 hover:bg-white hover:shadow-card transition-all cursor-pointer"
                                  onClick={() => handleOpenNoteEdit(n)}
                                >
                                  <div className="flex items-center justify-between mb-2">
                                    <div className="flex items-center gap-2">
                                      <Tag
                                        className={`rounded-full border-0 text-xs ${
                                          n.type === "cornell"
                                            ? "bg-sky-50 text-sky-600"
                                            : n.type === "feynman"
                                              ? "bg-amber-50 text-amber-600"
                                              : "bg-primary-50 text-primary"
                                        }`}
                                      >
                                        {n.type === "cornell"
                                          ? "康奈尔笔记"
                                          : n.type === "feynman"
                                            ? "费曼练习"
                                            : "反思"}
                                      </Tag>
                                      <span className="text-xs text-slate-400">
                                        {n.date}
                                      </span>
                                    </div>
                                    <span className="text-xs text-primary opacity-70">
                                      点击编辑
                                    </span>
                                  </div>
                                  <Typography.Text className="text-slate-700 text-sm leading-relaxed block">
                                    {n.content?.slice(0, 100)}
                                    {(n.content?.length || 0) > 100
                                      ? "..."
                                      : ""}
                                  </Typography.Text>
                                </div>
                              ))
                            ) : (
                              <div className="text-slate-400 text-sm text-center py-4">
                                暂无笔记记录
                              </div>
                            )}
                          </div>
                        ),
                      },
                    ]}
                  />
                </div>
              </div>
            ),
          },
          {
            key: "profile",
            label: (
              <span className="flex items-center gap-1.5">
                <EditOutlined /> 画像详情与管理
              </span>
            ),
            children: (
              <div className="space-y-5">
                {/* 画像摘要雷达图 */}
                <div className="bg-white rounded-2xl border border-slate-100 p-6">
                  <div className="flex items-center justify-between mb-4">
                    <Typography.Title
                      level={5}
                      className="!m-0 font-semibold text-slate-800"
                    >
                      六维画像雷达
                    </Typography.Title>
                  </div>
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <RadarChart
                        cx="50%"
                        cy="50%"
                        outerRadius="70%"
                        data={profileData}
                      >
                        <PolarGrid stroke="#e2e8f0" />
                        <PolarAngleAxis
                          dataKey="subject"
                          tick={{ fill: "#64748b", fontSize: 12 }}
                        />
                        <PolarRadiusAxis
                          angle={30}
                          domain={[0, 100]}
                          tick={false}
                          axisLine={false}
                        />
                        <Radar
                          name="当前画像"
                          dataKey="A"
                          stroke="#4f46e5"
                          fill="#4f46e5"
                          fillOpacity={0.15}
                          strokeWidth={2}
                        />
                      </RadarChart>
                    </ResponsiveContainer>
                  </div>
                  <div className="flex flex-wrap gap-2 justify-center mt-3">
                    {profileData.map((item) => (
                      <Tag
                        key={item.subject}
                        className="rounded-full border-0 bg-slate-100 text-slate-600 text-xs"
                      >
                        {item.subject}: {Math.round(item.A)}
                      </Tag>
                    ))}
                  </div>
                </div>

                {/* 维度详情 */}
                <div className="bg-white rounded-2xl border border-slate-100 p-6">
                  <Typography.Title
                    level={5}
                    className="!m-0 mb-4 font-semibold text-slate-800"
                  >
                    维度详情
                  </Typography.Title>
                  <div className="space-y-2.5">
                    {dimensions.length === 0 ? (
                      <div className="text-xs text-slate-400 py-3 text-center">
                        尚未生成画像，可在智能辅导对话中自动构建
                      </div>
                    ) : (
                      dimensions.map((dim) => (
                        <div key={dim.label}>
                          <div className="flex justify-between mb-1">
                            <Typography.Text className="text-sm text-slate-600 font-medium">
                              {dim.label}
                            </Typography.Text>
                            <Typography.Text
                              className="text-sm font-bold"
                              style={{ color: dim.color }}
                            >
                              {dim.value}
                            </Typography.Text>
                          </div>
                          <Progress
                            percent={dim.value}
                            showInfo={false}
                            strokeColor={dim.color}
                            trailColor="#f1f5f9"
                            size="small"
                          />
                        </div>
                      ))
                    )}
                  </div>
                </div>

                {/* 画像数据解读 */}
                <div className="bg-white rounded-2xl border border-slate-100 p-6">
                  <Typography.Title
                    level={5}
                    className="mb-5 font-semibold text-slate-800"
                  >
                    画像数据解读
                  </Typography.Title>
                  <div className="space-y-4 text-slate-600 leading-relaxed">
                    {/* 趋势状态卡片 */}
                    {trendInfo && (
                      <div
                        className={`p-4 rounded-xl border flex items-start gap-3 ${
                          trendInfo.state === "growth"
                            ? "bg-emerald-50 border-emerald-100 text-emerald-700"
                            : trendInfo.state === "warning"
                              ? "bg-red-50 border-red-100 text-red-700"
                              : trendInfo.state === "decline"
                                ? "bg-amber-50 border-amber-100 text-amber-700"
                                : "bg-slate-50 border-slate-100 text-slate-600"
                        }`}
                      >
                        {trendInfo.state === "growth" ? (
                          <RiseOutlined className="text-xl mt-1" />
                        ) : trendInfo.state === "warning" ? (
                          <AlertOutlined className="text-xl mt-1" />
                        ) : trendInfo.state === "decline" ? (
                          <FallOutlined className="text-xl mt-1" />
                        ) : (
                          <BulbOutlined className="text-xl mt-1" />
                        )}
                        <div className="flex-1">
                          <div className="font-semibold mb-1">
                            趋势状态：
                            {trendInfo.state === "growth"
                              ? "上升期"
                              : trendInfo.state === "warning"
                                ? "预警"
                                : trendInfo.state === "decline"
                                  ? "下滑期"
                                  : "平稳期"}
                            <span className="ml-2 text-xs opacity-70">
                              趋势因子 {trendInfo.factor.toFixed(2)}
                            </span>
                          </div>
                          <div className="text-sm leading-relaxed">
                            {trendInfo.intervention || "暂无干预建议"}
                          </div>
                        </div>
                      </div>
                    )}

                    <div className="p-5 rounded-xl bg-slate-50 border border-slate-100">
                      <p className="mb-2">
                        <strong className="text-slate-800">认知风格：</strong>{" "}
                        你的主要认知风格为{" "}
                        <Tag className="rounded-full border-0 bg-blue-50 text-blue-600">
                          {cognitivePrimary}
                        </Tag>
                        ，系统会优先推送
                        {cognitivePrimary === "visual"
                          ? "图表与动画类资源（内存模型图、指针示意图）"
                          : cognitivePrimary === "auditory"
                            ? "讲解视频与对话式讲义"
                            : cognitivePrimary === "kinesthetic"
                              ? "代码实战与可交互练习"
                              : "多模态混合资源"}
                        。
                      </p>
                      <p className="mb-2">
                        <strong className="text-slate-800">学习节奏：</strong>{" "}
                        当前学习节奏评估为{" "}
                        <Tag className="rounded-full border-0 bg-blue-50 text-blue-600">
                          {studySpeed}
                        </Tag>
                        {trendInfo?.dimensions?.speed_ratio !== undefined && (
                          <span className="text-xs text-slate-500 ml-1">
                            （速度比{" "}
                            {trendInfo.dimensions.speed_ratio.toFixed(2)}
                            {trendInfo.dimensions.speed_ratio > 0.2
                              ? " · 偏快"
                              : trendInfo.dimensions.speed_ratio < -0.2
                                ? " · 偏慢"
                                : " · 适中"}
                            ）
                          </span>
                        )}
                        ，系统在推荐内容时会自动调整讲解深度与练习量。
                      </p>
                      <p className="mb-2">
                        <strong className="text-slate-800">薄弱点：</strong>{" "}
                        {weakAreas.length
                          ? weakAreas.join("、")
                          : "暂无明显薄弱点"}
                        {trendInfo?.dimensions?.weakness_priority !==
                          undefined && (
                          <span className="text-xs text-slate-500 ml-1">
                            （优先级得分{" "}
                            {trendInfo.dimensions.weakness_priority.toFixed(2)}
                            {trendInfo.dimensions.weakness_priority < -0.2
                              ? " · 需重点关注"
                              : ""}
                            ）
                          </span>
                        )}
                        {weakAreas.length
                          ? "，系统已自动增加相关练习推送和可视化讲解。"
                          : "。"}
                      </p>
                      {trendInfo?.dimensions?.completion_rate !== undefined && (
                        <p className="mb-2">
                          <strong className="text-slate-800">完成率：</strong>{" "}
                          <Tag className="rounded-full border-0 bg-amber-50 text-amber-600">
                            {trendInfo.dimensions.completion_rate >= 0.4
                              ? "高"
                              : trendInfo.dimensions.completion_rate >= -0.2
                                ? "中"
                                : "偏低"}
                          </Tag>
                          （得分{" "}
                          {trendInfo.dimensions.completion_rate.toFixed(2)}）
                          {trendInfo.dimensions.completion_rate < -0.2
                            ? "，建议浏览过的章节尽量点击「标记完成」并配合练习。"
                            : trendInfo.dimensions.completion_rate >= 0.4
                              ? "，保持当前节奏，可挑战更高难度的综合题。"
                              : "，可以结合练习巩固已学内容。"}
                        </p>
                      )}
                      {trendInfo?.dimensions?.stability !== undefined && (
                        <p className="mb-2">
                          <strong className="text-slate-800">
                            学习稳定性：
                          </strong>{" "}
                          <Tag className="rounded-full border-0 bg-slate-100 text-slate-600">
                            {trendInfo.dimensions.stability >= 0.2
                              ? "稳定"
                              : trendInfo.dimensions.stability >= -0.2
                                ? "一般"
                                : "波动较大"}
                          </Tag>
                          （得分 {trendInfo.dimensions.stability.toFixed(2)}）
                        </p>
                      )}
                      <p>
                        <strong className="text-slate-800">兴趣方向：</strong>{" "}
                        {profile?.interest_areas?.length
                          ? profile.interest_areas
                              .map((a) =>
                                typeof a === "string"
                                  ? a
                                  : a.area || JSON.stringify(a),
                              )
                              .join("、")
                          : "C语言程序设计与系统开发"}
                        。
                      </p>
                    </div>
                  </div>
                </div>

                {/* 遗忘曲线 · 知识点衰减 */}
                <div className="bg-white rounded-2xl border border-slate-100 p-6">
                  <div className="flex items-center justify-between mb-4">
                    <Typography.Title
                      level={5}
                      className="!m-0 font-semibold text-slate-800"
                    >
                      遗忘曲线 · 知识点衰减
                    </Typography.Title>
                    <Tag className="rounded-full border-0 bg-slate-100 text-slate-600 text-xs">
                      艾宾浩斯
                    </Tag>
                  </div>
                  <Row gutter={20}>
                    <Col xs={24} lg={12}>
                      <div className="h-56">
                        <ResponsiveContainer width="100%" height="100%">
                          <LineChart
                            data={[
                              {
                                day: "第1天",
                                theoretical: 100,
                                actual: retentionItems[0]?.retention,
                              },
                              {
                                day: "第2天",
                                theoretical: 55,
                                actual: retentionItems[1]?.retention,
                              },
                              {
                                day: "第3天",
                                theoretical: 42,
                                actual: retentionItems[2]?.retention,
                              },
                              {
                                day: "第5天",
                                theoretical: 35,
                                actual: retentionItems[3]?.retention,
                              },
                              { day: "第8天", theoretical: 30 },
                              { day: "第15天", theoretical: 25 },
                              { day: "第30天", theoretical: 20 },
                            ]}
                          >
                            <CartesianGrid
                              strokeDasharray="3 3"
                              stroke="#f1f5f9"
                            />
                            <XAxis
                              dataKey="day"
                              tick={{ fill: "#64748b", fontSize: 11 }}
                              axisLine={false}
                              tickLine={false}
                            />
                            <YAxis
                              domain={[0, 100]}
                              tick={{ fill: "#64748b" }}
                              axisLine={false}
                              tickLine={false}
                            />
                            <Tooltip
                              contentStyle={{
                                borderRadius: 12,
                                border: "none",
                                boxShadow: "0 4px 12px rgba(0,0,0,0.06)",
                              }}
                            />
                            <Line
                              type="monotone"
                              dataKey="theoretical"
                              name="理论记忆保留率"
                              stroke="#ef4444"
                              strokeWidth={2}
                              dot={{ r: 3 }}
                              strokeDasharray="5 5"
                            />
                            {retentionItems.length > 0 && (
                              <Line
                                type="monotone"
                                dataKey="actual"
                                name="你的薄弱点保留率"
                                stroke="#4f46e5"
                                strokeWidth={2}
                                dot={{ r: 4, fill: "#4f46e5" }}
                                connectNulls={false}
                              />
                            )}
                          </LineChart>
                        </ResponsiveContainer>
                      </div>
                    </Col>
                    <Col xs={24} lg={12}>
                      <div className="space-y-3">
                        {retentionItems.length === 0 ? (
                          <div className="text-sm text-slate-400 text-center py-10">
                            画像中尚无薄弱点，继续学习几个知识点后这里会自动生成复习计划
                          </div>
                        ) : (
                          retentionItems.map((item) => (
                            <div
                              key={item.topic}
                              className="flex items-center gap-3 p-3 rounded-xl bg-slate-50 border border-slate-100"
                            >
                              <div className="flex-1">
                                <div className="text-sm font-medium text-slate-800">
                                  {item.topic}
                                </div>
                                <div className="text-xs text-slate-400">
                                  下次复习: {item.nextReview}
                                </div>
                              </div>
                              <div className="w-24">
                                <Progress
                                  percent={item.retention}
                                  size="small"
                                  strokeColor={
                                    item.retention > 70
                                      ? "#10b981"
                                      : item.retention > 50
                                        ? "#f59e0b"
                                        : "#ef4444"
                                  }
                                  trailColor="#f1f5f9"
                                  showInfo={false}
                                />
                              </div>
                              <Tag
                                className={`rounded-full border-0 text-xs ${item.retention > 70 ? "bg-emerald-50 text-emerald-600" : item.retention > 50 ? "bg-amber-50 text-amber-600" : "bg-red-50 text-red-600"}`}
                              >
                                {item.retention}%
                              </Tag>
                            </div>
                          ))
                        )}
                      </div>
                    </Col>
                  </Row>
                </div>

                {/* 画像历史变化 */}
                <div className="bg-white rounded-2xl border border-slate-100 p-6">
                  <div className="flex items-center justify-between mb-4">
                    <Typography.Title
                      level={5}
                      className="!m-0 font-semibold text-slate-800"
                    >
                      画像历史变化
                    </Typography.Title>
                    <Tag className="rounded-full border-0 bg-slate-100 text-slate-600 text-xs">
                      近7天
                    </Tag>
                  </div>
                  <div className="h-56">
                    {historyData.length === 0 ? (
                      <div className="h-full flex items-center justify-center text-slate-400 text-sm">
                        暂无趋势数据，完成几道练习后再来看
                      </div>
                    ) : (
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={historyData}>
                          <CartesianGrid
                            strokeDasharray="3 3"
                            stroke="#f1f5f9"
                          />
                          <XAxis
                            dataKey="date"
                            tick={{ fill: "#64748b" }}
                            axisLine={false}
                            tickLine={false}
                          />
                          <YAxis
                            domain={[0, 100]}
                            tick={{ fill: "#64748b" }}
                            axisLine={false}
                            tickLine={false}
                          />
                          <Tooltip
                            contentStyle={{
                              borderRadius: 12,
                              border: "none",
                              boxShadow: "0 4px 12px rgba(0,0,0,0.06)",
                            }}
                            cursor={{ stroke: "#e2e8f0", strokeWidth: 2 }}
                          />
                          <Line
                            type="monotone"
                            dataKey="value"
                            stroke="#4f46e5"
                            strokeWidth={3}
                            dot={{ fill: "#4f46e5", strokeWidth: 2, r: 4 }}
                            activeDot={{
                              r: 6,
                              fill: "#fff",
                              stroke: "#4f46e5",
                              strokeWidth: 2,
                            }}
                          />
                        </LineChart>
                      </ResponsiveContainer>
                    )}
                  </div>
                </div>

                {/* 排行榜 */}
                <div className="bg-white rounded-2xl border border-slate-100 p-6">
                  <div className="font-semibold text-slate-800 mb-4">
                    <TrophyOutlined className="mr-2 text-amber-500" />
                    排行榜
                  </div>
                  <Leaderboard />
                </div>

                {/* 成就徽章 */}
                <div className="bg-white rounded-2xl border border-slate-100 p-6">
                  <div className="flex items-center justify-between mb-6">
                    <div className="font-semibold text-slate-800">我的成就</div>
                    <Tag className="rounded-full border-0 bg-slate-100 text-slate-600 text-xs">
                      已解锁 {badgeList.filter((b) => b.unlocked).length} /{" "}
                      {badgeList.length}
                    </Tag>
                  </div>
                  <Row gutter={[20, 20]}>
                    {badgeList.map((badge: BadgeItemLocal) => (
                      <Col xs={12} sm={8} lg={6} key={badge.id}>
                        <div
                          className={`flex flex-col items-center gap-3 p-5 rounded-xl border transition-all ${
                            badge.unlocked
                              ? "bg-white border-slate-100 hover:shadow-card"
                              : "bg-slate-50 border-slate-100 opacity-50"
                          }`}
                        >
                          <div
                            className="w-14 h-14 rounded-full flex items-center justify-center text-white text-xl"
                            style={{
                              background: badge.unlocked
                                ? badge.color
                                : "#cbd5e1",
                            }}
                          >
                            {badge.icon}
                          </div>
                          <div className="text-center">
                            <div className="font-semibold text-slate-800 text-sm">
                              {badge.name}
                            </div>
                            <div className="text-xs text-slate-400 mt-1">
                              {badge.desc}
                            </div>
                          </div>
                          {badge.unlocked && (
                            <Tag className="rounded-full border-0 bg-emerald-50 text-emerald-600 text-xs">
                              已解锁
                            </Tag>
                          )}
                        </div>
                      </Col>
                    ))}
                  </Row>
                </div>
              </div>
            ),
          },
          {
            key: "pomodoro",
            label: (
              <span className="flex items-center gap-1.5">
                <ClockCircleOutlined /> 番茄专注钟
              </span>
            ),
            children: <PomodoroTimer />,
          },
        ]}
      />

      {/* 笔记编辑抽屉 */}
      <Drawer
        title={editingNote ? `编辑${editingNote.title}` : "编辑笔记"}
        placement="right"
        width={520}
        open={editDrawerOpen}
        onClose={() => {
          setEditDrawerOpen(false);
          setEditingNote(null);
        }}
        extra={
          editingNote && (
            <Popconfirm
              title="确定删除这条笔记吗？"
              description="删除后无法恢复"
              okText="删除"
              cancelText="取消"
              okButtonProps={{ danger: true }}
              onConfirm={handleDeleteNote}
            >
              <Button danger icon={<DeleteOutlined />} loading={savingEdit}>
                删除
              </Button>
            </Popconfirm>
          )
        }
        footer={
          <div className="flex justify-end gap-2">
            <Button
              onClick={() => {
                setEditDrawerOpen(false);
                setEditingNote(null);
              }}
            >
              取消
            </Button>
            <Button
              type="primary"
              loading={savingEdit}
              onClick={handleSaveNoteEdit}
              className="bg-primary"
            >
              保存修改
            </Button>
          </div>
        }
      >
        {editingNote && (
          <div className="space-y-4">
            <div className="text-xs text-slate-400">
              日期：{editingNote.date}
            </div>
            {editingNote.type === "cornell" ? (
              <>
                <div className="space-y-2">
                  <div className="text-xs font-medium text-slate-500">
                    线索栏 (Cues)
                  </div>
                  <Input.TextArea
                    rows={4}
                    value={editingNote.cues || ""}
                    onChange={(e) =>
                      setEditingNote({ ...editingNote, cues: e.target.value })
                    }
                    placeholder="关键词、问题..."
                    className="rounded-xl bg-slate-50 border-slate-200"
                  />
                </div>
                <div className="space-y-2">
                  <div className="text-xs font-medium text-slate-500">
                    笔记栏 (Notes)
                  </div>
                  <Input.TextArea
                    rows={10}
                    value={editingNote.notes || ""}
                    onChange={(e) =>
                      setEditingNote({ ...editingNote, notes: e.target.value })
                    }
                    placeholder="课堂/阅读笔记..."
                    className="rounded-xl bg-slate-50 border-slate-200"
                  />
                </div>
                <div className="space-y-2">
                  <div className="text-xs font-medium text-slate-500">
                    总结栏 (Summary)
                  </div>
                  <Input.TextArea
                    rows={3}
                    value={editingNote.summary || ""}
                    onChange={(e) =>
                      setEditingNote({
                        ...editingNote,
                        summary: e.target.value,
                      })
                    }
                    placeholder="一句话总结..."
                    className="rounded-xl bg-slate-50 border-slate-200"
                  />
                </div>
              </>
            ) : (
              <div className="space-y-2">
                <div className="text-xs font-medium text-slate-500">
                  {editingNote.type === "feynman" ? "费曼练习内容" : "笔记内容"}
                </div>
                <Input.TextArea
                  rows={14}
                  value={editingNote.content || ""}
                  onChange={(e) =>
                    setEditingNote({ ...editingNote, content: e.target.value })
                  }
                  className="rounded-xl bg-slate-50 border-slate-200"
                />
              </div>
            )}
          </div>
        )}
      </Drawer>
    </div>
  );
};

export default PersonalSpace;
