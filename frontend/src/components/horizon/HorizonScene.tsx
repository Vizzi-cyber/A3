/**
 * 横滑 2D 高级场景（HorizonScene）
 * 一张超宽"知识大陆"场景横幅，左右滑动浏览：
 *   - 横向滚动：鼠标拖拽 / 滚轮 / 左右箭头 / 键盘
 *   - 8 个交互站点（热区）：hover 发光+放大+浮层卡片，点击跳转功能页
 *   - 多层视差背景（云带/光点不同速度）
 * 背景图：public/images/knowledge-land.png（AI 生成，未生成时用 CSS 渐变占位）
 */
import React, { useCallback, useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { LeftOutlined, RightOutlined } from "@ant-design/icons";

export interface HorizonSite {
  id: string;
  label: string;
  desc: string;
  icon: string;
  color: string;
  route: string;
  /** 在场景横幅中的水平位置（0-100%） */
  x: number;
  /** 垂直位置（0-100%，相对场景高度） */
  y: number;
}

const SITES: HorizonSite[] = [
  { id: "c-language", label: "编程山谷 · C语言", desc: "芯片级编程训练，从语法到指针", icon: "💻", color: "#3b82f6", route: "/resources", x: 12, y: 52 },
  { id: "circuit", label: "电路之城", desc: "MNA 虚拟实验与故障诊断", icon: "⚡", color: "#f97316", route: "/circuit-simulator", x: 25, y: 48 },
  { id: "stm32", label: "嵌入式工厂", desc: "STM32 外设编程与实战", icon: "🔧", color: "#22c55e", route: "/learning-path", x: 38, y: 55 },
  { id: "tutor", label: "AI 学院", desc: "12 个智能体全天候辅导", icon: "🤖", color: "#22d3ee", route: "/tutor", x: 51, y: 45 },
  { id: "knowledge", label: "知识城堡", desc: "双向链接笔记与知识图谱", icon: "📚", color: "#f8fafc", route: "/knowledge-base", x: 63, y: 52 },
  { id: "challenges", label: "冒险星域", desc: "游戏化学习地图与挑战", icon: "🌍", color: "#10b981", route: "/challenges", x: 76, y: 48 },
  { id: "leaderboard", label: "成就殿堂", desc: "六维排行榜与荣誉", icon: "🏆", color: "#f59e0b", route: "/leaderboard", x: 87, y: 54 },
];

interface HorizonSceneProps {
  className?: string;
}

const HorizonScene: React.FC<HorizonSceneProps> = ({ className = "" }) => {
  const navigate = useNavigate();
  const viewportRef = useRef<HTMLDivElement>(null);
  const trackRef = useRef<HTMLDivElement>(null);
  const [active, setActive] = useState<string | null>(null);
  const [hovered, setHovered] = useState<string | null>(null);
  const [bgLoaded, setBgLoaded] = useState(false);

  // ---------- 横向滚动控制 ----------
  const scrollBy = useCallback((dx: number) => {
    const el = viewportRef.current;
    if (!el) return;
    el.scrollBy({ left: dx, behavior: "smooth" });
  }, []);

  const scrollToSite = useCallback((xPercent: number) => {
    const el = viewportRef.current;
    if (!el) return;
    const target = (el.scrollWidth - el.clientWidth) * (xPercent / 100);
    el.scrollTo({ left: target, behavior: "smooth" });
  }, []);

  // 滚轮 → 横向滚动
  useEffect(() => {
    const el = viewportRef.current;
    if (!el) return;
    const onWheel = (e: WheelEvent) => {
      e.preventDefault();
      el.scrollLeft += e.deltaY + e.deltaX;
    };
    el.addEventListener("wheel", onWheel, { passive: false });
    return () => el.removeEventListener("wheel", onWheel);
  }, []);

  // 键盘左右
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "ArrowRight") scrollBy(300);
      if (e.key === "ArrowLeft") scrollBy(-300);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [scrollBy]);

  // 鼠标拖拽（区分点击）
  const dragRef = useRef({ down: false, startX: 0, startScroll: 0, moved: 0 });
  const onPointerDown = (e: React.PointerEvent) => {
    const el = viewportRef.current;
    if (!el) return;
    dragRef.current = { down: true, startX: e.clientX, startScroll: el.scrollLeft, moved: 0 };
  };
  const onPointerMove = (e: React.PointerEvent) => {
    const el = viewportRef.current;
    const d = dragRef.current;
    if (!el || !d.down) return;
    const dx = e.clientX - d.startX;
    d.moved = Math.max(d.moved, Math.abs(dx));
    el.scrollLeft = d.startScroll - dx;
  };
  const onPointerUp = () => {
    dragRef.current.down = false;
  };

  // 背景图加载检测
  useEffect(() => {
    const img = new Image();
    img.onload = () => setBgLoaded(true);
    img.src = "/images/knowledge-land.png";
  }, []);

  return (
    <div className={`relative w-full h-[calc(100vh-140px)] min-h-[520px] rounded-2xl overflow-hidden border border-slate-800/40 bg-[#0b1026] ${className}`}>
      {/* ===== 横滑视口 ===== */}
      <div
        ref={viewportRef}
        className="w-full h-full overflow-x-auto overflow-y-hidden scrollbar-hide cursor-grab active:cursor-grabbing"
        onPointerDown={onPointerDown}
        onPointerMove={onPointerMove}
        onPointerUp={onPointerUp}
        onPointerLeave={onPointerUp}
      >
        {/* ===== 长场景轨道（宽 4000px） ===== */}
        <div
          ref={trackRef}
          className="relative h-full"
          style={{ width: 4000, minWidth: 4000 }}
        >
          {/* 背景：AI 生成的场景图（未生成时用渐变占位） */}
          {bgLoaded ? (
            <img
              src="/images/knowledge-land.png"
              alt="知识大陆"
              className="absolute inset-0 w-full h-full object-cover"
              draggable={false}
            />
          ) : (
            <div className="absolute inset-0 w-full h-full">
              {/* 占位：深空渐变 + 光带 + 网格（视觉近似） */}
              <div className="absolute inset-0 bg-gradient-to-r from-[#0b1026] via-[#131a3a] to-[#0b1026]" />
              <div className="absolute inset-0 opacity-40" style={{
                backgroundImage:
                  "radial-gradient(circle at 12% 55%, rgba(59,130,246,0.45), transparent 18%)," +
                  "radial-gradient(circle at 25% 50%, rgba(249,115,22,0.4), transparent 18%)," +
                  "radial-gradient(circle at 38% 58%, rgba(34,197,94,0.4), transparent 18%)," +
                  "radial-gradient(circle at 51% 45%, rgba(34,211,238,0.45), transparent 18%)," +
                  "radial-gradient(circle at 63% 52%, rgba(248,250,252,0.35), transparent 16%)," +
                  "radial-gradient(circle at 76% 48%, rgba(16,185,129,0.4), transparent 18%)," +
                  "radial-gradient(circle at 87% 55%, rgba(245,158,11,0.4), transparent 18%)",
              }} />
              {/* 光带连接 */}
              <div className="absolute inset-x-0 top-[52%] h-[2px] bg-gradient-to-r from-blue-500 via-cyan-400 to-amber-400 opacity-50" style={{ filter: "blur(1px)" }} />
              {/* 网格地平线 */}
              <div className="absolute inset-x-0 bottom-0 h-[22%] opacity-30" style={{
                backgroundImage: "linear-gradient(rgba(148,163,184,0.25) 1px, transparent 1px), linear-gradient(90deg, rgba(148,163,184,0.25) 1px, transparent 1px)",
                backgroundSize: "48px 32px",
                transform: "perspective(400px) rotateX(55deg) scale(1.4)",
                transformOrigin: "bottom",
              }} />
            </div>
          )}

          {/* ===== 交互站点（热区） ===== */}
          {SITES.map((site) => (
            <div
              key={site.id}
              className="absolute z-10 -translate-x-1/2 -translate-y-1/2"
              style={{ left: `${site.x}%`, top: `${site.y}%` }}
              onMouseEnter={() => setHovered(site.id)}
              onMouseLeave={() => setHovered((h) => (h === site.id ? null : h))}
              onClick={(e) => {
                if (dragRef.current.moved > 8) return; // 拖拽不触发点击
                e.stopPropagation();
                navigate(site.route);
              }}
            >
              {/* 物体：图标球体 */}
              <div
                className={`relative flex items-center justify-center rounded-full transition-all duration-300 ${
                  hovered === site.id || active === site.id
                    ? "scale-125"
                    : "scale-100"
                }`}
                style={{
                  width: 76,
                  height: 76,
                  background: `radial-gradient(circle at 30% 30%, ${site.color}55, ${site.color}22 60%, transparent)`,
                  border: `2px solid ${site.color}88`,
                  boxShadow: hovered === site.id
                    ? `0 0 30px ${site.color}aa, inset 0 0 18px ${site.color}44`
                    : `0 0 12px ${site.color}55, inset 0 0 8px ${site.color}22`,
                  cursor: "pointer",
                }}
              >
                <span className="text-3xl" style={{ filter: "drop-shadow(0 0 6px rgba(255,255,255,0.6))" }}>
                  {site.icon}
                </span>
                {/* hover 光晕 */}
                {hovered === site.id && (
                  <span
                    className="absolute inset-0 rounded-full animate-ping opacity-30"
                    style={{ background: site.color, animationDuration: "1.6s" }}
                  />
                )}
              </div>

              {/* 站点名称 */}
              <div className="mt-2 text-center w-28">
                <div
                  className="text-xs font-semibold text-white/90 transition-all"
                  style={{ textShadow: "0 0 8px rgba(0,0,0,0.8)" }}
                >
                  {site.label.split(" · ")[0]}
                </div>
              </div>

              {/* hover 浮层卡片 */}
              {hovered === site.id && (
                <div
                  className="absolute left-1/2 top-full mt-3 -translate-x-1/2 w-52 rounded-xl p-4 z-20 glass-strong"
                  style={{ background: "rgba(15,23,42,0.92)", border: `1px solid ${site.color}66` }}
                >
                  <div className="flex items-center gap-2">
                    <span className="text-xl">{site.icon}</span>
                    <div className="font-semibold text-white text-sm">{site.label}</div>
                  </div>
                  <div className="text-[11px] text-slate-300 mt-1.5 leading-relaxed">
                    {site.desc}
                  </div>
                  <div className="mt-2 text-[10px] text-slate-400">
                    👆 点击进入
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* ===== 顶部标题 ===== */}
      <div className="absolute top-4 left-1/2 -translate-x-1/2 z-20 text-center pointer-events-none">
        <div className="text-xs tracking-[0.3em] text-sky-300/70 uppercase">LearnLab · 知识大陆</div>
        <h2 className="text-lg md:text-xl font-bold text-white mt-1 drop-shadow-[0_0_12px_rgba(99,102,241,0.6)]">
          滑动探索，点击进入
        </h2>
      </div>

      {/* ===== 左右箭头 ===== */}
      <button
        onClick={() => scrollBy(-500)}
        className="absolute left-3 top-1/2 -translate-y-1/2 z-20 w-10 h-10 rounded-full bg-white/10 hover:bg-white/25 backdrop-blur border border-white/20 text-white flex items-center justify-center transition-all"
        aria-label="向左"
      >
        <LeftOutlined />
      </button>
      <button
        onClick={() => scrollBy(500)}
        className="absolute right-3 top-1/2 -translate-y-1/2 z-20 w-10 h-10 rounded-full bg-white/10 hover:bg-white/25 backdrop-blur border border-white/20 text-white flex items-center justify-center transition-all"
        aria-label="向右"
      >
        <RightOutlined />
      </button>

      {/* ===== 底部站点导航点 ===== */}
      <div className="absolute bottom-3 left-1/2 -translate-x-1/2 z-20 flex items-center gap-2 pointer-events-none">
        {SITES.map((site, i) => (
          <div
            key={site.id}
            className="h-1.5 rounded-full transition-all duration-300"
            style={{
              width: i === SITES.indexOf(SITES.find((s) => s.id === active) || SITES[0]) ? 18 : 6,
              background: site.color,
              opacity: 0.7,
            }}
          />
        ))}
      </div>

      {/* 底部提示 */}
      <div className="absolute bottom-8 left-1/2 -translate-x-1/2 z-20 text-[11px] text-slate-400/80 pointer-events-none">
        🖱️ 拖拽或滚轮横向滑动 · 悬停查看详情 · 点击进入
      </div>
    </div>
  );
};

export default HorizonScene;
