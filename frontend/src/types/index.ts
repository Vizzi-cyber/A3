// ============================================
// 全局类型定义 - AI Learning System
// ============================================

export interface ApiResponse<T = unknown> {
  status: string
  message?: string
  data?: T
  summary?: Record<string, unknown>
  llm_analysis?: Record<string, unknown>
}

// ---------- 学生画像 ----------
export interface CognitiveStyle {
  primary?: string
  scores?: Record<string, number>
}

export interface LearningTempo {
  study_speed?: string
  optimal_session_duration?: number
  weekly_study_capacity?: number
  focus_score?: number
}

export interface PracticalPreferences {
  coding_proficiency?: Record<string, unknown>
  preferred_practice_types?: string[]
  overall_score?: number
}

export interface KnowledgeBase {
  overall_score?: number
  [key: string]: unknown
}

export interface StudentProfile {
  student_id: string
  knowledge_base: KnowledgeBase
  cognitive_style: CognitiveStyle
  weak_areas: string[]
  error_patterns: Record<string, unknown>[]
  learning_goals: Record<string, unknown>[]
  interest_areas: Record<string, unknown>[]
  learning_tempo: LearningTempo
  practical_preferences: PracticalPreferences
  created_at?: string
  updated_at?: string
}

export interface ProfileUpdateRequest {
  dimension: string
  updates: Record<string, unknown>
  confidence?: number
  trigger?: string
}

export interface ProfileInitRequest {
  inputs: string[]
  initial_data?: Record<string, unknown>
}

export interface ProfileSummary {
  dominant_style: string
  current_level: string
  focus_areas: string[]
  weekly_study_hours: number
  last_updated: string
}

// ---------- 学习路径 ----------
export interface PathStage {
  stage_no: number
  title: string
  topics: string[]
  hours: number
  criteria: string
  resources: string[]
}

export interface LearningPathData {
  target?: string
  estimated_total_hours?: number
  stages?: PathStage[]
  [key: string]: unknown
}

export interface LearningPath {
  path_id: string
  student_id: string
  path: LearningPathData
}

export interface PathGenerationRequest {
  student_id: string
  target_topic: string
  current_knowledge?: string[]
  time_constraint?: number
  preference?: string
  daily_duration?: number
  difficulty?: number
}

export interface PathAdjustmentRequest {
  feedback: string
  current_path?: LearningPathData
}

export interface PathNode {
  id: number
  title: string
  status: string
  type: string
  resources: number
}

export interface CurrentPathResponse {
  status: string
  student_id: string
  current_step: number
  progress: number
  next_task: {
    kp_id: string
    name: string
    action: string
  }
  nodes?: PathNode[]
}

// ---------- 资源生成 ----------
export interface ResourceGenerationRequest {
  student_id: string
  topic: string
  resource_types?: string[]
  difficulty?: string
  cognitive_style?: string
}

export interface ResourceGenerationResponse {
  task_id: string
  status: string
  progress: number
  resources: Record<string, unknown>
  message: string
}

export interface DocumentGenerationRequest {
  student_id: string
  topic: string
  difficulty?: string
  kp_id?: string
}

export interface DocumentGenerationResponse {
  status: string
  document: string
  metadata: {
    topic: string
    generated_at: string
  }
}

export interface QuestionOption {
  id: string
  text: string
}

export interface QuestionItem {
  q_id: string
  type: string
  content: string
  options: QuestionOption[]
  correct_answer: string
  explanation: string
}

export interface QuestionsGenerationRequest {
  student_id: string
  topic: string
  count?: number
  kp_id?: string
}

export interface QuestionsGenerationResponse {
  status: string
  topic: string
  count: number
  questions: QuestionItem[] | QuestionItem
}

export interface MindmapGenerationRequest {
  student_id: string
  topic: string
  kp_id?: string
}

export interface MindmapNode {
  name: string
  children?: MindmapNode[]
}

export interface MindmapGenerationResponse {
  status: string
  mindmap: {
    root?: string
    children?: MindmapNode[]
  }
  format: string
}

export interface CodeGenerationRequest {
  student_id: string
  topic: string
  language?: string
  kp_id?: string
}

export interface CodeGenerationResponse {
  status: string
  code: string
  language: string
  filename: string
}

// ---------- 智能辅导 ----------
export interface TutorRequest {
  student_id: string
  question: string | VisionContentItem[]
  context?: Record<string, unknown>
  session_id?: string
}

export interface TutorResponse {
  response: string
  response_type: string
  resources?: Record<string, unknown>[]
  follow_up_questions?: string[]
}

// OpenAI vision 格式内容项
export type VisionContentItem =
  | { type: 'text'; text: string }
  | { type: 'image_url'; image_url: { url: string } }

export interface TutorMessage {
  role: 'user' | 'ai' | 'system'
  content: string | VisionContentItem[]
}

export interface TutorSessionHistoryResponse {
  status: string
  session_id: string
  messages: TutorMessage[]
}

// ---------- UI 通用 ----------
export interface ChatMessage {
  role: 'user' | 'ai' | 'system'
  content: string | VisionContentItem[]
  agent?: string
}

export interface ReflectionEntry {
  id: string
  date: string
  content: string
  topic: string
}

export interface ToastState {
  type: 'success' | 'error' | 'info'
  message: string
}
