import React, { useEffect, useState } from "react";
import {
  Card,
  Row,
  Col,
  List,
  Tag,
  Avatar,
  Button,
  Typography,
  Badge,
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
  WarningOutlined,
  AlertOutlined,
  BulbOutlined,
  RocketOutlined,
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

interface Alert {
  student_id: string;
  username: string;
  reasons: Array<{ text: string; suggestion: string }>;
  level: string;
  avg_score: number | null;
  recent_records: number;
}

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
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [alertStats, setAlertStats] = useState({
    high_risk: 0,
    medium_risk: 0,
    total: 0,
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    const handleVisibility = () => {
      if (document.visibilityState === "visible") {
        loadData();
      }
    };
    document.addEventListener("visibilitychange", handleVisibility);
    return () =>
      document.removeEventListener("visibilitychange", handleVisibility);
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [overviewRes, studentsRes, alertsRes] = await Promise.all([
        teacherApi.getOverview(),
        teacherApi.getStudents(),
        teacherApi.getAlerts().catch(() => null),
      ]);
      setOverview(overviewRes.data.overview || {});
      setStudents((studentsRes.data.students || []).slice(0, 10));
      if (alertsRes?.data) {
        setAlerts(alertsRes.data.alerts || []);
        setAlertStats({
          high_risk: alertsRes.data.high_risk || 0,
          medium_risk: alertsRes.data.medium_risk || 0,
          total: alertsRes.data.total || 0,
        });
      }
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
      color: "#0052ff",
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
      suffix: "分",
    },
    {
      title: "学习预警",
      value: alertStats.total,
      icon: <WarningOutlined />,
      color: alertStats.high_risk > 0 ? "#ef4444" : "#f59e0b",
      suffix:
        alertStats.high_risk > 0 ? `(高${alertStats.high_risk})` : undefined,
    },
  ];

  const chartData = students.map((s) => ({
    name: s.username?.slice(0, 4) || s.student_id.slice(0, 8),
    points: s.total_points,
  }));

  return (
    <div className="space-y-4">
      <Typography.Title level={4} className="!m-0">
        教师工作台
      </Typography.Title>

      {/* 统计卡片 */}
      <Row gutter={[16, 16]}>
        {stats.map((stat, idx) => (
          <Col xs={12} lg={6} key={idx}>
            <Card className="rounded-xl border-0 shadow-sm hover:shadow-md transition-shadow !p-3">
              <div className="flex items-center gap-3">
                <div
                  className="w-10 h-10 rounded-lg flex items-center justify-center text-white shrink-0"
                  style={{ backgroundColor: stat.color }}
                >
                  {stat.icon}
                </div>
                <div className="min-w-0">
                  <div className="text-xs text-slate-400 truncate">
                    {stat.title}
                  </div>
                  <div className="text-xl font-bold text-slate-800 leading-tight">
                    {stat.value}
                    {stat.suffix && (
                      <span className="text-xs font-normal text-slate-400 ml-1">
                        {stat.suffix}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </Card>
          </Col>
        ))}
      </Row>

      <Row gutter={[16, 16]}>
        {/* 学生积分趋势 */}
        <Col xs={24} lg={14}>
          <Card className="rounded-2xl border-0 shadow-sm" title="学生积分概览">
            <div className="h-52">
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
                    stroke="#0052ff"
                    strokeWidth={2}
                    dot={{ fill: "#0052ff", r: 4 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </Card>
        </Col>

        {/* 快捷操作 */}
        <Col xs={24} lg={10}>
          <Card className="rounded-2xl border-0 shadow-sm" title="快捷操作">
            <div className="grid grid-cols-2 gap-2">
              {[
                {
                  icon: <TeamOutlined />,
                  label: "学生管理",
                  path: "/teacher/students",
                },
                {
                  icon: <RiseOutlined />,
                  label: "学情分析",
                  path: "/teacher/analytics",
                },
                {
                  icon: <BookOutlined />,
                  label: "备课资源",
                  path: "/teacher/resources",
                },
                {
                  icon: <ClockCircleOutlined />,
                  label: "报告导出",
                  path: "/teacher/reports",
                },
                {
                  icon: <BulbOutlined />,
                  label: "AI备课",
                  path: "/teacher/lesson-plan",
                },
                {
                  icon: <RocketOutlined />,
                  label: "AI组卷",
                  path: "/teacher/smart-quiz",
                },
              ].map((item, idx) => (
                <Button
                  key={idx}
                  block
                  className="h-14 rounded-xl"
                  onClick={() => navigate(item.path)}
                >
                  <span className="text-lg">{item.icon}</span>
                  <div className="text-xs mt-0.5">{item.label}</div>
                </Button>
              ))}
            </div>
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        {/* 学习预警 */}
        <Col xs={24} lg={12}>
          <Card
            className="rounded-2xl border-0 shadow-sm"
            title={
              <div className="flex items-center gap-2">
                <AlertOutlined className="text-[#ef4444]" />
                <span>学习预警</span>
                {alertStats.high_risk > 0 && (
                  <Badge count={alertStats.high_risk} className="ant-badge" />
                )}
              </div>
            }
            extra={
              <Button
                type="link"
                size="small"
                onClick={() => navigate("/teacher/students")}
              >
                查看全部
              </Button>
            }
          >
            <List
              loading={loading}
              dataSource={alerts.slice(0, 5)}
              locale={{ emptyText: "暂无预警，一切正常" }}
              size="small"
              renderItem={(item) => (
                <List.Item className="!px-0">
                  <List.Item.Meta
                    avatar={
                      <Avatar
                        size="small"
                        className={
                          item.level === "high" ? "bg-red-500" : "bg-amber-500"
                        }
                      >
                        {(item.username || item.student_id)[0]}
                      </Avatar>
                    }
                    title={
                      <div className="flex items-center gap-2">
                        <span className="text-sm">
                          {item.username || item.student_id}
                        </span>
                        <Tag
                          className="rounded-full border-0 text-xs !py-0 !px-2"
                          color={item.level === "high" ? "error" : "warning"}
                        >
                          {item.level === "high" ? "高风险" : "中风险"}
                        </Tag>
                      </div>
                    }
                    description={
                      <div className="flex flex-wrap gap-1">
                        {item.reasons.slice(0, 2).map((reason, idx) => (
                          <Tag
                            key={idx}
                            className="rounded-full border-0 text-xs bg-red-50 text-red-600 !py-0"
                          >
                            {reason.text}
                          </Tag>
                        ))}
                        {item.reasons.length > 2 && (
                          <span className="text-xs text-slate-400">
                            +{item.reasons.length - 2}
                          </span>
                        )}
                      </div>
                    }
                  />
                </List.Item>
              )}
            />
          </Card>
        </Col>

        {/* 最近活跃学生 */}
        <Col xs={24} lg={12}>
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
                      <Avatar className="bg-[#0052ff]/10 text-[#0052ff]">
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
        </Col>
      </Row>
    </div>
  );
};

export default TeacherHome;
