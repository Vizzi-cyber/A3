import type { StudentProfile } from "../types";

export interface RadarDataItem {
  subject: string;
  A: number;
  fullMark: number;
}

function normalizeScore(val: unknown): number {
  if (typeof val !== "number") return 0;
  if (val > 1) return Math.round(val);
  if (val >= 0 && val <= 1) return Math.round(val * 100);
  return 0;
}

export const buildRadarData = (
  profile: StudentProfile | null,
): RadarDataItem[] => {
  if (!profile) {
    return [];
  }

  const p = profile;
  const kb = p.knowledge_base || {};
  const kbScore = normalizeScore(kb.overall_score) || 85;

  const cognitiveScores = p.cognitive_style?.scores || {};
  const cognitiveKeys = Object.keys(cognitiveScores);
  const cognitiveSum = cognitiveKeys.reduce(
    (sum, k) => sum + normalizeScore(cognitiveScores[k]) / 100,
    0,
  );
  const cognitiveAvg = cognitiveKeys.length
    ? cognitiveSum / cognitiveKeys.length
    : 0;
  const cognitiveScore = Math.round(cognitiveAvg * 100) || 65;

  const pp = p.practical_preferences || {};
  const ppScore = normalizeScore(pp.overall_score) || 80;

  const weak = p.weak_areas || [];
  // 薄弱点越少分数越高：0项=100, 1项=85, 2项=70, 3项=55, 4项以上=40
  const weakScore = Math.max(40, 100 - weak.length * 15);

  const goals = p.learning_goals || [];
  const completedGoals = goals.filter((g: unknown) => {
    if (typeof g === "object" && g !== null) {
      const obj = g as Record<string, unknown>;
      return !!obj.completed || obj.status === "completed";
    }
    return false;
  }).length;
  const progressScore = Math.min(
    100,
    (goals.length > 0 ? 60 : 50) + completedGoals * 8,
  );

  const tempo = p.learning_tempo || {};
  const focusScore = normalizeScore(tempo.focus_score) || 80;

  return [
    { subject: "知识基础", A: kbScore, fullMark: 100 },
    { subject: "认知风格", A: cognitiveScore, fullMark: 100 },
    { subject: "学习偏好", A: ppScore, fullMark: 100 },
    { subject: "薄弱点", A: weakScore, fullMark: 100 },
    { subject: "学习进度", A: progressScore, fullMark: 100 },
    { subject: "专注度", A: focusScore, fullMark: 100 },
  ];
};
