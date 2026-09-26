import type { CircuitComponent, Point, NetlistElement } from "../types";
import { getTerminalOffsets, COMPONENT_LENGTH } from "./constants";

export function getTerminalPositions(comp: CircuitComponent): Point[] {
  const offsets = getTerminalOffsets(comp.type, comp.direction);
  return offsets.map((off) => ({
    x: comp.position.x + off.x,
    y: comp.position.y + off.y,
  }));
}

export function pointEquals(a: Point, b: Point): boolean {
  return a.x === b.x && a.y === b.y;
}

export function pointsNear(a: Point, b: Point, tolerance: number = 1): boolean {
  return Math.abs(a.x - b.x) <= tolerance && Math.abs(a.y - b.y) <= tolerance;
}

export function generateNetlistText(
  netlist: NetlistElement[],
  nodeVoltages: Record<string, number>,
  branchCurrents: Record<string, number>,
): string {
  const lines = netlist.map((el) => {
    const v1 = nodeVoltages[`${el.node1}`] ?? "?";
    const v2 = nodeVoltages[`${el.node2}`] ?? "?";
    const i = branchCurrents[el.name] ?? "?";
    return `${el.name} (${el.type}): Node${el.node1}(${v1}V) -> Node${el.node2}(${v2}V), I=${i}A`;
  });
  return lines.join("\n");
}
