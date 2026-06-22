import React, { useEffect, useState } from "react";
import {
  Typography,
  Tabs,
  List,
  Avatar,
  Tag,
  Space,
  Button,
  Row,
  Col,
  Card,
  Statistic,
  message,
  Input,
} from "antd";
import {
  UserOutlined,
  TeamOutlined,
  BarChartOutlined,
  TrophyOutlined,
  BookOutlined,
  ClockCircleOutlined,
  FireOutlined,
  EditOutlined,
  SaveOutlined,
  DeleteOutlined,
  EyeOutlined,
} from "@ant-design/icons";
import { useNavigate } from "react-router-dom";
import { useAppStore } from "../store";
import { teacherApi } from "../services/api";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

interface StudentBrief {
  student_id: string;
  username: string;
  total_points: number;
  trend_state: string;
  trend_factor: number;
}

interface OverviewData {
  total_students: number;
  active_students: number;
  avg_weekly_hours: number;
  avg_score: number;
  total_quizzes: number;
  total_records: number;
}

interface TeachingNote {
  id: string;
  date: string;
  title: string;
  content: string;
  tags: string[];
}

const TeacherPersonalSpace: React.FC = () => {
  const navigate = useNavigate();
  const userInfo = useAppStore((s) => s.userInfo);
  const [activeTab, setActiveTab] = useState("overview");
  const [students, setStudents] = useState<StudentBrief[]>([]);
  const [overview, setOverview] = useState<OverviewData | null>(null);
  const [loading, setLoading] = useState(false);
  const [teachingNotes, setTeachingNotes] = useState<TeachingNote[]>([]);
  const [newNote, setNewNote] = useState({ title: "", content: "" });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [studentsRes, overviewRes] = await Promise.all([
        teacherApi.getStudents(),
        teacherApi.getOverview(),
      ]);
      setStudents(studentsRes.data.students || []);
      setOverview(overviewRes.data.overview || null);
    } catch {
      message.error("加载数据失败");
    } finally {
      setLoading(false);
    }
  };

  const handleSaveNote = () => {
    if (!newNote.title.trim() || !newNote.content.trim()) {
      message.warning("请填写标题和内容");
      return;
    }
    const note: TeachingNote = {
      id: `note_${Date.now()}`,
      date: new Date().toISOString().slice(0, 10),
      title: newNote.title,
      content: newNote.content,
      tags: ["教学反思"],
    };
    setTeachingNotes([note, ...teachingNotes]);
    setNewNote({ title: "", content: "" });
    message.success("笔记已保存");
  };

  const handleDeleteNote = (id: string) => {
    setTeachingNotes(teachingNotes.filter((n) => n.id !== id));
    message.success("已删除");
  };

  // 获取趋势颜色
  const getTrendColor = (state: string) => {
    switch (state) {
      case "growth":
        return "text-emerald-500";
      case "warning":
        return "text-red-500";
      case "decline":
        return "text-amber-500";
      default:
        return "text-slate-400";
    }
  };

  const getTrendLabel = (state: string) => {
    switch (state) {
      case "growth":
        return "上升";
      case "warning":
        return "预警";
      case "decline":
        return "下滑";
      default:
        return "平稳";
    }
  };

  // 模拟学生学习趋势数据
  const trendData = students.slice(0, 10).map((s) => ({
    name: s.username?.slice(0, 4) || s.student_id.slice(0, 8),
    points: s.total_points,
    trend: Math.round((s.trend_factor + 1) * 50),
  }));

  return (
    <div className="space-y-6">
      {/* 教师信息卡片 */}
      <div className="bg-gradient-to-r from-primary to-blue-600 rounded-2xl p-6 text-white">
        <div className="flex items-center gap-4">
          <Avatar
            size={64}
            icon={<UserOutlined />}
            className="bg-white/20 border-2 border-white/40"
          />
          <div className="flex-1">
            <Typography.Title level={3} className="!m-0 text-white">
              {userInfo?.username || "教师"}
            </Typography.Title>
            <Typography.Text className="text-white/80">
              教师工作台 · 个性化学习管理系统
            </Typography.Text>
          </div>
          <div className="text-right">
            <div className="text-3xl font-bold">{students.length}</div>
            <div className="text-white/80 text-sm">管理学生</div>
          </div>
        </div>
      </div>

      <Tabs
        activeKey={activeTab}
        onChange={setActiveTab}
        className="custom-tabs"
        items={[
          {
            key: "overview",
            label: (
              <span className="flex items-center gap-1.5">
                <BarChartOutlined /> 教学概览
              </span>
            ),
            children: (
              <div className="space-y-6">
                {/* 统计卡片 */}
                <Row gutter={[20, 20]}>
                  <Col xs={12} lg={6}>
                    <Card className="rounded-2xl border-0 shadow-sm">
                      <Statistic
                        title="总学生数"
                        value={overview?.total_students || 0}
                        prefix={<TeamOutlined className="text-primary" />}
                      />
                    </Card>
                  </Col>
                  <Col xs={12} lg={6}>
                    <Card className="rounded-2xl border-0 shadow-sm">
                      <Statistic
                        title="活跃学生(7天)"
                        value={overview?.active_students || 0}
                        prefix={<FireOutlined className="text-orange-500" />}
                      />
                    </Card>
                  </Col>
                  <Col xs={12} lg={6}>
                    <Card className="rounded-2xl border-0 shadow-sm">
                      <Statistic
                        title="平均测验分"
                        value={overview?.avg_score || 0}
                        precision={1}
                        prefix={<TrophyOutlined className="text-amber-500" />}
                      />
                    </Card>
                  </Col>
                  <Col xs={12} lg={6}>
                    <Card className="rounded-2xl border-0 shadow-sm">
                      <Statistic
                        title="总学习记录"
                        value={overview?.total_records || 0}
                        prefix={<BookOutlined className="text-blue-500" />}
                      />
                    </Card>
                  </Col>
                </Row>

                {/* 学生积分趋势 */}
                <div className="bg-white rounded-2xl border border-slate-100 p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div className="font-semibold text-slate-800">
                      学生积分概览
                    </div>
                    <Button type="link" onClick={() => navigate("/teacher")}>
                      查看完整排行
                    </Button>
                  </div>
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={trendData}>
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
                </div>
              </div>
            ),
          },
          {
            key: "students",
            label: (
              <span className="flex items-center gap-1.5">
                <TeamOutlined /> 学生管理
              </span>
            ),
            children: (
              <div className="bg-white rounded-2xl border border-slate-100 p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="font-semibold text-slate-800">学生列表</div>
                  <Button type="primary" onClick={() => navigate("/teacher")}>
                    进入教师工作台
                  </Button>
                </div>
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
                          onClick={() => navigate("/teacher")}
                        >
                          查看详情
                        </Button>,
                      ]}
                    >
                      <List.Item.Meta
                        avatar={
                          <Avatar
                            icon={<UserOutlined />}
                            className="bg-primary/10 text-primary"
                          />
                        }
                        title={student.username || student.student_id}
                        description={
                          <Space>
                            <span>积分: {student.total_points}</span>
                            <span
                              className={getTrendColor(student.trend_state)}
                            >
                              {getTrendLabel(student.trend_state)}
                            </span>
                          </Space>
                        }
                      />
                    </List.Item>
                  )}
                />
              </div>
            ),
          },
          {
            key: "notes",
            label: (
              <span className="flex items-center gap-1.5">
                <EditOutlined /> 教学笔记
              </span>
            ),
            children: (
              <div className="space-y-5">
                {/* 新建笔记 */}
                <div className="bg-white rounded-2xl border border-slate-100 p-6">
                  <div className="font-semibold text-slate-800 mb-4">
                    写教学笔记
                  </div>
                  <Input
                    placeholder="笔记标题"
                    value={newNote.title}
                    onChange={(e) =>
                      setNewNote({ ...newNote, title: e.target.value })
                    }
                    className="mb-3 rounded-xl"
                  />
                  <Input.TextArea
                    rows={4}
                    placeholder="记录教学心得、学生反馈、课程改进想法..."
                    value={newNote.content}
                    onChange={(e) =>
                      setNewNote({ ...newNote, content: e.target.value })
                    }
                    className="rounded-xl mb-3"
                  />
                  <Button
                    type="primary"
                    icon={<SaveOutlined />}
                    onClick={handleSaveNote}
                    className="bg-primary"
                  >
                    保存笔记
                  </Button>
                </div>

                {/* 笔记列表 */}
                <div className="bg-white rounded-2xl border border-slate-100 p-6">
                  <div className="font-semibold text-slate-800 mb-4">
                    我的笔记
                  </div>
                  {teachingNotes.length ? (
                    <div className="space-y-4">
                      {teachingNotes.map((note) => (
                        <div
                          key={note.id}
                          className="p-4 rounded-xl bg-slate-50 border border-slate-100 hover:border-primary/30 hover:bg-white hover:shadow-sm transition-all"
                        >
                          <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center gap-2">
                              <span className="font-medium text-slate-800">
                                {note.title}
                              </span>
                              <Tag className="rounded-full border-0 bg-primary-50 text-primary text-xs">
                                {note.tags[0]}
                              </Tag>
                            </div>
                            <Space>
                              <span className="text-xs text-slate-400">
                                {note.date}
                              </span>
                              <Button
                                type="text"
                                size="small"
                                danger
                                icon={<DeleteOutlined />}
                                onClick={() => handleDeleteNote(note.id)}
                              />
                            </Space>
                          </div>
                          <Typography.Paragraph className="text-slate-600 text-sm !mb-0 whitespace-pre-wrap">
                            {note.content}
                          </Typography.Paragraph>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-slate-400 text-sm py-8 text-center">
                      暂无笔记，开始记录你的教学心得吧
                    </div>
                  )}
                </div>
              </div>
            ),
          },
        ]}
      />
    </div>
  );
};

export default TeacherPersonalSpace;
