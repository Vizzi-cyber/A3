import React, { useEffect, useState } from 'react'
import { Typography, Tabs, List, Avatar, Tag, Space, Button, Progress, Row, Col, message } from 'antd'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar,
} from 'recharts'
import { useNavigate, useSearchParams } from 'react-router-dom'
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
import type { ReflectionEntry, StudentProfile, DashboardStats, Achievement } from '../types'
import { useAppStore } from '../store'

interface FavoriteItem {
  id?: string
  title: string
  resource_type: string
  url?: string
}

interface HistoryItem {
  title: string
  time: string
  type: string
}

interface FocusItem {
  day: string
  focus: number
  duration: number
}

interface ReviewTopic {
  topic: string
  retention: number
  nextReview: string
}

interface BadgeItemLocal {
  id: string
  name: string
  desc: string
  icon: React.ReactNode
  color: string
  unlocked: boolean
  unlocked_at?: string
}
import {
  profileApi,
  dashboardApi,
  gamificationApi,
  learningDataApi,
  favoritesApi,
  logReflectionApi,
  trendApi,
} from '../services/api'
import { StatCard } from '../components/StatCard'
import { Input, Collapse, Drawer, Popconfirm } from 'antd'
import { CaretRightOutlined, AlertOutlined, RiseOutlined, FallOutlined, DeleteOutlined } from '@ant-design/icons'

const typeMeta: Record<string, { icon: React.ReactNode; color: string; bg: string; label: string }> = {
  video: { icon: <VideoCameraOutlined />, color: '#ef4444', bg: '#fef2f2', label: '视频' },
  quiz: { icon: <TrophyOutlined />, color: '#f59e0b', bg: '#fffbeb', label: '练习' },
  code: { icon: <CodeOutlined />, color: '#3b82f6', bg: '#eff6ff', label: '代码' },
  profile: { icon: <EditOutlined />, color: '#8b5cf6', bg: '#f5f3ff', label: '画像' },
  doc: { icon: <FileTextOutlined />, color: '#10b981', bg: '#ecfdf5', label: '文档' },
  document: { icon: <FileTextOutlined />, color: '#10b981', bg: '#ecfdf5', label: '文档' },
  mindmap: { icon: <ApartmentOutlined />, color: '#8b5cf6', bg: '#f5f3ff', label: '思维导图' },
}

const PersonalSpace: React.FC = () => {
  const navigate = useNavigate()
  const [searchParams, setSearchParams] = useSearchParams()
  const initialTab = searchParams.get('tab') || 'history'
  const [activeTab, setActiveTab] = useState<string>(initialTab)
  const [profile, setProfile] = useState<StudentProfile | null>(null)
  const [dashboardStats, setDashboardStats] = useState<Record<string, unknown> | null>(null)
  const [points, setPoints] = useState<Record<string, unknown> | null>(null)
  const [achievements, setAchievements] = useState<Achievement[]>([])
  const [reflections, setReflections] = useState<ReflectionEntry[]>([])
  const [newReflection, setNewReflection] = useState('')
  const [favorites, setFavorites] = useState<FavoriteItem[]>([])
  const [learningHistory, setLearningHistory] = useState<HistoryItem[]>([])
  const [focusData, setFocusData] = useState<FocusItem[]>([])
  const [pomodoroStats, setPomodoroStats] = useState({ total: 0, today: 0, streak: 0 })
  const [cornellNotes, setCornellNotes] = useState({ cues: '', notes: '', summary: '' })
  const [feynmanInput, setFeynmanInput] = useState('')
  const [reviewTopics, setReviewTopics] = useState<ReviewTopic[]>([])
  const [trendInfo, setTrendInfo] = useState<{
    state: string
    factor: number
    dimensions: Record<string, number>
    intervention: string
  } | null>(null)
  const [notesHistory, setNotesHistory] = useState<Array<{
    id: string
    date: string
    type: 'cornell' | 'notes' | 'feynman' | 'other'
    title: string
    content: string
    rawContent?: string
  }>>([])
  // 笔记编辑抽屉
  const [editingNote, setEditingNote] = useState<{
    id: string
    date: string
    type: 'cornell' | 'notes' | 'feynman' | 'other'
    title: string
    cues?: string
    notes?: string
    summary?: string
    content?: string
  } | null>(null)
  const [editDrawerOpen, setEditDrawerOpen] = useState(false)
  const [savingEdit, setSavingEdit] = useState(false)
  const studentId = useAppStore((s) => s.studentId)

  // 同步 URL 中的 tab 参数到激活 Tab
  useEffect(() => {
    const t = searchParams.get('tab')
    if (t && t !== activeTab) setActiveTab(t)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams])

  useEffect(() => {
    const load = async () => {
      if (!studentId) return
      // 8 个独立接口并发拉取，单个失败不影响其它（fallback 到 null）
      const [pRes, dRes, ptRes, aRes, hRes, thRes, fRes, rRes] = await Promise.all([
        profileApi.get(studentId).catch(() => null),
        dashboardApi.getSummary(studentId).catch(() => null),
        gamificationApi.getPoints(studentId).catch(() => null),
        gamificationApi.getAchievements(studentId).catch(() => null),
        learningDataApi.getHistory(studentId, 200).catch(() => null),
        trendApi.getHistory(studentId, 7).catch(() => null),
        favoritesApi.get(studentId).catch(() => null),
        logReflectionApi.getReflections(studentId, 100).catch(() => null),
      ])

      try {
        if (pRes?.data?.data) setProfile(pRes.data.data)
        if (dRes?.data) setDashboardStats(dRes.data as unknown as Record<string, unknown>)
        if (ptRes?.data?.data) setPoints(ptRes.data.data)
        if (aRes?.data?.data) setAchievements(aRes.data.data)

        const recordsRaw = (hRes?.data?.records as unknown as Record<string, unknown>[]) || []
        const quizzesRaw = (hRes?.data?.quizzes as unknown as Record<string, unknown>[]) || []

        // 最近列表（前 5 条）展示
        if (recordsRaw.length) {
          const mapped = recordsRaw.slice(0, 5).map((r) => ({
            title: `${r.action || '学习'} ${r.kp_id || ''}`,
            time: r.created_at ? new Date(String(r.created_at)).toLocaleString() : '近期',
            type: String(r.action || '').includes('代码') ? 'code' : String(r.action || '').includes('测验') ? 'quiz' : 'doc',
          }))
          setLearningHistory(mapped)
        }

        // ---- 周专注度&时长聚合（最近 7 天）----
        const dayKeys: string[] = []
        const today = new Date()
        for (let i = 6; i >= 0; i--) {
          const d = new Date(today)
          d.setDate(today.getDate() - i)
          dayKeys.push(d.toISOString().slice(0, 10))
        }
        const dayLabels = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
        const focusAgg: Record<string, { progressSum: number; count: number; durationSum: number; quizScoreSum: number; quizCount: number; pomodoros: number }> = {}
        dayKeys.forEach((d) => { focusAgg[d] = { progressSum: 0, count: 0, durationSum: 0, quizScoreSum: 0, quizCount: 0, pomodoros: 0 } })
        let totalPomodoros = 0
        recordsRaw.forEach((r) => {
          const dateStr = String(r.created_at || '').slice(0, 10)
          const dur = Number(r.duration) || 0
          const action = String(r.action || '')
          const isPomodoro = dur >= 20 * 60 || action === 'complete' || action === 'practice' || action === 'quiz'
          if (isPomodoro) totalPomodoros += 1
          if (focusAgg[dateStr]) {
            focusAgg[dateStr].progressSum += Number(r.progress) || 0
            focusAgg[dateStr].count += 1
            focusAgg[dateStr].durationSum += dur
            if (isPomodoro) focusAgg[dateStr].pomodoros += 1
          }
        })
        quizzesRaw.forEach((q) => {
          const dateStr = String(q.created_at || '').slice(0, 10)
          if (focusAgg[dateStr]) {
            focusAgg[dateStr].quizScoreSum += Number(q.score) || 0
            focusAgg[dateStr].quizCount += 1
          }
        })

        // ---- 趋势历史（驱动专注度折线）----
        const trendByDate: Record<string, number> = {}
        const trendList = (thRes?.data?.data as Array<{ date: string; trend_factor: number }> | undefined) || []
        trendList.forEach((tp) => {
          const f = Math.max(-1, Math.min(1, Number(tp.trend_factor) || 0))
          trendByDate[String(tp.date).slice(0, 10)] = Math.round((f + 1) * 50)
        })

        const aggregated: FocusItem[] = dayKeys.map((d) => {
          const agg = focusAgg[d]
          let focus = 0
          if (trendByDate[d] !== undefined) {
            focus = trendByDate[d]
          } else if (agg.quizCount > 0) {
            focus = Math.round(agg.quizScoreSum / agg.quizCount)
          } else if (agg.count > 0) {
            focus = Math.round((agg.progressSum / agg.count) * 100)
          }
          return {
            day: dayLabels[new Date(d).getDay()],
            focus: Math.max(0, Math.min(100, focus)),
            duration: Math.round(agg.durationSum / 60),
          }
        })
        if (aggregated.some((a) => a.focus > 0 || a.duration > 0)) {
          setFocusData(aggregated)
        }

        // ---- 番茄钟统计 ----
        const todayKey = dayKeys[dayKeys.length - 1]
        const todayPomos = focusAgg[todayKey]?.pomodoros || 0
        let streak = 0
        for (let i = dayKeys.length - 1; i >= 0; i--) {
          if ((focusAgg[dayKeys[i]]?.pomodoros || 0) > 0) streak += 1
          else break
        }
        setPomodoroStats({ total: totalPomodoros, today: todayPomos, streak })

        // ---- 待复习知识点 ----
        const weakList: string[] = (pRes?.data?.data?.weak_areas as string[] | undefined) || []
        const tagScoreMap: Record<string, { sum: number; n: number }> = {}
        quizzesRaw.forEach((q) => {
          const tags = (q.weak_tags as string[] | undefined) || []
          const score = Number(q.score) || 0
          tags.forEach((t) => {
            if (!tagScoreMap[t]) tagScoreMap[t] = { sum: 0, n: 0 }
            tagScoreMap[t].sum += score
            tagScoreMap[t].n += 1
          })
        })
        if (weakList.length) {
          const reviews: ReviewTopic[] = weakList.slice(0, 6).map((w, i) => {
            const stat = tagScoreMap[w]
            const baseRetention = stat && stat.n > 0
              ? Math.round(stat.sum / stat.n)
              : Math.max(30, 70 - i * 8)
            const retention = Math.max(20, Math.min(95, baseRetention))
            const nextReview = retention < 50 ? '今天' : retention < 70 ? '明天' : '3天后'
            return { topic: w, retention, nextReview }
          })
          setReviewTopics(reviews)
        }

        // Favorites
        if (fRes?.data?.data) setFavorites(fRes.data.data as FavoriteItem[])

        // Reflections
        if (rRes?.data?.data) {
          const all = rRes.data.data as Record<string, unknown>[]
          const refs = all
            .filter((r) => {
              const tags = String(r.tags || '')
              return !tags.includes('cornell') && !tags.includes('feynman') && !tags.includes('notes')
            })
            .map((r) => ({
              id: String(r.reflection_id || `ref_${Date.now()}`),
              date: String(r.date || ''),
              content: String(r.content || ''),
              topic: (r.tags as string[])?.[0] || '今日学习',
            }))
          setReflections(refs)

          const cornellList = all.filter((r) => (r.tags as string[] | undefined)?.includes('cornell'))
          const cornell = cornellList[0]
          if (cornell) {
            try {
              setCornellNotes(JSON.parse(String(cornell.content)))
            } catch {
              setCornellNotes({ cues: String(cornell.content), notes: '', summary: '' })
            }
          }
          const feynman = all.find((r) => (r.tags as string[] | undefined)?.includes('feynman'))
          if (feynman) setFeynmanInput(String(feynman.content))

          const noteEntries = all
            .filter((r) => {
              const tags = (r.tags as string[] | undefined) || []
              return tags.includes('cornell') || tags.includes('notes') || tags.includes('feynman')
            })
            .map((r) => {
              const tags = (r.tags as string[] | undefined) || []
              const isCornell = tags.includes('cornell')
              const isFeynman = tags.includes('feynman')
              const kpTag = tags.find((t) => t && t !== 'cornell' && t !== 'notes' && t !== 'feynman')
              const rawContent = String(r.content || '')
              let preview = rawContent
              let title = isCornell ? '康奈尔笔记' : isFeynman ? '费曼练习' : '学习笔记'
              if (isCornell) {
                try {
                  const parsed = JSON.parse(rawContent) as { cues?: string; notes?: string; summary?: string }
                  preview = [parsed.summary, parsed.notes, parsed.cues].filter(Boolean).join('\n')
                } catch {
                  // 保留原文
                }
              }
              if (kpTag) title += ` · ${kpTag}`
              const type: 'cornell' | 'notes' | 'feynman' = isCornell ? 'cornell' : isFeynman ? 'feynman' : 'notes'
              return {
                id: String(r.reflection_id || `note_${Date.now()}_${Math.random()}`),
                date: String(r.date || ''),
                type,
                title,
                content: preview,
                rawContent,
              }
            })
            .sort((a, b) => (a.date > b.date ? -1 : 1))
          setNotesHistory(noteEntries)
        }

        // ---- 趋势分析（POST /trend/analyze 是写操作，不并发，放在最后单独跑）----
        try {
          const tRes = await trendApi.analyze(studentId)
          const td = tRes.data?.data as Record<string, unknown> | undefined
          if (td) {
            setTrendInfo({
              state: String(td.trend_state || 'stable'),
              factor: Number(td.trend_factor) || 0,
              dimensions: (td.dimensions as Record<string, number>) || {},
              intervention: String(td.intervention || ''),
            })
          }
        } catch {
          // 趋势分析失败时静默
        }
      } catch {
        // 静默处理聚合错误
      }
    }
    load()
  }, [studentId])

  const weakAreas = profile?.weak_areas || []
  const cognitivePrimary = profile?.cognitive_style?.primary || 'visual'
  const studySpeed = profile?.learning_tempo?.study_speed || 'moderate'

  const handleAddReflection = async () => {
    if (!newReflection.trim()) return
    try {
      const today = new Date().toISOString().slice(0, 10)
      await logReflectionApi.createReflection({
        student_id: studentId,
        date: today,
        content: newReflection.trim(),
        mood: 'neutral',
        tags: ['今日学习'],
      })
      const entry: ReflectionEntry = {
        id: `ref_${studentId}_${today}_${Date.now()}`,
        date: today,
        content: newReflection.trim(),
        topic: '今日学习',
      }
      setReflections([entry, ...reflections])
      setNewReflection('')
      message.success('反思已保存')
    } catch (e) {
      message.error('保存失败')
    }
  }

  const handleSaveCornell = async () => {
    try {
      const today = new Date().toISOString().slice(0, 10)
      const rawContent = JSON.stringify(cornellNotes)
      const res = await logReflectionApi.createReflection({
        student_id: studentId,
        date: today,
        content: rawContent,
        tags: ['cornell'],
      })
      const newId = String(res.data?.reflection_id || `note_${Date.now()}`)
      const preview = [cornellNotes.summary, cornellNotes.notes, cornellNotes.cues].filter(Boolean).join('\n')
      setNotesHistory((prev) => [
        { id: newId, date: today, type: 'cornell', title: '康奈尔笔记', content: preview, rawContent },
        ...prev,
      ])
      message.success('康奈尔笔记已保存')
    } catch (e) {
      message.error('保存失败')
    }
  }

  const handleSaveFeynman = async () => {
    if (!feynmanInput.trim()) return
    try {
      const today = new Date().toISOString().slice(0, 10)
      const res = await logReflectionApi.createReflection({
        student_id: studentId,
        date: today,
        content: feynmanInput.trim(),
        tags: ['feynman'],
      })
      const newId = String(res.data?.reflection_id || `note_${Date.now()}`)
      setNotesHistory((prev) => [
        { id: newId, date: today, type: 'feynman', title: '费曼练习', content: feynmanInput.trim() },
        ...prev,
      ])
      message.success('费曼练习已保存')
      setFeynmanInput('')
    } catch (e) {
      message.error('保存失败')
    }
  }

  // 打开笔记编辑抽屉
  const handleOpenNoteEdit = (n: { id: string; date: string; type: 'cornell' | 'notes' | 'feynman' | 'other'; title: string; content: string; rawContent?: string }) => {
    if (n.type === 'cornell') {
      // 优先用 rawContent 解析三段
      let cues = ''
      let notes = n.content
      let summary = ''
      if (n.rawContent) {
        try {
          const parsed = JSON.parse(n.rawContent) as { cues?: string; notes?: string; summary?: string }
          cues = parsed.cues || ''
          notes = parsed.notes || ''
          summary = parsed.summary || ''
        } catch {
          notes = n.rawContent
        }
      }
      setEditingNote({
        id: n.id,
        date: n.date,
        type: 'cornell',
        title: n.title,
        cues,
        notes,
        summary,
      })
    } else {
      setEditingNote({
        id: n.id,
        date: n.date,
        type: n.type,
        title: n.title,
        content: n.content,
      })
    }
    setEditDrawerOpen(true)
  }

  // 保存笔记编辑
  const handleSaveNoteEdit = async () => {
    if (!editingNote) return
    setSavingEdit(true)
    try {
      let content = ''
      let preview = ''
      if (editingNote.type === 'cornell') {
        const obj = {
          cues: editingNote.cues || '',
          notes: editingNote.notes || '',
          summary: editingNote.summary || '',
        }
        content = JSON.stringify(obj)
        preview = [obj.summary, obj.notes, obj.cues].filter(Boolean).join('\n')
      } else {
        content = editingNote.content || ''
        preview = content
      }
      await logReflectionApi.updateReflection(editingNote.id, { content })
      setNotesHistory((prev) => prev.map((it) => it.id === editingNote.id
        ? { ...it, content: preview, rawContent: content }
        : it))
      // 同步反思列表（若编辑的是反思项）
      if (editingNote.type === 'other') {
        setReflections((prev) => prev.map((it) => it.id === editingNote.id
          ? { ...it, content: preview }
          : it))
      }
      // 若编辑的是当前最新 cornell，同步更新主编辑器
      if (editingNote.type === 'cornell') {
        setCornellNotes({
          cues: editingNote.cues || '',
          notes: editingNote.notes || '',
          summary: editingNote.summary || '',
        })
      } else if (editingNote.type === 'feynman') {
        setFeynmanInput(editingNote.content || '')
      }
      message.success('已更新')
      setEditDrawerOpen(false)
      setEditingNote(null)
    } catch (e) {
      message.error('更新失败')
    } finally {
      setSavingEdit(false)
    }
  }

  // 删除笔记
  const handleDeleteNote = async () => {
    if (!editingNote) return
    setSavingEdit(true)
    try {
      await logReflectionApi.deleteReflection(editingNote.id)
      setNotesHistory((prev) => prev.filter((it) => it.id !== editingNote.id))
      // 同步从反思列表移除（如果在反思列表里）
      setReflections((prev) => prev.filter((it) => it.id !== editingNote.id))
      message.success('已删除')
      setEditDrawerOpen(false)
      setEditingNote(null)
    } catch (e) {
      message.error('删除失败')
    } finally {
      setSavingEdit(false)
    }
  }

  // 打开反思编辑（复用同一抽屉，type='other'）
  const handleOpenReflectionEdit = (r: ReflectionEntry) => {
    setEditingNote({
      id: r.id,
      date: r.date,
      type: 'other',
      title: r.topic || '反思',
      content: r.content,
    })
    setEditDrawerOpen(true)
  }

  const handleFavoriteClick = (item: FavoriteItem) => {
    if (item.resource_type === 'code' || item.resource_type === 'document' || item.resource_type === 'doc') {
      navigate(`/resources?topic=${encodeURIComponent(item.title)}`)
    } else {
      message.info('该资源暂无详情页')
    }
  }

  const statsRecord = (dashboardStats?.stats || {}) as Record<string, unknown>
  const statCardsData = [
    {
      title: '累计学习时长',
      value: Math.round((Number(statsRecord.weekly_hours) || 0) * 10) / 10,
      suffix: 'h',
      color: '#4f46e5',
      icon: <ClockCircleOutlined />,
    },
    {
      title: '最长连续打卡',
      value: Number(statsRecord.streak_days) || 0,
      suffix: '天',
      color: '#f59e0b',
      icon: <FireOutlined />,
    },
    {
      title: '获得勋章',
      value: achievements.filter((a) => a.unlocked_at).length,
      suffix: '枚',
      color: '#10b981',
      icon: <TrophyOutlined />,
    },
    {
      title: '收藏资源',
      value: favorites.length,
      suffix: '个',
      color: '#ec4899',
      icon: <HeartOutlined />,
    },
  ]

  const defaultBadges = [
    { id: '1', name: '初出茅庐', desc: '完成首次学习', icon: <StarOutlined />, color: '#f59e0b' },
    { id: '2', name: '代码能手', desc: '完成5次代码实操', icon: <CodeOutlined />, color: '#3b82f6' },
    { id: '3', name: '学习王者', desc: '连续打卡30天', icon: <CrownOutlined />, color: '#ef4444' },
    { id: '4', name: '全勤标兵', desc: '连续7天完成每日挑战', icon: <FireOutlined />, color: '#10b981' },
    { id: '5', name: '思维导图', desc: '生成10张思维导图', icon: <ApartmentOutlined />, color: '#8b5cf6' },
    { id: '6', name: '提问达人', desc: '向AI辅导提问50次', icon: <MessageOutlined />, color: '#0ea5e9' },
    { id: '7', name: '知识探索者', desc: '完成全部基础章节', icon: <BulbOutlined />, color: '#f59e0b' },
    { id: '8', name: '完美通过', desc: '测验全部满分', icon: <CheckCircleOutlined />, color: '#10b981' },
  ]

  const badgeList = defaultBadges.map((db) => {
    const unlocked = achievements.find((a) => a.name === db.name)
    return { ...db, unlocked: !!unlocked, unlocked_at: unlocked?.unlocked_at }
  })

  const weekFocus = focusData.length
    ? focusData
    : (() => {
        // 没数据时也铺满 7 天（按今天往前推），全部 0，避免出现假数据
        const labels = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
        const out: FocusItem[] = []
        const t = new Date()
        for (let i = 6; i >= 0; i--) {
          const d = new Date(t)
          d.setDate(t.getDate() - i)
          out.push({ day: labels[d.getDay()], focus: 0, duration: 0 })
        }
        return out
      })()

  return (
    <div className="space-y-6">
      <Row gutter={[20, 20]}>
        {statCardsData.map((stat, idx) => (
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
        activeKey={activeTab}
        onChange={(k) => {
          setActiveTab(k)
          if (k === 'history') {
            searchParams.delete('tab')
          } else {
            searchParams.set('tab', k)
          }
          setSearchParams(searchParams, { replace: true })
        }}
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
                          <LineChart data={weekFocus}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                            <XAxis dataKey="day" tick={{ fill: '#64748b' }} axisLine={false} tickLine={false} />
                            <YAxis domain={[0, 100]} tick={{ fill: '#64748b' }} axisLine={false} tickLine={false} />
                            <Tooltip
                              contentStyle={{ borderRadius: 12, border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.06)' }}
                              cursor={{ stroke: '#e2e8f0', strokeWidth: 2 }}
                            />
                            <Line
                              type="monotone"
                              dataKey="focus"
                              stroke="#4f46e5"
                              strokeWidth={3}
                              dot={{ fill: '#4f46e5', r: 4 }}
                              activeDot={{ r: 6, fill: '#fff', stroke: '#4f46e5', strokeWidth: 2 }}
                            />
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
                          <BarChart data={weekFocus}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                            <XAxis dataKey="day" tick={{ fill: '#64748b' }} axisLine={false} tickLine={false} />
                            <YAxis tick={{ fill: '#64748b' }} axisLine={false} tickLine={false} />
                            <Tooltip
                              contentStyle={{ borderRadius: 12, border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.06)' }}
                              cursor={{ fill: '#f8fafc' }}
                            />
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
                    dataSource={
                      learningHistory.length
                        ? learningHistory
                        : [{ title: '暂无学习记录', time: '-', type: 'doc' }]
                    }
                    renderItem={(item: HistoryItem) => {
                      const meta = typeMeta[item.type] || typeMeta.doc
                      return (
                        <List.Item className="hover:bg-slate-50 rounded-xl transition-colors px-2">
                          <List.Item.Meta
                            avatar={
                              <Avatar
                                icon={meta.icon}
                                style={{
                                  background: meta.bg,
                                  color: meta.color,
                                  border: `1px solid ${meta.color}15`,
                                }}
                              />
                            }
                            title={
                              <Typography.Text className="text-slate-700 font-medium text-sm">
                                {item.title}
                              </Typography.Text>
                            }
                            description={
                              <Space>
                                <Tag className="rounded-full text-xs border-0 bg-slate-100 text-slate-500">
                                  {meta.label}
                                </Tag>
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
                  {favorites.length ? (
                    favorites.map((item, idx: number) => (
                      <Col xs={24} sm={12} lg={8} key={item.id || idx}>
                        <div
                          className="p-5 rounded-xl bg-slate-50 hover:bg-white hover:shadow-card transition-all cursor-pointer border border-slate-100 hover:border-slate-200"
                          onClick={() => handleFavoriteClick(item)}
                        >
                          <Space align="start">
                            <div
                              className="w-10 h-10 rounded-lg flex items-center justify-center text-white text-lg shrink-0"
                              style={{ background: typeMeta[item.resource_type]?.color || '#64748b' }}
                            >
                              {typeMeta[item.resource_type]?.icon || <FileTextOutlined />}
                            </div>
                            <div>
                              <Typography.Text className="font-medium text-slate-800 block">
                                {item.title}
                              </Typography.Text>
                              <span className="text-xs text-slate-400 mt-0.5 block">
                                {item.resource_type}
                              </span>
                            </div>
                          </Space>
                        </div>
                      </Col>
                    ))
                  ) : (
                    <Col span={24}>
                      <div className="text-slate-400 text-sm">暂无收藏资源</div>
                    </Col>
                  )}
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
                    已解锁 {badgeList.filter((b) => b.unlocked).length} / {badgeList.length}
                  </Tag>
                </div>
                <Row gutter={[20, 20]}>
                  {badgeList.map((badge: BadgeItemLocal) => (
                    <Col xs={12} sm={8} lg={6} key={badge.id}>
                      <div
                        className={`flex flex-col items-center gap-3 p-5 rounded-xl border transition-all ${
                          badge.unlocked
                            ? 'bg-white border-slate-100 hover:shadow-card'
                            : 'bg-slate-50 border-slate-100 opacity-50'
                        }`}
                      >
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
                        {badge.unlocked && (
                          <Tag className="rounded-full border-0 bg-emerald-50 text-emerald-600 text-xs">
                            已解锁
                          </Tag>
                        )}
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
                    {reflections.length ? (
                      reflections.map((r) => (
                        <div
                          key={r.id}
                          className="p-4 rounded-xl bg-slate-50 border border-slate-100 hover:border-primary/30 hover:bg-white hover:shadow-card transition-all cursor-pointer"
                          onClick={() => handleOpenReflectionEdit(r)}
                        >
                          <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center gap-2">
                              <Tag className="rounded-full border-0 bg-primary-50 text-primary text-xs">
                                {r.topic}
                              </Tag>
                              <span className="text-xs text-slate-400">{r.date}</span>
                            </div>
                            <span className="text-xs text-primary opacity-70">点击编辑</span>
                          </div>
                          <Typography.Text className="text-slate-700 text-sm leading-relaxed block">
                            {r.content}
                          </Typography.Text>
                        </div>
                      ))
                    ) : (
                      <div className="text-slate-400 text-sm">暂无反思记录</div>
                    )}
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
                      <Input.TextArea
                        rows={10}
                        placeholder="记录关键词、问题..."
                        value={cornellNotes.cues}
                        onChange={(e) => setCornellNotes({ ...cornellNotes, cues: e.target.value })}
                        className="rounded-xl bg-slate-50 border-slate-200"
                      />
                    </div>
                    <div className="col-span-2 space-y-2">
                      <div className="text-xs font-medium text-slate-500">笔记栏 (Notes)</div>
                      <Input.TextArea
                        rows={10}
                        placeholder="记录课堂/阅读笔记..."
                        value={cornellNotes.notes}
                        onChange={(e) => setCornellNotes({ ...cornellNotes, notes: e.target.value })}
                        className="rounded-xl bg-slate-50 border-slate-200"
                      />
                    </div>
                  </div>
                  <div className="mt-4 space-y-2">
                    <div className="text-xs font-medium text-slate-500">总结栏 (Summary)</div>
                    <Input.TextArea
                      rows={3}
                      placeholder="用一句话总结本页核心内容..."
                      value={cornellNotes.summary}
                      onChange={(e) => setCornellNotes({ ...cornellNotes, summary: e.target.value })}
                      className="rounded-xl bg-slate-50 border-slate-200"
                    />
                  </div>
                  <Button type="primary" className="rounded-lg bg-primary mt-4" onClick={handleSaveCornell}>
                    <CheckCircleOutlined /> 保存康奈尔笔记
                  </Button>
                </div>

                {/* 笔记时间线（汉堡折叠） */}
                <div className="bg-white rounded-2xl border border-slate-100 p-2">
                  <Collapse
                    ghost
                    expandIcon={({ isActive }) => <CaretRightOutlined rotate={isActive ? 90 : 0} />}
                    items={[
                      {
                        key: 'notes-timeline',
                        label: (
                          <div className="flex items-center justify-between w-full pr-4">
                            <span className="font-semibold text-slate-800">
                              <FileTextOutlined className="mr-2 text-primary" />
                              我的笔记时间线
                            </span>
                            <Tag className="rounded-full border-0 bg-primary-50 text-primary text-xs">
                              {notesHistory.length} 条
                            </Tag>
                          </div>
                        ),
                        children: (
                          <div className="space-y-3 max-h-[480px] overflow-y-auto px-2 pb-2">
                            {notesHistory.length ? (
                              notesHistory.map((n) => (
                                <div
                                  key={n.id}
                                  className="p-4 rounded-xl bg-slate-50 border border-slate-100 hover:border-primary/30 hover:bg-white hover:shadow-card transition-all cursor-pointer"
                                  onClick={() => handleOpenNoteEdit(n)}
                                >
                                  <div className="flex items-center justify-between mb-2">
                                    <div className="flex items-center gap-2">
                                      <Tag
                                        className={`rounded-full border-0 text-xs ${
                                          n.type === 'cornell'
                                            ? 'bg-purple-50 text-purple-600'
                                            : n.type === 'feynman'
                                            ? 'bg-amber-50 text-amber-600'
                                            : 'bg-emerald-50 text-emerald-600'
                                        }`}
                                      >
                                        {n.title}
                                      </Tag>
                                    </div>
                                    <Space>
                                      <span className="text-xs text-slate-400">{n.date}</span>
                                      <span className="text-xs text-primary opacity-70">点击编辑</span>
                                    </Space>
                                  </div>
                                  <Typography.Paragraph
                                    className="text-slate-700 text-sm leading-relaxed !mb-0 whitespace-pre-wrap"
                                    ellipsis={{ rows: 4, expandable: false }}
                                  >
                                    {n.content || '（无内容）'}
                                  </Typography.Paragraph>
                                </div>
                              ))
                            ) : (
                              <div className="text-slate-400 text-sm py-6 text-center">暂无笔记，保存后会按时间顺序列在这里</div>
                            )}
                          </div>
                        ),
                      },
                    ]}
                  />
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
                    <strong>费曼技巧：</strong>
                    选择你要学习的概念，尝试用最简单的语言向一个"小孩"解释它。如果你卡住了，就回到材料中重新学习，然后再次尝试简化。
                  </div>
                  <Input.TextArea
                    rows={6}
                    placeholder="用你自己的话，尝试向一个外行解释最近学到的知识点..."
                    value={feynmanInput}
                    onChange={(e) => setFeynmanInput(e.target.value)}
                    className="rounded-xl bg-slate-50 border-slate-200 mb-3"
                  />
                  <Button type="primary" className="rounded-lg bg-primary" onClick={handleSaveFeynman}>
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
                          <LineChart
                            data={[
                              { day: '1天', memory: 100 },
                              { day: '2天', memory: 55 },
                              { day: '3天', memory: 42 },
                              { day: '5天', memory: 35 },
                              { day: '8天', memory: 30 },
                              { day: '15天', memory: 25 },
                              { day: '30天', memory: 20 },
                            ]}
                          >
                            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                            <XAxis
                              dataKey="day"
                              tick={{ fill: '#64748b', fontSize: 11 }}
                              axisLine={false}
                              tickLine={false}
                            />
                            <YAxis domain={[0, 100]} tick={{ fill: '#64748b' }} axisLine={false} tickLine={false} />
                            <Tooltip
                              contentStyle={{ borderRadius: 12, border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.06)' }}
                            />
                            <Line
                              type="monotone"
                              dataKey="memory"
                              name="理论记忆保留率"
                              stroke="#ef4444"
                              strokeWidth={2}
                              dot={{ r: 3 }}
                              strokeDasharray="5 5"
                            />
                          </LineChart>
                        </ResponsiveContainer>
                      </div>
                    </div>
                  </Col>
                  <Col xs={24} lg={12}>
                    <div className="bg-white rounded-2xl border border-slate-100 p-6">
                      <div className="font-semibold text-slate-800 mb-4">待复习知识点</div>
                      <div className="space-y-3">
                        {reviewTopics.length ? (
                          reviewTopics.map((item: ReviewTopic) => (
                            <div
                              key={item.topic}
                              className="flex items-center gap-3 p-3 rounded-xl bg-slate-50 border border-slate-100"
                            >
                              <div className="flex-1">
                                <div className="text-sm font-medium text-slate-800">{item.topic}</div>
                                <div className="text-xs text-slate-400">下次复习: {item.nextReview}</div>
                              </div>
                              <div className="w-20">
                                <Progress
                                  percent={item.retention}
                                  size="small"
                                  strokeColor={
                                    item.retention > 70
                                      ? '#10b981'
                                      : item.retention > 50
                                      ? '#f59e0b'
                                      : '#ef4444'
                                  }
                                  trailColor="#f1f5f9"
                                  showInfo={false}
                                />
                              </div>
                              <Tag
                                className={`rounded-full border-0 text-xs ${
                                  item.retention > 70
                                    ? 'bg-emerald-50 text-emerald-600'
                                    : item.retention > 50
                                    ? 'bg-amber-50 text-amber-600'
                                    : 'bg-red-50 text-red-600'
                                }`}
                              >
                                {item.retention}%
                              </Tag>
                            </div>
                          ))
                        ) : (
                          <div className="text-slate-400 text-sm">暂无薄弱知识点</div>
                        )}
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
                <Typography.Title level={5} className="mb-5 font-semibold text-slate-800">
                  画像数据解读
                </Typography.Title>
                <div className="space-y-4 text-slate-600 leading-relaxed">
                  {/* 趋势状态卡片 */}
                  {trendInfo && (
                    <div
                      className={`p-4 rounded-xl border flex items-start gap-3 ${
                        trendInfo.state === 'growth'
                          ? 'bg-emerald-50 border-emerald-100 text-emerald-700'
                          : trendInfo.state === 'warning'
                          ? 'bg-red-50 border-red-100 text-red-700'
                          : trendInfo.state === 'decline'
                          ? 'bg-amber-50 border-amber-100 text-amber-700'
                          : 'bg-slate-50 border-slate-100 text-slate-600'
                      }`}
                    >
                      {trendInfo.state === 'growth' ? (
                        <RiseOutlined className="text-xl mt-1" />
                      ) : trendInfo.state === 'warning' ? (
                        <AlertOutlined className="text-xl mt-1" />
                      ) : trendInfo.state === 'decline' ? (
                        <FallOutlined className="text-xl mt-1" />
                      ) : (
                        <BulbOutlined className="text-xl mt-1" />
                      )}
                      <div className="flex-1">
                        <div className="font-semibold mb-1">
                          趋势状态：
                          {trendInfo.state === 'growth' ? '上升期' : trendInfo.state === 'warning' ? '预警' : trendInfo.state === 'decline' ? '下滑期' : '平稳期'}
                          <span className="ml-2 text-xs opacity-70">趋势因子 {trendInfo.factor.toFixed(2)}</span>
                        </div>
                        <div className="text-sm leading-relaxed">{trendInfo.intervention || '暂无干预建议'}</div>
                      </div>
                    </div>
                  )}

                  <div className="p-5 rounded-xl bg-slate-50 border border-slate-100">
                    <p className="mb-2">
                      <strong className="text-slate-800">认知风格：</strong> 你的主要认知风格为{' '}
                      <Tag className="rounded-full border-0 bg-purple-50 text-purple-600">
                        {cognitivePrimary}
                      </Tag>
                      ，系统会优先推送
                      {cognitivePrimary === 'visual'
                        ? '图表与动画类资源（内存模型图、指针示意图）'
                        : cognitivePrimary === 'auditory'
                        ? '讲解视频与对话式讲义'
                        : cognitivePrimary === 'kinesthetic'
                        ? '代码实战与可交互练习'
                        : '多模态混合资源'}
                      。
                    </p>
                    <p className="mb-2">
                      <strong className="text-slate-800">学习节奏：</strong> 当前学习节奏评估为{' '}
                      <Tag className="rounded-full border-0 bg-blue-50 text-blue-600">{studySpeed}</Tag>
                      {trendInfo?.dimensions?.speed_ratio !== undefined && (
                        <span className="text-xs text-slate-500 ml-1">
                          （速度比 {trendInfo.dimensions.speed_ratio.toFixed(2)}
                          {trendInfo.dimensions.speed_ratio > 0.2 ? ' · 偏快' : trendInfo.dimensions.speed_ratio < -0.2 ? ' · 偏慢' : ' · 适中'}
                          ）
                        </span>
                      )}
                      ，系统在推荐内容时会自动调整讲解深度与练习量。
                    </p>
                    <p className="mb-2">
                      <strong className="text-slate-800">薄弱点：</strong>{' '}
                      {weakAreas.length ? weakAreas.join('、') : '暂无明显薄弱点'}
                      {trendInfo?.dimensions?.weakness_priority !== undefined && (
                        <span className="text-xs text-slate-500 ml-1">
                          （优先级得分 {trendInfo.dimensions.weakness_priority.toFixed(2)}
                          {trendInfo.dimensions.weakness_priority < -0.2 ? ' · 需重点关注' : ''}
                          ）
                        </span>
                      )}
                      {weakAreas.length ? '，系统已自动增加相关练习推送和可视化讲解。' : '。'}
                    </p>
                    {trendInfo?.dimensions?.completion_rate !== undefined && (
                      <p className="mb-2">
                        <strong className="text-slate-800">完成率：</strong>{' '}
                        <Tag className="rounded-full border-0 bg-amber-50 text-amber-600">
                          {(trendInfo.dimensions.completion_rate >= 0.4
                            ? '高'
                            : trendInfo.dimensions.completion_rate >= -0.2
                            ? '中'
                            : '偏低')}
                        </Tag>
                        （得分 {trendInfo.dimensions.completion_rate.toFixed(2)}）
                        {trendInfo.dimensions.completion_rate < -0.2
                          ? '，建议浏览过的章节尽量点击「标记完成」并配合练习。'
                          : trendInfo.dimensions.completion_rate >= 0.4
                          ? '，保持当前节奏，可挑战更高难度的综合题。'
                          : '，可以结合练习巩固已学内容。'}
                      </p>
                    )}
                    {trendInfo?.dimensions?.stability !== undefined && (
                      <p className="mb-2">
                        <strong className="text-slate-800">学习稳定性：</strong>{' '}
                        <Tag className="rounded-full border-0 bg-slate-100 text-slate-600">
                          {trendInfo.dimensions.stability >= 0.2 ? '稳定' : trendInfo.dimensions.stability >= -0.2 ? '一般' : '波动较大'}
                        </Tag>
                        （得分 {trendInfo.dimensions.stability.toFixed(2)}）
                      </p>
                    )}
                    <p>
                      <strong className="text-slate-800">兴趣方向：</strong>{' '}
                      {profile?.interest_areas?.length
                        ? profile.interest_areas.join('、')
                        : 'C语言程序设计与系统开发'}。
                    </p>
                  </div>
                </div>
                <Button
                  type="primary"
                  className="mt-5 rounded-lg bg-primary"
                  onClick={() => navigate('/profile')}
                >
                  手动修正画像
                </Button>
              </div>
            ),
          },
        ]}
      />

      {/* 笔记编辑抽屉 */}
      <Drawer
        title={editingNote ? `编辑${editingNote.title}` : '编辑笔记'}
        placement="right"
        width={520}
        open={editDrawerOpen}
        onClose={() => { setEditDrawerOpen(false); setEditingNote(null) }}
        extra={
          editingNote && (
            <Popconfirm
              title="确定删除这条笔记吗？"
              description="删除后无法恢复"
              okText="删除"
              cancelText="取消"
              okButtonProps={{ danger: true }}
              onConfirm={handleDeleteNote}
            >
              <Button danger icon={<DeleteOutlined />} loading={savingEdit}>删除</Button>
            </Popconfirm>
          )
        }
        footer={
          <div className="flex justify-end gap-2">
            <Button onClick={() => { setEditDrawerOpen(false); setEditingNote(null) }}>取消</Button>
            <Button type="primary" loading={savingEdit} onClick={handleSaveNoteEdit} className="bg-primary">
              保存修改
            </Button>
          </div>
        }
      >
        {editingNote && (
          <div className="space-y-4">
            <div className="text-xs text-slate-400">日期：{editingNote.date}</div>
            {editingNote.type === 'cornell' ? (
              <>
                <div className="space-y-2">
                  <div className="text-xs font-medium text-slate-500">线索栏 (Cues)</div>
                  <Input.TextArea
                    rows={4}
                    value={editingNote.cues || ''}
                    onChange={(e) => setEditingNote({ ...editingNote, cues: e.target.value })}
                    placeholder="关键词、问题..."
                    className="rounded-xl bg-slate-50 border-slate-200"
                  />
                </div>
                <div className="space-y-2">
                  <div className="text-xs font-medium text-slate-500">笔记栏 (Notes)</div>
                  <Input.TextArea
                    rows={10}
                    value={editingNote.notes || ''}
                    onChange={(e) => setEditingNote({ ...editingNote, notes: e.target.value })}
                    placeholder="课堂/阅读笔记..."
                    className="rounded-xl bg-slate-50 border-slate-200"
                  />
                </div>
                <div className="space-y-2">
                  <div className="text-xs font-medium text-slate-500">总结栏 (Summary)</div>
                  <Input.TextArea
                    rows={3}
                    value={editingNote.summary || ''}
                    onChange={(e) => setEditingNote({ ...editingNote, summary: e.target.value })}
                    placeholder="一句话总结..."
                    className="rounded-xl bg-slate-50 border-slate-200"
                  />
                </div>
              </>
            ) : (
              <div className="space-y-2">
                <div className="text-xs font-medium text-slate-500">
                  {editingNote.type === 'feynman' ? '费曼练习内容' : '笔记内容'}
                </div>
                <Input.TextArea
                  rows={14}
                  value={editingNote.content || ''}
                  onChange={(e) => setEditingNote({ ...editingNote, content: e.target.value })}
                  className="rounded-xl bg-slate-50 border-slate-200"
                />
              </div>
            )}
          </div>
        )}
      </Drawer>
    </div>
  )
}

export default PersonalSpace
