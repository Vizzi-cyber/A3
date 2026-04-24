import React, { useEffect, useState, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Typography, Card, Button, Tag, Space, Tabs, Input, List, Avatar, Spin,
  message, Badge, Tooltip, Progress, Radio
} from 'antd'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import {
  CodeOutlined, MessageOutlined, CheckCircleOutlined,
  ArrowLeftOutlined, SendOutlined, PlayCircleOutlined, TrophyOutlined,
  EditOutlined, ReadOutlined, LoadingOutlined,
  RobotOutlined, FireOutlined, StarOutlined,
  CopyOutlined, UserOutlined,
} from '@ant-design/icons'
import { useAppStore } from '../store'
import {
  resourceApi, tutorApi, knowledgeApi, learningDataApi, logReflectionApi,
} from '../services/api'
import type { ChatMessage, QuestionItem, QuestionOption } from '../types'

const ResourceDetail: React.FC = () => {
  const { kpId } = useParams<{ kpId: string }>()
  const navigate = useNavigate()
  const studentId = useAppStore((s) => s.studentId)

  const [kpName, setKpName] = useState('')
  const [kpSubject, setKpSubject] = useState('')
  const [loading, setLoading] = useState(true)

  // 讲义
  const [docContent, setDocContent] = useState('')

  // 代码
  const [codeContent, setCodeContent] = useState('')
  const [codeLanguage, setCodeLanguage] = useState<'Python' | 'C'>('C')
  const [codeResult, setCodeResult] = useState('')
  const [codeRunning, setCodeRunning] = useState(false)

  // 练习
  const [questions, setQuestions] = useState<QuestionItem[]>([])
  const [quizAnswers, setQuizAnswers] = useState<Record<string, string>>({})
  const [quizSubmitted, setQuizSubmitted] = useState<Record<string, boolean>>({})
  const [quizScore, setQuizScore] = useState<number | null>(null)
  const [quizSubmitting, setQuizSubmitting] = useState(false)

  // AI 辅导
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([
    { role: 'ai', content: '你好！我是你的 AI 学习助手。关于本知识点有任何疑问，随时问我。', agent: '辅导助手' },
  ])
  const [chatInput, setChatInput] = useState('')
  const [chatLoading, setChatLoading] = useState(false)
  const chatEndRef = useRef<HTMLDivElement>(null)

  // 笔记
  const [notes, setNotes] = useState('')
  const [savingNotes, setSavingNotes] = useState(false)

  // 完成状态
  const [completed, setCompleted] = useState(false)
  const [completing, setCompleting] = useState(false)

  // 加载知识点信息
  useEffect(() => {
    if (!kpId) return
    let ignore = false
    const load = async () => {
      try {
        const res = await knowledgeApi.get(kpId)
        if (!ignore && res.data?.data) {
          setKpName(res.data.data.name || '')
          setKpSubject(res.data.data.subject || '')
        }
      } catch {
        if (!ignore) {
          setKpName(`知识点 ${kpId}`)
        }
      }
    }
    load()
    return () => { ignore = true }
  }, [kpId])

  // 加载讲义 + 代码 + 练习
  useEffect(() => {
    if (!kpId) return
    let ignore = false
    const load = async () => {
      setLoading(true)
      try {
        const [docRes, codeRes, qRes] = await Promise.all([
          resourceApi.generateDocument({ student_id: studentId, topic: kpName, kp_id: kpId }),
          resourceApi.generateCode({ student_id: studentId, topic: kpName, language: codeLanguage, kp_id: kpId }),
          resourceApi.generateQuestions({ student_id: studentId, topic: kpName, count: 5, kp_id: kpId }),
        ])
        if (!ignore) {
          setDocContent(docRes.data.document || '')
          setCodeContent(codeRes.data.code || '')
          setQuestions(qRes.data.questions || [])
        }
      } catch (e) {
        if (!ignore) message.error('资源加载失败')
      } finally {
        if (!ignore) setLoading(false)
      }
    }
    load()
    return () => { ignore = true }
  }, [kpId, kpName, studentId, codeLanguage])

  // 自动滚动到聊天底部
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [chatMessages])

  // 运行代码
  const handleRunCode = async () => {
    if (!codeContent) return
    setCodeRunning(true)
    setCodeResult('')
    try {
      const res = await resourceApi.executeCode({ code: codeContent, language: codeLanguage.toLowerCase(), kp_id: kpId })
      setCodeResult(res.data.output || res.data.error || '无输出')
    } catch (e: any) {
      setCodeResult(e.message || '运行失败')
    } finally {
      setCodeRunning(false)
    }
  }

  // 提交练习
  const handleSubmitQuiz = async () => {
    if (!questions.length) return
    setQuizSubmitting(true)
    let correct = 0
    const submitted: Record<string, boolean> = {}
    questions.forEach((q) => {
      const ans = quizAnswers[q.q_id]
      const isCorrect = ans === q.correct_answer
      if (isCorrect) correct++
      submitted[q.q_id] = isCorrect
    })
    setQuizSubmitted(submitted)
    setQuizScore(Math.round((correct / questions.length) * 100))
    setQuizSubmitting(false)
    message.success(`答对 ${correct}/${questions.length} 题`)
  }

  // AI 辅导对话
  const handleSendChat = async () => {
    if (!chatInput.trim() || chatLoading) return
    const userMsg: ChatMessage = { role: 'user', content: chatInput }
    setChatMessages((prev) => [...prev, userMsg])
    setChatInput('')
    setChatLoading(true)
    try {
      const res = await tutorApi.ask({
        student_id: studentId,
        question: chatInput,
        context: { topic: kpName, kp_id: kpId },
      })
      setChatMessages((prev) => [
        ...prev,
        { role: 'ai', content: res.data.response, agent: '辅导助手' },
      ])
    } catch {
      message.error('AI 响应失败')
    } finally {
      setChatLoading(false)
    }
  }

  // 保存笔记
  const handleSaveNotes = async () => {
    if (!notes.trim()) return
    setSavingNotes(true)
    try {
      await logReflectionApi.createReflection({
        student_id: studentId,
        date: new Date().toISOString().split('T')[0],
        content: notes,
        tags: ['notes', kpId || ''],
      })
      message.success('笔记已保存')
    } catch {
      message.error('保存失败')
    } finally {
      setSavingNotes(false)
    }
  }

  // 标记完成
  const handleComplete = async () => {
    if (!kpId) return
    setCompleting(true)
    try {
      await learningDataApi.record({
        student_id: studentId,
        kp_id: kpId,
        action: 'complete',
        duration: 30,
        progress: 1,
        score: quizScore ?? undefined,
      })
      setCompleted(true)
      message.success('恭喜完成本知识点学习！')
    } catch {
      message.error('标记失败')
    } finally {
      setCompleting(false)
    }
  }

  // 复制代码
  const handleCopyCode = () => {
    navigator.clipboard.writeText(codeContent).then(() => message.success('已复制'))
  }

  if (!kpId) {
    return (
      <div className="flex items-center justify-center h-96">
        <Typography.Text className="text-slate-400">知识点参数缺失</Typography.Text>
      </div>
    )
  }

  const tabItems = [
    {
      key: 'doc',
      label: (
        <span className="flex items-center gap-1">
          <ReadOutlined /> 图文讲义
        </span>
      ),
      children: (
        <Spin spinning={loading}>
          <div className="prose prose-slate max-w-none">
            {docContent ? (
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{docContent}</ReactMarkdown>
            ) : (
              <div className="text-slate-400 text-center py-12">讲义内容加载中...</div>
            )}
          </div>
        </Spin>
      ),
    },
    {
      key: 'code',
      label: (
        <span className="flex items-center gap-1">
          <CodeOutlined /> 代码实操
        </span>
      ),
      children: (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <Space>
              <Radio.Group
                value={codeLanguage}
                onChange={(e) => setCodeLanguage(e.target.value)}
                buttonStyle="solid"
                className="rounded-lg overflow-hidden"
              >
                <Radio.Button value="C">C</Radio.Button>
                <Radio.Button value="Python">Python</Radio.Button>
              </Radio.Group>
            </Space>
            <Space>
              <Button size="small" icon={<CopyOutlined />} onClick={handleCopyCode}>复制</Button>
              <Button
                type="primary"
                size="small"
                icon={<PlayCircleOutlined />}
                loading={codeRunning}
                onClick={handleRunCode}
                className="bg-primary"
              >
                运行
              </Button>
            </Space>
          </div>
          <Input.TextArea
            value={codeContent}
            onChange={(e) => setCodeContent(e.target.value)}
            rows={14}
            className="font-mono text-sm rounded-xl bg-slate-900 text-slate-50 border-0"
          />
          {codeResult && (
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 font-mono text-sm whitespace-pre-wrap">
              {codeResult}
            </div>
          )}
        </div>
      ),
    },
    {
      key: 'quiz',
      label: (
        <span className="flex items-center gap-1">
          <TrophyOutlined /> 练习测试
        </span>
      ),
      children: (
        <div className="space-y-6">
          {quizScore !== null && (
            <div className="flex items-center gap-3 p-4 rounded-xl bg-slate-50 border border-slate-100">
              <Progress
                type="circle"
                percent={quizScore}
                size={64}
                strokeColor={quizScore >= 80 ? '#10b981' : quizScore >= 60 ? '#f59e0b' : '#ef4444'}
              />
              <div>
                <div className="font-bold text-slate-800">
                  {quizScore >= 80 ? '优秀！' : quizScore >= 60 ? '不错，继续加油' : '需要多复习'}
                </div>
                <div className="text-xs text-slate-400">答对 {Math.round((quizScore / 100) * questions.length)}/{questions.length} 题</div>
              </div>
            </div>
          )}
          {questions.length === 0 && !loading ? (
            <div className="text-slate-400 text-center py-12">暂无练习题</div>
          ) : (
            <List
              itemLayout="vertical"
              dataSource={questions}
              renderItem={(q, idx) => (
                <List.Item className="border border-slate-100 rounded-xl p-5 mb-4 hover:shadow-card transition-all">
                  <div className="flex items-start gap-3">
                    <Badge count={idx + 1} style={{ backgroundColor: '#4f46e5' }} />
                    <div className="flex-1">
                      <Typography.Text className="font-medium text-slate-800 block mb-3">{q.content}</Typography.Text>
                      <Radio.Group
                        value={quizAnswers[q.q_id]}
                        onChange={(e) => setQuizAnswers((prev) => ({ ...prev, [q.q_id]: e.target.value }))}
                        className="flex flex-col gap-2"
                      >
                        {q.options?.map((opt: QuestionOption) => (
                          <Radio
                            key={opt.id}
                            value={opt.id}
                            className={`text-sm ${quizSubmitted[q.q_id] ? (opt.id === q.correct_answer ? 'text-emerald-600' : quizAnswers[q.q_id] === opt.id ? 'text-red-500' : '') : ''}`}
                            disabled={quizSubmitted[q.q_id] !== undefined}
                          >
                            {opt.text}
                          </Radio>
                        ))}
                      </Radio.Group>
                      {quizSubmitted[q.q_id] !== undefined && (
                        <div className={`mt-3 text-xs p-3 rounded-lg ${quizSubmitted[q.q_id] ? 'bg-emerald-50 text-emerald-700' : 'bg-red-50 text-red-700'}`}>
                          <strong>解析：</strong>{q.explanation || (quizSubmitted[q.q_id] ? '回答正确！' : '回答错误，请查看正确答案。')}
                        </div>
                      )}
                    </div>
                  </div>
                </List.Item>
              )}
            />
          )}
          {questions.length > 0 && Object.keys(quizSubmitted).length === 0 && (
            <Button type="primary" loading={quizSubmitting} onClick={handleSubmitQuiz} className="rounded-lg bg-primary">
              提交答案
            </Button>
          )}
        </div>
      ),
    },
    {
      key: 'chat',
      label: (
        <span className="flex items-center gap-1">
          <RobotOutlined /> AI 辅导
        </span>
      ),
      children: (
        <div className="flex flex-col h-[520px] border border-slate-100 rounded-xl overflow-hidden">
          <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-50/50">
            {chatMessages.map((msg, idx) => (
              <div key={idx} className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
                <Avatar
                  size="small"
                  icon={msg.role === 'user' ? <UserOutlined /> : <RobotOutlined />}
                  className={msg.role === 'user' ? 'bg-primary' : 'bg-emerald-500'}
                />
                <div className={`max-w-[80%] px-4 py-3 rounded-2xl text-sm leading-relaxed ${
                  msg.role === 'user'
                    ? 'bg-primary text-white rounded-br-md'
                    : 'bg-white border border-slate-100 text-slate-700 rounded-bl-md'
                }`}>
                  {msg.role === 'ai' && msg.agent && (
                    <div className="text-xs text-slate-400 mb-1">{msg.agent}</div>
                  )}
                  {typeof msg.content === 'string' ? msg.content : JSON.stringify(msg.content)}
                </div>
              </div>
            ))}
            {chatLoading && (
              <div className="flex gap-3">
                <Avatar size="small" icon={<RobotOutlined />} className="bg-emerald-500" />
                <div className="px-4 py-3 rounded-2xl bg-white border border-slate-100 text-slate-400 text-sm">
                  <LoadingOutlined className="mr-2" />
                  思考中...
                </div>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>
          <div className="p-3 bg-white border-t border-slate-100">
            <Input.Search
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              onSearch={handleSendChat}
              placeholder="输入你的问题..."
              enterButton={<SendOutlined />}
              loading={chatLoading}
              className="rounded-lg"
            />
          </div>
        </div>
      ),
    },
    {
      key: 'notes',
      label: (
        <span className="flex items-center gap-1">
          <EditOutlined /> 学习笔记
        </span>
      ),
      children: (
        <div className="space-y-4">
          <Input.TextArea
            rows={12}
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="在这里记录学习笔记，数据会同步到画像分析..."
            className="rounded-xl bg-slate-50 border-slate-200"
          />
          <Button type="primary" loading={savingNotes} onClick={handleSaveNotes} className="rounded-lg bg-primary">
            保存笔记
          </Button>
        </div>
      ),
    },
  ]

  return (
    <div className="space-y-5">
      {/* 顶部导航栏 */}
      <div className="flex items-center justify-between">
        <Space>
          <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/learning-path')} className="rounded-lg border-slate-200">
            返回路径
          </Button>
          <div>
            <Typography.Title level={4} className="!m-0 text-slate-900">
              {kpName || '知识点学习'}
            </Typography.Title>
            {kpSubject && (
              <Typography.Text className="text-slate-400 text-xs">{kpSubject}</Typography.Text>
            )}
          </div>
        </Space>
        <Space>
          <Tooltip title="完成学习后可获得经验值">
            <Tag icon={<FireOutlined />} className="rounded-full border-0 bg-amber-50 text-amber-600 text-xs">
              完成后 +20 XP
            </Tag>
          </Tooltip>
          <Button
            type="primary"
            icon={completed ? <CheckCircleOutlined /> : <StarOutlined />}
            loading={completing}
            onClick={handleComplete}
            disabled={completed}
            className="rounded-lg bg-primary"
          >
            {completed ? '已完成' : '标记完成'}
          </Button>
        </Space>
      </div>

      {/* 主体内容 */}
      <Card className="border border-slate-100 rounded-2xl shadow-card" styles={{ body: { padding: '24px' } }}>
        <Spin spinning={loading}>
          <Tabs
            defaultActiveKey="doc"
            items={tabItems}
            className="resource-detail-tabs"
          />
        </Spin>
      </Card>
    </div>
  )
}

export default ResourceDetail
