import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Typography, Card, Row, Col, Button, Tag, Avatar, List, Space, Progress, message, Spin, Badge
} from 'antd'
import {
  Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer,
} from 'recharts'
import {
  PlayCircleOutlined,
  FileTextOutlined,
  CodeOutlined,
  MessageOutlined,
  RocketOutlined,
  BookOutlined,
  ClockCircleOutlined,
  FireOutlined,
  TrophyOutlined,
  ArrowRightOutlined,
  ApartmentOutlined,
} from '@ant-design/icons'
import { useAppStore } from '../store'
import { profileApi, dashboardApi } from '../services/api'
import { buildRadarData } from '../utils/profile'
import { StatCard } from '../components/StatCard'

const taskTypeMeta: Record<string, { icon: React.ReactNode; color: string; bg: string }> = {
  video: { icon: <PlayCircleOutlined />, color: '#ef4444', bg: '#fef2f2' },
  quiz: { icon: <BookOutlined />, color: '#f59e0b', bg: '#fffbeb' },
  doc: { icon: <FileTextOutlined />, color: '#10b981', bg: '#ecfdf5' },
  code: { icon: <CodeOutlined />, color: '#3b82f6', bg: '#eff6ff' },
}

const Dashboard: React.FC = () => {
  const navigate = useNavigate()
  const [profileData, setProfileData] = useState(buildRadarData(null))
  const [isLoading, setIsLoading] = useState(false)
  const [summaryLoading, setSummaryLoading] = useState(false)
  const [tasks, setTasks] = useState<any[]>([])
  const [recommendations, setRecommendations] = useState<any[]>([])
  const [stats, setStats] = useState({
    weekly_hours: 0,
    streak_days: 0,
    achievements: 0,
    favorites: 0,
    mastered_kps: 0,
    today_duration_min: 0,
  })
  const [welcomeTopic, setWelcomeTopic] = useState('新知识')
  const studentId = useAppStore((s) => s.studentId)

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true)
      setSummaryLoading(true)
      try {
        // 并行请求画像和 Dashboard 聚合数据
        const [profileRes, summaryRes] = await Promise.all([
          profileApi.get(studentId),
          dashboardApi.getSummary(studentId).catch((e) => { console.error('Dashboard 加载失败:', e); return null }),
        ])

        if (profileRes.data?.data) {
          setProfileData(buildRadarData(profileRes.data.data))
          const interests = profileRes.data.data.interest_areas || []
          if (interests.length > 0) setWelcomeTopic(String(interests[0]))
        }

        if (summaryRes?.data) {
          const d = summaryRes.data
          setStats(d.stats || stats)
          setTasks(d.tasks || [])
          setRecommendations(d.recommendations || [])
        }
      } catch (e) {
        console.error('Dashboard 数据加载失败:', e)
        message.error('获取数据失败，显示默认数据')
      } finally {
        setIsLoading(false)
        setSummaryLoading(false)
      }
    }
    fetchData()
  }, [studentId])

  const statCards = [
    { title: '本周学习', value: stats.weekly_hours, suffix: 'h', icon: <ClockCircleOutlined />, color: '#4f46e5', path: '/personal' },
    { title: '连续打卡', value: stats.streak_days, suffix: '天', icon: <FireOutlined />, color: '#f59e0b', path: '/personal' },
    { title: '掌握知识点', value: stats.mastered_kps, suffix: '个', icon: <TrophyOutlined />, color: '#10b981', path: '/profile' },
    { title: '待完成任务', value: tasks.length, suffix: '项', icon: <RocketOutlined />, color: '#0ea5e9', path: '/learning-path' },
  ]

  const typeIconMap: Record<string, { icon: React.ReactNode; color: string }> = {
    doc: { icon: <FileTextOutlined />, color: '#10b981' },
    video: { icon: <PlayCircleOutlined />, color: '#ef4444' },
    code: { icon: <CodeOutlined />, color: '#3b82f6' },
    tool: { icon: <ApartmentOutlined />, color: '#3b82f6' },
    tutor: { icon: <MessageOutlined />, color: '#8b5cf6' },
    推荐: { icon: <RocketOutlined />, color: '#f59e0b' },
    文章: { icon: <FileTextOutlined />, color: '#10b981' },
    视频: { icon: <PlayCircleOutlined />, color: '#ef4444' },
    代码: { icon: <CodeOutlined />, color: '#3b82f6' },
    工具: { icon: <ApartmentOutlined />, color: '#3b82f6' },
  }

  return (
    <div className="space-y-8">
      {/* 欢迎区 */}
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
        <div>
          <Typography.Title level={3} className="!m-0 text-slate-900 font-bold tracking-tight">
            欢迎回来，学习者
          </Typography.Title>
          <Typography.Text className="text-slate-500 block mt-1">
            今天继续学习 <span className="text-primary font-medium">{welcomeTopic}</span> 吗？
          </Typography.Text>
        </div>
        <Button type="primary" size="large" className="rounded-xl bg-primary" onClick={() => navigate('/resources')}>
          继续学习 <ArrowRightOutlined />
        </Button>
      </div>

      {/* 统计 */}
      <Row gutter={[20, 20]}>
        {statCards.map((stat, idx) => (
          <Col xs={12} lg={6} key={idx}>
            <StatCard
              icon={stat.icon}
              color={stat.color}
              title={stat.title}
              value={stat.value}
              suffix={stat.suffix}
              onClick={() => navigate(stat.path)}
            />
          </Col>
        ))}
      </Row>

      {/* 主体 */}
      <Row gutter={[24, 24]}>
        <Col xs={24} lg={16}>
          <Card
            title={<span className="font-semibold text-slate-800">今日学习任务</span>}
            extra={
              <Tag className="rounded-full border-0 bg-sky-50 text-sky-600 font-medium text-xs">
                {tasks.length} 项待完成
              </Tag>
            }
            className="border border-slate-100 rounded-2xl"
            styles={{ body: { padding: '20px 24px' } }}
          >
            <Spin spinning={summaryLoading}>
              <List
                itemLayout="horizontal"
                dataSource={tasks.length > 0 ? tasks : []}
                locale={{ emptyText: '暂无任务，去学习中心看看吧' }}
                renderItem={(item: any) => {
                  const meta = taskTypeMeta[item.type || 'doc'] || taskTypeMeta.doc
                  return (
                    <List.Item
                      actions={[
                        <Button
                          type="primary"
                          size="small"
                          className="rounded-lg bg-primary"
                          onClick={() => navigate('/learning-path')}
                        >
                          开始学习
                        </Button>,
                      ]}
                      className="hover:bg-slate-50 rounded-xl transition-colors px-2"
                    >
                      <List.Item.Meta
                        avatar={
                          <Avatar
                            icon={meta.icon}
                            style={{ background: meta.bg, color: meta.color }}
                            className="flex items-center justify-center"
                          />
                        }
                        title={
                          <Typography.Text className="font-medium text-slate-800">{item.title}</Typography.Text>
                        }
                        description={
                          <Space size={12}>
                            {item.duration && (
                              <span className="text-slate-400 text-xs flex items-center gap-1">
                                <ClockCircleOutlined /> {item.duration}
                              </span>
                            )}
                            {item.progress > 0 && (
                              <Progress percent={Math.round(item.progress * 100)} size="small" className="w-20" strokeColor={meta.color} trailColor="#f1f5f9" />
                            )}
                          </Space>
                        }
                      />
                    </List.Item>
                  )
                }}
              />
            </Spin>
          </Card>

          <Card
            title={<span className="font-semibold text-slate-800">推荐资源</span>}
            extra={
              <Button type="link" className="text-primary font-medium" onClick={() => navigate('/resources')}>
                查看全部 <ArrowRightOutlined />
              </Button>
            }
            className="border border-slate-100 rounded-2xl mt-6"
            styles={{ body: { padding: '24px' } }}
          >
            <Spin spinning={summaryLoading}>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {(recommendations.length > 0 ? recommendations : []).map((res: any, idx: number) => {
                  const iconMeta = typeIconMap[res.type || '推荐'] || typeIconMap['推荐']
                  return (
                    <div
                      key={idx}
                      className="flex items-center gap-4 p-4 rounded-xl bg-slate-50 hover:bg-white hover:shadow-card transition-all duration-300 cursor-pointer border border-transparent hover:border-slate-100"
                      onClick={() => navigate(res.type === 'tutor' || res.type === '辅导' ? '/tutor' : '/resources')}
                    >
                      <div
                        className="w-10 h-10 rounded-lg flex items-center justify-center text-white text-lg shrink-0"
                        style={{ background: iconMeta.color }}
                      >
                        {iconMeta.icon}
                      </div>
                      <div className="min-w-0">
                        <Typography.Text className="font-medium text-slate-800 block truncate">
                          {res.title}
                        </Typography.Text>
                        <span className="text-xs text-slate-400 mt-0.5 block">{res.type || '资源'}</span>
                      </div>
                    </div>
                  )
                })}
                {recommendations.length === 0 && (
                  <div className="text-slate-400 text-sm col-span-2 text-center py-4">暂无推荐资源</div>
                )}
              </div>
            </Spin>
          </Card>
        </Col>

        <Col xs={24} lg={8}>
          <Card
            title={
              <Space>
                <span className="font-semibold text-slate-800">画像摘要</span>
                <Badge count="AI" style={{ backgroundColor: '#4f46e5', fontSize: 10 }} />
              </Space>
            }
            extra={
              <Button type="link" className="text-primary font-medium" onClick={() => navigate('/profile')}>
                详情 <ArrowRightOutlined />
              </Button>
            }
            className="border border-slate-100 rounded-2xl h-full"
            styles={{ body: { padding: '24px' } }}
          >
            <Spin spinning={isLoading}>
              <div className="h-56">
                <ResponsiveContainer width="100%" height="100%" minWidth={200} minHeight={200}>
                  <RadarChart cx="50%" cy="50%" outerRadius="70%" data={profileData}>
                    <PolarGrid stroke="#e2e8f0" />
                    <PolarAngleAxis dataKey="subject" tick={{ fill: '#64748b', fontSize: 12 }} />
                    <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                    <Radar name="当前画像" dataKey="A" stroke="#4f46e5" fill="#4f46e5" fillOpacity={0.15} strokeWidth={2} />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
              <div className="flex flex-wrap gap-2 justify-center mt-3">
                {profileData.map((item) => (
                  <Tag key={item.subject} className="rounded-full border-0 bg-slate-100 text-slate-600 text-xs">
                    {item.subject}: {Math.round(item.A)}
                  </Tag>
                ))}
              </div>
            </Spin>
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default Dashboard
