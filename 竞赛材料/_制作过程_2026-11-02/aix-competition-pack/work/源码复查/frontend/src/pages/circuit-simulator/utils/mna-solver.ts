import type {
  CircuitComponent,
  Wire,
  SimulationResult,
  NetlistElement,
  Point,
  TransientResult,
  TransientOptions,
} from "../types";
import { getTerminalPositions } from "./circuit-utils";

// ─── 节点识别（并查集） ───────────────────────────────────────────────

class UnionFind {
  parent: number[];
  rank: number[];
  constructor(n: number) {
    this.parent = Array.from({ length: n }, (_, i) => i);
    this.rank = new Array(n).fill(0);
  }
  find(x: number): number {
    if (this.parent[x] !== x) this.parent[x] = this.find(this.parent[x]);
    return this.parent[x];
  }
  union(x: number, y: number) {
    const rx = this.find(x),
      ry = this.find(y);
    if (rx === ry) return;
    if (this.rank[rx] < this.rank[ry]) this.parent[rx] = ry;
    else if (this.rank[rx] > this.rank[ry]) this.parent[ry] = rx;
    else {
      this.parent[ry] = rx;
      this.rank[rx]++;
    }
  }
}

function pointKey(p: Point): string {
  return `${p.x},${p.y}`;
}

function buildNodeMap(
  components: CircuitComponent[],
  wires: Wire[],
): Map<string, number> {
  const allPoints: string[] = [];

  for (const comp of components) {
    const terminals = getTerminalPositions(comp);
    for (const t of terminals) {
      allPoints.push(pointKey(t));
    }
  }

  for (const wire of wires) {
    for (const p of wire.points) {
      allPoints.push(pointKey(p));
    }
  }

  const uniquePoints = [...new Set(allPoints)];
  if (uniquePoints.length === 0) return new Map();

  const uf = new UnionFind(uniquePoints.length);
  const pointIdx = new Map<string, number>();
  uniquePoints.forEach((pk, i) => pointIdx.set(pk, i));

  // Union wire points along each wire
  for (const wire of wires) {
    for (let i = 0; i < wire.points.length - 1; i++) {
      const k1 = pointKey(wire.points[i]);
      const k2 = pointKey(wire.points[i + 1]);
      const idx1 = pointIdx.get(k1);
      const idx2 = pointIdx.get(k2);
      if (idx1 !== undefined && idx2 !== undefined) {
        uf.union(idx1, idx2);
      }
    }
  }

  // Union ALL terminals at the same grid point (across different components)
  const allTerminals: string[] = [];
  for (const comp of components) {
    const terminals = getTerminalPositions(comp);
    for (const t of terminals) {
      allTerminals.push(pointKey(t));
    }
  }
  // Group terminals by position and union them
  const terminalGroups = new Map<string, number[]>();
  for (const tk of allTerminals) {
    const idx = pointIdx.get(tk);
    if (idx !== undefined) {
      const group = terminalGroups.get(tk) || [];
      group.push(idx);
      terminalGroups.set(tk, group);
    }
  }
  for (const group of terminalGroups.values()) {
    for (let i = 1; i < group.length; i++) {
      uf.union(group[0], group[i]);
    }
  }

  // Also union ALL wire points that touch component terminals
  for (const wire of wires) {
    for (const wp of wire.points) {
      const wpk = pointKey(wp);
      for (const comp of components) {
        const terminals = getTerminalPositions(comp);
        for (const t of terminals) {
          const tk = pointKey(t);
          if (tk === wpk) {
            const idxT = pointIdx.get(tk);
            const idxW = pointIdx.get(wpk);
            if (idxT !== undefined && idxW !== undefined) {
              uf.union(idxT, idxW);
            }
          }
        }
      }
    }
  }

  // Map to node indices, ground = 0
  // Union ALL ground terminals together first
  const groundIndices: number[] = [];
  for (const comp of components) {
    if (comp.type === "ground") {
      const t = getTerminalPositions(comp);
      if (t.length > 0) {
        const pk = pointKey(t[0]);
        const idx = pointIdx.get(pk);
        if (idx !== undefined) {
          groundIndices.push(idx);
        }
      }
    }
  }
  for (let i = 1; i < groundIndices.length; i++) {
    uf.union(groundIndices[0], groundIndices[i]);
  }
  const groundIdx = groundIndices.length > 0 ? uf.find(groundIndices[0]) : null;

  const nodeMap = new Map<string, number>();
  let nextNode = 1;
  for (const pk of uniquePoints) {
    const idx = pointIdx.get(pk)!;
    const root = uf.find(idx);
    if (root === groundIdx) {
      nodeMap.set(pk, 0);
    } else if (!nodeMap.has(`${root}`)) {
      nodeMap.set(`${root}`, nextNode++);
    }
  }

  // Re-assign using the root mapping
  const finalMap = new Map<string, number>();
  for (const pk of uniquePoints) {
    const idx = pointIdx.get(pk)!;
    const root = uf.find(idx);
    if (root === groundIdx) {
      finalMap.set(pk, 0);
    } else {
      finalMap.set(pk, nodeMap.get(`${root}`)!);
    }
  }

  return finalMap;
}

function getNodeForTerminal(
  comp: CircuitComponent,
  localIndex: number,
  nodeMap: Map<string, number>,
): number {
  const terminals = getTerminalPositions(comp);
  const t = terminals[localIndex];
  if (!t) return 0;
  const pk = pointKey(t);
  return nodeMap.get(pk) ?? 0;
}

// ─── 线性求解（列主元高斯消元） ───────────────────────────────────────

function gaussianElimination(A: number[][], b: number[]): number[] | null {
  const n = A.length;
  const aug = A.map((row, i) => [...row, b[i]]);

  for (let col = 0; col < n; col++) {
    // Partial pivoting
    let maxRow = col;
    let maxVal = Math.abs(aug[col][col]);
    for (let row = col + 1; row < n; row++) {
      if (Math.abs(aug[row][col]) > maxVal) {
        maxVal = Math.abs(aug[row][col]);
        maxRow = row;
      }
    }
    if (maxVal < 1e-12) return null; // Singular

    [aug[col], aug[maxRow]] = [aug[maxRow], aug[col]];

    for (let row = col + 1; row < n; row++) {
      const factor = aug[row][col] / aug[col][col];
      for (let j = col; j <= n; j++) {
        aug[row][j] -= factor * aug[col][j];
      }
    }
  }

  // Back substitution
  const x = new Array(n).fill(0);
  for (let i = n - 1; i >= 0; i--) {
    let sum = aug[i][n];
    for (let j = i + 1; j < n; j++) {
      sum -= aug[i][j] * x[j];
    }
    x[i] = sum / aug[i][i];
  }

  return x;
}

// ─── 网表构建（直流与暂态共用） ───────────────────────────────────────

const TYPE_PREFIX: Record<string, string> = {
  resistor: "R",
  capacitor: "C",
  inductor: "L",
  voltage_source: "V",
  current_source: "I",
};

export interface BuiltNetlist {
  netlist: NetlistElement[];
  errors: string[];
}

export function buildNetlist(
  components: CircuitComponent[],
  wires: Wire[],
): BuiltNetlist {
  const errors: string[] = [];
  const nodeMap = buildNodeMap(components, wires);
  const netlist: NetlistElement[] = [];
  const compCounters: Record<string, number> = {};

  for (const comp of components) {
    if (comp.type === "ground") continue;
    const prefix = TYPE_PREFIX[comp.type] ?? "I";
    compCounters[prefix] = (compCounters[prefix] || 0) + 1;
    const name = `${prefix}${compCounters[prefix]}`;

    const n1 = getNodeForTerminal(comp, 0, nodeMap);
    const n2 = getNodeForTerminal(comp, 1, nodeMap);

    if (n1 === 0 && n2 === 0) {
      errors.push(`${name}: 两端都接地，已短路`);
      continue;
    }

    netlist.push({
      name,
      type: comp.type,
      node1: n1,
      node2: n2,
      value: comp.value,
    });
  }

  const hasGround = components.some((c) => c.type === "ground");
  if (!hasGround) {
    errors.push("缺少接地元件(GND)，请添加一个接地");
  }

  return { netlist, errors };
}

// ─── MNA 直流求解内核 ─────────────────────────────────────────────────
//
// 约定（与参考教材 MNA 一致）：
//   - 电感在直流稳态下等效为 0V 电压源（短路），电流可由源支路方程读出；
//   - 电容在直流稳态下等效为开路（不参与导纳矩阵）；
//   - 电压源支路电流 solution[N+k] 定义为「从 node1 经元件流向 node2」。

interface MNASolution {
  nodeVoltages: Record<number, number>;
  sourceCurrents: Record<string, number>; // 电压源/电感支路电流（n1→n2）
  nodeCount: number;
}

function solveMNA(netlist: NetlistElement[]): MNASolution | null {
  const nodeSet = new Set<number>();
  for (const el of netlist) {
    if (el.node1 !== 0) nodeSet.add(el.node1);
    if (el.node2 !== 0) nodeSet.add(el.node2);
  }
  const nodes = [...nodeSet].sort((a, b) => a - b);
  const nodeIndex = new Map<number, number>();
  nodes.forEach((n, i) => nodeIndex.set(n, i));

  // 电压源类支路：独立电压源 + 直流稳态电感（0V 短路）
  const sourceBranches = netlist.filter(
    (el) => el.type === "voltage_source" || el.type === "inductor",
  );
  const N = nodes.length;
  const M = sourceBranches.length;
  const size = N + M;
  if (size === 0) return { nodeVoltages: {}, sourceCurrents: {}, nodeCount: 0 };

  const A = Array.from({ length: size }, () => new Array(size).fill(0));
  const b = new Array(size).fill(0);

  // Stamp resistors
  for (const el of netlist) {
    if (el.type !== "resistor") continue;
    const i = nodeIndex.get(el.node1) ?? -1;
    const j = nodeIndex.get(el.node2) ?? -1;
    const g = 1 / el.value;
    if (i >= 0) A[i][i] += g;
    if (j >= 0) A[j][j] += g;
    if (i >= 0 && j >= 0) {
      A[i][j] -= g;
      A[j][i] -= g;
    }
  }

  // Stamp voltage-source branches（独立电压源取其值；电感取 0V 短路）
  sourceBranches.forEach((el, k) => {
    const i = nodeIndex.get(el.node1) ?? -1;
    const j = nodeIndex.get(el.node2) ?? -1;
    const row = N + k;
    const v = el.type === "inductor" ? 0 : el.value;
    if (i >= 0) {
      A[i][row] += 1;
      A[row][i] += 1;
    }
    if (j >= 0) {
      A[j][row] -= 1;
      A[row][j] -= 1;
    }
    b[row] = v;
  });

  // Stamp current sources
  for (const el of netlist) {
    if (el.type !== "current_source") continue;
    const i = nodeIndex.get(el.node1) ?? -1;
    const j = nodeIndex.get(el.node2) ?? -1;
    if (i >= 0) b[i] -= el.value;
    if (j >= 0) b[j] += el.value;
  }

  const solution = gaussianElimination(A, b);
  if (!solution) return null;

  const nodeVoltages: Record<number, number> = {};
  nodes.forEach((n, i) => {
    nodeVoltages[n] = solution[i];
  });

  const sourceCurrents: Record<string, number> = {};
  sourceBranches.forEach((el, k) => {
    sourceCurrents[el.name] = solution[N + k];
  });

  return { nodeVoltages, sourceCurrents, nodeCount: N };
}

// ─── 直流稳态 ─────────────────────────────────────────────────────────

export function solveCircuit(
  components: CircuitComponent[],
  wires: Wire[],
): SimulationResult {
  const errors: string[] = [];

  if (components.length === 0) {
    return {
      nodeVoltages: {},
      branchCurrents: {},
      powerDissipation: {},
      errors: ["电路为空，请添加元件"],
    };
  }

  const { netlist, errors: netlistErrors } = buildNetlist(components, wires);
  errors.push(...netlistErrors);

  if (netlist.length === 0) {
    return {
      nodeVoltages: {},
      branchCurrents: {},
      powerDissipation: {},
      errors: ["没有有效元件，请添加元件并连接"],
    };
  }

  const sol = solveMNA(netlist);
  if (!sol) {
    return {
      nodeVoltages: {},
      branchCurrents: {},
      powerDissipation: {},
      errors: [...errors, "电路方程无解，可能存在悬浮节点或短路"],
    };
  }

  // Extract results
  const nodeVoltages: Record<string, number> = {};
  Object.entries(sol.nodeVoltages).forEach(([n, v]) => {
    nodeVoltages[n] = parseFloat(v.toPrecision(6));
  });

  const branchCurrents: Record<string, number> = {};
  const powerDissipation: Record<string, number> = {};

  for (const el of netlist) {
    const v1 = sol.nodeVoltages[el.node1] ?? 0;
    const v2 = sol.nodeVoltages[el.node2] ?? 0;
    if (el.type === "resistor") {
      const current = (v1 - v2) / el.value;
      branchCurrents[el.name] = parseFloat(current.toPrecision(6));
      powerDissipation[el.name] = parseFloat(
        (current * current * el.value).toPrecision(6),
      );
    } else if (el.type === "voltage_source" || el.type === "inductor") {
      const current = sol.sourceCurrents[el.name] ?? 0;
      branchCurrents[el.name] = parseFloat(current.toPrecision(6));
      powerDissipation[el.name] = parseFloat(
        ((v1 - v2) * current).toPrecision(6),
      );
    } else if (el.type === "current_source") {
      branchCurrents[el.name] = el.value;
      powerDissipation[el.name] = parseFloat(
        ((v1 - v2) * el.value).toPrecision(6),
      );
    }
    // 电容在直流稳态下开路：无电流、无耗散，不输出支路量
  }

  // 含动态元件时自动附带 RK4 暂态分析（电容充电 / 电感电流波形）
  const hasDynamic = netlist.some(
    (el) => (el.type === "capacitor" || el.type === "inductor") && el.value > 0,
  );
  const result: SimulationResult = {
    nodeVoltages,
    branchCurrents,
    powerDissipation,
    errors,
  };
  if (hasDynamic) {
    result.transient = runTransientFromNetlist(netlist, [], {});
  }
  return result;
}

// ─── 暂态分析（状态变量法 + RK4） ─────────────────────────────────────
//
// 方法：把电容替换为电压源 vc（其状态）、电感替换为电流源 il（其状态），
// 每个阶段做一次直流 MNA 求解，从解中读回：
//   - 电容支路电流 iC（电压源支路电流）→ dvc/dt = iC / C
//   - 电感两端电压 vL = V(n1) − V(n2)   → dil/dt = vL / L
// 得到显式状态方程 dx/dt = f(x)，用四阶 Runge-Kutta 推进。
// 线性电路下该状态变量法与教科书状态方程完全一致，且复用同一 MNA 内核。

interface StageState {
  vc: number[];
  il: number[];
}

function derivative(
  netlist: NetlistElement[],
  caps: NetlistElement[],
  inds: NetlistElement[],
  state: StageState,
): StageState | null {
  // 动态元件的「伴随替换」：C → 电压源 vc，L → 电流源 il
  const stageNetlist: NetlistElement[] = netlist.map((el) => {
    if (el.type === "capacitor") {
      const k = caps.indexOf(el);
      return { ...el, type: "voltage_source" as const, value: state.vc[k] };
    }
    if (el.type === "inductor") {
      const k = inds.indexOf(el);
      return { ...el, type: "current_source" as const, value: state.il[k] };
    }
    return el;
  });

  const sol = solveMNA(stageNetlist);
  if (!sol) return null;

  const dvc = caps.map((c) => {
    const iC = sol.sourceCurrents[c.name] ?? 0; // n1→n2 流经电容（现为电压源）
    return iC / c.value;
  });
  const dil = inds.map((l) => {
    const v1 = sol.nodeVoltages[l.node1] ?? 0;
    const v2 = sol.nodeVoltages[l.node2] ?? 0;
    return (v1 - v2) / l.value;
  });
  return { vc: dvc, il: dil };
}

function runTransientFromNetlist(
  netlist: NetlistElement[],
  initialErrors: string[],
  options: TransientOptions = {},
): TransientResult {
  const errors: string[] = [...initialErrors];
  const empty: TransientResult = {
    time: [],
    capacitorVoltages: {},
    inductorCurrents: {},
    errors,
  };

  const caps = netlist.filter((el) => el.type === "capacitor" && el.value > 0);
  const inds = netlist.filter((el) => el.type === "inductor" && el.value > 0);
  if (caps.length === 0 && inds.length === 0) {
    return empty;
  }

  const tEnd = options.tEnd ?? 0.01;
  const maxSteps = options.maxSteps ?? 2000;
  const requestedSteps = options.dt ? Math.ceil(tEnd / options.dt) : 500;
  const steps = Math.max(1, Math.min(maxSteps, requestedSteps));
  const dt = options.dt ?? tEnd / steps;

  // 初始状态：电容零电压、电感零电流（零输入初始条件）
  const state: StageState = {
    vc: new Array(caps.length).fill(0),
    il: new Array(inds.length).fill(0),
  };

  const time: number[] = [0];
  const capWaves: Record<string, number[]> = {};
  caps.forEach((c) => (capWaves[c.name] = [0]));
  const indWaves: Record<string, number[]> = {};
  inds.forEach((l) => (indWaves[l.name] = [0]));

  for (let step = 0; step < steps; step++) {
    const k1 = derivative(netlist, caps, inds, state);
    if (!k1) {
      errors.push(
        `暂态求解在 t=${(step * dt).toPrecision(4)}s 失败（方程奇异）`,
      );
      break;
    }
    const s2: StageState = {
      vc: state.vc.map((v, i) => v + (dt / 2) * k1.vc[i]),
      il: state.il.map((v, i) => v + (dt / 2) * k1.il[i]),
    };
    const k2 = derivative(netlist, caps, inds, s2);
    if (!k2) break;
    const s3: StageState = {
      vc: state.vc.map((v, i) => v + (dt / 2) * k2.vc[i]),
      il: state.il.map((v, i) => v + (dt / 2) * k2.il[i]),
    };
    const k3 = derivative(netlist, caps, inds, s3);
    if (!k3) break;
    const s4: StageState = {
      vc: state.vc.map((v, i) => v + dt * k3.vc[i]),
      il: state.il.map((v, i) => v + dt * k3.il[i]),
    };
    const k4 = derivative(netlist, caps, inds, s4);
    if (!k4) break;

    state.vc = state.vc.map(
      (v, i) =>
        v + (dt / 6) * (k1.vc[i] + 2 * k2.vc[i] + 2 * k3.vc[i] + k4.vc[i]),
    );
    state.il = state.il.map(
      (v, i) =>
        v + (dt / 6) * (k1.il[i] + 2 * k2.il[i] + 2 * k3.il[i] + k4.il[i]),
    );

    time.push(parseFloat(((step + 1) * dt).toPrecision(8)));
    caps.forEach((c, i) => capWaves[c.name].push(state.vc[i]));
    inds.forEach((l, i) => indWaves[l.name].push(state.il[i]));
  }

  return {
    time,
    capacitorVoltages: capWaves,
    inductorCurrents: indWaves,
    errors,
  };
}

/** 独立暂态分析入口（含网表构建）；电路无动态元件时返回空波形 + 说明错误。 */
export function runTransientAnalysis(
  components: CircuitComponent[],
  wires: Wire[],
  options: TransientOptions = {},
): TransientResult {
  const { netlist, errors } = buildNetlist(components, wires);
  const result = runTransientFromNetlist(netlist, errors, options);
  if (
    result.time.length === 0 &&
    !result.errors.some((e) => e.includes("暂态求解"))
  ) {
    result.errors.push("电路中无电容/电感（或值为 0），无需暂态分析");
  }
  return result;
}
