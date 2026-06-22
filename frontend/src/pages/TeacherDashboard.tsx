import React, { useState, useEffect } from "react";
import {
  Typography,
  Card,
  Button,
  Tag,
  Space,
  message,
  Table,
  Tabs,
  Input,
  Progress,
  Spin,
  Descriptions,
  Select,
} from "antd";
import {
  TeamOutlined,
  BarChartOutlined,
  TrophyOutlined,
  UserOutlined,
  SearchOutlined,
  BookOutlined,
  ClockCircleOutlined,
  RiseOutlined,
  FallOutlined,
  WarningOutlined,
  CheckCircleOutlined,
  ExperimentOutlined,
} from "@ant-design/icons";
import { teacherApi } from "../services/api";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
} from "recharts";

const COLORS = [
  "#4f46e5",
  "#10b981",
  "#f59e0b",
  "#ef4444",
  "#8b5cf6",
  "#06b6d4",
];

const TeacherDashboard: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState("overview");

  // 总览数据
  const [overview, setOverview] = useState<any>(null);
  const [weakPoints, setWeakPoints] = useState<any>(null);
  const [ranking, setRanking] = useState<any[]>([]);
  const [rankingSort, setRankingSort] = useState("points");
  const [loadErrors, setLoadErrors] = useState<Record<string, boolean>>({});

  // 学生管理
  const [students, setStudents] = useState<any[]>([]);
  const [studentSearch, setStudentSearch] = useState("");
  const [selectedStudent, setSelectedStudent] = useState<any>(null);
  const [studentDetail, setStudentDetail] = useState<any>(null);
  const [detailLoading, setDetailLoading] = useState(false);

  useEffect(() => {
    loadOverviewData();
  }, []);

  const loadOverviewData = async () => {
    setLoading(true);
    try {
      const [overviewRes, weakRes, rankRes] = await Promise.all([
        teacherApi.getOverview().catch(() => null),
        teacherApi.getWeakPoints().catch(() => null),
        teacherApi.getRanking("points").catch(() => null),
      ]);
      const errors: Record<string, boolean> = {};
      if (overviewRes?.data?.status === "success")
        setOverview(overviewRes.data.overview);
      else errors.overview = true;
      if (weakRes?.data?.status === "success") setWeakPoints(weakRes.data);
      else errors.weakPoints = true;
      if (rankRes?.data?.status === "success") setRanking(rankRes.data.ranking);
      else errors.ranking = true;
      if (Object.keys(errors).length > 0) setLoadErrors(errors);
    } catch (e) {
      message.error("加载数据失败");
    } finally {
      setLoading(false);
    }
  };

  const loadStudents = async () => {
    try {
      const { data } = await teacherApi.getStudents();
      if (data.status === "success") setStudents(data.students);
    } catch (e) {
      message.error("加载学生列表失败");
    }
  };

  const handleViewStudent = async (studentId: string) => {
    setSelectedStudent(studentId);
    setDetailLoading(true);
    try {
      const { data } = await teacherApi.getStudentDetail(studentId);
      if (data.status === "success") setStudentDetail(data.student);
    } catch (e) {
      message.error("加载学生详情失败");
    } finally {
      setDetailLoading(false);
    }
  };

  const handleRankingSort = async (sortBy: string) => {
    setRankingSort(sortBy);
    try {
      const { data } = await teacherApi.getRanking(sortBy);
      if (data.status === "success") setRanking(data.ranking);
    } catch (e) {
      message.error("加载排行失败");
    }
  };

  const getTrendIcon = (state: string) => {
    switch (state) {
      case "growth":
        return <RiseOutlined className="text-green-500" />;
      case "decline":
        return <FallOutlined className="text-red-500" />;
      case "warning":
        return <WarningOutlined className="text-orange-500" />;
      default:
        return <ClockCircleOutlined className="text-gray-400" />;
    }
  };

  const getTrendColor = (state: string) => {
    switch (state) {
      case "growth":
        return "green";
      case "decline":
        return "red";
      case "warning":
        return "orange";
      default:
        return "default";
    }
  };

  const filteredStudents = students.filter(
    (s) =>
      s.student_id?.includes(studentSearch) ||
      (s.username && s.username.includes(studentSearch)),
  );

  // 成绩分布数据
  const scoreDistribution = React.useMemo(() => {
    if (!ranking.length) return [];
    const ranges = [
      { range: "90-100", min: 90, max: 100 },
      { range: "80-89", min: 80, max: 89 },
      { range: "70-79", min: 70, max: 79 },
      { range: "60-69", min: 60, max: 69 },
      { range: "0-59", min: 0, max: 59 },
    ];
    return ranges.map((r) => ({
      range: r.range,
      count: ranking.filter((s) => s.avg_score >= r.min && s.avg_score <= r.max)
        .length,
    }));
  }, [ranking]);

  const renderOverview = () => (
    <div className="space-y-4">
      {/* 概览卡片 */}
      {loadErrors.overview && (
        <div className="p-3 rounded-lg bg-red-50 border border-red-100 flex items-center justify-between">
          <span className="text-sm text-red-500">概览数据加载失败</span>
          <Button size="small" type="link" onClick={loadOverviewData}>
            重试
          </Button>
        </div>
      )}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <Card size="small" className="text-center">
          <div className="text-2xl font-semibold text-blue-600">
            {overview?.total_students || 0}
          </div>
          <div className="text-xs text-gray-500">总学生数</div>
        </Card>
        <Card size="small" className="text-center">
          <div className="text-2xl font-semibold text-green-600">
            {overview?.active_students || 0}
          </div>
          <div className="text-xs text-gray-500">本周活跃</div>
        </Card>
        <Card size="small" className="text-center">
          <div className="text-2xl font-semibold text-purple-600">
            {overview?.avg_weekly_hours || 0}h
          </div>
          <div className="text-xs text-gray-500">周均学时</div>
        </Card>
        <Card size="small" className="text-center">
          <div className="text-2xl font-semibold text-orange-600">
            {overview?.avg_score || 0}
          </div>
          <div className="text-xs text-gray-500">平均成绩</div>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* 成绩分布 */}
        <Card
          title={<span className="text-sm font-medium">成绩分布</span>}
          size="small"
        >
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={scoreDistribution}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="range" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="count" fill="#4f46e5" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Card>

        {/* 薄弱知识点 */}
        <Card
          title={
            <span className="text-sm font-medium">全班薄弱知识点 TOP10</span>
          }
          size="small"
        >
          {weakPoints?.weak_tags?.length > 0 ? (
            <div className="space-y-2">
              {weakPoints.weak_tags
                .slice(0, 10)
                .map((item: any, idx: number) => (
                  <div key={idx} className="flex items-center gap-2">
                    <span className="text-xs text-gray-400 w-6">{idx + 1}</span>
                    <span className="text-sm flex-1">{item.tag}</span>
                    <Progress
                      percent={Math.min(100, item.count * 10)}
                      size="small"
                      style={{ width: 120 }}
                      showInfo={false}
                    />
                    <span className="text-xs text-gray-500 w-8">
                      {item.count}人
                    </span>
                  </div>
                ))}
            </div>
          ) : (
            <div className="text-center text-gray-400 py-8 text-sm">
              暂无数据
            </div>
          )}
        </Card>
      </div>

      {/* 学生排行 */}
      <Card
        title={<span className="text-sm font-medium">学生排行榜</span>}
        size="small"
        extra={
          <Select
            value={rankingSort}
            onChange={handleRankingSort}
            size="small"
            style={{ width: 100 }}
            options={[
              { value: "points", label: "按积分" },
              { value: "score", label: "按成绩" },
              { value: "hours", label: "按学时" },
            ]}
          />
        }
      >
        {loadErrors.ranking ? (
          <div className="py-8 text-center">
            <div className="text-sm text-red-400 mb-2">排行榜数据加载失败</div>
            <Button size="small" type="link" onClick={loadOverviewData}>
              重试
            </Button>
          </div>
        ) : (
          <Table
            dataSource={ranking}
            rowKey="student_id"
            size="small"
            pagination={{ pageSize: 10 }}
            columns={[
              {
                title: "排名",
                key: "rank",
                width: 60,
                render: (_: any, __: any, idx: number) => (
                  <span
                    className={idx < 3 ? "font-semibold text-orange-500" : ""}
                  >
                    {idx + 1}
                  </span>
                ),
              },
              {
                title: "学号",
                dataIndex: "student_id",
                key: "sid",
                width: 100,
              },
              { title: "姓名", dataIndex: "username", key: "name" },
              {
                title: "积分",
                dataIndex: "total_points",
                key: "points",
                width: 80,
                sorter: (a: any, b: any) => a.total_points - b.total_points,
              },
              {
                title: "学时",
                dataIndex: "total_hours",
                key: "hours",
                width: 80,
                render: (h: number) => `${h}h`,
              },
              {
                title: "平均分",
                dataIndex: "avg_score",
                key: "score",
                width: 80,
                render: (s: number) => (
                  <span
                    className={
                      s >= 80
                        ? "text-green-600"
                        : s >= 60
                          ? "text-orange-500"
                          : "text-red-500"
                    }
                  >
                    {s}
                  </span>
                ),
              },
            ]}
          />
        )}
      </Card>
    </div>
  );

  const renderStudentManagement = () => (
    <div className="space-y-4">
      <Card size="small">
        <div className="flex items-center gap-3">
          <Input
            placeholder="搜索学号或姓名"
            prefix={<SearchOutlined />}
            value={studentSearch}
            onChange={(e) => setStudentSearch(e.target.value)}
            style={{ width: 300 }}
          />
          <Tag>{filteredStudents.length} 名学生</Tag>
        </div>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* 学生列表 */}
        <Card title="学生列表" size="small">
          <Table
            dataSource={filteredStudents}
            rowKey="student_id"
            size="small"
            pagination={{ pageSize: 15 }}
            onRow={(record) => ({
              onClick: () => handleViewStudent(record.student_id),
              style: { cursor: "pointer" },
            })}
            columns={[
              {
                title: "学号",
                dataIndex: "student_id",
                key: "sid",
                width: 100,
              },
              { title: "姓名", dataIndex: "username", key: "name" },
              {
                title: "积分",
                dataIndex: "total_points",
                key: "points",
                width: 70,
              },
              {
                title: "状态",
                dataIndex: "trend_state",
                key: "trend",
                width: 80,
                render: (state: string) => (
                  <Tag color={getTrendColor(state)} icon={getTrendIcon(state)}>
                    {state === "growth"
                      ? "增长"
                      : state === "decline"
                        ? "下降"
                        : state === "warning"
                          ? "警告"
                          : "稳定"}
                  </Tag>
                ),
              },
            ]}
          />
        </Card>

        {/* 学生详情 */}
        <Card
          title={selectedStudent ? `${selectedStudent} 详情` : "学生详情"}
          size="small"
        >
          {detailLoading ? (
            <div className="text-center py-12">
              <Spin />
            </div>
          ) : studentDetail ? (
            <div className="space-y-3">
              <Descriptions size="small" column={2} bordered>
                <Descriptions.Item label="姓名">
                  {studentDetail.username}
                </Descriptions.Item>
                <Descriptions.Item label="学号">
                  {studentDetail.student_id}
                </Descriptions.Item>
                <Descriptions.Item label="总积分">
                  {studentDetail.points?.total || 0}
                </Descriptions.Item>
                <Descriptions.Item label="成就数">
                  {studentDetail.achievements_count || 0}
                </Descriptions.Item>
                <Descriptions.Item label="学习时长">
                  {studentDetail.learning_stats?.total_hours || 0}h
                </Descriptions.Item>
                <Descriptions.Item label="完成知识点">
                  {studentDetail.learning_stats?.completed_kps || 0}
                </Descriptions.Item>
                <Descriptions.Item label="测验次数">
                  {studentDetail.learning_stats?.quiz_count || 0}
                </Descriptions.Item>
                <Descriptions.Item label="平均分">
                  {studentDetail.learning_stats?.quiz_avg_score || 0}
                </Descriptions.Item>
              </Descriptions>

              {studentDetail.trend && (
                <div className="p-3 rounded bg-gray-50 border border-gray-200">
                  <div className="text-xs font-medium text-gray-500 mb-2">
                    趋势分析
                  </div>
                  <div className="flex items-center gap-3">
                    <Tag color={getTrendColor(studentDetail.trend.state)}>
                      {getTrendIcon(studentDetail.trend.state)}{" "}
                      {studentDetail.trend.state === "growth"
                        ? "增长"
                        : studentDetail.trend.state === "decline"
                          ? "下降"
                          : studentDetail.trend.state === "warning"
                            ? "警告"
                            : "稳定"}
                    </Tag>
                    <span className="text-sm text-gray-600">
                      因子: {studentDetail.trend.factor?.toFixed(2)} | 3天预测:{" "}
                      {(studentDetail.trend.predicted_mastery_3d * 100).toFixed(
                        0,
                      )}
                      %
                    </span>
                  </div>
                  {studentDetail.trend.intervention && (
                    <div className="text-xs text-orange-600 mt-2">
                      {studentDetail.trend.intervention}
                    </div>
                  )}
                </div>
              )}

              {studentDetail.profile?.weak_areas?.length > 0 && (
                <div>
                  <div className="text-xs font-medium text-gray-500 mb-1">
                    薄弱领域
                  </div>
                  <Space wrap>
                    {studentDetail.profile.weak_areas.map(
                      (a: string, i: number) => (
                        <Tag key={i} color="orange">
                          {a}
                        </Tag>
                      ),
                    )}
                  </Space>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center text-gray-400 py-12 text-sm">
              点击左侧学生查看详情
            </div>
          )}
        </Card>
      </div>
    </div>
  );

  const renderScoreAnalysis = () => (
    <div className="space-y-4">
      <Card title="全班成绩分布" size="small">
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={scoreDistribution}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="range" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar
              dataKey="count"
              name="人数"
              fill="#4f46e5"
              radius={[4, 4, 0, 0]}
            />
          </BarChart>
        </ResponsiveContainer>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <Card title="薄弱知识点统计" size="small">
          {loadErrors.weakPoints ? (
            <div className="py-8 text-center">
              <div className="text-sm text-red-400 mb-2">
                薄弱知识点数据加载失败
              </div>
              <Button size="small" type="link" onClick={loadOverviewData}>
                重试
              </Button>
            </div>
          ) : weakPoints?.weak_tags?.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={weakPoints.weak_tags.slice(0, 6)}
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  dataKey="count"
                  nameKey="tag"
                  label={({ tag, percent }) =>
                    `${tag} ${(percent * 100).toFixed(0)}%`
                  }
                >
                  {weakPoints.weak_tags
                    .slice(0, 6)
                    .map((_: any, idx: number) => (
                      <Cell key={idx} fill={COLORS[idx % COLORS.length]} />
                    ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="text-center text-gray-400 py-12">暂无数据</div>
          )}
        </Card>

        <Card title="薄弱领域统计" size="small">
          {weakPoints?.weak_areas?.length > 0 ? (
            <div className="space-y-3">
              {weakPoints.weak_areas
                .slice(0, 10)
                .map((item: any, idx: number) => (
                  <div key={idx} className="flex items-center gap-2">
                    <span className="text-sm flex-1">{item.area}</span>
                    <Progress
                      percent={Math.min(
                        100,
                        (item.count / (students.length || 1)) * 100,
                      )}
                      size="small"
                      style={{ width: 150 }}
                      format={(p) => `${item.count}人`}
                    />
                  </div>
                ))}
            </div>
          ) : (
            <div className="text-center text-gray-400 py-12">暂无数据</div>
          )}
        </Card>
      </div>
    </div>
  );

  return (
    <div className="space-y-5 pb-12">
      {/* 标题 */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-10 h-10 rounded-lg bg-indigo-50 flex items-center justify-center text-indigo-500">
              <ExperimentOutlined className="text-lg" />
            </div>
            <div>
              <Typography.Title level={4} className="!m-0 !text-gray-900">
                教师工作台
              </Typography.Title>
              <Typography.Text className="text-gray-500 text-sm">
                全班学情概览 · 学生管理 · 成绩分析
              </Typography.Text>
            </div>
          </div>
          <div className="hidden md:flex items-center gap-4">
            <div className="text-center">
              <div className="text-lg font-semibold text-gray-900">
                {overview?.total_students || 0}
              </div>
              <div className="text-xs text-gray-400">学生总数</div>
            </div>
            <div className="w-px h-8 bg-gray-200" />
            <div className="text-center">
              <div className="text-lg font-semibold text-green-600">
                {overview?.active_students || 0}
              </div>
              <div className="text-xs text-gray-400">本周活跃</div>
            </div>
            <div className="w-px h-8 bg-gray-200" />
            <div className="text-center">
              <div className="text-lg font-semibold text-orange-600">
                {overview?.avg_score || 0}
              </div>
              <div className="text-xs text-gray-400">平均分</div>
            </div>
          </div>
        </div>
      </div>

      {/* 内容区 */}
      <Spin spinning={loading}>
        <Tabs
          activeKey={activeTab}
          onChange={(key) => {
            setActiveTab(key);
            if (key === "students" && students.length === 0) loadStudents();
          }}
          items={[
            { key: "overview", label: "全班总览", children: renderOverview() },
            {
              key: "students",
              label: "学生管理",
              children: renderStudentManagement(),
            },
            {
              key: "scores",
              label: "成绩分析",
              children: renderScoreAnalysis(),
            },
          ]}
        />
      </Spin>
    </div>
  );
};

export default TeacherDashboard;
