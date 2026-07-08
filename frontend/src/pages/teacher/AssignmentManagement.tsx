import React, { useEffect, useState } from "react";
import {
  Card,
  Table,
  Button,
  Tag,
  Space,
  Typography,
  Modal,
  Form,
  Input,
  InputNumber,
  Select,
  DatePicker,
  message,
  Descriptions,
  List,
  Popconfirm,
  Tabs,
  Progress,
} from "antd";
import {
  PlusOutlined,
  EyeOutlined,
  DeleteOutlined,
  CheckOutlined,
  BarChartOutlined,
  SearchOutlined,
} from "@ant-design/icons";
import { assignmentApi } from "../../services/api";
import dayjs from "dayjs";

const AssignmentManagement: React.FC = () => {
  const [assignments, setAssignments] = useState<
    Array<{
      assignment_id: string;
      title: string;
      description: string;
      subject: string;
      deadline: string | null;
      max_score: number;
      questions_count: number;
      created_at: string;
      status: string;
      submission_count: number;
    }>
  >([]);
  const [loading, setLoading] = useState(false);
  const [createOpen, setCreateOpen] = useState(false);
  const [createForm] = Form.useForm();
  const [detailOpen, setDetailOpen] = useState(false);
  const [selectedAssignment, setSelectedAssignment] = useState<Record<
    string,
    unknown
  > | null>(null);
  const [submissions, setSubmissions] = useState<
    Array<Record<string, unknown>>
  >([]);
  const [submissionsLoading, setSubmissionsLoading] = useState(false);
  const [gradeModalOpen, setGradeModalOpen] = useState(false);
  const [selectedSubmission, setSelectedSubmission] = useState<Record<
    string,
    unknown
  > | null>(null);
  const [gradeForm] = Form.useForm();
  const [statsOpen, setStatsOpen] = useState(false);
  const [stats, setStats] = useState<Record<string, unknown> | null>(null);
  const [plagiarismResults, setPlagiarismResults] = useState<
    Array<Record<string, unknown>>
  >([]);
  const [plagiarismLoading, setPlagiarismLoading] = useState(false);

  useEffect(() => {
    loadAssignments();
  }, []);

  const loadAssignments = async () => {
    setLoading(true);
    try {
      const res = await assignmentApi.list();
      setAssignments(res.data.assignments || []);
    } catch {
      message.error("加载作业列表失败");
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    try {
      const values = await createForm.validateFields();
      await assignmentApi.create({
        title: values.title,
        description: values.description || "",
        subject: values.subject || "C语言",
        deadline: values.deadline ? values.deadline.toISOString() : undefined,
        max_score: values.max_score || 100,
      });
      message.success("作业创建成功");
      setCreateOpen(false);
      createForm.resetFields();
      loadAssignments();
    } catch {
      // validation error
    }
  };

  const handleViewDetail = async (assignmentId: string) => {
    try {
      const res = await assignmentApi.getDetail(assignmentId);
      setSelectedAssignment(res.data.assignment);
      setDetailOpen(true);
      loadSubmissions(assignmentId);
    } catch {
      message.error("获取作业详情失败");
    }
  };

  const loadSubmissions = async (assignmentId: string) => {
    setSubmissionsLoading(true);
    try {
      const res = await assignmentApi.getSubmissions(assignmentId);
      setSubmissions(res.data.submissions || []);
    } catch {
      // ignore
    } finally {
      setSubmissionsLoading(false);
    }
  };

  const handlePlagiarismCheck = async (assignmentId: string) => {
    setPlagiarismLoading(true);
    try {
      const res = await assignmentApi.plagiarismCheck(assignmentId);
      setPlagiarismResults(res.data.pairs || []);
      if ((res.data.pairs || []).length === 0) {
        message.info("未发现疑似抄袭的提交");
      } else {
        message.warning(`发现 ${res.data.pairs.length} 组疑似相似提交`);
      }
    } catch {
      message.error("查重检测失败");
    } finally {
      setPlagiarismLoading(false);
    }
  };

  const handleGrade = async () => {
    try {
      const values = await gradeForm.validateFields();
      await assignmentApi.grade({
        submission_id: selectedSubmission?.submission_id as string,
        score: values.score,
        feedback: values.feedback || "",
        grade: values.grade,
      });
      message.success("批改完成");
      setGradeModalOpen(false);
      gradeForm.resetFields();
      if (selectedAssignment) {
        loadSubmissions(selectedAssignment.assignment_id as string);
      }
    } catch {
      // validation error
    }
  };

  const handleViewStats = async (assignmentId: string) => {
    try {
      const res = await assignmentApi.getStats(assignmentId);
      setStats(res.data.stats);
      setStatsOpen(true);
    } catch {
      message.error("获取统计失败");
    }
  };

  const handleDelete = async (assignmentId: string) => {
    try {
      await assignmentApi.delete(assignmentId);
      message.success("删除成功");
      loadAssignments();
    } catch {
      message.error("删除失败");
    }
  };

  const columns = [
    {
      title: "作业名称",
      dataIndex: "title",
      key: "title",
      render: (title: string) => <span className="font-medium">{title}</span>,
    },
    {
      title: "学科",
      dataIndex: "subject",
      key: "subject",
    },
    {
      title: "截止时间",
      dataIndex: "deadline",
      key: "deadline",
      render: (d: string | null) =>
        d ? dayjs(d).format("MM-DD HH:mm") : "无限制",
    },
    {
      title: "提交数",
      dataIndex: "submission_count",
      key: "submission_count",
    },
    {
      title: "状态",
      dataIndex: "status",
      key: "status",
      render: (status: string) => (
        <Tag
          className="rounded-full border-0"
          color={status === "active" ? "success" : "default"}
        >
          {status === "active" ? "进行中" : "已关闭"}
        </Tag>
      ),
    },
    {
      title: "操作",
      key: "action",
      render: (_: unknown, record: { assignment_id: string }) => (
        <Space>
          <Button
            type="link"
            size="small"
            icon={<EyeOutlined />}
            onClick={() => handleViewDetail(record.assignment_id)}
          >
            详情
          </Button>
          <Button
            type="link"
            size="small"
            icon={<BarChartOutlined />}
            onClick={() => handleViewStats(record.assignment_id)}
          >
            统计
          </Button>
          <Popconfirm
            title="确定删除此作业？"
            onConfirm={() => handleDelete(record.assignment_id)}
          >
            <Button type="link" size="small" danger icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <Typography.Title level={4} className="!m-0">
          作业管理
        </Typography.Title>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          className="bg-[#0052ff] rounded-xl"
          onClick={() => setCreateOpen(true)}
        >
          创建作业
        </Button>
      </div>

      <Card className="rounded-2xl border-0 shadow-sm">
        <Table
          columns={columns}
          dataSource={assignments}
          rowKey="assignment_id"
          loading={loading}
          pagination={{ pageSize: 10 }}
        />
      </Card>

      {/* 创建作业弹窗 */}
      <Modal
        title="创建作业"
        open={createOpen}
        onCancel={() => {
          setCreateOpen(false);
          createForm.resetFields();
        }}
        onOk={handleCreate}
        okText="创建"
        cancelText="取消"
        width={600}
      >
        <Form form={createForm} layout="vertical">
          <Form.Item
            name="title"
            label="作业名称"
            rules={[{ required: true, message: "请输入作业名称" }]}
          >
            <Input placeholder="例如：第三章课后练习、指针作业1" />
          </Form.Item>
          <Form.Item name="description" label="作业说明">
            <Input.TextArea rows={3} placeholder="可选，作业要求和说明" />
          </Form.Item>
          <div className="grid grid-cols-2 gap-4">
            <Form.Item name="subject" label="学科" initialValue="C语言">
              <Select
                options={[
                  { value: "C语言", label: "C语言" },
                  { value: "电路分析", label: "电路分析" },
                  { value: "数据结构", label: "数据结构" },
                  { value: "STM32嵌入式", label: "STM32嵌入式" },
                ]}
              />
            </Form.Item>
            <Form.Item name="max_score" label="满分" initialValue={100}>
              <InputNumber min={1} max={100} className="w-full" />
            </Form.Item>
          </div>
          <Form.Item name="deadline" label="截止时间">
            <DatePicker
              showTime
              className="w-full"
              placeholder="可选，留空则无截止时间"
            />
          </Form.Item>
        </Form>
      </Modal>

      {/* 作业详情弹窗 */}
      <Modal
        title="作业详情"
        open={detailOpen}
        onCancel={() => {
          setDetailOpen(false);
          setSelectedAssignment(null);
          setSubmissions([]);
          setPlagiarismResults([]);
        }}
        footer={null}
        width={800}
      >
        {selectedAssignment && (
          <Tabs
            items={[
              {
                key: "info",
                label: "基本信息",
                children: (
                  <Descriptions bordered column={2}>
                    <Descriptions.Item label="作业名称">
                      {selectedAssignment.title as string}
                    </Descriptions.Item>
                    <Descriptions.Item label="学科">
                      {selectedAssignment.subject as string}
                    </Descriptions.Item>
                    <Descriptions.Item label="满分">
                      {selectedAssignment.max_score as number}
                    </Descriptions.Item>
                    <Descriptions.Item label="状态">
                      <Tag
                        className="rounded-full border-0"
                        color={
                          selectedAssignment.status === "active"
                            ? "success"
                            : "default"
                        }
                      >
                        {selectedAssignment.status === "active"
                          ? "进行中"
                          : "已关闭"}
                      </Tag>
                    </Descriptions.Item>
                    <Descriptions.Item label="创建时间" span={2}>
                      {dayjs(selectedAssignment.created_at as string).format(
                        "YYYY-MM-DD HH:mm",
                      )}
                    </Descriptions.Item>
                    <Descriptions.Item label="说明" span={2}>
                      {(selectedAssignment.description as string) || "无"}
                    </Descriptions.Item>
                  </Descriptions>
                ),
              },
              {
                key: "submissions",
                label: `提交记录 (${submissions.length})`,
                children: (
                  <List
                    loading={submissionsLoading}
                    dataSource={submissions as Array<Record<string, unknown>>}
                    locale={{ emptyText: "暂无提交" }}
                    renderItem={(item) => (
                      <List.Item
                        actions={[
                          <Button
                            key="grade"
                            type="link"
                            icon={<CheckOutlined />}
                            onClick={() => {
                              setSelectedSubmission(item);
                              gradeForm.setFieldsValue({
                                score: item.score,
                                feedback: item.feedback,
                              });
                              setGradeModalOpen(true);
                            }}
                          >
                            批改
                          </Button>,
                        ]}
                      >
                        <List.Item.Meta
                          title={item.username as string}
                          description={
                            <Space>
                              <span>
                                得分: {item.score as number}/
                                {item.max_score as number}
                              </span>
                              <Tag
                                className="rounded-full border-0"
                                color={
                                  item.status === "graded"
                                    ? "success"
                                    : "warning"
                                }
                              >
                                {item.status === "graded" ? "已批改" : "待批改"}
                              </Tag>
                              <span className="text-xs text-slate-400">
                                {dayjs(item.submitted_at as string).format(
                                  "MM-DD HH:mm",
                                )}
                              </span>
                            </Space>
                          }
                        />
                      </List.Item>
                    )}
                  />
                ),
              },
              {
                key: "plagiarism",
                label: "代码查重",
                children: (
                  <div>
                    <div className="mb-4">
                      <Button
                        type="primary"
                        icon={<SearchOutlined />}
                        loading={plagiarismLoading}
                        onClick={() =>
                          handlePlagiarismCheck(
                            selectedAssignment?.assignment_id as string,
                          )
                        }
                        className="bg-[#0052ff] rounded-xl"
                      >
                        执行查重检测
                      </Button>
                      <Typography.Text type="secondary" className="ml-3">
                        对比所有含代码的提交，检测相似度
                      </Typography.Text>
                    </div>
                    {plagiarismResults.length > 0 ? (
                      <List
                        dataSource={plagiarismResults}
                        renderItem={(item) => (
                          <List.Item>
                            <List.Item.Meta
                              title={
                                <Space>
                                  <Tag color="red">
                                    相似度 {item.similarity as number}%
                                  </Tag>
                                  <span>
                                    {item.student_a as string} {" ← → "}
                                    {item.student_b as string}
                                  </span>
                                </Space>
                              }
                            />
                          </List.Item>
                        )}
                      />
                    ) : (
                      !plagiarismLoading && (
                        <Typography.Text type="secondary">
                          点击上方按钮开始查重检测
                        </Typography.Text>
                      )
                    )}
                  </div>
                ),
              },
            ]}
          />
        )}
      </Modal>

      {/* 批改弹窗 */}
      <Modal
        title="批改作业"
        open={gradeModalOpen}
        onCancel={() => {
          setGradeModalOpen(false);
          gradeForm.resetFields();
        }}
        onOk={handleGrade}
        okText="确认批改"
        cancelText="取消"
      >
        <Form form={gradeForm} layout="vertical">
          <Form.Item
            name="score"
            label="分数"
            rules={[{ required: true, message: "请输入分数" }]}
          >
            <InputNumber
              min={0}
              max={(selectedSubmission?.max_score as number) || 100}
              className="w-full"
            />
          </Form.Item>
          <Form.Item name="grade" label="等级">
            <Select
              placeholder="可选"
              allowClear
              options={[
                { value: "A", label: "A - 优秀" },
                { value: "B", label: "B - 良好" },
                { value: "C", label: "C - 中等" },
                { value: "D", label: "D - 及格" },
                { value: "F", label: "F - 不及格" },
              ]}
            />
          </Form.Item>
          <Form.Item name="feedback" label="评语">
            <Input.TextArea rows={3} placeholder="可选，教师评语" />
          </Form.Item>
        </Form>
      </Modal>

      {/* 统计弹窗 */}
      <Modal
        title="作业统计"
        open={statsOpen}
        onCancel={() => {
          setStatsOpen(false);
          setStats(null);
        }}
        footer={null}
        width={600}
      >
        {stats && (
          <div className="space-y-4">
            <Descriptions bordered column={2}>
              <Descriptions.Item label="作业标题">
                {stats.title as string}
              </Descriptions.Item>
              <Descriptions.Item label="提交率">
                {stats.submission_rate as number}%
              </Descriptions.Item>
              <Descriptions.Item label="已提交">
                {stats.submitted_count as number}人
              </Descriptions.Item>
              <Descriptions.Item label="已批改">
                {stats.graded_count as number}人
              </Descriptions.Item>
              <Descriptions.Item label="平均分">
                {stats.avg_score as number}
              </Descriptions.Item>
              <Descriptions.Item label="最高分">
                {stats.max_score as number}
              </Descriptions.Item>
              <Descriptions.Item label="最低分">
                {stats.min_score as number}
              </Descriptions.Item>
              <Descriptions.Item label="总人数">
                {stats.total_students as number}
              </Descriptions.Item>
            </Descriptions>

            <div>
              <h4 className="font-medium mb-2">分数段分布</h4>
              <div className="space-y-2">
                {Object.entries(
                  stats.distribution as Record<string, number>,
                ).map(([range, count]) => {
                  const total = (stats.submitted_count as number) || 1;
                  const percent = Math.round((count / total) * 100);
                  return (
                    <div key={range} className="flex items-center gap-2">
                      <span className="w-16 text-sm text-slate-600">
                        {range}
                      </span>
                      <Progress
                        percent={percent}
                        size="small"
                        className="flex-1"
                        format={() => `${count}人`}
                      />
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default AssignmentManagement;
