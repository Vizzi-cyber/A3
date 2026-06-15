import React, { useEffect, useState } from "react";
import {
  Table,
  Card,
  Button,
  Space,
  Tag,
  Input,
  Avatar,
  message,
  Modal,
  Descriptions,
} from "antd";
import {
  SearchOutlined,
  EyeOutlined,
  UserOutlined,
  ReloadOutlined,
} from "@ant-design/icons";
import { useNavigate } from "react-router-dom";
import { teacherApi } from "../../services/api";

interface Student {
  student_id: string;
  username: string;
  email: string | null;
  is_active: boolean;
  total_points: number;
  trend_state: string;
  trend_factor: number;
  created_at: string | null;
}

const StudentManagement: React.FC = () => {
  const navigate = useNavigate();
  const [students, setStudents] = useState<Student[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchText, setSearchText] = useState("");
  const [detailVisible, setDetailVisible] = useState(false);
  const [selectedStudent, setSelectedStudent] = useState<Record<
    string,
    unknown
  > | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);

  useEffect(() => {
    loadStudents();
  }, []);

  const loadStudents = async () => {
    setLoading(true);
    try {
      const res = await teacherApi.getStudents();
      setStudents(res.data.students || []);
    } catch {
      message.error("加载学生列表失败");
    } finally {
      setLoading(false);
    }
  };

  const handleViewDetail = async (studentId: string) => {
    setDetailLoading(true);
    setDetailVisible(true);
    try {
      const res = await teacherApi.getStudentDetail(studentId);
      setSelectedStudent(res.data.student || null);
    } catch {
      message.error("获取学生详情失败");
    } finally {
      setDetailLoading(false);
    }
  };

  const columns = [
    {
      title: "学号",
      dataIndex: "student_id",
      key: "student_id",
      render: (id: string) => <span className="font-mono">{id}</span>,
    },
    {
      title: "姓名",
      dataIndex: "username",
      key: "username",
      render: (name: string, record: Student) => (
        <Space>
          <Avatar
            size="small"
            icon={<UserOutlined />}
            className="bg-primary/10 text-primary"
          />
          {name || record.student_id}
        </Space>
      ),
    },
    {
      title: "积分",
      dataIndex: "total_points",
      key: "total_points",
      sorter: (a: Student, b: Student) => a.total_points - b.total_points,
      render: (points: number) => (
        <span className="font-semibold text-primary">{points}</span>
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
          {state === "growth"
            ? "上升"
            : state === "warning"
              ? "预警"
              : state === "decline"
                ? "下滑"
                : "平稳"}
        </Tag>
      ),
    },
    {
      title: "状态",
      dataIndex: "is_active",
      key: "is_active",
      render: (active: boolean) => (
        <Tag
          className="rounded-full border-0"
          color={active ? "success" : "default"}
        >
          {active ? "活跃" : "未激活"}
        </Tag>
      ),
    },
    {
      title: "操作",
      key: "action",
      render: (_: unknown, record: Student) => (
        <Button
          type="link"
          icon={<EyeOutlined />}
          onClick={() => handleViewDetail(record.student_id)}
        >
          详情
        </Button>
      ),
    },
  ];

  const filteredStudents = students.filter(
    (s) =>
      s.student_id.toLowerCase().includes(searchText.toLowerCase()) ||
      (s.username || "").toLowerCase().includes(searchText.toLowerCase()),
  );

  const learningStats = (selectedStudent as Record<string, unknown>)
    ?.learning_stats as Record<string, unknown> | undefined;
  const profile = (selectedStudent as Record<string, unknown>)?.profile as
    | Record<string, unknown>
    | undefined;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold m-0">学生管理</h2>
        <Button icon={<ReloadOutlined />} onClick={loadStudents}>
          刷新
        </Button>
      </div>

      <Card className="rounded-2xl border-0 shadow-sm">
        <div className="mb-4">
          <Input
            placeholder="搜索学号或姓名"
            prefix={<SearchOutlined className="text-slate-400" />}
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            className="rounded-xl max-w-xs"
            allowClear
          />
        </div>
        <Table
          columns={columns}
          dataSource={filteredStudents}
          rowKey="student_id"
          loading={loading}
          pagination={{ pageSize: 10 }}
        />
      </Card>

      <Modal
        title="学生详情"
        open={detailVisible}
        onCancel={() => setDetailVisible(false)}
        footer={null}
        width={600}
      >
        {detailLoading ? (
          <div className="py-8 text-center text-slate-400">加载中...</div>
        ) : selectedStudent ? (
          <div className="space-y-4">
            <Descriptions bordered column={2}>
              <Descriptions.Item label="学号">
                {selectedStudent.student_id as string}
              </Descriptions.Item>
              <Descriptions.Item label="姓名">
                {selectedStudent.username as string}
              </Descriptions.Item>
              <Descriptions.Item label="积分">
                {((selectedStudent.points as Record<string, unknown>)
                  ?.total as number) || 0}
              </Descriptions.Item>
              <Descriptions.Item label="成就数">
                {(selectedStudent.achievements_count as number) || 0}
              </Descriptions.Item>
              <Descriptions.Item label="学习记录数">
                {(learningStats?.total_records as number) || 0}
              </Descriptions.Item>
              <Descriptions.Item label="学习时长">
                {(learningStats?.total_hours as number) || 0}h
              </Descriptions.Item>
              <Descriptions.Item label="测验平均分">
                {(learningStats?.quiz_avg_score as number) || 0}
              </Descriptions.Item>
              <Descriptions.Item label="测验次数">
                {(learningStats?.quiz_count as number) || 0}
              </Descriptions.Item>
            </Descriptions>

            {profile && (
              <div className="mt-4">
                <h4 className="font-medium mb-2">薄弱环节</h4>
                <div className="flex flex-wrap gap-2">
                  {((profile.weak_areas as string[]) || []).length ? (
                    (profile.weak_areas as string[]).map((area, idx) => (
                      <Tag key={idx} className="rounded-full" color="orange">
                        {area}
                      </Tag>
                    ))
                  ) : (
                    <span className="text-slate-400 text-sm">暂无数据</span>
                  )}
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="py-8 text-center text-slate-400">暂无数据</div>
        )}
      </Modal>
    </div>
  );
};

export default StudentManagement;
