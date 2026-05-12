import React, { useState, useEffect, useRef, useCallback } from "react";
import { Typography, Tag, message, Space, Tooltip } from "antd";
import {
  RobotOutlined,
  BulbOutlined,
  BookOutlined,
  NodeIndexOutlined,
  ToolOutlined,
  SafetyOutlined,
  ApartmentOutlined,
  FlagFilled,
  CheckCircleFilled,
} from "@ant-design/icons";
import { useAppStore } from "../store";
import { tutorApi } from "../services/api";
import { extractApiError } from "../utils/error";
import { ChatPanel } from "../components/ChatPanel";
import { PageCard } from "../components/PageCard";

import type { ChatMessage, VisionContentItem } from "../types";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";
const WS_BASE_URL = API_BASE_URL.replace(/^http/, "ws");

const initialMessages: ChatMessage[] = [
  {
    role: "ai",
    content:
      "你好！我是你的苏格拉底式AI辅导助手。在学习中遇到任何问题，我都会通过引导式提问帮助你独立思考，而不是直接给你答案。支持发送图片给我分析哦！",
  },
];

const suggestions = [
  "这个概念的核心原理是什么？",
  "能帮我梳理一下知识脉络吗？",
  "这个知识点在实际中如何应用？",
];

const Tutor: React.FC = () => {
  const studentId = useAppStore((s) => s.studentId);
  const [messages, setMessages] = useState<ChatMessage[]>(() => {
    try {
      const saved = sessionStorage.getItem(`tutor_messages_${studentId}`);
      if (saved) {
        const parsed = JSON.parse(saved) as ChatMessage[];
        if (Array.isArray(parsed) && parsed.length > 0) return parsed;
      }
    } catch {}
    return initialMessages;
  });
  const [loading, setLoading] = useState(false);
  const [multiAgentStep, setMultiAgentStep] = useState<
    "planner" | "worker" | "critic" | "done"
  >("done");
  const [ragActive, setRagActive] = useState(true);
  const [modelProvider, setModelProvider] = useState<
    "bigmodel" | "deepseek" | "openai" | "spark" | "default"
  >("default");
  const [wsConnected, setWsConnected] = useState(false);
  const [learningState, setLearningState] = useState<{
    state: string;
    hint: string;
  } | null>(null);
  const token = useAppStore((s) => s.token);

  // 持久化聊天记录到 sessionStorage
  useEffect(() => {
    sessionStorage.setItem(
      `tutor_messages_${studentId}`,
      JSON.stringify(messages),
    );
  }, [messages, studentId]);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const reconnectAttemptRef = useRef(0);
  const mountedRef = useRef(true);

  // 建立 WebSocket 连接（依赖 studentId/token，切换用户时会自动重连）
  const connectWebSocket = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;
    const sessionId = `${studentId}_tutor`;
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
            return [...prev, { role: "ai" as const, content: data.content }];
          });
        } else if (data.type === "agent_step") {
          // 后端真实多智能体阶段事件：planner / worker / critic
          const step = data.step;
          if (step === "planner" || step === "worker" || step === "critic") {
            setMultiAgentStep(step);
          }
        } else if (data.type === "learning_state") {
          setLearningState({ state: data.state, hint: data.hint });
        } else if (data.type === "complete") {
          setLoading(false);
          setMultiAgentStep("done");
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
      // 指数退避重连：1s → 2s → 5s → 10s（封顶），最多重试 10 次
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
  }, [token, studentId]);

  useEffect(() => {
    mountedRef.current = true;
    // token 变化时关闭旧连接，重新建立
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

  const handleSend = async (content: string | VisionContentItem[]) => {
    setMessages((prev) => [...prev, { role: "user" as const, content }]);
    setLoading(true);
    // 标记进入 planner，后续阶段由后端 agent_step 事件驱动（不再 setTimeout 假装）
    setMultiAgentStep("planner");

    // 优先使用 WebSocket 流式
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(
        JSON.stringify({
          type: "message",
          content:
            typeof content === "string" ? content : JSON.stringify(content),
          student_id: studentId,
          provider: modelProvider === "default" ? undefined : modelProvider,
          rag_active: ragActive,
        }),
      );
      // 不在这里 setLoading(false)，等待 complete 消息
      return;
    }

    // Fallback: HTTP POST
    try {
      const res = await tutorApi.ask({
        student_id: studentId,
        question: content,
        session_id: `${studentId}_tutor`,
        provider: modelProvider === "default" ? undefined : modelProvider,
        rag_active: ragActive,
      });
      const aiReply = res.data?.response || "服务暂时无响应，请稍后再试。";
      setMultiAgentStep("done");
      setMessages((prev) => [
        ...prev,
        { role: "ai" as const, content: aiReply },
      ]);
    } catch (e: unknown) {
      message.error(extractApiError(e, "请求失败"));
      setMultiAgentStep("done");
      setMessages((prev) => [
        ...prev,
        { role: "ai" as const, content: "服务暂时不可用，请稍后再试。" },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="h-[calc(100vh-140px)]">
      <PageCard
        className="h-full"
        bodyStyle={{
          height: "100%",
          padding: "20px 24px",
          display: "flex",
          flexDirection: "column",
        }}
      >
        <div className="flex items-center gap-3 mb-4 flex-wrap">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center text-white shadow-glow">
            <BookOutlined />
          </div>
          <div>
            <Typography.Title level={5} className="!m-0 text-slate-800">
              智能辅导
            </Typography.Title>
            <Typography.Text className="text-slate-400 text-xs">
              苏格拉底式教学法 · 全学科辅导
            </Typography.Text>
          </div>
          <Space className="ml-auto" wrap>
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
                className={`rounded-full border-0 text-xs cursor-pointer ${ragActive ? "bg-indigo-50 text-indigo-600" : "bg-slate-100 text-slate-400"}`}
                onClick={() => setRagActive(!ragActive)}
              >
                <ApartmentOutlined /> RAG
              </Tag>
            </Tooltip>
            <Tooltip title="切换大模型">
              <Tag
                className="rounded-full border-0 bg-slate-100 text-slate-600 text-xs cursor-pointer"
                onClick={() => {
                  const providers: Array<
                    "bigmodel" | "deepseek" | "openai" | "spark" | "default"
                  > = ["default", "bigmodel", "deepseek", "openai", "spark"];
                  const idx = providers.indexOf(modelProvider);
                  setModelProvider(providers[(idx + 1) % providers.length]);
                }}
              >
                <FlagFilled className="mr-1" />
                {modelProvider === "bigmodel"
                  ? "智谱AI"
                  : modelProvider === "deepseek"
                    ? "DeepSeek"
                    : modelProvider === "openai"
                      ? "OpenAI"
                      : modelProvider === "spark"
                        ? "讯飞星火"
                        : "默认模型"}
              </Tag>
            </Tooltip>
            <Tooltip
              title={
                wsConnected
                  ? "WebSocket 已连接，支持流式输出"
                  : "WebSocket 未连接，使用 HTTP 模式"
              }
            >
              <Tag
                color={wsConnected ? "success" : "warning"}
                className="rounded-full border-0 bg-emerald-50 text-emerald-600 font-medium"
              >
                {wsConnected ? "流式在线" : "HTTP 模式"}
              </Tag>
            </Tooltip>
          </Space>
        </div>

        {/* AI 学习状态感知横幅 */}
        {learningState && learningState.state !== "neutral" && (
          <div
            className={`mb-3 px-4 py-2.5 rounded-xl flex items-center gap-3 text-sm animate-fade-in ${
              learningState.state === "frustrated"
                ? "bg-amber-50 border border-amber-200 text-amber-700"
                : learningState.state === "confused"
                  ? "bg-blue-50 border border-blue-200 text-blue-700"
                  : "bg-emerald-50 border border-emerald-200 text-emerald-700"
            }`}
          >
            <RobotOutlined className="text-lg" />
            <span className="flex-1">
              {learningState.state === "frustrated"
                ? "AI发现你可能遇到了困难，我会用更简单的方式讲解"
                : learningState.state === "confused"
                  ? "AI发现你可能有些困惑，让我换个角度来解释"
                  : "你的思考很积极，我们可以继续深入探讨"}
            </span>
            <button
              onClick={() => setLearningState(null)}
              className="text-xs opacity-50 hover:opacity-100 transition-opacity"
            >
              ✕
            </button>
          </div>
        )}

        <div className="flex-1 min-h-0">
          <ChatPanel
            messages={messages}
            loading={loading}
            onSend={handleSend}
            title=""
            subtitle=""
            placeholder="输入你的问题..."
            showSuggestions
            suggestions={suggestions}
            showAvatars
            className="h-full"
          />
        </div>
      </PageCard>
    </div>
  );
};

export default Tutor;
