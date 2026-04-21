import React, { useState, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import {
  Typography, Card, Button, Input, Space, Tabs, Tag, Collapse,
  FloatButton, message, Spin, Tooltip, Badge, Modal, Empty
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
  PictureOutlined,
  CameraOutlined,
} from '@ant-design/icons'
import { useAppStore } from '../store'
import { resourceApi, tutorApi, imageApi, knowledgeApi, learningDataApi } from '../services/api'
import type { ChatMessage, QuestionItem, VisionContentItem } from '../types'
import { ChatPanel } from '../components/ChatPanel'

const ResourceCenter: React.FC = () => {
  const [activeKey, setActiveKey] = useState('')
  const [chatOpen, setChatOpen] = useState(false)
  const [messages, setMessages] = useState<ChatMessage[]>([
    { role: 'ai', content: '你好！我正在和你一起学习。有什么不懂的地方随时问我。' },
  ])
  const [notes, setNotes] = useState('')
  const [docContent, setDocContent] = useState('')
  const [codeContent, setCodeContent] = useState('')
  const [questions, setQuestions] = useState<QuestionItem[]>([])
  const [mindmap, setMindmap] = useState<{ root: string; children: { name: string }[] }>({ root: '', children: [] })
  const [loading, setLoading] = useState(false)
  const [resLoading, setResLoading] = useState(false)
  const [bottomTab, setBottomTab] = useState('code')
  const studentId = useAppStore((s) => s.studentId)

  // 课程目录状态
  const [courseMenu, setCourseMenu] = useState<any[]>([])
  const [menuLoading, setMenuLoading] = useState(false)
  const [completedKps, setCompletedKps] = useState<Set<string>>(new Set())
  const [selectedAnswers, setSelectedAnswers] = useState<Record<number, string>>({})

  // 文生图状态
  const [imagePrompt, setImagePrompt] = useState('')
  const [imageWidth, setImageWidth] = useState(1328)
  const [imageHeight, setImageHeight] = useState(1328)
  const [imageResult, setImageResult] = useState<string[]>([])
  const [imageLoading, setImageLoading] = useState(false)
  const [imageStatus, setImageStatus] = useState('')
  const [imageHistory, setImageHistory] = useState<any[]>([])
  const [previewImage, setPreviewImage] = useState<string | null>(null)
  const [codeOutput, setCodeOutput] = useState('')
  const [codeError, setCodeError] = useState('')
  const [codeExplanation, setCodeExplanation] = useState('')
  const [codeRunning, setCodeRunning] = useState(false)

  // 加载课程目录
  useEffect(() => {
    const loadMenu = async () => {
      setMenuLoading(true)
      try {
        const [kpRes, historyRes] = await Promise.all([
          knowledgeApi.list().catch(() => null),
          learningDataApi.getHistory(studentId, 100).catch(() => null),
        ])

        // 计算已完成的知识点（进度 >= 0.8）
        const completed = new Set<string>()
        if (historyRes?.data?.records) {
          historyRes.data.records.forEach((r: any) => {
            if ((r.progress || 0) >= 0.8) {
              completed.add(r.kp_id)
            }
          })
        }
        setCompletedKps(completed)

        if (kpRes?.data?.data?.length) {
          // 按 subject 分组
          const groups: Record<string, any[]> = {}
          kpRes.data.data.forEach((kp: any, idx: number) => {
            const subject = kp.subject || '未分类'
            if (!groups[subject]) groups[subject] = []
            groups[subject].push({
              key: kp.kp_id,
              label: kp.name,
              completed: completed.has(kp.kp_id),
            })
          })
          const menu = Object.entries(groups).map(([subject, children], idx) => ({
            key: `chapter_${idx}`,
            icon: <BookOutlined />,
            label: `${subject}`,
            children,
          }))
          setCourseMenu(menu)
          // 默认选中第一个
          if (!activeKey && menu[0]?.children?.[0]) {
            setActiveKey(menu[0].children[0].key)
          }
        } else {
          message.warning('暂无课程目录数据')
          setCourseMenu([])
        }
      } catch (e) {
        console.error('课程目录加载失败:', e)
        message.error('加载课程目录失败')
        setCourseMenu([])
      } finally {
        setMenuLoading(false)
        // 处理从搜索跳转过来的选中知识点
        const selectedKpId = localStorage.getItem('selected_kp_id')
        if (selectedKpId) {
          setActiveKey(selectedKpId)
          localStorage.removeItem('selected_kp_id')
          localStorage.removeItem('selected_kp_name')
        }
      }
    }
    loadMenu()
  }, [studentId])

  // 加载图片生成历史
  useEffect(() => {
    const loadImageHistory = async () => {
      try {
        const res = await imageApi.listTasks()
        if (res.data?.tasks) {
          setImageHistory(res.data.tasks)
        }
      } catch (e) {
        console.error('图片历史加载失败:', e)
      }
    }
    loadImageHistory()
  }, [])

  const currentTopic = courseMenu.flatMap((c: any) => c.children || []).find((c: any) => c.key === activeKey)?.label || '机器学习'

  useEffect(() => {
    if (!activeKey) return
    const topic = courseMenu.flatMap((c: any) => c.children || []).find((c: any) => c.key === activeKey)?.label || '机器学习'
    let ignore = false
    const load = async () => {
      setResLoading(true)
      try {
        const [docRes, codeRes, qRes, mapRes] = await Promise.all([
          resourceApi.generateDocument({ student_id: studentId, topic }),
          resourceApi.generateCode({ student_id: studentId, topic, language: 'Python' }),
          resourceApi.generateQuestions({ student_id: studentId, topic, count: 3 }),
          resourceApi.generateMindmap({ student_id: studentId, topic }),
        ])
        if (ignore) return
        if (docRes.data.document) setDocContent(docRes.data.document)
        if (codeRes.data.code) setCodeContent(codeRes.data.code)
        const qs = Array.isArray(qRes.data.questions) ? qRes.data.questions : []
        if (qs.length) setQuestions(qs)
        if (mapRes.data.mindmap) {
          setMindmap({
            root: mapRes.data.mindmap.root || topic,
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
  }, [activeKey, studentId, courseMenu])

  const handleSend = async (content?: string | VisionContentItem[]) => {
    if (!content || (typeof content === 'string' && !content.trim())) return
    const safeContent = content || ''
    setMessages((prev) => [...prev, { role: 'user', content: safeContent }])
    setLoading(true)
    try {
      const res = await tutorApi.ask({ student_id: studentId, question: safeContent, session_id: `${studentId}_resource` })
      setMessages((prev) => [...prev, { role: 'ai', content: res.data.response || '让我再想想...' }])
    } catch (e: unknown) {
      const errMsg = e instanceof Error ? e.message : '请求失败'
      message.error(errMsg)
      setMessages((prev) => [...prev, { role: 'ai', content: '服务暂时不可用。' }])
    } finally {
      setLoading(false)
    }
  }

  const copyCode = () => {
    navigator.clipboard.writeText(codeContent).then(() => message.success('代码已复制'))
  }

  const handleGenerateImage = async () => {
    if (!imagePrompt.trim()) {
      message.warning('请输入图像描述')
      return
    }
    setImageLoading(true)
    setImageStatus('提交任务中...')
    try {
      const res = await imageApi.generate({
        prompt: imagePrompt,
        width: imageWidth,
        height: imageHeight,
      })

      if (res.data.status === 'done' && res.data.image_urls) {
        setImageResult(res.data.image_urls)
        setImageStatus('生成完成')
        setImageLoading(false)
        message.success('图像生成成功')
        // 刷新历史
        imageApi.listTasks().then((r) => r.data?.tasks && setImageHistory(r.data.tasks)).catch(() => {})
        return
      }

      const tid = res.data.task_id
      setImageResult([])
      setImageStatus('任务已提交，生成中...')

      const poll = async () => {
        const maxAttempts = 40
        for (let i = 0; i < maxAttempts; i++) {
          await new Promise((r) => setTimeout(r, 3000))
          try {
            const r = await imageApi.getResult(tid)
            setImageStatus(`状态：${r.data.status}`)
            if (r.data.status === 'done') {
              setImageResult(r.data.image_urls || [])
              setImageStatus('生成完成')
              setImageLoading(false)
              message.success('图像生成成功')
              // 刷新历史
              imageApi.listTasks().then((hist) => hist.data?.tasks && setImageHistory(hist.data.tasks)).catch(() => {})
              return
            }
            if (r.data.status === 'not_found' || r.data.status === 'expired') {
              setImageStatus('任务失败或已过期')
              setImageLoading(false)
              return
            }
          } catch (e) {
            console.error('图像查询失败:', e)
          }
        }
        setImageStatus('查询超时，请稍后手动刷新')
        setImageLoading(false)
      }
      poll()
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : '生成失败'
      message.error(msg)
      setImageStatus(`失败：${msg}`)
      setImageLoading(false)
    }
  }

  const handleMarkComplete = async () => {
    if (!activeKey) {
      message.warning('请先选择一个知识点')
      return
    }
    try {
      await learningDataApi.record({
        student_id: studentId,
        kp_id: activeKey,
        action: 'review',
        duration: 300,
        progress: 1.0,
        score: 100,
      })
      setCompletedKps((prev) => new Set(prev).add(activeKey))
      message.success('已标记完成')
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : '标记失败'
      message.error(msg)
    }
  }

  const handleRunCode = async () => {
    if (!codeContent.trim()) {
      message.warning('代码内容为空')
      return
    }
    setCodeRunning(true)
    setCodeOutput('')
    setCodeError('')
    setCodeExplanation('')
    try {
      const res = await resourceApi.executeCode({ code: codeContent, language: 'Python' })
      if (res.data.error) {
        setCodeError(res.data.error)
        message.error('代码执行出错')
      } else {
        setCodeOutput(res.data.output)
        message.success('代码执行成功')
      }
      setCodeExplanation(res.data.explanation)
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : '执行失败'
      message.error(msg)
      setCodeError(msg)
    } finally {
      setCodeRunning(false)
    }
  }

  const handleSelectAnswer = (qIdx: number, optId: string, correct: string) => {
    setSelectedAnswers((prev) => ({ ...prev, [qIdx]: optId }))
    if (optId === correct) {
      message.success('回答正确！')
    } else {
      message.error('回答错误，再想想')
    }
  }

  const handleSaveNotes = async () => {
    if (!notes.trim()) {
      message.warning('笔记内容为空')
      return
    }
    try {
      await learningDataApi.record({
        student_id: studentId,
        kp_id: activeKey || 'notes',
        action: 'read',
        duration: 60,
        progress: 0.5,
        meta: { notes },
      })
      message.success('笔记已保存')
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : '保存失败'
      message.error(msg)
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
              <Typography.Text className="text-slate-400 text-xs">人工智能导论 · 机器学习基础</Typography.Text>
            </div>
          </Space>
          <Button type="primary" className="rounded-lg bg-primary" onClick={handleMarkComplete}>
            <CheckCircleOutlined /> 标记完成
          </Button>
        </div>
      </Card>

      <div className="flex gap-5 items-start">
        {/* 左侧目录 */}
        <Card className="border border-slate-100 rounded-2xl w-56 hidden xl:block flex-shrink-0" styles={{ body: { padding: '20px 16px' } }}>
          <Typography.Text className="font-semibold text-slate-800 block mb-4 text-sm">课程目录</Typography.Text>
          <Spin spinning={menuLoading}>
            <Collapse
              defaultActiveKey={courseMenu.length > 0 ? [courseMenu[0]?.key] : ['chapter1']}
              ghost
              expandIconPosition="end"
              items={courseMenu.map((chapter: any) => ({
                key: chapter.key,
                label: <span className="font-medium text-slate-700 text-sm">{chapter.label}</span>,
                children: (
                  <div className="flex flex-col gap-1">
                    {chapter.children?.map((item: any) => (
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
              </Space>
            }
            extra={<Tag className="rounded-full border-0 bg-slate-100 text-slate-600 text-xs">{currentTopic}</Tag>}
            styles={{ body: { padding: '40px' } }}
          >
            <Spin spinning={resLoading}>
              <div className="prose max-w-none text-slate-700 leading-relaxed text-[15px]">
                {docContent ? (
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>{docContent}</ReactMarkdown>
                ) : (
                  <Typography.Text className="text-slate-400">选择一个知识点开始学习...</Typography.Text>
                )}
              </div>
            </Spin>
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
                        <pre className="text-slate-200 whitespace-pre-wrap mt-2">{codeContent || '# 暂无代码'}</pre>
                      </div>
                      <Button type="primary" className="rounded-lg bg-primary" onClick={handleRunCode} loading={codeRunning}>
                        <ArrowRightOutlined /> 运行代码
                      </Button>
                      {(codeOutput || codeError || codeExplanation) && (
                        <div className="mt-3 space-y-2">
                          {codeOutput && (
                            <div className="bg-slate-800 rounded-lg p-3">
                              <Typography.Text className="text-xs text-slate-400 block mb-1">输出</Typography.Text>
                              <pre className="text-green-400 text-sm whitespace-pre-wrap">{codeOutput}</pre>
                            </div>
                          )}
                          {codeError && (
                            <div className="bg-red-50 border border-red-100 rounded-lg p-3">
                              <Typography.Text className="text-xs text-red-400 block mb-1">错误</Typography.Text>
                              <pre className="text-red-600 text-sm whitespace-pre-wrap">{codeError}</pre>
                            </div>
                          )}
                          {codeExplanation && (
                            <div className="bg-blue-50 border border-blue-100 rounded-lg p-3">
                              <Typography.Text className="text-xs text-blue-400 block mb-1">解释</Typography.Text>
                              <Typography.Text className="text-blue-700 text-sm">{codeExplanation}</Typography.Text>
                            </div>
                          )}
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
                      {questions.map((q, idx) => (
                        <Card key={idx} size="small" className="rounded-xl border-slate-100">
                          <Typography.Text className="font-medium text-slate-800 block mb-3">{idx + 1}. {q.content}</Typography.Text>
                          {q.options && (
                            <div className="space-y-2">
                              {q.options.map((opt) => (
                                <div
                                  key={opt.id}
                                  className={`px-3 py-2 rounded-lg text-sm transition-colors cursor-pointer ${
                                    selectedAnswers[idx] === opt.id
                                      ? opt.id === q.correct_answer
                                        ? 'bg-emerald-50 text-emerald-600 border border-emerald-200'
                                        : 'bg-red-50 text-red-600 border border-red-200'
                                      : 'text-slate-600 bg-slate-50 hover:bg-indigo-50 hover:text-primary'
                                  }`}
                                  onClick={() => handleSelectAnswer(idx, opt.id, q.correct_answer)}
                                >
                                  {opt.id}. {opt.text}
                                </div>
                              ))}
                            </div>
                          )}
                          {selectedAnswers[idx] !== undefined && (
                            <Tag className="mt-3 rounded-full border-0 bg-emerald-50 text-emerald-600 text-xs">答案：{q.correct_answer}</Tag>
                          )}
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
                      <Button type="primary" className="rounded-lg bg-primary" onClick={handleSaveNotes}>
                        <CheckCircleOutlined /> 保存笔记
                      </Button>
                    </div>
                  ),
                },
                {
                  key: 'image',
                  label: <span className="flex items-center gap-1.5 text-sm"><PictureOutlined /> 文生图</span>,
                  children: (
                    <div className="space-y-4">
                      <Input.TextArea
                        rows={3}
                        placeholder="描述你想生成的图像，例如：一只穿着宇航服的橘猫在月球上..."
                        value={imagePrompt}
                        onChange={(e) => setImagePrompt(e.target.value)}
                        className="rounded-xl"
                      />
                      <div className="flex gap-4 flex-wrap items-center">
                        <div className="flex items-center gap-2">
                          <Typography.Text className="text-sm text-slate-500">宽度</Typography.Text>
                          <Input type="number" value={imageWidth} onChange={(e) => setImageWidth(Number(e.target.value))} min={512} max={2048} className="w-24 rounded-lg" />
                        </div>
                        <div className="flex items-center gap-2">
                          <Typography.Text className="text-sm text-slate-500">高度</Typography.Text>
                          <Input type="number" value={imageHeight} onChange={(e) => setImageHeight(Number(e.target.value))} min={512} max={2048} className="w-24 rounded-lg" />
                        </div>
                      </div>
                      <Button type="primary" loading={imageLoading} onClick={handleGenerateImage} className="rounded-lg bg-primary">
                        <CameraOutlined /> 生成图像
                      </Button>
                      {imageStatus && (
                        <Typography.Text className="text-slate-500 text-sm block">{imageStatus}</Typography.Text>
                      )}
                      {imageResult.length > 0 && (
                        <div className="space-y-2">
                          <Typography.Text className="font-semibold text-slate-800 text-sm block">本次生成结果</Typography.Text>
                          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            {imageResult.map((url, i) => (
                              <img
                                key={i}
                                src={url}
                                alt={`generated-${i}`}
                                className="rounded-xl border border-slate-100 w-full object-cover cursor-pointer hover:shadow-md transition-shadow"
                                onClick={() => setPreviewImage(url)}
                              />
                            ))}
                          </div>
                        </div>
                      )}
                      {imageHistory.length > 0 && (
                        <div className="space-y-2 mt-4">
                          <Typography.Text className="font-semibold text-slate-800 text-sm block">历史生成记录</Typography.Text>
                          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                            {imageHistory.map((task: any, idx: number) => (
                              <div key={idx} className="relative group">
                                <img
                                  src={task.image_urls?.[0] || ''}
                                  alt={`history-${idx}`}
                                  className="rounded-lg border border-slate-100 w-full h-24 object-cover cursor-pointer hover:shadow-md transition-shadow"
                                  onClick={() => task.image_urls?.[0] && setPreviewImage(task.image_urls[0])}
                                  onError={(e) => { (e.target as HTMLImageElement).style.display = 'none' }}
                                />
                                <span className="absolute bottom-1 right-1 text-[10px] bg-black/50 text-white px-1.5 rounded">{task.status}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                      {imageHistory.length === 0 && imageResult.length === 0 && (
                        <Empty description="暂无生成记录" image={Empty.PRESENTED_IMAGE_SIMPLE} />
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
              onSend={(text) => handleSend(text)}
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

      {!chatOpen && (
        <FloatButton icon={<MessageOutlined />} type="primary" tooltip="打开 AI 辅导" onClick={() => setChatOpen(true)} className="right-6 bottom-6" />
      )}
      <Modal open={!!previewImage} footer={null} onCancel={() => setPreviewImage(null)} centered width="auto">
        {previewImage && <img src={previewImage} alt="preview" className="max-w-full max-h-[70vh] rounded-lg" />}
      </Modal>
    </div>
  )
}

export default ResourceCenter
