import React, { useState, useEffect, useRef, useCallback } from "react";
import {
  Typography,
  Tag,
  message,
  Space,
  Tooltip,
  Button,
  Card,
  Progress,
  Empty,
  Modal,
  Avatar,
} from "antd";
import {
  RobotOutlined,
  BookOutlined,
  NodeIndexOutlined,
  ApartmentOutlined,
  FlagFilled,
  PlusOutlined,
  DeleteOutlined,
  CopyOutlined,
  LikeOutlined,
  DislikeOutlined,
  SendOutlined,
  LoadingOutlined,
  MessageOutlined,
  BulbOutlined,
  UserOutlined,
} from "@ant-design/icons";
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
} from "recharts";
import { useAppStore } from "../store";
import { tutorApi, profileApi, dashboardApi } from "../services/api";
import { extractApiError } from "../utils/error";
import { buildRadarData } from "../utils/profile";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api/v1";
const WS_BASE_URL =
  import.meta.env.VITE_WS_BASE_URL ||
  (typeof window !== "undefined"
    ? `${window.location.protocol === "https:" ? "wss:" : "ws:"}//${window.location.host}${API_BASE_URL}`
    : "");

interface DisplayMessage {
  id: string;
  role: "user" | "ai";
  content: string;
  time: string;
  knowledge?: string[];
  resources?: { type: "doc" | "video" | "link"; title: string; url?: string }[];
}

const QUICK_ENTRIES = [
  { icon: "📝", label: "讲解这道题" },
  { icon: "🎯", label: "总结要点" },
  { icon: "📊", label: "薄弱诊断" },
  { icon: "💡", label: "举一反三" },
];

const WELCOME_SOCRATIC: DisplayMessage = {
  id: "welcome",
  role: "ai",
  content:
    "你好！我是你的苏格拉底式AI辅导助手。在学习中遇到任何问题，我都会通过引导式提问帮助你独立思考，而不是直接给你答案。\n\n试试问我任何学习相关的问题吧！",
  time: "",
};

const WELCOME_NORMAL: DisplayMessage = {
  id: "welcome",
  role: "ai",
  content:
    "你好！我是你的AI学习助手。有什么学习上的问题都可以问我，我会尽力帮你解答。\n\n试试问我任何学习相关的问题吧！",
  time: "",
};

const GUIDED_WELCOME: DisplayMessage = {
  id: "guided-welcome",
  role: "ai",
  content: `你好！我是你的 AI 学习导师。这是我第一次见到你，让我们先来了解一下你的学习情况吧！

**请告诉我：**

1. 你目前在哪个年级？
2. 你觉得哪些科目比较薄弱？
3. 你平时喜欢什么样的学习方式？（看视频、做练习、读文档等）

回答完这些问题后，我会为你生成个性化的学习画像，然后推荐最适合你的学习资源。`,
  time: "",
};

function formatTime(dateStr: string): string {
  if (!dateStr) return "";
  const d = new Date(dateStr);
  const now = new Date();
  const diffMs = now.getTime() - d.getTime();
  const diffDay = Math.floor(diffMs / 86400000);
  if (diffDay === 0) {
    return d.toLocaleTimeString("zh-CN", {
      hour: "2-digit",
      minute: "2-digit",
    });
  }
  if (diffDay === 1) return "昨天";
  if (diffDay < 7) return `${diffDay} 天前`;
  return `${Math.floor(diffDay / 7)} 周前`;
}

const Tutor: React.FC = () => {
  const studentId = useAppStore((s) => s.studentId);
  const token = useAppStore((s) => s.token);

  const [messages, setMessages] = useState<DisplayMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [activeConversationId, setActiveConversationId] = useState<
    string | undefined
  >(() => localStorage.getItem("tutor_active_conv") || undefined);
  const [isFirstLogin, setIsFirstLogin] = useState(false);
  const [multiAgentStep, setMultiAgentStep] = useState<
    "planner" | "worker" | "critic" | "done"
  >("done");
  const [ragActive, setRagActive] = useState(true);
  const [modelProvider, setModelProvider] = useState<
    "bigmodel" | "deepseek" | "openai" | "spark" | "mimo" | "default"
  >("default");
  const [wsConnected, setWsConnected] = useState(false);
  const [feedbackMap, setFeedbackMap] = useState<
    Record<string, "like" | "dislike" | null>
  >({});
  const [socraticMode, setSocraticMode] = useState(true);

  // 画像数据
  const [radarValues, setRadarValues] = useState<number[]>([
    50, 50, 50, 50, 50, 50,
  ]);
  const [weakPoints, setWeakPoints] = useState<
    { name: string; mastery: number }[]
  >([]);
  const [resourcePref, setResourcePref] = useState<Record<string, number>>({});
  const [profile, setProfile] = useState<any>(null);

  // 会话列表
  const [conversations, setConversations] = useState<any[]>([]);
  const [conversationsLoading, setConversationsLoading] = useState(false);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const reconnectAttemptRef = useRef(0);
  const mountedRef = useRef(true);
  const currentConversationIdRef = useRef<string | undefined>(undefined);
  const scrollRef = useRef<HTMLDivElement>(null);

  // 持久化会话ID
  useEffect(() => {
    if (activeConversationId) {
      localStorage.setItem("tutor_active_conv", activeConversationId);
    } else {
      localStorage.removeItem("tutor_active_conv");
    }
  }, [activeConversationId]);

  // 自动滚动
  useEffect(() => {
    scrollRef.current?.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [messages]);

  // 加载画像数据
  const loadProfile = useCallback(async () => {
    try {
      const profileRes = await profileApi.get(studentId);
      if (profileRes.data?.data) {
        const p = profileRes.data.data;
        setProfile(p);

        // 雷达图：使用 buildRadarData 的数据（6维中文标签）
        // radarValues 保留作为备用，但雷达图已改用 radarData

        // 资源偏好：从 practical_preferences 提取
        const pp = p.practical_preferences || {};
        const prefMap: Record<string, number> = {};
        if (pp.preferred_practice_types?.length) {
          pp.preferred_practice_types.forEach((t) => {
            prefMap[t] = (prefMap[t] || 0) + 1;
          });
        }
        if (pp.overall_score) {
          prefMap["综合评分"] = Math.round(pp.overall_score);
        }
        if (pp.interaction_pref) {
          const prefLabel =
            pp.interaction_pref === "video"
              ? "视频"
              : pp.interaction_pref === "audio"
                ? "音频"
                : "文本";
          prefMap[prefLabel] = (prefMap[prefLabel] || 0) + 10;
        }
        setResourcePref(prefMap);
      }
    } catch {
      // 静默失败
    }

    try {
      const summaryRes = await dashboardApi.getSummary(studentId);
      if (summaryRes.data) {
        const data = summaryRes.data;
        // 薄弱知识点：优先用 algorithm_analysis.effect_evaluation.predictions.potential_loss_points
        const lossPoints =
          data.algorithm_analysis?.effect_evaluation?.predictions
            ?.potential_loss_points;
        if (lossPoints?.length) {
          setWeakPoints(
            lossPoints.slice(0, 5).map((lp) => ({
              name: lp.tag,
              mastery: Math.max(10, Math.round((1 - lp.risk_score) * 100)),
            })),
          );
        } else {
          // fallback：从 profile.weak_areas 提取（显示名称，掌握度未知）
          const weak = data.profile_summary?.weak_areas || [];
          if (weak.length > 0) {
            setWeakPoints(
              weak.slice(0, 5).map((name: string) => ({
                name,
                mastery: 0, // 后端暂无掌握度数据
              })),
            );
          }
        }

        // 资源偏好：合并 profile_summary 中的数据
        const profileSummary = data.profile_summary;
        if (profileSummary?.knowledge_base) {
          setResourcePref((prev) => {
            const merged = { ...prev };
            Object.entries(profileSummary.knowledge_base).forEach(([k, v]) => {
              if (typeof v === "number" && k !== "overall_score") {
                merged[k] = Math.round(v);
              }
            });
            return merged;
          });
        }
      }
    } catch {
      // 静默失败
    }
  }, [studentId]);

  useEffect(() => {
    loadProfile();
  }, [loadProfile]);

  // 页面重新可见时刷新画像数据（从其他页面返回时同步更新）
  useEffect(() => {
    const handleVisibility = () => {
      if (document.visibilityState === "visible" && studentId) {
        loadProfile();
      }
    };
    document.addEventListener("visibilitychange", handleVisibility);
    return () =>
      document.removeEventListener("visibilitychange", handleVisibility);
  }, [studentId, loadProfile]);

  // 加载会话列表（只在初始加载时调用，不依赖 profile 避免循环重置）
  const loadConversations = useCallback(async () => {
    // 如果正在加载中或已有消息（非欢迎消息），跳过避免覆盖流式输出
    if (conversationsLoading) return;

    setConversationsLoading(true);
    try {
      const res = await tutorApi.getHistory(`${studentId}_default`);
      const data = res.data as any;
      // API 返回 messages 数组，需要转换为前端格式
      const msgs = data?.messages || [];
      const convs = msgs.map((m: any, idx: number) => ({
        id: `conv-${idx}`,
        role: m.role === "assistant" ? "ai" : m.role,
        content: m.content,
        time: "",
      }));
      setConversations(convs);

      // 只有在没有消息时才设置欢迎消息（避免覆盖正在进行的对话）
      setMessages((prev) => {
        // 如果已有用户消息，不重置
        if (prev.some((m) => m.role === "user")) return prev;

        // 如果有历史消息，加载历史
        if (convs.length > 0) {
          return convs;
        }

        // 只有当没有会话 AND 画像未初始化时才显示引导欢迎
        const hasProfile =
          profile?.knowledge_base &&
          Object.keys(profile.knowledge_base).length > 0;
        if (!hasProfile) {
          setIsFirstLogin(true);
          return [
            {
              ...GUIDED_WELCOME,
              time: new Date().toLocaleTimeString("zh-CN", {
                hour: "2-digit",
                minute: "2-digit",
              }),
            },
          ];
        }
        return [
          {
            ...(socraticMode ? WELCOME_SOCRATIC : WELCOME_NORMAL),
            time: new Date().toLocaleTimeString("zh-CN", {
              hour: "2-digit",
              minute: "2-digit",
            }),
          },
        ];
      });
    } catch {
      setMessages((prev) => {
        if (prev.some((m) => m.role === "user")) return prev;
        return [
          {
            ...(socraticMode ? WELCOME_SOCRATIC : WELCOME_NORMAL),
            time: new Date().toLocaleTimeString("zh-CN", {
              hour: "2-digit",
              minute: "2-digit",
            }),
          },
        ];
      });
    } finally {
      setConversationsLoading(false);
    }
  }, [studentId]); // 移除 profile 依赖，避免循环

  useEffect(() => {
    loadConversations();
  }, [loadConversations]);

  // 切换模式时更新欢迎语
  useEffect(() => {
    setMessages((prev) => {
      if (prev.length === 0) return prev;
      const first = prev[0];
      if (first.id !== "welcome") return prev;
      const newWelcome = socraticMode ? WELCOME_SOCRATIC : WELCOME_NORMAL;
      return [
        {
          ...newWelcome,
          time: new Date().toLocaleTimeString("zh-CN", {
            hour: "2-digit",
            minute: "2-digit",
          }),
        },
        ...prev.slice(1),
      ];
    });
  }, [socraticMode]);

  // 建立 WebSocket 连接
  const connectWebSocket = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;
    const sessionId = `${studentId}_default`;
    const wsUrl = token
      ? `${WS_BASE_URL}/tutor/ws/${sessionId}?token=${encodeURIComponent(token)}`
      : `${WS_BASE_URL}/tutor/ws/${sessionId}`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      setWsConnected(true);
      reconnectAttemptRef.current = 0;
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === "chunk") {
          setMessages((prev) => {
            const last = prev[prev.length - 1];
            if (last && last.role === "ai") {
              const newContent =
                typeof last.content === "string"
                  ? last.content + data.content
                  : data.content;
              return [...prev.slice(0, -1), { ...last, content: newContent }];
            }
            return [
              ...prev,
              {
                id: `ai-${Date.now()}`,
                role: "ai" as const,
                content: data.content,
                time: new Date().toLocaleTimeString("zh-CN", {
                  hour: "2-digit",
                  minute: "2-digit",
                }),
              },
            ];
          });
        } else if (data.type === "agent_step") {
          const step = data.step;
          if (step === "planner" || step === "worker" || step === "critic") {
            setMultiAgentStep(step);
          }
        } else if (data.type === "complete") {
          setLoading(false);
          setMultiAgentStep("done");
          // 对话完成后自动分析对话并更新画像
          setMessages((prev) => {
            const conversationText = prev
              .filter((m) => m.role === "user" || m.role === "ai")
              .map(
                (m) =>
                  `${m.role === "user" ? "学生" : "AI"}: ${typeof m.content === "string" ? m.content : ""}`,
              )
              .join("\n");
            if (conversationText.length > 20) {
              profileApi
                .analyzeConversation(studentId, conversationText)
                .catch(() => {});
            }
            return prev;
          });
          // 延迟刷新画像（等待分析完成）
          setTimeout(() => loadProfile(), 2000);
        } else if (data.type === "pong") {
          // keepalive
        }
      } catch {
        // ignore non-json
      }
    };

    ws.onerror = () => {
      setWsConnected(false);
    };

    ws.onclose = () => {
      setWsConnected(false);
      if (reconnectTimerRef.current) clearTimeout(reconnectTimerRef.current);
      if (reconnectAttemptRef.current >= 10) return;
      const backoff = [1000, 2000, 5000, 10000];
      const delay =
        backoff[Math.min(reconnectAttemptRef.current, backoff.length - 1)];
      reconnectAttemptRef.current += 1;
      reconnectTimerRef.current = setTimeout(() => {
        if (mountedRef.current) {
          connectWebSocket();
        }
      }, delay);
    };

    wsRef.current = ws;
  }, [token, studentId, loadProfile]);

  useEffect(() => {
    mountedRef.current = true;
    if (wsRef.current && wsRef.current.readyState !== WebSocket.CLOSED) {
      wsRef.current.close();
      wsRef.current = null;
    }
    connectWebSocket();
    return () => {
      mountedRef.current = false;
      if (reconnectTimerRef.current) clearTimeout(reconnectTimerRef.current);
      wsRef.current?.close();
    };
  }, [connectWebSocket]);

  // 定期 ping 保持连接
  useEffect(() => {
    const interval = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ type: "ping" }));
      }
    }, 30000);
    return () => clearInterval(interval);
  }, []);

  // 发送消息
  const handleSend = async (text?: string) => {
    const value = text ?? input.trim();
    if (!value) return;

    const userMsg: DisplayMessage = {
      id: `user-${Date.now()}`,
      role: "user",
      content: value,
      time: new Date().toLocaleTimeString("zh-CN", {
        hour: "2-digit",
        minute: "2-digit",
      }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);
    setMultiAgentStep("planner");

    // 优先使用 WebSocket 流式
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(
        JSON.stringify({
          type: "message",
          content: value,
          student_id: studentId,
          provider: modelProvider === "default" ? undefined : modelProvider,
          rag_active: ragActive,
          mode: socraticMode ? "socratic" : "normal",
        }),
      );
      return;
    }

    // Fallback: HTTP POST
    try {
      const res = await tutorApi.ask({
        student_id: studentId,
        question: value,
        session_id: `${studentId}_default`,
        provider: modelProvider === "default" ? undefined : modelProvider,
        rag_active: ragActive,
        mode: socraticMode ? "socratic" : "normal",
      });
      const aiReply = res.data?.response || "服务暂时无响应，请稍后再试。";
      setMultiAgentStep("done");
      setMessages((prev) => {
        const newMsgs = [
          ...prev,
          {
            id: `ai-${Date.now()}`,
            role: "ai" as const,
            content: aiReply,
            time: new Date().toLocaleTimeString("zh-CN", {
              hour: "2-digit",
              minute: "2-digit",
            }),
          },
        ];
        // 对话完成后自动分析对话并更新画像
        const conversationText = newMsgs
          .filter((m) => m.role === "user" || m.role === "ai")
          .map(
            (m) =>
              `${m.role === "user" ? "学生" : "AI"}: ${typeof m.content === "string" ? m.content : ""}`,
          )
          .join("\n");
        if (conversationText.length > 20) {
          profileApi
            .analyzeConversation(studentId, conversationText)
            .catch(() => {});
        }
        return newMsgs;
      });
      // 延迟刷新画像
      setTimeout(() => loadProfile(), 2000);
    } catch (e: unknown) {
      message.error(extractApiError(e, "请求失败"));
      setMultiAgentStep("done");
      setMessages((prev) => [
        ...prev,
        {
          id: `ai-${Date.now()}`,
          role: "ai" as const,
          content: "服务暂时不可用，请稍后再试。",
          time: new Date().toLocaleTimeString("zh-CN", {
            hour: "2-digit",
            minute: "2-digit",
          }),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  // 新建对话
  const startNewConversation = () => {
    setActiveConversationId(undefined);
    currentConversationIdRef.current = undefined;
    const hasProfile =
      profile?.knowledge_base && Object.keys(profile.knowledge_base).length > 0;
    if (isFirstLogin && !hasProfile) {
      setMessages([
        {
          ...GUIDED_WELCOME,
          time: new Date().toLocaleTimeString("zh-CN", {
            hour: "2-digit",
            minute: "2-digit",
          }),
        },
      ]);
    } else {
      setMessages([
        {
          ...(socraticMode ? WELCOME_SOCRATIC : WELCOME_NORMAL),
          time: new Date().toLocaleTimeString("zh-CN", {
            hour: "2-digit",
            minute: "2-digit",
          }),
        },
      ]);
    }
  };

  // 删除会话
  const handleDeleteConversation = async (
    conversationId: string,
    e: React.MouseEvent,
  ) => {
    e.stopPropagation();
    Modal.confirm({
      title: "确认删除",
      content: "删除后无法恢复，确定要删除这个对话吗？",
      okText: "删除",
      okType: "danger",
      cancelText: "取消",
      onOk: async () => {
        try {
          setConversations((prev) =>
            prev.filter((c) => c.conversation_id !== conversationId),
          );
          if (activeConversationId === conversationId) {
            startNewConversation();
          }
          message.success("已删除");
        } catch {
          message.error("删除失败");
        }
      },
    });
  };

  // 雷达图数据（使用 buildRadarData 生成友好的中文标签）
  const radarData = React.useMemo(() => buildRadarData(profile), [profile]);

  const tagColors = ["red", "orange", "gold", "green", "cyan"];

  return (
    <div className="flex gap-4 h-[calc(100vh-140px)]">
      {/* 左侧主聊天区 */}
      <div className="flex-1 flex flex-col">
        <Card
          className="flex-1 flex flex-col"
          bordered={false}
          title={
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center text-white shadow-glow">
                <RobotOutlined />
              </div>
              <div>
                <div className="font-bold text-slate-800 flex items-center gap-2">
                  AI 智能导师
                  <Tooltip title={socraticMode ? "苏格拉底式引导" : "普通对话"}>
                    <button
                      onClick={() => setSocraticMode(!socraticMode)}
                      className={`px-2 py-0.5 rounded-full text-[10px] font-medium border transition-all ${
                        socraticMode
                          ? "bg-amber-50 border-amber-200 text-amber-700"
                          : "bg-slate-50 border-slate-200 text-slate-500"
                      }`}
                    >
                      {socraticMode ? "苏格拉底" : "普通对话"}
                    </button>
                  </Tooltip>
                </div>
                <div className="text-xs text-slate-400 flex items-center gap-1">
                  {activeConversationId ? (
                    <>
                      <MessageOutlined style={{ fontSize: 10 }} />
                      {conversations
                        .find((c) => c.conversation_id === activeConversationId)
                        ?.first_message?.substring(0, 25) || "会话中"}
                    </>
                  ) : (
                    <>
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                      新对话
                    </>
                  )}
                </div>
              </div>
            </div>
          }
          extra={
            <Space>
              {multiAgentStep !== "done" && (
                <Tag className="rounded-full border-0 bg-blue-50 text-blue-600 text-xs">
                  <NodeIndexOutlined className="mr-1" />
                  {multiAgentStep === "planner"
                    ? "Planner 拆解中"
                    : multiAgentStep === "worker"
                      ? "Worker 生成中"
                      : "Critic 审核中"}
                </Tag>
              )}
              <Tooltip title={ragActive ? "RAG 检索增强已启用" : "RAG 已关闭"}>
                <Tag
                  className={`rounded-full border-0 text-xs cursor-pointer ${ragActive ? "bg-blue-50 text-blue-700" : "bg-slate-100 text-slate-600"}`}
                  onClick={() => setRagActive(!ragActive)}
                >
                  <ApartmentOutlined /> RAG
                </Tag>
              </Tooltip>
              <Tooltip title="当前使用讯飞星火">
                <Tag className="rounded-full border-0 bg-blue-50 text-blue-600 text-xs cursor-default">
                  <FlagFilled className="mr-1" />
                  讯飞星火
                </Tag>
              </Tooltip>
              <Tooltip
                title={wsConnected ? "WebSocket 已连接" : "WebSocket 未连接"}
              >
                <Tag
                  color={wsConnected ? "success" : "warning"}
                  className="rounded-full border-0"
                >
                  {wsConnected ? "流式在线" : "HTTP 模式"}
                </Tag>
              </Tooltip>
            </Space>
          }
          styles={{
            body: {
              padding: 0,
              height: "100%",
              display: "flex",
              flexDirection: "column",
            },
          }}
        >
          {/* 消息列表 */}
          <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((m) => (
              <div
                key={m.id}
                className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`flex gap-3 max-w-[75%] ${m.role === "user" ? "flex-row-reverse" : ""}`}
                >
                  <Avatar
                    size={32}
                    icon={
                      m.role === "user" ? <UserOutlined /> : <RobotOutlined />
                    }
                    style={{
                      background:
                        m.role === "user"
                          ? "#E5E6EB"
                          : "linear-gradient(135deg, #4f46e5, #7c3aed)",
                      color: m.role === "user" ? "#4E5969" : "#fff",
                      flexShrink: 0,
                    }}
                  />
                  <div
                    className={`rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                      m.role === "user"
                        ? "bg-primary text-white rounded-tr-sm"
                        : "bg-white border border-slate-200 rounded-tl-sm shadow-sm"
                    }`}
                  >
                    {m.role === "ai" ? (
                      <div className="prose prose-sm max-w-none">
                        <Markdown remarkPlugins={[remarkGfm]}>
                          {m.content}
                        </Markdown>
                      </div>
                    ) : (
                      m.content
                    )}

                    {m.knowledge && m.knowledge.length > 0 && (
                      <div className="mt-2 pt-2 border-t border-dashed border-slate-200 flex flex-wrap gap-1 items-center text-xs">
                        <BulbOutlined className="text-amber-500" />
                        <span className="text-slate-400">关联知识点：</span>
                        {m.knowledge.map((k) => (
                          <Tag
                            key={k}
                            className="rounded-full border-0 bg-slate-100 text-slate-600 text-xs m-0"
                          >
                            {k}
                          </Tag>
                        ))}
                      </div>
                    )}

                    {m.resources && m.resources.length > 0 && (
                      <div className="mt-2 pt-2 border-t border-slate-100 space-y-1">
                        {m.resources.map((r, idx) => (
                          <div
                            key={idx}
                            className="flex items-center gap-2 p-2 rounded-lg bg-slate-50 hover:bg-slate-100 transition-colors cursor-pointer"
                          >
                            <span className="text-primary">
                              {r.type === "doc"
                                ? "📄"
                                : r.type === "video"
                                  ? "🎬"
                                  : "🔗"}
                            </span>
                            <span className="flex-1 text-xs text-slate-600 truncate">
                              {r.title}
                            </span>
                          </div>
                        ))}
                      </div>
                    )}

                    {m.role === "ai" && m.id !== "welcome" && m.content && (
                      <div className="mt-2 pt-2 border-t border-slate-100 flex items-center gap-2 text-xs text-slate-400">
                        <Tooltip title="复制">
                          <Button
                            type="text"
                            size="small"
                            icon={<CopyOutlined />}
                            onClick={() => {
                              navigator.clipboard.writeText(m.content);
                              message.success("已复制");
                            }}
                          />
                        </Tooltip>
                        <Tooltip title="有帮助">
                          <Button
                            type="text"
                            size="small"
                            icon={<LikeOutlined />}
                            style={
                              feedbackMap[m.id] === "like"
                                ? { color: "#10B981" }
                                : undefined
                            }
                            onClick={() => {
                              const newVal =
                                feedbackMap[m.id] === "like" ? null : "like";
                              setFeedbackMap((prev) => ({
                                ...prev,
                                [m.id]: newVal,
                              }));
                              if (newVal) {
                                tutorApi
                                  .submitFeedback(m.id, { rating: "like" })
                                  .catch(() => {});
                              }
                              message.success("感谢反馈");
                            }}
                          />
                        </Tooltip>
                        <Tooltip title="没帮助">
                          <Button
                            type="text"
                            size="small"
                            icon={<DislikeOutlined />}
                            style={
                              feedbackMap[m.id] === "dislike"
                                ? { color: "#EF4444" }
                                : undefined
                            }
                            onClick={() => {
                              const newVal =
                                feedbackMap[m.id] === "dislike"
                                  ? null
                                  : "dislike";
                              setFeedbackMap((prev) => ({
                                ...prev,
                                [m.id]: newVal,
                              }));
                              if (newVal) {
                                tutorApi
                                  .submitFeedback(m.id, { rating: "dislike" })
                                  .catch(() => {});
                              }
                              message.success("感谢反馈");
                            }}
                          />
                        </Tooltip>
                        {m.time && <span className="ml-auto">{m.time}</span>}
                      </div>
                    )}
                    {m.role === "user" && (
                      <div className="mt-1 text-xs text-right opacity-60">
                        {m.time}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}

            {/* Typing 指示器 */}
            {loading && messages[messages.length - 1]?.content === "" && (
              <div className="flex justify-start">
                <div className="flex gap-3">
                  <Avatar
                    size={32}
                    icon={<RobotOutlined />}
                    style={{
                      background: "linear-gradient(135deg, #4f46e5, #7c3aed)",
                      color: "#fff",
                      flexShrink: 0,
                    }}
                  />
                  <div className="bg-white border border-slate-200 rounded-2xl rounded-tl-sm px-4 py-3 shadow-sm">
                    <div className="flex gap-1">
                      <span
                        className="w-2 h-2 bg-slate-400 rounded-full animate-pulse"
                        style={{ animationDelay: "0ms" }}
                      />
                      <span
                        className="w-2 h-2 bg-slate-400 rounded-full animate-pulse"
                        style={{ animationDelay: "150ms" }}
                      />
                      <span
                        className="w-2 h-2 bg-slate-400 rounded-full animate-pulse"
                        style={{ animationDelay: "300ms" }}
                      />
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* 快捷操作 */}
          <div className="px-4 py-2 border-t border-slate-100 flex gap-2 flex-wrap">
            {QUICK_ENTRIES.map((q) => (
              <Button
                key={q.label}
                size="small"
                onClick={() => handleSend(q.label)}
                className="rounded-full"
                disabled={loading}
              >
                <span className="mr-1">{q.icon}</span>
                {q.label}
              </Button>
            ))}
          </div>

          {/* 输入区 */}
          <div className="px-4 py-3 border-t border-slate-100 flex gap-2">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={
                socraticMode
                  ? "描述你的问题，苏格拉底式引导学习..."
                  : "描述你的问题，开始 AI 智能问答..."
              }
              className="flex-1 px-4 py-2 rounded-xl border border-slate-200 focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20 transition-all"
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleSend();
                }
              }}
              disabled={loading}
            />
            <Button
              type="primary"
              icon={loading ? <LoadingOutlined /> : <SendOutlined />}
              onClick={() => handleSend()}
              disabled={!input.trim() || loading}
              loading={loading}
              className="rounded-xl"
            >
              发送
            </Button>
          </div>
        </Card>
      </div>

      {/* 右侧信息栏 */}
      <div className="w-72 flex-shrink-0 flex flex-col gap-4">
        {/* 新对话按钮 */}
        <Button
          type="primary"
          icon={<PlusOutlined />}
          block
          className="rounded-xl"
          onClick={startNewConversation}
        >
          新对话
        </Button>

        {/* 历史会话列表 */}
        <Card
          title={<span className="font-semibold text-sm">历史会话</span>}
          size="small"
          bordered={false}
          className="rounded-2xl"
          styles={{ body: { padding: 8, maxHeight: 200, overflowY: "auto" } }}
          loading={conversationsLoading}
        >
          {conversations.length === 0 ? (
            <Empty
              description="暂无历史"
              image={Empty.PRESENTED_IMAGE_SIMPLE}
            />
          ) : (
            conversations.map((c) => (
              <div
                key={c.conversation_id}
                className={`p-2 rounded-lg cursor-pointer hover:bg-slate-50 transition-colors flex items-center justify-between group ${
                  activeConversationId === c.conversation_id
                    ? "bg-primary/5"
                    : ""
                }`}
              >
                <div
                  className="flex-1 min-w-0"
                  onClick={() => setActiveConversationId(c.conversation_id)}
                >
                  <div className="text-xs text-slate-800 truncate">
                    {c.first_message}
                  </div>
                  <div className="text-[10px] text-slate-400">
                    {formatTime(c.last_message_at)}
                  </div>
                </div>
                <DeleteOutlined
                  className="text-slate-300 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-opacity"
                  onClick={(e) =>
                    handleDeleteConversation(c.conversation_id, e)
                  }
                />
              </div>
            ))
          )}
        </Card>

        {/* 学情雷达 */}
        <Card
          title={<span className="font-semibold text-sm">学情雷达</span>}
          size="small"
          bordered={false}
          className="rounded-2xl"
        >
          <div className="h-48">
            {radarData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart
                  cx="50%"
                  cy="50%"
                  outerRadius="70%"
                  data={radarData}
                >
                  <PolarGrid stroke="#E5E6EB" />
                  <PolarAngleAxis
                    dataKey="subject"
                    tick={{ fill: "#4E5969", fontSize: 10 }}
                  />
                  <PolarRadiusAxis
                    angle={30}
                    domain={[0, 100]}
                    tick={false}
                    axisLine={false}
                  />
                  <Radar
                    name="当前能力"
                    dataKey="A"
                    stroke="#4f46e5"
                    fill="#4f46e5"
                    fillOpacity={0.2}
                    strokeWidth={2}
                  />
                </RadarChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-full text-slate-400 text-sm">
                加载中...
              </div>
            )}
          </div>
        </Card>

        {/* 薄弱知识点 */}
        <Card
          title={<span className="font-semibold text-sm">薄弱知识点</span>}
          size="small"
          bordered={false}
          className="rounded-2xl"
        >
          <div className="flex flex-wrap gap-1.5">
            {weakPoints.length > 0 ? (
              weakPoints.map((w, i) => (
                <Tag
                  key={w.name}
                  color={tagColors[i % tagColors.length]}
                  className="rounded-full"
                >
                  {w.name}
                </Tag>
              ))
            ) : (
              <span className="text-xs text-slate-400">暂无数据</span>
            )}
          </div>
        </Card>

        {/* 资源偏好 */}
        <Card
          title={<span className="font-semibold text-sm">资源偏好</span>}
          size="small"
          bordered={false}
          className="rounded-2xl"
        >
          {Object.keys(resourcePref).length > 0 ? (
            (() => {
              const total =
                Object.values(resourcePref).reduce((a, b) => a + b, 0) || 1;
              const colors = [
                "#4f46e5",
                "#10B981",
                "#F59E0B",
                "#EF4444",
                "#0D9488",
              ];
              return Object.entries(resourcePref).map(([label, value], idx) => {
                const pct = total > 0 ? Math.round((value / total) * 100) : 0;
                return (
                  <div key={label} className={idx > 0 ? "mt-2" : ""}>
                    <div className="flex justify-between text-xs text-slate-500 mb-1">
                      <span>{label}</span>
                      <span>{pct}%</span>
                    </div>
                    <Progress
                      percent={pct}
                      strokeColor={colors[idx % colors.length]}
                      size="small"
                      showInfo={false}
                    />
                  </div>
                );
              });
            })()
          ) : (
            <span className="text-xs text-slate-400">暂无数据</span>
          )}
        </Card>
      </div>
    </div>
  );
};

export default Tutor;
