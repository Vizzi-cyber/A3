import React, { useState, useEffect } from "react";
import { Card, Row, Col, Typography, Space, Tag, Spin } from "antd";
import {
  FileTextOutlined,
  VideoCameraOutlined,
  CodeOutlined,
  ApartmentOutlined,
  DownloadOutlined,
} from "@ant-design/icons";
import { teacherApi } from "../../services/api";
import PPTGenerator from "../../components/PPTGenerator";

interface Resource {
  resource_id: string;
  name: string;
  type: string;
  created_at: string;
  status: string;
  download_url?: string;
}

const TeachingResources: React.FC = () => {
  const [pptModalOpen, setPptModalOpen] = useState(false);
  const [resources, setResources] = useState<Resource[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadResources();
  }, []);

  const loadResources = async () => {
    setLoading(true);
    try {
      const res = await teacherApi.getResources();
      if (res.data?.resources) {
        setResources(res.data.resources);
      }
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  };

  const resourceTypes = [
    {
      title: "PPT课件",
      desc: "AI自动生成教学PPT",
      icon: <FileTextOutlined className="text-2xl" />,
      color: "#0052ff",
      onClick: () => setPptModalOpen(true),
    },
    {
      title: "教学视频",
      desc: "视频资源管理",
      icon: <VideoCameraOutlined className="text-2xl" />,
      color: "#ef4444",
      onClick: () => {},
    },
    {
      title: "代码示例",
      desc: "示例代码库",
      icon: <CodeOutlined className="text-2xl" />,
      color: "#3b82f6",
      onClick: () => {},
    },
    {
      title: "思维导图",
      desc: "知识结构图",
      icon: <ApartmentOutlined className="text-2xl" />,
      color: "#0052ff",
      onClick: () => {},
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
              onClick={item.onClick}
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

      {/* 已生成的资源列表 */}
      <Card className="rounded-2xl border-0 shadow-sm" title="我的资源">
        <Spin spinning={loading}>
          <div className="space-y-3">
            {resources.length === 0 ? (
              <div className="py-8 text-center">
                <div className="text-slate-400 mb-2">暂无已生成的资源</div>
                <div className="text-xs text-slate-300">
                  点击上方"PPT课件"卡片生成资源
                </div>
              </div>
            ) : (
              resources.map((item) => (
                <div
                  key={item.resource_id}
                  className="flex items-center justify-between p-4 rounded-xl bg-slate-50 hover:bg-white hover:shadow-sm transition-all"
                >
                  <div className="flex items-center gap-3">
                    <FileTextOutlined className="text-[#0052ff] text-lg" />
                    <div>
                      <div className="font-medium text-slate-800">
                        {item.name}
                      </div>
                      <div className="text-xs text-slate-400">
                        {item.created_at?.split("T")[0] || "未知时间"}
                      </div>
                    </div>
                  </div>
                  <Space>
                    <Tag className="rounded-full border-0 bg-blue-50 text-blue-600">
                      {item.type}
                    </Tag>
                    {item.download_url && (
                      <a
                        href={item.download_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1 text-blue-500 hover:text-blue-700"
                      >
                        <DownloadOutlined />
                        下载
                      </a>
                    )}
                  </Space>
                </div>
              ))
            )}
          </div>
        </Spin>
      </Card>

      {/* PPT 生成器弹窗 - 与学生端一致 */}
      <PPTGenerator
        open={pptModalOpen}
        onClose={() => {
          setPptModalOpen(false);
          loadResources();
        }}
      />
    </div>
  );
};

export default TeachingResources;
