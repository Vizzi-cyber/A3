"""
每日推送练习题 API
根据学生画像动态调整难度，从知识库中抽取练习题
"""
import json
import random
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..models.database import get_db
from ..models.knowledge import KnowledgePointModel, LearningRecordModel, QuizResultModel
from ..models.student import StudentProfileModel
from ..algorithms.bandit_selector import ThompsonSamplingSelector
from ..core.logger import setup_logger
from .auth import require_auth, get_current_student_id

logger = setup_logger()
router = APIRouter()

# AIC 算法增强：Thompson Sampling 选题器（按学生维度，进程内维护）
_bandit_selectors: Dict[str, ThompsonSamplingSelector] = {}


def _get_selector(student_id: str, arms: List[str]) -> ThompsonSamplingSelector:
    """获取（或新建）该学生的 MAB 选题器；知识点集合变化时重建。"""
    sel = _bandit_selectors.get(student_id)
    if sel is None or sel.arms != arms:
        sel = ThompsonSamplingSelector(arms)
        _bandit_selectors[student_id] = sel
    return sel


def _feedback_last_quiz(db: Session, student_id: str) -> None:
    """反馈闭环：把该生最近一次测验得分作为上一轮选题的收益，更新 MAB。"""
    try:
        last = (
            db.query(QuizResultModel)
            .filter(QuizResultModel.student_id == student_id)
            .order_by(QuizResultModel.created_at.desc())
            .first()
        )
        if last is not None and last.kp_id:
            selector = _bandit_selectors.get(student_id)
            if selector is not None:
                selector.update(last.kp_id, (last.score or 0) / 100.0)
    except Exception:
        pass  # 反馈失败不影响选题主流程


class DailyQuizResponse(BaseModel):
    date: str
    total_questions: int
    difficulty_level: str
    questions: List[Dict[str, Any]]
    weak_areas: List[str]


def _calculate_difficulty(profile: Optional[StudentProfileModel], mastery_map: Dict[str, float]) -> Dict[str, Any]:
    """根据学生画像计算推荐难度"""
    # 基础难度
    base_difficulty = 2.0

    if profile:
        # 知识基础影响
        kb = profile.knowledge_base or {}
        overall_score = kb.get("overall_score", 0.5)
        base_difficulty = 1.0 + overall_score * 4.0  # 映射到 1-5

        # 薄弱点需要降低难度
        weak_areas = profile.weak_areas or []
        if len(weak_areas) > 3:
            base_difficulty = max(1.0, base_difficulty - 0.5)

    # 学习进度影响
    if mastery_map:
        avg_progress = sum(mastery_map.values()) / len(mastery_map)
        if avg_progress > 0.8:
            base_difficulty = min(5.0, base_difficulty + 0.5)
        elif avg_progress < 0.3:
            base_difficulty = max(1.0, base_difficulty - 0.5)

    # 映射到难度等级
    difficulty = round(base_difficulty)
    difficulty = max(1, min(5, difficulty))

    level_names = {1: "入门", 2: "基础", 3: "进阶", 4: "挑战", 5: "困难"}
    return {
        "difficulty": difficulty,
        "level_name": level_names.get(difficulty, "基础"),
    }


def _get_weak_kp_ids(profile: Optional[StudentProfileModel], mastery_map: Dict[str, float]) -> List[str]:
    """获取薄弱知识点ID列表"""
    weak_ids = []

    # 从画像中获取
    if profile and profile.weak_areas:
        weak_ids.extend(profile.weak_areas[:5])

    # 从学习记录中获取进度低的
    for kp_id, progress in sorted(mastery_map.items(), key=lambda x: x[1]):
        if progress < 0.5 and kp_id not in weak_ids:
            weak_ids.append(kp_id)
        if len(weak_ids) >= 5:
            break

    return weak_ids


def _select_questions(
    all_questions: List[Dict[str, Any]],
    target_difficulty: int,
    count: int = 5,
    focus_kp_ids: Optional[List[str]] = None,
    preferred_kps: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """根据难度和薄弱点选择题目

    :param preferred_kps: AIC 算法增强——MAB（Thompson Sampling）推荐的
        优先知识点，优先从中选题，剩余名额再走原随机逻辑。
    """
    if not all_questions:
        return []

    # 按难度分组
    by_difficulty = {}
    for q in all_questions:
        d = q.get("difficulty", 2)
        by_difficulty.setdefault(d, []).append(q)

    selected = []

    # MAB 优先：从推荐知识点中选题（探索-利用的结果）
    if preferred_kps:
        pref_qs = [q for q in all_questions if q.get("_kp_id") in preferred_kps]
        if pref_qs:
            selected.extend(random.sample(pref_qs, min(len(pref_qs), count)))

    # 优先选择匹配难度的题目
    target_qs = by_difficulty.get(target_difficulty, [])
    if target_qs:
        selected.extend(random.sample(target_qs, min(len(target_qs), count)))

    # 不够则从相邻难度补充
    if len(selected) < count:
        for d_offset in [1, -1, 2, -2]:
            adj_d = target_difficulty + d_offset
            adj_qs = by_difficulty.get(adj_d, [])
            if adj_qs:
                remaining = count - len(selected)
                available = [q for q in adj_qs if q not in selected]
                selected.extend(random.sample(available, min(len(available), remaining)))
            if len(selected) >= count:
                break

    # 还不够就随机补充
    if len(selected) < count:
        remaining = count - len(selected)
        available = [q for q in all_questions if q not in selected]
        if available:
            selected.extend(random.sample(available, min(len(available), remaining)))

    return selected[:count]


@router.get("/daily")
async def get_daily_quiz(
    count: int = 5,
    subject: Optional[str] = None,
    db: Session = Depends(get_db),
    student_id: str = Depends(get_current_student_id),
):
    """获取每日练习题（根据学生画像动态调整难度）"""
    # 加载学生画像
    profile = db.query(StudentProfileModel).filter(StudentProfileModel.student_id == student_id).first()

    # 获取学习进度
    since = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0)
    progress_rows = (
        db.query(LearningRecordModel.kp_id, func.max(LearningRecordModel.progress).label("max_progress"))
        .filter(LearningRecordModel.student_id == student_id)
        .group_by(LearningRecordModel.kp_id)
        .all()
    )
    mastery_map = {row.kp_id: row.max_progress or 0.0 for row in progress_rows}

    # 计算推荐难度
    diff_info = _calculate_difficulty(profile, mastery_map)
    target_difficulty = diff_info["difficulty"]
    level_name = diff_info["level_name"]

    # 获取薄弱知识点
    weak_kp_ids = _get_weak_kp_ids(profile, mastery_map)

    # 从知识库中收集所有题目
    kp_query = db.query(KnowledgePointModel)
    if subject:
        COURSE_NAMES = {"C语言", "电路分析", "STM32嵌入式"}
        if subject in COURSE_NAMES:
            kp_query = kp_query.filter(KnowledgePointModel.course == subject)
        else:
            kp_query = kp_query.filter(KnowledgePointModel.subject == subject)
    kps = kp_query.all()
    all_questions = []
    for kp in kps:
        if not kp.questions:
            continue
        try:
            questions = json.loads(kp.questions) if isinstance(kp.questions, str) else kp.questions
        except (json.JSONDecodeError, TypeError):
            continue
        for q in questions:
            q["_kp_id"] = kp.kp_id
            q["_kp_name"] = kp.name
            all_questions.append(q)

    if not all_questions:
        return {
            "status": "success",
            "data": {
                "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                "total_questions": 0,
                "difficulty_level": level_name,
                "difficulty": target_difficulty,
                "questions": [],
                "weak_areas": weak_kp_ids,
                "message": "题库为空，请先导入练习题",
            },
        }

    # AIC 算法增强：Thompson Sampling 选题（探索-利用权衡）
    # 反馈闭环：先更新上一轮选题收益（最近一次测验得分），再选本轮的优先知识点
    preferred_kps: List[str] = []
    try:
        all_kps = list({q.get("_kp_id") for q in all_questions if q.get("_kp_id")})
        if len(all_kps) >= 2:
            selector = _get_selector(student_id, all_kps)
            _feedback_last_quiz(db, student_id)
            preferred_kps = selector.select(k=2)
    except Exception:
        preferred_kps = []  # MAB 异常时回退原随机逻辑

    # 选择题目：60% 来自薄弱点，40% 随机（均优先 MAB 推荐知识点）
    weak_questions = [q for q in all_questions if q.get("_kp_id") in weak_kp_ids]
    other_questions = [q for q in all_questions if q.get("_kp_id") not in weak_kp_ids]

    weak_count = min(int(count * 0.6), len(weak_questions))
    other_count = count - weak_count

    selected_weak = _select_questions(weak_questions, target_difficulty, weak_count, preferred_kps=preferred_kps)
    selected_other = _select_questions(other_questions, target_difficulty, other_count, preferred_kps=preferred_kps)

    daily_questions = selected_weak + selected_other
    random.shuffle(daily_questions)

    # 清理内部字段
    for q in daily_questions:
        q.pop("_kp_id", None)
        q.pop("_kp_name", None)

    return {
        "status": "success",
        "data": {
            "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "total_questions": len(daily_questions),
            "difficulty_level": level_name,
            "difficulty": target_difficulty,
            "questions": daily_questions,
            "weak_areas": weak_kp_ids,
        },
    }


@router.get("/stats")
async def get_quiz_stats(
    student_id: str = Depends(get_current_student_id),
    db: Session = Depends(get_db),
):
    """获取练习统计"""
    # 查询总题目数
    kps = db.query(KnowledgePointModel).all()
    total_questions = 0
    for kp in kps:
        if kp.questions:
            try:
                qs = json.loads(kp.questions) if isinstance(kp.questions, str) else kp.questions
                total_questions += len(qs)
            except (json.JSONDecodeError, TypeError):
                pass

    # 查询今日已做
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0)
    today_records = (
        db.query(LearningRecordModel)
        .filter(
            LearningRecordModel.student_id == student_id,
            LearningRecordModel.action == "practice",
            LearningRecordModel.created_at >= today,
        )
        .count()
    )

    return {
        "status": "success",
        "data": {
            "total_questions": total_questions,
            "today_completed": today_records,
            "knowledge_points_covered": len(kps),
        },
    }
