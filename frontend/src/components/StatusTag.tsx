import React from "react";
import { Tag } from "antd";

const statusColors: Record<string, string> = {
  completed: "#10b981",
  "in-progress": "#4f46e5",
  pending: "#94a3b8",
  locked: "#cbd5e1",
};

const statusBg: Record<string, string> = {
  completed: "#ecfdf5",
  "in-progress": "#eef2ff",
  pending: "#f8fafc",
  locked: "#f1f5f9",
};

const statusLabels: Record<string, string> = {
  completed: "已完成",
  "in-progress": "进行中",
  pending: "未开始",
  locked: "未解锁",
};

interface StatusTagProps {
  status: string;
  className?: string;
}

export const StatusTag: React.FC<StatusTagProps> = React.memo(
  ({ status, className = "" }) => {
    return (
      <Tag
        className={`rounded-full border-0 text-xs font-medium ${className}`}
        style={{
          background: statusBg[status] || statusBg.pending,
          color: statusColors[status] || statusColors.pending,
        }}
      >
        {statusLabels[status] || statusLabels.pending}
      </Tag>
    );
  },
);

StatusTag.displayName = "StatusTag";

export { statusColors, statusBg, statusLabels };
