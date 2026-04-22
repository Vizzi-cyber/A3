import React, { useState, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import {
  Typography, Card, Button, Input, Space, Tabs, Tag, Collapse,
  FloatButton, message, Spin, Tooltip, Badge, Modal
} from 'antd'
import {
  FileTextOutlined,
  CodeOutlined,
  MessageOutlined,
  EditOutlined,
  MenuFoldOutlined,
  BookOutlined,
  CheckCircleOutlined,
  ReadOutlined,
  ArrowRightOutlined,
  CopyOutlined,
  BulbOutlined,
  NodeIndexOutlined,
  FormOutlined,
  CameraOutlined,
  LikeOutlined,
  DislikeOutlined,
  SafetyOutlined,
  ToolOutlined,
  ApartmentOutlined,
  ThunderboltOutlined,
  StarOutlined,
  ReloadOutlined,
} from '@ant-design/icons'
import { useAppStore } from '../store'
import { resourceApi, tutorApi } from '../services/api'
import type { ChatMessage, QuestionItem, VisionContentItem } from '../types'
import { ChatPanel } from '../components/ChatPanel'

const { Panel } = Collapse

const courseMenu = [
  {
    key: 'chapter1',
    icon: <BookOutlined />,
    label: '第一章：机器学习概述',
    children: [
      { key: '1-1', label: '1.1 什么是机器学习', completed: true },
      { key: '1-2', label: '1.2 监督与无监督学习', completed: true },
      { key: '1-3', label: '1.3 机器学习基本流程', completed: false },
    ],
  },
  {
    key: 'chapter2',
    icon: <BookOutlined />,
    label: '第二章：数学基础',
    children: [
      { key: '2-1', label: '2.1 线性代数基础', completed: false },
      { key: '2-2', label: '2.2 概率论与统计', completed: false },
      { key: '2-3', label: '2.3 梯度下降原理', completed: false },
    ],
  },
  {
    key: 'chapter3',
    icon: <BookOutlined />,
    label: '第三章：经典算法',
    children: [
      { key: '3-1', label: '3.1 线性回归', completed: false },
      { key: '3-2', label: '3.2 逻辑回归', completed: false },
      { key: '3-3', label: '3.3 神经网络基础', completed: false },
    ],
  },
  {
    key: 'chapter4',
    icon: <BookOutlined />,
    label: '第四章：深度学习进阶',
    children: [
      { key: '4-1', label: '4.1 反向传播算法', completed: false },
      { key: '4-2', label: '4.2 CNN与图像识别', completed: false },
      { key: '4-3', label: '4.3 大模型应用开发', completed: false },
    ],
  },
]

const ResourceCenter: React.FC = () => {
  const [activeKey, setActiveKey] = useState('2-1')
  const [chatOpen, setChatOpen] = useState(false)
  const [messages, setMessages] = useState<ChatMessage[]>([
    { role: 'ai', content: '你好！我正在和你一起学习《线性代数基础》。矩阵运算、特征值分解是后续理解神经网络的关键，有什么不懂的地方随时问我。', agent: '辅导助手' },
  ])
  const [notes, setNotes] = useState('')
  const [docContent, setDocContent] = useState(`
## 什么是机器学习？

机器学习（Machine Learning）是人工智能的一个分支，它让计算机通过**数据**自动学习和改进，而无需显式编程。

### 核心思想
传统编程：规则 + 数据 → 答案
机器学习：数据 + 答案 → 规则

### 三大类别
- **监督学习（Supervised Learning）**：使用带标签的数据训练模型，如分类、回归
- **无监督学习（Unsupervised Learning）**：从无标签数据中发现模式，如聚类、降维
- **强化学习（Reinforcement Learning）**：通过与环境交互获得奖励来学习策略

### 典型应用场景
| 领域 | 应用示例 |
|------|---------|
| 计算机视觉 | 图像分类、目标检测、人脸识别 |
| 自然语言处理 | 机器翻译、文本生成、情感分析 |
| 推荐系统 | 商品推荐、内容个性化推送 |
| 自动驾驶 | 环境感知、路径规划、决策控制 |

> 💡 **关键洞察**：机器学习的本质是**函数拟合**——找一个函数 $f$，使得 $f(X) \approx Y$。
`)
  const [codeContent, setCodeContent] = useState(`import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

# 生成示例数据
X = np.array([[1], [2], [3], [4], [5]])
y = np.array([2.1, 4.0, 6.1, 7.8, 10.2])

# 创建并训练模型
model = LinearRegression()
model.fit(X, y)

# 预测
X_test = np.array([[6]])
prediction = model.predict(X_test)

print(f"斜率: {model.coef_[0]:.2f}")
print(f"截距: {model.intercept_:.2f}")
print(f"x=6 时预测值: {prediction[0]:.2f}")

# 可视化
plt.scatter(X, y, color='blue', label='真实数据')
plt.plot(X, model.predict(X), color='red', label='拟合直线')
plt.legend()
plt.show()`)
  const [questions, setQuestions] = useState<QuestionItem[]>([])
  const [mindmap, setMindmap] = useState<{ root: string; children: { name: string }[] }>({ root: '机器学习概述', children: [] })
  const [loading, setLoading] = useState(false)
  const [resLoading, setResLoading] = useState(false)
  const [bottomTab, setBottomTab] = useState('code')
  const [resourceFeedback, setResourceFeedback] = useState<Record<string, 'good' | 'bad' | null>>({})
  const [cornellNotes, setCornellNotes] = useState({ cues: '', notes: '', summary: '' })
  const [feynmanMode, setFeynmanMode] = useState(false)
  const [feynmanInput, setFeynmanInput] = useState('')
  const [ragActive, setRagActive] = useState(true)
  const [multiAgentStep, setMultiAgentStep] = useState<'planner' | 'worker' | 'critic' | 'done'>('done')
  const [ocrModalOpen, setOcrModalOpen] = useState(false)
  const studentId = useAppStore((s) => s.studentId)

  const currentTopic = courseMenu.flatMap(c => c.children || []).find(c => c.key === activeKey)?.label || '线性代数基础'

  useEffect(() => {
    let ignore = false
    const load = async () => {
      setResLoading(true)
      try {
        const [docRes, codeRes, qRes, mapRes] = await Promise.all([
          resourceApi.generateDocument({ student_id: studentId, topic: currentTopic }),
          resourceApi.generateCode({ student_id: studentId, topic: currentTopic, language: 'Python' }),
          resourceApi.generateQuestions({ student_id: studentId, topic: currentTopic, count: 3 }),
          resourceApi.generateMindmap({ student_id: studentId, topic: currentTopic }),
        ])
        if (ignore) return
        if (docRes.data.document) setDocContent(docRes.data.document)
        if (codeRes.data.code) setCodeContent(codeRes.data.code)
        const qs = Array.isArray(qRes.data.questions) ? qRes.data.questions : []
        if (qs.length) setQuestions(qs)
        if (mapRes.data.mindmap) {
          setMindmap({
            root: mapRes.data.mindmap.root || currentTopic,
            children: (mapRes.data.mindmap.children || []) as { name: string }[],
          })
        }
      } catch (e) {
        if (!ignore) message.error('资源加载失败，显示默认内容')
      } finally {
        if (!ignore) setResLoading(false)
      }
    }
    load()
    return () => { ignore = true }
  }, [activeKey, studentId])

  const handleSend = async (content: string | VisionContentItem[]) => {
    const question = typeof content === 'string' ? content : ''
    if (!question.trim()) return
    setMessages((prev) => [...prev, { role: 'user', content: question }])
    setLoading(true)
    try {
      const res = await tutorApi.ask({ student_id: studentId, question, session_id: `${studentId}_resource` })
      setMessages((prev) => [...prev, { role: 'ai', content: res.data.response || '让我再想想...', agent: '辅导助手' }])
    } catch (e: unknown) {
      const errMsg = e instanceof Error ? e.message : '请求失败'
      message.error(errMsg)
      setMessages((prev) => [...prev, { role: 'ai', content: '服务暂时不可用。', agent: '辅导助手' }])
    } finally {
      setLoading(false)
    }
  }

  const copyCode = () => {
    navigator.clipboard.writeText(codeContent).then(() => message.success('代码已复制'))
  }

  return (
    <div className="space-y-5">
      {/* 顶部标题栏 */}
      <Card className="border border-slate-100 rounded-2xl" bodyStyle={{ padding: '20px 24px' }}>
        <div className="flex items-center justify-between flex-wrap gap-3">
          <Space>
            <div className="w-10 h-10 rounded-xl bg-slate-900 flex items-center justify-center text-white">
              <ReadOutlined />
            </div>
            <div>
              <Typography.Title level={4} className="!m-0 text-slate-800">{currentTopic}</Typography.Title>
              <Typography.Text className="text-slate-400 text-xs">人工智能导论 · 机器学习基础</Typography.Text>
            </div>
          </Space>
          <Space>
            <Tooltip title="OCR 拍照上传纸质笔记或错题">
              <Button className="rounded-lg border-slate-200" icon={<CameraOutlined />} onClick={() => setOcrModalOpen(true)}>
                OCR识图
              </Button>
            </Tooltip>
            <Tooltip title={ragActive ? 'RAG 检索增强已启用' : 'RAG 已关闭'}>
              <Tag className={`rounded-full border-0 text-xs cursor-pointer ${ragActive ? 'bg-indigo-50 text-indigo-600' : 'bg-slate-100 text-slate-400'}`} onClick={() => setRagActive(!ragActive)}>
                <ApartmentOutlined /> {ragActive ? 'RAG 检索中' : 'RAG 关闭'}
              </Tag>
            </Tooltip>
            <Button type="primary" className="rounded-lg bg-primary">
              <CheckCircleOutlined /> 标记完成
            </Button>
          </Space>
        </div>
      </Card>

      <div className="flex gap-5 items-start">
        {/* 左侧目录 */}
        <Card className="border border-slate-100 rounded-2xl w-56 hidden xl:block flex-shrink-0" bodyStyle={{ padding: '20px 16px' }}>
          <Typography.Text className="font-semibold text-slate-800 block mb-4 text-sm">课程目录</Typography.Text>
          <Collapse defaultActiveKey={['chapter1', 'chapter2']} ghost expandIconPosition="end">
            {courseMenu.map((chapter) => (
              <Panel header={<span className="font-medium text-slate-700 text-sm">{chapter.label}</span>} key={chapter.key}>
                <div className="flex flex-col gap-1">
                  {chapter.children?.map((item) => (
                    <Button
                      key={item.key}
                      type={activeKey === item.key ? 'primary' : 'text'}
                      className={`justify-start text-left rounded-lg text-sm transition-all ${activeKey === item.key ? 'bg-primary' : 'text-slate-600 hover:bg-slate-50'}`}
                      icon={item.completed ? <CheckCircleOutlined className="text-success text-xs" /> : <FileTextOutlined className={activeKey === item.key ? 'text-white text-xs' : 'text-slate-400 text-xs'} />}
                      onClick={() => setActiveKey(item.key)}
                    >
                      {item.label}
                    </Button>
                  ))}
                </div>
              </Panel>
            ))}
          </Collapse>
        </Card>

        {/* 中间主内容区 */}
        <div className="flex-1 min-w-0 space-y-5">
          {/* 图文讲义 */}
          <Card
            className="border border-slate-100 rounded-2xl"
            title={
              <Space>
                <FileTextOutlined className="text-primary" />
                <span className="font-semibold text-slate-800">图文讲义</span>
                {multiAgentStep !== 'done' && (
                  <Tag className="rounded-full border-0 bg-blue-50 text-blue-600 text-xs">
                    <ThunderboltOutlined className="mr-1" />
                    {multiAgentStep === 'planner' ? 'Planner 规划中' : multiAgentStep === 'worker' ? 'Worker 生成中' : 'Critic 审核中'}
                  </Tag>
                )}
              </Space>
            }
            extra={
              <Space>
                <Tag className="rounded-full border-0 bg-slate-100 text-slate-600 text-xs">{currentTopic}</Tag>
                <Button.Group className="rounded-lg overflow-hidden">
                  <Button size="small" icon={<LikeOutlined />} className={resourceFeedback[currentTopic] === 'good' ? 'text-emerald-600' : ''} onClick={() => setResourceFeedback({ ...resourceFeedback, [currentTopic]: 'good' })} />
                  <Button size="small" icon={<DislikeOutlined />} className={resourceFeedback[currentTopic] === 'bad' ? 'text-red-500' : ''} onClick={() => setResourceFeedback({ ...resourceFeedback, [currentTopic]: 'bad' })} />
                </Button.Group>
              </Space>
            }
            bodyStyle={{ padding: '40px' }}
          >
            <Spin spinning={resLoading}>
              <div className="prose max-w-none text-slate-700 leading-relaxed text-[15px]">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{docContent}</ReactMarkdown>
              </div>
            </Spin>
            {resourceFeedback[currentTopic] === 'bad' && (
              <div className="mt-4 p-3 rounded-xl bg-red-50 border border-red-100 text-xs text-red-600">
                已记录负反馈，系统将自动优化该资源生成的 Prompt。
              </div>
            )}
          </Card>

          {/* 下方辅助功能区 */}
          <Card className="border border-slate-100 rounded-2xl" bodyStyle={{ padding: '20px 24px' }}>
            <Tabs
              activeKey={bottomTab}
              onChange={setBottomTab}
              items={[
                {
                  key: 'code',
                  label: <span className="flex items-center gap-1.5 text-sm"><CodeOutlined /> 代码编辑器</span>,
                  children: (
                    <div className="space-y-3">
                      <div className="bg-slate-900 rounded-xl p-5 font-mono text-sm text-slate-200 relative">
                        <div className="flex items-center justify-between mb-4">
                          <div className="flex gap-2">
                            <div className="w-3 h-3 rounded-full bg-red-400" />
                            <div className="w-3 h-3 rounded-full bg-yellow-400" />
                            <div className="w-3 h-3 rounded-full bg-green-400" />
                          </div>
                          <Tooltip title="复制代码">
                            <Button type="text" size="small" icon={<CopyOutlined className="text-slate-400 hover:text-white" />} onClick={copyCode} />
                          </Tooltip>
                        </div>
                        <pre className="text-green-400"># 请在这里编写代码</pre>
                        <pre className="text-slate-200 whitespace-pre-wrap mt-2">{codeContent}</pre>
                      </div>
                      <Button type="primary" className="rounded-lg bg-primary">
                        <ArrowRightOutlined /> 运行代码
                      </Button>
                    </div>
                  ),
                },
                {
                  key: 'quiz',
                  label: <span className="flex items-center gap-1.5 text-sm"><BulbOutlined /> 练习题 ({questions.length})</span>,
                  children: (
                    <div className="space-y-3">
                      {questions.length === 0 && <Typography.Text className="text-slate-400">暂无练习题</Typography.Text>}
                      {questions.map((q, idx) => (
                        <Card key={idx} size="small" className="rounded-xl border-slate-100">
                          <Typography.Text className="font-medium text-slate-800 block mb-3">{idx + 1}. {q.content}</Typography.Text>
                          {q.options && (
                            <div className="space-y-2">
                              {q.options.map((opt) => (
                                <div key={opt.id} className="text-slate-600 px-3 py-2 rounded-lg bg-slate-50 hover:bg-indigo-50 hover:text-primary transition-colors cursor-pointer text-sm">
                                  {opt.id}. {opt.text}
                                </div>
                              ))}
                            </div>
                          )}
                          <Tag className="mt-3 rounded-full border-0 bg-emerald-50 text-emerald-600 text-xs">答案：{q.correct_answer}</Tag>
                        </Card>
                      ))}
                    </div>
                  ),
                },
                {
                  key: 'mindmap',
                  label: <span className="flex items-center gap-1.5 text-sm"><NodeIndexOutlined /> 思维导图</span>,
                  children: (
                    <Card className="rounded-xl bg-slate-50 border-slate-100">
                      <Typography.Title level={5} className="text-center text-slate-800 font-bold">{mindmap.root || currentTopic}</Typography.Title>
                      <div className="flex flex-wrap gap-2 justify-center mt-6">
                        {(mindmap.children || []).map((c, i) => (
                          <Tag key={i} className="rounded-full px-3 py-1 text-sm border-0 bg-white text-slate-600 shadow-sm">{c.name}</Tag>
                        ))}
                      </div>
                    </Card>
                  ),
                },
                {
                  key: 'notes',
                  label: <span className="flex items-center gap-1.5 text-sm"><FormOutlined /> 我的笔记</span>,
                  children: (
                    <div className="space-y-3">
                      <Input.TextArea rows={8} placeholder="在这里记录学习笔记，数据会同步到画像分析..." value={notes} onChange={(e) => setNotes(e.target.value)} className="rounded-xl bg-slate-50 border-slate-200" />
                      <Button type="primary" className="rounded-lg bg-primary">
                        <CheckCircleOutlined /> 保存笔记
                      </Button>
                    </div>
                  ),
                },
                {
                  key: 'cornell',
                  label: <span className="flex items-center gap-1.5 text-sm"><EditOutlined /> 康奈尔笔记</span>,
                  children: (
                    <div className="space-y-3">
                      <div className="grid grid-cols-3 gap-4">
                        <div className="col-span-1 space-y-2">
                          <div className="text-xs font-medium text-slate-500">线索栏 (Cues)</div>
                          <Input.TextArea rows={8} placeholder="记录关键词、问题..." value={cornellNotes.cues} onChange={(e) => setCornellNotes({ ...cornellNotes, cues: e.target.value })} className="rounded-xl bg-slate-50 border-slate-200" />
                        </div>
                        <div className="col-span-2 space-y-2">
                          <div className="text-xs font-medium text-slate-500">笔记栏 (Notes)</div>
                          <Input.TextArea rows={8} placeholder="记录课堂/阅读笔记..." value={cornellNotes.notes} onChange={(e) => setCornellNotes({ ...cornellNotes, notes: e.target.value })} className="rounded-xl bg-slate-50 border-slate-200" />
                        </div>
                      </div>
                      <div className="space-y-2">
                        <div className="text-xs font-medium text-slate-500">总结栏 (Summary)</div>
                        <Input.TextArea rows={3} placeholder="用一句话总结本页核心内容..." value={cornellNotes.summary} onChange={(e) => setCornellNotes({ ...cornellNotes, summary: e.target.value })} className="rounded-xl bg-slate-50 border-slate-200" />
                      </div>
                      <Button type="primary" className="rounded-lg bg-primary">
                        <CheckCircleOutlined /> 保存康奈尔笔记
                      </Button>
                    </div>
                  ),
                },
                {
                  key: 'feynman',
                  label: <span className="flex items-center gap-1.5 text-sm"><BulbOutlined /> 费曼学习</span>,
                  children: (
                    <div className="space-y-3">
                      <div className="p-4 rounded-xl bg-amber-50 border border-amber-100 text-sm text-amber-800">
                        <strong>费曼学习法：</strong>尝试用最简单的语言向一个"小孩"解释你学到的概念。如果你卡住了，就回到材料中重新学习。
                      </div>
                      <Input.TextArea rows={6} placeholder="用你自己的话，尝试向一个外行解释当前知识点..." value={feynmanInput} onChange={(e) => setFeynmanInput(e.target.value)} className="rounded-xl bg-slate-50 border-slate-200" />
                      <Button type="primary" className="rounded-lg bg-primary" onClick={() => { if (feynmanInput.trim()) { message.success('费曼练习已保存，AI 将帮你检查理解盲点'); setFeynmanInput(''); } }}>
                        <ThunderboltOutlined /> 提交费曼练习
                      </Button>
                    </div>
                  ),
                },
              ]}
            />
          </Card>
        </div>

        {/* 右侧 AI 辅导 */}
        {chatOpen && (
          <Card className="border border-slate-100 rounded-2xl w-72 flex-shrink-0 hidden lg:flex flex-col" bodyStyle={{ padding: '16px', height: '100%', display: 'flex', flexDirection: 'column' }}>
            <ChatPanel
              messages={messages}
              loading={loading}
              onSend={handleSend}
              title="AI 辅导助手"
              subtitle="苏格拉底式教学"
              placeholder="输入问题..."
              showAvatars={false}
              extraHeader={
                <Button type="text" size="small" icon={<MenuFoldOutlined className="text-slate-400" />} onClick={() => setChatOpen(false)} />
              }
            />
          </Card>
        )}
      </div>

      {/* OCR 拍照上传弹窗 */}
      <Modal
        title={<span className="font-semibold text-slate-800">OCR 拍照上传</span>}
        open={ocrModalOpen}
        onCancel={() => setOcrModalOpen(false)}
        footer={null}
        width={520}
        className="rounded-2xl"
      >
        <div className="space-y-4 py-2">
          <div className="p-6 rounded-xl bg-slate-50 border border-dashed border-slate-300 text-center cursor-pointer hover:border-primary transition-all">
            <CameraOutlined className="text-3xl text-slate-300 mb-2" />
            <div className="text-sm text-slate-600">点击或拖拽上传纸质笔记 / 错题照片</div>
            <div className="text-xs text-slate-400 mt-1">支持 JPG、PNG，基于 PaddleOCR 识别</div>
          </div>
          <div className="flex items-center gap-2 text-xs text-slate-400">
            <SafetyOutlined />
            <span>端云协同：本地 Edge 端完成 OCR 识别，原始图片不上传云端</span>
          </div>
        </div>
      </Modal>

      {!chatOpen && (
        <FloatButton icon={<MessageOutlined />} type="primary" tooltip="打开 AI 辅导" onClick={() => setChatOpen(true)} className="right-6 bottom-6" />
      )}
    </div>
  )
}

export default ResourceCenter
