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
import { authApi, profileApi } from "./services/api";
import OnboardingQuestionnaire, {
  isOnboardingCompleted,
} from "./components/OnboardingQuestionnaire";
import "./App.css";

const SpacePortal = React.lazy(() => import("./pages/SpacePortal"));
const HorizonHome = React.lazy(() => import("./pages/HorizonHome"));
const ConstellationHome = React.lazy(() => import("./pages/ConstellationHome"));
const OverviewHome = React.lazy(() => import("./pages/OverviewHome"));
const HoloHome = React.lazy(() => import("./pages/HoloHome"));
const FragmentsHome = React.lazy(() => import("./pages/FragmentsHome"));
const NeoHome = React.lazy(() => import("./pages/NeoHome"));
const Dashboard = React.lazy(() => import("./pages/Dashboard"));
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
const KnowledgeBase = React.lazy(() => import("./pages/KnowledgeBase"));
const TeacherPersonalSpace = React.lazy(
  () => import("./pages/TeacherPersonalSpace"),
);

// 教师端页面
const TeacherHome = React.lazy(() => import("./pages/teacher/TeacherHome"));
const AssignmentManagement = React.lazy(
  () => import("./pages/teacher/AssignmentManagement"),
);
const StudentManagement = React.lazy(
  () => import("./pages/teacher/StudentManagement"),
);
const TeachingResources = React.lazy(
  () => import("./pages/teacher/TeachingResources"),
);
const LearningAnalytics = React.lazy(
  () => import("./pages/teacher/LearningAnalytics"),
);
const ClassAnalytics = React.lazy(
  () => import("./pages/teacher/ClassAnalytics"),
);
const ClassComparison = React.lazy(
  () => import("./pages/teacher/ClassComparison"),
);
const ReportExport = React.lazy(() => import("./pages/teacher/ReportExport"));
const SystemSettings = React.lazy(
  () => import("./pages/teacher/SystemSettings"),
);
const LessonPlan = React.lazy(() => import("./pages/teacher/LessonPlan"));
const LearningInsights = React.lazy(
  () => import("./pages/teacher/LearningInsights"),
);
const SmartQuiz = React.lazy(() => import("./pages/teacher/SmartQuiz"));
const PilotReport = React.lazy(() => import("./pages/teacher/PilotReport"));

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
    window.scrollTo(0, 0);
    const el = ref.current;
    if (!el) return;
    // 页面切换过渡：淡入 + 上浮 + 轻微缩放（0.35s）
    el.style.opacity = "0";
    el.style.transform = "translateY(20px) scale(0.99)";
    el.style.transition =
      "opacity 0.35s cubic-bezier(0.22, 1, 0.36, 1), transform 0.35s cubic-bezier(0.22, 1, 0.36, 1)";
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        el.style.opacity = "1";
        el.style.transform = "translateY(0) scale(1)";
      });
    });
  }, []);

  return <div ref={ref}>{children}</div>;
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
                <Route
                  path="/"
                  element={
                    <PageWrapper>
                      <NeoHome />
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
                  path="/teacher/home"
                  element={
                    <PageWrapper>
                      <TeacherHome />
                    </PageWrapper>
                  }
                />
                <Route
                  path="/teacher/assignments"
                  element={
                    <PageWrapper>
                      <AssignmentManagement />
                    </PageWrapper>
                  }
                />
                <Route
                  path="/teacher/students"
                  element={
                    <PageWrapper>
                      <StudentManagement />
                    </PageWrapper>
                  }
                />
                <Route
                  path="/teacher/resources"
                  element={
                    <PageWrapper>
                      <TeachingResources />
                    </PageWrapper>
                  }
                />
                <Route
                  path="/teacher/analytics"
                  element={
                    <PageWrapper>
                      <LearningAnalytics />
                    </PageWrapper>
                  }
                />
                <Route
                  path="/teacher/class-analytics"
                  element={
                    <PageWrapper>
                      <ClassAnalytics />
                    </PageWrapper>
                  }
                />
                <Route
                  path="/teacher/class-comparison"
                  element={
                    <PageWrapper>
                      <ClassComparison />
                    </PageWrapper>
                  }
                />
                <Route
                  path="/teacher/reports"
                  element={
                    <PageWrapper>
                      <ReportExport />
                    </PageWrapper>
                  }
                />
                <Route
                  path="/teacher/pilot-report"
                  element={
                    <PageWrapper>
                      <PilotReport />
                    </PageWrapper>
                  }
                />
                <Route
                  path="/teacher/lesson-plan"
                  element={
                    <PageWrapper>
                      <LessonPlan />
                    </PageWrapper>
                  }
                />
                <Route
                  path="/teacher/insights"
                  element={
                    <PageWrapper>
                      <LearningInsights />
                    </PageWrapper>
                  }
                />
                <Route
                  path="/teacher/smart-quiz"
                  element={
                    <PageWrapper>
                      <SmartQuiz />
                    </PageWrapper>
                  }
                />
                <Route
                  path="/teacher/settings"
                  element={
                    <PageWrapper>
                      <SystemSettings />
                    </PageWrapper>
                  }
                />
                <Route
                  path="/teacher/personal"
                  element={
                    <PageWrapper>
                      <TeacherPersonalSpace />
                    </PageWrapper>
                  }
                />
                <Route
                  path="/knowledge-base"
                  element={
                    <PageWrapper>
                      <KnowledgeBase />
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
  const [showOnboarding, setShowOnboarding] = useState(false);
  const [onboardingSubject, setOnboardingSubject] = useState("C语言");
  const currentSubject = useAppStore((s) => s.currentSubject);

  useEffect(() => {
    if (isLoggedIn) {
      authApi
        .me()
        .then(async (res) => {
          const u = res.data.data;
          useAppStore.getState().setUserInfo({
            student_id: u.student_id,
            username: u.username,
            role: u.role,
          });

          // 检查是否需要引导问卷（仅学生，仅C语言）
          if (u.role === "student" || u.role === "user") {
            if (!isOnboardingCompleted("C语言")) {
              setOnboardingSubject("C语言");
              setShowOnboarding(true);
            }
          }
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
    <>
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
      <OnboardingQuestionnaire
        open={showOnboarding}
        subject={onboardingSubject}
        onComplete={() => {
          setShowOnboarding(false);
          navigate("/learning-path");
        }}
      />
    </>
  );
};

export default App;
