import type { ComponentType, Direction, Point } from "../types";
import { GRID_SIZE, COMPONENT_LENGTH } from "./constants";

export function snapToGrid(
  px: number,
  py: number,
  gridSize: number = GRID_SIZE,
): Point {
  return {
    x: Math.round(px / gridSize),
    y: Math.round(py / gridSize),
  };
}

export function gridToPixel(
  gx: number,
  gy: number,
  gridSize: number = GRID_SIZE,
): Point {
  return { x: gx * gridSize, y: gy * gridSize };
}

export function pixelToGrid(
  px: number,
  py: number,
  gridSize: number = GRID_SIZE,
): Point {
  return {
    x: Math.round(px / gridSize),
    y: Math.round(py / gridSize),
  };
}

export function getComponentSVGPath(
  type: ComponentType,
  dir: Direction,
): string {
  const s = GRID_SIZE;
  const half = (COMPONENT_LENGTH / 2) * s;

  let path: string;
  switch (type) {
    case "resistor":
      path = `M ${-half},0 L ${-half + s},0 L ${-half + 1.25 * s},${-0.5 * s} L ${-half + 1.75 * s},${0.5 * s} L ${-half + 2.25 * s},${-0.5 * s} L ${-half + 2.75 * s},${0.5 * s} L ${half - s},0 L ${half},0`;
      break;
    case "capacitor":
      path = `M ${-half},0 L ${-0.3 * s},0 M ${-0.3 * s},${-1.2 * s} L ${-0.3 * s},${1.2 * s} M ${0.3 * s},${-1.2 * s} L ${0.3 * s},${1.2 * s} M ${0.3 * s},0 L ${half},0`;
      break;
    case "inductor":
      path = `M ${-half},0 L ${-half + s},0 Q ${-half + 1.5 * s},${-1.2 * s} ${-half + 2 * s},0 Q ${-half + 2.5 * s},${-1.2 * s} ${-half + 3 * s},0 Q ${-half + 3.5 * s},${-1.2 * s} ${half - s},0 L ${half},0`;
      break;
    case "voltage_source":
    case "current_source":
      return ""; // Special rendering
    case "ground":
      return `M 0,0 L 0,${s} M ${-s},${s} L ${s},${s} M ${-0.6 * s},${1.5 * s} L ${0.6 * s},${1.5 * s} M ${-0.2 * s},${2 * s} L ${0.2 * s},${2 * s}`;
    default:
      return "";
  }
  return rotatePath(path, dir);
}

function rotatePath(path: string, dir: Direction): string {
  if (dir === "right") return path;
  const cos = dir === "left" ? -1 : dir === "down" ? 0 : 0;
  const sin = dir === "down" ? 1 : dir === "up" ? -1 : 0;

  return path.replace(/(-?\d+\.?\d*),(-?\d+\.?\d*)/g, (_, xStr, yStr) => {
    const x = parseFloat(xStr);
    const y = parseFloat(yStr);
    const nx = x * cos - y * sin;
    const ny = x * sin + y * cos;
    return `${nx.toFixed(1)},${ny.toFixed(1)}`;
  });
}

export function getComponentBoundingBox(type: ComponentType): {
  width: number;
  height: number;
} {
  const s = GRID_SIZE;
  switch (type) {
    case "resistor":
    case "capacitor":
    case "inductor":
      return { width: COMPONENT_LENGTH * s, height: 2 * s };
    case "voltage_source":
    case "current_source":
      return { width: COMPONENT_LENGTH * s, height: COMPONENT_LENGTH * s };
    case "ground":
      return { width: 2 * s, height: 2.5 * s };
    default:
      return { width: COMPONENT_LENGTH * s, height: 2 * s };
  }
}

export function isPointNearComponent(
  px: number,
  py: number,
  comp: { position: Point; direction: Direction; type: ComponentType },
): boolean {
  const s = GRID_SIZE;
  const cx = comp.position.x * s;
  const cy = comp.position.y * s;
  const half = (COMPONENT_LENGTH / 2) * s;
  const margin = s;

  if (comp.direction === "right" || comp.direction === "left") {
    return (
      px >= cx - half - margin &&
      px <= cx + half + margin &&
      py >= cy - 2 * s - margin &&
      py <= cy + 2 * s + margin
    );
  } else {
    return (
      px >= cx - 2 * s - margin &&
      px <= cx + 2 * s + margin &&
      py >= cy - half - margin &&
      py <= cy + half + margin
    );
  }
}
