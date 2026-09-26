import { useState } from "react";
import { Search, ChevronDown, ChevronRight } from "lucide-react";
import { getAllComponents, categoryLabels } from "./componentLibrary";
import type { ComponentDef } from "./types";

interface Props {
  onDragStart: (type: ComponentDef) => void;
}

const categoryIcons: Record<string, string> = {
  mcu: "🔧",
  passive: "⚡",
  active: "🔌",
  output: "💡",
  sensor: "📡",
  power: "🔋",
  connector: "🔲",
};

export default function ComponentPalette({ onDragStart }: Props) {
  const [search, setSearch] = useState("");
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(
    new Set(["mcu"]),
  );

  const allComponents = getAllComponents();

  const filtered = search
    ? allComponents.filter(
        (c) =>
          c.label.toLowerCase().includes(search.toLowerCase()) ||
          c.type.toLowerCase().includes(search.toLowerCase()),
      )
    : allComponents;

  const grouped = Object.entries(categoryLabels).map(([key, label]) => ({
    key: key as ComponentDef["category"],
    label,
    icon: categoryIcons[key] || "📦",
    items: filtered.filter((c) => c.category === key),
  }));

  const toggleCategory = (key: string) => {
    setExpandedCategories((prev) => {
      const next = new Set(prev);
      if (next.has(key)) next.delete(key);
      else next.add(key);
      return next;
    });
  };

  const handleDragStart = (e: React.DragEvent, comp: ComponentDef) => {
    e.dataTransfer.setData("circuit-component", JSON.stringify(comp));
    onDragStart(comp);
  };

  return (
    <div className="w-[240px] shrink-0 bg-surface border border-border rounded-2xl card-shadow flex flex-col overflow-hidden">
      {/* Header */}
      <div className="px-4 pt-4 pb-3 border-b border-border">
        <h3 className="text-[13px] font-semibold text-ink mb-2">元件库</h3>
        <div className="relative">
          <Search
            size={14}
            className="absolute left-3 top-1/2 -translate-y-1/2 text-ink-faint"
          />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="搜索元件..."
            className="w-full pl-9 pr-3 py-2 bg-bg border border-border rounded-lg text-[12px] outline-none focus:border-accent transition-colors"
          />
        </div>
      </div>

      {/* Component list */}
      <div className="flex-1 overflow-y-auto px-2 py-2">
        {grouped.map((group) => {
          if (group.items.length === 0) return null;
          const isExpanded = expandedCategories.has(group.key);

          return (
            <div key={group.key} className="mb-1">
              <button
                onClick={() => toggleCategory(group.key)}
                className="w-full flex items-center gap-2 px-2 py-1.5 text-[12px] font-medium text-ink-secondary hover:text-ink transition-colors cursor-pointer rounded-lg hover:bg-bg"
              >
                {isExpanded ? (
                  <ChevronDown size={12} />
                ) : (
                  <ChevronRight size={12} />
                )}
                <span>{group.icon}</span>
                <span>{group.label}</span>
                <span className="ml-auto text-[10px] text-ink-faint bg-bg rounded-full px-1.5">
                  {group.items.length}
                </span>
              </button>

              {isExpanded && (
                <div className="flex flex-wrap gap-1.5 px-2 py-1.5">
                  {group.items.map((comp) => (
                    <div
                      key={comp.type}
                      draggable
                      onDragStart={(e) => handleDragStart(e, comp)}
                      className="flex flex-col items-center gap-1 p-2.5 rounded-xl border border-border-subtle hover:border-accent hover:bg-accent-light cursor-grab active:cursor-grabbing transition-all group w-[70px]"
                      title={comp.label}
                    >
                      <ComponentIcon type={comp.type} />
                      <span className="text-[10px] text-ink-secondary group-hover:text-accent transition-colors text-center leading-tight">
                        {comp.label}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Help */}
      <div className="px-4 py-3 border-t border-border bg-bg/50">
        <p className="text-[10px] text-ink-faint leading-relaxed">
          拖拽元件到画布 · 点击引脚连线 · 右键删除
        </p>
      </div>
    </div>
  );
}

// Simple SVG icons for each component type
function ComponentIcon({ type }: { type: string }) {
  const iconMap: Record<string, React.JSX.Element> = {
    led: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <path d="M12 4L6 12H18L12 4Z" fill="#c44b2b" opacity="0.8" />
        <rect x="8" y="12" width="8" height="3" rx="1" fill="#6b5e4f" />
        <line
          x1="10"
          y1="15"
          x2="10"
          y2="20"
          stroke="#6b5e4f"
          strokeWidth="1.5"
        />
        <line
          x1="14"
          y1="15"
          x2="14"
          y2="20"
          stroke="#6b5e4f"
          strokeWidth="1.5"
        />
      </svg>
    ),
    resistor: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <path
          d="M2 12H5L7 6L10 18L13 6L16 18L19 12H22"
          stroke="#6b5e4f"
          strokeWidth="1.5"
          fill="none"
        />
      </svg>
    ),
    capacitor: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <line
          x1="2"
          y1="12"
          x2="9"
          y2="12"
          stroke="#6b5e4f"
          strokeWidth="1.5"
        />
        <line x1="9" y1="6" x2="9" y2="18" stroke="#6b5e4f" strokeWidth="2" />
        <line x1="15" y1="6" x2="15" y2="18" stroke="#6b5e4f" strokeWidth="2" />
        <line
          x1="15"
          y1="12"
          x2="22"
          y2="12"
          stroke="#6b5e4f"
          strokeWidth="1.5"
        />
      </svg>
    ),
    battery: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <rect
          x="7"
          y="5"
          width="10"
          height="14"
          rx="2"
          fill="#e8a44a"
          opacity="0.3"
          stroke="#6b5e4f"
          strokeWidth="1.5"
        />
        <rect x="10" y="3" width="4" height="3" rx="1" fill="#e8a44a" />
        <text
          x="12"
          y="11"
          textAnchor="middle"
          fontSize="6"
          fontWeight="bold"
          fill="#1a1208"
        >
          +
        </text>
        <text
          x="12"
          y="18"
          textAnchor="middle"
          fontSize="8"
          fontWeight="bold"
          fill="#1a1208"
        >
          −
        </text>
      </svg>
    ),
    button: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <rect
          x="6"
          y="10"
          width="12"
          height="6"
          rx="2"
          fill="#f0f0f0"
          stroke="#6b5e4f"
          strokeWidth="1.5"
        />
        <rect
          x="8"
          y="6"
          width="8"
          height="5"
          rx="2"
          fill="#ddd"
          stroke="#6b5e4f"
          strokeWidth="1"
        />
      </svg>
    ),
    switch: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <rect
          x="4"
          y="8"
          width="16"
          height="8"
          rx="3"
          fill="#f0f0f0"
          stroke="#6b5e4f"
          strokeWidth="1.5"
        />
        <circle cx="8" cy="12" r="2" fill="#c44b2b" />
        <line x1="8" y1="12" x2="16" y2="8" stroke="#1a1208" strokeWidth="2" />
      </svg>
    ),
    motor: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <circle
          cx="12"
          cy="12"
          r="8"
          fill="#f0f0f0"
          stroke="#6b5e4f"
          strokeWidth="1.5"
        />
        <circle cx="12" cy="12" r="3" stroke="#6b5e4f" strokeWidth="1" />
        <text
          x="12"
          y="14"
          textAnchor="middle"
          fontSize="7"
          fontWeight="bold"
          fill="#1a1208"
        >
          M
        </text>
      </svg>
    ),
    buzzer: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <circle
          cx="12"
          cy="12"
          r="7"
          fill="#f0f0f0"
          stroke="#6b5e4f"
          strokeWidth="1.5"
        />
        <text
          x="12"
          y="14"
          textAnchor="middle"
          fontSize="8"
          fontWeight="bold"
          fill="#1a1208"
        >
          +
        </text>
      </svg>
    ),
    potentiometer: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <rect
          x="5"
          y="6"
          width="14"
          height="12"
          rx="2"
          fill="#f0f0f0"
          stroke="#6b5e4f"
          strokeWidth="1.5"
        />
        <line x1="7" y1="12" x2="17" y2="12" stroke="#a39480" strokeWidth="2" />
        <polygon points="12,7 9,12 15,12" fill="#c44b2b" />
      </svg>
    ),
    servo: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <rect
          x="5"
          y="5"
          width="14"
          height="14"
          rx="2"
          fill="#2a2a3a"
          stroke="#6b5e4f"
          strokeWidth="1.5"
        />
        <circle
          cx="12"
          cy="9"
          r="3"
          fill="#888"
          stroke="#aaa"
          strokeWidth="1"
        />
        <line x1="12" y1="9" x2="15" y2="7" stroke="#aaa" strokeWidth="2" />
      </svg>
    ),
    seven_segment: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <rect
          x="4"
          y="2"
          width="16"
          height="20"
          rx="2"
          fill="#1a1a2e"
          stroke="#6b5e4f"
          strokeWidth="1.5"
        />
        <text
          x="12"
          y="14"
          textAnchor="middle"
          fontSize="10"
          fontFamily="monospace"
          fill="#ff4444"
        >
          8
        </text>
      </svg>
    ),
    lcd: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <rect
          x="2"
          y="4"
          width="20"
          height="16"
          rx="2"
          fill="#2a6b4a"
          stroke="#6b5e4f"
          strokeWidth="1.5"
        />
        <rect x="4" y="6" width="16" height="8" rx="1" fill="#8bac0f" />
        <text x="12" y="12" textAnchor="middle" fontSize="5" fill="#1a2a00">
          Hello
        </text>
      </svg>
    ),
    ultrasonic: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <rect
          x="2"
          y="4"
          width="20"
          height="16"
          rx="2"
          fill="#3a7ca5"
          stroke="#6b5e4f"
          strokeWidth="1.5"
        />
        <circle
          cx="8"
          cy="12"
          r="4"
          fill="#ccc"
          stroke="#999"
          strokeWidth="1"
        />
        <circle
          cx="16"
          cy="12"
          r="4"
          fill="#ccc"
          stroke="#999"
          strokeWidth="1"
        />
      </svg>
    ),
    photoresistor: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <circle
          cx="12"
          cy="12"
          r="7"
          fill="#8866aa"
          stroke="#6b5e4f"
          strokeWidth="1.5"
        />
        <path
          d="M9 9L15 15M15 9L9 15"
          stroke="#fff"
          strokeWidth="1"
          opacity="0.5"
        />
        <line
          x1="18"
          y1="4"
          x2="16"
          y2="8"
          stroke="#ffdd44"
          strokeWidth="1.5"
        />
        <line
          x1="20"
          y1="6"
          x2="18"
          y2="10"
          stroke="#ffdd44"
          strokeWidth="1.5"
        />
      </svg>
    ),
    thermistor: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <rect
          x="6"
          y="4"
          width="12"
          height="16"
          rx="3"
          fill="#f0f0f0"
          stroke="#6b5e4f"
          strokeWidth="1.5"
        />
        <text
          x="12"
          y="14"
          textAnchor="middle"
          fontSize="8"
          fontWeight="bold"
          fill="#1a1208"
        >
          t°
        </text>
      </svg>
    ),
    arduino_uno: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <rect
          x="2"
          y="4"
          width="20"
          height="16"
          rx="2"
          fill="#1a5c8a"
          stroke="#6b5e4f"
          strokeWidth="1.5"
        />
        <rect x="7" y="8" width="10" height="6" rx="1" fill="#1a1a2e" />
        <circle cx="18" cy="6" r="1" fill="#00ff00" />
      </svg>
    ),
    esp32: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <rect
          x="2"
          y="4"
          width="20"
          height="16"
          rx="2"
          fill="#8b2252"
          stroke="#6b5e4f"
          strokeWidth="1.5"
        />
        <rect x="7" y="8" width="10" height="6" rx="1" fill="#1a1a2e" />
      </svg>
    ),
    stm32: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <rect
          x="2"
          y="4"
          width="20"
          height="16"
          rx="2"
          fill="#2a4a6a"
          stroke="#6b5e4f"
          strokeWidth="1.5"
        />
        <rect x="7" y="8" width="10" height="6" rx="1" fill="#1a1a2e" />
      </svg>
    ),
    stm32_bluepill: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <rect
          x="3"
          y="3"
          width="18"
          height="18"
          rx="2"
          fill="#1a3a6a"
          stroke="#0d1f3c"
          strokeWidth="1.5"
        />
        <rect x="7" y="7" width="10" height="8" rx="1" fill="#1a1a1a" />
        <text x="12" y="12" textAnchor="middle" fontSize="4" fill="#ccc">
          STM32
        </text>
        <circle cx="5" cy="5" r="1" fill="#00ff00" />
      </svg>
    ),
    oled_ssd1306: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <rect
          x="3"
          y="3"
          width="18"
          height="18"
          rx="2"
          fill="#1a2744"
          stroke="#6b5e4f"
          strokeWidth="1.5"
        />
        <rect x="5" y="5" width="14" height="8" rx="1" fill="#0a0a0a" />
        <text x="12" y="10" textAnchor="middle" fontSize="4" fill="#00ccff">
          OLED
        </text>
        <text x="12" y="19" textAnchor="middle" fontSize="3" fill="#888">
          I2C
        </text>
      </svg>
    ),
    mpu6050: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <rect
          x="3"
          y="3"
          width="18"
          height="18"
          rx="2"
          fill="#6a1b5e"
          stroke="#3d0e36"
          strokeWidth="1.5"
        />
        <rect x="7" y="7" width="10" height="6" rx="1" fill="#1a1a1a" />
        <text x="12" y="11" textAnchor="middle" fontSize="3.5" fill="#ccc">
          MPU
        </text>
      </svg>
    ),
    stlink: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <rect
          x="5"
          y="3"
          width="14"
          height="18"
          rx="2"
          fill="#555"
          stroke="#333"
          strokeWidth="1.5"
        />
        <rect x="8" y="3" width="8" height="3" rx="1" fill="#aaa" />
        <text x="12" y="13" textAnchor="middle" fontSize="4" fill="#fff">
          ST
        </text>
        <text x="12" y="17" textAnchor="middle" fontSize="3" fill="#ccc">
          Link
        </text>
      </svg>
    ),
    usb_ttl: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <rect
          x="4"
          y="3"
          width="16"
          height="18"
          rx="2"
          fill="#2a5a2a"
          stroke="#1a3a1a"
          strokeWidth="1.5"
        />
        <rect x="8" y="3" width="8" height="3" rx="1" fill="#aaa" />
        <text x="12" y="13" textAnchor="middle" fontSize="4" fill="#fff">
          USB
        </text>
        <text x="12" y="17" textAnchor="middle" fontSize="3" fill="#ccc">
          TTL
        </text>
      </svg>
    ),
    ir_sensor: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <rect
          x="3"
          y="4"
          width="18"
          height="16"
          rx="2"
          fill="#2a4a2a"
          stroke="#1a3a1a"
          strokeWidth="1.5"
        />
        <circle
          cx="8"
          cy="10"
          r="3"
          fill="#4a2a4a"
          stroke="#6b5e4f"
          strokeWidth="1"
        />
        <circle
          cx="16"
          cy="10"
          r="3"
          fill="#2a2a4a"
          stroke="#6b5e4f"
          strokeWidth="1"
        />
      </svg>
    ),
    rotary_encoder: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <rect
          x="5"
          y="4"
          width="14"
          height="14"
          rx="2"
          fill="#888"
          stroke="#555"
          strokeWidth="1.5"
        />
        <circle
          cx="12"
          cy="10"
          r="4"
          fill="#aaa"
          stroke="#888"
          strokeWidth="1"
        />
        <line
          x1="12"
          y1="10"
          x2="15"
          y2="8"
          stroke="#c44b2b"
          strokeWidth="1.5"
        />
      </svg>
    ),
    w25q64: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <rect
          x="3"
          y="4"
          width="18"
          height="16"
          rx="2"
          fill="#1a3a5a"
          stroke="#0d1f3c"
          strokeWidth="1.5"
        />
        <rect x="6" y="7" width="12" height="6" rx="1" fill="#1a1a1a" />
        <text x="12" y="11" textAnchor="middle" fontSize="3.5" fill="#ccc">
          W25Q64
        </text>
        <text x="12" y="18" textAnchor="middle" fontSize="3" fill="#888">
          SPI
        </text>
      </svg>
    ),
    ground: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <line x1="12" y1="4" x2="12" y2="10" stroke="#6b5e4f" strokeWidth="2" />
        <line x1="6" y1="10" x2="18" y2="10" stroke="#6b5e4f" strokeWidth="2" />
        <line x1="8" y1="14" x2="16" y2="14" stroke="#6b5e4f" strokeWidth="2" />
        <line
          x1="10"
          y1="18"
          x2="14"
          y2="18"
          stroke="#6b5e4f"
          strokeWidth="2"
        />
      </svg>
    ),
    vcc: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <line
          x1="12"
          y1="20"
          x2="12"
          y2="10"
          stroke="#e8a44a"
          strokeWidth="2"
        />
        <polygon points="12,6 8,12 16,12" fill="#e8a44a" />
        <text
          x="12"
          y="5"
          textAnchor="middle"
          fontSize="6"
          fontWeight="bold"
          fill="#e8a44a"
        >
          VCC
        </text>
      </svg>
    ),
    breadboard: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <rect
          x="2"
          y="6"
          width="20"
          height="12"
          rx="2"
          fill="#f5f0e0"
          stroke="#6b5e4f"
          strokeWidth="1.5"
        />
        <line x1="2" y1="12" x2="22" y2="12" stroke="#ddd" strokeWidth="1" />
        {[4, 7, 10, 13, 16, 19].map((x) => (
          <circle key={`t${x}`} cx={x} cy="9" r="0.8" fill="#cc4444" />
        ))}
        {[4, 7, 10, 13, 16, 19].map((x) => (
          <circle key={`b${x}`} cx={x} cy="15" r="0.8" fill="#4444cc" />
        ))}
      </svg>
    ),
  };

  return (
    iconMap[type] || (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <rect
          x="4"
          y="4"
          width="16"
          height="16"
          rx="3"
          fill="#f0f0f0"
          stroke="#6b5e4f"
          strokeWidth="1.5"
        />
      </svg>
    )
  );
}
