/**
 * AI 引擎状态条（AlgorithmStatusBar）
 * 显示当前生效算法的实时状态——让"算法在工作"可见：
 *   🧠 BKT 掌握度（均值） · ⏰ FSRS 待复习 · 📐 IRT 能力 θ
 * 发光芯片式，固定页面角落。数据来自 /algorithms/* 接口。
 */
import React, { useEffect, useState } from "react";
import api from "../../services/api";

interface EngineStatus {
  bktMastery: number | null;   // 平均掌握度 %
  fsrsDue: number | null;      // 待复习数
  irtTheta: number | null;     // 能力 θ
  loading: boolean;
}

const AlgorithmStatusBar: React.FC<{ className?: string }> = ({ className = "" }) => {
  const [status, setStatus] = useState<EngineStatus>({ bktMastery: null, fsrsDue: null, irtTheta: null, loading: true });
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    let alive = true;
    const load = async () => {
      try {
        const [mastery, due, ability] = await Promise.allSettled([
          api.get("/algorithms/bkt/mastery/student_001"),
          api.get("/algorithms/memory/due/student_001"),
          api.get("/algorithms/irt/ability/student_001"),
        ]);
        const val = (r: PromiseSettledResult<any>) => (r.status === "fulfilled" ? r.value?.data?.data : null);
        const m = val(mastery);
        const d = val(due);
        const a = val(ability);
        if (!alive) return;
        const masteryMap = m?.mastery_map ?? {};
        const values = Object.values(masteryMap).filter((v) => typeof v === "number");
        setStatus({
          bktMastery: values.length ? Math.round((values.reduce((s: number, v: any) => s + v, 0) / values.length) * 100) : null,
          fsrsDue: d?.due_cards?.length ?? null,
          irtTheta: a?.ability_theta ?? null,
          loading: false,
        });
      } catch {
        if (alive) setStatus((s) => ({ ...s, loading: false }));
      }
    };
    load();
    return () => { alive = false; };
  }, []);

  if (status.loading) return null;

  const chips = [
    { label: "BKT 掌握度", value: status.bktMastery != null ? `${status.bktMastery}%` : "—", color: "#6366f1", icon: "🧠" },
    { label: "FSRS 待复习", value: status.fsrsDue != null ? `${status.fsrsDue} 项` : "0", color: "#f59e0b", icon: "⏰" },
    { label: "IRT 能力", value: status.irtTheta != null ? status.irtTheta.toFixed(2) : "—", color: "#22d3ee", icon: "📐" },
  ];

  return (
    <div className={`select-none ${className}`} style={{ zIndex: 9000 }}>
      {/* 默认折叠小胶囊：不挡页面内容，悬浮/点击展开算法数据 */}
      <div
        className="flex items-center gap-1.5 rounded-full px-2.5 py-1 cursor-pointer transition-all"
        style={{
          background: "rgba(255,255,255,0.92)",
          border: "1px solid rgba(99,102,241,0.28)",
          boxShadow: "0 4px 12px rgba(15,23,42,0.08)",
          backdropFilter: "blur(8px)",
        }}
        onMouseEnter={() => setExpanded(true)}
        onMouseLeave={() => setExpanded(false)}
        onClick={() => setExpanded((e) => !e)}
      >
        <span className="relative flex w-1.5 h-1.5">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-70" />
          <span className="relative inline-flex rounded-full w-1.5 h-1.5 bg-indigo-500" />
        </span>
        <span className="text-[10px] font-semibold whitespace-nowrap" style={{ color: "#4f46e5" }}>
          ⚡ AI 引擎
        </span>
        {expanded && (
          <>
            <span className="w-px h-3 mx-0.5" style={{ background: "#e2e8f0" }} />
            {chips.map((c) => (
              <span
                key={c.label}
                className="flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-semibold whitespace-nowrap"
                style={{
                  background: `${c.color}14`,
                  color: c.color,
                  border: `1px solid ${c.color}22`,
                }}
                title={c.label}
              >
                <span>{c.icon}</span>
                <span>{c.label.split(" ")[0]}</span>
                <span>{c.value}</span>
              </span>
            ))}
          </>
        )}
      </div>
    </div>
  );
};

export default AlgorithmStatusBar;
