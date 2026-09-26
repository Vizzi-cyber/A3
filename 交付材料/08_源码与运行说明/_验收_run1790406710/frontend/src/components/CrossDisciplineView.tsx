import React, { useEffect, useMemo, useState } from "react";
import {
  Select,
  Tag,
  Spin,
  Empty,
  Card,
  Checkbox,
  Button,
  message,
} from "antd";
import { ApartmentOutlined } from "@ant-design/icons";
import { knowledgeApi, pathApi, learningDataApi } from "../services/api";
import { useAppStore } from "../store";

// 跨学科综合实战项目模板（编程思维→电路建模→嵌入式实现链路落地）
const PROJECTS = [
  {
    id: "smart-fan",
    title: "智能温控风扇",
    description:
      "用 C 语言编写温度采集逻辑，设计分压采样电路，在 STM32 上实现 PWM 调速——一个项目走通三大学科全链路。",
    courses: ["C语言", "电路分析", "STM32嵌入式"],
    tasks: [
      "用 C 语言编写 ADC 采样与数据处理函数（指针传参）",
      "在仿真器中搭建热敏电阻分压采样电路并验证",
      "配置 STM32 定时器 PWM 输出控制风扇转速",
      "结合温度阈值编写调速逻辑（位运算控制寄存器）",
      "运行仿真验证：温度升高 → 占空比增大 → 转速提升",
    ],
  },
  {
    id: "led-breath",
    title: "呼吸灯与按键交互",
    description:
      "从 LED 点亮到呼吸灯效果，再到按键切换模式——循序渐进掌握 GPIO、定时器与中断的联动。",
    courses: ["C语言", "STM32嵌入式"],
    tasks: [
      "编写 GPIO 初始化代码（位运算配置寄存器）",
      "实现 LED 闪烁（延时循环 + 位操作）",
      "实现 PWM 呼吸灯效果（定时器比较值渐变）",
      "添加按键输入检测与消抖（GPIO 输入 + 延时）",
      "按键切换呼吸/闪烁双模式，验证完整交互",
    ],
  },
];

interface CourseMeta {
  course_id: string;
  name: string;
  discipline: string;
  icon: string;
  color: string;
  cross_count: number;
  core_phases?: string[];
  linked_courses: { course: string; link: string }[];
}

interface KpNode {
  kp_id: string;
  name: string;
  course: string;
  subject: string;
  prerequisites: string[];
}

const COURSE_COLORS: Record<string, string> = {
  C语言: "#1677ff",
  电路分析: "#fa541c",
  STM32嵌入式: "#52c41a",
};

const COURSE_ORDER = ["C语言", "电路分析", "STM32嵌入式"];

// 预置跨学科目标知识点（体现"编程思维→电路建模→嵌入式实现"链路）
const TARGETS = [
  { kp_id: "kp_s05", label: "定时器与PWM（STM32）" },
  { kp_id: "kp_s06", label: "ADC模数转换（STM32）" },
  { kp_id: "kp_s07", label: "DMA数据转运（STM32）" },
  { kp_id: "kp_s08", label: "UART串口通信（STM32）" },
  { kp_id: "kp_e03", label: "支路电流法（电路分析）" },
];

interface ChainResult {
  dependency_chain: string[];
  cross_discipline: {
    target_course: string;
    course_stats: Record<string, number>;
    cross_courses: string[];
    is_cross_discipline: boolean;
  };
}

const CrossDisciplineView: React.FC = () => {
  const [courses, setCourses] = useState<CourseMeta[]>([]);
  const [kps, setKps] = useState<KpNode[]>([]);
  const [target, setTarget] = useState<string>("kp_s05");
  const [chain, setChain] = useState<ChainResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [checkedTasks, setCheckedTasks] = useState<Record<string, boolean>>({});
  const [completedProjects, setCompletedProjects] = useState<
    Record<string, boolean>
  >({});
  const studentId = useAppStore((s) => s.studentId);

  const handleCompleteProject = (p: (typeof PROJECTS)[number]) => {
    const allDone = p.tasks.every((_, i) => checkedTasks[`${p.id}_${i}`]);
    if (!allDone) {
      message.warning("请先完成全部实战任务再提交");
      return;
    }
    setCompletedProjects((prev) => ({ ...prev, [p.id]: true }));
    message.success(`已完成跨学科实战项目：${p.title}`);
    // 完成度采集（试点数据分析）
    if (studentId) {
      learningDataApi
        .submitExperiment({
          student_id: studentId,
          experiment_type: "cross_project",
          action: "complete",
          detail: {
            project_id: p.id,
            title: p.title,
            courses: p.courses,
          },
        })
        .catch(() => {});
    }
  };

  useEffect(() => {
    pathApi
      .getCourses()
      .then((res) => setCourses(res.data.data || []))
      .catch(() => {});
    knowledgeApi
      .list()
      .then((res) => setKps(res.data.data || []))
      .catch(() => {});
  }, []);

  useEffect(() => {
    if (!target) return;
    setLoading(true);
    setChain(null);
    pathApi
      .crossDiscipline(target)
      .then((res) => setChain(res.data.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [target]);

  // 计算拓扑层级布局
  const dag = useMemo(() => {
    if (!chain || kps.length === 0) return null;
    const kpMap = new Map(kps.map((k) => [k.kp_id, k]));
    const chainSet = new Set(chain.dependency_chain);

    // 节点级别 = 最长前置链长度
    const levelMap: Record<string, number> = {};
    const calcLevel = (id: string): number => {
      if (levelMap[id] !== undefined) return levelMap[id];
      const kp = kpMap.get(id);
      if (!kp) {
        levelMap[id] = 0;
        return 0;
      }
      const prereqs = (kp.prerequisites || []).filter((p) => chainSet.has(p));
      const lv =
        prereqs.length === 0
          ? 0
          : Math.max(...prereqs.map((p) => calcLevel(p))) + 1;
      levelMap[id] = lv;
      return lv;
    };
    chain.dependency_chain.forEach(calcLevel);

    // 按层级分组
    const levels: { id: string; kp: KpNode; level: number }[][] = [];
    for (const id of chain.dependency_chain) {
      const kp = kpMap.get(id);
      if (!kp) continue;
      const lv = levelMap[id];
      if (!levels[lv]) levels[lv] = [];
      levels[lv].push({ id, kp, level: lv });
    }
    return { levels, kpMap };
  }, [chain, kps]);

  const NODE_W = 150;
  const NODE_H = 46;
  const GAP_X = 80;
  const GAP_Y = 24;
  const PAD = 30;

  const svgW = useMemo(() => {
    if (!dag || dag.levels.length === 0) return 0;
    return (
      PAD * 2 + dag.levels.length * NODE_W + (dag.levels.length - 1) * GAP_X
    );
  }, [dag]);

  const svgH = useMemo(() => {
    if (!dag || dag.levels.length === 0) return 0;
    const maxNodes = Math.max(...dag.levels.map((l) => l.length));
    return PAD * 2 + maxNodes * NODE_H + (maxNodes - 1) * GAP_Y;
  }, [dag]);

  const crossTotal = chain?.cross_discipline?.course_stats || {};
  const chainCourses = chain?.cross_discipline?.cross_courses || [];

  return (
    <div className="space-y-4">
      {/* 学科卡片 */}
      <div className="grid grid-cols-3 gap-3">
        {courses.map((c) => (
          <div
            key={c.course_id}
            className="rounded-lg border p-3"
            style={{ borderColor: c.color + "40" }}
          >
            <div className="flex items-center gap-2">
              <span
                className="w-8 h-8 rounded-lg flex items-center justify-center text-base"
                style={{ backgroundColor: c.color + "1a" }}
              >
                {c.icon}
              </span>
              <div>
                <div className="font-medium text-gray-800 text-sm">
                  {c.name}
                </div>
                <div className="text-[11px] text-gray-500">{c.discipline}</div>
              </div>
            </div>
            <div className="mt-2 flex items-center gap-1.5">
              <Tag
                color={c.cross_count > 0 ? "green" : "default"}
                style={{ fontSize: 11 }}
              >
                跨课程关联 {c.cross_count}
              </Tag>
              <span className="text-[11px] text-gray-400">
                {c.core_phases?.join(" / ") || ""}
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* 目标选择 */}
      <div className="flex items-center gap-3">
        <span className="text-sm text-gray-600 shrink-0">
          选择跨学科学习目标：
        </span>
        <Select
          value={target}
          onChange={setTarget}
          options={TARGETS.map((t) => ({ value: t.kp_id, label: t.label }))}
          style={{ width: 260 }}
        />
        {chain && (
          <Tag color="purple">
            依赖链跨越 {chainCourses.length} 门课：{chainCourses.join(" → ")}
          </Tag>
        )}
      </div>

      {/* DAG 图 */}
      {loading && (
        <div className="flex justify-center py-16">
          <Spin />
        </div>
      )}
      {!loading && !dag && (
        <Empty description="暂无跨学科路径数据" className="py-16" />
      )}
      {!loading && dag && dag.levels.length > 0 && (
        <div className="rounded-lg border border-gray-200 p-4 bg-white">
          <div className="flex items-center gap-2 mb-3">
            <ApartmentOutlined className="text-indigo-500" />
            <span className="text-sm font-medium text-gray-700">
              跨学科知识依赖图（按拓扑层级）
            </span>
            <div className="ml-auto flex gap-3">
              {COURSE_ORDER.map((c) => (
                <span
                  key={c}
                  className="flex items-center gap-1 text-[11px] text-gray-500"
                >
                  <span
                    className="w-2.5 h-2.5 rounded-full inline-block"
                    style={{ backgroundColor: COURSE_COLORS[c] }}
                  />
                  {c}
                </span>
              ))}
            </div>
          </div>
          <div className="overflow-x-auto">
            <svg width={svgW} height={svgH}>
              {/* 边 */}
              {dag.levels.flatMap((level, li) =>
                level.map(({ id, kp }) => {
                  const x = PAD + li * (NODE_W + GAP_X);
                  const y =
                    PAD +
                    level.indexOf({ id, kp, level: li }) * (NODE_H + GAP_Y);
                  return (kp.prerequisites || [])
                    .filter((p) => dag.kpMap.has(p))
                    .map((p) => {
                      const pNode = dag.kpMap.get(p)!;
                      // 找前置节点位置
                      for (let pl = 0; pl < dag.levels.length; pl++) {
                        const idx = dag.levels[pl].findIndex((n) => n.id === p);
                        if (idx >= 0) {
                          const px = PAD + pl * (NODE_W + GAP_X) + NODE_W;
                          const py = PAD + idx * (NODE_H + GAP_Y) + NODE_H / 2;
                          return (
                            <path
                              key={`${p}-${id}`}
                              d={`M ${px} ${py} C ${px + 24} ${py}, ${x - 24} ${y + NODE_H / 2}, ${x} ${y + NODE_H / 2}`}
                              fill="none"
                              stroke="#d1d5db"
                              strokeWidth="1.2"
                              opacity="0.8"
                            />
                          );
                        }
                      }
                      return null;
                    });
                }),
              )}
              {/* 节点 */}
              {dag.levels.flatMap((level, li) =>
                level.map(({ id, kp }, ni) => {
                  const x = PAD + li * (NODE_W + GAP_X);
                  const y = PAD + ni * (NODE_H + GAP_Y);
                  const color = COURSE_COLORS[kp.course] || "#999";
                  return (
                    <g key={id}>
                      <rect
                        x={x}
                        y={y}
                        width={NODE_W}
                        height={NODE_H}
                        rx={8}
                        fill={color + "0d"}
                        stroke={color}
                        strokeWidth="1.5"
                      />
                      <text
                        x={x + NODE_W / 2}
                        y={y + 19}
                        textAnchor="middle"
                        fontSize="12"
                        fontWeight="500"
                        fill="#374151"
                      >
                        {kp.name.length > 12
                          ? kp.name.slice(0, 12) + "…"
                          : kp.name}
                      </text>
                      <text
                        x={x + NODE_W / 2}
                        y={y + 35}
                        textAnchor="middle"
                        fontSize="10"
                        fill={color}
                      >
                        {kp.course}
                      </text>
                    </g>
                  );
                }),
              )}
            </svg>
          </div>
          {/* 课程统计 */}
          <div className="mt-3 flex items-center gap-2 text-xs text-gray-500">
            知识分布：
            {COURSE_ORDER.filter((c) => crossTotal[c]).map((c) => (
              <span key={c} className="flex items-center gap-1">
                <span
                  className="w-2 h-2 rounded-full inline-block"
                  style={{ backgroundColor: COURSE_COLORS[c] }}
                />
                {c} × {crossTotal[c]}
              </span>
            ))}
            <span className="text-gray-400 ml-auto">
              目标知识点所在课程：{chain?.cross_discipline?.target_course}
            </span>
          </div>
        </div>
      )}

      {/* 跨学科学习链路说明 */}
      <Card size="small" title="跨学科学习链路设计">
        <div className="text-sm text-gray-600 leading-relaxed">
          <p className="mb-2">
            <b>编程思维 → 电路建模 → 嵌入式实现</b>
          </p>
          <p className="text-xs text-gray-500 mb-1">
            ① C语言（指针/位运算/数组）为嵌入式开发提供直接编程基础；
          </p>
          <p className="text-xs text-gray-500 mb-1">
            ② 电路分析（分压采样/电压波形）为外围电路设计提供理论支撑；
          </p>
          <p className="text-xs text-gray-500">
            ③ STM32
            综合应用两门基础学科，构成"新工科计算机×电子信息"跨学科学习闭环。
          </p>
        </div>
      </Card>

      {/* 跨学科综合实战项目（AIC 创新点：链路落地实践） */}
      <Card size="small" title="🧭 跨学科综合实战项目">
        <div className="space-y-4">
          {PROJECTS.map((p) => {
            const isDone = completedProjects[p.id];
            return (
              <div
                key={p.id}
                className={`rounded-lg border p-4 ${
                  isDone ? "border-green-200 bg-green-50/40" : "border-gray-200"
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="font-medium text-gray-800">{p.title}</div>
                  <div className="flex gap-1">
                    {p.courses.map((c) => (
                      <Tag
                        key={c}
                        style={{ fontSize: 11 }}
                        color={
                          c === "C语言"
                            ? "blue"
                            : c === "电路分析"
                              ? "orange"
                              : "green"
                        }
                      >
                        {c}
                      </Tag>
                    ))}
                  </div>
                </div>
                <p className="text-sm text-gray-600 mb-3">{p.description}</p>
                <div className="space-y-1.5 mb-3">
                  {p.tasks.map((t, i) => (
                    <div
                      key={i}
                      className="flex items-center gap-2 text-sm text-gray-600 bg-white rounded-lg p-2 border border-gray-100"
                    >
                      <Checkbox
                        checked={!!checkedTasks[`${p.id}_${i}`]}
                        onChange={(e) =>
                          setCheckedTasks((prev) => ({
                            ...prev,
                            [`${p.id}_${i}`]: e.target.checked,
                          }))
                        }
                      />
                      <span>{t}</span>
                    </div>
                  ))}
                </div>
                <Button
                  size="small"
                  type="primary"
                  disabled={isDone}
                  onClick={() => handleCompleteProject(p)}
                >
                  {isDone ? "已完成 ✓" : "完成实战项目"}
                </Button>
              </div>
            );
          })}
        </div>
      </Card>
    </div>
  );
};

export default CrossDisciplineView;
