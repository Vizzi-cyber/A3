import React from 'react'
import { Card, Space, Typography } from 'antd'

interface StatCardProps {
  icon: React.ReactNode
  color: string
  title: string
  value: React.ReactNode
  suffix?: string
  onClick?: () => void
}

export const StatCard: React.FC<StatCardProps> = ({ icon, color, title, value, suffix, onClick }) => {
  return (
    <Card
      className={`border border-slate-100 rounded-2xl ${onClick ? 'cursor-pointer' : ''}`}
      onClick={onClick}
      styles={{ body: { padding: '20px' } }}
    >
      <Space align="start" size={14}>
        <div
          className="w-11 h-11 rounded-xl flex items-center justify-center text-white text-lg shrink-0"
          style={{ background: color }}
        >
          {icon}
        </div>
        <div>
          <Typography.Text className="text-slate-500 text-sm block">{title}</Typography.Text>
          <div className="flex items-baseline gap-1">
            <Typography.Text className="text-[26px] font-bold text-slate-800 tracking-tight leading-tight">
              {value}
            </Typography.Text>
            {suffix && <span className="text-sm font-medium text-slate-400">{suffix}</span>}
          </div>
        </div>
      </Space>
    </Card>
  )
}
