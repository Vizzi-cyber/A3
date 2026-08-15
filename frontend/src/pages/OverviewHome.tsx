/**
 * 学习全景首页（LearningOverviewHome）
 * 浅色高级首页，与全站 antd / Dashboard 风格完全统一：
 *   - 顶部：欢迎语 + 深色学习进度横幅（Dashboard 同款视觉）
 *   - 数据总览：4 张统计卡（数字滚动）+ 掌握度环形
 *   - 功能全景：8 个功能卡片（图标 + 名称 + 真实数据 + hover 上浮 + 点击进入）
 *   - 今日任务 + 学习路径摘要
 * 数据来源：后端真实接口（dashboard / learning-path / daily-quiz / gamification）
 */
import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Typography, Progress, Button, Tag, Empty,
} from "antd";
import {
  NodeIndexOutlined, CodeOutlined, ThunderboltOutlined, RobotOutlined,
  EditOutlined, BookOutlined, TrophyOutlined, LineChartOutlined,
  FireOutlined, ClockCircleOutlined, RightOutlined, CheckCircleOutlined,
  ArrowRightOutlined,
} from "@ant-design/icons";
import CountUp from "../components/animations/CountUp";
import AnimatedRing from "../components/animations/AnimatedRing";
import AnimatedText from "../components/animations/AnimatedText";
import api from "../services/api";

interface OverviewData {
  weeklyHours: number;
  totalHours: number;
  masteredKps: number;
  achievements: number;
  favorites: number;
  streakDays: number;
  todayMin: number;
  tasks: { title: string; type?: string }[];
  pathProgress: number;
  pathNodes: number;
  quizTotal: number;
  quizCovered: number;
  points: number;
  level: number;
}

const EMPTY: OverviewData = {
  weeklyHours: 0, totalHours: 0, masteredKps: 0, achievements: 0, favorites: 0,
  streakDays: 0, todayMin: 0, tasks: [], pathProgress: 0, pathNodes: 0,
  quizTotal: 0, quizCovered: 0, points: 0, level: 1,
};

const OverviewHome: React.FC = () => {
  const navigate = useNavigate();
  const [data, setData] = useState<OverviewData>(EMPTY);
  const [username, setUsername] = useState("同学");

  useEffect(() => {
    const load = async () => {
      try {
        const [dash, path, quiz, gam, me] = await Promise.allSettled([
          api.get("/dashboard/student_001/summary"),
          api.get("/learning-path/student_001/current"),
          api.get("/daily-quiz/stats"),
          api.get("/gamification/student_001/points"),
          api.get("/auth/me"),
        ]);
        const val = (r: PromiseSettledResult<any>) => (r.status === "fulfilled" ? r.value?.data : null);
        const stats = val(dash)?.stats ?? {};
        const pathD = val(path)?.data ?? val(path) ?? {};
        const quizD = val(quiz)?.data ?? val(quiz) ?? {};
        const gamD = val(gam)?.data ?? val(gam) ?? {};
        const meD = val(me)?.data ?? val(me) ?? {};

        setData({
          weeklyHours: stats.weekly_hours ?? 0,
          totalHours: stats.total_hours ?? 0,
          masteredKps: stats.mastered_kps ?? 0,
          achievements: stats.achievements ?? 0,
          favorites: stats.favorites ?? 0,
          streakDays: stats.streak_days ?? 0,
          todayMin: stats.today_duration_min ?? 0,
          tasks: (stats.tasks ?? (val(dash)?.tasks ?? [])).slice?.(0, 3) ?? [],
          pathProgress: pathD.progress ?? 0,
          pathNodes: pathD.nodes?.length ?? pathD.total_nodes ?? 0,
          quizTotal: quizD.total_questions ?? 0,
          quizCovered: quizD.knowledge_points_covered ?? 0,
          points: gamD.points ?? gamD.total_points ?? 0,
          level: gamD.level ?? stats.level ?? 1,
        });
        if (meD.username) setUsername(meD.username);
      } catch {
        // 保持占位
      }
    };
    load();
  }, []);

  // 功能卡片配置
  const features = [
    {
      icon: <NodeIndexOutlined />, label: "学习路径", desc: "ADPP 自适应规划",
      data: `${data.pathNodes} 节点 · ${Math.round(data.pathProgress)}%`,
      color: "#6366f1", bg: "bg-indigo-50 text-indigo-500", route: "/learning-path",
    },
    {
      icon: <CodeOutlined />, label: "C语言中心", desc: "芯片级编程训练",
      data: "16 知识点", color: "#3b82f6", bg: "bg-blue-50 text-blue-500", route: "/resources",
    },
    {
      icon: <ThunderboltOutlined />, label: "电路仿真", desc: "MNA 虚拟实验",
      data: "故障诊断 + AI 分析", color: "#f97316", bg: "bg-orange-50 text-orange-500", route: "/circuit-simulator",
    },
    {
      icon: <RobotOutlined />, label: "AI 智能辅导", desc: "12 个智能体",
      data: "苏格拉底式引导", color: "#22d3ee", bg: "bg-cyan-50 text-cyan-500", route: "/tutor",
    },
    {
      icon: <EditOutlined />, label: "每日练习", desc: "个性化选题",
      data: `已练 ${data.quizTotal} 题`, color: "#0ea5e9", bg: "bg-sky-50 text-sky-500", route: "/learning-path",
    },
    {
      icon: <BookOutlined />, label: "知识库", desc: "双向链接笔记",
      data: "WikiLink 知识图谱", color: "#8b5cf6", bg: "bg-violet-50 text-violet-500", route: "/knowledge-base",
    },
    {
      icon: <TrophyOutlined />, label: "成就排行", desc: "六维积分榜",
      data: `${data.achievements} 成就 · ${data.points} 积分`, color: "#f59e0b", bg: "bg-amber-50 text-amber-500", route: "/leaderboard",
    },
    {
      icon: <LineChartOutlined />, label: "学情分析", desc: "趋势与效果评估",
      data: `累计 ${data.totalHours}h`, color: "#10b981", bg: "bg-emerald-50 text-emerald-500", route: "/personal",
    },
  ];

  const statCards = [
    { title: "本周学习", value: data.weeklyHours, suffix: "h", icon: <ClockCircleOutlined />, color: "#0052ff" },
    { title: "连续打卡", value: data.streakDays, suffix: "天", icon: <FireOutlined />, color: "#f59e0b" },
    { title: "掌握知识点", value: data.masteredKps, suffix: "个", icon: <CheckCircleOutlined />, color: "#10b981" },
    { title: "待完成任务", value: data.tasks.length, suffix: "项", icon: <RightOutlined />, color: "#0ea5e9" },
  ];

  return (
    <div className="space-y-6">
      {/* ===== 欢迎 + 学习进度横幅（Dashboard 同款深色横幅） ===== */}
      <div className="bg-gray-900 rounded-2xl p-6 lg:p-8 flex flex-col lg:flex-row gap-6 lg:gap-10 text-white relative overflow-hidden">
        {/* 装饰光晕 */}
        <div className="absolute -right-20 -top-24 w-72 h-72 rounded-full bg-indigo-500/25 blur-3xl pointer-events-none" />
        <div className="absolute -left-16 -bottom-24 w-64 h-64 rounded-full bg-sky-500/20 blur-3xl pointer-events-none" />

        <div className="flex-1 relative z-10">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-xs text-slate-300">欢迎回来</span>
          </div>
          <h2 className="text-2xl lg:text-3xl font-bold mt-1.5">
            <AnimatedText text={`${username}，今天也要加油！`} delay={0.1} />
          </h2>
          <p className="text-sm text-slate-300/90 mt-2 leading-relaxed">
            今天已学习 {data.todayMin} 分钟，距目标 2 小时还有{" "}
            <span className="text-sky-300 font-semibold">
              {Math.max(0, 120 - data.todayMin)} 分钟
            </span>
            。按你的 ADPP 路径继续探索吧！
          </p>
          <div className="mt-4 flex flex-wrap gap-2">
            <Tag className="rounded-full border-0 bg-white/10 text-white">Lv.{data.level}</Tag>
            <Tag className="rounded-full border-0 bg-white/10 text-white">{data.points} 积分</Tag>
            <Tag className="rounded-full border-0 bg-white/10 text-white">连续 {data.streakDays} 天</Tag>
          </div>
        </div>

        {/* 掌握度环形 */}
        <div className="flex items-center gap-5 relative z-10">
          <AnimatedRing
            percent={Math.min(100, Math.round((data.masteredKps / 20) * 100))}
            size={110}
            strokeWidth={10}
            color="#60a5fa"
            trackColor="rgba(255,255,255,0.15)"
          >
            <div className="text-center">
              <div className="text-2xl font-bold text-white">
                <CountUp value={data.masteredKps} duration={1.5} />
              </div>
              <div className="text-[10px] text-slate-300">已掌握/20</div>
            </div>
          </AnimatedRing>
          <div className="hidden sm:block">
            <div className="font-semibold">本周进度</div>
            <div className="text-xs text-slate-300 mt-1">累计学习 {data.totalHours}h</div>
            <Button
              type="primary"
              size="small"
              className="mt-3 rounded-full bg-sky-400 border-sky-400 hover:!bg-sky-300"
              icon={<ArrowRightOutlined />}
              onClick={() => navigate("/learning-path")}
            >
              继续学习
            </Button>
          </div>
        </div>
      </div>

      {/* ===== 数据总览 ===== */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((s) => (
          <div key={s.title} className="bg-white rounded-2xl border border-slate-100 shadow-card p-5 hover:shadow-card-hover transition-all duration-300 hover:-translate-y-0.5">
            <div className="flex items-center justify-between">
              <span className="text-xs text-slate-500">{s.title}</span>
              <span className="w-8 h-8 rounded-full flex items-center justify-center" style={{ background: `${s.color}15`, color: s.color }}>
                {s.icon}
              </span>
            </div>
            <div className="mt-2 text-2xl font-bold text-slate-800">
              <CountUp value={s.value} duration={1.4} />
              <span className="text-sm font-medium text-slate-400 ml-1">{s.suffix}</span>
            </div>
          </div>
        ))}
      </div>

      {/* ===== 功能全景 ===== */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <Typography.Title level={5} className="!m-0 text-slate-800 font-semibold">
            功能全景
          </Typography.Title>
          <span className="text-xs text-slate-400">悬停查看 · 点击进入</span>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {features.map((f) => (
            <div
              key={f.label}
              className="group bg-white rounded-2xl border border-slate-100 shadow-card p-5 cursor-pointer transition-all duration-300 hover:shadow-card-hover hover:-translate-y-1 hover:border-slate-200"
              onClick={() => navigate(f.route)}
            >
              <div className="flex items-start justify-between">
                <div className={`w-11 h-11 rounded-xl ${f.bg} flex items-center justify-center text-xl transition-transform duration-300 group-hover:scale-110`}>
                  {f.icon}
                </div>
                <ArrowRightOutlined className="text-slate-300 group-hover:text-[#0052ff] group-hover:translate-x-1 transition-all" />
              </div>
              <div className="mt-3 font-semibold text-slate-800 group-hover:text-[#0052ff] transition-colors">
                {f.label}
              </div>
              <div className="text-xs text-slate-400 mt-0.5">{f.desc}</div>
              <div className="mt-2.5 inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium" style={{ background: `${f.color}12`, color: f.color }}>
                <span className="w-1.5 h-1.5 rounded-full" style={{ background: f.color }} />
                {f.data}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* ===== 今日任务 + 路径摘要 ===== */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="bg-white rounded-2xl border border-slate-100 shadow-card p-5">
          <div className="font-semibold text-slate-800 mb-3 flex items-center gap-2">
            <ClockCircleOutlined className="text-[#0052ff]" />
            今日任务
          </div>
          {data.tasks.length > 0 ? (
            <div className="space-y-2">
              {data.tasks.map((t, i) => (
                <div key={i} className="flex items-center gap-2.5 p-2.5 rounded-xl bg-slate-50 hover:bg-slate-100 transition-colors">
                  <CheckCircleOutlined className="text-emerald-500" />
                  <span className="text-sm text-slate-700">{t.title}</span>
                </div>
              ))}
            </div>
          ) : (
            <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description={<span className="text-xs text-slate-400">暂无待办，享受学习吧</span>} />
          )}
        </div>

        <div className="bg-white rounded-2xl border border-slate-100 shadow-card p-5">
          <div className="font-semibold text-slate-800 mb-3 flex items-center gap-2">
            <NodeIndexOutlined className="text-[#0052ff]" />
            学习路径进度
          </div>
          <div className="flex items-center justify-between text-xs text-slate-500 mb-2">
            <span>{data.pathNodes} 个知识点</span>
            <span>{Math.round(data.pathProgress)}%</span>
          </div>
          <Progress
            percent={Math.round(data.pathProgress)}
            strokeColor={{ "0%": "#6366f1", "100%": "#10b981" }}
            trailColor="#f1f5f9"
          />
          <div className="mt-3 flex items-center justify-between">
            <span className="text-xs text-slate-400">每日练习已覆盖 {data.quizCovered} 个知识点</span>
            <Button
              type="link"
              size="small"
              className="!text-[#0052ff]"
              onClick={() => navigate("/learning-path")}
            >
              查看路径 <RightOutlined />
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OverviewHome;
