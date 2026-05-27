/**
 * 等级系统工具
 * 以后端 /gamification-tree/level-config 接口为唯一数据源
 * 前端仅做展示计算，不硬编码阈值
 */

export interface LevelConfig {
  xp_per_level: number;
  max_level: number;
  level_names: Record<number, string>;
}

export interface LevelInfo {
  level: number;
  level_name: string;
  current_xp: number;
  xp_to_next: number;
  total_xp: number;
  xp_per_level: number;
  progress_pct: number;
}

// 默认配置（仅在接口未返回时兜底使用）
const DEFAULT_CONFIG: LevelConfig = {
  xp_per_level: 500,
  max_level: 10,
  level_names: {
    1: "初学者",
    2: "探索者",
    3: "学习者",
    4: "进阶者",
    5: "熟练者",
    6: "精通者",
    7: "专家",
    8: "大师",
    9: "宗师",
    10: "传奇",
  },
};

let _cachedConfig: LevelConfig | null = null;

export async function fetchLevelConfig(): Promise<LevelConfig> {
  try {
    const { api } = await import("../services/api");
    const res = await api.get("/gamification-tree/level-config");
    const data = res.data?.data;
    if (data) {
      _cachedConfig = {
        xp_per_level: data.xp_per_level,
        max_level: data.max_level,
        level_names: data.level_names,
      };
      return _cachedConfig;
    }
  } catch {}
  return DEFAULT_CONFIG;
}

export function getLevelConfig(): LevelConfig {
  return _cachedConfig || DEFAULT_CONFIG;
}

/**
 * 从 total_xp 计算等级信息（前端本地计算，与后端保持一致）
 */
export function calcLevel(totalXp: number, config?: LevelConfig): LevelInfo {
  const cfg = config || getLevelConfig();
  const rawLevel = Math.floor(totalXp / cfg.xp_per_level) + 1;
  const level = Math.min(rawLevel, cfg.max_level);
  const currentXp = totalXp % cfg.xp_per_level;
  return {
    level,
    level_name: cfg.level_names[level] || `Lv.${level}`,
    current_xp: currentXp,
    xp_to_next: level < cfg.max_level ? cfg.xp_per_level : 0,
    total_xp: totalXp,
    xp_per_level: cfg.xp_per_level,
    progress_pct:
      level < cfg.max_level
        ? Math.round((currentXp / cfg.xp_per_level) * 100)
        : 100,
  };
}
