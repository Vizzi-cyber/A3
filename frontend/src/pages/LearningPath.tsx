import React, { useEffect, useState } from 'react'
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
import { pathApi, profileApi } from '../services/api'
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

const nodeResources = [
  { title: 'C语言基础视频讲解', type: 'video', icon: <PlayCircleOutlined />, color: '#ef4444' },
  { title: '指针与内存代码示例', type: 'code', icon: <CodeOutlined />, color: '#3b82f6' },
  { title: '数据结构学习笔记', type: 'doc', icon: <FileTextOutlined />, color: '#10b981' },
  { title: '算法练习题 x10', type: 'quiz', icon: <BookOutlined />, color: '#f59e0b' },
]

const LearningPathPage: React.FC = () => {
  const [viewMode, setViewMode] = useState<'map' | 'timeline' | 'graph'>('map')
  const [drawerOpen, setDrawerOpen] = useState(false)
  const [selectedNode, setSelectedNode] = useState<PathNode | null>(null)
  const [pathData, setPathData] = useState<Record<string, unknown> | null>(null)
  const [pathNodes, setPathNodes] = useState<PathNode[]>([])
  const [loading, setLoading] = useState(false)
  const [showReviewAlert, setShowReviewAlert] = useState(true)
  const [dailyDuration, setDailyDuration] = useState(90)
  const [difficulty, setDifficulty] = useState(3)
  const [learningPreference, setLearningPreference] = useState('balanced')
  const [targetTopic, setTargetTopic] = useState('掌握 C语言程序设计与数据结构基础')
  const [adjustFeedback, setAdjustFeedback] = useState('')
  const [profileSuggestions, setProfileSuggestions] = useState<string[]>([])
  const [activeAdjustTab, setActiveAdjustTab] = useState<'params' | 'nodes' | 'feedback'>('params')
  const studentId = useAppStore((s) => s.studentId)
  const navigate = useNavigate()

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
          const nodes: PathNode[] = res.data.nodes || [
            { id: 1, title: 'C语言概述与开发环境', status: 'completed', type: '入门', resources: 5 },
            { id: 2, title: '数据类型与变量', status: 'completed', type: '基础', resources: 5 },
            { id: 3, title: '运算符与表达式', status: 'in-progress', type: '基础', resources: 5 },
            { id: 4, title: '输入输出与顺序结构', status: 'pending', type: '基础', resources: 5 },
          ]
          setPathData(res.data as unknown as Record<string, unknown>)
          setPathNodes(nodes as PathNode[])
        }
      } catch (e) {
        setPathNodes([
          { id: 1, title: 'C语言概述与开发环境', status: 'completed', type: '入门', resources: 5 },
          { id: 2, title: '数据类型与变量', status: 'completed', type: '基础', resources: 5 },
          { id: 3, title: '运算符与表达式', status: 'in-progress', type: '基础', resources: 5 },
          { id: 4, title: '输入输出与顺序结构', status: 'pending', type: '基础', resources: 5 },
          { id: 5, title: '选择结构', status: 'locked', type: '核心', resources: 5 },
          { id: 6, title: '循环结构', status: 'locked', type: '核心', resources: 5 },
          { id: 7, title: '数组', status: 'locked', type: '核心', resources: 5 },
          { id: 8, title: '字符串', status: 'locked', type: '核心', resources: 5 },
          { id: 9, title: '函数与递归', status: 'locked', type: '核心', resources: 5 },
          { id: 10, title: '指针基础', status: 'locked', type: '进阶', resources: 5 },
          { id: 11, title: '指针与数组', status: 'locked', type: '进阶', resources: 5 },
          { id: 12, title: '结构体与联合体', status: 'locked', type: '进阶', resources: 5 },
          { id: 13, title: '文件操作', status: 'locked', type: '进阶', resources: 5 },
          { id: 14, title: '动态内存管理', status: 'locked', type: '高级', resources: 5 },
        ])
      }
    }
    load()
  }, [studentId])

  const openNodeDetail = (node: PathNode) => {
    setSelectedNode(node)
    setDrawerOpen(true)
  }

  const handleGeneratePath = async () => {
    setLoading(true)
    try {
      const res = await pathApi.generate({
        student_id: studentId,
        target_topic: '掌握 C语言程序设计与数据结构基础',
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

  const handleNodeAction = (nodeId: number, action: 'complete' | 'skip' | 'reset') => {
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

  const handleBatchComplete = (ids: number[]) => {
    setPathNodes((prev) =>
      prev.map((n) => (ids.includes(n.id) ? { ...n, status: 'completed' } : n))
    )
    message.success(`已批量标记 ${ids.length} 个节点为已完成`)
  }

  const completedCount = pathNodes.filter((n) => n.status === 'completed').length
  const progress = pathNodes.length ? Math.round((completedCount / pathNodes.length) * 100) : 0

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
              <Typography.Title level={4} className="!m-0 text-slate-800">C语言程序设计学习路径</Typography.Title>
              <Typography.Text className="text-slate-400 text-xs">编程基础方向 · 共 {pathNodes.length} 个阶段</Typography.Text>
            </div>
          </Space>
          <Space>
            <Radio.Group value={viewMode} onChange={(e) => setViewMode(e.target.value)} buttonStyle="solid" className="rounded-lg overflow-hidden">
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
      {showReviewAlert && (
        <div className="bg-amber-50 border border-amber-100 rounded-2xl p-4 flex items-center gap-3">
          <ExclamationCircleOutlined className="text-amber-500 text-lg" />
          <div className="flex-1">
            <div className="text-sm font-medium text-amber-800">遗忘曲线提醒：有 3 个知识点需要今日复习</div>
            <div className="text-xs text-amber-600">数据类型与变量、控制结构、指针与内存 — 基于艾宾浩斯遗忘曲线计算</div>
          </div>
          <Button size="small" className="rounded-lg border-amber-200 text-amber-700" onClick={() => setShowReviewAlert(false)}>
            稍后提醒
          </Button>
          <Button size="small" type="primary" className="rounded-lg bg-amber-500 border-amber-500">
            <ReloadOutlined /> 开始复习
          </Button>
        </div>
      )}

      {/* 地图视图 — 统一垂直布局 */}
      {viewMode === 'map' && (
        <div className="bg-white rounded-2xl border border-slate-100 p-8 md:p-10">
          <div className="relative max-w-2xl mx-auto">
            <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-slate-100" />
            <div className="space-y-8">
              {pathNodes.map((node) => (
                <div key={node.id} className="flex items-start gap-5 relative">
                  <div
                    className="relative z-10 w-12 h-12 rounded-full flex items-center justify-center text-white text-lg shrink-0 shadow-sm"
                    style={{ background: statusColors[node.status] }}
                    onClick={() => openNodeDetail(node)}
                  >
                    {node.status === 'completed' ? <CheckCircleOutlined /> :
                     node.status === 'in-progress' ? <ClockCircleOutlined /> :
                     node.status === 'locked' ? <LockOutlined /> :
                     <EnvironmentOutlined />}
                  </div>
                  <div
                    className="flex-1 p-5 rounded-xl bg-white border border-slate-100 hover:border-slate-200 hover:shadow-card transition-all cursor-pointer"
                    onClick={() => openNodeDetail(node)}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <Tag
                        className="rounded-full border-0 text-xs font-medium"
                        style={{ background: statusBg[node.status], color: statusColors[node.status] }}
                      >
                        {statusLabels[node.status]}
                      </Tag>
                      <span className="text-xs text-slate-400">{node.type}</span>
                    </div>
                    <Typography.Text className="font-bold text-slate-800 text-lg block">{node.title}</Typography.Text>
                    <Typography.Text className="text-slate-400 text-sm">{node.resources} 个学习资源</Typography.Text>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* 时间轴视图 */}
      {viewMode === 'timeline' && (
        <div className="bg-white rounded-2xl border border-slate-100 p-8 md:p-10">
          <Timeline
            mode="left"
            items={pathNodes.map((node) => ({
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
            }))}
          />
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
            <div className="flex flex-wrap justify-center gap-4">
              {[
                { id: 1, title: 'C语言概述', level: 1, status: 'completed', type: '基础' },
                { id: 2, title: '数据类型与变量', level: 1, status: 'completed', type: '基础' },
                { id: 3, title: '运算符与表达式', level: 2, status: 'in-progress', type: '基础' },
                { id: 4, title: '输入输出', level: 2, status: 'pending', type: '基础' },
                { id: 5, title: '选择结构', level: 2, status: 'locked', type: '核心' },
                { id: 6, title: '循环结构', level: 3, status: 'locked', type: '核心' },
                { id: 7, title: '数组', level: 3, status: 'locked', type: '核心' },
                { id: 8, title: '字符串', level: 3, status: 'locked', type: '核心' },
                { id: 9, title: '函数与递归', level: 4, status: 'locked', type: '进阶' },
                { id: 10, title: '指针基础', level: 4, status: 'locked', type: '进阶' },
                { id: 11, title: '结构体', level: 4, status: 'locked', type: '进阶' },
                { id: 12, title: '文件操作', level: 5, status: 'locked', type: '高级' },
              ].map((node) => (
                <div key={node.id} className="flex flex-col items-center">
                  <div
                    className="w-32 p-3 rounded-xl border text-center cursor-pointer transition-all hover:shadow-card"
                    style={{
                      borderColor: statusColors[node.status],
                      background: statusBg[node.status],
                    }}
                    onClick={() => openNodeDetail(node as PathNode)}
                  >
                    <div className="text-xs text-slate-400 mb-1">L{node.level}</div>
                    <div className="text-sm font-medium text-slate-800">{node.title}</div>
                  </div>
                  {node.id < 12 && <div className="h-6 w-0.5 bg-slate-200 my-1" />}
                </div>
              ))}
            </div>
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
        onClose={() => { setDrawerOpen(false); setSelectedNode(null) }}
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
              <List
                itemLayout="horizontal"
                dataSource={nodeResources}
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
            </div>

            {selectedNode.status === 'completed' && (
              <div>
                <Typography.Text className="font-semibold text-slate-800 block mb-3 text-sm">学习反思</Typography.Text>
                <div className="space-y-3">
                  <Input.TextArea
                    rows={4}
                    placeholder="完成这个节点后，你学到了什么？有哪些收获或疑问？"
                    className="rounded-xl bg-slate-50 border-slate-200"
                  />
                  <Button className="rounded-lg border-slate-200">提交反思</Button>
                </div>
              </div>
            )}

            <Button
              type="primary"
              block
              className="rounded-lg bg-primary h-10"
              onClick={() => {
                const nodeKpId = selectedNode.kp_id || selectedNode.id
                navigate(`/resource/${nodeKpId}`)
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
                              navigate(`/resource/${node.kp_id || node.id}`)
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
