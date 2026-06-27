import { useState, useEffect } from "react";
import { Settings, RotateCw, Trash2, Copy } from "lucide-react";
import type { CircuitComponent, SimulationState } from "./types";
import { getComponentDef } from "./componentLibrary";

interface Props {
  component: CircuitComponent | null;
  onUpdate: (id: string, updates: Partial<CircuitComponent>) => void;
  onDelete: (id: string) => void;
  onDuplicate: (id: string) => void;
  simState: SimulationState | null;
}

const ledColors = [
  { label: "红色", value: "#ff3333" },
  { label: "绿色", value: "#33cc33" },
  { label: "蓝色", value: "#3366ff" },
  { label: "黄色", value: "#ffcc00" },
  { label: "白色", value: "#ffffff" },
  { label: "紫色", value: "#9933ff" },
  { label: "橙色", value: "#ff8800" },
];

export default function PropertyInspector({
  component,
  onUpdate,
  onDelete,
  onDuplicate,
  simState,
}: Props) {
  const [label, setLabel] = useState("");

  useEffect(() => {
    if (component) {
      setLabel(component.label || "");
    }
  }, [component?.id, component?.label]);

  if (!component) {
    return (
      <div className="w-[240px] shrink-0 bg-surface border border-border rounded-2xl card-shadow flex flex-col items-center justify-center p-6">
        <Settings size={24} className="text-ink-faint mb-3" />
        <p className="text-[12px] text-ink-faint text-center">
          选择一个元件查看和编辑属性
        </p>
      </div>
    );
  }

  const def = getComponentDef(component.type);
  const compState = simState?.componentStates[component.id];

  const handleLabelChange = (value: string) => {
    setLabel(value);
    onUpdate(component.id, { label: value });
  };

  const handlePropChange = (key: string, value: string | number | boolean) => {
    onUpdate(component.id, {
      props: { ...component.props, [key]: value },
    });
  };

  const handleRotate = () => {
    const next = ((component.rotation + 90) % 360) as 0 | 90 | 180 | 270;
    onUpdate(component.id, { rotation: next });
  };

  return (
    <div className="w-[240px] shrink-0 bg-surface border border-border rounded-2xl card-shadow flex flex-col overflow-hidden">
      {/* Header */}
      <div className="px-4 py-3 border-b border-border">
        <div className="flex items-center justify-between">
          <h3 className="text-[13px] font-semibold text-ink">属性</h3>
          <div className="flex items-center gap-1">
            <button
              onClick={handleRotate}
              className="w-7 h-7 rounded-lg flex items-center justify-center text-ink-faint hover:text-accent hover:bg-accent-light transition-colors cursor-pointer"
              title="旋转"
            >
              <RotateCw size={13} />
            </button>
            <button
              onClick={() => onDuplicate(component.id)}
              className="w-7 h-7 rounded-lg flex items-center justify-center text-ink-faint hover:text-accent hover:bg-accent-light transition-colors cursor-pointer"
              title="复制"
            >
              <Copy size={13} />
            </button>
            <button
              onClick={() => onDelete(component.id)}
              className="w-7 h-7 rounded-lg flex items-center justify-center text-ink-faint hover:text-red-500 hover:bg-red-50 transition-colors cursor-pointer"
              title="删除"
            >
              <Trash2 size={13} />
            </button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto px-4 py-3 flex flex-col gap-4">
        {/* Component type */}
        <div className="flex items-center gap-2 p-2.5 bg-bg rounded-xl">
          <div className="w-8 h-8 rounded-lg bg-accent-light flex items-center justify-center">
            <span className="text-[12px] font-bold text-accent">
              {def.label[0]}
            </span>
          </div>
          <div>
            <div className="text-[12px] font-semibold text-ink">
              {def.label}
            </div>
            <div className="text-[10px] text-ink-faint">{component.type}</div>
          </div>
        </div>

        {/* Label */}
        <div>
          <label className="text-[11px] font-medium text-ink-secondary mb-1.5 block">
            标签名称
          </label>
          <input
            type="text"
            value={label}
            onChange={(e) => handleLabelChange(e.target.value)}
            className="w-full px-3 py-2 bg-bg border border-border rounded-lg text-[12px] outline-none focus:border-accent transition-colors"
          />
        </div>

        {/* Rotation */}
        <div>
          <label className="text-[11px] font-medium text-ink-secondary mb-1.5 block">
            旋转角度
          </label>
          <div className="flex gap-1.5">
            {[0, 90, 180, 270].map((angle) => (
              <button
                key={angle}
                onClick={() =>
                  onUpdate(component.id, {
                    rotation: angle as 0 | 90 | 180 | 270,
                  })
                }
                className={`flex-1 py-1.5 rounded-lg text-[11px] font-medium transition-colors cursor-pointer ${
                  component.rotation === angle
                    ? "bg-accent text-white"
                    : "bg-bg text-ink-secondary hover:bg-border-subtle"
                }`}
              >
                {angle}°
              </button>
            ))}
          </div>
        </div>

        {/* Position */}
        <div>
          <label className="text-[11px] font-medium text-ink-secondary mb-1.5 block">
            位置
          </label>
          <div className="flex gap-2">
            <div className="flex-1">
              <span className="text-[10px] text-ink-faint">X</span>
              <input
                type="number"
                value={Math.round(component.x)}
                onChange={(e) =>
                  onUpdate(component.id, { x: parseInt(e.target.value) || 0 })
                }
                className="w-full px-2 py-1 bg-bg border border-border rounded-lg text-[11px] outline-none focus:border-accent"
              />
            </div>
            <div className="flex-1">
              <span className="text-[10px] text-ink-faint">Y</span>
              <input
                type="number"
                value={Math.round(component.y)}
                onChange={(e) =>
                  onUpdate(component.id, { y: parseInt(e.target.value) || 0 })
                }
                className="w-full px-2 py-1 bg-bg border border-border rounded-lg text-[11px] outline-none focus:border-accent"
              />
            </div>
          </div>
        </div>

        {/* Component-specific properties */}
        <div className="border-t border-border pt-3">
          <h4 className="text-[11px] font-semibold text-ink-secondary mb-2">
            元件参数
          </h4>

          {/* LED color picker */}
          {component.type === "led" && (
            <div className="mb-3">
              <label className="text-[10px] text-ink-faint mb-1.5 block">
                颜色
              </label>
              <div className="flex flex-wrap gap-1.5">
                {ledColors.map((color) => (
                  <button
                    key={color.value}
                    onClick={() => handlePropChange("color", color.value)}
                    className={`w-7 h-7 rounded-lg border-2 transition-all cursor-pointer ${
                      component.props.color === color.value
                        ? "border-accent scale-110"
                        : "border-transparent"
                    }`}
                    style={{ backgroundColor: color.value }}
                    title={color.label}
                  />
                ))}
              </div>
            </div>
          )}

          {/* Resistor value */}
          {component.type === "resistor" && (
            <div className="mb-3">
              <label className="text-[10px] text-ink-faint mb-1.5 block">
                阻值 (Ω)
              </label>
              <select
                value={component.props.resistance as number}
                onChange={(e) =>
                  handlePropChange("resistance", parseInt(e.target.value))
                }
                className="w-full px-2 py-1.5 bg-bg border border-border rounded-lg text-[11px] outline-none"
              >
                {[
                  100, 220, 330, 470, 1000, 2200, 4700, 10000, 47000, 100000,
                ].map((r) => (
                  <option key={r} value={r}>
                    {r >= 1000 ? `${r / 1000}kΩ` : `${r}Ω`}
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Capacitor value */}
          {component.type === "capacitor" && (
            <div className="mb-3">
              <label className="text-[10px] text-ink-faint mb-1.5 block">
                容值 (μF)
              </label>
              <select
                value={component.props.capacitance as number}
                onChange={(e) =>
                  handlePropChange("capacitance", parseFloat(e.target.value))
                }
                className="w-full px-2 py-1.5 bg-bg border border-border rounded-lg text-[11px] outline-none"
              >
                {[0.1, 1, 10, 22, 47, 100, 220, 470, 1000].map((c) => (
                  <option key={c} value={c}>
                    {c < 1 ? `${c * 1000}nF` : `${c}μF`}
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Battery voltage */}
          {component.type === "battery" && (
            <div className="mb-3">
              <label className="text-[10px] text-ink-faint mb-1.5 block">
                电压 (V)
              </label>
              <select
                value={component.props.voltage as number}
                onChange={(e) =>
                  handlePropChange("voltage", parseFloat(e.target.value))
                }
                className="w-full px-2 py-1.5 bg-bg border border-border rounded-lg text-[11px] outline-none"
              >
                {[1.5, 3, 3.3, 5, 9, 12, 24].map((v) => (
                  <option key={v} value={v}>
                    {v}V
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* VCC voltage */}
          {component.type === "vcc" && (
            <div className="mb-3">
              <label className="text-[10px] text-ink-faint mb-1.5 block">
                电压 (V)
              </label>
              <select
                value={component.props.voltage as number}
                onChange={(e) =>
                  handlePropChange("voltage", parseFloat(e.target.value))
                }
                className="w-full px-2 py-1.5 bg-bg border border-border rounded-lg text-[11px] outline-none"
              >
                {[3.3, 5, 12].map((v) => (
                  <option key={v} value={v}>
                    {v}V
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Buzzer frequency */}
          {component.type === "buzzer" && (
            <div className="mb-3">
              <label className="text-[10px] text-ink-faint mb-1.5 block">
                频率 (Hz)
              </label>
              <input
                type="range"
                min={200}
                max={5000}
                step={100}
                value={component.props.frequency as number}
                onChange={(e) =>
                  handlePropChange("frequency", parseInt(e.target.value))
                }
                className="w-full"
              />
              <div className="text-[10px] text-ink-faint text-right">
                {component.props.frequency}Hz
              </div>
            </div>
          )}

          {/* Potentiometer position */}
          {component.type === "potentiometer" && (
            <div className="mb-3">
              <label className="text-[10px] text-ink-faint mb-1.5 block">
                位置 (%)
              </label>
              <input
                type="range"
                min={0}
                max={100}
                value={component.props.position as number}
                onChange={(e) =>
                  handlePropChange("position", parseInt(e.target.value))
                }
                className="w-full"
              />
              <div className="text-[10px] text-ink-faint text-right">
                {component.props.position}%
              </div>
            </div>
          )}

          {/* Photoresistor light level */}
          {component.type === "photoresistor" && (
            <div className="mb-3">
              <label className="text-[10px] text-ink-faint mb-1.5 block">
                光照强度 (%)
              </label>
              <input
                type="range"
                min={0}
                max={100}
                value={component.props.lightLevel as number}
                onChange={(e) =>
                  handlePropChange("lightLevel", parseInt(e.target.value))
                }
                className="w-full"
              />
              <div className="text-[10px] text-ink-faint text-right">
                {component.props.lightLevel}%
              </div>
            </div>
          )}

          {/* Thermistor temperature */}
          {component.type === "thermistor" && (
            <div className="mb-3">
              <label className="text-[10px] text-ink-faint mb-1.5 block">
                温度 (°C)
              </label>
              <input
                type="range"
                min={-20}
                max={100}
                value={component.props.temperature as number}
                onChange={(e) =>
                  handlePropChange("temperature", parseInt(e.target.value))
                }
                className="w-full"
              />
              <div className="text-[10px] text-ink-faint text-right">
                {component.props.temperature}°C
              </div>
            </div>
          )}

          {/* Button state */}
          {component.type === "button" && (
            <div className="mb-3">
              <label className="text-[10px] text-ink-faint mb-1.5 block">
                状态
              </label>
              <button
                onClick={() =>
                  handlePropChange("pressed", !component.props.pressed)
                }
                className={`w-full py-2 rounded-lg text-[12px] font-semibold transition-colors cursor-pointer ${
                  component.props.pressed
                    ? "bg-accent text-white"
                    : "bg-bg text-ink-secondary hover:bg-border-subtle"
                }`}
              >
                {component.props.pressed ? "按下中..." : "点击按下"}
              </button>
            </div>
          )}

          {/* Switch state */}
          {component.type === "switch" && (
            <div className="mb-3">
              <label className="text-[10px] text-ink-faint mb-1.5 block">
                状态
              </label>
              <button
                onClick={() => handlePropChange("on", !component.props.on)}
                className={`w-full py-2 rounded-lg text-[12px] font-semibold transition-colors cursor-pointer ${
                  component.props.on
                    ? "bg-teal text-white"
                    : "bg-bg text-ink-secondary hover:bg-border-subtle"
                }`}
              >
                {component.props.on ? "开启" : "关闭"}
              </button>
            </div>
          )}
        </div>

        {/* Simulation state (read-only) */}
        {simState?.running && compState && (
          <div className="border-t border-border pt-3">
            <h4 className="text-[11px] font-semibold text-ink-secondary mb-2">
              <span className="inline-block w-2 h-2 rounded-full bg-teal mr-1.5 animate-pulse" />
              仿真状态
            </h4>
            <div className="flex flex-col gap-1.5">
              {Object.entries(compState).map(([key, value]) => (
                <div key={key} className="flex items-center justify-between">
                  <span className="text-[10px] text-ink-faint capitalize">
                    {key}
                  </span>
                  <span className="text-[10px] font-medium text-ink">
                    {typeof value === "boolean"
                      ? value
                        ? "是"
                        : "否"
                      : String(value)}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Pin info */}
        <div className="border-t border-border pt-3">
          <h4 className="text-[11px] font-semibold text-ink-secondary mb-2">
            引脚信息
          </h4>
          <div className="flex flex-col gap-1.5">
            {def.pins.map((pin) => {
              const pinState = simState?.pinStates[`${component.id}:${pin.id}`];
              return (
                <div key={pin.id} className="flex items-center gap-2">
                  <span
                    className="w-2 h-2 rounded-full"
                    style={{
                      backgroundColor:
                        pin.type === "power"
                          ? "#e8a44a"
                          : pin.type === "ground"
                            ? "#6b5e4f"
                            : pinState?.isHigh
                              ? "#1a6b5a"
                              : "#a39480",
                    }}
                  />
                  <span className="text-[10px] text-ink-secondary flex-1">
                    {pin.label}
                  </span>
                  <span className="text-[9px] text-ink-faint bg-bg rounded px-1.5 py-0.5">
                    {pin.type}
                  </span>
                  {simState?.running && pinState && (
                    <span className="text-[9px] font-mono text-ink-faint">
                      {pinState.voltage.toFixed(1)}V
                    </span>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
