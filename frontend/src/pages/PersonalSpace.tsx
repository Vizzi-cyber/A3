import React, { useEffect, useState } from 'react'
import { Typography, Tabs, List, Avatar, Tag, Space, Button, Progress, Row, Col } from 'antd'
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
  CrownOutlined,
  ThunderboltOutlined,
  BulbOutlined,
  MessageOutlined,
  ApartmentOutlined,
  CheckCircleOutlined,
  ReloadOutlined,
  BookOutlined,
} from '@ant-design/icons'
import type { ReflectionEntry } from '../types'
import { useAppStore } from '../store'
import { profileApi } from '../services/api'
import { StatCard } from '../components/StatCard'
import { Input, message } from 'antd'

const focusData = [
  { day: '周一', focus: 75, duration: 120 },
  { day: '周二', focus: 82, duration: 150 },
  { day: '周三', focus: 68, duration: 90 },
  { day: '周四', focus: 88, duration: 180 },
  { day: '周五', focus: 79, duration: 140 },
  { day: '周六', focus: 92, duration: 200 },
  { day: '周日', focus: 85, duration: 160 },
]

const historyList = [
  { title: '完成 2.1 线性代数基础 图文讲义', time: '今天 10:23', type: 'doc' },
  { title: '提交 梯度下降原理练习题 x3', time: '今天 09:45', type: 'quiz' },
  { title: '收藏 《神经网络PyTorch代码模板》', time: '昨天 16:30', type: 'code' },
  { title: '更新学习画像：数学基础 +5', time: '昨天 14:20', type: 'profile' },
  { title: '完成 1.2 监督学习与无监督学习 阅读', time: '昨天 10:00', type: 'doc' },
]

const favorites = [
  { title: '神经网络PyTorch代码模板', type: 'code', icon: <CodeOutlined />, color: '#3b82f6' },
  { title: '李宏毅机器学习课程笔记', type: 'doc', icon: <FileTextOutlined />, color: '#10b981' },
  { title: '反向传播算法3D动画', type: 'video', icon: <VideoCameraOutlined />, color: '#ef4444' },
]

const typeMeta: Record<string, { icon: React.ReactNode; color: string; bg: string; label: string }> = {
  video: { icon: <VideoCameraOutlined />, color: '#ef4444', bg: '#fef2f2', label: '视频' },
  quiz: { icon: <TrophyOutlined />, color: '#f59e0b', bg: '#fffbeb', label: '练习' },
  code: { icon: <CodeOutlined />, color: '#3b82f6', bg: '#eff6ff', label: '代码' },
  profile: { icon: <EditOutlined />, color: '#8b5cf6', bg: '#f5f3ff', label: '画像' },
  doc: { icon: <FileTextOutlined />, color: '#10b981', bg: '#ecfdf5', label: '文档' },
}

const statCards = [
  { title: '累计学习时长', value: 42, suffix: 'h', color: '#4f46e5', icon: <ClockCircleOutlined /> },
  { title: '最长连续打卡', value: 15, suffix: '天', color: '#f59e0b', icon: <FireOutlined /> },
  { title: '获得勋章', value: 8, suffix: '枚', color: '#10b981', icon: <TrophyOutlined /> },
  { title: '收藏资源', value: 23, suffix: '个', color: '#ec4899', icon: <HeartOutlined /> },
]

const allBadges = [
  { id: '1', name: '初出茅庐', desc: '完成首次学习', icon: <StarOutlined />, color: '#f59e0b', unlocked: true },
  { id: '2', name: '代码能手', desc: '完成5次代码实操', icon: <CodeOutlined />, color: '#3b82f6', unlocked: true },
  { id: '3', name: '学习王者', desc: '连续打卡30天', icon: <CrownOutlined />, color: '#ef4444', unlocked: false },
  { id: '4', name: '全勤标兵', desc: '连续7天完成每日挑战', icon: <FireOutlined />, color: '#10b981', unlocked: false },
  { id: '5', name: '思维导图', desc: '生成10张思维导图', icon: <ApartmentOutlined />, color: '#8b5cf6', unlocked: false },
  { id: '6', name: '提问达人', desc: '向AI辅导提问50次', icon: <MessageOutlined />, color: '#0ea5e9', unlocked: false },
  { id: '7', name: '知识探索者', desc: '完成全部基础章节', icon: <BulbOutlined />, color: '#f59e0b', unlocked: false },
  { id: '8', name: '完美通过', desc: '测验全部满分', icon: <CheckCircleOutlined />, color: '#10b981', unlocked: false },
]

const defaultReflections: ReflectionEntry[] = [
  { id: '1', date: '2026-04-19', content: '今天学习了梯度下降原理，理解了学习率对收敛的影响。下次需要多做一些调参练习。', topic: '梯度下降与优化' },
  { id: '2', date: '2026-04-18', content: '线性代数基础部分矩阵运算已经比较熟练，但特征值分解还需要加强理解。', topic: '线性代数基础' },
]

const PersonalSpace: React.FC = () => {
  const [profile, setProfile] = useState<any>(null)
  const [reflections, setReflections] = useState<ReflectionEntry[]>(defaultReflections)
  const [newReflection, setNewReflection] = useState('')
  const [pomodoroStats, setPomodoroStats] = useState({ total: 42, today: 4, streak: 5 })
  const [cornellNotes, setCornellNotes] = useState({ cues: '', notes: '', summary: '' })
  const [feynmanInput, setFeynmanInput] = useState('')
  const studentId = useAppStore((s) => s.studentId)

  useEffect(() => {
    const load = async () => {
      try {
        const res: any = await profileApi.get(studentId)
        if (res.data) setProfile(res.data)
      } catch (e) {
        // ignore
      }
    }
    load()
  }, [studentId])

  const weakAreas = profile?.weak_areas || ['概率论', '梯度下降原理']
  const cognitivePrimary = profile?.cognitive_style?.primary || 'visual'
  const studySpeed = profile?.learning_tempo?.study_speed || 'moderate'

  const handleAddReflection = () => {
    if (!newReflection.trim()) return
    const entry: ReflectionEntry = {
      id: Date.now().toString(),
      date: new Date().toISOString().slice(0, 10),
      content: newReflection.trim(),
      topic: '今日学习',
    }
    setReflections([entry, ...reflections])
    setNewReflection('')
  }

  return (
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
        <Col xs={12} lg={6}>
          <StatCard
            icon={<ClockCircleOutlined />}
            color="#ef4444"
            title="今日番茄钟"
            value={pomodoroStats.today}
            suffix="个"
          />
        </Col>
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
                        <ResponsiveContainer width="100%" height="100%">
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
                        <ResponsiveContainer width="100%" height="100%">
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
                    dataSource={historyList}
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
                  {favorites.map((item, idx) => (
                    <Col xs={24} sm={12} lg={8} key={idx}>
                      <div className="p-5 rounded-xl bg-slate-50 hover:bg-white hover:shadow-card transition-all cursor-pointer border border-slate-100 hover:border-slate-200">
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
                </Row>
              </div>
            ),
          },
          {
            key: 'badges',
            label: (
              <span className="flex items-center gap-1.5">
                <TrophyOutlined /> 成就徽章
              </span>
            ),
            children: (
              <div className="bg-white rounded-2xl border border-slate-100 p-6">
                <div className="flex items-center justify-between mb-6">
                  <div className="font-semibold text-slate-800">我的成就</div>
                  <Tag className="rounded-full border-0 bg-slate-100 text-slate-600 text-xs">
                    已解锁 {allBadges.filter(b => b.unlocked).length} / {allBadges.length}
                  </Tag>
                </div>
                <Row gutter={[20, 20]}>
                  {allBadges.map((badge) => (
                    <Col xs={12} sm={8} lg={6} key={badge.id}>
                      <div className={`flex flex-col items-center gap-3 p-5 rounded-xl border transition-all ${badge.unlocked ? 'bg-white border-slate-100 hover:shadow-card' : 'bg-slate-50 border-slate-100 opacity-50'}`}>
                        <div
                          className="w-14 h-14 rounded-full flex items-center justify-center text-white text-xl"
                          style={{ background: badge.unlocked ? badge.color : '#cbd5e1' }}
                        >
                          {badge.icon}
                        </div>
                        <div className="text-center">
                          <div className="font-semibold text-slate-800 text-sm">{badge.name}</div>
                          <div className="text-xs text-slate-400 mt-1">{badge.desc}</div>
                        </div>
                        {badge.unlocked && <Tag className="rounded-full border-0 bg-emerald-50 text-emerald-600 text-xs">已解锁</Tag>}
                      </div>
                    </Col>
                  ))}
                </Row>
              </div>
            ),
          },
          {
            key: 'reflection',
            label: (
              <span className="flex items-center gap-1.5">
                <EditOutlined /> 自我反思
              </span>
            ),
            children: (
              <div className="space-y-5">
                <div className="bg-white rounded-2xl border border-slate-100 p-6">
                  <div className="font-semibold text-slate-800 mb-4">写今日反思</div>
                  <Input.TextArea
                    rows={4}
                    placeholder="今天学到了什么？有哪些地方还需要提高？记录下来，帮助你加深记忆..."
                    value={newReflection}
                    onChange={(e) => setNewReflection(e.target.value)}
                    className="rounded-xl bg-slate-50 border-slate-200 mb-3"
                  />
                  <Button type="primary" className="rounded-lg bg-primary" onClick={handleAddReflection}>
                    保存反思
                  </Button>
                </div>

                <div className="bg-white rounded-2xl border border-slate-100 p-6">
                  <div className="font-semibold text-slate-800 mb-4">反思记录</div>
                  <div className="space-y-4">
                    {reflections.map((r) => (
                      <div key={r.id} className="p-4 rounded-xl bg-slate-50 border border-slate-100">
                        <div className="flex items-center gap-2 mb-2">
                          <Tag className="rounded-full border-0 bg-primary-50 text-primary text-xs">{r.topic}</Tag>
                          <span className="text-xs text-slate-400">{r.date}</span>
                        </div>
                        <Typography.Text className="text-slate-700 text-sm leading-relaxed block">{r.content}</Typography.Text>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ),
          },
          {
            key: 'cornell',
            label: (
              <span className="flex items-center gap-1.5">
                <BookOutlined /> 康奈尔笔记
              </span>
            ),
            children: (
              <div className="space-y-5">
                <div className="bg-white rounded-2xl border border-slate-100 p-6">
                  <div className="font-semibold text-slate-800 mb-4">康奈尔笔记法</div>
                  <div className="grid grid-cols-3 gap-4">
                    <div className="col-span-1 space-y-2">
                      <div className="text-xs font-medium text-slate-500">线索栏 (Cues)</div>
                      <Input.TextArea rows={10} placeholder="记录关键词、问题..." value={cornellNotes.cues} onChange={(e) => setCornellNotes({ ...cornellNotes, cues: e.target.value })} className="rounded-xl bg-slate-50 border-slate-200" />
                    </div>
                    <div className="col-span-2 space-y-2">
                      <div className="text-xs font-medium text-slate-500">笔记栏 (Notes)</div>
                      <Input.TextArea rows={10} placeholder="记录课堂/阅读笔记..." value={cornellNotes.notes} onChange={(e) => setCornellNotes({ ...cornellNotes, notes: e.target.value })} className="rounded-xl bg-slate-50 border-slate-200" />
                    </div>
                  </div>
                  <div className="mt-4 space-y-2">
                    <div className="text-xs font-medium text-slate-500">总结栏 (Summary)</div>
                    <Input.TextArea rows={3} placeholder="用一句话总结本页核心内容..." value={cornellNotes.summary} onChange={(e) => setCornellNotes({ ...cornellNotes, summary: e.target.value })} className="rounded-xl bg-slate-50 border-slate-200" />
                  </div>
                  <Button type="primary" className="rounded-lg bg-primary mt-4">
                    <CheckCircleOutlined /> 保存康奈尔笔记
                  </Button>
                </div>
              </div>
            ),
          },
          {
            key: 'feynman',
            label: (
              <span className="flex items-center gap-1.5">
                <BulbOutlined /> 费曼练习
              </span>
            ),
            children: (
              <div className="space-y-5">
                <div className="bg-white rounded-2xl border border-slate-100 p-6">
                  <div className="font-semibold text-slate-800 mb-4">费曼学习法</div>
                  <div className="p-4 rounded-xl bg-amber-50 border border-amber-100 text-sm text-amber-800 mb-4">
                    <strong>费曼技巧：</strong>选择你要学习的概念，尝试用最简单的语言向一个"小孩"解释它。如果你卡住了，就回到材料中重新学习，然后再次尝试简化。
                  </div>
                  <Input.TextArea rows={6} placeholder="用你自己的话，尝试向一个外行解释最近学到的知识点..." value={feynmanInput} onChange={(e) => setFeynmanInput(e.target.value)} className="rounded-xl bg-slate-50 border-slate-200 mb-3" />
                  <Button type="primary" className="rounded-lg bg-primary" onClick={() => { if (feynmanInput.trim()) { message.success('费曼练习已保存'); setFeynmanInput(''); } }}>
                    <ThunderboltOutlined /> 提交费曼练习
                  </Button>
                </div>
              </div>
            ),
          },
          {
            key: 'forgetting',
            label: (
              <span className="flex items-center gap-1.5">
                <ReloadOutlined /> 遗忘曲线
              </span>
            ),
            children: (
              <div className="space-y-5">
                <Row gutter={[20, 20]}>
                  <Col xs={24} lg={12}>
                    <div className="bg-white rounded-2xl border border-slate-100 p-6">
                      <div className="flex items-center gap-2 mb-4">
                        <LineChartOutlined className="text-primary" />
                        <span className="font-semibold text-slate-800">艾宾浩斯遗忘曲线</span>
                      </div>
                      <div className="h-60">
                        <ResponsiveContainer width="100%" height="100%">
                          <LineChart data={[
                            { day: '1天', memory: 100 },
                            { day: '2天', memory: 55 },
                            { day: '3天', memory: 42 },
                            { day: '5天', memory: 35 },
                            { day: '8天', memory: 30 },
                            { day: '15天', memory: 25 },
                            { day: '30天', memory: 20 },
                          ]}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                            <XAxis dataKey="day" tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
                            <YAxis domain={[0, 100]} tick={{ fill: '#64748b' }} axisLine={false} tickLine={false} />
                            <Tooltip contentStyle={{ borderRadius: 12, border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.06)' }} />
                            <Line type="monotone" dataKey="memory" name="理论记忆保留率" stroke="#ef4444" strokeWidth={2} dot={{ r: 3 }} strokeDasharray="5 5" />
                          </LineChart>
                        </ResponsiveContainer>
                      </div>
                    </div>
                  </Col>
                  <Col xs={24} lg={12}>
                    <div className="bg-white rounded-2xl border border-slate-100 p-6">
                      <div className="font-semibold text-slate-800 mb-4">待复习知识点</div>
                      <div className="space-y-3">
                        {[
                          { topic: '线性代数基础', retention: 62, nextReview: '今天' },
                          { topic: '梯度下降原理', retention: 85, nextReview: '明天' },
                          { topic: '神经网络结构', retention: 45, nextReview: '今天' },
                          { topic: '反向传播算法', retention: 78, nextReview: '后天' },
                        ].map((item) => (
                          <div key={item.topic} className="flex items-center gap-3 p-3 rounded-xl bg-slate-50 border border-slate-100">
                            <div className="flex-1">
                              <div className="text-sm font-medium text-slate-800">{item.topic}</div>
                              <div className="text-xs text-slate-400">下次复习: {item.nextReview}</div>
                            </div>
                            <div className="w-20">
                              <Progress percent={item.retention} size="small" strokeColor={item.retention > 70 ? '#10b981' : item.retention > 50 ? '#f59e0b' : '#ef4444'} trailColor="#f1f5f9" showInfo={false} />
                            </div>
                            <Tag className={`rounded-full border-0 text-xs ${item.retention > 70 ? 'bg-emerald-50 text-emerald-600' : item.retention > 50 ? 'bg-amber-50 text-amber-600' : 'bg-red-50 text-red-600'}`}>
                              {item.retention}%
                            </Tag>
                          </div>
                        ))}
                      </div>
                    </div>
                  </Col>
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
                <Button type="primary" className="mt-5 rounded-lg bg-primary">手动修正画像</Button>
              </div>
            ),
          },
        ]}
      />
    </div>
  )
}

export default PersonalSpace
