import React, { useEffect, useState, useRef, Suspense } from "react";
import { Routes, Route, Navigate, useNavigate } from "react-router-dom";
import { Layout, Spin } from "antd";
import AppHeader from "./components/AppHeader";
import Sidebar from "./components/Sidebar";
import GlobalToast from "./components/GlobalToast";
import { ErrorBoundary } from "./components/ErrorBoundary";
import Login from "./pages/Login";
import LandingPage from "./pages/LandingPage";
import NotFound from "./pages/NotFound";
import { useAppStore } from "./store";
import { authApi } from "./services/api";
import "./App.css";

const Dashboard = React.lazy(() => import("./pages/Dashboard"));
const Profile = React.lazy(() => import("./pages/Profile"));
const LearningPath = React.lazy(() => import("./pages/LearningPath"));
const ResourceCenter = React.lazy(() => import("./pages/ResourceCenter"));
const ResourceDetail = React.lazy(() => import("./pages/ResourceDetail"));
const PersonalSpace = React.lazy(() => import("./pages/PersonalSpace"));
const Tutor = React.lazy(() => import("./pages/Tutor"));
const LearningChallenge = React.lazy(() => import("./pages/LearningChallenge"));
const LeaderboardPlus = React.lazy(() => import("./pages/LeaderboardPlus"));
const ErrorDiagnosis = React.lazy(() => import("./pages/ErrorDiagnosis"));
const ProjectCollaboration = React.lazy(
  () => import("./pages/ProjectCollaboration"),
);
const TeacherDashboard = React.lazy(() => import("./pages/TeacherDashboard"));

const PageLoader = () => (
  <div className="flex items-center justify-center min-h-[60vh]">
    <Spin size="large" />
  </div>
);

/** 全屏初始化加载 */
const InitLoader = () => (
  <div className="fixed inset-0 flex items-center justify-center bg-slate-50 z-50">
    <Spin size="large" />
  </div>
);

/** 页面进入动画包装器 */
const PageWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // 页面切换时滚动到顶部
    window.scrollTo(0, 0);

    const el = ref.current;
    if (!el) return;
    el.style.opacity = "0";
    el.style.transform = "translateY(10px)";
    el.style.transition = "opacity 0.3s ease-out, transform 0.3s ease-out";

    const frame = requestAnimationFrame(() => {
      el.style.opacity = "1";
      el.style.transform = "translateY(0)";
    });

    return () => {
      cancelAnimationFrame(frame);
      el.style.opacity = "0";
    };
  }, []);

  return (
    <div ref={ref} style={{ opacity: 0 }}>
      {children}
    </div>
  );
};

/** 根据角色选择首页 */
const HomeRoute: React.FC = () => {
  const userInfo = useAppStore((s) => s.userInfo);
  if (userInfo?.role === "teacher" || userInfo?.role === "admin") {
    return <Navigate to="/teacher" replace />;
  }
  return (
    <PageWrapper>
      <Dashboard />
    </PageWrapper>
  );
};

const { Content } = Layout;

const PrivateLayout: React.FC = () => {
  const sidebarCollapsed = useAppStore((s) => s.sidebarCollapsed);

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
          <ErrorBoundary>
            <Suspense fallback={<PageLoader />}>
              <Routes>
                <Route path="/" element={<HomeRoute />} />
                <Route
                  path="/profile"
                  element={
                    <PageWrapper>
                      <Profile />
                    </PageWrapper>
                  }
                />
                <Route
                  path="/learning-path"
                  element={
                    <PageWrapper>
                      <LearningPath />
                    </PageWrapper>
                  }
                />
                <Route
                  path="/resources"
                  element={
                    <PageWrapper>
                      <ResourceCenter />
                    </PageWrapper>
                  }
                />
                <Route
                  path="/resource/:kpId"
                  element={
                    <PageWrapper>
                      <ResourceDetail />
                    </PageWrapper>
                  }
                />
                <Route
                  path="/personal"
                  element={
                    <PageWrapper>
                      <PersonalSpace />
                    </PageWrapper>
                  }
                />
                <Route
                  path="/challenges"
                  element={
                    <PageWrapper>
                      <LearningChallenge />
                    </PageWrapper>
                  }
                />
                <Route
                  path="/leaderboard"
                  element={
                    <PageWrapper>
                      <LeaderboardPlus />
                    </PageWrapper>
                  }
                />
                <Route
                  path="/tutor"
                  element={
                    <PageWrapper>
                      <Tutor />
                    </PageWrapper>
                  }
                />
                <Route
                  path="/error-diagnosis"
                  element={
                    <PageWrapper>
                      <ErrorDiagnosis />
                    </PageWrapper>
                  }
                />
                <Route
                  path="/project-collaboration"
                  element={
                    <PageWrapper>
                      <ProjectCollaboration />
                    </PageWrapper>
                  }
                />
                <Route
                  path="/teacher"
                  element={
                    <PageWrapper>
                      <TeacherDashboard />
                    </PageWrapper>
                  }
                />
                <Route
                  path="*"
                  element={
                    <PageWrapper>
                      <NotFound />
                    </PageWrapper>
                  }
                />
              </Routes>
            </Suspense>
          </ErrorBoundary>
        </Content>
      </Layout>
    </Layout>
  );
};

const App: React.FC = () => {
  const isLoggedIn = useAppStore((s) => s.isLoggedIn);
  const navigate = useNavigate();
  const [authChecked, setAuthChecked] = useState(!isLoggedIn); // 未登录时无需等待

  useEffect(() => {
    if (isLoggedIn) {
      authApi
        .me()
        .then((res) => {
          const u = res.data.data;
          useAppStore.getState().setUserInfo({
            student_id: u.student_id,
            username: u.username,
            role: u.role,
          });
        })
        .catch(() => {
          // token invalid, handled by interceptor (will trigger logout + redirect)
        })
        .finally(() => {
          setAuthChecked(true);
        });
    }
  }, [isLoggedIn]);

  // 监听全局认证过期事件，内存路由跳转（避免 window.location.href 硬刷新）
  useEffect(() => {
    const handler = () => navigate("/login", { replace: true });
    window.addEventListener("auth:expired", handler);
    return () => window.removeEventListener("auth:expired", handler);
  }, [navigate]);

  // 初始加载时验证 token，避免闪现登录页
  if (!authChecked) {
    return <InitLoader />;
  }

  return (
    <Routes>
      <Route
        path="/login"
        element={isLoggedIn ? <Navigate to="/" replace /> : <Login />}
      />
      <Route
        path="/"
        element={isLoggedIn ? <PrivateLayout /> : <LandingPage />}
      />
      <Route
        path="/*"
        element={isLoggedIn ? <PrivateLayout /> : <Navigate to="/" replace />}
      />
    </Routes>
  );
};

export default App;
