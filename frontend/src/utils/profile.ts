import type { StudentProfile } from '../types'

export interface RadarDataItem {
  subject: string
  A: number
  fullMark: number
}

export const buildRadarData = (profile: StudentProfile | null): RadarDataItem[] => {
  if (!profile) {
    return [
      { subject: '知识基础', A: 85, fullMark: 100 },
      { subject: '数学基础', A: 65, fullMark: 100 },
      { subject: '编程能力', A: 80, fullMark: 100 },
      { subject: '薄弱点', A: 60, fullMark: 100 },
      { subject: '学习进度', A: 75, fullMark: 100 },
      { subject: '专注度', A: 80, fullMark: 100 },
    ]
  }

  const p = profile
  const cognitiveScores = p.cognitive_style?.scores || {}
  const cognitiveKeys = Object.keys(cognitiveScores)
  const cognitiveAvg = cognitiveKeys.length
    ? (Object.values(cognitiveScores).reduce((a, b) => (a as number) + (b as number), 0) as number) / cognitiveKeys.length
    : 0.7

  return [
    { subject: '知识基础', A: p.knowledge_base?.overall_score ?? 85, fullMark: 100 },
    { subject: '认知风格', A: Math.round(cognitiveAvg * 100), fullMark: 100 },
    { subject: '学习偏好', A: p.practical_preferences?.overall_score ?? 90, fullMark: 100 },
    { subject: '薄弱点', A: p.weak_areas?.length ? 60 : 85, fullMark: 100 },
    { subject: '学习进度', A: p.learning_goals?.length ? 75 : 50, fullMark: 100 },
    { subject: '专注度', A: p.learning_tempo?.focus_score ?? 80, fullMark: 100 },
  ]
}
