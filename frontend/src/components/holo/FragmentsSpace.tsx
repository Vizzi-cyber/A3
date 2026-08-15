/**
 * 白色碎片漂浮空间（FragmentsSpace）
 * 浅色主题适配：白色磨砂玻璃"碎片"卡片散布在页面各个角落，
 * 正面永远可读（无 3D 旋转），轻柔漂浮，hover 上浮发光，点击进入。
 * 背景：浅色渐变 + 淡雅光斑 + 极淡网格（无深空、无噪点粒子）
 */
import React, { useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import gsap from "gsap";
import { Progress } from "antd";
import CountUp from "../animations/CountUp";
import AnimatedRing from "../animations/AnimatedRing";
import AnimatedText from "../animations/AnimatedText";
import { HoloData } from "./useHoloData";

interface Fragment {
  id: string;
  route: string;
  /** 桌面端散布位置（百分比，错落） */
  x: number;
  y: number;
  w: number;
  icon: string;
  accent: string;
  title: string;
  float: number; // 漂浮幅度
  duration: number; // 漂浮周期
  render: (d: HoloData) => React.ReactNode;
}

const FragmentsSpace: React.FC<{ data: HoloData }> = ({ data }) => {
  const navigate = useNavigate();
  const sceneRef = useRef<HTMLDivElement>(null);

  // 碎片配置（散布全页，错落有致）
  const fragments: Fragment[] = [
    {
      id: "mastery", route: "/learning-path", x: 6, y: 14, w: 250, icon: "🧠", accent: "#6366f1", title: "知识掌握",
      float: 10, duration: 4.6,
      render: (d) => (
        <div className="flex items-center gap-3">
          <AnimatedRing percent={Math.min(100, Math.round((d.masteredKps / 20) * 100))} size={60} strokeWidth={6} color="#6366f1" trackColor="#eef1f6">
            <span className="text-sm font-bold text-slate-800"><CountUp value={d.masteredKps} duration={1.2} /></span>
          </AnimatedRing>
          <div className="text-xs text-slate-500 leading-relaxed">
            已掌握知识点<br /><span className="text-slate-800 font-semibold">{d.masteredKps}/20</span>
          </div>
        </div>
      ),
    },
    {
      id: "weekly", route: "/personal", x: 74, y: 10, w: 230, icon: "⏱", accent: "#0ea5e9", title: "本周学习",
      float: 13, duration: 5.2,
      render: (d) => (
        <div>
          <div className="text-3xl font-bold text-slate-800">
            <CountUp value={d.weeklyHours} duration={1.4} decimals={1} /><span className="text-base text-slate-400 ml-1">h</span>
          </div>
          <div className="mt-2 flex gap-3 text-[11px] text-slate-500">
            <span>🔥 连续 {d.streakDays} 天</span>
            <span>今日 {d.todayMin} min</span>
          </div>
        </div>
      ),
    },
    {
      id: "path", route: "/learning-path", x: 12, y: 58, w: 260, icon: "🧭", accent: "#8b5cf6", title: "学习路径 · ADPP",
      float: 8, duration: 4.2,
      render: (d) => (
        <div>
          <div className="flex justify-between text-[11px] text-slate-500 mb-1.5">
            <span>{d.pathNodes} 个知识点</span>
            <span>{Math.round(d.pathProgress)}%</span>
          </div>
          <Progress percent={Math.round(d.pathProgress)} showInfo={false} strokeColor={{ "0%": "#6366f1", "100%": "#10b981" }} trailColor="#f1f5f9" size="small" />
        </div>
      ),
    },
    {
      id: "quiz", route: "/learning-path", x: 80, y: 52, w: 240, icon: "✏️", accent: "#f97316", title: "每日练习",
      float: 11, duration: 4.8,
      render: (d) => (
        <div>
          <div className="text-2xl font-bold text-slate-800">
            <CountUp value={d.quizTotal} duration={1.3} /><span className="text-sm text-slate-400 ml-1">题</span>
          </div>
          <div className="text-[11px] text-slate-500 mt-1">覆盖 {d.quizCovered} 个知识点</div>
        </div>
      ),
    },
    {
      id: "rank", route: "/leaderboard", x: 70, y: 74, w: 250, icon: "🏆", accent: "#f59e0b", title: "成就排行",
      float: 9, duration: 5.0,
      render: (d) => (
        <div className="space-y-1.5">
          {(d.topRankers.length ? d.topRankers : [{ name: "加载中…", score: 0 }]).map((r, i) => (
            <div key={i} className="flex items-center gap-2 text-xs">
              <span>{["🥇", "🥈", "🥉"][i] ?? "·"}</span>
              <span className="text-slate-700 flex-1 truncate">{r.name}</span>
              <span className="text-slate-400">{r.score}</span>
            </div>
          ))}
        </div>
      ),
    },
    {
      id: "honor", route: "/leaderboard", x: 30, y: 80, w: 220, icon: "🎖", accent: "#10b981", title: "成就 · 积分",
      float: 12, duration: 4.4,
      render: (d) => (
        <div className="text-xl font-bold text-slate-800">
          {d.achievements} <span className="text-sm font-normal text-slate-400">项成就</span>
          <div className="mt-1 text-sm text-slate-500"><CountUp value={d.points} duration={1.2} /> 积分 · Lv.{d.level}</div>
        </div>
      ),
    },
  ];

  // 轻柔漂浮动画（GSAP，幅度小、周期随机，不绕圈）
  useEffect(() => {
    const el = sceneRef.current;
    if (!el) return;
    const cards = el.querySelectorAll<HTMLElement>(".frag-desk");
    const ctx = gsap.context(() => {
      cards.forEach((card, i) => {
        const f = fragments[i];
        gsap.to(card, {
          y: f.float,
          rotation: 1.2,
          duration: f.duration,
          yoyo: true,
          repeat: -1,
          ease: "sine.inOut",
          delay: i * 0.6,
        });
      });
    }, el);
    return () => ctx.revert();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div
      ref={sceneRef}
      className="relative w-full rounded-2xl border border-slate-200/70 overflow-hidden"
      style={{
        minHeight: "calc(100vh - 140px)",
        minWidth: 900,
        background:
          "linear-gradient(150deg, #f8fafc 0%, #eef2ff 35%, #f5f3ff 65%, #f0f9ff 100%)",
      }}
    >
      {/* 淡雅光斑 */}
      <div className="absolute -top-24 -left-24 w-96 h-96 rounded-full bg-indigo-200/40 blur-3xl pointer-events-none" />
      <div className="absolute top-1/3 -right-32 w-[28rem] h-[28rem] rounded-full bg-sky-200/35 blur-3xl pointer-events-none" />
      <div className="absolute -bottom-32 left-1/4 w-[26rem] h-[26rem] rounded-full bg-violet-200/30 blur-3xl pointer-events-none" />
      {/* 极淡网格 */}
      <div className="absolute inset-0 opacity-[0.35] pointer-events-none" style={{
        backgroundImage:
          "linear-gradient(rgba(99,102,241,0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(99,102,241,0.05) 1px, transparent 1px)",
        backgroundSize: "56px 56px",
      }} />

      {/* 顶部标题 */}
      <div className="relative z-10 pt-10 pb-6 text-center pointer-events-none">
        <div className="text-xs tracking-[0.3em] text-indigo-400/80 uppercase">LearnLab · 碎片空间</div>
        <h2 className="text-2xl md:text-3xl font-bold text-slate-800 mt-2">
          <AnimatedText text="散落的知识碎片，等你拾起" delay={0.1} />
        </h2>
        <p className="text-sm text-slate-400 mt-2">悬停查看 · 点击拾起</p>
      </div>

      {/* 漂浮碎片（桌面散布全页） */}
      <div className="relative z-10 hidden lg:block" style={{ height: "calc(100vh - 220px)" }}>
        {fragments.map((f) => (
          <div
            key={f.id}
            className="fragment-card frag-desk absolute -translate-x-1/2 -translate-y-1/2 cursor-pointer"
            style={{ left: `${f.x}%`, top: `${f.y}%` }}
            onClick={() => navigate(f.route)}
          >
            <div
              className="rounded-2xl p-5 transition-all duration-300 hover:-translate-y-1.5 hover:shadow-xl"
              style={{
                width: f.w,
                background: "rgba(255,255,255,0.82)",
                border: "1px solid rgba(255,255,255,0.9)",
                boxShadow: "0 8px 28px rgba(15,23,42,0.08)",
                backdropFilter: "blur(14px)",
              }}
              onMouseEnter={(e) => {
                const el = e.currentTarget;
                el.style.boxShadow = `0 14px 40px rgba(15,23,42,0.12), 0 0 0 1.5px ${f.accent}55`;
                el.style.borderColor = `${f.accent}44`;
              }}
              onMouseLeave={(e) => {
                const el = e.currentTarget;
                el.style.boxShadow = "0 8px 28px rgba(15,23,42,0.08)";
                el.style.borderColor = "rgba(255,255,255,0.9)";
              }}
            >
              <div className="flex items-center gap-2 mb-2.5">
                <span className="w-8 h-8 rounded-lg flex items-center justify-center text-base" style={{ background: `${f.accent}14`, color: f.accent }}>
                  {f.icon}
                </span>
                <span className="text-sm font-semibold text-slate-700">{f.title}</span>
              </div>
              {f.render(data)}
            </div>
          </div>
        ))}
      </div>

      {/* 窄屏：流式网格（碎片不重叠） */}
      <div className="relative z-10 p-4 lg:hidden grid grid-cols-1 sm:grid-cols-2 gap-4">
        {fragments.map((f) => (
          <div
            key={f.id}
            className="fragment-card cursor-pointer rounded-2xl p-4 transition-all hover:shadow-lg"
            style={{ background: "rgba(255,255,255,0.85)", border: "1px solid rgba(255,255,255,0.9)", boxShadow: "0 6px 20px rgba(15,23,42,0.07)" }}
            onClick={() => navigate(f.route)}
          >
            <div className="flex items-center gap-2 mb-2">
              <span className="w-7 h-7 rounded-lg flex items-center justify-center text-sm" style={{ background: `${f.accent}14`, color: f.accent }}>{f.icon}</span>
              <span className="text-sm font-semibold text-slate-700">{f.title}</span>
            </div>
            {f.render(data)}
          </div>
        ))}
      </div>
    </div>
  );
};

export default FragmentsSpace;
