import React from "react";
import { useCircuitStore } from "./store";

const MeasurementOverlay: React.FC = () => {
  const { simulationResult } = useCircuitStore();

  if (!simulationResult) return null;

  const { nodeVoltages, branchCurrents, errors } = simulationResult;

  if (errors.length === 0 && Object.keys(nodeVoltages).length === 0)
    return null;

  return (
    <div className="absolute top-3 right-3 bg-white rounded-lg border border-gray-200 p-3 shadow-sm max-w-xs">
      <h4 className="text-xs font-semibold text-gray-700 mb-2">仿真结果</h4>

      {errors.length > 0 && (
        <div className="mb-2">
          {errors.map((err, i) => (
            <div
              key={i}
              className="text-xs text-amber-600 bg-amber-50 rounded px-2 py-1 mb-1"
            >
              {err}
            </div>
          ))}
        </div>
      )}

      {Object.keys(nodeVoltages).length > 0 && (
        <div className="mb-2">
          <div className="text-xs text-gray-500 mb-1">节点电压</div>
          <div className="grid grid-cols-2 gap-1">
            {Object.entries(nodeVoltages).map(([node, voltage]) => (
              <div
                key={node}
                className="text-xs font-mono bg-blue-50 rounded px-2 py-1"
              >
                V{node}: {voltage.toFixed(3)}V
              </div>
            ))}
          </div>
        </div>
      )}

      {Object.keys(branchCurrents).length > 0 && (
        <div>
          <div className="text-xs text-gray-500 mb-1">支路电流</div>
          <div className="grid grid-cols-2 gap-1">
            {Object.entries(branchCurrents).map(([name, current]) => (
              <div
                key={name}
                className="text-xs font-mono bg-green-50 rounded px-2 py-1"
              >
                {name}:{" "}
                {Math.abs(current) < 0.001
                  ? `${(current * 1e6).toFixed(1)}μA`
                  : Math.abs(current) < 1
                    ? `${(current * 1e3).toFixed(2)}mA`
                    : `${current.toFixed(3)}A`}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default MeasurementOverlay;
