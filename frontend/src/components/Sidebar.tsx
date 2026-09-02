import React, { useState, useEffect } from "react";
import { Layout, Menu, Typography, Space, Tooltip } from "antd";
import { useNavigate, useLocation } from "react-router-dom";
import {
  DashboardOutlined,
  NodeIndexOutlined,
  ReadOutlined,
  UserOutlined,
  RobotOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  FlagOutlined,
  TrophyOutlined,
  BugOutlined,
  ProjectOutlined,
  ThunderboltOutlined,
  ExperimentOutlined,
  BookOutlined,
  HomeOutlined,
  FileTextOutlined,
  TeamOutlined,
  BarChartOutlined,
  LineChartOutlined,
  FileExcelOutlined,
  SettingOutlined,
  BulbOutlined,
  RocketOutlined,
} from "@ant-design/icons";
import { useAppStore } from "../store";
import { dashboardApi, withCache } from "../services/api";

const { Sider } = Layout;

const preloadRoute = (path: string) => {
  const loaders: Record<string, () => Promise<unknown>> = {
    "/": () => import("../pages/Dashboard"),
    "/tutor": () => import("../pages/Tutor"),
    "/learning-path": () => import("../pages/LearningPath"),
    "/resources": () => import("../pages/ResourceCenter"),
    "/challenges": () => import("../pages/LearningChallenge"),
    "/personal": () => import("../pages/PersonalSpace"),
    "/knowledge-base": () => import("../pages/KnowledgeBase"),
  };
  loaders[path]?.();
};

const studentMenuItems = [
  { key: "/", icon: <DashboardOutlined />, label: "学习仪表盘" },

  { key: "/tutor", icon: <RobotOutlined />, label: "智能辅导" },
  { key: "/learning-path", icon: <NodeIndexOutlined />, label: "学习路径" },
  { key: "/resources", icon: <ReadOutlined />, label: "学习中心" },
  { key: "/challenges", icon: <ThunderboltOutlined />, label: "知识冒险" },
  { key: "/error-diagnosis", icon: <BugOutlined />, label: "错误诊断" },
  {
    key: "/project-collaboration",
    icon: <ProjectOutlined />,
    label: "项目协作",
  },
  { key: "/personal", icon: <UserOutlined />, label: "个人空间" },
  { key: "/knowledge-base", icon: <BookOutlined />, label: "知识库" },
];

const teacherMenuItems = [
  { key: "/teacher", icon: <DashboardOutlined />, label: "首页" },
  {
    key: "/teacher/assignments",
    icon: <FileTextOutlined />,
    label: "作业管理",
  },
  { key: "/teacher/students", icon: <TeamOutlined />, label: "学生管理" },
  { key: "/teacher/resources", icon: <BookOutlined />, label: "备课资源" },
  { key: "/teacher/analytics", icon: <BarChartOutlined />, label: "学情分析" },
  {
    key: "/teacher/class-analytics",
    icon: <LineChartOutlined />,
    label: "班级学情",
  },
  {
    key: "/teacher/class-comparison",
    icon: <ExperimentOutlined />,
    label: "班级对比",
  },
  { key: "/teacher/reports", icon: <FileExcelOutlined />, label: "报告导出" },
  {
    key: "/teacher/pilot-report",
    icon: <BarChartOutlined />,
    label: "试点数据分析",
  },
  { type: "divider" as const },
  { key: "/teacher/lesson-plan", icon: <BulbOutlined />, label: "AI智能备课" },
  {
    key: "/teacher/insights",
    icon: <LineChartOutlined />,
    label: "AI学情洞察",
  },
  { key: "/teacher/smart-quiz", icon: <RocketOutlined />, label: "AI智能组卷" },
  { type: "divider" as const },
  { key: "/teacher/settings", icon: <SettingOutlined />, label: "系统设置" },
  { key: "/teacher/personal", icon: <UserOutlined />, label: "个人空间" },
];

const Sidebar: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const collapsed = useAppStore((s) => s.sidebarCollapsed);
  const toggleSidebar = useAppStore((s) => s.toggleSidebar);
  const studentId = useAppStore((s) => s.studentId);
  const userInfo = useAppStore((s) => s.userInfo);
  const isTeacher = userInfo?.role === "teacher" || userInfo?.role === "admin";
  const menuItems = isTeacher ? teacherMenuItems : studentMenuItems;
  const [todayMinutes, setTodayMinutes] = useState(0);

  useEffect(() => {
    withCache(`summary:${studentId}`, 30_000, () =>
      dashboardApi.getSummary(studentId),
    )
      .then((res) => {
        setTodayMinutes(res.data?.stats?.today_duration_min || 0);
      })
      .catch(() => {});
  }, [studentId]);

  const handleNavigate = (path: string) => {
    if (location.pathname === path) return;
    navigate(path);
  };

  const navMenuItems = React.useMemo(
    () =>
      menuItems
        .filter((item) => item.key)
        .map((item) => ({
          key: item.key!,
          icon: item.icon,
          label: collapsed ? (
            <Tooltip title={item.label} placement="right">
              <span>{item.label}</span>
            </Tooltip>
          ) : (
            item.label
          ),
          onClick: () => handleNavigate(item.key!),
          onMouseEnter: () => preloadRoute(item.key!),
          onFocus: () => preloadRoute(item.key!),
        })),
    [collapsed, navigate, location.pathname],
  );

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
            <Typography.Title
              level={5}
              className="!m-0 text-slate-900 font-bold tracking-tight"
            >
              LearnLab
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
          style={
            {
              "--ant-menu-item-selected-bg": "rgba(79, 70, 229, 0.08)",
              "--ant-menu-item-selected-color": "#4f46e5",
            } as React.CSSProperties
          }
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
              {todayMinutes >= 60
                ? `${Math.floor(todayMinutes / 60)}h ${todayMinutes % 60}m`
                : `${todayMinutes}m`}
            </Typography.Text>
            <div className="mt-3 h-1.5 bg-slate-200 rounded-full overflow-hidden">
              <div
                className="h-full bg-primary rounded-full"
                style={{
                  width: `${Math.min(100, Math.round((todayMinutes / 120) * 100))}%`,
                }}
              />
            </div>
            <div className="flex justify-between mt-1.5">
              <Typography.Text className="text-xs text-slate-400">
                目标: 2小时
              </Typography.Text>
              <Typography.Text className="text-xs text-primary font-medium">
                {Math.min(100, Math.round((todayMinutes / 120) * 100))}%
              </Typography.Text>
            </div>
          </div>
        </div>
      )}

      {collapsed && (
        <div className="absolute bottom-4 left-0 right-0 flex justify-center">
          <Tooltip
            title={`今日已学 ${todayMinutes >= 60 ? `${Math.floor(todayMinutes / 60)}h ${todayMinutes % 60}m` : `${todayMinutes}m`}`}
          >
            <div className="w-10 h-10 rounded-full bg-primary flex items-center justify-center text-white text-xs font-bold">
              {Math.min(100, Math.round((todayMinutes / 120) * 100))}%
            </div>
          </Tooltip>
        </div>
      )}
    </Sider>
  );
};

export default Sidebar;
