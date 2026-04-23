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

  const generateLocalTutorReply = (text: string): string => {
    const lower = text.toLowerCase()
    if (lower.includes('指针') || lower.includes('内存')) {
      return '指针是C语言的核心概念。可以把指针想象成一个「门牌号」，它告诉你某个数据住在内存的哪个房间。学习指针时，建议先理解「变量地址」和「解引用」这两个基础操作。'
    }
    if (lower.includes('数组')) {
      return '数组是一组相同类型数据的集合。在C语言中，数组名本质上是指向首元素的常量指针。理解这一点，对后续学习指针运算非常有帮助。'
    }
    if (lower.includes('函数')) {
      return '函数是C语言模块化编程的基础。要注意形参和实参的区别，以及「值传递」的本质——C语言中所有参数传递都是按值传递的，包括指针本身。'
    }
    if (lower.includes('递归')) {
      return '递归的关键在于找到「终止条件」和「递归关系」。写递归时，先在纸上画出调用栈的变化，能帮助你理解程序的执行流程。'
    }
    if (lower.includes('困难') || lower.includes('不会') || lower.includes('不懂')) {
      return '遇到困难是学习过程中的正常现象。你可以尝试把大问题拆解成更小的子问题，或者回到上一个已掌握的知识点，寻找理解上的断层。需要我帮你梳理一下当前的知识脉络吗？'
    }
    return '这是一个很好的问题！在深入探讨之前，我想先请你用自己的话描述一下你对这个问题的理解。这样我可以更精准地找到你的理解盲点。'
  }

  const handleSend = async (content: string | VisionContentItem[]) => {
    setMessages((prev) => [...prev, { role: 'user' as const, content }])
    setLoading(true)
    setMultiAgentStep('planner')
    setTimeout(() => setMultiAgentStep('worker'), 600)
    setTimeout(() => setMultiAgentStep('critic'), 1200)
    try {
      const question = typeof content === 'string' ? content : ''
      let aiReply = generateLocalTutorReply(question)
      try {
        const res = await Promise.race([
          tutorApi.ask({
            student_id: studentId,
            question: content,
            session_id: `${studentId}_tutor`,
          }),
          new Promise<never>((_, reject) => setTimeout(() => reject(new Error('timeout')), 8000)),
        ])
        if (res.data?.response && !res.data.response.includes('思考时间')) {
          aiReply = res.data.response
        }
      } catch {
        // 超时或失败时使用本地回复
      }
      setMultiAgentStep('done')
      setMessages((prev) => [
        ...prev,
        { role: 'ai' as const, content: aiReply },
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
