import React, { useEffect, useState } from "react";
import { Drawer, List, Typography, Tag, Spin, Empty } from "antd";
import {
  ThunderboltOutlined,
  UserOutlined,
  RobotOutlined,
  ClockCircleOutlined,
} from "@ant-design/icons";
import { adjustmentLogApi } from "../services/api";
import type { PathAdjustmentLog } from "../types";

const { Text } = Typography;

interface AdjustmentLogPanelProps {
  open: boolean;
  onClose: () => void;
  studentId: string;
}

const triggerTypeConfig: Record<
  string,
  { icon: React.ReactNode; color: string; label: string }
> = {
  onboarding: {
    icon: <RobotOutlined />,
    color: "blue",
    label: "初始生成",
  },
  auto: {
    icon: <ThunderboltOutlined />,
    color: "orange",
    label: "自动调整",
  },
  manual: {
    icon: <UserOutlined />,
    color: "green",
    label: "手动调整",
  },
};

const AdjustmentLogPanel: React.FC<AdjustmentLogPanelProps> = ({
  open,
  onClose,
  studentId,
}) => {
  const [logs, setLogs] = useState<PathAdjustmentLog[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (open && studentId) {
      setLoading(true);
      adjustmentLogApi
        .getLogs(studentId)
        .then((res) => {
          setLogs(res.data?.data || []);
        })
        .catch(() => {
          setLogs([]);
        })
        .finally(() => {
          setLoading(false);
        });
    }
  }, [open, studentId]);

  const formatTime = (isoString: string) => {
    if (!isoString) return "";
    const date = new Date(isoString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMin = Math.floor(diffMs / 60000);
    const diffHour = Math.floor(diffMs / 3600000);
    const diffDay = Math.floor(diffMs / 86400000);

    if (diffMin < 1) return "刚刚";
    if (diffMin < 60) return `${diffMin}分钟前`;
    if (diffHour < 24) return `${diffHour}小时前`;
    if (diffDay < 7) return `${diffDay}天前`;
    return date.toLocaleDateString("zh-CN");
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return "green";
    if (confidence >= 0.5) return "orange";
    return "red";
  };

  return (
    <Drawer
      title="路径调整记录"
      placement="right"
      onClose={onClose}
      open={open}
      width={400}
      className="rounded-l-2xl"
    >
      {loading ? (
        <div className="flex justify-center py-12">
          <Spin />
        </div>
      ) : logs.length === 0 ? (
        <Empty description="暂无调整记录" className="py-12" />
      ) : (
        <List
          dataSource={logs}
          renderItem={(log) => {
            const config =
              triggerTypeConfig[log.trigger_type] || triggerTypeConfig.auto;
            return (
              <List.Item className="!items-start">
                <div className="w-full">
                  <div className="flex items-center gap-2 mb-2">
                    <Tag
                      icon={config.icon}
                      color={config.color}
                      className="rounded-full"
                    >
                      {config.label}
                    </Tag>
                    <Tag
                      color={getConfidenceColor(log.confidence)}
                      className="rounded-full"
                    >
                      置信度 {(log.confidence * 100).toFixed(0)}%
                    </Tag>
                  </div>
                  <Text className="text-sm text-slate-600 block mb-1">
                    {log.reason || "无调整原因"}
                  </Text>
                  <div className="flex items-center gap-1 text-xs text-slate-400">
                    <ClockCircleOutlined />
                    <span>{formatTime(log.created_at)}</span>
                  </div>

                  {/* 路径变化摘要 */}
                  {log.old_path_snapshot && log.new_path_snapshot && (
                    <div className="mt-2 p-2 bg-slate-50 rounded-lg text-xs">
                      <Text className="text-slate-500">
                        路径阶段数：{log.old_path_snapshot.stages?.length || 0}{" "}
                        → {log.new_path_snapshot.stages?.length || 0}
                      </Text>
                    </div>
                  )}
                </div>
              </List.Item>
            );
          }}
        />
      )}
    </Drawer>
  );
};

export default AdjustmentLogPanel;
