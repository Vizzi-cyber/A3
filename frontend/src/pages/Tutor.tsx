import React, { useState } from 'react'
import { Typography, Tag, message } from 'antd'
import { RobotOutlined, BulbOutlined, BookOutlined } from '@ant-design/icons'
import { useAppStore } from '../store'
import { tutorApi } from '../services/api'
import { ChatPanel } from '../components/ChatPanel'
import { PageCard } from '../components/PageCard'

import type { ChatMessage, VisionContentItem } from '../types'

const initialMessages: ChatMessage[] = [
  {
    role: 'ai',
    content: '你好！我是你的苏格拉底式AI辅导助手。在学习中遇到任何问题，我都会通过引导式提问帮助你独立思考，而不是直接给你答案。支持发送图片给我分析哦！',
  },
]

const suggestions = [
  '这个概念的核心原理是什么？',
  '能帮我梳理一下知识脉络吗？',
  '这个知识点在实际中如何应用？',
]

const Tutor: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>(initialMessages)
  const [loading, setLoading] = useState(false)
  const studentId = useAppStore((s) => s.studentId)

  const handleSend = async (content: string | VisionContentItem[]) => {
    setMessages((prev) => [...prev, { role: 'user' as const, content }])
    setLoading(true)
    try {
      const res = await tutorApi.ask({
        student_id: studentId,
        question: content,
        session_id: `${studentId}_tutor`,
      })
      setMessages((prev) => [
        ...prev,
        { role: 'ai' as const, content: res.data.response || '让我再思考一下...' },
      ])
    } catch (e: unknown) {
      const errMsg = e instanceof Error ? e.message : '请求失败'
      message.error(errMsg)
      setMessages((prev) => [
        ...prev,
        { role: 'ai' as const, content: '服务暂时不可用，请稍后再试。' },
      ])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="h-[calc(100vh-140px)]">
      <PageCard className="h-full" bodyStyle={{ height: '100%', padding: '20px 24px', display: 'flex', flexDirection: 'column' }}>
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center text-white shadow-glow">
            <BookOutlined />
          </div>
          <div>
            <Typography.Title level={5} className="!m-0 text-slate-800">智能辅导</Typography.Title>
            <Typography.Text className="text-slate-400 text-xs">苏格拉底式教学法 · 机器学习专项</Typography.Text>
          </div>
          <Tag color="success" className="rounded-full border-0 bg-emerald-50 text-emerald-600 font-medium ml-auto">
            在线
          </Tag>
        </div>
        <div className="flex-1 min-h-0">
          <ChatPanel
            messages={messages}
            loading={loading}
            onSend={handleSend}
            title=""
            subtitle=""
            placeholder="输入你的问题..."
            showSuggestions
            suggestions={suggestions}
            showAvatars
            className="h-full"
          />
        </div>
      </PageCard>
    </div>
  )
}

export default Tutor
