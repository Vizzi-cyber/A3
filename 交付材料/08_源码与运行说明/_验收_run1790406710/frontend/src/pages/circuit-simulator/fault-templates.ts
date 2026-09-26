/**
 * 故障实验模板（AIC 算法创新赛 · AI+学科交叉 亮点功能）
 * "AI+虚拟实验实训"新范式：仿真只给数值，AI 给诊断
 *
 * 每个故障实验：基于预设电路注入故障（断路/短路/错值），
 * 学生观察测量异常 → 选择故障原因 → 本地规则即时判定 + AI 详细解析
 */
import type { PresetCircuit } from "./store";

export interface FaultOption {
  label: string;
  correct: boolean;
  explanation: string; // 为什么对/为什么错（教学解析）
}

export interface FaultTemplate {
  id: string;
  name: string;
  difficulty: "入门" | "进阶";
  basedOn: string; // 基础预设电路 id（voltage-divider / rc-circuit / current-source-test）
  overrides: Record<string, number>; // 注入故障：元件原始id -> 故障值
  task: string; // 实验任务描述
  phenomenon: string; // 故障现象（学生观察到的异常）
  normalValues: string; // 正常电路的预期测量值
  options: FaultOption[]; // 诊断选项（含正确项）
  aiPrompt: string; // 发送给 AI 的故障背景描述
}

export const FAULT_TEMPLATES: FaultTemplate[] = [
  {
    id: "fault-divider-open",
    name: "分压电路 · R2 断路",
    difficulty: "入门",
    basedOn: "voltage-divider",
    overrides: { r2: 1e9 }, // 2kΩ → 1GΩ 模拟断路
    task: "5V 电压源 + 1kΩ(R1) + 2kΩ(R2) 串联分压电路。实测中间节点电压为 5V（正常应为 3.33V），请诊断电路故障。",
    phenomenon: "中间节点电压异常升高至接近 5V，R2 上无电流流过。",
    normalValues: "正常电路：中间节点 ≈ 3.33V，电流 ≈ 1.67mA",
    options: [
      {
        label: "A. R2 断路",
        correct: true,
        explanation:
          "R2 断路后回路无电流，中间节点经 R1 直接与 5V 电源相连（R1 上无电流、无压降），因此测得 5V。这是分压电路最常见的故障。",
      },
      {
        label: "B. R1 短路",
        correct: false,
        explanation:
          "R1 短路时中间节点同样接近 5V，但此时 R2 上有电流（电流 ≈ 2.5mA），可通过测量 R2 支路电流区分两种故障。",
      },
      {
        label: "C. 电压源内阻增大",
        correct: false,
        explanation:
          "电压源内阻增大主要影响带载能力，分压输出会略有下降而非升高到 5V。",
      },
      {
        label: "D. 电路正常",
        correct: false,
        explanation:
          "正常分压输出应为 3.33V，实测 5V 明显异常，说明电路存在故障。",
      },
    ],
    aiPrompt:
      "分压电路（5V + 1kΩ + 2kΩ）实测中间节点电压 5V，怀疑 R2 断路，请讲解如何用万用表测量定位此故障（测量节点电压、测电阻、电流对比法）。",
  },
  {
    id: "fault-divider-short",
    name: "分压电路 · R1 短路",
    difficulty: "入门",
    basedOn: "voltage-divider",
    overrides: { r1: 0.001 }, // 1kΩ → 0.001Ω 模拟短路
    task: "5V 电压源 + 1kΩ(R1) + 2kΩ(R2) 串联分压电路。实测中间节点电压为 5V（正常应为 3.33V），请诊断电路故障。",
    phenomenon: "中间节点电压异常升高至 5V，回路电流增大至 2.5mA。",
    normalValues: "正常电路：中间节点 ≈ 3.33V，电流 ≈ 1.67mA",
    options: [
      {
        label: "A. R1 短路",
        correct: true,
        explanation:
          "R1 短路（阻值≈0）时其压降为 0，中间节点直接与 5V 相连。回路电流变为 5V/2kΩ = 2.5mA，明显大于正常的 1.67mA。",
      },
      {
        label: "B. R2 断路",
        correct: false,
        explanation:
          "R2 断路时回路无电流，电流表读数为 0；而 R1 短路时电流增大。通过电流测量即可区分。",
      },
      {
        label: "C. R2 短路",
        correct: false,
        explanation: "R2 短路时中间节点接地，电压应接近 0V，与实测 5V 相反。",
      },
      {
        label: "D. 电压源电压升高",
        correct: false,
        explanation:
          "若仅电压源升高，分压比例不变，中间节点仍应约为电源电压的 2/3，不会达到 5V。",
      },
    ],
    aiPrompt:
      "分压电路（5V + 1kΩ + 2kΩ）实测中间节点 5V、电流 2.5mA，怀疑 R1 短路，请讲解短路故障与断路故障的判别方法（测量电流区分）。",
  },
  {
    id: "fault-current-open",
    name: "电流源电路 · R1 断路",
    difficulty: "进阶",
    basedOn: "current-source-test",
    overrides: { r1: 1e9 }, // 100Ω → 1GΩ 模拟断路
    task: "10mA 电流源 + 100Ω(R1) + 200Ω(R2) 串联电路。实测 R2 两端电压为 0V（正常应为 2V），请诊断电路故障。",
    phenomenon: "回路无电流，R2 两端电压降为 0V，电流源输出被阻断。",
    normalValues: "正常电路：R2 电压 = 10mA × 200Ω = 2V",
    options: [
      {
        label: "A. R1 断路",
        correct: true,
        explanation:
          "R1 断路使回路中断，电流源无法建立电流通路，R2 上无电流、电压为 0V。电流源开路时输出电压会异常升高（尝试维持恒流）。",
      },
      {
        label: "B. R2 短路",
        correct: false,
        explanation:
          "R2 短路时其两端电压为 0V，但回路电流仍为 10mA（流经 R1），与断路现象不同——可通过测量 R1 电压（应为 1V）区分。",
      },
      {
        label: "C. 电流源损坏",
        correct: false,
        explanation:
          "若电流源内部开路，R1、R2 上均无电流；但 R1 断路同样造成无电流。需要断开电路分别测量各元件端电压定位。",
      },
      {
        label: "D. 电路正常",
        correct: false,
        explanation:
          "正常时 R2 两端应为 2V（欧姆定律 U=IR），实测 0V 说明回路电流为零，存在断路故障。",
      },
    ],
    aiPrompt:
      "电流源电路（10mA + 100Ω + 200Ω 串联）实测 R2 电压 0V（正常 2V），怀疑 R1 断路，请讲解恒流源开路故障的特征与排查方法。",
  },
];

/** 根据故障模板找到基础预设电路（组件数据从 store 的 PRESET_CIRCUITS 读取） */
export function findBasePreset(
  fault: FaultTemplate,
  presets: PresetCircuit[],
): PresetCircuit | undefined {
  return presets.find((p) => p.id === fault.basedOn);
}
