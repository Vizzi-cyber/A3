import React, { useEffect, useState } from "react";
import {
  Card,
  Row,
  Col,
  Statistic,
  List,
  Tag,
  Avatar,
  Button,
  Typography,
  Space,
} from "antd";
import {
  TeamOutlined,
  BookOutlined,
  TrophyOutlined,
  FireOutlined,
  RiseOutlined,
  ClockCircleOutlined,
  EyeOutlined,
} from "@ant-design/icons";
import { useNavigate } from "react-router-dom";
import { teacherApi } from "../../services/api";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

const TeacherHome: React.FC = () => {
  const navigate = useNavigate();
  const [overview, setOverview] = useState<Record<string, unknown>>({});
  const [students, setStudents] = useState<
    Array<{
      student_id: string;
      username: string;
      total_points: number;
      trend_state: string;
    }>
  >([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [overviewRes, studentsRes] = await Promise.all([
        teacherApi.getOverview(),
        teacherApi.getStudents(),
      ]);
      setOverview(overviewRes.data.overview || {});
      setStudents((studentsRes.data.students || []).slice(0, 10));
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  };

  const stats = [
    {
      title: "总学生数",
      value: Number((overview as Record<string, unknown>).total_students) || 0,
      icon: <TeamOutlined />,
      color: "#4f46e5",
    },
    {
      title: "活跃学生",
      value: Number((overview as Record<string, unknown>).active_students) || 0,
      icon: <FireOutlined />,
      color: "#f59e0b",
    },
    {
      title: "平均测验分",
      value: Number((overview as Record<string, unknown>).avg_score) || 0,
      icon: <TrophyOutlined />,
      color: "#10b981",
    },
    {
      title: "总学习记录",
      value: Number((overview as Record<string, unknown>).total_records) || 0,
      icon: <BookOutlined />,
      color: "#ec4899",
    },
  ];

  const chartData = students.map((s) => ({
    name: s.username?.slice(0, 4) || s.student_id.slice(0, 8),
    points: s.total_points,
  }));

  return (
    <div className="space-y-6">
      <Typography.Title level={4} className="!m-0">
        教师工作台
      </Typography.Title>

      {/* 统计卡片 */}
      <Row gutter={[20, 20]}>
        {stats.map((stat, idx) => (
          <Col xs={12} lg={6} key={idx}>
            <Card className="rounded-2xl border-0 shadow-sm hover:shadow-md transition-shadow">
              <Statistic
                title={stat.title}
                value={stat.value}
                prefix={<span style={{ color: stat.color }}>{stat.icon}</span>}
              />
            </Card>
          </Col>
        ))}
      </Row>

      <Row gutter={[20, 20]}>
        {/* 学生积分趋势 */}
        <Col xs={24} lg={14}>
          <Card className="rounded-2xl border-0 shadow-sm" title="学生积分概览">
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                  <XAxis
                    dataKey="name"
                    tick={{ fill: "#64748b", fontSize: 11 }}
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
                  <Line
                    type="monotone"
                    dataKey="points"
                    name="积分"
                    stroke="#4f46e5"
                    strokeWidth={2}
                    dot={{ fill: "#4f46e5", r: 4 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </Card>
        </Col>

        {/* 快捷操作 */}
        <Col xs={24} lg={10}>
          <Card className="rounded-2xl border-0 shadow-sm" title="快捷操作">
            <div className="grid grid-cols-2 gap-3">
              <Button
                block
                className="h-16 rounded-xl"
                onClick={() => navigate("/teacher/students")}
              >
                <TeamOutlined className="text-lg" />
                <div className="text-xs mt-1">学生管理</div>
              </Button>
              <Button
                block
                className="h-16 rounded-xl"
                onClick={() => navigate("/teacher/analytics")}
              >
                <RiseOutlined className="text-lg" />
                <div className="text-xs mt-1">学情分析</div>
              </Button>
              <Button
                block
                className="h-16 rounded-xl"
                onClick={() => navigate("/teacher/resources")}
              >
                <BookOutlined className="text-lg" />
                <div className="text-xs mt-1">备课资源</div>
              </Button>
              <Button
                block
                className="h-16 rounded-xl"
                onClick={() => navigate("/teacher/reports")}
              >
                <ClockCircleOutlined className="text-lg" />
                <div className="text-xs mt-1">报告导出</div>
              </Button>
            </div>
          </Card>
        </Col>
      </Row>

      {/* 最近活跃学生 */}
      <Card className="rounded-2xl border-0 shadow-sm" title="最近活跃学生">
        <List
          loading={loading}
          dataSource={students}
          renderItem={(student) => (
            <List.Item
              className="hover:bg-slate-50 rounded-xl transition-colors"
              actions={[
                <Button
                  key="detail"
                  type="link"
                  icon={<EyeOutlined />}
                  onClick={() => navigate("/teacher/students")}
                >
                  查看
                </Button>,
              ]}
            >
              <List.Item.Meta
                avatar={
                  <Avatar className="bg-primary/10 text-primary">
                    {(student.username || student.student_id)[0]}
                  </Avatar>
                }
                title={student.username || student.student_id}
                description={
                  <Space>
                    <span>积分: {student.total_points}</span>
                    <Tag
                      className="rounded-full border-0 text-xs"
                      color={
                        student.trend_state === "growth"
                          ? "success"
                          : student.trend_state === "warning"
                            ? "error"
                            : "default"
                      }
                    >
                      {student.trend_state === "growth"
                        ? "上升"
                        : student.trend_state === "warning"
                          ? "预警"
                          : "平稳"}
                    </Tag>
                  </Space>
                }
              />
            </List.Item>
          )}
        />
      </Card>
    </div>
  );
};

export default TeacherHome;
