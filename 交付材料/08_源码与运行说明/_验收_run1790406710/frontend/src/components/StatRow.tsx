import React from "react";

interface StatRowProps {
  label: string;
  value: React.ReactNode;
  valueClassName?: string;
}

export const StatRow: React.FC<StatRowProps> = React.memo(
  ({ label, value, valueClassName = "text-slate-800" }) => (
    <div className="flex items-center justify-between">
      <span className="text-sm text-slate-600">{label}</span>
      <span className={`text-sm font-bold ${valueClassName}`}>{value}</span>
    </div>
  ),
);

StatRow.displayName = "StatRow";
