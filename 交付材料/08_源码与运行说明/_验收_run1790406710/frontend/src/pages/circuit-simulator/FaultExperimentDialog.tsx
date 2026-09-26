import React, { useState } from "react";
import { Modal, Button, Radio, Spin, Tag, message, Divider } from "antd";
import {
  ExperimentOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  RobotOutlined,
  DownloadOutlined,
  CopyOutlined,
} from "@ant-design/icons";
import { useCircuitStore, PRESET_CIRCUITS } from "./store";
import { FAULT_TEMPLATES, FaultTemplate } from "./fault-templates";
import { circuitApi, learningDataApi } from "../../services/api";
import { useAppStore } from "../../store";

interface FaultExperimentDialogProps {
  open: boolean;
  onClose: () => void;
}

/**
 * 故障诊断实验（AIC "AI+学科交叉"亮点功能）
 * 流程：选择故障实验 → 加载故障电路并仿真 → 观察测量异常 → 诊断原因 → 判定 + AI 解析
 */
const FaultExperimentDialog: React.FC<FaultExperimentDialogProps> = ({
  open,
  onClose,
}) => {
  const { components, wires, simulationResult, loadFault, simulate } =
    useCircuitStore();
  const studentId = useAppStore((s) => s.studentId);
  const [selected, setSelected] = useState<FaultTemplate | null>(null);
  const [answer, setAnswer] = useState<string>("");
  const [submitted, setSubmitted] = useState(false);
  const [aiAnalysis, setAiAnalysis] = useState("");
  const [aiLoading, setAiLoading] = useState(false);
  const [report, setReport] = useState("");

  // 选择实验并加载故障电路
  const handleSelect = (fault: FaultTemplate) => {
    setSelected(fault);
    setAnswer("");
    setSubmitted(false);
    setAiAnalysis("");
    loadFault(fault.basedOn, fault.overrides);
    // 加载后自动仿真，让学生直接看到异常测量值
    setTimeout(() => simulate(), 100);
    // 实验行为埋点（试点数据分析）
    if (studentId) {
      learningDataApi
        .submitExperiment({
          student_id: studentId,
          experiment_type: "circuit_fault",
          action: "run",
          detail: { fault_id: fault.id, fault_name: fault.name },
        })
        .catch(() => {});
    }
  };

  // 本地规则判定
  const handleSubmit = () => {
    if (!answer) {
      message.warning("请先选择故障原因");
      return;
    }
    setSubmitted(true);
    // 实验行为埋点（试点数据分析）
    const correct = !!selected?.options.find((o) => o.label === answer)
      ?.correct;
    if (studentId && selected) {
      learningDataApi
        .submitExperiment({
          student_id: studentId,
          experiment_type: "circuit_fault",
          action: "submit",
          detail: { fault_id: selected.id, answer, correct },
        })
        .catch(() => {});
    }
  };

  // AI 详细解析（后端诊断模式）
  const handleAiAnalysis = async () => {
    if (!selected) return;
    setAiLoading(true);
    setAiAnalysis("");
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

      const correctOption = selected.options.find((o) => o.correct);
      const res = await circuitApi.analyze({
        netlist,
        node_voltages: simulationResult?.nodeVoltages || {},
        branch_currents: simulationResult?.branchCurrents || {},
        is_diagnosis: true,
        fault_description: selected.aiPrompt,
        student_answer: answer,
        expected_answer: correctOption?.label || "",
        student_level: "intermediate",
      });
      if (res.data.status === "success") {
        setAiAnalysis(res.data.analysis || "解析完成");
      } else {
        setAiAnalysis("AI 解析失败，请重试");
      }
    } catch (err: any) {
      setAiAnalysis(`解析出错: ${err.message || "网络错误"}`);
    } finally {
      setAiLoading(false);
    }
  };

  // 生成实验报告（Markdown）
  const buildReport = (): string => {
    if (!selected || !chosenOption) return "";
    const date = new Date().toISOString().slice(0, 10);
    const correctOption = selected.options.find((o) => o.correct);
    const lines = [
      "# 电路故障诊断实验报告",
      "",
      `**实验名称**：${selected.name}`,
      `**实验日期**：${date}`,
      `**难度等级**：${selected.difficulty}`,
      "",
      "## 一、实验任务",
      selected.task,
      "",
      "## 二、故障现象观察",
      selected.phenomenon,
      "",
      "## 三、正常电路参考",
      selected.normalValues,
      "",
      "## 四、诊断结论",
      `- 我的诊断：**${answer}**`,
      `- 判定结果：${chosenOption.correct ? "✅ 诊断正确" : "❌ 诊断有误"}`,
      `- 标准答案：${correctOption?.label || ""}`,
      "",
      "### 解析",
      chosenOption.explanation,
      "",
    ];
    if (aiAnalysis) {
      lines.push("## 五、AI 评估", aiAnalysis, "");
    }
    lines.push("## 六、实验心得", "", "（请写下你在本实验中的收获与思考）", "");
    return lines.join("\n");
  };

  const handleGenerateReport = () => {
    const md = buildReport();
    if (md) {
      setReport(md);
      message.success("实验报告已生成");
    }
  };

  const handleDownloadReport = () => {
    if (!report) return;
    const blob = new Blob([report], { type: "text/markdown;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `故障实验报告_${selected?.id || "circuit"}_${new Date().toISOString().slice(0, 10)}.md`;
    a.click();
    URL.revokeObjectURL(url);
    message.success("报告已下载");
  };

  const handleCopyReport = async () => {
    if (!report) return;
    try {
      await navigator.clipboard.writeText(report);
      message.success("报告已复制到剪贴板");
    } catch {
      message.warning("复制失败，请手动选择复制");
    }
  };

  const chosenOption = selected?.options.find((o) => o.label === answer);

  return (
    <Modal
      title={
        <div className="flex items-center gap-2">
          <ExperimentOutlined className="text-orange-500" />
          <span>故障诊断实验</span>
          <Tag color="orange" className="ml-1">
            AI+虚拟实验实训
          </Tag>
        </div>
      }
      open={open}
      onCancel={onClose}
      footer={null}
      width={760}
      styles={{ body: { maxHeight: "68vh", overflowY: "auto" } }}
    >
      {/* 步骤1：选择实验 */}
      {!selected && (
        <div>
          <div className="text-sm text-gray-600 mb-3">
            选择故障实验：加载故障电路后观察测量数据异常，诊断故障原因（实验闭环：现象观察
            → 假设 → 验证）
          </div>
          <div className="space-y-3">
            {FAULT_TEMPLATES.map((f) => (
              <div
                key={f.id}
                className="border border-gray-200 rounded-lg p-3 hover:border-orange-300 hover:bg-orange-50/50 cursor-pointer transition-colors"
                onClick={() => handleSelect(f)}
              >
                <div className="flex items-center justify-between">
                  <span className="font-medium text-gray-800">{f.name}</span>
                  <Tag color={f.difficulty === "入门" ? "green" : "orange"}>
                    {f.difficulty}
                  </Tag>
                </div>
                <div className="text-xs text-gray-500 mt-1">{f.task}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 步骤2-3：诊断与判定 */}
      {selected && (
        <div>
          <div className="flex items-center justify-between mb-2">
            <span className="font-medium text-gray-800">{selected.name}</span>
            <Button size="small" onClick={() => setSelected(null)}>
              换一个实验
            </Button>
          </div>

          {/* 实验现象 */}
          <div className="bg-orange-50 border border-orange-200 rounded-lg p-3 mb-3">
            <div className="text-xs font-medium text-orange-600 mb-1">
              📋 实验任务
            </div>
            <div className="text-sm text-gray-700">{selected.task}</div>
            <div className="text-xs text-orange-600/80 mt-2">
              故障现象：{selected.phenomenon}
            </div>
            <div className="text-xs text-green-600/80 mt-1">
              {selected.normalValues}
            </div>
          </div>

          {/* 诊断选项 */}
          <div className="mb-3">
            <div className="text-xs font-medium text-gray-600 mb-2">
              请选择故障原因：
            </div>
            <Radio.Group
              value={answer}
              onChange={(e) => {
                setAnswer(e.target.value);
                setSubmitted(false);
              }}
              className="w-full"
            >
              <div className="space-y-2">
                {selected.options.map((o) => (
                  <Radio
                    key={o.label}
                    value={o.label}
                    className="block !items-start"
                  >
                    <div
                      className={`text-sm ${
                        submitted && o.correct
                          ? "text-green-600"
                          : "text-gray-700"
                      }`}
                    >
                      {o.label}
                    </div>
                  </Radio>
                ))}
              </div>
            </Radio.Group>
          </div>

          {/* 判定结果 */}
          {submitted && chosenOption && (
            <div
              className={`rounded-lg p-3 mb-3 ${
                chosenOption.correct
                  ? "bg-green-50 border border-green-200"
                  : "bg-red-50 border border-red-200"
              }`}
            >
              <div className="flex items-center gap-2 mb-1">
                {chosenOption.correct ? (
                  <>
                    <CheckCircleOutlined className="text-green-500" />
                    <span className="font-medium text-green-700">
                      ✅ 诊断正确！
                    </span>
                  </>
                ) : (
                  <>
                    <CloseCircleOutlined className="text-red-500" />
                    <span className="font-medium text-red-700">
                      ❌ 诊断有误，再想想
                    </span>
                  </>
                )}
              </div>
              <div className="text-sm text-gray-600">
                {chosenOption.explanation}
              </div>
            </div>
          )}

          {/* 操作按钮 */}
          <div className="flex gap-2">
            <Button
              type="primary"
              onClick={handleSubmit}
              disabled={!answer}
              className="!bg-orange-500 !border-orange-500"
            >
              提交诊断
            </Button>
            <Button
              icon={<RobotOutlined />}
              onClick={handleAiAnalysis}
              loading={aiLoading}
              disabled={!submitted}
            >
              AI 详细解析
            </Button>
            <Button
              icon={<DownloadOutlined />}
              onClick={handleGenerateReport}
              disabled={!submitted}
            >
              生成实验报告
            </Button>
          </div>

          {/* 实验报告预览 */}
          {report && (
            <div className="mt-3 bg-white border border-gray-200 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700">
                  📄 实验报告预览
                </span>
                <div className="flex gap-2">
                  <Button
                    size="small"
                    icon={<DownloadOutlined />}
                    onClick={handleDownloadReport}
                  >
                    下载 .md
                  </Button>
                  <Button
                    size="small"
                    icon={<CopyOutlined />}
                    onClick={handleCopyReport}
                  >
                    复制
                  </Button>
                </div>
              </div>
              <pre className="text-xs text-gray-600 whitespace-pre-wrap bg-gray-50 rounded p-3 max-h-64 overflow-auto">
                {report}
              </pre>
            </div>
          )}

          {/* AI 解析 */}
          {aiLoading && (
            <div className="flex items-center justify-center py-6 mt-3">
              <Spin tip="AI 正在评估你的诊断...">
                <div style={{ padding: 30 }} />
              </Spin>
            </div>
          )}
          {aiAnalysis && !aiLoading && (
            <>
              <Divider />
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="text-sm font-medium text-gray-700 mb-2 flex items-center gap-1">
                  <RobotOutlined className="text-indigo-500" /> AI 诊断评估
                </div>
                <div className="text-sm text-gray-600 whitespace-pre-wrap leading-relaxed">
                  {aiAnalysis}
                </div>
              </div>
            </>
          )}
        </div>
      )}
    </Modal>
  );
};

export default FaultExperimentDialog;
