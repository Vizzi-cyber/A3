import React, { useState } from 'react'
import { Typography, Tag, message, Space, Badge, Tooltip } from 'antd'
import {
  RobotOutlined,
  BulbOutlined,
  BookOutlined,
  NodeIndexOutlined,
  ToolOutlined,
  SafetyOutlined,
  ApartmentOutlined,
  FlagFilled,
  CheckCircleFilled,
} from '@ant-design/icons'
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
  const [multiAgentStep, setMultiAgentStep] = useState<'planner' | 'worker' | 'critic' | 'done'>('done')
  const [ragActive, setRagActive] = useState(true)
  const [modelProvider, setModelProvider] = useState<'wenxin' | 'qwen' | 'default'>('default')
  const studentId = useAppStore((s) => s.studentId)

  const handleSend = async (content: string | VisionContentItem[]) => {
    setMessages((prev) => [...prev, { role: 'user' as const, content }])
    setLoading(true)
    setMultiAgentStep('planner')
    setTimeout(() => setMultiAgentStep('worker'), 600)
    setTimeout(() => setMultiAgentStep('critic'), 1200)
    try {
      const res = await tutorApi.ask({
        student_id: studentId,
        question: content,
        session_id: `${studentId}_tutor`,
      })
      setMultiAgentStep('done')
      setMessages((prev) => [
        ...prev,
        { role: 'ai' as const, content: res.data.response || '让我再思考一下...' },
      ])
    } catch (e: unknown) {
      const errMsg = e instanceof Error ? e.message : '请求失败'
      message.error(errMsg)
      setMultiAgentStep('done')
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
        <div className="flex items-center gap-3 mb-4 flex-wrap">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center text-white shadow-glow">
            <BookOutlined />
          </div>
          <div>
            <Typography.Title level={5} className="!m-0 text-slate-800">智能辅导</Typography.Title>
            <Typography.Text className="text-slate-400 text-xs">苏格拉底式教学法 · 全学科辅导</Typography.Text>
          </div>
          <Space className="ml-auto" wrap>
            {multiAgentStep !== 'done' && (
              <Tag className="rounded-full border-0 bg-blue-50 text-blue-600 text-xs">
                <NodeIndexOutlined className="mr-1" />
                {multiAgentStep === 'planner' ? 'Planner 拆解中' : multiAgentStep === 'worker' ? 'Worker 生成中' : 'Critic 审核中'}
              </Tag>
            )}
            <Tooltip title={ragActive ? 'RAG 检索增强已启用' : 'RAG 已关闭'}>
              <Tag className={`rounded-full border-0 text-xs cursor-pointer ${ragActive ? 'bg-indigo-50 text-indigo-600' : 'bg-slate-100 text-slate-400'}`} onClick={() => setRagActive(!ragActive)}>
                <ApartmentOutlined /> RAG
              </Tag>
            </Tooltip>
            <Tooltip title="切换大模型">
              <Tag className="rounded-full border-0 bg-slate-100 text-slate-600 text-xs cursor-pointer" onClick={() => setModelProvider(modelProvider === 'default' ? 'wenxin' : modelProvider === 'wenxin' ? 'qwen' : 'default')}>
                <FlagFilled className="mr-1" />
                {modelProvider === 'wenxin' ? '文心一言' : modelProvider === 'qwen' ? '通义千问' : '默认模型'}
              </Tag>
            </Tooltip>
            <Tag color="success" className="rounded-full border-0 bg-emerald-50 text-emerald-600 font-medium">
              在线
            </Tag>
          </Space>
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
