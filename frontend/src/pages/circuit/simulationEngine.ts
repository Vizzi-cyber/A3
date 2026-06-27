import type {
  CircuitComponent,
  Wire,
  SimulationState,
  PinState,
  PinMapping,
} from "./types";
import { getComponentDef } from "./componentLibrary";

// ─── Graph adjacency ───

interface Connection {
  fromComponent: string;
  fromPin: string;
  toComponent: string;
  toPin: string;
  wireId: string;
}

function buildAdjacency(
  components: CircuitComponent[],
  wires: Wire[],
): Map<string, Connection[]> {
  const adj = new Map<string, Connection[]>();
  for (const comp of components) {
    const def = getComponentDef(comp.type);
    for (const pin of def.pins) {
      adj.set(`${comp.id}:${pin.id}`, []);
    }
  }
  for (const wire of wires) {
    const keyA = `${wire.from.componentId}:${wire.from.pinId}`;
    const keyB = `${wire.to.componentId}:${wire.to.pinId}`;
    const conn: Connection = {
      fromComponent: wire.from.componentId,
      fromPin: wire.from.pinId,
      toComponent: wire.to.componentId,
      toPin: wire.to.pinId,
      wireId: wire.id,
    };
    adj.get(keyA)?.push(conn);
    adj
      .get(keyB)
      ?.push({
        ...conn,
        fromComponent: conn.toComponent,
        fromPin: conn.toPin,
        toComponent: conn.fromComponent,
        toPin: conn.fromPin,
      });
  }
  return adj;
}

// ─── Code Parser ───

interface ParsedProgram {
  pinModeMap: Map<string, "input" | "output" | "input_pullup" | "pwm">;
  digitalWriteMap: Map<string, 0 | 1>;
  analogWriteMap: Map<string, number>;
  analogReadTargets: Set<string>;
  digitalReadTargets: Set<string>;
  delayMs: number;
  serialPrints: string[];
  loopCount: number;
  gpioWriteMap: Map<string, 0 | 1>; // HAL_GPIO_WritePin: "PA0" -> 0/1
  gpioReadTargets: Set<string>; // HAL_GPIO_ReadPin targets
  gpioToggleTargets: Set<string>; // HAL_GPIO_TogglePin targets
  timPwmMap: Map<string, number>; // TIM_SetCompare / __HAL_TIM_SET_COMPARE: "TIM2_CH1" -> value
  printfOutputs: string[]; // printf outputs
  isSTM32: boolean; // whether this is STM32 HAL code
  // Ordered sequence of GPIO write operations for step-by-step execution
  gpioSequence: Array<{ pin: string; value: 0 | 1 }>;
  timSequence: Array<{ channel: string; value: number }>;
  printfSequence: string[];
}

function parseCode(code: string): ParsedProgram {
  const result: ParsedProgram = {
    pinModeMap: new Map(),
    digitalWriteMap: new Map(),
    analogWriteMap: new Map(),
    analogReadTargets: new Set(),
    digitalReadTargets: new Set(),
    delayMs: 100,
    serialPrints: [],
    loopCount: 0,
    gpioWriteMap: new Map(),
    gpioReadTargets: new Set(),
    gpioToggleTargets: new Set(),
    timPwmMap: new Map(),
    printfOutputs: [],
    isSTM32: false,
    gpioSequence: [],
    timSequence: [],
    printfSequence: [],
  };

  // Detect STM32 HAL code
  const isSTM32 = /HAL_|GPIO[A-C]|stm32|TIM\d|USART\d/i.test(code);
  result.isSTM32 = isSTM32;

  let match: RegExpExecArray | null;

  if (isSTM32) {
    // ─── STM32 HAL Parsing ───

    // HAL_GPIO_WritePin(GPIOx, GPIO_PIN_x, GPIO_PIN_SET/RESET)
    const gpioWriteRegex =
      /HAL_GPIO_WritePin\s*\(\s*GPIO([A-C])\s*,\s*GPIO_PIN_(\d+)\s*,\s*(GPIO_PIN_SET|GPIO_PIN_RESET|SET|RESET)\s*\)/gi;
    while ((match = gpioWriteRegex.exec(code)) !== null) {
      const port = match[1].toUpperCase();
      const pin = match[2];
      const val = match[3].toUpperCase().includes("SET") ? 1 : 0;
      result.gpioWriteMap.set(`P${port}${pin}`, val);
      result.gpioSequence.push({ pin: `P${port}${pin}`, value: val as 0 | 1 });
    }

    // HAL_GPIO_TogglePin(GPIOx, GPIO_PIN_x)
    const gpioToggleRegex =
      /HAL_GPIO_TogglePin\s*\(\s*GPIO([A-C])\s*,\s*GPIO_PIN_(\d+)\s*\)/gi;
    while ((match = gpioToggleRegex.exec(code)) !== null) {
      const port = match[1].toUpperCase();
      const pin = match[2];
      result.gpioToggleTargets.add(`P${port}${pin}`);
    }

    // HAL_GPIO_ReadPin(GPIOx, GPIO_PIN_x)
    const gpioReadRegex =
      /HAL_GPIO_ReadPin\s*\(\s*GPIO([A-C])\s*,\s*GPIO_PIN_(\d+)\s*\)/gi;
    while ((match = gpioReadRegex.exec(code)) !== null) {
      const port = match[1].toUpperCase();
      const pin = match[2];
      result.gpioReadTargets.add(`P${port}${pin}`);
    }

    // GPIO_ResetBits / GPIO_SetBits (Standard Peripheral Library)
    const setBitsRegex =
      /GPIO_SetBits\s*\(\s*GPIO([A-C])\s*,\s*GPIO_Pin_(\d+)\s*\)/gi;
    while ((match = setBitsRegex.exec(code)) !== null) {
      const pin = `P${match[1].toUpperCase()}${match[2]}`;
      result.gpioWriteMap.set(pin, 1);
      result.gpioSequence.push({ pin, value: 1 });
    }
    const resetBitsRegex =
      /GPIO_ResetBits\s*\(\s*GPIO([A-C])\s*,\s*GPIO_Pin_(\d+)\s*\)/gi;
    while ((match = resetBitsRegex.exec(code)) !== null) {
      const pin = `P${match[1].toUpperCase()}${match[2]}`;
      result.gpioWriteMap.set(pin, 0);
      result.gpioSequence.push({ pin, value: 0 });
    }

    // GPIO_WriteBit
    const writeBitRegex =
      /GPIO_WriteBit\s*\(\s*GPIO([A-C])\s*,\s*GPIO_Pin_(\d+)\s*,\s*(Bit_SET|Bit_RESET)\s*\)/gi;
    while ((match = writeBitRegex.exec(code)) !== null) {
      result.gpioWriteMap.set(
        `P${match[1].toUpperCase()}${match[2]}`,
        match[3] === "Bit_SET" ? 1 : 0,
      );
    }

    // GPIO_ReadInputDataBit
    const readInputRegex =
      /GPIO_ReadInputDataBit\s*\(\s*GPIO([A-C])\s*,\s*GPIO_Pin_(\d+)\s*\)/gi;
    while ((match = readInputRegex.exec(code)) !== null) {
      result.gpioReadTargets.add(`P${match[1].toUpperCase()}${match[2]}`);
    }

    // TIM_SetCompare1/2/3/4
    const timCompareRegex =
      /TIM_SetCompare(\d)\s*\(\s*TIM(\d)\s*,\s*(\d+)\s*\)/gi;
    while ((match = timCompareRegex.exec(code)) !== null) {
      const ch = match[1];
      const tim = match[2];
      const channel = `TIM${tim}_CH${ch}`;
      result.timPwmMap.set(channel, parseInt(match[3]));
      result.timSequence.push({ channel, value: parseInt(match[3]) });
    }

    // __HAL_TIM_SET_COMPARE
    const halTimRegex =
      /__HAL_TIM_SET_COMPARE\s*\(\s*&htim(\d)\s*,\s*TIM_CHANNEL_(\d)\s*,\s*(\d+)\s*\)/gi;
    while ((match = halTimRegex.exec(code)) !== null) {
      const channel = `TIM${match[1]}_CH${match[2]}`;
      result.timPwmMap.set(channel, parseInt(match[3]));
      result.timSequence.push({ channel, value: parseInt(match[3]) });
    }

    // HAL_Delay
    const halDelayRegex = /HAL_Delay\s*\(\s*(\d+)\s*\)/gi;
    while ((match = halDelayRegex.exec(code)) !== null) {
      result.delayMs = parseInt(match[1]);
    }

    // Delay_ms (Standard Peripheral Library)
    const delayMsRegex = /Delay_ms\s*\(\s*(\d+)\s*\)/gi;
    while ((match = delayMsRegex.exec(code)) !== null) {
      result.delayMs = parseInt(match[1]);
    }

    // printf
    const printfRegex = /printf\s*\(\s*["'`]([^"'`]*)["'`]/gi;
    while ((match = printfRegex.exec(code)) !== null) {
      result.printfOutputs.push(match[1]);
      result.printfSequence.push(match[1]);
    }

    // USART_SendData (single char)
    const usartRegex = /USART_SendData\s*\(\s*USART(\d)/gi;
    while ((match = usartRegex.exec(code)) !== null) {
      // Just detect USART usage
    }
  } else {
    // ─── Arduino Parsing (legacy) ───

    // Parse pinMode calls
    const pinModeRegex =
      /pinMode\s*\(\s*["']?(\w+)["']?\s*,\s*(INPUT_PULLUP|INPUT|OUTPUT)\s*\)/gi;
    while ((match = pinModeRegex.exec(code)) !== null) {
      const pin = match[1].toUpperCase();
      const mode = match[2].toUpperCase();
      if (mode === "OUTPUT") result.pinModeMap.set(pin, "output");
      else if (mode === "INPUT_PULLUP")
        result.pinModeMap.set(pin, "input_pullup");
      else result.pinModeMap.set(pin, "input");
    }

    // Parse digitalWrite calls
    const dwRegex =
      /digitalWrite\s*\(\s*["']?(\w+)["']?\s*,\s*(HIGH|LOW|1|0)\s*\)/gi;
    while ((match = dwRegex.exec(code)) !== null) {
      const pin = match[1].toUpperCase();
      const val = match[2].toUpperCase() === "HIGH" || match[2] === "1" ? 1 : 0;
      result.digitalWriteMap.set(pin, val);
      result.gpioSequence.push({ pin, value: val as 0 | 1 });
    }

    // Parse analogWrite (PWM) calls
    const awRegex = /analogWrite\s*\(\s*["']?(\w+)["']?\s*,\s*(\d+)\s*\)/gi;
    while ((match = awRegex.exec(code)) !== null) {
      const pin = match[1].toUpperCase();
      result.analogWriteMap.set(pin, parseInt(match[2]));
    }

    // Parse analogRead targets
    const arRegex = /analogRead\s*\(\s*["']?(\w+)["']?\s*\)/gi;
    while ((match = arRegex.exec(code)) !== null) {
      result.analogReadTargets.add(match[1].toUpperCase());
    }

    // Parse digitalRead targets
    const drRegex = /digitalRead\s*\(\s*["']?(\w+)["']?\s*\)/gi;
    while ((match = drRegex.exec(code)) !== null) {
      result.digitalReadTargets.add(match[1].toUpperCase());
    }

    // Parse delay
    const delayRegex = /delay\s*\(\s*(\d+)\s*\)/gi;
    while ((match = delayRegex.exec(code)) !== null) {
      result.delayMs = parseInt(match[1]);
    }

    // Parse Serial.print
    const serialRegex =
      /Serial\.print(?:ln)?\s*\(\s*["'`]([^"'`]*)["'`]\s*\)/gi;
    while ((match = serialRegex.exec(code)) !== null) {
      result.serialPrints.push(match[1]);
    }
  }

  return result;
}

// ─── Simulation Engine ───

export class CircuitSimulator {
  private components: CircuitComponent[] = [];
  private pinMappings: PinMapping[] = [];
  private code: string = "";

  // Internal state
  private pinStates = new Map<string, PinState>();
  private componentStates = new Map<
    string,
    Record<string, string | number | boolean>
  >();
  private adjacency = new Map<string, Connection[]>();
  private logs: string[] = [];
  private errors: string[] = [];
  private time = 0;
  private running = false;
  private loopTimer: ReturnType<typeof setInterval> | null = null;
  private parsedProgram: ParsedProgram | null = null;
  private onChange: ((state: SimulationState) => void) | null = null;
  private sequenceIndex = 0; // tracks current position in gpioSequence

  // Initialize / update circuit
  setCircuit(components: CircuitComponent[], wires: Wire[]) {
    this.components = components;
    this.adjacency = buildAdjacency(components, wires);
  }

  setCode(code: string, mappings: PinMapping[]) {
    this.code = code;
    this.pinMappings = mappings;
  }

  setOnChange(cb: (state: SimulationState) => void) {
    this.onChange = cb;
  }

  // Get pin state
  getPinState(componentId: string, pinId: string): PinState {
    const key = `${componentId}:${pinId}`;
    return (
      this.pinStates.get(key) || {
        voltage: 0,
        value: 0,
        analog: 0,
        isHigh: false,
      }
    );
  }

  // Set pin state directly (for interactive components like buttons)
  setPinStateDirect(
    componentId: string,
    pinId: string,
    state: Partial<PinState>,
  ) {
    const key = `${componentId}:${pinId}`;
    const existing = this.getPinState(componentId, pinId);
    this.pinStates.set(key, { ...existing, ...state });
  }

  // Get full simulation state
  getState(): SimulationState {
    const pinStatesObj: Record<string, PinState> = {};
    this.pinStates.forEach((v, k) => {
      pinStatesObj[k] = v;
    });
    const compStatesObj: Record<
      string,
      Record<string, string | number | boolean>
    > = {};
    this.componentStates.forEach((v, k) => {
      compStatesObj[k] = v;
    });
    return {
      running: this.running,
      time: this.time,
      pinStates: pinStatesObj,
      componentStates: compStatesObj,
      errors: [...this.errors],
      logs: [...this.logs],
    };
  }

  // ─── Simulation Loop ───

  start() {
    if (this.running) return;
    this.running = true;
    this.time = 0;
    this.errors = [];
    this.logs = [];
    this.sequenceIndex = 0;
    this.parsedProgram = parseCode(this.code);

    // Initial setup pass
    this.runSetup();
    this.propagatePower();
    this.evaluateComponents();

    // Loop — execute one GPIO step per tick for visible state changes
    const tickInterval = Math.max(this.parsedProgram.delayMs / 10, 16);
    this.loopTimer = setInterval(() => {
      this.runStep();
      this.propagatePower();
      this.evaluateComponents();
      this.time += this.parsedProgram!.delayMs;
      this.notifyChange();
    }, tickInterval);
  }

  stop() {
    this.running = false;
    if (this.loopTimer) {
      clearInterval(this.loopTimer);
      this.loopTimer = null;
    }
    // Reset all outputs to off
    this.pinStates.clear();
    this.componentStates.clear();
    this.sequenceIndex = 0;
    this.notifyChange();
  }

  // ─── Setup Phase ───

  private runSetup() {
    if (!this.parsedProgram) return;
    // Apply pinMode settings via mappings
    for (const mapping of this.pinMappings) {
      const arduinoPin = mapping.arduinoPin.toUpperCase();
      const mode = this.parsedProgram.pinModeMap.get(arduinoPin);
      if (mode) {
        mapping.mode = mode;
      }
    }
  }

  // ─── Loop Phase (step-by-step execution) ───

  private runStep() {
    if (!this.parsedProgram) return;

    const prog = this.parsedProgram;

    if (prog.isSTM32) {
      // Execute one GPIO operation from the sequence per tick
      if (prog.gpioSequence.length > 0) {
        const step =
          prog.gpioSequence[this.sequenceIndex % prog.gpioSequence.length];
        const mapping = this.pinMappings.find((m) => {
          const mappedPin = m.arduinoPin.toUpperCase();
          return (
            mappedPin === step.pin ||
            mappedPin === `P${step.pin.charAt(1)}${step.pin.slice(2)}`
          );
        });
        if (mapping) {
          // Set the MCU pin state (for power propagation)
          const mcuComp = this.components.find((c) => {
            const def = getComponentDef(c.type);
            return def.category === "mcu";
          });
          if (mcuComp) {
            const mcuKey = `${mcuComp.id}:${mapping.arduinoPin}`;
            this.pinStates.set(mcuKey, {
              voltage: step.value ? 3.3 : 0,
              value: step.value,
              analog: step.value ? 4095 : 0,
              isHigh: !!step.value,
            });
          }
          // Also set the target component pin state directly
          const targetKey = `${mapping.componentId}:${mapping.componentPinId}`;
          this.pinStates.set(targetKey, {
            voltage: step.value ? 3.3 : 0,
            value: step.value,
            analog: step.value ? 4095 : 0,
            isHigh: !!step.value,
          });
        }
      }

      // Execute one TIM PWM step from the sequence
      if (prog.timSequence.length > 0) {
        const step =
          prog.timSequence[this.sequenceIndex % prog.timSequence.length];
        const mapping = this.pinMappings.find(
          (m) => m.arduinoPin.toUpperCase() === step.channel,
        );
        if (mapping) {
          const mcuComp = this.components.find((c) => {
            const def = getComponentDef(c.type);
            return def.category === "mcu";
          });
          if (mcuComp) {
            const mcuKey = `${mcuComp.id}:${mapping.arduinoPin}`;
            const maxVal = 999;
            const voltage = (step.value / maxVal) * 3.3;
            this.pinStates.set(mcuKey, {
              voltage,
              value: step.value > maxVal / 2 ? 1 : 0,
              analog: Math.round((step.value / maxVal) * 4095),
              isHigh: step.value > 0,
            });
          }
          const targetKey = `${mapping.componentId}:${mapping.componentPinId}`;
          const maxVal = 999;
          const voltage = (step.value / maxVal) * 3.3;
          this.pinStates.set(targetKey, {
            voltage,
            value: step.value > maxVal / 2 ? 1 : 0,
            analog: Math.round((step.value / maxVal) * 4095),
            isHigh: step.value > 0,
          });
        }
      }

      // Execute one printf from the sequence
      if (prog.printfSequence.length > 0) {
        const msg =
          prog.printfSequence[this.sequenceIndex % prog.printfSequence.length];
        const expanded = msg
          .replace(/\\r\\n$/g, "")
          .replace(/%d/g, "0")
          .replace(/%s/g, "");
        this.logs.push(`[T=${this.time}ms] USART: ${expanded}`);
        if (this.logs.length > 100) this.logs.shift();
      }

      // Apply toggle pins
      for (const pin of prog.gpioToggleTargets) {
        const mapping = this.pinMappings.find((m) => {
          const mappedPin = m.arduinoPin.toUpperCase();
          return (
            mappedPin === pin ||
            mappedPin === `P${pin.charAt(1)}${pin.slice(2)}`
          );
        });
        if (mapping) {
          const mcuComp = this.components.find((c) => {
            const def = getComponentDef(c.type);
            return def.category === "mcu";
          });
          const current = this.pinStates.get(
            `${mcuComp?.id}:${mapping.arduinoPin}`,
          );
          const newIsHigh = current ? !current.isHigh : true;
          const newState = {
            voltage: newIsHigh ? 3.3 : 0,
            value: newIsHigh ? 1 : 0,
            analog: newIsHigh ? 4095 : 0,
            isHigh: newIsHigh,
          };
          if (mcuComp) {
            this.pinStates.set(`${mcuComp.id}:${mapping.arduinoPin}`, newState);
          }
          this.pinStates.set(
            `${mapping.componentId}:${mapping.componentPinId}`,
            newState,
          );
        }
      }
    } else {
      // Arduino mode — step through digital/analog writes
      const dwEntries = Array.from(prog.digitalWriteMap.entries());
      if (dwEntries.length > 0) {
        const [pin, value] = dwEntries[this.sequenceIndex % dwEntries.length];
        const mapping = this.pinMappings.find(
          (m) => m.arduinoPin.toUpperCase() === pin,
        );
        if (mapping) {
          const mcuComp = this.components.find((c) => {
            const def = getComponentDef(c.type);
            return def.category === "mcu";
          });
          const newState = {
            voltage: value ? 5 : 0,
            value,
            analog: value ? 1023 : 0,
            isHigh: !!value,
          };
          if (mcuComp) {
            this.pinStates.set(`${mcuComp.id}:${mapping.arduinoPin}`, newState);
          }
          this.pinStates.set(
            `${mapping.componentId}:${mapping.componentPinId}`,
            newState,
          );
        }
      }

      const awEntries = Array.from(prog.analogWriteMap.entries());
      if (awEntries.length > 0) {
        const [pin, value] = awEntries[this.sequenceIndex % awEntries.length];
        const mapping = this.pinMappings.find(
          (m) => m.arduinoPin.toUpperCase() === pin,
        );
        if (mapping) {
          const voltage = (value / 255) * 5;
          const mcuComp = this.components.find((c) => {
            const def = getComponentDef(c.type);
            return def.category === "mcu";
          });
          const newState = {
            voltage,
            value: value > 127 ? 1 : 0,
            analog: Math.round((value / 255) * 1023),
            isHigh: value > 0,
          };
          if (mcuComp) {
            this.pinStates.set(`${mcuComp.id}:${mapping.arduinoPin}`, newState);
          }
          this.pinStates.set(
            `${mapping.componentId}:${mapping.componentPinId}`,
            newState,
          );
        }
      }

      // Serial prints
      if (prog.serialPrints.length > 0) {
        const msg =
          prog.serialPrints[this.sequenceIndex % prog.serialPrints.length];
        const expanded = msg.replace(
          /\$\{(\w+)\}/g,
          (_, varName) => `[${varName}]`,
        );
        this.logs.push(`[T=${this.time}ms] ${expanded}`);
        if (this.logs.length > 100) this.logs.shift();
      }
    }

    this.sequenceIndex++;
  }

  // ─── Power Propagation (BFS) ───

  private propagatePower() {
    // Find all power sources
    const powerSources: string[] = [];
    const groundSources: string[] = [];

    for (const comp of this.components) {
      const def = getComponentDef(comp.type);
      if (comp.type === "battery" || comp.type === "vcc") {
        for (const pin of def.pins) {
          if (pin.type === "power") {
            const key = `${comp.id}:${pin.id}`;
            const voltage =
              comp.type === "battery"
                ? (comp.props.voltage as number) || 9
                : (comp.props.voltage as number) || 5;
            this.pinStates.set(key, {
              voltage,
              value: 1,
              analog: Math.round((voltage / 5) * 1023),
              isHigh: true,
            });
            powerSources.push(key);
          }
          if (pin.type === "ground") {
            const key = `${comp.id}:${pin.id}`;
            this.pinStates.set(key, {
              voltage: 0,
              value: 0,
              analog: 0,
              isHigh: false,
            });
            groundSources.push(key);
          }
        }
      }
      if (comp.type === "ground") {
        const key = `${comp.id}:gnd`;
        this.pinStates.set(key, {
          voltage: 0,
          value: 0,
          analog: 0,
          isHigh: false,
        });
        groundSources.push(key);
      }
    }

    // Treat MCU pins set by code as virtual power/ground sources
    const mcuComp = this.components.find((c) => {
      const def = getComponentDef(c.type);
      return def.category === "mcu";
    });
    if (mcuComp) {
      for (const mapping of this.pinMappings) {
        const mcuPinKey = `${mcuComp.id}:${mapping.arduinoPin}`;
        const mcuState = this.pinStates.get(mcuPinKey);
        if (mcuState) {
          if (mcuState.isHigh) {
            powerSources.push(mcuPinKey);
          } else {
            groundSources.push(mcuPinKey);
          }
        }
      }
    }

    // BFS propagation from power sources
    const visited = new Set<string>();
    const queue: string[] = [...powerSources];

    while (queue.length > 0) {
      const current = queue.shift()!;
      if (visited.has(current)) continue;
      visited.add(current);

      const currentState = this.pinStates.get(current);
      if (!currentState) continue;

      const connections = this.adjacency.get(current) || [];
      for (const conn of connections) {
        const neighborKey = `${conn.toComponent}:${conn.toPin}`;
        if (visited.has(neighborKey)) continue;

        // Check if neighbor is ground — creates a path
        const neighborComp = this.components.find(
          (c) => c.id === conn.toComponent,
        );
        if (!neighborComp) continue;
        const neighborDef = getComponentDef(neighborComp.type);
        const neighborPinDef = neighborDef.pins.find(
          (p) => p.id === conn.toPin,
        );
        if (!neighborPinDef) continue;

        if (
          neighborPinDef.type === "ground" ||
          groundSources.includes(neighborKey)
        ) {
          // Ground sinks voltage
          this.pinStates.set(neighborKey, {
            voltage: 0,
            value: 0,
            analog: 0,
            isHigh: false,
          });
        } else {
          // Pass voltage through (simplified — no resistance calculation yet)
          this.pinStates.set(neighborKey, { ...currentState });
        }
        queue.push(neighborKey);
      }
    }
  }

  // ─── Component Evaluation ───

  private evaluateComponents() {
    for (const comp of this.components) {
      switch (comp.type) {
        case "led":
          this.evaluateLED(comp);
          break;
        case "motor":
          this.evaluateMotor(comp);
          break;
        case "buzzer":
          this.evaluateBuzzer(comp);
          break;
        case "servo":
          this.evaluateServo(comp);
          break;
        case "button":
          this.evaluateButton(comp);
          break;
        case "switch":
          this.evaluateSwitch(comp);
          break;
        case "seven_segment":
          this.evaluateSevenSegment(comp);
          break;
        case "lcd":
          this.evaluateLCD(comp);
          break;
        case "oled_ssd1306":
          this.evaluateOLED(comp);
          break;
        case "mpu6050":
          this.evaluateMPU6050(comp);
          break;
        case "ir_sensor":
          this.evaluateIRSensor(comp);
          break;
        case "rotary_encoder":
          this.evaluateRotaryEncoder(comp);
          break;
      }
    }
  }

  private evaluateLED(comp: CircuitComponent) {
    const anodeState = this.getPinState(comp.id, "anode");
    const maxV = this.parsedProgram?.isSTM32 ? 3.3 : 5;
    const isOn = anodeState.isHigh;
    const brightness = isOn ? Math.min(anodeState.voltage / maxV, 1) : 0;
    this.componentStates.set(comp.id, {
      on: isOn,
      brightness,
      color: (comp.props.color as string) || "#ff3333",
    });
  }

  private evaluateMotor(comp: CircuitComponent) {
    const posState = this.getPinState(comp.id, "positive");
    const negState = this.getPinState(comp.id, "negative");
    const voltageDiff = posState.voltage - negState.voltage;
    const speed = Math.min(Math.abs(voltageDiff) / 5, 1);
    const direction =
      voltageDiff > 0 ? "forward" : voltageDiff < 0 ? "reverse" : "stopped";
    this.componentStates.set(comp.id, {
      speed,
      direction,
      rpm: Math.round(speed * ((comp.props.maxRPM as number) || 300)),
    });
  }

  private evaluateBuzzer(comp: CircuitComponent) {
    const posState = this.getPinState(comp.id, "positive");
    const active = posState.isHigh;
    this.componentStates.set(comp.id, {
      active,
      frequency: active ? (comp.props.frequency as number) || 1000 : 0,
    });
  }

  private evaluateServo(comp: CircuitComponent) {
    const signalState = this.getPinState(comp.id, "signal");
    // PWM to angle: 0-255 maps to 0-180 degrees
    const angle = Math.round((signalState.analog / 1023) * 180);
    this.componentStates.set(comp.id, {
      angle,
      moving: signalState.isHigh,
    });
  }

  private evaluateButton(comp: CircuitComponent) {
    const pressed = comp.props.pressed as boolean;
    if (pressed) {
      // Button connects its two pins
      const pin1State = this.getPinState(comp.id, "pin1");
      this.setPinStateDirect(comp.id, "pin2", pin1State);
    }
    this.componentStates.set(comp.id, { pressed });
  }

  private evaluateSwitch(comp: CircuitComponent) {
    const on = comp.props.on as boolean;
    if (on) {
      const pin1State = this.getPinState(comp.id, "pin1");
      this.setPinStateDirect(comp.id, "pin2", pin1State);
    }
    this.componentStates.set(comp.id, { on });
  }

  private evaluateSevenSegment(comp: CircuitComponent) {
    const segments: Record<string, boolean> = {};
    for (const seg of ["a", "b", "c", "d", "e", "f", "g", "dp"]) {
      const state = this.getPinState(comp.id, seg);
      segments[seg] = state.isHigh;
    }
    // Decode digit
    const digit = decodeSevenSegment(segments);
    this.componentStates.set(comp.id, { ...segments, digit });
  }

  private evaluateLCD(comp: CircuitComponent) {
    const enState = this.getPinState(comp.id, "en");
    const rsState = this.getPinState(comp.id, "rs");
    const d4 = this.getPinState(comp.id, "d4");
    const d5 = this.getPinState(comp.id, "d5");
    const d6 = this.getPinState(comp.id, "d6");
    const d7 = this.getPinState(comp.id, "d7");
    const data = (d7.value << 3) | (d6.value << 2) | (d5.value << 1) | d4.value;
    this.componentStates.set(comp.id, {
      enabled: enState.isHigh,
      registerSelect: rsState.isHigh ? "data" : "command",
      data,
      text: (comp.props.text as string) || "",
    });
  }

  private evaluateOLED(comp: CircuitComponent) {
    const sclState = this.getPinState(comp.id, "SCL");
    const sdaState = this.getPinState(comp.id, "SDA");
    const vccState = this.getPinState(comp.id, "VCC");
    const powered = vccState.isHigh;
    // I2C activity detection
    const i2cActive = sclState.isHigh || sdaState.isHigh;
    this.componentStates.set(comp.id, {
      powered,
      i2cActive,
      text: (comp.props.text as string) || "OLED Ready",
      address: (comp.props.address as string) || "0x3C",
    });
  }

  private evaluateMPU6050(comp: CircuitComponent) {
    const vccState = this.getPinState(comp.id, "VCC");
    const powered = vccState.isHigh;
    this.componentStates.set(comp.id, {
      powered,
      ax: (comp.props.ax as number) || 0,
      ay: (comp.props.ay as number) || 0,
      az: (comp.props.az as number) || 0,
      address: (comp.props.address as string) || "0x68",
    });
  }

  private evaluateIRSensor(comp: CircuitComponent) {
    const outState = this.getPinState(comp.id, "OUT");
    const vccState = this.getPinState(comp.id, "VCC");
    const powered = vccState.isHigh;
    const detected = powered && !outState.isHigh; // Active low when object detected
    this.componentStates.set(comp.id, {
      powered,
      detected,
    });
  }

  private evaluateRotaryEncoder(comp: CircuitComponent) {
    const clkState = this.getPinState(comp.id, "CLK");
    const dtState = this.getPinState(comp.id, "DT");
    const swState = this.getPinState(comp.id, "SW");
    const position = (comp.props.position as number) || 0;
    this.componentStates.set(comp.id, {
      position,
      clkHigh: clkState.isHigh,
      dtHigh: dtState.isHigh,
      pressed: !swState.isHigh, // Active low button
    });
  }

  private notifyChange() {
    if (this.onChange) {
      this.onChange(this.getState());
    }
  }
}

// ─── Seven Segment Decoder ───

function decodeSevenSegment(segs: Record<string, boolean>): number {
  const patterns: Record<number, string> = {
    0: "abcdef",
    1: "bc",
    2: "abdeg",
    3: "abcdg",
    4: "bcfg",
    5: "acdfg",
    6: "acdefg",
    7: "abc",
    8: "abcdefg",
    9: "abcdfg",
  };
  const active = Object.entries(segs)
    .filter(([k, v]) => k !== "dp" && v)
    .map(([k]) => k)
    .sort()
    .join("");

  for (const [digit, pattern] of Object.entries(patterns)) {
    if (pattern.split("").sort().join("") === active) {
      return parseInt(digit);
    }
  }
  return -1;
}

// Singleton instance
export const simulator = new CircuitSimulator();
