/**
 * 学科空间 3D 物体构建器
 * 用 three.js 几何体组合出 stylized 风格物体（书本/芯片/电路板/奖杯/星球/雷达/数据柱），
 * 机器人使用真实 GLTF 模型（RobotExpressive.glb）。
 * 每个物体返回 Group，支持 hover 高亮（emissive）与点击交互。
 */
import * as THREE from "three";

export interface SpaceObjectDef {
  id: string;
  label: string;
  desc: string;
  color: string;
  emissive: string;
  route: string;
  position: [number, number, number];
  scale?: number;
}

/** 材质工具：统一标准材质，支持 hover 发光 */
function mat(color: string, emissive = "#000000", emissiveIntensity = 0): THREE.MeshStandardMaterial {
  return new THREE.MeshStandardMaterial({
    color,
    emissive,
    emissiveIntensity,
    roughness: 0.35,
    metalness: 0.3,
  });
}

/** 书本：封面 + 书页 + 书脊 */
function buildBook(color: string, emissive: string): THREE.Group {
  const g = new THREE.Group();
  const cover = new THREE.Mesh(new THREE.BoxGeometry(1.6, 0.12, 1.2), mat(color, emissive, 0.25));
  cover.position.y = 0.06;
  const pages = new THREE.Mesh(new THREE.BoxGeometry(1.5, 0.08, 1.1), mat("#f8fafc"));
  pages.position.y = 0.02;
  const spine = new THREE.Mesh(new THREE.BoxGeometry(0.14, 0.1, 1.16), mat("#e2e8f0"));
  spine.position.x = -0.75;
  g.add(cover, pages, spine);
  return g;
}

/** 芯片：基板 + 针脚 + 发光核心 */
function buildChip(color: string, emissive: string): THREE.Group {
  const g = new THREE.Group();
  const base = new THREE.Mesh(new THREE.BoxGeometry(1.8, 0.14, 1.8), mat("#1e293b"));
  const die = new THREE.Mesh(new THREE.BoxGeometry(0.9, 0.06, 0.9), mat(color, emissive, 1.2));
  die.position.y = 0.1;
  const pinGeo = new THREE.BoxGeometry(0.08, 0.18, 0.08);
  const pinM = mat("#cbd5e1", "#fbbf24", 0.5);
  for (let i = -0.6; i <= 0.6; i += 0.3) {
    for (const [x, z] of [[i, -0.95], [i, 0.95], [-0.95, i], [0.95, i]] as const) {
      const pin = new THREE.Mesh(pinGeo, pinM);
      pin.position.set(x, -0.13, z);
      g.add(pin);
    }
  }
  g.add(base, die);
  return g;
}

/** 电路板：板 + 圆柱元件 + 发光 LED */
function buildBoard(color: string, emissive: string): THREE.Group {
  const g = new THREE.Group();
  const board = new THREE.Mesh(new THREE.BoxGeometry(2.4, 0.08, 1.8), mat("#064e3b"));
  const capGeo = new THREE.CylinderGeometry(0.14, 0.14, 0.2, 16);
  for (const [x, z] of [[-0.7, -0.5], [0.6, 0.4], [-0.3, 0.6], [0.8, -0.6]] as const) {
    const cap = new THREE.Mesh(capGeo, mat("#334155"));
    cap.position.set(x, 0.12, z);
    g.add(cap);
  }
  const led = new THREE.Mesh(new THREE.SphereGeometry(0.1, 12, 12), mat(color, emissive, 2));
  led.position.set(0.9, 0.1, 0.6);
  const trace = new THREE.Mesh(new THREE.BoxGeometry(2.3, 0.02, 1.7), mat(color, emissive, 0.4));
  trace.position.y = 0.05;
  g.add(board, led, trace);
  return g;
}

/** 奖杯：底座 + 杯身 + 杯口 */
function buildTrophy(color: string, emissive: string): THREE.Group {
  const g = new THREE.Group();
  const base = new THREE.Mesh(new THREE.BoxGeometry(0.7, 0.12, 0.7), mat("#92400e", emissive, 0.3));
  const stem = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.12, 0.5), mat(color, emissive, 0.35));
  stem.position.y = 0.31;
  const cup = new THREE.Mesh(new THREE.CylinderGeometry(0.38, 0.18, 0.6, 20), mat(color, emissive, 0.6));
  cup.position.y = 0.8;
  const rim = new THREE.Mesh(new THREE.TorusGeometry(0.38, 0.05, 12, 28), mat("#fbbf24", "#fde68a", 0.7));
  rim.position.y = 1.08;
  rim.rotation.x = Math.PI / 2;
  g.add(base, stem, cup, rim);
  return g;
}

/** 星球：球体 + 轨道环 + 卫星 */
function buildPlanet(color: string, emissive: string): THREE.Group {
  const g = new THREE.Group();
  const sphere = new THREE.Mesh(new THREE.SphereGeometry(0.8, 32, 32), mat(color, emissive, 0.55));
  const ring = new THREE.Mesh(new THREE.TorusGeometry(1.2, 0.04, 12, 48), mat("#94a3b8", emissive, 0.25));
  ring.rotation.x = Math.PI / 2.4;
  const moon = new THREE.Mesh(new THREE.SphereGeometry(0.14, 16, 16), mat("#cbd5e1", "#f8fafc", 0.5));
  moon.position.set(1.5, 0.25, 0);
  g.add(sphere, ring, moon);
  return g;
}

/** 雷达：圆环 + 旋转扫描线 */
function buildRadar(color: string, emissive: string): THREE.Group {
  const g = new THREE.Group();
  const ring = new THREE.Mesh(new THREE.TorusGeometry(0.7, 0.05, 12, 40), mat(color, emissive, 0.5));
  ring.rotation.x = Math.PI / 2;
  const inner = new THREE.Mesh(new THREE.TorusGeometry(0.45, 0.03, 10, 32), mat("#475569", emissive, 0.2));
  inner.rotation.x = Math.PI / 2;
  // 扫描扇形（自定义几何体）
  const sectorGeo = new THREE.BufferGeometry();
  const vertices: number[] = [0, 0, 0];
  const n = 24;
  for (let i = 0; i <= n; i++) {
    const a = (i / n) * Math.PI * 0.5;
    vertices.push(Math.cos(a) * 0.7, 0, Math.sin(a) * 0.7);
  }
  sectorGeo.setAttribute("position", new THREE.Float32BufferAttribute(vertices, 3));
  const sector = new THREE.Mesh(sectorGeo, new THREE.MeshBasicMaterial({
    color: emissive, transparent: true, opacity: 0.35, side: THREE.DoubleSide,
  }));
  g.add(ring, inner, sector);
  // 存扫描线引用（用于动画）
  (g as any).sector = sector;
  return g;
}

/** 数据柱：圆柱阵列（学情/数据入口） */
function buildBars(color: string, emissive: string): THREE.Group {
  const g = new THREE.Group();
  const heights = [0.9, 1.4, 0.6, 1.1];
  heights.forEach((h, i) => {
    const bar = new THREE.Mesh(
      new THREE.CylinderGeometry(0.16, 0.16, h, 16),
      mat(i === 1 ? color : "#475569", i === 1 ? emissive : "#000000", i === 1 ? 0.8 : 0),
    );
    bar.position.set((i - 1.5) * 0.5, h / 2, 0);
    g.add(bar);
  });
  const base = new THREE.Mesh(new THREE.BoxGeometry(2.2, 0.08, 0.9), mat("#334155"));
  base.position.y = 0.04;
  g.add(base);
  return g;
}

/** 构建单个物体 */
export function buildObject(def: SpaceObjectDef): THREE.Group {
  let obj: THREE.Group;
  switch (def.id) {
    case "learning-path": obj = buildBook(def.color, def.emissive); break;
    case "c-language": obj = buildChip(def.color, def.emissive); break;
    case "circuit": obj = buildBoard(def.color, def.emissive); break;
    case "achievements": obj = buildTrophy(def.color, def.emissive); break;
    case "challenges": obj = buildPlanet(def.color, def.emissive); break;
    case "personal": obj = buildRadar(def.color, def.emissive); break;
    case "analytics": obj = buildBars(def.color, def.emissive); break;
    default: obj = buildBook(def.color, def.emissive);
  }
  obj.userData = { id: def.id, label: def.label, desc: def.desc, route: def.route, color: def.color };
  if (def.scale) obj.scale.setScalar(def.scale);
  obj.position.set(def.position[0], def.position[1], def.position[2]);
  // 不可见命中球：扩大 raycast 命中面积（物体悬浮动画时点击/悬停稳定）
  const hitbox = new THREE.Mesh(
    new THREE.SphereGeometry(2.0, 8, 8),
    new THREE.MeshBasicMaterial({ visible: false }),
  );
  hitbox.position.set(0, 0.1, 0);
  hitbox.userData.hitbox = true;
  obj.add(hitbox);
  return obj;
}

/** 空间入口物体清单（8 个） */
export const SPACE_OBJECTS: SpaceObjectDef[] = [
  {
    id: "learning-path", label: "学习路径", desc: "ADPP 自适应路径规划",
    color: "#6366f1", emissive: "#818cf8", route: "/learning-path",
    position: [-3.6, 0.4, -2.5], scale: 1.15,
  },
  {
    id: "c-language", label: "C语言中心", desc: "芯片级编程训练",
    color: "#3b82f6", emissive: "#60a5fa", route: "/resources",
    position: [-2.1, -0.1, -4.2], scale: 1.0,
  },
  {
    id: "circuit", label: "电路仿真", desc: "MNA 虚拟实验",
    color: "#f97316", emissive: "#fb923c", route: "/circuit-simulator",
    position: [2.1, 0.2, -4.2], scale: 1.0,
  },
  {
    id: "achievements", label: "成就排行", desc: "六维积分榜",
    color: "#f59e0b", emissive: "#fbbf24", route: "/leaderboard",
    position: [3.6, 0.5, -2.5], scale: 1.15,
  },
  {
    id: "challenges", label: "知识冒险", desc: "游戏化学习地图",
    color: "#10b981", emissive: "#34d399", route: "/challenges",
    position: [0, 1.9, -6.2], scale: 1.2,
  },
  {
    id: "personal", label: "个人空间", desc: "六维画像与数据",
    color: "#0ea5e9", emissive: "#38bdf8", route: "/personal",
    position: [-1.6, 1.2, -5.6], scale: 1.0,
  },
  {
    id: "analytics", label: "学情分析", desc: "趋势与效果评估",
    color: "#8b5cf6", emissive: "#a78bfa", route: "/teacher/analytics",
    position: [1.7, 1.2, -5.6], scale: 1.0,
  },
];
