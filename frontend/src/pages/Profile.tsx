import React, { useState, useEffect } from 'react'
import { Typography, Card, Button, Tag, Space, Progress, Row, Col, message } from 'antd'
import {
  Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer,
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
} from 'recharts'
import {
  PlayCircleOutlined,
  AimOutlined,
  ReloadOutlined,
  BulbOutlined,
  ArrowRightOutlined,
  LineChartOutlined,
  NodeIndexOutlined,
  RobotOutlined,
  ToolOutlined,
  SafetyOutlined,
  AudioOutlined,
  VideoCameraOutlined,
  ReadOutlined,
} from '@ant-design/icons'
import { useAppStore } from '../store'
import { profileApi, tutorApi } from '../services/api'
import { buildRadarData } from '../utils/profile'
import { ChatPanel } from '../components/ChatPanel'
import { PageCard } from '../components/PageCard'
import type { ChatMessage, StudentProfile, VisionContentItem } from '../types'

const historyData = [
  { date: '周一', value: 68 },
  { date: '周二', value: 70 },
  { date: '周三', value: 72 },
  { date: '周四', value: 75 },
  { date: '周五', value: 78 },
  { date: '周六', value: 80 },
  { date: '周日', value: 82 },
]

const quickActions = [
  { icon: <PlayCircleOutlined />, title: '开始评估', desc: '对话式画像评估', color: '#4f46e5' },
  { icon: <AimOutlined />, title: '设定目标', desc: '更新学习目标', color: '#0ea5e9' },
  { icon: <ReloadOutlined />, title: '重新画像', desc: '重置并重新构建', color: '#10b981' },
]

const Profile: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    { role: 'ai', content: '你好！我是你的AI学习画像师。在学习编程之前，我想了解一下：你是否有编程基础？对C语言的指针和内存管理是否了解？这会影响我为你推荐的学习路径。', agent: '评估智能体' },
  ])
  const [profileData, setProfileData] = useState(buildRadarData(null))
  const [dimensions, setDimensions] = useState([
    { label: '知识基础', value: 85, color: '#4f46e5' },
    { label: '数学基础', value: 65, color: '#0ea5e9' },
    { label: '编程能力', value: 80, color: '#10b981' },
    { label: '薄弱点识别', value: 60, color: '#f59e0b' },
    { label: '学习进度', value: 75, color: '#8b5cf6' },
    { label: '专注度', value: 80, color: '#ec4899' },
  ])
  const [interactionPref, setInteractionPref] = useState<'video' | 'text' | 'audio'>('text')
  const [multiAgentStatus, setMultiAgentStatus] = useState({ planner: true, worker: true, critic: false })
  const [loading, setLoading] = useState(false)
  const studentId = useAppStore((s) => s.studentId)

  useEffect(() => {
    const load = async () => {
      try {
        const res = await profileApi.get(studentId)
        if (res.data.data) updateVisuals(res.data.data)
      } catch (e) {
        message.error('获取画像失败，显示默认数据')
      }
    }
    load()
  }, [studentId])

  const updateVisuals = (p: StudentProfile) => {
    const radar = buildRadarData(p)
    setProfileData(radar)
    setDimensions(radar.map((item) => ({
      label: item.subject,
      value: Math.round(item.A),
      color:
        item.subject === '知识基础' ? '#4f46e5' :
        item.subject === '认知风格' ? '#0ea5e9' :
        item.subject === '学习偏好' ? '#10b981' :
        item.subject === '薄弱点' ? '#f59e0b' :
        item.subject === '学习进度' ? '#8b5cf6' : '#ec4899',
    })))
  }

  const handleSend = async (content: string | VisionContentItem[]) => {
    const text = typeof content === 'string' ? content : ''
    if (!text.trim()) return
    setMessages((prev) => [...prev, { role: 'user' as const, content: text }])
    setLoading(true)
    try {
      // 1. 获取 AI 回复（先让画像师对话）
      let aiReply = '服务暂时无响应，请稍后再试。'
      try {
        const tutorRes = await tutorApi.ask({ student_id: studentId, question: text, session_id: `${studentId}_profile` })
        aiReply = tutorRes.data?.response || aiReply
      } catch (e: unknown) {
        const errMsg = e instanceof Error ? e.message : '请求失败'
        message.error(errMsg)
      }
      setMessages((prev) => [...prev, { role: 'ai' as const, content: aiReply, agent: '评估智能体' }])

      // 2. 调用 LLM 分析对话并更新画像（把最近几条对话作为上下文）
      const recentMessages = [...messages.slice(-4), { role: 'user' as const, content: text }]
      const conversationContext = recentMessages
        .map((m) => `${m.role === 'user' ? '学生' : 'AI'}：${typeof m.content === 'string' ? m.content : ''}`)
        .join('\n')

      try {
        const analyzeRes = await profileApi.analyzeConversation(studentId, conversationContext)
        if (analyzeRes.data?.data) {
          updateVisuals(analyzeRes.data.data)
          message.success('画像已根据对话自动更新')
        }
      } catch (e: unknown) {
        // 画像分析失败不影响对话体验
        console.warn('画像分析失败', e)
      }
    } catch (e: unknown) {
      const errMsg = e instanceof Error ? e.message : '请求失败'
      message.error(errMsg)
      setMessages((prev) => [...prev, { role: 'ai' as const, content: '服务暂时不可用，请稍后再试。', agent: '评估智能体' }])
    } finally {
      setLoading(false)
    }
  }

  const handleInitProfile = async () => {
    try {
      await profileApi.initialize(studentId, { inputs: ['我是一名计算机专业大二学生，对编程很感兴趣。有一定的高数基础，但数据结构和算法比较薄弱。喜欢通过代码实践来学习，想系统学习C语言。'] })
      const res = await profileApi.get(studentId)
      if (res.data.data) updateVisuals(res.data.data)
      message.success('画像初始化成功')
    } catch (e: unknown) {
      const errMsg = e instanceof Error ? e.message : '初始化失败'
      message.error(errMsg)
    }
  }

  return (
    <div className="space-y-6">
      {/* 快捷操作 */}
      <div className="flex flex-wrap gap-3">
        {quickActions.map((action, idx) => (
          <button
            key={idx}
            onClick={idx === 2 ? handleInitProfile : undefined}
            className="flex items-center gap-3 px-5 py-3 rounded-xl bg-white border border-slate-100 hover:border-slate-200 hover:shadow-card transition-all text-left"
          >
            <div
              className="w-10 h-10 rounded-lg flex items-center justify-center text-lg shrink-0"
              style={{ background: action.color + '12', color: action.color }}
            >
              {action.icon}
            </div>
            <div>
              <div className="font-semibold text-slate-800 text-sm">{action.title}</div>
              <div className="text-xs text-slate-500">{action.desc}</div>
            </div>
          </button>
        ))}
      </div>

      <Row gutter={[20, 20]} align="stretch">
        {/* AI画像师聊天 */}
        <Col xs={24} lg={9}>
          <PageCard className="h-full min-h-[600px]" bodyStyle={{ height: '100%', padding: '24px' }}>
            <ChatPanel
              messages={messages}
              loading={loading}
              onSend={handleSend}
              title="AI 画像师"
              subtitle="正在实时分析你的学习特征"
              placeholder="回复 AI 画像师..."
              inputPrefix={<BulbOutlined className="text-slate-400" />}
            />
          </PageCard>
        </Col>

        {/* 画像雷达 + 维度 + 偏好 + 智能体 —— 2x2 紧凑布局 */}
        <Col xs={24} lg={15}>
          <Row gutter={[20, 20]}>
            <Col xs={24} md={12}>
              <PageCard
                title={<Space>
                  <span className="font-semibold text-slate-800">六维画像雷达</span>
                </Space>}
              >
                <div className="h-52">
                  <ResponsiveContainer width="100%" height="100%">
                    <RadarChart cx="50%" cy="50%" outerRadius="70%" data={profileData}>
                      <PolarGrid stroke="#e2e8f0" />
                      <PolarAngleAxis dataKey="subject" tick={{ fill: '#64748b', fontSize: 11 }} />
                      <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                      <Radar name="当前画像" dataKey="A" stroke="#4f46e5" fill="#4f46e5" fillOpacity={0.15} strokeWidth={2} />
                    </RadarChart>
                  </ResponsiveContainer>
                </div>
              </PageCard>
            </Col>

            <Col xs={24} md={12}>
              <PageCard title={<span className="font-semibold text-slate-800">维度详情</span>}>
                <div className="space-y-3">
                  {dimensions.map((dim) => (
                    <div key={dim.label}>
                      <div className="flex justify-between mb-1">
                        <Typography.Text className="text-sm text-slate-600 font-medium">{dim.label}</Typography.Text>
                        <Typography.Text className="text-sm font-bold" style={{ color: dim.color }}>{dim.value}</Typography.Text>
                      </div>
                      <Progress percent={dim.value} showInfo={false} strokeColor={dim.color} trailColor="#f1f5f9" size="small" />
                    </div>
                  ))}
                </div>
              </PageCard>
            </Col>

            <Col xs={24} md={12}>
              <PageCard title={<span className="font-semibold text-slate-800">交互偏好</span>}>
                <div className="flex gap-2">
                  {[
                    { key: 'video', icon: <VideoCameraOutlined />, label: '视频' },
                    { key: 'text', icon: <ReadOutlined />, label: '图文' },
                    { key: 'audio', icon: <AudioOutlined />, label: '语音' },
                  ].map((item: any) => (
                    <button
                      key={item.key}
                      onClick={() => setInteractionPref(item.key)}
                      className={`flex-1 flex flex-col items-center gap-2 p-3 rounded-xl border transition-all ${interactionPref === item.key ? 'bg-primary-50 border-primary text-primary' : 'bg-white border-slate-100 text-slate-500 hover:border-slate-200'}`}
                    >
                      <div className="text-lg">{item.icon}</div>
                      <span className="text-xs font-medium">{item.label}</span>
                    </button>
                  ))}
                </div>
                <div className="mt-2 text-xs text-slate-400">
                  优先推送{interactionPref === 'video' ? '视频讲解类' : interactionPref === 'audio' ? '音频播客类' : '图文文档类'}资源。
                </div>
              </PageCard>
            </Col>

            <Col xs={24} md={12}>
              <PageCard title={<span className="font-semibold text-slate-800">多智能体协作</span>}>
                <div className="space-y-2">
                  {[
                    { key: 'planner', icon: <NodeIndexOutlined />, label: 'Planner', desc: '拆解学习目标', active: multiAgentStatus.planner },
                    { key: 'worker', icon: <ToolOutlined />, label: 'Worker', desc: '生成导图与习题', active: multiAgentStatus.worker },
                    { key: 'critic', icon: <SafetyOutlined />, label: 'Critic', desc: '防幻觉过滤', active: multiAgentStatus.critic },
                  ].map((agent: any) => (
                    <div key={agent.key} className={`flex items-center gap-2.5 p-2.5 rounded-lg border transition-all ${agent.active ? 'bg-white border-slate-200' : 'bg-slate-50 border-slate-100 opacity-60'}`}>
                      <div className={`w-8 h-8 rounded-lg flex items-center justify-center text-white shrink-0 ${agent.active ? 'bg-primary' : 'bg-slate-300'}`}>
                        {agent.icon}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="text-sm font-medium text-slate-800 truncate">{agent.label}</div>
                        <div className="text-xs text-slate-400 truncate">{agent.desc}</div>
                      </div>
                      <Tag className={`rounded-full border-0 text-xs ${agent.active ? 'bg-emerald-50 text-emerald-600' : 'bg-slate-100 text-slate-400'}`}>
                        {agent.active ? '运行中' : '待机'}
                      </Tag>
                    </div>
                  ))}
                </div>
              </PageCard>
            </Col>
          </Row>
        </Col>
      </Row>

      <PageCard
        title={<span className="font-semibold text-slate-800">画像历史变化</span>}
        extra={<Tag className="rounded-full border-0 bg-slate-100 text-slate-600 text-xs">近7天</Tag>}
      >
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={historyData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="date" tick={{ fill: '#64748b' }} axisLine={false} tickLine={false} />
              <YAxis domain={[60, 100]} tick={{ fill: '#64748b' }} axisLine={false} tickLine={false} />
              <Tooltip
                contentStyle={{ borderRadius: 12, border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.06)' }}
                cursor={{ stroke: '#e2e8f0', strokeWidth: 2 }}
              />
              <Line type="monotone" dataKey="value" stroke="#4f46e5" strokeWidth={3} dot={{ fill: '#4f46e5', strokeWidth: 2, r: 4 }} activeDot={{ r: 6, fill: '#fff', stroke: '#4f46e5', strokeWidth: 2 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </PageCard>

      {/* 遗忘曲线维度 */}
      <PageCard
        title={<span className="font-semibold text-slate-800">遗忘曲线 · 知识点衰减</span>}
        extra={<Tag className="rounded-full border-0 bg-slate-100 text-slate-600 text-xs">艾宾浩斯</Tag>}
      >
        <Row gutter={[24, 24]}>
          <Col xs={24} lg={12}>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={[
                  { day: '第1天', memory: 100 },
                  { day: '第2天', memory: 55 },
                  { day: '第3天', memory: 42 },
                  { day: '第5天', memory: 35 },
                  { day: '第8天', memory: 30 },
                  { day: '第15天', memory: 25 },
                  { day: '第30天', memory: 20 },
                ]}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                  <XAxis dataKey="day" tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
                  <YAxis domain={[0, 100]} tick={{ fill: '#64748b' }} axisLine={false} tickLine={false} />
                  <Tooltip contentStyle={{ borderRadius: 12, border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.06)' }} />
                  <Line type="monotone" dataKey="memory" name="理论记忆保留率" stroke="#ef4444" strokeWidth={2} dot={{ r: 3 }} strokeDasharray="5 5" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </Col>
          <Col xs={24} lg={12}>
            <div className="space-y-3">
              {[
                { topic: '数据类型与变量', retention: 85, nextReview: '明天' },
                { topic: '控制结构', retention: 62, nextReview: '今天' },
                { topic: '指针与内存', retention: 45, nextReview: '今天' },
                { topic: '函数与递归', retention: 78, nextReview: '后天' },
              ].map((item) => (
                <div key={item.topic} className="flex items-center gap-3 p-3 rounded-xl bg-slate-50 border border-slate-100">
                  <div className="flex-1">
                    <div className="text-sm font-medium text-slate-800">{item.topic}</div>
                    <div className="text-xs text-slate-400">下次复习: {item.nextReview}</div>
                  </div>
                  <div className="w-24">
                    <Progress percent={item.retention} size="small" strokeColor={item.retention > 70 ? '#10b981' : item.retention > 50 ? '#f59e0b' : '#ef4444'} trailColor="#f1f5f9" showInfo={false} />
                  </div>
                  <Tag className={`rounded-full border-0 text-xs ${item.retention > 70 ? 'bg-emerald-50 text-emerald-600' : item.retention > 50 ? 'bg-amber-50 text-amber-600' : 'bg-red-50 text-red-600'}`}>
                    {item.retention}%
                  </Tag>
                </div>
              ))}
            </div>
          </Col>
        </Row>
      </PageCard>
    </div>
  )
}

export default Profile
