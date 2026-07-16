import React, { useState, useRef, useEffect, useCallback } from "react";
import { Button, Select, Slider, Tag } from "antd";
import {
  PlayCircleOutlined,
  PauseCircleOutlined,
  StepForwardOutlined,
  ReloadOutlined,
} from "@ant-design/icons";

interface AlgoStep {
  array: number[];
  comparing: number[];
  swapping: number[];
  sorted: number[];
  pivot?: number;
  description: string;
  line: number;
}

interface AlgorithmVisualizerProps {
  algorithm?: string;
}

/** 伪代码定义 */
const PSEUDO_CODE: Record<string, string[]> = {
  bubble: [
    "function bubbleSort(arr):",
    "  n = arr.length",
    "  for i = 0 to n-1:",
    "    for j = 0 to n-i-2:",
    "      if arr[j] > arr[j+1]:",
    "        swap(arr[j], arr[j+1])",
    "  return arr",
  ],
  quick: [
    "function quickSort(arr, low, high):",
    "  if low < high:",
    "    pivot = partition(arr, low, high)",
    "    quickSort(arr, low, pivot-1)",
    "    quickSort(arr, pivot+1, high)",
    "function partition(arr, low, high):",
    "  pivot = arr[high]",
    "  i = low - 1",
    "  for j = low to high-1:",
    "    if arr[j] <= pivot:",
    "      i++; swap(arr[i], arr[j])",
    "  swap(arr[i+1], arr[high])",
    "  return i + 1",
  ],
  insertion: [
    "function insertionSort(arr):",
    "  for i = 1 to n-1:",
    "    key = arr[i]",
    "    j = i - 1",
    "    while j >= 0 and arr[j] > key:",
    "      arr[j+1] = arr[j]",
    "      j--",
    "    arr[j+1] = key",
    "  return arr",
  ],
  selection: [
    "function selectionSort(arr):",
    "  for i = 0 to n-1:",
    "    min_idx = i",
    "    for j = i+1 to n:",
    "      if arr[j] < arr[min_idx]:",
    "        min_idx = j",
    "    swap(arr[i], arr[min_idx])",
    "  return arr",
  ],
};

/** 冒泡排序步骤生成 */
function generateBubbleSteps(arr: number[]): AlgoStep[] {
  const steps: AlgoStep[] = [];
  const a = [...arr];
  const n = a.length;
  const sorted: number[] = [];

  steps.push({
    array: [...a],
    comparing: [],
    swapping: [],
    sorted: [...sorted],
    description: "开始冒泡排序",
    line: 0,
  });

  for (let i = 0; i < n - 1; i++) {
    for (let j = 0; j < n - i - 1; j++) {
      steps.push({
        array: [...a],
        comparing: [j, j + 1],
        swapping: [],
        sorted: [...sorted],
        description: `比较 arr[${j}]=${a[j]} 和 arr[${j + 1}]=${a[j + 1]}`,
        line: 4,
      });

      if (a[j] > a[j + 1]) {
        [a[j], a[j + 1]] = [a[j + 1], a[j]];
        steps.push({
          array: [...a],
          comparing: [],
          swapping: [j, j + 1],
          sorted: [...sorted],
          description: `交换 ${a[j + 1]} 和 ${a[j]}`,
          line: 5,
        });
      }
    }
    sorted.push(n - 1 - i);
    steps.push({
      array: [...a],
      comparing: [],
      swapping: [],
      sorted: [...sorted],
      description: `第 ${i + 1} 轮完成，${a[n - 1 - i]} 已就位`,
      line: 2,
    });
  }
  sorted.push(0);
  steps.push({
    array: [...a],
    comparing: [],
    swapping: [],
    sorted: Array.from({ length: n }, (_, i) => i),
    description: "排序完成！",
    line: 6,
  });

  return steps;
}

/** 快速排序步骤生成 */
function generateQuickSteps(arr: number[]): AlgoStep[] {
  const steps: AlgoStep[] = [];
  const a = [...arr];
  const n = a.length;
  const sorted: number[] = [];

  steps.push({
    array: [...a],
    comparing: [],
    swapping: [],
    sorted: [],
    description: "开始快速排序",
    line: 0,
  });

  function quickSort(low: number, high: number) {
    if (low < high) {
      const pivotIdx = partition(low, high);
      quickSort(low, pivotIdx - 1);
      quickSort(pivotIdx + 1, high);
    } else if (low === high) {
      sorted.push(low);
    }
  }

  function partition(low: number, high: number): number {
    const pivot = a[high];
    steps.push({
      array: [...a],
      comparing: [],
      swapping: [],
      sorted: [...sorted],
      pivot: high,
      description: `选择 pivot = ${pivot} (index ${high})`,
      line: 6,
    });

    let i = low - 1;
    for (let j = low; j < high; j++) {
      steps.push({
        array: [...a],
        comparing: [j, high],
        swapping: [],
        sorted: [...sorted],
        pivot: high,
        description: `比较 arr[${j}]=${a[j]} 与 pivot=${pivot}`,
        line: 9,
      });

      if (a[j] <= pivot) {
        i++;
        if (i !== j) {
          [a[i], a[j]] = [a[j], a[i]];
          steps.push({
            array: [...a],
            comparing: [],
            swapping: [i, j],
            sorted: [...sorted],
            pivot: high,
            description: `交换 arr[${i}] 和 arr[${j}]`,
            line: 10,
          });
        }
      }
    }

    [a[i + 1], a[high]] = [a[high], a[i + 1]];
    sorted.push(i + 1);
    steps.push({
      array: [...a],
      comparing: [],
      swapping: [i + 1, high],
      sorted: [...sorted],
      description: `pivot ${pivot} 放到位置 ${i + 1}`,
      line: 11,
    });

    return i + 1;
  }

  quickSort(0, n - 1);
  steps.push({
    array: [...a],
    comparing: [],
    swapping: [],
    sorted: Array.from({ length: n }, (_, i) => i),
    description: "快速排序完成！",
    line: 4,
  });

  return steps;
}

/** 插入排序步骤生成 */
function generateInsertionSteps(arr: number[]): AlgoStep[] {
  const steps: AlgoStep[] = [];
  const a = [...arr];
  const n = a.length;
  const sorted: number[] = [0];

  steps.push({
    array: [...a],
    comparing: [],
    swapping: [],
    sorted: [...sorted],
    description: "开始插入排序",
    line: 0,
  });

  for (let i = 1; i < n; i++) {
    const key = a[i];
    let j = i - 1;

    steps.push({
      array: [...a],
      comparing: [i],
      swapping: [],
      sorted: [...sorted],
      description: `取出 key = ${key}，向左寻找插入位置`,
      line: 2,
    });

    while (j >= 0 && a[j] > key) {
      steps.push({
        array: [...a],
        comparing: [j, j + 1],
        swapping: [],
        sorted: [...sorted],
        description: `arr[${j}]=${a[j]} > ${key}，右移`,
        line: 4,
      });
      a[j + 1] = a[j];
      j--;
    }
    a[j + 1] = key;
    sorted.push(i);
    steps.push({
      array: [...a],
      comparing: [],
      swapping: [j + 1],
      sorted: [...sorted],
      description: `${key} 插入到位置 ${j + 1}`,
      line: 7,
    });
  }

  steps.push({
    array: [...a],
    comparing: [],
    swapping: [],
    sorted: Array.from({ length: n }, (_, i) => i),
    description: "插入排序完成！",
    line: 8,
  });

  return steps;
}

/** 选择排序步骤生成 */
function generateSelectionSteps(arr: number[]): AlgoStep[] {
  const steps: AlgoStep[] = [];
  const a = [...arr];
  const n = a.length;
  const sorted: number[] = [];

  steps.push({
    array: [...a],
    comparing: [],
    swapping: [],
    sorted: [],
    description: "开始选择排序",
    line: 0,
  });

  for (let i = 0; i < n - 1; i++) {
    let minIdx = i;
    steps.push({
      array: [...a],
      comparing: [i],
      swapping: [],
      sorted: [...sorted],
      description: `从位置 ${i} 开始寻找最小值，当前最小 = ${a[i]}`,
      line: 2,
    });

    for (let j = i + 1; j < n; j++) {
      steps.push({
        array: [...a],
        comparing: [minIdx, j],
        swapping: [],
        sorted: [...sorted],
        description: `比较 arr[${j}]=${a[j]} 与当前最小 ${a[minIdx]}`,
        line: 4,
      });
      if (a[j] < a[minIdx]) {
        minIdx = j;
      }
    }

    if (minIdx !== i) {
      [a[i], a[minIdx]] = [a[minIdx], a[i]];
      steps.push({
        array: [...a],
        comparing: [],
        swapping: [i, minIdx],
        sorted: [...sorted],
        description: `交换 arr[${i}] 和 arr[${minIdx}]`,
        line: 6,
      });
    }
    sorted.push(i);
  }
  sorted.push(n - 1);

  steps.push({
    array: [...a],
    comparing: [],
    swapping: [],
    sorted: Array.from({ length: n }, (_, i) => i),
    description: "选择排序完成！",
    line: 7,
  });

  return steps;
}

const ALGO_MAP: Record<
  string,
  { name: string; generate: (_arr: number[]) => AlgoStep[] }
> = {
  bubble: { name: "冒泡排序", generate: generateBubbleSteps },
  quick: { name: "快速排序", generate: generateQuickSteps },
  insertion: { name: "插入排序", generate: generateInsertionSteps },
  selection: { name: "选择排序", generate: generateSelectionSteps },
};

/** 生成随机数组 */
function randomArray(size: number = 12): number[] {
  return Array.from(
    { length: size },
    () => Math.floor(Math.random() * 90) + 10,
  );
}

const AlgorithmVisualizer: React.FC<AlgorithmVisualizerProps> = ({
  algorithm: defaultAlgo = "bubble",
}) => {
  const [algo, setAlgo] = useState(defaultAlgo);
  const [array, setArray] = useState<number[]>(() => randomArray());
  const [steps, setSteps] = useState<AlgoStep[]>([]);
  const [stepIdx, setStepIdx] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [speed, setSpeed] = useState(500);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // 生成步骤
  const generateSteps = useCallback(() => {
    const gen = ALGO_MAP[algo]?.generate;
    if (gen) {
      setSteps(gen(array));
      setStepIdx(0);
      setPlaying(false);
    }
  }, [algo, array]);

  useEffect(() => {
    generateSteps();
  }, [generateSteps]);

  // 绘制
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || steps.length === 0) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const step = steps[stepIdx] || steps[0];
    const { array: arr, comparing, swapping, sorted, pivot } = step;

    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    ctx.scale(dpr, dpr);

    const w = rect.width;
    const h = rect.height;
    const barW = (w - 40) / arr.length - 4;
    const maxVal = Math.max(...arr);

    ctx.clearRect(0, 0, w, h);

    // 绘制柱状图
    arr.forEach((val, i) => {
      const barH = (val / maxVal) * (h - 60);
      const x = 20 + i * (barW + 4);
      const y = h - 30 - barH;

      let color = "#6366f1"; // 默认 indigo
      if (sorted.includes(i)) color = "#10b981"; // 已排序 emerald
      if (comparing.includes(i)) color = "#f59e0b"; // 比较中 amber
      if (swapping.includes(i)) color = "#ef4444"; // 交换中 red
      if (pivot === i) color = "#8b5cf6"; // pivot purple

      // 柱子
      ctx.fillStyle = color;
      ctx.beginPath();
      ctx.roundRect(x, y, barW, barH, [4, 4, 0, 0]);
      ctx.fill();

      // 数值
      ctx.fillStyle = "#64748b";
      ctx.font = "11px monospace";
      ctx.textAlign = "center";
      ctx.fillText(String(val), x + barW / 2, h - 12);
    });
  }, [stepIdx, steps]);

  // 播放控制
  useEffect(() => {
    if (playing && stepIdx < steps.length - 1) {
      timerRef.current = setInterval(() => {
        setStepIdx((prev) => {
          if (prev >= steps.length - 1) {
            setPlaying(false);
            return prev;
          }
          return prev + 1;
        });
      }, speed);
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [playing, speed, steps.length, stepIdx]);

  const handlePlay = () => {
    if (stepIdx >= steps.length - 1) {
      setStepIdx(0);
    }
    setPlaying(true);
  };

  const handlePause = () => setPlaying(false);

  const handleStep = () => {
    setPlaying(false);
    if (stepIdx < steps.length - 1) {
      setStepIdx((prev) => prev + 1);
    }
  };

  const handleReset = () => {
    setPlaying(false);
    setStepIdx(0);
  };

  const handleNewArray = () => {
    setPlaying(false);
    setArray(randomArray());
  };

  const currentStep = steps[stepIdx];
  const pseudoCode = PSEUDO_CODE[algo] || [];

  return (
    <div className="space-y-4">
      {/* 控制栏 */}
      <div className="flex items-center gap-3 flex-wrap">
        <Select
          value={algo}
          onChange={(v) => {
            setAlgo(v);
            setPlaying(false);
          }}
          style={{ width: 140 }}
          options={Object.entries(ALGO_MAP).map(([k, v]) => ({
            label: v.name,
            value: k,
          }))}
        />
        <Button onClick={handleNewArray} icon={<ReloadOutlined />}>
          新数组
        </Button>
        <div className="flex items-center gap-1">
          {playing ? (
            <Button
              type="primary"
              icon={<PauseCircleOutlined />}
              onClick={handlePause}
              className="bg-primary"
            />
          ) : (
            <Button
              type="primary"
              icon={<PlayCircleOutlined />}
              onClick={handlePlay}
              className="bg-primary"
            />
          )}
          <Button icon={<StepForwardOutlined />} onClick={handleStep} />
          <Button icon={<ReloadOutlined />} onClick={handleReset} />
        </div>
        <div className="flex items-center gap-2 ml-2">
          <span className="text-xs text-slate-400">速度</span>
          <Slider
            min={100}
            max={1500}
            step={100}
            value={speed}
            onChange={setSpeed}
            style={{ width: 100 }}
            tooltip={{ formatter: (v) => `${v}ms` }}
          />
        </div>
        <Tag className="rounded-full border-0 bg-slate-50 text-slate-600 ml-auto">
          步骤 {stepIdx + 1} / {steps.length}
        </Tag>
      </div>

      {/* 可视化区域 + 伪代码（上下排列） */}
      <div className="flex flex-col gap-4">
        {/* Canvas */}
        <div>
          <div className="bg-white rounded-xl border border-slate-100 shadow-card p-3">
            <canvas
              ref={canvasRef}
              className="w-full"
              style={{ height: 280 }}
            />
            {/* 描述 */}
            {currentStep && (
              <div className="mt-2 text-center text-sm text-slate-600 font-medium">
                {currentStep.description}
              </div>
            )}
          </div>
        </div>

        {/* 伪代码 */}
        <div>
          <div className="bg-slate-900 rounded-xl p-4">
            <div className="text-xs text-slate-400 mb-2 font-mono">伪代码</div>
            <pre className="text-xs leading-6 font-mono whitespace-pre-wrap break-words overflow-auto">
              {pseudoCode.map((line, idx) => (
                <div
                  key={idx}
                  className={`px-2 py-0.5 rounded transition-colors ${
                    currentStep?.line === idx
                      ? "bg-indigo-500/30 text-indigo-300"
                      : "text-slate-400"
                  }`}
                >
                  <span className="text-slate-600 mr-2 select-none">
                    {idx + 1}
                  </span>
                  {line}
                </div>
              ))}
            </pre>
          </div>
        </div>
      </div>

      {/* 图例 */}
      <div className="flex justify-center gap-4 text-xs text-slate-400">
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 rounded bg-indigo-500 inline-block" /> 默认
        </span>
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 rounded bg-amber-500 inline-block" /> 比较中
        </span>
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 rounded bg-red-500 inline-block" /> 交换中
        </span>
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 rounded bg-emerald-500 inline-block" />{" "}
          已排序
        </span>
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 rounded bg-purple-500 inline-block" /> Pivot
        </span>
      </div>
    </div>
  );
};

export default AlgorithmVisualizer;
