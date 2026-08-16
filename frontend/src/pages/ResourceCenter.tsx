import React, { useState, useEffect, useRef, useMemo } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import {
  Typography,
  Card,
  Button,
  Input,
  Space,
  Tabs,
  Tag,
  Collapse,
  FloatButton,
  message,
  Spin,
  Tooltip,
  Modal,
} from "antd";
import {
  FileTextOutlined,
  CodeOutlined,
  MessageOutlined,
  MenuFoldOutlined,
  BookOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  ExperimentOutlined,
  ReadOutlined,
  ArrowRightOutlined,
  CopyOutlined,
  BulbOutlined,
  NodeIndexOutlined,
  CameraOutlined,
  LikeOutlined,
  DislikeOutlined,
  SafetyOutlined,
  ApartmentOutlined,
  ThunderboltOutlined,
  ReloadOutlined,
  PictureOutlined,
} from "@ant-design/icons";
import { useAppStore } from "../store";
import {
  resourceApi,
  tutorApi,
  imageApi,
  knowledgeApi,
  ocrApi,
  learningDataApi,
  logReflectionApi,
  profileApi,
  stm32Api,
} from "../services/api";
import PPTGenerator from "../components/PPTGenerator";
import type { ChatMessage, QuestionItem, VisionContentItem } from "../types";
import { extractApiError } from "../utils/error";
import { useElapsedTime } from "../hooks/useElapsedTime";
import { ChatPanel } from "../components/ChatPanel";
import { MarkdownViewer } from "../components/MarkdownViewer";
import CodeEditor from "../components/CodeEditor";
import AlgorithmVisualizer from "../components/AlgorithmVisualizer";
import MindmapView from "../components/MindmapView";
import Stm32Experiments from "../components/Stm32Experiments";
import { kbApi } from "../services/knowledgeBaseApi";
import "../styles/markdown-content.css";

interface CourseMenuItem {
  key: string;
  icon: React.ReactNode;
  label: string;
  children: { key: string; label: string; completed: boolean }[];
}

const ResourceCenter: React.FC = () => {
  const [activeKey, setActiveKey] = useState("");
  // 知识点切换时记录起点，标记完成时上报真实停留时长
  const getElapsed = useElapsedTime([activeKey]);
  const [courseMenu, setCourseMenu] = useState<CourseMenuItem[]>([]);
  const [menuLoading, setMenuLoading] = useState(false);
  const [chatOpen, setChatOpen] = useState(true);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [notes, setNotes] = useState("");
  const [docContent, setDocContent] = useState("");
  const [codeContent, setCodeContent] = useState("");
  const [codeLanguage, setCodeLanguage] = useState<"Python" | "C">("C");
  const prevCodeLangRef = useRef(codeLanguage);
  const [questions, setQuestions] = useState<QuestionItem[]>([]);
  const [quizAnswers, setQuizAnswers] = useState<Record<string, string>>({});
  const [quizSubmitted, setQuizSubmitted] = useState<Record<string, boolean>>(
    {},
  );
  const [quizScore, setQuizScore] = useState<number | null>(null);
  const [quizSubmitting, _setQuizSubmitting] = useState(false);
  const [mindmapContent, setMindmapContent] = useState("");
  const [loading, setLoading] = useState(false);
  const [resLoading, setResLoading] = useState(false);
  const [bottomTab, setBottomTab] = useState("code");
  const [resourceFeedback, setResourceFeedback] = useState<
    Record<string, "good" | "bad" | null>
  >({});
  const [cornellNotes, setCornellNotes] = useState({
    cues: "",
    notes: "",
    summary: "",
  });
  const [ragActive, setRagActive] = useState(true);
  const [multiAgentStep, _setMultiAgentStep] = useState<
    "planner" | "worker" | "critic" | "done"
  >("done");
  const [ocrModalOpen, setOcrModalOpen] = useState(false);
  const [ocrLoading, setOcrLoading] = useState(false);
  const [ocrImage, setOcrImage] = useState("");
  const [ocrResult, setOcrResult] = useState("");
  const [codeResult, setCodeResult] = useState("");
  const [codeRunning, setCodeRunning] = useState(false);
  const [codeExplanation, setCodeExplanation] = useState("");
  const [codeExplaining, setCodeExplaining] = useState(false);
  const [explainModalOpen, setExplainModalOpen] = useState(false);
  const [imagePrompt, setImagePrompt] = useState("");
  const [generatedImage, setGeneratedImage] = useState("");
  const [imageLoading, setImageLoading] = useState(false);
  const mountedRef = useRef(true);
  const [pptModalOpen, setPptModalOpen] = useState(false);
  const [markingComplete, setMarkingComplete] = useState(false);
  const studentId = useAppStore((s) => s.studentId);
  const storeCurrentSubject = useAppStore((s) => s.currentSubject);
  const location = useLocation();
  const navigate = useNavigate();
  const [weakReviewTopics, setWeakReviewTopics] = useState<string[]>([]);
  const [showReviewBanner, setShowReviewBanner] = useState(true);
  const [stm32WiringDiagrams, setStm32WiringDiagrams] = useState<
    { filename: string; title: string; url: string }[]
  >([]);
  const [stm32Projects, setStm32Projects] = useState<
    { dirname: string; title: string; file_count: number }[]
  >([]);
  const [selectedProject, setSelectedProject] = useState<{
    dirname: string;
    title: string;
    files: { path: string; size: number }[];
  } | null>(null);
  const [projectFilesLoading, setProjectFilesLoading] = useState(false);

  const welcomeMessages: Record<string, string> = {
    C语言:
      "你好！我正在和你一起学习《C语言基础》。C语言是计算机专业的入门语言，掌握它对于理解计算机底层原理至关重要。有什么不懂的地方随时问我。",
    电路分析:
      "你好！我正在和你一起学习《电路分析》。电路分析是电气工程的基础课程，掌握电路定律和分析方法对理解电子系统至关重要。有什么不懂的地方随时问我。",
    STM32嵌入式:
      "你好！我正在和你一起学习《STM32嵌入式开发》。STM32是嵌入式领域最主流的微控制器之一，掌握它能帮助你快速入门物联网和智能硬件开发。有什么不懂的地方随时问我。",
  };

  // kp_id → STM32 课程文件映射
  const stm32KpCourseMap: Record<string, string> = {
    kp_s01: "01_基础入门",
    kp_s02: "01_基础入门",
    kp_s03: "03_输入设备",
    kp_s04: "02_显示模块",
    kp_s05: "04_定时器",
    kp_s06: "05_ADC模数转换",
    kp_s07: "06_DMA数据转运",
    kp_s08: "07_串口通信",
    kp_s09: "08_I2C通信",
    kp_s10: "09_SPI通信",
    kp_s11: "10_RTC实时时钟",
    kp_s12: "11_低功耗模式",
    kp_s13: "12_看门狗",
    kp_s14: "13_Flash操作",
  };

  // kp_id → 接线图章节前缀映射（文件名格式："{章节号}-{序号} 名称.jpg"）
  const stm32WiringChapterMap: Record<string, string[]> = {
    kp_s01: ["2", "3"], // 基础入门：工程模板、LED/蜂鸣器/按键
    kp_s02: ["2", "3"], // 基础入门（同上）
    kp_s03: ["5"], // 输入设备：红外传感器、旋转编码器
    kp_s04: ["4"], // 显示模块：OLED
    kp_s05: ["6"], // 定时器：定时中断、PWM、输入捕获、编码器
    kp_s06: ["7"], // ADC：单通道、多通道
    kp_s07: ["8"], // DMA：数据转运、DMA+AD
    kp_s08: ["9"], // 串口：发送、接收、HEX、文本
    kp_s09: ["10"], // I2C：软件/硬件I2C读写MPU6050
    kp_s10: ["11"], // SPI：软件/硬件SPI读写W25Q64
    kp_s11: ["12"], // RTC：备份寄存器、实时时钟
    kp_s12: ["13"], // 低功耗：主频、睡眠、停止、待机
    kp_s13: ["14"], // 看门狗：独立看门狗、窗口看门狗
    kp_s14: ["15"], // Flash：读写内部FLASH、芯片ID
  };

  const currentTopic = useMemo(
    () =>
      courseMenu
        .flatMap((c) => c.children || [])
        .find((c) => c.key === activeKey)?.label || "",
    [courseMenu, activeKey],
  );

  const currentSubject = useMemo(
    () =>
      courseMenu
        .find((c) => c.children?.some((ch) => ch.key === activeKey))
        ?.label?.replace(/^第\d+章[：:]\s*/, "") || "",
    [courseMenu, activeKey],
  );

  // 组件卸载标记
  useEffect(() => {
    return () => {
      mountedRef.current = false;
    };
  }, []);

  // 加载课程目录
  useEffect(() => {
    let ignore = false;
    const loadMenu = async () => {
      setMenuLoading(true);
      try {
        const res = await knowledgeApi.list(storeCurrentSubject);
        if (ignore) return;
        const kps: Record<string, unknown>[] = res.data?.data || [];
        // 按 subject 字段分组（每个 subject 为一章）
        const subjectMap = new Map<string, Record<string, unknown>[]>();
        for (const kp of kps) {
          const subj = String(kp.subject || "未分类");
          if (!subjectMap.has(subj)) {
            subjectMap.set(subj, []);
          }
          subjectMap.get(subj)!.push(kp);
        }
        const menu: CourseMenuItem[] = [];
        let chapterIdx = 0;
        for (const [subjectName, subjectKps] of subjectMap) {
          chapterIdx++;
          menu.push({
            key: `chapter_${chapterIdx}`,
            icon: <BookOutlined />,
            label: `第${chapterIdx}章：${subjectName}`,
            children: subjectKps.map((kp, idx) => ({
              key: String(kp.kp_id || `kp_${chapterIdx}_${idx}`),
              label: `${chapterIdx}.${idx + 1} ${String(kp.name || "未命名")}`,
              completed: false,
            })),
          });
        }
        setCourseMenu(menu);

        // 课程切换时始终重置到新课程的第一个知识点
        // 仅从其他页面明确跳转时（有 kpId 路由参数）才定位到指定知识点
        const navKpId =
          ((location.state as Record<string, unknown> | null)?.kpId as
            | string
            | undefined) ||
          localStorage.getItem("selected_kp_id") ||
          undefined;
        if (navKpId) {
          localStorage.removeItem("selected_kp_id");
          if (location.state) {
            window.history.replaceState({}, "");
          }
          const found = menu
            .flatMap((m) => m.children || [])
            .find((c) => c.key === navKpId);
          if (found) {
            setActiveKey(navKpId);
            return;
          }
        }
        // 默认选择新课程第一个知识点
        if (menu.length > 0 && menu[0].children.length > 0) {
          setActiveKey(menu[0].children[0].key);
        }
      } catch (_e) {
        if (!ignore) message.error("课程目录加载失败");
      } finally {
        if (!ignore) setMenuLoading(false);
      }
    };
    loadMenu();
    return () => {
      ignore = true;
    };
  }, [storeCurrentSubject]);

  // 切换课程时更新欢迎语
  useEffect(() => {
    setMessages([
      {
        role: "ai",
        content:
          welcomeMessages[storeCurrentSubject] || welcomeMessages["C语言"],
        agent: "辅导助手",
      },
    ]);
  }, [storeCurrentSubject]);

  // 加载已完成知识点列表，初始化目录打勾状态
  useEffect(() => {
    if (!studentId) return;
    let ignore = false;
    const syncCompleted = async () => {
      try {
        const res = await learningDataApi.getCompleted(studentId);
        const completedKps = res.data?.completed_kps || [];
        if (!ignore && completedKps.length > 0) {
          setCourseMenu((prev) =>
            prev.map((ch) => ({
              ...ch,
              children:
                ch.children?.map((item) =>
                  completedKps.includes(item.key)
                    ? { ...item, completed: true }
                    : item,
                ) || [],
            })),
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
  }, [studentId, courseMenu.length]);

  // 加载已保存的笔记/反思
  useEffect(() => {
    if (!studentId) return;
    let ignore = false;
    const loadReflections = async () => {
      try {
        const res = await logReflectionApi.getReflections(studentId, 30);
        if (ignore || !res.data?.data) return;
        const refs = res.data.data as Record<string, unknown>[];
        const plainNote = refs.find((r) =>
          String(r.tags || "").includes("notes"),
        );
        if (plainNote) setNotes(String(plainNote.content || ""));
        const cornell = refs.find((r) =>
          String(r.tags || "").includes("cornell"),
        );
        if (cornell) {
          try {
            setCornellNotes(JSON.parse(String(cornell.content || "{}")));
          } catch {
            setCornellNotes({
              cues: String(cornell.content || ""),
              notes: "",
              summary: "",
            });
          }
        }
      } catch {
        /* ignore */
      }
    };
    loadReflections();
    return () => {
      ignore = true;
    };
  }, [studentId]);

  // 切换代码语言时重新生成代码（仅当语言本身变化时触发，避免 activeKey 切换导致重复请求）
  // STM32 课程跳过：代码已包含在课程 Markdown 中
  useEffect(() => {
    if (!activeKey || !currentTopic) return;
    if (activeKey.startsWith("kp_s")) return;
    if (prevCodeLangRef.current === codeLanguage) return;
    prevCodeLangRef.current = codeLanguage;
    let ignore = false;
    const loadCode = async () => {
      try {
        const codeRes = await resourceApi.generateCode({
          student_id: studentId,
          topic: currentTopic,
          language: codeLanguage,
          kp_id: activeKey,
        });
        if (!ignore && codeRes.data?.code) setCodeContent(codeRes.data.code);
      } catch {
        // ignore
      }
    };
    loadCode();
    return () => {
      ignore = true;
    };
  }, [codeLanguage, activeKey, studentId, currentTopic]);

  useEffect(() => {
    if (!activeKey || !currentTopic) return;
    let ignore = false;
    const isStm32 = activeKey.startsWith("kp_s");

    const load = async () => {
      setResLoading(true);
      try {
        if (isStm32) {
          // STM32 课程：从后端课程文件加载
          const courseId = stm32KpCourseMap[activeKey];
          if (courseId) {
            const courseRes = await stm32Api.getCourseContent(courseId);
            if (ignore) return;
            if (courseRes.data?.data?.content) {
              setDocContent(courseRes.data.data.content);
            }
          }

          // STM32 课程仍使用 API 加载练习题和思维导图
          const [qRes, mapRes] = await Promise.all([
            resourceApi.generateQuestions({
              student_id: studentId,
              topic: currentTopic,
              count: 3,
              kp_id: activeKey,
              subject: storeCurrentSubject,
            }),
            resourceApi.generateMindmap({
              student_id: studentId,
              topic: currentTopic,
              kp_id: activeKey,
            }),
          ]);
          if (ignore) return;
          const qs = Array.isArray(qRes.data?.questions)
            ? qRes.data.questions
            : [];
          if (qs.length) setQuestions(qs);
          setQuizAnswers({});
          setQuizSubmitted({});
          setQuizScore(null);
          if (mapRes.data?.mindmap) {
            const raw = mapRes.data.mindmap;
            if (typeof raw === "string") {
              setMindmapContent(raw);
            } else if ((raw as any).root || (raw as any).name) {
              const toMarkmap = (data: any, depth = 0): string => {
                const prefix = "#".repeat(Math.max(1, depth + 1));
                const n = data.name || data.root || "";
                let text = `${prefix} ${n}\n`;
                if (data.children) {
                  for (const c of data.children)
                    text += toMarkmap(c, depth + 1);
                }
                return text;
              };
              setMindmapContent(toMarkmap(raw));
            } else {
              setMindmapContent("");
            }
          }
        } else {
          // C语言 / 电路分析：原有逻辑
          const docRes = await resourceApi.generateDocument({
            student_id: studentId,
            topic: currentTopic,
            kp_id: activeKey,
          });
          if (ignore) return;
          if (docRes.data?.document) {
            setDocContent(docRes.data.document);
            // 自动保存到知识库
            kbApi
              .autoOrganize({
                kp_id: activeKey,
                title: currentTopic + " 学习笔记",
                content: docRes.data.document.slice(0, 500),
                subject: storeCurrentSubject,
                action: "learn",
              })
              .catch(() => {});
          }

          const [codeRes, qRes, mapRes] = await Promise.all([
            resourceApi.generateCode({
              student_id: studentId,
              topic: currentTopic,
              language: codeLanguage,
              kp_id: activeKey,
            }),
            resourceApi.generateQuestions({
              student_id: studentId,
              topic: currentTopic,
              count: 3,
              kp_id: activeKey,
              subject: storeCurrentSubject,
            }),
            resourceApi.generateMindmap({
              student_id: studentId,
              topic: currentTopic,
              kp_id: activeKey,
            }),
          ]);
          if (ignore) return;
          if (codeRes.data?.code) setCodeContent(codeRes.data.code);
          const qs = Array.isArray(qRes.data?.questions)
            ? qRes.data.questions
            : [];
          if (qs.length) setQuestions(qs);
          setQuizAnswers({});
          setQuizSubmitted({});
          setQuizScore(null);
          if (mapRes.data?.mindmap) {
            const raw = mapRes.data.mindmap;
            if (typeof raw === "string") {
              setMindmapContent(raw);
            } else if ((raw as any).root || (raw as any).name) {
              const toMarkmap = (data: any, depth = 0): string => {
                const prefix = "#".repeat(Math.max(1, depth + 1));
                const n = data.name || data.root || "";
                let text = `${prefix} ${n}\n`;
                if (data.children) {
                  for (const c of data.children)
                    text += toMarkmap(c, depth + 1);
                }
                return text;
              };
              setMindmapContent(toMarkmap(raw));
            } else {
              setMindmapContent("");
            }
          }
        }
      } catch (_e) {
        if (!ignore) message.error("资源加载失败，显示默认内容");
      } finally {
        if (!ignore) setResLoading(false);
      }
    };
    load();
    return () => {
      ignore = true;
    };
  }, [activeKey, studentId]);

  // 独立加载 STM32 接线图和代码工程（避免竞态条件）
  useEffect(() => {
    if (storeCurrentSubject !== "STM32嵌入式") return;
    let ignore = false;
    const load = async () => {
      try {
        const [wiringRes, projectsRes] = await Promise.allSettled([
          stm32Api.listWiringDiagrams(),
          stm32Api.listProjects(),
        ]);
        if (ignore) return;
        if (wiringRes.status === "fulfilled") {
          setStm32WiringDiagrams(wiringRes.value.data?.data?.diagrams || []);
        }
        if (projectsRes.status === "fulfilled") {
          setStm32Projects(projectsRes.value.data?.data?.projects || []);
        }
      } catch {
        // 静默失败
      }
    };
    load();
    return () => {
      ignore = true;
    };
  }, [storeCurrentSubject]);

  // 加载艾宾浩斯复习提醒
  useEffect(() => {
    profileApi
      .get(studentId)
      .then((res) => {
        const p = res.data?.data;
        if (p?.weak_areas?.length) {
          setWeakReviewTopics(p.weak_areas.slice(0, 5));
        }
      })
      .catch(() => {});
  }, [studentId]);

  const handleSend = async (content: string | VisionContentItem[]) => {
    const question = typeof content === "string" ? content : "";
    if (!question.trim()) return;
    setMessages((prev) => [...prev, { role: "user", content: question }]);
    setLoading(true);
    try {
      const res = await tutorApi.ask({
        student_id: studentId,
        question,
        session_id: `${studentId}_resource`,
      });
      const aiReply = res.data?.response || "服务暂时无响应，请稍后再试。";
      setMessages((prev) => [
        ...prev,
        { role: "ai", content: aiReply, agent: "辅导助手" },
      ]);
    } catch (e: unknown) {
      message.error(extractApiError(e, "请求失败"));
      setMessages((prev) => [
        ...prev,
        { role: "ai", content: "服务暂时不可用。", agent: "辅导助手" },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const copyCode = () => {
    navigator.clipboard
      .writeText(codeContent)
      .then(() => message.success("代码已复制"));
  };

  const handleRunCode = async () => {
    setCodeRunning(true);
    setCodeResult("");
    try {
      const res = await resourceApi.executeCode({
        code: codeContent,
        language: codeLanguage,
      });
      const data = res.data as unknown as Record<string, unknown>;
      const output = String(data.output ?? "");
      const error = String(data.error ?? "");
      const explanation = String(data.explanation ?? "");

      if (output) {
        setCodeResult(output);
      } else if (error) {
        setCodeResult(
          `【编译/运行错误】\n${error}${explanation ? "\n\n说明：" + explanation : ""}`,
        );
      } else {
        setCodeResult(
          `执行完成，无标准输出。\n\n后端说明：${explanation || "程序已正常结束，但未产生 stdout。"}`,
        );
      }
    } catch (e: unknown) {
      setCodeResult("执行出错：" + extractApiError(e, "执行失败"));
    } finally {
      setCodeRunning(false);
    }
  };

  const handleExplainCode = async () => {
    if (!codeContent.trim()) {
      message.warning("请先编写代码");
      return;
    }
    setCodeExplaining(true);
    setCodeExplanation("");
    try {
      const res = await tutorApi.ask({
        student_id: studentId,
        question: codeContent,
        context: { language: codeLanguage },
        task: "explain_code",
        session_id: `${studentId}_explain`,
      });
      setCodeExplanation(res.data?.response || "暂无解释");
      setExplainModalOpen(true);
    } catch (e: unknown) {
      message.error(extractApiError(e, "解释失败"));
    } finally {
      setCodeExplaining(false);
    }
  };

  const handleOcrFileChange = async (
    e: React.ChangeEvent<HTMLInputElement>,
  ) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (!file.type.startsWith("image/")) {
      message.warning("请上传图片文件");
      return;
    }
    const reader = new FileReader();
    reader.onload = (ev) => {
      const result = ev.target?.result as string;
      if (result) setOcrImage(result);
    };
    reader.readAsDataURL(file);
    e.target.value = "";
  };

  const handleOcrRecognize = async () => {
    if (!ocrImage) {
      message.warning("请先上传图片");
      return;
    }
    setOcrLoading(true);
    try {
      const res = await ocrApi.recognize({
        image_base64: ocrImage,
        prompt:
          "请识别这张图片中的所有文字内容，保持原有的段落和格式。如果是数学公式，请用 LaTeX 表示。如果是错题，请标注题号和答案区域。",
      });
      setOcrResult(res.data?.text || "");
      message.success("识别成功");
    } catch (e: unknown) {
      message.error(extractApiError(e, "识别失败"));
    } finally {
      setOcrLoading(false);
    }
  };

  const handleOcrToNotes = () => {
    if (!ocrResult) return;
    setNotes((prev) => prev + "\n\n【OCR识别结果】\n" + ocrResult);
    setOcrModalOpen(false);
    setOcrImage("");
    setOcrResult("");
    message.success("已导入笔记");
  };

  const handleMarkComplete = async () => {
    if (!activeKey) {
      message.warning("请先选择一个知识点");
      return;
    }
    setMarkingComplete(true);
    try {
      const elapsedSec = getElapsed();
      await learningDataApi.record({
        student_id: studentId,
        kp_id: activeKey,
        action: "complete",
        duration: elapsedSec,
        progress: 1.0,
      });
      // 同步更新目录打勾状态
      setCourseMenu((prev) =>
        prev.map((ch) => ({
          ...ch,
          children:
            ch.children?.map((item) =>
              item.key === activeKey ? { ...item, completed: true } : item,
            ) || [],
        })),
      );
      message.success("已标记完成");
    } catch (e: unknown) {
      message.error(extractApiError(e, "标记失败"));
    } finally {
      setMarkingComplete(false);
    }
  };

  const handleGenerateImage = async () => {
    if (!imagePrompt.trim()) {
      message.warning("请输入图片描述");
      return;
    }
    setImageLoading(true);
    try {
      const res = await imageApi.generate({ prompt: imagePrompt });
      // 功能未配置
      if (res.data?.status === "not_configured") {
        message.warning(res.data?.message || "文生图功能未配置");
        setImageLoading(false);
        return;
      }
      // 同步直接返回图片
      if (res.data?.image_urls && res.data.image_urls.length > 0) {
        setGeneratedImage(res.data.image_urls[0]);
        message.success("图片生成成功");
        return;
      }
      // 异步任务：轮询查询结果
      const taskId = res.data?.task_id;
      if (res.data?.status === "submitted" && taskId) {
        message.info("图片生成中，请稍候…");
        const poll = async (attempt: number): Promise<void> => {
          if (attempt <= 0 || !mountedRef.current) {
            if (mountedRef.current)
              message.error("图片生成超时，请稍后手动刷新");
            throw new Error("timeout");
          }
          await new Promise((resolve) => setTimeout(resolve, 2000));
          if (!mountedRef.current) throw new Error("unmounted");
          const pollRes = await imageApi.getResult(taskId);
          if (
            pollRes.data?.status === "done" &&
            pollRes.data?.image_urls &&
            pollRes.data.image_urls.length > 0
          ) {
            setGeneratedImage(pollRes.data.image_urls[0]);
            message.success("图片生成成功");
            return;
          }
          if (
            pollRes.data?.status === "failed" ||
            pollRes.data?.status === "error"
          ) {
            message.error(
              "图片生成失败：" + (pollRes.data?.message || "未知错误"),
            );
            throw new Error("failed");
          }
          return poll(attempt - 1);
        };
        await poll(30);
      } else {
        message.info("图片生成中，请稍后查看");
      }
    } catch (e: unknown) {
      const errMsg = extractApiError(e, "生成失败");
      message.error(errMsg);
    } finally {
      setImageLoading(false);
    }
  };

  return (
    <div className="relative space-y-5">
      {/* 背景光晕（知识空间风格） */}
      <div className="absolute -top-10 -right-16 w-72 h-72 rounded-full bg-indigo-100/60 blur-3xl pointer-events-none" />
      <div className="absolute top-1/3 -left-16 w-64 h-64 rounded-full bg-sky-100/60 blur-3xl pointer-events-none" />
      {/* FSRS 记忆调度提醒（玻璃卡） */}
      {showReviewBanner && weakReviewTopics.length > 0 && (
        <div className="relative overflow-hidden rounded-2xl px-5 py-3 flex items-center gap-3"
          style={{
            background: "rgba(255,255,255,0.92)",
            border: "1px solid rgba(245,158,11,0.3)",
            boxShadow: "0 8px 28px rgba(245,158,11,0.12)",
            backdropFilter: "blur(10px)",
          }}>
          <div className="relative w-9 h-9 rounded-xl flex items-center justify-center text-base" style={{ background: "#f59e0b1c", color: "#d97706" }}>
            <ReloadOutlined />
          </div>
          <div className="flex-1 relative">
            <div className="text-sm font-medium text-amber-800 flex items-center gap-2">
              <span className="text-[9px] px-1.5 py-0.5 rounded-full font-semibold" style={{ background: "#f59e0b1c", color: "#d97706", border: "1px solid #f59e0b33" }}>
                🧠 FSRS 记忆调度
              </span>
              有 {weakReviewTopics.length} 个知识点到期复习
            </div>
            <div className="text-xs text-amber-600 mt-0.5">
              {weakReviewTopics.join("、")}
            </div>
          </div>
          <Button
            size="small"
            className="rounded-lg border-amber-200 text-amber-700"
            onClick={() => setShowReviewBanner(false)}
          >
            稍后提醒
          </Button>
          <Button
            size="small"
            type="primary"
            className="rounded-lg bg-amber-500 border-amber-500"
            onClick={() => navigate("/learning-path")}
          >
            <ReloadOutlined /> 去复习
          </Button>
        </div>
      )}

      {/* 顶部标题栏 */}
      <Card
        className="border border-slate-100 rounded-2xl"
        styles={{ body: { padding: "20px 24px" } }}
      >
        <div className="flex items-center justify-between flex-wrap gap-3">
          <Space>
            <Tooltip title="返回学习路径">
              <Button
                className="rounded-lg border-slate-200"
                icon={
                  <ArrowRightOutlined style={{ transform: "rotate(180deg)" }} />
                }
                onClick={() => navigate("/learning-path")}
              />
            </Tooltip>
            <div className="w-10 h-10 rounded-xl bg-slate-900 flex items-center justify-center text-white">
              <ReadOutlined />
            </div>
            <div>
              <Typography.Title level={4} className="!m-0 text-slate-800">
                {currentTopic}
              </Typography.Title>
              <Typography.Text className="text-slate-400 text-xs">
                {currentSubject || "学习资源"}
              </Typography.Text>
            </div>
          </Space>
          <Space>
            <Tooltip title="OCR 拍照上传纸质笔记或错题">
              <Button
                className="rounded-lg border-slate-200"
                icon={<CameraOutlined />}
                onClick={() => setOcrModalOpen(true)}
              >
                OCR识图
              </Button>
            </Tooltip>
            <Tooltip title="AI智能生成学习PPT">
              <Button
                className="rounded-lg border-slate-200"
                icon={<FileTextOutlined />}
                onClick={() => setPptModalOpen(true)}
              >
                生成PPT
              </Button>
            </Tooltip>
            <Tooltip title={ragActive ? "RAG 检索增强已启用" : "RAG 已关闭"}>
              <Tag
                className={`rounded-full border-0 text-xs cursor-pointer ${ragActive ? "bg-blue-50 text-blue-700" : "bg-slate-100 text-slate-600"}`}
                onClick={() => setRagActive(!ragActive)}
              >
                <ApartmentOutlined /> {ragActive ? "RAG 检索中" : "RAG 关闭"}
              </Tag>
            </Tooltip>
            <Button
              type="primary"
              className="rounded-lg bg-primary"
              onClick={handleMarkComplete}
              loading={markingComplete}
            >
              <CheckCircleOutlined /> 标记完成
            </Button>
          </Space>
        </div>
      </Card>

      <div className="flex gap-5 items-start">
        {/* 左侧列 —— 目录 + 线索栏（加宽填充） */}
        <div className="hidden xl:flex flex-shrink-0 w-80 sticky top-16 self-start z-10 flex-col gap-4 h-[calc(100vh-5rem)]">
          {/* 课程目录 */}
          <Card
            className="border border-slate-100 rounded-2xl max-h-[calc(100vh-24rem)] overflow-y-auto"
            styles={{ body: { padding: "20px 16px" } }}
          >
            <Typography.Text className="font-semibold text-slate-800 block mb-4 text-sm">
              课程目录
            </Typography.Text>
            <Spin spinning={menuLoading}>
              <Collapse
                defaultActiveKey={courseMenu.map((c) => c.key)}
                ghost
                expandIconPosition="end"
                items={useMemo(
                  () =>
                    courseMenu.map((chapter) => ({
                      key: chapter.key,
                      label: (
                        <span className="font-medium text-slate-700 text-sm">
                          {chapter.label}
                        </span>
                      ),
                      children: (
                        <div className="flex flex-col gap-1">
                          {chapter.children?.map((item) => (
                            <Button
                              key={item.key}
                              type={activeKey === item.key ? "primary" : "text"}
                              className={`justify-start text-left rounded-lg text-sm transition-all ${
                                activeKey === item.key
                                  ? "bg-primary"
                                  : "text-slate-600 hover:bg-slate-50"
                              }`}
                              icon={
                                item.completed ? (
                                  <CheckCircleOutlined className="text-success text-xs" />
                                ) : (
                                  <FileTextOutlined
                                    className={
                                      activeKey === item.key
                                        ? "text-white text-xs"
                                        : "text-slate-400 text-xs"
                                    }
                                  />
                                )
                              }
                              onClick={() => setActiveKey(item.key)}
                            >
                              {item.label}
                            </Button>
                          ))}
                        </div>
                      ),
                    })),
                  [courseMenu, activeKey],
                )}
              />
            </Spin>
          </Card>

          {/* 线索栏 Cues —— 独立模块，填充剩余空间 */}
          <Card
            className="border border-slate-100 rounded-2xl flex-1 flex flex-col"
            styles={{
              body: {
                padding: "16px",
                display: "flex",
                flexDirection: "column",
                height: "100%",
              },
            }}
          >
            <Typography.Text className="font-semibold text-slate-800 block mb-2 text-sm">
              线索栏 / Cues
            </Typography.Text>
            <Input.TextArea
              value={cornellNotes.cues}
              onChange={(e) => {
                const text = e.target.value;
                setCornellNotes((prev) => ({ ...prev, cues: text }));
                if (
                  (window as unknown as Record<string, unknown>)._cuesDebounce
                ) {
                  clearTimeout(
                    (window as unknown as Record<string, unknown>)
                      ._cuesDebounce as ReturnType<typeof setTimeout>,
                  );
                }
                (window as unknown as Record<string, unknown>)._cuesDebounce =
                  setTimeout(() => {
                    if (!text.trim() || !studentId) return;
                    logReflectionApi
                      .createReflection({
                        student_id: studentId,
                        date: new Date().toISOString().slice(0, 10),
                        content: text.trim(),
                        tags: ["cues", `kp_${activeKey}`],
                      })
                      .catch(() => {});
                    profileApi
                      .analyzeConversation(
                        studentId,
                        `学生在学习${currentTopic || "当前知识点"}时记录的线索/疑问：${text.trim()}`,
                      )
                      .catch(() => {});
                  }, 1500);
              }}
              placeholder="记录关键词、疑问或线索..."
              className="rounded-lg bg-slate-50 border-slate-200 text-sm flex-1"
              style={{ resize: "none" }}
            />
            <Typography.Text className="text-[10px] text-slate-400 block mt-1">
              自动保存，同步到画像师
            </Typography.Text>
          </Card>
        </div>

        {/* 中间主内容区 */}
        <div className="flex-1 min-w-0 space-y-5">
          {/* 图文讲义 */}
          <Card
            className="border border-slate-100 rounded-2xl"
            title={
              <Space>
                <FileTextOutlined className="text-primary" />
                <span className="font-semibold text-slate-800">图文讲义</span>
                {multiAgentStep !== "done" && (
                  <Tag className="rounded-full border-0 bg-blue-50 text-blue-600 text-xs">
                    <ThunderboltOutlined className="mr-1" />
                    {multiAgentStep === "planner"
                      ? "Planner 规划中"
                      : multiAgentStep === "worker"
                        ? "Worker 生成中"
                        : "Critic 审核中"}
                  </Tag>
                )}
              </Space>
            }
            extra={
              <Space>
                <Tag className="rounded-full border-0 bg-slate-100 text-slate-600 text-xs">
                  {currentTopic}
                </Tag>
                <Space.Compact className="rounded-lg overflow-hidden">
                  <Button
                    size="small"
                    icon={<LikeOutlined />}
                    className={
                      resourceFeedback[currentTopic] === "good"
                        ? "text-emerald-600"
                        : ""
                    }
                    onClick={() => {
                      setResourceFeedback((prev) => ({
                        ...prev,
                        [currentTopic]: "good",
                      }));
                      learningDataApi
                        .submitFeedback({
                          student_id: studentId,
                          kp_id: activeKey,
                          rating: "good",
                        })
                        .catch(() => {});
                    }}
                  />
                  <Button
                    size="small"
                    icon={<DislikeOutlined />}
                    className={
                      resourceFeedback[currentTopic] === "bad"
                        ? "text-red-500"
                        : ""
                    }
                    onClick={() => {
                      setResourceFeedback((prev) => ({
                        ...prev,
                        [currentTopic]: "bad",
                      }));
                      learningDataApi
                        .submitFeedback({
                          student_id: studentId,
                          kp_id: activeKey,
                          rating: "bad",
                        })
                        .catch(() => {});
                    }}
                  />
                </Space.Compact>
              </Space>
            }
            styles={{ body: { padding: "40px" } }}
          >
            <Spin spinning={resLoading}>
              <div
                onClick={(e) => {
                  const target = e.target as HTMLElement;
                  const link = target.closest(
                    ".course-nav-link",
                  ) as HTMLElement;
                  if (!link) return;
                  const courseId = link.dataset.courseId;
                  if (!courseId) return;
                  e.preventDefault();
                  // 反向查找对应的 kp_id（courseId 可能是 URL 编码的）
                  const decodedCourseId = decodeURIComponent(courseId);
                  const reverseMap = Object.entries(stm32KpCourseMap);
                  const match = reverseMap.find(
                    ([, cid]) => cid === decodedCourseId,
                  );
                  if (match) {
                    setActiveKey(match[0]);
                  }
                }}
              >
                <MarkdownViewer content={docContent} />
              </div>
            </Spin>
            {resourceFeedback[currentTopic] === "bad" && (
              <div className="mt-4 p-3 rounded-xl bg-red-50 border border-red-100 text-xs text-red-600">
                已记录负反馈，系统将自动优化该资源生成的 Prompt。
              </div>
            )}
          </Card>

          {/* 下方辅助功能区 */}
          <Card
            className="border border-slate-100 rounded-2xl"
            styles={{ body: { padding: "20px 24px" } }}
          >
            <Tabs
              activeKey={bottomTab}
              onChange={setBottomTab}
              items={[
                {
                  key: "code",
                  label: (
                    <span className="flex items-center gap-1.5 text-sm">
                      <CodeOutlined /> 代码编辑器
                    </span>
                  ),
                  children: (
                    <div className="space-y-3">
                      <div className="bg-slate-900 rounded-xl p-5 font-mono text-sm text-slate-200 relative">
                        <div className="flex items-center justify-between mb-4">
                          <div className="flex items-center gap-3">
                            <div className="flex gap-2">
                              <div className="w-3 h-3 rounded-full bg-red-400" />
                              <div className="w-3 h-3 rounded-full bg-yellow-400" />
                              <div className="w-3 h-3 rounded-full bg-green-400" />
                            </div>
                            <Tag
                              className={`cursor-pointer rounded-full text-xs ${codeLanguage === "Python" ? "bg-blue-500 text-white border-blue-500" : "bg-slate-700 text-slate-300 border-slate-600"}`}
                              onClick={() => {
                                setCodeLanguage("Python");
                                setCodeResult("");
                              }}
                            >
                              Python
                            </Tag>
                            <Tag
                              className={`cursor-pointer rounded-full text-xs ${codeLanguage === "C" ? "bg-blue-500 text-white border-blue-500" : "bg-slate-700 text-slate-300 border-slate-600"}`}
                              onClick={() => {
                                setCodeLanguage("C");
                                setCodeResult("");
                              }}
                            >
                              C
                            </Tag>
                          </div>
                          <Tooltip title="复制代码">
                            <Button
                              type="text"
                              size="small"
                              icon={
                                <CopyOutlined className="text-slate-400 hover:text-white" />
                              }
                              onClick={copyCode}
                            />
                          </Tooltip>
                        </div>
                        <CodeEditor
                          value={codeContent}
                          onChange={setCodeContent}
                          language={codeLanguage}
                          height="320px"
                        />
                      </div>
                      <Space>
                        <Button
                          type="primary"
                          className="rounded-lg bg-primary"
                          onClick={handleRunCode}
                          loading={codeRunning}
                        >
                          <ArrowRightOutlined /> 运行{codeLanguage}代码
                        </Button>
                        <Button
                          className="rounded-lg border-indigo-200 text-indigo-600"
                          onClick={handleExplainCode}
                          loading={codeExplaining}
                        >
                          <BulbOutlined /> 解释代码
                        </Button>
                      </Space>
                      {codeResult && (
                        <div className="mt-2">
                          <div className="flex items-center justify-between mb-1">
                            <span className="text-slate-400 text-xs">
                              运行结果
                            </span>
                            <Button
                              type="link"
                              size="small"
                              className="text-xs text-primary"
                              onClick={() => {
                                navigator.clipboard
                                  .writeText(codeResult)
                                  .then(() => message.success("结果已复制"));
                              }}
                            >
                              复制结果
                            </Button>
                          </div>
                          <Input.TextArea
                            value={codeResult}
                            readOnly
                            rows={8}
                            className="bg-slate-800 text-green-400 border-slate-700 font-mono text-sm !shadow-none !outline-none focus:!border-slate-700 hover:!border-slate-700"
                            style={{ resize: "vertical", lineHeight: 1.6 }}
                          />
                        </div>
                      )}
                    </div>
                  ),
                },
                {
                  key: "quiz",
                  label: (
                    <span className="flex items-center gap-1.5 text-sm">
                      <BulbOutlined /> 练习题 ({questions.length})
                    </span>
                  ),
                  children: (
                    <div className="space-y-3">
                      {questions.length === 0 && (
                        <Typography.Text className="text-slate-400">
                          暂无练习题
                        </Typography.Text>
                      )}
                      {questions.length > 0 && (
                        <div className="flex items-center justify-between mb-2">
                          <div className="text-sm text-slate-500">
                            已答 {Object.keys(quizSubmitted).length} /{" "}
                            {questions.length} 题
                            {quizScore !== null && (
                              <Tag className="ml-2 rounded-full border-0 bg-primary-50 text-primary text-xs font-bold">
                                得分: {quizScore} 分
                              </Tag>
                            )}
                          </div>
                          {Object.keys(quizSubmitted).length > 0 && (
                            <Button
                              size="small"
                              className="rounded-lg text-xs"
                              onClick={() => {
                                setQuizAnswers({});
                                setQuizSubmitted({});
                                setQuizScore(null);
                              }}
                            >
                              重新作答
                            </Button>
                          )}
                        </div>
                      )}
                      {questions.map((q, idx) => {
                        const submitted = quizSubmitted[q.q_id];
                        const selected = quizAnswers[q.q_id];
                        const isCorrect =
                          submitted && selected === q.correct_answer;
                        return (
                          <Card
                            key={q.q_id}
                            size="small"
                            className={`rounded-xl border-slate-100 ${submitted ? (isCorrect ? "border-emerald-200 bg-emerald-50/30" : "border-red-200 bg-red-50/30") : ""}`}
                          >
                            <div className="flex items-start gap-2 mb-3">
                              <span className="w-6 h-6 rounded-full bg-primary/10 text-primary text-xs font-bold flex items-center justify-center shrink-0 mt-0.5">
                                {idx + 1}
                              </span>
                              <Typography.Text className="font-medium text-slate-800">
                                {q.content}
                              </Typography.Text>
                            </div>
                            {q.options && (
                              <div className="space-y-2 pl-8">
                                {q.options.map((opt) => {
                                  const isSelected = selected === opt.id;
                                  const isCorrectOpt =
                                    opt.id === q.correct_answer;
                                  let optClass =
                                    "px-3 py-2 rounded-lg text-sm border transition-all ";
                                  if (submitted) {
                                    if (isCorrectOpt) {
                                      optClass +=
                                        "bg-emerald-100 border-emerald-300 text-emerald-700";
                                    } else if (isSelected && !isCorrectOpt) {
                                      optClass +=
                                        "bg-red-100 border-red-300 text-red-700";
                                    } else {
                                      optClass +=
                                        "bg-slate-50 border-slate-100 text-slate-400";
                                    }
                                  } else {
                                    optClass += isSelected
                                      ? "bg-primary-50 border-primary-200 text-primary cursor-pointer"
                                      : "bg-slate-50 border-slate-100 text-slate-700 hover:bg-blue-50 hover:border-blue-200 hover:text-primary cursor-pointer";
                                  }
                                  return (
                                    <div
                                      key={opt.id}
                                      className={optClass}
                                      onClick={() => {
                                        if (!submitted)
                                          setQuizAnswers((prev) => ({
                                            ...prev,
                                            [q.q_id]: opt.id,
                                          }));
                                      }}
                                    >
                                      <div className="flex items-center gap-2">
                                        <span
                                          className={`w-5 h-5 rounded-full flex items-center justify-center text-xs font-bold shrink-0 ${isSelected ? "bg-primary text-white" : "bg-white border border-slate-300 text-slate-500"}`}
                                        >
                                          {opt.id}
                                        </span>
                                        <span>{opt.text}</span>
                                        {submitted && isCorrectOpt && (
                                          <CheckCircleOutlined className="text-emerald-500 ml-auto" />
                                        )}
                                        {submitted &&
                                          isSelected &&
                                          !isCorrectOpt && (
                                            <CloseCircleOutlined className="text-red-500 ml-auto" />
                                          )}
                                      </div>
                                    </div>
                                  );
                                })}
                              </div>
                            )}
                            {submitted && (
                              <div className="mt-3 pl-8">
                                <div
                                  className={`text-xs font-medium mb-1 ${isCorrect ? "text-emerald-600" : "text-red-600"}`}
                                >
                                  {isCorrect
                                    ? "回答正确！"
                                    : `回答错误，正确答案是 ${q.correct_answer}`}
                                </div>
                                <div className="text-xs text-slate-500 bg-white/60 rounded-lg p-2 border border-slate-100">
                                  <span className="font-medium text-slate-600">
                                    解析：
                                  </span>
                                  {q.explanation}
                                </div>
                              </div>
                            )}
                            {!submitted && selected && (
                              <div className="mt-3 pl-8">
                                <Button
                                  type="primary"
                                  size="small"
                                  className="rounded-lg bg-primary text-xs"
                                  loading={quizSubmitting}
                                  onClick={() => {
                                    setQuizSubmitted((prev) => ({
                                      ...prev,
                                      [q.q_id]: true,
                                    }));
                                    // 自动计算总分
                                    const newSubmitted = {
                                      ...quizSubmitted,
                                      [q.q_id]: true,
                                    };
                                    const newAnswers = {
                                      ...quizAnswers,
                                      [q.q_id]: selected,
                                    };
                                    const total = questions.reduce(
                                      (sum, qq) => {
                                        if (
                                          newSubmitted[qq.q_id] &&
                                          newAnswers[qq.q_id] ===
                                            qq.correct_answer
                                        )
                                          return sum + 1;
                                        return sum;
                                      },
                                      0,
                                    );
                                    setQuizScore(total);
                                  }}
                                >
                                  提交答案
                                </Button>
                              </div>
                            )}
                          </Card>
                        );
                      })}
                    </div>
                  ),
                },
                {
                  key: "mindmap",
                  label: (
                    <span className="flex items-center gap-1.5 text-sm">
                      <NodeIndexOutlined /> 思维导图
                    </span>
                  ),
                  children: (
                    <div className="rounded-xl bg-white border border-slate-100 p-2">
                      <MindmapView content={mindmapContent} />
                    </div>
                  ),
                },
                {
                  key: "visualizer",
                  label: (
                    <span className="flex items-center gap-1.5 text-sm">
                      <ThunderboltOutlined /> 算法可视化
                    </span>
                  ),
                  children: <AlgorithmVisualizer />,
                },
                ...(storeCurrentSubject === "STM32嵌入式"
                  ? [
                      {
                        key: "wiring",
                        label: (
                          <span className="flex items-center gap-1.5 text-sm">
                            <PictureOutlined /> 接线图
                          </span>
                        ),
                        children: (
                          <div className="space-y-4">
                            {(() => {
                              // 按当前知识点过滤接线图
                              const chapters =
                                stm32WiringChapterMap[activeKey] || [];
                              const filtered =
                                chapters.length > 0
                                  ? stm32WiringDiagrams.filter((d) =>
                                      chapters.some((ch) =>
                                        d.filename.startsWith(`${ch}-`),
                                      ),
                                    )
                                  : stm32WiringDiagrams;

                              if (filtered.length === 0) {
                                return (
                                  <Typography.Text className="text-slate-400">
                                    暂无接线图
                                  </Typography.Text>
                                );
                              }

                              return (
                                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                                  {filtered.map((d) => (
                                    <div
                                      key={d.filename}
                                      className="rounded-xl border border-slate-200 overflow-hidden hover:shadow-md transition-all cursor-pointer"
                                      onClick={() =>
                                        window.open(
                                          `/api/v1/stm32/wiring/${d.filename}`,
                                          "_blank",
                                        )
                                      }
                                    >
                                      <img
                                        src={`/api/v1/stm32/wiring/${d.filename}`}
                                        alt={d.title}
                                        className="w-full h-40 object-cover bg-slate-100"
                                        loading="lazy"
                                        onError={(e) => {
                                          (e.target as HTMLImageElement).src =
                                            "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='160'%3E%3Crect fill='%23f1f5f9' width='200' height='160'/%3E%3Ctext x='100' y='84' text-anchor='middle' fill='%2394a3b8' font-size='13'%3E图片加载失败%3C/text%3E%3C/svg%3E";
                                        }}
                                      />
                                      <div className="p-2 text-xs text-slate-600 text-center truncate">
                                        {d.title}
                                      </div>
                                    </div>
                                  ))}
                                </div>
                              );
                            })()}
                          </div>
                        ),
                      },
                      {
                        key: "projects",
                        label: (
                          <span className="flex items-center gap-1.5 text-sm">
                            <CodeOutlined /> 代码工程
                          </span>
                        ),
                        children: (
                          <div className="space-y-3">
                            {(() => {
                              // 按当前知识点过滤代码工程
                              const chapters =
                                stm32WiringChapterMap[activeKey] || [];
                              const filtered =
                                chapters.length > 0
                                  ? stm32Projects.filter((p) =>
                                      chapters.some((ch) =>
                                        p.dirname.startsWith(`${ch}-`),
                                      ),
                                    )
                                  : stm32Projects;

                              if (filtered.length === 0) {
                                return (
                                  <Typography.Text className="text-slate-400">
                                    暂无代码工程
                                  </Typography.Text>
                                );
                              }

                              return filtered.map((p) => (
                                <Card
                                  key={p.dirname}
                                  size="small"
                                  className="rounded-xl border-slate-100 hover:border-primary/30 transition-all cursor-pointer"
                                  title={
                                    <span className="text-sm font-medium text-slate-700">
                                      {p.title}
                                    </span>
                                  }
                                  extra={
                                    <Tag className="rounded-full border-0 bg-slate-100 text-slate-500 text-xs">
                                      {p.file_count} 个文件
                                    </Tag>
                                  }
                                  onClick={async () => {
                                    setProjectFilesLoading(true);
                                    try {
                                      const res =
                                        await stm32Api.getProjectFiles(
                                          p.dirname,
                                        );
                                      setSelectedProject({
                                        dirname: p.dirname,
                                        title: p.title,
                                        files: res.data?.data?.files || [],
                                      });
                                    } catch {
                                      message.error("加载工程文件失败");
                                    } finally {
                                      setProjectFilesLoading(false);
                                    }
                                  }}
                                >
                                  <Typography.Text className="text-xs text-slate-400">
                                    工程目录：{p.dirname}
                                  </Typography.Text>
                                </Card>
                              ));
                            })()}
                          </div>
                        ),
                      },
                      {
                        key: "experiments",
                        label: (
                          <span className="flex items-center gap-1.5 text-sm">
                            <ExperimentOutlined /> 实验实训
                          </span>
                        ),
                        children: <Stm32Experiments kpId={activeKey} />,
                      },
                    ]
                  : []),
              ]}
            />
          </Card>
        </div>

        {/* 右侧 AI 辅导 */}
        {chatOpen && (
          <div className="hidden xl:block w-64 flex-shrink-0 sticky top-16 self-start h-[calc(100vh-5rem)]">
            <Card
              className="border border-slate-100 rounded-2xl h-full flex flex-col"
              styles={{
                body: {
                  padding: "16px",
                  height: "100%",
                  display: "flex",
                  flexDirection: "column",
                  overflow: "hidden",
                },
              }}
            >
              <ChatPanel
                messages={messages}
                loading={loading}
                onSend={handleSend}
                title="AI 辅导助手"
                subtitle="苏格拉底式教学"
                placeholder="输入问题..."
                showAvatars={false}
                extraHeader={
                  <Button
                    type="text"
                    size="small"
                    icon={<MenuFoldOutlined className="text-slate-400" />}
                    onClick={() => setChatOpen(false)}
                  />
                }
              />
            </Card>
          </div>
        )}
      </div>

      {/* OCR 拍照上传弹窗 */}
      <Modal
        title={
          <span className="font-semibold text-slate-800">OCR 拍照上传</span>
        }
        open={ocrModalOpen}
        onCancel={() => {
          setOcrModalOpen(false);
          setOcrImage("");
          setOcrResult("");
        }}
        footer={null}
        width={560}
        className="rounded-2xl"
      >
        <div className="space-y-4 py-2">
          {!ocrImage ? (
            <label className="block p-6 rounded-xl bg-slate-50 border border-dashed border-slate-300 text-center cursor-pointer hover:border-primary transition-all">
              <CameraOutlined className="text-3xl text-slate-300 mb-2" />
              <div className="text-sm text-slate-600">
                点击上传纸质笔记 / 错题照片
              </div>
              <div className="text-xs text-slate-400 mt-1">
                支持 JPG、PNG，基于大模型 Vision 识别
              </div>
              <input
                type="file"
                accept="image/*"
                className="hidden"
                onChange={handleOcrFileChange}
              />
            </label>
          ) : (
            <div className="space-y-3">
              <img
                src={ocrImage}
                alt="ocr"
                className="w-full max-h-64 object-contain rounded-lg border border-slate-200"
              />
              <div className="flex gap-2">
                <Button
                  loading={ocrLoading}
                  type="primary"
                  className="bg-primary rounded-lg flex-1"
                  onClick={handleOcrRecognize}
                >
                  {ocrLoading ? "识别中..." : "开始识别"}
                </Button>
                <Button
                  className="rounded-lg"
                  onClick={() => {
                    setOcrImage("");
                    setOcrResult("");
                  }}
                >
                  重新上传
                </Button>
              </div>
            </div>
          )}

          {ocrResult && (
            <div className="space-y-2">
              <div className="text-sm font-medium text-slate-700">识别结果</div>
              <div className="p-3 rounded-lg bg-slate-50 border border-slate-200 text-sm text-slate-700 whitespace-pre-wrap max-h-48 overflow-y-auto">
                {ocrResult}
              </div>
              <Button
                type="primary"
                className="bg-primary rounded-lg w-full"
                onClick={handleOcrToNotes}
              >
                导入笔记
              </Button>
            </div>
          )}

          <div className="flex items-center gap-2 text-xs text-slate-400">
            <SafetyOutlined />
            <span>端云协同：图片通过 HTTPS 上传，识别结果本地展示</span>
          </div>
        </div>
      </Modal>

      {/* 代码解释弹窗 */}
      <Modal
        title={
          <span className="font-semibold text-slate-800">
            <BulbOutlined className="mr-2 text-indigo-500" />
            AI 代码解释
          </span>
        }
        open={explainModalOpen}
        onCancel={() => setExplainModalOpen(false)}
        footer={null}
        width={640}
        className="rounded-2xl"
      >
        <div className="p-2 text-sm text-slate-700 leading-relaxed whitespace-pre-wrap max-h-[60vh] overflow-y-auto">
          {codeExplanation}
        </div>
      </Modal>

      {/* 代码工程文件列表弹窗 */}
      <Modal
        title={
          <span className="text-sm font-semibold">
            {selectedProject?.title || "代码工程"}
          </span>
        }
        open={!!selectedProject}
        onCancel={() => setSelectedProject(null)}
        footer={null}
        width={560}
        className="rounded-2xl"
      >
        {projectFilesLoading ? (
          <div className="flex items-center justify-center py-8">
            <Spin />
          </div>
        ) : selectedProject ? (
          <div className="max-h-[60vh] overflow-y-auto">
            <div className="text-xs text-slate-400 mb-3">
              目录：{selectedProject.dirname} · {selectedProject.files.length}{" "}
              个文件
            </div>
            <div className="space-y-1">
              {selectedProject.files.map((f) => (
                <div
                  key={f.path}
                  className="flex items-center gap-2 px-3 py-1.5 rounded-lg hover:bg-slate-50 text-sm"
                >
                  <CodeOutlined className="text-slate-400 text-xs" />
                  <span className="flex-1 text-slate-700 font-mono text-xs truncate">
                    {f.path}
                  </span>
                  <span className="text-slate-400 text-xs whitespace-nowrap">
                    {f.size > 1024
                      ? `${(f.size / 1024).toFixed(1)} KB`
                      : `${f.size} B`}
                  </span>
                </div>
              ))}
            </div>
          </div>
        ) : null}
      </Modal>

      {!chatOpen && (
        <FloatButton
          icon={<MessageOutlined />}
          type="primary"
          tooltip="打开 AI 辅导"
          onClick={() => setChatOpen(true)}
          className="right-6 bottom-6"
        />
      )}

      {/* PPT 生成器 */}
      <PPTGenerator
        open={pptModalOpen}
        onClose={() => setPptModalOpen(false)}
        defaultTopic={currentTopic}
        defaultSubject={currentSubject}
      />
    </div>
  );
};

export default ResourceCenter;
