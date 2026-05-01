import React, { useEffect, useState, useMemo, useRef, useCallback } from 'react'
import { Typography, Card, Button, Tag, Space, Timeline, Drawer, Slider, Radio, Progress, Avatar, List, message, Input, Badge, Tooltip, Divider, Popconfirm, Checkbox } from 'antd'
import {
  CheckCircleOutlined,
  ClockCircleOutlined,
  LockOutlined,
  EnvironmentOutlined,
  SwapOutlined,
  BookOutlined,
  PlayCircleOutlined,
  FileTextOutlined,
  CodeOutlined,
  GlobalOutlined,
  FlagOutlined,
  RocketOutlined,
  ArrowRightOutlined,
  NodeIndexOutlined,
  ReloadOutlined,
  ExclamationCircleOutlined,
  ApartmentOutlined,
  BulbOutlined,
  SaveOutlined,
  StepForwardOutlined,
  CloseCircleOutlined,
  UndoOutlined,
  EyeOutlined,
} from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import { useAppStore } from '../store'
import { pathApi, profileApi, learningDataApi, logReflectionApi } from '../services/api'
import { buildRadarData } from '../utils/profile'
import type { PathNode, PathStage, StudentProfile, LearningPathData } from '../types'

const statusColors: Record<string, string> = {
  completed: '#10b981',
  'in-progress': '#4f46e5',
  pending: '#94a3b8',
  locked: '#cbd5e1',
}

const statusLabels: Record<string, string> = {
  completed: '已完成',
  'in-progress': '进行中',
  pending: '未开始',
  locked: '未解锁',
}

const statusBg: Record<string, string> = {
  completed: '#ecfdf5',
  'in-progress': '#eef2ff',
  pending: '#f8fafc',
  locked: '#f1f5f9',
}

const resourceTypeMeta: Record<string, { icon: React.ReactNode; color: string }> = {
  video: { icon: <PlayCircleOutlined />, color: '#ef4444' },
  code: { icon: <CodeOutlined />, color: '#3b82f6' },
  doc: { icon: <FileTextOutlined />, color: '#10b981' },
  quiz: { icon: <BookOutlined />, color: '#f59e0b' },
  document: { icon: <FileTextOutlined />, color: '#10b981' },
  视频: { icon: <PlayCircleOutlined />, color: '#ef4444' },
  代码: { icon: <CodeOutlined />, color: '#3b82f6' },
  文档: { icon: <FileTextOutlined />, color: '#10b981' },
  练习: { icon: <BookOutlined />, color: '#f59e0b' },
  题目: { icon: <BookOutlined />, color: '#f59e0b' },
}

const LearningPathPage: React.FC = () => {
  const [viewMode, setViewMode] = useState<'map' | 'timeline' | 'graph'>(() => {
    if (typeof window === 'undefined') return 'map'
    return (localStorage.getItem('learning_path_view_mode') as 'map' | 'timeline' | 'graph') || 'map'
  })
  const [drawerOpen, setDrawerOpen] = useState(false)
  const [selectedNode, setSelectedNode] = useState<PathNode | null>(null)
  const [pathData, setPathData] = useState<Record<string, unknown> | null>(null)
  const [pathNodes, setPathNodes] = useState<PathNode[]>([])
  const [pathStages, setPathStages] = useState<PathStage[]>([])
  const [loading, setLoading] = useState(false)
  const [showReviewAlert, setShowReviewAlert] = useState(() => {
    // 当天稍后提醒后保持隐藏；新一天自动恢复
    if (typeof window === 'undefined') return true
    const today = new Date().toISOString().slice(0, 10)
    return localStorage.getItem('review_alert_dismissed') !== today
  })
  const [dailyDuration, setDailyDuration] = useState(90)
  const [difficulty, setDifficulty] = useState(3)
  const [learningPreference, setLearningPreference] = useState('balanced')
  const [targetTopic, setTargetTopic] = useState('掌握 C语言程序设计与数据结构基础')
  const [adjustFeedback, setAdjustFeedback] = useState('')
  const [profileSuggestions, setProfileSuggestions] = useState<string[]>([])
  const [weakReviewTopics, setWeakReviewTopics] = useState<string[]>([])
  const [activeAdjustTab, setActiveAdjustTab] = useState<'params' | 'nodes' | 'feedback'>('params')
  const [reflectionText, setReflectionText] = useState('')
  const [submittingReflection, setSubmittingReflection] = useState(false)
  const studentId = useAppStore((s) => s.studentId)
  const navigate = useNavigate()

  // 力导向拓扑图相关 refs
  const graphRef = useRef<SVGSVGElement>(null)
  const nodePositionsRef = useRef<Map<number, { x: number; y: number; vx: number; vy: number }>>(new Map())
  const dragRef = useRef<{ id: number; offsetX: number; offsetY: number; startX: number; startY: number; moved: boolean } | null>(null)
  const animFrameRef = useRef<number>(0)
  const [graphTick, setGraphTick] = useState(0)

  // 加载本地保存的偏好和路径数据
  useEffect(() => {
    const saved = localStorage.getItem(`path_prefs_${studentId}`)
    if (saved) {
      try {
        const p = JSON.parse(saved)
        setDailyDuration(p.dailyDuration ?? 90)
        setDifficulty(p.difficulty ?? 3)
        setLearningPreference(p.learningPreference ?? 'balanced')
        setTargetTopic(p.targetTopic ?? '掌握 C语言程序设计与数据结构基础')
      } catch {}
    }
  }, [studentId])

  // 加载画像建议
  useEffect(() => {
    const loadProfile = async () => {
      try {
        const res = await profileApi.get(studentId)
        const p = res.data?.data
        if (p) {
          const suggestions: string[] = []
          if (p.weak_areas?.length) suggestions.push(`薄弱点：${p.weak_areas.slice(0, 3).join('、')} — 建议优先安排`)
          if (p.learning_tempo?.study_speed === 'fast') suggestions.push('你的学习节奏较快，可适当提高难度或缩短每日时长')
          if (p.learning_tempo?.study_speed === 'slow') suggestions.push('你的学习节奏较缓，建议降低难度并增加每日时长')
          if (p.cognitive_style?.primary === 'kinesthetic') suggestions.push('你是动手实践型学习者，建议多选代码实战类资源')
          if ((p.practical_preferences?.overall_score ?? 1) < 0.5) suggestions.push('实践偏好分较低，建议增加练习比重')
          setProfileSuggestions(suggestions)
          // 复习提醒来自薄弱点列表（取前 5 条）
          setWeakReviewTopics((p.weak_areas || []).slice(0, 5))
        }
      } catch {}
    }
    loadProfile()
  }, [studentId])

  useEffect(() => {
    const load = async () => {
      try {
        const res = await pathApi.current(studentId)
        if (res.data) {
          const nodes: PathNode[] = res.data.nodes || []
          // 后端 current 接口可能挂载 path.stages，方便后续给节点详情显示资源类型
          const respAny = res.data as unknown as { path?: { stages?: PathStage[] } }
          const stages: PathStage[] = respAny.path?.stages || []
          setPathData(res.data as unknown as Record<string, unknown>)
          setPathNodes(nodes as PathNode[])
          setPathStages(stages)
        }
      } catch {
        // 路径未生成或后端异常时不再回退到硬编码 14 节点，由空状态 UI 提示
        setPathNodes([])
        setPathStages([])
      }
    }
    load()
  }, [studentId])

  // 从后端同步已完成节点（避免刷新后丢失）
  useEffect(() => {
    if (!studentId || pathNodes.length === 0) return
    let ignore = false
    const syncCompleted = async () => {
      try {
        const res = await learningDataApi.getCompleted(studentId)
        const completedKps = res.data?.completed_kps || []
        if (!ignore && completedKps.length) {
          setPathNodes((prev) =>
            prev.map((n) => {
              const nodeKp = nodeKpId(n)
              return completedKps.includes(nodeKp) ? { ...n, status: 'completed' } : n
            })
          )
        }
      } catch {
        // 静默失败
      }
    }
    syncCompleted()
    return () => { ignore = true }
    // 只在 studentId 变化或首次拿到 nodes 时执行
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [studentId, pathNodes.length])

  // 初始化节点位置
  useEffect(() => {
    if (pathNodes.length === 0) return
    const W = 900, H = 600
    const existing = nodePositionsRef.current
    pathNodes.forEach((node, i) => {
      if (!existing.has(node.id)) {
        const angle = (2 * Math.PI * i) / pathNodes.length
        const rx = W * 0.3, ry = H * 0.3
        existing.set(node.id, {
          x: W / 2 + rx * Math.cos(angle) + (Math.random() - 0.5) * 40,
          y: H / 2 + ry * Math.sin(angle) + (Math.random() - 0.5) * 40,
          vx: 0, vy: 0,
        })
      }
    })
  }, [pathNodes])

  // 构建边列表
  const graphEdges = useMemo(() => {
    const edges: [number, number][] = []
    for (let i = 0; i < pathNodes.length - 1; i++) {
      edges.push([pathNodes[i].id, pathNodes[i + 1].id])
    }
    // 同阶段内节点互连（每 4 个一组）
    for (let i = 0; i < pathNodes.length; i += 4) {
      for (let j = i; j < Math.min(i + 4, pathNodes.length) - 1; j++) {
        if (!edges.some(([a, b]) => (a === pathNodes[j].id && b === pathNodes[j + 1].id) || (b === pathNodes[j].id && a === pathNodes[j + 1].id))) {
          edges.push([pathNodes[j].id, pathNodes[j + 1].id])
        }
      }
    }
    return edges
  }, [pathNodes])

  // 力导向模拟
  useEffect(() => {
    if (pathNodes.length === 0) return
    const W = 900, H = 600
    let settled = false

    const step = () => {
      if (settled) return
      const pos = nodePositionsRef.current
      let totalMovement = 0

      // 斥力（所有节点对）
      for (let i = 0; i < pathNodes.length; i++) {
        for (let j = i + 1; j < pathNodes.length; j++) {
          const a = pos.get(pathNodes[i].id)
          const b = pos.get(pathNodes[j].id)
          if (!a || !b) continue
          let dx = b.x - a.x, dy = b.y - a.y
          let dist = Math.sqrt(dx * dx + dy * dy) || 1
          if (dist < 300) {
            const force = 2000 / (dist * dist)
            const fx = (dx / dist) * force, fy = (dy / dist) * force
            if (dragRef.current?.id !== pathNodes[i].id) { a.vx -= fx; a.vy -= fy }
            if (dragRef.current?.id !== pathNodes[j].id) { b.vx += fx; b.vy += fy }
          }
        }
      }

      // 引力（相连节点）
      const springLen = 140
      for (const [id1, id2] of graphEdges) {
        const a = pos.get(id1), b = pos.get(id2)
        if (!a || !b) continue
        const dx = b.x - a.x, dy = b.y - a.y
        const dist = Math.sqrt(dx * dx + dy * dy) || 1
        const force = (dist - springLen) * 0.005
        const fx = (dx / dist) * force, fy = (dy / dist) * force
        if (dragRef.current?.id !== id1) { a.vx += fx; a.vy += fy }
        if (dragRef.current?.id !== id2) { b.vx -= fx; b.vy -= fy }
      }

      // 居中力 + 边界 + 阻尼
      for (const node of pathNodes) {
        const p = pos.get(node.id)
        if (!p) continue
        if (dragRef.current?.id !== node.id) {
          p.vx += (W / 2 - p.x) * 0.0003
          p.vy += (H / 2 - p.y) * 0.0003
          p.vx *= 0.9; p.vy *= 0.9
          p.x += p.vx; p.y += p.vy
          p.x = Math.max(50, Math.min(W - 50, p.x))
          p.y = Math.max(50, Math.min(H - 50, p.y))
        }
        totalMovement += Math.abs(p.vx) + Math.abs(p.vy)
      }

      setGraphTick((t) => t + 1)

      if (totalMovement < 0.5) {
        settled = true
      }
      animFrameRef.current = requestAnimationFrame(step)
    }

    animFrameRef.current = requestAnimationFrame(step)
    return () => cancelAnimationFrame(animFrameRef.current)
  }, [pathNodes, graphEdges])

  // 拖拽交互
  const getNodeRadius = (status: string) =>
    status === 'completed' ? 32 : status === 'in-progress' ? 30 : status === 'locked' ? 26 : 28

  const svgCoords = useCallback((e: React.PointerEvent | MouseEvent) => {
    const svg = graphRef.current
    if (!svg) return { x: 0, y: 0 }
    const rect = svg.getBoundingClientRect()
    return {
      x: (e.clientX - rect.left) * (900 / rect.width),
      y: (e.clientY - rect.top) * (600 / rect.height),
    }
  }, [])

  const handleGraphPointerDown = useCallback((e: React.PointerEvent) => {
    const { x: mx, y: my } = svgCoords(e)

    for (const node of pathNodes) {
      const p = nodePositionsRef.current.get(node.id)
      if (!p) continue
      const r = getNodeRadius(node.status) + 8
      if (Math.hypot(mx - p.x, my - p.y) < r) {
        dragRef.current = { id: node.id, offsetX: mx - p.x, offsetY: my - p.y, startX: mx, startY: my, moved: false }
        return
      }
    }
  }, [pathNodes, svgCoords])

  const handleGraphPointerMove = useCallback((e: React.PointerEvent) => {
    if (!dragRef.current) return
    const { x: mx, y: my } = svgCoords(e)
    if (Math.hypot(mx - dragRef.current.startX, my - dragRef.current.startY) > 5) {
      dragRef.current.moved = true
    }
    if (!dragRef.current.moved) return
    const p = nodePositionsRef.current.get(dragRef.current.id)
    if (!p) return
    p.x = mx - dragRef.current.offsetX
    p.y = my - dragRef.current.offsetY
    p.x = Math.max(50, Math.min(850, p.x))
    p.y = Math.max(50, Math.min(550, p.y))
    p.vx = 0; p.vy = 0
    setGraphTick((t) => t + 1)
  }, [svgCoords])

  const handleGraphPointerUp = useCallback((e: React.PointerEvent) => {
    if (!dragRef.current) return
    if (!dragRef.current.moved) {
      // 没有移动，视为点击 → 打开节点详情
      const node = pathNodes.find((n) => n.id === dragRef.current!.id)
      if (node) openNodeDetail(node)
    }
    dragRef.current = null
  }, [pathNodes])

  // 重置布局
  const resetGraphLayout = useCallback(() => {
    const W = 900, H = 600
    nodePositionsRef.current.clear()
    pathNodes.forEach((node, i) => {
      const angle = (2 * Math.PI * i) / pathNodes.length
      const rx = W * 0.3, ry = H * 0.3
      nodePositionsRef.current.set(node.id, {
        x: W / 2 + rx * Math.cos(angle),
        y: H / 2 + ry * Math.sin(angle),
        vx: 0, vy: 0,
      })
    })
    setGraphTick((t) => t + 1)
  }, [pathNodes])

  // 提交学习反思
  const handleSubmitReflection = async () => {
    if (!selectedNode || !reflectionText.trim()) return
    setSubmittingReflection(true)
    try {
      await logReflectionApi.createReflection({
        student_id: studentId,
        date: new Date().toISOString().slice(0, 10),
        content: `[${selectedNode.title}] ${reflectionText}`,
        tags: ['learning-path', selectedNode.title],
      })
      message.success('反思已提交')
      setReflectionText('')
    } catch (e) {
      message.error((e as Error).message || '提交失败')
    } finally {
      setSubmittingReflection(false)
    }
  }

  const openNodeDetail = (node: PathNode) => {
    setSelectedNode(node)
    setDrawerOpen(true)
  }

  // 节点 -> kp_id 映射（保留 kp_id；缺失时退化为 kp_c01..14）
  const nodeKpId = (node: PathNode): string => {
    if (node.kp_id) return String(node.kp_id)
    const idNum = Number(node.id)
    if (Number.isFinite(idNum) && idNum >= 1 && idNum <= 16) {
      return `kp_c${String(idNum).padStart(2, '0')}`
    }
    return String(node.id)
  }

  // 取节点对应阶段的真实资源类型（来自后端 path.stages[idx].resources）
  const getNodeResources = (node: PathNode): { title: string; type: string; icon: React.ReactNode; color: string }[] => {
    const idx = pathNodes.findIndex((n) => n.id === node.id)
    const stage = pathStages[idx]
    if (!stage?.resources?.length) return []
    return stage.resources.map((r, i) => {
      const meta = resourceTypeMeta[r] || { icon: <FileTextOutlined />, color: '#64748b' }
      return {
        title: `${stage.title}：${r}`,
        type: r,
        icon: meta.icon,
        color: meta.color,
        // 强制 key
        ...{ _i: i },
      }
    })
  }

  const handleGeneratePath = async () => {
    setLoading(true)
    try {
      const res = await pathApi.generate({
        student_id: studentId,
        target_topic: targetTopic,
        daily_duration: dailyDuration,
        difficulty: difficulty,
        preference: learningPreference,
      })
      const responseData = res.data as unknown as Record<string, unknown>
      const pathPayload = (responseData.data as Record<string, unknown> | undefined)?.path as Record<string, unknown> | undefined
      const stages: PathStage[] = (pathPayload?.stages as PathStage[] | undefined) || []
      const nodes: PathNode[] = stages.map((s, idx) => ({
        id: idx + 1,
        title: s.title,
        status: (idx === 0 ? 'in-progress' : 'pending') as PathNode['status'],
        type: s.resources?.[0] || '综合',
        resources: s.topics?.length || 3,
      }))
      setPathNodes(nodes)
      setPathStages(stages)
      setPathData(responseData.data as Record<string, unknown>)
      message.success('路径生成成功')
    } catch (e) {
      message.error((e as Error).message || '生成失败')
    } finally {
      setLoading(false)
    }
  }

  const handleSavePreferences = () => {
    const prefs = { dailyDuration, difficulty, learningPreference, targetTopic }
    localStorage.setItem(`path_prefs_${studentId}`, JSON.stringify(prefs))
    message.success('偏好设置已保存')
  }

  const handleAdjustPath = async () => {
    if (!adjustFeedback.trim()) {
      message.warning('请输入调整反馈')
      return
    }
    setLoading(true)
    try {
      const res = await pathApi.adjust(studentId, {
        feedback: adjustFeedback,
        current_path: pathData?.path as LearningPathData | undefined,
      })
      const adjustData = (res.data as unknown as Record<string, unknown>).data as Record<string, unknown> | undefined
      const stages: PathStage[] = (adjustData?.stages as PathStage[] | undefined) || []
      if (stages.length) {
        const nodes: PathNode[] = stages.map((s, idx) => ({
          id: idx + 1,
          title: s.title,
          status: (idx === 0 ? 'in-progress' : 'pending') as PathNode['status'],
          type: s.resources?.[0] || '综合',
          resources: s.topics?.length || 3,
        }))
        setPathNodes(nodes)
        setPathStages(stages)
        setPathData({ ...pathData, path: adjustData })
      }
      message.success('路径已调整')
      setAdjustFeedback('')
    } catch (e) {
      message.error((e as Error).message || '调整失败')
    } finally {
      setLoading(false)
    }
  }

  const handleNodeAction = async (nodeId: number, action: 'complete' | 'skip' | 'reset') => {
    const node = pathNodes.find((n) => n.id === nodeId)
    // 标记完成：写入后端
    if (action === 'complete' && node) {
      try {
        await learningDataApi.record({
          student_id: studentId,
          kp_id: nodeKpId(node),
          action: 'complete',
          duration: 0,
          progress: 1,
        })
      } catch (e) {
        message.error((e as Error).message || '同步后端失败')
        return
      }
    }
    setPathNodes((prev) =>
      prev.map((n) => {
        if (n.id !== nodeId) return n
        if (action === 'complete') return { ...n, status: 'completed' }
        if (action === 'skip') return { ...n, status: 'pending', skipped: true }
        if (action === 'reset') return { ...n, status: 'pending', skipped: false }
        return n
      })
    )
    message.success(action === 'complete' ? '已标记完成' : action === 'skip' ? '已跳过该节点' : '已重置进度')
  }

  const handleBatchComplete = async (ids: number[]) => {
    const targets = pathNodes.filter((n) => ids.includes(n.id))
    try {
      await Promise.all(
        targets.map((n) =>
          learningDataApi.record({
            student_id: studentId,
            kp_id: nodeKpId(n),
            action: 'complete',
            duration: 0,
            progress: 1,
          })
        )
      )
    } catch (e) {
      message.error((e as Error).message || '批量同步失败')
      return
    }
    setPathNodes((prev) =>
      prev.map((n) => (ids.includes(n.id) ? { ...n, status: 'completed' } : n))
    )
    message.success(`已批量标记 ${ids.length} 个节点为已完成`)
  }

  const completedCount = pathNodes.filter((n) => n.status === 'completed').length
  const progress = pathNodes.length ? Math.round((completedCount / pathNodes.length) * 100) : 0

  const timelineItems = useMemo(() => pathNodes.map((node) => ({
    dot: (
      <div className="w-9 h-9 rounded-full flex items-center justify-center text-white shadow-sm" style={{ background: statusColors[node.status] }}>
        {node.status === 'completed' ? <CheckCircleOutlined /> :
         node.status === 'in-progress' ? <ClockCircleOutlined /> :
         node.status === 'locked' ? <LockOutlined /> :
         <EnvironmentOutlined />}
      </div>
    ),
    color: statusColors[node.status],
    children: (
      <div
        className="p-5 rounded-xl bg-white border border-slate-100 hover:border-slate-200 hover:shadow-card transition-all cursor-pointer"
        onClick={() => openNodeDetail(node)}
      >
        <div className="flex items-center gap-2 mb-2">
          <Tag
            className="rounded-full border-0 text-xs font-medium"
            style={{ background: statusBg[node.status], color: statusColors[node.status] }}
          >
            {statusLabels[node.status]}
          </Tag>
          <span className="text-xs text-slate-400">{node.type}</span>
        </div>
        <Typography.Text className="font-bold text-slate-800 block text-base">{node.title}</Typography.Text>
        <Typography.Text className="text-slate-400 text-sm">{node.resources} 个资源</Typography.Text>
      </div>
    ),
  })), [pathNodes])

  return (
    <div className="space-y-5">
      {/* 顶部控制栏 */}
      <Card className="border border-slate-100 rounded-2xl" styles={{ body: { padding: '24px' } }}>
        <div className="flex flex-wrap items-center justify-between gap-4">
          <Space>
            <div className="w-10 h-10 rounded-xl bg-slate-900 flex items-center justify-center text-white">
              <FlagOutlined />
            </div>
            <div>
              <Typography.Title level={4} className="!m-0 text-slate-800">{targetTopic || '学习路径'}</Typography.Title>
              <Typography.Text className="text-slate-400 text-xs">个性化路径 · 共 {pathNodes.length} 个阶段</Typography.Text>
            </div>
          </Space>
          <Space>
            <Radio.Group value={viewMode} onChange={(e) => {
              const v = e.target.value as 'map' | 'timeline' | 'graph'
              setViewMode(v)
              localStorage.setItem('learning_path_view_mode', v)
            }} buttonStyle="solid" className="rounded-lg overflow-hidden">
              <Radio.Button value="map"><GlobalOutlined /> 地图视图</Radio.Button>
              <Radio.Button value="timeline"><ClockCircleOutlined /> 时间轴</Radio.Button>
              <Radio.Button value="graph"><NodeIndexOutlined /> 知识图谱</Radio.Button>
            </Radio.Group>
            <Tooltip title="基于知识图谱约束的 LLM 路径规划">
              <Tag className="rounded-full border-0 bg-indigo-50 text-indigo-600 text-xs cursor-default"><ApartmentOutlined /> KG 约束</Tag>
            </Tooltip>
            <Button type="primary" icon={<SwapOutlined />} loading={loading} className="rounded-lg bg-primary" onClick={() => setDrawerOpen(true)}>
              调整路径
            </Button>
            <Button className="rounded-lg border-slate-200" onClick={handleGeneratePath} loading={loading}>
              重新生成
            </Button>
          </Space>
        </div>

        <div className="mt-6">
          <div className="flex justify-between text-sm text-slate-500 mb-2">
            <span className="font-medium">总体进度</span>
            <span className="font-bold text-primary">{progress}%</span>
          </div>
          <Progress
            percent={progress}
            strokeColor={{ from: '#4f46e5', to: '#0ea5e9' }}
            trailColor="#f1f5f9"
            size="small"
            showInfo={false}
            strokeLinecap="round"
          />
        </div>
      </Card>

      {/* 艾宾浩斯复习提醒 */}
      {showReviewAlert && weakReviewTopics.length > 0 && (
        <div className="bg-amber-50 border border-amber-100 rounded-2xl p-4 flex items-center gap-3">
          <ExclamationCircleOutlined className="text-amber-500 text-lg" />
          <div className="flex-1">
            <div className="text-sm font-medium text-amber-800">
              遗忘曲线提醒：有 {weakReviewTopics.length} 个知识点需要今日复习
            </div>
            <div className="text-xs text-amber-600">
              {weakReviewTopics.slice(0, 3).join('、')} — 基于画像薄弱点与艾宾浩斯遗忘曲线计算
            </div>
          </div>
          <Button
            size="small"
            className="rounded-lg border-amber-200 text-amber-700"
            onClick={() => {
              const today = new Date().toISOString().slice(0, 10)
              localStorage.setItem('review_alert_dismissed', today)
              setShowReviewAlert(false)
            }}
          >
            稍后提醒
          </Button>
          <Button
            size="small"
            type="primary"
            className="rounded-lg bg-amber-500 border-amber-500"
            onClick={() => navigate('/personal?tab=forgetting')}
          >
            <ReloadOutlined /> 开始复习
          </Button>
        </div>
      )}

      {/* 地图视图 — 球状力导向拓扑图 */}
      {viewMode === 'map' && (
        <div className="bg-white rounded-2xl border border-slate-100 p-6 md:p-8">
          {pathNodes.length === 0 ? (
            <div className="text-center py-12">
              <RocketOutlined className="text-3xl text-slate-300 mb-3" />
              <Typography.Text className="text-slate-400 text-sm block">暂无学习路径</Typography.Text>
              <Button type="primary" className="rounded-lg bg-primary mt-4" onClick={handleGeneratePath} loading={loading}>
                立即生成 <ArrowRightOutlined />
              </Button>
            </div>
          ) : (
            <>
              <div className="flex justify-end mb-3">
                <Button size="small" className="rounded-lg border-slate-200 text-slate-500" icon={<ReloadOutlined />} onClick={resetGraphLayout}>
                  重置布局
                </Button>
              </div>
              <div className="w-full overflow-hidden rounded-xl bg-gradient-to-br from-slate-50 to-indigo-50/30 border border-slate-100">
                <svg
                  ref={graphRef}
                  viewBox="0 0 900 600"
                  className="w-full h-auto select-none"
                  style={{ cursor: dragRef.current ? 'grabbing' : 'default', minHeight: 400 }}
                  onPointerDown={handleGraphPointerDown}
                  onPointerMove={handleGraphPointerMove}
                  onPointerUp={handleGraphPointerUp}
                  onPointerCancel={handleGraphPointerUp}
                >
                  <defs>
                    {/* 球体渐变 */}
                    {pathNodes.map((node) => {
                      const c = statusColors[node.status]
                      return (
                        <radialGradient key={`grad-${node.id}`} id={`grad-${node.id}`} cx="35%" cy="30%">
                          <stop offset="0%" stopColor="#fff" stopOpacity="0.6" />
                          <stop offset="50%" stopColor={c} stopOpacity="0.9" />
                          <stop offset="100%" stopColor={c} stopOpacity="1" />
                        </radialGradient>
                      )
                    })}
                    {/* 阴影 */}
                    <filter id="ball-shadow" x="-30%" y="-20%" width="160%" height="160%">
                      <feDropShadow dx="0" dy="4" stdDeviation="6" floodColor="#000" floodOpacity="0.12" />
                    </filter>
                    {/* 发光 */}
                    <filter id="ball-glow" x="-50%" y="-50%" width="200%" height="200%">
                      <feGaussianBlur in="SourceGraphic" stdDeviation="8" result="blur" />
                      <feMerge>
                        <feMergeNode in="blur" />
                        <feMergeNode in="SourceGraphic" />
                      </feMerge>
                    </filter>
                  </defs>

                  {/* 连线 */}
                  {graphEdges.map(([id1, id2]) => {
                    const p1 = nodePositionsRef.current.get(id1)
                    const p2 = nodePositionsRef.current.get(id2)
                    if (!p1 || !p2) return null
                    const n1 = pathNodes.find((n) => n.id === id1)
                    const bothDone = n1?.status === 'completed'
                    const isLineDone = bothDone && pathNodes.find((n) => n.id === id2)?.status === 'completed'
                    return (
                      <line
                        key={`edge-${id1}-${id2}`}
                        x1={p1.x} y1={p1.y}
                        x2={p2.x} y2={p2.y}
                        stroke={isLineDone ? '#10b981' : '#cbd5e1'}
                        strokeWidth={isLineDone ? 2.5 : 1.5}
                        strokeDasharray={isLineDone ? undefined : '6 4'}
                        strokeLinecap="round"
                        opacity={isLineDone ? 0.8 : 0.5}
                      />
                    )
                  })}

                  {/* 节点球体 */}
                  {pathNodes.map((node, idx) => {
                    const p = nodePositionsRef.current.get(node.id)
                    if (!p) return null
                    const r = getNodeRadius(node.status)
                    const isDragged = dragRef.current?.id === node.id
                    return (
                      <g
                        key={node.id}
                        style={{ cursor: isDragged ? 'grabbing' : 'grab' }}
                      >
                        {/* 外发光（进行中） */}
                        {node.status === 'in-progress' && (
                          <circle cx={p.x} cy={p.y} r={r + 10} fill="none" stroke="#4f46e5" strokeWidth="2" opacity="0.15">
                            <animate attributeName="r" values={`${r + 8};${r + 14};${r + 8}`} dur="2s" repeatCount="indefinite" />
                            <animate attributeName="opacity" values="0.15;0.05;0.15" dur="2s" repeatCount="indefinite" />
                          </circle>
                        )}
                        {/* 球体 */}
                        <circle
                          cx={p.x} cy={p.y} r={r}
                          fill={`url(#grad-${node.id})`}
                          filter="url(#ball-shadow)"
                          stroke={isDragged ? '#4f46e5' : 'rgba(255,255,255,0.5)'}
                          strokeWidth={isDragged ? 3 : 1.5}
                        />
                        {/* 高光 */}
                        <ellipse
                          cx={p.x - r * 0.2} cy={p.y - r * 0.3}
                          rx={r * 0.4} ry={r * 0.2}
                          fill="rgba(255,255,255,0.35)"
                        />
                        {/* 编号 */}
                        <text
                          x={p.x} y={p.y - 4}
                          textAnchor="middle"
                          dominantBaseline="middle"
                          fill="white"
                          fontSize="14"
                          fontWeight="bold"
                          style={{ pointerEvents: 'none', textShadow: '0 1px 2px rgba(0,0,0,0.3)' }}
                        >
                          {idx + 1}
                        </text>
                        {/* 标题 */}
                        <text
                          x={p.x} y={p.y + 12}
                          textAnchor="middle"
                          dominantBaseline="middle"
                          fill="white"
                          fontSize="8"
                          opacity="0.9"
                          style={{ pointerEvents: 'none' }}
                        >
                          {node.title.length > 5 ? node.title.slice(0, 5) + '..' : node.title}
                        </text>
                        {/* 底部标题标签 */}
                        <text
                          x={p.x} y={p.y + r + 16}
                          textAnchor="middle"
                          dominantBaseline="middle"
                          fill="#475569"
                          fontSize="11"
                          fontWeight="600"
                          style={{ pointerEvents: 'none' }}
                        >
                          {node.title.length > 8 ? node.title.slice(0, 8) + '..' : node.title}
                        </text>
                        {/* 状态标签 */}
                        <text
                          x={p.x} y={p.y + r + 30}
                          textAnchor="middle"
                          dominantBaseline="middle"
                          fill={statusColors[node.status]}
                          fontSize="9"
                          style={{ pointerEvents: 'none' }}
                        >
                          {statusLabels[node.status]}
                        </text>
                      </g>
                    )
                  })}
                </svg>
              </div>
              {/* 图例 */}
              <div className="flex justify-center gap-6 mt-4 flex-wrap">
                {Object.entries(statusLabels).map(([key, label]) => (
                  <div key={key} className="flex items-center gap-1.5">
                    <div className="w-3 h-3 rounded-full" style={{ background: statusColors[key] }} />
                    <span className="text-xs text-slate-500">{label}</span>
                  </div>
                ))}
                <div className="flex items-center gap-1.5">
                  <div className="w-6 h-0 border-t-2 border-slate-300 border-dashed" />
                  <span className="text-xs text-slate-500">依赖</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <div className="w-6 h-0 border-t-2 border-emerald-400" />
                  <span className="text-xs text-slate-500">已完成</span>
                </div>
              </div>
            </>
          )}
        </div>
      )}

      {/* 时间轴视图 — 带日期和里程碑 */}
      {viewMode === 'timeline' && (
        <div className="bg-white rounded-2xl border border-slate-100 p-8 md:p-10">
          {pathNodes.length === 0 ? (
            <div className="text-center py-12 text-slate-400 text-sm">暂无学习路径</div>
          ) : (
            <div className="max-w-2xl mx-auto">
              {/* 时间轴概览 */}
              <div className="flex items-center justify-between mb-8 pb-4 border-b border-slate-100">
                <div>
                  <Typography.Text className="text-slate-500 text-sm">预计总时长</Typography.Text>
                  <div className="text-2xl font-bold text-slate-800">
                    {Math.ceil(pathNodes.reduce((sum, n) => sum + (n.resources || 3) * 20, 0) / dailyDuration)} 天
                  </div>
                </div>
                <div className="text-right">
                  <Typography.Text className="text-slate-500 text-sm">每日学习</Typography.Text>
                  <div className="text-2xl font-bold text-slate-800">{dailyDuration} 分钟</div>
                </div>
              </div>

              {/* 自定义时间轴：避免 antd Timeline label 挤压 */}
              <div className="relative">
                {/* 中心线 */}
                <div className="absolute left-4 md:left-1/2 top-0 bottom-0 w-0.5 bg-slate-100 -translate-x-1/2" />
                <div className="space-y-8">
                  {pathNodes.map((node, idx) => {
                    const cumulativeMinutes = pathNodes.slice(0, idx).reduce((sum, n) => sum + (n.resources || 3) * 20, 0)
                    const dayNum = Math.floor(cumulativeMinutes / dailyDuration) + 1
                    const weekNum = Math.ceil(dayNum / 7)
                    const isMilestone = dayNum % 7 === 1 && idx > 0
                    const isLeft = idx % 2 === 0
                    return (
                      <div key={node.id} className={`relative flex items-start gap-4 md:gap-8 ${isLeft ? 'md:flex-row' : 'md:flex-row-reverse'}`}>
                        {/* 移动端：左侧固定；桌面端：交替 */}
                        <div className="hidden md:block flex-1" />
                        {/* 时间轴节点圆点 */}
                        <div className="relative z-10 shrink-0">
                          <div
                            className="w-10 h-10 rounded-full flex items-center justify-center text-white shadow-sm text-sm"
                            style={{ background: statusColors[node.status] }}
                          >
                            {node.status === 'completed' ? <CheckCircleOutlined /> :
                             node.status === 'in-progress' ? <ClockCircleOutlined /> :
                             node.status === 'locked' ? <LockOutlined /> :
                             <span className="text-xs font-bold">{idx + 1}</span>}
                          </div>
                        </div>
                        {/* 内容卡片 */}
                        <div className={`flex-1 ${isLeft ? 'md:text-left' : 'md:text-right'}`}>
                          {/* 日期标签 */}
                          <div className={`mb-2 text-xs leading-relaxed ${isLeft ? 'md:text-left' : 'md:text-right'}`}>
                            <span className="font-bold text-slate-600 mr-2">第 {dayNum} 天</span>
                            <span className="text-slate-400">{(node.resources || 3) * 20} 分钟</span>
                            {isMilestone && (
                              <span className="text-amber-500 font-medium ml-2">第 {weekNum} 周</span>
                            )}
                          </div>
                          {/* 卡片 */}
                          <div
                            className={`inline-block p-5 rounded-xl bg-white border border-slate-100 hover:border-slate-200 hover:shadow-card transition-all cursor-pointer max-w-sm text-left ${isMilestone ? 'ring-2 ring-amber-100' : ''}`}
                            onClick={() => openNodeDetail(node)}
                          >
                            {isMilestone && (
                              <Tag className="rounded-full border-0 bg-amber-50 text-amber-600 text-xs mb-2">
                                <FlagOutlined /> 里程碑 · 第 {weekNum} 周
                              </Tag>
                            )}
                            <div className="flex items-center gap-2 mb-2 flex-wrap">
                              <Tag
                                className="rounded-full border-0 text-xs font-medium"
                                style={{ background: statusBg[node.status], color: statusColors[node.status] }}
                              >
                                {statusLabels[node.status]}
                              </Tag>
                              <span className="text-xs text-slate-400">{node.type}</span>
                            </div>
                            <Typography.Text className="font-bold text-slate-800 block text-base">{node.title}</Typography.Text>
                            <Typography.Text className="text-slate-400 text-sm">{node.resources} 个资源</Typography.Text>
                          </div>
                        </div>
                        {/* 移动端占位 */}
                        <div className="md:hidden flex-1" />
                      </div>
                    )
                  })}
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* 知识图谱视图 */}
      {viewMode === 'graph' && (
        <div className="bg-white rounded-2xl border border-slate-100 p-8 md:p-10">
          <div className="text-center mb-8">
            <Typography.Title level={5} className="!m-0 text-slate-800">知识图谱路径规划</Typography.Title>
            <Typography.Text className="text-slate-400 text-xs block mt-1">基于结构化知识图谱约束 LLM 生成，确保路径科学性</Typography.Text>
          </div>
          <div className="relative max-w-3xl mx-auto">
            {pathNodes.length === 0 ? (
              <div className="text-center py-10 text-slate-400 text-sm">尚未生成学习路径，请先在右上角点击「重新生成」</div>
            ) : (
              <div className="flex flex-wrap justify-center gap-4">
                {pathNodes.map((node, idx) => {
                  const level = Math.floor(idx / 3) + 1
                  return (
                    <div key={node.id} className="flex flex-col items-center">
                      <div
                        className="w-32 p-3 rounded-xl border text-center cursor-pointer transition-all hover:shadow-card"
                        style={{
                          borderColor: statusColors[node.status],
                          background: statusBg[node.status],
                        }}
                        onClick={() => openNodeDetail(node)}
                      >
                        <div className="text-xs text-slate-400 mb-1">L{level}</div>
                        <div className="text-sm font-medium text-slate-800 truncate">{node.title}</div>
                      </div>
                      {idx < pathNodes.length - 1 && <div className="h-6 w-0.5 bg-slate-200 my-1" />}
                    </div>
                  )
                })}
              </div>
            )}
            <div className="mt-6 flex flex-wrap gap-2 justify-center">
              {pathNodes.filter((n) => n.status === 'completed').map((n) => (
                <Tag key={n.id} className="rounded-full border-0 bg-emerald-50 text-emerald-600 text-xs">{n.title}</Tag>
              ))}
              {pathNodes.filter((n) => n.status === 'in-progress').map((n) => (
                <Tag key={n.id} className="rounded-full border-0 bg-indigo-50 text-indigo-600 text-xs">{n.title}</Tag>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* 节点详情/调整抽屉 */}
      <Drawer
        title={
          selectedNode ? (
            <Space>
              <div className="w-8 h-8 rounded-lg flex items-center justify-center text-white" style={{ background: statusColors[selectedNode.status] }}>
                {selectedNode.status === 'completed' ? <CheckCircleOutlined /> : selectedNode.status === 'in-progress' ? <ClockCircleOutlined /> : <RocketOutlined />}
              </div>
              <span className="font-semibold">{selectedNode.title}</span>
            </Space>
          ) : (
            <span className="font-semibold">调整学习路径</span>
          )
        }
        placement="right"
        onClose={() => { setDrawerOpen(false); setSelectedNode(null); setReflectionText('') }}
        open={drawerOpen}
        width={440}
        className="rounded-l-2xl"
      >
        {selectedNode ? (
          <div className="space-y-6">
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-100">
              <Space>
                <Tag
                  className="rounded-full border-0 text-xs font-medium"
                  style={{ background: statusBg[selectedNode.status], color: statusColors[selectedNode.status] }}
                >
                  {statusLabels[selectedNode.status]}
                </Tag>
                <Tag className="rounded-full border-0 bg-slate-100 text-slate-600 text-xs">{selectedNode.type}</Tag>
              </Space>
              <Typography.Text className="text-slate-600 block mt-3 leading-relaxed text-sm">
                该节点包含 <strong className="text-slate-800">{selectedNode.resources}</strong> 个多模态学习资源，完成后可解锁后续内容。
              </Typography.Text>
            </div>

            <div>
              <Typography.Text className="font-semibold text-slate-800 block mb-3 text-sm">关联资源</Typography.Text>
              {(() => {
                const items = getNodeResources(selectedNode)
                if (items.length === 0) {
                  return <div className="text-xs text-slate-400 px-2 py-3">该节点尚无资源数据，可点击下方按钮去资源中心生成</div>
                }
                return (
                  <List
                    itemLayout="horizontal"
                    dataSource={items}
                    renderItem={(item) => (
                      <List.Item className="hover:bg-slate-50 rounded-xl transition-colors px-2">
                        <List.Item.Meta
                          avatar={
                            <Avatar style={{ background: item.color + '12', color: item.color }} icon={item.icon} className="text-xs" />
                          }
                          title={<Typography.Text className="text-slate-700 font-medium text-sm">{item.title}</Typography.Text>}
                          description={<Tag className="rounded-full text-xs border-0 bg-slate-100 text-slate-500">{item.type}</Tag>}
                        />
                      </List.Item>
                    )}
                  />
                )
              })()}
            </div>

            {selectedNode.status === 'completed' && (
              <div>
                <Typography.Text className="font-semibold text-slate-800 block mb-3 text-sm">学习反思</Typography.Text>
                <div className="space-y-3">
                  <Input.TextArea
                    rows={4}
                    value={reflectionText}
                    onChange={(e) => setReflectionText(e.target.value)}
                    placeholder="完成这个节点后，你学到了什么？有哪些收获或疑问？"
                    className="rounded-xl bg-slate-50 border-slate-200"
                  />
                  <Button className="rounded-lg border-slate-200" loading={submittingReflection} onClick={handleSubmitReflection}>提交反思</Button>
                </div>
              </div>
            )}

            <Button
              type="primary"
              block
              className="rounded-lg bg-primary h-10"
              onClick={() => {
                navigate(`/resource/${nodeKpId(selectedNode)}`)
                setDrawerOpen(false)
              }}
            >
              {selectedNode.status === 'completed' ? '重新学习' : '开始学习'} <ArrowRightOutlined />
            </Button>
          </div>
        ) : (
          <div className="space-y-6">
            {/* 路径概览卡片 */}
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-100">
              <div className="flex items-center justify-between mb-3">
                <Typography.Text className="font-semibold text-slate-800 text-sm">当前路径概览</Typography.Text>
                <Tag className="rounded-full border-0 bg-indigo-50 text-indigo-600 text-xs">{pathNodes.length} 个阶段</Tag>
              </div>
              <div className="grid grid-cols-3 gap-3 text-center">
                <div className="p-2 rounded-lg bg-white border border-slate-100">
                  <div className="text-lg font-bold text-emerald-600">{completedCount}</div>
                  <div className="text-xs text-slate-400">已完成</div>
                </div>
                <div className="p-2 rounded-lg bg-white border border-slate-100">
                  <div className="text-lg font-bold text-indigo-600">{pathNodes.filter((n) => n.status === 'in-progress').length}</div>
                  <div className="text-xs text-slate-400">进行中</div>
                </div>
                <div className="p-2 rounded-lg bg-white border border-slate-100">
                  <div className="text-lg font-bold text-slate-600">{Math.max(1, Math.round((pathNodes.length - completedCount) * dailyDuration / 60))}h</div>
                  <div className="text-xs text-slate-400">预计剩余</div>
                </div>
              </div>
              <div className="mt-3">
                <Progress percent={progress} strokeColor={{ from: '#4f46e5', to: '#0ea5e9' }} trailColor="#f1f5f9" size="small" showInfo={false} strokeLinecap="round" />
                <div className="text-right text-xs text-slate-400 mt-1">总进度 {progress}%</div>
              </div>
            </div>

            {/* 画像个性化建议 */}
            {profileSuggestions.length > 0 && (
              <div className="p-3 rounded-xl bg-amber-50 border border-amber-100">
                <div className="flex items-center gap-2 mb-2">
                  <BulbOutlined className="text-amber-500" />
                  <Typography.Text className="font-semibold text-amber-800 text-sm">基于画像的建议</Typography.Text>
                </div>
                <div className="space-y-1.5">
                  {profileSuggestions.map((s, i) => (
                    <div key={i} className="text-xs text-amber-700 leading-relaxed flex items-start gap-1.5">
                      <span className="shrink-0 mt-0.5 w-1 h-1 rounded-full bg-amber-400" />
                      {s}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Tab 切换 */}
            <Radio.Group
              value={activeAdjustTab}
              onChange={(e) => setActiveAdjustTab(e.target.value)}
              buttonStyle="solid"
              className="w-full flex rounded-lg overflow-hidden"
            >
              <Radio.Button value="params" className="flex-1 text-center text-xs">参数设置</Radio.Button>
              <Radio.Button value="nodes" className="flex-1 text-center text-xs">节点管理</Radio.Button>
              <Radio.Button value="feedback" className="flex-1 text-center text-xs">智能微调</Radio.Button>
            </Radio.Group>

            {/* 参数设置 Tab */}
            {activeAdjustTab === 'params' && (
              <div className="space-y-6">
                <div>
                  <Typography.Text className="font-semibold text-slate-800 block mb-2 text-sm">学习目标主题</Typography.Text>
                  <Input
                    value={targetTopic}
                    onChange={(e) => setTargetTopic(e.target.value)}
                    placeholder="例如：掌握 C语言程序设计与数据结构基础"
                    className="rounded-lg"
                  />
                  <Typography.Text className="text-xs text-slate-400 block mt-1">修改后点击「重新规划」生效</Typography.Text>
                </div>

                <div>
                  <Typography.Text className="font-semibold text-slate-800 block mb-3 text-sm">学习偏好</Typography.Text>
                  <Radio.Group value={learningPreference} onChange={(e) => setLearningPreference(e.target.value)} className="flex flex-col gap-3">
                    <Radio value="theory" className="text-sm">加强理论（更多文档、讲解视频）</Radio>
                    <Radio value="practice" className="text-sm">多些练习（更多代码、算法题）</Radio>
                    <Radio value="balanced" className="text-sm">平衡模式（理论+实践兼顾）</Radio>
                  </Radio.Group>
                </div>

                <div>
                  <div className="flex justify-between mb-2">
                    <Typography.Text className="font-semibold text-slate-800 text-sm">每日学习时长</Typography.Text>
                    <Typography.Text className="text-xs text-slate-500">{dailyDuration} 分钟</Typography.Text>
                  </div>
                  <Slider min={30} max={240} step={15} value={dailyDuration} onChange={setDailyDuration} marks={{ 30: '30m', 120: '2h', 240: '4h' }} tooltip={{ formatter: (v) => `${v}分钟` }} />
                </div>

                <div>
                  <div className="flex justify-between mb-2">
                    <Typography.Text className="font-semibold text-slate-800 text-sm">难度偏好</Typography.Text>
                    <Typography.Text className="text-xs text-slate-500">{difficulty === 1 ? '简单' : difficulty === 2 ? '较易' : difficulty === 3 ? '适中' : difficulty === 4 ? '较难' : '挑战'}</Typography.Text>
                  </div>
                  <Slider min={1} max={5} step={1} value={difficulty} onChange={setDifficulty} marks={{ 1: '简单', 3: '适中', 5: '挑战' }} />
                </div>

                <div className="flex gap-2">
                  <Button className="rounded-lg border-slate-200 flex-1" icon={<SaveOutlined />} onClick={handleSavePreferences}>
                    保存偏好
                  </Button>
                  <Button type="primary" className="rounded-lg bg-primary flex-1" onClick={() => { handleGeneratePath(); setDrawerOpen(false); }} loading={loading}>
                    重新规划 <ArrowRightOutlined />
                  </Button>
                </div>
              </div>
            )}

            {/* 节点管理 Tab */}
            {activeAdjustTab === 'nodes' && (
              <div className="space-y-4">
                <Typography.Text className="font-semibold text-slate-800 block text-sm">节点状态管理</Typography.Text>
                <div className="space-y-2 max-h-[360px] overflow-y-auto pr-1">
                  {pathNodes.map((node) => (
                    <div
                      key={node.id}
                      className="flex items-center gap-3 p-3 rounded-xl bg-white border border-slate-100 hover:border-slate-200 transition-all"
                    >
                      <div
                        className="w-8 h-8 rounded-full flex items-center justify-center text-white text-xs shrink-0"
                        style={{ background: statusColors[node.status] }}
                      >
                        {node.id}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="text-sm font-medium text-slate-800 truncate">{node.title}</div>
                        <div className="text-xs text-slate-400">{node.type} · {statusLabels[node.status]}{node.skipped ? ' · 已跳过' : ''}</div>
                      </div>
                      <div className="flex gap-1">
                        {node.status !== 'completed' && (
                          <Tooltip title="标记完成">
                            <Button
                              size="small"
                              className="rounded-lg border-emerald-200 text-emerald-600"
                              icon={<CheckCircleOutlined />}
                              onClick={() => handleNodeAction(node.id, 'complete')}
                            />
                          </Tooltip>
                        )}
                        {node.status !== 'completed' && !node.skipped && (
                          <Tooltip title="跳过">
                            <Button
                              size="small"
                              className="rounded-lg border-amber-200 text-amber-600"
                              icon={<StepForwardOutlined />}
                              onClick={() => handleNodeAction(node.id, 'skip')}
                            />
                          </Tooltip>
                        )}
                        {(node.status === 'completed' || node.skipped) && (
                          <Tooltip title="重置">
                            <Button
                              size="small"
                              className="rounded-lg border-slate-200 text-slate-500"
                              icon={<UndoOutlined />}
                              onClick={() => handleNodeAction(node.id, 'reset')}
                            />
                          </Tooltip>
                        )}
                        <Tooltip title="开始学习">
                          <Button
                            size="small"
                            type="primary"
                            className="rounded-lg bg-primary"
                            icon={<EyeOutlined />}
                            onClick={() => {
                              navigate(`/resource/${nodeKpId(node)}`)
                              setDrawerOpen(false)
                            }}
                          />
                        </Tooltip>
                      </div>
                    </div>
                  ))}
                </div>

                {pathNodes.some((n) => n.status === 'pending' && !n.skipped) && (
                  <Popconfirm
                    title="批量标记完成"
                    description="将前几个未开始节点标记为已完成？"
                    onConfirm={() => {
                      const pendingIds = pathNodes.filter((n) => n.status === 'pending' && !n.skipped).slice(0, 3).map((n) => n.id)
                      handleBatchComplete(pendingIds)
                    }}
                    okText="确认"
                    cancelText="取消"
                  >
                    <Button block className="rounded-lg border-slate-200">
                      批量标记前 3 个节点为已完成
                    </Button>
                  </Popconfirm>
                )}
              </div>
            )}

            {/* 智能微调 Tab */}
            {activeAdjustTab === 'feedback' && (
              <div className="space-y-6">
                <div className="p-3 rounded-xl bg-indigo-50 border border-indigo-100">
                  <Typography.Text className="text-xs text-indigo-700 block leading-relaxed">
                    通过自然语言描述你的调整需求，AI 将在现有路径基础上做局部优化，而不会完全重置路径。
                  </Typography.Text>
                </div>

                <div>
                  <Typography.Text className="font-semibold text-slate-800 block mb-2 text-sm">调整反馈</Typography.Text>
                  <Input.TextArea
                    rows={4}
                    value={adjustFeedback}
                    onChange={(e) => setAdjustFeedback(e.target.value)}
                    placeholder="例如：指针部分太难了，希望多加一些基础练习；或者我想跳过文件操作，直接学动态内存..."
                    className="rounded-xl bg-slate-50 border-slate-200"
                  />
                </div>

                <div className="flex flex-wrap gap-2">
                  {[
                    '指针部分太难，多加点基础练习',
                    '我想加快进度，减少理论讲解',
                    '跳过文件操作，优先学动态内存',
                    '增加更多实战项目',
                  ].map((tip) => (
                    <Tag
                      key={tip}
                      className="rounded-full border-slate-200 text-slate-600 text-xs cursor-pointer hover:border-primary hover:text-primary transition-all"
                      onClick={() => setAdjustFeedback(tip)}
                    >
                      {tip}
                    </Tag>
                  ))}
                </div>

                <Button type="primary" block className="rounded-lg bg-primary h-10" onClick={handleAdjustPath} loading={loading}>
                  智能微调路径 <ArrowRightOutlined />
                </Button>
              </div>
            )}
          </div>
        )}
      </Drawer>
    </div>
  )
}

export default LearningPathPage
