import React from "react";
import { Card } from "antd";

interface SectionCardProps {
  children: React.ReactNode;
  className?: string;
  title?: React.ReactNode;
  extra?: React.ReactNode;
  bodyPadding?: string | number;
}

export const SectionCard: React.FC<SectionCardProps> = React.memo(
  ({ children, className = "", title, extra, bodyPadding = "24px" }) => (
    <Card
      className={`border border-slate-100 rounded-2xl shadow-card ${className}`}
      title={title}
      extra={extra}
      styles={{ body: { padding: bodyPadding } }}
    >
      {children}
    </Card>
  ),
);

SectionCard.displayName = "SectionCard";
