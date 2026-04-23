import React, { useEffect, useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Typography, Card, Row, Col, Button, Tag, Avatar, List, Space, Progress, message, Spin, Badge, Tooltip, Modal
} from 'antd'
import {
  Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer,
} from 'recharts'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
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
  StarOutlined,
  CrownOutlined,
  GiftOutlined,
  NodeIndexOutlined,
  PauseCircleOutlined,
  CheckCircleFilled,
  FlagFilled,
  EnvironmentOutlined,
  CheckCircleOutlined,
} from '@ant-design/icons'
import { useAppStore } from '../store'
import { profileApi, dashboardApi } from '../services/api'
import { buildRadarData } from '../utils/profile'
import { StatCard } from '../components/StatCard'

gsap.registerPlugin(ScrollTrigger)

const taskTypeMeta: Record<string, { icon: React.ReactNode; color: string; bg: string }> = {
  video: { icon: <PlayCircleOutlined />, color: '#ef4444', bg: '#fef2f2' },
  quiz: { icon: <BookOutlined />, color: '#f59e0b', bg: '#fffbeb' },
  doc: { icon: <FileTextOutlined />, color: '#10b981', bg: '#ecfdf5' },
  code: { icon: <CodeOutlined />, color: '#3b82f6', bg: '#eff6ff' },
}

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

const pathNodes = [
  { id: 1, title: 'C语言概述与开发环境', status: 'completed', type: '入门' },
  { id: 2, title: '数据类型与变量', status: 'completed', type: '基础' },
  { id: 3, title: '控制结构', status: 'in-progress', type: '核心' },
  { id: 4, title: '数组与字符串', status: 'pending', type: '核心' },
]

const statusColors: Record<string, string> = {
  completed: '#10b981',
  'in-progress': '#4f46e5',
  pending: '#94a3b8',
}

const POMODORO_FOCUS = 25 * 60
const POMODORO_BREAK = 5 * 60

const challenges = [
  { title: '完成今日图文讲义阅读', reward: 20, completed: false },
  { title: '提交1份代码实操', reward: 30, completed: true },
  { title: '连续打卡满7天', reward: 50, completed: false },
]

const badges = [
  { name: '初出茅庐', icon: <StarOutlined />, color: '#f59e0b', unlocked: true },
  { name: '代码能手', icon: <CodeOutlined />, color: '#3b82f6', unlocked: true },
  { name: '学习王者', icon: <CrownOutlined />, color: '#ef4444', unlocked: false },
  { name: '全勤标兵', icon: <FireOutlined />, color: '#10b981', unlocked: false },
]

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

  const [pomodoroTime, setPomodoroTime] = useState(POMODORO_FOCUS)
  const [isPomodoroRunning, setIsPomodoroRunning] = useState(false)
  const [isBreak, setIsBreak] = useState(false)
  const [pomodoroCount, setPomodoroCount] = useState(4)
  const [kgModalOpen, setKgModalOpen] = useState(false)
  const [algorithmAnalysis, setAlgorithmAnalysis] = useState<any>(null)

  const studentId = useAppStore((s) => s.studentId)
  const journeyRef = useRef<HTMLDivElement>(null)
  const pathRef = useRef<SVGPathElement>(null)
  const sceneRefs = useRef<(HTMLDivElement | null)[]>([])

  // Pomodoro timer
  useEffect(() => {
    let timer: any
    if (isPomodoroRunning && pomodoroTime > 0) {
      timer = setInterval(() => setPomodoroTime((t) => t - 1), 1000)
    } else if (isPomodoroRunning && pomodoroTime === 0) {
      setIsPomodoroRunning(false)
      if (!isBreak) {
        setPomodoroCount((c) => c + 1)
        message.success('专注时间结束！休息一下吧')
        setIsBreak(true)
        setPomodoroTime(POMODORO_BREAK)
      } else {
        message.success('休息结束，继续专注！')
        setIsBreak(false)
        setPomodoroTime(POMODORO_FOCUS)
      }
    }
    return () => clearInterval(timer)
  }, [isPomodoroRunning, pomodoroTime, isBreak])

  // Data fetching
  useEffect(() => {
    let timeoutId: ReturnType<typeof setTimeout>
    const fetchData = async () => {
      setIsLoading(true)
      setSummaryLoading(true)
      // 10秒超时兜底
      timeoutId = setTimeout(() => {
        setIsLoading(false)
        setSummaryLoading(false)
        message.warning('数据加载超时，请刷新重试')
      }, 10000)
      try {
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
          setAlgorithmAnalysis(d.algorithm_analysis || null)
        }
      } catch (e) {
        console.error('Dashboard 数据加载失败:', e)
        message.error('获取数据失败，显示默认数据')
      } finally {
        clearTimeout(timeoutId)
        setIsLoading(false)
        setSummaryLoading(false)
      }
    }
    fetchData()
    return () => clearTimeout(timeoutId)
  }, [studentId])

  // 3D scroll-driven animations
  useEffect(() => {
    const path = pathRef.current
    const triggerEl = journeyRef.current
    if (!path || !triggerEl) return

    const pathLength = path.getTotalLength()
    path.style.strokeDasharray = `${pathLength}`
    path.style.strokeDashoffset = `${pathLength}`

    const pathTween = gsap.to(path, {
      strokeDashoffset: 0,
      ease: 'none',
      scrollTrigger: {
        trigger: triggerEl,
        start: 'top 80%',
        end: 'bottom 20%',
        scrub: 1.2,
      },
    })

    sceneRefs.current.forEach((el, i) => {
      if (!el) return
      const isLeft = i % 2 === 0
      gsap.fromTo(
        el,
        {
          opacity: 0,
          rotateY: isLeft ? -45 : 45,
          rotateX: 12,
          z: -200,
          scale: 0.75,
          y: 60,
        },
        {
          opacity: 1,
          rotateY: 0,
          rotateX: 0,
          z: 0,
          scale: 1,
          y: 0,
          duration: 1,
          ease: 'power3.out',
          scrollTrigger: {
            trigger: el,
            start: 'top 88%',
            end: 'top 45%',
            scrub: 1,
          },
        }
      )
    })

    const decorEls = triggerEl.querySelectorAll('.journey-decor')
    decorEls.forEach((dec, i) => {
      gsap.to(dec, {
        y: (i % 2 === 0 ? -80 : 80),
        ease: 'none',
        scrollTrigger: {
          trigger: triggerEl,
          start: 'top bottom',
          end: 'bottom top',
          scrub: true,
        },
      })
    })

    return () => {
      pathTween.kill()
      ScrollTrigger.getAll().forEach((t) => t.kill())
    }
  }, [])

  const statCards = [
    { title: '本周学习', value: stats.weekly_hours, suffix: 'h', icon: <ClockCircleOutlined />, color: '#4f46e5', path: '/personal' },
    { title: '连续打卡', value: stats.streak_days, suffix: '天', icon: <FireOutlined />, color: '#f59e0b', path: '/personal' },
    { title: '掌握知识点', value: stats.mastered_kps, suffix: '个', icon: <TrophyOutlined />, color: '#10b981', path: '/profile' },
    { title: '待完成任务', value: tasks.length, suffix: '项', icon: <RocketOutlined />, color: '#0ea5e9', path: '/learning-path' },
  ]

  const setSceneRef = (idx: number) => (el: HTMLDivElement | null) => {
    sceneRefs.current[idx] = el
  }

  return (
    <div className="space-y-8">
      {/* ===== 顶部静态区 ===== */}
      <div className="flex flex-col lg:flex-row gap-6">
        <div className="flex-1">
          <Typography.Title level={3} className="!m-0 text-slate-900 font-bold tracking-tight">
            欢迎回来，学习者
          </Typography.Title>
          <Typography.Text className="text-slate-500 block mt-1">
            今天继续学习 <span className="text-primary font-medium">{welcomeTopic}</span> 吗？
          </Typography.Text>
        </div>
        <div className="flex items-center gap-4 bg-white rounded-2xl border border-slate-100 px-6 py-4">
          <div className="text-center">
            <div className="text-xs text-slate-500 mb-1">当前等级</div>
            <div className="text-xl font-bold text-primary">Lv.5</div>
          </div>
          <div className="flex-1 w-40">
            <div className="flex justify-between text-xs text-slate-500 mb-1">
              <span>经验值</span>
              <span>340 / 500</span>
            </div>
            <Progress percent={68} showInfo={false} strokeColor="#4f46e5" trailColor="#f1f5f9" size="small" />
          </div>
          <Button type="primary" className="rounded-xl bg-primary" onClick={() => navigate('/resources')}>
            继续学习 <ArrowRightOutlined />
          </Button>
        </div>
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

      {/* 算法分析结果 */}
      {algorithmAnalysis && (
        <Row gutter={[20, 20]}>
          <Col xs={24} lg={12}>
            <Card className="border border-slate-100 rounded-2xl shadow-card" title={
              <Space><NodeIndexOutlined className="text-primary text-lg" /><span className="font-semibold text-slate-800">学习趋势分析</span></Space>
            } styles={{ body: { padding: '24px' } }}>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-600">趋势状态</span>
                  <Tag className={`rounded-full border-0 text-xs font-medium ${
                    algorithmAnalysis.trend_analysis?.trend_state === 'growth' ? 'bg-emerald-50 text-emerald-600' :
                    algorithmAnalysis.trend_analysis?.trend_state === 'warning' ? 'bg-red-50 text-red-600' :
                    algorithmAnalysis.trend_analysis?.trend_state === 'decline' ? 'bg-amber-50 text-amber-600' :
                    'bg-slate-100 text-slate-600'
                  }`}>
                    {algorithmAnalysis.trend_analysis?.trend_state === 'growth' ? '上升趋势' :
                     algorithmAnalysis.trend_analysis?.trend_state === 'warning' ? '预警' :
                     algorithmAnalysis.trend_analysis?.trend_state === 'decline' ? '下滑' : '平稳'}
                  </Tag>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-600">综合趋势因子</span>
                  <span className="text-sm font-bold text-slate-800">{algorithmAnalysis.trend_analysis?.trend_factor?.toFixed(2) ?? '--'}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-600">3天后预测掌握度</span>
                  <span className="text-sm font-bold text-primary">{algorithmAnalysis.trend_analysis?.predicted_mastery_3d?.toFixed(1) ?? '--'}%</span>
                </div>
                <div className="p-3 rounded-xl bg-slate-50 border border-slate-100 text-xs text-slate-600 leading-relaxed">
                  <strong>干预建议：</strong>{algorithmAnalysis.trend_analysis?.intervention || '暂无建议'}
                </div>
                <div className="grid grid-cols-2 gap-2">
                  {Object.entries(algorithmAnalysis.trend_analysis?.dimensions || {}).map(([key, val]: [string, any]) => (
                    <div key={key} className="p-2 rounded-lg bg-slate-50 text-center">
                      <div className="text-xs text-slate-400">{key === 'mastery_trend' ? '掌握度趋势' : key === 'speed_ratio' ? '学习速度' : key === 'time_efficiency' ? '时间效率' : key === 'weakness_priority' ? '薄弱点优先' : '稳定性'}</div>
                      <div className="text-sm font-bold text-slate-800">{(val * 100).toFixed(0)}%</div>
                    </div>
                  ))}
                </div>
              </div>
            </Card>
          </Col>
          <Col xs={24} lg={12}>
            <Card className="border border-slate-100 rounded-2xl shadow-card" title={
              <Space><TrophyOutlined className="text-primary text-lg" /><span className="font-semibold text-slate-800">学习效果评估</span></Space>
            } styles={{ body: { padding: '24px' } }}>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-600">总体正确率</span>
                  <span className="text-sm font-bold text-slate-800">{algorithmAnalysis.effect_evaluation?.realtime_metrics?.accuracy?.toFixed(1) ?? '--'}%</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-600">掌握度</span>
                  <span className="text-sm font-bold text-slate-800">{algorithmAnalysis.effect_evaluation?.realtime_metrics?.mastery?.toFixed(1) ?? '--'}%</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-600">提升速率</span>
                  <span className={`text-sm font-bold ${(algorithmAnalysis.effect_evaluation?.realtime_metrics?.improvement_rate || 0) >= 0 ? 'text-emerald-600' : 'text-red-500'}`}>
                    {(algorithmAnalysis.effect_evaluation?.realtime_metrics?.improvement_rate || 0) >= 0 ? '+' : ''}{algorithmAnalysis.effect_evaluation?.realtime_metrics?.improvement_rate?.toFixed(1) ?? '--'}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-600">预测下次得分</span>
                  <span className="text-sm font-bold text-primary">{algorithmAnalysis.effect_evaluation?.predictions?.next_score?.toFixed(1) ?? '--'}</span>
                </div>
                <div className="p-3 rounded-xl bg-slate-50 border border-slate-100">
                  <div className="text-xs text-slate-500 mb-2 font-medium">潜在失分点 TOP3</div>
                  <div className="space-y-1">
                    {(algorithmAnalysis.effect_evaluation?.predictions?.potential_loss_points || []).slice(0, 3).map((p: any, i: number) => (
                      <div key={i} className="flex items-center justify-between text-xs">
                        <span className="text-slate-600">{p.tag}</span>
                        <span className="text-slate-400">风险 {(p.risk_score * 100).toFixed(0)}%</span>
                      </div>
                    ))}
                    {(algorithmAnalysis.effect_evaluation?.predictions?.potential_loss_points || []).length === 0 && (
                      <span className="text-xs text-slate-400">暂无显著失分点</span>
                    )}
                  </div>
                </div>
                <div className="p-3 rounded-xl bg-indigo-50 border border-indigo-100 text-xs text-indigo-700 leading-relaxed">
                  <strong>干预策略（{algorithmAnalysis.effect_evaluation?.intervention?.priority === 'high' ? '高优先级' : '正常'}）：</strong>
                  {(algorithmAnalysis.effect_evaluation?.intervention?.strategies || []).map((s: any) => s.action).join('；') || '继续保持'}
                </div>
              </div>
            </Card>
          </Col>
        </Row>
      )}

      {/* ===== 3D 滚动旅程区 ===== */}
      <div
        ref={journeyRef}
        className="relative"
        style={{ perspective: '1200px', perspectiveOrigin: '50% 50%' }}
      >
        {/* SVG 描边路径 */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-5xl pointer-events-none" style={{ zIndex: 0 }}>
          <svg viewBox="0 0 1378 4200" fill="none" preserveAspectRatio="xMidYMin meet" className="w-full h-auto">
            <path
              ref={pathRef}
              d="M639.668 100C639.668 100 105.669 100 199.669 601.503C293.669 1103.01 1277.17 691.502 1277.17 1399.5C1277.17 2107.5 -155.332 1968 140.168 2400C435.669 2832 1442.66 2600 713.168 3200C-16.3318 3800 639.668 3900 639.668 4100"
              stroke="#FF5F0A"
              strokeWidth="160"
              strokeLinecap="round"
              opacity="0.25"
            />
          </svg>
        </div>

        {/* 背景装饰 —— 视差层 */}
        <div className="journey-decor absolute top-32 left-10 w-32 h-32 rounded-full bg-indigo-100 opacity-40 blur-2xl" />
        <div className="journey-decor absolute top-[600px] right-12 w-40 h-40 rounded-full bg-amber-100 opacity-40 blur-2xl" />
        <div className="journey-decor absolute top-[1200px] left-16 w-36 h-36 rounded-full bg-emerald-100 opacity-40 blur-2xl" />
        <div className="journey-decor absolute top-[1800px] right-20 w-44 h-44 rounded-full bg-rose-100 opacity-30 blur-2xl" />
        <div className="journey-decor absolute top-[2400px] left-8 w-32 h-32 rounded-full bg-sky-100 opacity-40 blur-2xl" />
        <div className="journey-decor absolute top-[3000px] right-10 w-40 h-40 rounded-full bg-purple-100 opacity-30 blur-2xl" />

        {/* 旅程内容 */}
        <div className="relative space-y-32 py-20" style={{ zIndex: 1 }}>

          {/* === Scene 1: 学习路径（左） === */}
          <div ref={setSceneRef(0)} className="flex justify-start px-4 md:px-12" style={{ transformStyle: 'preserve-3d' }}>
            <div className="w-full max-w-xl">
              <Card className="border border-slate-100 rounded-2xl shadow-card" styles={{ body: { padding: '28px' } }}>
                <div className="flex items-center gap-2 mb-5">
                  <NodeIndexOutlined className="text-primary text-lg" />
                  <span className="font-semibold text-slate-800">当前学习路径</span>
                  <Tag className="rounded-full border-0 bg-primary-50 text-primary text-xs ml-auto">共 {pathNodes.length} 个阶段</Tag>
                </div>
                <div className="relative max-w-md mx-auto">
                  <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-slate-100" />
                  <div className="space-y-6">
                    {pathNodes.map((node) => (
                      <div key={node.id} className="flex items-start gap-4 relative">
                        <div
                          className="relative z-10 w-12 h-12 rounded-full flex items-center justify-center text-white text-lg shrink-0 shadow-sm cursor-pointer"
                          style={{ background: statusColors[node.status] }}
                          onClick={() => navigate('/learning-path')}
                        >
                          {node.status === 'completed' ? <CheckCircleOutlined /> :
                           node.status === 'in-progress' ? <ClockCircleOutlined /> :
                           <EnvironmentOutlined />}
                        </div>
                        <div className="flex-1 p-4 rounded-xl bg-white border border-slate-100 hover:border-slate-200 hover:shadow-card transition-all cursor-pointer" onClick={() => navigate('/learning-path')}>
                          <div className="flex items-center justify-between mb-1">
                            <Tag className="rounded-full border-0 text-xs font-medium" style={{ background: node.status === 'completed' ? '#ecfdf5' : node.status === 'in-progress' ? '#eef2ff' : '#f8fafc', color: statusColors[node.status] }}>
                              {node.status === 'completed' ? '已完成' : node.status === 'in-progress' ? '进行中' : '未开始'}
                            </Tag>
                            <span className="text-xs text-slate-400">{node.type}</span>
                          </div>
                          <div className="font-bold text-slate-800">{node.title}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </Card>
            </div>
          </div>

          {/* === Scene 2: 番茄钟（右） === */}
          <div ref={setSceneRef(1)} className="flex justify-end px-4 md:px-12" style={{ transformStyle: 'preserve-3d' }}>
            <div className="w-full max-w-md">
              <Card className="border border-slate-100 rounded-2xl shadow-card" styles={{ body: { padding: '28px' } }}>
                <div className="flex items-center justify-between mb-5">
                  <div className="flex items-center gap-2">
                    <ClockCircleOutlined className="text-primary text-lg" />
                    <span className="font-semibold text-slate-800">番茄专注钟</span>
                  </div>
                  <Tag className="rounded-full border-0 bg-primary-50 text-primary text-xs font-medium">{pomodoroCount} 个番茄</Tag>
                </div>
                <div className="text-center py-2">
                  <div className={`text-6xl font-bold tracking-tight mb-3 ${isBreak ? 'text-emerald-500' : 'text-primary'}`}>
                    {Math.floor(pomodoroTime / 60).toString().padStart(2, '0')}:{(pomodoroTime % 60).toString().padStart(2, '0')}
                  </div>
                  <div className="text-xs text-slate-400 mb-5">{isBreak ? '休息时间 · 恢复精力' : '专注时间 · 保持高效'}</div>
                  <Space>
                    <Button type="primary" shape="round" icon={isPomodoroRunning ? <PauseCircleOutlined /> : <PlayCircleOutlined />} onClick={() => setIsPomodoroRunning(!isPomodoroRunning)} className="bg-primary">
                      {isPomodoroRunning ? '暂停' : '开始'}
                    </Button>
                    <Button shape="round" onClick={() => { setIsPomodoroRunning(false); setPomodoroTime(isBreak ? POMODORO_BREAK : POMODORO_FOCUS) }}>重置</Button>
                  </Space>
                </div>
              </Card>
            </div>
          </div>

          {/* === Scene 3: 今日任务（左） === */}
          <div ref={setSceneRef(2)} className="flex justify-start px-4 md:px-12" style={{ transformStyle: 'preserve-3d' }}>
            <div className="w-full max-w-xl">
              <Card
                className="border border-slate-100 rounded-2xl shadow-card"
                title={<span className="font-semibold text-slate-800">今日学习任务</span>}
                extra={
                  <Tag className="rounded-full border-0 bg-sky-50 text-sky-600 font-medium text-xs">
                    {tasks.length} 项待完成
                  </Tag>
                }
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
            </div>
          </div>

          {/* === Scene 4: 今日挑战（右） === */}
          <div ref={setSceneRef(3)} className="flex justify-end px-4 md:px-12" style={{ transformStyle: 'preserve-3d' }}>
            <div className="w-full max-w-lg">
              <Card className="border border-slate-100 rounded-2xl shadow-card" title={<span className="font-semibold text-slate-800">今日挑战</span>}
                extra={<Tag className="rounded-full border-0 bg-amber-50 text-amber-600 text-xs font-medium">+{challenges.filter(c => !c.completed).reduce((s, c) => s + c.reward, 0)} 经验待领取</Tag>}
                styles={{ body: { padding: '24px' } }}>
                <div className="flex flex-wrap gap-3">
                  {challenges.map((c, idx) => (
                    <div key={idx} className={`flex items-center gap-3 px-4 py-3 rounded-xl border transition-all ${c.completed ? 'bg-slate-50 border-slate-100 opacity-60' : 'bg-white border-slate-200 hover:border-primary hover:shadow-card cursor-pointer'}`}>
                      <div className={`w-8 h-8 rounded-lg flex items-center justify-center text-white text-sm shrink-0 ${c.completed ? 'bg-slate-300' : 'bg-warning'}`}>
                        {c.completed ? <TrophyOutlined /> : <GiftOutlined />}
                      </div>
                      <div>
                        <div className={`text-sm font-medium ${c.completed ? 'text-slate-400 line-through' : 'text-slate-800'}`}>{c.title}</div>
                        <div className="text-xs text-slate-400">+{c.reward} XP</div>
                      </div>
                    </div>
                  ))}
                </div>
              </Card>
            </div>
          </div>

          {/* === Scene 5: 推荐资源（左） === */}
          <div ref={setSceneRef(4)} className="flex justify-start px-4 md:px-12" style={{ transformStyle: 'preserve-3d' }}>
            <div className="w-full max-w-xl">
              <Card
                className="border border-slate-100 rounded-2xl shadow-card"
                title={<span className="font-semibold text-slate-800">推荐资源</span>}
                extra={
                  <Button type="link" className="text-primary font-medium" onClick={() => navigate('/resources')}>
                    查看全部 <ArrowRightOutlined />
                  </Button>
                }
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
            </div>
          </div>

          {/* === Scene 6: 画像摘要 + 徽章（右） === */}
          <div ref={setSceneRef(5)} className="flex justify-end px-4 md:px-12" style={{ transformStyle: 'preserve-3d' }}>
            <div className="w-full max-w-md space-y-5">
              <Card className="border border-slate-100 rounded-2xl shadow-card" title={<Space><span className="font-semibold text-slate-800">画像摘要</span><Badge count="AI" style={{ backgroundColor: '#4f46e5', fontSize: 10 }} /></Space>}
                extra={<Button type="link" className="text-primary font-medium" onClick={() => navigate('/profile')}>详情 <ArrowRightOutlined /></Button>}
                styles={{ body: { padding: '24px' } }}>
                <Spin spinning={isLoading}>
                  {!isLoading && (
                    <>
                      <div className="h-56">
                        <ResponsiveContainer width="100%" height="100%">
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
                          <Tag key={item.subject} className="rounded-full border-0 bg-slate-100 text-slate-600 text-xs">{item.subject}: {Math.round(item.A)}</Tag>
                        ))}
                      </div>
                    </>
                  )}
                </Spin>
              </Card>

              <Card className="border border-slate-100 rounded-2xl shadow-card" title={<span className="font-semibold text-slate-800">成就徽章</span>}
                extra={<Button type="link" className="text-primary font-medium" onClick={() => navigate('/personal')}>全部 <ArrowRightOutlined /></Button>}
                styles={{ body: { padding: '24px' } }}>
                <div className="grid grid-cols-4 gap-3">
                  {badges.map((b, idx) => (
                    <div key={idx} className={`flex flex-col items-center gap-2 p-3 rounded-xl transition-all ${b.unlocked ? 'bg-slate-50' : 'bg-slate-50 opacity-40'}`}>
                      <div className="w-10 h-10 rounded-full flex items-center justify-center text-white text-lg" style={{ background: b.unlocked ? b.color : '#cbd5e1' }}>{b.icon}</div>
                      <span className="text-xs text-slate-600 font-medium text-center">{b.name}</span>
                    </div>
                  ))}
                </div>
              </Card>
            </div>
          </div>

          {/* === Scene 7: 知识图谱 + 算力适配（左，合并一行） === */}
          <div ref={setSceneRef(6)} className="flex justify-start px-4 md:px-12" style={{ transformStyle: 'preserve-3d' }}>
            <div className="w-full max-w-xl space-y-5">
              <Card className="border border-slate-100 rounded-2xl shadow-card" title={<span className="font-semibold text-slate-800">知识图谱</span>} styles={{ body: { padding: '24px' } }}>
                <div className="flex items-center gap-4 p-4 rounded-xl bg-gradient-to-br from-indigo-50 to-purple-50 border border-indigo-100 cursor-pointer hover:shadow-card transition-all" onClick={() => setKgModalOpen(true)}>
                  <div className="w-12 h-12 rounded-xl bg-indigo-500 flex items-center justify-center text-white text-xl shrink-0"><NodeIndexOutlined /></div>
                  <div>
                    <div className="font-semibold text-slate-800 text-sm">查看知识关联</div>
                    <div className="text-xs text-slate-500 mt-0.5">基于知识图谱的科学路径规划</div>
                  </div>
                  <ArrowRightOutlined className="text-indigo-400 ml-auto" />
                </div>
              </Card>

              <Card className="border border-slate-100 rounded-2xl shadow-card" title={<span className="font-semibold text-slate-800">算力适配</span>} styles={{ body: { padding: '24px' } }}>
                <div className="flex flex-wrap gap-2">
                  <Tooltip title="已适配文心一言"><Tag icon={<FlagFilled />} className="rounded-full border-0 bg-blue-50 text-blue-600 text-xs">文心一言</Tag></Tooltip>
                  <Tooltip title="已适配通义千问"><Tag icon={<FlagFilled />} className="rounded-full border-0 bg-purple-50 text-purple-600 text-xs">通义千问</Tag></Tooltip>
                  <Tooltip title="已适配国产算力平台"><Tag icon={<FlagFilled />} className="rounded-full border-0 bg-emerald-50 text-emerald-600 text-xs">昇腾 NPU</Tag></Tooltip>
                  <Tooltip title="RAG 检索增强"><Tag icon={<CheckCircleFilled />} className="rounded-full border-0 bg-slate-100 text-slate-600 text-xs">RAG 架构</Tag></Tooltip>
                </div>
              </Card>
            </div>
          </div>

          {/* === Scene 8: 旅程终点（居中） === */}
          <div ref={setSceneRef(7)} className="flex justify-center px-4" style={{ transformStyle: 'preserve-3d' }}>
            <div className="w-full max-w-lg text-center py-16">
              <div className="text-5xl mb-4">🎓</div>
              <Typography.Title level={4} className="!m-0 text-slate-800 font-bold">学习之路，永无止境</Typography.Title>
              <Typography.Text className="text-slate-400 text-sm block mt-2">继续探索，下一站的风景更精彩</Typography.Text>
              <Button type="primary" size="large" className="rounded-xl bg-primary mt-6" onClick={() => navigate('/resources')}>
                开始学习 <ArrowRightOutlined />
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* 知识图谱弹窗 */}
      <Modal title={<span className="font-semibold text-slate-800">知识图谱概览</span>} open={kgModalOpen} onCancel={() => setKgModalOpen(false)} footer={null} width={720} className="rounded-2xl">
        <div className="space-y-4 py-2">
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-100">
            <div className="font-semibold text-slate-800 mb-2">编程基础 · 核心知识网络</div>
            <div className="grid grid-cols-3 gap-3">
              {['变量与类型', '控制结构', '数组与字符串', '函数与递归', '指针与内存', '结构体', '文件操作', '预处理', '动态内存'].map((node) => (
                <div key={node} className="p-3 rounded-lg bg-white border border-slate-200 text-center text-sm text-slate-700 hover:border-primary hover:shadow-sm transition-all cursor-pointer">{node}</div>
              ))}
            </div>
          </div>
          <div className="flex items-center gap-2 text-xs text-slate-400"><NodeIndexOutlined /><span>知识图谱确保学习路径科学性，减少大模型幻觉影响</span></div>
        </div>
      </Modal>
    </div>
  )
}

export default Dashboard
