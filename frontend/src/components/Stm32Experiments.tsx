import React, { useEffect, useState } from "react";
import {
  Card,
  Tag,
  Checkbox,
  Button,
  message,
  Spin,
  Empty,
  Collapse,
} from "antd";
import {
  ExperimentOutlined,
  CheckCircleOutlined,
  BulbOutlined,
} from "@ant-design/icons";
import { stm32Api, learningDataApi } from "../services/api";
import { useAppStore } from "../store";

interface Experiment {
  id: number;
  title: string;
  knowledge_id: number;
  difficulty: string;
  objective: string;
  principle: string;
  components: string[];
  steps: { step: number; action: string; detail: string }[];
}

interface KpNode {
  id: number;
  name: string;
}

interface Stm32ExperimentsProps {
  kpId: string; // 当前知识点 kp_id（如 kp_s02）
}

/**
 * STM32 实验任务（AIC "实验实训"核心环节）
 * 实验步骤勾选 → 完成度采集（experiment_logs）
 */
const Stm32Experiments: React.FC<Stm32ExperimentsProps> = ({ kpId }) => {
  const studentId = useAppStore((s) => s.studentId);
  const [experiments, setExperiments] = useState<Experiment[]>([]);
  const [loading, setLoading] = useState(true);
  const [checked, setChecked] = useState<Record<string, boolean>>({});
  const [completed, setCompleted] = useState<Record<number, boolean>>({});

  useEffect(() => {
    let ignore = false;
    setLoading(true);
    stm32Api
      .getKnowledgeTree()
      .then((res) => {
        if (ignore) return;
        const data = res.data.data;
        const exps = (data.experiments || []) as unknown as Experiment[];
        // kp_id（kp_s02）→ 数字 id（knowledge_tree 中实验的 knowledge_id 为数字）
        const numId = parseInt(String(kpId).replace("kp_s", ""), 10);
        const related = exps.filter(
          (e) => e.knowledge_id === numId || e.knowledge_id === numId - 0,
        );
        setExperiments(related);
      })
      .catch(() => setExperiments([]))
      .finally(() => setLoading(false));
    return () => {
      ignore = true;
    };
  }, [kpId]);

  const handleCheck = (expId: number, stepIdx: number, isChecked: boolean) => {
    setChecked((prev) => ({ ...prev, [`${expId}_${stepIdx}`]: isChecked }));
  };

  const handleComplete = (exp: Experiment) => {
    const expSteps = exp.steps || [];
    const allDone = expSteps.every((_, i) => checked[`${exp.id}_${i}`]);
    if (expSteps.length > 0 && !allDone) {
      message.warning("请先完成全部实验步骤再提交");
      return;
    }
    setCompleted((prev) => ({ ...prev, [exp.id]: true }));
    message.success(`已完成实验：${exp.title}`);
    // 完成度采集（试点数据分析）
    if (studentId) {
      learningDataApi
        .submitExperiment({
          student_id: studentId,
          experiment_type: "stm32_experiment",
          action: "complete",
          detail: {
            experiment_id: exp.id,
            title: exp.title,
            steps_total: expSteps.length,
          },
        })
        .catch(() => {});
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <Spin />
      </div>
    );
  }

  if (experiments.length === 0) {
    return (
      <div className="py-12">
        <Empty
          description="当前知识点暂无配套实验"
          image={Empty.PRESENTED_IMAGE_SIMPLE}
        />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {experiments.map((exp) => {
        const expSteps = exp.steps || [];
        const allDone =
          expSteps.length > 0 &&
          expSteps.every((_, i) => checked[`${exp.id}_${i}`]);
        const isDone = completed[exp.id];
        return (
          <Card
            key={exp.id}
            size="small"
            className={
              isDone ? "border-green-200" : allDone ? "border-emerald-300" : ""
            }
            title={
              <span className="flex items-center gap-2">
                <ExperimentOutlined className="text-orange-500" />
                {exp.title}
                {isDone && (
                  <Tag color="green" icon={<CheckCircleOutlined />}>
                    已完成
                  </Tag>
                )}
                <Tag color={exp.difficulty === "简单" ? "green" : "orange"}>
                  {exp.difficulty}
                </Tag>
              </span>
            }
          >
            {/* 实验目标 */}
            <div className="mb-3">
              <div className="text-xs font-medium text-slate-500 mb-1">
                🎯 实验目标
              </div>
              <div className="text-sm text-slate-700">{exp.objective}</div>
            </div>

            {/* 元件清单 */}
            {exp.components && exp.components.length > 0 && (
              <div className="mb-3">
                <div className="text-xs font-medium text-slate-500 mb-1">
                  🔧 所需元件
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {exp.components.map((c, i) => (
                    <Tag key={i} className="rounded-md">
                      {c}
                    </Tag>
                  ))}
                </div>
              </div>
            )}

            {/* 实验步骤（勾选） */}
            {expSteps.length > 0 && (
              <div className="mb-3">
                <div className="text-xs font-medium text-slate-500 mb-1">
                  📋 实验步骤
                </div>
                <div className="space-y-1.5">
                  {expSteps.map((s, i) => (
                    <div
                      key={i}
                      className="flex items-start gap-2 bg-slate-50 rounded-lg p-2"
                    >
                      <Checkbox
                        checked={!!checked[`${exp.id}_${i}`]}
                        onChange={(e) =>
                          handleCheck(exp.id, i, e.target.checked)
                        }
                      />
                      <div className="flex-1">
                        <div className="text-sm text-slate-700">
                          <span className="font-medium">
                            {s.step}. {s.action}
                          </span>
                        </div>
                        {s.detail && (
                          <div className="text-xs text-slate-500 mt-0.5 font-mono">
                            {s.detail}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* 实验原理（折叠） */}
            {exp.principle && (
              <Collapse
                ghost
                size="small"
                className="mb-3"
                items={[
                  {
                    key: "principle",
                    label: (
                      <span className="text-xs text-slate-500">
                        <BulbOutlined /> 实验原理
                      </span>
                    ),
                    children: (
                      <div className="text-sm text-slate-600 leading-relaxed">
                        {exp.principle}
                      </div>
                    ),
                  },
                ]}
              />
            )}

            {/* 提交完成 */}
            <div className="flex items-center gap-2">
              <Button
                size="small"
                type="primary"
                className={
                  allDone
                    ? "!bg-green-500 !border-green-500"
                    : "!bg-orange-500 !border-orange-500"
                }
                disabled={isDone}
                onClick={() => handleComplete(exp)}
              >
                {isDone ? "已完成 ✓" : allDone ? "提交实验完成" : "标记完成"}
              </Button>
              {expSteps.length > 0 && !allDone && !isDone && (
                <span className="text-xs text-slate-400">
                  勾选全部步骤后可提交
                </span>
              )}
            </div>
          </Card>
        );
      })}
    </div>
  );
};

export default Stm32Experiments;
