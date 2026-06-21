import React, {
  useEffect,
  useLayoutEffect,
  useState,
  useMemo,
  useRef,
  useCallback,
} from "react";
import {
  Typography,
  Card,
  Button,
  Tag,
  Space,
  Drawer,
  Slider,
  Radio,
  Progress,
  Avatar,
  List,
  message,
  Input,
  Tooltip,
  Popconfirm,
  Select,
  Steps,
  Modal,
  Tree,
} from "antd";
import {
  CheckCircleOutlined,
  ClockCircleOutlined,
  SwapOutlined,
  BookOutlined,
  PlayCircleOutlined,
  FileTextOutlined,
  CodeOutlined,
  FlagOutlined,
  RocketOutlined,
  ArrowRightOutlined,
  ReloadOutlined,
  ExclamationCircleOutlined,
  ApartmentOutlined,
  BulbOutlined,
  SaveOutlined,
  StepForwardOutlined,
  UndoOutlined,
  EyeOutlined,
  HistoryOutlined,
  ThunderboltOutlined,
  RobotOutlined,
  ReadOutlined,
} from "@ant-design/icons";
import { useNavigate } from "react-router-dom";
import { useAppStore } from "../store";
import {
  pathApi,
  profileApi,
  learningDataApi,
  logReflectionApi,
  apiGet,
} from "../services/api";
import { kbApi } from "../services/knowledgeBaseApi";
// import { buildRadarData } from "../utils/profile";
import { StatusIcon } from "../components/StatusIcon";
import AdjustmentLogPanel from "../components/AdjustmentLogPanel";
import {
  // StatusTag,
  statusColors,
  statusBg,
  statusLabels,
} from "../components/StatusTag";
import type {
  PathNode,
  PathStage,
  // StudentProfile,
  LearningPathData,
} from "../types";

const resourceTypeMeta: Record<
  string,
  { icon: React.ReactNode; color: string }
> = {
  video: { icon: <PlayCircleOutlined />, color: "#ef4444" },
  code: { icon: <CodeOutlined />, color: "#3b82f6" },
  doc: { icon: <FileTextOutlined />, color: "#10b981" },
  quiz: { icon: <BookOutlined />, color: "#f59e0b" },
  questions: { icon: <BookOutlined />, color: "#f59e0b" },
  document: { icon: <FileTextOutlined />, color: "#10b981" },
  mindmap: { icon: <ApartmentOutlined />, color: "#8b5cf6" },
  reading: { icon: <ReadOutlined />, color: "#06b6d4" },
  视频: { icon: <PlayCircleOutlined />, color: "#ef4444" },
  代码: { icon: <CodeOutlined />, color: "#3b82f6" },
  文档: { icon: <FileTextOutlined />, color: "#10b981" },
  练习: { icon: <BookOutlined />, color: "#f59e0b" },
  题目: { icon: <BookOutlined />, color: "#f59e0b" },
};

interface ResourceItem {
  id: number;
  title: string;
  type: string;
  subject: string;
  difficulty: string;
  content?: string;
  generated_by: string;
  view_count: number;
  favorite_count: number;
  created_at: string;
}

const AGENT_STEPS = [
  { title: "画像分析", description: "ProfileAgent 分析学习画像" },
  { title: "资源生成", description: "ResourceAgent 生成针对性资源" },
  { title: "路径整合", description: "PathAgent 整合到学习路径" },
];

/** 将思维导图 JSON 转为 antd Tree data */
function parseMindmapToTree(data: unknown): Array<Record<string, unknown>> {
  if (!data || typeof data !== "object") return [];
  const obj = data as Record<string, unknown>;
  if (obj.root && Array.isArray(obj.children)) {
    return [
      {
        title: String(obj.root),
        key: "root",
        children: obj.children.map((c, i) => parseMindmapNode(c, `root_${i}`)),
      },
    ];
  }
  return [{ title: "思维导图", key: "root", children: [] }];
}

function parseMindmapNode(node: unknown, key: string): Record<string, unknown> {
  if (!node || typeof node !== "object") return { title: String(node), key };
  const n = node as Record<string, unknown>;
  const children = Array.isArray(n.children)
    ? n.children.map((c, i) => parseMindmapNode(c, `${key}_${i}`))
    : [];
  return { title: String(n.name || n.title || "?"), key, children };
}

/** 资源内容渲染器：根据类型使用不同渲染方式 */
const ResourceContentRenderer: React.FC<{ type: string; content: string }> = ({
  type,
  content,
}) => {
  if (type === "mindmap") {
    try {
      const data = JSON.parse(content);
      const treeData = parseMindmapToTree(data);
      return (
        <div className="max-h-96 overflow-auto">
          <Tree treeData={treeData} defaultExpandAll showLine />
        </div>
      );
    } catch {
      return (
        <pre className="text-sm whitespace-pre-wrap max-h-96 overflow-auto bg-slate-50 p-3 rounded-lg">
          {content}
        </pre>
      );
    }
  }

  if (type === "questions" || type === "quiz") {
    try {
      const questions = JSON.parse(content);
      if (Array.isArray(questions)) {
        return (
          <div className="space-y-4 max-h-96 overflow-auto">
            {questions.map((q: Record<string, unknown>, i: number) => (
              <div key={i} className="p-3 bg-slate-50 rounded-lg">
                <div className="font-medium text-sm mb-2">
                  {i + 1}. {String(q.content || q.question || "")}
                </div>
                {Array.isArray(q.options) &&
                  q.options.map((opt: Record<string, string>, j: number) => (
                    <div key={j} className="text-sm text-slate-600 ml-4">
                      {opt.id || String.fromCharCode(65 + j)}.{" "}
                      {opt.text || String(opt)}
                    </div>
                  ))}
                {q.correct_answer ? (
                  <div className="text-xs text-emerald-600 mt-2">
                    正确答案: {String(q.correct_answer)}
                  </div>
                ) : null}
                {q.explanation ? (
                  <div className="text-xs text-slate-400 mt-1">
                    解析: {String(q.explanation)}
                  </div>
                ) : null}
              </div>
            ))}
          </div>
        );
      }
    } catch {
      // fall through
    }
  }

  if (type === "code") {
    return (
      <pre className="text-sm bg-slate-900 text-slate-100 p-4 rounded-lg max-h-96 overflow-auto whitespace-pre-wrap">
        <code>{content}</code>
      </pre>
    );
  }

  // document / reading / 其他：纯文本展示
  return (
    <div className="text-sm leading-relaxed whitespace-pre-wrap max-h-96 overflow-auto">
      {content}
    </div>
  );
};

const LearningPathPage: React.FC = () => {
  const viewMode = "timeline";
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [selectedNode, setSelectedNode] = useState<PathNode | null>(null);
  const [pathData, setPathData] = useState<Record<string, unknown> | null>(
    null,
  );
  const [pathNodes, setPathNodes] = useState<PathNode[]>([]);
  const [pathStages, setPathStages] = useState<PathStage[]>([]);
  const [loading, setLoading] = useState(false);
  const [showReviewAlert, setShowReviewAlert] = useState(() => {
    // 当天稍后提醒后保持隐藏；新一天自动恢复
    if (typeof window === "undefined") return true;
    const today = new Date().toISOString().slice(0, 10);
    return localStorage.getItem("review_alert_dismissed") !== today;
  });
  const [dailyDuration, setDailyDuration] = useState(90);
  const [difficulty, setDifficulty] = useState(3);
  const [learningPreference, setLearningPreference] = useState("balanced");
  const [targetTopic, setTargetTopic] =
    useState("掌握 C语言程序设计与数据结构基础");
  const [adjustFeedback, setAdjustFeedback] = useState("");
  const [profileSuggestions, setProfileSuggestions] = useState<string[]>([]);
  const [weakReviewTopics, setWeakReviewTopics] = useState<string[]>([]);
  const nodeOpenTimeRef = useRef<number>(Date.now());
  const [activeAdjustTab, setActiveAdjustTab] = useState<
    "params" | "nodes" | "feedback"
  >("params");
  const [reflectionText, setReflectionText] = useState("");
  const [submittingReflection, setSubmittingReflection] = useState(false);
  const [adjustLogOpen, setAdjustLogOpen] = useState(false);
  const [changedNodeIds, setChangedNodeIds] = useState<Set<number>>(new Set());
  const prevNodesRef = useRef<PathNode[]>([]);
  const studentId = useAppStore((s) => s.studentId);
  // ===== 资源生成相关状态 =====
  const [genSubject, setGenSubject] = useState("C语言");
  const [genTarget, setGenTarget] = useState<"weak" | "goal" | "custom">(
    "weak",
  );
  const [genType, setGenType] = useState("document");
  const [genDifficulty, setGenDifficulty] = useState("medium");
  const [generatingResource, setGeneratingResource] = useState(false);
  const [agentStep, setAgentStep] = useState(-1);
  const [genResult, setGenResult] = useState("");
  const [resources, setResources] = useState<ResourceItem[]>([]);
  const [resourcesLoading, setResourcesLoading] = useState(false);
  const [selectedWeakPoints, setSelectedWeakPoints] = useState<string[]>([]);
  const [weakPoints, setWeakPoints] = useState<
    Array<{ name: string; mastery: number }>
  >([]);
  const [resourceFilter, setResourceFilter] = useState({
    type: "",
    subject: "",
    difficulty: "",
  });
  const [resourceKeyword, setResourceKeyword] = useState("");
  const [resourcePage, setResourcePage] = useState(1);
  const [resourceDetailOpen, setResourceDetailOpen] = useState(false);
  const [selectedResource, setSelectedResource] = useState<ResourceItem | null>(
    null,
  );
  const currentSubject = useAppStore((s) => s.currentSubject);
  const navigate = useNavigate();
  const timelineRef = useRef<HTMLDivElement>(null);
  const strokePathRef = useRef<SVGPathElement>(null);
  const [timelineHeight, setTimelineHeight] = useState(0);
  const [visibleCount, setVisibleCount] = useState(0);
  const visibleCountRef = useRef(visibleCount);
  useEffect(() => {
    visibleCountRef.current = visibleCount;
  }, [visibleCount]);

  // 根据课程切换默认学习目标
  useEffect(() => {
    if (currentSubject === "电路分析") {
      setTargetTopic("掌握电路分析基础理论与分析方法");
    } else {
      setTargetTopic("掌握 C语言程序设计与数据结构基础");
    }
  }, [currentSubject]);

  // 同步资源生成学科与全局学科
  useEffect(() => {
    if (currentSubject) setGenSubject(currentSubject);
  }, [currentSubject]);

  const lineD = useMemo(() => {
    const h = Math.max(timelineHeight, 1);
    return `M 8 0 L 8 ${h}`;
  }, [timelineHeight]);

  // 加载本地保存的偏好和路径数据（按课程分别存储）
  useEffect(() => {
    const saved = localStorage.getItem(
      `path_prefs_${studentId}_${currentSubject}`,
    );
    if (saved) {
      try {
        const p = JSON.parse(saved);
        setDailyDuration(p.dailyDuration ?? 90);
        setDifficulty(p.difficulty ?? 3);
        setLearningPreference(p.learningPreference ?? "balanced");
        setTargetTopic(p.targetTopic);
      } catch {}
    }
  }, [studentId, currentSubject]);

  // 加载画像建议
  useEffect(() => {
    const loadProfile = async () => {
      try {
        const res = await profileApi.get(studentId);
        const p = res.data?.data;
        if (p) {
          const suggestions: string[] = [];
          if (p.weak_areas?.length)
            suggestions.push(
              `薄弱点：${p.weak_areas.slice(0, 3).join("、")} — 建议优先安排`,
            );
          if (p.learning_tempo?.study_speed === "fast")
            suggestions.push("你的学习节奏较快，可适当提高难度或缩短每日时长");
          if (p.learning_tempo?.study_speed === "slow")
            suggestions.push("你的学习节奏较缓，建议降低难度并增加每日时长");
          if (p.cognitive_style?.primary === "kinesthetic")
            suggestions.push("你是动手实践型学习者，建议多选代码实战类资源");
          if ((p.practical_preferences?.overall_score ?? 1) < 0.5)
            suggestions.push("实践偏好分较低，建议增加练习比重");
          setProfileSuggestions(suggestions);
          // 复习提醒来自薄弱点列表（取前 5 条）
          setWeakReviewTopics((p.weak_areas || []).slice(0, 5));
        }
      } catch {}
    };
    loadProfile();
  }, [studentId, currentSubject]);

  useEffect(() => {
    let ignore = false;
    // 切换课程时先清空旧数据，避免显示上一门课的内容
    setPathNodes([]);
    setPathStages([]);
    setPathData(null);
    setVisibleCount(0);
    visibleCountRef.current = 0;
    setLoading(true);
    const load = async () => {
      try {
        const res = await pathApi.current(studentId, currentSubject);
        if (ignore) return;
        if (res.data) {
          const nodes: PathNode[] = res.data.nodes || [];
          const respAny = res.data as unknown as {
            path?: { stages?: PathStage[] };
          };
          const stages: PathStage[] = respAny.path?.stages || [];
          setPathData(res.data as unknown as Record<string, unknown>);
          setPathNodes(nodes as PathNode[]);
          setPathStages(stages);
        }
      } catch {
        if (!ignore) {
          setPathNodes([]);
          setPathStages([]);
        }
      } finally {
        if (!ignore) setLoading(false);
      }
    };
    load();
    return () => {
      ignore = true;
    };
  }, [studentId, currentSubject]);

  // 时间轴 SVG 高度随内容自适应
  useLayoutEffect(() => {
    const el = timelineRef.current;
    if (!el) return;
    const update = () => {
      const h = el.scrollHeight;
      if (h > 0) setTimelineHeight(h);
    };
    update();
    const ro = new ResizeObserver(update);
    ro.observe(el);
    return () => ro.disconnect();
  }, [pathNodes.length]);

  // scroll-powered SVG stroke：随滚动逐渐绘制时间轴线
  useEffect(() => {
    const path = strokePathRef.current;
    const container = timelineRef.current;
    if (!path || !container || timelineHeight <= 0) return;

    const len = path.getTotalLength();
    path.style.strokeDasharray = `${len}`;
    path.style.strokeDashoffset = `${len}`;

    const onScroll = () => {
      const rect = container.getBoundingClientRect();
      const vh = window.innerHeight;
      // 当容器进入视口 80% 时开始绘制，底部到达视口 20% 时完成
      const start = rect.top - vh * 0.8;
      const end = rect.bottom - vh * 0.2;
      const range = end - start;
      const progress = Math.max(0, Math.min(1, -start / range));
      path.style.strokeDashoffset = `${len * (1 - progress)}`;

      // 随 path 绘制进度逐步显现节点（只增不减）
      const count = Math.min(
        pathNodes.length,
        Math.max(
          visibleCountRef.current,
          Math.ceil(progress * pathNodes.length),
        ),
      );
      setVisibleCount(count);
    };

    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();

    return () => window.removeEventListener("scroll", onScroll);
  }, [timelineHeight, pathNodes.length]);

  // 从后端同步已完成节点（避免刷新后丢失）
  useEffect(() => {
    if (!studentId || pathNodes.length === 0) return;
    let ignore = false;
    const syncCompleted = async () => {
      try {
        const res = await learningDataApi.getCompleted(studentId);
        const completedKps = res.data?.completed_kps || [];
        if (!ignore && completedKps.length) {
          setPathNodes((prev) =>
            prev.map((n) => {
              const nodeKp = nodeKpId(n);
              return completedKps.includes(nodeKp)
                ? { ...n, status: "completed" }
                : n;
            }),
          );
        }
      } catch {
        // 静默失败
      }
    };
    syncCompleted();
    return () => {
      ignore = true;
    };
    // 只在 studentId 变化或首次拿到 nodes 时执行
  }, [studentId, pathNodes.length]);

  // 检测节点变化，添加动画效果
  useEffect(() => {
    const prevIds = new Set(
      prevNodesRef.current.map((n) => `${n.id}-${n.status}`),
    );
    const changed = new Set<number>();
    pathNodes.forEach((n) => {
      if (!prevIds.has(`${n.id}-${n.status}`)) {
        changed.add(n.id);
      }
    });
    setChangedNodeIds(changed);
    prevNodesRef.current = [...pathNodes];

    // 2秒后清除动画
    if (changed.size > 0) {
      const timer = setTimeout(() => setChangedNodeIds(new Set()), 2000);
      return () => clearTimeout(timer);
    }
  }, [pathNodes]);

  // 提交学习反思
  const handleSubmitReflection = async () => {
    if (!selectedNode || !reflectionText.trim()) return;
    setSubmittingReflection(true);
    try {
      await logReflectionApi.createReflection({
        student_id: studentId,
        date: new Date().toISOString().slice(0, 10),
        content: `[${selectedNode.title}] ${reflectionText}`,
        tags: ["learning-path", selectedNode.title],
      });
      message.success("反思已提交");

      // 异步：将笔记经 Agent 分析后存入知识库
      const nodeKp = selectedNode.kp_id || `kp_${selectedNode.id}`;
      kbApi
        .analyzeAndSave({
          content: reflectionText,
          kp_id: nodeKp,
          title: selectedNode.title,
        })
        .catch(() => {});

      setReflectionText("");
    } catch (e) {
      message.error((e as Error).message || "提交失败");
    } finally {
      setSubmittingReflection(false);
    }
  };

  const openNodeDetail = (node: PathNode) => {
    setSelectedNode(node);
    setDrawerOpen(true);
    nodeOpenTimeRef.current = Date.now();
  };

  // 节点 -> kp_id 映射（保留 kp_id；缺失时根据课程退化）
  const nodeKpId = (node: PathNode): string => {
    if (node.kp_id) return String(node.kp_id);
    const idNum = Number(node.id);
    const prefix = currentSubject === "电路分析" ? "kp_e" : "kp_c";
    if (Number.isFinite(idNum) && idNum >= 1 && idNum <= 20) {
      return `${prefix}${String(idNum).padStart(2, "0")}`;
    }
    return String(node.id);
  };

  // 取节点对应阶段的真实资源类型（来自后端 path.stages[idx].resources）
  const getNodeResources = (
    node: PathNode,
  ): {
    title: string;
    type: string;
    icon: React.ReactNode;
    color: string;
  }[] => {
    const idx = pathNodes.findIndex((n) => n.id === node.id);
    const stage = pathStages[idx];
    if (!stage?.resources?.length) return [];
    return stage.resources.map((r, i) => {
      const meta = resourceTypeMeta[r] || {
        icon: <FileTextOutlined />,
        color: "#64748b",
      };
      return {
        title: `${stage.title}：${r}`,
        type: r,
        icon: meta.icon,
        color: meta.color,
        // 强制 key
        ...{ _i: i },
      };
    });
  };

  const handleGeneratePath = async () => {
    setLoading(true);
    try {
      const res = await pathApi.generate({
        student_id: studentId,
        target_topic: targetTopic,
        daily_duration: dailyDuration,
        difficulty: difficulty,
        preference: learningPreference,
        subject: currentSubject,
      });
      const responseData = res.data as unknown as Record<string, unknown>;
      const pathPayload = (
        responseData.data as Record<string, unknown> | undefined
      )?.path as Record<string, unknown> | undefined;
      const stages: PathStage[] =
        (pathPayload?.stages as PathStage[] | undefined) || [];
      const nodes: PathNode[] = stages.map((s, idx) => ({
        id: idx + 1,
        title: s.title,
        status: (idx === 0 ? "in-progress" : "pending") as PathNode["status"],
        type: s.resources?.[0] || "综合",
        resources: s.topics?.length || 3,
      }));
      setPathNodes(nodes);
      setPathStages(stages);
      setPathData(responseData.data as Record<string, unknown>);
      message.success("路径生成成功");
    } catch (e) {
      message.error((e as Error).message || "生成失败");
    } finally {
      setLoading(false);
    }
  };

  const handleSavePreferences = () => {
    const prefs = {
      dailyDuration,
      difficulty,
      learningPreference,
      targetTopic,
    };
    localStorage.setItem(
      `path_prefs_${studentId}_${currentSubject}`,
      JSON.stringify(prefs),
    );
    message.success("偏好设置已保存");
  };

  const handleAdjustPath = async () => {
    if (!adjustFeedback.trim()) {
      message.warning("请输入调整反馈");
      return;
    }
    setLoading(true);
    try {
      const res = await pathApi.adjust(studentId, {
        feedback: adjustFeedback,
        current_path: pathData?.path as LearningPathData | undefined,
      });
      const adjustData = (res.data as unknown as Record<string, unknown>)
        .data as Record<string, unknown> | undefined;
      const stages: PathStage[] =
        (adjustData?.stages as PathStage[] | undefined) || [];
      if (stages.length) {
        const nodes: PathNode[] = stages.map((s, idx) => ({
          id: idx + 1,
          title: s.title,
          status: (idx === 0 ? "in-progress" : "pending") as PathNode["status"],
          type: s.resources?.[0] || "综合",
          resources: s.topics?.length || 3,
        }));
        setPathNodes(nodes);
        setPathStages(stages);
        setPathData({ ...pathData, path: adjustData });
      }
      message.success("路径已调整");
      setAdjustFeedback("");
    } catch (e) {
      message.error((e as Error).message || "调整失败");
    } finally {
      setLoading(false);
    }
  };

  const handleNodeAction = async (
    nodeId: number,
    action: "complete" | "skip" | "reset",
  ) => {
    const node = pathNodes.find((n) => n.id === nodeId);
    // 标记完成：写入后端
    if (action === "complete" && node) {
      const elapsedSec = Math.max(
        30,
        Math.round((Date.now() - nodeOpenTimeRef.current) / 1000),
      );
      try {
        await learningDataApi.record({
          student_id: studentId,
          kp_id: nodeKpId(node),
          action: "complete",
          duration: elapsedSec,
          progress: 1,
        });
        // 自动整理到知识库
        kbApi
          .autoOrganize({
            kp_id: nodeKpId(node),
            title: node.title,
            content: `# ${node.title}\n\n学习路径节点完成。`,
            action: "learn",
          })
          .catch(() => {});
      } catch (e) {
        message.error((e as Error).message || "同步后端失败");
        return;
      }
    }
    setPathNodes((prev) =>
      prev.map((n) => {
        if (n.id !== nodeId) return n;
        if (action === "complete") return { ...n, status: "completed" };
        if (action === "skip")
          return { ...n, status: "pending", skipped: true };
        if (action === "reset")
          return { ...n, status: "pending", skipped: false };
        return n;
      }),
    );
    message.success(
      action === "complete"
        ? "已标记完成"
        : action === "skip"
          ? "已跳过该节点"
          : "已重置进度",
    );
  };

  const handleBatchComplete = async (ids: number[]) => {
    const targets = pathNodes.filter((n) => ids.includes(n.id));
    const elapsedSec = Math.max(
      30,
      Math.round((Date.now() - nodeOpenTimeRef.current) / 1000),
    );
    try {
      await Promise.all(
        targets.map((n) =>
          learningDataApi.record({
            student_id: studentId,
            kp_id: nodeKpId(n),
            action: "complete",
            duration: elapsedSec,
            progress: 1,
          }),
        ),
      );
      // 批量自动整理到知识库
      kbApi
        .batchOrganize(
          targets.map((n) => ({
            kp_id: nodeKpId(n),
            title: n.title,
            content: `# ${n.title}\n\n学习路径节点完成。`,
            action: "learn" as const,
          })),
        )
        .catch(() => {});
    } catch (e) {
      message.error((e as Error).message || "批量同步失败");
      return;
    }
    setPathNodes((prev) =>
      prev.map((n) => (ids.includes(n.id) ? { ...n, status: "completed" } : n)),
    );
    message.success(`已批量标记 ${ids.length} 个节点为已完成`);
  };

  // ===== 资源生成相关函数 =====
  const loadResources = async () => {
    setResourcesLoading(true);
    try {
      const res = await apiGet<{ code: number; data: ResourceItem[] }>(
        "/resource/list",
      );
      setResources(res.data || []);
    } catch {
      // 静默失败
    } finally {
      setResourcesLoading(false);
    }
  };

  useEffect(() => {
    loadResources();
  }, []);

  // 加载薄弱知识点
  useEffect(() => {
    const loadWeakPoints = async () => {
      try {
        const res = await profileApi.get(studentId);
        const p = res.data?.data;
        if (p?.weak_areas?.length) {
          setWeakPoints(
            p.weak_areas.map((area: string) => ({
              name: area,
              mastery: Math.floor(Math.random() * 40 + 30),
            })),
          );
        }
      } catch {
        // 静默失败
      }
    };
    loadWeakPoints();
  }, [studentId]);

  const handleGenerateResource = async () => {
    setGeneratingResource(true);
    setAgentStep(0);
    setGenResult("");
    try {
      // 调用后端异步任务接口
      const token = useAppStore.getState().token || "";
      const res = await fetch(
        `${import.meta.env.VITE_API_BASE_URL || "/api/v1"}/resource/generate`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            student_id: studentId,
            topic:
              genTarget === "weak"
                ? selectedWeakPoints.join("、") || "薄弱知识点"
                : targetTopic,
            title:
              genTarget === "weak"
                ? selectedWeakPoints.join("、") || "薄弱知识点"
                : targetTopic,
            type: genType,
            resource_types: [genType],
            subject: genSubject,
            difficulty: genDifficulty,
            weak_points: genTarget === "weak" ? selectedWeakPoints : undefined,
          }),
        },
      );
      const data = await res.json();
      const taskId = data.task_id;
      if (!taskId) {
        throw new Error(data.message || "启动生成任务失败");
      }

      // 轮询任务状态
      setAgentStep(1);
      let pollCount = 0;
      const MAX_POLL = 45; // 90 seconds max
      const pollInterval = setInterval(async () => {
        pollCount++;
        if (pollCount > MAX_POLL) {
          clearInterval(pollInterval);
          setGeneratingResource(false);
          setAgentStep(-1);
          message.error("生成超时，请稍后重试");
          return;
        }
        try {
          const taskRes = await fetch(
            `${import.meta.env.VITE_API_BASE_URL || "/api/v1"}/resource/task/${taskId}`,
            {
              headers: {
                Authorization: `Bearer ${useAppStore.getState().token || ""}`,
              },
            },
          );
          const taskData = await taskRes.json();
          if (taskData.status === "completed") {
            clearInterval(pollInterval);
            setAgentStep(AGENT_STEPS.length);
            setGeneratingResource(false);
            // 提取生成结果
            const resources = taskData.resources || {};
            const firstKey = Object.keys(resources)[0];
            if (firstKey) {
              const val = resources[firstKey];
              setGenResult(
                typeof val === "string" ? val : JSON.stringify(val, null, 2),
              );
            }
            loadResources();
            message.success("资源生成完成");
          } else if (taskData.status === "failed") {
            clearInterval(pollInterval);
            setGeneratingResource(false);
            setAgentStep(-1);
            message.error(taskData.message || "生成失败");
          } else {
            // 仍在运行，更新进度
            setAgentStep(
              taskData.progress > 0.5 ? 2 : taskData.progress > 0 ? 1 : 0,
            );
          }
        } catch {
          // 轮询出错，停止
          clearInterval(pollInterval);
          setGeneratingResource(false);
          setAgentStep(-1);
          message.error("网络错误，请稍后重试");
        }
      }, 2000);
    } catch (e) {
      setGeneratingResource(false);
      setAgentStep(-1);
      message.error((e as Error).message || "生成失败");
    }
  };

  const completedCount = pathNodes.filter(
    (n) => n.status === "completed",
  ).length;
  const progress = pathNodes.length
    ? Math.round((completedCount / pathNodes.length) * 100)
    : 0;

  const _timelineItems = useMemo(
    () =>
      pathNodes.map((node) => ({
        dot: (
          <div
            className="w-9 h-9 rounded-full flex items-center justify-center text-white shadow-sm"
            style={{ background: statusColors[node.status] }}
          >
            <StatusIcon status={node.status} />
          </div>
        ),
        color: statusColors[node.status],
        children: (
          <div
            className="p-5 rounded-xl bg-white border border-slate-100 hover:border-slate-200 hover:shadow-card transition-all cursor-pointer"
            onClick={() => openNodeDetail(node)}
          >
            <div className="flex items-center gap-2 mb-2">
              <Tag
                className="rounded-full border-0 text-xs font-medium"
                style={{
                  background: statusBg[node.status],
                  color: statusColors[node.status],
                }}
              >
                {statusLabels[node.status]}
              </Tag>
              <span className="text-xs text-slate-400">{node.type}</span>
            </div>
            <Typography.Text className="font-bold text-slate-800 block text-base">
              {node.title}
            </Typography.Text>
            <Typography.Text className="text-slate-400 text-sm">
              {node.resources} 个资源
            </Typography.Text>
          </div>
        ),
      })),
    [pathNodes],
  );

  return (
    <div className="space-y-5">
      {/* 顶部控制栏 */}
      <Card
        className="border border-slate-100 rounded-2xl"
        styles={{ body: { padding: "24px" } }}
      >
        <div className="flex flex-wrap items-center justify-between gap-4">
          <Space>
            <div className="w-10 h-10 rounded-xl bg-slate-900 flex items-center justify-center text-white">
              <FlagOutlined />
            </div>
            <div>
              <Typography.Title level={4} className="!m-0 text-slate-800">
                {targetTopic || "学习路径"}
              </Typography.Title>
              <Typography.Text className="text-slate-400 text-xs">
                个性化路径 · 共 {pathNodes.length} 个阶段
              </Typography.Text>
            </div>
          </Space>
          <Space>
            <Tag className="rounded-full border-0 bg-indigo-50 text-indigo-600 text-xs cursor-default">
              <ClockCircleOutlined /> 时间轴视图
            </Tag>
            <Tooltip title="基于知识图谱约束的 LLM 路径规划">
              <Tag className="rounded-full border-0 bg-indigo-50 text-indigo-600 text-xs cursor-default">
                <ApartmentOutlined /> KG 约束
              </Tag>
            </Tooltip>
            <Button
              type="primary"
              icon={<SwapOutlined />}
              loading={loading}
              className="rounded-lg bg-primary"
              onClick={() => setDrawerOpen(true)}
            >
              调整路径
            </Button>
            <Button
              className="rounded-lg border-slate-200"
              onClick={handleGeneratePath}
              loading={loading}
            >
              重新生成
            </Button>
            <Button
              className="rounded-lg border-slate-200"
              icon={<HistoryOutlined />}
              onClick={() => setAdjustLogOpen(true)}
            >
              调整记录
            </Button>
          </Space>
        </div>

        <div className="mt-6">
          <div className="flex justify-between text-sm text-slate-500 mb-2">
            <span className="font-medium">总体进度</span>
            <span className="font-bold text-primary">{progress}%</span>
          </div>
          <Progress
            percent={progress}
            strokeColor={{ from: "#4f46e5", to: "#0ea5e9" }}
            trailColor="#f1f5f9"
            size="small"
            showInfo={false}
            strokeLinecap="round"
          />
        </div>
      </Card>

      {/* 艾宾浩斯复习提醒 */}
      {showReviewAlert && weakReviewTopics.length > 0 && (
        <div className="bg-amber-50 border border-amber-100 rounded-2xl p-4 flex items-center gap-3">
          <ExclamationCircleOutlined className="text-amber-500 text-lg" />
          <div className="flex-1">
            <div className="text-sm font-medium text-amber-800">
              遗忘曲线提醒：有 {weakReviewTopics.length} 个知识点需要今日复习
            </div>
            <div className="text-xs text-amber-600">
              {weakReviewTopics.slice(0, 3).join("、")} —
              基于画像薄弱点与艾宾浩斯遗忘曲线计算
            </div>
          </div>
          <Button
            size="small"
            className="rounded-lg border-amber-200 text-amber-700"
            onClick={() => {
              const today = new Date().toISOString().slice(0, 10);
              localStorage.setItem("review_alert_dismissed", today);
              setShowReviewAlert(false);
            }}
          >
            稍后提醒
          </Button>
          <Button
            size="small"
            type="primary"
            className="rounded-lg bg-amber-500 border-amber-500"
            onClick={() => navigate("/personal?tab=forgetting")}
          >
            <ReloadOutlined /> 开始复习
          </Button>
        </div>
      )}

      {viewMode === "timeline" && (
        <div className="bg-white rounded-2xl border border-slate-100 p-8 md:p-10">
          {pathNodes.length === 0 ? (
            <div className="text-center py-12 text-slate-400 text-sm">
              暂无学习路径
            </div>
          ) : (
            <div className="max-w-2xl mx-auto">
              {/* 时间轴概览 */}
              <div className="flex items-center justify-between mb-8 pb-4 border-b border-slate-100">
                <div>
                  <Typography.Text className="text-slate-500 text-sm">
                    预计总时长
                  </Typography.Text>
                  <div className="text-2xl font-bold text-slate-800">
                    {Math.ceil(
                      pathNodes.reduce(
                        (sum, n) => sum + (n.resources || 3) * 20,
                        0,
                      ) / dailyDuration,
                    )}{" "}
                    天
                  </div>
                </div>
                <div className="text-right">
                  <Typography.Text className="text-slate-500 text-sm">
                    每日学习
                  </Typography.Text>
                  <div className="text-2xl font-bold text-slate-800">
                    {dailyDuration} 分钟
                  </div>
                </div>
              </div>

              {/* 自定义时间轴：避免 antd Timeline label 挤压 */}
              <div className="relative" ref={timelineRef}>
                {/* scroll-powered SVG stroke 中心线（背景层） */}
                <svg
                  className="absolute left-4 md:left-1/2 top-0 -translate-x-1/2 pointer-events-none overflow-visible"
                  width={16}
                  height={timelineHeight}
                  viewBox={`0 0 16 ${Math.max(timelineHeight, 1)}`}
                >
                  {/* 底色参考线 */}
                  <path
                    d={lineD}
                    stroke="#e2e8f0"
                    strokeWidth={6}
                    strokeLinecap="round"
                    fill="none"
                  />
                  {/* scroll-powered 深绿色绘制线 */}
                  <path
                    ref={strokePathRef}
                    d={lineD}
                    stroke="#10b981"
                    strokeWidth={6}
                    strokeLinecap="round"
                    fill="none"
                  />
                </svg>
                <div className="space-y-8">
                  {pathNodes.map((node, idx) => {
                    const cumulativeMinutes = pathNodes
                      .slice(0, idx)
                      .reduce((sum, n) => sum + (n.resources || 3) * 20, 0);
                    const dayNum =
                      Math.floor(cumulativeMinutes / dailyDuration) + 1;
                    const weekNum = Math.ceil(dayNum / 7);
                    const isMilestone = dayNum % 7 === 1 && idx > 0;
                    const isLeft = idx % 2 === 0;
                    return (
                      <div
                        key={node.id}
                        className={`relative flex items-start gap-4 md:gap-8 transition-opacity transition-transform duration-700 ${idx < visibleCount ? "opacity-100 translate-y-0" : "opacity-0 translate-y-6"} ${isLeft ? "md:flex-row" : "md:flex-row-reverse"}`}
                      >
                        {/* 移动端：左侧固定；桌面端：交替 */}
                        <div className="hidden md:block flex-1" />
                        {/* 时间轴节点圆点 */}
                        <div className="relative z-10 shrink-0">
                          <div
                            className="w-10 h-10 rounded-full flex items-center justify-center text-white shadow-sm text-sm"
                            style={{ background: statusColors[node.status] }}
                          >
                            <StatusIcon
                              status={node.status}
                              pendingIcon={
                                <span className="text-xs font-bold">
                                  {idx + 1}
                                </span>
                              }
                            />
                          </div>
                        </div>
                        {/* 内容卡片 */}
                        <div
                          className={`flex-1 ${isLeft ? "md:text-left" : "md:text-right"}`}
                        >
                          {/* 日期标签 */}
                          <div
                            className={`mb-2 text-xs leading-relaxed ${isLeft ? "md:text-left" : "md:text-right"}`}
                          >
                            <span className="font-bold text-slate-600 mr-2">
                              第 {dayNum} 天
                            </span>
                            <span className="text-slate-400">
                              {(node.resources || 3) * 20} 分钟
                            </span>
                            {isMilestone && (
                              <span className="text-amber-500 font-medium ml-2">
                                第 {weekNum} 周
                              </span>
                            )}
                          </div>
                          {/* 卡片 */}
                          <div
                            className={`inline-block p-5 rounded-xl bg-white border border-slate-100 hover:border-slate-200 hover:shadow-card transition-all cursor-pointer max-w-sm text-left ${isMilestone ? "ring-2 ring-amber-100" : ""} ${changedNodeIds.has(node.id) ? "animate-pulse-once ring-2 ring-indigo-200" : ""}`}
                            onClick={() => openNodeDetail(node)}
                          >
                            {isMilestone && (
                              <Tag className="rounded-full border-0 bg-amber-50 text-amber-600 text-xs mb-2">
                                <FlagOutlined /> 里程碑 · 第 {weekNum} 周
                              </Tag>
                            )}
                            <div className="flex items-center gap-2 mb-2 flex-wrap">
                              <Tag
                                className="rounded-full border-0 text-xs font-medium"
                                style={{
                                  background: statusBg[node.status],
                                  color: statusColors[node.status],
                                }}
                              >
                                {statusLabels[node.status]}
                              </Tag>
                              <span className="text-xs text-slate-400">
                                {node.type}
                              </span>
                            </div>
                            <Typography.Text className="font-bold text-slate-800 block text-base">
                              {node.title}
                            </Typography.Text>
                            <Typography.Text className="text-slate-400 text-sm">
                              {node.resources} 个资源
                            </Typography.Text>
                          </div>
                        </div>
                        {/* 移动端占位 */}
                        <div className="md:hidden flex-1" />
                      </div>
                    );
                  })}
                  {/* 最后一个节点后的“未完待续”标记 */}
                  <div className="relative flex items-start gap-4 md:gap-8">
                    <div className="hidden md:block flex-1" />
                    <div className="relative z-10 shrink-0">
                      <div className="w-10 h-10 rounded-full flex items-center justify-center text-white shadow-sm text-sm bg-emerald-500">
                        <span className="text-lg leading-none">…</span>
                      </div>
                    </div>
                    <div className="flex-1">
                      <div className="inline-block px-3 py-1.5 rounded-full bg-emerald-50 border border-emerald-100 text-xs font-medium text-emerald-600">
                        未完待续 · 更多知识点持续更新中
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* AI 资源生成面板 */}
      <div className="bg-gradient-to-br from-blue-50 to-slate-50 rounded-2xl border border-blue-100 p-6">
        <div className="flex items-center gap-3 mb-5">
          <div className="w-10 h-10 rounded-xl bg-primary flex items-center justify-center text-white text-lg">
            <ThunderboltOutlined />
          </div>
          <div className="flex-1">
            <div className="font-semibold text-slate-800">AI 智能生成资源</div>
            <div className="text-xs text-slate-400">
              基于你的学习画像和最近错题，一键生成针对性资源
            </div>
          </div>
          <Tag color="blue" className="rounded-full">
            Beta
          </Tag>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <Select
            value={genSubject}
            onChange={setGenSubject}
            size="middle"
            style={{ width: 120 }}
            options={[
              { value: "C语言", label: "C语言" },
              { value: "电路分析", label: "电路分析" },
            ]}
          />
          <Select
            value={genTarget}
            onChange={setGenTarget}
            size="middle"
            style={{ width: 140 }}
            options={[
              { value: "weak", label: "针对薄弱点" },
              { value: "goal", label: "针对学习目标" },
              { value: "custom", label: "自定义主题" },
            ]}
          />
          <Select
            value={genType}
            onChange={setGenType}
            size="middle"
            style={{ width: 120 }}
            options={[
              { value: "document", label: "课程讲义" },
              { value: "mindmap", label: "知识导图" },
              { value: "quiz", label: "练习题目" },
              { value: "reading", label: "扩展阅读" },
              { value: "code", label: "代码示例" },
            ]}
          />
          <Select
            value={genDifficulty}
            onChange={setGenDifficulty}
            size="middle"
            style={{ width: 100 }}
            options={[
              { value: "easy", label: "简单" },
              { value: "medium", label: "中等" },
              { value: "hard", label: "困难" },
            ]}
          />
          <Button
            type="primary"
            icon={<ThunderboltOutlined />}
            onClick={handleGenerateResource}
            loading={generatingResource}
            className="rounded-lg bg-primary"
          >
            一键生成
          </Button>
        </div>

        {genTarget === "weak" && weakPoints.length > 0 && (
          <div className="mt-3 p-3 bg-white rounded-xl border border-slate-100">
            <div className="text-xs text-slate-400 mb-2">
              选择要针对的薄弱知识点（不选则全部针对）：
            </div>
            <div className="flex flex-wrap gap-1.5">
              {weakPoints.map((wp) => (
                <Tag
                  key={wp.name}
                  color={
                    selectedWeakPoints.includes(wp.name) ? "blue" : "default"
                  }
                  className="cursor-pointer text-xs"
                  onClick={() =>
                    setSelectedWeakPoints((prev) =>
                      prev.includes(wp.name)
                        ? prev.filter((n) => n !== wp.name)
                        : [...prev, wp.name],
                    )
                  }
                >
                  {wp.name} ({wp.mastery}%)
                </Tag>
              ))}
            </div>
          </div>
        )}

        {agentStep >= 0 && (
          <div className="mt-4 p-3 bg-white rounded-xl border border-slate-100">
            <div className="text-sm font-semibold text-slate-800 mb-2">
              <RobotOutlined /> 多智能体协作中
            </div>
            <Steps
              current={agentStep}
              size="small"
              items={AGENT_STEPS.map((s, i) => ({
                title: s.title,
                description: s.description,
                status:
                  agentStep > i
                    ? "finish"
                    : agentStep === i
                      ? "process"
                      : "wait",
              }))}
            />
          </div>
        )}

        {genResult && (
          <div className="mt-4 p-4 bg-white rounded-xl border border-slate-100 text-sm leading-relaxed whitespace-pre-wrap max-h-48 overflow-auto">
            {genResult}
          </div>
        )}
      </div>

      {/* 资源列表 */}
      <div className="bg-white rounded-2xl border border-slate-100 p-6">
        <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
          <div className="font-semibold text-slate-800 flex items-center gap-2">
            我的资源
            <Button
              type="text"
              size="small"
              icon={<ReloadOutlined />}
              onClick={loadResources}
              loading={resourcesLoading}
            />
          </div>
          <Space wrap>
            <Input.Search
              placeholder="搜索资源"
              allowClear
              style={{ width: 180 }}
              onSearch={(v) => {
                setResourceKeyword(v);
                setResourcePage(1);
              }}
            />
            <Select
              value={resourceFilter.type || undefined}
              onChange={(v) => {
                setResourceFilter((f) => ({ ...f, type: v || "" }));
                setResourcePage(1);
              }}
              style={{ width: 90 }}
              allowClear
              placeholder="类型"
              options={[
                { value: "document", label: "讲义" },
                { value: "questions", label: "练习" },
                { value: "quiz", label: "测验" },
                { value: "mindmap", label: "导图" },
                { value: "code", label: "代码" },
                { value: "reading", label: "阅读" },
              ]}
            />
            <Select
              value={resourceFilter.subject || undefined}
              onChange={(v) => {
                setResourceFilter((f) => ({ ...f, subject: v || "" }));
                setResourcePage(1);
              }}
              style={{ width: 100 }}
              allowClear
              placeholder="学科"
              options={[
                { value: "C语言", label: "C语言" },
                { value: "电路分析", label: "电路分析" },
              ]}
            />
            <Select
              value={resourceFilter.difficulty || undefined}
              onChange={(v) => {
                setResourceFilter((f) => ({ ...f, difficulty: v || "" }));
                setResourcePage(1);
              }}
              style={{ width: 90 }}
              allowClear
              placeholder="难度"
              options={[
                { value: "easy", label: "简单" },
                { value: "medium", label: "中等" },
                { value: "hard", label: "困难" },
              ]}
            />
          </Space>
          <div className="text-xs text-slate-400 mt-2">
            共 {resources.length} 个资源
          </div>
        </div>

        {(() => {
          const filtered = resources
            .filter(
              (r) => !resourceFilter.type || r.type === resourceFilter.type,
            )
            .filter(
              (r) =>
                !resourceFilter.subject || r.subject === resourceFilter.subject,
            )
            .filter(
              (r) =>
                !resourceFilter.difficulty ||
                r.difficulty === resourceFilter.difficulty,
            )
            .filter(
              (r) => !resourceKeyword || r.title.includes(resourceKeyword),
            );
          const pageSize = 8;
          const paged = filtered.slice(
            (resourcePage - 1) * pageSize,
            resourcePage * pageSize,
          );

          if (resourcesLoading) {
            return (
              <div className="text-center py-8 text-slate-400 text-sm">
                加载中...
              </div>
            );
          }

          if (filtered.length === 0) {
            return (
              <div className="text-center py-8 text-slate-400 text-sm">
                暂无资源，使用上方AI生成面板创建
              </div>
            );
          }

          return (
            <>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                {paged.map((r) => {
                  const typeColor =
                    r.type === "document"
                      ? "green"
                      : r.type === "mindmap"
                        ? "blue"
                        : r.type === "questions" || r.type === "quiz"
                          ? "orange"
                          : r.type === "code"
                            ? "geekblue"
                            : r.type === "reading"
                              ? "cyan"
                              : "default";
                  return (
                    <div
                      key={r.id}
                      className="p-4 rounded-xl border border-slate-100 hover:border-primary/30 hover:shadow-sm transition-all cursor-pointer"
                      onClick={() => {
                        setSelectedResource(r);
                        setResourceDetailOpen(true);
                      }}
                    >
                      <div className="flex items-center gap-2 mb-2">
                        {resourceTypeMeta[r.type]?.icon || <FileTextOutlined />}
                        <Tag
                          className="rounded-full text-xs border-0"
                          color={typeColor}
                        >
                          {r.type}
                        </Tag>
                        {r.difficulty && (
                          <Tag
                            className="rounded-full text-xs border-0"
                            color={
                              r.difficulty === "easy"
                                ? "success"
                                : r.difficulty === "hard"
                                  ? "error"
                                  : "default"
                            }
                          >
                            {r.difficulty === "easy"
                              ? "简单"
                              : r.difficulty === "hard"
                                ? "困难"
                                : "中等"}
                          </Tag>
                        )}
                      </div>
                      <div className="font-medium text-sm text-slate-800 line-clamp-2 mb-1">
                        {r.title}
                      </div>
                      <div className="flex items-center justify-between text-xs text-slate-400">
                        <span>{r.created_at?.slice(0, 10)}</span>
                        {r.subject && <span>{r.subject}</span>}
                      </div>
                    </div>
                  );
                })}
              </div>
              {filtered.length > pageSize && (
                <div className="mt-4 flex justify-center">
                  <input
                    type="range"
                    min={1}
                    max={Math.ceil(filtered.length / pageSize)}
                    value={resourcePage}
                    onChange={(e) => setResourcePage(Number(e.target.value))}
                    className="w-48"
                  />
                  <span className="ml-2 text-xs text-slate-400">
                    {resourcePage}/{Math.ceil(filtered.length / pageSize)} 页
                  </span>
                </div>
              )}
            </>
          );
        })()}
      </div>

      {/* 知识图谱视图 */}
      {/* 节点详情/调整抽屉 */}
      <Drawer
        title={
          selectedNode ? (
            <Space>
              <div
                className="w-8 h-8 rounded-lg flex items-center justify-center text-white"
                style={{ background: statusColors[selectedNode.status] }}
              >
                <StatusIcon
                  status={selectedNode.status}
                  pendingIcon={<RocketOutlined />}
                />
              </div>
              <span className="font-semibold">{selectedNode.title}</span>
            </Space>
          ) : (
            <span className="font-semibold">调整学习路径</span>
          )
        }
        placement="right"
        onClose={() => {
          setDrawerOpen(false);
          setSelectedNode(null);
          setReflectionText("");
        }}
        open={drawerOpen}
        width={440}
        className="rounded-l-2xl"
      >
        {selectedNode ? (
          <div className="space-y-6">
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-100">
              <Space>
                <Tag
                  className="rounded-full border-0 text-xs font-medium"
                  style={{
                    background: statusBg[selectedNode.status],
                    color: statusColors[selectedNode.status],
                  }}
                >
                  {statusLabels[selectedNode.status]}
                </Tag>
                <Tag className="rounded-full border-0 bg-slate-100 text-slate-600 text-xs">
                  {selectedNode.type}
                </Tag>
              </Space>
              <Typography.Text className="text-slate-600 block mt-3 leading-relaxed text-sm">
                该节点包含{" "}
                <strong className="text-slate-800">
                  {selectedNode.resources}
                </strong>{" "}
                个多模态学习资源，完成后可解锁后续内容。
              </Typography.Text>
            </div>

            <div>
              <Typography.Text className="font-semibold text-slate-800 block mb-3 text-sm">
                关联资源
              </Typography.Text>
              {(() => {
                const items = getNodeResources(selectedNode);
                if (items.length === 0) {
                  return (
                    <div className="text-xs text-slate-400 px-2 py-3">
                      该节点尚无资源数据，可点击下方按钮去资源中心生成
                    </div>
                  );
                }
                return (
                  <List
                    itemLayout="horizontal"
                    dataSource={items}
                    renderItem={(item) => (
                      <List.Item className="hover:bg-slate-50 rounded-xl transition-colors px-2">
                        <List.Item.Meta
                          avatar={
                            <Avatar
                              style={{
                                background: item.color + "12",
                                color: item.color,
                              }}
                              icon={item.icon}
                              className="text-xs"
                            />
                          }
                          title={
                            <Typography.Text className="text-slate-700 font-medium text-sm">
                              {item.title}
                            </Typography.Text>
                          }
                          description={
                            <Tag className="rounded-full text-xs border-0 bg-slate-100 text-slate-500">
                              {item.type}
                            </Tag>
                          }
                        />
                      </List.Item>
                    )}
                  />
                );
              })()}
            </div>

            {selectedNode.status === "completed" && (
              <div>
                <Typography.Text className="font-semibold text-slate-800 block mb-3 text-sm">
                  学习反思
                </Typography.Text>
                <div className="space-y-3">
                  <Input.TextArea
                    rows={4}
                    value={reflectionText}
                    onChange={(e) => setReflectionText(e.target.value)}
                    placeholder="完成这个节点后，你学到了什么？有哪些收获或疑问？"
                    className="rounded-xl bg-slate-50 border-slate-200"
                  />
                  <Button
                    className="rounded-lg border-slate-200"
                    loading={submittingReflection}
                    onClick={handleSubmitReflection}
                  >
                    提交反思
                  </Button>
                </div>
              </div>
            )}

            <Button
              type="primary"
              block
              className="rounded-lg bg-primary h-10"
              onClick={() => {
                navigate(`/resource/${nodeKpId(selectedNode)}`);
                setDrawerOpen(false);
              }}
            >
              {selectedNode.status === "completed" ? "重新学习" : "开始学习"}{" "}
              <ArrowRightOutlined />
            </Button>
          </div>
        ) : (
          <div className="space-y-6">
            {/* 路径概览卡片 */}
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-100">
              <div className="flex items-center justify-between mb-3">
                <Typography.Text className="font-semibold text-slate-800 text-sm">
                  当前路径概览
                </Typography.Text>
                <Tag className="rounded-full border-0 bg-indigo-50 text-indigo-600 text-xs">
                  {pathNodes.length} 个阶段
                </Tag>
              </div>
              <div className="grid grid-cols-3 gap-3 text-center">
                <div className="p-2 rounded-lg bg-white border border-slate-100">
                  <div className="text-lg font-bold text-emerald-600">
                    {completedCount}
                  </div>
                  <div className="text-xs text-slate-400">已完成</div>
                </div>
                <div className="p-2 rounded-lg bg-white border border-slate-100">
                  <div className="text-lg font-bold text-indigo-600">
                    {pathNodes.filter((n) => n.status === "in-progress").length}
                  </div>
                  <div className="text-xs text-slate-400">进行中</div>
                </div>
                <div className="p-2 rounded-lg bg-white border border-slate-100">
                  <div className="text-lg font-bold text-slate-600">
                    {Math.max(
                      1,
                      Math.round(
                        ((pathNodes.length - completedCount) * dailyDuration) /
                          60,
                      ),
                    )}
                    h
                  </div>
                  <div className="text-xs text-slate-400">预计剩余</div>
                </div>
              </div>
              <div className="mt-3">
                <Progress
                  percent={progress}
                  strokeColor={{ from: "#4f46e5", to: "#0ea5e9" }}
                  trailColor="#f1f5f9"
                  size="small"
                  showInfo={false}
                  strokeLinecap="round"
                />
                <div className="text-right text-xs text-slate-400 mt-1">
                  总进度 {progress}%
                </div>
              </div>
            </div>

            {/* 画像个性化建议 */}
            {profileSuggestions.length > 0 && (
              <div className="p-3 rounded-xl bg-amber-50 border border-amber-100">
                <div className="flex items-center gap-2 mb-2">
                  <BulbOutlined className="text-amber-500" />
                  <Typography.Text className="font-semibold text-amber-800 text-sm">
                    基于画像的建议
                  </Typography.Text>
                </div>
                <div className="space-y-1.5">
                  {profileSuggestions.map((s, i) => (
                    <div
                      key={i}
                      className="text-xs text-amber-700 leading-relaxed flex items-start gap-1.5"
                    >
                      <span className="shrink-0 mt-0.5 w-1 h-1 rounded-full bg-amber-400" />
                      {s}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Tab 切换 */}
            <Radio.Group
              value={activeAdjustTab}
              onChange={(e) => setActiveAdjustTab(e.target.value)}
              buttonStyle="solid"
              className="w-full flex rounded-lg overflow-hidden"
            >
              <Radio.Button
                value="params"
                className="flex-1 text-center text-xs"
              >
                参数设置
              </Radio.Button>
              <Radio.Button
                value="nodes"
                className="flex-1 text-center text-xs"
              >
                节点管理
              </Radio.Button>
              <Radio.Button
                value="feedback"
                className="flex-1 text-center text-xs"
              >
                智能微调
              </Radio.Button>
            </Radio.Group>

            {/* 参数设置 Tab */}
            {activeAdjustTab === "params" && (
              <div className="space-y-6">
                <div>
                  <Typography.Text className="font-semibold text-slate-800 block mb-2 text-sm">
                    学习目标主题
                  </Typography.Text>
                  <Input
                    value={targetTopic}
                    onChange={(e) => setTargetTopic(e.target.value)}
                    placeholder="例如：掌握 C语言程序设计与数据结构基础"
                    className="rounded-lg"
                  />
                  <Typography.Text className="text-xs text-slate-400 block mt-1">
                    修改后点击「重新规划」生效
                  </Typography.Text>
                </div>

                <div>
                  <Typography.Text className="font-semibold text-slate-800 block mb-3 text-sm">
                    学习偏好
                  </Typography.Text>
                  <Radio.Group
                    value={learningPreference}
                    onChange={(e) => setLearningPreference(e.target.value)}
                    className="flex flex-col gap-3"
                  >
                    <Radio value="theory" className="text-sm">
                      加强理论（更多文档、讲解视频）
                    </Radio>
                    <Radio value="practice" className="text-sm">
                      多些练习（更多代码、算法题）
                    </Radio>
                    <Radio value="balanced" className="text-sm">
                      平衡模式（理论+实践兼顾）
                    </Radio>
                  </Radio.Group>
                </div>

                <div>
                  <div className="flex justify-between mb-2">
                    <Typography.Text className="font-semibold text-slate-800 text-sm">
                      每日学习时长
                    </Typography.Text>
                    <Typography.Text className="text-xs text-slate-500">
                      {dailyDuration} 分钟
                    </Typography.Text>
                  </div>
                  <Slider
                    min={30}
                    max={240}
                    step={15}
                    value={dailyDuration}
                    onChange={setDailyDuration}
                    marks={{ 30: "30m", 120: "2h", 240: "4h" }}
                    tooltip={{ formatter: (v) => `${v}分钟` }}
                  />
                </div>

                <div>
                  <div className="flex justify-between mb-2">
                    <Typography.Text className="font-semibold text-slate-800 text-sm">
                      难度偏好
                    </Typography.Text>
                    <Typography.Text className="text-xs text-slate-500">
                      {difficulty <= 2
                        ? "简单"
                        : difficulty <= 4
                          ? "较易"
                          : difficulty <= 6
                            ? "适中"
                            : difficulty <= 8
                              ? "较难"
                              : "挑战"}
                    </Typography.Text>
                  </div>
                  <Slider
                    min={1}
                    max={10}
                    step={1}
                    value={difficulty}
                    onChange={setDifficulty}
                    marks={{ 1: "简单", 5: "适中", 10: "挑战" }}
                  />
                </div>

                <div className="flex gap-2">
                  <Button
                    className="rounded-lg border-slate-200 flex-1"
                    icon={<SaveOutlined />}
                    onClick={handleSavePreferences}
                  >
                    保存偏好
                  </Button>
                  <Button
                    type="primary"
                    className="rounded-lg bg-primary flex-1"
                    onClick={() => {
                      handleGeneratePath();
                      setDrawerOpen(false);
                    }}
                    loading={loading}
                  >
                    重新规划 <ArrowRightOutlined />
                  </Button>
                </div>
              </div>
            )}

            {/* 节点管理 Tab */}
            {activeAdjustTab === "nodes" && (
              <div className="space-y-4">
                <Typography.Text className="font-semibold text-slate-800 block text-sm">
                  节点状态管理
                </Typography.Text>
                <div className="space-y-2 max-h-[360px] overflow-y-auto pr-1">
                  {pathNodes.map((node) => (
                    <div
                      key={node.id}
                      className="flex items-center gap-3 p-3 rounded-xl bg-white border border-slate-100 hover:border-slate-200 transition-all"
                    >
                      <div
                        className="w-8 h-8 rounded-full flex items-center justify-center text-white text-xs shrink-0"
                        style={{ background: statusColors[node.status] }}
                      >
                        {node.id}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="text-sm font-medium text-slate-800 truncate">
                          {node.title}
                        </div>
                        <div className="text-xs text-slate-400">
                          {node.type} · {statusLabels[node.status]}
                          {node.skipped ? " · 已跳过" : ""}
                        </div>
                      </div>
                      <div className="flex gap-1">
                        {node.status !== "completed" && (
                          <Tooltip title="标记完成">
                            <Button
                              size="small"
                              className="rounded-lg border-emerald-200 text-emerald-600"
                              icon={<CheckCircleOutlined />}
                              onClick={() =>
                                handleNodeAction(node.id, "complete")
                              }
                            />
                          </Tooltip>
                        )}
                        {node.status !== "completed" && !node.skipped && (
                          <Tooltip title="跳过">
                            <Button
                              size="small"
                              className="rounded-lg border-amber-200 text-amber-600"
                              icon={<StepForwardOutlined />}
                              onClick={() => handleNodeAction(node.id, "skip")}
                            />
                          </Tooltip>
                        )}
                        {(node.status === "completed" || node.skipped) && (
                          <Tooltip title="重置">
                            <Button
                              size="small"
                              className="rounded-lg border-slate-200 text-slate-500"
                              icon={<UndoOutlined />}
                              onClick={() => handleNodeAction(node.id, "reset")}
                            />
                          </Tooltip>
                        )}
                        <Tooltip title="开始学习">
                          <Button
                            size="small"
                            type="primary"
                            className="rounded-lg bg-primary"
                            icon={<EyeOutlined />}
                            onClick={() => {
                              navigate(`/resource/${nodeKpId(node)}`);
                              setDrawerOpen(false);
                            }}
                          />
                        </Tooltip>
                      </div>
                    </div>
                  ))}
                </div>

                {pathNodes.some(
                  (n) => n.status === "pending" && !n.skipped,
                ) && (
                  <Popconfirm
                    title="批量标记完成"
                    description="将前几个未开始节点标记为已完成？"
                    onConfirm={() => {
                      const pendingIds = pathNodes
                        .filter((n) => n.status === "pending" && !n.skipped)
                        .slice(0, 3)
                        .map((n) => n.id);
                      handleBatchComplete(pendingIds);
                    }}
                    okText="确认"
                    cancelText="取消"
                  >
                    <Button block className="rounded-lg border-slate-200">
                      批量标记前 3 个节点为已完成
                    </Button>
                  </Popconfirm>
                )}
              </div>
            )}

            {/* 智能微调 Tab */}
            {activeAdjustTab === "feedback" && (
              <div className="space-y-6">
                <div className="p-3 rounded-xl bg-indigo-50 border border-indigo-100">
                  <Typography.Text className="text-xs text-indigo-700 block leading-relaxed">
                    通过自然语言描述你的调整需求，AI
                    将在现有路径基础上做局部优化，而不会完全重置路径。
                  </Typography.Text>
                </div>

                <div>
                  <Typography.Text className="font-semibold text-slate-800 block mb-2 text-sm">
                    调整反馈
                  </Typography.Text>
                  <Input.TextArea
                    rows={4}
                    value={adjustFeedback}
                    onChange={(e) => setAdjustFeedback(e.target.value)}
                    placeholder="例如：指针部分太难了，希望多加一些基础练习；或者我想跳过文件操作，直接学动态内存..."
                    className="rounded-xl bg-slate-50 border-slate-200"
                  />
                </div>

                <div className="flex flex-wrap gap-2">
                  {[
                    "指针部分太难，多加点基础练习",
                    "我想加快进度，减少理论讲解",
                    "跳过文件操作，优先学动态内存",
                    "增加更多实战项目",
                  ].map((tip) => (
                    <Tag
                      key={tip}
                      className="rounded-full border-slate-200 text-slate-600 text-xs cursor-pointer hover:border-primary hover:text-primary transition-all"
                      onClick={() => setAdjustFeedback(tip)}
                    >
                      {tip}
                    </Tag>
                  ))}
                </div>

                <Button
                  type="primary"
                  block
                  className="rounded-lg bg-primary h-10"
                  onClick={handleAdjustPath}
                  loading={loading}
                >
                  智能微调路径 <ArrowRightOutlined />
                </Button>
              </div>
            )}
          </div>
        )}
      </Drawer>

      {/* 资源详情弹窗 */}
      <Modal
        title={selectedResource?.title}
        open={resourceDetailOpen}
        onCancel={() => {
          setResourceDetailOpen(false);
          setSelectedResource(null);
        }}
        footer={null}
        width={700}
      >
        {selectedResource && (
          <div className="mt-4">
            <Space className="mb-4">
              <Tag color="blue">{selectedResource.type}</Tag>
              <Tag>{selectedResource.subject}</Tag>
              <Tag
                color={
                  selectedResource.difficulty === "easy"
                    ? "success"
                    : selectedResource.difficulty === "hard"
                      ? "error"
                      : "default"
                }
              >
                {selectedResource.difficulty === "easy"
                  ? "简单"
                  : selectedResource.difficulty === "hard"
                    ? "困难"
                    : "中等"}
              </Tag>
            </Space>
            {selectedResource.content ? (
              <ResourceContentRenderer
                type={selectedResource.type}
                content={selectedResource.content}
              />
            ) : (
              <div className="text-slate-400 text-sm py-8 text-center">
                暂无内容预览
              </div>
            )}
          </div>
        )}
      </Modal>

      {/* 调整记录面板 */}
      <AdjustmentLogPanel
        open={adjustLogOpen}
        onClose={() => setAdjustLogOpen(false)}
        studentId={studentId}
      />
    </div>
  );
};

export default LearningPathPage;
