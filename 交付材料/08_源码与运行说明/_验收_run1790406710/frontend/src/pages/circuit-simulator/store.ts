import { create } from "zustand";
import type {
  CircuitComponent,
  Wire,
  Mode,
  Direction,
  ComponentType,
  SimulationResult,
  Point,
} from "./types";
import { COMPONENT_LENGTH, getTerminalOffsets } from "./utils/constants";
import { solveCircuit } from "./utils/mna-solver";

let nextId = 1;
function genId(prefix: string) {
  return `${prefix}_${nextId++}`;
}

// 撤销/重做历史记录
interface HistoryEntry {
  components: CircuitComponent[];
  wires: Wire[];
}

interface CircuitState {
  components: CircuitComponent[];
  wires: Wire[];
  selectedId: string | null;
  mode: Mode;
  simulationResult: SimulationResult | null;
  wirePoints: Point[];
  history: HistoryEntry[];
  historyIndex: number;

  addComponent: (type: ComponentType, gridPos: Point) => void;
  removeComponent: (id: string) => void;
  updateComponentValue: (id: string, value: number) => void;
  rotateComponent: (id: string) => void;
  moveComponent: (id: string, pos: Point) => void;
  selectComponent: (id: string | null) => void;
  setMode: (mode: Mode) => void;
  addWirePoint: (point: Point) => void;
  finishWire: () => void;
  cancelWire: () => void;
  removeWire: (id: string) => void;
  simulate: () => void;
  clearAll: () => void;
  loadPreset: (presetId: string) => void;
  loadFault: (presetId: string, overrides: Record<string, number>) => void;
  undo: () => void;
  redo: () => void;
  saveToHistory: () => void;
}

const DIRECTION_CYCLE: Direction[] = ["right", "down", "left", "up"];

// ─── Preset Circuit Definitions ───

export interface PresetComponent {
  id: string;
  type: ComponentType;
  position: Point;
  direction: Direction;
  value: number;
}

export interface PresetWire {
  points: Point[];
}

export interface PresetCircuit {
  id: string;
  name: string;
  description: string;
  components: PresetComponent[];
  wires: PresetWire[];
}

export const PRESET_CIRCUITS: PresetCircuit[] = [
  {
    id: "voltage-divider",
    name: "分压电路",
    description: "5V 电压源 + 1kΩ + 2kΩ 串联分压，可测中间节点电压",
    components: [
      {
        id: "gnd1",
        type: "ground",
        position: { x: 1, y: 3 },
        direction: "right",
        value: 0,
      },
      {
        id: "v1",
        type: "voltage_source",
        position: { x: 3, y: 3 },
        direction: "left",
        value: 5,
      },
      {
        id: "r1",
        type: "resistor",
        position: { x: 7, y: 3 },
        direction: "right",
        value: 1000,
      },
      {
        id: "r2",
        type: "resistor",
        position: { x: 11, y: 3 },
        direction: "right",
        value: 2000,
      },
    ],
    wires: [
      {
        points: [
          { x: 13, y: 3 },
          { x: 13, y: 5 },
          { x: 1, y: 5 },
          { x: 1, y: 3 },
        ],
      },
    ],
  },
  {
    id: "rc-circuit",
    name: "RC 充电电路",
    description: "5V 电压源 + 1kΩ 电阻 + 1μF 电容串联充电电路",
    components: [
      {
        id: "gnd1",
        type: "ground",
        position: { x: 1, y: 7 },
        direction: "right",
        value: 0,
      },
      {
        id: "v1",
        type: "voltage_source",
        position: { x: 3, y: 7 },
        direction: "left",
        value: 5,
      },
      {
        id: "r1",
        type: "resistor",
        position: { x: 7, y: 7 },
        direction: "right",
        value: 1000,
      },
      {
        id: "c1",
        type: "capacitor",
        position: { x: 11, y: 7 },
        direction: "right",
        value: 0.000001,
      },
    ],
    wires: [
      {
        points: [
          { x: 13, y: 7 },
          { x: 13, y: 9 },
          { x: 1, y: 9 },
          { x: 1, y: 7 },
        ],
      },
    ],
  },
  {
    id: "current-source-test",
    name: "电流源电路",
    description: "10mA 电流源驱动 100Ω + 200Ω 串联电阻，测量电压",
    components: [
      {
        id: "gnd1",
        type: "ground",
        position: { x: 1, y: 11 },
        direction: "right",
        value: 0,
      },
      {
        id: "i1",
        type: "current_source",
        position: { x: 3, y: 11 },
        direction: "right",
        value: 0.01,
      },
      {
        id: "r1",
        type: "resistor",
        position: { x: 7, y: 11 },
        direction: "right",
        value: 100,
      },
      {
        id: "r2",
        type: "resistor",
        position: { x: 11, y: 11 },
        direction: "right",
        value: 200,
      },
    ],
    wires: [
      {
        points: [
          { x: 13, y: 11 },
          { x: 13, y: 13 },
          { x: 1, y: 13 },
          { x: 1, y: 11 },
        ],
      },
    ],
  },
];

function createTerminals(
  id: string,
  type: ComponentType,
  pos: Point,
  dir: Direction,
) {
  const offsets = getTerminalOffsets(type, dir);
  return offsets.map((off, i) => ({
    id: `${id}_t${i}`,
    componentId: id,
    position: { x: pos.x + off.x, y: pos.y + off.y },
    localIndex: i,
  }));
}

export const useCircuitStore = create<CircuitState>((set, get) => ({
  components: [],
  wires: [],
  selectedId: null,
  mode: "select",
  simulationResult: null,
  wirePoints: [],
  history: [],
  historyIndex: -1,

  saveToHistory: () => {
    const { components, wires, history, historyIndex } = get();
    const newHistory = history.slice(0, historyIndex + 1);
    newHistory.push({ components: [...components], wires: [...wires] });
    if (newHistory.length > 50) newHistory.shift();
    set({ history: newHistory, historyIndex: newHistory.length - 1 });
  },

  undo: () => {
    const { history, historyIndex } = get();
    if (historyIndex <= 0) return;
    const prev = history[historyIndex - 1];
    set({
      components: [...prev.components],
      wires: [...prev.wires],
      historyIndex: historyIndex - 1,
      selectedId: null,
      simulationResult: null,
    });
  },

  redo: () => {
    const { history, historyIndex } = get();
    if (historyIndex >= history.length - 1) return;
    const next = history[historyIndex + 1];
    set({
      components: [...next.components],
      wires: [...next.wires],
      historyIndex: historyIndex + 1,
      selectedId: null,
      simulationResult: null,
    });
  },

  addComponent: (type, gridPos) => {
    const id = genId(type[0].toUpperCase());
    const dir: Direction = "right";
    const comp: CircuitComponent = {
      id,
      type,
      position: gridPos,
      direction: dir,
      value:
        type === "ground"
          ? 0
          : type === "voltage_source"
            ? 5
            : type === "current_source"
              ? 0.01
              : type === "capacitor"
                ? 1e-6
                : type === "inductor"
                  ? 1e-3
                  : 100,
      terminals: createTerminals(id, type, gridPos, dir),
    };
    set((s) => ({
      components: [...s.components, comp],
      selectedId: id,
      simulationResult: null,
    }));
    get().saveToHistory();
  },

  removeComponent: (id) => {
    set((s) => ({
      components: s.components.filter((c) => c.id !== id),
      wires: s.wires.filter((w) => {
        const terminals =
          s.components.find((c) => c.id === id)?.terminals || [];
        const tIds = new Set(terminals.map((t) => t.id));
        return (
          !tIds.has(w.startTerminalId || "") && !tIds.has(w.endTerminalId || "")
        );
      }),
      selectedId: s.selectedId === id ? null : s.selectedId,
      simulationResult: null,
    }));
    get().saveToHistory();
  },

  updateComponentValue: (id, value) => {
    set((s) => ({
      components: s.components.map((c) => (c.id === id ? { ...c, value } : c)),
      simulationResult: null,
    }));
    get().saveToHistory();
  },

  rotateComponent: (id) => {
    set((s) => {
      const comp = s.components.find((c) => c.id === id);
      if (!comp) return s;
      const idx = DIRECTION_CYCLE.indexOf(comp.direction);
      const newDir = DIRECTION_CYCLE[(idx + 1) % 4];
      const newTerminals = createTerminals(
        id,
        comp.type,
        comp.position,
        newDir,
      );
      return {
        components: s.components.map((c) =>
          c.id === id
            ? { ...c, direction: newDir, terminals: newTerminals }
            : c,
        ),
        simulationResult: null,
      };
    });
    get().saveToHistory();
  },

  moveComponent: (id, pos) => {
    set((s) => {
      const comp = s.components.find((c) => c.id === id);
      if (!comp) return s;
      const newTerminals = createTerminals(id, comp.type, pos, comp.direction);
      return {
        components: s.components.map((c) =>
          c.id === id ? { ...c, position: pos, terminals: newTerminals } : c,
        ),
        simulationResult: null,
      };
    });
    // 拖动过程中不保存历史，只在拖动结束时保存
  },

  selectComponent: (id) => set({ selectedId: id }),
  setMode: (mode) => set({ mode, wirePoints: [] }),

  addWirePoint: (point) => {
    set((s) => ({ wirePoints: [...s.wirePoints, point] }));
  },

  finishWire: () => {
    const { wirePoints, components } = get();
    if (wirePoints.length < 2) {
      set({ wirePoints: [] });
      return;
    }

    // 连线验证：检查起点和终点是否连接到元件端子
    const startPt = wirePoints[0];
    const endPt = wirePoints[wirePoints.length - 1];

    let startConnected = false;
    let endConnected = false;

    for (const comp of components) {
      for (const terminal of comp.terminals) {
        if (
          Math.abs(terminal.position.x - startPt.x) < 0.1 &&
          Math.abs(terminal.position.y - startPt.y) < 0.1
        ) {
          startConnected = true;
        }
        if (
          Math.abs(terminal.position.x - endPt.x) < 0.1 &&
          Math.abs(terminal.position.y - endPt.y) < 0.1
        ) {
          endConnected = true;
        }
      }
    }

    // 如果起点或终点没有连接到端子，提示用户
    if (!startConnected || !endConnected) {
      // 允许悬空连线，但标记为不完整
      console.warn("连线未完全连接到元件端子");
    }

    // 检查是否连接了同一个元件的两个端子（短路检测）
    let startTerminalComp = null;
    let endTerminalComp = null;
    for (const comp of components) {
      for (const terminal of comp.terminals) {
        if (
          Math.abs(terminal.position.x - startPt.x) < 0.1 &&
          Math.abs(terminal.position.y - startPt.y) < 0.1
        ) {
          startTerminalComp = comp.id;
        }
        if (
          Math.abs(terminal.position.x - endPt.x) < 0.1 &&
          Math.abs(terminal.position.y - endPt.y) < 0.1
        ) {
          endTerminalComp = comp.id;
        }
      }
    }

    // 如果连接了同一个元件的两个端子，警告短路
    if (
      startTerminalComp &&
      endTerminalComp &&
      startTerminalComp === endTerminalComp
    ) {
      console.warn("警告：连线连接了同一个元件的两个端子，可能造成短路");
    }

    const wire: Wire = {
      id: genId("W"),
      points: [...wirePoints],
    };
    set((s) => ({
      wires: [...s.wires, wire],
      wirePoints: [],
      simulationResult: null,
    }));
    get().saveToHistory();
  },

  cancelWire: () => set({ wirePoints: [] }),

  removeWire: (id) => {
    set((s) => ({
      wires: s.wires.filter((w) => w.id !== id),
      simulationResult: null,
    }));
  },

  simulate: () => {
    const { components, wires } = get();
    const result = solveCircuit(components, wires);
    set({ simulationResult: result });
  },

  clearAll: () =>
    set({
      components: [],
      wires: [],
      selectedId: null,
      simulationResult: null,
      wirePoints: [],
    }),

  // ─── Preset Circuits ───

  loadPreset: (presetId: string) => {
    const preset = PRESET_CIRCUITS.find((p) => p.id === presetId);
    if (!preset) return;
    // Reset IDs to avoid collisions
    nextId = 1000;
    // Recreate components with fresh IDs
    const newComponents: CircuitComponent[] = preset.components.map((c) => {
      const newId = genId(c.type[0].toUpperCase());
      return {
        ...c,
        id: newId,
        terminals: createTerminals(newId, c.type, c.position, c.direction),
      };
    });
    const newWires: Wire[] = preset.wires.map((w) => ({
      id: genId("W"),
      points: w.points.map((p) => ({ ...p })),
    }));
    set({
      components: newComponents,
      wires: newWires,
      selectedId: null,
      simulationResult: null,
      wirePoints: [],
    });
    get().saveToHistory();
  },

  // ─── Fault Experiment (故障实验) ───
  // 加载故障电路：基于预设电路，用 overrides 覆盖指定元件的值模拟故障
  // 例：loadFault("voltage-divider", { r2: 1e9 }) 将 r2 改为 1GΩ 模拟断路

  loadFault: (presetId: string, overrides: Record<string, number>) => {
    const preset = PRESET_CIRCUITS.find((p) => p.id === presetId);
    if (!preset) return;
    nextId = 1000;
    const newComponents: CircuitComponent[] = preset.components.map((c) => {
      const newId = genId(c.type[0].toUpperCase());
      // 用原始 id 作为 override 键（r1/r2/v1/c1），在重命名前取值
      const overrideValue = overrides[c.id];
      return {
        ...c,
        id: newId,
        value: overrideValue !== undefined ? overrideValue : c.value,
        terminals: createTerminals(newId, c.type, c.position, c.direction),
      };
    });
    const newWires: Wire[] = preset.wires.map((w) => ({
      id: genId("W"),
      points: w.points.map((p) => ({ ...p })),
    }));
    set({
      components: newComponents,
      wires: newWires,
      selectedId: null,
      simulationResult: null,
      wirePoints: [],
    });
    get().saveToHistory();
  },
}));
