import React from 'react'
import { Layout, Menu, Avatar, Typography, Space, Tooltip } from 'antd'
import { useNavigate, useLocation } from 'react-router-dom'
import {
  DashboardOutlined,
  PieChartOutlined,
  NodeIndexOutlined,
  ReadOutlined,
  UserOutlined,
  RobotOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
} from '@ant-design/icons'
import { useAppStore } from '../store'

const { Sider } = Layout

const menuItems = [
  { key: '/', icon: <DashboardOutlined />, label: '学习仪表盘' },
  { key: '/profile', icon: <PieChartOutlined />, label: '对话画像' },
  { key: '/learning-path', icon: <NodeIndexOutlined />, label: '学习路径' },
  { key: '/resources', icon: <ReadOutlined />, label: '学习中心' },
  { key: '/tutor', icon: <RobotOutlined />, label: '智能辅导' },
  { key: '/personal', icon: <UserOutlined />, label: '个人空间' },
]

const Sidebar: React.FC = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const collapsed = useAppStore((s) => s.sidebarCollapsed)
  const toggleSidebar = useAppStore((s) => s.toggleSidebar)

  const navMenuItems = React.useMemo(
    () =>
      menuItems.map((item) => ({
        key: item.key,
        icon: item.icon,
        label: collapsed ? (
          <Tooltip title={item.label} placement="right">
            <span>{item.label}</span>
          </Tooltip>
        ) : (
          item.label
        ),
        onClick: () => navigate(item.key),
      })),
    [collapsed, navigate],
  )

  return (
    <Sider
      width={240}
      collapsedWidth={80}
      collapsed={collapsed}
      theme="light"
      className="fixed left-0 top-0 h-screen z-50 border-r border-slate-200 bg-white transition-all duration-300"
    >
      {/* Logo区域 */}
      <div className="h-16 flex items-center px-5 border-b border-slate-100 justify-between">
        <Space>
          <div className="w-9 h-9 rounded-xl flex items-center justify-center bg-primary">
            <RobotOutlined className="text-white text-lg" />
          </div>
          {!collapsed && (
            <Typography.Title level={5} className="!m-0 text-slate-900 font-bold tracking-tight">
              AI Learning
            </Typography.Title>
          )}
        </Space>
        <button
          onClick={toggleSidebar}
          className="text-slate-400 hover:text-primary transition-colors p-1 rounded-lg hover:bg-slate-50"
        >
          {collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
        </button>
      </div>

      {/* 菜单区域 */}
      <div className="py-4 px-2">
        <Menu
          mode="inline"
          inlineCollapsed={collapsed}
          selectedKeys={[location.pathname]}
          items={navMenuItems}
          className="border-r-0 bg-transparent"
          style={{
            '--ant-menu-item-selected-bg': 'rgba(79, 70, 229, 0.08)',
            '--ant-menu-item-selected-color': '#4f46e5',
          } as React.CSSProperties}
        />
      </div>

      {/* 底部学习进度 */}
      {!collapsed && (
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-slate-100">
          <div className="bg-slate-50 rounded-xl p-4 border border-slate-100">
            <Typography.Text className="text-xs text-slate-500 block mb-2 font-medium">
              今日学习时长
            </Typography.Text>
            <Typography.Text className="text-2xl font-bold text-primary block tracking-tight">
              1h 24m
            </Typography.Text>
            <div className="mt-3 h-1.5 bg-slate-200 rounded-full overflow-hidden">
              <div className="h-full w-3/5 bg-primary rounded-full" />
            </div>
            <div className="flex justify-between mt-1.5">
              <Typography.Text className="text-xs text-slate-400">目标: 2小时</Typography.Text>
              <Typography.Text className="text-xs text-primary font-medium">60%</Typography.Text>
            </div>
          </div>
        </div>
      )}

      {collapsed && (
        <div className="absolute bottom-4 left-0 right-0 flex justify-center">
          <Tooltip title="今日已学 1h 24m">
            <div className="w-10 h-10 rounded-full bg-primary flex items-center justify-center text-white text-xs font-bold">
              60%
            </div>
          </Tooltip>
        </div>
      )}
    </Sider>
  )
}

export default Sidebar
