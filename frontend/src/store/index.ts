import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { ToastState } from "../types";

interface UserInfo {
  student_id: string;
  username: string;
  role: string;
}

interface AppState {
  studentId: string;
  setStudentId: (_id: string) => void;

  token: string | null;
  isLoggedIn: boolean;
  userInfo: UserInfo | null;
  login: (_token: string, _studentId: string) => void;
  logout: () => void;
  setUserInfo: (_info: UserInfo) => void;

  currentSubject: string;
  setCurrentSubject: (_subject: string) => void;

  toast: ToastState | null;
  setToast: (_toast: ToastState | null) => void;

  sidebarCollapsed: boolean;
  toggleSidebar: () => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      studentId: "",
      setStudentId: (id) => set({ studentId: id }),

      token: null,
      isLoggedIn: false,
      userInfo: null,
      login: (token, studentId) => set({ token, isLoggedIn: true, studentId }),
      logout: () =>
        set({
          token: null,
          isLoggedIn: false,
          userInfo: null,
          studentId: "",
        }),
      setUserInfo: (info) => set({ userInfo: info }),

      currentSubject: "C语言",
      setCurrentSubject: (subject) => set({ currentSubject: subject }),

      toast: null,
      setToast: (toast) => set({ toast }),

      sidebarCollapsed: false,
      toggleSidebar: () =>
        set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),
    }),
    {
      name: "ai-learning-storage",
      partialize: (state) => ({
        token: state.token,
        studentId: state.studentId,
        userInfo: state.userInfo,
        currentSubject: state.currentSubject,
      }),
      merge: (persisted, current) => {
        const p = persisted as Partial<AppState>;
        return {
          ...current,
          ...p,
          isLoggedIn: !!p.token,
        };
      },
    },
  ),
);
