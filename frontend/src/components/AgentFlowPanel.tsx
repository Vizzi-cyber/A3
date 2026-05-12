import React, { useEffect, useRef, useState, useCallback } from "react";
import { Button, Tag, Timeline, Spin, message } from "antd";
import {
  RobotOutlined,
  UserOutlined,
  NodeIndexOutlined,
  FileTextOutlined,
  MessageOutlined,
  CheckCircleOutlined,
  LoadingOutlined,
  CloseCircleOutlined,
  PlayCircleOutlined,
  ThunderboltOutlined,
} from "@ant-design/icons";
import { agentFlowApi } from "../services/api";
import { useAppStore } from "../store";
import type { AgentFlowRun, AgentNodeState } from "../types";

/** Agent 节点配置 */
const AGENT_DEFS = [
  {
    key: "supervisor",
    label: "调度中心",
    icon: <RobotOutlined />,
    desc: "分析任务，路由决策",
  },
  {
    key: "profiler",
    label: "画像师",
    icon: <UserOutlined />,
    desc: "分析6维学生画像",
  },
  {
    key: "path_planner",
    label: "路径规划师",
    icon: <NodeIndexOutlined />,
    desc: "DAG学习路径规划",
  },
  {
    key: "resource_generator",
    label: "资源生成师",
    icon: <FileTextOutlined />,
    desc: "生成个性化资源",
  },
  {
    key: "tutor",
    label: "辅导助手",
    icon: <MessageOutlined />,
    desc: "智能答疑解惑",
  },
  {
    key: "assembler",
    label: "结果汇总",
    icon: <CheckCircleOutlined />,
    desc: "汇总输出最终结果",
  },
] as const;

type AgentKey = (typeof AGENT_DEFS)[number]["key"];

/** 状态配色 */
const STATUS_STYLES: Record<
  string,
  { bg: string; border: string; text: string; ring: string }
> = {
  idle: {
    bg: "bg-slate-50",
    border: "border-slate-200",
    text: "text-slate-400",
    ring: "",
  },
  running: {
    bg: "bg-indigo-50",
    border: "border-indigo-300",
    text: "text-indigo-700",
    ring: "ring-2 ring-indigo-200 animate-pulse-soft",
  },
  completed: {
    bg: "bg-emerald-50",
    border: "border-emerald-300",
    text: "text-emerald-700",
    ring: "",
  },
  failed: {
    bg: "bg-red-50",
    border: "border-red-300",
    text: "text-red-700",
    ring: "",
  },
};

const STATUS_ICON: Record<string, React.ReactNode> = {
  idle: null,
  running: <LoadingOutlined spin className="text-indigo-500" />,
  completed: <CheckCircleOutlined className="text-emerald-500" />,
  failed: <CloseCircleOutlined className="text-red-500" />,
};

const STATUS_LABEL: Record<string, string> = {
  idle: "待命",
  running: "执行中",
  completed: "完成",
  failed: "失败",
};

/** 单个 Agent 节点卡片 */
const AgentNodeCard: React.FC<{
  def: (typeof AGENT_DEFS)[number];
  state: AgentNodeState | undefined;
}> = React.memo(({ def, state }) => {
  const s = state?.status || "idle";
  const style = STATUS_STYLES[s];

  return (
    <div
      className={`relative flex flex-col items-center gap-2 p-3 rounded-xl border-2 transition-all duration-300 min-w-[100px] ${style.bg} ${style.border} ${style.ring}`}
    >
      <div className={`text-2xl ${style.text}`}>{def.icon}</div>
      <div className={`text-xs font-bold ${style.text}`}>{def.label}</div>
      {s !== "idle" && (
        <Tag
          className={`rounded-full border-0 text-[10px] px-2 ${style.bg} ${style.text}`}
          icon={STATUS_ICON[s]}
        >
          {STATUS_LABEL[s]}
        </Tag>
      )}
      {state?.task && s === "running" && (
        <div className="text-[10px] text-slate-500 text-center max-w-[100px] truncate">
          {state.task}
        </div>
      )}
    </div>
  );
});
AgentNodeCard.displayName = "AgentNodeCard";

/** SVG 连线（带动画） */
const FlowConnector: React.FC<{ active: boolean; completed: boolean }> = ({
  active,
  completed,
}) => (
  <div className="flex items-center justify-center w-8">
    <svg width="32" height="12" className="overflow-visible">
      <line
        x1="0"
        y1="6"
        x2="32"
        y2="6"
        stroke={completed ? "#10b981" : active ? "#6366f1" : "#e2e8f0"}
        strokeWidth={2}
        strokeDasharray={active && !completed ? "4 4" : "none"}
        className={
          active && !completed ? "animate-[dash_1s_linear_infinite]" : ""
        }
      />
      {(active || completed) && (
        <polygon
          points="28,2 32,6 28,10"
          fill={completed ? "#10b981" : "#6366f1"}
        />
      )}
    </svg>
  </div>
);

/** 主组件 */
const AgentFlowPanel: React.FC<{
  onRun?: (taskType: string) => void;
}> = React.memo(({ onRun }) => {
  const studentId = useAppStore((s) => s.studentId);
  const [runData, setRunData] = useState<AgentFlowRun | null>(null);
  const [runId, setRunId] = useState<string | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  /** 启动一次 Agent 工作流 */
  const handleStart = useCallback(
    async (taskType: string) => {
      try {
        const res = await agentFlowApi.startRun({
          student_id: studentId,
          task_type: taskType,
          context: { topic: "C语言数据结构" },
        });
        setRunId(res.data.run_id);
        setIsRunning(true);
        setRunData(null);
        onRun?.(taskType);
      } catch {
        message.error("启动工作流失败");
      }
    },
    [studentId, onRun],
  );

  /** 轮询状态 */
  useEffect(() => {
    if (!runId || !isRunning) return;

    const poll = async () => {
      try {
        const res = await agentFlowApi.getStatus(runId);
        setRunData(res.data);
        if (res.data.status !== "running") {
          setIsRunning(false);
        }
      } catch {
        // ignore poll errors
      }
    };

    poll();
    pollRef.current = setInterval(poll, 1500);
    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, [runId, isRunning]);

  /** 连线状态判断 */
  const getConnectorState = (fromKey: string, toKey: string) => {
    if (!runData) return { active: false, completed: false };
    const from = runData.agents[fromKey];
    const to = runData.agents[toKey];
    const fromDone = from?.status === "completed";
    const toRunning = to?.status === "running";
    const toDone = to?.status === "completed";
    return {
      active: fromDone && (toRunning || toDone),
      completed: fromDone && toDone,
    };
  };

  return (
    <div className="rounded-2xl border border-slate-100 bg-white shadow-card p-5 space-y-4">
      {/* 标题栏 */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-indigo-500 flex items-center justify-center text-white">
            <ThunderboltOutlined />
          </div>
          <div>
            <div className="font-bold text-slate-800 text-sm">
              多智能体协作引擎
            </div>
            <div className="text-xs text-slate-400">
              LangGraph 驱动 · 5个AI智能体实时协同
            </div>
          </div>
        </div>
        <div className="flex gap-2">
          <Button
            type="primary"
            size="small"
            icon={<PlayCircleOutlined />}
            loading={isRunning}
            onClick={() => handleStart("profile_update")}
            className="rounded-lg bg-primary"
          >
            {isRunning ? "执行中..." : "运行画像分析"}
          </Button>
          <Button
            size="small"
            loading={isRunning}
            onClick={() => handleStart("resource_generation")}
            className="rounded-lg"
          >
            生成资源
          </Button>
          <Button
            size="small"
            loading={isRunning}
            onClick={() => handleStart("path_planning")}
            className="rounded-lg"
          >
            规划路径
          </Button>
        </div>
      </div>

      {/* Agent 节点流 */}
      <div className="flex items-center justify-center gap-0 overflow-x-auto py-2">
        {AGENT_DEFS.map((def, idx) => (
          <React.Fragment key={def.key}>
            <AgentNodeCard
              def={def}
              state={runData?.agents[def.key as AgentKey]}
            />
            {idx < AGENT_DEFS.length - 1 && (
              <FlowConnector
                active={
                  getConnectorState(def.key, AGENT_DEFS[idx + 1].key).active
                }
                completed={
                  getConnectorState(def.key, AGENT_DEFS[idx + 1].key).completed
                }
              />
            )}
          </React.Fragment>
        ))}
      </div>

      {/* 执行日志 */}
      {runData && runData.logs.length > 0 && (
        <div className="max-h-40 overflow-y-auto rounded-xl bg-slate-50 p-3 border border-slate-100">
          <Timeline
            className="!mt-0 !mb-0"
            items={runData.logs.slice(-10).map((log) => ({
              color:
                log.status === "completed"
                  ? "green"
                  : log.status === "failed"
                    ? "red"
                    : "blue",
              children: (
                <div className="flex items-center gap-2 text-xs">
                  <span className="text-slate-400 font-mono">
                    {new Date(log.timestamp).toLocaleTimeString("zh-CN", {
                      hour: "2-digit",
                      minute: "2-digit",
                      second: "2-digit",
                    })}
                  </span>
                  <Tag
                    className={`rounded-full border-0 text-[10px] ${
                      log.status === "completed"
                        ? "bg-emerald-50 text-emerald-600"
                        : log.status === "failed"
                          ? "bg-red-50 text-red-600"
                          : "bg-indigo-50 text-indigo-600"
                    }`}
                  >
                    {AGENT_DEFS.find((d) => d.key === log.agent)?.label ||
                      log.agent}
                  </Tag>
                  <span className="text-slate-600">{log.message}</span>
                </div>
              ),
            }))}
          />
        </div>
      )}

      {/* 空状态 */}
      {!runData && !isRunning && (
        <div className="text-center py-4 text-slate-400 text-xs">
          点击上方按钮启动多智能体协作，观察实时执行过程
        </div>
      )}

      {/* 完成状态 */}
      {runData && runData.status === "completed" && (
        <div className="text-center py-2">
          <Tag className="rounded-full bg-emerald-50 text-emerald-600 border-0 px-3 py-1">
            <CheckCircleOutlined /> 工作流执行完成 ·{" "}
            {runData.task_type === "profile_update"
              ? "画像分析"
              : runData.task_type === "resource_generation"
                ? "资源生成"
                : runData.task_type === "path_planning"
                  ? "路径规划"
                  : runData.task_type}
          </Tag>
        </div>
      )}
      {runData && runData.status === "failed" && (
        <div className="text-center py-2">
          <Tag className="rounded-full bg-red-50 text-red-600 border-0 px-3 py-1">
            <CloseCircleOutlined /> 执行失败
          </Tag>
        </div>
      )}
    </div>
  );
});

AgentFlowPanel.displayName = "AgentFlowPanel";

export default AgentFlowPanel;
