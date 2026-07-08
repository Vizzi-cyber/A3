import React, { useState, useEffect } from "react";
import {
  Card,
  Row,
  Col,
  Typography,
  Space,
  Tag,
  Spin,
  Modal,
  Input,
  Select,
  Button,
  message,
  Tabs,
  Empty,
} from "antd";
import {
  FileTextOutlined,
  CodeOutlined,
  ApartmentOutlined,
  DownloadOutlined,
  CopyOutlined,
} from "@ant-design/icons";
import { pptApi, resourceApi, teacherApi } from "../../services/api";
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

  // 思维导图
  const [mindmapOpen, setMindmapOpen] = useState(false);
  const [mindmapTopic, setMindmapTopic] = useState("");
  const [mindmapGenerating, setMindmapGenerating] = useState(false);
  const [mindmapData, setMindmapData] = useState<Record<
    string,
    unknown
  > | null>(null);

  // 代码示例
  const [codeOpen, setCodeOpen] = useState(false);
  const [codeTopic, setCodeTopic] = useState("");
  const [codeLanguage, setCodeLanguage] = useState("C");
  const [codeGenerating, setCodeGenerating] = useState(false);
  const [codeData, setCodeData] = useState<string | null>(null);

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

  const handleGenerateMindmap = async () => {
    if (!mindmapTopic.trim()) {
      message.warning("请输入主题");
      return;
    }
    setMindmapGenerating(true);
    try {
      const res = await resourceApi.generateMindmap({
        student_id: "teacher_001",
        topic: mindmapTopic,
      });
      if (res.data?.mindmap) {
        setMindmapData(res.data.mindmap);
        message.success("思维导图生成成功");
      }
    } catch {
      message.error("思维导图生成失败");
    } finally {
      setMindmapGenerating(false);
    }
  };

  const handleGenerateCode = async () => {
    if (!codeTopic.trim()) {
      message.warning("请输入主题");
      return;
    }
    setCodeGenerating(true);
    try {
      const res = await resourceApi.generateCode({
        student_id: "teacher_001",
        topic: codeTopic,
        language: codeLanguage,
      });
      if (res.data?.code) {
        setCodeData(res.data.code);
        message.success("代码示例生成成功");
      }
    } catch {
      message.error("代码示例生成失败");
    } finally {
      setCodeGenerating(false);
    }
  };

  const handleCopyCode = () => {
    if (codeData) {
      navigator.clipboard.writeText(codeData);
      message.success("已复制到剪贴板");
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
      title: "代码示例",
      desc: "示例代码库",
      icon: <CodeOutlined className="text-2xl" />,
      color: "#3b82f6",
      onClick: () => setCodeOpen(true),
    },
    {
      title: "思维导图",
      desc: "知识结构图",
      icon: <ApartmentOutlined className="text-2xl" />,
      color: "#0052ff",
      onClick: () => setMindmapOpen(true),
    },
  ];

  const renderMindmapTree = (
    node: Record<string, unknown>,
    level = 0,
  ): React.ReactNode => {
    const name = (node.name || node.root || "") as string;
    const children = (node.children || []) as Record<string, unknown>[];
    return (
      <div key={name + level} style={{ marginLeft: level * 20 }}>
        <div
          className={`py-1 px-2 rounded ${level === 0 ? "font-bold text-[#0052ff] text-base" : "text-slate-700 text-sm"}`}
        >
          {level > 0 && <span className="text-slate-300 mr-1">-</span>}
          {name}
        </div>
        {children.map((child, idx) => (
          <div key={idx}>{renderMindmapTree(child, level + 1)}</div>
        ))}
      </div>
    );
  };

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
                  点击上方卡片生成资源
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

      {/* PPT 生成器弹窗 */}
      <PPTGenerator
        open={pptModalOpen}
        onClose={() => {
          setPptModalOpen(false);
          loadResources();
        }}
      />

      {/* 思维导图弹窗 */}
      <Modal
        title="AI 思维导图生成"
        open={mindmapOpen}
        onCancel={() => {
          setMindmapOpen(false);
          setMindmapData(null);
          setMindmapTopic("");
        }}
        footer={null}
        width={700}
      >
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-600 mb-2">
              主题
            </label>
            <Input
              placeholder="例如：C语言指针详解、数据结构总复习"
              value={mindmapTopic}
              onChange={(e) => setMindmapTopic(e.target.value)}
              onPressEnter={handleGenerateMindmap}
            />
          </div>
          <Button
            type="primary"
            icon={<ApartmentOutlined />}
            onClick={handleGenerateMindmap}
            loading={mindmapGenerating}
            className="bg-[#0052ff]"
          >
            生成思维导图
          </Button>

          {mindmapData && (
            <div className="mt-4 p-4 bg-slate-50 rounded-xl max-h-96 overflow-auto">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-slate-600">
                  生成结果
                </span>
                <Button
                  size="small"
                  icon={<CopyOutlined />}
                  onClick={() => {
                    navigator.clipboard.writeText(
                      JSON.stringify(mindmapData, null, 2),
                    );
                    message.success("已复制到剪贴板");
                  }}
                >
                  复制JSON
                </Button>
              </div>
              {renderMindmapTree(mindmapData)}
            </div>
          )}
        </div>
      </Modal>

      {/* 代码示例弹窗 */}
      <Modal
        title="AI 代码示例生成"
        open={codeOpen}
        onCancel={() => {
          setCodeOpen(false);
          setCodeData(null);
          setCodeTopic("");
        }}
        footer={null}
        width={800}
      >
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-600 mb-2">
                主题
              </label>
              <Input
                placeholder="例如：链表增删查改、冒泡排序实现"
                value={codeTopic}
                onChange={(e) => setCodeTopic(e.target.value)}
                onPressEnter={handleGenerateCode}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-600 mb-2">
                编程语言
              </label>
              <Select
                value={codeLanguage}
                onChange={setCodeLanguage}
                className="w-full"
                options={[
                  { value: "C", label: "C语言" },
                  { value: "Python", label: "Python" },
                  { value: "Java", label: "Java" },
                ]}
              />
            </div>
          </div>
          <Button
            type="primary"
            icon={<CodeOutlined />}
            onClick={handleGenerateCode}
            loading={codeGenerating}
            className="bg-[#0052ff]"
          >
            生成代码示例
          </Button>

          {codeData && (
            <div className="mt-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-slate-600">
                  生成结果
                </span>
                <Space>
                  <Button
                    size="small"
                    icon={<CopyOutlined />}
                    onClick={handleCopyCode}
                  >
                    复制代码
                  </Button>
                  <Button
                    size="small"
                    icon={<DownloadOutlined />}
                    onClick={() => {
                      const ext =
                        codeLanguage.toLowerCase() === "c"
                          ? "c"
                          : codeLanguage.toLowerCase();
                      const blob = new Blob([codeData], { type: "text/plain" });
                      const url = URL.createObjectURL(blob);
                      const a = document.createElement("a");
                      a.href = url;
                      a.download = `${codeTopic}.${ext}`;
                      a.click();
                      URL.revokeObjectURL(url);
                    }}
                  >
                    下载文件
                  </Button>
                </Space>
              </div>
              <pre className="p-4 bg-slate-900 text-green-400 rounded-xl text-sm overflow-auto max-h-80 font-mono">
                {codeData}
              </pre>
            </div>
          )}
        </div>
      </Modal>
    </div>
  );
};

export default TeachingResources;
