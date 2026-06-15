import React, { useEffect, useState } from "react";
import {
  Card,
  Row,
  Col,
  Typography,
  Button,
  List,
  Tag,
  Space,
  message,
  DatePicker,
  Select,
} from "antd";
import {
  FileTextOutlined,
  DownloadOutlined,
  FileExcelOutlined,
  FilePdfOutlined,
  ClockCircleOutlined,
} from "@ant-design/icons";
import { teacherApi } from "../../services/api";
import dayjs from "dayjs";

const ReportExport: React.FC = () => {
  const [students, setStudents] = useState<
    Array<{ student_id: string; username: string }>
  >([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadStudents();
  }, []);

  const loadStudents = async () => {
    setLoading(true);
    try {
      const res = await teacherApi.getStudents();
      setStudents(res.data.students || []);
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  };

  const handleExport = (type: string, format: string) => {
    message.success(`${type}已导出为${format}格式`);
  };

  const reports = [
    {
      title: "学生学习报告",
      desc: "包含学习时长、测验成绩、进度等详细数据",
      icon: <FileTextOutlined className="text-xl" />,
      color: "#4f46e5",
    },
    {
      title: "班级成绩分析",
      desc: "班级整体成绩分布、平均分、排名等统计",
      icon: <FileExcelOutlined className="text-xl" />,
      color: "#10b981",
    },
    {
      title: "学情分析报告",
      desc: "学习趋势、薄弱环节、干预建议等分析",
      icon: <FilePdfOutlined className="text-xl" />,
      color: "#ef4444",
    },
  ];

  const recentExports = [
    { name: "班级学情报告_20240115.pdf", date: "2024-01-15", size: "2.3MB" },
    { name: "学生学习报告_20240114.xlsx", date: "2024-01-14", size: "1.8MB" },
    { name: "成绩分析_20240113.pdf", date: "2024-01-13", size: "3.1MB" },
  ];

  return (
    <div className="space-y-6">
      <Typography.Title level={4} className="!m-0">
        报告导出
      </Typography.Title>

      {/* 报告类型 */}
      <Row gutter={[20, 20]}>
        {reports.map((report, idx) => (
          <Col xs={24} lg={8} key={idx}>
            <Card className="rounded-2xl border-0 shadow-sm hover:shadow-md transition-all">
              <div className="text-center">
                <div
                  className="w-14 h-14 rounded-2xl mx-auto mb-4 flex items-center justify-center text-white"
                  style={{ backgroundColor: report.color }}
                >
                  {report.icon}
                </div>
                <div className="font-semibold text-slate-800 mb-2">
                  {report.title}
                </div>
                <div className="text-slate-400 text-sm mb-4">{report.desc}</div>
                <Space>
                  <Button
                    size="small"
                    onClick={() => handleExport(report.title, "PDF")}
                  >
                    PDF
                  </Button>
                  <Button
                    size="small"
                    onClick={() => handleExport(report.title, "Excel")}
                  >
                    Excel
                  </Button>
                </Space>
              </div>
            </Card>
          </Col>
        ))}
      </Row>

      <Row gutter={[20, 20]}>
        {/* 导出配置 */}
        <Col xs={24} lg={12}>
          <Card className="rounded-2xl border-0 shadow-sm" title="自定义导出">
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-600 mb-2">
                  选择学生
                </label>
                <Select
                  mode="multiple"
                  placeholder="选择要导出的学生"
                  className="w-full"
                  options={students.map((s) => ({
                    value: s.student_id,
                    label: s.username || s.student_id,
                  }))}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-600 mb-2">
                  时间范围
                </label>
                <DatePicker.RangePicker className="w-full" />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-600 mb-2">
                  导出格式
                </label>
                <Select
                  defaultValue="pdf"
                  className="w-full"
                  options={[
                    { value: "pdf", label: "PDF文档" },
                    { value: "excel", label: "Excel表格" },
                    { value: "word", label: "Word文档" },
                  ]}
                />
              </div>
              <Button type="primary" className="bg-primary rounded-xl" block>
                <DownloadOutlined /> 生成报告
              </Button>
            </div>
          </Card>
        </Col>

        {/* 最近导出 */}
        <Col xs={24} lg={12}>
          <Card className="rounded-2xl border-0 shadow-sm" title="最近导出">
            <List
              dataSource={recentExports}
              renderItem={(item) => (
                <List.Item
                  actions={[
                    <Button
                      key="download"
                      type="link"
                      icon={<DownloadOutlined />}
                    >
                      下载
                    </Button>,
                  ]}
                >
                  <List.Item.Meta
                    avatar={
                      <FileTextOutlined className="text-primary text-lg" />
                    }
                    title={item.name}
                    description={
                      <Space>
                        <ClockCircleOutlined className="text-xs" />
                        <span className="text-xs">{item.date}</span>
                        <Tag className="rounded-full border-0 text-xs">
                          {item.size}
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

export default ReportExport;
