import React, { useEffect, useState, Suspense } from 'react'
import { Routes, Route, Navigate, useNavigate } from 'react-router-dom'
import { Layout, Spin } from 'antd'
import AppHeader from './components/AppHeader'
import Sidebar from './components/Sidebar'
import GlobalToast from './components/GlobalToast'
import Login from './pages/Login'
import NotFound from './pages/NotFound'
import { useAppStore } from './store'
import { authApi } from './services/api'
import './App.css'

const Dashboard = React.lazy(() => import('./pages/Dashboard'))
const Profile = React.lazy(() => import('./pages/Profile'))
const LearningPath = React.lazy(() => import('./pages/LearningPath'))
const ResourceCenter = React.lazy(() => import('./pages/ResourceCenter'))
const ResourceDetail = React.lazy(() => import('./pages/ResourceDetail'))
const PersonalSpace = React.lazy(() => import('./pages/PersonalSpace'))
const Tutor = React.lazy(() => import('./pages/Tutor'))

const PageLoader = () => (
  <div className="flex items-center justify-center min-h-[60vh]">
    <Spin size="large" />
  </div>
)

/** 页面进入动画包装器：只在自身挂载时触发，不强制重挂载 Routes/Suspense */
const PageWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(false)
    const timer = setTimeout(() => setMounted(true), 30)
    return () => clearTimeout(timer)
  }, [])

  return (
    <div className={mounted ? 'page-enter' : 'opacity-0'}>
      {children}
    </div>
  )
}

const { Content } = Layout

const PrivateLayout: React.FC = () => {
  const sidebarCollapsed = useAppStore((s) => s.sidebarCollapsed)

  return (
    <Layout className="min-h-screen bg-slate-50">
      <GlobalToast />
      <Sidebar />
      <Layout
        className="transition-all duration-300 ease-smooth bg-slate-50"
        style={{ marginLeft: sidebarCollapsed ? 80 : 240 }}
      >
        <AppHeader />
        <Content className="p-6 md:p-8 min-h-[280px]">
          <Suspense fallback={<PageLoader />}>
            <Routes>
              <Route path="/" element={<PageWrapper><Dashboard /></PageWrapper>} />
              <Route path="/profile" element={<PageWrapper><Profile /></PageWrapper>} />
              <Route path="/learning-path" element={<PageWrapper><LearningPath /></PageWrapper>} />
              <Route path="/resources" element={<PageWrapper><ResourceCenter /></PageWrapper>} />
              <Route path="/resource/:kpId" element={<PageWrapper><ResourceDetail /></PageWrapper>} />
              <Route path="/personal" element={<PageWrapper><PersonalSpace /></PageWrapper>} />
              <Route path="/tutor" element={<PageWrapper><Tutor /></PageWrapper>} />
              <Route path="*" element={<PageWrapper><NotFound /></PageWrapper>} />
            </Routes>
          </Suspense>
        </Content>
      </Layout>
    </Layout>
  )
}

const App: React.FC = () => {
  const isLoggedIn = useAppStore((s) => s.isLoggedIn)
  const navigate = useNavigate()

  useEffect(() => {
    if (isLoggedIn) {
      authApi.me().then((res) => {
        const u = res.data.data
        useAppStore.getState().setUserInfo({ student_id: u.student_id, username: u.username, role: u.role })
      }).catch(() => {
        // token invalid, handled by interceptor
      })
    }
  }, [isLoggedIn])

  // 监听全局认证过期事件，内存路由跳转（避免 window.location.href 硬刷新）
  useEffect(() => {
    const handler = () => navigate('/login', { replace: true })
    window.addEventListener('auth:expired', handler)
    return () => window.removeEventListener('auth:expired', handler)
  }, [navigate])

  return (
    <Routes>
      <Route path="/login" element={isLoggedIn ? <Navigate to="/" replace /> : <Login />} />
      <Route path="/*" element={isLoggedIn ? <PrivateLayout /> : <Navigate to="/login" replace />} />
    </Routes>
  )
}

export default App
