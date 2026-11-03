import type { ComponentType, Direction, Point } from "../types";

export const GRID_SIZE = 20;
export const CANVAS_WIDTH = 2000;
export const CANVAS_HEIGHT = 1400;

export const COMPONENT_LENGTH = 4; // in grid units

export interface ComponentDef {
  type: ComponentType;
  label: string;
  unit: string;
  defaultValue: number;
  prefixes: { label: string; factor: number }[];
}

export const COMPONENT_DEFS: Record<ComponentType, ComponentDef> = {
  resistor: {
    type: "resistor",
    label: "电阻 R",
    unit: "Ω",
    defaultValue: 100,
    prefixes: [
      { label: "", factor: 1 },
      { label: "k", factor: 1e3 },
      { label: "M", factor: 1e6 },
    ],
  },
  capacitor: {
    type: "capacitor",
    label: "电容 C",
    unit: "F",
    defaultValue: 1e-6,
    prefixes: [
      { label: "μ", factor: 1e-6 },
      { label: "n", factor: 1e-9 },
      { label: "p", factor: 1e-12 },
    ],
  },
  inductor: {
    type: "inductor",
    label: "电感 L",
    unit: "H",
    defaultValue: 1e-3,
    prefixes: [
      { label: "m", factor: 1e-3 },
      { label: "μ", factor: 1e-6 },
    ],
  },
  voltage_source: {
    type: "voltage_source",
    label: "电压源 V",
    unit: "V",
    defaultValue: 5,
    prefixes: [
      { label: "", factor: 1 },
      { label: "m", factor: 1e-3 },
      { label: "k", factor: 1e3 },
    ],
  },
  current_source: {
    type: "current_source",
    label: "电流源 I",
    unit: "A",
    defaultValue: 0.01,
    prefixes: [
      { label: "", factor: 1 },
      { label: "m", factor: 1e-3 },
      { label: "μ", factor: 1e-6 },
    ],
  },
  ground: {
    type: "ground",
    label: "接地 GND",
    unit: "",
    defaultValue: 0,
    prefixes: [],
  },
};

export const COMPONENT_ORDER: ComponentType[] = [
  "resistor",
  "capacitor",
  "inductor",
  "voltage_source",
  "current_source",
  "ground",
];

export function getTerminalOffsets(
  type: ComponentType,
  dir: Direction,
): Point[] {
  const len = COMPONENT_LENGTH;
  const half = len / 2;

  // Ground only has one terminal (the connection point at center)
  if (type === "ground") {
    return [{ x: 0, y: 0 }];
  }

  const offsets: Point[] = [
    { x: -half, y: 0 },
    { x: half, y: 0 },
  ];
  return offsets.map((p) => rotatePoint(p, dir));
}

function rotatePoint(p: Point, dir: Direction): Point {
  switch (dir) {
    case "right":
      return p;
    case "down":
      return { x: -p.y, y: p.x };
    case "left":
      return { x: -p.x, y: -p.y };
    case "up":
      return { x: p.y, y: -p.x };
  }
}

export function formatValue(value: number, type: ComponentType): string {
  const def = COMPONENT_DEFS[type];
  if (type === "ground") return "";
  if (value === 0) return `0 ${def.unit}`;

  const absVal = Math.abs(value);
  for (let i = def.prefixes.length - 1; i >= 0; i--) {
    const p = def.prefixes[i];
    if (absVal >= p.factor * 0.999) {
      const display = value / p.factor;
      return `${parseFloat(display.toPrecision(4))} ${p.label}${def.unit}`;
    }
  }
  return `${value} ${def.unit}`;
}
