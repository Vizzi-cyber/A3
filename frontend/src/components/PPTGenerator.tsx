import React, { useState, useRef, useCallback } from "react";
import { Modal, Input, Button, Progress, message, Select } from "antd";
import {
  FileTextOutlined,
  DownloadOutlined,
  LoadingOutlined,
  CheckCircleOutlined,
} from "@ant-design/icons";
import { pptApi } from "../services/api";

interface PPTGeneratorProps {
  open: boolean;
  onClose: () => void;
  defaultTopic?: string;
}

const SUBJECTS = [
  "C语言数据结构",
  "C语言程序设计",
  "计算机组成原理",
  "操作系统",
  "计算机网络",
  "算法设计与分析",
  "数据库原理",
];

const PPTGenerator: React.FC<PPTGeneratorProps> = ({
  open,
  onClose,
  defaultTopic = "",
}) => {
  const [topic, setTopic] = useState(defaultTopic);
  const [subject, setSubject] = useState("C语言数据结构");
  const [generating, setGenerating] = useState(false);
  const [taskId, setTaskId] = useState<string | null>(null);
  const [status, setStatus] = useState<string>("");
  const [progress, setProgress] = useState(0);
  const [filename, setFilename] = useState<string | null>(null);
  const [slideCount, setSlideCount] = useState<number | null>(null);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const stopPolling = useCallback(() => {
    if (pollRef.current) {
      clearInterval(pollRef.current);
      pollRef.current = null;
    }
  }, []);

  const handleGenerate = async () => {
    if (!topic.trim()) {
      message.warning("请输入PPT主题");
      return;
    }
    setGenerating(true);
    setProgress(0);
    setStatus("pending");
    setFilename(null);
    setSlideCount(null);

    try {
      const res = await pptApi.generate({ topic: topic.trim(), subject });
      const tid = res.data.task_id;
      setTaskId(tid);
      setStatus("generating");

      // 轮询状态
      pollRef.current = setInterval(async () => {
        try {
          const statusRes = await pptApi.getStatus(tid);
          const data = statusRes.data.data;
          setStatus(data.status);
          setProgress(data.progress);

          if (data.status === "completed") {
            setFilename(data.filename);
            setSlideCount(data.slide_count);
            setGenerating(false);
            stopPolling();
            message.success("PPT生成完成！");
          } else if (data.status === "failed") {
            setGenerating(false);
            stopPolling();
            message.error(data.message || "PPT生成失败");
          }
        } catch {
          // ignore poll errors
        }
      }, 1500);
    } catch {
      setGenerating(false);
      message.error("启动PPT生成失败");
    }
  };

  const handleDownload = () => {
    if (taskId && filename) {
      const url = pptApi.downloadUrl(taskId);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      a.click();
    }
  };

  const handleClose = () => {
    stopPolling();
    setGenerating(false);
    setTaskId(null);
    setStatus("");
    setProgress(0);
    setFilename(null);
    setSlideCount(null);
    onClose();
  };

  return (
    <Modal
      title={
        <div className="flex items-center gap-2">
          <FileTextOutlined className="text-indigo-500 text-lg" />
          <span className="font-bold">AI智能生成PPT</span>
        </div>
      }
      open={open}
      onCancel={handleClose}
      footer={null}
      width={520}
      destroyOnClose
    >
      <div className="space-y-5 py-2">
        {/* 主题输入 */}
        <div>
          <div className="text-sm font-medium text-slate-700 mb-1.5">
            学习主题
          </div>
          <Input
            placeholder="例如：二叉树的遍历、快速排序、图的最短路径..."
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            onPressEnter={handleGenerate}
            disabled={generating}
            size="large"
            className="rounded-xl"
          />
        </div>

        {/* 学科选择 */}
        <div>
          <div className="text-sm font-medium text-slate-700 mb-1.5">学科</div>
          <Select
            value={subject}
            onChange={setSubject}
            disabled={generating}
            className="w-full"
            size="large"
            options={SUBJECTS.map((s) => ({ label: s, value: s }))}
          />
        </div>

        {/* 生成按钮 */}
        {!filename && (
          <Button
            type="primary"
            size="large"
            block
            loading={generating}
            onClick={handleGenerate}
            disabled={!topic.trim()}
            className="rounded-xl h-12 bg-primary"
          >
            {generating ? "正在生成中..." : "开始生成PPT"}
          </Button>
        )}

        {/* 进度 */}
        {generating && (
          <div className="space-y-2">
            <Progress
              percent={progress}
              strokeColor={{
                "0%": "#6366f1",
                "100%": "#10b981",
              }}
              className="!m-0"
            />
            <div className="text-center text-xs text-slate-400">
              {status === "pending" && "准备中..."}
              {status === "generating_outline" && "AI正在生成大纲..."}
              {status === "building_pptx" && "正在构建PPT文件..."}
              {status === "generating" && "处理中..."}
            </div>
          </div>
        )}

        {/* 完成 */}
        {filename && (
          <div className="bg-emerald-50 rounded-xl p-4 border border-emerald-100">
            <div className="flex items-center gap-3">
              <CheckCircleOutlined className="text-emerald-500 text-2xl" />
              <div className="flex-1">
                <div className="font-bold text-emerald-700">生成完成</div>
                <div className="text-xs text-emerald-600 mt-0.5">
                  {slideCount}页 · {filename}
                </div>
              </div>
              <Button
                type="primary"
                icon={<DownloadOutlined />}
                onClick={handleDownload}
                className="rounded-lg bg-emerald-500 border-emerald-500 hover:bg-emerald-600"
              >
                下载
              </Button>
            </div>
          </div>
        )}

        {/* 提示 */}
        <div className="text-xs text-slate-400 space-y-1">
          <p>AI将自动为你生成包含以下深度内容的PPT：</p>
          <ul className="list-disc pl-4 space-y-0.5">
            <li>概念定义 + 核心性质 + 生活类比</li>
            <li>数据结构/语法详解（含C语言结构体代码）</li>
            <li>算法步骤 + 完整C代码 + 复杂度分析</li>
            <li>代码逐行解析</li>
            <li>对比分析（如数组 vs 链表）</li>
            <li>知识结构图</li>
            <li>常见易错点（含错误/正确代码对比）</li>
            <li>练习题（基础+应用+综合，含详细解析）</li>
          </ul>
        </div>
      </div>
    </Modal>
  );
};

export default PPTGenerator;
