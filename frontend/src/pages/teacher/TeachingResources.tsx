import React, { useState } from "react";
import {
  Card,
  Row,
  Col,
  Button,
  Typography,
  message,
  Space,
  Input,
  Select,
  Tag,
} from "antd";
import {
  FileTextOutlined,
  VideoCameraOutlined,
  CodeOutlined,
  ApartmentOutlined,
  DownloadOutlined,
  PlusOutlined,
} from "@ant-design/icons";
import { pptApi } from "../../services/api";

const TeachingResources: React.FC = () => {
  const [generating, setGenerating] = useState(false);
  const [pptTopic, setPptTopic] = useState("");
  const [pptSubject, setPptSubject] = useState("C语言");

  const handleGeneratePPT = async () => {
    if (!pptTopic.trim()) {
      message.warning("请输入PPT主题");
      return;
    }
    setGenerating(true);
    try {
      const res = await pptApi.generate({
        topic: pptTopic,
        subject: pptSubject,
      });
      message.success("PPT生成任务已提交");
      // 轮询状态
      const taskId = res.data.task_id;
      pollPPTStatus(taskId);
    } catch {
      message.error("PPT生成失败");
    } finally {
      setGenerating(false);
    }
  };

  const pollPPTStatus = async (taskId: string) => {
    let attempts = 0;
    const maxAttempts = 60;
    const poll = async () => {
      try {
        const res = await pptApi.getStatus(taskId);
        const status = res.data.data.status;
        if (status === "completed") {
          message.success("PPT生成完成！");
          return;
        }
        if (status === "failed") {
          message.error("PPT生成失败");
          return;
        }
        if (attempts < maxAttempts) {
          attempts++;
          setTimeout(poll, 2000);
        }
      } catch {
        // ignore
      }
    };
    poll();
  };

  const resourceTypes = [
    {
      title: "PPT课件",
      desc: "AI自动生成教学PPT",
      icon: <FileTextOutlined className="text-2xl" />,
      color: "#0052ff",
      action: "ppt",
    },
    {
      title: "教学视频",
      desc: "视频资源管理",
      icon: <VideoCameraOutlined className="text-2xl" />,
      color: "#ef4444",
      action: "video",
    },
    {
      title: "代码示例",
      desc: "示例代码库",
      icon: <CodeOutlined className="text-2xl" />,
      color: "#3b82f6",
      action: "code",
    },
    {
      title: "思维导图",
      desc: "知识结构图",
      icon: <ApartmentOutlined className="text-2xl" />,
      color: "#0052ff",
      action: "mindmap",
    },
  ];

  return (
    <div className="space-y-6">
      <Typography.Title level={4} className="!m-0">
        备课资源
      </Typography.Title>

      {/* 资源类型卡片 */}
      <Row gutter={[20, 20]}>
        {resourceTypes.map((item, idx) => (
          <Col xs={12} lg={6} key={idx}>
            <Card
              className="rounded-2xl border-0 shadow-sm hover:shadow-md transition-all cursor-pointer"
              hoverable
            >
              <div className="text-center">
                <div
                  className="w-16 h-16 rounded-2xl mx-auto mb-4 flex items-center justify-center text-white"
                  style={{ backgroundColor: item.color }}
                >
                  {item.icon}
                </div>
                <div className="font-semibold text-slate-800">{item.title}</div>
                <div className="text-slate-400 text-sm mt-1">{item.desc}</div>
              </div>
            </Card>
          </Col>
        ))}
      </Row>

      {/* PPT生成 */}
      <Card className="rounded-2xl border-0 shadow-sm" title="AI PPT生成">
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-600 mb-2">
                PPT主题
              </label>
              <Input
                placeholder="例如：C语言指针详解"
                value={pptTopic}
                onChange={(e) => setPptTopic(e.target.value)}
                className="rounded-xl"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-600 mb-2">
                学科
              </label>
              <Select
                value={pptSubject}
                onChange={setPptSubject}
                className="w-full"
                options={[
                  { value: "C语言", label: "C语言" },
                  { value: "电路分析", label: "电路分析" },
                  { value: "数据结构", label: "数据结构" },
                ]}
              />
            </div>
          </div>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={handleGeneratePPT}
            loading={generating}
            className="bg-[#0052ff] rounded-xl"
          >
            生成PPT
          </Button>
        </div>
      </Card>

      {/* 已生成的资源列表 */}
      <Card className="rounded-2xl border-0 shadow-sm" title="我的资源">
        <div className="space-y-3">
          {[
            {
              name: "C语言指针基础.pptx",
              type: "PPT",
              date: "2024-01-15",
              status: "completed",
            },
            {
              name: "电路分析实验报告.docx",
              type: "文档",
              date: "2024-01-14",
              status: "completed",
            },
            {
              name: "数据结构复习.pdf",
              type: "PDF",
              date: "2024-01-13",
              status: "completed",
            },
          ].map((item, idx) => (
            <div
              key={idx}
              className="flex items-center justify-between p-4 rounded-xl bg-slate-50 hover:bg-white hover:shadow-sm transition-all"
            >
              <div className="flex items-center gap-3">
                <FileTextOutlined className="text-[#0052ff] text-lg" />
                <div>
                  <div className="font-medium text-slate-800">{item.name}</div>
                  <div className="text-xs text-slate-400">{item.date}</div>
                </div>
              </div>
              <Space>
                <Tag className="rounded-full border-0 bg-[#0052ff]-50 text-[#0052ff]">
                  {item.type}
                </Tag>
                <Button type="link" icon={<DownloadOutlined />}>
                  下载
                </Button>
              </Space>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
};

export default TeachingResources;
