import React from "react";
import {
  CheckCircleOutlined,
  ClockCircleOutlined,
  LockOutlined,
  EnvironmentOutlined,
  RocketOutlined,
} from "@ant-design/icons";

export type NodeStatus = "completed" | "in-progress" | "pending" | "locked";

interface StatusIconProps {
  status: NodeStatus;
  pendingIcon?: React.ReactNode;
  className?: string;
}

export const StatusIcon: React.FC<StatusIconProps> = ({
  status,
  pendingIcon = <EnvironmentOutlined />,
  className,
}) => {
  const icon =
    status === "completed" ? (
      <CheckCircleOutlined />
    ) : status === "in-progress" ? (
      <ClockCircleOutlined />
    ) : status === "locked" ? (
      <LockOutlined />
    ) : (
      pendingIcon
    );

  return className ? <span className={className}>{icon}</span> : <>{icon}</>;
};
