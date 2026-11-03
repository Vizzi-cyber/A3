/**
 * 3D 立体化学习空间展示区（SpaceShowcase）
 * 欢迎页（登录前）上的可切换 3D 展示模块：
 *   - 学科课程：3D 环形课程轮播（CourseCarousel3D）
 *   - 知识星云：悬浮知识空间（SpaceScene）
 *   - 数据驾驶舱：3D 数据指挥舱（NeoConsole）
 * 一次只渲染一个，用 Tab 切换，避免同时挂载多个 WebGL 场景。
 */
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import CourseCarousel3D from "./animations/CourseCarousel3D";
import SpaceScene from "./three/SpaceScene";
import NeoConsole from "./holo/NeoConsole";
import type { HoloData } from "./holo/useHoloData";

/** 3D 环形课程轮播数据 */
const CAROUSEL_ITEMS = [
  {
    icon: "💻",
    name: "C语言程序设计",
    discipline: "计算机科学与技术",
    color: "from-blue-500 to-blue-600",
    desc: "指针、位运算、数组——嵌入式开发的直接编程基础",
    kps: "16 个知识点",
  },
  {
    icon: "⚡",
    name: "电路分析基础",
    discipline: "电子信息工程",
    color: "from-orange-500 to-red-500",
    desc: "分压采样、电压波形——外围电路设计的理论支撑",
    kps: "5 个知识点 + MNA仿真",
  },
  {
    icon: "🔧",
    name: "STM32嵌入式开发",
    discipline: "计算机 × 电子信息（交叉）",
    color: "from-green-500 to-emerald-600",
    desc: "GPIO/定时器/ADC/通信接口——综合应用两门基础学科",
    kps: "14 个知识点 + 7 个实验",
  },
];

/** 数据驾驶舱演示数据（欢迎页未登录，用静态演示数据而非后端接口） */
const DEMO_DATA: HoloData = {
  weeklyHours: 6.5,
  totalHours: 128,
  masteredKps: 9,
  achievements: 7,
  favorites: 12,
  streakDays: 5,
  todayMin: 45,
  pathProgress: 42,
  pathNodes: 35,
  quizTotal: 120,
  quizCovered: 14,
  points: 2860,
  level: 12,
  topRankers: [
    { name: "林同学", score: 3240 },
    { name: "张同学", score: 2980 },
    { name: "陈同学", score: 2710 },
  ],
  tasks: [
    { title: "完成「指针」专项练习", type: "practice" },
    { title: "复习「基尔霍夫定律」", type: "review" },
    { title: "STM32 GPIO 实验", type: "experiment" },
  ],
  trend: [
    { date: "2026-08-14", value: 1.2 },
    { date: "2026-08-15", value: 0.8 },
    { date: "2026-08-16", value: 1.5 },
    { date: "2026-08-17", value: 2.1 },
    { date: "2026-08-18", value: 1.7 },
    { date: "2026-08-19", value: 2.6 },
    { date: "2026-08-20", value: 2.0 },
  ],
  graphNodes: [
    {
      kp_id: "c_var",
      name: "变量与类型",
      course: "C语言",
      difficulty: 0.3,
      status: "completed",
      mastery: 0.95,
    },
    {
      kp_id: "c_array",
      name: "数组",
      course: "C语言",
      difficulty: 0.4,
      status: "completed",
      mastery: 0.9,
    },
    {
      kp_id: "c_pointer",
      name: "指针",
      course: "C语言",
      difficulty: 0.7,
      status: "in-progress",
      mastery: 0.55,
    },
    {
      kp_id: "c_func",
      name: "函数",
      course: "C语言",
      difficulty: 0.5,
      status: "completed",
      mastery: 0.85,
    },
    {
      kp_id: "c_struct",
      name: "结构体",
      course: "C语言",
      difficulty: 0.6,
      status: "pending",
      mastery: 0.2,
    },
    {
      kp_id: "c_bit",
      name: "位运算",
      course: "C语言",
      difficulty: 0.65,
      status: "pending",
      mastery: 0.3,
    },
    {
      kp_id: "ckt_kcl",
      name: "基尔霍夫定律",
      course: "电路分析",
      difficulty: 0.5,
      status: "in-progress",
      mastery: 0.6,
    },
    {
      kp_id: "ckt_div",
      name: "分压电路",
      course: "电路分析",
      difficulty: 0.45,
      status: "completed",
      mastery: 0.88,
    },
    {
      kp_id: "ckt_opamp",
      name: "运算放大器",
      course: "电路分析",
      difficulty: 0.75,
      status: "locked",
      mastery: null,
    },
    {
      kp_id: "stm32_gpio",
      name: "GPIO",
      course: "STM32嵌入式",
      difficulty: 0.4,
      status: "in-progress",
      mastery: 0.7,
    },
    {
      kp_id: "stm32_timer",
      name: "定时器",
      course: "STM32嵌入式",
      difficulty: 0.6,
      status: "pending",
      mastery: 0.1,
    },
    {
      kp_id: "stm32_adc",
      name: "ADC采样",
      course: "STM32嵌入式",
      difficulty: 0.7,
      status: "locked",
      mastery: null,
    },
  ],
  graphEdges: [
    ["c_var", "c_array"],
    ["c_array", "c_pointer"],
    ["c_var", "c_func"],
    ["c_struct", "stm32_gpio"],
    ["c_bit", "stm32_gpio"],
    ["ckt_kcl", "ckt_div"],
    ["ckt_div", "ckt_opamp"],
    ["c_pointer", "stm32_gpio"],
    ["stm32_gpio", "stm32_timer"],
    ["stm32_timer", "stm32_adc"],
    ["ckt_div", "stm32_adc"],
  ],
};

const TABS = [
  { key: "courses", label: "学科课程", icon: "💻", hint: "3D 环形课程轮播" },
  { key: "space", label: "知识星云", icon: "🌌", hint: "悬浮知识空间" },
  { key: "console", label: "数据驾驶舱", icon: "📊", hint: "3D 数据指挥舱" },
] as const;

type TabKey = (typeof TABS)[number]["key"];

const SpaceShowcase: React.FC = () => {
  const [active, setActive] = useState<TabKey>("courses");
  const navigate = useNavigate();

  return (
    <section className="py-20 px-6 bg-gradient-to-b from-indigo-50/40 to-white">
      <div className="max-w-7xl mx-auto">
        {/* 标题 */}
        <div className="text-center mb-10">
          <div className="inline-block px-3 py-1 rounded-full bg-indigo-50 border border-indigo-100 text-indigo-600 text-xs font-medium mb-4">
            3D 沉浸体验
          </div>
          <h2 className="text-3xl md:text-5xl font-bold text-slate-900 tracking-tight">
            立体化学习空间
          </h2>
          <p className="mt-4 text-slate-500 max-w-2xl mx-auto text-lg">
            可拖拽旋转、缩放交互的三维学习界面
          </p>
        </div>

        {/* Tab 切换 */}
        <div className="flex justify-center gap-2 mb-8 flex-wrap">
          {TABS.map((t) => {
            const isActive = active === t.key;
            return (
              <button
                key={t.key}
                onClick={() => setActive(t.key)}
                className={`px-4 py-2 rounded-full text-sm font-medium border transition-all ${
                  isActive
                    ? "bg-indigo-600 text-white border-indigo-600 shadow-md"
                    : "bg-white text-slate-600 border-slate-200 hover:border-indigo-200 hover:text-indigo-600"
                }`}
              >
                <span className="mr-1.5">{t.icon}</span>
                {t.label}
              </button>
            );
          })}
        </div>

        {/* 展示区：一次只渲染一个 */}
        <div className="min-h-[480px]">
          {active === "courses" && <CourseCarousel3D items={CAROUSEL_ITEMS} />}

          {active === "space" && (
            <div className="h-[560px] rounded-2xl overflow-hidden border border-slate-200 shadow-xl">
              <SpaceScene onNavigate={() => navigate("/login")} />
            </div>
          )}

          {active === "console" && <NeoConsole data={DEMO_DATA} />}
        </div>
      </div>
    </section>
  );
};

export default SpaceShowcase;
