/**
 * 全息悬浮学习空间（HoloSpace）
 * react-three-fiber + drei 实现的科幻全息场景：
 *   - 柔和深空氛围 + 漂浮尘埃粒子（Sparkles）
 *   - 中央：知识图谱全息投影（发光节点球 + 连线 + 缓慢旋转 + 数据流光点）
 *   - 四周：5 个漂浮全息碎片卡（真实 HTML：掌握度环形 / 本周统计 / 路径进度 /
 *           排行榜 / 每日练习），Float 漂浮 + 半透明玻璃 + hover 放大 + 点击跳转
 *   - 拖拽旋转场景（OrbitControls）
 * 数据：useHoloData 拉取后端真实数据
 */
import React, { useMemo, useRef, useState } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { Float, Html, OrbitControls, Sparkles } from "@react-three/drei";
import * as THREE from "three";
import { useNavigate } from "react-router-dom";
import { Progress } from "antd";
import CountUp from "../animations/CountUp";
import AnimatedRing from "../animations/AnimatedRing";
import { HoloData } from "./useHoloData";

/* ================= 中央知识图谱全息投影 ================= */

interface GraphNode {
  id: string;
  name: string;
  color: string;
  angle: number;
  radius: number;
  y: number;
}

// 8 个代表知识点节点（按课程着色：C语言蓝 / 电路橙 / STM32 绿）
const GRAPH_NODES: GraphNode[] = [
  { id: "c1", name: "变量与类型", color: "#3b82f6", angle: 0, radius: 2.2, y: 0.6 },
  { id: "c2", name: "指针与内存", color: "#60a5fa", angle: 45, radius: 2.4, y: -0.3 },
  { id: "c3", name: "位运算", color: "#93c5fd", angle: 90, radius: 2.0, y: 0.4 },
  { id: "e1", name: "分压电路", color: "#f97316", angle: 135, radius: 2.3, y: -0.2 },
  { id: "e2", name: "RC 充放电", color: "#fb923c", angle: 180, radius: 2.1, y: 0.5 },
  { id: "s1", name: "GPIO 控制", color: "#22c55e", angle: 225, radius: 2.5, y: -0.4 },
  { id: "s2", name: "定时器 PWM", color: "#4ade80", angle: 270, radius: 2.2, y: 0.3 },
  { id: "s3", name: "ADC 采样", color: "#86efac", angle: 315, radius: 2.4, y: 0.1 },
];

function GraphNodeMesh({ node, hovered, onHover }: {
  node: GraphNode;
  hovered: boolean;
  onHover: (id: string | null) => void;
}) {
  const ref = useRef<THREE.Mesh>(null);
  useFrame((state) => {
    if (!ref.current) return;
    // 节点轻微呼吸发光
    const pulse = 1 + Math.sin(state.clock.elapsedTime * 2 + node.angle) * 0.08;
    ref.current.scale.setScalar(hovered ? pulse * 1.5 : pulse);
  });

  return (
    <group position={[
      Math.cos((node.angle * Math.PI) / 180) * node.radius,
      node.y,
      Math.sin((node.angle * Math.PI) / 180) * node.radius,
    ]}>
      {/* 发光球体 */}
      <mesh
        ref={ref}
        onPointerOver={(e) => { e.stopPropagation(); onHover(node.id); }}
        onPointerOut={() => onHover(null)}
      >
        <sphereGeometry args={[0.16, 24, 24]} />
        <meshStandardMaterial
          color={node.color}
          emissive={node.color}
          emissiveIntensity={hovered ? 2.2 : 1.1}
          transparent
          opacity={0.92}
        />
      </mesh>
      {/* 全息标签（Html 悬浮） */}
      <Html position={[0, 0.32, 0]} center distanceFactor={9} pointerEvents="none">
        <div
          className="text-[10px] whitespace-nowrap px-2 py-0.5 rounded-full"
          style={{
            color: "#e2e8f0",
            background: "rgba(15,23,42,0.72)",
            border: `1px solid ${node.color}66`,
            textShadow: "0 0 6px rgba(0,0,0,0.8)",
            backdropFilter: "blur(2px)",
          }}
        >
          {node.name}
        </div>
      </Html>
    </group>
  );
}

function HoloGraph() {
  const group = useRef<THREE.Group>(null);
  const [hovered, setHovered] = useState<string | null>(null);

  // 连线（中心 → 节点 + 相邻节点环）
  const lines = useMemo(() => {
    const segs: [number, number, number][] = [];
    GRAPH_NODES.forEach((n) => {
      const a = (n.angle * Math.PI) / 180;
      segs.push([Math.cos(a) * n.radius, n.y, Math.sin(a) * n.radius]);
    });
    return segs;
  }, []);

  useFrame((state) => {
    if (!group.current) return;
    // 整体缓慢旋转 + 轻微浮动
    group.current.rotation.y = state.clock.elapsedTime * 0.12;
    group.current.position.y = Math.sin(state.clock.elapsedTime * 0.5) * 0.15;
  });

  return (
    <group ref={group}>
      {/* 中心核心球 */}
      <mesh>
        <sphereGeometry args={[0.34, 32, 32]} />
        <meshStandardMaterial
          color="#818cf8"
          emissive="#6366f1"
          emissiveIntensity={1.6}
          transparent
          opacity={0.9}
        />
      </mesh>
      {/* 数据流粒子（沿节点环） */}
      <Sparkles count={60} scale={[5, 3, 5]} size={2} speed={0.4} color="#93c5fd" />
      {/* 连线：中心到节点 */}
      {lines.map((p, i) => (
        <line key={`l${i}`}>
          <bufferGeometry>
            <bufferAttribute
              attach="attributes-position"
              args={[new Float32Array([0, 0, 0, p[0], p[1], p[2]]), 3]}
            />
          </bufferGeometry>
          <lineBasicMaterial color={GRAPH_NODES[i].color} transparent opacity={0.45} />
        </line>
      ))}
      {/* 节点环连线 */}
      {GRAPH_NODES.map((n, i) => {
        const n2 = GRAPH_NODES[(i + 1) % GRAPH_NODES.length];
        const a1 = (n.angle * Math.PI) / 180;
        const a2 = (n2.angle * Math.PI) / 180;
        const p1 = [Math.cos(a1) * n.radius, n.y, Math.sin(a1) * n.radius];
        const p2 = [Math.cos(a2) * n2.radius, n2.y, Math.sin(a2) * n2.radius];
        return (
          <line key={`ring${i}`}>
            <bufferGeometry>
              <bufferAttribute
                attach="attributes-position"
                args={[new Float32Array([...p1, ...p2]), 3]}
              />
            </bufferGeometry>
            <lineBasicMaterial color="#94a3b8" transparent opacity={0.22} />
          </line>
        );
      })}
      {/* 节点 */}
      {GRAPH_NODES.map((n) => (
        <GraphNodeMesh key={n.id} node={n} hovered={hovered === n.id} onHover={setHovered} />
      ))}
    </group>
  );
}

/* ================= 漂浮全息碎片卡 ================= */

function HoloCard({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return (
    <div
      className={`holo-card rounded-2xl p-4 text-left ${className}`}
      style={{
        background: "rgba(17,24,39,0.68)",
        border: "1px solid rgba(148,163,184,0.35)",
        boxShadow: "0 0 24px rgba(99,102,241,0.18), inset 0 0 18px rgba(99,102,241,0.08)",
        backdropFilter: "blur(10px)",
        color: "#f1f5f9",
      }}
    >
      {children}
    </div>
  );
}

function FloatingCard({
  data, navigate,
}: {
  data: HoloData;
  navigate: (r: string) => void;
}) {
  // 5 张碎片卡的配置（位置 / 内容 / 跳转）
  const cards: {
    id: string; route: string;
    position: [number, number, number];
    rotation: [number, number, number];
    floatSpeed: number; floatIntensity: number;
    render: () => React.ReactNode;
  }[] = [
    {
      id: "mastery", route: "/learning-path",
      position: [-3.4, 1.5, -1.2], rotation: [0.1, 0.5, -0.05],
      floatSpeed: 1.1, floatIntensity: 0.45,
      render: () => (
        <HoloCard className="w-[210px]">
          <div className="text-[10px] text-slate-400 uppercase tracking-widest">知识掌握</div>
          <div className="flex items-center gap-3 mt-2">
            <AnimatedRing percent={Math.min(100, Math.round((data.masteredKps / 20) * 100))} size={64} strokeWidth={7} color="#818cf8" trackColor="rgba(255,255,255,0.12)">
              <span className="text-white text-sm font-bold"><CountUp value={data.masteredKps} duration={1.2} /></span>
            </AnimatedRing>
            <div className="text-[10px] text-slate-300">已掌握知识点<br /><span className="text-white text-sm font-semibold">{data.masteredKps}/20</span></div>
          </div>
        </HoloCard>
      ),
    },
    {
      id: "weekly", route: "/personal",
      position: [3.6, 1.2, -1.5], rotation: [-0.08, -0.5, 0.06],
      floatSpeed: 0.9, floatIntensity: 0.5,
      render: () => (
        <HoloCard className="w-[190px]">
          <div className="text-[10px] text-slate-400 uppercase tracking-widest">本周学习</div>
          <div className="text-3xl font-bold text-white mt-1"><CountUp value={data.weeklyHours} duration={1.4} /><span className="text-base text-slate-300 ml-1">h</span></div>
          <div className="flex gap-3 mt-2 text-[10px] text-slate-300">
            <span>🔥 {data.streakDays} 天</span>
            <span>⏱ 今日 {data.todayMin}m</span>
          </div>
        </HoloCard>
      ),
    },
    {
      id: "path", route: "/learning-path",
      position: [-2.6, -1.4, -2.2], rotation: [0.05, 0.7, 0.04],
      floatSpeed: 1.3, floatIntensity: 0.4,
      render: () => (
        <HoloCard className="w-[220px]">
          <div className="text-[10px] text-slate-400 uppercase tracking-widest">学习路径 · ADPP</div>
          <div className="flex justify-between text-[11px] mt-2 text-slate-300">
            <span>{data.pathNodes} 知识点</span>
            <span>{Math.round(data.pathProgress)}%</span>
          </div>
          <Progress percent={Math.round(data.pathProgress)} showInfo={false} strokeColor={{ "0%": "#818cf8", "100%": "#34d399" }} trailColor="rgba(255,255,255,0.12)" size="small" className="mt-1.5" />
        </HoloCard>
      ),
    },
    {
      id: "rank", route: "/leaderboard",
      position: [3.2, -1.2, -2.4], rotation: [-0.06, -0.6, -0.04],
      floatSpeed: 1.0, floatIntensity: 0.55,
      render: () => (
        <HoloCard className="w-[190px]">
          <div className="text-[10px] text-slate-400 uppercase tracking-widest">成就 · 排行</div>
          <div className="mt-2 space-y-1.5">
            {(data.topRankers.length ? data.topRankers : [
              { name: "排行榜加载中", score: 0 },
            ]).map((r, i) => (
              <div key={i} className="flex items-center gap-2 text-[11px]">
                <span className="text-amber-300">{["🥇", "🥈", "🥉"][i] ?? "·"}</span>
                <span className="text-slate-200 flex-1 truncate">{r.name}</span>
                <span className="text-slate-400">{r.score}</span>
              </div>
            ))}
          </div>
        </HoloCard>
      ),
    },
    {
      id: "quiz", route: "/learning-path",
      position: [0, -2.3, -1.8], rotation: [0.1, 0.1, 0],
      floatSpeed: 1.2, floatIntensity: 0.35,
      render: () => (
        <HoloCard className="w-[200px]">
          <div className="text-[10px] text-slate-400 uppercase tracking-widest">每日练习</div>
          <div className="mt-1 text-sm text-slate-200">
            已练 <span className="text-white font-bold text-lg"><CountUp value={data.quizTotal} duration={1.2} /></span> 题
          </div>
          <div className="text-[10px] text-slate-400 mt-1">覆盖 {data.quizCovered} 个知识点 · Lv.{data.level} · {data.points} 积分</div>
        </HoloCard>
      ),
    },
  ];

  return (
    <>
      {cards.map((c) => (
        <Float
          key={c.id}
          speed={c.floatSpeed}
          rotationIntensity={0.15}
          floatIntensity={Math.min(c.floatIntensity, 0.28)}
        >
          <group position={c.position} rotation={c.rotation}>
            <Html transform occlude="blending" distanceFactor={10} wrapperClass="holo-wrap" zIndexRange={[20, 0]}>
              <div
                className="holo-click-zone cursor-pointer transition-transform duration-300 hover:scale-105"
                onPointerDown={(e) => { e.stopPropagation(); navigate(c.route); }}
              >
                {c.render()}
              </div>
            </Html>
          </group>
        </Float>
      ))}
    </>
  );
}

/* ================= 主组件 ================= */

const HoloSpace: React.FC<{ data: HoloData }> = ({ data }) => {
  const navigate = useNavigate();

  return (
    <div className="relative w-full h-[calc(100vh-140px)] min-h-[560px] rounded-2xl overflow-hidden border border-slate-800/50">
      {/* 顶部标题 */}
      <div className="absolute top-4 left-1/2 -translate-x-1/2 z-30 text-center pointer-events-none">
        <div className="text-xs tracking-[0.3em] text-indigo-300/80 uppercase">LearnLab · 全息学习空间</div>
        <h2 className="text-lg md:text-xl font-bold text-white mt-1 drop-shadow-[0_0_12px_rgba(99,102,241,0.7)]">
          知识在空间中漂浮，点击碎片查看
        </h2>
      </div>

      <Canvas
        camera={{ position: [0, 1.2, 7.5], fov: 55 }}
        gl={{ antialias: true, alpha: true }}
        dpr={[1, 2]}
      >
        {/* 柔和深空氛围（非纯黑） */}
        <color attach="background" args={["#0b1026"]} />
        <fog attach="fog" args={["#0b1026", 9, 20]} />

        {/* 灯光 */}
        <ambientLight intensity={0.5} color="#e2e8f0" />
        <directionalLight position={[5, 8, 6]} intensity={1.0} color="#ffffff" />
        <pointLight position={[-5, 2, -3]} intensity={24} color="#6366f1" />
        <pointLight position={[5, -1, -4]} intensity={20} color="#22d3ee" />
        <pointLight position={[0, 4, 2]} intensity={14} color="#a78bfa" />

        {/* 漂浮尘埃粒子 */}
        <Sparkles count={160} scale={[14, 8, 10]} size={2.2} speed={0.3} color="#a5b4fc" opacity={0.55} />

        {/* 中央知识图谱全息 */}
        <HoloGraph />

        {/* 漂浮碎片卡 */}
        <FloatingCard data={data} navigate={(r) => navigate(r)} />

        {/* 拖拽旋转 */}
        <OrbitControls
          enablePan={false}
          enableZoom={false}
          minPolarAngle={Math.PI / 3.2}
          maxPolarAngle={Math.PI / 1.7}
          target={[0, 0.1, 0]}
          autoRotate
          autoRotateSpeed={0.4}
        />
      </Canvas>

      {/* 底部提示 */}
      <div className="absolute bottom-4 left-1/2 -translate-x-1/2 z-30 text-[11px] text-slate-400/80 pointer-events-none">
        🖱️ 拖拽旋转场景 · 悬停查看 · 点击碎片进入功能
      </div>

      {/* 全息卡样式注入 */}
      <style>{`
        .holo-wrap {
          pointer-events: auto !important;
        }
        .holo-click-zone {
          padding: 14px;
          margin: -14px;
          pointer-events: auto;
        }
        .holo-card {
          transition: box-shadow 0.3s ease, border-color 0.3s ease;
          pointer-events: none;
        }
        .holo-card:hover {
          border-color: rgba(129,140,248,0.75);
          box-shadow: 0 0 34px rgba(99,102,241,0.42), inset 0 0 20px rgba(99,102,241,0.14);
        }
      `}</style>
    </div>
  );
};

export default HoloSpace;
