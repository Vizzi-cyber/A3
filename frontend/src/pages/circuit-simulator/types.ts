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
}

export interface NetlistElement {
  name: string;
  type: ComponentType;
  node1: number;
  node2: number;
  value: number;
}
