import type {
  CircuitComponent,
  Wire,
  CanvasTransform,
  SelectionState,
  SimulationState,
  PinDef,
  ComponentType,
} from "./types";
import { getComponentDef } from "./componentLibrary";

// ─── Color Palette ───

const COLORS = {
  bg: "#ffffff",
  grid: "#f0f0f0",
  gridMajor: "#e0e0e0",
  component: "#1a1208",
  componentFill: "#ffffff",
  componentStroke: "#6b5e4f",
  pin: "#c44b2b",
  pinHover: "#ff6b4a",
  pinConnected: "#1a6b5a",
  wire: "#1a1208",
  wireActive: "#c44b2b",
  selected: "#c44b2b",
  selectedFill: "rgba(196, 75, 43, 0.08)",
  hover: "rgba(196, 75, 43, 0.15)",
  ledOn: "#ff4444",
  ledOff: "#882222",
  power: "#e8a44a",
  ground: "#6b5e4f",
  text: "#1a1208",
  textSecondary: "#6b5e4f",
  textFaint: "#a39480",
};

// ─── Canvas Renderer ───

export class CircuitCanvasRenderer {
  private ctx: CanvasRenderingContext2D;
  private canvas: HTMLCanvasElement;
  private transform: CanvasTransform = { x: 0, y: 0, scale: 1 };
  private hoveredComponent: string | null = null;
  private hoveredPin: string | null = null; // "componentId:pinId"
  private animFrame = 0;

  constructor(canvas: HTMLCanvasElement) {
    this.canvas = canvas;
    this.ctx = canvas.getContext("2d")!;
  }

  setTransform(t: CanvasTransform) {
    this.transform = t;
  }

  setHoveredComponent(id: string | null) {
    this.hoveredComponent = id;
  }

  setHoveredPin(pin: string | null) {
    this.hoveredPin = pin;
  }

  // ─── Main Render ───

  render(
    components: CircuitComponent[],
    wires: Wire[],
    selection: SelectionState,
    simState: SimulationState | null,
    dragPreview: {
      from: { x: number; y: number };
      to: { x: number; y: number };
    } | null,
    snapTarget?: { x: number; y: number } | null,
  ) {
    const { ctx, canvas, transform } = this;
    this.animFrame++;

    // Clear
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Background
    ctx.fillStyle = COLORS.bg;
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Apply transform
    ctx.save();
    ctx.translate(transform.x, transform.y);
    ctx.scale(transform.scale, transform.scale);

    // Draw grid
    this.drawGrid(canvas.width, canvas.height);

    // Draw wires
    for (const wire of wires) {
      this.drawWire(wire, components, selection.wireIds.has(wire.id), simState);
    }

    // Draw drag preview wire
    if (dragPreview) {
      this.drawDragWire(dragPreview.from, dragPreview.to);
    }

    // Draw snap indicator
    if (snapTarget) {
      this.drawSnapIndicator(snapTarget.x, snapTarget.y);
    }

    // Draw components
    const connectedPins = new Set<string>();
    for (const wire of wires) {
      connectedPins.add(`${wire.from.componentId}:${wire.from.pinId}`);
      connectedPins.add(`${wire.to.componentId}:${wire.to.pinId}`);
    }
    for (const comp of components) {
      const isSelected = selection.componentIds.has(comp.id);
      const isHovered = this.hoveredComponent === comp.id;
      this.drawComponent(comp, isSelected, isHovered, simState, connectedPins);
    }

    ctx.restore();
  }

  // ─── Grid ───

  private drawGrid(canvasW: number, canvasH: number) {
    const { ctx, transform } = this;
    const gridSize = 20;
    const majorGridSize = 100;

    const startX =
      Math.floor(-transform.x / transform.scale / gridSize) * gridSize;
    const startY =
      Math.floor(-transform.y / transform.scale / gridSize) * gridSize;
    const endX = startX + canvasW / transform.scale + gridSize * 2;
    const endY = startY + canvasH / transform.scale + gridSize * 2;

    // Minor grid
    ctx.strokeStyle = COLORS.grid;
    ctx.lineWidth = 0.5 / transform.scale;
    ctx.beginPath();
    for (let x = startX; x < endX; x += gridSize) {
      if (x % majorGridSize === 0) continue;
      ctx.moveTo(x, startY);
      ctx.lineTo(x, endY);
    }
    for (let y = startY; y < endY; y += gridSize) {
      if (y % majorGridSize === 0) continue;
      ctx.moveTo(startX, y);
      ctx.lineTo(endX, y);
    }
    ctx.stroke();

    // Major grid
    ctx.strokeStyle = COLORS.gridMajor;
    ctx.lineWidth = 1 / transform.scale;
    ctx.beginPath();
    for (
      let x = Math.floor(startX / majorGridSize) * majorGridSize;
      x < endX;
      x += majorGridSize
    ) {
      ctx.moveTo(x, startY);
      ctx.lineTo(x, endY);
    }
    for (
      let y = Math.floor(startY / majorGridSize) * majorGridSize;
      y < endY;
      y += majorGridSize
    ) {
      ctx.moveTo(startX, y);
      ctx.lineTo(endX, y);
    }
    ctx.stroke();
  }

  // ─── Wire Drawing ───

  private drawWire(
    wire: Wire,
    components: CircuitComponent[],
    isSelected: boolean,
    simState: SimulationState | null,
  ) {
    const { ctx, transform } = this;

    const fromComp = components.find((c) => c.id === wire.from.componentId);
    const toComp = components.find((c) => c.id === wire.to.componentId);
    if (!fromComp || !toComp) return;

    const fromDef = getComponentDef(fromComp.type);
    const toDef = getComponentDef(toComp.type);
    const fromPinDef = fromDef.pins.find((p) => p.id === wire.from.pinId);
    const toPinDef = toDef.pins.find((p) => p.id === wire.to.pinId);
    if (!fromPinDef || !toPinDef) return;

    const from = this.getPinWorldPos(fromComp, fromPinDef);
    const to = this.getPinWorldPos(toComp, toPinDef);

    // Check if wire is active
    let isActive = false;
    if (simState) {
      const fromKey = `${wire.from.componentId}:${wire.from.pinId}`;
      const fromState = simState.pinStates[fromKey];
      isActive = fromState?.isHigh || false;
    }

    ctx.strokeStyle = isSelected
      ? COLORS.selected
      : isActive
        ? COLORS.wireActive
        : COLORS.wire;
    ctx.lineWidth = isSelected ? 3 / transform.scale : 2 / transform.scale;
    ctx.lineCap = "round";
    ctx.lineJoin = "round";

    if (wire.waypoints.length > 0) {
      // Draw smooth curve through waypoints
      this.drawSmoothWirePath(from, wire.waypoints, to);
    } else {
      // Draw smooth bezier curve based on pin directions
      this.drawBezierWire(from, fromPinDef.side, to, toPinDef.side);
    }

    // Junction dots at endpoints
    ctx.fillStyle = isActive ? COLORS.wireActive : COLORS.wire;
    ctx.beginPath();
    ctx.arc(from.x, from.y, 3 / transform.scale, 0, Math.PI * 2);
    ctx.fill();
    ctx.beginPath();
    ctx.arc(to.x, to.y, 3 / transform.scale, 0, Math.PI * 2);
    ctx.fill();
  }

  private drawBezierWire(
    from: { x: number; y: number },
    fromSide: "top" | "bottom" | "left" | "right",
    to: { x: number; y: number },
    toSide: "top" | "bottom" | "left" | "right",
  ) {
    const { ctx } = this;
    const dist = Math.sqrt((to.x - from.x) ** 2 + (to.y - from.y) ** 2);
    const tension = Math.min(Math.max(dist * 0.4, 30), 120);

    const dirMap: Record<string, { x: number; y: number }> = {
      right: { x: 1, y: 0 },
      left: { x: -1, y: 0 },
      top: { x: 0, y: -1 },
      bottom: { x: 0, y: 1 },
    };
    const fd = dirMap[fromSide] || { x: 1, y: 0 };
    const td = dirMap[toSide] || { x: -1, y: 0 };

    const cp1 = { x: from.x + fd.x * tension, y: from.y + fd.y * tension };
    const cp2 = { x: to.x + td.x * tension, y: to.y + td.y * tension };

    ctx.beginPath();
    ctx.moveTo(from.x, from.y);
    ctx.bezierCurveTo(cp1.x, cp1.y, cp2.x, cp2.y, to.x, to.y);
    ctx.stroke();
  }

  private drawSmoothWirePath(
    from: { x: number; y: number },
    waypoints: { x: number; y: number }[],
    to: { x: number; y: number },
  ) {
    const { ctx } = this;
    const allPts = [from, ...waypoints, to];

    if (allPts.length < 3) {
      ctx.beginPath();
      ctx.moveTo(from.x, from.y);
      ctx.lineTo(to.x, to.y);
      ctx.stroke();
      return;
    }

    ctx.beginPath();
    ctx.moveTo(allPts[0].x, allPts[0].y);
    for (let i = 0; i < allPts.length - 1; i++) {
      const p0 = allPts[Math.max(0, i - 1)];
      const p1 = allPts[i];
      const p2 = allPts[i + 1];
      const p3 = allPts[Math.min(allPts.length - 1, i + 2)];

      const cp1x = p1.x + (p2.x - p0.x) / 6;
      const cp1y = p1.y + (p2.y - p0.y) / 6;
      const cp2x = p2.x - (p3.x - p1.x) / 6;
      const cp2y = p2.y - (p3.y - p1.y) / 6;

      ctx.bezierCurveTo(cp1x, cp1y, cp2x, cp2y, p2.x, p2.y);
    }
    ctx.stroke();
  }

  private drawDragWire(
    from: { x: number; y: number },
    to: { x: number; y: number },
  ) {
    const { ctx, transform } = this;
    ctx.strokeStyle = COLORS.selected;
    ctx.lineWidth = 2 / transform.scale;
    ctx.setLineDash([6 / transform.scale, 4 / transform.scale]);
    ctx.lineCap = "round";

    const dist = Math.sqrt((to.x - from.x) ** 2 + (to.y - from.y) ** 2);
    const tension = Math.min(Math.max(dist * 0.35, 20), 80);

    // Assume dragging from right side, curving toward the cursor
    const cp1 = { x: from.x + tension, y: from.y };
    const cp2 = { x: to.x - tension, y: to.y };

    ctx.beginPath();
    ctx.moveTo(from.x, from.y);
    ctx.bezierCurveTo(cp1.x, cp1.y, cp2.x, cp2.y, to.x, to.y);
    ctx.stroke();
    ctx.setLineDash([]);
  }

  private drawSnapIndicator(x: number, y: number) {
    const { ctx, transform } = this;
    const pulse = (Math.sin(this.animFrame * 0.15) + 1) / 2;
    const radius = 8 + pulse * 4;

    // Outer glow ring
    ctx.strokeStyle = COLORS.selected + "80";
    ctx.lineWidth = 2 / transform.scale;
    ctx.beginPath();
    ctx.arc(x, y, radius / transform.scale, 0, Math.PI * 2);
    ctx.stroke();

    // Inner filled dot
    ctx.fillStyle = COLORS.selected + "40";
    ctx.beginPath();
    ctx.arc(x, y, (radius - 2) / transform.scale, 0, Math.PI * 2);
    ctx.fill();
  }

  // ─── Component Drawing ───

  private drawComponent(
    comp: CircuitComponent,
    isSelected: boolean,
    isHovered: boolean,
    simState: SimulationState | null,
    connectedPins?: Set<string>,
  ) {
    const { ctx, transform } = this;
    const def = getComponentDef(comp.type);
    const w = def.width;
    const h = def.height;

    ctx.save();
    ctx.translate(comp.x + w / 2, comp.y + h / 2);
    ctx.rotate((comp.rotation * Math.PI) / 180);
    ctx.translate(-w / 2, -h / 2);

    // Selection / hover highlight
    if (isSelected) {
      ctx.fillStyle = COLORS.selectedFill;
      ctx.strokeStyle = COLORS.selected;
      ctx.lineWidth = 2 / transform.scale;
      this.roundRect(-4, -4, w + 8, h + 8, 6);
      ctx.fill();
      ctx.stroke();
    } else if (isHovered) {
      ctx.fillStyle = COLORS.hover;
      this.roundRect(-2, -2, w + 4, h + 4, 4);
      ctx.fill();
    }

    // Draw component body based on type
    const compState = simState?.componentStates[comp.id];
    this.drawComponentBody(comp.type, w, h, comp.props, compState);

    // Draw pins
    for (const pin of def.pins) {
      const pinPos = this.getPinLocalPos(pin, w, h);
      const pinKey = `${comp.id}:${pin.id}`;
      const isPinHovered = this.hoveredPin === pinKey;
      const pinState = simState?.pinStates[pinKey];
      const isConnected = connectedPins?.has(pinKey) ?? false;

      this.drawPin(
        pinPos.x,
        pinPos.y,
        pin.type,
        isPinHovered,
        isConnected,
        pinState?.isHigh,
      );
    }

    // Label
    ctx.fillStyle = COLORS.text;
    ctx.font = `${10 / transform.scale}px "DM Sans", sans-serif`;
    ctx.textAlign = "center";
    ctx.textBaseline = "top";
    ctx.fillText(comp.label || def.label, w / 2, h + 6);

    ctx.restore();
  }

  // ─── Component Body Renderers ───

  private drawComponentBody(
    type: ComponentType,
    w: number,
    h: number,
    props: Record<string, string | number | boolean>,
    state?: Record<string, string | number | boolean>,
  ) {
    switch (type) {
      case "led":
        this.drawLED(w, h, props, state);
        break;
      case "resistor":
        this.drawResistor(w, h, props);
        break;
      case "capacitor":
        this.drawCapacitor(w, h, props);
        break;
      case "battery":
        this.drawBattery(w, h, props);
        break;
      case "button":
        this.drawButton(w, h, state);
        break;
      case "switch":
        this.drawSwitch(w, h, state);
        break;
      case "motor":
        this.drawMotor(w, h, state);
        break;
      case "buzzer":
        this.drawBuzzer(w, h, state);
        break;
      case "potentiometer":
        this.drawPotentiometer(w, h, props);
        break;
      case "servo":
        this.drawServo(w, h, state);
        break;
      case "arduino_uno":
      case "esp32":
      case "stm32":
        this.drawMCU(type, w, h, props);
        break;
      case "stm32_bluepill":
        this.drawBluePill(w, h, props);
        break;
      case "oled_ssd1306":
        this.drawOLED(w, h, state);
        break;
      case "mpu6050":
        this.drawMPU6050(w, h, state);
        break;
      case "stlink":
        this.drawSTLink(w, h);
        break;
      case "usb_ttl":
        this.drawUSBTTL(w, h);
        break;
      case "ir_sensor":
        this.drawIRSensor(w, h, state);
        break;
      case "rotary_encoder":
        this.drawRotaryEncoder(w, h, state);
        break;
      case "w25q64":
        this.drawW25Q64(w, h);
        break;
      case "seven_segment":
        this.drawSevenSegment(w, h, state);
        break;
      case "lcd":
        this.drawLCD(w, h, state);
        break;
      case "ultrasonic":
        this.drawUltrasonic(w, h, state);
        break;
      case "photoresistor":
        this.drawPhotoresistor(w, h, props);
        break;
      case "thermistor":
        this.drawThermistor(w, h, props);
        break;
      case "ground":
        this.drawGroundSymbol(w, h);
        break;
      case "vcc":
        this.drawVCCSymbol(w, h, props);
        break;
      case "breadboard":
        this.drawBreadboard(w, h);
        break;
      default:
        this.drawGenericBox(w, h, type);
    }
  }

  private drawLED(
    w: number,
    h: number,
    props: Record<string, string | number | boolean>,
    state?: Record<string, string | number | boolean>,
  ) {
    const { ctx } = this;
    const color = (props.color as string) || "#ff3333";
    const isOn = state?.on as boolean;
    const brightness = (state?.brightness as number) || 0;

    // LED body (dome shape)
    ctx.beginPath();
    ctx.arc(w / 2, h * 0.35, w * 0.35, Math.PI, 0);
    ctx.lineTo(w * 0.85, h * 0.55);
    ctx.lineTo(w * 0.15, h * 0.55);
    ctx.closePath();

    if (isOn) {
      // Glow effect
      const gradient = ctx.createRadialGradient(
        w / 2,
        h * 0.35,
        0,
        w / 2,
        h * 0.35,
        w * 0.5,
      );
      gradient.addColorStop(0, color);
      gradient.addColorStop(0.6, color + "80");
      gradient.addColorStop(1, color + "00");
      ctx.fillStyle = gradient;
      ctx.fill();

      // Inner glow
      ctx.fillStyle = color;
      ctx.globalAlpha = brightness;
      ctx.fill();
      ctx.globalAlpha = 1;
    } else {
      ctx.fillStyle = COLORS.componentFill;
      ctx.fill();
    }
    ctx.strokeStyle = COLORS.componentStroke;
    ctx.lineWidth = 1.5;
    ctx.stroke();

    // Flat side (cathode)
    ctx.beginPath();
    ctx.moveTo(w * 0.15, h * 0.55);
    ctx.lineTo(w * 0.85, h * 0.55);
    ctx.strokeStyle = COLORS.componentStroke;
    ctx.lineWidth = 1.5;
    ctx.stroke();

    // Legs
    ctx.strokeStyle = COLORS.componentStroke;
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(w * 0.4, h * 0.55);
    ctx.lineTo(w * 0.4, h);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(w * 0.6, h * 0.55);
    ctx.lineTo(w * 0.6, h);
    ctx.stroke();

    // Light rays when on
    if (isOn) {
      ctx.strokeStyle = color + "60";
      ctx.lineWidth = 1;
      for (let i = -2; i <= 2; i++) {
        const angle = -Math.PI / 2 + (i * Math.PI) / 8;
        const startX = w / 2 + Math.cos(angle) * w * 0.4;
        const startY = h * 0.35 + Math.sin(angle) * w * 0.4;
        const endX = w / 2 + Math.cos(angle) * w * 0.65;
        const endY = h * 0.35 + Math.sin(angle) * w * 0.65;
        ctx.beginPath();
        ctx.moveTo(startX, startY);
        ctx.lineTo(endX, endY);
        ctx.stroke();
      }
    }
  }

  private drawResistor(
    w: number,
    h: number,
    props: Record<string, string | number | boolean>,
  ) {
    const { ctx } = this;
    const resistance = props.resistance as number;

    // Zigzag body
    ctx.strokeStyle = COLORS.componentStroke;
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(0, h / 2);
    ctx.lineTo(w * 0.15, h / 2);

    const segments = 6;
    const segW = (w * 0.7) / segments;
    const amplitude = h * 0.35;
    for (let i = 0; i < segments; i++) {
      const x = w * 0.15 + i * segW;
      const dir = i % 2 === 0 ? -1 : 1;
      ctx.lineTo(x + segW / 2, h / 2 + dir * amplitude);
      ctx.lineTo(x + segW, h / 2);
    }

    ctx.lineTo(w * 0.85, h / 2);
    ctx.lineTo(w, h / 2);
    ctx.stroke();

    // Color bands
    if (resistance) {
      const bands = resistanceToBands(resistance);
      const bandW = w * 0.06;
      const startX = w * 0.25;
      for (let i = 0; i < bands.length && i < 4; i++) {
        ctx.fillStyle = bands[i];
        ctx.fillRect(startX + i * w * 0.13, h * 0.15, bandW, h * 0.7);
      }
    }

    // Value label
    ctx.fillStyle = COLORS.textSecondary;
    ctx.font = '9px "DM Sans", sans-serif';
    ctx.textAlign = "center";
    ctx.fillText(`${resistance}Ω`, w / 2, h + 10);
  }

  private drawCapacitor(
    w: number,
    h: number,
    _props: Record<string, string | number | boolean>,
  ) {
    const { ctx } = this;
    // Two parallel plates
    ctx.strokeStyle = COLORS.componentStroke;
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(w * 0.3, h * 0.2);
    ctx.lineTo(w * 0.3, h * 0.8);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(w * 0.7, h * 0.2);
    ctx.lineTo(w * 0.7, h * 0.8);
    ctx.stroke();

    // Leads
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(0, h / 2);
    ctx.lineTo(w * 0.3, h / 2);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(w * 0.7, h / 2);
    ctx.lineTo(w, h / 2);
    ctx.stroke();

    // + symbol
    ctx.fillStyle = COLORS.textSecondary;
    ctx.font = 'bold 10px "DM Sans", sans-serif';
    ctx.textAlign = "center";
    ctx.fillText("+", w * 0.15, h / 2 - 6);
  }

  private drawBattery(
    w: number,
    h: number,
    props: Record<string, string | number | boolean>,
  ) {
    const { ctx } = this;
    const voltage = props.voltage as number;

    // Battery body
    ctx.fillStyle = COLORS.componentFill;
    ctx.strokeStyle = COLORS.componentStroke;
    ctx.lineWidth = 1.5;
    this.roundRect(w * 0.2, h * 0.15, w * 0.6, h * 0.7, 4);
    ctx.fill();
    ctx.stroke();

    // Positive terminal
    ctx.fillStyle = COLORS.power;
    ctx.fillRect(w * 0.35, h * 0.1, w * 0.3, h * 0.08);

    // + and - symbols
    ctx.fillStyle = COLORS.text;
    ctx.font = 'bold 14px "DM Sans", sans-serif';
    ctx.textAlign = "center";
    ctx.fillText("+", w / 2, h * 0.35);
    ctx.font = 'bold 16px "DM Sans", sans-serif';
    ctx.fillText("−", w / 2, h * 0.75);

    // Voltage
    ctx.fillStyle = COLORS.textSecondary;
    ctx.font = '10px "DM Sans", sans-serif';
    ctx.fillText(`${voltage}V`, w / 2, h * 0.55);

    // Leads
    ctx.strokeStyle = COLORS.componentStroke;
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(w / 2, 0);
    ctx.lineTo(w / 2, h * 0.1);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(w / 2, h * 0.85);
    ctx.lineTo(w / 2, h);
    ctx.stroke();
  }

  private drawButton(
    w: number,
    h: number,
    state?: Record<string, string | number | boolean>,
  ) {
    const { ctx } = this;
    const pressed = state?.pressed as boolean;

    // Button base
    ctx.fillStyle = COLORS.componentFill;
    ctx.strokeStyle = COLORS.componentStroke;
    ctx.lineWidth = 1.5;
    this.roundRect(w * 0.1, h * 0.4, w * 0.8, h * 0.3, 4);
    ctx.fill();
    ctx.stroke();

    // Button cap
    ctx.fillStyle = pressed ? "#ddd" : "#f0f0f0";
    ctx.strokeStyle = COLORS.componentStroke;
    this.roundRect(w * 0.2, pressed ? h * 0.35 : h * 0.2, w * 0.6, h * 0.2, 4);
    ctx.fill();
    ctx.stroke();

    // Leads
    ctx.strokeStyle = COLORS.componentStroke;
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(0, h / 2);
    ctx.lineTo(w * 0.1, h / 2);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(w * 0.9, h / 2);
    ctx.lineTo(w, h / 2);
    ctx.stroke();
  }

  private drawSwitch(
    w: number,
    h: number,
    state?: Record<string, string | number | boolean>,
  ) {
    const { ctx } = this;
    const on = state?.on as boolean;

    // Base
    ctx.fillStyle = COLORS.componentFill;
    ctx.strokeStyle = COLORS.componentStroke;
    ctx.lineWidth = 1.5;
    this.roundRect(w * 0.1, h * 0.3, w * 0.8, h * 0.4, 4);
    ctx.fill();
    ctx.stroke();

    // Switch lever
    ctx.strokeStyle = COLORS.component;
    ctx.lineWidth = 2.5;
    ctx.beginPath();
    ctx.moveTo(w * 0.3, h * 0.5);
    if (on) {
      ctx.lineTo(w * 0.7, h * 0.5);
    } else {
      ctx.lineTo(w * 0.55, h * 0.2);
    }
    ctx.stroke();

    // Contact points
    ctx.fillStyle = COLORS.pin;
    ctx.beginPath();
    ctx.arc(w * 0.3, h * 0.5, 3, 0, Math.PI * 2);
    ctx.fill();
    ctx.beginPath();
    ctx.arc(w * 0.7, h * 0.5, 3, 0, Math.PI * 2);
    ctx.fill();
  }

  private drawMotor(
    w: number,
    h: number,
    state?: Record<string, string | number | boolean>,
  ) {
    const { ctx } = this;
    const speed = (state?.speed as number) || 0;
    const direction = state?.direction as string;

    // Motor body (circle)
    ctx.fillStyle = COLORS.componentFill;
    ctx.strokeStyle = COLORS.componentStroke;
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(w / 2, h / 2, w * 0.4, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();

    // Inner circle
    ctx.beginPath();
    ctx.arc(w / 2, h / 2, w * 0.2, 0, Math.PI * 2);
    ctx.stroke();

    // Rotation indicator
    if (speed > 0) {
      const angle = (this.animFrame * speed * 0.1) % (Math.PI * 2);
      ctx.strokeStyle = COLORS.selected;
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(w / 2, h / 2);
      ctx.lineTo(
        w / 2 + Math.cos(angle) * w * 0.35,
        h / 2 + Math.sin(angle) * w * 0.35,
      );
      ctx.stroke();

      // Direction arrow
      const arrowAngle = angle + (direction === "reverse" ? -0.5 : 0.5);
      const arrowR = w * 0.3;
      ctx.beginPath();
      ctx.arc(w / 2, h / 2, arrowR, arrowAngle - 0.3, arrowAngle + 0.3);
      ctx.stroke();
    }

    // M label
    ctx.fillStyle = COLORS.text;
    ctx.font = 'bold 12px "DM Sans", sans-serif';
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText("M", w / 2, h / 2);

    // Shaft
    ctx.strokeStyle = COLORS.componentStroke;
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(w * 0.9, h / 2);
    ctx.lineTo(w, h / 2);
    ctx.stroke();
  }

  private drawBuzzer(
    w: number,
    h: number,
    state?: Record<string, string | number | boolean>,
  ) {
    const { ctx } = this;
    const active = state?.active as boolean;

    // Body
    ctx.fillStyle = active ? "#ffeedd" : COLORS.componentFill;
    ctx.strokeStyle = COLORS.componentStroke;
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.arc(w / 2, h / 2, w * 0.4, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();

    // + symbol
    ctx.fillStyle = COLORS.textSecondary;
    ctx.font = 'bold 11px "DM Sans", sans-serif';
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText("+", w / 2, h / 2);

    // Sound waves when active
    if (active) {
      ctx.strokeStyle = COLORS.selected + "60";
      ctx.lineWidth = 1;
      for (let i = 1; i <= 3; i++) {
        ctx.beginPath();
        ctx.arc(w * 0.8, h / 2, w * 0.15 * i, -Math.PI / 3, Math.PI / 3);
        ctx.stroke();
      }
    }
  }

  private drawPotentiometer(
    w: number,
    h: number,
    props: Record<string, string | number | boolean>,
  ) {
    const { ctx } = this;
    const position = ((props.position as number) || 50) / 100;

    // Body (rectangular)
    ctx.fillStyle = COLORS.componentFill;
    ctx.strokeStyle = COLORS.componentStroke;
    ctx.lineWidth = 1.5;
    this.roundRect(w * 0.15, h * 0.2, w * 0.7, h * 0.6, 4);
    ctx.fill();
    ctx.stroke();

    // Resistance track
    ctx.strokeStyle = COLORS.textFaint;
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(w * 0.25, h * 0.5);
    ctx.lineTo(w * 0.75, h * 0.5);
    ctx.stroke();

    // Wiper arrow
    const wiperX = w * 0.25 + position * w * 0.5;
    ctx.fillStyle = COLORS.pin;
    ctx.beginPath();
    ctx.moveTo(wiperX, h * 0.3);
    ctx.lineTo(wiperX - 4, h * 0.5);
    ctx.lineTo(wiperX + 4, h * 0.5);
    ctx.closePath();
    ctx.fill();

    // Terminal pins
    ctx.strokeStyle = COLORS.componentStroke;
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(0, h * 0.3);
    ctx.lineTo(w * 0.15, h * 0.3);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(0, h * 0.7);
    ctx.lineTo(w * 0.15, h * 0.7);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(w * 0.85, h / 2);
    ctx.lineTo(w, h / 2);
    ctx.stroke();
  }

  private drawServo(
    w: number,
    h: number,
    state?: Record<string, string | number | boolean>,
  ) {
    const { ctx } = this;
    const angle = (state?.angle as number) ?? 90;

    // Servo body
    ctx.fillStyle = "#2a2a3a";
    ctx.strokeStyle = COLORS.componentStroke;
    ctx.lineWidth = 1.5;
    this.roundRect(w * 0.1, h * 0.15, w * 0.8, h * 0.7, 3);
    ctx.fill();
    ctx.stroke();

    // Horn (rotating arm)
    const hornAngle = ((angle - 90) * Math.PI) / 180;
    ctx.strokeStyle = "#888";
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(w / 2, h * 0.3);
    ctx.lineTo(
      w / 2 + Math.cos(hornAngle) * w * 0.3,
      h * 0.3 + Math.sin(hornAngle) * w * 0.3,
    );
    ctx.stroke();

    // Pivot
    ctx.fillStyle = "#aaa";
    ctx.beginPath();
    ctx.arc(w / 2, h * 0.3, 4, 0, Math.PI * 2);
    ctx.fill();

    // Angle label
    ctx.fillStyle = "#fff";
    ctx.font = '9px "DM Sans", sans-serif';
    ctx.textAlign = "center";
    ctx.fillText(`${angle}°`, w / 2, h * 0.7);

    // Wire colors
    ctx.fillStyle = "#c44b2b";
    ctx.fillRect(w * 0.2, h * 0.85, 3, h * 0.15);
    ctx.fillStyle = "#c44b2b";
    ctx.fillRect(w * 0.5, h * 0.85, 3, h * 0.15);
    ctx.fillStyle = "#6b5e4f";
    ctx.fillRect(w * 0.8, h * 0.85, 3, h * 0.15);
  }

  private drawMCU(
    type: ComponentType,
    w: number,
    h: number,
    _props: Record<string, string | number | boolean>,
  ) {
    const { ctx } = this;

    // PCB body
    const bgColor =
      type === "arduino_uno"
        ? "#1a5c8a"
        : type === "esp32"
          ? "#8b2252"
          : "#2a4a6a";
    ctx.fillStyle = bgColor;
    ctx.strokeStyle = COLORS.componentStroke;
    ctx.lineWidth = 1.5;
    this.roundRect(0, 0, w, h, 6);
    ctx.fill();
    ctx.stroke();

    // IC chip
    ctx.fillStyle = "#1a1a2e";
    this.roundRect(w * 0.25, h * 0.3, w * 0.5, h * 0.4, 3);
    ctx.fill();

    // Chip label
    ctx.fillStyle = "#ccc";
    ctx.font = 'bold 9px "DM Sans", sans-serif';
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    const chipLabel =
      type === "arduino_uno"
        ? "ATmega328P"
        : type === "esp32"
          ? "ESP32"
          : "STM32";
    ctx.fillText(chipLabel, w / 2, h * 0.5);

    // Brand
    ctx.fillStyle = "#fff";
    ctx.font = 'bold 11px "DM Sans", sans-serif';
    const brand =
      type === "arduino_uno" ? "Arduino" : type === "esp32" ? "ESP32" : "STM32";
    ctx.fillText(brand, w / 2, h * 0.18);

    // USB connector (Arduino)
    if (type === "arduino_uno") {
      ctx.fillStyle = "#333";
      this.roundRect(w * 0.05, h * 0.02, w * 0.2, h * 0.1, 2);
      ctx.fill();
    }

    // Power LED
    ctx.fillStyle = "#00ff00";
    ctx.beginPath();
    ctx.arc(w * 0.85, h * 0.1, 3, 0, Math.PI * 2);
    ctx.fill();

    // Pin headers
    ctx.strokeStyle = "#444";
    ctx.lineWidth = 0.5;
    for (let i = 0; i < 14; i++) {
      const x = w * 0.08 + (i / 14) * w * 0.84;
      ctx.fillStyle = "#222";
      ctx.fillRect(x - 2, -4, 4, 6);
    }
    for (let i = 0; i < 6; i++) {
      const x = w * 0.2 + (i / 6) * w * 0.6;
      ctx.fillStyle = "#222";
      ctx.fillRect(x - 2, h - 2, 4, 6);
    }
  }

  private drawSevenSegment(
    w: number,
    h: number,
    state?: Record<string, string | number | boolean>,
  ) {
    const { ctx } = this;

    // Background
    ctx.fillStyle = "#1a1a2e";
    ctx.strokeStyle = COLORS.componentStroke;
    ctx.lineWidth = 1.5;
    this.roundRect(0, 0, w, h, 4);
    ctx.fill();
    ctx.stroke();

    // Segment positions (relative to a 50x70 box)
    const segments: Record<
      string,
      { x1: number; y1: number; x2: number; y2: number }
    > = {
      a: { x1: 10, y1: 8, x2: 40, y2: 8 },
      b: { x1: 42, y1: 10, x2: 42, y2: 32 },
      c: { x1: 42, y1: 38, x2: 42, y2: 60 },
      d: { x1: 10, y1: 62, x2: 40, y2: 62 },
      e: { x1: 8, y1: 38, x2: 8, y2: 60 },
      f: { x1: 8, y1: 10, x2: 8, y2: 32 },
      g: { x1: 10, y1: 35, x2: 40, y2: 35 },
    };

    const scaleX = w / 50;
    const scaleY = h / 70;

    for (const [seg, pos] of Object.entries(segments)) {
      const isOn = state?.[seg] as boolean;
      ctx.strokeStyle = isOn ? "#ff4444" : "#331111";
      ctx.lineWidth = 3;
      ctx.lineCap = "round";
      ctx.beginPath();
      ctx.moveTo(pos.x1 * scaleX, pos.y1 * scaleY);
      ctx.lineTo(pos.x2 * scaleX, pos.y2 * scaleY);
      ctx.stroke();
    }

    // Decimal point
    const dpOn = state?.dp as boolean;
    ctx.fillStyle = dpOn ? "#ff4444" : "#331111";
    ctx.beginPath();
    ctx.arc(w * 0.88, h * 0.88, 2.5, 0, Math.PI * 2);
    ctx.fill();
  }

  private drawLCD(
    w: number,
    h: number,
    state?: Record<string, string | number | boolean>,
  ) {
    const { ctx } = this;

    // PCB
    ctx.fillStyle = "#2a6b4a";
    ctx.strokeStyle = COLORS.componentStroke;
    ctx.lineWidth = 1.5;
    this.roundRect(0, 0, w, h, 4);
    ctx.fill();
    ctx.stroke();

    // Screen
    ctx.fillStyle = "#8bac0f";
    ctx.fillRect(w * 0.1, h * 0.1, w * 0.8, h * 0.6);

    // Text on screen
    const text = (state?.text as string) || "";
    ctx.fillStyle = "#1a2a00";
    ctx.font = "10px monospace";
    ctx.textAlign = "left";
    ctx.textBaseline = "top";
    if (text) {
      ctx.fillText(text.substring(0, 16), w * 0.13, h * 0.15);
    } else {
      ctx.fillText("________________", w * 0.13, h * 0.15);
      ctx.fillText("________________", w * 0.13, h * 0.35);
    }

    // Pin header row
    for (let i = 0; i < 16; i++) {
      const x = w * 0.05 + (i / 16) * w * 0.9;
      ctx.fillStyle = "#222";
      ctx.fillRect(x - 1, h - 3, 3, 5);
    }
  }

  private drawUltrasonic(
    w: number,
    h: number,
    _state?: Record<string, string | number | boolean>,
  ) {
    const { ctx } = this;

    // PCB
    ctx.fillStyle = "#3a7ca5";
    ctx.strokeStyle = COLORS.componentStroke;
    ctx.lineWidth = 1.5;
    this.roundRect(0, 0, w, h, 4);
    ctx.fill();
    ctx.stroke();

    // Two transducers
    ctx.fillStyle = "#ccc";
    ctx.beginPath();
    ctx.arc(w * 0.25, h * 0.5, w * 0.15, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();
    ctx.beginPath();
    ctx.arc(w * 0.75, h * 0.5, w * 0.15, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();

    // Labels
    ctx.fillStyle = "#333";
    ctx.font = '8px "DM Sans", sans-serif';
    ctx.textAlign = "center";
    ctx.fillText("T", w * 0.25, h * 0.53);
    ctx.fillText("R", w * 0.75, h * 0.53);

    // Crystal pattern
    for (let i = 0; i < 3; i++) {
      ctx.strokeStyle = "#999";
      ctx.lineWidth = 0.5;
      ctx.beginPath();
      ctx.arc(w * 0.25, h * 0.5, w * 0.08 + i * 3, 0, Math.PI * 2);
      ctx.stroke();
    }
  }

  private drawPhotoresistor(
    w: number,
    h: number,
    _props: Record<string, string | number | boolean>,
  ) {
    const { ctx } = this;

    // Body
    ctx.fillStyle = "#8866aa";
    ctx.strokeStyle = COLORS.componentStroke;
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.arc(w / 2, h / 2, w * 0.35, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();

    // Zigzag symbol
    ctx.strokeStyle = "#fff";
    ctx.lineWidth = 1;
    ctx.beginPath();
    for (let i = 0; i < 4; i++) {
      const y = h * 0.3 + (i / 4) * h * 0.4;
      const x = i % 2 === 0 ? w * 0.35 : w * 0.65;
      ctx.lineTo(x, y);
    }
    ctx.stroke();

    // Light arrows
    ctx.strokeStyle = "#ffdd44";
    ctx.lineWidth = 1;
    for (let i = -1; i <= 1; i++) {
      const startX = w * 0.7 + i * 6;
      ctx.beginPath();
      ctx.moveTo(startX, h * 0.1);
      ctx.lineTo(startX - 3, h * 0.25);
      ctx.stroke();
    }

    // Leads
    ctx.strokeStyle = COLORS.componentStroke;
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(w / 2, h * 0.85);
    ctx.lineTo(w / 2, h);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(w / 2, h * 0.15);
    ctx.lineTo(w / 2, 0);
    ctx.stroke();
  }

  private drawThermistor(
    w: number,
    h: number,
    _props: Record<string, string | number | boolean>,
  ) {
    const { ctx } = this;

    // Body (like resistor but with t)
    ctx.fillStyle = COLORS.componentFill;
    ctx.strokeStyle = COLORS.componentStroke;
    ctx.lineWidth = 1.5;
    this.roundRect(w * 0.2, h * 0.15, w * 0.6, h * 0.7, 3);
    ctx.fill();
    ctx.stroke();

    // t symbol
    ctx.fillStyle = COLORS.text;
    ctx.font = 'bold 14px "DM Sans", sans-serif';
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText("t°", w / 2, h / 2);

    // Leads
    ctx.strokeStyle = COLORS.componentStroke;
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(0, h / 2);
    ctx.lineTo(w * 0.2, h / 2);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(w * 0.8, h / 2);
    ctx.lineTo(w, h / 2);
    ctx.stroke();
  }

  private drawGroundSymbol(w: number, h: number) {
    const { ctx } = this;

    ctx.strokeStyle = COLORS.ground;
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(w / 2, 0);
    ctx.lineTo(w / 2, h * 0.4);
    ctx.stroke();

    // Three horizontal lines
    for (let i = 0; i < 3; i++) {
      const y = h * 0.4 + i * h * 0.18;
      const lineW = w * 0.6 - i * w * 0.15;
      ctx.beginPath();
      ctx.moveTo(w / 2 - lineW / 2, y);
      ctx.lineTo(w / 2 + lineW / 2, y);
      ctx.stroke();
    }
  }

  private drawVCCSymbol(
    w: number,
    h: number,
    props: Record<string, string | number | boolean>,
  ) {
    const { ctx } = this;

    // Arrow up
    ctx.fillStyle = COLORS.power;
    ctx.strokeStyle = COLORS.power;
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(w / 2, h);
    ctx.lineTo(w / 2, h * 0.3);
    ctx.stroke();

    // Arrow head
    ctx.beginPath();
    ctx.moveTo(w / 2, h * 0.2);
    ctx.lineTo(w / 2 - 6, h * 0.45);
    ctx.lineTo(w / 2 + 6, h * 0.45);
    ctx.closePath();
    ctx.fill();

    // VCC label
    ctx.fillStyle = COLORS.text;
    ctx.font = 'bold 10px "DM Sans", sans-serif';
    ctx.textAlign = "center";
    ctx.fillText(`VCC`, w / 2, h * 0.15);
    ctx.font = '8px "DM Sans", sans-serif';
    ctx.fillText(`${props.voltage || 5}V`, w / 2, h * 0.05);
  }

  private drawBreadboard(w: number, h: number) {
    const { ctx } = this;

    // Board body
    ctx.fillStyle = "#f5f0e0";
    ctx.strokeStyle = COLORS.componentStroke;
    ctx.lineWidth = 1.5;
    this.roundRect(0, 0, w, h, 4);
    ctx.fill();
    ctx.stroke();

    // Holes grid
    const rows = 10;
    const cols = 20;
    const holeSpacing = Math.min(w / (cols + 1), h / (rows + 1));
    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        const x = holeSpacing + c * holeSpacing;
        const y = holeSpacing + r * holeSpacing;
        ctx.fillStyle = r === 0 || r === rows - 1 ? "#cc4444" : "#4444cc";
        ctx.beginPath();
        ctx.arc(x, y, 1.5, 0, Math.PI * 2);
        ctx.fill();
      }
    }

    // Center divider
    ctx.strokeStyle = "#ccc";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(w * 0.05, h / 2);
    ctx.lineTo(w * 0.95, h / 2);
    ctx.stroke();
  }

  private drawGenericBox(w: number, h: number, type: string) {
    const { ctx } = this;
    ctx.fillStyle = COLORS.componentFill;
    ctx.strokeStyle = COLORS.componentStroke;
    ctx.lineWidth = 1.5;
    this.roundRect(0, 0, w, h, 4);
    ctx.fill();
    ctx.stroke();
    ctx.fillStyle = COLORS.textSecondary;
    ctx.font = '10px "DM Sans", sans-serif';
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(type, w / 2, h / 2);
  }

  // ─── STM32 Blue Pill ───

  private drawBluePill(
    w: number,
    h: number,
    _props: Record<string, string | number | boolean>,
  ) {
    const { ctx } = this;

    // PCB body (blue)
    ctx.fillStyle = "#1a3a6a";
    ctx.strokeStyle = "#0d1f3c";
    ctx.lineWidth = 1.5;
    this.roundRect(0, 0, w, h, 4);
    ctx.fill();
    ctx.stroke();

    // STM32 chip (black rectangle in center)
    ctx.fillStyle = "#1a1a1a";
    this.roundRect(w * 0.2, h * 0.25, w * 0.6, h * 0.5, 2);
    ctx.fill();

    // Chip label
    ctx.fillStyle = "#ccc";
    ctx.font = `bold ${Math.max(7, w * 0.06)}px "DM Sans", sans-serif`;
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText("STM32", w / 2, h * 0.44);
    ctx.fillText("F103C8T6", w / 2, h * 0.56);

    // Brand
    ctx.fillStyle = "#fff";
    ctx.font = `bold ${Math.max(8, w * 0.07)}px "DM Sans", sans-serif`;
    ctx.fillText("Blue Pill", w / 2, h * 0.12);

    // 32.768kHz crystal
    ctx.fillStyle = "#888";
    ctx.fillRect(w * 0.72, h * 0.35, w * 0.12, h * 0.06);

    // Power LED
    ctx.fillStyle = "#00ff00";
    ctx.beginPath();
    ctx.arc(w * 0.15, h * 0.12, 2, 0, Math.PI * 2);
    ctx.fill();

    // Reset button
    ctx.fillStyle = "#666";
    this.roundRect(w * 0.78, h * 0.82, w * 0.12, h * 0.08, 1);
    ctx.fill();
    ctx.fillStyle = "#aaa";
    ctx.font = '5px "DM Sans", sans-serif';
    ctx.fillText("RST", w * 0.84, h * 0.86);

    // USB micro connector
    ctx.fillStyle = "#888";
    this.roundRect(w * 0.38, 0, w * 0.24, h * 0.05, 1);
    ctx.fill();
  }

  // ─── OLED SSD1306 ───

  private drawOLED(
    w: number,
    h: number,
    state?: Record<string, string | number | boolean>,
  ) {
    const { ctx } = this;

    // PCB
    ctx.fillStyle = "#1a2744";
    ctx.strokeStyle = COLORS.componentStroke;
    ctx.lineWidth = 1.5;
    this.roundRect(0, 0, w, h, 4);
    ctx.fill();
    ctx.stroke();

    // OLED screen
    ctx.fillStyle = "#0a0a0a";
    ctx.fillRect(w * 0.08, h * 0.08, w * 0.84, h * 0.55);

    // Screen content
    const text = (state?.text as string) || "";
    ctx.fillStyle = "#00ccff";
    ctx.font = "8px monospace";
    ctx.textAlign = "left";
    ctx.textBaseline = "top";
    if (text) {
      const lines = text.split("\n");
      lines.slice(0, 4).forEach((line, i) => {
        ctx.fillText(line.substring(0, 16), w * 0.12, h * 0.12 + i * 12);
      });
    } else {
      ctx.fillStyle = "#003344";
      ctx.fillText("OLED SSD1306", w * 0.12, h * 0.15);
      ctx.fillText("128x64 I2C", w * 0.12, h * 0.3);
    }

    // I2C label
    ctx.fillStyle = "#aaa";
    ctx.font = '7px "DM Sans", sans-serif';
    ctx.textAlign = "center";
    ctx.fillText("I2C", w / 2, h * 0.72);

    // Pin labels
    ctx.font = '6px "DM Sans", sans-serif';
    ctx.fillStyle = "#888";
    ctx.fillText("VCC", w * 0.15, h * 0.9);
    ctx.fillText("GND", w * 0.38, h * 0.9);
    ctx.fillText("SCL", w * 0.62, h * 0.9);
    ctx.fillText("SDA", w * 0.85, h * 0.9);
  }

  // ─── MPU6050 ───

  private drawMPU6050(
    w: number,
    h: number,
    state?: Record<string, string | number | boolean>,
  ) {
    const { ctx } = this;

    // Module PCB (purple/red)
    ctx.fillStyle = "#6a1b5e";
    ctx.strokeStyle = "#3d0e36";
    ctx.lineWidth = 1.5;
    this.roundRect(0, 0, w, h, 4);
    ctx.fill();
    ctx.stroke();

    // MPU6050 chip
    ctx.fillStyle = "#1a1a1a";
    this.roundRect(w * 0.2, h * 0.2, w * 0.6, h * 0.4, 2);
    ctx.fill();

    // Chip label
    ctx.fillStyle = "#ccc";
    ctx.font = `bold ${Math.max(7, w * 0.06)}px "DM Sans", sans-serif`;
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText("MPU6050", w / 2, h * 0.35);

    // Decoupling capacitor
    ctx.fillStyle = "#444";
    ctx.fillRect(w * 0.75, h * 0.25, w * 0.1, h * 0.08);

    // Accelerometer data display
    const ax = (state?.ax as number) ?? 0;
    const ay = (state?.ay as number) ?? 0;
    const az = (state?.az as number) ?? 0;
    ctx.fillStyle = "#aaa";
    ctx.font = "7px monospace";
    ctx.textAlign = "left";
    ctx.fillText(`ax:${ax}`, w * 0.08, h * 0.72);
    ctx.fillText(`ay:${ay}`, w * 0.08, h * 0.82);
    ctx.fillText(`az:${az}`, w * 0.08, h * 0.92);

    // Pin labels
    ctx.font = '6px "DM Sans", sans-serif';
    ctx.textAlign = "center";
    ctx.fillStyle = "#888";
    ctx.fillText("VCC", w * 0.15, h * 0.08);
    ctx.fillText("GND", w * 0.38, h * 0.08);
    ctx.fillText("SCL", w * 0.62, h * 0.08);
    ctx.fillText("SDA", w * 0.85, h * 0.08);
  }

  // ─── ST-Link V2 ───

  private drawSTLink(w: number, h: number) {
    const { ctx } = this;

    // Metal body
    ctx.fillStyle = "#555";
    ctx.strokeStyle = "#333";
    ctx.lineWidth = 1.5;
    this.roundRect(0, 0, w, h, 4);
    ctx.fill();
    ctx.stroke();

    // USB connector
    ctx.fillStyle = "#aaa";
    this.roundRect(w * 0.3, 0, w * 0.4, h * 0.12, 2);
    ctx.fill();

    // SWD header
    ctx.fillStyle = "#222";
    this.roundRect(w * 0.15, h * 0.75, w * 0.7, h * 0.15, 2);
    ctx.fill();

    // Pin labels
    ctx.fillStyle = "#ccc";
    ctx.font = '6px "DM Sans", sans-serif';
    ctx.textAlign = "center";
    const labels = ["SWDIO", "GND", "SWCLK", "3V3"];
    labels.forEach((label, i) => {
      ctx.fillText(label, w * 0.25 + i * w * 0.18, h * 0.92);
    });

    // Label
    ctx.fillStyle = "#fff";
    ctx.font = `bold ${Math.max(8, w * 0.07)}px "DM Sans", sans-serif`;
    ctx.textAlign = "center";
    ctx.fillText("ST-Link", w / 2, h * 0.35);
    ctx.fillText("V2", w / 2, h * 0.5);
  }

  // ─── USB-TTL ───

  private drawUSBTTL(w: number, h: number) {
    const { ctx } = this;

    // Body
    ctx.fillStyle = "#2a5a2a";
    ctx.strokeStyle = "#1a3a1a";
    ctx.lineWidth = 1.5;
    this.roundRect(0, 0, w, h, 4);
    ctx.fill();
    ctx.stroke();

    // USB connector
    ctx.fillStyle = "#aaa";
    this.roundRect(w * 0.3, 0, w * 0.4, h * 0.12, 2);
    ctx.fill();

    // Pin header
    ctx.fillStyle = "#222";
    this.roundRect(w * 0.1, h * 0.75, w * 0.8, h * 0.15, 2);
    ctx.fill();

    // Pin labels
    ctx.fillStyle = "#ccc";
    ctx.font = '6px "DM Sans", sans-serif';
    ctx.textAlign = "center";
    ctx.fillText("TXD", w * 0.2, h * 0.92);
    ctx.fillText("RXD", w * 0.4, h * 0.92);
    ctx.fillText("GND", w * 0.6, h * 0.92);
    ctx.fillText("3V3", w * 0.8, h * 0.92);

    // Label
    ctx.fillStyle = "#fff";
    ctx.font = `bold ${Math.max(8, w * 0.07)}px "DM Sans", sans-serif`;
    ctx.fillText("USB-TTL", w / 2, h * 0.4);

    // Activity LED
    ctx.fillStyle = "#00ff00";
    ctx.beginPath();
    ctx.arc(w * 0.85, h * 0.15, 2, 0, Math.PI * 2);
    ctx.fill();
  }

  // ─── IR Sensor / Photoresistor Module ───

  private drawIRSensor(
    w: number,
    h: number,
    state?: Record<string, string | number | boolean>,
  ) {
    const { ctx } = this;

    // PCB
    ctx.fillStyle = "#2a4a2a";
    ctx.strokeStyle = "#1a3a1a";
    ctx.lineWidth = 1.5;
    this.roundRect(0, 0, w, h, 4);
    ctx.fill();
    ctx.stroke();

    // IR LED (transparent dome)
    ctx.fillStyle = "#4a2a4a";
    ctx.beginPath();
    ctx.arc(w * 0.3, h * 0.4, w * 0.18, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();

    // Phototransistor
    ctx.fillStyle = "#2a2a4a";
    ctx.beginPath();
    ctx.arc(w * 0.7, h * 0.4, w * 0.15, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();

    // Detection indicator
    const detected = state?.detected as boolean;
    if (detected) {
      ctx.strokeStyle = "#ff4444";
      ctx.lineWidth = 1;
      for (let i = 1; i <= 3; i++) {
        ctx.beginPath();
        ctx.arc(w * 0.3, h * 0.4, w * 0.2 + i * 4, -Math.PI / 3, Math.PI / 3);
        ctx.stroke();
      }
    }

    // Comparator IC
    ctx.fillStyle = "#1a1a1a";
    this.roundRect(w * 0.25, h * 0.6, w * 0.5, h * 0.2, 2);
    ctx.fill();

    // Pin labels
    ctx.fillStyle = "#aaa";
    ctx.font = '6px "DM Sans", sans-serif';
    ctx.textAlign = "center";
    ctx.fillText("VCC", w * 0.2, h * 0.92);
    ctx.fillText("GND", w * 0.5, h * 0.92);
    ctx.fillText("OUT", w * 0.8, h * 0.92);

    // Sensitivity pot
    ctx.fillStyle = "#444";
    ctx.beginPath();
    ctx.arc(w * 0.85, h * 0.7, 4, 0, Math.PI * 2);
    ctx.fill();
  }

  // ─── Rotary Encoder ───

  private drawRotaryEncoder(
    w: number,
    h: number,
    state?: Record<string, string | number | boolean>,
  ) {
    const { ctx } = this;

    // Body
    ctx.fillStyle = "#888";
    ctx.strokeStyle = "#555";
    ctx.lineWidth = 1.5;
    this.roundRect(w * 0.15, h * 0.1, w * 0.7, h * 0.6, 3);
    ctx.fill();
    ctx.stroke();

    // Shaft
    ctx.fillStyle = "#aaa";
    ctx.beginPath();
    ctx.arc(w / 2, h * 0.35, w * 0.15, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();

    // Rotation indicator
    const position = (state?.position as number) ?? 0;
    const angle = ((position % 360) * Math.PI) / 180;
    ctx.strokeStyle = "#c44b2b";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(w / 2, h * 0.35);
    ctx.lineTo(
      w / 2 + Math.cos(angle) * w * 0.12,
      h * 0.35 + Math.sin(angle) * w * 0.12,
    );
    ctx.stroke();

    // Detent marks
    for (let i = 0; i < 20; i++) {
      const a = (i / 20) * Math.PI * 2;
      ctx.strokeStyle = "#666";
      ctx.lineWidth = 0.5;
      ctx.beginPath();
      ctx.moveTo(
        w / 2 + Math.cos(a) * w * 0.18,
        h * 0.35 + Math.sin(a) * w * 0.18,
      );
      ctx.lineTo(
        w / 2 + Math.cos(a) * w * 0.22,
        h * 0.35 + Math.sin(a) * w * 0.22,
      );
      ctx.stroke();
    }

    // Pin labels
    ctx.fillStyle = "#333";
    ctx.font = '6px "DM Sans", sans-serif';
    ctx.textAlign = "center";
    ctx.fillText("CLK", w * 0.2, h * 0.85);
    ctx.fillText("DT", w * 0.4, h * 0.85);
    ctx.fillText("SW", w * 0.6, h * 0.85);
    ctx.fillText("VCC", w * 0.8, h * 0.85);
    ctx.fillText("GND", w / 2, h * 0.95);
  }

  // ─── W25Q64 Flash ───

  private drawW25Q64(w: number, h: number) {
    const { ctx } = this;

    // Module PCB
    ctx.fillStyle = "#1a3a5a";
    ctx.strokeStyle = "#0d1f3c";
    ctx.lineWidth = 1.5;
    this.roundRect(0, 0, w, h, 4);
    ctx.fill();
    ctx.stroke();

    // Flash chip (SOIC-8)
    ctx.fillStyle = "#1a1a1a";
    this.roundRect(w * 0.15, h * 0.2, w * 0.7, h * 0.4, 2);
    ctx.fill();

    // Pin 1 dot
    ctx.fillStyle = "#ccc";
    ctx.beginPath();
    ctx.arc(w * 0.2, h * 0.28, 2, 0, Math.PI * 2);
    ctx.fill();

    // Chip label
    ctx.fillStyle = "#ccc";
    ctx.font = `bold ${Math.max(7, w * 0.06)}px "DM Sans", sans-serif`;
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText("W25Q64", w / 2, h * 0.35);
    ctx.fillText("8MB Flash", w / 2, h * 0.48);

    // Pin labels
    ctx.fillStyle = "#aaa";
    ctx.font = '6px "DM Sans", sans-serif';
    ctx.textAlign = "center";
    ctx.fillText("CS", w * 0.15, h * 0.85);
    ctx.fillText("DO", w * 0.33, h * 0.85);
    ctx.fillText("GND", w * 0.5, h * 0.85);
    ctx.fillText("DI", w * 0.67, h * 0.85);
    ctx.fillText("CLK", w * 0.85, h * 0.85);
    ctx.fillText("VCC", w / 2, h * 0.1);
  }

  // ─── Pin Drawing ───

  private drawPin(
    x: number,
    y: number,
    type: string,
    isHovered: boolean,
    isConnected: boolean,
    isHigh?: boolean,
  ) {
    const { ctx, transform } = this;
    const radius = isHovered ? 5 : 4;

    let color = COLORS.pin;
    if (isHigh) color = COLORS.pinConnected;
    else if (isConnected) color = COLORS.pinConnected;
    else if (isHovered) color = COLORS.pinHover;

    // Pin circle
    ctx.fillStyle = isHovered ? color + "40" : "transparent";
    ctx.beginPath();
    ctx.arc(x, y, radius + 2, 0, Math.PI * 2);
    ctx.fill();

    ctx.fillStyle = color;
    ctx.strokeStyle = COLORS.componentStroke;
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.arc(x, y, radius, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();

    // Type indicator
    if (type === "power") {
      ctx.fillStyle = "#fff";
      ctx.font = `bold ${6 / transform.scale}px "DM Sans", sans-serif`;
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText("+", x, y);
    } else if (type === "ground") {
      ctx.fillStyle = "#fff";
      ctx.font = `bold ${6 / transform.scale}px "DM Sans", sans-serif`;
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText("−", x, y);
    }
  }

  // ─── Helpers ───

  getPinWorldPos(
    comp: CircuitComponent,
    pin: PinDef,
  ): { x: number; y: number } {
    const def = getComponentDef(comp.type);
    const w = def.width;
    const h = def.height;
    const local = this.getPinLocalPos(pin, w, h);

    // Apply rotation
    const cx = w / 2;
    const cy = h / 2;
    const dx = local.x - cx;
    const dy = local.y - cy;
    const rad = (comp.rotation * Math.PI) / 180;
    const rx = dx * Math.cos(rad) - dy * Math.sin(rad) + cx;
    const ry = dx * Math.sin(rad) + dy * Math.cos(rad) + cy;

    return { x: comp.x + rx, y: comp.y + ry };
  }

  getPinLocalPos(pin: PinDef, w: number, h: number): { x: number; y: number } {
    switch (pin.side) {
      case "top":
        return { x: pin.offset * w, y: 0 };
      case "bottom":
        return { x: pin.offset * w, y: h };
      case "left":
        return { x: 0, y: pin.offset * h };
      case "right":
        return { x: w, y: pin.offset * h };
    }
  }

  private roundRect(x: number, y: number, w: number, h: number, r: number) {
    const { ctx } = this;
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.lineTo(x + w - r, y);
    ctx.quadraticCurveTo(x + w, y, x + w, y + r);
    ctx.lineTo(x + w, y + h - r);
    ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
    ctx.lineTo(x + r, y + h);
    ctx.quadraticCurveTo(x, y + h, x, y + h - r);
    ctx.lineTo(x, y + r);
    ctx.quadraticCurveTo(x, y, x + r, y);
    ctx.closePath();
  }
}

// ─── Resistor Color Bands ───

const bandColors: Record<string, string> = {
  "0": "#000000",
  "1": "#8B4513",
  "2": "#ff0000",
  "3": "#ff8c00",
  "4": "#ffff00",
  "5": "#00aa00",
  "6": "#0000ff",
  "7": "#8b008b",
  "8": "#808080",
  "9": "#ffffff",
};

function resistanceToBands(value: number): string[] {
  const str = value.toString();
  if (str.length < 2) return ["#000000", "#000000", "#000000"];

  const d1 = str[0];
  const d2 = str[1];
  const multiplier = str.length - 2;

  return [
    bandColors[d1] || "#000",
    bandColors[d2] || "#000",
    bandColors[multiplier.toString()] || "#000",
    "#c4a000", // tolerance (gold = 5%)
  ];
}
