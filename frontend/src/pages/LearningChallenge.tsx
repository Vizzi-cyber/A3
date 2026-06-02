import React, { useEffect, useState, useRef } from "react";
import { Spin, Tag, Progress, Button, message } from "antd";
import {
  BookOutlined,
  TrophyOutlined,
  FireOutlined,
  CompassOutlined,
  CrownOutlined,
  ClockCircleOutlined,
  ThunderboltOutlined,
  StarOutlined,
  CheckCircleFilled,
  LockFilled,
  AimOutlined,
  RocketOutlined,
} from "@ant-design/icons";
import { useNavigate } from "react-router-dom";
import gsap from "gsap";
import { useAppStore } from "../store";
import { challengeApi } from "../services/api";
import type { ChallengeItem, ChallengeMapNode } from "../services/api";

// ==================== 世界观定义 ====================
const WORLD_LORE = {
  title: "数据结构大陆",
  subtitle: "一片由代码与算法构成的神秘大陆，唯有掌握核心知识的勇者才能穿越",
  regions: [
    {
      id: "array_village",
      name: "数组村庄",
      desc: "冒险的起点，这里居住着最基础的数据结构守护者",
      color: "#10b981",
      bg: "from-emerald-50 to-green-50",
      icon: "🏘️",
    },
    {
      id: "stack_canyon",
      name: "栈峡谷",
      desc: "深邃的峡谷中隐藏着后进先出的秘密",
      color: "#0ea5e9",
      bg: "from-sky-50 to-blue-50",
      icon: "🏔️",
    },
    {
      id: "tree_forest",
      name: "树之森林",
      desc: "参天大树构成的迷宫，每棵树都是一个知识分支",
      color: "#22c55e",
      bg: "from-green-50 to-lime-50",
      icon: "🌲",
    },
    {
      id: "graph_maze",
      name: "图论迷宫",
      desc: "错综复杂的路径网络，需要BFS和DFS才能找到出口",
      color: "#f59e0b",
      bg: "from-amber-50 to-yellow-50",
      icon: "🌀",
    },
    {
      id: "dp_temple",
      name: "动态规划神殿",
      desc: "大陆最深处的古老神殿，蕴含着最优解的力量",
      color: "#8b5cf6",
      bg: "from-purple-50 to-violet-50",
      icon: "🏛️",
    },
  ],
};

// ==================== 挑战图标 ====================
const ICON_MAP: Record<string, React.ReactNode> = {
  book: <BookOutlined />,
  trophy: <TrophyOutlined />,
  fire: <FireOutlined />,
  compass: <CompassOutlined />,
  crown: <CrownOutlined />,
  clock: <ClockCircleOutlined />,
  thunder: <ThunderboltOutlined />,
  star: <StarOutlined />,
};

const DIFFICULTY_COLOR: Record<number, string> = {
  1: "#10b981",
  2: "#0ea5e9",
  3: "#f59e0b",
  4: "#ef4444",
  5: "#8b5cf6",
};

const DIFFICULTY_LABEL: Record<number, string> = {
  1: "新手",
  2: "学徒",
  3: "精英",
  4: "大师",
  5: "传说",
};

// ==================== 探索地图 ====================
const ExploreMap: React.FC<{
  nodes: ChallengeMapNode[];
  activeIdx: number;
  onSelect: (_idx: number) => void;
  challenges: ChallengeItem[];
}> = ({ nodes, activeIdx, onSelect, challenges: _challenges }) => {
  const mapRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!mapRef.current) return;
    const paths = mapRef.current.querySelectorAll(".map-path");
    const nodeEls = mapRef.current.querySelectorAll(".map-node");

    gsap.fromTo(
      paths,
      { strokeDashoffset: 1000, strokeDasharray: "1000" },
      {
        strokeDashoffset: 0,
        duration: 1.5,
        stagger: 0.1,
        ease: "power2.out",
      },
    );

    gsap.fromTo(
      nodeEls,
      { scale: 0, opacity: 0 },
      {
        scale: 1,
        opacity: 1,
        duration: 0.4,
        stagger: 0.08,
        ease: "back.out(1.7)",
      },
    );
  }, [nodes]);

  if (nodes.length === 0) return null;

  // 计算地图布局 — 蛇形路径，使用百分比定位
  const cols = 4;
  const rows = Math.ceil(nodes.length / cols);
  const layoutNodes = nodes.map((n, i) => {
    const row = Math.floor(i / cols);
    const col = row % 2 === 0 ? i % cols : cols - 1 - (i % cols);
    return {
      ...n,
      xPercent: 12 + (col / (cols - 1)) * 76, // 12% ~ 88%
      yPercent: 20 + (row / Math.max(rows - 1, 1)) * 60, // 20% ~ 80%
    };
  });

  // 找到对应的challenge数据
  const findChallenge = (cid: string) => _challenges.find((c) => c.id === cid);

  return (
    <div
      ref={containerRef}
      className="relative rounded-lg border border-gray-200 overflow-hidden bg-gray-50"
      style={{ minHeight: 280 }}
    >
      {/* SVG连线 */}
      <svg
        ref={mapRef}
        className="absolute inset-0 w-full h-full pointer-events-none"
        style={{ zIndex: 1 }}
      >
        {layoutNodes.map((node, idx) => {
          if (idx === 0) return null;
          const prev = layoutNodes[idx - 1];
          const ch = findChallenge(node.challenge_id);
          const completed = ch?.completed;
          return (
            <line
              key={`path-${idx}`}
              className="map-path"
              x1={`${prev.xPercent}%`}
              y1={`${prev.yPercent}%`}
              x2={`${node.xPercent}%`}
              y2={`${node.yPercent}%`}
              stroke={completed ? "#10b981" : "#cbd5e1"}
              strokeWidth={3}
              strokeDasharray={completed ? "none" : "8 4"}
              strokeLinecap="round"
            />
          );
        })}
      </svg>

      {/* 节点 */}
      {layoutNodes.map((node, idx) => {
        const ch = findChallenge(node.challenge_id);
        const completed = ch?.completed;
        const isActive = idx === activeIdx;
        const isLocked =
          idx > 0 &&
          !findChallenge(layoutNodes[idx - 1].challenge_id)?.completed;
        const region = WORLD_LORE.regions[idx % WORLD_LORE.regions.length];

        return (
          <div
            key={node.node_id}
            className="map-node absolute cursor-pointer transition-all duration-300 -translate-x-1/2 -translate-y-1/2"
            style={{
              left: `${node.xPercent}%`,
              top: `${node.yPercent}%`,
              zIndex: isActive ? 10 : 2,
            }}
            onClick={() => !isLocked && onSelect(idx)}
          >
            {/* 节点光环 */}
            {isActive && (
              <div
                className="absolute inset-0 -m-3 rounded-full animate-pulse-soft"
                style={{ background: `${region.color}20` }}
              />
            )}

            {/* 节点主体 */}
            <div
              className={`w-14 h-14 rounded-full flex items-center justify-center text-white font-bold text-lg border-4 border-white shadow-lg transition-all duration-300 ${
                completed
                  ? "bg-emerald-500"
                  : isLocked
                    ? "bg-slate-300 cursor-not-allowed"
                    : isActive
                      ? "scale-110"
                      : "hover:scale-105"
              }`}
              style={
                !completed && !isLocked
                  ? { background: region.color }
                  : undefined
              }
            >
              {completed ? (
                <CheckCircleFilled />
              ) : isLocked ? (
                <LockFilled className="text-slate-400" />
              ) : (
                <span className="text-sm">{node.node_id}</span>
              )}
            </div>

            {/* 节点名称 */}
            <div
              className={`text-center mt-1.5 text-[11px] font-bold max-w-[80px] leading-tight ${
                completed
                  ? "text-emerald-600"
                  : isLocked
                    ? "text-slate-300"
                    : "text-slate-600"
              }`}
            >
              {node.name}
            </div>
          </div>
        );
      })}
    </div>
  );
};

// ==================== 挑战详情卡片 ====================
const ChallengeDetail: React.FC<{
  challenge: ChallengeItem;
  region: (typeof WORLD_LORE.regions)[number];
}> = ({ challenge, region }) => {
  const color = DIFFICULTY_COLOR[challenge.difficulty] || "#6366f1";

  return (
    <div
      className={`rounded-2xl border p-5 transition-all duration-300 ${
        challenge.completed
          ? "bg-emerald-50/50 border-emerald-200"
          : "bg-white border-slate-100 shadow-card hover:shadow-card-hover"
      }`}
    >
      {/* 头部 */}
      <div className="flex items-start gap-3 mb-3">
        <div
          className="w-10 h-10 rounded-lg flex items-center justify-center text-white text-lg shrink-0"
          style={{ background: challenge.completed ? "#10b981" : color }}
        >
          {challenge.completed ? (
            <CheckCircleFilled />
          ) : (
            ICON_MAP[challenge.icon] || <StarOutlined />
          )}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="font-semibold text-gray-800">
              {challenge.name}
            </span>
            <Tag
              color={DIFFICULTY_COLOR[challenge.difficulty]}
              className="text-xs"
            >
              {DIFFICULTY_LABEL[challenge.difficulty]}
            </Tag>
            <Tag className="text-xs">+{challenge.reward} 成长值</Tag>
          </div>
          <div className="text-xs text-gray-400 mt-1">
            {region.icon} {region.name}
          </div>
        </div>
      </div>

      {/* 叙事描述 */}
      <div className="bg-gray-50 rounded p-3 mb-3 text-sm text-gray-600">
        {challenge.description}
      </div>

      {/* 进度 */}
      <div className="flex items-center gap-3">
        <Progress
          percent={challenge.progress_pct}
          showInfo={false}
          strokeColor={challenge.completed ? "#10b981" : color}
          trailColor="#f1f5f9"
          size="small"
          className="flex-1 !m-0"
        />
        <span className="text-xs text-slate-500 font-mono whitespace-nowrap">
          {challenge.progress}/{challenge.target}
        </span>
      </div>
    </div>
  );
};

// ==================== 统计概览 ====================
const StatsBar: React.FC<{
  summary: {
    total: number;
    completed: number;
    total_reward: number;
    streak_days: number;
  };
}> = ({ summary }) => {
  const barRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (barRef.current) {
      gsap.fromTo(
        barRef.current.querySelectorAll(".stat-item"),
        { opacity: 0, y: 10 },
        { opacity: 1, y: 0, duration: 0.4, stagger: 0.1, ease: "power2.out" },
      );
    }
  }, []);

  return (
    <div ref={barRef} className="grid grid-cols-4 gap-3">
      {[
        {
          icon: <AimOutlined />,
          label: "已完成",
          value: summary.completed,
          color: "#10b981",
        },
        {
          icon: <CompassOutlined />,
          label: "进行中",
          value: summary.total - summary.completed,
          color: "#0ea5e9",
        },
        {
          icon: <ThunderboltOutlined />,
          label: "成长值",
          value: summary.total_reward,
          color: "#f59e0b",
        },
        {
          icon: <FireOutlined />,
          label: "连续天数",
          value: summary.streak_days,
          color: "#ef4444",
        },
      ].map((item) => (
        <div
          key={item.label}
          className="stat-item bg-white rounded-xl border border-slate-100 shadow-card p-3 text-center hover:shadow-card-hover transition-all duration-300 hover:-translate-y-0.5"
        >
          <div
            className="w-9 h-9 rounded-lg mx-auto mb-1.5 flex items-center justify-center text-white"
            style={{ background: item.color }}
          >
            {item.icon}
          </div>
          <div className="text-xl font-bold text-gray-800">{item.value}</div>
          <div className="text-xs text-gray-400">{item.label}</div>
        </div>
      ))}
    </div>
  );
};

// ==================== 学习挑战主页面 ====================
const LearningChallenge: React.FC = () => {
  const navigate = useNavigate();
  const studentId = useAppStore((s) => s.studentId);
  const [challenges, setChallenges] = useState<ChallengeItem[]>([]);
  const [mapNodes, setMapNodes] = useState<ChallengeMapNode[]>([]);
  const [summary, setSummary] = useState({
    total: 0,
    completed: 0,
    total_reward: 0,
    streak_days: 0,
  });
  const [loading, setLoading] = useState(true);
  const [activeNodeIdx, setActiveNodeIdx] = useState(0);
  const pageRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let ignore = false;
    setLoading(true);
    challengeApi
      .getChallenges(studentId)
      .then((res) => {
        if (ignore) return;
        const data = res.data.data;
        setChallenges(data.challenges);
        setMapNodes(data.map_nodes);
        setSummary(data.summary);
      })
      .catch(() => {
        if (!ignore) message.error("获取挑战数据失败");
      })
      .finally(() => {
        if (!ignore) setLoading(false);
      });
    return () => {
      ignore = true;
    };
  }, [studentId]);

  // 入场动画
  useEffect(() => {
    if (loading || !pageRef.current) return;
    gsap.fromTo(
      pageRef.current.querySelectorAll(".anim-item"),
      { opacity: 0, y: 15 },
      { opacity: 1, y: 0, duration: 0.45, stagger: 0.06, ease: "power2.out" },
    );
  }, [loading]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
        <Spin size="large" />
        <div className="text-sm text-slate-400">正在加载数据结构大陆...</div>
      </div>
    );
  }

  const activeChallenge = challenges[activeNodeIdx];
  const activeRegion =
    WORLD_LORE.regions[activeNodeIdx % WORLD_LORE.regions.length];

  return (
    <div ref={pageRef} className="max-w-6xl mx-auto space-y-6">
      {/* 世界观标题 */}
      <div className="anim-item">
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-800 flex items-center gap-3">
                <span className="text-3xl">🗺️</span>
                {WORLD_LORE.title}
              </h1>
              <p className="text-sm text-gray-400 mt-1.5 max-w-lg">
                {WORLD_LORE.subtitle}
              </p>
            </div>
            <div className="hidden md:flex items-center gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-800">
                  {summary.completed}
                </div>
                <div className="text-xs text-gray-400">已征服</div>
              </div>
              <div className="w-px h-10 bg-gray-200" />
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-800">
                  {summary.total}
                </div>
                <div className="text-xs text-gray-400">总挑战</div>
              </div>
              <Button
                icon={<TrophyOutlined />}
                onClick={() => navigate("/leaderboard")}
              >
                排行榜
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* 统计概览 */}
      <div className="anim-item">
        <StatsBar summary={summary} />
      </div>

      {/* 探索地图 */}
      <div className="anim-item">
        <div className="flex items-center gap-2 mb-3">
          <CompassOutlined className="text-indigo-500" />
          <span className="text-sm font-bold text-slate-700">探索地图</span>
          <Tag className="rounded-full border-0 bg-indigo-50 text-indigo-600 text-xs ml-auto">
            {Math.round((summary.completed / Math.max(summary.total, 1)) * 100)}
            % 已探索
          </Tag>
        </div>
        <ExploreMap
          nodes={mapNodes}
          activeIdx={activeNodeIdx}
          onSelect={setActiveNodeIdx}
          challenges={challenges}
        />
      </div>

      {/* 当前挑战详情 + 挑战列表 */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-5">
        {/* 左侧：当前挑战详情 */}
        <div className="lg:col-span-1 anim-item">
          {activeChallenge && (
            <div className="space-y-3 sticky top-4">
              {/* 区域信息 */}
              <div className="rounded-lg border border-gray-200 p-3 bg-gray-50">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-lg">{activeRegion.icon}</span>
                  <span className="font-semibold text-gray-800 text-sm">
                    {activeRegion.name}
                  </span>
                </div>
                <div className="text-xs text-gray-500">{activeRegion.desc}</div>
              </div>

              <ChallengeDetail
                challenge={activeChallenge}
                region={activeRegion}
              />
            </div>
          )}
        </div>

        {/* 右侧：全部挑战列表 */}
        <div className="lg:col-span-3 space-y-3">
          <div className="flex items-center gap-2 mb-1">
            <RocketOutlined className="text-indigo-500" />
            <span className="text-sm font-bold text-slate-700">全部挑战</span>
            <Tag className="rounded-full border-0 bg-slate-50 text-slate-500 text-xs ml-auto">
              {summary.total - summary.completed} 个可挑战
            </Tag>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {challenges.map((ch, idx) => {
              const region =
                WORLD_LORE.regions[idx % WORLD_LORE.regions.length];
              return (
                <div
                  key={ch.id}
                  className="anim-item cursor-pointer"
                  onClick={() => setActiveNodeIdx(idx)}
                >
                  <ChallengeDetail challenge={ch} region={region} />
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

export default LearningChallenge;
