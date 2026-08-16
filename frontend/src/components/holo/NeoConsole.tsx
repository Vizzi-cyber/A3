/**
 * 深色数据指挥舱（NeoConsole）
 * 精致的深空沉浸式数据可视化首页：
 *   - 背景：深蓝黑渐变 + drei Grid 透视网格 + 细腻粒子（Sparkles）
 *   - 中央：真实数据驱动的 3D 可视化
 *       · 掌握度 3D 发光弧环（masteredKps/20 驱动，Bloom 泛光）
 *       · 学习趋势 3D 波形线（weeklyHours 驱动）
 *       · 知识点全息图谱（8 节点 + 连线，缓慢旋转）
 *   - 四周：billboard 数据面板（Html 屏幕投影，文字永远清晰，
 *     磨砂深色玻璃 + 渐变描边 + 辉光），hover 发光放大，点击跳转
 *   - Bloom 柔和辉光后处理 + 拖拽旋转（OrbitControls）
 * 技术：react-three-fiber + drei + @react-three/postprocessing
 */
import React, { useMemo, useRef, useState, useEffect } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { Float, Grid, Html, Line, OrbitControls, Sparkles } from "@react-three/drei";
import { EffectComposer, Bloom } from "@react-three/postprocessing";
import * as THREE from "three";
import { useNavigate } from "react-router-dom";
import { Progress } from "antd";
import { AreaChart, Area, BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Cell } from "recharts";
import CountUp from "../animations/CountUp";
import AnimatedRing from "../animations/AnimatedRing";
import AnimatedText from "../animations/AnimatedText";
import { HoloData } from "./useHoloData";
import { calcLevel } from "../../utils/level";
import ParticleNetwork from "./ParticleNetwork";
import ForceGraph3D from "./ForceGraph3D";

/* ================= 中央：掌握度 3D 发光弧环 ================= */
function MasteryArc({ percent }: { percent: number }) {
  const points = useMemo(() => {
    const pts: THREE.Vector3[] = [];
    const angle = (Math.min(100, Math.max(0, percent)) / 100) * Math.PI * 2;
    const N = 80;
    for (let i = 0; i <= N; i++) {
      const a = (i / N) * angle - Math.PI / 2;
      pts.push(new THREE.Vector3(Math.cos(a) * 1.5, Math.sin(a) * 1.5, 0));
    }
    return pts;
  }, [percent]);
  return (
    <Line points={points} color="#818cf8" lineWidth={3.5} transparent opacity={0.95} />
  );
}

/* ================= 中央：趋势 3D 波形线 ================= */
function TrendWave({ intensity }: { intensity: number }) {
  const ref = useRef<any>(null);
  const count = 57;
  const points = useMemo(() => {
    const pts: THREE.Vector3[] = [];
    for (let i = 0; i < count; i++) {
      pts.push(new THREE.Vector3(0, 0, 0));
    }
    return pts;
  }, []);

  // 波形沿 Z 轴传播（波峰移动 = 数据流动轨迹）
  useFrame((state) => {
    const line = ref.current;
    if (!line) return;
    const t = state.clock.elapsedTime;
    const attr = line.geometry.attributes.position as THREE.BufferAttribute;
    const arr = attr.array as Float32Array;
    for (let i = 0; i < count; i++) {
      const z = (i / (count - 1)) * 7 - 3.5;
      // 两个叠加波：主波沿 Z 传播 + 副波反向，形成流动感
      const y = Math.sin(z * 1.5 + t * 1.8) * 0.22 * (0.5 + intensity)
              + Math.sin(z * 0.7 - t * 1.1) * 0.14;
      arr[i * 3] = z * 0.4;
      arr[i * 3 + 1] = y;
      arr[i * 3 + 2] = z;
    }
    attr.needsUpdate = true;
  });

  return (
    <group position={[0, -1.1, 0]}>
      <Line ref={ref} points={points} color="#22d3ee" lineWidth={2} transparent opacity={0.75} />
    </group>
  );
}

/* ================= 中央：知识点全息图谱 ================= */
const GRAPH_NODES = [
  { name: "变量与类型", color: "#3b82f6", angle: 0, radius: 2.1, y: 0.5 },
  { name: "指针与内存", color: "#60a5fa", angle: 45, radius: 2.3, y: -0.35 },
  { name: "位运算", color: "#93c5fd", angle: 90, radius: 1.9, y: 0.35 },
  { name: "分压电路", color: "#f97316", angle: 135, radius: 2.2, y: -0.25 },
  { name: "RC 充放电", color: "#fb923c", angle: 180, radius: 2.0, y: 0.45 },
  { name: "GPIO 控制", color: "#22c55e", angle: 225, radius: 2.4, y: -0.4 },
  { name: "定时器 PWM", color: "#4ade80", angle: 270, radius: 2.1, y: 0.3 },
  { name: "ADC 采样", color: "#86efac", angle: 315, radius: 2.3, y: 0.1 },
];

function HoloGraph() {
  const group = useRef<THREE.Group>(null);
  const [hovered, setHovered] = useState<string | null>(null);

  useFrame((state) => {
    if (!group.current) return;
    group.current.rotation.y = state.clock.elapsedTime * 0.16;
    group.current.position.y = Math.sin(state.clock.elapsedTime * 0.5) * 0.12;
  });

  return (
    <group ref={group} position={[0, 0.9, 0]}>
      {/* 中心核心 */}
      <mesh>
        <sphereGeometry args={[0.28, 32, 32]} />
        <meshStandardMaterial color="#a5b4fc" emissive="#6366f1" emissiveIntensity={1.8} transparent opacity={0.92} />
      </mesh>
      {/* 中心到节点连线 */}
      {GRAPH_NODES.map((n, i) => {
        const a = (n.angle * Math.PI) / 180;
        const p: [number, number, number] = [Math.cos(a) * n.radius, n.y, Math.sin(a) * n.radius];
        return (
          <Line key={`cl${i}`} points={[new THREE.Vector3(0, 0, 0), new THREE.Vector3(...p)]} color={n.color} lineWidth={1} transparent opacity={0.35} />
        );
      })}
      {/* 节点 */}
      {GRAPH_NODES.map((n) => {
        const a = (n.angle * Math.PI) / 180;
        return (
          <group key={n.name} position={[Math.cos(a) * n.radius, n.y, Math.sin(a) * n.radius]}>
            <mesh
              onPointerOver={(e) => { e.stopPropagation(); setHovered(n.name); }}
              onPointerOut={() => setHovered(null)}
            >
              <sphereGeometry args={[0.13, 20, 20]} />
              <meshStandardMaterial
                color={n.color}
                emissive={n.color}
                emissiveIntensity={hovered === n.name ? 2.4 : 1.2}
                transparent opacity={0.92}
              />
            </mesh>
            {/* hover 显示名称（billboard，永远正对相机） */}
            {hovered === n.name && (
              <Html center distanceFactor={10} pointerEvents="none">
                <div className="whitespace-nowrap px-2.5 py-1 rounded-md text-[11px]"
                  style={{ background: "rgba(255,255,255,0.92)", border: `1px solid ${n.color}77`, color: "#334155", boxShadow: `0 0 14px ${n.color}44` }}>
                  {n.name}
                </div>
              </Html>
            )}
          </group>
        );
      })}
    </group>
  );
}

/* ================= 四周：billboard 数据面板 ================= */
interface PanelDef {
  id: string; route: string;
  position?: [number, number, number];
  icon: string; accent: string; title: string;
  render: (d: HoloData) => React.ReactNode;
}

/** 卡片屏幕均匀网格位置（4 列 × 3 行，统一深度 z=-3，相机正对时不重叠） */
const GRID_POSITIONS: [number, number, number][] = [
  [-5.0, 2.6, -3], [-1.7, 2.6, -3], [1.7, 2.6, -3], [5.0, 2.6, -3],
  [-5.0, 0, -3], [-1.7, 0, -3], [1.7, 0, -3], [5.0, 0, -3],
  [-5.0, -2.6, -3], [-1.7, -2.6, -3], [1.7, -2.6, -3], [5.0, -2.6, -3],
];

/** 有机错落：在网格基础上加固定随机偏移（保证不重叠，但去死板感） */
const ORGANIC_POSITIONS = GRID_POSITIONS.map((p, i) => {
  // 用固定种子生成偏移（±0.55，小于间距一半）
  const seed = (i * 7919) % 10000;
  const jx = ((seed % 100) / 100 - 0.5) * 1.0;
  const jy = (((seed * 37) % 100) / 100 - 0.5) * 0.9;
  const jz = (((seed * 131) % 100) / 100 - 0.5) * 0.4;
  return [p[0] + jx, p[1] + jy, p[2] + jz] as [number, number, number];
});

/**
 * 3D 环形卡片：在 XY 平面等分分布（同一 Z 深度），面向圆心。
 * 从 Z 轴（顶部）俯视时卡片 edge-on 不可见；悬停卡片时滚轮环绕旋转。
 */
function NeoPanel({ def, data, onNavigate, angle, y, onRingWheel }: {
  def: PanelDef; data: HoloData; onNavigate: (r: string) => void;
  angle: number; y: number; onRingWheel: (dy: number) => void;
}) {
  // 圆柱分布：卡片同一高度，正面（+Z）朝径向向外（观察者可见）
  const R = 6.2;
  const quat = useMemo(() => new THREE.Quaternion().setFromUnitVectors(
    new THREE.Vector3(0, 0, 1),
    new THREE.Vector3(Math.cos(angle), 0, Math.sin(angle)),
  ), [angle]);
  return (
    <group
      position={[Math.cos(angle) * R, 0, Math.sin(angle) * R]}
      quaternion={quat}
      scale={0.3}
    >
      <Html
        transform
        distanceFactor={22}
        zIndexRange={[20, 0]}
        wrapperClass="holo-ring-card"
      >
        <div
          className="neo-panel cursor-pointer select-none"
          style={{
            width: 176,
            background: "rgba(255,255,255,0.9)", border: "1px solid rgba(148,163,184,0.28)", borderRadius: 14, boxShadow: "0 10px 30px rgba(15,23,42,0.08), inset 0 1px 0 rgba(255,255,255,0.9)",
            backdropFilter: "blur(14px)",
            padding: 12,
          }}
          onClick={(e) => { e.stopPropagation(); onNavigate(def.route); }}
          onWheel={(e) => { e.stopPropagation(); e.preventDefault(); onRingWheel(e.deltaY); }}
        >
          <div className="mb-2 h-[2px] rounded-full" style={{ background: `linear-gradient(90deg, ${def.accent}, transparent)` }} />
          <div className="flex items-center gap-2">
            <span className="w-6.5 h-6.5 rounded-md flex items-center justify-center text-sm" style={{ background: `${def.accent}1c`, color: def.accent, boxShadow: `0 0 12px ${def.accent}33` }}>
              {def.icon}
            </span>
            <span className="text-xs font-semibold" style={{ color: "#1e293b", letterSpacing: "0.03em" }}>
              {def.title}
            </span>
          </div>
          <div className="mt-2">{def.render(data)}</div>
        </div>
      </Html>
    </group>
  );
}

function NeoPanels({ data, onNavigate }: { data: HoloData; onNavigate: (r: string) => void }) {
  const ringRef = useRef<THREE.Group>(null);
  const [ringAngle, setRingAngle] = useState(0);

  // 悬停卡片时滚轮 → 卡片组环绕旋转（展示下一张）
  const rotateRing = (dy: number) => {
    const delta = dy * 0.006;
    setRingAngle((a) => a + delta);
  };

  // 卡片持续轻微环绕（自动展示）+ 悬停时停止
  const [autoSpin, setAutoSpin] = useState(true);
  useFrame((_, delta) => {
    if (ringRef.current && autoSpin) {
      ringRef.current.rotation.y += delta * 0.3;
    }
  });

  // 圆柱分布：10 张卡等分角度（36°），全部同一高度（y=0）
  // 卡片正面朝外，俯视（Z 轴顶部）时 edge-on 不可见
  const cylinderPos = useMemo(() => {
    return Array.from({ length: 10 }, (_, i) => ({
      angle: (Math.PI * 2 * i) / 10,
      y: 0,
    }));
  }, []);

  const panels: PanelDef[] = [
    {
      id: "mastery", route: "/learning-path",
      icon: "🧠", accent: "#818cf8", title: "知识掌握",
      render: (d) => (
        <div className="flex items-center gap-3">
          <AnimatedRing percent={Math.min(100, Math.round((d.masteredKps / 20) * 100))} size={54} strokeWidth={5} color="#818cf8" trackColor="rgba(255,255,255,0.1)">
            <span className="text-xs font-bold text-slate-800"><CountUp value={d.masteredKps} duration={1.2} /></span>
          </AnimatedRing>
          <div className="text-[10px] leading-relaxed" style={{ color: "#94a3b8" }}>
            已掌握知识点<br /><span className="text-slate-800 font-semibold text-sm">{d.masteredKps}/20</span>
          </div>
        </div>
      ),
    },
    {
      id: "weekly", route: "/personal",
      icon: "⏱", accent: "#38bdf8", title: "本周学习",
      render: (d) => (
        <div>
          <div className="text-2xl font-bold text-slate-800">
            <CountUp value={d.weeklyHours} duration={1.4} decimals={1} /><span className="text-xs text-slate-400 ml-1">h</span>
          </div>
          <div className="mt-1.5 flex gap-3 text-[10px]" style={{ color: "#94a3b8" }}>
            <span>🔥 {d.streakDays} 天</span><span>今日 {d.todayMin}m</span>
          </div>
        </div>
      ),
    },
    {
      id: "path", route: "/learning-path",
      icon: "🧭", accent: "#a78bfa", title: "学习路径 · ADPP",
      render: (d) => (
        <div>
          <div className="flex justify-between text-[10px]" style={{ color: "#94a3b8" }}>
            <span>{d.pathNodes} 知识点</span><span>{Math.round(d.pathProgress)}%</span>
          </div>
          <Progress percent={Math.round(d.pathProgress)} showInfo={false} strokeColor={{ "0%": "#818cf8", "100%": "#34d399" }} trailColor="rgba(255,255,255,0.1)" size="small" className="mt-1.5" />
        </div>
      ),
    },
    {
      id: "rank", route: "/leaderboard",
      icon: "🏆", accent: "#fbbf24", title: "成就排行",
      render: (d) => (
        <div className="space-y-1">
          {(d.topRankers.length ? d.topRankers : [{ name: "加载中…", score: 0 }]).slice(0, 3).map((r, i) => (
            <div key={i} className="flex items-center gap-2 text-[11px]">
              <span>{["🥇", "🥈", "🥉"][i]}</span>
              <span className="flex-1 truncate" style={{ color: "#cbd5e1" }}>{r.name}</span>
              <span style={{ color: "#94a3b8" }}>{r.score}</span>
            </div>
          ))}
        </div>
      ),
    },
    {
      id: "quiz", route: "/learning-path",
      icon: "✏️", accent: "#fb923c", title: "每日练习",
      render: (d) => (
        <div className="text-lg font-bold text-slate-800">
          <CountUp value={d.quizTotal} duration={1.3} />
          <span className="text-xs font-normal text-slate-400 ml-1">题</span>
          <div className="text-[10px] font-normal mt-0.5" style={{ color: "#94a3b8" }}>覆盖 {d.quizCovered} 知识点</div>
        </div>
      ),
    },
    {
      id: "honor", route: "/leaderboard",
      icon: "🎖", accent: "#34d399", title: "成就 · 积分",
      render: (d) => (
        <div>
          <div className="text-xl font-bold text-slate-800">
            {d.achievements}<span className="text-xs font-normal text-slate-400 ml-1">成就</span>
          </div>
          <div className="text-[10px] mt-1" style={{ color: "#94a3b8" }}>
            <CountUp value={d.points} duration={1.2} /> 积分 · Lv.{d.level}
          </div>
        </div>
      ),
    },
    {
      id: "trend", route: "/personal",
      icon: "📈", accent: "#22d3ee", title: "学习趋势",
      render: (d) => {
        const data = (d.trend && d.trend.length ? d.trend : [
          { date: "D1", value: 0 }, { date: "D2", value: 0 }, { date: "D3", value: 0 },
        ]).map((t, i) => ({ ...t, name: (t.date ?? "").slice(5) || `D${i + 1}` }));
        return (
          <div className="h-14">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data}>
                <defs>
                  <linearGradient id="trendFill" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#22d3ee" stopOpacity={0.5} />
                    <stop offset="100%" stopColor="#22d3ee" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <YAxis hide domain={["auto", "auto"]} />
                <Area type="monotone" dataKey="value" stroke="#22d3ee" strokeWidth={1.5} fill="url(#trendFill)" />
              </AreaChart>
            </ResponsiveContainer>
            <div className="text-[9px] mt-1" style={{ color: "#64748b" }}>近 {data.length} 天学习时长走势</div>
          </div>
        );
      },
    },
    {
      id: "courseProgress", route: "/learning-path",
      icon: "📊", accent: "#38bdf8", title: "课程进度",
      render: (d) => {
        // 按课程统计完成/总数（来自真实知识点状态）
        const courseNames = ["C语言", "电路分析", "STM32嵌入式"];
        const data = courseNames.map((c) => {
          const nodes = d.graphNodes.filter((n) => n.course === c);
          const done = nodes.filter((n) => n.status === "completed").length;
          return { name: c === "C语言" ? "C" : c === "电路分析" ? "电" : "STM32", full: c, total: nodes.length, done, pct: nodes.length ? Math.round((done / nodes.length) * 100) : 0 };
        });
        const colors = ["#3b82f6", "#f97316", "#22c55e"];
        return (
          <div>
            <div className="h-12">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data} margin={{ top: 4, right: 4, left: 4, bottom: 0 }}>
                  <Bar dataKey="pct" radius={[3, 3, 0, 0]}>
                    {data.map((_, i) => <Cell key={i} fill={colors[i]} />)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div className="flex justify-between text-[9px] mt-1" style={{ color: "#64748b" }}>
              {data.map((c, i) => (
                <span key={c.full}><span style={{ color: colors[i] }}>●</span> {c.done}/{c.total}</span>
              ))}
            </div>
          </div>
        );
      },
    },
    {
      id: "level", route: "/personal",
      icon: "🎚", accent: "#a78bfa", title: "成长等级",
      render: (d) => {
        const lv = calcLevel(d.points);
        return (
          <div>
            <div className="flex items-center justify-between text-[10px]" style={{ color: "#94a3b8" }}>
              <span>Lv.{lv.level} {lv.level_name}</span><span>{lv.current_xp}/{lv.xp_per_level}</span>
            </div>
            <div className="mt-1.5 h-1.5 rounded-full overflow-hidden" style={{ background: "#e0e7ff" }}>
              <div className="h-full rounded-full" style={{ width: `${lv.progress_pct}%`, background: "linear-gradient(90deg,#6366f1,#22d3ee)" }} />
            </div>
            <div className="text-[10px] mt-1.5" style={{ color: "#94a3b8" }}>距离下一级还差 {lv.xp_to_next} XP</div>
          </div>
        );
      },
    },
    {
      id: "tasks", route: "/learning-path",
      icon: "📋", accent: "#38bdf8", title: "今日任务",
      render: (d) => (
        <div className="space-y-1">
          {(d.tasks.length ? d.tasks : [{ title: "暂无待办任务" }]).slice(0, 4).map((t, i) => (
            <div key={i} className="flex items-center gap-1.5 text-[11px]" style={{ color: "#cbd5e1" }}>
              <span style={{ color: "#38bdf8" }}>▸</span>
              <span className="truncate flex-1">{t.title}</span>
            </div>
          ))}
        </div>
      ),
    },
  ];

  return (
    <group
      ref={ringRef}
      rotation={[0, ringAngle, 0]}
      position={[0, -0.7, 0]}
      onPointerOver={() => setAutoSpin(false)}
      onPointerOut={() => setAutoSpin(true)}
    >
      {panels.map((p, i) => {
        const c = cylinderPos[i % cylinderPos.length];
        return (
          <NeoPanel
            key={p.id}
            def={p}
            data={data}
            onNavigate={onNavigate}
            angle={c.angle}
            y={c.y}
            onRingWheel={rotateRing}
          />
        );
      })}
    </group>
  );
}

/* ================= 主组件 ================= */
const NeoConsole: React.FC<{ data: HoloData }> = ({ data }) => {
  const navigate = useNavigate();
  const [showHint, setShowHint] = useState(() => !localStorage.getItem("hint_seen"));
  useEffect(() => {
    if (!showHint) return;
    const t = setTimeout(() => {
      setShowHint(false);
      localStorage.setItem("hint_seen", "1");
    }, 6000);
    return () => clearTimeout(t);
  }, [showHint]);
  const masteryPercent = Math.min(100, Math.round((data.masteredKps / 20) * 100));
  const waveIntensity = Math.min(1, Math.max(0.2, data.weeklyHours / 8));

  return (
    <div className="relative w-full rounded-2xl overflow-hidden border border-slate-700/50"
      style={{ height: "calc(100vh - 140px)", minHeight: 600, background: "#eef2fb" }}>
      {/* 左上角操作提示（首次显示 6 秒后自动隐藏） */}
      {showHint && (
      <div className="absolute top-3 left-4 z-20 pointer-events-none" style={{ transition: "opacity 0.5s" }}>
        <div
          className="flex items-center gap-3 px-4 py-1.5 rounded-full text-[11px]"
          style={{
            background: "rgba(255,255,255,0.82)",
            border: "1px solid rgba(99,102,241,0.18)",
            boxShadow: "0 4px 14px rgba(15,23,42,0.08)",
            color: "#64748b",
            backdropFilter: "blur(8px)",
          }}
        >
          <span>🖱️ 拖拽旋转</span>
          <span style={{ color: "#cbd5e1" }}>|</span>
          <span>滚轮缩放</span>
          <span style={{ color: "#cbd5e1" }}>|</span>
          <span>悬停卡片滚轮环绕</span>
          <span style={{ color: "#cbd5e1" }}>|</span>
          <span>点击卡片 / 节点查看</span>
        </div>
      </div>
      )}

      <Canvas camera={{ position: [0, 0.1, 13.5], fov: 44 }} dpr={[1, 2]} gl={{ antialias: true }}>
        {/* 背景：深蓝黑 */}
        <color attach="background" args={["#eef2fb"]} />
        <fog attach="fog" args={["#eef2fb", 10, 26]} />

        {/* 灯光（冷色氛围） */}
        <ambientLight intensity={0.5} color="#e2e8f0" />
        <directionalLight position={[5, 8, 6]} intensity={1.1} color="#ffffff" />
        <pointLight position={[-6, 2, -3]} intensity={30} color="#6366f1" />
        <pointLight position={[6, -1, -4]} intensity={24} color="#22d3ee" />
        <pointLight position={[0, 5, 3]} intensity={16} color="#a78bfa" />

        {/* 3D 粒子网络背景（AI 神经网络视觉，替代网格地面） */}
        <ParticleNetwork count={420} linkDistance={1.9} radius={8} />

        {/* 细腻粒子 */}
        <Sparkles count={80} scale={[14, 7, 10]} size={1.6} speed={0.25} color="#818cf8" opacity={0.45} />

        {/* 中央数据可视化（图谱几何中心与卡片环正中心对齐 (0,-0.7,0)） */}
        <group position={[0, -0.7, 0]}>
          <MasteryArc percent={masteryPercent} />
          {/* 3D 力导向知识图谱（35 个真实知识点 + 前置依赖，Fruchterman-Reingold 算法） */}
          {data.graphNodes.length >= 2 && (
            <ForceGraph3D nodes={data.graphNodes} edges={data.graphEdges} />
          )}
        </group>
        <TrendWave intensity={waveIntensity} />

        {/* 3D 环形数据卡片（环绕旋转） */}
        <NeoPanels data={data} onNavigate={(r) => navigate(r)} />

        {/* 拖拽旋转 */}
        <OrbitControls
          enablePan={false}
          enableZoom={true}
          zoomSpeed={0.9}
          minDistance={5}
          maxDistance={22}
          minPolarAngle={Math.PI / 3}
          maxPolarAngle={Math.PI / 1.15}
          target={[0, 0.2, 0]}
          autoRotate
          autoRotateSpeed={0.35}
        />

        {/* Bloom 柔和辉光 */}
        <EffectComposer multisampling={0}>
          <Bloom intensity={1.15} luminanceThreshold={0.25} luminanceSmoothing={0.6} mipmapBlur radius={0.7} />
        </EffectComposer>
      </Canvas>



      {/* 面板 hover 辉光 */}
      <style>{`
        .neo-panel { transition: box-shadow 0.3s ease, border-color 0.3s ease, transform 0.3s ease; }
        .neo-panel:hover {
          border-color: rgba(129,140,248,0.6);
          box-shadow: 0 14px 50px rgba(2,6,23,0.6), 0 0 24px rgba(99,102,241,0.35), inset 0 1px 0 rgba(255,255,255,0.1);
        }
      `}</style>
    </div>
  );
};

export default NeoConsole;
