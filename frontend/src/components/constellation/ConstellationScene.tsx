/**
 * 光遇星盘 · 数据流场景（ConstellationScene）
 * 把系统真实学习数据做成"星座星盘"：
 *   - 中心：学生核心数据（本周学习/掌握/成就）
 *   - 外围 6 个星座节点（学习路径/每日练习/课程/知识库/收藏/荣誉），发光线连成星座图案
 *   - 数据流：沿连线的流动光点 + 背景星尘
 *   - hover 节点：放大发光 + 浮层显示真实数据；点击进入功能页
 * 数据来源：后端真实接口（dashboard/learning-path/daily-quiz/gamification）
 */
import React, { useCallback, useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../services/api";

interface ConstellationData {
  weeklyHours: number;
  totalHours: number;
  masteredKps: number;
  achievements: number;
  favorites: number;
  streakDays: number;
  pathProgress: number;
  pathNodes: number;
  quizTotal: number;
  quizCovered: number;
  points: number;
  rank: number;
}

const EMPTY: ConstellationData = {
  weeklyHours: 0, totalHours: 0, masteredKps: 0, achievements: 0, favorites: 0,
  streakDays: 0, pathProgress: 0, pathNodes: 0, quizTotal: 0, quizCovered: 0,
  points: 0, rank: 0,
};

interface NodeDef {
  id: string;
  label: string;
  icon: string;
  color: string;
  route?: string;
  /** 相对中心的角度（度）与半径 */
  angle: number;
  radius: number;
  /** 浮层内容（渲染真实数据） */
  renderInfo: (d: ConstellationData) => string;
}

interface ConstellationSceneProps {
  studentId?: string;
  className?: string;
}

const ConstellationScene: React.FC<ConstellationSceneProps> = ({ studentId = "student_001", className = "" }) => {
  const navigate = useNavigate();
  const [data, setData] = useState<ConstellationData>(EMPTY);
  const [hovered, setHovered] = useState<string | null>(null);
  const [loaded, setLoaded] = useState(false);
  const wrapRef = useRef<HTMLDivElement>(null);

  // ---------- 拉取真实数据 ----------
  useEffect(() => {
    let alive = true;
    const load = async () => {
      try {
        const [dash, path, quiz, gam] = await Promise.allSettled([
          api.get(`/dashboard/${studentId}/summary`),
          api.get(`/learning-path/${studentId}/current`),
          api.get("/daily-quiz/stats"),
          api.get(`/gamification/${studentId}/points`),
        ]);
        const val = (r: PromiseSettledResult<any>) => (r.status === "fulfilled" ? r.value?.data : null);
        const dashData = val(dash);
        const pathData = val(path);
        const quizData = val(quiz);
        const gamData = val(gam);

        const stats = dashData?.stats ?? {};
        const pathD = pathData?.data ?? pathData ?? {};
        const quizD = quizData?.data ?? quizData ?? {};
        const gamD = gamData?.data ?? gamData ?? {};

        if (!alive) return;
        setData({
          weeklyHours: stats.weekly_hours ?? 0,
          totalHours: stats.total_hours ?? 0,
          masteredKps: stats.mastered_kps ?? 0,
          achievements: stats.achievements ?? 0,
          favorites: stats.favorites ?? 0,
          streakDays: stats.streak_days ?? 0,
          pathProgress: pathD.progress ?? 0,
          pathNodes: pathD.nodes?.length ?? pathD.total_nodes ?? 0,
          quizTotal: quizD.total_questions ?? 0,
          quizCovered: quizD.knowledge_points_covered ?? 0,
          points: gamD.points ?? gamD.total_points ?? 0,
          rank: gamD.rank ?? 0,
        });
      } catch {
        // 数据拉取失败保持占位
      } finally {
        if (alive) setLoaded(true);
      }
    };
    load();
    return () => { alive = false; };
  }, [studentId]);

  // ---------- 节点定义（星座图案：中心 + 6 节点） ----------
  const nodes: NodeDef[] = [
    {
      id: "path", label: "学习路径", icon: "🧭", color: "#6366f1", route: "/learning-path",
      angle: 90, radius: 130,
      renderInfo: (d) => `${d.pathNodes} 个节点 · 进度 ${Math.round(d.pathProgress)}%\n当前目标持续探索中`,
    },
    {
      id: "quiz", label: "每日练习", icon: "✏️", color: "#0ea5e9", route: "/learning-path",
      angle: 30, radius: 155,
      renderInfo: (d) => `已练 ${d.quizTotal} 题 · 覆盖 ${d.quizCovered} 个知识点`,
    },
    {
      id: "courses", label: "学科课程", icon: "📖", color: "#22d3ee", route: "/resources",
      angle: -30, radius: 160,
      renderInfo: () => `C语言 16 点 · 电路 5+仿真\nSTM32 14 点 + 7 实验`,
    },
    {
      id: "circuit", label: "电路仿真", icon: "⚡", color: "#f97316", route: "/circuit-simulator",
      angle: -90, radius: 130,
      renderInfo: () => "MNA 虚拟实验\n电路故障诊断与仿真",
    },
    {
      id: "favorites", label: "收藏夹", icon: "⭐", color: "#fbbf24", route: "/personal",
      angle: -150, radius: 150,
      renderInfo: (d) => `${d.favorites} 条收藏资源\n随时回顾学习`,
    },
    {
      id: "honor", label: "成就殿堂", icon: "🏆", color: "#f59e0b", route: "/leaderboard",
      angle: 150, radius: 145,
      renderInfo: (d) => `${d.achievements} 项成就 · ${d.points} 积分\n连续打卡 ${d.streakDays} 天`,
    },
  ];

  // 中心节点（核心数据）
  const center = {
    label: "本周学习",
    info: (d: ConstellationData) =>
      `${d.weeklyHours} h 本周 · 累计 ${d.totalHours} h\n掌握 ${d.masteredKps} 个知识点`,
  };

  // ---------- 节点屏幕坐标 ----------
  const toXY = (angleDeg: number, radius: number) => {
    const rad = (angleDeg * Math.PI) / 180;
    return { x: Math.cos(rad) * radius, y: -Math.sin(rad) * radius };
  };

  const nodeXY = useCallback((n: NodeDef) => toXY(n.angle, n.radius), []);

  // ---------- 数据流光点（沿连线流动） ----------
  const flowRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const el = flowRef.current;
    if (!el) return;
    // 用 CSS 动画的光点群（每 600ms 生成一个沿连线移动的光点）
    let id = 0;
    const timer = setInterval(() => {
      if (id > 14) { id = 0; }
      const dot = document.createElement("div");
      dot.className = "flow-dot";
      dot.style.setProperty("--i", String(id % 5));
      el.appendChild(dot);
      setTimeout(() => dot.remove(), 2600);
      id++;
    }, 420);
    return () => clearInterval(timer);
  }, []);

  // 星盘缓慢旋转
  const [spin, setSpin] = useState(false);
  useEffect(() => {
    const t = setTimeout(() => setSpin(true), 300);
    return () => clearTimeout(t);
  }, []);

  const dim = 560; // 星盘尺寸

  return (
    <div ref={wrapRef} className={`relative w-full h-[calc(100vh-140px)] min-h-[560px] rounded-2xl overflow-hidden border border-slate-800/40 bg-[#070b1c] ${className}`}>
      {/* 深空背景 */}
      <div className="absolute inset-0 bg-gradient-to-br from-[#070b1c] via-[#0c1230] to-[#0a0e24]" />
      {/* 星尘粒子 */}
      <div className="absolute inset-0" style={{
        backgroundImage:
          "radial-gradient(1px 1px at 20% 30%, rgba(255,255,255,0.5), transparent), " +
          "radial-gradient(1px 1px at 70% 20%, rgba(147,197,253,0.6), transparent), " +
          "radial-gradient(1.5px 1.5px at 40% 70%, rgba(255,255,255,0.4), transparent), " +
          "radial-gradient(1px 1px at 85% 60%, rgba(147,197,253,0.5), transparent), " +
          "radial-gradient(1px 1px at 10% 85%, rgba(255,255,255,0.35), transparent), " +
          "radial-gradient(1.5px 1.5px at 55% 45%, rgba(165,180,252,0.5), transparent), " +
          "radial-gradient(1px 1px at 90% 85%, rgba(255,255,255,0.4), transparent)",
      }} />

      {/* ===== 星盘舞台（居中） ===== */}
      <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2">
        <div
          className="relative transition-transform duration-[3000ms] ease-out"
          style={{ width: dim, height: dim, transform: spin ? "rotate(0deg)" : "rotate(8deg)" }}
        >
          {/* 星座连线（SVG） */}
          <svg width={dim} height={dim} className="absolute inset-0 pointer-events-none">
            <defs>
              <linearGradient id="const-line" x1="0" y1="0" x2="1" y2="1">
                <stop offset="0%" stopColor="#6366f1" stopOpacity="0.7" />
                <stop offset="100%" stopColor="#22d3ee" stopOpacity="0.7" />
              </linearGradient>
            </defs>
            {/* 中心到各节点 */}
            {nodes.map((n) => {
              const p = nodeXY(n);
              return (
                <line
                  key={`c-${n.id}`}
                  x1={dim / 2} y1={dim / 2}
                  x2={dim / 2 + p.x} y2={dim / 2 + p.y}
                  stroke="url(#const-line)"
                  strokeWidth={1.5}
                  opacity={hovered === n.id ? 1 : 0.55}
                  style={{ transition: "opacity 0.3s" }}
                />
              );
            })}
            {/* 节点间连线（星座多边形） */}
            {nodes.map((n, i) => {
              const n1 = nodeXY(n);
              const n2 = nodeXY(nodes[(i + 1) % nodes.length]);
              return (
                <line
                  key={`p-${n.id}`}
                  x1={dim / 2 + n1.x} y1={dim / 2 + n1.y}
                  x2={dim / 2 + n2.x} y2={dim / 2 + n2.y}
                  stroke="#94a3b8"
                  strokeWidth={0.8}
                  opacity={0.25}
                  strokeDasharray="4 6"
                />
              );
            })}
          </svg>

          {/* 数据流光点容器（CSS 动画） */}
          <div ref={flowRef} className="absolute inset-0 pointer-events-none overflow-hidden" />

          {/* 中心节点（核心数据） */}
          <div
            className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-10"
            onMouseEnter={() => setHovered("__center")}
            onMouseLeave={() => setHovered(null)}
          >
            <div
              className="relative flex flex-col items-center justify-center rounded-full text-center cursor-pointer transition-all duration-300"
              style={{
                width: 132, height: 132,
                background: "radial-gradient(circle at 35% 30%, rgba(99,102,241,0.5), rgba(34,211,238,0.12) 65%, transparent)",
                border: "2px solid rgba(129,140,248,0.7)",
                boxShadow: hovered === "__center"
                  ? "0 0 46px rgba(99,102,241,0.8), inset 0 0 22px rgba(129,140,248,0.4)"
                  : "0 0 22px rgba(99,102,241,0.5), inset 0 0 12px rgba(129,140,248,0.2)",
              }}
            >
              <div className="text-[10px] tracking-widest text-indigo-200/80 uppercase">{center.label}</div>
              <div className="text-2xl font-bold text-white mt-1">{data.weeklyHours}h</div>
              <div className="text-[10px] text-slate-300/80">掌握 {data.masteredKps} 知识点</div>
              {hovered === "__center" && (
                <div className="absolute top-full mt-3 w-44 rounded-xl p-3 text-left z-20" style={{ background: "rgba(15,23,42,0.95)", border: "1px solid rgba(129,140,248,0.5)" }}>
                  <div className="text-white text-[11px] leading-relaxed whitespace-pre-line">{center.info(data)}</div>
                </div>
              )}
            </div>
          </div>

          {/* 星座节点 */}
          {nodes.map((n) => {
            const p = nodeXY(n);
            const active = hovered === n.id;
            return (
              <div
                key={n.id}
                className="absolute z-10 -translate-x-1/2 -translate-y-1/2 cursor-pointer"
                style={{ left: dim / 2 + p.x, top: dim / 2 + p.y }}
                onMouseEnter={() => setHovered(n.id)}
                onMouseLeave={() => setHovered((h) => (h === n.id ? null : h))}
                onClick={() => { if (n.route) navigate(n.route); }}
              >
                <div
                  className="relative flex items-center justify-center rounded-full transition-all duration-300"
                  style={{
                    width: 64, height: 64,
                    background: `radial-gradient(circle at 35% 30%, ${n.color}55, ${n.color}1e 65%, transparent)`,
                    border: `2px solid ${n.color}99`,
                    boxShadow: active
                      ? `0 0 30px ${n.color}bb, inset 0 0 14px ${n.color}44`
                      : `0 0 12px ${n.color}55, inset 0 0 8px ${n.color}22`,
                    transform: active ? "scale(1.18)" : "scale(1)",
                  }}
                >
                  <span className="text-2xl" style={{ filter: "drop-shadow(0 0 5px rgba(255,255,255,0.5))" }}>{n.icon}</span>
                  {active && (
                    <span className="absolute inset-0 rounded-full animate-ping opacity-25" style={{ background: n.color, animationDuration: "1.5s" }} />
                  )}
                </div>
                <div className="mt-1 text-center text-[11px] font-semibold text-white/85" style={{ textShadow: "0 0 6px rgba(0,0,0,0.9)" }}>
                  {n.label}
                </div>
                {/* hover 数据浮层 */}
                {active && (
                  <div
                    className="absolute left-1/2 top-full mt-2 -translate-x-1/2 w-44 rounded-xl p-3 z-20"
                    style={{ background: "rgba(15,23,42,0.95)", border: `1px solid ${n.color}77` }}
                  >
                    <div className="flex items-center gap-1.5 mb-1">
                      <span>{n.icon}</span>
                      <span className="text-white text-xs font-semibold">{n.label}</span>
                    </div>
                    <div className="text-slate-200 text-[11px] leading-relaxed whitespace-pre-line">
                      {n.renderInfo(data)}
                    </div>
                    <div className="mt-1.5 text-[9px] text-slate-400">👆 点击进入</div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* 标题 */}
      <div className="absolute top-4 left-1/2 -translate-x-1/2 z-20 text-center pointer-events-none">
        <div className="text-xs tracking-[0.3em] text-indigo-300/70 uppercase">LearnLab · 知识星盘</div>
        <h2 className="text-lg md:text-xl font-bold text-white mt-1 drop-shadow-[0_0_12px_rgba(99,102,241,0.6)]">
          悬停查看数据 · 点击进入
        </h2>
      </div>

      {/* 数据流样式注入 */}
      <style>{`
        .flow-dot {
          position: absolute;
          left: 50%;
          top: 50%;
          width: 5px;
          height: 5px;
          border-radius: 9999px;
          background: #a5b4fc;
          box-shadow: 0 0 8px rgba(129,140,248,0.9);
          animation: flow-radial 2.6s linear infinite;
          opacity: 0;
          pointer-events: none;
        }
        @keyframes flow-radial {
          0%   { transform: translate(-50%, -50%) translate(0, -150px) scale(0.6); opacity: 0; }
          15%  { opacity: 0.9; }
          85%  { opacity: 0.7; }
          100% { transform: translate(-50%, -50%) translate(0, 150px) scale(0.4); opacity: 0; }
        }
      `}</style>
    </div>
  );
};

export default ConstellationScene;
