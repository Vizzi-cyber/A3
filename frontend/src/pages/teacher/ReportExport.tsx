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
  Select,
  Empty,
} from "antd";
import {
  FileTextOutlined,
  DownloadOutlined,
  TrophyOutlined,
  BarChartOutlined,
  TeamOutlined,
  UnorderedListOutlined,
} from "@ant-design/icons";
import { teacherApi } from "../../services/api";

const ReportExport: React.FC = () => {
  const [students, setStudents] = useState<
    Array<{ student_id: string; username: string }>
  >([]);
  const [loading, setLoading] = useState(false);
  const [selectedStudents, setSelectedStudents] = useState<string[]>([]);
  const [exporting, setExporting] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const res = await teacherApi.getStudents();
      if (res.data?.students) {
        setStudents(res.data.students);
      }
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async (reportType: string) => {
    setExporting(reportType);
    try {
      const res = await teacherApi.exportReport({
        report_type: reportType,
        student_ids: selectedStudents.length > 0 ? selectedStudents : undefined,
      });

      // 下载文件
      const blob = new Blob([res.data as BlobPart], { type: "text/csv" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${reportType}_${new Date().toISOString().slice(0, 10)}.csv`;
      a.click();
      URL.revokeObjectURL(url);

      message.success("导出成功");
    } catch {
      message.error("导出失败");
    } finally {
      setExporting(null);
    }
  };

  const reports = [
    {
      type: "scores",
      title: "成绩报表",
      desc: "包含每位学生的测验次数、平均分、最高分、最低分",
      icon: <TrophyOutlined className="text-xl" />,
      color: "#0052ff",
    },
    {
      type: "progress",
      title: "学习进度报表",
      desc: "包含学习记录数、学习时长、已完成知识点数",
      icon: <BarChartOutlined className="text-xl" />,
      color: "#10b981",
    },
    {
      type: "ranking",
      title: "学生排行榜",
      desc: "按积分排名，包含学习时长、平均分、趋势状态",
      icon: <TeamOutlined className="text-xl" />,
      color: "#f59e0b",
    },
    {
      type: "all",
      title: "综合报表",
      desc: "包含积分、学习时长、知识点、测验、趋势等完整数据",
      icon: <UnorderedListOutlined className="text-xl" />,
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
        {reports.map((report) => (
          <Col xs={24} sm={12} lg={6} key={report.type}>
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
                <div className="text-slate-400 text-sm mb-4 h-10">
                  {report.desc}
                </div>
                <Button
                  type="primary"
                  icon={<DownloadOutlined />}
                  loading={exporting === report.type}
                  onClick={() => handleExport(report.type)}
                  className="bg-[#0052ff] rounded-xl"
                  block
                >
                  导出CSV
                </Button>
              </div>
            </Card>
          </Col>
        ))}
      </Row>

      {/* 筛选学生 */}
      <Card className="rounded-2xl border-0 shadow-sm" title="筛选学生（可选）">
        <div className="space-y-4">
          <Select
            mode="multiple"
            placeholder="选择特定学生导出（留空则导出全部）"
            className="w-full"
            value={selectedStudents}
            onChange={setSelectedStudents}
            options={students.map((s) => ({
              value: s.student_id,
              label: `${s.username || s.student_id} (${s.student_id})`,
            }))}
            maxTagCount={5}
          />
          <div className="text-sm text-slate-400">
            {selectedStudents.length > 0
              ? `已选择 ${selectedStudents.length} 名学生`
              : "未选择学生，将导出全部学生数据"}
          </div>
        </div>
      </Card>

      {/* 使用说明 */}
      <Card className="rounded-2xl border-0 shadow-sm" title="导出说明">
        <div className="space-y-2 text-sm text-slate-600">
          <p>
            <strong>成绩报表：</strong>
            展示每位学生的测验统计，包含测验次数、平均分、最高分和最低分。
          </p>
          <p>
            <strong>学习进度报表：</strong>
            展示学习行为统计，包含学习记录总数、累计学习时长和已完成知识点数。
          </p>
          <p>
            <strong>学生排行榜：</strong>
            按积分从高到低排名，展示积分、学习时长、平均分和趋势状态。
          </p>
          <p>
            <strong>综合报表：</strong>
            整合以上所有维度的完整数据，适合做学期总结。
          </p>
          <p className="text-slate-400">
            导出文件为 CSV 格式，可直接用 Excel 打开。
          </p>
        </div>
      </Card>
    </div>
  );
};

export default ReportExport;
