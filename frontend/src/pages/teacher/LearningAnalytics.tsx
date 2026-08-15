/**
 * 学情分析数据大屏（LearningAnalytics）
 * 深色科技风数据可视化大屏（与数据指挥舱风格统一）：
 *   - 班级总览统计（学生/测验/平均分/通过率/覆盖知识点）
 *   - 知识点掌握度 3D 柱状图（ECharts-GL Bar3D）
 *   - 学习趋势 + 线性回归预测（未来 7 天）折线图
 *   - 分数段分布 + 班级对比
 *   - 学生 × 知识点掌握热力图
 * 后端：/api/v1/analytics/dashboard（聚合 + 预测算法）
 */
import React, { useEffect, useRef } from "react";
import * as echarts from "echarts";
import "echarts-gl";
import { Typography, Select, Empty } from "antd";
import api from "../../services/api";

/* ---------- ECharts 通用封装 ---------- */
function useECharts(option: any | null, dark: boolean) {
  const ref = useRef<HTMLDivElement>(null);
  const chartRef = useRef<echarts.ECharts | null>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const chart = echarts.init(el, dark ? "dark" : undefined);
    chartRef.current = chart;
    const onResize = () => chart.resize();
    window.addEventListener("resize", onResize);
    return () => {
      window.removeEventListener("resize", onResize);
      chart.dispose();
      chartRef.current = null;
    };
  }, [dark]);

  useEffect(() => {
    if (option && chartRef.current) {
      chartRef.current.setOption(option, true);
    }
  }, [option]);

  return ref;
}

const DARK_TEXT = "#94a3b8";
const DARK_GRID = "rgba(148,163,184,0.15)";
const ACCENTS = ["#6366f1", "#22d3ee", "#34d399", "#f59e0b", "#f87171", "#a78bfa"];

interface AnalyticsData {
  empty?: boolean;
  message?: string;
  overview?: {
    students: number; quizzes: number; avg_score: number;
    pass_rate: number; kps_covered: number;
  };
  kp_mastery?: { kp: string; mastery: number }[];
  score_dist?: { range: string; count: number }[];
  trend?: { days: string[]; values: number[]; forecast: number[]; smoothed: number[] };
  class_compare?: { class: string; avg: number; count: number }[];
  heatmap?: { students: string[]; kps: string[]; data: { student: string; values: (number | null)[] }[] };
}

/* ---------- 图表组件 ---------- */
const StatCard: React.FC<{ label: string; value: React.ReactNode; accent: string }> = ({ label, value, accent }) => (
  <div className="rounded-xl p-4 border" style={{ background: "rgba(13,18,38,0.7)", borderColor: "rgba(148,163,184,0.15)" }}>
    <div className="text-[11px]" style={{ color: DARK_TEXT }}>{label}</div>
    <div className="text-2xl font-bold mt-1" style={{ color: accent, textShadow: `0 0 18px ${accent}55` }}>{value}</div>
  </div>
);

const ChartPanel: React.FC<{ title: string; children: React.ReactNode; height?: number }> = ({ title, children, height = 280 }) => (
  <div className="rounded-xl p-4 border" style={{ background: "rgba(13,18,38,0.7)", borderColor: "rgba(148,163,184,0.15)", height: height + 46 }}>
    <div className="text-xs font-semibold mb-2" style={{ color: "#cbd5e1" }}>{title}</div>
    <div style={{ height }}>{children}</div>
  </div>
);

/* ---------- 主组件 ---------- */
const LearningAnalytics: React.FC = () => {
  const [data, setData] = React.useState<AnalyticsData | null>(null);
  const [classId, setClassId] = React.useState<string | undefined>();
  const [classes, setClasses] = React.useState<{ class_id: string; name?: string }[]>([]);

  useEffect(() => {
    api.get("/teacher/classes").then((r) => {
      const d = r.data?.data ?? r.data ?? [];
      setClasses(Array.isArray(d) ? d : []);
    }).catch(() => {});
  }, []);

  useEffect(() => {
    api.get("/analytics/dashboard", { params: classId ? { class_id: classId } : {} })
      .then((r) => setData(r.data?.data ?? null))
      .catch(() => setData({ empty: true, message: "加载失败" }));
  }, [classId]);

  // ---- ECharts options（深色科技风） ----
  const masteryOption: any = data?.kp_mastery?.length ? {
    backgroundColor: "transparent",
    tooltip: { trigger: "axis" },
    grid3D: {
      boxWidth: 90, boxDepth: 60, boxHeight: 70,
      viewControl: { alpha: 22, beta: 30, autoRotate: true, autoRotateSpeed: 4 },
      light: { main: { intensity: 1.1 }, ambient: { intensity: 0.5 } },
    },
    xAxis3D: { type: "category", data: (data.kp_mastery ?? []).map((k) => k.kp.replace(/^kp_/, "").slice(0, 8)), axisLabel: { color: DARK_TEXT, fontSize: 10 } },
    yAxis3D: { type: "category", data: ["掌握度"], axisLabel: { color: DARK_TEXT } },
    zAxis3D: { type: "value", name: "%", axisLabel: { color: DARK_TEXT } },
    series: [{
      type: "bar3D",
      data: (data.kp_mastery ?? []).map((k, i) => [i, 0, k.mastery]),
      shading: "lambert",
      itemStyle: { color: (p: any) => ACCENTS[p.dataIndex % ACCENTS.length] },
      emphasis: { label: { show: true, formatter: (p: any) => `${p.value[2]}%`, color: "#fff" } },
    }],
  } : null;

  const trendOption: any = data?.trend?.values?.length ? (() => {
    const t = data.trend!;
    const days = [...t.days];
    const nextDays = Array.from({ length: t.forecast.length }, (_, i) => `+${i + 1}天`);
    return {
      backgroundColor: "transparent",
      tooltip: { trigger: "axis" },
      legend: { data: ["实际", "平滑", "预测"], textStyle: { color: DARK_TEXT }, top: 0 },
      grid: { left: 40, right: 20, top: 30, bottom: 30 },
      xAxis: { type: "category", data: [...days, ...nextDays], axisLabel: { color: DARK_TEXT, fontSize: 10 } },
      yAxis: { type: "value", name: "均分", axisLabel: { color: DARK_TEXT }, splitLine: { lineStyle: { color: DARK_GRID } } },
      series: [
        { name: "实际", type: "line", data: t.values, smooth: true, symbolSize: 6, itemStyle: { color: "#22d3ee" }, lineStyle: { color: "#22d3ee", width: 2 }, areaStyle: { color: "rgba(34,211,238,0.12)" } },
        { name: "平滑", type: "line", data: [...t.smoothed, ...Array(nextDays.length).fill(null)], lineStyle: { color: "#a78bfa", width: 1.5, type: "dashed" }, symbol: "none" },
        { name: "预测", type: "line", data: [...Array(t.values.length - 1).fill(null), ...t.forecast], lineStyle: { color: "#f59e0b", width: 2.5, type: "solid" }, symbol: "circle", symbolSize: 5, itemStyle: { color: "#f59e0b" } },
      ],
    };
  })() : null;

  const distOption: any = data?.score_dist?.length ? {
    backgroundColor: "transparent",
    tooltip: { trigger: "axis" },
    grid: { left: 36, right: 16, top: 16, bottom: 28 },
    xAxis: { type: "category", data: (data.score_dist ?? []).map((d) => d.range), axisLabel: { color: DARK_TEXT } },
    yAxis: { type: "value", axisLabel: { color: DARK_TEXT }, splitLine: { lineStyle: { color: DARK_GRID } } },
    series: [{
      type: "bar", data: (data.score_dist ?? []).map((d) => d.count), barWidth: 22,
      itemStyle: { color: { type: "linear", x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: "#6366f1" }, { offset: 1, color: "#1e2a5a" }] }, borderRadius: [4, 4, 0, 0] },
    }],
  } : null;

  const classOption: any = data?.class_compare?.length ? {
    backgroundColor: "transparent",
    tooltip: { trigger: "axis" },
    grid: { left: 36, right: 16, top: 16, bottom: 28 },
    xAxis: { type: "category", data: (data.class_compare ?? []).map((c) => c.class), axisLabel: { color: DARK_TEXT } },
    yAxis: { type: "value", name: "均分", axisLabel: { color: DARK_TEXT }, splitLine: { lineStyle: { color: DARK_GRID } } },
    series: [{
      type: "bar", data: (data.class_compare ?? []).map((c) => c.avg), barWidth: 30,
      itemStyle: { color: { type: "linear", x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: "#34d399" }, { offset: 1, color: "#065f46" }] }, borderRadius: [4, 4, 0, 0] },
      label: { show: true, position: "top", color: "#cbd5e1", formatter: "{c}" },
    }],
  } : null;

  const heatOption: any = data?.heatmap?.data?.length ? (() => {
    const h = data.heatmap!;
    const cells: [number, number, number][] = [];
    h.data.forEach((row, i) => {
      row.values.forEach((v, j) => {
        if (v != null) cells.push([j, i, v]);
      });
    });
    return {
      backgroundColor: "transparent",
      tooltip: { formatter: (p: any) => `${h.kps[p.value[0]]}<br/>${h.students[p.value[1]]}: ${p.value[2]} 分` },
      grid: { left: 90, right: 20, top: 20, bottom: 60 },
      xAxis: { type: "category", data: h.kps.map((k) => k.replace(/^kp_/, "")), axisLabel: { color: DARK_TEXT, fontSize: 10 } },
      yAxis: { type: "category", data: h.students, axisLabel: { color: DARK_TEXT, fontSize: 10 } },
      visualMap: { min: 0, max: 100, calculable: true, orient: "horizontal", left: "center", bottom: 0, textStyle: { color: DARK_TEXT }, inRange: { color: ["#1e1b4b", "#6366f1", "#22d3ee", "#34d399"] } },
      series: [{ type: "heatmap", data: cells, label: { show: true, color: "#e2e8f0", fontSize: 9 } }],
    };
  })() : null;

  const masteryRef = useECharts(masteryOption, true);
  const trendRef = useECharts(trendOption, true);
  const distRef = useECharts(distOption, true);
  const classRef = useECharts(classOption, true);
  const heatRef = useECharts(heatOption, true);

  if (data?.empty) {
    return (
      <div className="rounded-2xl p-10 flex justify-center items-center" style={{ minHeight: 400, background: "rgba(13,18,38,0.6)" }}>
        <Empty description={<span style={{ color: "#94a3b8" }}>{data.message ?? "暂无数据"}</span>} />
      </div>
    );
  }

  const o = data?.overview;

  return (
    <div className="space-y-4" style={{ background: "transparent" }}>
      {/* 顶部标题 + 班级筛选 */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <Typography.Title level={4} className="!m-0" style={{ color: "#e2e8f0", fontWeight: 700 }}>
          📊 班级学情分析大屏
        </Typography.Title>
        <Select
          allowClear
          placeholder="全部班级"
          style={{ width: 200 }}
          options={classes.map((c) => ({ value: c.class_id, label: c.class_id }))}
          onChange={(v) => setClassId(v)}
        />
      </div>

      {/* 总览统计 */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-3">
        <StatCard label="学生数" value={o?.students ?? 0} accent="#818cf8" />
        <StatCard label="测验次数" value={o?.quizzes ?? 0} accent="#22d3ee" />
        <StatCard label="平均分" value={o?.avg_score ?? 0} accent="#34d399" />
        <StatCard label="通过率" value={`${o?.pass_rate ?? 0}%`} accent="#f59e0b" />
        <StatCard label="覆盖知识点" value={o?.kps_covered ?? 0} accent="#f87171" />
      </div>

      {/* 第一行：3D 掌握度 + 趋势预测 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <ChartPanel title="知识点掌握度 3D 分布（可拖动旋转）">
          <div ref={masteryRef} className="w-full h-full" />
        </ChartPanel>
        <ChartPanel title="班级平均分趋势 + 线性回归预测（未来 7 天）">
          <div ref={trendRef} className="w-full h-full" />
        </ChartPanel>
      </div>

      {/* 第二行：分数分布 + 班级对比 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <ChartPanel title="分数段分布">
          <div ref={distRef} className="w-full h-full" />
        </ChartPanel>
        <ChartPanel title="班级平均分对比">
          <div ref={classRef} className="w-full h-full" />
        </ChartPanel>
      </div>

      {/* 热力图 */}
      <ChartPanel title="学生 × 知识点 掌握热力图" height={320}>
        <div ref={heatRef} className="w-full h-full" />
      </ChartPanel>
    </div>
  );
};

export default LearningAnalytics;
