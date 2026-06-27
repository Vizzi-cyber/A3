// ─── Circuit Component Types ───

export type ComponentType =
  | "led"
  | "resistor"
  | "capacitor"
  | "battery"
  | "button"
  | "switch"
  | "motor"
  | "buzzer"
  | "potentiometer"
  | "photoresistor"
  | "thermistor"
  | "servo"
  | "seven_segment"
  | "lcd"
  | "ultrasonic"
  | "arduino_uno"
  | "esp32"
  | "stm32"
  | "stm32_bluepill"
  | "oled_ssd1306"
  | "mpu6050"
  | "stlink"
  | "usb_ttl"
  | "ir_sensor"
  | "rotary_encoder"
  | "w25q64"
  | "breadboard"
  | "ground"
  | "vcc";

export type PinType = "digital" | "analog" | "power" | "ground" | "pwm" | "io";

export interface PinDef {
  id: string;
  label: string;
  type: PinType;
  side: "top" | "bottom" | "left" | "right";
  offset: number; // 0-1 position along the side
}

export interface ComponentDef {
  type: ComponentType;
  label: string;
  category:
    | "passive"
    | "active"
    | "mcu"
    | "power"
    | "sensor"
    | "output"
    | "connector";
  width: number;
  height: number;
  pins: PinDef[];
  defaultProps: Record<string, string | number | boolean>;
}

// ─── Circuit Instance Types ───

export interface CircuitComponent {
  id: string;
  type: ComponentType;
  x: number;
  y: number;
  rotation: 0 | 90 | 180 | 270;
  props: Record<string, string | number | boolean>;
  label: string;
}

export interface WireEndpoint {
  componentId: string;
  pinId: string;
}

export interface Wire {
  id: string;
  from: WireEndpoint;
  to: WireEndpoint;
  waypoints: { x: number; y: number }[]; // for routing
}

// ─── Simulation Types ───

export interface PinState {
  voltage: number; // 0-5V
  value: number; // digital (0 or 1, but using number for flexibility)
  analog: number; // 0-1023 (ADC)
  isHigh: boolean;
}

export interface SimulationState {
  running: boolean;
  time: number; // ms
  pinStates: Record<string, PinState>; // "componentId:pinId" -> state
  componentStates: Record<string, Record<string, string | number | boolean>>;
  errors: string[];
  logs: string[];
}

// ─── Code Execution Types ───

export interface ArduinoProgram {
  setup: string;
  loop: string;
  fullCode: string;
  pinMappings: PinMapping[];
}

export interface PinMapping {
  arduinoPin: string; // e.g. "D13", "A0"
  componentId: string;
  componentPinId: string;
  mode: "input" | "output" | "input_pullup" | "pwm";
}

// ─── Canvas Types ───

export interface CanvasTransform {
  x: number;
  y: number;
  scale: number;
}

export interface DragState {
  type: "component" | "wire" | "pan" | "selection" | null;
  componentId?: string;
  fromPin?: WireEndpoint;
  offsetX?: number;
  offsetY?: number;
  startX?: number;
  startY?: number;
}

export interface SelectionState {
  componentIds: Set<string>;
  wireIds: Set<string>;
}

// ─── Predefined Circuit Templates ───

export interface CircuitTemplate {
  id: string;
  name: string;
  description: string;
  difficulty: "beginner" | "intermediate" | "advanced";
  components: CircuitComponent[];
  wires: Wire[];
  code: string;
  thumbnail?: string;
}
