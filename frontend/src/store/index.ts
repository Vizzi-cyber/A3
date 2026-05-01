import { create } from 'zustand'
import { persist } from 'zustand/middleware'
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

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      studentId: 'student_001',
      setStudentId: (id) => set({ studentId: id }),

      token: null,
      isLoggedIn: false,
      userInfo: null,
      login: (token, studentId) =>
        set({ token, isLoggedIn: true, studentId }),
      logout: () =>
        set({ token: null, isLoggedIn: false, userInfo: null, studentId: '' }),
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
      toggleSidebar: () =>
        set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),
    }),
    {
      name: 'ai-learning-storage',
      partialize: (state) => ({
        token: state.token,
        studentId: state.studentId,
      }),
      merge: (persisted, current) => {
        const p = persisted as Partial<AppState>
        return {
          ...current,
          ...p,
          isLoggedIn: !!p.token,
        }
      },
    }
  )
)
