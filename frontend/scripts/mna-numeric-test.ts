/**
 * MNA 求解器数值验证（直流 + RK4 暂态）
 * 运行：cd frontend && npm run test:mna
 * 用教科书解析解对照：
 *   - RC 充电：vc(t) = V(1 − e^(−t/RC))
 *   - RL 升流：i(t) = (V/R)(1 − e^(−tR/L))
 *   - LC 振荡：vc(t) = V(1 − cos(ω0·t))，峰值 2V
 *   - 直流电感短路：稳态电流 = V/R
 */
import {
  solveCircuit,
  runTransientAnalysis,
} from "../src/pages/circuit-simulator/utils/mna-solver";
import { getTerminalPositions } from "../src/pages/circuit-simulator/utils/circuit-utils";
import type {
  CircuitComponent,
  Wire,
  ComponentType,
} from "../src/pages/circuit-simulator/types";

let nextId = 1;

function comp(
  type: ComponentType,
  x: number,
  y: number,
  value: number,
): CircuitComponent {
  return {
    id: `t${nextId++}`,
    type,
    position: { x, y },
    direction: "right",
    value,
    terminals: [],
  };
}

/** 闭环连接：电源 t0（正端）→ 元件链 → 接地；电源 t1（负端） → 接地 */
function series(components: CircuitComponent[]): Wire[] {
  const wires: Wire[] = [];
  const source = components[0];
  const gnd = components[components.length - 1];
  const gndT = getTerminalPositions(gnd)[0];
  let prevT = getTerminalPositions(source)[0];
  for (let i = 1; i < components.length - 1; i++) {
    const t = getTerminalPositions(components[i]);
    wires.push({ id: `w${nextId++}`, points: [prevT, t[0]] });
    prevT = t[1];
  }
  wires.push({ id: `w${nextId++}`, points: [prevT, gndT] });
  wires.push({
    id: `w${nextId++}`,
    points: [getTerminalPositions(source)[1], gndT],
  });
  return wires;
}

let failures = 0;
function check(name: string, cond: boolean, detail: string): void {
  if (cond) {
    console.log(`  ✅ ${name}`);
  } else {
    failures++;
    console.log(`  ❌ ${name} (${detail})`);
  }
}

function main(): void {
  console.log("MNA 求解器数值验证");

  // ── 1. 纯电阻直流 ──
  {
    const c = [
      comp("voltage_source", 0, 0, 5),
      comp("resistor", 10, 0, 10),
      comp("ground", 20, 0, 0),
    ];
    const r = solveCircuit(c, series(c));
    check(
      "纯电阻直流：电流 = V/R = 0.5A",
      Math.abs((r.branchCurrents["R1"] ?? 0) - 0.5) < 1e-9,
      `R1=${r.branchCurrents["R1"]}`,
    );
  }

  // ── 2. RL 直流：电感应短路（修复验证） ──
  {
    const c = [
      comp("voltage_source", 0, 0, 5),
      comp("resistor", 10, 0, 10),
      comp("inductor", 20, 0, 1e-3),
      comp("ground", 30, 0, 0),
    ];
    const r = solveCircuit(c, series(c));
    check(
      "RL 直流：电感短路稳态电流 ≈ 0.5A",
      Math.abs((r.branchCurrents["L1"] ?? 0) - 0.5) < 1e-6,
      `L1=${r.branchCurrents["L1"]}`,
    );
  }

  // ── 3. RC 充电暂态：vc(5ms) = 5(1 − e^−5) ≈ 4.966V ──
  {
    const c = [
      comp("voltage_source", 0, 0, 5),
      comp("resistor", 10, 0, 1000),
      comp("capacitor", 20, 0, 1e-6),
      comp("ground", 30, 0, 0),
    ];
    const t = runTransientAnalysis(c, series(c), { tEnd: 0.005, dt: 1e-5 });
    const vc = t.capacitorVoltages["C1"] ?? [];
    const expected = 5 * (1 - Math.exp(-5));
    check(
      "RC 暂态：起点 vc(0)=0",
      Math.abs(vc[0] ?? -1) < 1e-12,
      `vc0=${vc[0]}`,
    );
    check(
      "RC 暂态：vc(5ms) ≈ 4.966V",
      vc.length > 0 && Math.abs(vc[vc.length - 1] - expected) < 0.02,
      `vcEnd=${vc[vc.length - 1]} expected≈${expected}`,
    );
    const mono = vc.every((v, i) => i === 0 || v >= vc[i - 1] - 1e-9);
    check("RC 暂态：单调充电", mono);
  }

  // ── 4. RL 升流暂态：i(5τ) = 0.5(1 − e^−5) ≈ 0.4966A ──
  {
    const c = [
      comp("voltage_source", 0, 0, 5),
      comp("resistor", 10, 0, 10),
      comp("inductor", 20, 0, 1e-3),
      comp("ground", 30, 0, 0),
    ];
    const t = runTransientAnalysis(c, series(c), { tEnd: 5e-4, dt: 1e-6 });
    const il = t.inductorCurrents["L1"] ?? [];
    const expected = 0.5 * (1 - Math.exp(-5));
    check(
      "RL 暂态：i(5τ) ≈ 0.4966A",
      il.length > 0 && Math.abs(il[il.length - 1] - expected) < 0.005,
      `ilEnd=${il[il.length - 1]} expected≈${expected}`,
    );
  }

  // ── 5. LC 振荡：vc(t) = 5(1 − cos(ω0 t))，半周期峰值 ≈ 10V ──
  {
    const c = [
      comp("voltage_source", 0, 0, 5),
      comp("inductor", 10, 0, 1e-3),
      comp("capacitor", 20, 0, 1e-6),
      comp("ground", 30, 0, 0),
    ];
    const t = runTransientAnalysis(c, series(c), { tEnd: 1.5e-4, dt: 2e-6 });
    const vc = t.capacitorVoltages["C1"] ?? [];
    const peak = Math.max(...vc);
    check(
      "LC 振荡：半周期峰值 ≈ 10V（RK4 幅值保持）",
      Math.abs(peak - 10) < 0.15,
      `peak=${peak.toFixed(4)}`,
    );
    const omega0 = 1 / Math.sqrt(1e-3 * 1e-6);
    const halfPeriod = Math.PI / omega0; // ≈ 99.3μs
    const idx = vc.reduce((best, v, i) => (v > vc[best] ? i : best), 0);
    const tPeak = t.time[idx];
    check(
      "LC 振荡：峰值出现在 T/2 ≈ 99.3μs",
      Math.abs(tPeak - halfPeriod) < 4e-6,
      `tPeak=${(tPeak * 1e6).toFixed(1)}μs expected≈${(halfPeriod * 1e6).toFixed(1)}μs`,
    );
  }

  // ── 6. solveCircuit 自动附带暂态 ──
  {
    const c = [
      comp("voltage_source", 0, 0, 5),
      comp("resistor", 10, 0, 1000),
      comp("capacitor", 20, 0, 1e-6),
      comp("ground", 30, 0, 0),
    ];
    const r = solveCircuit(c, series(c));
    check(
      "solveCircuit 自动附带暂态波形",
      !!r.transient && (r.transient.capacitorVoltages["C1"]?.length ?? 0) > 100,
      `steps=${r.transient?.capacitorVoltages["C1"]?.length ?? 0}`,
    );
  }

  if (failures > 0) {
    console.log(`\n结果: ${failures} 项失败`);
    process.exit(1);
  }
  console.log("\n结果: 全部通过");
}

main();
