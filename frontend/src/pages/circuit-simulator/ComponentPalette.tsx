import React from "react";
import { COMPONENT_DEFS, COMPONENT_ORDER, GRID_SIZE } from "./utils/constants";
import { getComponentSVGPath } from "./utils/drawing-utils";
import type { ComponentType } from "./types";

const MiniIcon: React.FC<{ type: ComponentType }> = ({ type }) => {
  const s = 3;
  const w = 32;
  const h = 24;
  const cx = w / 2;
  const cy = h / 2;

  const renderIcon = () => {
    switch (type) {
      case "resistor":
        return (
          <polyline
            points={`${cx - 12},${cy} ${cx - 9},${cy} ${cx - 7},${cy - 4} ${cx - 4},${cy + 4} ${cx - 1},${cy - 4} ${cx + 2},${cy + 4} ${cx + 5},${cy - 4} ${cx + 8},${cy} ${cx + 12},${cy}`}
            stroke="#374151"
            strokeWidth={1.5}
            fill="none"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        );
      case "capacitor":
        return (
          <g>
            <line
              x1={cx - 12}
              y1={cy}
              x2={cx - 3}
              y2={cy}
              stroke="#374151"
              strokeWidth={1.5}
            />
            <line
              x1={cx - 3}
              y1={cy - 6}
              x2={cx - 3}
              y2={cy + 6}
              stroke="#374151"
              strokeWidth={1.5}
            />
            <line
              x1={cx + 3}
              y1={cy - 6}
              x2={cx + 3}
              y2={cy + 6}
              stroke="#374151"
              strokeWidth={1.5}
            />
            <line
              x1={cx + 3}
              y1={cy}
              x2={cx + 12}
              y2={cy}
              stroke="#374151"
              strokeWidth={1.5}
            />
          </g>
        );
      case "inductor":
        return (
          <path
            d={`M ${cx - 12},${cy} L ${cx - 9},${cy} Q ${cx - 7},${cy - 5} ${cx - 5},${cy} Q ${cx - 3},${cy - 5} ${cx - 1},${cy} Q ${cx + 1},${cy - 5} ${cx + 3},${cy} Q ${cx + 5},${cy - 5} ${cx + 7},${cy} L ${cx + 12},${cy}`}
            stroke="#374151"
            strokeWidth={1.5}
            fill="none"
            strokeLinecap="round"
          />
        );
      case "voltage_source":
        return (
          <g>
            <circle
              cx={cx}
              cy={cy}
              r={8}
              fill="white"
              stroke="#374151"
              strokeWidth={1.5}
            />
            <text
              x={cx}
              y={cy - 1}
              textAnchor="middle"
              fontSize={8}
              fontWeight="bold"
              fill="#dc2626"
            >
              +
            </text>
            <text
              x={cx}
              y={cy + 6}
              textAnchor="middle"
              fontSize={8}
              fontWeight="bold"
              fill="#2563eb"
            >
              −
            </text>
          </g>
        );
      case "current_source":
        return (
          <g>
            <circle
              cx={cx}
              cy={cy}
              r={8}
              fill="white"
              stroke="#374151"
              strokeWidth={1.5}
            />
            <line
              x1={cx - 4}
              y1={cy + 3}
              x2={cx + 4}
              y2={cy + 3}
              stroke="#374151"
              strokeWidth={1.5}
            />
            <polygon
              points={`${cx + 4},${cy + 3} ${cx + 1},${cy + 0.5} ${cx + 1},${cy + 5.5}`}
              fill="#374151"
            />
          </g>
        );
      case "ground":
        return (
          <g>
            <line
              x1={cx}
              y1={cy - 4}
              x2={cx}
              y2={cy + 2}
              stroke="#374151"
              strokeWidth={1.5}
            />
            <line
              x1={cx - 6}
              y1={cy + 2}
              x2={cx + 6}
              y2={cy + 2}
              stroke="#374151"
              strokeWidth={1.5}
            />
            <line
              x1={cx - 4}
              y1={cy + 5}
              x2={cx + 4}
              y2={cy + 5}
              stroke="#374151"
              strokeWidth={1.5}
            />
            <line
              x1={cx - 2}
              y1={cy + 8}
              x2={cx + 2}
              y2={cy + 8}
              stroke="#374151"
              strokeWidth={1.5}
            />
          </g>
        );
      default:
        return null;
    }
  };

  return (
    <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`}>
      {renderIcon()}
    </svg>
  );
};

const ComponentPalette: React.FC = () => {
  const handleDragStart = (e: React.DragEvent, type: ComponentType) => {
    e.dataTransfer.setData("component-type", type);
    e.dataTransfer.effectAllowed = "copy";
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4 h-full">
      <h3 className="text-sm font-semibold text-gray-700 mb-3">元件面板</h3>
      <div className="space-y-2">
        {COMPONENT_ORDER.map((type) => {
          const def = COMPONENT_DEFS[type];
          return (
            <div
              key={type}
              draggable
              onDragStart={(e) => handleDragStart(e, type)}
              className="flex items-center gap-3 p-2 rounded-lg border border-gray-100 hover:border-indigo-300 hover:bg-indigo-50 cursor-grab active:cursor-grabbing transition-all"
            >
              <MiniIcon type={type} />
              <div className="text-xs">
                <div className="font-medium text-gray-700">{def.label}</div>
                <div className="text-gray-400">
                  {type !== "ground" ? `${def.defaultValue}${def.unit}` : ""}
                </div>
              </div>
            </div>
          );
        })}
      </div>
      <div className="mt-4 p-3 bg-gray-50 rounded-lg text-xs text-gray-500">
        <p className="font-medium text-gray-600 mb-1">操作提示</p>
        <ul className="space-y-1">
          <li>拖拽元件到画布放置</li>
          <li>双击编辑元件参数</li>
          <li>点击端子开始连线</li>
          <li>Escape / 右键 取消连线</li>
          <li>Delete 删除选中元件</li>
          <li>Ctrl+Z 撤销 / Ctrl+Y 重做</li>
          <li>Alt+拖拽 平移画布</li>
          <li>滚轮 缩放画布</li>
        </ul>
      </div>
    </div>
  );
};

export default ComponentPalette;
