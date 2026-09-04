export type ComponentType =
  | "resistor"
  | "capacitor"
  | "inductor"
  | "voltage_source"
  | "current_source"
  | "ground";
export type Mode = "select" | "wire" | "delete";
export type Direction = "right" | "down" | "left" | "up";

export interface Point {
  x: number;
  y: number;
}

export interface Terminal {
  id: string;
  componentId: string;
  position: Point;
  localIndex: number;
}

export interface CircuitComponent {
  id: string;
  type: ComponentType;
  position: Point;
  direction: Direction;
  value: number;
  terminals: Terminal[];
}

export interface Wire {
  id: string;
  points: Point[];
  startTerminalId?: string;
  endTerminalId?: string;
}

export interface SimulationResult {
  nodeVoltages: Record<string, number>;
  branchCurrents: Record<string, number>;
  powerDissipation: Record<string, number>;
  errors: string[];
  /** 含电容/电感时自动附带 RK4 暂态分析结果 */
  transient?: TransientResult;
}

export interface TransientResult {
  time: number[];
  capacitorVoltages: Record<string, number[]>;
  inductorCurrents: Record<string, number[]>;
  errors: string[];
}

export interface TransientOptions {
  tEnd?: number; // 仿真时长（秒）
  dt?: number; // 步长（秒）
  maxSteps?: number; // 步数上限
}

export interface NetlistElement {
  name: string;
  type: ComponentType;
  node1: number;
  node2: number;
  value: number;
}
