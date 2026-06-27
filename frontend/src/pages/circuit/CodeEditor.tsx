import { useState, useRef, useCallback, useEffect } from "react";
import { Play, Square, Terminal, Code2, Link2, Trash2 } from "lucide-react";
import type { PinMapping, CircuitComponent } from "./types";
import { getComponentDef } from "./componentLibrary";

interface Props {
  code: string;
  onCodeChange: (code: string) => void;
  pinMappings: PinMapping[];
  onPinMappingsChange: (mappings: PinMapping[]) => void;
  components: CircuitComponent[];
  isRunning: boolean;
  onRun: () => void;
  onStop: () => void;
  logs: string[];
  errors: string[];
}

// STM32 C keyword highlighting
const keywords = [
  // C keywords
  "void",
  "int",
  "uint8_t",
  "uint16_t",
  "uint32_t",
  "int8_t",
  "int16_t",
  "int32_t",
  "float",
  "double",
  "char",
  "const",
  "static",
  "volatile",
  "struct",
  "typedef",
  "if",
  "else",
  "for",
  "while",
  "return",
  "sizeof",
  "NULL",
  // STM32 Standard Peripheral Library
  "GPIO_InitTypeDef",
  "TIM_TimeBaseInitTypeDef",
  "TIM_OCInitTypeDef",
  "USART_InitTypeDef",
  "EXTI_InitTypeDef",
  "NVIC_InitTypeDef",
  "GPIO_Mode_Out_PP",
  "GPIO_Mode_IPU",
  "GPIO_Mode_AF_PP",
  "GPIO_Mode_IN_FLOATING",
  "GPIO_Mode_IPD",
  "GPIO_Mode_AIN",
  "GPIO_Mode_Out_OD",
  "GPIO_Speed_50MHz",
  "GPIO_Speed_2MHz",
  "GPIO_Speed_10MHz",
  "TIM_CounterMode_Up",
  "TIM_OCMode_PWM1",
  "TIM_OCMode_PWM2",
  "TIM_OutputState_Enable",
  "TIM_OCPolarity_High",
  "TIM_CKD_DIV1",
  "TIM_IT_Update",
  "USART_Mode_Tx",
  "USART_Mode_Rx",
  "USART_WordLength_8b",
  "USART_StopBits_1",
  "USART_Parity_No",
  "USART_HardwareFlowControl_None",
  "BitAction",
  "Bit_SET",
  "Bit_RESET",
  "ENABLE",
  "DISABLE",
  "RESET",
  // HAL functions
  "HAL_GPIO_WritePin",
  "HAL_GPIO_ReadPin",
  "HAL_GPIO_TogglePin",
  "HAL_Delay",
  "HAL_Init",
  "HAL_TIM_PWM_Start",
  "__HAL_TIM_SET_COMPARE",
  "__HAL_RCC_GPIOA_CLK_ENABLE",
  // Standard Peripheral functions
  "GPIO_Init",
  "GPIO_SetBits",
  "GPIO_ResetBits",
  "GPIO_WriteBit",
  "GPIO_ReadInputDataBit",
  "GPIO_ReadOutputDataBit",
  "RCC_APB2PeriphClockCmd",
  "RCC_APB1PeriphClockCmd",
  "TIM_TimeBaseInit",
  "TIM_OC1Init",
  "TIM_OC2Init",
  "TIM_SetCompare1",
  "TIM_SetCompare2",
  "TIM_Cmd",
  "TIM_PWM_Init",
  "TIM_PWM_ConfigChannel",
  "USART_Init",
  "USART_SendData",
  "USART_ReceiveData",
  "USART_GetFlagStatus",
  "USART_Cmd",
  "USART_ITConfig",
  "EXTI_Init",
  "EXTI_ClearITPendingBit",
  "EXTI_GetITStatus",
  "GPIO_EXTILineConfig",
  "NVIC_SetPriority",
  "NVIC_EnableIRQ",
  "SystemClock_Config",
  "MX_GPIO_Init",
  // GPIO Ports
  "GPIOA",
  "GPIOB",
  "GPIOC",
  "GPIO_Pin_0",
  "GPIO_Pin_1",
  "GPIO_Pin_2",
  "GPIO_Pin_3",
  "GPIO_Pin_4",
  "GPIO_Pin_5",
  "GPIO_Pin_6",
  "GPIO_Pin_7",
  "GPIO_Pin_8",
  "GPIO_Pin_9",
  "GPIO_Pin_10",
  "GPIO_Pin_11",
  "GPIO_Pin_12",
  "GPIO_Pin_13",
  "GPIO_Pin_14",
  "GPIO_Pin_15",
  // RCC
  "RCC_APB2Periph_GPIOA",
  "RCC_APB2Periph_GPIOB",
  "RCC_APB2Periph_GPIOC",
  "RCC_APB2Periph_AFIO",
  "RCC_APB2Periph_USART1",
  "RCC_APB1Periph_TIM2",
  "RCC_APB1Periph_TIM3",
  "RCC_APB1Periph_TIM4",
  "RCC_APB1Periph_USART2",
  "RCC_APB1Periph_USART3",
  // TIM
  "TIM2",
  "TIM3",
  "TIM4",
  "TIM_CHANNEL_1",
  "TIM_CHANNEL_2",
  "TIM_CHANNEL_3",
  "TIM_CHANNEL_4",
  // USART
  "USART1",
  "USART2",
  "USART3",
  "USART_FLAG_TXE",
  "USART_FLAG_RXNE",
  // EXTI
  "EXTI_Line0",
  "EXTI_Line1",
  "EXTI_Line2",
  "EXTI_Mode_Interrupt",
  "EXTI_Trigger_Falling",
  "EXTI_Trigger_Rising",
  "GPIO_PortSourceGPIOA",
  "GPIO_PinSource0",
  "GPIO_PinSource1",
  "EXTI0_IRQn",
  "EXTI1_IRQn",
  "TIM2_IRQn",
];

const builtins = [
  // STM32 pin names
  "PA0",
  "PA1",
  "PA2",
  "PA3",
  "PA4",
  "PA5",
  "PA6",
  "PA7",
  "PA8",
  "PA9",
  "PA10",
  "PA11",
  "PA12",
  "PA13",
  "PA14",
  "PA15",
  "PB0",
  "PB1",
  "PB3",
  "PB4",
  "PB5",
  "PB6",
  "PB7",
  "PB8",
  "PB9",
  "PB10",
  "PB11",
  "PB12",
  "PB13",
  "PB14",
  "PB15",
  "PC13",
  "PC14",
  "PC15",
  // Common values
  "GPIO_PIN_SET",
  "GPIO_PIN_RESET",
  "fputc",
  "main",
];

export default function CodeEditor({
  code,
  onCodeChange,
  pinMappings,
  onPinMappingsChange,
  components,
  isRunning,
  onRun,
  onStop,
  logs,
  errors,
}: Props) {
  const [activeTab, setActiveTab] = useState<"code" | "pins" | "serial">(
    "code",
  );
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [highlightedCode, setHighlightedCode] = useState("");

  const highlightSyntax = useCallback((src: string) => {
    // Simple syntax highlighting via regex replacement
    let html = src
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");

    // Comments
    html = html.replace(/(\/\/.*$)/gm, '<span style="color:#a39480">$1</span>');
    html = html.replace(
      /(\/\*[\s\S]*?\*\/)/g,
      '<span style="color:#a39480">$1</span>',
    );

    // Strings
    html = html.replace(
      /("(?:[^"\\]|\\.)*")/g,
      '<span style="color:#1a6b5a">$1</span>',
    );

    // Numbers
    html = html.replace(
      /\b(\d+\.?\d*)\b/g,
      '<span style="color:#e8a44a">$1</span>',
    );

    // Keywords
    for (const kw of keywords) {
      html = html.replace(
        new RegExp(`\\b(${kw})\\b`, "g"),
        '<span style="color:#c44b2b;font-weight:600">$1</span>',
      );
    }

    // Builtins (pin names)
    for (const bi of builtins) {
      html = html.replace(
        new RegExp(`\\b(${bi})\\b`, "g"),
        '<span style="color:#1a6b5a;font-weight:600">$1</span>',
      );
    }

    return html;
  }, []);

  useEffect(() => {
    setHighlightedCode(highlightSyntax(code));
  }, [code, highlightSyntax]);

  const handleTextareaChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    onCodeChange(e.target.value);
  };

  const handleScroll = () => {
    const textarea = textareaRef.current;
    const highlight = textarea?.parentElement?.querySelector(
      ".code-highlight",
    ) as HTMLElement;
    if (textarea && highlight) {
      highlight.scrollTop = textarea.scrollTop;
      highlight.scrollLeft = textarea.scrollLeft;
    }
  };

  // Pin mapping management
  const addMapping = () => {
    const mcu = components.find((c) => {
      const def = getComponentDef(c.type);
      return def.category === "mcu";
    });
    if (!mcu) return;

    const newMapping: PinMapping = {
      arduinoPin: "PA0",
      componentId: "",
      componentPinId: "",
      mode: "output",
    };
    onPinMappingsChange([...pinMappings, newMapping]);
  };

  const updateMapping = (
    index: number,
    field: keyof PinMapping,
    value: string,
  ) => {
    const updated = [...pinMappings];
    updated[index] = { ...updated[index], [field]: value };
    onPinMappingsChange(updated);
  };

  const removeMapping = (index: number) => {
    onPinMappingsChange(pinMappings.filter((_, i) => i !== index));
  };

  const nonMcuComponents = components.filter((c) => {
    const def = getComponentDef(c.type);
    return def.category !== "mcu" && def.pins.length > 0;
  });

  return (
    <div className="flex flex-col h-full">
      {/* Tabs */}
      <div className="flex items-center gap-1 px-3 py-2 border-b border-border">
        <button
          onClick={() => setActiveTab("code")}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[12px] font-medium transition-colors cursor-pointer ${
            activeTab === "code"
              ? "bg-ink text-surface"
              : "text-ink-secondary hover:bg-bg"
          }`}
        >
          <Code2 size={12} />
          代码
        </button>
        <button
          onClick={() => setActiveTab("pins")}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[12px] font-medium transition-colors cursor-pointer ${
            activeTab === "pins"
              ? "bg-ink text-surface"
              : "text-ink-secondary hover:bg-bg"
          }`}
        >
          <Link2 size={12} />
          引脚映射
          {pinMappings.length > 0 && (
            <span className="w-4 h-4 rounded-full bg-accent text-white text-[9px] flex items-center justify-center">
              {pinMappings.length}
            </span>
          )}
        </button>
        <button
          onClick={() => setActiveTab("serial")}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[12px] font-medium transition-colors cursor-pointer ${
            activeTab === "serial"
              ? "bg-ink text-surface"
              : "text-ink-secondary hover:bg-bg"
          }`}
        >
          <Terminal size={12} />
          串口监视器
          {logs.length > 0 && (
            <span className="w-4 h-4 rounded-full bg-teal text-white text-[9px] flex items-center justify-center">
              {logs.length}
            </span>
          )}
        </button>

        <div className="flex-1" />

        {/* Run/Stop buttons */}
        {isRunning ? (
          <button
            onClick={onStop}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-red-500 text-white text-[12px] font-semibold hover:bg-red-600 transition-colors cursor-pointer"
          >
            <Square size={12} />
            停止
          </button>
        ) : (
          <button
            onClick={onRun}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-teal text-white text-[12px] font-semibold hover:bg-teal/90 transition-colors cursor-pointer"
          >
            <Play size={12} />
            运行
          </button>
        )}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-hidden">
        {activeTab === "code" && (
          <div className="relative h-full">
            {/* Syntax-highlighted overlay */}
            <div
              className="code-highlight absolute inset-0 p-4 font-mono text-[12px] leading-[1.8] whitespace-pre-wrap break-words pointer-events-none overflow-auto text-transparent"
              dangerouslySetInnerHTML={{ __html: highlightedCode }}
              style={{
                caretColor: "transparent",
              }}
            />
            {/* Actual textarea */}
            <textarea
              ref={textareaRef}
              value={code}
              onChange={handleTextareaChange}
              onScroll={handleScroll}
              spellCheck={false}
              className="w-full h-full p-4 font-mono text-[12px] leading-[1.8] bg-ink text-white/90 resize-none outline-none border-0 whitespace-pre-wrap break-words relative z-10"
              style={{ caretColor: "#fff" }}
            />
          </div>
        )}

        {activeTab === "pins" && (
          <div className="p-4 overflow-y-auto h-full">
            <div className="flex items-center justify-between mb-4">
              <h4 className="text-[13px] font-semibold text-ink">
                引脚映射配置
              </h4>
              <button
                onClick={addMapping}
                disabled={
                  !components.some(
                    (c) => getComponentDef(c.type).category === "mcu",
                  )
                }
                className="px-3 py-1.5 rounded-lg bg-accent text-white text-[11px] font-semibold hover:bg-accent-dark transition-colors cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed"
              >
                + 添加映射
              </button>
            </div>

            {pinMappings.length === 0 ? (
              <div className="text-center py-8">
                <Link2 size={24} className="mx-auto mb-2 text-ink-faint" />
                <p className="text-[12px] text-ink-faint">暂无引脚映射</p>
                <p className="text-[11px] text-ink-faint mt-1">
                  添加映射来连接 Arduino 引脚和电路元件
                </p>
              </div>
            ) : (
              <div className="flex flex-col gap-3">
                {pinMappings.map((mapping, index) => (
                  <div
                    key={index}
                    className="p-3 bg-bg rounded-xl border border-border"
                  >
                    <div className="flex items-center gap-2 mb-2">
                      {/* Arduino pin selector */}
                      <select
                        value={mapping.arduinoPin}
                        onChange={(e) =>
                          updateMapping(index, "arduinoPin", e.target.value)
                        }
                        className="flex-1 px-2 py-1.5 bg-surface border border-border rounded-lg text-[12px] outline-none"
                      >
                        <optgroup label="STM32">
                          {[
                            "PA0",
                            "PA1",
                            "PA2",
                            "PA3",
                            "PA4",
                            "PA5",
                            "PA6",
                            "PA7",
                            "PA8",
                            "PA9",
                            "PA10",
                            "PA11",
                            "PA12",
                            "PA13",
                            "PA14",
                            "PA15",
                            "PB0",
                            "PB1",
                            "PB3",
                            "PB4",
                            "PB5",
                            "PB6",
                            "PB7",
                            "PB8",
                            "PB9",
                            "PB10",
                            "PB11",
                            "PB12",
                            "PB13",
                            "PB14",
                            "PB15",
                            "PC13",
                            "PC14",
                            "PC15",
                          ].map((pin) => (
                            <option key={pin} value={pin}>
                              {pin}
                            </option>
                          ))}
                        </optgroup>
                        <optgroup label="Arduino">
                          {[
                            "D0",
                            "D1",
                            "D2",
                            "D3",
                            "D4",
                            "D5",
                            "D6",
                            "D7",
                            "D8",
                            "D9",
                            "D10",
                            "D11",
                            "D12",
                            "D13",
                            "A0",
                            "A1",
                            "A2",
                            "A3",
                            "A4",
                            "A5",
                          ].map((pin) => (
                            <option key={pin} value={pin}>
                              {pin}
                            </option>
                          ))}
                        </optgroup>
                        <optgroup label="Timer">
                          {[
                            "TIM2_CH1",
                            "TIM2_CH2",
                            "TIM2_CH3",
                            "TIM2_CH4",
                            "TIM3_CH1",
                            "TIM3_CH2",
                            "TIM3_CH3",
                            "TIM3_CH4",
                          ].map((pin) => (
                            <option key={pin} value={pin}>
                              {pin}
                            </option>
                          ))}
                        </optgroup>
                      </select>

                      <span className="text-[11px] text-ink-faint">→</span>

                      {/* Component selector */}
                      <select
                        value={mapping.componentId}
                        onChange={(e) =>
                          updateMapping(index, "componentId", e.target.value)
                        }
                        className="flex-1 px-2 py-1.5 bg-surface border border-border rounded-lg text-[12px] outline-none"
                      >
                        <option value="">选择元件...</option>
                        {nonMcuComponents.map((comp) => (
                          <option key={comp.id} value={comp.id}>
                            {comp.label || getComponentDef(comp.type).label}
                          </option>
                        ))}
                      </select>

                      {/* Pin selector */}
                      <select
                        value={mapping.componentPinId}
                        onChange={(e) =>
                          updateMapping(index, "componentPinId", e.target.value)
                        }
                        className="flex-1 px-2 py-1.5 bg-surface border border-border rounded-lg text-[12px] outline-none"
                      >
                        <option value="">选择引脚...</option>
                        {mapping.componentId &&
                          getComponentDef(
                            components.find((c) => c.id === mapping.componentId)
                              ?.type || "led",
                          ).pins.map((pin) => (
                            <option key={pin.id} value={pin.id}>
                              {pin.label}
                            </option>
                          ))}
                      </select>

                      <button
                        onClick={() => removeMapping(index)}
                        className="w-7 h-7 rounded-lg flex items-center justify-center text-ink-faint hover:text-red-500 hover:bg-red-50 transition-colors cursor-pointer"
                      >
                        <Trash2 size={12} />
                      </button>
                    </div>

                    {/* Mode selector */}
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] text-ink-faint">模式:</span>
                      {(
                        ["output", "input", "input_pullup", "pwm"] as const
                      ).map((mode) => (
                        <button
                          key={mode}
                          onClick={() => updateMapping(index, "mode", mode)}
                          className={`px-2 py-0.5 rounded text-[10px] font-medium transition-colors cursor-pointer ${
                            mapping.mode === mode
                              ? "bg-accent text-white"
                              : "bg-surface text-ink-secondary hover:bg-border-subtle"
                          }`}
                        >
                          {mode.toUpperCase()}
                        </button>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Quick mapping hint */}
            {components.some(
              (c) => getComponentDef(c.type).category === "mcu",
            ) &&
              nonMcuComponents.length > 0 && (
                <div className="mt-4 p-3 bg-accent-light/50 rounded-xl border border-accent/10">
                  <p className="text-[11px] text-ink-secondary leading-relaxed">
                    <strong>提示:</strong> 将 STM32 的 GPIO 引脚连接到
                    LED、电机等输出元件的信号引脚。 TIM2_CH1 (PA0), TIM2_CH2
                    (PA1), TIM2_CH3 (PA2), TIM2_CH4 (PA3) 支持 PWM 输出。
                  </p>
                </div>
              )}
          </div>
        )}

        {activeTab === "serial" && (
          <div className="h-full flex flex-col">
            <div className="flex-1 overflow-y-auto p-4 font-mono text-[11px]">
              {logs.length === 0 && errors.length === 0 ? (
                <div className="text-center py-8">
                  <Terminal size={24} className="mx-auto mb-2 text-ink-faint" />
                  <p className="text-[12px] text-ink-faint">
                    串口输出将显示在这里
                  </p>
                  <p className="text-[11px] text-ink-faint mt-1">
                    使用 printf() 通过 USART 输出信息
                  </p>
                </div>
              ) : (
                <>
                  {errors.map((err, i) => (
                    <div key={`err-${i}`} className="text-red-500 mb-1">
                      [ERROR] {err}
                    </div>
                  ))}
                  {logs.map((log, i) => (
                    <div key={`log-${i}`} className="text-teal mb-1">
                      {log}
                    </div>
                  ))}
                </>
              )}
            </div>
            {logs.length > 0 && (
              <div className="px-4 py-2 border-t border-border">
                <button
                  onClick={() => onStop()}
                  className="text-[10px] text-ink-faint hover:text-ink transition-colors cursor-pointer"
                >
                  清空
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
