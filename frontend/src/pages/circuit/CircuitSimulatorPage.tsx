import { useState, useRef, useEffect, useCallback } from "react";
import {
  ZoomIn,
  ZoomOut,
  Maximize2,
  Download,
  Upload,
  Trash2,
  MousePointer,
  Pen,
  Grid3X3,
  BookOpen,
  Play,
  Square,
  Settings,
} from "lucide-react";
import ComponentPalette from "./ComponentPalette";
import PropertyInspector from "./PropertyInspector";
import CodeEditor from "./CodeEditor";
import { CircuitCanvasRenderer } from "./canvasRenderer";
import { simulator } from "./simulationEngine";
import { getComponentDef } from "./componentLibrary";
import { circuitTemplates } from "./circuitTemplates";
import type {
  CircuitComponent,
  Wire,
  CanvasTransform,
  DragState,
  SelectionState,
  PinMapping,
  SimulationState,
  ComponentDef,
  WireEndpoint,
} from "./types";

let nextId = 1;
function genId() {
  return `c${nextId++}`;
}
function genWireId() {
  return `w${nextId++}`;
}

export default function CircuitSimulatorPage() {
  // ─── State ───
  const [components, setComponents] = useState<CircuitComponent[]>([]);
  const [wires, setWires] = useState<Wire[]>([]);
  const [transform, setTransform] = useState<CanvasTransform>({
    x: 0,
    y: 0,
    scale: 1,
  });
  const [selection, setSelection] = useState<SelectionState>({
    componentIds: new Set(),
    wireIds: new Set(),
  });
  const [dragState, setDragState] = useState<DragState>({ type: null });
  const [tool, setTool] = useState<"select" | "wire">("select");
  const [code, setCode] = useState(
    circuitTemplates.find((t) => t.id === "stm32-traffic-light")?.code ||
      circuitTemplates[0].code,
  );
  const [pinMappings, setPinMappings] = useState<PinMapping[]>([]);
  const [simState, setSimState] = useState<SimulationState | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [showGrid, setShowGrid] = useState(true);
  const [showTemplates, setShowTemplates] = useState(false);
  const [dragWirePreview, setDragWirePreview] = useState<{
    from: { x: number; y: number };
    to: { x: number; y: number };
  } | null>(null);
  const [snapTarget, setSnapTarget] = useState<{ x: number; y: number } | null>(
    null,
  );
  const [hoveredPin, setHoveredPin] = useState<string | null>(null);
  const [showLeftPanel, setShowLeftPanel] = useState(false);
  const [showRightPanel, setShowRightPanel] = useState(false);

  useEffect(() => {
    if (showTemplates) {
      document.body.style.overflow = "hidden";
      return () => {
        document.body.style.overflow = "";
      };
    }
  }, [showTemplates]);

  const canvasRef = useRef<HTMLCanvasElement>(null);
  const rendererRef = useRef<CircuitCanvasRenderer | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const dragStartRef = useRef<{
    x: number;
    y: number;
    compX?: number;
    compY?: number;
  } | null>(null);
  const wireStartRef = useRef<WireEndpoint | null>(null);

  // ─── Canvas Setup ───

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const renderer = new CircuitCanvasRenderer(canvas);
    rendererRef.current = renderer;

    const resize = () => {
      const container = containerRef.current;
      if (!container) return;
      canvas.width = container.clientWidth * window.devicePixelRatio;
      canvas.height = container.clientHeight * window.devicePixelRatio;
      canvas.style.width = `${container.clientWidth}px`;
      canvas.style.height = `${container.clientHeight}px`;
      const ctx = canvas.getContext("2d")!;
      ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
    };

    resize();
    window.addEventListener("resize", resize);
    return () => window.removeEventListener("resize", resize);
  }, []);

  // ─── Auto-load traffic light template on first mount ───

  useEffect(() => {
    loadTemplate("stm32-traffic-light");
  }, []);

  // ─── Render Loop ───

  useEffect(() => {
    const renderer = rendererRef.current;
    if (!renderer) return;

    renderer.setTransform(transform);
    renderer.setHoveredComponent(
      selection.componentIds.values().next().value || null,
    );
    renderer.setHoveredPin(hoveredPin);

    renderer.render(
      components,
      wires,
      selection,
      simState,
      dragWirePreview,
      snapTarget,
    );
  }, [
    components,
    wires,
    selection,
    transform,
    simState,
    dragWirePreview,
    hoveredPin,
    snapTarget,
  ]);

  // ─── Simulation ───

  useEffect(() => {
    simulator.setOnChange((state) => {
      setSimState(state);
      // Trigger re-render
      setComponents((prev) => [...prev]);
    });
  }, []);

  const handleRun = useCallback(() => {
    simulator.setCircuit(components, wires);
    simulator.setCode(code, pinMappings);
    simulator.start();
    setIsRunning(true);
  }, [components, wires, code, pinMappings]);

  const handleStop = useCallback(() => {
    simulator.stop();
    setIsRunning(false);
    setSimState(null);
  }, []);

  // ─── Mouse Events ───

  const getCanvasPos = (e: React.MouseEvent): { x: number; y: number } => {
    const canvas = canvasRef.current!;
    const rect = canvas.getBoundingClientRect();
    return {
      x: (e.clientX - rect.left - transform.x) / transform.scale,
      y: (e.clientY - rect.top - transform.y) / transform.scale,
    };
  };

  const findComponentAt = (x: number, y: number): CircuitComponent | null => {
    // Search in reverse order (top-most first)
    for (let i = components.length - 1; i >= 0; i--) {
      const comp = components[i];
      const def = getComponentDef(comp.type);
      if (
        x >= comp.x &&
        x <= comp.x + def.width &&
        y >= comp.y &&
        y <= comp.y + def.height
      ) {
        return comp;
      }
    }
    return null;
  };

  const findPinAt = (
    x: number,
    y: number,
  ): { componentId: string; pinId: string } | null => {
    const threshold = 10 / transform.scale;
    for (const comp of components) {
      const def = getComponentDef(comp.type);
      for (const pin of def.pins) {
        const pos = rendererRef.current?.getPinWorldPos(comp, pin);
        if (pos) {
          const dx = x - pos.x;
          const dy = y - pos.y;
          if (Math.sqrt(dx * dx + dy * dy) < threshold) {
            return { componentId: comp.id, pinId: pin.id };
          }
        }
      }
    }
    return null;
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    if (e.button === 2) return; // right click handled separately
    const pos = getCanvasPos(e);

    // Check for pin click (wire mode or auto-detect)
    const pin = findPinAt(pos.x, pos.y);
    if (pin && (tool === "wire" || e.shiftKey)) {
      setDragState({ type: "wire", fromPin: pin });
      wireStartRef.current = pin;
      const pinPos = rendererRef.current?.getPinWorldPos(
        components.find((c) => c.id === pin.componentId)!,
        getComponentDef(
          components.find((c) => c.id === pin.componentId)!.type,
        ).pins.find((p) => p.id === pin.pinId)!,
      );
      if (pinPos) {
        setDragWirePreview({ from: pinPos, to: pos });
      }
      return;
    }

    // Check for component click
    const comp = findComponentAt(pos.x, pos.y);
    if (comp) {
      if (e.ctrlKey || e.metaKey) {
        // Toggle selection
        setSelection((prev) => {
          const next = new Set(prev.componentIds);
          if (next.has(comp.id)) next.delete(comp.id);
          else next.add(comp.id);
          return { componentIds: next, wireIds: prev.wireIds };
        });
      } else {
        if (!selection.componentIds.has(comp.id)) {
          setSelection({
            componentIds: new Set([comp.id]),
            wireIds: new Set(),
          });
        }
      }
      setDragState({
        type: "component",
        componentId: comp.id,
        offsetX: pos.x - comp.x,
        offsetY: pos.y - comp.y,
      });
      dragStartRef.current = {
        x: pos.x,
        y: pos.y,
        compX: comp.x,
        compY: comp.y,
      };
      return;
    }

    // Pan
    setSelection({ componentIds: new Set(), wireIds: new Set() });
    setDragState({ type: "pan", startX: e.clientX, startY: e.clientY });
    dragStartRef.current = {
      x: e.clientX - transform.x,
      y: e.clientY - transform.y,
    };
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    const pos = getCanvasPos(e);

    // Update hovered pin
    const pin = findPinAt(pos.x, pos.y);
    setHoveredPin(pin ? `${pin.componentId}:${pin.pinId}` : null);

    if (dragState.type === "component" && dragState.componentId) {
      const newX = pos.x - (dragState.offsetX || 0);
      const newY = pos.y - (dragState.offsetY || 0);
      // Snap to grid
      const snappedX = Math.round(newX / 20) * 20;
      const snappedY = Math.round(newY / 20) * 20;
      setComponents((prev) =>
        prev.map((c) =>
          c.id === dragState.componentId
            ? { ...c, x: snappedX, y: snappedY }
            : c,
        ),
      );
    } else if (dragState.type === "pan" && dragStartRef.current) {
      const start = dragStartRef.current;
      setTransform((prev) => ({
        ...prev,
        x: e.clientX - start.x,
        y: e.clientY - start.y,
      }));
    } else if (dragState.type === "wire" && wireStartRef.current) {
      const fromPin = wireStartRef.current;
      const fromComp = components.find((c) => c.id === fromPin.componentId);
      if (fromComp) {
        const fromDef = getComponentDef(fromComp.type);
        const pinDef = fromDef.pins.find((p) => p.id === fromPin.pinId);
        if (pinDef) {
          const pinPos = rendererRef.current?.getPinWorldPos(fromComp, pinDef);
          if (pinPos) {
            // Check for nearby pin to snap to
            const nearPin = findPinAt(pos.x, pos.y);
            if (
              nearPin &&
              (nearPin.componentId !== fromPin.componentId ||
                nearPin.pinId !== fromPin.pinId)
            ) {
              const nearComp = components.find(
                (c) => c.id === nearPin.componentId,
              );
              if (nearComp) {
                const nearDef = getComponentDef(nearComp.type);
                const nearPinDef = nearDef.pins.find(
                  (p) => p.id === nearPin.pinId,
                );
                if (nearPinDef) {
                  const snapPos = rendererRef.current?.getPinWorldPos(
                    nearComp,
                    nearPinDef,
                  );
                  if (snapPos) {
                    setSnapTarget(snapPos);
                    setDragWirePreview({ from: pinPos, to: snapPos });
                    return;
                  }
                }
              }
            }
            setSnapTarget(null);
            setDragWirePreview({ from: pinPos, to: pos });
          }
        }
      }
    }
  };

  const handleMouseUp = (e: React.MouseEvent) => {
    if (dragState.type === "wire" && wireStartRef.current) {
      const ws = wireStartRef.current;
      const pos = getCanvasPos(e);
      const endPin = findPinAt(pos.x, pos.y);
      if (
        endPin &&
        (endPin.componentId !== ws.componentId || endPin.pinId !== ws.pinId)
      ) {
        // Prevent duplicate wires
        const exists = wires.some(
          (w) =>
            (w.from.componentId === ws.componentId &&
              w.from.pinId === ws.pinId &&
              w.to.componentId === endPin.componentId &&
              w.to.pinId === endPin.pinId) ||
            (w.from.componentId === endPin.componentId &&
              w.from.pinId === endPin.pinId &&
              w.to.componentId === ws.componentId &&
              w.to.pinId === ws.pinId),
        );
        if (!exists) {
          // Create wire
          const newWire: Wire = {
            id: genWireId(),
            from: ws,
            to: endPin,
            waypoints: [],
          };
          setWires((prev) => [...prev, newWire]);
        }
      }
    }
    setDragState({ type: null });
    dragStartRef.current = null;
    wireStartRef.current = null;
    setDragWirePreview(null);
    setSnapTarget(null);
  };

  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault();
    const scaleFactor = e.deltaY > 0 ? 0.9 : 1.1;
    const newScale = Math.max(0.2, Math.min(3, transform.scale * scaleFactor));

    const canvas = canvasRef.current!;
    const rect = canvas.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;

    setTransform((prev) => ({
      x: mouseX - (mouseX - prev.x) * (newScale / prev.scale),
      y: mouseY - (mouseY - prev.y) * (newScale / prev.scale),
      scale: newScale,
    }));
  };

  // ─── Drop from palette ───

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const data = e.dataTransfer.getData("circuit-component");
    if (!data) return;
    const compDef: ComponentDef = JSON.parse(data);
    const canvas = canvasRef.current!;
    const rect = canvas.getBoundingClientRect();
    const x =
      Math.round((e.clientX - rect.left - transform.x) / transform.scale / 20) *
      20;
    const y =
      Math.round((e.clientY - rect.top - transform.y) / transform.scale / 20) *
      20;

    const newComp: CircuitComponent = {
      id: genId(),
      type: compDef.type,
      x,
      y,
      rotation: 0,
      props: { ...compDef.defaultProps },
      label: compDef.label,
    };
    setComponents((prev) => [...prev, newComp]);
    setSelection({ componentIds: new Set([newComp.id]), wireIds: new Set() });
    setShowRightPanel(true);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = "copy";
  };

  // ─── Component Operations ───

  const handleUpdateComponent = (
    id: string,
    updates: Partial<CircuitComponent>,
  ) => {
    setComponents((prev) =>
      prev.map((c) => (c.id === id ? { ...c, ...updates } : c)),
    );
  };

  const handleDeleteComponent = (id: string) => {
    setComponents((prev) => prev.filter((c) => c.id !== id));
    setWires((prev) =>
      prev.filter((w) => w.from.componentId !== id && w.to.componentId !== id),
    );
    setSelection((prev) => {
      const next = new Set(prev.componentIds);
      next.delete(id);
      return { componentIds: next, wireIds: prev.wireIds };
    });
  };

  const handleDuplicateComponent = (id: string) => {
    const comp = components.find((c) => c.id === id);
    if (!comp) return;
    const newComp: CircuitComponent = {
      ...comp,
      id: genId(),
      x: comp.x + 40,
      y: comp.y + 40,
      label: comp.label + " (副本)",
    };
    setComponents((prev) => [...prev, newComp]);
    setSelection({ componentIds: new Set([newComp.id]), wireIds: new Set() });
  };

  const handleDeleteSelected = () => {
    const compIds = selection.componentIds;
    const wireIds = selection.wireIds;
    setComponents((prev) => prev.filter((c) => !compIds.has(c.id)));
    setWires((prev) =>
      prev.filter(
        (w) =>
          !wireIds.has(w.id) &&
          !compIds.has(w.from.componentId) &&
          !compIds.has(w.to.componentId),
      ),
    );
    setSelection({ componentIds: new Set(), wireIds: new Set() });
  };

  // ─── Template Loading ───

  const loadTemplate = (templateId: string) => {
    const template = circuitTemplates.find((t) => t.id === templateId);
    if (!template) return;
    nextId = 100;
    // Build ID mapping: template IDs → new IDs
    const idMap: Record<string, string> = {};
    const newComponents = template.components.map((c) => {
      const newId = genId();
      idMap[c.id] = newId;
      return { ...c, id: newId };
    });
    const newWires = template.wires.map((w) => ({
      ...w,
      id: genWireId(),
      from: {
        ...w.from,
        componentId: idMap[w.from.componentId] || w.from.componentId,
      },
      to: { ...w.to, componentId: idMap[w.to.componentId] || w.to.componentId },
    }));

    // Auto-generate pin mappings from template wires
    const mcuComp = template.components.find(
      (c) =>
        c.type === "stm32_bluepill" ||
        c.type === "stm32" ||
        c.type === "arduino_uno" ||
        c.type === "esp32",
    );
    const autoMappings: PinMapping[] = [];
    if (mcuComp) {
      for (const wire of template.wires) {
        let mcuPinId: string | null = null;
        let targetCompId: string | null = null;
        let targetPinId: string | null = null;
        if (wire.from.componentId === mcuComp.id) {
          mcuPinId = wire.from.pinId;
          targetCompId = idMap[wire.to.componentId];
          targetPinId = wire.to.pinId;
        } else if (wire.to.componentId === mcuComp.id) {
          mcuPinId = wire.to.pinId;
          targetCompId = idMap[wire.from.componentId];
          targetPinId = wire.from.pinId;
        }
        if (mcuPinId && targetCompId && targetPinId) {
          // Skip power/ground pins — simulation handles those via propagation
          const pinDef = getComponentDef(mcuComp.type).pins.find(
            (p) => p.id === mcuPinId,
          );
          if (pinDef && pinDef.type !== "power" && pinDef.type !== "ground") {
            // Avoid duplicates
            const exists = autoMappings.some((m) => m.arduinoPin === mcuPinId);
            if (!exists) {
              // Determine mode: PWM for timer channels, output for GPIO, input for read patterns
              const isPwm =
                /TIM\d+_CH\d/.test(mcuPinId) || pinDef.type === "pwm";
              const isInput = pinDef.type === "analog";
              autoMappings.push({
                arduinoPin: mcuPinId,
                componentId: targetCompId,
                componentPinId: targetPinId,
                mode: isPwm ? "pwm" : isInput ? "input" : "output",
              });
            }
          }
        }
      }
    }

    setComponents(newComponents);
    setWires(newWires);
    setCode(template.code);
    setPinMappings(autoMappings);
    setSelection({ componentIds: new Set(), wireIds: new Set() });
    setShowTemplates(false);
    setTransform({ x: 0, y: 0, scale: 1 });
  };

  // ─── Zoom Controls ───

  const handleZoomIn = () =>
    setTransform((prev) => ({ ...prev, scale: Math.min(3, prev.scale * 1.2) }));
  const handleZoomOut = () =>
    setTransform((prev) => ({
      ...prev,
      scale: Math.max(0.2, prev.scale / 1.2),
    }));
  const handleZoomFit = () => {
    if (components.length === 0) {
      setTransform({ x: 0, y: 0, scale: 1 });
      return;
    }
    let minX = Infinity,
      minY = Infinity,
      maxX = -Infinity,
      maxY = -Infinity;
    for (const comp of components) {
      const def = getComponentDef(comp.type);
      minX = Math.min(minX, comp.x);
      minY = Math.min(minY, comp.y);
      maxX = Math.max(maxX, comp.x + def.width);
      maxY = Math.max(maxY, comp.y + def.height);
    }
    const canvas = canvasRef.current!;
    const containerW = canvas.clientWidth;
    const containerH = canvas.clientHeight;
    const padding = 60;
    const scaleX = (containerW - padding * 2) / (maxX - minX);
    const scaleY = (containerH - padding * 2) / (maxY - minY);
    const scale = Math.min(scaleX, scaleY, 2);
    setTransform({
      x:
        padding -
        minX * scale +
        (containerW - padding * 2 - (maxX - minX) * scale) / 2,
      y:
        padding -
        minY * scale +
        (containerH - padding * 2 - (maxY - minY) * scale) / 2,
      scale,
    });
  };

  // ─── Keyboard Shortcuts ───

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (
        (e.target as HTMLElement).tagName === "INPUT" ||
        (e.target as HTMLElement).tagName === "TEXTAREA"
      )
        return;

      if (e.key === "Delete" || e.key === "Backspace") {
        handleDeleteSelected();
      } else if (e.key === "Escape") {
        setSelection({ componentIds: new Set(), wireIds: new Set() });
        setDragState({ type: null });
        wireStartRef.current = null;
        setDragWirePreview(null);
        setSnapTarget(null);
      } else if (e.key === "w" || e.key === "W") {
        setTool("wire");
      } else if (e.key === "v" || e.key === "V") {
        setTool("select");
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [selection]);

  // ─── Export / Import ───

  const handleExport = () => {
    const data = { components, wires, code, pinMappings };
    const blob = new Blob([JSON.stringify(data, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "circuit.json";
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleImport = () => {
    const input = document.createElement("input");
    input.type = "file";
    input.accept = ".json";
    input.onchange = (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = (ev) => {
        try {
          const data = JSON.parse(ev.target?.result as string);
          if (data.components) setComponents(data.components);
          if (data.wires) setWires(data.wires);
          if (data.code) setCode(data.code);
          if (data.pinMappings) setPinMappings(data.pinMappings);
        } catch {
          alert("文件格式错误");
        }
      };
      reader.readAsText(file);
    };
    input.click();
  };

  const handleClear = () => {
    setComponents([]);
    setWires([]);
    setSelection({ componentIds: new Set(), wireIds: new Set() });
    setCode(circuitTemplates[0].code);
    setPinMappings([]);
  };

  // ─── Selected component ───

  const selectedComp =
    selection.componentIds.size === 1
      ? components.find(
          (c) => c.id === selection.componentIds.values().next().value,
        ) || null
      : null;

  return (
    <div className="flex flex-col h-[calc(100vh-100px)]">
      {/* Page Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h1 className="font-display text-[22px] font-bold tracking-tight text-ink">
            电路仿真器
          </h1>
          <p className="text-[14px] text-ink-secondary mt-1">
            拖拽元件、连线、编写代码，实时仿真电路
          </p>
        </div>
        <div className="flex items-center gap-2">
          {/* Mobile panel toggles */}
          <button
            onClick={() => setShowLeftPanel(!showLeftPanel)}
            className="lg:hidden flex items-center gap-1.5 px-3 py-2 rounded-xl border border-border bg-surface text-[12px] font-medium text-ink-secondary hover:text-ink hover:bg-bg transition-colors cursor-pointer"
          >
            <Grid3X3 size={14} />
            元件
          </button>
          <button
            onClick={() => setShowRightPanel(!showRightPanel)}
            className="lg:hidden flex items-center gap-1.5 px-3 py-2 rounded-xl border border-border bg-surface text-[12px] font-medium text-ink-secondary hover:text-ink hover:bg-bg transition-colors cursor-pointer"
          >
            <Settings size={14} />
            属性
          </button>
          <button
            onClick={() => setShowTemplates(!showTemplates)}
            className="flex items-center gap-1.5 px-3 py-2 rounded-xl border border-border bg-surface text-[12px] font-medium text-ink-secondary hover:text-ink hover:bg-bg transition-colors cursor-pointer"
          >
            <BookOpen size={14} />
            <span className="hidden sm:inline">示例电路</span>
          </button>
          <button
            onClick={handleImport}
            className="flex items-center gap-1.5 px-3 py-2 rounded-xl border border-border bg-surface text-[12px] font-medium text-ink-secondary hover:text-ink hover:bg-bg transition-colors cursor-pointer"
          >
            <Upload size={14} />
            <span className="hidden sm:inline">导入</span>
          </button>
          <button
            onClick={handleExport}
            className="flex items-center gap-1.5 px-3 py-2 rounded-xl border border-border bg-surface text-[12px] font-medium text-ink-secondary hover:text-ink hover:bg-bg transition-colors cursor-pointer"
          >
            <Download size={14} />
            <span className="hidden sm:inline">导出</span>
          </button>
        </div>
      </div>

      {/* Template picker overlay */}
      {showTemplates && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center  "
          onClick={() => setShowTemplates(false)}
        >
          <div
            className="bg-surface rounded-2xl shadow-2xl border border-border max-w-[700px] w-full mx-4 max-h-[80vh] overflow-hidden"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="px-6 py-4 border-b border-border">
              <h3 className="text-[16px] font-bold text-ink">示例电路</h3>
              <p className="text-[12px] text-ink-secondary mt-1">
                选择一个预设电路快速开始
              </p>
            </div>
            <div className="p-6 overflow-y-auto max-h-[60vh] grid grid-cols-2 gap-4">
              {circuitTemplates.map((t) => (
                <button
                  key={t.id}
                  onClick={() => loadTemplate(t.id)}
                  className="text-left p-4 rounded-xl border border-border hover:border-accent hover:bg-accent-light transition-all cursor-pointer group"
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[14px] font-semibold text-ink group-hover:text-accent transition-colors">
                      {t.name}
                    </span>
                    <span
                      className={`text-[10px] px-2 py-0.5 rounded-full ${
                        t.difficulty === "beginner"
                          ? "bg-teal-light text-teal"
                          : t.difficulty === "intermediate"
                            ? "bg-warm-light text-warm"
                            : "bg-accent-light text-accent"
                      }`}
                    >
                      {t.difficulty === "beginner"
                        ? "入门"
                        : t.difficulty === "intermediate"
                          ? "进阶"
                          : "高级"}
                    </span>
                  </div>
                  <p className="text-[12px] text-ink-secondary leading-relaxed">
                    {t.description}
                  </p>
                  <div className="mt-2 flex items-center gap-2 text-[10px] text-ink-faint">
                    <span>{t.components.length} 个元件</span>
                    <span>·</span>
                    <span>{t.wires.length} 根导线</span>
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Toolbar */}
      <div className="flex items-center gap-1 mb-3 p-1.5 bg-surface border border-border rounded-xl overflow-x-auto scrollbar-hide">
        {/* Tool selector */}
        <button
          onClick={() => setTool("select")}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[12px] font-medium transition-colors cursor-pointer ${
            tool === "select"
              ? "bg-ink text-surface"
              : "text-ink-secondary hover:bg-bg"
          }`}
        >
          <MousePointer size={13} />
          选择
        </button>
        <button
          onClick={() => setTool("wire")}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[12px] font-medium transition-colors cursor-pointer ${
            tool === "wire"
              ? "bg-ink text-surface"
              : "text-ink-secondary hover:bg-bg"
          }`}
        >
          <Pen size={13} />
          连线
        </button>

        <div className="w-px h-5 bg-border mx-1" />

        {/* Zoom */}
        <button
          onClick={handleZoomOut}
          className="w-8 h-8 rounded-lg flex items-center justify-center text-ink-secondary hover:bg-bg transition-colors cursor-pointer"
          title="缩小"
        >
          <ZoomOut size={14} />
        </button>
        <span className="text-[11px] text-ink-faint w-10 text-center">
          {Math.round(transform.scale * 100)}%
        </span>
        <button
          onClick={handleZoomIn}
          className="w-8 h-8 rounded-lg flex items-center justify-center text-ink-secondary hover:bg-bg transition-colors cursor-pointer"
          title="放大"
        >
          <ZoomIn size={14} />
        </button>
        <button
          onClick={handleZoomFit}
          className="w-8 h-8 rounded-lg flex items-center justify-center text-ink-secondary hover:bg-bg transition-colors cursor-pointer"
          title="适应画布"
        >
          <Maximize2 size={14} />
        </button>

        <div className="w-px h-5 bg-border mx-1" />

        {/* Grid */}
        <button
          onClick={() => setShowGrid(!showGrid)}
          className={`w-8 h-8 rounded-lg flex items-center justify-center transition-colors cursor-pointer ${
            showGrid
              ? "bg-accent-light text-accent"
              : "text-ink-secondary hover:bg-bg"
          }`}
          title="网格"
        >
          <Grid3X3 size={14} />
        </button>

        <div className="flex-1" />

        {/* Simulation controls */}
        {isRunning ? (
          <button
            onClick={handleStop}
            className="flex items-center gap-1.5 px-4 py-1.5 rounded-lg bg-red-500 text-white text-[12px] font-semibold hover:bg-red-600 transition-colors cursor-pointer"
          >
            <Square size={12} />
            停止仿真
          </button>
        ) : (
          <button
            onClick={handleRun}
            className="flex items-center gap-1.5 px-4 py-1.5 rounded-lg bg-teal text-white text-[12px] font-semibold hover:bg-teal/90 transition-colors cursor-pointer"
          >
            <Play size={12} />
            运行仿真
          </button>
        )}

        <div className="w-px h-5 bg-border mx-1" />

        {/* Clear */}
        <button
          onClick={handleClear}
          className="w-8 h-8 rounded-lg flex items-center justify-center text-ink-faint hover:text-red-500 hover:bg-red-50 transition-colors cursor-pointer"
          title="清空画布"
        >
          <Trash2 size={14} />
        </button>
      </div>

      {/* Main content */}
      <div className="flex flex-1 gap-4 min-h-0 relative">
        {/* Mobile: Left panel overlay */}
        {showLeftPanel && (
          <div
            className="lg:hidden fixed inset-0 z-40 "
            onClick={() => setShowLeftPanel(false)}
          >
            <div
              className="absolute left-0 top-0 bottom-0 w-[260px] bg-surface p-3 overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <ComponentPalette
                onDragStart={() => {
                  setShowRightPanel(true);
                  setShowLeftPanel(false);
                }}
              />
            </div>
          </div>
        )}

        {/* Desktop: Left: Component Palette */}
        <div className="hidden lg:block">
          <ComponentPalette onDragStart={() => setShowRightPanel(true)} />
        </div>

        {/* Center: Canvas + Code Editor */}
        <div className="flex flex-col flex-1 min-w-0 gap-4">
          {/* Canvas */}
          <div
            ref={containerRef}
            className="flex-1 bg-surface border border-border rounded-2xl card-shadow overflow-hidden relative cursor-crosshair"
            onMouseDown={handleMouseDown}
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
            onWheel={handleWheel}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onContextMenu={(e) => {
              e.preventDefault();
              // Right-click: delete component under cursor
              const pos = getCanvasPos(e);
              const comp = findComponentAt(pos.x, pos.y);
              if (comp) handleDeleteComponent(comp.id);
            }}
          >
            <canvas ref={canvasRef} className="block" />

            {/* Canvas overlay info */}
            {components.length === 0 && (
              <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                <div className="text-center">
                  <div className="w-16 h-16 rounded-2xl bg-accent-light flex items-center justify-center mx-auto mb-4">
                    <Grid3X3 size={28} className="text-accent" />
                  </div>
                  <p className="text-[14px] font-semibold text-ink mb-1">
                    从左侧拖拽元件到画布
                  </p>
                  <p className="text-[12px] text-ink-faint">
                    或点击"示例电路"快速开始
                  </p>
                </div>
              </div>
            )}

            {/* Running indicator */}
            {isRunning && (
              <div className="absolute top-3 left-3 flex items-center gap-2 px-3 py-1.5 bg-teal/90 text-white rounded-lg text-[11px] font-semibold shadow-lg">
                <span className="w-2 h-2 rounded-full bg-white animate-pulse" />
                仿真运行中 · T={simState?.time || 0}ms
              </div>
            )}

            {/* Component count */}
            <div className="absolute bottom-3 left-3 text-[10px] text-ink-faint bg-surface/80  px-2 py-1 rounded-lg">
              {components.length} 元件 · {wires.length} 导线
            </div>
          </div>

          {/* Code Editor */}
          <div className="h-[260px] shrink-0 bg-surface border border-border rounded-2xl card-shadow overflow-hidden">
            <CodeEditor
              code={code}
              onCodeChange={setCode}
              pinMappings={pinMappings}
              onPinMappingsChange={setPinMappings}
              components={components}
              isRunning={isRunning}
              onRun={handleRun}
              onStop={handleStop}
              logs={simState?.logs || []}
              errors={simState?.errors || []}
            />
          </div>
        </div>

        {/* Mobile: Right panel overlay */}
        {showRightPanel && (
          <div
            className="lg:hidden fixed inset-0 z-40 "
            onClick={() => setShowRightPanel(false)}
          >
            <div
              className="absolute right-0 top-0 bottom-0 w-[260px] bg-surface p-3 overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <PropertyInspector
                component={selectedComp}
                onUpdate={handleUpdateComponent}
                onDelete={handleDeleteComponent}
                onDuplicate={handleDuplicateComponent}
                simState={simState}
              />
            </div>
          </div>
        )}

        {/* Desktop: Right: Property Inspector */}
        <div className="hidden lg:block">
          <PropertyInspector
            component={selectedComp}
            onUpdate={handleUpdateComponent}
            onDelete={handleDeleteComponent}
            onDuplicate={handleDuplicateComponent}
            simState={simState}
          />
        </div>
      </div>
    </div>
  );
}
