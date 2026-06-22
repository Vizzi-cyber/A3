import React, { useState, useEffect } from "react";
import { Card, Row, Col, Typography, Table, Tag, Empty, Spin } from "antd";
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
import { useAppStore } from "../../store";
import { teacherApi } from "../../services/api";

interface StudentSummary {
  student_id: string;
  username: string;
  total_points: number;
  trend_state: string;
  trend_factor: number;
}

const ClassComparison: React.FC = () => {
  const [students, setStudents] = useState<StudentSummary[]>([]);
  const [overview, setOverview] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState(false);
  const userInfo = useAppStore((s) => s.userInfo);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const [studentsRes, overviewRes] = await Promise.all([
          teacherApi.getStudents().catch(() => null),
          teacherApi.getOverview().catch(() => null),
        ]);
        if (studentsRes?.data?.students) {
          setStudents(studentsRes.data.students);
        }
        if (overviewRes?.data?.overview) {
          setOverview(overviewRes.data.overview);
        }
      } catch {
        setStudents([]);
      } finally {
        setLoading(false);
      }
    };
    if (userInfo?.role === "teacher" || userInfo?.role === "admin") {
      fetchData();
    }
  }, [userInfo]);

  // 基于真实学生数据生成对比图表
  const chartData =
    students.length > 0
      ? [
          {
            name: "全部学生",
            平均积分: Math.round(
              students.reduce((s, st) => s + st.total_points, 0) /
                students.length,
            ),
            学生人数: students.length,
          },
          {
            name: "上升趋势",
            平均积分: Math.round(
              students
                .filter((s) => s.trend_state === "growth")
                .reduce((s, st) => s + st.total_points, 0) /
                Math.max(
                  1,
                  students.filter((s) => s.trend_state === "growth").length,
                ),
            ),
            学生人数: students.filter((s) => s.trend_state === "growth").length,
          },
          {
            name: "预警状态",
            平均积分: Math.round(
              students
                .filter((s) => s.trend_state === "warning")
                .reduce((s, st) => s + st.total_points, 0) /
                Math.max(
                  1,
                  students.filter((s) => s.trend_state === "warning").length,
                ),
            ),
            学生人数: students.filter((s) => s.trend_state === "warning")
              .length,
          },
        ]
      : [];

  const columns = [
    {
      title: "学生",
      dataIndex: "username",
      key: "username",
      render: (name: string) => <span className="font-medium">{name}</span>,
    },
    {
      title: "积分",
      dataIndex: "total_points",
      key: "total_points",
      render: (points: number) => (
        <Tag className="rounded-full border-0" color="blue">
          {points}分
        </Tag>
      ),
    },
    {
      title: "趋势",
      dataIndex: "trend_state",
      key: "trend_state",
      render: (state: string) => (
        <Tag
          className="rounded-full border-0"
          color={
            state === "growth"
              ? "success"
              : state === "warning"
                ? "warning"
                : state === "decline"
                  ? "error"
                  : "default"
          }
        >
          {state === "growth"
            ? "上升"
            : state === "warning"
              ? "预警"
              : state === "decline"
                ? "下滑"
                : "稳定"}
        </Tag>
      ),
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
        <Typography.Title level={4} className="!m-0">
          班级对比
        </Typography.Title>
      </div>

      {students.length === 0 ? (
        <Card className="rounded-2xl border-0 shadow-sm">
          <Empty description="暂无学生数据" />
        </Card>
      ) : (
        <>
          <Row gutter={[20, 20]}>
            <Col xs={24} lg={14}>
              <Card
                className="rounded-2xl border-0 shadow-sm"
                title="学生趋势对比"
              >
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
                      <Bar
                        dataKey="平均积分"
                        fill="#0052ff"
                        radius={[8, 8, 0, 0]}
                      />
                      <Bar
                        dataKey="学生人数"
                        fill="#10b981"
                        radius={[8, 8, 0, 0]}
                      />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </Card>
            </Col>

            <Col xs={24} lg={10}>
              <Card className="rounded-2xl border-0 shadow-sm" title="学生列表">
                <Table
                  columns={columns}
                  dataSource={students.slice(0, 10)}
                  pagination={false}
                  size="small"
                  rowKey="student_id"
                />
              </Card>
            </Col>
          </Row>

          <Card className="rounded-2xl border-0 shadow-sm" title="班级分析">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-100">
                <div className="font-medium text-emerald-700 mb-2">
                  总学生数
                </div>
                <div className="text-2xl font-bold text-emerald-600">
                  {overview.total_students || students.length}
                </div>
              </div>
              <div className="p-4 rounded-xl bg-amber-50 border border-amber-100">
                <div className="font-medium text-amber-700 mb-2">平均分</div>
                <div className="text-2xl font-bold text-amber-600">
                  {overview.avg_score || "-"}
                </div>
              </div>
              <div className="p-4 rounded-xl bg-blue-50 border border-blue-100">
                <div className="font-medium text-blue-700 mb-2">活跃学生</div>
                <div className="text-2xl font-bold text-blue-600">
                  {overview.active_students || 0}
                </div>
              </div>
            </div>
          </Card>
        </>
      )}
    </div>
  );
};

export default ClassComparison;
