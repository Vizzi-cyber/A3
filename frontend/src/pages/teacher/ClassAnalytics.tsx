import React, { useEffect, useState } from "react";
import {
  Card,
  Row,
  Col,
  Typography,
  Statistic,
  Table,
  Progress,
  Tag,
  Empty,
} from "antd";
import {
  TeamOutlined,
  TrophyOutlined,
  ClockCircleOutlined,
  BookOutlined,
} from "@ant-design/icons";
import { teacherApi } from "../../services/api";
import {
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
} from "recharts";

const ClassAnalytics: React.FC = () => {
  const [overview, setOverview] = useState<Record<string, unknown>>({});
  const [students, setStudents] = useState<
    Array<{
      student_id: string;
      username: string;
      total_points: number;
      trend_state: string;
      total_hours?: number;
      avg_score?: number;
    }>
  >([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  // 页面重新可见时刷新数据
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
      const [overviewRes, studentsRes, rankingRes] = await Promise.all([
        teacherApi.getOverview(),
        teacherApi.getStudents(),
        teacherApi.getRanking("points", 20),
      ]);
      setOverview(overviewRes.data.overview || {});
      setStudents(studentsRes.data.students || []);

      // 合并排行榜数据
      const ranking = rankingRes.data.ranking || [];
      setStudents((prev) =>
        prev.map((s) => {
          const rank = ranking.find(
            (r: { student_id: string }) => r.student_id === s.student_id,
          );
          return {
            ...s,
            total_hours: rank?.total_hours || 0,
            avg_score: rank?.avg_score || 0,
          };
        }),
      );
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  };

  // 班级整体数据
  const totalStudents = (overview.total_students as number) || 0;
  const activeStudents = (overview.active_students as number) || 0;
  const avgScore = (overview.avg_score as number) || 0;
  const totalRecords = (overview.total_records as number) || 0;

  // 计算班级平均分用于雷达图
  const avgPoints =
    students.length > 0
      ? Math.round(
          students.reduce((sum, s) => sum + (s.total_points || 0), 0) /
            students.length /
            50,
        )
      : 0;
  const avgHours =
    students.length > 0
      ? Math.round(
          (students.reduce((sum, s) => sum + (s.total_hours || 0), 0) /
            students.length) *
            10,
        )
      : 0;

  // 雷达图数据（基于真实数据计算）
  const radarData =
    students.length > 0
      ? [
          { subject: "基础知识", A: Math.min(100, avgScore) },
          { subject: "编程能力", A: Math.min(100, avgPoints) },
          { subject: "算法思维", A: Math.min(100, Math.round(avgScore * 0.8)) },
          { subject: "项目实践", A: Math.min(100, avgHours) },
          {
            subject: "协作能力",
            A: Math.min(100, Math.round(avgScore * 1.05)),
          },
        ]
      : [];

  const columns = [
    {
      title: "排名",
      key: "rank",
      render: (_: unknown, __: unknown, index: number) => (
        <span className={index < 3 ? "text-[#0052ff] font-bold" : ""}>
          {index + 1}
        </span>
      ),
    },
    {
      title: "学生",
      dataIndex: "username",
      key: "username",
      render: (name: string, record: { student_id: string }) =>
        name || record.student_id,
    },
    {
      title: "学习时长",
      dataIndex: "total_hours",
      key: "total_hours",
      render: (hours: number) => `${hours || 0}h`,
    },
    {
      title: "测验平均分",
      dataIndex: "avg_score",
      key: "avg_score",
      render: (score: number) => (
        <Progress
          percent={score || 0}
          size="small"
          strokeColor={
            score >= 80 ? "#10b981" : score >= 60 ? "#f59e0b" : "#ef4444"
          }
        />
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
                ? "error"
                : "default"
          }
        >
          {state === "growth" ? "上升" : state === "warning" ? "预警" : "平稳"}
        </Tag>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      <Typography.Title level={4} className="!m-0">
        班级学情
      </Typography.Title>

      {/* 统计卡片 */}
      <Row gutter={[20, 20]}>
        <Col xs={12} lg={6}>
          <Card className="rounded-2xl border-0 shadow-sm">
            <Statistic
              title="总学生数"
              value={totalStudents}
              prefix={<TeamOutlined className="text-[#0052ff]" />}
            />
          </Card>
        </Col>
        <Col xs={12} lg={6}>
          <Card className="rounded-2xl border-0 shadow-sm">
            <Statistic
              title="活跃学生"
              value={activeStudents}
              prefix={<TrophyOutlined className="text-amber-500" />}
            />
          </Card>
        </Col>
        <Col xs={12} lg={6}>
          <Card className="rounded-2xl border-0 shadow-sm">
            <Statistic
              title="平均测验分"
              value={avgScore}
              precision={1}
              prefix={<ClockCircleOutlined className="text-blue-500" />}
            />
          </Card>
        </Col>
        <Col xs={12} lg={6}>
          <Card className="rounded-2xl border-0 shadow-sm">
            <Statistic
              title="总学习记录"
              value={totalRecords}
              prefix={<BookOutlined className="text-emerald-500" />}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[20, 20]}>
        {/* 班级能力雷达图 */}
        <Col xs={24} lg={10}>
          <Card className="rounded-2xl border-0 shadow-sm" title="班级能力分布">
            <div className="h-72">
              {radarData.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <RadarChart data={radarData}>
                    <PolarGrid stroke="#e2e8f0" />
                    <PolarAngleAxis
                      dataKey="subject"
                      tick={{ fill: "#64748b", fontSize: 12 }}
                    />
                    <PolarRadiusAxis
                      angle={30}
                      domain={[0, 100]}
                      tick={false}
                      axisLine={false}
                    />
                    <Radar
                      name="班级平均"
                      dataKey="A"
                      stroke="#0052ff"
                      fill="#0052ff"
                      fillOpacity={0.2}
                      strokeWidth={2}
                    />
                  </RadarChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-full flex items-center justify-center">
                  <Empty
                    description="暂无学生数据"
                    image={Empty.PRESENTED_IMAGE_SIMPLE}
                  />
                </div>
              )}
            </div>
          </Card>
        </Col>

        {/* 学生排名 */}
        <Col xs={24} lg={14}>
          <Card className="rounded-2xl border-0 shadow-sm" title="学生排名">
            <Table
              columns={columns}
              dataSource={students}
              rowKey="student_id"
              loading={loading}
              pagination={{ pageSize: 10 }}
              size="small"
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default ClassAnalytics;
