import React, { useState, useEffect } from "react";
import { Typography, Tag, Progress, Row, Col, message } from "antd";
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";
import {
  PlayCircleOutlined,
  AimOutlined,
  ReloadOutlined,
  BulbOutlined,
} from "@ant-design/icons";
import { useAppStore } from "../store";
import { profileApi, tutorApi, trendApi, dashboardApi } from "../services/api";
import { buildRadarData } from "../utils/profile";
import { extractApiError } from "../utils/error";
import { ChatPanel } from "../components/ChatPanel";
import { PageCard } from "../components/PageCard";
import type { ChatMessage, StudentProfile, VisionContentItem } from "../types";

const quickActions = [
  {
    icon: <PlayCircleOutlined />,
    title: "开始评估",
    desc: "对话式画像评估",
    color: "#4f46e5",
  },
  {
    icon: <AimOutlined />,
    title: "设定目标",
    desc: "更新学习目标",
    color: "#0ea5e9",
  },
  {
    icon: <ReloadOutlined />,
    title: "重新画像",
    desc: "重置并重新构建",
    color: "#10b981",
  },
];

const Profile: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: "ai",
      content:
        "你好！我是你的AI学习画像师。在学习编程之前，我想了解一下：你是否有编程基础？对C语言的指针和内存管理是否了解？这会影响我为你推荐的学习路径。",
      agent: "评估智能体",
    },
  ]);
  const [profileData, setProfileData] = useState(buildRadarData(null));
  const [dimensions, setDimensions] = useState<
    { label: string; value: number; color: string }[]
  >([]);
  const [interactionPref, setInteractionPref] = useState<
    "video" | "text" | "audio"
  >("text");
  const [multiAgentStatus, setMultiAgentStatus] = useState({
    planner: false,
    worker: false,
    critic: false,
  });
  const [historyData, setHistoryData] = useState<
    { date: string; value: number }[]
  >([]);
  const [retentionItems, setRetentionItems] = useState<
    { topic: string; retention: number; nextReview: string }[]
  >([]);
  const [loading, setLoading] = useState(false);
  const studentId = useAppStore((s) => s.studentId);

  useEffect(() => {
    let ignore = false;
    const load = async () => {
      setLoading(true);
      try {
        const [profileRes, trendRes, summaryRes] = await Promise.all([
          profileApi.get(studentId),
          trendApi.getHistory(studentId, 7).catch(() => null),
          dashboardApi.getSummary(studentId).catch(() => null),
        ]);

        if (profileRes.data.data) {
          updateVisuals(profileRes.data.data);
          const pref =
            profileRes.data.data.practical_preferences?.interaction_pref;
          if (pref) setInteractionPref(pref);
          // 由 weak_areas 派生「遗忘曲线 · 知识点衰减」列表
          const weak = profileRes.data.data.weak_areas || [];
          if (weak.length) {
            setRetentionItems(
              weak.slice(0, 4).map((topic, i) => ({
                topic,
                // 越靠前越薄弱 -> retention 越低（35% ~ 80%）
                retention: Math.max(30, 80 - i * 12),
                nextReview:
                  i === 0
                    ? "今天"
                    : i === 1
                      ? "今天"
                      : i === 2
                        ? "明天"
                        : "后天",
              })),
            );
          }
        }

        // 画像历史变化 = trend_factor 序列（×100 转成 0~100）
        if (trendRes?.data?.data?.length) {
          setHistoryData(
            trendRes.data.data.slice(-7).map((d) => ({
              date: d.date.slice(5),
              value: Math.round(d.trend_factor * 100),
            })),
          );
        }

        // 多智能体状态 —— 后端有 trend_analysis -> planner; effect_evaluation -> worker; intervention_strategies -> critic
        if (summaryRes?.data?.algorithm_analysis) {
          const algo = summaryRes.data.algorithm_analysis;
          setMultiAgentStatus({
            planner: !!algo.trend_analysis,
            worker: !!algo.effect_evaluation,
            critic: !!algo.effect_evaluation?.intervention_strategies?.length,
          });
        }
      } catch {
        if (!ignore) message.error("获取画像失败，显示默认数据");
      } finally {
        if (!ignore) setLoading(false);
      }
    };
    load();
    return () => {
      ignore = true;
    };
  }, [studentId]);

  const updateVisuals = (p: StudentProfile) => {
    const radar = buildRadarData(p);
    setProfileData(radar);
    setDimensions(
      radar.map((item) => ({
        label: item.subject,
        value: Math.round(item.A),
        color:
          item.subject === "知识基础"
            ? "#4f46e5"
            : item.subject === "认知风格"
              ? "#0ea5e9"
              : item.subject === "学习偏好"
                ? "#10b981"
                : item.subject === "薄弱点"
                  ? "#f59e0b"
                  : item.subject === "学习进度"
                    ? "#8b5cf6"
                    : "#ec4899",
      })),
    );
  };

  const handleSend = async (content: string | VisionContentItem[]) => {
    const text = typeof content === "string" ? content : "";
    if (!text.trim()) return;
    setMessages((prev) => [...prev, { role: "user" as const, content: text }]);
    setLoading(true);
    try {
      // 1. 获取 AI 回复（先让画像师对话）
      let aiReply = "服务暂时无响应，请稍后再试。";
      try {
        const tutorRes = await tutorApi.ask({
          student_id: studentId,
          question: text,
          session_id: `${studentId}_profile`,
        });
        aiReply = tutorRes.data?.response || aiReply;
      } catch (e: unknown) {
        message.error(extractApiError(e, "请求失败"));
      }
      setMessages((prev) => [
        ...prev,
        { role: "ai" as const, content: aiReply, agent: "评估智能体" },
      ]);

      // 2. 调用 LLM 分析对话并更新画像（把最近几条对话作为上下文）
      const recentMessages = [
        ...messages.slice(-4),
        { role: "user" as const, content: text },
      ];
      const conversationContext = recentMessages
        .map(
          (m) =>
            `${m.role === "user" ? "学生" : "AI"}：${typeof m.content === "string" ? m.content : ""}`,
        )
        .join("\n");

      try {
        const analyzeRes = await profileApi.analyzeConversation(
          studentId,
          conversationContext,
        );
        if (analyzeRes.data?.data) {
          updateVisuals(analyzeRes.data.data);
          message.success("画像已根据对话自动更新");
        }
      } catch {
        // 画像分析失败不影响对话体验
      }
    } catch (e: unknown) {
      message.error(extractApiError(e, "请求失败"));
      setMessages((prev) => [
        ...prev,
        {
          role: "ai" as const,
          content: "服务暂时不可用，请稍后再试。",
          agent: "评估智能体",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleStartEvaluation = () => {
    handleSend(
      "请对我进行一次全面的学习画像评估，包括编程基础、认知风格、学习偏好和薄弱点分析。",
    );
  };

  const handleSetGoal = () => {
    handleSend(
      "我想设定一个新的学习目标，请帮我梳理当前的学习状态并给出目标建议。",
    );
  };

  const handleInitProfile = async () => {
    try {
      await profileApi.initialize(studentId, {
        inputs: [
          "我是一名计算机专业大二学生，对编程很感兴趣。有一定的高数基础，但数据结构和算法比较薄弱。喜欢通过代码实践来学习，想系统学习C语言。",
        ],
      });
      const res = await profileApi.get(studentId);
      if (res.data.data) updateVisuals(res.data.data);
      message.success("画像初始化成功");
    } catch (e: unknown) {
      message.error(extractApiError(e, "初始化失败"));
    }
  };

  const chatQuickActions = (
    <div className="flex gap-2 mb-3">
      {quickActions.map((action, idx) => (
        <button
          key={idx}
          onClick={
            idx === 0
              ? handleStartEvaluation
              : idx === 1
                ? handleSetGoal
                : handleInitProfile
          }
          className="flex items-center gap-2 px-3 py-2 rounded-lg bg-slate-50 border border-slate-100 hover:border-slate-200 hover:bg-white hover:shadow-sm transition-all text-left flex-1"
        >
          <div
            className="w-7 h-7 rounded-md flex items-center justify-center text-sm shrink-0"
            style={{ background: action.color + "12", color: action.color }}
          >
            {action.icon}
          </div>
          <div>
            <div className="font-semibold text-slate-800 text-xs leading-tight">
              {action.title}
            </div>
            <div className="text-[10px] text-slate-400">{action.desc}</div>
          </div>
        </button>
      ))}
    </div>
  );

  return (
    <div className="flex flex-col gap-4">
      <Row gutter={16} align="stretch">
        {/* 左侧：六维画像雷达 + 维度详情 */}
        <Col xs={24} lg={9}>
          <div className="flex flex-col gap-4 h-full">
            <PageCard
              title={
                <span className="font-semibold text-slate-800">
                  六维画像雷达
                </span>
              }
              bodyStyle={{
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <div className="w-full h-56">
                <ResponsiveContainer width="100%" height="100%">
                  <RadarChart
                    cx="50%"
                    cy="50%"
                    outerRadius="75%"
                    data={profileData}
                  >
                    <PolarGrid stroke="#e2e8f0" />
                    <PolarAngleAxis
                      dataKey="subject"
                      tick={{ fill: "#64748b", fontSize: 11 }}
                    />
                    <PolarRadiusAxis
                      angle={30}
                      domain={[0, 100]}
                      tick={false}
                      axisLine={false}
                    />
                    <Radar
                      name="当前画像"
                      dataKey="A"
                      stroke="#4f46e5"
                      fill="#4f46e5"
                      fillOpacity={0.15}
                      strokeWidth={2}
                    />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
            </PageCard>

            <PageCard
              title={
                <span className="font-semibold text-slate-800">维度详情</span>
              }
              className="flex-1"
            >
              <div className="space-y-2.5">
                {dimensions.length === 0 ? (
                  <div className="text-xs text-slate-400 py-3 text-center">
                    尚未生成画像，可在右侧对话或点击「重新画像」
                  </div>
                ) : (
                  dimensions.map((dim) => (
                    <div key={dim.label}>
                      <div className="flex justify-between mb-1">
                        <Typography.Text className="text-sm text-slate-600 font-medium">
                          {dim.label}
                        </Typography.Text>
                        <Typography.Text
                          className="text-sm font-bold"
                          style={{ color: dim.color }}
                        >
                          {dim.value}
                        </Typography.Text>
                      </div>
                      <Progress
                        percent={dim.value}
                        showInfo={false}
                        strokeColor={dim.color}
                        trailColor="#f1f5f9"
                        size="small"
                      />
                    </div>
                  ))
                )}
              </div>
            </PageCard>
          </div>
        </Col>

        {/* 右侧：AI画像师聊天 */}
        <Col xs={24} lg={15}>
          <PageCard
            className="h-full"
            bodyStyle={{ height: "100%", padding: "20px" }}
          >
            <ChatPanel
              messages={messages}
              loading={loading}
              onSend={handleSend}
              title="AI 画像师"
              subtitle="正在实时分析你的学习特征"
              placeholder="回复 AI 画像师..."
              inputPrefix={<BulbOutlined className="text-slate-400" />}
              preInput={chatQuickActions}
            />
          </PageCard>
        </Col>
      </Row>

      <PageCard
        title={
          <span className="font-semibold text-slate-800">画像历史变化</span>
        }
        extra={
          <Tag className="rounded-full border-0 bg-slate-100 text-slate-600 text-xs">
            近7天
          </Tag>
        }
      >
        <div className="h-56">
          {historyData.length === 0 ? (
            <div className="h-full flex items-center justify-center text-slate-400 text-sm">
              暂无趋势数据，完成几道练习后再来看
            </div>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={historyData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis
                  dataKey="date"
                  tick={{ fill: "#64748b" }}
                  axisLine={false}
                  tickLine={false}
                />
                <YAxis
                  domain={[0, 100]}
                  tick={{ fill: "#64748b" }}
                  axisLine={false}
                  tickLine={false}
                />
                <Tooltip
                  contentStyle={{
                    borderRadius: 12,
                    border: "none",
                    boxShadow: "0 4px 12px rgba(0,0,0,0.06)",
                  }}
                  cursor={{ stroke: "#e2e8f0", strokeWidth: 2 }}
                />
                <Line
                  type="monotone"
                  dataKey="value"
                  stroke="#4f46e5"
                  strokeWidth={3}
                  dot={{ fill: "#4f46e5", strokeWidth: 2, r: 4 }}
                  activeDot={{
                    r: 6,
                    fill: "#fff",
                    stroke: "#4f46e5",
                    strokeWidth: 2,
                  }}
                />
              </LineChart>
            </ResponsiveContainer>
          )}
        </div>
      </PageCard>

      {/* 遗忘曲线维度 */}
      <PageCard
        title={
          <span className="font-semibold text-slate-800">
            遗忘曲线 · 知识点衰减
          </span>
        }
        extra={
          <Tag className="rounded-full border-0 bg-slate-100 text-slate-600 text-xs">
            艾宾浩斯
          </Tag>
        }
      >
        <Row gutter={20}>
          <Col xs={24} lg={12}>
            <div className="h-56">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart
                  data={[
                    {
                      day: "第1天",
                      theoretical: 100,
                      actual: retentionItems[0]?.retention,
                    },
                    {
                      day: "第2天",
                      theoretical: 55,
                      actual: retentionItems[1]?.retention,
                    },
                    {
                      day: "第3天",
                      theoretical: 42,
                      actual: retentionItems[2]?.retention,
                    },
                    {
                      day: "第5天",
                      theoretical: 35,
                      actual: retentionItems[3]?.retention,
                    },
                    { day: "第8天", theoretical: 30 },
                    { day: "第15天", theoretical: 25 },
                    { day: "第30天", theoretical: 20 },
                  ]}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                  <XAxis
                    dataKey="day"
                    tick={{ fill: "#64748b", fontSize: 11 }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <YAxis
                    domain={[0, 100]}
                    tick={{ fill: "#64748b" }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <Tooltip
                    contentStyle={{
                      borderRadius: 12,
                      border: "none",
                      boxShadow: "0 4px 12px rgba(0,0,0,0.06)",
                    }}
                  />
                  <Line
                    type="monotone"
                    dataKey="theoretical"
                    name="理论记忆保留率"
                    stroke="#ef4444"
                    strokeWidth={2}
                    dot={{ r: 3 }}
                    strokeDasharray="5 5"
                  />
                  {retentionItems.length > 0 && (
                    <Line
                      type="monotone"
                      dataKey="actual"
                      name="你的薄弱点保留率"
                      stroke="#4f46e5"
                      strokeWidth={2}
                      dot={{ r: 4, fill: "#4f46e5" }}
                      connectNulls={false}
                    />
                  )}
                </LineChart>
              </ResponsiveContainer>
            </div>
          </Col>
          <Col xs={24} lg={12}>
            <div className="space-y-3">
              {retentionItems.length === 0 ? (
                <div className="text-sm text-slate-400 text-center py-10">
                  画像中尚无薄弱点，继续学习几个知识点后这里会自动生成复习计划
                </div>
              ) : (
                retentionItems.map((item) => (
                  <div
                    key={item.topic}
                    className="flex items-center gap-3 p-3 rounded-xl bg-slate-50 border border-slate-100"
                  >
                    <div className="flex-1">
                      <div className="text-sm font-medium text-slate-800">
                        {item.topic}
                      </div>
                      <div className="text-xs text-slate-400">
                        下次复习: {item.nextReview}
                      </div>
                    </div>
                    <div className="w-24">
                      <Progress
                        percent={item.retention}
                        size="small"
                        strokeColor={
                          item.retention > 70
                            ? "#10b981"
                            : item.retention > 50
                              ? "#f59e0b"
                              : "#ef4444"
                        }
                        trailColor="#f1f5f9"
                        showInfo={false}
                      />
                    </div>
                    <Tag
                      className={`rounded-full border-0 text-xs ${item.retention > 70 ? "bg-emerald-50 text-emerald-600" : item.retention > 50 ? "bg-amber-50 text-amber-600" : "bg-red-50 text-red-600"}`}
                    >
                      {item.retention}%
                    </Tag>
                  </div>
                ))
              )}
            </div>
          </Col>
        </Row>
      </PageCard>
    </div>
  );
};

export default Profile;
