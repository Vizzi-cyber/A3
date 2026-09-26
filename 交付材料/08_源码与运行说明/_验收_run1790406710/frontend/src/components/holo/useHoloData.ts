/**
 * 全息空间数据 hook：拉取系统真实数据（含 35 知识点图谱 + 前置依赖）
 */
import { useEffect, useState } from "react";
import api from "../../services/api";

export interface GraphNode {
  kp_id: string;
  name: string;
  course: string;
  difficulty: number;
  /** 学习状态：completed / in-progress / pending / locked / unknown */
  status: string;
  /** 掌握度 0-1（来自画像 knowledge_base） */
  mastery: number | null;
}

export interface HoloData {
  weeklyHours: number;
  totalHours: number;
  masteredKps: number;
  achievements: number;
  favorites: number;
  streakDays: number;
  todayMin: number;
  pathProgress: number;
  pathNodes: number;
  quizTotal: number;
  quizCovered: number;
  points: number;
  level: number;
  topRankers: { name: string; score: number }[];
  /** 待办任务列表 */
  tasks: { title: string; type?: string }[];
  /** 学习趋势（近 7 天，来自 dashboard.trend） */
  trend: { date: string; value: number }[];
  /** 知识图谱（真实知识点 + 前置依赖） */
  graphNodes: GraphNode[];
  graphEdges: [string, string][];
}

const EMPTY: HoloData = {
  weeklyHours: 0, totalHours: 0, masteredKps: 0, achievements: 0, favorites: 0,
  streakDays: 0, todayMin: 0, pathProgress: 0, pathNodes: 0, quizTotal: 0,
  quizCovered: 0, points: 0, level: 1, topRankers: [], tasks: [], trend: [], graphNodes: [], graphEdges: [],
};

export function useHoloData(studentId = "student_001") {
  const [data, setData] = useState<HoloData>(EMPTY);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    let alive = true;
    const load = async () => {
      try {
        const [dash, path, quiz, gam, leader, kp, profile] = await Promise.allSettled([
          api.get(`/dashboard/${studentId}/summary`),
          api.get(`/learning-path/${studentId}/current`),
          api.get("/daily-quiz/stats"),
          api.get(`/gamification/${studentId}/points`),
          api.get("/gamification/leaderboard/week"),
          api.get("/knowledge/list"),
          api.get(`/profile/${studentId}`),
        ]);
        const val = (r: PromiseSettledResult<any>) => (r.status === "fulfilled" ? r.value?.data : null);
        const stats = val(dash)?.stats ?? {};
        const pathD = val(path)?.data ?? val(path) ?? {};
        const quizD = val(quiz)?.data ?? val(quiz) ?? {};
        const gamD = val(gam)?.data ?? val(gam) ?? {};
        const lbD = val(leader)?.data ?? val(leader) ?? {};
        const kpD = val(kp)?.data ?? val(kp) ?? {};
        const kpList = Array.isArray(kpD) ? kpD : (kpD.knowledge_points ?? kpD.list ?? kpD.items ?? []);
        const top = Array.isArray(lbD) ? lbD.slice(0, 3) : (lbD.list ?? lbD.leaderboard ?? []).slice(0, 3);

        // 节点状态：来自学习路径（completed / in-progress / pending / locked）
        const pathNodesArr = Array.isArray(pathD) ? pathD : (pathD.nodes ?? []);
        const statusMap: Record<string, string> = {};
        pathNodesArr.forEach((n: any) => {
          if (n.kp_id && n.status) statusMap[n.kp_id] = n.status;
        });
        // 掌握度：来自画像 knowledge_base（按知识点名匹配）
        const kb = val(profile)?.knowledge_base ?? val(profile)?.data?.knowledge_base ?? {};
        const masteryMap: Record<string, number> = {};
        Object.entries(kb).forEach(([name, score]) => {
          if (typeof score === "number") masteryMap[name] = score;
        });

        // 图谱：35 个真实知识点 + 前置依赖边 + 状态 + 掌握度
        const graphNodes: GraphNode[] = kpList.map((k: any) => ({
          kp_id: k.kp_id,
          name: k.name,
          course: k.course ?? "",
          difficulty: k.difficulty ?? 0.5,
          status: statusMap[k.kp_id] ?? "unknown",
          mastery: masteryMap[k.name] ?? null,
        }));
        const graphEdges: [string, string][] = [];
        kpList.forEach((k: any) => {
          (k.prerequisites ?? []).forEach((p: string) => graphEdges.push([p, k.kp_id]));
        });

        if (!alive) return;
        setData({
          weeklyHours: stats.weekly_hours ?? 0,
          totalHours: stats.total_hours ?? 0,
          masteredKps: stats.mastered_kps ?? 0,
          achievements: stats.achievements ?? 0,
          favorites: stats.favorites ?? 0,
          streakDays: stats.streak_days ?? 0,
          todayMin: stats.today_duration_min ?? 0,
          pathProgress: pathD.progress ?? 0,
          pathNodes: pathD.nodes?.length ?? pathD.total_nodes ?? 0,
          quizTotal: quizD.total_questions ?? 0,
          quizCovered: quizD.knowledge_points_covered ?? 0,
          points: gamD.points ?? gamD.total_points ?? 0,
          level: gamD.level ?? stats.level ?? 1,
          topRankers: top.map((r: any) => ({ name: r.student_id ?? r.name ?? "?", score: r.points ?? r.score ?? 0 })),
          tasks: ((val(dash) as any)?.tasks ?? stats.tasks ?? []).slice(0, 5),
          trend: (((val(dash) as any)?.trend) ?? []).slice(-14),
          graphNodes,
          graphEdges,
        });
      } catch {
        // 降级
      } finally {
        if (alive) setLoaded(true);
      }
    };
    load();
    return () => { alive = false; };
  }, [studentId]);

  return { data, loaded };
}
