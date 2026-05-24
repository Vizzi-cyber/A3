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

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000,
  headers: {
    "Content-Type": "application/json",
  },
});

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
    const status = error.response?.status;
    const data = error.response?.data;
    const message =
      data?.message || data?.detail || error.message || "请求失败";
    if (status === 401) {
      useAppStore.getState().logout();
      window.dispatchEvent(new CustomEvent("auth:expired"));
      return Promise.reject(new Error("登录已过期，请重新登录"));
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
  current: (studentId: string) =>
    api.get<CurrentPathResponse>(`/learning-path/${studentId}/current`),
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
    api.get<{ status: string; tasks: unknown[] }>("/image/tasks"),
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
    interest_areas: string[];
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
        next_predicted_score: number;
      };
      loss_points: Array<{ kp_id: string; loss: number }>;
      intervention_strategies: string[];
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

export interface LearningRecordRequest {
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
      records: unknown[];
      quizzes: unknown[];
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
        timeline: unknown[];
      }>;
    }>(
      `/log-reflection/${studentId}/logs`,
      date ? { params: { date } } : undefined,
    ),
  getReview: (studentId: string) =>
    api.get<{
      status: string;
      student_id: string;
      summary: unknown;
      daily_logs: unknown[];
      reflections: unknown[];
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

export default api;
