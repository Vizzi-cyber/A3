import React, { useEffect, useState, Suspense } from 'react'
import { Routes, Route, useLocation, Navigate } from 'react-router-dom'
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

const { Content } = Layout

const PrivateLayout: React.FC = () => {
  const location = useLocation()
  const sidebarCollapsed = useAppStore((s) => s.sidebarCollapsed)
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(false)
    const timer = setTimeout(() => setMounted(true), 30)
    return () => clearTimeout(timer)
  }, [location.pathname])

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
          <div
            key={location.pathname}
            className={mounted ? 'page-enter' : 'opacity-0'}
          >
            <Suspense fallback={<PageLoader />}>
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/profile" element={<Profile />} />
                <Route path="/learning-path" element={<LearningPath />} />
                <Route path="/resources" element={<ResourceCenter />} />
                <Route path="/resource/:kpId" element={<ResourceDetail />} />
                <Route path="/personal" element={<PersonalSpace />} />
                <Route path="/tutor" element={<Tutor />} />
                <Route path="*" element={<NotFound />} />
              </Routes>
            </Suspense>
          </div>
        </Content>
      </Layout>
    </Layout>
  )
}

const App: React.FC = () => {
  const isLoggedIn = useAppStore((s) => s.isLoggedIn)
  const setUserInfo = useAppStore((s) => s.setUserInfo)

  useEffect(() => {
    if (isLoggedIn) {
      authApi.me().then((res) => {
        const u = res.data.data
        setUserInfo({ student_id: u.student_id, username: u.username, role: u.role })
      }).catch(() => {
        // token invalid, handled by interceptor
      })
    }
  }, [isLoggedIn, setUserInfo])

  return (
    <Routes>
      <Route path="/login" element={isLoggedIn ? <Navigate to="/" replace /> : <Login />} />
      <Route path="/*" element={isLoggedIn ? <PrivateLayout /> : <Navigate to="/login" replace />} />
    </Routes>
  )
}

export default App
