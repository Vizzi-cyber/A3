import type {
  CircuitComponent,
  Wire,
  SimulationResult,
  NetlistElement,
  Point,
} from "../types";
import { GRID_SIZE, COMPONENT_LENGTH } from "./constants";
import { getTerminalPositions } from "./circuit-utils";

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

export function solveCircuit(
  components: CircuitComponent[],
  wires: Wire[],
): SimulationResult {
  const errors: string[] = [];
  const nodeMap = buildNodeMap(components, wires);

  if (components.length === 0) {
    return {
      nodeVoltages: {},
      branchCurrents: {},
      powerDissipation: {},
      errors: ["电路为空，请添加元件"],
    };
  }

  // Build netlist
  const netlist: NetlistElement[] = [];
  let compCounters: Record<string, number> = {};

  for (const comp of components) {
    if (comp.type === "ground") continue;
    const prefix =
      comp.type === "resistor"
        ? "R"
        : comp.type === "capacitor"
          ? "C"
          : comp.type === "inductor"
            ? "L"
            : comp.type === "voltage_source"
              ? "V"
              : "I";
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

  if (netlist.length === 0) {
    return {
      nodeVoltages: {},
      branchCurrents: {},
      powerDissipation: {},
      errors: ["没有有效元件，请添加元件并连接"],
    };
  }

  // Check for ground
  const hasGround = components.some((c) => c.type === "ground");
  if (!hasGround) {
    errors.push("缺少接地元件(GND)，请添加一个接地");
  }

  // MNA
  const nodeSet = new Set<number>();
  for (const el of netlist) {
    if (el.node1 !== 0) nodeSet.add(el.node1);
    if (el.node2 !== 0) nodeSet.add(el.node2);
  }
  const nodes = [...nodeSet].sort((a, b) => a - b);
  const nodeIndex = new Map<number, number>();
  nodes.forEach((n, i) => nodeIndex.set(n, i));

  const voltageSources = netlist.filter((el) => el.type === "voltage_source");
  const N = nodes.length;
  const M = voltageSources.length;
  const size = N + M;

  if (size === 0) {
    return {
      nodeVoltages: {},
      branchCurrents: {},
      powerDissipation: {},
      errors,
    };
  }

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

  // Stamp voltage sources
  voltageSources.forEach((el, k) => {
    const i = nodeIndex.get(el.node1) ?? -1;
    const j = nodeIndex.get(el.node2) ?? -1;
    const row = N + k;
    if (i >= 0) {
      A[i][row] += 1;
      A[row][i] += 1;
    }
    if (j >= 0) {
      A[j][row] -= 1;
      A[row][j] -= 1;
    }
    b[row] = el.value;
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
  if (!solution) {
    return {
      nodeVoltages: {},
      branchCurrents: {},
      powerDissipation: {},
      errors: [...errors, "电路方程无解，可能存在悬浮节点或短路"],
    };
  }

  // Extract results
  const nodeVoltages: Record<string, number> = {};
  nodes.forEach((n, i) => {
    nodeVoltages[`${n}`] = parseFloat(solution[i].toPrecision(6));
  });

  const branchCurrents: Record<string, number> = {};
  const powerDissipation: Record<string, number> = {};

  for (const el of netlist) {
    if (el.type === "resistor") {
      const v1 = nodeVoltages[`${el.node1}`] ?? 0;
      const v2 = nodeVoltages[`${el.node2}`] ?? 0;
      const current = (v1 - v2) / el.value;
      branchCurrents[el.name] = parseFloat(current.toPrecision(6));
      powerDissipation[el.name] = parseFloat(
        (current * current * el.value).toPrecision(6),
      );
    } else if (el.type === "voltage_source") {
      const vsIdx = voltageSources.indexOf(el);
      branchCurrents[el.name] = parseFloat(solution[N + vsIdx].toPrecision(6));
      const v1 = nodeVoltages[`${el.node1}`] ?? 0;
      const v2 = nodeVoltages[`${el.node2}`] ?? 0;
      powerDissipation[el.name] = parseFloat(
        ((v1 - v2) * solution[N + vsIdx]).toPrecision(6),
      );
    } else if (el.type === "current_source") {
      branchCurrents[el.name] = el.value;
      const v1 = nodeVoltages[`${el.node1}`] ?? 0;
      const v2 = nodeVoltages[`${el.node2}`] ?? 0;
      powerDissipation[el.name] = parseFloat(
        ((v1 - v2) * el.value).toPrecision(6),
      );
    }
  }

  return { nodeVoltages, branchCurrents, powerDissipation, errors };
}
