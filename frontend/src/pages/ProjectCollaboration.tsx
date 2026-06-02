import React, { useState, useEffect } from "react";
import {
  Typography,
  Button,
  Select,
  Input,
  Tag,
  Space,
  message,
  Steps,
  Table,
  Collapse,
  Modal,
  Form,
  Progress,
  Tabs,
  Card,
  Tooltip,
  Spin,
} from "antd";
import {
  ProjectOutlined,
  TeamOutlined,
  RocketOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  PlusOutlined,
  DeleteOutlined,
  ThunderboltOutlined,
  TrophyOutlined,
  CalendarOutlined,
  CodeOutlined,
  FlagOutlined,
  AlertOutlined,
  ShareAltOutlined,
  FileTextOutlined,
  SendOutlined,
  DashboardOutlined,
  BarChartOutlined,
  WarningOutlined,
  SyncOutlined,
} from "@ant-design/icons";
import { useAppStore } from "../store";
import { api, collaborationApi, evaluationApi } from "../services/api";

const { Panel } = Collapse;
const { TextArea } = Input;

interface Project {
  id: string;
  name: string;
  difficulty: number;
  description: string;
}

interface TaskItem {
  id: string;
  name: string;
  description: string;
  difficulty: number;
  estimated_hours: number;
  knowledge_points: string[];
  dependencies: string[];
  deliverables: string[];
  assigned_to?: string;
  status?: "pending" | "in_progress" | "completed";
}

interface TeamMember {
  student_id: string;
  name: string;
  skills: string[];
  preferences: string[];
  current_task?: string;
}

interface Decomposition {
  project_name: string;
  total_estimated_hours: number;
  modules: Array<{
    id: string;
    name: string;
    description: string;
    tasks: TaskItem[];
  }>;
  suggested_team_assignments: Array<{
    role: string;
    responsibilities: string[];
    tasks: string[];
  }>;
  milestones: Array<{
    name: string;
    tasks: string[];
    deadline_day: number;
  }>;
}

const DIFFICULTY_COLOR: Record<number, string> = {
  1: "green",
  2: "blue",
  3: "orange",
  4: "red",
  5: "purple",
};

const DIFFICULTY_LABEL: Record<number, string> = {
  1: "入门",
  2: "基础",
  3: "中等",
  4: "进阶",
  5: "挑战",
};

const ProjectCollaboration: React.FC = () => {
  const studentId = useAppStore((s) => s.studentId);
  const [loading, setLoading] = useState(false);
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProject, setSelectedProject] = useState<string>("");
  const [customProjectName, setCustomProjectName] = useState("");
  const [teamSize, setTeamSize] = useState(3);
  const [teamLevel, setTeamLevel] = useState("beginner");
  const [currentStep, setCurrentStep] = useState(0);

  const [teamMembers, setTeamMembers] = useState<TeamMember[]>([]);
  const [addMemberModalVisible, setAddMemberModalVisible] = useState(false);
  const [newMember, setNewMember] = useState<TeamMember>({
    student_id: "",
    name: "",
    skills: [],
    preferences: [],
  });

  const [decomposition, setDecomposition] = useState<Decomposition | null>(
    null,
  );
  const [assignments, setAssignments] = useState<any>(null);

  // 协作督导状态
  const [dailyReport, setDailyReport] = useState<any>(null);
  const [blockers, setBlockers] = useState<any[]>([]);
  const [knowledgePlan, setKnowledgePlan] = useState<any>(null);
  const [conflictModalVisible, setConflictModalVisible] = useState(false);
  const [conflictDesc, setConflictDesc] = useState("");
  const [conflictResolution, setConflictResolution] = useState<any>(null);
  const [supervisorLoading, setSupervisorLoading] = useState(false);

  // 代码提交状态
  const [codeSubmissions, setCodeSubmissions] = useState<
    Array<{ file_name: string; code: string; student_id: string }>
  >([]);
  const [codeModalVisible, setCodeModalVisible] = useState(false);
  const [newCode, setNewCode] = useState({
    file_name: "main.c",
    code: "",
    student_id: "",
  });

  // 评估报告状态
  const [evaluationReport, setEvaluationReport] = useState<any>(null);
  const [evaluationLoading, setEvaluationLoading] = useState(false);

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      const { data } = await api.get("/project-decomposer/projects");
      if (data.status === "success") {
        setProjects(data.projects);
      }
    } catch (error: any) {
      message.error("加载项目列表失败");
    }
  };

  const handleDecompose = async () => {
    if (!selectedProject && !customProjectName) {
      message.warning("请选择或输入项目名称");
      return;
    }

    setLoading(true);
    try {
      const { data } = await api.post("/project-decomposer/decompose", {
        project_id: selectedProject || undefined,
        project_name: customProjectName || undefined,
        team_size: teamSize,
        team_level: teamLevel,
      });

      if (data.status === "success") {
        const decomp = data.decomposition;
        if (decomp && !decomp.modules) decomp.modules = [];
        if (decomp && !decomp.milestones) decomp.milestones = [];
        setDecomposition(decomp);
        setCurrentStep(1);
        message.success("项目拆解完成");
      } else {
        message.error(data.detail || "拆解失败");
      }
    } catch (error: any) {
      message.error(error?.message || "请求失败");
    } finally {
      setLoading(false);
    }
  };

  const handleMatchTeam = async () => {
    if (teamMembers.length === 0) {
      message.warning("请先添加团队成员");
      return;
    }

    setLoading(true);
    try {
      const { data } = await api.post("/role-matcher/match", {
        students: teamMembers,
        project_tasks: decomposition,
      });

      if (data.status === "success") {
        setAssignments(data.assignments);
        setCurrentStep(2);
        message.success("团队匹配完成");
      } else {
        message.error(data.detail || "匹配失败");
      }
    } catch (error: any) {
      message.error(error?.message || "请求失败");
    } finally {
      setLoading(false);
    }
  };

  const handleAddMember = () => {
    if (!newMember.name || !newMember.student_id) {
      message.warning("请填写成员信息");
      return;
    }
    setTeamMembers([...teamMembers, { ...newMember }]);
    setNewMember({ student_id: "", name: "", skills: [], preferences: [] });
    setAddMemberModalVisible(false);
  };

  const handleRemoveMember = (index: number) => {
    const updated = [...teamMembers];
    updated.splice(index, 1);
    setTeamMembers(updated);
  };

  const getTotalTasks = () => {
    if (!decomposition?.modules) return 0;
    return decomposition.modules.reduce(
      (acc, m) => acc + (m.tasks?.length || 0),
      0,
    );
  };

  // 协作督导功能
  const handleDailyReport = async () => {
    setSupervisorLoading(true);
    try {
      const { data } = await collaborationApi.dailyReport({
        project_id: decomposition?.project_name || "unknown",
        team_members: teamMembers.map((m) => ({
          student_id: m.student_id,
          name: m.name,
          skills: m.skills,
        })),
      });
      if (data.status === "success") {
        setDailyReport(data.report);
        message.success("每日报告已生成");
      }
    } catch (error: any) {
      message.error(error?.message || "生成报告失败");
    } finally {
      setSupervisorLoading(false);
    }
  };

  const handleDetectBlockers = async () => {
    setSupervisorLoading(true);
    try {
      const { data } = await collaborationApi.detectBlockers({
        team_members: teamMembers.map((m) => ({
          student_id: m.student_id,
          name: m.name,
          skills: m.skills,
        })),
      });
      if (data.status === "success") {
        setBlockers(data.blockers || []);
        message.success("阻塞检测完成");
      }
    } catch (error: any) {
      message.error(error?.message || "检测失败");
    } finally {
      setSupervisorLoading(false);
    }
  };

  const handleKnowledgeSharing = async () => {
    setSupervisorLoading(true);
    try {
      const { data } = await collaborationApi.knowledgeSharing({
        team_members: teamMembers.map((m) => ({
          student_id: m.student_id,
          name: m.name,
          skills: m.skills,
        })),
        project_modules:
          decomposition?.modules?.map((m) => ({
            name: m.name,
            description: m.description,
          })) || [],
      });
      if (data.status === "success") {
        setKnowledgePlan(data.plan);
        message.success("知识共享计划已生成");
      }
    } catch (error: any) {
      message.error(error?.message || "生成计划失败");
    } finally {
      setSupervisorLoading(false);
    }
  };

  const handleResolveConflict = async () => {
    if (!conflictDesc.trim()) {
      message.warning("请描述冲突内容");
      return;
    }
    setSupervisorLoading(true);
    try {
      const { data } = await collaborationApi.resolveConflict({
        conflict_description: conflictDesc,
        involved_members: teamMembers.map((m) => ({
          student_id: m.student_id,
          name: m.name,
        })),
        project_context: decomposition?.project_name || "",
      });
      if (data.status === "success") {
        setConflictResolution(data.resolution);
        message.success("冲突解决方案已生成");
      }
    } catch (error: any) {
      message.error(error?.message || "解决冲突失败");
    } finally {
      setSupervisorLoading(false);
    }
  };

  // 代码提交
  const handleSubmitCode = () => {
    if (!newCode.code.trim()) {
      message.warning("请输入代码内容");
      return;
    }
    setCodeSubmissions([...codeSubmissions, { ...newCode }]);
    setNewCode({ file_name: "main.c", code: "", student_id: "" });
    setCodeModalVisible(false);
    message.success("代码已提交");
  };

  // 生成评估报告
  const handleGenerateReport = async () => {
    setEvaluationLoading(true);
    try {
      const { data } = await evaluationApi.fullReport({
        project_info: {
          name: decomposition?.project_name || "",
          description: selectedProject
            ? projects.find((p) => p.id === selectedProject)?.description
            : "",
        },
        team_members: teamMembers.map((m) => ({
          student_id: m.student_id,
          name: m.name,
          skills: m.skills,
        })),
        code_submissions: codeSubmissions,
        knowledge_points:
          decomposition?.modules?.flatMap(
            (m) => m.tasks?.flatMap((t) => t.knowledge_points) || [],
          ) || [],
        team_level: teamLevel,
      });
      if (data.status === "success") {
        setEvaluationReport(data.report);
        message.success("评估报告已生成");
      }
    } catch (error: any) {
      message.error(error?.message || "生成报告失败");
    } finally {
      setEvaluationLoading(false);
    }
  };

  // 渲染协作督导面板
  const renderCollaborationDashboard = () => (
    <div className="space-y-4">
      <div className="bg-white rounded-lg border border-gray-200 p-5">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <DashboardOutlined className="text-gray-400" />
            <span className="font-medium text-gray-700">协作督导中心</span>
          </div>
          <Button onClick={() => setCurrentStep(2)}>返回团队匹配</Button>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
          <Button
            type="primary"
            icon={<FileTextOutlined />}
            onClick={handleDailyReport}
            loading={supervisorLoading}
            block
          >
            每日报告
          </Button>
          <Button
            icon={<WarningOutlined />}
            onClick={handleDetectBlockers}
            loading={supervisorLoading}
            block
          >
            阻塞检测
          </Button>
          <Button
            icon={<ShareAltOutlined />}
            onClick={handleKnowledgeSharing}
            loading={supervisorLoading}
            block
          >
            知识共享
          </Button>
          <Button
            icon={<AlertOutlined />}
            onClick={() => setConflictModalVisible(true)}
            block
          >
            冲突解决
          </Button>
        </div>
      </div>

      {/* 每日报告 */}
      {dailyReport && (
        <div className="bg-white rounded-lg border border-gray-200 p-5">
          <div className="flex items-center gap-2 mb-4">
            <FileTextOutlined className="text-gray-400" />
            <span className="font-medium text-gray-700">每日协作报告</span>
          </div>
          <div className="text-sm text-gray-600 mb-4">
            {dailyReport.summary}
          </div>

          {dailyReport.team_health && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
              <div className="p-3 rounded-lg bg-blue-50 border border-blue-200 text-center">
                <div className="text-lg font-semibold text-blue-600">
                  {dailyReport.team_health.collaboration_score}
                </div>
                <div className="text-xs text-gray-500">协作分数</div>
              </div>
              <div className="p-3 rounded-lg bg-green-50 border border-green-200 text-center">
                <div className="text-lg font-semibold text-green-600">
                  {dailyReport.team_health.communication_score}
                </div>
                <div className="text-xs text-gray-500">沟通分数</div>
              </div>
              <div className="p-3 rounded-lg bg-orange-50 border border-orange-200 text-center">
                <div className="text-lg font-semibold text-orange-600">
                  {dailyReport.team_health.progress_score}
                </div>
                <div className="text-xs text-gray-500">进度分数</div>
              </div>
              <div className="p-3 rounded-lg bg-purple-50 border border-purple-200 text-center">
                <div className="text-lg font-semibold text-purple-600">
                  {dailyReport.team_health.overall_score}
                </div>
                <div className="text-xs text-gray-500">综合分数</div>
              </div>
            </div>
          )}

          {dailyReport.member_status && (
            <Table
              dataSource={dailyReport.member_status}
              rowKey="student_id"
              size="small"
              pagination={false}
              columns={[
                { title: "姓名", dataIndex: "name", key: "name" },
                {
                  title: "已完成",
                  dataIndex: "tasks_completed",
                  key: "completed",
                  width: 80,
                },
                {
                  title: "进行中",
                  dataIndex: "tasks_in_progress",
                  key: "in_progress",
                  width: 80,
                },
                {
                  title: "贡献分",
                  dataIndex: "contribution_score",
                  key: "score",
                  width: 100,
                  render: (s: number) => <Progress percent={s} size="small" />,
                },
              ]}
            />
          )}

          {dailyReport.recommendations && (
            <div className="mt-4 p-3 rounded bg-yellow-50 border border-yellow-200">
              <div className="text-sm font-medium text-gray-700 mb-2">建议</div>
              <ul className="m-0 pl-4 space-y-1">
                {dailyReport.recommendations.map((r: string, i: number) => (
                  <li key={i} className="text-sm text-gray-600 list-disc">
                    {r}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* 阻塞检测结果 */}
      {blockers.length > 0 && (
        <div className="bg-white rounded-lg border border-gray-200 p-5">
          <div className="flex items-center gap-2 mb-4">
            <WarningOutlined className="text-orange-400" />
            <span className="font-medium text-gray-700">阻塞检测结果</span>
          </div>
          <div className="space-y-3">
            {blockers.map((b: any, idx: number) => (
              <div
                key={idx}
                className="p-3 rounded-lg bg-orange-50 border border-orange-200"
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium text-gray-700">{b.name}</span>
                  <Tag color={b.severity === "high" ? "red" : "orange"}>
                    {b.severity === "high" ? "严重" : "中等"}
                  </Tag>
                </div>
                <div className="text-sm text-gray-600">
                  当前任务：{b.current_task}
                </div>
                <div className="text-sm text-gray-600">
                  卡住时间：{b.minutes_stuck} 分钟
                </div>
                <div className="text-sm text-blue-600 mt-1">{b.suggestion}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 知识共享计划 */}
      {knowledgePlan && (
        <div className="bg-white rounded-lg border border-gray-200 p-5">
          <div className="flex items-center gap-2 mb-4">
            <ShareAltOutlined className="text-green-400" />
            <span className="font-medium text-gray-700">知识共享计划</span>
          </div>

          {knowledgePlan.skill_gaps && knowledgePlan.skill_gaps.length > 0 && (
            <div className="mb-4">
              <div className="text-sm font-medium text-gray-700 mb-2">
                技能缺口
              </div>
              <div className="space-y-2">
                {knowledgePlan.skill_gaps.map((gap: any, i: number) => (
                  <div
                    key={i}
                    className="p-2 rounded bg-gray-50 border border-gray-200 text-sm"
                  >
                    <span className="font-medium">{gap.member}</span> 缺少：
                    {gap.missing_skills?.map((s: string, j: number) => (
                      <Tag key={j}>{s}</Tag>
                    ))}
                    {gap.recommended_mentor && (
                      <span className="text-gray-500 ml-2">
                        推荐导师：{gap.recommended_mentor}
                      </span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {knowledgePlan.sharing_sessions &&
            knowledgePlan.sharing_sessions.length > 0 && (
              <div>
                <div className="text-sm font-medium text-gray-700 mb-2">
                  分享会安排
                </div>
                <Table
                  dataSource={knowledgePlan.sharing_sessions}
                  rowKey="topic"
                  size="small"
                  pagination={false}
                  columns={[
                    { title: "主题", dataIndex: "topic", key: "topic" },
                    {
                      title: "主讲人",
                      dataIndex: "presenter",
                      key: "presenter",
                      width: 100,
                    },
                    {
                      title: "时长",
                      dataIndex: "duration_minutes",
                      key: "duration",
                      width: 80,
                      render: (m: number) => `${m}分钟`,
                    },
                  ]}
                />
              </div>
            )}
        </div>
      )}

      {/* 代码提交区 */}
      <div className="bg-white rounded-lg border border-gray-200 p-5">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <CodeOutlined className="text-gray-400" />
            <span className="font-medium text-gray-700">代码提交</span>
            <Tag>{codeSubmissions.length} 个提交</Tag>
          </div>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => setCodeModalVisible(true)}
          >
            提交代码
          </Button>
        </div>

        {codeSubmissions.length > 0 ? (
          <div className="space-y-3">
            {codeSubmissions.map((sub, idx) => (
              <div
                key={idx}
                className="p-3 rounded-lg bg-gray-50 border border-gray-200"
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium text-gray-700 text-sm">
                    {sub.file_name}
                  </span>
                  <Tag>{sub.student_id}</Tag>
                </div>
                <pre className="bg-gray-900 text-green-400 p-3 rounded text-xs overflow-x-auto max-h-40">
                  {sub.code}
                </pre>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-400">
            <CodeOutlined className="text-2xl mb-2" />
            <div className="text-sm">暂无代码提交</div>
          </div>
        )}
      </div>

      {/* 评估报告 */}
      <div className="bg-white rounded-lg border border-gray-200 p-5">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <BarChartOutlined className="text-gray-400" />
            <span className="font-medium text-gray-700">成果评估</span>
          </div>
          <Button
            type="primary"
            icon={<ThunderboltOutlined />}
            onClick={handleGenerateReport}
            loading={evaluationLoading}
          >
            生成评估报告
          </Button>
        </div>

        {evaluationReport ? (
          <div className="space-y-4">
            <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
              <div className="p-3 rounded-lg bg-blue-50 border border-blue-200 text-center">
                <div className="text-xl font-semibold text-blue-600">
                  {evaluationReport.overall_score}
                </div>
                <div className="text-xs text-gray-500">综合分数</div>
              </div>
              <div className="p-3 rounded-lg bg-green-50 border border-green-200 text-center">
                <div className="text-xl font-semibold text-green-600">
                  {evaluationReport.grade}
                </div>
                <div className="text-xs text-gray-500">等级</div>
              </div>
              {evaluationReport.dimension_scores &&
                Object.entries(evaluationReport.dimension_scores).map(
                  ([key, val]: [string, any]) => (
                    <div
                      key={key}
                      className="p-3 rounded-lg bg-gray-50 border border-gray-200 text-center"
                    >
                      <div className="text-lg font-semibold text-gray-700">
                        {val}
                      </div>
                      <div className="text-xs text-gray-500">
                        {key === "code_quality"
                          ? "代码质量"
                          : key === "collaboration"
                            ? "协作"
                            : key === "deliverable"
                              ? "交付物"
                              : "学习"}
                      </div>
                    </div>
                  ),
                )}
            </div>

            <div className="text-sm text-gray-600">
              {evaluationReport.summary}
            </div>

            {evaluationReport.team_performance && (
              <Table
                dataSource={evaluationReport.team_performance}
                rowKey="student_id"
                size="small"
                pagination={false}
                columns={[
                  { title: "姓名", dataIndex: "name", key: "name" },
                  {
                    title: "综合分",
                    dataIndex: "overall_score",
                    key: "overall",
                    width: 80,
                  },
                  {
                    title: "代码贡献",
                    dataIndex: "code_contribution",
                    key: "code",
                    width: 80,
                  },
                  {
                    title: "协作分",
                    dataIndex: "collaboration_score",
                    key: "collab",
                    width: 80,
                  },
                  {
                    title: "学习分",
                    dataIndex: "learning_score",
                    key: "learning",
                    width: 80,
                  },
                ]}
              />
            )}

            {evaluationReport.project_highlights && (
              <div className="p-3 rounded bg-green-50 border border-green-200">
                <div className="text-sm font-medium text-gray-700 mb-2">
                  项目亮点
                </div>
                <ul className="m-0 pl-4 space-y-1">
                  {evaluationReport.project_highlights.map(
                    (h: string, i: number) => (
                      <li key={i} className="text-sm text-gray-600 list-disc">
                        {h}
                      </li>
                    ),
                  )}
                </ul>
              </div>
            )}

            {evaluationReport.final_recommendations && (
              <div className="p-3 rounded bg-blue-50 border border-blue-200">
                <div className="text-sm font-medium text-gray-700 mb-2">
                  最终建议
                </div>
                <ul className="m-0 pl-4 space-y-1">
                  {evaluationReport.final_recommendations.map(
                    (r: string, i: number) => (
                      <li key={i} className="text-sm text-gray-600 list-disc">
                        {r}
                      </li>
                    ),
                  )}
                </ul>
              </div>
            )}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-400">
            <BarChartOutlined className="text-2xl mb-2" />
            <div className="text-sm">点击上方按钮生成综合评估报告</div>
          </div>
        )}
      </div>

      <div className="flex gap-3">
        <Button
          size="large"
          onClick={() => setCurrentStep(2)}
          className="flex-1"
        >
          返回团队匹配
        </Button>
        <Button
          size="large"
          onClick={() => setCurrentStep(0)}
          className="flex-1"
        >
          重新选择项目
        </Button>
      </div>
    </div>
  );

  return (
    <div className="space-y-6 pb-8">
      {/* 顶部标题区 */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-10 h-10 rounded-lg bg-blue-50 flex items-center justify-center text-blue-500">
              <ProjectOutlined className="text-lg" />
            </div>
            <div>
              <Typography.Title level={4} className="!m-0 !text-gray-900">
                项目式协作学习
              </Typography.Title>
              <Typography.Text className="text-gray-500 text-sm">
                AI驱动的项目拆解 · 智能组队 · 协作督导 · 成果评估
              </Typography.Text>
            </div>
          </div>
          <div className="hidden md:flex items-center gap-4">
            <div className="text-center">
              <div className="text-lg font-semibold text-gray-900">
                {projects.length}
              </div>
              <div className="text-xs text-gray-400">内置项目</div>
            </div>
            <div className="w-px h-8 bg-gray-200" />
            <div className="text-center">
              <div className="text-lg font-semibold text-gray-900">
                {teamMembers.length}
              </div>
              <div className="text-xs text-gray-400">团队成员</div>
            </div>
            <div className="w-px h-8 bg-gray-200" />
            <div className="text-center">
              <div className="text-lg font-semibold text-gray-900">
                {getTotalTasks()}
              </div>
              <div className="text-xs text-gray-400">拆解任务</div>
            </div>
          </div>
        </div>
      </div>

      {/* 步骤导航 */}
      <div className="bg-white rounded-lg border border-gray-200 p-5">
        <Steps
          current={currentStep}
          items={[
            {
              title: <span className="text-sm">选择项目</span>,
              description: "选择或自定义C语言项目",
            },
            {
              title: <span className="text-sm">任务拆解</span>,
              description: "AI自动拆解为可执行任务",
            },
            {
              title: <span className="text-sm">团队匹配</span>,
              description: "智能匹配团队成员",
            },
            {
              title: <span className="text-sm">协作督导</span>,
              description: "进度监控·代码提交·评估",
            },
          ]}
        />
      </div>

      {/* Step 1: 选择项目 */}
      {currentStep === 0 && (
        <div className="max-w-3xl mx-auto space-y-4">
          <div className="bg-white rounded-lg border border-gray-200 p-5">
            <div className="flex items-center gap-2 mb-4">
              <RocketOutlined className="text-gray-400" />
              <span className="font-medium text-gray-700">选择内置项目</span>
              <Tag className="ml-auto">{projects.length} 个可用</Tag>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {projects.map((p) => {
                const isSelected = selectedProject === p.id;
                return (
                  <div
                    key={p.id}
                    onClick={() => setSelectedProject(p.id)}
                    className={`p-4 rounded-lg border cursor-pointer transition-colors ${
                      isSelected
                        ? "border-blue-500 bg-blue-50"
                        : "border-gray-200 hover:border-gray-300 hover:bg-gray-50"
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      <div className="w-9 h-9 rounded bg-gray-100 flex items-center justify-center text-gray-500 font-medium text-sm">
                        {p.name.charAt(0)}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="font-medium text-gray-700 text-sm mb-1">
                          {p.name}
                        </div>
                        <div className="text-xs text-gray-400 mb-2 line-clamp-2">
                          {p.description}
                        </div>
                        <Tag
                          color={DIFFICULTY_COLOR[p.difficulty]}
                          className="text-xs"
                        >
                          {DIFFICULTY_LABEL[p.difficulty]}
                        </Tag>
                      </div>
                      {isSelected && (
                        <CheckCircleOutlined className="text-blue-500" />
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="bg-white rounded-lg border border-gray-200 p-5">
            <div className="flex items-center gap-2 mb-4">
              <ProjectOutlined className="text-gray-400" />
              <span className="font-medium text-gray-700">或自定义项目</span>
            </div>
            <Input
              value={customProjectName}
              onChange={(e) => setCustomProjectName(e.target.value)}
              placeholder="输入自定义项目名称，如：学生成绩管理系统"
              size="large"
              className="rounded-lg"
            />
          </div>

          <div className="bg-white rounded-lg border border-gray-200 p-5">
            <div className="flex items-center gap-2 mb-4">
              <TeamOutlined className="text-gray-400" />
              <span className="font-medium text-gray-700">团队配置</span>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <div className="text-sm text-gray-500 mb-2">团队人数</div>
                <Select
                  value={teamSize}
                  onChange={setTeamSize}
                  style={{ width: "100%" }}
                  size="large"
                  options={[2, 3, 4, 5].map((n) => ({
                    value: n,
                    label: `${n} 人团队`,
                  }))}
                />
              </div>
              <div>
                <div className="text-sm text-gray-500 mb-2">团队水平</div>
                <Select
                  value={teamLevel}
                  onChange={setTeamLevel}
                  style={{ width: "100%" }}
                  size="large"
                  options={[
                    { value: "beginner", label: "初学者" },
                    { value: "intermediate", label: "中级" },
                    { value: "advanced", label: "高级" },
                  ]}
                />
              </div>
            </div>
          </div>

          <Button
            type="primary"
            size="large"
            block
            onClick={handleDecompose}
            loading={loading}
            className="h-10"
          >
            开始拆解项目
          </Button>
        </div>
      )}

      {/* Step 2: 任务拆解结果 */}
      {currentStep === 1 && decomposition && (
        <div className="space-y-4">
          <div className="bg-white rounded-lg border border-gray-200 p-5">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-blue-50 flex items-center justify-center text-blue-500">
                  <ProjectOutlined />
                </div>
                <div>
                  <div className="font-semibold text-gray-900">
                    {decomposition.project_name}
                  </div>
                  <div className="text-xs text-gray-400">项目拆解结果</div>
                </div>
              </div>
              <Button onClick={() => setCurrentStep(0)}>返回修改</Button>
            </div>

            <div className="grid grid-cols-4 gap-3">
              <div className="p-3 rounded-lg bg-gray-50 border border-gray-200 text-center">
                <div className="text-xl font-semibold text-gray-900">
                  {decomposition.modules.length}
                </div>
                <div className="text-xs text-gray-400">模块数</div>
              </div>
              <div className="p-3 rounded-lg bg-gray-50 border border-gray-200 text-center">
                <div className="text-xl font-semibold text-gray-900">
                  {getTotalTasks()}
                </div>
                <div className="text-xs text-gray-400">任务数</div>
              </div>
              <div className="p-3 rounded-lg bg-gray-50 border border-gray-200 text-center">
                <div className="text-xl font-semibold text-gray-900">
                  {decomposition.total_estimated_hours}h
                </div>
                <div className="text-xs text-gray-400">预计工时</div>
              </div>
              <div className="p-3 rounded-lg bg-gray-50 border border-gray-200 text-center">
                <div className="text-xl font-semibold text-gray-900">
                  {decomposition.milestones.length}
                </div>
                <div className="text-xs text-gray-400">里程碑</div>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg border border-gray-200 p-5">
            <div className="flex items-center gap-2 mb-4">
              <CodeOutlined className="text-gray-400" />
              <span className="font-medium text-gray-700">模块详情</span>
            </div>
            <Collapse
              defaultActiveKey={decomposition.modules.map((m) => m.id)}
              className="bg-transparent border-0"
            >
              {decomposition.modules.map((module) => (
                <Panel
                  header={
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-gray-700">
                        {module.name}
                      </span>
                      <Tag className="ml-auto">
                        {module.tasks.length} 个任务
                      </Tag>
                    </div>
                  }
                  key={module.id}
                  className="bg-white rounded-lg border border-gray-200 mb-2"
                >
                  <div className="text-sm text-gray-500 mb-4">
                    {module.description}
                  </div>
                  <Table
                    dataSource={module.tasks}
                    rowKey="id"
                    size="small"
                    pagination={false}
                    columns={[
                      {
                        title: "任务名称",
                        dataIndex: "name",
                        key: "name",
                        render: (name: string) => (
                          <span className="font-medium text-gray-700">
                            {name}
                          </span>
                        ),
                      },
                      {
                        title: "难度",
                        dataIndex: "difficulty",
                        key: "difficulty",
                        width: 80,
                        render: (d: number) => (
                          <Tag color={DIFFICULTY_COLOR[d]}>
                            {DIFFICULTY_LABEL[d]}
                          </Tag>
                        ),
                      },
                      {
                        title: "预计工时",
                        dataIndex: "estimated_hours",
                        key: "estimated_hours",
                        width: 100,
                        render: (h: number) => (
                          <span className="text-gray-500">{h}h</span>
                        ),
                      },
                      {
                        title: "知识点",
                        dataIndex: "knowledge_points",
                        key: "knowledge_points",
                        render: (points: string[]) => (
                          <Space size={[0, 4]} wrap>
                            {points.map((p, i) => (
                              <Tag key={i}>{p}</Tag>
                            ))}
                          </Space>
                        ),
                      },
                    ]}
                  />
                </Panel>
              ))}
            </Collapse>
          </div>

          {decomposition.milestones.length > 0 && (
            <div className="bg-white rounded-lg border border-gray-200 p-5">
              <div className="flex items-center gap-2 mb-4">
                <FlagOutlined className="text-gray-400" />
                <span className="font-medium text-gray-700">项目里程碑</span>
              </div>
              <div className="space-y-2">
                {decomposition.milestones.map((m, idx) => (
                  <div
                    key={idx}
                    className="flex items-center gap-4 p-3 rounded bg-gray-50 border border-gray-200"
                  >
                    <div className="w-7 h-7 rounded-full bg-gray-200 flex items-center justify-center text-gray-600 font-medium text-xs">
                      {idx + 1}
                    </div>
                    <div className="flex-1">
                      <div className="font-medium text-gray-700 text-sm">
                        {m.name}
                      </div>
                      <div className="text-xs text-gray-400">
                        包含 {m.tasks.length} 个任务
                      </div>
                    </div>
                    <div className="flex items-center gap-1 text-xs text-gray-500">
                      <CalendarOutlined />
                      <span>第{m.deadline_day}天</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          <Button
            type="primary"
            size="large"
            block
            onClick={() => setCurrentStep(2)}
            className="h-10"
          >
            下一步：组建团队
          </Button>
        </div>
      )}

      {/* Step 3: 团队匹配 */}
      {currentStep === 2 && (
        <div className="space-y-4">
          <div className="bg-white rounded-lg border border-gray-200 p-5">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <TeamOutlined className="text-gray-400" />
                <span className="font-medium text-gray-700">团队成员管理</span>
                <Tag>{teamMembers.length} 人</Tag>
              </div>
              <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={() => setAddMemberModalVisible(true)}
              >
                添加成员
              </Button>
            </div>

            {teamMembers.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {teamMembers.map((member, idx) => (
                  <div
                    key={idx}
                    className="flex items-start gap-3 p-4 rounded-lg bg-gray-50 border border-gray-200"
                  >
                    <div className="w-9 h-9 rounded-full bg-gray-200 flex items-center justify-center text-gray-600 font-medium text-sm">
                      {member.name.charAt(0)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="font-medium text-gray-700 text-sm">
                        {member.name}
                      </div>
                      <div className="text-xs text-gray-400 mb-2">
                        学号: {member.student_id}
                      </div>
                      <Space size={[0, 4]} wrap>
                        {member.skills.map((s, i) => (
                          <Tag key={i} className="text-xs">
                            {s}
                          </Tag>
                        ))}
                      </Space>
                    </div>
                    <Button
                      type="text"
                      danger
                      icon={<DeleteOutlined />}
                      onClick={() => handleRemoveMember(idx)}
                      size="small"
                    />
                  </div>
                ))}
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center py-12 text-gray-400">
                <TeamOutlined className="text-3xl mb-3 text-gray-300" />
                <div className="text-sm text-gray-500 mb-1">暂无团队成员</div>
                <div className="text-xs text-gray-400">
                  点击"添加成员"按钮开始组建团队
                </div>
              </div>
            )}
          </div>

          <Button
            type="primary"
            size="large"
            block
            onClick={handleMatchTeam}
            loading={loading}
            disabled={teamMembers.length < 2}
            className="h-10"
          >
            智能匹配团队
          </Button>

          {assignments && (
            <div className="bg-white rounded-lg border border-gray-200 p-5">
              <div className="flex items-center gap-2 mb-4">
                <TrophyOutlined className="text-gray-400" />
                <span className="font-medium text-gray-700">团队分工方案</span>
              </div>

              <div className="space-y-3">
                {assignments.team_assignments?.map(
                  (assignment: any, idx: number) => (
                    <div
                      key={idx}
                      className="p-4 rounded-lg bg-gray-50 border border-gray-200"
                    >
                      <div className="flex items-center gap-3 mb-2">
                        <div className="w-7 h-7 rounded-full bg-gray-200 flex items-center justify-center text-gray-600 font-medium text-xs">
                          {idx + 1}
                        </div>
                        <div className="flex-1">
                          <span className="font-medium text-gray-700 text-sm">
                            {assignment.student_name}
                          </span>
                        </div>
                        <Tag>{assignment.primary_role}</Tag>
                      </div>
                      <div className="text-sm text-gray-600 mb-2 ml-10">
                        {assignment.reason}
                      </div>
                      <div className="ml-10">
                        <span className="text-xs text-gray-400">
                          成长方向：
                        </span>
                        <Space size={[0, 4]} wrap>
                          {assignment.growth_areas?.map(
                            (area: string, i: number) => (
                              <Tag key={i} className="text-xs">
                                {area}
                              </Tag>
                            ),
                          )}
                        </Space>
                      </div>
                    </div>
                  ),
                )}
              </div>

              {assignments.team_dynamics && (
                <div className="mt-4 p-4 rounded-lg bg-green-50 border border-green-200">
                  <div className="flex items-center gap-2 mb-3">
                    <CheckCircleOutlined className="text-green-600" />
                    <span className="font-medium text-gray-700 text-sm">
                      团队优势
                    </span>
                  </div>
                  <ul className="m-0 pl-4 space-y-1">
                    {assignments.team_dynamics.strengths?.map(
                      (s: string, i: number) => (
                        <li key={i} className="text-sm text-gray-600 list-disc">
                          {s}
                        </li>
                      ),
                    )}
                  </ul>
                </div>
              )}
            </div>
          )}

          <div className="flex gap-3">
            <Button
              size="large"
              onClick={() => setCurrentStep(1)}
              className="flex-1"
            >
              返回任务拆解
            </Button>
            <Button
              type="primary"
              size="large"
              onClick={() => setCurrentStep(3)}
              className="flex-1"
            >
              进入协作督导
            </Button>
          </div>
        </div>
      )}

      {/* Step 4: 协作督导 */}
      {currentStep === 3 && renderCollaborationDashboard()}

      {/* 添加成员弹窗 */}
      <Modal
        title="添加团队成员"
        open={addMemberModalVisible}
        onOk={handleAddMember}
        onCancel={() => setAddMemberModalVisible(false)}
        okText="添加"
        cancelText="取消"
      >
        <Form layout="vertical" className="mt-4">
          <Form.Item label="学号" required>
            <Input
              value={newMember.student_id}
              onChange={(e) =>
                setNewMember({ ...newMember, student_id: e.target.value })
              }
              placeholder="输入学号"
            />
          </Form.Item>
          <Form.Item label="姓名" required>
            <Input
              value={newMember.name}
              onChange={(e) =>
                setNewMember({ ...newMember, name: e.target.value })
              }
              placeholder="输入姓名"
            />
          </Form.Item>
          <Form.Item label="技能">
            <Select
              mode="tags"
              value={newMember.skills}
              onChange={(skills) => setNewMember({ ...newMember, skills })}
              placeholder="输入技能，按回车添加"
            />
          </Form.Item>
          <Form.Item label="偏好">
            <Select
              mode="tags"
              value={newMember.preferences}
              onChange={(prefs) =>
                setNewMember({ ...newMember, preferences: prefs })
              }
              placeholder="输入偏好，按回车添加"
            />
          </Form.Item>
        </Form>
      </Modal>

      {/* 冲突解决弹窗 */}
      <Modal
        title="冲突解决"
        open={conflictModalVisible}
        onOk={handleResolveConflict}
        onCancel={() => {
          setConflictModalVisible(false);
          setConflictResolution(null);
          setConflictDesc("");
        }}
        okText="生成解决方案"
        cancelText="关闭"
        width={600}
      >
        <div className="space-y-4 mt-4">
          <div>
            <div className="text-sm text-gray-500 mb-2">描述冲突内容</div>
            <TextArea
              value={conflictDesc}
              onChange={(e) => setConflictDesc(e.target.value)}
              placeholder="请描述团队中出现的冲突或分歧..."
              rows={3}
            />
          </div>

          {conflictResolution && (
            <div className="space-y-3">
              <div className="p-3 rounded bg-gray-50 border border-gray-200">
                <div className="text-sm font-medium text-gray-700 mb-1">
                  冲突类型
                </div>
                <Tag>{conflictResolution.conflict_type}</Tag>
              </div>
              <div className="p-3 rounded bg-gray-50 border border-gray-200">
                <div className="text-sm font-medium text-gray-700 mb-1">
                  根本原因
                </div>
                <div className="text-sm text-gray-600">
                  {conflictResolution.root_cause}
                </div>
              </div>
              {conflictResolution.solutions && (
                <div>
                  <div className="text-sm font-medium text-gray-700 mb-2">
                    解决方案
                  </div>
                  {conflictResolution.solutions.map((sol: any, i: number) => (
                    <div
                      key={i}
                      className={`p-3 rounded border mb-2 ${sol.recommended ? "bg-green-50 border-green-200" : "bg-gray-50 border-gray-200"}`}
                    >
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-sm font-medium text-gray-700">
                          {sol.option}
                        </span>
                        {sol.recommended && <Tag color="green">推荐</Tag>}
                      </div>
                      <div className="text-xs text-gray-500">
                        优点：{sol.pros?.join("、")}
                      </div>
                      <div className="text-xs text-gray-500">
                        缺点：{sol.cons?.join("、")}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </Modal>

      {/* 代码提交弹窗 */}
      <Modal
        title="提交代码"
        open={codeModalVisible}
        onOk={handleSubmitCode}
        onCancel={() => setCodeModalVisible(false)}
        okText="提交"
        cancelText="取消"
        width={700}
      >
        <Form layout="vertical" className="mt-4">
          <Form.Item label="文件名">
            <Input
              value={newCode.file_name}
              onChange={(e) =>
                setNewCode({ ...newCode, file_name: e.target.value })
              }
              placeholder="如 main.c"
            />
          </Form.Item>
          <Form.Item label="提交者学号">
            <Input
              value={newCode.student_id}
              onChange={(e) =>
                setNewCode({ ...newCode, student_id: e.target.value })
              }
              placeholder="输入学号"
            />
          </Form.Item>
          <Form.Item label="代码内容" required>
            <TextArea
              value={newCode.code}
              onChange={(e) => setNewCode({ ...newCode, code: e.target.value })}
              placeholder="粘贴你的代码..."
              rows={10}
              style={{ fontFamily: "monospace" }}
            />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default ProjectCollaboration;
