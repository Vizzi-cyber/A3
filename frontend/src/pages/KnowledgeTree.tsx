import React, { useEffect, useState, useRef } from "react";
import { Spin, Tag, message } from "antd";
import {
  TrophyOutlined,
  StarOutlined,
  FireOutlined,
  RiseOutlined,
  ClockCircleOutlined,
  BookOutlined,
  ThunderboltOutlined,
  HeartOutlined,
  ExperimentOutlined,
} from "@ant-design/icons";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import gsap from "gsap";
import { useAppStore } from "../store";
import { knowledgeTreeApi } from "../services/api";
import type { KnowledgeTreeData } from "../services/api";
import { calcLevel, getLevelConfig, fetchLevelConfig } from "../utils/level";

// ==================== 树状态配置 ====================
const TREE_CONFIG: Record<
  string,
  {
    crown: string;
    crownDark: string;
    leaf: string;
    trunk: string;
    glow: string;
    particles: string;
    flowerColors: string[];
    fruitColors: string[];
  }
> = {
  seedling: {
    crown: "#bbf7d0",
    crownDark: "#86efac",
    leaf: "#4ade80",
    trunk: "#92400e",
    glow: "transparent",
    particles: "#86efac",
    flowerColors: [],
    fruitColors: [],
  },
  growing: {
    crown: "#86efac",
    crownDark: "#4ade80",
    leaf: "#22c55e",
    trunk: "#78350f",
    glow: "rgba(34,197,94,0.15)",
    particles: "#4ade80",
    flowerColors: [],
    fruitColors: [],
  },
  blooming: {
    crown: "#6ee7b7",
    crownDark: "#34d399",
    leaf: "#10b981",
    trunk: "#78350f",
    glow: "rgba(251,191,36,0.2)",
    particles: "#fcd34d",
    flowerColors: ["#fbbf24", "#f472b6", "#c084fc", "#fb923c"],
    fruitColors: [],
  },
  fruiting: {
    crown: "#34d399",
    crownDark: "#10b981",
    leaf: "#059669",
    trunk: "#78350f",
    glow: "rgba(249,115,22,0.2)",
    particles: "#fb923c",
    flowerColors: ["#fbbf24", "#f472b6"],
    fruitColors: ["#ef4444", "#f97316", "#dc2626"],
  },
  glowing: {
    crown: "#a78bfa",
    crownDark: "#8b5cf6",
    leaf: "#7c3aed",
    trunk: "#78350f",
    glow: "rgba(139,92,246,0.35)",
    particles: "#c4b5fd",
    flowerColors: ["#fbbf24", "#f472b6", "#c084fc", "#60a5fa"],
    fruitColors: ["#ef4444", "#f97316"],
  },
  wilting: {
    crown: "#fde68a",
    crownDark: "#fbbf24",
    leaf: "#d97706",
    trunk: "#92400e",
    glow: "rgba(245,158,11,0.15)",
    particles: "#fbbf24",
    flowerColors: [],
    fruitColors: [],
  },
};

// ==================== 粒子Canvas ====================
const ParticleCanvas: React.FC<{
  state: string;
  width: number;
  height: number;
}> = ({ state, width, height }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animRef = useRef<number>(0);
  const particlesRef = useRef<
    Array<{
      x: number;
      y: number;
      vx: number;
      vy: number;
      r: number;
      alpha: number;
      color: string;
      life: number;
      maxLife: number;
    }>
  >([]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || width === 0) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const dpr = window.devicePixelRatio || 1;
    canvas.width = width * dpr;
    canvas.height = height * dpr;
    ctx.scale(dpr, dpr);

    const cfg = TREE_CONFIG[state] || TREE_CONFIG.seedling;
    const colors = [cfg.particles, cfg.leaf, cfg.crown];
    const isGlowing = state === "glowing";
    const isWilting = state === "wilting";
    const maxParticles = isGlowing ? 35 : isWilting ? 12 : 20;

    const spawn = () => {
      if (particlesRef.current.length >= maxParticles) return;
      const color = colors[Math.floor(Math.random() * colors.length)];
      particlesRef.current.push({
        x: width * 0.2 + Math.random() * width * 0.6,
        y: height * 0.15 + Math.random() * height * 0.5,
        vx: (Math.random() - 0.5) * 0.4,
        vy: -0.2 - Math.random() * 0.5,
        r: 1.5 + Math.random() * 2.5,
        alpha: 0,
        color,
        life: 0,
        maxLife: 120 + Math.random() * 120,
      });
    };

    const animate = () => {
      ctx.clearRect(0, 0, width, height);
      if (Math.random() < 0.12) spawn();

      particlesRef.current = particlesRef.current.filter((p) => {
        p.life++;
        p.x += p.vx;
        p.y += p.vy;
        p.vx += (Math.random() - 0.5) * 0.05;

        const fadeIn = Math.min(p.life / 20, 1);
        const fadeOut = Math.max(1 - (p.life - p.maxLife + 30) / 30, 0);
        p.alpha = fadeIn * fadeOut * 0.7;

        if (p.life > p.maxLife) return false;

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = p.color;
        ctx.globalAlpha = p.alpha;
        ctx.fill();
        ctx.globalAlpha = 1;

        return true;
      });

      animRef.current = requestAnimationFrame(animate);
    };

    animate();
    return () => cancelAnimationFrame(animRef.current);
  }, [state, width, height]);

  return (
    <canvas
      ref={canvasRef}
      className="absolute inset-0 pointer-events-none z-20"
      style={{ width, height }}
    />
  );
};

// ==================== 增强SVG树 ====================
const TreeSVG: React.FC<{ state: string; growthValue: number }> = ({
  state,
  growthValue: _growthValue,
}) => {
  const cfg = TREE_CONFIG[state] || TREE_CONFIG.seedling;
  const isSeedling = state === "seedling";
  const isGlowing = state === "glowing";
  const isWilting = state === "wilting";
  const hasFlowers = ["blooming", "fruiting", "glowing"].includes(state);
  const hasFruits = ["fruiting", "glowing"].includes(state);
  const treeRef = useRef<SVGSVGElement>(null);

  // GSAP入场动画
  useEffect(() => {
    if (!treeRef.current) return;
    const tl = gsap.timeline();
    const trunk = treeRef.current.querySelector(".tree-trunk");
    const crown = treeRef.current.querySelectorAll(".tree-crown");
    const branches = treeRef.current.querySelectorAll(".tree-branch");

    gsap.set([trunk, ...crown, ...branches], { opacity: 0 });
    if (trunk) tl.to(trunk, { opacity: 1, duration: 0.6, ease: "power2.out" });
    branches.forEach((b) => {
      tl.to(b, { opacity: 1, duration: 0.3, ease: "power2.out" }, `-=${0.15}`);
    });
    crown.forEach((c) => {
      tl.fromTo(
        c,
        { opacity: 0, scale: 0.5, transformOrigin: "center center" },
        { opacity: 1, scale: 1, duration: 0.5, ease: "back.out(1.5)" },
        `-=${0.3}`,
      );
    });

    return () => {
      tl.kill();
    };
  }, [state]);

  // 呼吸动画
  useEffect(() => {
    if (!treeRef.current || isSeedling) return;
    const crownEls = treeRef.current.querySelectorAll(".tree-crown");
    const breathAnims = Array.from(crownEls).map((el) =>
      gsap.to(el, {
        scale: 1.03,
        duration: 2 + Math.random(),
        repeat: -1,
        yoyo: true,
        ease: "sine.inOut",
        transformOrigin: "center center",
      }),
    );
    return () => {
      breathAnims.forEach((a: gsap.core.Tween) => a.kill());
    };
  }, [state, isSeedling]);

  const crownPositions = [
    { cx: 100, cy: 85, r: 42 },
    { cx: 65, cy: 105, r: 32 },
    { cx: 135, cy: 105, r: 32 },
    { cx: 100, cy: 115, r: 36 },
    { cx: 78, cy: 72, r: 26 },
    { cx: 122, cy: 76, r: 24 },
    { cx: 100, cy: 60, r: 20 },
  ];

  return (
    <div className="relative flex items-center justify-center">
      {/* 发光背景 */}
      {cfg.glow !== "transparent" && (
        <div
          className="absolute w-72 h-72 rounded-full"
          style={{
            background: `radial-gradient(circle, ${cfg.glow} 0%, transparent 70%)`,
            animation: isGlowing
              ? "pulse-soft 2s ease-in-out infinite"
              : undefined,
          }}
        />
      )}

      <svg
        ref={treeRef}
        width="220"
        height="260"
        viewBox="0 0 220 260"
        className="relative z-10"
      >
        {/* 地面阴影 */}
        <ellipse
          cx="110"
          cy="245"
          rx="70"
          ry="10"
          fill="#e2e8f0"
          opacity="0.4"
        />
        <ellipse
          cx="110"
          cy="245"
          rx="50"
          ry="6"
          fill="#cbd5e1"
          opacity="0.3"
        />

        {/* 树干 */}
        <path
          className="tree-trunk"
          d={
            isSeedling
              ? "M105,240 L105,195 Q110,190 115,195 L115,240 Z"
              : "M102,240 L104,145 Q110,138 116,145 L118,240 Z"
          }
          fill={cfg.trunk}
        />
        {/* 树干纹理 */}
        {!isSeedling && (
          <>
            <line
              x1="108"
              y1="160"
              x2="109"
              y2="200"
              stroke="#5c3310"
              strokeWidth="1"
              opacity="0.3"
            />
            <line
              x1="112"
              y1="155"
              x2="113"
              y2="210"
              stroke="#5c3310"
              strokeWidth="0.8"
              opacity="0.2"
            />
          </>
        )}

        {/* 树枝 */}
        {!isSeedling && (
          <g className="tree-branch">
            <path
              d="M108,160 Q80,140 60,125"
              stroke={cfg.trunk}
              strokeWidth="5"
              fill="none"
              strokeLinecap="round"
            />
            <path
              d="M112,155 Q140,130 158,118"
              stroke={cfg.trunk}
              strokeWidth="5"
              fill="none"
              strokeLinecap="round"
            />
            <path
              d="M106,175 Q75,160 55,150"
              stroke={cfg.trunk}
              strokeWidth="3.5"
              fill="none"
              strokeLinecap="round"
            />
            <path
              d="M114,170 Q145,155 162,148"
              stroke={cfg.trunk}
              strokeWidth="3"
              fill="none"
              strokeLinecap="round"
            />
          </g>
        )}

        {/* 树冠 */}
        {isSeedling ? (
          <g className="tree-crown">
            <ellipse
              cx="95"
              cy="190"
              rx="14"
              ry="9"
              fill={cfg.leaf}
              transform="rotate(-35 95 190)"
              opacity="0.9"
            />
            <ellipse
              cx="125"
              cy="190"
              rx="14"
              ry="9"
              fill={cfg.leaf}
              transform="rotate(35 125 190)"
              opacity="0.9"
            />
            <ellipse cx="110" cy="185" rx="8" ry="12" fill={cfg.crown} />
            {/* 露珠 */}
            <circle cx="98" cy="186" r="1.5" fill="white" opacity="0.6" />
          </g>
        ) : (
          crownPositions.map((pos, i) => (
            <circle
              key={i}
              className="tree-crown"
              cx={pos.cx}
              cy={pos.cy}
              r={pos.r}
              fill={i % 2 === 0 ? cfg.crown : cfg.crownDark}
              opacity={0.85 - i * 0.03}
            />
          ))
        )}

        {/* 花朵 */}
        {hasFlowers &&
          [
            { x: 70, y: 92, r: 5 },
            { x: 125, y: 78, r: 4.5 },
            { x: 90, y: 68, r: 5 },
            { x: 140, y: 100, r: 4 },
            { x: 62, y: 112, r: 3.5 },
            { x: 110, y: 58, r: 4 },
            { x: 150, y: 115, r: 3 },
          ].map((f, i) => (
            <g key={`flower-${i}`} className="tree-crown">
              {/* 花瓣 */}
              {[0, 72, 144, 216, 288].map((angle) => (
                <ellipse
                  key={angle}
                  cx={f.x + Math.cos((angle * Math.PI) / 180) * f.r * 0.6}
                  cy={f.y + Math.sin((angle * Math.PI) / 180) * f.r * 0.6}
                  rx={f.r * 0.45}
                  ry={f.r * 0.25}
                  fill={cfg.flowerColors[i % cfg.flowerColors.length]}
                  opacity="0.8"
                  transform={`rotate(${angle} ${f.x} ${f.y})`}
                />
              ))}
              <circle cx={f.x} cy={f.y} r={f.r * 0.3} fill="#fbbf24" />
            </g>
          ))}

        {/* 果实 */}
        {hasFruits &&
          [
            { x: 78, y: 108, r: 7 },
            { x: 120, y: 92, r: 6 },
            { x: 100, y: 120, r: 7 },
            { x: 142, y: 118, r: 5 },
          ].map((fr, i) => (
            <g key={`fruit-${i}`} className="tree-crown">
              <circle
                cx={fr.x}
                cy={fr.y}
                r={fr.r}
                fill={cfg.fruitColors[i % cfg.fruitColors.length]}
              />
              {/* 果实高光 */}
              <circle
                cx={fr.x - fr.r * 0.25}
                cy={fr.y - fr.r * 0.25}
                r={fr.r * 0.3}
                fill="white"
                opacity="0.3"
              />
              {/* 果柄 */}
              <line
                x1={fr.x}
                y1={fr.y - fr.r}
                x2={fr.x + 2}
                y2={fr.y - fr.r - 5}
                stroke="#78350f"
                strokeWidth="1.5"
                strokeLinecap="round"
              />
            </g>
          ))}

        {/* 枯叶飘落 */}
        {isWilting && (
          <g>
            {[
              { x: 50, delay: 0, dur: 4 },
              { x: 90, delay: 1.2, dur: 3.5 },
              { x: 140, delay: 0.6, dur: 4.2 },
              { x: 160, delay: 2, dur: 3.8 },
            ].map((leaf, i) => (
              <ellipse
                key={`fall-leaf-${i}`}
                cx={leaf.x}
                cy={180}
                rx="4"
                ry="2.5"
                fill={i % 2 === 0 ? "#d97706" : "#b45309"}
                opacity="0.7"
                transform={`rotate(${20 + i * 15} ${leaf.x} 180)`}
              >
                <animate
                  attributeName="cy"
                  values="180;250"
                  dur={`${leaf.dur}s`}
                  begin={`${leaf.delay}s`}
                  repeatCount="indefinite"
                />
                <animate
                  attributeName="opacity"
                  values="0.7;0"
                  dur={`${leaf.dur}s`}
                  begin={`${leaf.delay}s`}
                  repeatCount="indefinite"
                />
                <animateTransform
                  attributeName="transform"
                  type="rotate"
                  values={`0 ${leaf.x} 180;360 ${leaf.x} 250`}
                  dur={`${leaf.dur}s`}
                  begin={`${leaf.delay}s`}
                  repeatCount="indefinite"
                />
              </ellipse>
            ))}
          </g>
        )}

        {/* 发光光点 */}
        {isGlowing && (
          <g>
            {[
              { cx: 55, cy: 75, r: 2.5, dur: "2s" },
              { cx: 160, cy: 85, r: 2, dur: "2.5s" },
              { cx: 85, cy: 55, r: 2, dur: "1.8s" },
              { cx: 130, cy: 60, r: 2.5, dur: "2.2s" },
              { cx: 45, cy: 110, r: 1.5, dur: "3s" },
              { cx: 170, cy: 115, r: 1.5, dur: "2.8s" },
            ].map((dot, i) => (
              <circle
                key={`glow-${i}`}
                cx={dot.cx}
                cy={dot.cy}
                r={dot.r}
                fill={cfg.flowerColors[i % cfg.flowerColors.length]}
              >
                <animate
                  attributeName="opacity"
                  values="0.2;1;0.2"
                  dur={dot.dur}
                  repeatCount="indefinite"
                />
                <animate
                  attributeName="r"
                  values={`${dot.r * 0.5};${dot.r * 1.3};${dot.r * 0.5}`}
                  dur={dot.dur}
                  repeatCount="indefinite"
                />
              </circle>
            ))}
          </g>
        )}
      </svg>
    </div>
  );
};

// ==================== AI成长评语 ====================
const AIGrowthComment: React.FC<{ data: KnowledgeTreeData }> = ({ data }) => {
  const comments: string[] = [];

  if (data.streak_days >= 7) {
    comments.push(
      `连续学习${data.streak_days}天，坚持的力量让知识树熠熠生辉！`,
    );
  } else if (data.streak_days >= 3) {
    comments.push(
      `已连续学习${data.streak_days}天，再坚持一下知识树就要开花了！`,
    );
  }

  if (data.mastery_rate >= 80) {
    comments.push(
      `知识掌握率${data.mastery_rate}%，你已经是这片知识森林的强者。`,
    );
  } else if (data.mastery_rate >= 50) {
    comments.push(`掌握率${data.mastery_rate}%，知识树正在茁壮成长中。`);
  }

  if (data.trend_factor > 0.3) {
    comments.push("学习趋势强劲上升，成长速度令人瞩目！");
  } else if (data.trend_factor < -0.3) {
    comments.push("最近学习状态有所下滑，建议回顾薄弱知识点。");
  }

  if (data.avg_score >= 85) {
    comments.push(`测验均分${data.avg_score}，果实累累指日可待。`);
  }

  if (comments.length === 0) {
    comments.push("每一次学习都在为知识树注入养分，继续加油！");
  }

  return (
    <div className="bg-gradient-to-r from-indigo-50 via-white to-purple-50 rounded-2xl border border-indigo-100 p-5">
      <div className="flex items-start gap-3">
        <div className="w-9 h-9 rounded-xl bg-indigo-500 flex items-center justify-center text-white shrink-0">
          <ExperimentOutlined />
        </div>
        <div>
          <div className="text-sm font-bold text-indigo-700 mb-1">
            AI 成长评语
          </div>
          <div className="space-y-1">
            {comments.map((c, i) => (
              <div key={i} className="text-sm text-slate-600 leading-relaxed">
                {c}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

// ==================== 统计卡片 ====================
const StatCard: React.FC<{
  icon: React.ReactNode;
  label: string;
  value: string | number;
  color: string;
  sub?: string;
}> = ({ icon, label, value, color, sub }) => (
  <div className="bg-white rounded-xl border border-slate-100 p-4 shadow-card hover:shadow-card-hover transition-all duration-300 hover:-translate-y-0.5">
    <div className="flex items-center gap-3">
      <div
        className="w-10 h-10 rounded-xl flex items-center justify-center text-white text-lg"
        style={{ background: `linear-gradient(135deg, ${color}, ${color}dd)` }}
      >
        {icon}
      </div>
      <div>
        <div className="text-xs text-slate-400 font-medium">{label}</div>
        <div className="text-xl font-bold text-slate-800">{value}</div>
        {sub && <div className="text-xs text-slate-400 mt-0.5">{sub}</div>}
      </div>
    </div>
  </div>
);

// ==================== 成长日志 ====================
const GrowthLogItem: React.FC<{
  log: { date: string; type: string; message: string; icon: string };
}> = ({ log }) => {
  const iconMap: Record<string, React.ReactNode> = {
    trophy: <TrophyOutlined className="text-amber-500" />,
    star: <StarOutlined className="text-indigo-500" />,
    fire: <FireOutlined className="text-red-500" />,
    heart: <HeartOutlined className="text-pink-500" />,
  };
  return (
    <div className="flex items-start gap-3 py-2.5 group">
      <div className="w-9 h-9 rounded-xl bg-slate-50 flex items-center justify-center text-sm border border-slate-100 group-hover:border-indigo-200 transition-colors">
        {iconMap[log.icon] || <StarOutlined className="text-slate-400" />}
      </div>
      <div className="flex-1 min-w-0">
        <div className="text-sm text-slate-700 font-medium">{log.message}</div>
        <div className="text-xs text-slate-400 mt-0.5">{log.date}</div>
      </div>
    </div>
  );
};

// ==================== 等级进度条 ====================
const LevelProgress: React.FC<{ level: number; totalPoints: number }> = ({
  level,
  totalPoints,
}) => {
  const lvInfo = calcLevel(totalPoints);
  const cfg = getLevelConfig();
  const barRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (barRef.current) {
      gsap.fromTo(
        barRef.current,
        { width: "0%" },
        { width: `${lvInfo.progress_pct}%`, duration: 1.2, ease: "power2.out" },
      );
    }
  }, [lvInfo.progress_pct]);

  return (
    <div className="bg-white rounded-2xl border border-slate-100 p-5 shadow-card">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-amber-100 flex items-center justify-center">
            <ThunderboltOutlined className="text-amber-600" />
          </div>
          <span className="font-bold text-slate-800">
            {lvInfo.level_name} Lv.{level}
          </span>
        </div>
        <span className="text-xs text-slate-400 bg-slate-50 px-2 py-1 rounded-full">
          {totalPoints} 积分
        </span>
      </div>
      <div className="h-3.5 bg-slate-100 rounded-full overflow-hidden">
        <div
          ref={barRef}
          className="h-full rounded-full"
          style={{
            background:
              "linear-gradient(90deg, #6366f1, #8b5cf6, #a78bfa, #c4b5fd)",
            boxShadow: "0 0 8px rgba(99,102,241,0.4)",
          }}
        />
      </div>
      <div className="flex justify-between mt-2">
        <span className="text-xs text-slate-400 font-medium">Lv.{level}</span>
        <span className="text-xs text-indigo-500 font-bold">
          {lvInfo.current_xp}/{lvInfo.xp_per_level}
        </span>
        <span className="text-xs text-slate-400 font-medium">
          {level < cfg.max_level ? `Lv.${level + 1}` : "MAX"}
        </span>
      </div>
    </div>
  );
};

// ==================== 知识树主页面 ====================
const KnowledgeTree: React.FC = () => {
  const studentId = useAppStore((s) => s.studentId);
  const [data, setData] = useState<KnowledgeTreeData | null>(null);
  const [loading, setLoading] = useState(true);
  const containerRef = useRef<HTMLDivElement>(null);
  const treeContainerRef = useRef<HTMLDivElement>(null);
  const [canvasSize, setCanvasSize] = useState({ w: 0, h: 0 });

  useEffect(() => {
    let ignore = false;
    setLoading(true);
    fetchLevelConfig().catch(() => {});
    knowledgeTreeApi
      .getTree(studentId)
      .then((res) => {
        if (!ignore) setData(res.data.data);
      })
      .catch(() => {
        if (!ignore) message.error("获取知识树数据失败");
      })
      .finally(() => {
        if (!ignore) setLoading(false);
      });
    return () => {
      ignore = true;
    };
  }, [studentId]);

  // 测量树容器尺寸给粒子Canvas
  useEffect(() => {
    if (!treeContainerRef.current) return;
    const observer = new ResizeObserver((entries) => {
      for (const entry of entries) {
        setCanvasSize({
          w: entry.contentRect.width,
          h: entry.contentRect.height,
        });
      }
    });
    observer.observe(treeContainerRef.current);
    return () => observer.disconnect();
  }, [data]);

  // 页面入场动画
  useEffect(() => {
    if (!containerRef.current || loading) return;
    const cards = containerRef.current.querySelectorAll(".anim-card");
    gsap.fromTo(
      cards,
      { opacity: 0, y: 20 },
      {
        opacity: 1,
        y: 0,
        duration: 0.5,
        stagger: 0.08,
        ease: "power2.out",
      },
    );
  }, [loading, data]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
        <Spin size="large" />
        <div className="text-sm text-slate-400">正在唤醒知识树...</div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="text-center py-20">
        <div className="text-6xl mb-4">🌱</div>
        <div className="text-lg text-slate-500 font-medium">暂无学习数据</div>
        <div className="text-sm text-slate-400 mt-1">
          开始学习后，知识树将会在这里成长
        </div>
      </div>
    );
  }

  const stateLabel: Record<string, string> = {
    seedling: "种子期",
    growing: "成长期",
    blooming: "绽放期",
    fruiting: "收获期",
    glowing: "闪耀期",
    wilting: "需要关注",
  };

  const stateEmoji: Record<string, string> = {
    seedling: "🌱",
    growing: "🌿",
    blooming: "🌸",
    fruiting: "🍎",
    glowing: "✨",
    wilting: "🍂",
  };

  const stateColor: Record<string, string> = {
    seedling: "#86efac",
    growing: "#4ade80",
    blooming: "#fbbf24",
    fruiting: "#f97316",
    glowing: "#a78bfa",
    wilting: "#fbbf24",
  };

  return (
    <div ref={containerRef} className="max-w-6xl mx-auto space-y-6">
      {/* 页面标题 */}
      <div className="anim-card flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-3">
            <span className="text-3xl">
              {stateEmoji[data.tree_state] || "🌱"}
            </span>
            知识树
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            每一次学习都在浇灌你的知识之树 · 见证成长的力量
          </p>
        </div>
        <Tag
          className="rounded-full px-4 py-1.5 text-sm font-bold border-0"
          style={{
            background: `${stateColor[data.tree_state]}20`,
            color: stateColor[data.tree_state],
          }}
        >
          {stateLabel[data.tree_state] || data.tree_state}
        </Tag>
      </div>

      {/* 主区域 */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 左侧：知识树 */}
        <div className="lg:col-span-1 space-y-4">
          <div
            ref={treeContainerRef}
            className="anim-card bg-white rounded-2xl border border-slate-100 shadow-card p-6 text-center relative overflow-hidden"
            style={{ minHeight: 360 }}
          >
            {/* 背景网格 */}
            <div
              className="absolute inset-0 opacity-[0.03]"
              style={{
                backgroundImage:
                  "radial-gradient(circle, #6366f1 1px, transparent 1px)",
                backgroundSize: "20px 20px",
              }}
            />

            {/* 粒子层 */}
            {canvasSize.w > 0 && (
              <ParticleCanvas
                state={data.tree_state}
                width={canvasSize.w}
                height={canvasSize.h}
              />
            )}

            {/* 树 */}
            <TreeSVG state={data.tree_state} growthValue={data.growth_value} />

            {/* 树状态信息 */}
            <div className="mt-4 relative z-10">
              <div className="text-lg font-bold text-slate-800">
                {data.tree_label}
              </div>
              <div className="flex items-center justify-center gap-4 mt-2">
                <div className="text-center">
                  <div className="text-xs text-slate-400">成长值</div>
                  <div className="text-lg font-bold text-indigo-600">
                    {data.growth_value}
                  </div>
                </div>
                <div className="w-px h-8 bg-slate-200" />
                <div className="text-center">
                  <div className="text-xs text-slate-400">等级</div>
                  <div className="text-lg font-bold text-amber-600">
                    Lv.{data.level}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* 等级进度 */}
          <div className="anim-card">
            <LevelProgress level={data.level} totalPoints={data.total_points} />
          </div>
        </div>

        {/* 右侧：数据面板 */}
        <div className="lg:col-span-2 space-y-4">
          {/* 统计卡片 */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <div className="anim-card">
              <StatCard
                icon={<FireOutlined />}
                label="连续学习"
                value={`${data.streak_days}天`}
                color="#ef4444"
              />
            </div>
            <div className="anim-card">
              <StatCard
                icon={<BookOutlined />}
                label="掌握知识点"
                value={data.completed_kps}
                color="#6366f1"
                sub={`/ ${data.touched_kps} 已学习`}
              />
            </div>
            <div className="anim-card">
              <StatCard
                icon={<RiseOutlined />}
                label="掌握率"
                value={`${data.mastery_rate}%`}
                color="#10b981"
              />
            </div>
            <div className="anim-card">
              <StatCard
                icon={<ClockCircleOutlined />}
                label="学习时长"
                value={`${data.total_hours}h`}
                color="#0ea5e9"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <div className="anim-card">
              <StatCard
                icon={<TrophyOutlined />}
                label="测验次数"
                value={data.total_quizzes}
                color="#f59e0b"
                sub={`均分 ${data.avg_score}`}
              />
            </div>
            <div className="anim-card">
              <StatCard
                icon={<StarOutlined />}
                label="解锁成就"
                value={data.achievements}
                color="#8b5cf6"
              />
            </div>
            <div className="anim-card">
              <StatCard
                icon={<ThunderboltOutlined />}
                label="总积分"
                value={data.total_points}
                color="#f97316"
              />
            </div>
            <div className="anim-card">
              <StatCard
                icon={<RiseOutlined />}
                label="趋势因子"
                value={data.trend_factor.toFixed(2)}
                color={data.trend_factor >= 0 ? "#10b981" : "#ef4444"}
                sub={data.trend_factor >= 0 ? "上升趋势" : "需要关注"}
              />
            </div>
          </div>

          {/* AI成长评语 */}
          <div className="anim-card">
            <AIGrowthComment data={data} />
          </div>

          {/* 学习趋势图 */}
          <div className="anim-card bg-white rounded-2xl border border-slate-100 shadow-card p-5">
            <div className="flex items-center gap-2 mb-4">
              <RiseOutlined className="text-indigo-500" />
              <span className="text-sm font-bold text-slate-700">
                近7天学习趋势
              </span>
            </div>
            <ResponsiveContainer width="100%" height={200}>
              <AreaChart data={data.daily_trend}>
                <defs>
                  <linearGradient id="colorRecords" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.2} />
                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="colorScore" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.2} />
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis
                  dataKey="date"
                  tick={{ fontSize: 11, fill: "#94a3b8" }}
                  axisLine={false}
                  tickLine={false}
                  tickFormatter={(v: string) => v.slice(5)}
                />
                <YAxis
                  tick={{ fontSize: 11, fill: "#94a3b8" }}
                  axisLine={false}
                  tickLine={false}
                />
                <Tooltip
                  contentStyle={{
                    borderRadius: "12px",
                    border: "1px solid #e2e8f0",
                    boxShadow: "0 4px 12px rgba(0,0,0,0.08)",
                    fontSize: "12px",
                  }}
                  formatter={(value: number, name: string) => [
                    value,
                    name === "records" ? "学习次数" : "平均分",
                  ]}
                  labelFormatter={(label: string) => `日期: ${label}`}
                />
                <Area
                  type="monotone"
                  dataKey="records"
                  stroke="#6366f1"
                  strokeWidth={2.5}
                  fill="url(#colorRecords)"
                  name="records"
                  dot={{ r: 3, fill: "#6366f1" }}
                />
                <Area
                  type="monotone"
                  dataKey="score"
                  stroke="#10b981"
                  strokeWidth={2.5}
                  fill="url(#colorScore)"
                  name="score"
                  dot={{ r: 3, fill: "#10b981" }}
                />
              </AreaChart>
            </ResponsiveContainer>
            <div className="flex justify-center gap-6 mt-3">
              <div className="flex items-center gap-1.5 text-xs text-slate-500">
                <div className="w-3 h-1 bg-indigo-500 rounded" />
                学习次数
              </div>
              <div className="flex items-center gap-1.5 text-xs text-slate-500">
                <div className="w-3 h-1 bg-emerald-500 rounded" />
                平均分
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 成长日志 */}
      {data.growth_logs.length > 0 && (
        <div className="anim-card bg-white rounded-2xl border border-slate-100 shadow-card p-5">
          <div className="flex items-center gap-2 mb-4">
            <StarOutlined className="text-amber-500" />
            <span className="text-sm font-bold text-slate-700">成长里程碑</span>
            <Tag className="rounded-full border-0 bg-amber-50 text-amber-600 text-xs ml-auto">
              {data.growth_logs.length} 条记录
            </Tag>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-x-6">
            {data.growth_logs.map((log, idx) => (
              <GrowthLogItem key={`${log.date}-${idx}`} log={log} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default KnowledgeTree;
