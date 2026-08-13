import React, { useEffect, useState } from "react";
import {
  Card,
  Statistic,
  Row,
  Col,
  Table,
  Tag,
  Segmented,
  Spin,
  Empty,
  Button,
  message,
} from "antd";
import {
  TeamOutlined,
  ClockCircleOutlined,
  ExperimentOutlined,
  BarChartOutlined,
  RiseOutlined,
  DownloadOutlined,
} from "@ant-design/icons";
import { teacherApi } from "../../services/api";

interface StudentRow {
  student_id: string;
  record_count: number;
  total_duration_hours: number;
  completed_kps: number;
  quiz_count: number;
  avg_score: number;
  max_score: number;
}

interface PilotReportData {
  status: string;
  period_days: number;
  summary: {
    active_students: number;
    total_duration_hours: number;
    avg_daily_hours: number;
    total_records: number;
    total_quizzes: number;
    avg_score: number;
    total_experiments: number;
    completed_kps_total: number;
  };
  quiz_pre_post: {
    pre_avg: number;
    post_avg: number;
    improvement: number;
    sample_size: number;
  } | null;
  trend_distribution: Record<string, number>;
  experiments: Record<string, number>;
  top_features: { feature: string; count: number }[];
  students: StudentRow[];
}

const EXPERIMENT_LABELS: Record<string, string> = {
  circuit_simulate: "模拟电路仿真",
  circuit_fault: "故障诊断实验",
  stm32_simulate: "STM32仿真",
};

const TREND_LABELS: Record<string, string> = {
  growth: "成长",
  stable: "稳定",
  decline: "下滑",
  warning: "预警",
};

const PilotReport: React.FC = () => {
  const [days, setDays] = useState(30);
  const [data, setData] = useState<PilotReportData | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    teacherApi
      .getPilotReport(days)
      .then((res) => {
        setData(res.data);
      })
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, [days]);

  // 导出 Markdown 报告（参赛文档素材）
  const handleExport = async () => {
    try {
      const res = await teacherApi.getPilotReport(days, "markdown");
      const md = res.data.markdown;
      if (!md) {
        message.warning("暂无报告内容可导出");
        return;
      }
      const blob = new Blob([md], { type: "text/markdown;charset=utf-8" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `LearnLab试点报告_${days}天_${new Date().toISOString().slice(0, 10)}.md`;
      a.click();
      URL.revokeObjectURL(url);
      message.success("报告已导出（Markdown）");
    } catch {
      message.error("导出失败");
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-24">
        <Spin tip="正在生成试点数据分析报告..." size="large">
          <div style={{ padding: 60 }} />
        </Spin>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="py-24">
        <Empty description="暂无试点数据" />
      </div>
    );
  }

  const s = data.summary;
  const maxFeatureCount = Math.max(1, ...data.top_features.map((f) => f.count));

  const columns = [
    { title: "学生", dataIndex: "student_id", key: "student_id" },
    {
      title: "学习记录",
      dataIndex: "record_count",
      key: "record_count",
      width: 90,
    },
    {
      title: "学习时长(h)",
      dataIndex: "total_duration_hours",
      key: "total_duration_hours",
      width: 110,
    },
    {
      title: "掌握知识点",
      dataIndex: "completed_kps",
      key: "completed_kps",
      width: 100,
    },
    {
      title: "测验次数",
      dataIndex: "quiz_count",
      key: "quiz_count",
      width: 90,
    },
    {
      title: "平均分",
      dataIndex: "avg_score",
      key: "avg_score",
      width: 80,
      render: (v: number) => <span className="font-medium">{v}</span>,
    },
    { title: "最高分", dataIndex: "max_score", key: "max_score", width: 80 },
  ];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold text-gray-800 flex items-center gap-2">
            <BarChartOutlined className="text-indigo-500" />
            试点数据分析
          </h2>
          <p className="text-sm text-gray-500 mt-1">
            AIC 应用效果验证数据源：学习行为 / 测验成绩 / 实验参与 / 功能使用
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button icon={<DownloadOutlined />} onClick={handleExport}>
            导出报告(Markdown)
          </Button>
          <Segmented
            options={[
              { label: "7天", value: 7 },
              { label: "14天", value: 14 },
              { label: "30天", value: 30 },
            ]}
            value={days}
            onChange={(v) => setDays(v as number)}
          />
        </div>
      </div>

      {/* 统计卡片 */}
      <Row gutter={16}>
        <Col span={4}>
          <Card>
            <Statistic
              title="活跃学生"
              value={s.active_students}
              prefix={<TeamOutlined className="text-indigo-500" />}
            />
          </Card>
        </Col>
        <Col span={4}>
          <Card>
            <Statistic
              title="总学习时长(h)"
              value={s.total_duration_hours}
              prefix={<ClockCircleOutlined className="text-blue-500" />}
            />
          </Card>
        </Col>
        <Col span={4}>
          <Card>
            <Statistic
              title="日均时长(h)"
              value={s.avg_daily_hours}
              precision={2}
            />
          </Card>
        </Col>
        <Col span={4}>
          <Card>
            <Statistic
              title="测验次数"
              value={s.total_quizzes}
              prefix={<RiseOutlined className="text-green-500" />}
            />
          </Card>
        </Col>
        <Col span={4}>
          <Card>
            <Statistic title="平均分" value={s.avg_score} precision={1} />
          </Card>
        </Col>
        <Col span={4}>
          <Card>
            <Statistic
              title="实验次数"
              value={s.total_experiments}
              prefix={<ExperimentOutlined className="text-orange-500" />}
            />
          </Card>
        </Col>
      </Row>

      {/* 前后测对比 + 实验参与 + 趋势 */}
      <Row gutter={16}>
        <Col span={8}>
          <Card title="前后测成绩对比" size="small">
            {data.quiz_pre_post ? (
              <div>
                <div className="flex items-center gap-4 mb-3">
                  <div className="flex-1 text-center">
                    <div className="text-xs text-gray-500">前测平均</div>
                    <div className="text-xl font-bold text-gray-700">
                      {data.quiz_pre_post.pre_avg}
                    </div>
                  </div>
                  <RiseOutlined
                    className="text-green-500"
                    style={{ fontSize: 20 }}
                  />
                  <div className="flex-1 text-center">
                    <div className="text-xs text-gray-500">后测平均</div>
                    <div className="text-xl font-bold text-indigo-600">
                      {data.quiz_pre_post.post_avg}
                    </div>
                  </div>
                </div>
                <div className="text-center text-sm">
                  提升
                  <Tag
                    color={
                      data.quiz_pre_post.improvement >= 0 ? "green" : "red"
                    }
                    className="ml-1"
                  >
                    {data.quiz_pre_post.improvement > 0 ? "+" : ""}
                    {data.quiz_pre_post.improvement} 分
                  </Tag>
                  <span className="text-gray-400 text-xs ml-2">
                    (样本 {data.quiz_pre_post.sample_size} 次测验)
                  </span>
                </div>
              </div>
            ) : (
              <Empty
                description="测验数据不足（需≥6次）"
                image={Empty.PRESENTED_IMAGE_SIMPLE}
              />
            )}
          </Card>
        </Col>
        <Col span={8}>
          <Card title="实验参与分布" size="small">
            {Object.keys(data.experiments).length > 0 ? (
              <div className="space-y-2">
                {Object.entries(data.experiments).map(([k, v]) => (
                  <div key={k} className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">
                      {EXPERIMENT_LABELS[k] || k}
                    </span>
                    <Tag color="orange">{v} 次</Tag>
                  </div>
                ))}
              </div>
            ) : (
              <Empty
                description="暂无实验数据"
                image={Empty.PRESENTED_IMAGE_SIMPLE}
              />
            )}
          </Card>
        </Col>
        <Col span={8}>
          <Card title="学习趋势分布" size="small">
            {Object.keys(data.trend_distribution).length > 0 ? (
              <div className="space-y-2">
                {Object.entries(data.trend_distribution).map(([k, v]) => (
                  <div key={k} className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">
                      {TREND_LABELS[k] || k}
                    </span>
                    <Tag>{v}</Tag>
                  </div>
                ))}
              </div>
            ) : (
              <Empty
                description="暂无趋势数据"
                image={Empty.PRESENTED_IMAGE_SIMPLE}
              />
            )}
          </Card>
        </Col>
      </Row>

      {/* 功能使用 Top */}
      <Card title="功能使用 Top" size="small">
        {data.top_features.length > 0 ? (
          <div className="space-y-2">
            {data.top_features.map((f) => (
              <div key={f.feature} className="flex items-center gap-3">
                <span className="w-24 text-sm text-gray-600 shrink-0">
                  {f.feature}
                </span>
                <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-indigo-400 to-indigo-600 rounded-full"
                    style={{ width: `${(f.count / maxFeatureCount) * 100}%` }}
                  />
                </div>
                <span className="text-xs text-gray-500 w-10 text-right">
                  {f.count}
                </span>
              </div>
            ))}
          </div>
        ) : (
          <Empty
            description="暂无功能使用数据"
            image={Empty.PRESENTED_IMAGE_SIMPLE}
          />
        )}
      </Card>

      {/* 学生明细 */}
      <Card title="学生明细" size="small">
        <Table
          dataSource={data.students}
          columns={columns}
          rowKey="student_id"
          size="small"
          pagination={false}
        />
      </Card>
    </div>
  );
};

export default PilotReport;
