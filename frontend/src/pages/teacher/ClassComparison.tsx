import React, { useState, useEffect } from "react";
import {
  Card,
  Row,
  Col,
  Typography,
  Table,
  Tag,
  Empty,
  Spin,
  Statistic,
  Segmented,
} from "antd";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { teacherApi } from "../../services/api";

interface ClassRow {
  class_id: string;
  student_count: number;
  avg_score: number;
  total_hours: number;
  avg_records_per_student: number;
  completed_kps: number;
}

interface ClassMeta {
  class_id: string;
  student_count: number;
  avg_score: number;
  avg_points: number;
  total_hours: number;
}

/**
 * 班级对比（AIC 试点"实验组 vs 对照组"数据源）
 * 展示各班级的人数/平均分/学习时长/活跃度，支持时间范围切换
 */
const ClassComparison: React.FC = () => {
  const [days, setDays] = useState(30);
  const [classes, setClasses] = useState<ClassRow[]>([]);
  const [meta, setMeta] = useState<ClassMeta[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      teacherApi.getClassComparison(days).catch(() => null),
      teacherApi.getClasses().catch(() => null),
    ])
      .then(([cmpRes, metaRes]) => {
        setClasses(cmpRes?.data?.classes || []);
        setMeta(metaRes?.data?.classes || []);
      })
      .finally(() => setLoading(false));
  }, [days]);

  // 图表数据：平均分 / 人均学习时长
  const chartData = classes.map((c) => ({
    name: c.class_id,
    平均分: c.avg_score,
    人均记录数: c.avg_records_per_student,
  }));

  const columns = [
    {
      title: "班级",
      dataIndex: "class_id",
      key: "class_id",
      render: (v: string) => (
        <span className="font-medium text-indigo-600">{v}</span>
      ),
    },
    { title: "学生人数", dataIndex: "student_count", key: "student_count" },
    {
      title: "平均分",
      dataIndex: "avg_score",
      key: "avg_score",
      render: (v: number) => <Tag color="blue">{v} 分</Tag>,
    },
    {
      title: "学习时长(h)",
      dataIndex: "total_hours",
      key: "total_hours",
      render: (v: number) => <span>{v.toFixed(1)}</span>,
    },
    {
      title: "人均学习记录",
      dataIndex: "avg_records_per_student",
      key: "avg_records_per_student",
    },
    {
      title: "完成知识点",
      dataIndex: "completed_kps",
      key: "completed_kps",
      render: (v: number) => <Tag color="green">{v} 个</Tag>,
    },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <Typography.Title level={4} className="!m-0">
            班级对比
          </Typography.Title>
          <Typography.Text type="secondary" className="text-sm">
            各班级学习表现对比（试点实验组/对照组数据源）
          </Typography.Text>
        </div>
        <Segmented
          options={[
            { label: "7天", value: 7 },
            { label: "30天", value: 30 },
            { label: "90天", value: 90 },
          ]}
          value={days}
          onChange={(v) => setDays(v as number)}
        />
      </div>

      {classes.length === 0 ? (
        <Empty description="暂无班级数据（请先在数据库中为学生分配班级）" />
      ) : (
        <>
          {/* 班级概览卡片 */}
          <Row gutter={16}>
            {meta.map((c) => (
              <Col span={8} key={c.class_id}>
                <Card size="small">
                  <Statistic
                    title={c.class_id}
                    value={c.student_count}
                    suffix="人"
                  />
                  <div className="mt-2 grid grid-cols-3 gap-2 text-center text-xs">
                    <div>
                      <div className="text-gray-400">平均分</div>
                      <div className="font-medium text-indigo-600">
                        {c.avg_score}
                      </div>
                    </div>
                    <div>
                      <div className="text-gray-400">平均积分</div>
                      <div className="font-medium">{c.avg_points}</div>
                    </div>
                    <div>
                      <div className="text-gray-400">总时长(h)</div>
                      <div className="font-medium">{c.total_hours}</div>
                    </div>
                  </div>
                </Card>
              </Col>
            ))}
          </Row>

          {/* 对比图表 */}
          <Card size="small" title={`近 ${days} 天班级表现对比`}>
            {chartData.length > 1 ? (
              <div style={{ height: 300 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData} barSize={40}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                    <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                    <YAxis tick={{ fontSize: 12 }} />
                    <Tooltip />
                    <Legend />
                    <Bar
                      dataKey="平均分"
                      fill="#6366f1"
                      radius={[4, 4, 0, 0]}
                    />
                    <Bar
                      dataKey="人均记录数"
                      fill="#22c55e"
                      radius={[4, 4, 0, 0]}
                    />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <Empty
                description="至少需要 2 个班级才能对比"
                image={Empty.PRESENTED_IMAGE_SIMPLE}
              />
            )}
          </Card>

          {/* 明细表 */}
          <Card size="small" title="班级明细">
            <Table
              dataSource={classes}
              columns={columns}
              rowKey="class_id"
              size="small"
              pagination={false}
            />
          </Card>
        </>
      )}
    </div>
  );
};

export default ClassComparison;
