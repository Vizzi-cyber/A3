import React, { useState, useMemo, useEffect, useCallback } from "react";
import {
  Typography,
  Input,
  Button,
  Select,
  Tag,
  Space,
  Spin,
  message,
  Collapse,
  Tooltip,
  List,
  Empty,
  Popconfirm,
  Badge,
} from "antd";
import {
  BugOutlined,
  CodeOutlined,
  ThunderboltOutlined,
  MedicineBoxOutlined,
  SearchOutlined,
  BulbOutlined,
  CheckCircleOutlined,
  WarningOutlined,
  InfoCircleOutlined,
  ExclamationCircleOutlined,
  NodeIndexOutlined,
  HistoryOutlined,
  DeleteOutlined,
  ClockCircleOutlined,
  FileTextOutlined,
} from "@ant-design/icons";
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { useAppStore } from "../store";
import { api, profileApi, learningDataApi } from "../services/api";

const { TextArea } = Input;
const { Panel } = Collapse;

interface ErrorAnalysis {
  syntax_errors: Array<{
    line: number;
    description: string;
    fix: string;
  }>;
  logic_errors: Array<{
    description: string;
    impact: string;
    fix: string;
  }>;
  misconceptions: Array<{
    type: string;
    description: string;
    why_student_makes_this_mistake: string;
    correct_concept: string;
  }>;
  suggestions: string[];
  overall_assessment: string;
}

interface MisconceptionTrace {
  error_surface: string;
  thinking_process: string;
  root_cause: string;
  error_model: {
    type: string;
    subtype: string;
    description: string;
  };
  related_errors: string[];
  severity: string;
  confidence: number;
}

interface CorrectionStrategy {
  correction_strategy: {
    approach: string;
    steps: string[];
    key_points: string[];
  };
  socratic_questions: string[];
  comparison_examples: {
    wrong: string;
    correct: string;
    explanation: string;
  };
  practice_suggestions: string[];
  estimated_correction_time: string;
}

interface DiagnosisRecord {
  id: string;
  timestamp: number;
  code: string;
  language: string;
  errorAnalysis: ErrorAnalysis | null;
  misconceptionTrace: MisconceptionTrace | null;
  correctionStrategy: CorrectionStrategy | null;
  errorTypes: string[];
}

const HISTORY_KEY = "error_diagnosis_history";

const ErrorDiagnosis: React.FC = () => {
  const studentId = useAppStore((s) => s.studentId);
  const [code, setCode] = useState("");
  const [language, setLanguage] = useState("C");
  const [studentLevel, setStudentLevel] = useState("beginner");
  const [errorOutput, setErrorOutput] = useState("");
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<"catch" | "trace">("catch");
  const [showHistory, setShowHistory] = useState(false);
  const [history, setHistory] = useState<DiagnosisRecord[]>([]);

  const [errorAnalysis, setErrorAnalysis] = useState<ErrorAnalysis | null>(
    null,
  );
  const [misconceptionTrace, setMisconceptionTrace] =
    useState<MisconceptionTrace | null>(null);
  const [correctionStrategy, setCorrectionStrategy] =
    useState<CorrectionStrategy | null>(null);

  // 加载诊断历史
  useEffect(() => {
    try {
      const saved = localStorage.getItem(HISTORY_KEY);
      if (saved) {
        const parsed = JSON.parse(saved) as DiagnosisRecord[];
        setHistory(parsed);
      }
    } catch {}
  }, []);

  // 保存诊断历史
  const saveToHistory = useCallback(
    (record: DiagnosisRecord) => {
      const updated = [record, ...history].slice(0, 50); // 最多保留50条
      setHistory(updated);
      localStorage.setItem(HISTORY_KEY, JSON.stringify(updated));
    },
    [history],
  );

  // 删除单条记录
  const deleteRecord = useCallback(
    (id: string) => {
      const updated = history.filter((r) => r.id !== id);
      setHistory(updated);
      localStorage.setItem(HISTORY_KEY, JSON.stringify(updated));
      message.success("已删除");
    },
    [history],
  );

  // 清空所有记录
  const clearHistory = useCallback(() => {
    setHistory([]);
    localStorage.removeItem(HISTORY_KEY);
    message.success("已清空所有记录");
  }, []);

  // 从历史记录中恢复
  const restoreRecord = useCallback((record: DiagnosisRecord) => {
    setCode(record.code);
    setLanguage(record.language);
    setErrorAnalysis(record.errorAnalysis);
    setMisconceptionTrace(record.misconceptionTrace);
    setCorrectionStrategy(record.correctionStrategy);
    setActiveTab(record.errorAnalysis ? "catch" : "trace");
    setShowHistory(false);
    message.success("已恢复诊断记录");
  }, []);

  const handleCatchError = async () => {
    if (!code.trim()) {
      message.warning("请输入代码");
      return;
    }

    setLoading(true);
    try {
      const { data } = await api.post(
        "/error-catcher/analyze",
        {
          code,
          language,
          task: "catch_error",
          student_level: studentLevel,
          error_output: errorOutput || undefined,
        },
        { timeout: 120000 },
      );

      if (data.status === "success") {
        setErrorAnalysis(data.analysis);
        setActiveTab("catch");
        message.success("错误分析完成");

        // 收集错误类型
        const errorTypes: string[] = [];
        if (data.analysis.syntax_errors?.length) errorTypes.push("语法错误");
        if (data.analysis.logic_errors?.length) errorTypes.push("逻辑错误");
        if (data.analysis.misconceptions?.length) errorTypes.push("思维误区");

        // 保存到诊断历史
        const record: DiagnosisRecord = {
          id: `diag_${Date.now()}`,
          timestamp: Date.now(),
          code,
          language,
          errorAnalysis: data.analysis,
          misconceptionTrace: null,
          correctionStrategy: null,
          errorTypes,
        };
        saveToHistory(record);

        // 异步更新学生画像
        const conversationContext = `学生在错误诊断中提交了${language}代码，发现以下问题：${errorTypes.join("、")}。总体评估：${data.analysis.overall_assessment}`;
        profileApi
          .analyzeConversation(studentId, conversationContext)
          .catch(() => {});

        // 异步上报学习数据（记录错误诊断行为）
        learningDataApi
          .record({
            student_id: studentId,
            kp_id: "error_diagnosis",
            action: "error_analysis",
            duration: 0,
            progress: 0.1,
            meta: {
              error_types: errorTypes,
              syntax_count: data.analysis.syntax_errors?.length || 0,
              logic_count: data.analysis.logic_errors?.length || 0,
              misconception_count: data.analysis.misconceptions?.length || 0,
            },
          })
          .catch(() => {});
      } else {
        message.error(data.detail || "分析失败");
      }
    } catch (error: any) {
      message.error(error?.message || "请求失败，请检查网络");
    } finally {
      setLoading(false);
    }
  };

  const handleTraceError = async () => {
    if (!code.trim()) {
      message.warning("请输入代码");
      return;
    }

    // 根据错误分析结果动态确定错误类型
    let errorType = "思维误区";
    if (errorAnalysis) {
      if (errorAnalysis.syntax_errors?.length > 0) {
        errorType = "语法错误";
      } else if (errorAnalysis.logic_errors?.length > 0) {
        errorType = "逻辑错误";
      } else if (errorAnalysis.misconceptions?.length > 0) {
        errorType = "思维误区";
      }
    }

    setLoading(true);
    try {
      const { data } = await api.post(
        "/misconception-tracer/full-analysis",
        {
          code,
          error_type: errorType,
          error_description: errorAnalysis?.overall_assessment || "",
        },
        { timeout: 180000 },
      );

      if (data.status === "success") {
        setMisconceptionTrace(data.trace);
        setCorrectionStrategy(data.correction);
        setActiveTab("trace");
        message.success("思维溯源完成");

        // 更新当前分析的记录的溯源信息（匹配当前代码内容）
        if (history.length > 0) {
          const updated = history.map((r) =>
            r.code === code
              ? {
                  ...r,
                  misconceptionTrace: data.trace,
                  correctionStrategy: data.correction,
                }
              : r,
          );
          setHistory(updated);
          localStorage.setItem(HISTORY_KEY, JSON.stringify(updated));
        }

        // 异步更新学生画像（思维溯源信息）
        const traceContext = `思维溯源分析：错误类型=${data.trace.error_model?.type || "未知"}，根本原因=${data.trace.root_cause}，严重程度=${data.trace.severity}`;
        profileApi.analyzeConversation(studentId, traceContext).catch(() => {});

        // 上报思维溯源学习数据
        learningDataApi
          .record({
            student_id: studentId,
            kp_id: "error_diagnosis",
            action: "misconception_trace",
            duration: 0,
            progress: 0.2,
            meta: {
              error_model_type: data.trace.error_model?.type || "unknown",
              root_cause: data.trace.root_cause,
              severity: data.trace.severity,
              correction_time: data.correction?.estimated_correction_time,
            },
          })
          .catch(() => {});
      } else {
        message.error(data.detail || "分析失败");
      }
    } catch (error: any) {
      message.error(error?.message || "请求失败，请检查网络");
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "high":
        return "red";
      case "medium":
        return "orange";
      case "low":
        return "green";
      default:
        return "default";
    }
  };

  // 思维缺陷图谱数据（雷达图）
  const radarData = useMemo(() => {
    if (!errorAnalysis) return [];
    const dims = [
      { dimension: "语法理解", fullMark: 100 },
      { dimension: "逻辑思维", fullMark: 100 },
      { dimension: "概念掌握", fullMark: 100 },
      { dimension: "代码规范", fullMark: 100 },
      { dimension: "调试能力", fullMark: 100 },
      { dimension: "问题分析", fullMark: 100 },
    ];

    const syntaxCount = errorAnalysis.syntax_errors?.length || 0;
    const logicCount = errorAnalysis.logic_errors?.length || 0;
    const misconceptionCount = errorAnalysis.misconceptions?.length || 0;
    const totalErrors = syntaxCount + logicCount + misconceptionCount;

    // 基于错误数量的合理评分：无错误=95，每增加一个错误扣分，最低20
    const syntaxScore = Math.max(20, 95 - syntaxCount * 15);
    const logicScore = Math.max(20, 95 - logicCount * 20);
    const conceptScore = Math.max(20, 95 - misconceptionCount * 25);

    // 代码规范：有命名/格式相关语法错误则扣分
    const hasNormIssues = errorAnalysis.syntax_errors?.some(
      (e) =>
        e.description?.includes("命名") ||
        e.description?.includes("规范") ||
        e.description?.includes("格式"),
    );
    const normScore = hasNormIssues
      ? Math.max(30, 80 - syntaxCount * 10)
      : totalErrors === 0
        ? 95
        : 75;

    // 调试能力：提供了编译器错误信息说明有调试意识
    const debugScore = errorOutput.trim() ? 70 : totalErrors === 0 ? 90 : 55;

    // 问题分析：总体评估越详细说明分析能力越强
    const assessmentLen = errorAnalysis.overall_assessment?.length || 0;
    const analysisScore =
      assessmentLen > 100
        ? 80
        : assessmentLen > 50
          ? 65
          : totalErrors === 0
            ? 85
            : 50;

    return dims.map((d, i) => {
      const scores = [
        syntaxScore,
        logicScore,
        conceptScore,
        normScore,
        debugScore,
        analysisScore,
      ];
      return { ...d, score: scores[i], student: scores[i] };
    });
  }, [errorAnalysis, errorOutput]);

  // 思维溯源流程图节点
  const traceFlowNodes = useMemo(() => {
    if (!misconceptionTrace) return [];
    return [
      {
        id: "surface",
        label: "错误表象",
        content: misconceptionTrace.error_surface,
        color: "#ef4444",
        bgColor: "#fef2f2",
        borderColor: "#fca5a5",
      },
      {
        id: "thinking",
        label: "思维过程",
        content: misconceptionTrace.thinking_process,
        color: "#f97316",
        bgColor: "#fff7ed",
        borderColor: "#fdba74",
      },
      {
        id: "model",
        label: "错误模型",
        content: `${misconceptionTrace.error_model?.type || "未知"} - ${misconceptionTrace.error_model?.subtype || "未知"}`,
        color: "#a855f7",
        bgColor: "#faf5ff",
        borderColor: "#d8b4fe",
      },
      {
        id: "root",
        label: "根本原因",
        content: misconceptionTrace.root_cause,
        color: "#3b82f6",
        bgColor: "#eff6ff",
        borderColor: "#93c5fd",
      },
    ];
  }, [misconceptionTrace]);

  return (
    <div className="space-y-6 pb-8">
      {/* 顶部标题区 */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-10 h-10 rounded-lg bg-red-50 flex items-center justify-center text-red-500">
              <BugOutlined className="text-lg" />
            </div>
            <div>
              <Typography.Title level={4} className="!m-0 !text-gray-900">
                错误诊断系统
              </Typography.Title>
              <Typography.Text className="text-gray-500 text-sm">
                智能捕捉代码错误 · 溯源思维误区 · 生成纠正策略
              </Typography.Text>
            </div>
          </div>
          <div className="hidden md:flex items-center gap-4">
            <div className="text-center">
              <div className="text-lg font-semibold text-gray-900">
                {errorAnalysis?.syntax_errors?.length || 0}
              </div>
              <div className="text-xs text-gray-400">语法错误</div>
            </div>
            <div className="w-px h-8 bg-gray-200" />
            <div className="text-center">
              <div className="text-lg font-semibold text-gray-900">
                {errorAnalysis?.logic_errors?.length || 0}
              </div>
              <div className="text-xs text-gray-400">逻辑错误</div>
            </div>
            <div className="w-px h-8 bg-gray-200" />
            <div className="text-center">
              <div className="text-lg font-semibold text-gray-900">
                {errorAnalysis?.misconceptions?.length || 0}
              </div>
              <div className="text-xs text-gray-400">思维误区</div>
            </div>
          </div>
        </div>
      </div>

      {/* 主内容区 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
        {/* 左侧：代码输入 */}
        <div className="flex flex-col gap-4 h-full">
          <div className="bg-white rounded-lg border border-gray-200 p-5 flex-1 flex flex-col">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <CodeOutlined className="text-gray-400" />
                <span className="font-medium text-gray-700">代码输入</span>
              </div>
              <Space>
                <Select
                  value={language}
                  onChange={setLanguage}
                  style={{ width: 100 }}
                  size="small"
                  options={[{ value: "C", label: "C语言" }]}
                />
                <Select
                  value={studentLevel}
                  onChange={setStudentLevel}
                  style={{ width: 100 }}
                  size="small"
                  options={[
                    { value: "beginner", label: "初学者" },
                    { value: "intermediate", label: "中级" },
                    { value: "advanced", label: "高级" },
                  ]}
                />
              </Space>
            </div>
            <TextArea
              value={code}
              onChange={(e) => setCode(e.target.value)}
              placeholder={
                '请输入C语言代码...\n\n示例：\n#include <stdio.h>\nint main() {\n    int a = 1;\n    if(a = 1) {\n        printf("equal");\n    }\n    return 0;\n}'
              }
              style={{
                flex: 1,
                minHeight: 300,
                fontFamily: "'Fira Code', 'Source Code Pro', monospace",
                fontSize: 13,
                lineHeight: 1.6,
              }}
              className="rounded-lg"
            />
          </div>

          <div className="bg-white rounded-lg border border-gray-200 p-5">
            <div className="flex items-center gap-2 mb-3">
              <InfoCircleOutlined className="text-gray-400" />
              <span className="text-sm text-gray-600">编译器错误信息</span>
              <span className="text-xs text-gray-400">(可选)</span>
            </div>
            <TextArea
              value={errorOutput}
              onChange={(e) => setErrorOutput(e.target.value)}
              placeholder="如果有编译器错误信息，请粘贴在这里..."
              style={{
                height: 80,
                fontFamily: "'Fira Code', 'Source Code Pro', monospace",
                fontSize: 12,
              }}
              className="rounded-lg"
            />
          </div>

          <div className="flex gap-3 mt-auto">
            <Button
              type="primary"
              icon={<SearchOutlined />}
              onClick={handleCatchError}
              loading={loading}
              size="large"
              className="flex-1 h-10"
            >
              捕捉错误
            </Button>
            <Button
              icon={<BulbOutlined />}
              onClick={handleTraceError}
              loading={loading}
              disabled={!errorAnalysis}
              size="large"
              className="flex-1 h-10"
            >
              溯源思维
            </Button>
          </div>
        </div>

        {/* 右侧：分析结果 */}
        <div className="flex flex-col gap-4">
          {/* Tab切换 */}
          <div className="bg-white rounded-lg border border-gray-200 p-1 flex">
            <button
              onClick={() => setActiveTab("catch")}
              className={`flex-1 flex items-center justify-center gap-2 py-2 rounded text-sm font-medium transition-colors ${
                activeTab === "catch"
                  ? "bg-gray-900 text-white"
                  : "text-gray-500 hover:text-gray-700 hover:bg-gray-50"
              }`}
            >
              <BugOutlined />
              错误分析
            </button>
            <button
              onClick={() => setActiveTab("trace")}
              className={`flex-1 flex items-center justify-center gap-2 py-2 rounded text-sm font-medium transition-colors ${
                activeTab === "trace"
                  ? "bg-gray-900 text-white"
                  : "text-gray-500 hover:text-gray-700 hover:bg-gray-50"
              }`}
            >
              <ThunderboltOutlined />
              思维溯源
            </button>
          </div>

          {/* 内容区 */}
          <div className="bg-white rounded-lg border border-gray-200 p-5 min-h-[400px] max-h-[700px] overflow-y-auto flex-1">
            <Spin spinning={loading}>
              {activeTab === "catch" ? (
                errorAnalysis ? (
                  <div className="space-y-4">
                    {/* 总体评估 */}
                    <div className="p-4 rounded-lg bg-gray-50 border border-gray-200">
                      <div className="flex items-center gap-2 mb-2">
                        <InfoCircleOutlined className="text-gray-500" />
                        <span className="font-medium text-gray-700 text-sm">
                          总体评估
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 m-0">
                        {errorAnalysis.overall_assessment}
                      </p>
                    </div>

                    {/* 语法错误 */}
                    {errorAnalysis.syntax_errors?.length > 0 && (
                      <Collapse
                        defaultActiveKey={["syntax"]}
                        className="bg-transparent border-0"
                      >
                        <Panel
                          header={
                            <div className="flex items-center gap-2">
                              <ExclamationCircleOutlined className="text-red-500" />
                              <span className="font-medium text-gray-700">
                                语法错误
                              </span>
                              <Tag color="red">
                                {errorAnalysis.syntax_errors.length}
                              </Tag>
                            </div>
                          }
                          key="syntax"
                          className="bg-white rounded-lg border border-gray-200 mb-2"
                        >
                          {errorAnalysis.syntax_errors.map((err, idx) => (
                            <div
                              key={idx}
                              className="p-3 rounded bg-red-50 border border-red-100 mb-2 last:mb-0"
                            >
                              <div className="flex items-center gap-2 mb-1">
                                <Tag color="red" className="text-xs">
                                  第{err.line}行
                                </Tag>
                                <span className="font-medium text-sm text-gray-700">
                                  {err.description}
                                </span>
                              </div>
                              <div className="flex items-start gap-2 text-xs text-gray-500">
                                <CheckCircleOutlined className="text-green-500 mt-0.5" />
                                <span>修复建议：{err.fix}</span>
                              </div>
                            </div>
                          ))}
                        </Panel>
                      </Collapse>
                    )}

                    {/* 逻辑错误 */}
                    {errorAnalysis.logic_errors?.length > 0 && (
                      <Collapse
                        defaultActiveKey={["logic"]}
                        className="bg-transparent border-0"
                      >
                        <Panel
                          header={
                            <div className="flex items-center gap-2">
                              <WarningOutlined className="text-orange-500" />
                              <span className="font-medium text-gray-700">
                                逻辑错误
                              </span>
                              <Tag color="orange">
                                {errorAnalysis.logic_errors.length}
                              </Tag>
                            </div>
                          }
                          key="logic"
                          className="bg-white rounded-lg border border-gray-200 mb-2"
                        >
                          {errorAnalysis.logic_errors.map((err, idx) => (
                            <div
                              key={idx}
                              className="p-3 rounded bg-orange-50 border border-orange-100 mb-2 last:mb-0"
                            >
                              <div className="font-medium text-sm text-gray-700 mb-1">
                                {err.description}
                              </div>
                              <div className="text-xs text-gray-500 mb-1">
                                <span className="font-medium">影响：</span>
                                {err.impact}
                              </div>
                              <div className="flex items-start gap-2 text-xs text-gray-500">
                                <CheckCircleOutlined className="text-green-500 mt-0.5" />
                                <span>修复建议：{err.fix}</span>
                              </div>
                            </div>
                          ))}
                        </Panel>
                      </Collapse>
                    )}

                    {/* 思维误区 */}
                    {errorAnalysis.misconceptions?.length > 0 && (
                      <Collapse
                        defaultActiveKey={["misconceptions"]}
                        className="bg-transparent border-0"
                      >
                        <Panel
                          header={
                            <div className="flex items-center gap-2">
                              <ThunderboltOutlined className="text-blue-500" />
                              <span className="font-medium text-gray-700">
                                思维误区
                              </span>
                              <Tag color="purple">
                                {errorAnalysis.misconceptions.length}
                              </Tag>
                            </div>
                          }
                          key="misconceptions"
                          className="bg-white rounded-lg border border-gray-200 mb-2"
                        >
                          {errorAnalysis.misconceptions.map((m, idx) => (
                            <div
                              key={idx}
                              className="p-3 rounded bg-purple-50 border border-purple-100 mb-2 last:mb-0"
                            >
                              <Tag color="purple" className="mb-2">
                                {m.type}
                              </Tag>
                              <div className="font-medium text-sm text-gray-700 mb-2">
                                {m.description}
                              </div>
                              <div className="text-xs text-gray-500 mb-1">
                                <span className="font-medium text-gray-600">
                                  为什么犯这个错：
                                </span>
                                {m.why_student_makes_this_mistake}
                              </div>
                              <div className="text-xs text-gray-500">
                                <span className="font-medium text-gray-600">
                                  正确概念：
                                </span>
                                {m.correct_concept}
                              </div>
                            </div>
                          ))}
                        </Panel>
                      </Collapse>
                    )}

                    {/* 建议 */}
                    {errorAnalysis.suggestions?.length > 0 && (
                      <div className="p-4 rounded-lg bg-green-50 border border-green-200">
                        <div className="flex items-center gap-2 mb-3">
                          <BulbOutlined className="text-green-600" />
                          <span className="font-medium text-gray-700 text-sm">
                            改进建议
                          </span>
                        </div>
                        <ul className="m-0 pl-4 space-y-1">
                          {errorAnalysis.suggestions.map((s, idx) => (
                            <li
                              key={idx}
                              className="text-sm text-gray-600 list-disc"
                            >
                              {s}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* 思维缺陷图谱（雷达图） */}
                    {radarData.length > 0 && (
                      <div className="p-4 rounded-lg bg-blue-50 border border-blue-200">
                        <div className="flex items-center gap-2 mb-3">
                          <NodeIndexOutlined className="text-blue-600" />
                          <span className="font-medium text-gray-700 text-sm">
                            思维缺陷图谱
                          </span>
                        </div>
                        <ResponsiveContainer width="100%" height={280}>
                          <RadarChart
                            data={radarData}
                            cx="50%"
                            cy="50%"
                            outerRadius="70%"
                          >
                            <PolarGrid stroke="#e5e7eb" />
                            <PolarAngleAxis
                              dataKey="dimension"
                              tick={{ fontSize: 12, fill: "#6b7280" }}
                            />
                            <PolarRadiusAxis
                              angle={30}
                              domain={[0, 100]}
                              tick={{ fontSize: 10 }}
                            />
                            <Radar
                              name="能力评估"
                              dataKey="score"
                              stroke="#3b82f6"
                              fill="#3b82f6"
                              fillOpacity={0.3}
                            />
                            <Legend wrapperStyle={{ fontSize: 12 }} />
                          </RadarChart>
                        </ResponsiveContainer>
                        <div className="text-xs text-gray-500 text-center mt-2">
                          分数越低表示该维度存在较大改进空间
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="flex flex-col items-center justify-center py-16 text-gray-400">
                    <CodeOutlined className="text-4xl mb-4 text-gray-300" />
                    <div className="text-sm font-medium text-gray-500 mb-1">
                      输入代码开始分析
                    </div>
                    <div className="text-xs text-gray-400">
                      点击"捕捉错误"按钮进行错误分析
                    </div>
                  </div>
                )
              ) : misconceptionTrace ? (
                <div className="space-y-4">
                  {/* 错误模型 */}
                  <div className="p-4 rounded-lg bg-gray-50 border border-gray-200">
                    <div className="flex items-center gap-3 mb-3">
                      <Tag
                        color={getSeverityColor(misconceptionTrace.severity)}
                      >
                        严重程度: {misconceptionTrace.severity}
                      </Tag>
                      <Tag>
                        置信度:{" "}
                        {Math.round(misconceptionTrace.confidence * 100)}%
                      </Tag>
                    </div>
                    <div className="flex items-center gap-2 mb-2">
                      <ThunderboltOutlined className="text-gray-500" />
                      <span className="font-medium text-gray-700 text-sm">
                        {misconceptionTrace.error_model?.type || "未知"}
                      </span>
                      <span className="text-xs text-gray-400">
                        - {misconceptionTrace.error_model?.subtype || "未知"}
                      </span>
                    </div>
                    <p className="text-xs text-gray-500 m-0">
                      {misconceptionTrace.error_model?.description || ""}
                    </p>
                  </div>

                  {/* 分析详情 */}
                  <div className="space-y-3">
                    <div className="p-3 rounded-lg bg-white border border-gray-200">
                      <div className="text-xs font-medium text-gray-400 mb-1">
                        错误表象
                      </div>
                      <div className="text-sm text-gray-600">
                        {misconceptionTrace.error_surface}
                      </div>
                    </div>
                    <div className="p-3 rounded-lg bg-white border border-gray-200">
                      <div className="text-xs font-medium text-gray-400 mb-1">
                        学生思维过程
                      </div>
                      <div className="text-sm text-gray-600">
                        {misconceptionTrace.thinking_process}
                      </div>
                    </div>
                    <div className="p-3 rounded-lg bg-white border border-gray-200">
                      <div className="text-xs font-medium text-gray-400 mb-1">
                        根本原因
                      </div>
                      <div className="text-sm text-gray-600">
                        {misconceptionTrace.root_cause}
                      </div>
                    </div>
                  </div>

                  {/* 关联错误 */}
                  {misconceptionTrace.related_errors?.length > 0 && (
                    <div className="p-3 rounded-lg bg-orange-50 border border-orange-200">
                      <div className="text-xs font-medium text-orange-600 mb-2">
                        关联错误
                      </div>
                      <ul className="m-0 pl-4 space-y-1">
                        {misconceptionTrace.related_errors.map((err, idx) => (
                          <li
                            key={idx}
                            className="text-xs text-gray-600 list-disc"
                          >
                            {err}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* 纠正策略 */}
                  {correctionStrategy && (
                    <div className="p-4 rounded-lg bg-green-50 border border-green-200">
                      <div className="flex items-center gap-2 mb-3">
                        <MedicineBoxOutlined className="text-green-600" />
                        <span className="font-medium text-gray-700 text-sm">
                          纠正策略
                        </span>
                      </div>
                      <div className="text-sm text-gray-600 mb-3">
                        {correctionStrategy.correction_strategy.approach}
                      </div>
                      <div className="mb-3">
                        <div className="text-xs font-medium text-gray-500 mb-2">
                          引导性问题
                        </div>
                        <ul className="m-0 pl-4 space-y-1">
                          {correctionStrategy.socratic_questions.map(
                            (q, idx) => (
                              <li
                                key={idx}
                                className="text-xs text-gray-600 list-decimal"
                              >
                                {q}
                              </li>
                            ),
                          )}
                        </ul>
                      </div>
                      <div className="flex items-center gap-2 text-xs text-green-600">
                        <span>预计纠正时间：</span>
                        <Tag color="success">
                          {correctionStrategy.estimated_correction_time} 分钟
                        </Tag>
                      </div>
                    </div>
                  )}

                  {/* 思维溯源流程图 */}
                  {traceFlowNodes.length > 0 && (
                    <div className="p-4 rounded-lg bg-indigo-50 border border-indigo-200">
                      <div className="flex items-center gap-2 mb-4">
                        <NodeIndexOutlined className="text-indigo-600" />
                        <span className="font-medium text-gray-700 text-sm">
                          思维溯源流程图
                        </span>
                      </div>
                      <div className="flex flex-col items-center gap-0">
                        {traceFlowNodes.map((node, idx) => (
                          <React.Fragment key={node.id}>
                            <div
                              className="w-full max-w-md p-3 rounded-lg border text-center"
                              style={{
                                backgroundColor: node.bgColor,
                                borderColor: node.borderColor,
                              }}
                            >
                              <div
                                className="text-xs font-semibold mb-1 uppercase tracking-wide"
                                style={{ color: node.color }}
                              >
                                {node.label}
                              </div>
                              <div className="text-sm text-gray-700 leading-relaxed">
                                {node.content}
                              </div>
                            </div>
                            {idx < traceFlowNodes.length - 1 && (
                              <div className="flex flex-col items-center my-1">
                                <div className="w-0.5 h-4 bg-gray-300" />
                                <div
                                  className="w-0 h-0 border-l-[6px] border-l-transparent border-r-[6px] border-r-transparent border-t-[8px]"
                                  style={{ borderTopColor: "#9ca3af" }}
                                />
                              </div>
                            )}
                          </React.Fragment>
                        ))}
                      </div>
                      <div className="text-xs text-gray-500 text-center mt-3">
                        从错误表象到根本原因的完整溯源路径
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center py-16 text-gray-400">
                  <BulbOutlined className="text-4xl mb-4 text-gray-300" />
                  <div className="text-sm font-medium text-gray-500 mb-1">
                    先进行错误分析
                  </div>
                  <div className="text-xs text-gray-400">
                    然后点击"溯源思维"深入分析
                  </div>
                </div>
              )}
            </Spin>
          </div>
        </div>
      </div>

      {/* 诊断记录面板 */}
      <div className="bg-white rounded-lg border border-gray-200 p-5">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <HistoryOutlined className="text-gray-400" />
            <span className="font-medium text-gray-700">诊断记录</span>
            <Badge
              count={history.length}
              style={{ backgroundColor: "#4f46e5" }}
            />
          </div>
          <Space>
            <Button
              size="small"
              icon={<HistoryOutlined />}
              onClick={() => setShowHistory(!showHistory)}
              className="text-gray-500"
            >
              {showHistory ? "收起" : "展开"}
            </Button>
            {history.length > 0 && (
              <Popconfirm
                title="确定清空所有诊断记录？"
                onConfirm={clearHistory}
                okText="确认"
                cancelText="取消"
              >
                <Button size="small" danger icon={<DeleteOutlined />}>
                  清空
                </Button>
              </Popconfirm>
            )}
          </Space>
        </div>

        {showHistory && (
          <div className="max-h-96 overflow-y-auto">
            {history.length === 0 ? (
              <Empty
                description="暂无诊断记录"
                image={Empty.PRESENTED_IMAGE_SIMPLE}
              />
            ) : (
              <List
                dataSource={history}
                renderItem={(record) => (
                  <List.Item
                    className="hover:bg-gray-50 rounded-lg px-3 cursor-pointer transition-colors"
                    onClick={() => restoreRecord(record)}
                    actions={[
                      <Popconfirm
                        key="delete"
                        title="确定删除此记录？"
                        onConfirm={(e) => {
                          e?.stopPropagation();
                          deleteRecord(record.id);
                        }}
                        onCancel={(e) => e?.stopPropagation()}
                        okText="确认"
                        cancelText="取消"
                      >
                        <Button
                          type="text"
                          size="small"
                          danger
                          icon={<DeleteOutlined />}
                          onClick={(e) => e.stopPropagation()}
                        />
                      </Popconfirm>,
                    ]}
                  >
                    <List.Item.Meta
                      avatar={
                        <div className="w-8 h-8 rounded-lg bg-red-50 flex items-center justify-center">
                          <BugOutlined className="text-red-500" />
                        </div>
                      }
                      title={
                        <div className="flex items-center gap-2">
                          <span className="text-sm text-gray-700 font-medium truncate max-w-48">
                            {record.code.split("\n")[0] || "未命名代码"}
                          </span>
                          {record.errorTypes.map((type) => (
                            <Tag key={type} color="red" className="text-xs">
                              {type}
                            </Tag>
                          ))}
                        </div>
                      }
                      description={
                        <div className="flex items-center gap-3 text-xs text-gray-400">
                          <span className="flex items-center gap-1">
                            <ClockCircleOutlined />
                            {new Date(record.timestamp).toLocaleString(
                              "zh-CN",
                              {
                                month: "short",
                                day: "numeric",
                                hour: "2-digit",
                                minute: "2-digit",
                              },
                            )}
                          </span>
                          <span className="flex items-center gap-1">
                            <FileTextOutlined />
                            {record.language}
                          </span>
                          {record.correctionStrategy && (
                            <Tag color="green" className="text-xs">
                              已溯源
                            </Tag>
                          )}
                        </div>
                      }
                    />
                  </List.Item>
                )}
              />
            )}
          </div>
        )}

        {!showHistory && history.length > 0 && (
          <div className="text-xs text-gray-400">
            共 {history.length} 条记录，点击「展开」查看详情，点击记录可恢复
          </div>
        )}
      </div>
    </div>
  );
};

export default ErrorDiagnosis;
