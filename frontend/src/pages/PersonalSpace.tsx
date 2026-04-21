import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Typography, Tabs, List, Avatar, Tag, Space, Button, Progress, Row, Col, Spin, message } from 'antd'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar,
} from 'recharts'
import {
  FileTextOutlined,
  VideoCameraOutlined,
  CodeOutlined,
  StarOutlined,
  HeartOutlined,
  HistoryOutlined,
  EditOutlined,
  TrophyOutlined,
  FireOutlined,
  ClockCircleOutlined,
  BarChartOutlined,
  LineChartOutlined,
} from '@ant-design/icons'
import { useAppStore } from '../store'
import { profileApi, dashboardApi, favoritesApi, learningDataApi } from '../services/api'
import { StatCard } from '../components/StatCard'

const typeMeta: Record<string, { icon: React.ReactNode; color: string; bg: string; label: string }> = {
  video: { icon: <VideoCameraOutlined />, color: '#ef4444', bg: '#fef2f2', label: '视频' },
  quiz: { icon: <TrophyOutlined />, color: '#f59e0b', bg: '#fffbeb', label: '练习' },
  code: { icon: <CodeOutlined />, color: '#3b82f6', bg: '#eff6ff', label: '代码' },
  profile: { icon: <EditOutlined />, color: '#8b5cf6', bg: '#f5f3ff', label: '画像' },
  doc: { icon: <FileTextOutlined />, color: '#10b981', bg: '#ecfdf5', label: '文档' },
}

const PersonalSpace: React.FC = () => {
  const [profile, setProfile] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [focusData, setFocusData] = useState<any[]>([])
  const [historyList, setHistoryList] = useState<any[]>([])
  const [favorites, setFavorites] = useState<any[]>([])
  const [stats, setStats] = useState({
    total_hours: 0,
    streak: 0,
    achievements: 0,
    favorites_count: 0,
  })
  const studentId = useAppStore((s) => s.studentId)
  const navigate = useNavigate()

  useEffect(() => {
    const load = async () => {
      setLoading(true)
      try {
        const [profileRes, summaryRes, favoritesRes, historyRes] = await Promise.all([
          profileApi.get(studentId).catch(() => null),
          dashboardApi.getSummary(studentId).catch(() => null),
          favoritesApi.get(studentId).catch(() => null),
          learningDataApi.getHistory(studentId, 20).catch(() => null),
        ])

        if (profileRes?.data?.data) setProfile(profileRes.data.data)

        if (summaryRes?.data) {
          const d = summaryRes.data
          setStats({
            total_hours: Math.round((d.stats?.weekly_hours || 0) * 4),
            streak: d.stats?.streak_days || 0,
            achievements: d.stats?.achievements || 0,
            favorites_count: d.stats?.favorites || 0,
          })
          if (d.trend?.length) {
            // 把趋势数据映射到 focusData 格式（后端 value 已为 0-100 分数或分钟数）
            const mapped = d.trend.slice(-7).map((t: any) => ({
              day: t.date || '--',
              focus: Math.min(100, Math.round(t.value || 0)),
              duration: Math.round(t.value || 0),
            }))
            if (mapped.length >= 1) setFocusData(mapped)
          }
        }

        if (favoritesRes?.data?.data) {
          const favs = favoritesRes.data.data.map((f: any) => ({
            title: f.title,
            type: f.resource_type || 'doc',
            icon: typeMeta[f.resource_type]?.icon || <FileTextOutlined />,
            color: f.meta?.color || '#4f46e5',
          }))
          if (favs.length > 0) setFavorites(favs)
        }

        if (historyRes?.data) {
          const records = historyRes.data.records || []
          const mappedHistory = records.slice(0, 8).map((r: any) => {
            const actionLabelMap: Record<string, string> = {
              watch: '视频', read: '文档', practice: '练习', review: '复习',
            }
            return {
              title: `完成 ${r.kp_id || '学习记录'} ${actionLabelMap[r.action] || r.action}`,
              time: r.created_at ? new Date(r.created_at).toLocaleString('zh-CN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }) : '',
              type: r.action === 'watch' ? 'video' : r.action === 'practice' ? 'quiz' : 'doc',
            }
          })
          if (mappedHistory.length > 0) setHistoryList(mappedHistory)
        }
      } catch (e) {
        console.error('个人空间数据加载失败:', e)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [studentId])

  const weakAreas = profile?.weak_areas || []
  const cognitivePrimary = profile?.cognitive_style?.primary || 'visual'
  const studySpeed = profile?.learning_tempo?.study_speed || 'moderate'

  const statCards = [
    { title: '累计学习时长', value: stats.total_hours, suffix: 'h', color: '#4f46e5', icon: <ClockCircleOutlined /> },
    { title: '最长连续打卡', value: stats.streak, suffix: '天', color: '#f59e0b', icon: <FireOutlined /> },
    { title: '获得勋章', value: stats.achievements, suffix: '枚', color: '#10b981', icon: <TrophyOutlined /> },
    { title: '收藏资源', value: stats.favorites_count, suffix: '个', color: '#ec4899', icon: <HeartOutlined /> },
  ]

  return (
    <Spin spinning={loading}>
      <div className="space-y-6">
        {/* 统计卡片 */}
        <Row gutter={[20, 20]}>
          {statCards.map((stat, idx) => (
            <Col xs={12} lg={6} key={idx}>
              <StatCard
                icon={stat.icon}
                color={stat.color}
                title={stat.title}
                value={stat.value}
                suffix={stat.suffix}
              />
            </Col>
          ))}
        </Row>

        <Tabs
          defaultActiveKey="history"
          className="custom-tabs"
          items={[
            {
              key: 'history',
              label: (
                <span className="flex items-center gap-1.5">
                  <HistoryOutlined /> 学习历史与分析
                </span>
              ),
              children: (
                <div className="space-y-5">
                  <Row gutter={[20, 20]}>
                    <Col xs={24} lg={12}>
                      <div className="bg-white rounded-2xl border border-slate-100 p-6">
                        <div className="flex items-center gap-2 mb-4">
                          <LineChartOutlined className="text-primary" />
                          <span className="font-semibold text-slate-800">专注度趋势</span>
                        </div>
                        <div className="h-60">
                          <ResponsiveContainer width="100%" height="100%" minWidth={200} minHeight={200}>
                            <LineChart data={focusData}>
                              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                              <XAxis dataKey="day" tick={{ fill: '#64748b' }} axisLine={false} tickLine={false} />
                              <YAxis domain={[0, 100]} tick={{ fill: '#64748b' }} axisLine={false} tickLine={false} />
                              <Tooltip contentStyle={{ borderRadius: 12, border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.06)' }} cursor={{ stroke: '#e2e8f0', strokeWidth: 2 }} />
                              <Line type="monotone" dataKey="focus" stroke="#4f46e5" strokeWidth={3} dot={{ fill: '#4f46e5', r: 4 }} activeDot={{ r: 6, fill: '#fff', stroke: '#4f46e5', strokeWidth: 2 }} />
                            </LineChart>
                          </ResponsiveContainer>
                        </div>
                      </div>
                    </Col>
                    <Col xs={24} lg={12}>
                      <div className="bg-white rounded-2xl border border-slate-100 p-6">
                        <div className="flex items-center gap-2 mb-4">
                          <BarChartOutlined className="text-secondary" />
                          <span className="font-semibold text-slate-800">每日学习时长</span>
                        </div>
                        <div className="h-60">
                          <ResponsiveContainer width="100%" height="100%" minWidth={200} minHeight={200}>
                            <BarChart data={focusData}>
                              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                              <XAxis dataKey="day" tick={{ fill: '#64748b' }} axisLine={false} tickLine={false} />
                              <YAxis tick={{ fill: '#64748b' }} axisLine={false} tickLine={false} />
                              <Tooltip contentStyle={{ borderRadius: 12, border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.06)' }} cursor={{ fill: '#f8fafc' }} />
                              <Bar dataKey="duration" fill="url(#colorDuration)" radius={[8, 8, 0, 0]} />
                              <defs>
                                <linearGradient id="colorDuration" x1="0" y1="0" x2="0" y2="1">
                                  <stop offset="5%" stopColor="#4f46e5" stopOpacity={0.9} />
                                  <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0.7} />
                                </linearGradient>
                              </defs>
                            </BarChart>
                          </ResponsiveContainer>
                        </div>
                      </div>
                    </Col>
                  </Row>

                  <div className="bg-white rounded-2xl border border-slate-100 p-6">
                    <div className="font-semibold text-slate-800 mb-4">最近学习记录</div>
                    <List
                      itemLayout="horizontal"
                      dataSource={historyList.length > 0 ? historyList : []}
                      locale={{ emptyText: '暂无学习记录' }}
                      renderItem={(item) => {
                        const meta = typeMeta[item.type] || typeMeta.doc
                        return (
                          <List.Item className="hover:bg-slate-50 rounded-xl transition-colors px-2">
                            <List.Item.Meta
                              avatar={
                                <Avatar
                                  icon={meta.icon}
                                  style={{ background: meta.bg, color: meta.color, border: `1px solid ${meta.color}15` }}
                                />
                              }
                              title={<Typography.Text className="text-slate-700 font-medium text-sm">{item.title}</Typography.Text>}
                              description={
                                <Space>
                                  <Tag className="rounded-full text-xs border-0 bg-slate-100 text-slate-500">{meta.label}</Tag>
                                  <span className="text-slate-400 text-xs">{item.time}</span>
                                </Space>
                              }
                            />
                          </List.Item>
                        )
                      }}
                    />
                  </div>
                </div>
              ),
            },
            {
              key: 'favorites',
              label: (
                <span className="flex items-center gap-1.5">
                  <StarOutlined /> 资源库与收藏夹
                </span>
              ),
              children: (
                <div className="bg-white rounded-2xl border border-slate-100 p-6">
                  <div className="font-semibold text-slate-800 mb-5">我的收藏</div>
                  <Row gutter={[20, 20]}>
                    {(favorites.length > 0 ? favorites : []).map((item: any, idx: number) => (
                      <Col xs={24} sm={12} lg={8} key={idx}>
                        <div
                          className="p-5 rounded-xl bg-slate-50 hover:bg-white hover:shadow-card transition-all cursor-pointer border border-slate-100 hover:border-slate-200"
                          onClick={() => {
                            if (item.url) {
                              window.open(item.url, '_blank')
                            } else {
                              navigate('/resources')
                              message.info(`已跳转至学习中心，查找 ${item.title}`)
                            }
                          }}
                        >
                          <Space align="start">
                            <div
                              className="w-10 h-10 rounded-lg flex items-center justify-center text-white text-lg shrink-0"
                              style={{ background: item.color }}
                            >
                              {item.icon}
                            </div>
                            <div>
                              <Typography.Text className="font-medium text-slate-800 block">{item.title}</Typography.Text>
                              <span className="text-xs text-slate-400 mt-0.5 block">{item.type}</span>
                            </div>
                          </Space>
                        </div>
                      </Col>
                    ))}
                    {favorites.length === 0 && (
                      <div className="text-slate-400 text-sm text-center w-full py-8">暂无收藏资源</div>
                    )}
                  </Row>
                </div>
              ),
            },
            {
              key: 'profile',
              label: (
                <span className="flex items-center gap-1.5">
                  <EditOutlined /> 画像详情与管理
                </span>
              ),
              children: (
                <div className="bg-white rounded-2xl border border-slate-100 p-6">
                  <Typography.Title level={5} className="mb-5 font-semibold text-slate-800">画像数据解读</Typography.Title>
                  <div className="space-y-4 text-slate-600 leading-relaxed">
                    <div className="p-5 rounded-xl bg-slate-50 border border-slate-100">
                      <p className="mb-2"><strong className="text-slate-800">认知风格：</strong> 你的主要认知风格为 <Tag className="rounded-full border-0 bg-purple-50 text-purple-600">{cognitivePrimary}</Tag>，系统会优先推送图表和动画类资源（如神经网络结构图、损失函数收敛曲线）。</p>
                      <p className="mb-2"><strong className="text-slate-800">数学基础：</strong> 当前数学基础评估为 <Tag className="rounded-full border-0 bg-blue-50 text-blue-600">{studySpeed}</Tag>，系统在推荐内容时会自动补充线性代数和概率论的前置知识。</p>
                      <p className="mb-2"><strong className="text-slate-800">薄弱点：</strong> {weakAreas.join('、') || '暂无'}，系统已自动增加相关练习推送和3D动画讲解。</p>
                      <p><strong className="text-slate-800">兴趣方向：</strong> {profile?.interest_areas?.join('、') || '人工智能与机器学习'}。</p>
                    </div>
                  </div>
                  <Button type="primary" className="mt-5 rounded-lg bg-primary" onClick={() => navigate('/profile')}>手动修正画像</Button>
                </div>
              ),
            },
          ]}
        />
      </div>
    </Spin>
  )
}

export default PersonalSpace
