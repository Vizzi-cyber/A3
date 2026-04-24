import React, { useEffect, useState } from 'react'
import { Typography, Card, Button, Tag, Space, Timeline, Drawer, Slider, Radio, Progress, Avatar, List, message, Input, Badge, Tooltip } from 'antd'
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
} from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import { useAppStore } from '../store'
import { pathApi } from '../services/api'

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
  const [selectedNode, setSelectedNode] = useState<any | null>(null)
  const [pathData, setPathData] = useState<any>(null)
  const [pathNodes, setPathNodes] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [showReviewAlert, setShowReviewAlert] = useState(true)
  const [dailyDuration, setDailyDuration] = useState(90)
  const [difficulty, setDifficulty] = useState(3)
  const [learningPreference, setLearningPreference] = useState('balanced')
  const studentId = useAppStore((s) => s.studentId)
  const navigate = useNavigate()

  useEffect(() => {
    const load = async () => {
      try {
        const res: any = await pathApi.current(studentId)
        if (res.data) {
          const nodes = res.data.nodes || [
            { id: 1, title: 'C语言概述与开发环境', status: 'completed', type: '入门', resources: 5 },
            { id: 2, title: '数据类型与变量', status: 'completed', type: '基础', resources: 5 },
            { id: 3, title: '运算符与表达式', status: 'in-progress', type: '基础', resources: 5 },
            { id: 4, title: '输入输出与顺序结构', status: 'pending', type: '基础', resources: 5 },
          ]
          setPathData(res.data)
          setPathNodes(nodes)
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

  const openNodeDetail = (node: any) => {
    setSelectedNode(node)
    setDrawerOpen(true)
  }

  const handleGeneratePath = async () => {
    setLoading(true)
    try {
      const res: any = await pathApi.generate({
        student_id: studentId,
        target_topic: '掌握 C语言程序设计与数据结构基础',
        daily_duration: dailyDuration,
        difficulty: difficulty,
        preference: learningPreference,
      })
      const stages = res.data?.path?.stages || []
      const nodes = stages.map((s: any, idx: number) => ({
        id: idx + 1,
        title: s.title,
        status: idx === 0 ? 'in-progress' : 'pending',
        type: s.resources?.[0] || '综合',
        resources: s.topics?.length || 3,
      }))
      setPathNodes(nodes)
      setPathData(res.data)
      message.success('路径生成成功')
    } catch (e: any) {
      message.error(e.message || '生成失败')
    } finally {
      setLoading(false)
    }
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
                { id: 1, title: 'C语言概述', level: 1, status: 'completed' },
                { id: 2, title: '数据类型与变量', level: 1, status: 'completed' },
                { id: 3, title: '运算符与表达式', level: 2, status: 'in-progress' },
                { id: 4, title: '输入输出', level: 2, status: 'pending' },
                { id: 5, title: '选择结构', level: 2, status: 'locked' },
                { id: 6, title: '循环结构', level: 3, status: 'locked' },
                { id: 7, title: '数组', level: 3, status: 'locked' },
                { id: 8, title: '字符串', level: 3, status: 'locked' },
                { id: 9, title: '函数与递归', level: 4, status: 'locked' },
                { id: 10, title: '指针基础', level: 4, status: 'locked' },
                { id: 11, title: '结构体', level: 4, status: 'locked' },
                { id: 12, title: '文件操作', level: 5, status: 'locked' },
              ].map((node) => (
                <div key={node.id} className="flex flex-col items-center">
                  <div
                    className="w-32 p-3 rounded-xl border text-center cursor-pointer transition-all hover:shadow-card"
                    style={{
                      borderColor: statusColors[node.status],
                      background: statusBg[node.status],
                    }}
                    onClick={() => openNodeDetail(node)}
                  >
                    <div className="text-xs text-slate-400 mb-1">L{node.level}</div>
                    <div className="text-sm font-medium text-slate-800">{node.title}</div>
                  </div>
                  {node.id < 12 && <div className="h-6 w-0.5 bg-slate-200 my-1" />}
                </div>
              ))}
            </div>
            <div className="mt-6 flex flex-wrap gap-2 justify-center">
              {pathNodes.filter((n: any) => n.status === 'completed').map((n: any) => (
                <Tag key={n.id} className="rounded-full border-0 bg-emerald-50 text-emerald-600 text-xs">{n.title}</Tag>
              ))}
              {pathNodes.filter((n: any) => n.status === 'in-progress').map((n: any) => (
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
                const kpId = selectedNode.kp_id || selectedNode.id
                navigate('/resource', { state: { kpId, title: selectedNode.title } })
                setDrawerOpen(false)
              }}
            >
              {selectedNode.status === 'completed' ? '重新学习' : '开始学习'} <ArrowRightOutlined />
            </Button>
          </div>
        ) : (
          <div className="space-y-8">
            <div>
              <Typography.Text className="font-semibold text-slate-800 block mb-3 text-sm">学习偏好</Typography.Text>
              <Radio.Group value={learningPreference} onChange={(e) => setLearningPreference(e.target.value)} className="flex flex-col gap-3">
                <Radio value="theory" className="text-sm">加强理论</Radio>
                <Radio value="practice" className="text-sm">多些练习</Radio>
                <Radio value="balanced" className="text-sm">平衡模式</Radio>
              </Radio.Group>
            </div>

            <div>
              <Typography.Text className="font-semibold text-slate-800 block mb-3 text-sm">每日学习时长</Typography.Text>
              <Slider min={30} max={240} step={15} value={dailyDuration} onChange={setDailyDuration} marks={{ 30: '30m', 120: '2h', 240: '4h' }} tooltip={{ formatter: (v) => `${v}分钟` }} />
            </div>

            <div>
              <Typography.Text className="font-semibold text-slate-800 block mb-3 text-sm">难度偏好</Typography.Text>
              <Slider min={1} max={5} step={1} value={difficulty} onChange={setDifficulty} marks={{ 1: '简单', 3: '适中', 5: '挑战' }} />
            </div>

            <Button type="primary" block className="rounded-lg bg-primary h-10" onClick={() => { handleGeneratePath(); setDrawerOpen(false); }} loading={loading}>
              重新规划路径 <ArrowRightOutlined />
            </Button>
          </div>
        )}
      </Drawer>
    </div>
  )
}

export default LearningPathPage
