import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, Form, Input, Button, Tabs, Typography, message } from 'antd'
import { RobotOutlined, UserOutlined, LockOutlined, MailOutlined } from '@ant-design/icons'
import { authApi } from '../services/api'
import { useAppStore } from '../store'

const Login: React.FC = () => {
  const navigate = useNavigate()
  const login = useAppStore((s) => s.login)
  const setUserInfo = useAppStore((s) => s.setUserInfo)
  const [activeTab, setActiveTab] = useState('login')
  const [loading, setLoading] = useState(false)

  const handleLogin = async (values: { student_id: string; password: string }) => {
    setLoading(true)
    try {
      const res = await authApi.login(values)
      const token = res.data.access_token
      login(token, values.student_id)

      // 获取用户信息
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

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="flex items-center justify-center gap-3 mb-8">
          <div className="w-12 h-12 rounded-xl bg-primary flex items-center justify-center shadow-glow">
            <RobotOutlined className="text-white text-2xl" />
          </div>
          <div>
            <Typography.Title level={3} className="!m-0 text-slate-900">
              AI Learning
            </Typography.Title>
            <Typography.Text className="text-slate-400 text-sm">
              基于大模型的个性化学习系统
            </Typography.Text>
          </div>
        </div>

        <Card className="rounded-2xl shadow-card border-slate-100">
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
        </Card>

        {import.meta.env.DEV && (
          <div className="text-center mt-6 text-slate-400 text-sm">
            <p>测试账号：student_001 / 123456</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default Login
