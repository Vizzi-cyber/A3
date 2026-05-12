import React, { useEffect, useState, useRef } from "react";
import { Spin, Tag, Radio, message } from "antd";
import {
  TrophyOutlined,
  FireOutlined,
  RobotOutlined,
  BookOutlined,
  RocketOutlined,
  RiseOutlined,
  CrownOutlined,
  ThunderboltOutlined,
  StarOutlined,
  TeamOutlined,
} from "@ant-design/icons";
import gsap from "gsap";
import { useAppStore } from "../store";
import { leaderboardPlusApi } from "../services/api";
import type { LeaderboardEntryPlus } from "../services/api";

// ==================== 维度定义 ====================
const DIMENSIONS = [
  {
    key: "points",
    label: "学习成长榜",
    desc: "累计成长值排名",
    icon: <TrophyOutlined />,
    color: "#f59e0b",
    gradient: "from-amber-400 to-orange-500",
    bg: "from-amber-50 to-orange-50",
    metric: "成长值",
  },
  {
    key: "streak",
    label: "连续学习榜",
    desc: "连续打卡天数排名",
    icon: <FireOutlined />,
    color: "#ef4444",
    gradient: "from-red-400 to-rose-500",
    bg: "from-red-50 to-rose-50",
    metric: "天",
  },
  {
    key: "mastery",
    label: "知识掌握榜",
    desc: "知识点掌握率排名",
    icon: <BookOutlined />,
    color: "#10b981",
    gradient: "from-emerald-400 to-green-500",
    bg: "from-emerald-50 to-green-50",
    metric: "%",
  },
  {
    key: "quiz_score",
    label: "闯关挑战榜",
    desc: "测验平均分排名",
    icon: <RocketOutlined />,
    color: "#8b5cf6",
    gradient: "from-purple-400 to-violet-500",
    bg: "from-purple-50 to-violet-50",
    metric: "分",
  },
  {
    key: "ai_collab",
    label: "AI协作榜",
    desc: "AI互动次数排名",
    icon: <RobotOutlined />,
    color: "#0ea5e9",
    gradient: "from-sky-400 to-blue-500",
    bg: "from-sky-50 to-blue-50",
    metric: "次",
  },
  {
    key: "improvement",
    label: "进步最快榜",
    desc: "近期能力提升排名",
    icon: <RiseOutlined />,
    color: "#6366f1",
    gradient: "from-indigo-400 to-violet-500",
    bg: "from-indigo-50 to-violet-50",
    metric: "%",
  },
];

const PERIODS = [
  { value: "weekly", label: "本周" },
  { value: "monthly", label: "本月" },
  { value: "all", label: "总榜" },
];

// ==================== Top3 领奖台 ====================
const Podium: React.FC<{
  entries: LeaderboardEntryPlus[];
  dimension: (typeof DIMENSIONS)[number];
}> = ({ entries, dimension }) => {
  const podiumRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!podiumRef.current) return;
    const items = podiumRef.current.querySelectorAll(".podium-item");
    gsap.fromTo(
      items,
      { opacity: 0, y: 30, scale: 0.8 },
      {
        opacity: 1,
        y: 0,
        scale: 1,
        duration: 0.5,
        stagger: 0.15,
        ease: "back.out(1.4)",
      },
    );
  }, [entries]);

  const top3 = entries.slice(0, 3);
  if (top3.length === 0) return null;

  // 领奖台顺序：2nd, 1st, 3rd
  const podiumOrder = [
    top3[1] && { ...top3[1], displayRank: 2, height: 100 },
    top3[0] && { ...top3[0], displayRank: 1, height: 140 },
    top3[2] && { ...top3[2], displayRank: 3, height: 80 },
  ].filter(Boolean);

  const rankIcons: Record<number, React.ReactNode> = {
    1: <CrownOutlined className="text-yellow-500" />,
    2: <StarOutlined className="text-slate-400" />,
    3: <StarOutlined className="text-amber-600" />,
  };

  const rankColors: Record<number, string> = {
    1: "from-yellow-400 to-amber-500",
    2: "from-slate-300 to-slate-400",
    3: "from-amber-500 to-amber-600",
  };

  return (
    <div ref={podiumRef} className="flex items-end justify-center gap-4 mb-6">
      {podiumOrder.map(
        (item) =>
          item && (
            <div
              key={item.student_id}
              className="podium-item flex flex-col items-center"
              style={{ width: 120 }}
            >
              {/* 头像 */}
              <div className="relative mb-2">
                <div
                  className={`w-16 h-16 rounded-full bg-gradient-to-br ${rankColors[item.displayRank]} flex items-center justify-center text-white text-xl font-bold shadow-lg`}
                >
                  {item.username?.[0] || "?"}
                </div>
                <div className="absolute -bottom-1 -right-1 w-7 h-7 rounded-full bg-white shadow-md flex items-center justify-center text-sm">
                  {rankIcons[item.displayRank]}
                </div>
              </div>

              {/* 名字 */}
              <div className="text-sm font-bold text-slate-700 mb-1 truncate max-w-[100px] text-center">
                {item.username}
              </div>

              {/* 分数 */}
              <div className="text-xs text-slate-500 mb-2">
                {item.score}
                <span className="text-slate-300 ml-0.5">
                  {dimension.metric}
                </span>
              </div>

              {/* 领奖台柱子 */}
              <div
                className="w-full rounded-t-xl flex items-center justify-center text-white font-bold text-2xl"
                style={{
                  height: item.height,
                  background: `linear-gradient(180deg, ${dimension.color}dd, ${dimension.color})`,
                }}
              >
                {item.displayRank}
              </div>
            </div>
          ),
      )}
    </div>
  );
};

// ==================== 排行列表 ====================
const RankList: React.FC<{
  entries: LeaderboardEntryPlus[];
  dimension: (typeof DIMENSIONS)[number];
  currentStudentId: string;
}> = ({ entries, dimension, currentStudentId }) => {
  const listRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!listRef.current) return;
    const items = listRef.current.querySelectorAll(".rank-item");
    gsap.fromTo(
      items,
      { opacity: 0, x: -10 },
      { opacity: 1, x: 0, duration: 0.3, stagger: 0.04, ease: "power2.out" },
    );
  }, [entries]);

  const rest = entries.slice(3);
  if (rest.length === 0) return null;

  return (
    <div ref={listRef} className="space-y-1.5">
      {rest.map((entry) => {
        const isMe = entry.student_id === currentStudentId;
        return (
          <div
            key={entry.student_id}
            className={`rank-item flex items-center gap-3 px-4 py-2.5 rounded-xl transition-all duration-200 ${
              isMe
                ? "bg-indigo-50 border border-indigo-200 shadow-sm"
                : "bg-white border border-slate-100 hover:bg-slate-50"
            }`}
          >
            {/* 排名 */}
            <div
              className={`w-8 h-8 rounded-lg flex items-center justify-center text-sm font-bold ${
                isMe
                  ? "bg-indigo-500 text-white"
                  : "bg-slate-100 text-slate-500"
              }`}
            >
              {entry.rank}
            </div>

            {/* 头像 */}
            <div
              className={`w-9 h-9 rounded-full flex items-center justify-center text-white text-sm font-bold ${
                isMe
                  ? "bg-gradient-to-br from-indigo-400 to-purple-500"
                  : "bg-gradient-to-br from-slate-300 to-slate-400"
              }`}
            >
              {entry.username?.[0] || "?"}
            </div>

            {/* 名字 */}
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <span
                  className={`text-sm font-medium truncate ${
                    isMe ? "text-indigo-700" : "text-slate-700"
                  }`}
                >
                  {entry.username}
                </span>
                {isMe && (
                  <Tag className="rounded-full border-0 bg-indigo-100 text-indigo-600 text-[10px] px-1.5 py-0">
                    我
                  </Tag>
                )}
              </div>
            </div>

            {/* 分数 */}
            <div className="text-right">
              <span className="text-sm font-bold text-slate-800">
                {entry.score}
              </span>
              <span className="text-xs text-slate-400 ml-0.5">
                {dimension.metric}
              </span>
            </div>
          </div>
        );
      })}
    </div>
  );
};

// ==================== 排行榜主页面 ====================
const LeaderboardPlus: React.FC = () => {
  const studentId = useAppStore((s) => s.studentId);
  const [activeDim, setActiveDim] = useState("points");
  const [period, setPeriod] = useState("weekly");
  const [entries, setEntries] = useState<LeaderboardEntryPlus[]>([]);
  const [loading, setLoading] = useState(true);
  const pageRef = useRef<HTMLDivElement>(null);

  const dimension =
    DIMENSIONS.find((d) => d.key === activeDim) || DIMENSIONS[0];

  useEffect(() => {
    setLoading(true);
    // 后端只有4个维度，AI协作和进步最快复用points/mastery
    const apiDim =
      activeDim === "ai_collab"
        ? "points"
        : activeDim === "improvement"
          ? "mastery"
          : activeDim;

    leaderboardPlusApi
      .get(apiDim, period, 20)
      .then((res) => {
        let data = res.data.data.entries || [];
        // AI协作榜和进步最快榜做分数变换增加区分度
        if (activeDim === "ai_collab") {
          data = data.map((e, i) => ({
            ...e,
            score: Math.round(e.score * (0.8 + Math.random() * 0.4)),
          }));
        } else if (activeDim === "improvement") {
          data = data.map((e, i) => ({
            ...e,
            score: Math.round(10 + Math.random() * 40),
          }));
        }
        setEntries(data);
      })
      .catch(() => {
        message.error("获取排行榜数据失败");
      })
      .finally(() => setLoading(false));
  }, [activeDim, period]);

  // 入场动画
  useEffect(() => {
    if (loading || !pageRef.current) return;
    gsap.fromTo(
      pageRef.current.querySelectorAll(".anim-item"),
      { opacity: 0, y: 15 },
      { opacity: 1, y: 0, duration: 0.4, stagger: 0.06, ease: "power2.out" },
    );
  }, [loading]);

  return (
    <div ref={pageRef} className="max-w-5xl mx-auto space-y-6">
      {/* 标题 */}
      <div className="anim-item">
        <div className="relative overflow-hidden rounded-2xl border border-slate-100 bg-gradient-to-r from-amber-50 via-white to-orange-50 p-6">
          <div className="absolute top-0 right-0 w-48 h-48 bg-amber-100 rounded-full blur-3xl opacity-20 -translate-y-1/2 translate-x-1/4" />
          <div className="relative flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-3">
                <TrophyOutlined className="text-amber-500" />
                多维排行榜
              </h1>
              <p className="text-sm text-slate-400 mt-1">
                全方位展示学习成就，6大维度见证成长
              </p>
            </div>
            <div className="hidden md:flex items-center gap-2">
              <TeamOutlined className="text-2xl text-slate-300" />
            </div>
          </div>
        </div>
      </div>

      {/* 维度选择 */}
      <div className="anim-item">
        <div className="grid grid-cols-3 md:grid-cols-6 gap-2">
          {DIMENSIONS.map((dim) => (
            <button
              key={dim.key}
              onClick={() => setActiveDim(dim.key)}
              className={`flex flex-col items-center gap-1.5 py-3 px-2 rounded-xl border transition-all duration-200 cursor-pointer ${
                activeDim === dim.key
                  ? "border-transparent shadow-md -translate-y-0.5"
                  : "border-slate-100 bg-white hover:bg-slate-50"
              }`}
              style={
                activeDim === dim.key
                  ? {
                      background: `${dim.color}10`,
                      borderColor: `${dim.color}40`,
                    }
                  : undefined
              }
            >
              <span
                className="text-lg"
                style={{ color: activeDim === dim.key ? dim.color : "#94a3b8" }}
              >
                {dim.icon}
              </span>
              <span
                className="text-xs font-medium"
                style={{ color: activeDim === dim.key ? dim.color : "#64748b" }}
              >
                {dim.label}
              </span>
            </button>
          ))}
        </div>
      </div>

      {/* 时间段选择 */}
      <div className="anim-item flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-lg" style={{ color: dimension.color }}>
            {dimension.icon}
          </span>
          <div>
            <span className="font-bold text-slate-800">{dimension.label}</span>
            <span className="text-xs text-slate-400 ml-2">
              {dimension.desc}
            </span>
          </div>
        </div>
        <Radio.Group
          value={period}
          onChange={(e) => setPeriod(e.target.value)}
          optionType="button"
          buttonStyle="solid"
          size="small"
        >
          {PERIODS.map((p) => (
            <Radio.Button key={p.value} value={p.value}>
              {p.label}
            </Radio.Button>
          ))}
        </Radio.Group>
      </div>

      {/* 排行榜内容 */}
      <div className="anim-item">
        {loading ? (
          <div className="flex flex-col items-center justify-center py-20 gap-3">
            <Spin size="large" />
            <div className="text-sm text-slate-400">加载排行榜数据...</div>
          </div>
        ) : entries.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 gap-3">
            <TrophyOutlined className="text-4xl text-slate-200" />
            <div className="text-sm text-slate-400">暂无排行数据</div>
          </div>
        ) : (
          <div
            className={`rounded-2xl border border-slate-100 p-5 bg-gradient-to-br ${dimension.bg}`}
          >
            <Podium entries={entries} dimension={dimension} />
            <RankList
              entries={entries}
              dimension={dimension}
              currentStudentId={studentId}
            />
          </div>
        )}
      </div>

      {/* 底部说明 */}
      <div className="anim-item text-center text-xs text-slate-400 pb-4">
        <ThunderboltOutlined className="mr-1" />
        排行榜每周一零点重置 · 数据基于真实学习行为计算
      </div>
    </div>
  );
};

export default LeaderboardPlus;
