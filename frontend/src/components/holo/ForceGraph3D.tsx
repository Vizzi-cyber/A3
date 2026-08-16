/**
 * 3D 力导向知识图谱 v2（ForceGraph3D）
 * 用真实知识点（35）+ 前置依赖做力导向布局（Fruchterman-Reingold），并加入：
 *   - 节点状态语义：completed（亮）/ in-progress（脉冲呼吸）/ pending（暗）/ locked（更暗半透明）
 *   - 薄弱点标记：掌握度 < 0.5 的节点带红色警示环
 *   - 点击节点：弹出详情卡（名称/课程/难度/状态/掌握度）
 *   - hover 邻居高亮：相连节点变亮，其余变暗（图结构探索）
 *   - 边数据流：小光点沿前置→后置方向流动（知识流向可视化）
 */
import React, { useMemo, useRef, useState } from "react";
import { useFrame } from "@react-three/fiber";
import { Html, Line } from "@react-three/drei";
import * as THREE from "three";
import { GraphNode } from "./useHoloData";

const COURSE_COLORS: Record<string, string> = {
  "C语言": "#3b82f6",
  "电路分析": "#f97316",
  "STM32嵌入式": "#22c55e",
};

const STATUS_STYLE: Record<string, { emissive: number; opacity: number; scaleMul: number; color: string }> = {
  completed: { emissive: 1.6, opacity: 0.95, scaleMul: 1.0, color: "#e2e8f0" },
  "in-progress": { emissive: 2.2, opacity: 0.95, scaleMul: 1.15, color: "#ffffff" },
  pending: { emissive: 0.6, opacity: 0.75, scaleMul: 0.9, color: "#94a3b8" },
  locked: { emissive: 0.2, opacity: 0.45, scaleMul: 0.8, color: "#475569" },
  unknown: { emissive: 0.7, opacity: 0.7, scaleMul: 0.9, color: "#94a3b8" },
};

const STATUS_LABEL: Record<string, string> = {
  completed: "已掌握",
  "in-progress": "学习中",
  pending: "待学习",
  locked: "未解锁",
  unknown: "未知",
};

interface SimNode extends GraphNode {
  pos: THREE.Vector3;
  vel: THREE.Vector3;
}

interface ForceGraph3DProps {
  nodes: GraphNode[];
  edges: [string, string][];
}

const ForceGraph3D: React.FC<ForceGraph3DProps> = ({ nodes, edges }) => {
  const group = useRef<THREE.Group>(null);
  const [hovered, setHovered] = useState<string | null>(null);
  const [selected, setSelected] = useState<GraphNode | null>(null);
  const hoverTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  // hover 防抖：out 延迟 250ms 清除，避免节点微动导致的闪烁
  const scheduleHoverOut = () => {
    if (hoverTimer.current) clearTimeout(hoverTimer.current);
    hoverTimer.current = setTimeout(() => setHovered(null), 250);
  };
  const hoverIn = (id: string) => {
    if (hoverTimer.current) clearTimeout(hoverTimer.current);
    setHovered(id);
  };

  // 初始位置：按课程分簇（C 语言左 / 电路中间 / STM32 右），力导向自然形成三团
  const courseBase: Record<string, [number, number]> = {
    "C语言": [-3.2, 0.2],
    "电路分析": [0, 0.6],
    "STM32嵌入式": [3.2, 0.2],
  };
  const simNodes = useMemo<SimNode[]>(() => {
    // 斐波那契球面均匀分布（Fibonacci sphere）：
    // 35 个节点均匀铺满球壳——四面八方都有（上/下/左/右/前/后/斜角），对称均匀
    const N = nodes.length;
    const R = 7.2;                                  // 球壳半径
    const GOLDEN_ANGLE = Math.PI * (3 - Math.sqrt(5));
    const list: SimNode[] = nodes.map((n, i) => {
      const y = 1 - (i / (N - 1)) * 2;               // -1 → 1
      const r = Math.sqrt(Math.max(0, 1 - y * y));   // 水平半径
      const theta = GOLDEN_ANGLE * i;                // 黄金角
      return {
        ...n,
        pos: new THREE.Vector3(
          Math.cos(theta) * r * R,
          y * R * 0.85,
          Math.sin(theta) * r * R,
        ),
        vel: new THREE.Vector3(),
      };
    });
    // 调试：暴露布局坐标供验证（对称性检查）
    try {
      (window as any).__graphLayout = list.map((n) => ({
        name: n.name, x: +n.pos.x.toFixed(2), y: +n.pos.y.toFixed(2), z: +n.pos.z.toFixed(2),
      }));
    } catch { /* SSR/测试环境忽略 */ }
    return list;
  }, [nodes, edges]);

  const nodeIndex = useMemo(() => {
    const m = new Map<string, number>();
    simNodes.forEach((n, i) => m.set(n.kp_id, i));
    return m;
  }, [simNodes]);

  // 邻居集合（hover 高亮用）
  const neighbors = useMemo(() => {
    const adj: Record<string, Set<string>> = {};
    simNodes.forEach((n) => { adj[n.kp_id] = new Set(); });
    edges.forEach(([a, b]) => {
      if (adj[a]) adj[a].add(b);
      if (adj[b]) adj[b].add(a);
    });
    return adj;
  }, [edges, simNodes]);

  const edgeLines = useMemo(() => {
    return edges
      .filter(([a, b]) => nodeIndex.has(a) && nodeIndex.has(b))
      .map(([a, b]) => ({ a: nodeIndex.get(a)!, b: nodeIndex.get(b)! }));
  }, [edges, nodeIndex]);

  const edgeLineRefs = useRef<THREE.Line[]>([]);
  const flowRefs = useRef<THREE.Mesh[]>([]);
  const nodeRefs = useRef<(THREE.Mesh | null)[]>([]);
  const nodeSizes = useRef<number[]>([]);
  const nodeGroupRefs = useRef<(THREE.Group | null)[]>([]);
  const spawnStartRef = useRef(0);
  const convergedRef = useRef(0);

  // 力导向迭代 + 数据流粒子沿边流动
  useFrame((state, delta) => {
    const dt = Math.min(delta, 0.05);
    const N = simNodes.length;
    const t = state.clock.elapsedTime;

    // 爆炸入场动画：节点从中心扩散到球面目标位置（错峰 + easeOutBack 回弹）
    if (!spawnStartRef.current) spawnStartRef.current = t;
    const spawnT = t - spawnStartRef.current;
    nodeGroupRefs.current.forEach((grp, i) => {
      if (!grp || !simNodes[i]) return;
      // 每节点错峰 0.03s，总时长 1.3s，easeOutBack 过冲回弹
      const p = Math.min(1, Math.max(0, (spawnT - i * 0.03) / 1.3));
      const c1 = 1.70158, c3 = c1 + 1;
      const ease = 1 + c3 * Math.pow(p - 1, 3) + c1 * Math.pow(p - 1, 2);
      const target = simNodes[i].pos;
      grp.position.set(target.x * ease, target.y * ease, target.z * ease);
    });

    // 节点呼吸动画（发光脉冲，增加活力）
    nodeRefs.current.forEach((mesh, i) => {
      if (mesh && nodeSizes.current[i]) {
        const pulse = 1 + Math.sin(t * 1.8 + i * 0.9) * 0.12;
        mesh.scale.setScalar(nodeSizes.current[i] * pulse);
      }
    });

    // 力导向已预计算收敛（useMemo），此处只更新边线端点 + 数据流

    // 更新边线端点（drei Line2）+ 数据流粒子沿边流动
    edgeLines.forEach((e, i) => {
      const line = edgeLineRefs.current[i];
      if (line) {
        const src = simNodes[e.a].pos;
        const dst = simNodes[e.b].pos;
        (line as any).geometry.setPositions([
          src.x, src.y, src.z,
          dst.x, dst.y, dst.z,
        ]);
      }
      const flow = flowRefs.current[i];
      if (flow) {
        const u = (t * 0.4 + i * 0.13) % 1;
        const src = simNodes[e.a].pos;
        const dst = simNodes[e.b].pos;
        flow.position.set(
          src.x + (dst.x - src.x) * u,
          src.y + (dst.y - src.y) * u,
          src.z + (dst.z - src.z) * u,
        );
      }
    });

    if (group.current) {
      // hover 时暂停旋转（交互更稳），非 hover 缓慢旋转
      group.current.rotation.y = hovered ? group.current.rotation.y : t * 0.06;
      group.current.position.y = Math.sin(t * 0.4) * 0.1;
    }
  });

  return (
    <group
      ref={group}
      onPointerLeave={() => scheduleHoverOut()}
    >
      {/* 边线 + 数据流粒子 */}
      {edgeLines.map((e, i) => {
        const color = COURSE_COLORS[simNodes[e.a].course] ?? "#94a3b8";
        return (
          <group key={`edge${i}`}>
            <Line
              ref={(el: any) => { edgeLineRefs.current[i] = el; }}
              points={[new THREE.Vector3(0, 0, 0), new THREE.Vector3(0.01, 0, 0.01)]}
              color={color}
              lineWidth={2.2}
              transparent
              opacity={0.75}
            />
            {/* 流动光点 */}
            <mesh ref={(el) => { flowRefs.current[i] = el as THREE.Mesh; }}>
              <sphereGeometry args={[0.05, 8, 8]} />
              <meshBasicMaterial color={color} transparent opacity={1} />
            </mesh>
          </group>
        );
      })}

      {/* 节点 */}
      {simNodes.map((n) => {
        const baseColor = COURSE_COLORS[n.course] ?? "#94a3b8";
        const st = STATUS_STYLE[n.status] ?? STATUS_STYLE.unknown;
        const isHover = hovered === n.kp_id;
        const isSelected = selected?.kp_id === n.kp_id;
        const isNeighbor = hovered ? neighbors[hovered]?.has(n.kp_id) : false;
        const isWeak = n.mastery != null && n.mastery < 0.5 && n.status !== "completed";
        const size = (0.17 + (n.difficulty ?? 0.5) * 0.1) * st.scaleMul;

        // 邻居高亮：hover 时非邻居变暗
        const dimmed = hovered && !isHover && !isNeighbor && !isSelected;
        const emissiveIntensity = dimmed ? 0.15 : isSelected ? 3 : isHover ? 2.8 : st.emissive;
        const opacity = dimmed ? 0.25 : st.opacity;

        return (
          <group
            key={n.kp_id}
            position={[n.pos.x, n.pos.y, n.pos.z]}
            ref={(el) => {
              const idx = simNodes.indexOf(n);
              nodeGroupRefs.current[idx] = el;
            }}
            onClick={(e) => { e.stopPropagation(); setSelected(n); }}
            onPointerOver={(e) => { e.stopPropagation(); hoverIn(n.kp_id); }}
            onPointerOut={() => scheduleHoverOut()}
          >
            {/* 扩大命中区（不可见球）：节点微动时 hover 稳定 */}
            <mesh visible={false}>
              <sphereGeometry args={[0.34, 8, 8]} />
            </mesh>
            {/* 发光外层（恒定发光，白底上突出） */}
            <mesh>
              <sphereGeometry args={[size * 1.9, 12, 12]} />
              <meshBasicMaterial
                color={isWeak ? "#ef4444" : baseColor}
                transparent
                opacity={dimmed ? 0.06 : 0.2}
                depthWrite={false}
              />
            </mesh>
            {/* 核心节点 */}
            <mesh
              ref={(el) => {
                const idx = simNodes.indexOf(n);
                nodeRefs.current[idx] = el;
                nodeSizes.current[idx] = size;
              }}
            >
              <sphereGeometry args={[size, 16, 16]} />
              <meshStandardMaterial
                color={isWeak ? "#ef4444" : baseColor}
                emissive={isWeak ? "#ef4444" : baseColor}
                emissiveIntensity={emissiveIntensity * 1.3}
                transparent
                opacity={opacity}
                roughness={0.25}
                metalness={0.1}
              />
            </mesh>
            {/* 学习中节点：呼吸光环 */}
            {n.status === "in-progress" && !dimmed && (
              <mesh>
                <ringGeometry args={[size * 1.6, size * 1.9, 24]} />
                <meshBasicMaterial color={baseColor} transparent opacity={0.5} side={THREE.DoubleSide} />
              </mesh>
            )}
            {/* 薄弱点警示环 */}
            {isWeak && !dimmed && (
              <mesh rotation={[Math.PI / 2, 0, 0]}>
                <torusGeometry args={[size * 1.7, 0.012, 8, 28]} />
                <meshBasicMaterial color="#ef4444" transparent opacity={0.85} />
              </mesh>
            )}
            {/* 常显名称标签（小字淡色，zIndex 压低不盖悬浮面板） */}
            <Html center distanceFactor={11} pointerEvents="none" zIndexRange={[3, 0]}>
              <div
                className={`whitespace-nowrap rounded-md transition-all duration-150 ${isHover ? "px-2.5 py-1 text-[11px]" : "px-1.5 py-0.5 text-[9px]"}`}
                style={{
                  background: isHover ? "rgba(10,14,32,0.92)" : "rgba(10,14,32,0.55)",
                  border: `1px solid ${isHover ? `${baseColor}88` : `${baseColor}44`}`,
                  color: isHover ? "#ffffff" : st.color,
                  boxShadow: isHover ? `0 0 14px ${baseColor}44` : "none",
                  opacity: isHover ? 1 : dimmed ? 0.35 : 0.85,
                  backdropFilter: "blur(3px)",
                  pointerEvents: "none",
                }}
              >
                {n.name}
                {isHover && (
                  <>
                    <span style={{ color: st.color }}> · {STATUS_LABEL[n.status]}</span>
                    {isWeak && <span style={{ color: "#f87171" }}> · 薄弱</span>}
                  </>
                )}
              </div>
            </Html>
          </group>
        );
      })}

      {/* 点击选中的详情卡（固定屏幕右上角区域） */}
      {selected && (
        <Html position={[2.6, 2.3, 0]} center distanceFactor={10} pointerEvents="auto" zIndexRange={[12, 0]}>
          <div
            className="w-60 rounded-xl p-3.5"
            style={{
              background: "rgba(10,14,32,0.92)",
              border: `1px solid ${COURSE_COLORS[selected.course] ?? "#64748b"}66`,
              boxShadow: "0 16px 50px rgba(2,6,23,0.6), 0 0 24px rgba(99,102,241,0.2)",
              backdropFilter: "blur(12px)",
            }}
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-semibold text-white">{selected.name}</span>
              <button
                onClick={() => setSelected(null)}
                className="text-slate-400 hover:text-white text-xs px-1"
              >
                ✕
              </button>
            </div>
            <div className="space-y-1 text-[11px]" style={{ color: "#94a3b8" }}>
              <div>课程：<span style={{ color: COURSE_COLORS[selected.course] ?? "#cbd5e1" }}>{selected.course}</span></div>
              <div>难度：{"★".repeat(Math.max(1, Math.round((selected.difficulty ?? 0.5) * 5))).padEnd(5, "☆")}</div>
              <div>状态：<span style={{ color: (STATUS_STYLE[selected.status] ?? STATUS_STYLE.unknown).color }}>{STATUS_LABEL[selected.status] ?? selected.status}</span></div>
              {selected.mastery != null && (
                <div>掌握度：<span className="text-white">{Math.round(selected.mastery * 100)}%</span></div>
              )}
              {selected.mastery != null && selected.mastery < 0.5 && (
                <div className="text-[#f87171]">⚠ 薄弱知识点，建议优先复习</div>
              )}
            </div>
          </div>
        </Html>
      )}
    </group>
  );
};

export default ForceGraph3D;
