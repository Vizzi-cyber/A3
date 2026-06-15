import React from "react";
import { Card, Row, Col, Typography, Table, Tag, Select } from "antd";
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

const ClassComparison: React.FC = () => {
  const classData = [
    {
      name: "班级A",
      avgScore: 78,
      avgHours: 12,
      completionRate: 85,
      activeRate: 90,
    },
    {
      name: "班级B",
      avgScore: 72,
      avgHours: 10,
      completionRate: 78,
      activeRate: 82,
    },
    {
      name: "班级C",
      avgScore: 85,
      avgScore2: 15,
      avgHours: 14,
      completionRate: 92,
      activeRate: 95,
    },
  ];

  const chartData = classData.map((c) => ({
    name: c.name,
    平均分: c.avgScore,
    学习时长: c.avgHours,
    完成率: c.completionRate,
  }));

  const columns = [
    {
      title: "班级",
      dataIndex: "name",
      key: "name",
      render: (name: string) => <span className="font-medium">{name}</span>,
    },
    {
      title: "平均分",
      dataIndex: "avgScore",
      key: "avgScore",
      render: (score: number) => (
        <Tag
          className="rounded-full border-0"
          color={score >= 80 ? "success" : score >= 60 ? "warning" : "error"}
        >
          {score}分
        </Tag>
      ),
    },
    {
      title: "平均学时",
      dataIndex: "avgHours",
      key: "avgHours",
      render: (hours: number) => `${hours}h`,
    },
    {
      title: "完成率",
      dataIndex: "completionRate",
      key: "completionRate",
      render: (rate: number) => `${rate}%`,
    },
    {
      title: "活跃率",
      dataIndex: "activeRate",
      key: "activeRate",
      render: (rate: number) => `${rate}%`,
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <Typography.Title level={4} className="!m-0">
          班级对比
        </Typography.Title>
        <Select
          defaultValue="all"
          className="w-32"
          options={[
            { value: "all", label: "全部班级" },
            { value: "classA", label: "班级A" },
            { value: "classB", label: "班级B" },
          ]}
        />
      </div>

      <Row gutter={[20, 20]}>
        <Col xs={24} lg={14}>
          <Card className="rounded-2xl border-0 shadow-sm" title="班级成绩对比">
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                  <XAxis
                    dataKey="name"
                    tick={{ fill: "#64748b" }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <YAxis
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
                  <Legend />
                  <Bar dataKey="平均分" fill="#4f46e5" radius={[8, 8, 0, 0]} />
                  <Bar
                    dataKey="学习时长"
                    fill="#10b981"
                    radius={[8, 8, 0, 0]}
                  />
                  <Bar dataKey="完成率" fill="#f59e0b" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </Card>
        </Col>

        <Col xs={24} lg={10}>
          <Card className="rounded-2xl border-0 shadow-sm" title="详细数据">
            <Table
              columns={columns}
              dataSource={classData}
              pagination={false}
              size="small"
            />
          </Card>
        </Col>
      </Row>

      <Card className="rounded-2xl border-0 shadow-sm" title="班级分析">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-100">
            <div className="font-medium text-emerald-700 mb-2">表现最佳</div>
            <div className="text-sm text-emerald-600">
              班级C平均分最高(85分)，学习时长最长(14h)，建议推广其学习方法。
            </div>
          </div>
          <div className="p-4 rounded-xl bg-amber-50 border border-amber-100">
            <div className="font-medium text-amber-700 mb-2">需要改进</div>
            <div className="text-sm text-amber-600">
              班级B平均学时较低(10h)，建议增加课堂互动和课后练习。
            </div>
          </div>
          <div className="p-4 rounded-xl bg-blue-50 border border-blue-100">
            <div className="font-medium text-blue-700 mb-2">共同提升</div>
            <div className="text-sm text-blue-600">
              三个班级在"指针"章节普遍薄弱，建议统一加强该部分教学。
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default ClassComparison;
