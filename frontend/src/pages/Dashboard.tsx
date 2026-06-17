import React, { useEffect, useState, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import dayjs from "dayjs";
import {
  Typography,
  Row,
  Col,
  Button,
  Tag,
  Avatar,
  List,
  Space,
  Progress,
  message,
  Spin,
  Tooltip,
  Modal,
  Calendar,
} from "antd";
import { ResponsiveContainer, AreaChart, Area } from "recharts";
import {
  PlayCircleOutlined,
  FileTextOutlined,
  CodeOutlined,
  MessageOutlined,
  RocketOutlined,
  BookOutlined,
  ClockCircleOutlined,
  FireOutlined,
  TrophyOutlined,
  ArrowRightOutlined,
  ApartmentOutlined,
  StarOutlined,
  NodeIndexOutlined,
  CheckCircleFilled,
  FlagFilled,
  CheckCircleOutlined,
  MoreOutlined,
  CalendarOutlined,
  DownOutlined,
} from "@ant-design/icons";
import { useAppStore } from "../store";
import {
  profileApi,
  dashboardApi,
  pathApi,
  gamificationApi,
  knowledgeApi,
  dailyQuizApi,
} from "../services/api";
import { buildRadarData } from "../utils/profile";
import { calcLevel, fetchLevelConfig } from "../utils/level";
// import { StatCard } from "../components/StatCard";
import { SectionCard } from "../components/SectionCard";
// import { StatRow } from "../components/StatRow";
import { statusColors } from "../components/StatusTag";
import type {
  DashboardTask,
  DashboardRecommendation,
  DashboardStats,
  AlgorithmAnalysis,
  PathNode,
  Achievement,
} from "../types";

const RESOURCE_META: Record<
  string,
  { icon: React.ReactNode; color: string; bg: string }
> = {
  doc: { icon: <FileTextOutlined />, color: "#10b981", bg: "#ecfdf5" },
  文档: { icon: <FileTextOutlined />, color: "#10b981", bg: "#ecfdf5" },
  video: { icon: <PlayCircleOutlined />, color: "#ef4444", bg: "#fef2f2" },
  视频: { icon: <PlayCircleOutlined />, color: "#ef4444", bg: "#fef2f2" },
  code: { icon: <CodeOutlined />, color: "#3b82f6", bg: "#eff6ff" },
  代码: { icon: <CodeOutlined />, color: "#3b82f6", bg: "#eff6ff" },
  quiz: { icon: <BookOutlined />, color: "#f59e0b", bg: "#fffbeb" },
  练习: { icon: <BookOutlined />, color: "#f59e0b", bg: "#fffbeb" },
  题目: { icon: <BookOutlined />, color: "#f59e0b", bg: "#fffbeb" },
  tool: { icon: <ApartmentOutlined />, color: "#3b82f6", bg: "#eff6ff" },
  工具: { icon: <ApartmentOutlined />, color: "#3b82f6", bg: "#eff6ff" },
  tutor: { icon: <MessageOutlined />, color: "#0052ff", bg: "#f3f0ff" },
  推荐: { icon: <RocketOutlined />, color: "#f59e0b", bg: "#fffbeb" },
  文章: { icon: <FileTextOutlined />, color: "#10b981", bg: "#ecfdf5" },
};

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [summaryLoading, setSummaryLoading] = useState(false);
  const [tasks, setTasks] = useState<DashboardTask[]>([]);
  const [recommendations, setRecommendations] = useState<
    DashboardRecommendation[]
  >([]);
  const [stats, setStats] = useState<DashboardStats>({
    weekly_hours: 0,
    streak_days: 0,
    achievements: 0,
    favorites: 0,
    mastered_kps: 0,
    today_duration_min: 0,
  });
  const [pathNodesState, setPathNodesState] = useState<PathNode[]>([]);
  const [kgModalOpen, setKgModalOpen] = useState(false);
  const [pointsInfo, setPointsInfo] = useState<{
    total: number;
    level: number;
    current: number;
    need: number;
    percent: number;
  } | null>(null);
  const [kgNodes, setKgNodes] = useState<
    { id: string; name: string; prerequisites: string[] }[]
  >([]);

  // 每日练习
  const [dailyQuiz, setDailyQuiz] = useState<{
    date: string;
    total_questions: number;
    questions: Array<{
      q_id: string;
      type: string;
      content: string;
      difficulty: number;
      source: string;
      hint: string;
      tags: string[];
      options?: Array<{ id: string; text: string }>;
      correct_answer?: string;
    }>;
    difficulty_level: string;
    difficulty: number;
    weak_areas: string[];
  } | null>(null);
  const [quizLoading, _setQuizLoading] = useState(false);
  const [currentQuizIdx, setCurrentQuizIdx] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);
  const [showAnswer, setShowAnswer] = useState(false);

  const [activeDates, setActiveDates] = useState<Set<string>>(new Set());
  const [calendarDate, setCalendarDate] = useState(dayjs());
  const [loadErrors, setLoadErrors] = useState<Record<string, boolean>>({});

  const studentId = useAppStore((s) => s.studentId);
  const currentSubject = useAppStore((s) => s.currentSubject);
  const userInfo = useAppStore((s) => s.userInfo);
  const displayName = userInfo?.username || "学习者";

  // Data fetching
  useEffect(() => {
    let timeoutId: ReturnType<typeof setTimeout>;
    const fetchData = async () => {
      setIsLoading(true);
      setSummaryLoading(true);
      timeoutId = setTimeout(() => {
        setIsLoading(false);
        setSummaryLoading(false);
        message.warning("数据加载超时，请刷新重试");
      }, 10000);
      try {
        // 关键数据优先加载
        const [summaryRes, pointsRes, kgRes, pathRes] = await Promise.all([
          dashboardApi.getSummary(studentId).catch(() => null),
          gamificationApi.getPoints(studentId).catch(() => null),
          knowledgeApi.list(currentSubject).catch(() => null),
          pathApi.current(studentId, currentSubject).catch(() => null),
        ]);

        // 非关键数据延迟加载，不阻塞首屏
        const now = new Date();
        const [dailyQuizRes, activeDatesRes] = await Promise.all([
          dailyQuizApi.getDaily(5, currentSubject).catch(() => null),
          dashboardApi
            .getActiveDates(studentId, now.getFullYear(), now.getMonth() + 1)
            .catch(() => null),
        ]);

        const errors: Record<string, boolean> = {};

        if (summaryRes?.data) {
          const d = summaryRes.data;
          setStats(d.stats || stats);
          setTasks(d.tasks || []);
          setRecommendations(d.recommendations || []);
        } else {
          errors.summary = true;
        }

        if (pathRes?.data?.nodes?.length) {
          setPathNodesState(
            pathRes.data.nodes.map(
              (n: PathNode & { name?: string }, idx: number) => ({
                id: n.id || idx + 1,
                title: n.title || n.name || `节点${idx + 1}`,
                status: n.status || "pending",
                type: n.type || "综合",
                kp_id: n.kp_id,
              }),
            ),
          );
        } else if (!pathRes) {
          errors.path = true;
        }

        if (pointsRes?.data?.data) {
          const total = pointsRes.data.data.total_points || 0;
          const lv = calcLevel(total);
          setPointsInfo({
            total,
            level: lv.level,
            current: lv.current_xp,
            need: lv.xp_per_level,
            percent: lv.progress_pct,
          });
        } else if (!pointsRes) {
          errors.points = true;
        }

        if (kgRes?.data?.data?.length) {
          setKgNodes(
            kgRes.data.data.slice(0, 14).map((k) => ({
              id: k.kp_id,
              name: k.name,
              prerequisites: k.prerequisites || [],
            })),
          );
        } else if (!kgRes) {
          errors.kg = true;
        }

        if (dailyQuizRes?.data?.data) {
          setDailyQuiz(dailyQuizRes.data.data);
        } else if (!dailyQuizRes) {
          errors.quiz = true;
        }

        if (activeDatesRes?.data?.data) {
          setActiveDates(new Set(activeDatesRes.data.data));
        }

        if (Object.keys(errors).length > 0) {
          setLoadErrors(errors);
        }
      } catch {
        message.error("部分数据加载失败");
      } finally {
        clearTimeout(timeoutId);
        setIsLoading(false);
        setSummaryLoading(false);
      }
    };
    fetchData();
    return () => clearTimeout(timeoutId);
  }, [studentId, currentSubject]);

  // Fetch active dates when calendar month changes
  useEffect(() => {
    if (!studentId) return;
    dashboardApi
      .getActiveDates(studentId, calendarDate.year(), calendarDate.month() + 1)
      .then((res) => {
        if (res.data?.data) {
          setActiveDates(new Set(res.data.data));
        }
      })
      .catch(() => {});
  }, [studentId, calendarDate]);

  const completedCount = pathNodesState.filter(
    (n) => n.status === "completed",
  ).length;

  const courseCards = useMemo(() => {
    const list =
      pathNodesState.length > 0
        ? pathNodesState.slice(0, 3)
        : [
            {
              id: "1",
              title: "设计基础",
              status: "in-progress",
              type: "设计",
            },
            {
              id: "2",
              title: "UX设计原理",
              status: "pending",
              type: "UX",
            },
            {
              id: "3",
              title: "3D建模入门",
              status: "pending",
              type: "3D",
            },
          ];
    const styles = [
      {
        bg: "bg-[#e8f0fe]",
        text: "text-[#003ecc]",
        bar: "bg-[#0052ff]",
        icon: <ApartmentOutlined />,
        num: "01",
      },
      {
        bg: "bg-[#fef3c7]",
        text: "text-[#92400e]",
        bar: "bg-[#d97706]",
        icon: <RocketOutlined />,
        num: "02",
      },
      {
        bg: "bg-[#fef9c3]",
        text: "text-[#713f12]",
        bar: "bg-[#a16207]",
        icon: <StarOutlined />,
        num: "03",
      },
    ];
    return list.map((course, i) => ({ ...course, ...styles[i] }));
  }, [pathNodesState]);

  const statCards = useMemo(
    () => [
      {
        title: "本周学习",
        value: stats.weekly_hours,
        suffix: "h",
        icon: <ClockCircleOutlined />,
        color: "#0052ff",
        path: "/personal",
      },
      {
        title: "连续打卡",
        value: stats.streak_days,
        suffix: "天",
        icon: <FireOutlined />,
        color: "#f59e0b",
        path: "/personal",
      },
      {
        title: "掌握知识点",
        value: stats.mastered_kps,
        suffix: "个",
        icon: <TrophyOutlined />,
        color: "#10b981",
        path: "/profile",
      },
      {
        title: "待完成任务",
        value: tasks.length,
        suffix: "项",
        icon: <RocketOutlined />,
        color: "#0ea5e9",
        path: "/learning-path",
      },
    ],
    [stats.weekly_hours, stats.streak_days, stats.mastered_kps, tasks.length],
  );

  const assignmentList = useMemo(() => {
    return tasks.length > 0 ? tasks.slice(0, 5) : [];
  }, [tasks]);

  const upcomingList = useMemo(() => {
    return tasks.length > 0 ? tasks.slice(0, 3) : [];
  }, [tasks]);

  const upcomingStyles = [
    { bg: "bg-[#e8f0fe]", text: "text-[#003ecc]" },
    { bg: "bg-[#fef3c7]", text: "text-[#92400e]" },
    { bg: "bg-[#fef9c3]", text: "text-[#713f12]" },
  ];

  return (
    <div className="space-y-8 pb-12">
      {/* ===== 顶部标题区 ===== */}
      <div className="flex items-center justify-between">
        <Typography.Title
          level={3}
          className="!m-0 text-slate-900 font-bold tracking-tight"
        >
          学习进度
        </Typography.Title>
        <div className="flex items-center gap-3">
          <div className="hidden sm:flex items-center gap-2 bg-white rounded-full border border-slate-100 px-4 py-2">
            <span className="text-xs text-slate-500">
              Lv.{pointsInfo?.level ?? 1}
            </span>
            <div className="w-20">
              <Progress
                percent={pointsInfo?.percent ?? 0}
                showInfo={false}
                strokeColor="#0052ff"
                trailColor="#f1f5f9"
                size="small"
              />
            </div>
          </div>
          <div className="w-9 h-9 rounded-full bg-slate-100 flex items-center justify-center text-slate-500 cursor-pointer hover:bg-slate-200 transition-colors">
            <CalendarOutlined />
          </div>
          <div className="w-9 h-9 rounded-full bg-slate-100 flex items-center justify-center text-slate-500 cursor-pointer hover:bg-slate-200 transition-colors relative">
            <FireOutlined />
            {stats.streak_days > 0 && (
              <span className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 rounded-full text-white text-[10px] flex items-center justify-center font-bold">
                {stats.streak_days}
              </span>
            )}
          </div>
          <div className="w-10 h-10 rounded-full bg-[#0052ff] flex items-center justify-center text-white font-bold text-sm">
            学
          </div>
        </div>
      </div>

      {/* ===== 学习进度横幅 ===== */}
      <div className="bg-gray-900 rounded-2xl p-6 lg:p-8 flex flex-col lg:flex-row gap-6 lg:gap-8 text-white">
        {/* 左侧 */}
        <div className="flex-1 flex flex-col justify-center min-w-[240px]">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/10 border border-white/10 w-fit mb-4">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-xs text-gray-300">
              欢迎回来，{displayName}
            </span>
          </div>
          <div className="text-2xl lg:text-[2rem] font-bold mb-6 leading-tight">
            你本周已完成{" "}
            <span className="text-white font-bold">{completedCount}</span> 节课!
          </div>
          <Button
            className="w-fit rounded-full bg-white text-[#1e1b4b] border-0 font-semibold hover:bg-[#e8f0fe] hover:shadow-lg hover:shadow-[#003ecc]/20 transition-all px-6"
            onClick={() => navigate("/learning-path")}
          >
            查看全部 <ArrowRightOutlined />
          </Button>
        </div>

        {/* 右侧课程卡片 */}
        <div className="flex gap-4 overflow-x-auto pb-2 relative z-10">
          {loadErrors.path && (
            <div className="min-w-[170px] flex-shrink-0 rounded-2xl p-5 bg-red-50 border border-red-100 flex flex-col items-center justify-center text-center">
              <div className="text-sm text-red-400 mb-2">路径加载失败</div>
              <Button
                size="small"
                type="link"
                onClick={() => window.location.reload()}
              >
                重试
              </Button>
            </div>
          )}
          {courseCards.map((course) => {
            const isCompleted = course.status === "completed";
            const isInProgress = course.status === "in-progress";
            const progressVal = isCompleted ? 100 : isInProgress ? 60 : 20;
            const statusLabel = isCompleted
              ? "已完成"
              : isInProgress
                ? "进行中"
                : "未开始";
            return (
              <div
                key={course.id}
                className={`${course.bg} rounded-2xl p-5 min-w-[170px] flex-shrink-0 text-slate-800 cursor-pointer hover:shadow-xl hover:-translate-y-1 transition-all relative overflow-hidden`}
                onClick={() =>
                  navigate("/resources", {
                    state: { kpId: (course as any).kp_id },
                  })
                }
              >
                {/* 顶部装饰条 */}
                <div
                  className={`absolute top-0 left-0 right-0 h-1 ${course.bar}`}
                  style={{ opacity: 0.6 }}
                />

                <div className="flex items-center justify-between mb-5">
                  <span
                    className={`text-xs font-bold px-2 py-0.5 rounded-full bg-white/50 ${course.text}`}
                  >
                    {course.num}
                  </span>
                  <span
                    className={`text-[10px] px-2 py-0.5 rounded-full font-medium ${isCompleted ? "bg-emerald-100 text-emerald-600" : isInProgress ? "bg-blue-100 text-blue-600" : "bg-slate-100 text-slate-500"}`}
                  >
                    {statusLabel}
                  </span>
                </div>
                <div
                  className={`w-10 h-10 rounded-xl flex items-center justify-center text-lg mb-3 shadow-sm bg-white/60 ${course.text}`}
                >
                  {course.icon}
                </div>
                <div className="font-bold text-sm mb-1 leading-tight">
                  {course.title}
                </div>
                <div className="text-xs text-slate-500 mb-4">
                  {course.type || "课程"}
                </div>
                <div className="flex items-center gap-2">
                  <div className="flex-1 h-1.5 bg-white/60 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full ${course.bar} transition-all duration-500`}
                      style={{ width: `${progressVal}%` }}
                    />
                  </div>
                  <span className="text-[10px] font-bold text-slate-500">
                    {progressVal}%
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* ===== 统计 + 日历 / 任务 + 待办 两栏 ===== */}
      <Row gutter={[24, 24]}>
        {/* 左侧主内容 */}
        <Col xs={24} lg={16}>
          {/* 统计 */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <Typography.Title
                level={5}
                className="!m-0 text-slate-800 font-semibold"
              >
                数据统计
              </Typography.Title>
            </div>
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
              {statCards.map((stat, idx) => {
                const sparkData = Array.from({ length: 7 }, (_, i) => ({
                  v: Math.max(
                    0,
                    (Number(stat.value) || 0) *
                      (0.4 + Math.sin(i + idx) * 0.3 + i * 0.1),
                  ),
                }));
                return (
                  <div
                    key={idx}
                    className="bg-white rounded-2xl p-5 border border-slate-100 hover:shadow-lg hover:-translate-y-0.5 transition-all cursor-pointer group"
                    onClick={() => navigate(stat.path)}
                  >
                    <div className="flex items-center justify-between mb-3">
                      <div
                        className="w-9 h-9 rounded-xl flex items-center justify-center text-white text-sm shrink-0 shadow-sm"
                        style={{ background: stat.color }}
                      >
                        {stat.icon}
                      </div>
                      <div className="w-16 h-8">
                        <ResponsiveContainer width="100%" height="100%">
                          <AreaChart data={sparkData}>
                            <defs>
                              <linearGradient
                                id={`spark-${idx}`}
                                x1="0"
                                y1="0"
                                x2="0"
                                y2="1"
                              >
                                <stop
                                  offset="0%"
                                  stopColor={stat.color}
                                  stopOpacity={0.3}
                                />
                                <stop
                                  offset="100%"
                                  stopColor={stat.color}
                                  stopOpacity={0}
                                />
                              </linearGradient>
                            </defs>
                            <Area
                              type="monotone"
                              dataKey="v"
                              stroke={stat.color}
                              strokeWidth={2}
                              fill={`url(#spark-${idx})`}
                              isAnimationActive={false}
                            />
                          </AreaChart>
                        </ResponsiveContainer>
                      </div>
                    </div>
                    <div className="text-2xl font-bold text-slate-800 mb-0.5 group-hover:text-[#0052ff] transition-colors">
                      {stat.value}
                      <span className="text-sm font-medium text-slate-400 ml-1">
                        {stat.suffix}
                      </span>
                    </div>
                    <div className="text-xs text-slate-500">{stat.title}</div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* 每日推送练习题 */}
          <div className="mt-8">
            <div className="flex items-center justify-between mb-4">
              <Typography.Title
                level={5}
                className="!m-0 text-slate-800 font-semibold"
              >
                <BookOutlined className="mr-2 text-[#0052ff]" />
                每日练习
              </Typography.Title>
              {dailyQuiz && (
                <div className="flex items-center gap-2">
                  <Tag className="rounded-full border-0 bg-[#e8f0fe] text-[#0052ff] text-xs">
                    难度: {dailyQuiz.difficulty_level}
                  </Tag>
                  <Tag className="rounded-full border-0 bg-slate-100 text-slate-600 text-xs">
                    {dailyQuiz.total_questions} 题
                  </Tag>
                </div>
              )}
            </div>
            <div className="bg-white rounded-2xl border border-slate-100 p-5 shadow-[0_8px_30px_rgb(0,0,0,0.12)]">
              <Spin spinning={quizLoading}>
                {loadErrors.quiz ? (
                  <div className="py-8 text-center">
                    <div className="text-sm text-red-400 mb-2">
                      练习题加载失败
                    </div>
                    <Button
                      size="small"
                      type="link"
                      onClick={() => {
                        setLoadErrors((e) => {
                          const n = { ...e };
                          delete n.quiz;
                          return n;
                        });
                        window.location.reload();
                      }}
                    >
                      重试
                    </Button>
                  </div>
                ) : dailyQuiz && dailyQuiz.questions.length > 0 ? (
                  <div>
                    {/* 题目进度条 */}
                    <div className="flex items-center gap-3 mb-5">
                      {dailyQuiz.questions.map((_, idx) => (
                        <div
                          key={idx}
                          className={`flex-1 h-2 rounded-full transition-all cursor-pointer ${
                            idx === currentQuizIdx
                              ? "bg-[#0052ff]"
                              : idx < currentQuizIdx
                                ? "bg-emerald-400"
                                : "bg-slate-100"
                          }`}
                          onClick={() => {
                            setCurrentQuizIdx(idx);
                            setSelectedAnswer(null);
                            setShowAnswer(false);
                          }}
                        />
                      ))}
                    </div>

                    {/* 当前题目 */}
                    {(() => {
                      const q = dailyQuiz.questions[currentQuizIdx];
                      if (!q) return null;
                      return (
                        <div>
                          <div className="flex items-center gap-3 mb-3">
                            <span className="w-7 h-7 rounded-lg bg-[#0052ff]/10 text-[#0052ff] flex items-center justify-center text-xs font-bold">
                              {currentQuizIdx + 1}
                            </span>
                            <Tag className="rounded-full border-0 bg-slate-100 text-slate-600 text-xs">
                              {q.type}
                            </Tag>
                            <Tag className="rounded-full border-0 bg-amber-50 text-amber-600 text-xs">
                              难度 {q.difficulty}/5
                            </Tag>
                            {q.source && (
                              <Tag className="rounded-full border-0 bg-blue-50 text-blue-600 text-xs">
                                来源: {q.source}
                              </Tag>
                            )}
                          </div>

                          <div className="text-slate-800 text-sm mb-4 leading-relaxed">
                            {q.content}
                          </div>

                          {/* 选项（选择题） */}
                          {q.options && q.options.length > 0 && (
                            <div className="space-y-2 mb-4">
                              {q.options.map((opt) => (
                                <div
                                  key={opt.id}
                                  className={`flex items-center gap-3 p-3 rounded-xl border cursor-pointer transition-all text-sm ${
                                    selectedAnswer === opt.id
                                      ? showAnswer
                                        ? opt.id === q.correct_answer
                                          ? "bg-emerald-50 border-emerald-300"
                                          : "bg-red-50 border-red-300"
                                        : "bg-[#0052ff]/5 border-[#0052ff]"
                                      : showAnswer &&
                                          opt.id === q.correct_answer
                                        ? "bg-emerald-50 border-emerald-300"
                                        : "bg-white border-slate-200 hover:border-slate-300 hover:bg-slate-50"
                                  }`}
                                  onClick={() => {
                                    if (!showAnswer) {
                                      setSelectedAnswer(opt.id);
                                    }
                                  }}
                                >
                                  <span
                                    className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium shrink-0 ${
                                      selectedAnswer === opt.id
                                        ? "bg-[#0052ff] text-white"
                                        : "bg-slate-100 text-slate-600"
                                    }`}
                                  >
                                    {opt.id}
                                  </span>
                                  <span className="text-slate-700">
                                    {opt.text}
                                  </span>
                                  {showAnswer &&
                                    opt.id === q.correct_answer && (
                                      <CheckCircleOutlined className="text-emerald-500 ml-auto" />
                                    )}
                                </div>
                              ))}
                            </div>
                          )}

                          {/* 提示 */}
                          {showAnswer && q.hint && (
                            <div className="p-3 rounded-xl bg-amber-50 border border-amber-100 mb-3">
                              <div className="text-xs text-amber-800">
                                <span className="font-medium">提示：</span>
                                {q.hint}
                              </div>
                            </div>
                          )}

                          {/* 操作按钮 */}
                          <div className="flex items-center gap-2">
                            {!showAnswer && q.options && (
                              <Button
                                type="primary"
                                size="small"
                                className="rounded-lg bg-[#0052ff]"
                                disabled={!selectedAnswer}
                                onClick={() => setShowAnswer(true)}
                              >
                                提交答案
                              </Button>
                            )}
                            {!showAnswer && !q.options && (
                              <Button
                                type="primary"
                                size="small"
                                className="rounded-lg bg-[#0052ff]"
                                onClick={() => setShowAnswer(true)}
                              >
                                查看提示
                              </Button>
                            )}
                            <Button
                              size="small"
                              className="rounded-lg"
                              onClick={() => {
                                if (
                                  currentQuizIdx <
                                  dailyQuiz.questions.length - 1
                                ) {
                                  setCurrentQuizIdx(currentQuizIdx + 1);
                                  setSelectedAnswer(null);
                                  setShowAnswer(false);
                                }
                              }}
                              disabled={
                                currentQuizIdx >= dailyQuiz.questions.length - 1
                              }
                            >
                              下一题 <ArrowRightOutlined />
                            </Button>
                          </div>
                        </div>
                      );
                    })()}

                    {/* 薄弱知识点提示 */}
                    {dailyQuiz.weak_areas.length > 0 && (
                      <div className="mt-4 pt-3 border-t border-slate-100">
                        <div className="text-xs text-slate-400 mb-2">
                          今日练习重点覆盖你的薄弱知识点：
                        </div>
                        <div className="flex flex-wrap gap-2">
                          {dailyQuiz.weak_areas.slice(0, 3).map((area) => (
                            <Tag
                              key={area}
                              className="rounded-full border-0 bg-red-50 text-red-500 text-xs"
                            >
                              {area}
                            </Tag>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="py-8 text-center">
                    <div className="w-12 h-12 rounded-2xl bg-[#e8f0fe] flex items-center justify-center text-[#a8c4f9] text-xl mx-auto mb-2">
                      <BookOutlined />
                    </div>
                    <div className="text-sm text-slate-500 mb-1">
                      暂无练习题
                    </div>
                    <div className="text-xs text-slate-400">
                      完善学习资料后将为你推荐练习题
                    </div>
                  </div>
                )}
              </Spin>
            </div>
          </div>
        </Col>

        {/* 右侧边栏 */}
        <Col xs={24} lg={8}>
          {/* 日历 */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <Typography.Title
                level={5}
                className="!m-0 text-slate-800 font-semibold"
              >
                {calendarDate.format("YYYY年M月")}
              </Typography.Title>
              <div className="flex gap-1">
                <Button
                  type="text"
                  size="small"
                  icon={<DownOutlined className="rotate-90 text-xs" />}
                  onClick={() =>
                    setCalendarDate(calendarDate.subtract(1, "month"))
                  }
                />
                <Button
                  type="text"
                  size="small"
                  icon={<DownOutlined className="-rotate-90 text-xs" />}
                  onClick={() => setCalendarDate(calendarDate.add(1, "month"))}
                />
              </div>
            </div>
            <div className="bg-white rounded-2xl border border-slate-100 p-4 overflow-hidden calendar-active-dates">
              <style>{`
                .calendar-active-dates .ant-picker-cell-in-view .ant-picker-cell-inner {
                  border-radius: 8px;
                }
                .calendar-active-dates .active-date .ant-picker-cell-inner {
                  background: #28a745 !important;
                  color: #fff !important;
                  border-radius: 8px;
                }
                .calendar-active-dates .active-date:hover .ant-picker-cell-inner {
                  background: #218838 !important;
                }
                .calendar-active-dates .ant-picker-calendar-header {
                  display: none !important;
                }
                .calendar-active-dates .ant-picker-cell .ant-picker-calendar-date-value {
                  display: block !important;
                }
                .calendar-active-dates .ant-picker-cell .ant-picker-calendar-date-content {
                  display: none !important;
                }
              `}</style>
              <Calendar
                fullscreen={false}
                value={calendarDate}
                onChange={(date) => setCalendarDate(date)}
                cellRender={(date, info) => {
                  if (info.type === "date") {
                    const dateStr = date.format("YYYY-MM-DD");
                    const isActive = activeDates.has(dateStr);
                    return (
                      <div className={isActive ? "active-date" : ""}>
                        {info.originNode}
                      </div>
                    );
                  }
                  return info.originNode;
                }}
              />
            </div>
          </div>

          {/* 即将开始 */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <Typography.Title
                level={5}
                className="!m-0 text-slate-800 font-semibold"
              >
                即将开始
              </Typography.Title>
              <Button
                type="link"
                className="text-[#0052ff] font-medium"
                onClick={() => navigate("/learning-path")}
              >
                查看全部
              </Button>
            </div>
            <div className="space-y-3">
              {upcomingList.map((task, idx) => {
                const meta =
                  RESOURCE_META[task.type || "doc"] || RESOURCE_META.doc;
                const us = upcomingStyles[idx];
                return (
                  <div
                    key={task.task_id || idx}
                    className="flex items-center gap-4 bg-white rounded-2xl border border-slate-100 p-4 hover:shadow-md transition-all cursor-pointer"
                    onClick={() => navigate("/learning-path")}
                  >
                    <div
                      className={`w-12 h-12 rounded-xl ${us.bg} flex items-center justify-center text-xl ${us.text}`}
                    >
                      {meta.icon}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="font-medium text-sm text-slate-800 truncate">
                        {task.title}
                      </div>
                      <div className="text-xs text-slate-400 mt-0.5">
                        {task.duration ? `${task.duration} 分钟` : "待完成"}
                      </div>
                    </div>
                    <ArrowRightOutlined className="text-slate-300 text-sm" />
                  </div>
                );
              })}
              {upcomingList.length === 0 && (
                <div className="py-10 text-center bg-white rounded-2xl border border-slate-100">
                  <div className="w-14 h-14 rounded-2xl bg-slate-50 flex items-center justify-center text-slate-300 text-2xl mx-auto mb-3">
                    <CalendarOutlined />
                  </div>
                  <div className="text-sm text-slate-500 mb-1">
                    暂无即将开始的事件
                  </div>
                  <div className="text-xs text-slate-400">
                    学习路径中待办的任务会显示在这里
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* 我的任务 */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <Typography.Title
                level={5}
                className="!m-0 text-slate-800 font-semibold"
              >
                我的任务
              </Typography.Title>
              <Button
                type="link"
                className="text-[#0052ff] font-medium"
                onClick={() => navigate("/learning-path")}
              >
                查看全部
              </Button>
            </div>
            <div className="space-y-3">
              <Spin spinning={summaryLoading}>
                {assignmentList.length === 0 ? (
                  <div className="py-10 text-center bg-white rounded-2xl border border-slate-100">
                    <div className="w-14 h-14 rounded-2xl bg-slate-50 flex items-center justify-center text-slate-300 text-2xl mx-auto mb-3">
                      <RocketOutlined />
                    </div>
                    <div className="text-sm text-slate-500 mb-1">暂无任务</div>
                    <div className="text-xs text-slate-400">
                      去学习中心开启新的学习旅程吧
                    </div>
                  </div>
                ) : (
                  assignmentList.map((item, idx) => {
                    const meta =
                      RESOURCE_META[item.type || "doc"] || RESOURCE_META.doc;
                    const progressPct = Math.round(item.progress * 100);
                    return (
                      <div
                        key={item.task_id || idx}
                        className="flex items-center gap-4 bg-white rounded-2xl border border-slate-100 p-4 hover:shadow-md transition-all cursor-pointer"
                        onClick={() => navigate("/learning-path")}
                      >
                        <div
                          className="w-12 h-12 rounded-xl flex items-center justify-center text-xl"
                          style={{
                            background: meta.bg,
                            color: meta.color,
                          }}
                        >
                          {meta.icon}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <div className="font-medium text-sm text-slate-800 truncate">
                              {item.title}
                            </div>
                            {progressPct === 100 && (
                              <Tag className="rounded-full border-0 bg-emerald-50 text-emerald-600 text-[10px] px-2 py-0 leading-normal">
                                已完成
                              </Tag>
                            )}
                          </div>
                          <div className="flex items-center gap-2 mt-1">
                            <span className="text-xs text-slate-400">
                              {item.type || "任务"}
                            </span>
                            {item.progress > 0 && (
                              <>
                                <Progress
                                  percent={progressPct}
                                  size="small"
                                  className="w-16"
                                  strokeColor={meta.color}
                                  trailColor="#f1f5f9"
                                />
                                <span className="text-xs text-slate-400">
                                  {progressPct}%
                                </span>
                              </>
                            )}
                          </div>
                        </div>
                        <ArrowRightOutlined className="text-slate-300 text-sm" />
                      </div>
                    );
                  })
                )}
              </Spin>
            </div>
          </div>
        </Col>
      </Row>

      {/* 知识图谱弹窗 */}
      <Modal
        title={
          <span className="font-semibold text-slate-800">知识图谱概览</span>
        }
        open={kgModalOpen}
        onCancel={() => setKgModalOpen(false)}
        footer={null}
        width={720}
        className="rounded-2xl"
      >
        <div className="space-y-4 py-2">
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-100">
            <div className="font-semibold text-slate-800 mb-2">
              核心知识网络
            </div>
            {kgNodes.length > 0 ? (
              <svg
                width="100%"
                viewBox="0 0 640 400"
                className="overflow-visible"
              >
                <defs>
                  <radialGradient id="kg-node-grad">
                    <stop offset="0%" stopColor="#818cf8" />
                    <stop offset="100%" stopColor="#0052ff" />
                  </radialGradient>
                  <marker
                    id="kg-arrow"
                    viewBox="0 0 10 10"
                    refX="10"
                    refY="5"
                    markerWidth="6"
                    markerHeight="6"
                    orient="auto-start-reverse"
                  >
                    <path d="M 0 0 L 10 5 L 0 10 z" fill="#94a3b8" />
                  </marker>
                </defs>
                {(() => {
                  const nodeMap = new Map(
                    kgNodes.map((n, i) => {
                      const angle =
                        (2 * Math.PI * i) / kgNodes.length - Math.PI / 2;
                      const cx = 320 + 160 * Math.cos(angle);
                      const cy = 200 + 140 * Math.sin(angle);
                      return [n.id, { cx, cy }];
                    }),
                  );
                  return kgNodes.flatMap((node) =>
                    node.prerequisites
                      .filter((pre) => nodeMap.has(pre))
                      .map((pre) => {
                        const from = nodeMap.get(pre)!;
                        const to = nodeMap.get(node.id)!;
                        return (
                          <line
                            key={`${pre}-${node.id}`}
                            x1={from.cx}
                            y1={from.cy}
                            x2={to.cx}
                            y2={to.cy}
                            stroke="#cbd5e1"
                            strokeWidth={1.5}
                            markerEnd="url(#kg-arrow)"
                          />
                        );
                      }),
                  );
                })()}
                {kgNodes.map((node, i) => {
                  const angle =
                    (2 * Math.PI * i) / kgNodes.length - Math.PI / 2;
                  const cx = 320 + 160 * Math.cos(angle);
                  const cy = 200 + 140 * Math.sin(angle);
                  return (
                    <g key={node.id}>
                      <circle
                        cx={cx}
                        cy={cy}
                        r={24}
                        fill="url(#kg-node-grad)"
                        filter="drop-shadow(0 2px 4px rgba(79,70,229,0.3))"
                      />
                      <text
                        x={cx}
                        y={cy + 1}
                        textAnchor="middle"
                        dominantBaseline="central"
                        fill="white"
                        fontSize={10}
                        fontWeight={600}
                      >
                        {node.name.length > 4
                          ? node.name.slice(0, 4) + ".."
                          : node.name}
                      </text>
                    </g>
                  );
                })}
              </svg>
            ) : (
              <div className="text-sm text-slate-400 text-center py-6">
                暂无知识点数据
              </div>
            )}
          </div>
          <div className="flex items-center gap-2 text-xs text-slate-400">
            <NodeIndexOutlined />
            <span>知识图谱确保学习路径科学性，减少大模型幻觉影响</span>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default Dashboard;
