import React, { useEffect, useState } from 'react'
import { Routes, Route, useLocation, Navigate } from 'react-router-dom'
import { Layout } from 'antd'
import AppHeader from './components/AppHeader'
import Sidebar from './components/Sidebar'
import GlobalToast from './components/GlobalToast'
import Dashboard from './pages/Dashboard'
import Profile from './pages/Profile'
import LearningPath from './pages/LearningPath'
import ResourceCenter from './pages/ResourceCenter'
import PersonalSpace from './pages/PersonalSpace'
import Tutor from './pages/Tutor'
import Login from './pages/Login'
import NotFound from './pages/NotFound'
import { useAppStore } from './store'
import { authApi } from './services/api'
import './App.css'

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
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/profile" element={<Profile />} />
              <Route path="/learning-path" element={<LearningPath />} />
              <Route path="/resources" element={<ResourceCenter />} />
              <Route path="/personal" element={<PersonalSpace />} />
              <Route path="/tutor" element={<Tutor />} />
              <Route path="*" element={<NotFound />} />
            </Routes>
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
