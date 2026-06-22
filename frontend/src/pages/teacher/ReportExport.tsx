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
  Empty,
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
  const [recentExports, setRecentExports] = useState<
    Array<{
      export_id: string;
      name: string;
      date: string;
      format: string;
      status: string;
    }>
  >([]);
  const [loading, setLoading] = useState(false);
  const [selectedStudents, setSelectedStudents] = useState<string[]>([]);
  const [dateRange, setDateRange] = useState<
    [dayjs.Dayjs | null, dayjs.Dayjs | null]
  >([null, null]);
  const [exportFormat, setExportFormat] = useState("pdf");

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [studentsRes, exportsRes] = await Promise.all([
        teacherApi.getStudents().catch(() => null),
        teacherApi.getExportRecords().catch(() => null),
      ]);
      if (studentsRes?.data?.students) {
        setStudents(studentsRes.data.students);
      }
      if (exportsRes?.data?.exports) {
        setRecentExports(
          exportsRes.data.exports.map((e) => ({
            export_id: e.export_id,
            name: `${e.report_type}_${e.created_at.split("T")[0]}.${e.format}`,
            date: e.created_at.split("T")[0],
            format: e.format,
            status: e.status,
          })),
        );
      }
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async (type: string, format: string) => {
    try {
      await teacherApi.createExport({
        report_type: type,
        format: format,
      });
      message.success(`${type}导出任务已创建`);
      loadData(); // 刷新导出记录
    } catch {
      message.error("导出失败");
    }
  };

  const reports = [
    {
      title: "学生学习报告",
      desc: "包含学习时长、测验成绩、进度等详细数据",
      icon: <FileTextOutlined className="text-xl" />,
      color: "#0052ff",
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
                  value={selectedStudents}
                  onChange={setSelectedStudents}
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
                <DatePicker.RangePicker
                  className="w-full"
                  value={dateRange}
                  onChange={(dates) => setDateRange(dates || [null, null])}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-600 mb-2">
                  导出格式
                </label>
                <Select
                  value={exportFormat}
                  onChange={setExportFormat}
                  className="w-full"
                  options={[
                    { value: "pdf", label: "PDF文档" },
                    { value: "excel", label: "Excel表格" },
                    { value: "word", label: "Word文档" },
                  ]}
                />
              </div>
              <Button
                type="primary"
                className="bg-[#0052ff] rounded-xl"
                block
                onClick={() => handleExport("自定义报告", exportFormat)}
              >
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
              locale={{
                emptyText: (
                  <Empty
                    description="暂无导出记录"
                    image={Empty.PRESENTED_IMAGE_SIMPLE}
                  />
                ),
              }}
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
                      <FileTextOutlined className="text-[#0052ff] text-lg" />
                    }
                    title={item.name}
                    description={
                      <Space>
                        <ClockCircleOutlined className="text-xs" />
                        <span className="text-xs">{item.date}</span>
                        <Tag className="rounded-full border-0 text-xs">
                          {item.format?.toUpperCase()}
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
