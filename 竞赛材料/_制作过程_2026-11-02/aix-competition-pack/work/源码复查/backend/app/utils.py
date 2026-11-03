"""
公共工具函数
"""
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Set


def safe_float(v: Any, default: float = 0.0) -> float:
    """安全转换为 float"""
    try:
        return float(v) if v is not None else default
    except (ValueError, TypeError):
        return default


def profile_to_dict(profile, extra: Optional[Dict] = None) -> Dict[str, Any]:
    """将 StudentProfileModel 转为字典"""
    if not profile:
        return {
            "student_id": "",
            "knowledge_base": {},
            "cognitive_style": {},
            "weak_areas": [],
            "interest_areas": [],
            "learning_tempo": {},
            "learning_goals": [],
            "updated_at": None,
        }
    result = {
        "student_id": profile.student_id,
        "knowledge_base": profile.knowledge_base or {},
        "cognitive_style": profile.cognitive_style or {},
        "weak_areas": profile.weak_areas or [],
        "interest_areas": profile.interest_areas or [],
        "learning_tempo": profile.learning_tempo or {},
        "learning_goals": profile.learning_goals or [],
        "updated_at": profile.updated_at.isoformat() if profile.updated_at else None,
    }
    if extra:
        result.update(extra)
    return result


def calculate_streak(date_strings: List[str]) -> int:
    """
    计算连续学习天数
    date_strings: 日期字符串列表，格式 "YYYY-MM-DD"
    """
    if not date_strings:
        return 0
    seen_days: Set = set()
    for d in date_strings:
        if d:
            try:
                seen_days.add(datetime.strptime(str(d), "%Y-%m-%d").date())
            except (ValueError, TypeError):
                continue
    if not seen_days:
        return 0
    today = datetime.now(timezone.utc).date()
    streak = 0
    for i in range(365):
        d = today - timedelta(days=i)
        if d in seen_days:
            streak += 1
        else:
            break
    return streak
