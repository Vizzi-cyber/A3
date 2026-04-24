import React, { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, Form, Input, Button, Tabs, Typography, message, Divider } from 'antd'
import { RobotOutlined, UserOutlined, LockOutlined, MailOutlined, BookOutlined, BulbOutlined, MessageOutlined } from '@ant-design/icons'
import gsap from 'gsap'
import { SplitText } from 'gsap/SplitText'
import { authApi } from '../services/api'
import { useAppStore } from '../store'

const Login: React.FC = () => {
  const navigate = useNavigate()
  const login = useAppStore((s) => s.login)
  const setUserInfo = useAppStore((s) => s.setUserInfo)
  const [activeTab, setActiveTab] = useState('login')
  const [loading, setLoading] = useState(false)

  // ===== Block Reveal 动画 =====
  const brandRef = useRef<HTMLDivElement>(null)
  const titleRef = useRef<HTMLHeadingElement>(null)
  const descRef = useRef<HTMLParagraphElement>(null)

  useEffect(() => {
    const section = brandRef.current
    const titleEl = titleRef.current
    const descEl = descRef.current
    if (!section || !titleEl) return

    const splits: any[] = []
    const allBlocks: HTMLDivElement[] = []
    const allLines: HTMLElement[] = []

    const setupText = (element: HTMLElement) => {
      const split = new SplitText(element, {
        type: 'lines',
        linesClass: 'block-line++',
        lineThreshold: 0.1,
      })
      splits.push(split)

      split.lines.forEach((line: Element) => {
        const el = line as HTMLElement
        const wrapper = document.createElement('div')
        wrapper.className = 'block-line-wrapper'
        el.parentNode?.insertBefore(wrapper, el)
        wrapper.appendChild(el)

        const block = document.createElement('div')
        block.className = 'block-revealer'
        block.style.backgroundColor = '#e2e8f0'
        wrapper.appendChild(block)

        allLines.push(el)
        allBlocks.push(block)
      })
    }

    setupText(titleEl)
    if (descEl) setupText(descEl)

    gsap.set(allLines, { opacity: 0 })
    gsap.set(allBlocks, { scaleX: 0, transformOrigin: 'left center' })

    allBlocks.forEach((block, index) => {
      const tl = gsap.timeline({ delay: 0.3 + index * 0.15 })
      tl.to(block, {
        scaleX: 1,
        duration: 0.75,
        ease: 'power4.inOut',
      })
      tl.set(allLines[index], { opacity: 1 })
      tl.set(block, { transformOrigin: 'right center' })
      tl.to(block, {
        scaleX: 0,
        duration: 0.75,
        ease: 'power4.inOut',
      })
    })

    return () => {
      splits.forEach((s) => s.revert())
      const wrappers = section.querySelectorAll('.block-line-wrapper')
      wrappers.forEach((wrapper) => {
        if (wrapper.parentNode && wrapper.firstChild) {
          wrapper.parentNode.insertBefore(wrapper.firstChild, wrapper)
          wrapper.remove()
        }
      })
    }
  }, [])

  const handleLogin = async (values: { student_id: string; password: string }) => {
    setLoading(true)
    try {
      const res = await authApi.login(values)
      const token = res.data.access_token
      login(token, values.student_id)

      try {
        const meRes = await authApi.me()
        const u = meRes.data.data
        setUserInfo({ student_id: u.student_id, username: u.username, role: u.role })
      } catch {
        // ignore
      }

      message.success('登录成功')
      navigate('/')
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : '登录失败'
      message.error(msg)
    } finally {
      setLoading(false)
    }
  }

  const handleRegister = async (values: { student_id: string; username: string; email?: string; password: string }) => {
    setLoading(true)
    try {
      await authApi.register(values)
      message.success('注册成功，请登录')
      setActiveTab('login')
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : '注册失败'
      message.error(msg)
    } finally {
      setLoading(false)
    }
  }

  const features = [
    {
      icon: <BookOutlined className="text-primary text-lg" />,
      title: '知识图谱驱动',
      desc: '基于知识图谱的科学路径规划，避免大模型幻觉带来的偏差',
    },
    {
      icon: <BulbOutlined className="text-warning text-lg" />,
      title: '个性化推荐',
      desc: '多维画像分析，精准匹配最适合你的学习资源与节奏',
    },
    {
      icon: <MessageOutlined className="text-success text-lg" />,
      title: 'AI 智能辅导',
      desc: '24 小时在线答疑，代码纠错、论文润色、学习规划全覆盖',
    },
  ]

  return (
    <div className="min-h-screen relative flex">
      {/* 全屏统一背景 */}
      <div className="absolute inset-0">
        <img
          src="/login_bg.jpg"
          alt="background"
          className="w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-black/50" />
      </div>

      {/* 内容区 */}
      <div className="relative z-10 flex flex-col lg:flex-row w-full min-h-screen">
        {/* ===== 左侧：登录 + 平台介绍 ===== */}
        <div className="w-full lg:w-5/12 xl:w-1/3 flex items-center justify-center px-6 md:px-10 py-12">
          <div className="w-full max-w-sm">
            <Card
              className="rounded-2xl shadow-2xl border-0 overflow-hidden"
              bodyStyle={{ padding: 0 }}
            >
              {/* 上半：登录 / 注册 */}
              <div className="p-6 md:p-8">
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-10 h-10 rounded-xl bg-primary flex items-center justify-center shadow-glow">
                    <RobotOutlined className="text-white text-xl" />
                  </div>
                  <div>
                    <Typography.Title level={4} className="!m-0 text-slate-900">
                      AI Learning
                    </Typography.Title>
                    <Typography.Text className="text-slate-400 text-sm">
                      基于大模型的个性化学习系统
                    </Typography.Text>
                  </div>
                </div>

                <Tabs
                  activeKey={activeTab}
                  onChange={setActiveTab}
                  centered
                  className="mb-4"
                  items={[
                    { key: 'login', label: '登录' },
                    { key: 'register', label: '注册' },
                  ]}
                />

                {activeTab === 'login' && (
                  <Form layout="vertical" onFinish={handleLogin}>
                    <Form.Item
                      label="学号"
                      name="student_id"
                      rules={[{ required: true, message: '请输入学号' }]}
                    >
                      <Input
                        prefix={<UserOutlined className="text-slate-400" />}
                        placeholder="请输入学号"
                        className="rounded-lg"
                        size="large"
                      />
                    </Form.Item>
                    <Form.Item
                      label="密码"
                      name="password"
                      rules={[{ required: true, message: '请输入密码' }]}
                    >
                      <Input.Password
                        prefix={<LockOutlined className="text-slate-400" />}
                        placeholder="请输入密码"
                        className="rounded-lg"
                        size="large"
                      />
                    </Form.Item>
                    <Form.Item className="mb-0">
                      <Button
                        type="primary"
                        htmlType="submit"
                        block
                        loading={loading}
                        className="rounded-lg bg-primary h-10"
                      >
                        登录
                      </Button>
                    </Form.Item>
                  </Form>
                )}

                {activeTab === 'register' && (
                  <Form layout="vertical" onFinish={handleRegister}>
                    <Form.Item
                      label="学号"
                      name="student_id"
                      rules={[{ required: true, message: '请输入学号' }]}
                    >
                      <Input
                        prefix={<UserOutlined className="text-slate-400" />}
                        placeholder="请输入学号"
                        className="rounded-lg"
                        size="large"
                      />
                    </Form.Item>
                    <Form.Item
                      label="用户名"
                      name="username"
                      rules={[{ required: true, message: '请输入用户名' }]}
                    >
                      <Input
                        prefix={<UserOutlined className="text-slate-400" />}
                        placeholder="请输入用户名"
                        className="rounded-lg"
                        size="large"
                      />
                    </Form.Item>
                    <Form.Item
                      label="邮箱（可选）"
                      name="email"
                    >
                      <Input
                        prefix={<MailOutlined className="text-slate-400" />}
                        placeholder="请输入邮箱"
                        className="rounded-lg"
                        size="large"
                      />
                    </Form.Item>
                    <Form.Item
                      label="密码"
                      name="password"
                      rules={[{ required: true, min: 6, message: '密码至少6位' }]}
                    >
                      <Input.Password
                        prefix={<LockOutlined className="text-slate-400" />}
                        placeholder="请输入密码"
                        className="rounded-lg"
                        size="large"
                      />
                    </Form.Item>
                    <Form.Item className="mb-0">
                      <Button
                        type="primary"
                        htmlType="submit"
                        block
                        loading={loading}
                        className="rounded-lg bg-primary h-10"
                      >
                        注册
                      </Button>
                    </Form.Item>
                  </Form>
                )}
              </div>

              <Divider className="!m-0" />

              {/* 下半：平台简介 */}
              <div className="p-6 md:p-8 bg-slate-50/80">
                <Typography.Text className="text-xs text-slate-400 uppercase tracking-wider font-semibold block mb-4">
                  平台特色
                </Typography.Text>
                <div className="space-y-4">
                  {features.map((f, idx) => (
                    <div key={idx} className="flex items-start gap-3">
                      <div className="w-9 h-9 rounded-lg bg-white flex items-center justify-center shadow-sm shrink-0 mt-0.5">
                        {f.icon}
                      </div>
                      <div>
                        <div className="text-sm font-semibold text-slate-800">{f.title}</div>
                        <div className="text-xs text-slate-500 mt-0.5 leading-relaxed">{f.desc}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </Card>

            {import.meta.env.DEV && (
              <div className="text-center mt-4 text-white/50 text-xs">
                <p>测试账号：student_001 / 123456</p>
              </div>
            )}
          </div>
        </div>

        {/* ===== 右侧：Block Reveal 品牌展示区 ===== */}
        <div
          ref={brandRef}
          className="hidden lg:flex flex-1 relative items-center justify-center overflow-hidden"
        >
          <div className="relative z-10 text-center px-12 xl:px-24">
            <h1
              ref={titleRef}
              className="text-3xl md:text-4xl xl:text-5xl font-bold text-white leading-tight tracking-tight"
            >
              AI 驱动的个性化学习，点亮知识新边界
            </h1>
            <p
              ref={descRef}
              className="mt-6 text-base md:text-lg text-white/80 font-medium max-w-lg mx-auto"
            >
              从机器学习到深度学习，为你量身打造专属成长路径，让每一次学习都精准高效
            </p>

            <div className="mt-10 flex items-center justify-center gap-8 text-white/60 text-sm">
              <div className="flex flex-col items-center gap-2">
                <div className="w-10 h-10 rounded-full bg-white/10 flex items-center justify-center text-white text-lg">📚</div>
                <span>智能课程</span>
              </div>
              <div className="flex flex-col items-center gap-2">
                <div className="w-10 h-10 rounded-full bg-white/10 flex items-center justify-center text-white text-lg">🎯</div>
                <span>精准推荐</span>
              </div>
              <div className="flex flex-col items-center gap-2">
                <div className="w-10 h-10 rounded-full bg-white/10 flex items-center justify-center text-white text-lg">🤖</div>
                <span>AI 辅导</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Login
