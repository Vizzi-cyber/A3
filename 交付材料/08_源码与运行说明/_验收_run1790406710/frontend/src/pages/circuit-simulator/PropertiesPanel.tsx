import React, { useState, useEffect } from "react";
import { Button, InputNumber, Select, Tooltip } from "antd";
import { DeleteOutlined, RotateRightOutlined } from "@ant-design/icons";
import { useCircuitStore } from "./store";
import { COMPONENT_DEFS, COMPONENT_LENGTH } from "./utils/constants";
import { formatValue } from "./utils/constants";
import type { Direction } from "./types";

const PropertiesPanel: React.FC = () => {
  const {
    components,
    selectedId,
    updateComponentValue,
    removeComponent,
    rotateComponent,
    selectComponent,
  } = useCircuitStore();
  const selected = components.find((c) => c.id === selectedId);

  const [editValue, setEditValue] = useState<number>(100);

  useEffect(() => {
    if (selected) {
      setEditValue(selected.value);
    }
  }, [selected]);

  if (!selected) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-4 h-full flex flex-col items-center justify-center text-gray-400">
        <div className="text-3xl mb-2">📐</div>
        <div className="text-sm">选择元件查看属性</div>
      </div>
    );
  }

  const def = COMPONENT_DEFS[selected.type];

  const handleValueChange = (val: number | null) => {
    if (val === null || val <= 0) return;
    setEditValue(val);
    updateComponentValue(selected.id, val);
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4 h-full overflow-y-auto">
      <h3 className="text-sm font-semibold text-gray-700 mb-3">元件属性</h3>

      {/* Component type */}
      <div className="mb-4 p-3 bg-gray-50 rounded-lg">
        <div className="text-xs text-gray-500">类型</div>
        <div className="text-sm font-medium text-gray-700">{def.label}</div>
      </div>

      {/* Value editor */}
      {selected.type !== "ground" && (
        <div className="mb-4">
          <label className="block text-xs text-gray-500 mb-1">
            参数值 ({def.unit})
          </label>
          <InputNumber
            value={editValue}
            onChange={handleValueChange}
            min={0.001}
            step={
              selected.type === "resistor"
                ? 10
                : selected.type === "voltage_source"
                  ? 1
                  : 0.001
            }
            className="w-full"
            size="small"
          />
          <div className="mt-1 text-xs text-gray-400">
            当前: {formatValue(editValue, selected.type)}
          </div>
        </div>
      )}

      {/* Quick value buttons */}
      {selected.type === "resistor" && (
        <div className="mb-4">
          <label className="block text-xs text-gray-500 mb-1">常用值</label>
          <div className="flex flex-wrap gap-1">
            {[10, 47, 100, 220, 330, 470, 1000, 2200, 4700, 10000].map((v) => (
              <Button
                key={v}
                size="small"
                type={editValue === v ? "primary" : "default"}
                onClick={() => handleValueChange(v)}
                className="text-xs"
              >
                {v >= 1000 ? `${v / 1000}kΩ` : `${v}Ω`}
              </Button>
            ))}
          </div>
        </div>
      )}

      {selected.type === "voltage_source" && (
        <div className="mb-4">
          <label className="block text-xs text-gray-500 mb-1">常用值</label>
          <div className="flex flex-wrap gap-1">
            {[1, 3.3, 5, 9, 12, 24].map((v) => (
              <Button
                key={v}
                size="small"
                type={editValue === v ? "primary" : "default"}
                onClick={() => handleValueChange(v)}
                className="text-xs"
              >
                {v}V
              </Button>
            ))}
          </div>
        </div>
      )}

      {selected.type === "current_source" && (
        <div className="mb-4">
          <label className="block text-xs text-gray-500 mb-1">常用值</label>
          <div className="flex flex-wrap gap-1">
            {[0.001, 0.005, 0.01, 0.05, 0.1].map((v) => (
              <Button
                key={v}
                size="small"
                type={editValue === v ? "primary" : "default"}
                onClick={() => handleValueChange(v)}
                className="text-xs"
              >
                {v < 0.001 ? `${v * 1e6}μA` : v < 1 ? `${v * 1e3}mA` : `${v}A`}
              </Button>
            ))}
          </div>
        </div>
      )}

      {/* Direction */}
      <div className="mb-4 p-3 bg-gray-50 rounded-lg">
        <div className="text-xs text-gray-500">方向</div>
        <div className="text-sm text-gray-700">
          {selected.direction === "right"
            ? "→ 水平向右"
            : selected.direction === "left"
              ? "← 水平向左"
              : selected.direction === "down"
                ? "↓ 竖直向下"
                : "↑ 竖直向上"}
        </div>
      </div>

      {/* Position */}
      <div className="mb-4 p-3 bg-gray-50 rounded-lg">
        <div className="text-xs text-gray-500">位置</div>
        <div className="text-sm font-mono text-gray-700">
          ({selected.position.x}, {selected.position.y})
        </div>
      </div>

      {/* Actions */}
      <div className="flex gap-2">
        <Tooltip title="旋转90°">
          <Button
            icon={<RotateRightOutlined />}
            onClick={() => rotateComponent(selected.id)}
          >
            旋转
          </Button>
        </Tooltip>
        <Tooltip title="删除">
          <Button
            danger
            icon={<DeleteOutlined />}
            onClick={() => {
              removeComponent(selected.id);
              selectComponent(null);
            }}
          >
            删除
          </Button>
        </Tooltip>
      </div>
    </div>
  );
};

export default PropertiesPanel;
