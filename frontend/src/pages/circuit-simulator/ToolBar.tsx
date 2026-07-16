import React from "react";
import { Button, Tooltip, Divider, message } from "antd";
import {
  AimOutlined,
  LineChartOutlined,
  DeleteOutlined,
  PlayCircleOutlined,
  ClearOutlined,
  RobotOutlined,
  UndoOutlined,
  RedoOutlined,
} from "@ant-design/icons";
import { useCircuitStore } from "./store";
import type { Mode } from "./types";

interface ToolBarProps {
  onAiAnalysis: () => void;
}

const ToolBar: React.FC<ToolBarProps> = ({ onAiAnalysis }) => {
  const {
    mode,
    setMode,
    simulate,
    clearAll,
    loadPreset,
    components,
    wires,
    undo,
    redo,
    history,
    historyIndex,
  } = useCircuitStore();

  const modes: { key: Mode; icon: React.ReactNode; label: string }[] = [
    { key: "select", icon: <AimOutlined />, label: "选择" },
    { key: "wire", icon: <LineChartOutlined />, label: "连线" },
    { key: "delete", icon: <DeleteOutlined />, label: "删除" },
  ];

  const handleSimulate = () => {
    if (components.length === 0) {
      message.warning("请先添加元件");
      return;
    }
    simulate();
    message.success("仿真完成");
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 px-4 py-2 flex items-center gap-3">
      {/* Mode buttons */}
      <div className="flex items-center border border-gray-200 rounded-lg overflow-hidden">
        {modes.map((m) => (
          <button
            key={m.key}
            onClick={() => setMode(m.key)}
            className={`px-3 py-1.5 text-xs font-medium transition-colors flex items-center gap-1.5 ${
              mode === m.key
                ? "bg-indigo-500 text-white"
                : "bg-white text-gray-600 hover:bg-gray-50"
            }`}
          >
            {m.icon}
            {m.label}
          </button>
        ))}
      </div>

      <Divider type="vertical" />

      {/* Simulate */}
      <Tooltip title="运行仿真 (Ctrl+Enter)">
        <Button
          type="primary"
          icon={<PlayCircleOutlined />}
          onClick={handleSimulate}
          className="!bg-indigo-500 !border-indigo-500"
        >
          仿真
        </Button>
      </Tooltip>

      {/* AI Analysis */}
      <Tooltip title="AI 分析电路">
        <Button icon={<RobotOutlined />} onClick={onAiAnalysis}>
          AI 分析
        </Button>
      </Tooltip>

      <Divider type="vertical" />

      {/* Preset Circuits */}
      <div className="flex items-center gap-1">
        <span className="text-xs text-gray-500 mr-1">预设:</span>
        <button
          onClick={() => {
            loadPreset("voltage-divider");
            message.success("已加载：分压电路");
          }}
          className="px-2.5 py-1 text-xs font-medium rounded-md bg-indigo-50 text-indigo-600 hover:bg-indigo-100 transition-colors"
        >
          分压电路
        </button>
        <button
          onClick={() => {
            loadPreset("rc-circuit");
            message.success("已加载：RC 充电电路");
          }}
          className="px-2.5 py-1 text-xs font-medium rounded-md bg-indigo-50 text-indigo-600 hover:bg-indigo-100 transition-colors"
        >
          RC 电路
        </button>
        <button
          onClick={() => {
            loadPreset("current-source-test");
            message.success("已加载：电流源电路");
          }}
          className="px-2.5 py-1 text-xs font-medium rounded-md bg-indigo-50 text-indigo-600 hover:bg-indigo-100 transition-colors"
        >
          电流源电路
        </button>
      </div>

      <Divider type="vertical" />

      {/* Undo/Redo */}
      <Tooltip title="撤销 (Ctrl+Z)">
        <Button
          icon={<UndoOutlined />}
          onClick={undo}
          disabled={historyIndex <= 0}
        />
      </Tooltip>
      <Tooltip title="重做 (Ctrl+Y)">
        <Button
          icon={<RedoOutlined />}
          onClick={redo}
          disabled={historyIndex >= history.length - 1}
        />
      </Tooltip>

      <Divider type="vertical" />

      {/* Clear */}
      <Tooltip title="清空画布">
        <Button danger icon={<ClearOutlined />} onClick={clearAll}>
          清空
        </Button>
      </Tooltip>

      {/* Stats */}
      <div className="ml-auto flex items-center gap-4 text-xs text-gray-500">
        <span>元件: {components.length}</span>
        <span>导线: {wires.length}</span>
      </div>
    </div>
  );
};

export default ToolBar;
