import axios from "axios";
import type { AxiosResponse } from "axios";
import { useAppStore } from "../store";
import type {
  StudentProfile,
  ProfileUpdateRequest,
  ProfileInitRequest,
  ProfileSummary,
  LearningPath,
  PathGenerationRequest,
  PathAdjustmentRequest,
  CurrentPathResponse,
  ResourceGenerationRequest,
  ResourceGenerationResponse,
  DocumentGenerationRequest,
  DocumentGenerationResponse,
  QuestionsGenerationRequest,
  QuestionsGenerationResponse,
  MindmapGenerationRequest,
  MindmapGenerationResponse,
  CodeGenerationRequest,
  CodeGenerationResponse,
  TutorRequest,
  TutorResponse,
  TutorSessionHistoryResponse,
} from "../types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api/v1";

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
});

// 请求去重：相同 key 的并发请求只保留最新一个
const pendingControllers = new Map<string, AbortController>();

/**
 * 创建带去重的请求函数
 * @param key 去重 key（如 "GET:/profile/123"）
 * @param fn 实际请求函数，接收 AbortSignal
 */
export function withDedup<T>(
  key: string,
  fn: (signal: AbortSignal) => Promise<T>,
): Promise<T> {
  const existing = pendingControllers.get(key);
  if (existing) existing.abort();
  const controller = new AbortController();
  pendingControllers.set(key, controller);
  return fn(controller.signal).finally(() => {
    if (pendingControllers.get(key) === controller) {
      pendingControllers.delete(key);
    }
  });
}

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    const token = useAppStore.getState().token;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error),
);

// 响应拦截器
api.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error) => {
    // 网络错误 / 离线状态
    if (!error.response) {
      if (error.code === "ERR_NETWORK" || error.code === "ERR_FAILED") {
        return Promise.reject(new Error("网络连接失败，请检查网络状态"));
      }
      if (error.code === "ECONNABORTED") {
        return Promise.reject(new Error("请求超时，请稍后再试"));
      }
      return Promise.reject(new Error("网络异常，请稍后再试"));
    }
    const status = error.response?.status;
    const data = error.response?.data;
    const message =
      data?.message || data?.detail || error.message || "请求失败";
    if (status === 401) {
      useAppStore.getState().logout();
      window.dispatchEvent(new CustomEvent("auth:expired"));
      return Promise.reject(new Error("登录已过期，请重新登录"));
    }
    if (status === 403) {
      return Promise.reject(new Error("没有权限执行此操作"));
    }
    if (status === 404) {
      return Promise.reject(new Error("请求的资源不存在"));
    }
    if (status === 429) {
      return Promise.reject(new Error("请求过于频繁，请稍后再试"));
    }
    if (status === 503) {
      return Promise.reject(new Error("服务暂时不可用，请稍后再试"));
    }
    return Promise.reject(new Error(message));
  },
);

// ---------- 学生画像 ----------
export const profileApi = {
  get: (studentId: string) =>
    api.get<{ status: string; data: StudentProfile }>(`/profile/${studentId}`),
  update: (studentId: string, data: ProfileUpdateRequest) =>
    api.post<{
      status: string;
      message: string;
      data: StudentProfile;
      llm_analysis?: Record<string, unknown>;
    }>(`/profile/${studentId}/update`, data),
  summary: (studentId: string) =>
    api.get<{ status: string; summary: ProfileSummary }>(
      `/profile/${studentId}/summary`,
    ),
  initialize: (studentId: string, data: ProfileInitRequest) =>
    api.post<{ status: string; message: string; data: StudentProfile }>(
      `/profile/${studentId}/initialize`,
      data,
    ),
  analyzeConversation: (studentId: string, conversation: string) =>
    api.post<{ status: string; message: string; data: StudentProfile }>(
      `/profile/${studentId}/analyze-conversation`,
      { conversation },
    ),
  getRetention: (studentId: string) =>
    api.get<{
      status: string;
      data: Array<{
        topic: string;
        retention: number;
        nextReview: string;
      }>;
      message?: string;
    }>(`/profile/${studentId}/retention`),
};

// ---------- 资源生成 ----------
export interface CodeExecuteRequest {
  code: string;
  language?: string;
  kp_id?: string;
}

export interface CodeExecuteResponse {
  status: string;
  output: string;
  error: string;
  explanation: string;
}

export const resourceApi = {
  generate: (data: ResourceGenerationRequest) =>
    api.post<ResourceGenerationResponse>("/resource/generate", data),
  getTask: (taskId: string) =>
    api.get<ResourceGenerationResponse>(`/resource/task/${taskId}`),
  generateDocument: (data: DocumentGenerationRequest) =>
    api.post<DocumentGenerationResponse>("/resource/document/generate", data),
  generateQuestions: (data: QuestionsGenerationRequest) =>
    api.post<QuestionsGenerationResponse>("/resource/questions/generate", data),
  generateMindmap: (data: MindmapGenerationRequest) =>
    api.post<MindmapGenerationResponse>("/resource/mindmap/generate", data),
  generateCode: (data: CodeGenerationRequest) =>
    api.post<CodeGenerationResponse>("/resource/code/generate", data),
  executeCode: (data: CodeExecuteRequest) =>
    api.post<CodeExecuteResponse>("/resource/code/execute", data),
};

// ---------- 学习路径 ----------
export const pathApi = {
  generate: (data: PathGenerationRequest) =>
    api.post<{ status: string; data: LearningPath }>(
      "/learning-path/generate",
      data,
    ),
  current: (studentId: string, subject?: string) =>
    api.get<CurrentPathResponse>(
      `/learning-path/${studentId}/current`,
      subject ? { params: { subject } } : undefined,
    ),
  adjust: (studentId: string, data: PathAdjustmentRequest) =>
    api.post<{ status: string; message: string; data: LearningPath["path"] }>(
      `/learning-path/${studentId}/adjust`,
      data,
    ),
  dagGenerate: (data: {
    student_id: string;
    target_kp_id: string;
    mastery_map?: Record<string, number>;
  }) =>
    api.post<{ status: string; data: unknown }>(
      "/learning-path/dag/generate",
      data,
    ),
};

// ---------- 智能辅导 ----------
export const tutorApi = {
  ask: (data: TutorRequest) => api.post<TutorResponse>("/tutor/ask", data),
  getHistory: (sessionId: string) =>
    api.get<TutorSessionHistoryResponse>(`/tutor/session/${sessionId}/history`),
  submitFeedback: (
    qaId: string,
    data: { rating: "like" | "dislike"; comment?: string },
  ) => api.post<{ status: string }>(`/tutor/qa-feedback/${qaId}`, data),
};

// ---------- 用户权限 ----------
export interface LoginRequest {
  student_id: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface RegisterRequest {
  student_id: string;
  username: string;
  email?: string;
  password: string;
}

export interface UserInfoResponse {
  status: string;
  data: {
    student_id: string;
    username: string;
    email: string | null;
    role: string;
    is_active: boolean;
  };
}

// ---------- 文生图 ----------
export interface ImageGenerateRequest {
  prompt: string;
  width?: number;
  height?: number;
  seed?: number;
  scale?: number;
  use_pre_llm?: boolean;
}

export interface ImageGenerateResponse {
  task_id: string;
  status: string;
  image_urls?: string[];
  message: string;
}

export interface ImageResultResponse {
  task_id: string;
  status: string;
  image_urls?: string[];
  binary_data?: string[];
  message: string;
}

export const imageApi = {
  generate: (data: ImageGenerateRequest) =>
    api.post<ImageGenerateResponse>("/image/generate", data),
  getResult: (taskId: string) =>
    api.get<ImageResultResponse>(`/image/result/${taskId}`),
  listTasks: () =>
    api.get<{
      status: string;
      tasks: Array<{
        task_id: string;
        status: string;
        image_urls?: string[];
        created_at?: string;
      }>;
    }>("/image/tasks"),
};

export const authApi = {
  login: (data: LoginRequest) => api.post<LoginResponse>("/auth/login", data),
  register: (data: RegisterRequest) =>
    api.post<{ status: string; message: string; student_id: string }>(
      "/auth/register",
      data,
    ),
  me: () => api.get<UserInfoResponse>("/auth/me"),
};

// ---------- Dashboard ----------
export interface DashboardSummaryResponse {
  status: string;
  student_id: string;
  stats: {
    weekly_hours: number;
    streak_days: number;
    achievements: number;
    favorites: number;
    mastered_kps: number;
    today_duration_min: number;
  };
  tasks: Array<{
    task_id: string;
    title: string;
    description?: string;
    progress: number;
    type: string;
  }>;
  recommendations: Array<{
    title: string;
    type: string;
    url?: string | null;
  }>;
  profile_summary: {
    knowledge_base: Record<string, unknown>;
    cognitive_style: Record<string, unknown>;
    weak_areas: string[];
    interest_areas: (
      | string
      | { area?: string; level?: number; [key: string]: unknown }
    )[];
  };
  trend: Array<{ date: string; value: number }>;
  algorithm_analysis?: {
    trend_analysis?: {
      trend_state: string;
      trend_factor: number;
      predicted_mastery_3d: number;
      dimensions: Record<string, number>;
    };
    effect_evaluation?: {
      realtime_metrics: {
        accuracy: number;
        mastery: number;
        improvement_rate: number;
        weakness_concentration: number;
      };
      predictions?: {
        next_score: number;
        potential_loss_points: Array<{
          tag: string;
          frequency: number;
          risk_score: number;
          suggestion: string;
        }>;
        efficiency_trend: string;
      };
      intervention?: {
        priority: string;
        strategies: Array<{
          type: string;
          action: string;
        }>;
      };
      dashboard?: {
        score_history: number[];
        weak_area_distribution: Record<string, number>;
      };
      loss_points?: Array<{ kp_id: string; loss: number }>;
      intervention_strategies?: string[];
    };
  };
}

export const dashboardApi = {
  getSummary: (studentId: string) =>
    api.get<DashboardSummaryResponse>(`/dashboard/${studentId}/summary`),
  getTimeline: (studentId: string) =>
    api.get<{
      status: string;
      data: {
        milestones: Array<{
          date: string;
          type: string;
          title: string;
          icon: string;
          color: string;
        }>;
        daily_curve: Array<{
          date: string;
          minutes: number;
          kp_count: number;
          quiz_count: number;
          avg_score: number;
        }>;
        summary: {
          total_milestones: number;
          mastery_count: number;
          high_score_count: number;
          achievement_count: number;
        };
      };
    }>(`/dashboard/${studentId}/timeline`),
  getActiveDates: (studentId: string, year: number, month: number) =>
    api.get<{ status: string; data: string[] }>(
      `/dashboard/${studentId}/active-dates`,
      { params: { year, month } },
    ),
};

// ---------- Favorites ----------
export interface FavoriteItem {
  id: string;
  title: string;
  resource_type: string;
  url?: string | null;
  meta?: Record<string, unknown>;
  created_at?: string;
}

export const favoritesApi = {
  get: (studentId: string) =>
    api.get<{ status: string; data: FavoriteItem[] }>(
      `/favorites/${studentId}`,
    ),
  add: (
    studentId: string,
    data: {
      title: string;
      resource_type: string;
      url?: string;
      meta?: Record<string, unknown>;
    },
  ) =>
    api.post<{ status: string; id: string }>(`/favorites/${studentId}`, data),
  remove: (studentId: string, favoriteId: string) =>
    api.delete<{ status: string; message: string }>(
      `/favorites/${studentId}/${favoriteId}`,
    ),
};

// ---------- OCR ----------
export interface OCRRequest {
  image_base64: string;
  prompt?: string;
  provider?: string;
}

export interface OCRResponse {
  status: string;
  text: string;
  note_type?: string;
}

export const ocrApi = {
  recognize: (data: OCRRequest) =>
    api.post<OCRResponse>("/ocr/recognize", data),
  upload: (file: File, prompt?: string, provider?: string) => {
    const form = new FormData();
    form.append("file", file);
    if (prompt) form.append("prompt", prompt);
    if (provider) form.append("provider", provider);
    return api.post<OCRResponse>("/ocr/upload", form, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
};

// ---------- Gamification ----------
export const gamificationApi = {
  getPoints: (studentId: string) =>
    api.get<{
      status: string;
      data: {
        total_points: number;
        daily_points: number;
        weekly_points: number;
      };
    }>(`/gamification/${studentId}/points`),
  getAchievements: (studentId: string) =>
    api.get<{
      status: string;
      data: Array<{
        achievement_id: string;
        name: string;
        description?: string;
        icon?: string;
        unlocked_at?: string;
      }>;
    }>(`/gamification/${studentId}/achievements`),
  getTasks: (studentId: string) =>
    api.get<{
      status: string;
      data: Array<{
        task_id: string;
        title: string;
        description?: string;
        task_type: string;
        reward_points: number;
        progress: number;
        completed: boolean;
        completed_at?: string;
      }>;
    }>(`/gamification/${studentId}/tasks`),
  getLeaderboard: (period: string = "weekly", limit: number = 10) =>
    api.get<{
      status: string;
      data: Array<{
        student_id: string;
        username?: string;
        points: number;
        rank: number;
        streak_days?: number;
        level?: number;
      }>;
    }>(`/gamification/leaderboard/${period}`, { params: { limit } }),
};

interface LearningRecordRequest {
  student_id: string;
  kp_id: string;
  action: string;
  duration?: number;
  progress?: number;
  score?: number;
  meta?: Record<string, unknown>;
}

// ---------- 知识树成长系统 ----------
export interface KnowledgeTreeData {
  tree_state: string;
  tree_label: string;
  growth_value: number;
  level: number;
  level_name: string;
  level_info: {
    level: number;
    level_name: string;
    current_xp: number;
    xp_to_next: number;
    total_xp: number;
    xp_per_level: number;
    progress_pct: number;
  };
  total_points: number;
  streak_days: number;
  mastery_rate: number;
  total_hours: number;
  completed_kps: number;
  touched_kps: number;
  total_quizzes: number;
  avg_score: number;
  achievements: number;
  trend_factor: number;
  growth_logs: Array<{
    date: string;
    type: string;
    message: string;
    icon: string;
  }>;
  daily_trend: Array<{
    date: string;
    records: number;
    score: number;
  }>;
}

export const knowledgeTreeApi = {
  getTree: (studentId: string) =>
    api.get<{ status: string; data: KnowledgeTreeData }>(
      `/gamification-tree/${studentId}/tree`,
    ),
};

// ---------- 学习挑战 ----------
export interface ChallengeItem {
  id: string;
  name: string;
  description: string;
  type: string;
  target: number;
  reward: number;
  icon: string;
  difficulty: number;
  progress: number;
  completed: boolean;
  progress_pct: number;
}

export interface ChallengeMapNode {
  node_id: number;
  challenge_id: string;
  name: string;
  difficulty: number;
  completed: boolean;
  x: number;
  y: number;
}

export const challengeApi = {
  getChallenges: (studentId: string) =>
    api.get<{
      status: string;
      data: {
        challenges: ChallengeItem[];
        map_nodes: ChallengeMapNode[];
        summary: {
          total: number;
          completed: number;
          total_reward: number;
          streak_days: number;
        };
      };
    }>(`/gamification-challenge/${studentId}/challenges`),
};

// ---------- 增强排行榜 ----------
export interface LeaderboardEntryPlus {
  student_id: string;
  username: string;
  score: number;
  rank: number;
}

export const leaderboardPlusApi = {
  get: (dimension: string, period: string = "weekly", limit: number = 20) =>
    api.get<{
      status: string;
      data: {
        dimension: string;
        period: string;
        entries: LeaderboardEntryPlus[];
      };
    }>(`/gamification-challenge/leaderboard/${dimension}`, {
      params: { period, limit },
    }),
};

// ---------- PPT生成 ----------
export const pptApi = {
  generate: (data: { topic: string; subject?: string }) =>
    api.post<{ status: string; task_id: string; message: string }>(
      "/ppt/generate",
      data,
    ),
  getStatus: (taskId: string) =>
    api.get<{
      status: string;
      data: {
        task_id: string;
        status: string;
        progress: number;
        filename: string | null;
        slide_count: number | null;
        message: string;
      };
    }>(`/ppt/${taskId}/status`),
  downloadUrl: (taskId: string) => {
    const token = useAppStore.getState().token;
    const url = `${API_BASE_URL}/ppt/${taskId}/download`;
    if (token) {
      return `${url}?token=${encodeURIComponent(token)}`;
    }
    return url;
  },
};

// ---------- Learning Data ----------
export const learningDataApi = {
  getHistory: (studentId: string, limit?: number) =>
    api.get<{
      status: string;
      student_id: string;
      records: Array<{
        kp_id: string;
        progress: number;
        created_at?: string;
        [key: string]: unknown;
      }>;
      quizzes: Array<{
        kp_id: string;
        score: number;
        created_at?: string;
        [key: string]: unknown;
      }>;
    }>(`/learning-data/${studentId}/history`, {
      params: { limit: limit || 50 },
    }),
  record: (data: LearningRecordRequest) =>
    api.post<{
      status: string;
      record_id: string;
      points_awarded?: number;
      total_points?: number;
    }>("/learning-data/record", data),
  getCompleted: (studentId: string) =>
    api.get<{
      status: string;
      student_id: string;
      completed_kps: string[];
      count: number;
    }>(`/learning-data/${studentId}/completed`),
  submitFeedback: (data: {
    student_id: string;
    kp_id: string;
    rating: string;
  }) => api.post<{ status: string }>("/learning-data/feedback", data),
  submitQuiz: (data: {
    student_id: string;
    kp_id: string;
    total_questions: number;
    correct_count: number;
    score: number;
    weak_tags?: string[];
    time_spent?: number;
    answers?: Record<string, unknown>;
  }) =>
    api.post<{
      status: string;
      quiz_id?: string;
      points_awarded?: number;
    }>("/learning-data/quiz", data),
};

// ---------- 反思与日志 ----------
export const logReflectionApi = {
  getReflections: (studentId: string, limit?: number) =>
    api.get<{
      status: string;
      data: Array<{
        reflection_id: string;
        date: string;
        content: string;
        mood: string;
        tags: string[];
        ai_feedback?: string;
        created_at?: string;
      }>;
    }>(`/log-reflection/${studentId}/reflections`, {
      params: { limit: limit || 30 },
    }),
  createReflection: (data: {
    student_id: string;
    date: string;
    content: string;
    mood?: string;
    tags?: string[];
    ai_feedback?: string;
  }) =>
    api.post<{ status: string; message?: string; reflection_id: string }>(
      "/log-reflection/reflections/create",
      data,
    ),
  updateReflection: (
    reflectionId: string,
    data: {
      content?: string;
      mood?: string;
      tags?: string[];
      ai_feedback?: string;
    },
  ) =>
    api.put<{ status: string; reflection_id: string }>(
      `/log-reflection/reflections/${reflectionId}`,
      data,
    ),
  deleteReflection: (reflectionId: string) =>
    api.delete<{ status: string; reflection_id: string }>(
      `/log-reflection/reflections/${reflectionId}`,
    ),
  getLogs: (studentId: string, date?: string) =>
    api.get<{
      status: string;
      data: Array<{
        log_id: string;
        date: string;
        total_duration: number;
        kp_count: number;
        quiz_count: number;
        avg_score: number;
        mistakes: string[];
        path_progress: number;
        completed_tasks: string[];
        timeline: Array<{
          time: string;
          activity: string;
          [key: string]: unknown;
        }>;
      }>;
    }>(
      `/log-reflection/${studentId}/logs`,
      date ? { params: { date } } : undefined,
    ),
  getReview: (studentId: string) =>
    api.get<{
      status: string;
      student_id: string;
      summary: Record<string, unknown>;
      daily_logs: Array<{
        date: string;
        total_duration: number;
        [key: string]: unknown;
      }>;
      reflections: Array<{
        reflection_id: string;
        content: string;
        created_at?: string;
        [key: string]: unknown;
      }>;
    }>(`/log-reflection/${studentId}/review`),
};

// ---------- Trend ----------
export const trendApi = {
  getHistory: (studentId: string, days?: number) =>
    api.get<{
      status: string;
      student_id: string;
      data: Array<{
        date: string;
        trend_factor: number;
        trend_state: string;
        dimensions: Record<string, number>;
        predicted_mastery_3d: number;
        intervention: string;
      }>;
    }>(`/trend/${studentId}/history`, { params: { days: days || 30 } }),
  analyze: (studentId: string) =>
    api.post<{ status: string; data: unknown }>("/trend/analyze", {
      student_id: studentId,
    }),
};

// ---------- 知识点 ----------
export const knowledgeApi = {
  list: (subject?: string) =>
    api.get<{
      status: string;
      data: Array<{
        kp_id: string;
        name: string;
        subject: string;
        difficulty: number;
        prerequisites: string[];
        tags: string[];
      }>;
    }>(`/knowledge/list`, subject ? { params: { subject } } : undefined),
  get: (kpId: string) =>
    api.get<{ status: string; data: unknown }>(`/knowledge/${kpId}`),
  search: (q: string) =>
    api.get<{
      status: string;
      data: Array<{
        kp_id: string;
        name: string;
        subject: string;
        difficulty: number;
        prerequisites: string[];
        tags: string[];
      }>;
    }>(`/knowledge/search`, { params: { q } }),
};

// ---------- 每日练习 ----------
export const dailyQuizApi = {
  getDaily: (count?: number, subject?: string) =>
    api.get<{
      status: string;
      data: {
        date: string;
        total_questions: number;
        difficulty_level: string;
        difficulty: number;
        questions: Array<{
          q_id: string;
          type: string;
          content: string;
          difficulty: number;
          source: string;
          hint: string;
          tags: string[];
          options?: Array<{ id: string; text: string }>;
          correct_answer?: string;
        }>;
        weak_areas: string[];
      };
    }>(
      "/daily-quiz/daily",
      count || subject
        ? {
            params: {
              ...(count ? { count } : {}),
              ...(subject ? { subject } : {}),
            },
          }
        : undefined,
    ),
  getStats: () =>
    api.get<{
      status: string;
      data: {
        total_questions: number;
        today_completed: number;
        knowledge_points_covered: number;
      };
    }>("/daily-quiz/stats"),
};

// ---------- Agent 工作流 ----------
export const agentFlowApi = {
  startRun: (data: {
    student_id: string;
    task_type: string;
    context?: Record<string, unknown>;
  }) =>
    api.post<{ run_id: string; status: string; task_type: string }>(
      "/agent-flow/run",
      data,
    ),
  getStatus: (runId: string) =>
    api.get<import("../types").AgentFlowRun>(`/agent-flow/${runId}/status`),
};

// ---------- 协作督导 ----------
export interface TeamMember {
  student_id: string;
  name: string;
  skills?: string[];
  current_task?: string;
}

export const collaborationApi = {
  dailyReport: (data: {
    project_id: string;
    team_members: TeamMember[];
    progress_data?: Record<string, unknown>;
  }) =>
    api.post<{
      status: string;
      task: string;
      report: Record<string, unknown>;
    }>("/collaboration-supervisor/daily-report", data),

  detectBlockers: (data: {
    team_members: TeamMember[];
    progress_data?: Record<string, unknown>;
  }) =>
    api.post<{
      status: string;
      task: string;
      blockers: unknown[];
      analysis: Record<string, unknown>;
    }>("/collaboration-supervisor/detect-blockers", data),

  resolveConflict: (data: {
    conflict_description: string;
    involved_members: TeamMember[];
    project_context?: string;
  }) =>
    api.post<{
      status: string;
      task: string;
      resolution: Record<string, unknown>;
    }>("/collaboration-supervisor/resolve-conflict", data),

  knowledgeSharing: (data: {
    team_members: TeamMember[];
    project_modules?: Record<string, unknown>[];
  }) =>
    api.post<{
      status: string;
      task: string;
      plan: Record<string, unknown>;
    }>("/collaboration-supervisor/knowledge-sharing", data),

  syncProgress: (data: {
    project_id: string;
    team_members: TeamMember[];
    progress_data?: Record<string, unknown>;
  }) =>
    api.post<{
      status: string;
      task: string;
      project_id: string;
      overall_progress: number;
      total_tasks: number;
      completed_tasks: number;
      member_progress: unknown[];
      sync_time: string;
    }>("/collaboration-supervisor/sync-progress", data),
};

// ---------- 项目拆解 ----------
export interface ProjectInfo {
  id: string;
  name: string;
  description: string;
  difficulty: number;
  type?: string;
  [key: string]: unknown;
}

export const projectDecomposerApi = {
  getProjects: () =>
    api.get<{ status: string; projects: ProjectInfo[] }>(
      "/project-decomposer/projects",
    ),
  decompose: (data: {
    project_id?: string;
    project_name?: string;
    team_size?: number;
    team_level?: string;
  }) =>
    api.post<{
      status: string;
      decomposition: Record<string, unknown>;
      detail?: string;
    }>("/project-decomposer/decompose", data),
  estimate: (data: {
    project_type: string;
    team_size: number;
    [key: string]: unknown;
  }) =>
    api.post<{
      status: string;
      estimation: Record<string, unknown>;
    }>("/project-decomposer/estimate", data),
};

// ---------- 角色匹配 ----------
export interface StudentInfo {
  student_id: string;
  name?: string;
  skills?: string[];
  [key: string]: unknown;
}

export const roleMatcherApi = {
  getRoles: () =>
    api.get<{ status: string; roles: Record<string, unknown>[] }>(
      "/role-matcher/roles",
    ),
  match: (data: {
    students: StudentInfo[];
    project_tasks: Record<string, unknown>;
    [key: string]: unknown;
  }) =>
    api.post<{
      status: string;
      assignments: Record<string, unknown>[];
      detail?: string;
    }>("/role-matcher/match", data),
};

// ---------- 匹配推荐 ----------
export const matchingApi = {
  matchResources: (data: {
    student_id: string;
    resources: Array<Record<string, unknown>>;
    top_k?: number;
  }) =>
    api.post<{
      status: string;
      data: {
        matches: Array<{
          resource_id: string;
          score: number;
          reasons: string[];
        }>;
      };
    }>("/matching/resources", data),

  matchPaths: (data: {
    student_id: string;
    path_candidates: Array<Record<string, unknown>>;
    top_k?: number;
  }) =>
    api.post<{
      status: string;
      data: {
        matches: Array<{
          path_id: string;
          score: number;
          reasons: string[];
        }>;
      };
    }>("/matching/paths", data),
};

// ---------- 成果评估 ----------
export const evaluationApi = {
  evaluateCode: (data: {
    code_submission: { file_name?: string; code: string; student_id?: string };
    language?: string;
  }) =>
    api.post<{
      status: string;
      task: string;
      evaluation: Record<string, unknown>;
    }>("/result-evaluator/evaluate-code", data),

  evaluateCollaboration: (data: {
    team_members: TeamMember[];
    collaboration_data?: Record<string, unknown>;
  }) =>
    api.post<{
      status: string;
      task: string;
      evaluation: Record<string, unknown>;
    }>("/result-evaluator/evaluate-collaboration", data),

  evaluateDeliverable: (data: {
    project_info: Record<string, unknown>;
    deliverables?: Record<string, unknown>[];
    team_level?: string;
  }) =>
    api.post<{
      status: string;
      task: string;
      evaluation: Record<string, unknown>;
    }>("/result-evaluator/evaluate-deliverable", data),

  evaluateLearning: (data: {
    team_members: TeamMember[];
    project_info?: Record<string, unknown>;
    knowledge_points?: string[];
  }) =>
    api.post<{
      status: string;
      task: string;
      evaluation: Record<string, unknown>;
    }>("/result-evaluator/evaluate-learning", data),

  fullReport: (data: {
    project_info: Record<string, unknown>;
    team_members: TeamMember[];
    code_submissions?: { file_name?: string; code: string }[];
    collaboration_data?: Record<string, unknown>;
    deliverables?: Record<string, unknown>[];
    knowledge_points?: string[];
    team_level?: string;
  }) =>
    api.post<{
      status: string;
      task: string;
      report: Record<string, unknown>;
    }>("/result-evaluator/full-report", data),
};

// ---------- 教师端 ----------
export const teacherApi = {
  getStudents: () =>
    api.get<{
      status: string;
      students: Array<{
        student_id: string;
        username: string;
        email: string | null;
        is_active: boolean;
        created_at: string | null;
        total_points: number;
        trend_state: string;
        trend_factor: number;
      }>;
      total: number;
    }>("/teacher/students"),

  getOverview: () =>
    api.get<{
      status: string;
      overview: {
        total_students: number;
        active_students: number;
        avg_weekly_hours: number;
        avg_score: number;
        total_quizzes: number;
        total_records: number;
      };
    }>("/teacher/overview"),

  getStudentDetail: (studentId: string) =>
    api.get<{ status: string; student: Record<string, unknown> }>(
      `/teacher/student/${studentId}/detail`,
    ),

  getStudentProgress: (studentId: string, limit?: number) =>
    api.get<{
      status: string;
      student_id: string;
      records: Array<Record<string, unknown>>;
      total: number;
    }>(`/teacher/student/${studentId}/progress`, {
      params: { limit: limit || 50 },
    }),

  getStudentScores: (studentId: string, limit?: number) =>
    api.get<{
      status: string;
      student_id: string;
      quizzes: Array<Record<string, unknown>>;
      avg_score: number;
      total: number;
    }>(`/teacher/student/${studentId}/scores`, {
      params: { limit: limit || 30 },
    }),

  getStudentTrends: (studentId: string, days?: number) =>
    api.get<{
      status: string;
      student_id: string;
      trends: Array<Record<string, unknown>>;
    }>(`/teacher/student/${studentId}/trends`, {
      params: { days: days || 30 },
    }),

  getStudentReflections: (studentId: string, limit?: number) =>
    api.get<{
      status: string;
      student_id: string;
      reflections: Array<Record<string, unknown>>;
    }>(`/teacher/student/${studentId}/reflections`, {
      params: { limit: limit || 20 },
    }),

  getRanking: (sortBy?: string, limit?: number) =>
    api.get<{
      status: string;
      ranking: Array<{
        student_id: string;
        username: string;
        total_points: number;
        total_hours: number;
        avg_score: number;
      }>;
      sort_by: string;
    }>("/teacher/ranking", {
      params: { sort_by: sortBy || "points", limit: limit || 20 },
    }),

  getWeakPoints: () =>
    api.get<{
      status: string;
      weak_tags: Array<{ tag: string; count: number }>;
      weak_areas: Array<{ area: string; count: number }>;
    }>("/teacher/weak-points"),

  getExportRecords: () =>
    api.get<{
      status: string;
      exports: Array<{
        export_id: string;
        report_type: string;
        format: string;
        student_ids?: string[];
        created_at: string;
        file_size?: string;
        status: string;
      }>;
      total: number;
    }>("/teacher/exports"),

  createExport: (data: {
    report_type: string;
    format: string;
    student_ids?: string[];
  }) =>
    api.post<{
      status: string;
      export_id: string;
      report_type: string;
      format: string;
      created_at: string;
      message: string;
    }>("/teacher/exports", null, { params: data }),

  getResources: () =>
    api.get<{
      status: string;
      resources: Array<{
        resource_id: string;
        name: string;
        type: string;
        created_at: string;
        status: string;
        download_url?: string;
      }>;
      total: number;
    }>("/teacher/resources"),

  getSystemInfo: () =>
    api.get<{
      status: string;
      system_info: {
        version: string;
        ai_model: string;
        database_status: string;
        last_updated: string;
      };
    }>("/teacher/system-info"),
};

// ---------- 教师注册 ----------
export const teacherAuthApi = {
  register: (data: {
    student_id: string;
    username: string;
    email?: string;
    password: string;
  }) =>
    api.post<{ status: string; message: string; student_id: string }>(
      "/auth/register-teacher",
      data,
    ),
};

// ---------- 引导问卷 ----------
export const onboardingApi = {
  check: () =>
    api.get<{ status: string; completed: boolean }>("/onboarding/check"),
  submit: (data: import("../types").OnboardingAnswers) =>
    api.post<{
      status: string;
      data: {
        path: import("../types").LearningPathData;
        profile: Record<string, unknown>;
      };
    }>("/onboarding/submit", data),
};

// ---------- 路径调整日志 ----------
export const adjustmentLogApi = {
  getLogs: (studentId: string, limit?: number) =>
    api.get<{
      status: string;
      data: import("../types").PathAdjustmentLog[];
    }>(`/path-adjustment/${studentId}/logs`, {
      params: { limit: limit || 20 },
    }),
};

// ---------- 电路分析 ----------
export const circuitApi = {
  analyze: (data: {
    netlist: Array<{
      name: string;
      type: string;
      node1: number;
      node2: number;
      value: number;
    }>;
    node_voltages?: Record<string, number>;
    branch_currents?: Record<string, number>;
    student_question?: string;
    student_level?: string;
  }) =>
    api.post<{
      status: string;
      analysis?: string;
      circuit_description?: string;
    }>("/circuit-analysis/analyze", data),
};

// ---------- SSE 流式传输 ----------
export interface StreamCallbacks {
  onToken?: (token: string) => void;
  onKnowledgePoints?: (points: string[]) => void;
  onResources?: (
    resources: Array<{ type: string; title: string; url?: string }>,
  ) => void;
  onAgentStep?: (agent: string, status: string) => void;
  onAgentResult?: (agent: string, content: string) => void;
  onResourceContent?: (content: string) => void;
  onDone?: () => void;
  onError?: (message: string) => void;
}

export async function apiGet<T>(path: string): Promise<T> {
  const token = useAppStore.getState().token;
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  const res = await fetch(`${API_BASE_URL}${path}`, { headers });
  if (res.status === 401) {
    useAppStore.getState().logout();
    window.location.href = "/login";
    throw new Error("登录已过期，请重新登录");
  }
  if (!res.ok) {
    const err = await res
      .json()
      .catch(() => ({ message: `HTTP ${res.status}` }));
    throw new Error(err.message || "请求失败");
  }
  return res.json();
}

export async function apiStream(
  path: string,
  body: unknown,
  callbacks: StreamCallbacks,
): Promise<void> {
  const token = useAppStore.getState().token;
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers,
    body: JSON.stringify(body),
  });
  if (res.status === 401) {
    useAppStore.getState().logout();
    window.location.href = "/login";
    throw new Error("登录已过期，请重新登录");
  }
  if (!res.ok) {
    const err = await res.json().catch(() => ({ message: "请求失败" }));
    throw new Error(err.message || `HTTP ${res.status}`);
  }
  if (!res.body) throw new Error("响应体为空");

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let doneCalled = false;
  const markDone = () => {
    if (!doneCalled) {
      doneCalled = true;
      callbacks.onDone?.();
    }
  };

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const parts = buffer.split("\n\n");
    buffer = parts.pop() || "";
    for (const part of parts) {
      if (!part.startsWith("data: ")) continue;
      try {
        const parsed = JSON.parse(part.slice(6));
        if (parsed.type === "token") callbacks.onToken?.(parsed.content);
        if (parsed.type === "knowledge_points")
          callbacks.onKnowledgePoints?.(parsed.data);
        if (parsed.type === "resources") callbacks.onResources?.(parsed.data);
        if (parsed.type === "agent_step")
          callbacks.onAgentStep?.(parsed.agent, parsed.status);
        if (parsed.type === "agent_result")
          callbacks.onAgentResult?.(parsed.agent, parsed.content);
        if (parsed.type === "resource_content")
          callbacks.onResourceContent?.(parsed.content);
        if (parsed.type === "done") markDone();
        if (parsed.type === "error") {
          callbacks.onError?.(parsed.message || "服务异常");
          markDone();
        }
      } catch {
        // SSE parse error, skip
      }
    }
  }
  markDone();
}

// ---------- STM32 课程内容 ----------
export const stm32Api = {
  listCourses: () =>
    api.get<{
      status: string;
      data: {
        courses: Array<{
          id: string;
          filename: string;
          title: string;
        }>;
      };
    }>("/stm32/courses"),

  getCourseContent: (courseId: string) =>
    api.get<{
      status: string;
      data: {
        id: string;
        filename: string;
        title: string;
        content: string;
      };
    }>(`/stm32/courses/${encodeURIComponent(courseId)}`),

  listWiringDiagrams: () =>
    api.get<{
      status: string;
      data: {
        diagrams: Array<{
          filename: string;
          title: string;
          url: string;
        }>;
      };
    }>("/stm32/wiring-diagrams"),

  listProjects: () =>
    api.get<{
      status: string;
      data: {
        projects: Array<{
          dirname: string;
          title: string;
          file_count: number;
        }>;
      };
    }>("/stm32/projects"),

  getProjectFiles: (dirname: string) =>
    api.get<{
      status: string;
      data: {
        dirname: string;
        files: Array<{ path: string; size: number }>;
      };
    }>(`/stm32/projects/${encodeURIComponent(dirname)}`),

  getKnowledgeTree: () =>
    api.get<{
      status: string;
      data: {
        courses: Array<Record<string, unknown>>;
        knowledge_points: Array<Record<string, unknown>>;
        experiments: Array<Record<string, unknown>>;
        learning_paths: Array<Record<string, unknown>>;
      };
    }>("/stm32/knowledge-tree"),
};

export default api;
