import React, { useState } from "react";
import { Modal, Input, Button, Spin, Tag, message } from "antd";
import { RobotOutlined, SendOutlined, ReloadOutlined } from "@ant-design/icons";
import { useCircuitStore } from "./store";
import { useAppStore } from "../../store";
import { api } from "../../services/api";

interface AiAnalysisDialogProps {
  open: boolean;
  onClose: () => void;
}

const AiAnalysisDialog: React.FC<AiAnalysisDialogProps> = ({
  open,
  onClose,
}) => {
  const { components, wires, simulationResult } = useCircuitStore();
  const studentId = useAppStore((s) => s.studentId);
  const [question, setQuestion] = useState("");
  const [analysis, setAnalysis] = useState("");
  const [loading, setLoading] = useState(false);

  const quickQuestions = [
    "这个电路的功能是什么？",
    "电路中各元件的作用是什么？",
    "如何优化这个电路？",
    "这个电路有什么潜在问题？",
  ];

  const handleAnalyze = async (q?: string) => {
    const questionText = q || question || "请分析这个电路";
    if (components.length === 0) {
      message.warning("请先添加电路元件");
      return;
    }

    setLoading(true);
    setAnalysis("");

    try {
      const netlist = components
        .filter((c) => c.type !== "ground")
        .map((c, i) => ({
          name: `${c.type[0].toUpperCase()}${i + 1}`,
          type: c.type,
          node1: c.terminals[0] ? Math.round(c.terminals[0].position.x) : 0,
          node2: c.terminals[1] ? Math.round(c.terminals[1].position.x) : 1,
          value: c.value,
        }));

      const res = await api.post("/circuit-analysis/analyze", {
        netlist,
        node_voltages: simulationResult?.nodeVoltages || {},
        branch_currents: simulationResult?.branchCurrents || {},
        student_question: questionText,
        student_level: "beginner",
      });

      const data = res.data;
      if (data.status === "success") {
        setAnalysis(data.analysis || "分析完成");
      } else {
        setAnalysis("分析失败，请重试");
      }
    } catch (err: any) {
      setAnalysis(`分析出错: ${err.message || "网络错误"}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal
      title={
        <div className="flex items-center gap-2">
          <RobotOutlined className="text-indigo-500" />
          <span>AI 电路分析</span>
        </div>
      }
      open={open}
      onCancel={onClose}
      footer={null}
      width={700}
      styles={{ body: { maxHeight: "60vh", overflowY: "auto" } }}
    >
      {/* Quick questions */}
      <div className="mb-4">
        <div className="text-xs text-gray-500 mb-2">快捷问题</div>
        <div className="flex flex-wrap gap-2">
          {quickQuestions.map((q) => (
            <Tag
              key={q}
              className="cursor-pointer hover:bg-indigo-50"
              onClick={() => {
                setQuestion(q);
                handleAnalyze(q);
              }}
            >
              {q}
            </Tag>
          ))}
        </div>
      </div>

      {/* Input */}
      <div className="flex gap-2 mb-4">
        <Input
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="输入你的问题..."
          onPressEnter={() => handleAnalyze()}
        />
        <Button
          type="primary"
          icon={<SendOutlined />}
          onClick={() => handleAnalyze()}
          loading={loading}
          className="!bg-indigo-500 !border-indigo-500"
        >
          分析
        </Button>
      </div>

      {/* Results */}
      {loading && (
        <div className="flex items-center justify-center py-8">
          <Spin tip="AI 正在分析电路..." />
        </div>
      )}

      {analysis && !loading && (
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">分析结果</span>
            <Button
              size="small"
              icon={<ReloadOutlined />}
              onClick={() => handleAnalyze()}
            >
              重新分析
            </Button>
          </div>
          <div className="text-sm text-gray-600 whitespace-pre-wrap leading-relaxed">
            {analysis}
          </div>
        </div>
      )}

      {!analysis && !loading && (
        <div className="text-center py-8 text-gray-400">
          <RobotOutlined className="text-3xl mb-2" />
          <div className="text-sm">点击分析或选择快捷问题开始</div>
        </div>
      )}
    </Modal>
  );
};

export default AiAnalysisDialog;
