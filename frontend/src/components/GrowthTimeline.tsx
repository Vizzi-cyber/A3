import React, { useEffect, useState } from "react";
import { Spin, Tag } from "antd";
import {
  TrophyOutlined,
  StarOutlined,
  AlertOutlined,
  SafetyCertificateOutlined,
  RiseOutlined,
} from "@ant-design/icons";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
} from "recharts";
import { useAppStore } from "../store";
import { dashboardApi } from "../services/api";

interface Milestone {
  date: string;
  type: string;
  title: string;
  icon: string;
  color: string;
}

interface DailyCurve {
  date: string;
  minutes: number;
  kp_count: number;
  quiz_count: number;
  avg_score: number;
}

const ICON_MAP: Record<string, React.ReactNode> = {
  trophy: <TrophyOutlined />,
  star: <StarOutlined />,
  alert: <AlertOutlined />,
  medal: <SafetyCertificateOutlined />,
};

/** 里程碑节点 */
const MilestoneNode: React.FC<{
  milestone: Milestone;
  index: number;
}> = ({ milestone, index }) => {
  const isLeft = index % 2 === 0;

  return (
    <div
      className={`flex items-start gap-4 ${isLeft ? "" : "flex-row-reverse"}`}
    >
      {/* 内容卡片 */}
      <div
        className={`flex-1 max-w-[45%] ${isLeft ? "text-right" : "text-left"}`}
      >
        <div
          className="inline-block bg-white rounded-xl border border-slate-100 shadow-card p-3 hover:shadow-card-hover transition-shadow"
          style={{ borderLeftColor: milestone.color, borderLeftWidth: 3 }}
        >
          <div className="text-sm font-medium text-slate-800">
            {milestone.title}
          </div>
          <div className="text-xs text-slate-400 mt-1">{milestone.date}</div>
        </div>
      </div>

      {/* 中间节点 */}
      <div className="flex flex-col items-center shrink-0">
        <div
          className="w-10 h-10 rounded-full flex items-center justify-center text-white text-sm shadow-md"
          style={{ background: milestone.color }}
        >
          {ICON_MAP[milestone.icon] || <StarOutlined />}
        </div>
        {index < 9 && <div className="w-0.5 h-8 bg-slate-200 mt-1" />}
      </div>

      {/* 占位 */}
      <div className="flex-1 max-w-[45%]" />
    </div>
  );
};

/** 成长时间轴主组件 */
const GrowthTimeline: React.FC = () => {
  const studentId = useAppStore((s) => s.studentId);
  const [milestones, setMilestones] = useState<Milestone[]>([]);
  const [dailyCurve, setDailyCurve] = useState<DailyCurve[]>([]);
  const [summary, setSummary] = useState({
    total_milestones: 0,
    mastery_count: 0,
    high_score_count: 0,
    achievement_count: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    dashboardApi
      .getTimeline(studentId)
      .then((res) => {
        const data = res.data.data;
        setMilestones(data.milestones);
        setDailyCurve(data.daily_curve);
        setSummary(data.summary);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [studentId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Spin />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 概览统计 */}
      <div className="grid grid-cols-4 gap-3">
        {[
          {
            label: "里程碑",
            value: summary.total_milestones,
            color: "#6366f1",
          },
          {
            label: "知识点掌握",
            value: summary.mastery_count,
            color: "#10b981",
          },
          {
            label: "高分测验",
            value: summary.high_score_count,
            color: "#f59e0b",
          },
          {
            label: "成就解锁",
            value: summary.achievement_count,
            color: "#8b5cf6",
          },
        ].map((item) => (
          <div
            key={item.label}
            className="text-center p-3 rounded-xl bg-white border border-slate-100 shadow-card"
          >
            <div className="text-2xl font-bold" style={{ color: item.color }}>
              {item.value}
            </div>
            <div className="text-xs text-slate-400 mt-0.5">{item.label}</div>
          </div>
        ))}
      </div>

      {/* 学习曲线 */}
      {dailyCurve.length > 0 && (
        <div className="bg-white rounded-xl border border-slate-100 shadow-card p-5">
          <div className="flex items-center gap-2 mb-4">
            <RiseOutlined className="text-indigo-500" />
            <span className="text-sm font-bold text-slate-700">
              近30天学习趋势
            </span>
          </div>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={dailyCurve}>
              <defs>
                <linearGradient id="colorMinutes" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#6366f1" stopOpacity={0.2} />
                  <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                </linearGradient>
              </defs>
              <XAxis
                dataKey="date"
                tick={{ fontSize: 10, fill: "#94a3b8" }}
                axisLine={false}
                tickLine={false}
                tickFormatter={(v: string) => v.slice(5)}
              />
              <YAxis
                tick={{ fontSize: 10, fill: "#94a3b8" }}
                axisLine={false}
                tickLine={false}
              />
              <Tooltip
                contentStyle={{
                  borderRadius: "12px",
                  border: "1px solid #e2e8f0",
                  fontSize: "12px",
                }}
                formatter={(value: number, name: string) => {
                  const labels: Record<string, string> = {
                    minutes: "学习时长(min)",
                    kp_count: "知识点",
                    quiz_count: "测验",
                  };
                  return [value, labels[name] || name];
                }}
                labelFormatter={(label: string) => `日期: ${label}`}
              />
              <Area
                type="monotone"
                dataKey="minutes"
                stroke="#6366f1"
                strokeWidth={2}
                fill="url(#colorMinutes)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* 里程碑时间轴 */}
      {milestones.length > 0 && (
        <div className="bg-white rounded-xl border border-slate-100 shadow-card p-5">
          <div className="flex items-center gap-2 mb-4">
            <TrophyOutlined className="text-amber-500" />
            <span className="text-sm font-bold text-slate-700">成长里程碑</span>
            <Tag className="rounded-full border-0 bg-indigo-50 text-indigo-600 text-xs ml-auto">
              最近{Math.min(milestones.length, 10)}条
            </Tag>
          </div>
          <div className="space-y-1">
            {milestones.slice(0, 10).map((m, idx) => (
              <MilestoneNode
                key={`${m.date}-${idx}`}
                milestone={m}
                index={idx}
              />
            ))}
          </div>
        </div>
      )}

      {/* 空状态 */}
      {milestones.length === 0 && !loading && (
        <div className="text-center py-8 text-slate-400 text-sm">
          开始学习后，你的成长里程碑将在这里展示
        </div>
      )}
    </div>
  );
};

export default GrowthTimeline;
