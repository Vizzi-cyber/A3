import React, { useState, useEffect, useRef } from 'react'
import { useLocation } from 'react-router-dom'
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
  CloseCircleOutlined,
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
  PictureOutlined,
} from '@ant-design/icons'
import { useAppStore } from '../store'
import { resourceApi, tutorApi, imageApi, knowledgeApi, ocrApi, learningDataApi, logReflectionApi } from '../services/api'
import type { ChatMessage, QuestionItem, VisionContentItem } from '../types'
import { extractApiError } from '../utils/error'
import { useElapsedTime } from '../hooks/useElapsedTime'
import { ChatPanel } from '../components/ChatPanel'

interface CourseMenuItem {
  key: string
  icon: React.ReactNode
  label: string
  children: { key: string; label: string; completed: boolean }[]
}

const ResourceCenter: React.FC = () => {
  const [activeKey, setActiveKey] = useState('')
  // 知识点切换时记录起点，标记完成时上报真实停留时长
  const getElapsed = useElapsedTime([activeKey])
  const [courseMenu, setCourseMenu] = useState<CourseMenuItem[]>([])
  const [menuLoading, setMenuLoading] = useState(false)
  const [chatOpen, setChatOpen] = useState(false)
  const [messages, setMessages] = useState<ChatMessage[]>([
    { role: 'ai', content: '你好！我正在和你一起学习《C语言基础》。C语言是计算机专业的入门语言，掌握它对于理解计算机底层原理至关重要。有什么不懂的地方随时问我。', agent: '辅导助手' },
  ])
  const [notes, setNotes] = useState('')
  const [docContent, setDocContent] = useState('')
  const [codeContent, setCodeContent] = useState('')
  const [codeLanguage, setCodeLanguage] = useState<'Python' | 'C'>('C')
  const [questions, setQuestions] = useState<QuestionItem[]>([])
  const [quizAnswers, setQuizAnswers] = useState<Record<string, string>>({})
  const [quizSubmitted, setQuizSubmitted] = useState<Record<string, boolean>>({})
  const [quizScore, setQuizScore] = useState<number | null>(null)
  const [quizSubmitting, setQuizSubmitting] = useState(false)
  const [mindmap, setMindmap] = useState<{ root: string; children: { name: string }[] }>({ root: '', children: [] })
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
  const [ocrLoading, setOcrLoading] = useState(false)
  const [ocrImage, setOcrImage] = useState('')
  const [ocrResult, setOcrResult] = useState('')
  const [codeResult, setCodeResult] = useState('')
  const [codeRunning, setCodeRunning] = useState(false)
  const [imagePrompt, setImagePrompt] = useState('')
  const [generatedImage, setGeneratedImage] = useState('')
  const [imageLoading, setImageLoading] = useState(false)
  const [savingNotes, setSavingNotes] = useState(false)
  const [savingCornell, setSavingCornell] = useState(false)
  const [savingFeynman, setSavingFeynman] = useState(false)
  const [markingComplete, setMarkingComplete] = useState(false)
  const studentId = useAppStore((s) => s.studentId)
  const location = useLocation()

  const currentTopic = courseMenu.flatMap(c => c.children || []).find(c => c.key === activeKey)?.label || ''

  // 加载课程目录
  useEffect(() => {
    let ignore = false
    const loadMenu = async () => {
      setMenuLoading(true)
      try {
        const res = await knowledgeApi.list()
        if (ignore) return
        const kps: Record<string, unknown>[] = res.data.data || []
        // 按 subject 分组
        const groups: Record<string, Record<string, unknown>[]> = {}
        kps.forEach((kp) => {
          const subject = String(kp.subject || '其他')
          if (!groups[subject]) groups[subject] = []
          groups[subject].push(kp)
        })
        // 构建 courseMenu
        let chapterIndex = 1
        const menu: CourseMenuItem[] = []
        Object.entries(groups).forEach(([subject, items]) => {
          menu.push({
            key: `chapter_${subject}`,
            icon: <BookOutlined />,
            label: `第${chapterIndex}章：${subject}`,
            children: items.map((kp, idx) => ({
              key: String(kp.kp_id || `kp_${idx}`),
              label: `${chapterIndex}.${idx + 1} ${String(kp.name || '未命名')}`,
              completed: false,
            })),
          })
          chapterIndex++
        })
        setCourseMenu(menu)

        // 优先使用路由传入的 kpId（从学习路径跳转过来）
        const navKpId = (location.state as Record<string, unknown> | null)?.kpId as string | undefined
        if (navKpId) {
          const found = menu.flatMap(m => m.children || []).find(c => c.key === navKpId)
          if (found) {
            setActiveKey(navKpId)
          } else if (menu.length > 0 && menu[0].children.length > 0) {
            setActiveKey(menu[0].children[0].key)
          }
        } else if (menu.length > 0 && menu[0].children.length > 0) {
          setActiveKey(menu[0].children[0].key)
        }
      } catch (e) {
        if (!ignore) message.error('课程目录加载失败')
      } finally {
        if (!ignore) setMenuLoading(false)
      }
    }
    loadMenu()
    return () => { ignore = true }
  }, [])

  // 加载已保存的笔记/反思
  useEffect(() => {
    if (!studentId) return
    let ignore = false
    const loadReflections = async () => {
      try {
        const res = await logReflectionApi.getReflections(studentId, 30)
        if (ignore || !res.data?.data) return
        const refs = res.data.data as Record<string, unknown>[]
        const plainNote = refs.find((r) => String(r.tags || '').includes('notes'))
        if (plainNote) setNotes(String(plainNote.content || ''))
        const cornell = refs.find((r) => String(r.tags || '').includes('cornell'))
        if (cornell) {
          try { setCornellNotes(JSON.parse(String(cornell.content || '{}'))) } catch { setCornellNotes({ cues: String(cornell.content || ''), notes: '', summary: '' }) }
        }
        const feynman = refs.find((r) => String(r.tags || '').includes('feynman'))
        if (feynman) setFeynmanInput(String(feynman.content || ''))
      } catch { /* ignore */ }
    }
    loadReflections()
    return () => { ignore = true }
  }, [studentId])

  // 切换代码语言时重新生成代码
  useEffect(() => {
    if (!activeKey || !currentTopic) return
    let ignore = false
    const loadCode = async () => {
      try {
        const codeRes = await resourceApi.generateCode({ student_id: studentId, topic: currentTopic, language: codeLanguage, kp_id: activeKey })
        if (!ignore && codeRes.data.code) setCodeContent(codeRes.data.code)
      } catch {
        // ignore
      }
    }
    loadCode()
    return () => { ignore = true }
  }, [codeLanguage, activeKey, studentId, currentTopic])

  useEffect(() => {
    if (!activeKey || !currentTopic) return
    let ignore = false
    const load = async () => {
      setResLoading(true)
      try {
        const [docRes, codeRes, qRes, mapRes] = await Promise.all([
          resourceApi.generateDocument({ student_id: studentId, topic: currentTopic, kp_id: activeKey }),
          resourceApi.generateCode({ student_id: studentId, topic: currentTopic, language: codeLanguage, kp_id: activeKey }),
          resourceApi.generateQuestions({ student_id: studentId, topic: currentTopic, count: 3, kp_id: activeKey }),
          resourceApi.generateMindmap({ student_id: studentId, topic: currentTopic, kp_id: activeKey }),
        ])
        if (ignore) return
        if (docRes.data.document) setDocContent(docRes.data.document)
        if (codeRes.data.code) setCodeContent(codeRes.data.code)
        const qs = Array.isArray(qRes.data.questions) ? qRes.data.questions : []
        if (qs.length) setQuestions(qs)
        // 重置答题状态
        setQuizAnswers({})
        setQuizSubmitted({})
        setQuizScore(null)
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
      const res = await tutorApi.ask({
        student_id: studentId,
        question,
        session_id: `${studentId}_resource`,
      })
      const aiReply = res.data?.response || '服务暂时无响应，请稍后再试。'
      setMessages((prev) => [...prev, { role: 'ai', content: aiReply, agent: '辅导助手' }])
    } catch (e: unknown) {
      message.error(extractApiError(e, '请求失败'))
      setMessages((prev) => [...prev, { role: 'ai', content: '服务暂时不可用。', agent: '辅导助手' }])
    } finally {
      setLoading(false)
    }
  }

  const copyCode = () => {
    navigator.clipboard.writeText(codeContent).then(() => message.success('代码已复制'))
  }

  const handleRunCode = async () => {
    setCodeRunning(true)
    setCodeResult('')
    try {
      const res = await resourceApi.executeCode({ code: codeContent, language: codeLanguage })
      const data = res.data as unknown as Record<string, unknown>
      const output = String(data.output ?? '')
      const error = String(data.error ?? '')
      const explanation = String(data.explanation ?? '')

      if (output) {
        setCodeResult(output)
      } else if (error) {
        setCodeResult(`【编译/运行错误】\n${error}${explanation ? '\n\n说明：' + explanation : ''}`)
      } else {
        setCodeResult(`执行完成，无标准输出。\n\n后端说明：${explanation || '程序已正常结束，但未产生 stdout。'}`)
      }
    } catch (e: unknown) {
      setCodeResult('执行出错：' + extractApiError(e, '执行失败'))
    } finally {
      setCodeRunning(false)
    }
  }

  const handleOcrFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    if (!file.type.startsWith('image/')) {
      message.warning('请上传图片文件')
      return
    }
    const reader = new FileReader()
    reader.onload = (ev) => {
      const result = ev.target?.result as string
      if (result) setOcrImage(result)
    }
    reader.readAsDataURL(file)
    e.target.value = ''
  }

  const handleOcrRecognize = async () => {
    if (!ocrImage) {
      message.warning('请先上传图片')
      return
    }
    setOcrLoading(true)
    try {
      const res = await ocrApi.recognize({
        image_base64: ocrImage,
        prompt: '请识别这张图片中的所有文字内容，保持原有的段落和格式。如果是数学公式，请用 LaTeX 表示。如果是错题，请标注题号和答案区域。',
      })
      setOcrResult(res.data.text)
      message.success('识别成功')
    } catch (e: unknown) {
      message.error(extractApiError(e, '识别失败'))
    } finally {
      setOcrLoading(false)
    }
  }

  const handleOcrToNotes = () => {
    if (!ocrResult) return
    setNotes((prev) => prev + '\n\n【OCR识别结果】\n' + ocrResult)
    setOcrModalOpen(false)
    setOcrImage('')
    setOcrResult('')
    message.success('已导入笔记')
  }

  const handleMarkComplete = async () => {
    if (!activeKey) {
      message.warning('请先选择一个知识点')
      return
    }
    setMarkingComplete(true)
    try {
      const elapsedSec = getElapsed()
      await learningDataApi.record({
        student_id: studentId,
        kp_id: activeKey,
        action: 'complete',
        duration: elapsedSec,
        progress: 1.0,
      })
      message.success('已标记完成')
    } catch (e: unknown) {
      message.error(extractApiError(e, '标记失败'))
    } finally {
      setMarkingComplete(false)
    }
  }

  const handleSaveNotes = async () => {
    if (!notes.trim()) {
      message.warning('笔记内容为空')
      return
    }
    setSavingNotes(true)
    try {
      await logReflectionApi.createReflection({
        student_id: studentId,
        date: new Date().toISOString().slice(0, 10),
        content: notes.trim(),
        mood: 'neutral',
        tags: ['notes'],
      })
      message.success('笔记已保存')
    } catch (e: unknown) {
      message.error(extractApiError(e, '保存失败'))
    } finally {
      setSavingNotes(false)
    }
  }

  const handleSaveCornell = async () => {
    if (!cornellNotes.cues.trim() && !cornellNotes.notes.trim() && !cornellNotes.summary.trim()) {
      message.warning('康奈尔笔记内容为空')
      return
    }
    setSavingCornell(true)
    try {
      await logReflectionApi.createReflection({
        student_id: studentId,
        date: new Date().toISOString().slice(0, 10),
        content: JSON.stringify(cornellNotes),
        mood: 'neutral',
        tags: ['cornell'],
      })
      message.success('康奈尔笔记已保存')
    } catch (e: unknown) {
      message.error(extractApiError(e, '保存失败'))
    } finally {
      setSavingCornell(false)
    }
  }

  const handleSubmitFeynman = async () => {
    if (!feynmanInput.trim()) {
      message.warning('请先输入费曼练习内容')
      return
    }
    setSavingFeynman(true)
    try {
      await logReflectionApi.createReflection({
        student_id: studentId,
        date: new Date().toISOString().slice(0, 10),
        content: feynmanInput.trim(),
        mood: 'neutral',
        tags: ['feynman'],
      })
      message.success('费曼练习已保存')
      setFeynmanInput('')
    } catch (e: unknown) {
      message.error(extractApiError(e, '保存失败'))
    } finally {
      setSavingFeynman(false)
    }
  }

  const handleGenerateImage = async () => {
    if (!imagePrompt.trim()) {
      message.warning('请输入图片描述')
      return
    }
    setImageLoading(true)
    try {
      const res = await imageApi.generate({ prompt: imagePrompt })
      // 同步直接返回图片
      if (res.data.image_urls && res.data.image_urls.length > 0) {
        setGeneratedImage(res.data.image_urls[0])
        message.success('图片生成成功')
        return
      }
      // 异步任务：轮询查询结果
      const taskId = res.data.task_id
      if (res.data.status === 'submitted' && taskId) {
        message.info('图片生成中，请稍候…')
        const poll = async (attempt: number): Promise<void> => {
          if (attempt <= 0) {
            message.error('图片生成超时，请稍后手动刷新')
            throw new Error('timeout')
          }
          await new Promise((resolve) => setTimeout(resolve, 2000))
          const pollRes = await imageApi.getResult(taskId)
          if (pollRes.data.status === 'done' && pollRes.data.image_urls && pollRes.data.image_urls.length > 0) {
            setGeneratedImage(pollRes.data.image_urls[0])
            message.success('图片生成成功')
            return
          }
          if (pollRes.data.status === 'failed' || pollRes.data.status === 'error') {
            message.error('图片生成失败：' + (pollRes.data.message || '未知错误'))
            throw new Error('failed')
          }
          return poll(attempt - 1)
        }
        await poll(15)
      } else {
        message.info('图片生成中，请稍后查看')
      }
    } catch (e: unknown) {
      const errMsg = extractApiError(e, '生成失败')
      if (errMsg !== 'timeout' && errMsg !== 'failed') {
        message.error(errMsg)
      }
    } finally {
      setImageLoading(false)
    }
  }

  return (
    <div className="space-y-5">
      {/* 顶部标题栏 */}
      <Card className="border border-slate-100 rounded-2xl" styles={{ body: { padding: '20px 24px' } }}>
        <div className="flex items-center justify-between flex-wrap gap-3">
          <Space>
            <div className="w-10 h-10 rounded-xl bg-slate-900 flex items-center justify-center text-white">
              <ReadOutlined />
            </div>
            <div>
              <Typography.Title level={4} className="!m-0 text-slate-800">{currentTopic}</Typography.Title>
              <Typography.Text className="text-slate-400 text-xs">C语言程序设计 · 编程基础</Typography.Text>
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
            <Button type="primary" className="rounded-lg bg-primary" onClick={handleMarkComplete} loading={markingComplete}>
              <CheckCircleOutlined /> 标记完成
            </Button>
          </Space>
        </div>
      </Card>

      <div className="flex gap-5 items-start">
        {/* 左侧目录 */}
        <Card className="border border-slate-100 rounded-2xl w-56 hidden xl:block flex-shrink-0" styles={{ body: { padding: '20px 16px' } }}>
          <Typography.Text className="font-semibold text-slate-800 block mb-4 text-sm">课程目录</Typography.Text>
          <Spin spinning={menuLoading}>
            <Collapse
              defaultActiveKey={courseMenu.map(c => c.key)}
              ghost
              expandIconPosition="end"
              items={courseMenu.map((chapter) => ({
                key: chapter.key,
                label: <span className="font-medium text-slate-700 text-sm">{chapter.label}</span>,
                children: (
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
                ),
              }))}
            />
          </Spin>
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
                <Space.Compact className="rounded-lg overflow-hidden">
                  <Button size="small" icon={<LikeOutlined />} className={resourceFeedback[currentTopic] === 'good' ? 'text-emerald-600' : ''} onClick={() => setResourceFeedback({ ...resourceFeedback, [currentTopic]: 'good' })} />
                  <Button size="small" icon={<DislikeOutlined />} className={resourceFeedback[currentTopic] === 'bad' ? 'text-red-500' : ''} onClick={() => setResourceFeedback({ ...resourceFeedback, [currentTopic]: 'bad' })} />
                </Space.Compact>
              </Space>
            }
            styles={{ body: { padding: '40px' } }}
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
          <Card className="border border-slate-100 rounded-2xl" styles={{ body: { padding: '20px 24px' } }}>
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
                          <div className="flex items-center gap-3">
                            <div className="flex gap-2">
                              <div className="w-3 h-3 rounded-full bg-red-400" />
                              <div className="w-3 h-3 rounded-full bg-yellow-400" />
                              <div className="w-3 h-3 rounded-full bg-green-400" />
                            </div>
                            <Tag
                              className={`cursor-pointer rounded-full text-xs ${codeLanguage === 'Python' ? 'bg-blue-500 text-white border-blue-500' : 'bg-slate-700 text-slate-300 border-slate-600'}`}
                              onClick={() => { setCodeLanguage('Python'); setCodeResult('') }}
                            >Python</Tag>
                            <Tag
                              className={`cursor-pointer rounded-full text-xs ${codeLanguage === 'C' ? 'bg-blue-500 text-white border-blue-500' : 'bg-slate-700 text-slate-300 border-slate-600'}`}
                              onClick={() => { setCodeLanguage('C'); setCodeResult('') }}
                            >C</Tag>
                          </div>
                          <Tooltip title="复制代码">
                            <Button type="text" size="small" icon={<CopyOutlined className="text-slate-400 hover:text-white" />} onClick={copyCode} />
                          </Tooltip>
                        </div>
                        <Input.TextArea
                          value={codeContent}
                          onChange={(e) => setCodeContent(e.target.value)}
                          rows={12}
                          className="bg-slate-900 text-slate-200 border-slate-700 font-mono text-sm !p-0 !shadow-none !outline-none focus:!border-slate-700 focus:!shadow-none hover:!bg-slate-900 hover:!border-slate-700"
                          style={{ resize: 'vertical', lineHeight: 1.6 }}
                        />
                      </div>
                      <Button type="primary" className="rounded-lg bg-primary" onClick={handleRunCode} loading={codeRunning}>
                        <ArrowRightOutlined /> 运行{codeLanguage}代码
                      </Button>
                      {codeResult && (
                        <div className="mt-2">
                          <div className="flex items-center justify-between mb-1">
                            <span className="text-slate-400 text-xs">运行结果</span>
                            <Button type="link" size="small" className="text-xs text-primary" onClick={() => { navigator.clipboard.writeText(codeResult).then(() => message.success('结果已复制')) }}>
                              复制结果
                            </Button>
                          </div>
                          <Input.TextArea
                            value={codeResult}
                            readOnly
                            rows={8}
                            className="bg-slate-800 text-green-400 border-slate-700 font-mono text-sm !shadow-none !outline-none focus:!border-slate-700 hover:!border-slate-700"
                            style={{ resize: 'vertical', lineHeight: 1.6 }}
                          />
                        </div>
                      )}
                    </div>
                  ),
                },
                {
                  key: 'quiz',
                  label: <span className="flex items-center gap-1.5 text-sm"><BulbOutlined /> 练习题 ({questions.length})</span>,
                  children: (
                    <div className="space-y-3">
                      {questions.length === 0 && <Typography.Text className="text-slate-400">暂无练习题</Typography.Text>}
                      {questions.length > 0 && (
                        <div className="flex items-center justify-between mb-2">
                          <div className="text-sm text-slate-500">
                            已答 {Object.keys(quizSubmitted).length} / {questions.length} 题
                            {quizScore !== null && (
                              <Tag className="ml-2 rounded-full border-0 bg-primary-50 text-primary text-xs font-bold">
                                得分: {quizScore} 分
                              </Tag>
                            )}
                          </div>
                          {Object.keys(quizSubmitted).length > 0 && (
                            <Button size="small" className="rounded-lg text-xs" onClick={() => { setQuizAnswers({}); setQuizSubmitted({}); setQuizScore(null); }}>
                              重新作答
                            </Button>
                          )}
                        </div>
                      )}
                      {questions.map((q, idx) => {
                        const submitted = quizSubmitted[q.q_id]
                        const selected = quizAnswers[q.q_id]
                        const isCorrect = submitted && selected === q.correct_answer
                        return (
                          <Card key={q.q_id} size="small" className={`rounded-xl border-slate-100 ${submitted ? (isCorrect ? 'border-emerald-200 bg-emerald-50/30' : 'border-red-200 bg-red-50/30') : ''}`}>
                            <div className="flex items-start gap-2 mb-3">
                              <span className="w-6 h-6 rounded-full bg-primary/10 text-primary text-xs font-bold flex items-center justify-center shrink-0 mt-0.5">{idx + 1}</span>
                              <Typography.Text className="font-medium text-slate-800">{q.content}</Typography.Text>
                            </div>
                            {q.options && (
                              <div className="space-y-2 pl-8">
                                {q.options.map((opt) => {
                                  const isSelected = selected === opt.id
                                  const isCorrectOpt = opt.id === q.correct_answer
                                  let optClass = 'px-3 py-2 rounded-lg text-sm border transition-all '
                                  if (submitted) {
                                    if (isCorrectOpt) {
                                      optClass += 'bg-emerald-100 border-emerald-300 text-emerald-700'
                                    } else if (isSelected && !isCorrectOpt) {
                                      optClass += 'bg-red-100 border-red-300 text-red-700'
                                    } else {
                                      optClass += 'bg-slate-50 border-slate-100 text-slate-400'
                                    }
                                  } else {
                                    optClass += isSelected
                                      ? 'bg-primary-50 border-primary-200 text-primary cursor-pointer'
                                      : 'bg-slate-50 border-slate-100 text-slate-600 hover:bg-indigo-50 hover:border-indigo-200 hover:text-primary cursor-pointer'
                                  }
                                  return (
                                    <div key={opt.id} className={optClass} onClick={() => {
                                      if (!submitted) setQuizAnswers(prev => ({ ...prev, [q.q_id]: opt.id }))
                                    }}>
                                      <div className="flex items-center gap-2">
                                        <span className={`w-5 h-5 rounded-full flex items-center justify-center text-xs font-bold shrink-0 ${isSelected ? 'bg-primary text-white' : 'bg-white border border-slate-300 text-slate-500'}`}>
                                          {opt.id}
                                        </span>
                                        <span>{opt.text}</span>
                                        {submitted && isCorrectOpt && <CheckCircleOutlined className="text-emerald-500 ml-auto" />}
                                        {submitted && isSelected && !isCorrectOpt && <CloseCircleOutlined className="text-red-500 ml-auto" />}
                                      </div>
                                    </div>
                                  )
                                })}
                              </div>
                            )}
                            {submitted && (
                              <div className="mt-3 pl-8">
                                <div className={`text-xs font-medium mb-1 ${isCorrect ? 'text-emerald-600' : 'text-red-600'}`}>
                                  {isCorrect ? '回答正确！' : `回答错误，正确答案是 ${q.correct_answer}`}
                                </div>
                                <div className="text-xs text-slate-500 bg-white/60 rounded-lg p-2 border border-slate-100">
                                  <span className="font-medium text-slate-600">解析：</span>{q.explanation}
                                </div>
                              </div>
                            )}
                            {!submitted && selected && (
                              <div className="mt-3 pl-8">
                                <Button type="primary" size="small" className="rounded-lg bg-primary text-xs" loading={quizSubmitting} onClick={() => {
                                  setQuizSubmitted(prev => ({ ...prev, [q.q_id]: true }))
                                  // 自动计算总分
                                  const newSubmitted = { ...quizSubmitted, [q.q_id]: true }
                                  const newAnswers = { ...quizAnswers, [q.q_id]: selected }
                                  const total = questions.reduce((sum, qq) => {
                                    if (newSubmitted[qq.q_id] && newAnswers[qq.q_id] === qq.correct_answer) return sum + 1
                                    return sum
                                  }, 0)
                                  setQuizScore(total)
                                }}>
                                  提交答案
                                </Button>
                              </div>
                            )}
                          </Card>
                        )
                      })}
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
                      <Button type="primary" className="rounded-lg bg-primary" onClick={handleSaveNotes} loading={savingNotes}>
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
                      <Button type="primary" className="rounded-lg bg-primary" onClick={handleSaveCornell} loading={savingCornell}>
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
                      <Button type="primary" className="rounded-lg bg-primary" onClick={handleSubmitFeynman} loading={savingFeynman}>
                        <ThunderboltOutlined /> 提交费曼练习
                      </Button>
                    </div>
                  ),
                },
                {
                  key: 'image',
                  label: <span className="flex items-center gap-1.5 text-sm"><PictureOutlined /> AI 绘图</span>,
                  children: (
                    <div className="space-y-3">
                      <div className="p-4 rounded-xl bg-indigo-50 border border-indigo-100 text-sm text-indigo-800 space-y-1">
                        <div><strong>AI 绘图：</strong>输入图片描述，AI 将为你生成对应的学习插图或概念示意图。</div>
                        <div className="text-xs text-indigo-600">
                          提示：描述请使用中文；如需图中出现特定文字，请用双引号括起，如栈区、堆区。
                        </div>
                      </div>
                      <Input.TextArea rows={3} placeholder="例如：C语言内存模型示意图，展示栈区和堆区的区别，图中所有文字使用中文..." value={imagePrompt} onChange={(e) => setImagePrompt(e.target.value)} className="rounded-xl bg-slate-50 border-slate-200" />
                      <Button type="primary" className="rounded-lg bg-primary" onClick={handleGenerateImage} loading={imageLoading}>
                        <PictureOutlined /> 生成图片
                      </Button>
                      {generatedImage && (
                        <div className="mt-3">
                          <img src={generatedImage} alt="AI 生成图片" className="rounded-xl border border-slate-200 max-w-full" />
                        </div>
                      )}
                    </div>
                  ),
                },
              ]}
            />
          </Card>
        </div>

        {/* 右侧 AI 辅导 */}
        {chatOpen && (
          <Card className="border border-slate-100 rounded-2xl w-72 flex-shrink-0 hidden lg:flex flex-col" styles={{ body: { padding: '16px', height: '100%', display: 'flex', flexDirection: 'column' } }}>
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
        onCancel={() => { setOcrModalOpen(false); setOcrImage(''); setOcrResult('') }}
        footer={null}
        width={560}
        className="rounded-2xl"
      >
        <div className="space-y-4 py-2">
          {!ocrImage ? (
            <label className="block p-6 rounded-xl bg-slate-50 border border-dashed border-slate-300 text-center cursor-pointer hover:border-primary transition-all">
              <CameraOutlined className="text-3xl text-slate-300 mb-2" />
              <div className="text-sm text-slate-600">点击上传纸质笔记 / 错题照片</div>
              <div className="text-xs text-slate-400 mt-1">支持 JPG、PNG，基于大模型 Vision 识别</div>
              <input type="file" accept="image/*" className="hidden" onChange={handleOcrFileChange} />
            </label>
          ) : (
            <div className="space-y-3">
              <img src={ocrImage} alt="ocr" className="w-full max-h-64 object-contain rounded-lg border border-slate-200" />
              <div className="flex gap-2">
                <Button loading={ocrLoading} type="primary" className="bg-primary rounded-lg flex-1" onClick={handleOcrRecognize}>
                  {ocrLoading ? '识别中...' : '开始识别'}
                </Button>
                <Button className="rounded-lg" onClick={() => { setOcrImage(''); setOcrResult('') }}>
                  重新上传
                </Button>
              </div>
            </div>
          )}

          {ocrResult && (
            <div className="space-y-2">
              <div className="text-sm font-medium text-slate-700">识别结果</div>
              <div className="p-3 rounded-lg bg-slate-50 border border-slate-200 text-sm text-slate-700 whitespace-pre-wrap max-h-48 overflow-y-auto">
                {ocrResult}
              </div>
              <Button type="primary" className="bg-primary rounded-lg w-full" onClick={handleOcrToNotes}>
                导入笔记
              </Button>
            </div>
          )}

          <div className="flex items-center gap-2 text-xs text-slate-400">
            <SafetyOutlined />
            <span>端云协同：图片通过 HTTPS 上传，识别结果本地展示</span>
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
