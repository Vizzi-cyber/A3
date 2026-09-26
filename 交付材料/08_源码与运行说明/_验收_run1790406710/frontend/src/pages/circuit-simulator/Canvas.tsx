import React, { useRef, useState, useCallback } from "react";
import { useCircuitStore } from "./store";
import {
  GRID_SIZE,
  CANVAS_WIDTH,
  CANVAS_HEIGHT,
  COMPONENT_LENGTH,
  COMPONENT_DEFS,
} from "./utils/constants";
import { snapToGrid, getComponentSVGPath } from "./utils/drawing-utils";
import {
  getTerminalPositions,
  pointsNear,
  pointEquals,
} from "./utils/circuit-utils";
import type { CircuitComponent, Point, ComponentType } from "./types";

const TERMINAL_SNAP_RADIUS = 20; // 端子吸附半径（像素）

const Canvas: React.FC = () => {
  const s = GRID_SIZE;
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [viewBox, setViewBox] = useState({ x: -200, y: -200, w: 1200, h: 800 });
  const [isPanning, setIsPanning] = useState(false);
  const [panStart, setPanStart] = useState({ x: 0, y: 0 });
  const [isDraggingComp, setIsDraggingComp] = useState(false);
  const [dragCompId, setDragCompId] = useState<string | null>(null);
  const [dragOffset, setDragOffset] = useState<Point>({ x: 0, y: 0 });
  const [isDraggingPalette, setIsDraggingPalette] = useState(false);
  const [hoverTerminal, setHoverTerminal] = useState<Point | null>(null);

  const {
    components,
    wires,
    selectedId,
    mode,
    simulationResult,
    wirePoints,
    selectComponent,
    addComponent,
    removeComponent,
    removeWire,
    addWirePoint,
    finishWire,
    cancelWire,
    moveComponent,
  } = useCircuitStore();

  React.useEffect(() => {
    (window as any).__circuitStore = useCircuitStore;
  }, []);

  const getSVGPoint = useCallback(
    (clientX: number, clientY: number): Point => {
      const svg = svgRef.current;
      if (!svg) return { x: 0, y: 0 };
      const rect = svg.getBoundingClientRect();
      const scaleX = viewBox.w / rect.width;
      const scaleY = viewBox.h / rect.height;
      return {
        x: (clientX - rect.left) * scaleX + viewBox.x,
        y: (clientY - rect.top) * scaleY + viewBox.y,
      };
    },
    [viewBox],
  );

  const findNearTerminal = useCallback(
    (gridPt: Point): Point | null => {
      const store = useCircuitStore.getState();
      let best: Point | null = null;
      let bestDist = Infinity;
      for (const comp of store.components) {
        const terminals = getTerminalPositions(comp);
        for (const t of terminals) {
          const dx = Math.abs(t.x - gridPt.x) * s;
          const dy = Math.abs(t.y - gridPt.y) * s;
          if (dx <= TERMINAL_SNAP_RADIUS && dy <= TERMINAL_SNAP_RADIUS) {
            const dist = dx * dx + dy * dy;
            if (dist < bestDist) {
              bestDist = dist;
              best = t;
            }
          }
        }
      }
      return best;
    },
    [s],
  );

  const handleMouseDown = useCallback(
    (e: React.MouseEvent) => {
      // 中键或Alt+左键：平移
      if (e.button === 1 || (e.button === 0 && e.altKey)) {
        setIsPanning(true);
        setPanStart({ x: e.clientX, y: e.clientY });
        return;
      }
      // 右键：取消连线
      if (e.button === 2) {
        const store = useCircuitStore.getState();
        if (store.mode === "wire" && store.wirePoints.length > 0) {
          store.cancelWire();
        }
        return;
      }
      if (e.button !== 0) return;

      const store = useCircuitStore.getState();
      const pt = getSVGPoint(e.clientX, e.clientY);
      const gridPt = snapToGrid(pt.x, pt.y);

      if (store.mode === "wire") {
        if (store.wirePoints.length >= 2) {
          const lastPt = store.wirePoints[store.wirePoints.length - 1];
          if (pointEquals(gridPt, lastPt)) {
            store.finishWire();
            return;
          }
        }
        const snapped = findNearTerminal(gridPt) || gridPt;
        store.addWirePoint(snapped);
        return;
      }

      if (store.mode === "delete") {
        for (const comp of store.components) {
          const cx = comp.position.x * s;
          const cy = comp.position.y * s;
          const dist = Math.sqrt((pt.x - cx) ** 2 + (pt.y - cy) ** 2);
          if (dist < (COMPONENT_LENGTH * s) / 2 + s) {
            store.removeComponent(comp.id);
            return;
          }
        }
        for (const wire of store.wires) {
          for (const wp of wire.points) {
            const wx = wp.x * s;
            const wy = wp.y * s;
            if (Math.sqrt((pt.x - wx) ** 2 + (pt.y - wy) ** 2) < s * 1.5) {
              store.removeWire(wire.id);
              return;
            }
          }
        }
        return;
      }

      // Select mode - check for terminal click to start wiring
      const nearTerminal = findNearTerminal(gridPt);
      if (nearTerminal) {
        store.setMode("wire");
        store.addWirePoint(nearTerminal);
        return;
      }

      // Select mode - check for component click to start drag
      for (const comp of store.components) {
        const cx = comp.position.x * s;
        const cy = comp.position.y * s;
        const dist = Math.sqrt((pt.x - cx) ** 2 + (pt.y - cy) ** 2);
        if (dist < (COMPONENT_LENGTH * s) / 2 + s) {
          store.selectComponent(comp.id);
          setIsDraggingComp(true);
          setDragCompId(comp.id);
          setDragOffset({
            x: gridPt.x - comp.position.x,
            y: gridPt.y - comp.position.y,
          });
          return;
        }
      }
      store.selectComponent(null);
    },
    [getSVGPoint, findNearTerminal, s],
  );

  const handleMouseMove = useCallback(
    (e: React.MouseEvent) => {
      if (isPanning) {
        const svg = svgRef.current;
        if (!svg) return;
        const rect = svg.getBoundingClientRect();
        const scaleX = viewBox.w / rect.width;
        const scaleY = viewBox.h / rect.height;
        const dx = (e.clientX - panStart.x) * scaleX;
        const dy = (e.clientY - panStart.y) * scaleY;
        setViewBox((v) => ({ ...v, x: v.x - dx, y: v.y - dy }));
        setPanStart({ x: e.clientX, y: e.clientY });
        return;
      }

      if (isDraggingComp && dragCompId) {
        const pt = getSVGPoint(e.clientX, e.clientY);
        const gridPt = snapToGrid(pt.x, pt.y);
        const newX = gridPt.x - dragOffset.x;
        const newY = gridPt.y - dragOffset.y;
        moveComponent(dragCompId, { x: newX, y: newY });
        return;
      }

      // Wire mode: track nearest terminal for visual feedback
      const store = useCircuitStore.getState();
      if (store.mode === "wire") {
        const pt = getSVGPoint(e.clientX, e.clientY);
        const gridPt = snapToGrid(pt.x, pt.y);
        const near = findNearTerminal(gridPt);
        setHoverTerminal(near);
      } else {
        setHoverTerminal(null);
      }
    },
    [
      isPanning,
      panStart,
      viewBox,
      isDraggingComp,
      dragCompId,
      dragOffset,
      getSVGPoint,
      moveComponent,
      findNearTerminal,
    ],
  );

  const handleMouseUp = useCallback(() => {
    if (isDraggingComp && dragCompId) {
      // 拖动结束时保存一次历史
      useCircuitStore.getState().saveToHistory();
    }
    setIsPanning(false);
    setIsDraggingComp(false);
    setDragCompId(null);
  }, [isDraggingComp, dragCompId]);

  const handleWheel = useCallback((e: React.WheelEvent) => {
    e.preventDefault();
    const factor = e.deltaY > 0 ? 1.1 : 0.9;
    setViewBox((v) => ({
      x: v.x + (v.w * (1 - factor)) / 2,
      y: v.y + (v.h * (1 - factor)) / 2,
      w: v.w * factor,
      h: v.h * factor,
    }));
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = "copy";
    setIsDraggingPalette(true);
  }, []);

  const handleDragLeave = useCallback(() => {
    setIsDraggingPalette(false);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDraggingPalette(false);
      const type = e.dataTransfer.getData("component-type") as ComponentType;
      if (!type) return;
      const pt = getSVGPoint(e.clientX, e.clientY);
      const gridPt = snapToGrid(pt.x, pt.y);
      addComponent(type, gridPt);
    },
    [getSVGPoint, addComponent],
  );

  const handleDoubleClick = useCallback(
    (e: React.MouseEvent) => {
      const store = useCircuitStore.getState();
      const pt = getSVGPoint(e.clientX, e.clientY);

      if (store.mode === "wire" && store.wirePoints.length >= 2) {
        store.finishWire();
        return;
      }

      if (store.mode === "select") {
        for (const comp of store.components) {
          const cx = comp.position.x * s;
          const cy = comp.position.y * s;
          const dist = Math.sqrt((pt.x - cx) ** 2 + (pt.y - cy) ** 2);
          if (dist < (COMPONENT_LENGTH * s) / 2 + s) {
            store.selectComponent(comp.id);
            return;
          }
        }
      }
    },
    [getSVGPoint, s],
  );

  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    const store = useCircuitStore.getState();
    if (e.key === "Escape") {
      store.cancelWire();
    }
    if ((e.key === "Delete" || e.key === "Backspace") && store.selectedId) {
      const comp = store.components.find((c) => c.id === store.selectedId);
      if (comp) store.removeComponent(comp.id);
    }
    // 撤销/重做快捷键
    if ((e.ctrlKey || e.metaKey) && e.key === "z" && !e.shiftKey) {
      e.preventDefault();
      store.undo();
    }
    if (
      (e.ctrlKey || e.metaKey) &&
      (e.key === "y" || (e.key === "z" && e.shiftKey))
    ) {
      e.preventDefault();
      store.redo();
    }
  }, []);

  return (
    <div
      ref={containerRef}
      className="w-full h-full relative"
      style={{
        cursor: isPanning
          ? "grabbing"
          : isDraggingComp
            ? "move"
            : mode === "wire"
              ? "crosshair"
              : mode === "delete"
                ? "not-allowed"
                : "default",
      }}
    >
      {isDraggingPalette && (
        <div className="absolute inset-0 border-2 border-dashed border-indigo-400 bg-indigo-50/20 pointer-events-none z-10 rounded-lg" />
      )}
      <svg
        ref={svgRef}
        className="w-full h-full"
        viewBox={`${viewBox.x} ${viewBox.y} ${viewBox.w} ${viewBox.h}`}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        onWheel={handleWheel}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDoubleClick={handleDoubleClick}
        onKeyDown={handleKeyDown}
        tabIndex={0}
        style={{ background: "#fafafa", outline: "none" }}
      >
        <defs>
          <pattern
            id="grid-dots"
            width={GRID_SIZE}
            height={GRID_SIZE}
            patternUnits="userSpaceOnUse"
            patternTransform={`translate(${viewBox.x % GRID_SIZE},${viewBox.y % GRID_SIZE})`}
          >
            <circle
              cx={GRID_SIZE / 2}
              cy={GRID_SIZE / 2}
              r={1}
              fill="#d0d0d0"
            />
          </pattern>
        </defs>
        <rect
          x={viewBox.x - 200}
          y={viewBox.y - 200}
          width={viewBox.w + 400}
          height={viewBox.h + 400}
          fill="url(#grid-dots)"
        />

        {/* Wires */}
        {wires.map((wire) => {
          const d = wire.points
            .map((p, i) => `${i === 0 ? "M" : "L"} ${p.x * s} ${p.y * s}`)
            .join(" ");
          return (
            <path
              key={wire.id}
              d={d}
              stroke="#374151"
              strokeWidth={2.5}
              fill="none"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          );
        })}

        {/* Current wire being drawn */}
        {wirePoints.length > 0 && (
          <polyline
            points={wirePoints.map((p) => `${p.x * s},${p.y * s}`).join(" ")}
            stroke="#4f46e5"
            strokeWidth={2}
            fill="none"
            strokeDasharray="6,3"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        )}

        {/* Hover terminal highlight in wire mode */}
        {mode === "wire" && hoverTerminal && (
          <circle
            cx={hoverTerminal.x * s}
            cy={hoverTerminal.y * s}
            r={10}
            fill="#4f46e5"
            opacity={0.15}
            stroke="#4f46e5"
            strokeWidth={2}
          />
        )}

        {/* Terminal snap indicators in wire mode */}
        {mode === "wire" &&
          wirePoints.length > 0 &&
          (() => {
            const lastPt = wirePoints[wirePoints.length - 1];
            const indicators: React.ReactNode[] = [];
            for (const comp of components) {
              const terminals = getTerminalPositions(comp);
              for (const t of terminals) {
                if (pointEquals(t, lastPt)) continue;
                const dx = Math.abs(t.x - lastPt.x) * s;
                const dy = Math.abs(t.y - lastPt.y) * s;
                if (
                  dx <= TERMINAL_SNAP_RADIUS * 2 &&
                  dy <= TERMINAL_SNAP_RADIUS * 2
                ) {
                  indicators.push(
                    <circle
                      key={`snap-${comp.id}-${t.x}-${t.y}`}
                      cx={t.x * s}
                      cy={t.y * s}
                      r={8}
                      fill="none"
                      stroke="#4f46e5"
                      strokeWidth={1.5}
                      strokeDasharray="3,2"
                      opacity={0.6}
                    />,
                  );
                }
              }
            }
            return indicators;
          })()}

        {/* Components */}
        {components.map((comp) => (
          <CircuitComponentSVG
            key={comp.id}
            comp={comp}
            isSelected={comp.id === selectedId}
          />
        ))}

        {/* Node voltage labels */}
        {simulationResult &&
          Object.keys(simulationResult.nodeVoltages).length > 0 && (
            <text
              x={viewBox.x + 20}
              y={viewBox.y + 30}
              fontSize={14}
              fill="#1e40af"
              fontWeight="bold"
            >
              仿真结果
            </text>
          )}
      </svg>
    </div>
  );
};

const CircuitComponentSVG: React.FC<{
  comp: CircuitComponent;
  isSelected: boolean;
}> = React.memo(({ comp, isSelected }) => {
  const s = GRID_SIZE;
  const cx = comp.position.x * s;
  const cy = comp.position.y * s;
  const terminals = getTerminalPositions(comp);
  const color = isSelected ? "#4f46e5" : "#374151";

  const renderComponent = () => {
    switch (comp.type) {
      case "resistor":
      case "capacitor":
      case "inductor":
      case "ground": {
        const path = getComponentSVGPath(comp.type, comp.direction);
        return (
          <path
            d={path}
            stroke={color}
            strokeWidth={2}
            fill="none"
            strokeLinecap="round"
          />
        );
      }
      case "voltage_source": {
        const r = 1.2 * s;
        return (
          <g>
            <circle
              cx={0}
              cy={0}
              r={r}
              fill="white"
              stroke={color}
              strokeWidth={2}
            />
            <text
              x={0}
              y={-r * 0.3}
              textAnchor="middle"
              fontSize={14}
              fontWeight="bold"
              fill="#dc2626"
            >
              +
            </text>
            <text
              x={0}
              y={r * 0.5}
              textAnchor="middle"
              fontSize={14}
              fontWeight="bold"
              fill="#2563eb"
            >
              −
            </text>
            <line
              x1={0}
              y1={0}
              x2={-(COMPONENT_LENGTH / 2) * s}
              y2={0}
              stroke={color}
              strokeWidth={2}
            />
            <line
              x1={0}
              y1={0}
              x2={(COMPONENT_LENGTH / 2) * s}
              y2={0}
              stroke={color}
              strokeWidth={2}
            />
          </g>
        );
      }
      case "current_source": {
        const r = 1.2 * s;
        return (
          <g>
            <circle
              cx={0}
              cy={0}
              r={r}
              fill="white"
              stroke={color}
              strokeWidth={2}
            />
            <line
              x1={-r * 0.5}
              y1={r * 0.4}
              x2={r * 0.5}
              y2={r * 0.4}
              stroke={color}
              strokeWidth={2}
            />
            <polygon
              points={`${r * 0.5},${r * 0.4} ${r * 0.2},${r * 0.15} ${r * 0.2},${r * 0.65}`}
              fill={color}
            />
            <line
              x1={0}
              y1={0}
              x2={-(COMPONENT_LENGTH / 2) * s}
              y2={0}
              stroke={color}
              strokeWidth={2}
            />
            <line
              x1={0}
              y1={0}
              x2={(COMPONENT_LENGTH / 2) * s}
              y2={0}
              stroke={color}
              strokeWidth={2}
            />
          </g>
        );
      }
      default:
        return null;
    }
  };

  return (
    <g transform={`translate(${cx}, ${cy})`} style={{ cursor: "pointer" }}>
      {renderComponent()}

      {/* Terminal dots */}
      {terminals.map((t, i) => (
        <circle
          key={`${comp.id}-t${i}`}
          cx={(t.x - comp.position.x) * s}
          cy={(t.y - comp.position.y) * s}
          r={5}
          fill={isSelected ? "#4f46e5" : "#6b7280"}
          stroke="white"
          strokeWidth={2}
        />
      ))}

      {/* Selection highlight */}
      {isSelected && (
        <rect
          x={-(COMPONENT_LENGTH / 2) * s - 8}
          y={-2 * s - 8}
          width={COMPONENT_LENGTH * s + 16}
          height={4 * s + 16}
          rx={4}
          fill="none"
          stroke="#4f46e5"
          strokeWidth={1.5}
          strokeDasharray="4,3"
          opacity={0.6}
        />
      )}

      {/* Value label */}
      {comp.type !== "ground" && (
        <text
          x={0}
          y={comp.direction === "right" || comp.direction === "left" ? 30 : 0}
          textAnchor="middle"
          fontSize={11}
          fill="#4b5563"
          fontFamily="monospace"
          fontWeight="500"
        >
          {comp.value < 0.001
            ? `${(comp.value * 1e6).toFixed(1)}μ`
            : comp.value < 1
              ? `${(comp.value * 1e3).toFixed(1)}m`
              : comp.value >= 1000
                ? `${(comp.value / 1000).toFixed(1)}k`
                : comp.value.toFixed(1)}
          {comp.type === "resistor"
            ? "Ω"
            : comp.type === "capacitor"
              ? "F"
              : comp.type === "inductor"
                ? "H"
                : comp.type === "voltage_source"
                  ? "V"
                  : "A"}
        </text>
      )}
    </g>
  );
});

CircuitComponentSVG.displayName = "CircuitComponentSVG";

export default Canvas;
