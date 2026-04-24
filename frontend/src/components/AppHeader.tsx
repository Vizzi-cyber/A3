import React, { useState, useRef, useEffect } from 'react'
import {
  Layout, Input, Badge, Avatar, Dropdown, Space, Typography, message, Popover, List, Modal, Spin,
} from 'antd'
import { useNavigate } from 'react-router-dom'
import {
  SearchOutlined,
  BellOutlined,
  QuestionCircleOutlined,
  UserOutlined,
  SettingOutlined,
  LogoutOutlined,
  FileTextOutlined,
  CheckCircleOutlined,
  RocketOutlined,
  TrophyOutlined,
  CloseOutlined,
} from '@ant-design/icons'
import { useAppStore } from '../store'
import { knowledgeApi, dashboardApi } from '../services/api'

const { Header } = Layout

interface SearchResult {
  kp_id: string
  name: string
  subject: string
  tags: string[]
}

interface NotificationItem {
  id: string
  title: string
  desc?: string
  type: string
  time: string
}

const AppHeader: React.FC = () => {
  const navigate = useNavigate()
  const userInfo = useAppStore((s) => s.userInfo)
  const logout = useAppStore((s) => s.logout)
  const studentId = useAppStore((s) => s.studentId)

  // 搜索
  const [searchValue, setSearchValue] = useState('')
  const [searchResults, setSearchResults] = useState<SearchResult[]>([])
  const [searchLoading, setSearchLoading] = useState(false)
  const [searchOpen, setSearchOpen] = useState(false)
  const searchRef = useRef<HTMLDivElement>(null)

  // 通知
  const [notifications, setNotifications] = useState<NotificationItem[]>([])
  const [notifLoading, setNotifLoading] = useState(false)
  const [notifOpen, setNotifOpen] = useState(false)

  // 帮助
  const [helpOpen, setHelpOpen] = useState(false)

  useEffect(() => {
    const timer = setTimeout(() => {
      if (searchValue.trim()) {
        doSearch(searchValue)
      } else {
        setSearchResults([])
        setSearchOpen(false)
      }
    }, 300)
    return () => clearTimeout(timer)
  }, [searchValue])

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(e.target as Node)) {
        setSearchOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const doSearch = async (q: string) => {
    setSearchLoading(true)
    try {
      const res = await knowledgeApi.search(q)
      setSearchResults(res.data?.data || [])
      setSearchOpen(true)
    } catch {
      setSearchResults([])
    } finally {
      setSearchLoading(false)
    }
  }

  const handleSelectResult = (kp: SearchResult) => {
    setSearchOpen(false)
    setSearchValue('')
    navigate('/resources')
    // 通过 localStorage 传递选中知识点，ResourceCenter 可读取
    localStorage.setItem('selected_kp_id', kp.kp_id)
    localStorage.setItem('selected_kp_name', kp.name)
    message.success(`已跳转至 ${kp.name}`)
  }

  const loadNotifications = async () => {
    if (notifLoading) return
    setNotifLoading(true)
    try {
      const res = await dashboardApi.getSummary(studentId)
      const d = res.data
      const list: NotificationItem[] = []
      if (d.tasks?.length) {
        d.tasks.forEach((t: Record<string, unknown>) => {
          list.push({
            id: String(t.task_id || ''),
            title: String(t.title || ''),
            desc: String(t.description || ''),
            type: 'task',
            time: '刚刚',
          })
        })
      }
      if (d.recommendations?.length) {
        d.recommendations.slice(0, 2).forEach((r: Record<string, unknown>, i: number) => {
          list.push({
            id: `rec_${i}`,
            title: String(r.title || ''),
            desc: '为你推荐的新资源',
            type: 'recommend',
            time: '今天',
          })
        })
      }
      if (d.stats?.streak_days > 0) {
        list.push({
          id: 'streak',
          title: `已连续打卡 ${d.stats.streak_days} 天`,
          desc: '继续保持！',
          type: 'achievement',
          time: '今天',
        })
      }
      setNotifications(list)
    } catch {
      setNotifications([])
    } finally {
      setNotifLoading(false)
    }
  }

  const handleMenuClick = ({ key }: { key: string }) => {
    if (key === 'profile') {
      navigate('/personal')
    } else if (key === 'settings') {
      message.info('设置功能开发中')
    } else if (key === 'logout') {
      logout()
      message.success('已退出登录')
      setTimeout(() => {
        window.location.href = '/login'
      }, 300)
    }
  }

  const items = [
    { key: 'profile', icon: <UserOutlined />, label: '个人中心' },
    { key: 'settings', icon: <SettingOutlined />, label: '设置' },
    { type: 'divider' as const },
    { key: 'logout', icon: <LogoutOutlined />, label: '退出登录' },
  ]

  const displayName = userInfo?.username || '学习者'

  const typeIcon: Record<string, React.ReactNode> = {
    task: <RocketOutlined className="text-primary" />,
    recommend: <FileTextOutlined className="text-emerald-500" />,
    achievement: <TrophyOutlined className="text-amber-500" />,
  }

  return (
    <>
      <Header className="glass px-6 md:px-8 flex items-center justify-between sticky top-0 z-40 h-16">
        <div className="flex items-center gap-4 flex-1">
          <Typography.Text className="text-slate-500 text-sm hidden xl:block">
            欢迎回来，{displayName}！继续今天的学习之旅吧！
          </Typography.Text>
        </div>

        <div className="flex items-center gap-4 md:gap-6">
          <div className="hidden md:block relative" ref={searchRef}>
            <SearchOutlined className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 z-10" />
            <Input
              placeholder="搜索课程、资源或知识点..."
              className="w-64 lg:w-72 rounded-full bg-slate-100 border-slate-200 pl-9 hover:bg-white focus:bg-white transition-all"
              value={searchValue}
              onChange={(e) => setSearchValue(e.target.value)}
              onPressEnter={() => searchResults[0] && handleSelectResult(searchResults[0])}
            />
            {searchOpen && (
              <div className="absolute top-full left-0 right-0 mt-2 bg-white rounded-xl shadow-card border border-slate-100 z-50 overflow-hidden">
                <Spin spinning={searchLoading}>
                  {searchResults.length > 0 ? (
                    <List
                      size="small"
                      dataSource={searchResults}
                      renderItem={(item) => (
                        <List.Item
                          className="cursor-pointer hover:bg-slate-50 px-4"
                          onClick={() => handleSelectResult(item)}
                        >
                          <List.Item.Meta
                            title={<span className="text-sm text-slate-700">{item.name}</span>}
                            description={<span className="text-xs text-slate-400">{item.subject} {item.tags?.join(' ')}</span>}
                          />
                        </List.Item>
                      )}
                    />
                  ) : (
                    <div className="px-4 py-3 text-sm text-slate-400">未找到相关知识点</div>
                  )}
                </Spin>
              </div>
            )}
          </div>

          <Space size={12}>
            <Popover
              open={notifOpen}
              onOpenChange={(open) => {
                setNotifOpen(open)
                if (open) loadNotifications()
              }}
              placement="bottomRight"
              content={
                <div className="w-72">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-semibold text-slate-800 text-sm">通知中心</span>
                    <button
                      className="text-slate-400 hover:text-primary text-xs"
                      onClick={() => setNotifOpen(false)}
                    >
                      <CloseOutlined />
                    </button>
                  </div>
                  <Spin spinning={notifLoading}>
                    {notifications.length > 0 ? (
                      <List
                        size="small"
                        dataSource={notifications}
                        renderItem={(n) => (
                          <List.Item className="px-0">
                            <List.Item.Meta
                              avatar={<div className="mt-0.5">{typeIcon[n.type] || <BellOutlined />}</div>}
                              title={<span className="text-sm text-slate-700">{n.title}</span>}
                              description={<span className="text-xs text-slate-400">{n.desc} · {n.time}</span>}
                            />
                          </List.Item>
                        )}
                      />
                    ) : (
                      <div className="text-center py-4 text-slate-400 text-sm">暂无新通知</div>
                    )}
                  </Spin>
                </div>
              }
              trigger="click"
            >
              <Badge dot color="#ef4444">
                <button className="w-9 h-9 rounded-full bg-slate-50 hover:bg-slate-100 flex items-center justify-center text-slate-500 hover:text-primary transition-all"
                >
                  <BellOutlined className="text-lg" />
                </button>
              </Badge>
            </Popover>
            <button
              className="w-9 h-9 rounded-full bg-slate-50 hover:bg-slate-100 flex items-center justify-center text-slate-500 hover:text-primary transition-all"
              onClick={() => setHelpOpen(true)}
            >
              <QuestionCircleOutlined className="text-lg" />
            </button>

            <Dropdown menu={{ items, onClick: handleMenuClick }} placement="bottomRight" arrow>
              <Space className="cursor-pointer hover:bg-slate-50/80 px-3 py-1.5 rounded-full transition-all border border-transparent hover:border-slate-100">
                <Avatar size="small" icon={<UserOutlined />} className="bg-primary" />
                <span className="hidden sm:inline text-slate-700 font-medium text-sm">{displayName}</span>
              </Space>
            </Dropdown>
          </Space>
        </div>
      </Header>

      <Modal
        title="帮助中心"
        open={helpOpen}
        onCancel={() => setHelpOpen(false)}
        footer={null}
        width={560}
      >
        <div className="space-y-4 text-slate-600 text-sm leading-relaxed">
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-100">
            <p className="font-semibold text-slate-800 mb-2">🚀 快速开始</p>
            <p>1. 登录后进入「学习仪表盘」查看今日任务和推荐资源。</p>
            <p>2. 在「学习中心」选择左侧目录中的知识点，查看图文讲义、代码示例和练习题。</p>
            <p>3. 遇到不懂的问题，随时打开「智能辅导」向 AI 助手提问，支持发送图片。</p>
          </div>
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-100">
            <p className="font-semibold text-slate-800 mb-2">📚 学习中心功能</p>
            <p>• 图文讲义：AI 生成的 Markdown 格式文档</p>
            <p>• 代码编辑器：可编辑 Python 代码，点击「运行代码」查看执行结果</p>
            <p>• 练习题：选择题，点击选项即可作答，答对答错有即时反馈</p>
            <p>• 思维导图：当前知识点的结构概览</p>
            <p>• 我的笔记：记录学习心得，自动同步到学习数据</p>
            <p>• 文生图：输入描述生成 AI 图像，辅助理解抽象概念</p>
          </div>
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-100">
            <p className="font-semibold text-slate-800 mb-2">🎯 学习路径</p>
            <p>系统会根据你的画像自动生成个性化学习路径。你可以在「学习路径」页面查看进度，点击节点查看详情，或调整路径偏好。</p>
          </div>
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-100">
            <p className="font-semibold text-slate-800 mb-2">👤 个人空间</p>
            <p>查看学习历史趋势、收藏夹资源和画像详情。系统会根据你的学习行为持续优化推荐内容。</p>
          </div>
          <div className="text-center pt-2">
            <Typography.Text className="text-xs text-slate-400">如有问题请联系管理员 · AI Learning 团队</Typography.Text>
          </div>
        </div>
      </Modal>
    </>
  )
}

export default AppHeader
