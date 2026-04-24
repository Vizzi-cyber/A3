import { create } from 'zustand'
import type { StudentProfile, LearningPath, ToastState } from '../types'

interface UserInfo {
  student_id: string
  username: string
  role: string
}

interface AppState {
  studentId: string
  setStudentId: (id: string) => void

  token: string | null
  isLoggedIn: boolean
  userInfo: UserInfo | null
  login: (token: string, studentId: string) => void
  logout: () => void
  setUserInfo: (info: UserInfo) => void

  profile: StudentProfile | null
  setProfile: (profile: StudentProfile | null) => void

  currentPath: LearningPath | null
  setCurrentPath: (path: LearningPath | null) => void

  loading: boolean
  setLoading: (loading: boolean) => void

  toast: ToastState | null
  setToast: (toast: ToastState | null) => void

  sidebarCollapsed: boolean
  toggleSidebar: () => void
}

const storedToken = localStorage.getItem('token')
const storedStudentId = localStorage.getItem('student_id')

export const useAppStore = create<AppState>((set) => ({
  studentId: storedStudentId || 'student_001',
  setStudentId: (id) => {
    localStorage.setItem('student_id', id)
    set({ studentId: id })
  },

  token: storedToken,
  isLoggedIn: !!storedToken,
  userInfo: null,
  login: (token, studentId) => {
    localStorage.setItem('token', token)
    localStorage.setItem('student_id', studentId)
    set({ token, isLoggedIn: true, studentId })
  },
  logout: () => {
    localStorage.removeItem('token')
    localStorage.removeItem('student_id')
    set({ token: null, isLoggedIn: false, userInfo: null, studentId: '' })
  },
  setUserInfo: (info) => set({ userInfo: info }),

  profile: null,
  setProfile: (profile) => set({ profile }),

  currentPath: null,
  setCurrentPath: (path) => set({ currentPath: path }),

  loading: false,
  setLoading: (loading) => set({ loading }),

  toast: null,
  setToast: (toast) => set({ toast }),

  sidebarCollapsed: false,
  toggleSidebar: () => set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),
}))
