import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { ToastState } from "../types";

/** Decode JWT payload without verification (for expiry check only) */
function decodeJwtPayload(token: string): Record<string, unknown> | null {
  try {
    const base64Url = token.split(".")[1];
    const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split("")
        .map((c) => "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2))
        .join(""),
    );
    return JSON.parse(jsonPayload);
  } catch {
    return null;
  }
}

function isTokenExpired(token: string): boolean {
  const payload = decodeJwtPayload(token);
  if (!payload || typeof payload.exp !== "number") return false;
  return payload.exp * 1000 < Date.now();
}

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
        const token = typeof p.token === "string" ? p.token : null;
        const tokenValid = !!token && !isTokenExpired(token);
        const studentId = typeof p.studentId === "string" ? p.studentId : "";
        const userInfo =
          p.userInfo &&
          typeof p.userInfo === "object" &&
          "student_id" in p.userInfo
            ? (p.userInfo as UserInfo)
            : current.userInfo;
        const currentSubject =
          typeof p.currentSubject === "string"
            ? p.currentSubject
            : current.currentSubject;
        return {
          ...current,
          token: tokenValid ? token : null,
          isLoggedIn: tokenValid,
          studentId: tokenValid ? studentId : "",
          userInfo,
          currentSubject,
        };
      },
    },
  ),
);
