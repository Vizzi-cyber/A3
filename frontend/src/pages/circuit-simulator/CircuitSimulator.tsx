import React, { useState } from "react";
import Canvas from "./Canvas";
import ComponentPalette from "./ComponentPalette";
import PropertiesPanel from "./PropertiesPanel";
import ToolBar from "./ToolBar";
import MeasurementOverlay from "./MeasurementOverlay";
import AiAnalysisDialog from "./AiAnalysisDialog";

const CircuitSimulator: React.FC = () => {
  const [aiOpen, setAiOpen] = useState(false);

  return (
    <div className="space-y-4 pb-8">
      {/* Header */}
      <div className="bg-white rounded-lg border border-gray-200 p-5">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center">
            <svg
              className="w-5 h-5 text-white"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M13 10V3L4 14h7v7l9-11h-7z"
              />
            </svg>
          </div>
          <div>
            <h1 className="text-lg font-bold text-gray-800">电路仿真器</h1>
            <p className="text-sm text-gray-500">
              拖拽元件到画布，连线后仿真分析电路
            </p>
          </div>
        </div>
      </div>

      {/* Toolbar */}
      <ToolBar onAiAnalysis={() => setAiOpen(true)} />

      {/* Main content */}
      <div
        className="flex gap-4"
        style={{ height: "calc(100vh - 260px)", minHeight: "500px" }}
      >
        {/* Left: Component Palette */}
        <div className="w-48 shrink-0">
          <ComponentPalette />
        </div>

        {/* Center: Canvas */}
        <div className="flex-1 bg-white rounded-lg border border-gray-200 overflow-hidden relative">
          <Canvas />
          <MeasurementOverlay />
        </div>

        {/* Right: Properties Panel */}
        <div className="w-64 shrink-0">
          <PropertiesPanel />
        </div>
      </div>

      {/* AI Analysis Dialog */}
      <AiAnalysisDialog open={aiOpen} onClose={() => setAiOpen(false)} />
    </div>
  );
};

export default CircuitSimulator;
