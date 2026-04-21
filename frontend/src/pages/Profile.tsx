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
} from '@ant-design/icons'
import { useAppStore } from '../store'
import { profileApi, trendApi } from '../services/api'
import { buildRadarData } from '../utils/profile'
import { ChatPanel } from '../components/ChatPanel'
import { PageCard } from '../components/PageCard'
import type { ChatMessage, StudentProfile } from '../types'

const quickActions = [
  { icon: <PlayCircleOutlined />, title: '开始评估', desc: '对话式画像评估', color: '#4f46e5' },
  { icon: <AimOutlined />, title: '设定目标', desc: '更新学习目标', color: '#0ea5e9' },
  { icon: <ReloadOutlined />, title: '重新画像', desc: '重置并重新构建', color: '#10b981' },
]

const Profile: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    { role: 'ai', content: '你好！我是你的AI学习画像师。为了更好地为你推荐学习路径，我想先了解一下你的学习背景。比如你的数学基础和编程能力如何？' },
  ])
  const [profileData, setProfileData] = useState(buildRadarData(null))
  const [dimensions, setDimensions] = useState([
    { label: '知识基础', value: 0, color: '#4f46e5' },
    { label: '数学基础', value: 0, color: '#0ea5e9' },
    { label: '编程能力', value: 0, color: '#10b981' },
    { label: '薄弱点识别', value: 0, color: '#f59e0b' },
    { label: '学习进度', value: 0, color: '#8b5cf6' },
    { label: '专注度', value: 0, color: '#ec4899' },
  ])
  const [historyData, setHistoryData] = useState<{ date: string; value: number }[]>([])
  const [loading, setLoading] = useState(false)
  const studentId = useAppStore((s) => s.studentId)

  useEffect(() => {
    const load = async () => {
      try {
        const [profileRes, trendRes] = await Promise.all([
          profileApi.get(studentId).catch((e) => { console.error('画像加载失败:', e); return null }),
          trendApi.getHistory(studentId, 7).catch((e) => { console.error('趋势加载失败:', e); return null }),
        ])
        if (profileRes?.data?.data) updateVisuals(profileRes.data.data)
        if (trendRes?.data?.data?.length) {
          const mapped = trendRes.data.data
            .slice(-7)
            .map((t: any) => ({
              date: t.date?.slice(5) || '',
              value: Math.round(((t.trend_factor || 0.5) * 100)),
            }))
          if (mapped.length >= 3) setHistoryData(mapped)
        }
      } catch (e) {
        console.error('画像数据加载失败:', e)
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
        item.subject === '数学基础' ? '#0ea5e9' :
        item.subject === '编程能力' ? '#10b981' :
        item.subject === '薄弱点' ? '#f59e0b' :
        item.subject === '学习进度' ? '#8b5cf6' : '#ec4899',
    })))
  }

  const handleSend = async (content: string | import('../types').VisionContentItem[]) => {
    setMessages((prev) => [...prev, { role: 'user' as const, content }])
    setLoading(true)
    try {
      const safeText = typeof content === 'string' ? content : '(图片消息)'
      await profileApi.update(studentId, { dimension: 'interest', updates: { goals: [safeText] } })
      const res = await profileApi.get(studentId)
      if (res.data.data) updateVisuals(res.data.data)
      setMessages((prev) => [...prev, { role: 'ai' as const, content: '收到！我会根据你的反馈更新画像数据。' }])
    } catch (e: unknown) {
      const errMsg = e instanceof Error ? e.message : '更新失败'
      message.error(errMsg)
      setMessages((prev) => [...prev, { role: 'ai' as const, content: '更新画像时出了点小问题，但我已记录你的反馈。' }])
    } finally {
      setLoading(false)
    }
  }

  const handleInitProfile = async () => {
    try {
      await profileApi.initialize(studentId, { inputs: ['我是一名计算机专业大二学生，对人工智能很感兴趣。线性代数有一定基础，但概率论和微积分比较薄弱。喜欢通过代码实践来学习，Python比较熟练。'] })
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
            onClick={idx === 0 ? () => message.info('请在下方聊天框中回复画像师的问题，完成评估') : idx === 1 ? () => message.info('请在下方聊天框中输入你的学习目标') : handleInitProfile}
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

      <Row gutter={[20, 20]}>
        {/* AI画像师聊天 */}
        <Col xs={24} lg={14}>
          <PageCard className="h-[600px]" bodyStyle={{ height: '100%', padding: '24px' }}>
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

        {/* 画像雷达 + 维度 */}
        <Col xs={24} lg={10}>
          <PageCard
            title={<Space>
              <span className="font-semibold text-slate-800">六维画像雷达</span>
            </Space>}
            className="mb-5"
          >
            <div className="h-56">
              <ResponsiveContainer width="100%" height="100%" minWidth={200} minHeight={200}>
                <RadarChart cx="50%" cy="50%" outerRadius="70%" data={profileData}>
                  <PolarGrid stroke="#e2e8f0" />
                  <PolarAngleAxis dataKey="subject" tick={{ fill: '#64748b', fontSize: 11 }} />
                  <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                  <Radar name="当前画像" dataKey="A" stroke="#4f46e5" fill="#4f46e5" fillOpacity={0.15} strokeWidth={2} />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          </PageCard>

          <PageCard title={<span className="font-semibold text-slate-800">维度详情</span>}>
            <div className="space-y-4">
              {dimensions.map((dim) => (
                <div key={dim.label}>
                  <div className="flex justify-between mb-1.5">
                    <Typography.Text className="text-sm text-slate-600 font-medium">{dim.label}</Typography.Text>
                    <Typography.Text className="text-sm font-bold" style={{ color: dim.color }}>{dim.value}</Typography.Text>
                  </div>
                  <Progress percent={dim.value} showInfo={false} strokeColor={dim.color} trailColor="#f1f5f9" size="small" />
                </div>
              ))}
            </div>
          </PageCard>
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
    </div>
  )
}

export default Profile
