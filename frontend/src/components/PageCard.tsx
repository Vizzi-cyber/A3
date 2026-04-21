import React from 'react'
import { Card } from 'antd'

interface PageCardProps {
  children: React.ReactNode
  className?: string
  title?: React.ReactNode
  extra?: React.ReactNode
  bodyStyle?: React.CSSProperties
}

export const PageCard: React.FC<PageCardProps> = ({ children, className = '', title, extra, bodyStyle }) => {
  return (
    <Card
      title={title}
      extra={extra}
      className={`border border-slate-100 rounded-2xl ${className}`}
      styles={{ body: bodyStyle }}
    >
      {children}
    </Card>
  )
}
