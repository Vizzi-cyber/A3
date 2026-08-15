/**
 * 学科空间入口页（SpacePortal）
 * 3D 悬浮知识空间：点击 3D 物体进入对应功能页面。
 * 全屏场景 + 顶部标题 + 底部功能提示。
 */
import React from "react";
import { useNavigate } from "react-router-dom";
import SpaceScene from "../components/three/SpaceScene";

const SpacePortal: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="relative w-full h-[calc(100vh-120px)] min-h-[560px] overflow-hidden rounded-2xl border border-slate-800/60 bg-[#0a0e1f]">
      {/* 顶部标题 */}
      <div className="absolute top-4 left-1/2 -translate-x-1/2 z-10 text-center pointer-events-none">
        <div className="text-xs tracking-[0.3em] text-sky-300/70 uppercase">
          LearnLab · 知识空间
        </div>
        <h2 className="text-xl md:text-2xl font-bold text-white mt-1 drop-shadow-[0_0_12px_rgba(99,102,241,0.6)]">
          悬浮于知识星云，点选你的目的地
        </h2>
      </div>

      {/* 3D 场景 */}
      <SpaceScene onNavigate={(route) => navigate(route)} className="w-full h-full" />

      {/* 左侧物体索引 */}
      <div className="absolute left-4 top-1/2 -translate-y-1/2 z-10 hidden md:block space-y-2">
        {[
          { label: "🤖 AI 辅导", route: "/tutor" },
          { label: "📚 学习路径", route: "/learning-path" },
          { label: "💻 C语言中心", route: "/resources" },
          { label: "⚡ 电路仿真", route: "/circuit-simulator" },
          { label: "🏆 成就排行", route: "/leaderboard" },
          { label: "🌍 知识冒险", route: "/challenges" },
          { label: "🧭 个人空间", route: "/personal" },
          { label: "📊 学情分析", route: "/teacher/analytics" },
        ].map((item) => (
          <button
            key={item.route}
            onClick={() => navigate(item.route)}
            className="block w-full text-left px-3 py-1.5 rounded-lg text-xs text-slate-300 bg-white/5 hover:bg-sky-400/20 hover:text-white border border-white/5 hover:border-sky-300/40 transition-all"
          >
            {item.label}
          </button>
        ))}
      </div>
    </div>
  );
};

export default SpacePortal;
