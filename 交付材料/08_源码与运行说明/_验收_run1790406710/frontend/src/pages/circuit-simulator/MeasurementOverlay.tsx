import React from "react";
import { useCircuitStore } from "./store";
import type { TransientResult } from "./types";

/** 稳态建立时间：波形最后一次离开终值 ±1% 带的时刻 */
function settlingSeconds(wave: number[]): number | null {
  if (wave.length < 2) return null;
  const final = wave[wave.length - 1];
  const band = 0.01 * Math.max(Math.abs(final), 1e-9);
  for (let i = wave.length - 1; i >= 0; i--) {
    if (Math.abs(wave[i] - final) > band) {
      return i < wave.length - 1 ? i + 1 : i;
    }
  }
  return 0;
}

function formatSeconds(s: number): string {
  if (s < 1e-6) return `${(s * 1e9).toFixed(1)}ns`;
  if (s < 1e-3) return `${(s * 1e6).toFixed(1)}μs`;
  if (s < 1) return `${(s * 1e3).toFixed(2)}ms`;
  return `${s.toFixed(3)}s`;
}

const TransientPanel: React.FC<{ transient: TransientResult }> = ({
  transient,
}) => {
  const rows: { name: string; kind: string; settle: string; final: string }[] =
    [];

  Object.entries(transient.capacitorVoltages).forEach(([name, wave]) => {
    const t = settlingSeconds(wave);
    rows.push({
      name,
      kind: "电容电压",
      settle: t === null ? "—" : formatSeconds(transient.time[t] ?? 0),
      final: `${(wave[wave.length - 1] ?? 0).toFixed(3)}V`,
    });
  });
  Object.entries(transient.inductorCurrents).forEach(([name, wave]) => {
    const t = settlingSeconds(wave);
    rows.push({
      name,
      kind: "电感电流",
      settle: t === null ? "—" : formatSeconds(transient.time[t] ?? 0),
      final: `${(wave[wave.length - 1] ?? 0).toFixed(3)}A`,
    });
  });
  if (rows.length === 0) return null;

  return (
    <div className="mb-2">
      <div className="text-xs text-gray-500 mb-1">暂态分析（RK4）</div>
      <div className="grid gap-1">
        {rows.map((r) => (
          <div
            key={r.name}
            className="text-xs font-mono bg-purple-50 rounded px-2 py-1"
          >
            {r.name} {r.kind}: 终值 {r.final}，稳态建立 ≈ {r.settle}
          </div>
        ))}
      </div>
    </div>
  );
};

const MeasurementOverlay: React.FC = () => {
  const { simulationResult } = useCircuitStore();

  if (!simulationResult) return null;

  const { nodeVoltages, branchCurrents, errors, transient } = simulationResult;

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

      {transient && <TransientPanel transient={transient} />}

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
