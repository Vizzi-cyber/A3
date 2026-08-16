/**
 * AI 引擎状态条（AlgorithmStatusBar）
 * 显示当前生效算法的实时状态——让"算法在工作"可见：
 *   🧠 BKT 掌握度（均值） · ⏰ FSRS 待复习 · 📐 IRT 能力 θ
 * 发光芯片式，固定页面角落。数据来自 /algorithms/* 接口。
 */
import React, { useEffect, useState } from "react";
import { Popover } from "antd";
import { ThunderboltOutlined } from "@ant-design/icons";
import api from "../../services/api";

interface EngineStatus {
  bktMastery: number | null;   // 平均掌握度 %
  fsrsDue: number | null;      // 待复习数
  irtTheta: number | null;     // 能力 θ
  loading: boolean;
}

const AlgorithmStatusBar: React.FC<{ className?: string }> = ({ className = "" }) => {
  const [status, setStatus] = useState<EngineStatus>({ bktMastery: null, fsrsDue: null, irtTheta: null, loading: true });

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
    <Popover
      content={
        <div className="flex items-center gap-2 py-1">
          {chips.map((c) => (
            <span
              key={c.label}
              className="flex items-center gap-1 rounded-full px-2 py-1 text-[11px] font-semibold"
              style={{
                background: `${c.color}12`,
                color: c.color,
                border: `1px solid ${c.color}26`,
              }}
              title={c.label}
            >
              <span>{c.icon}</span>
              <span>{c.label.split(" ")[0]}</span>
              <span>{c.value}</span>
            </span>
          ))}
        </div>
      }
      placement="bottomRight"
      trigger="click"
      arrow
    >
      <button
        className="relative w-9 h-9 rounded-full bg-slate-50 hover:bg-slate-100 flex items-center justify-center text-slate-500 hover:text-primary transition-all"
        title="AI 引擎状态"
      >
        <ThunderboltOutlined className="text-lg" />
        <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 rounded-full bg-indigo-500">
          <span className="absolute inset-0 rounded-full bg-indigo-400 animate-ping opacity-70" />
        </span>
      </button>
    </Popover>
  );
};

export default AlgorithmStatusBar;
