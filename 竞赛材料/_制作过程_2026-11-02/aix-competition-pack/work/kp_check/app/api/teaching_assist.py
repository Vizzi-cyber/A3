"""
AI教研助手API
智能备课、学情洞察、智能组卷
"""
import json
import hashlib
import time
from typing import Optional, List, Dict, Any
from functools import lru_cache

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..core.logger import setup_logger
from ..core.config import settings
from ..models.database import get_db
from ..models.user import UserModel
from ..models.knowledge import QuizResultModel, LearningRecordModel
from .auth import require_teacher

logger = setup_logger()
router = APIRouter()

# ---------------------------------------------------------------------------
# LLM 响应缓存（简单内存缓存，TTL 10分钟）
# ---------------------------------------------------------------------------
_LLM_CACHE: Dict[str, tuple] = {}  # key -> (result, timestamp)
_CACHE_TTL = 600  # 10分钟

def _get_cache_key(messages: List[Dict]) -> str:
    """生成缓存 key"""
    content = json.dumps(messages, ensure_ascii=False, sort_keys=True)
    return hashlib.md5(content.encode()).hexdigest()

def _get_cached(messages: List[Dict]) -> Optional[Dict]:
    """获取缓存"""
    key = _get_cache_key(messages)
    if key in _LLM_CACHE:
        result, ts = _LLM_CACHE[key]
        if time.time() - ts < _CACHE_TTL:
            return result
        del _LLM_CACHE[key]
    return None

def _set_cache(messages: List[Dict], result: Dict):
    """设置缓存"""
    key = _get_cache_key(messages)
    _LLM_CACHE[key] = (result, time.time())
    # 清理过期缓存
    if len(_LLM_CACHE) > 100:
        now = time.time()
        expired = [k for k, (_, ts) in _LLM_CACHE.items() if now - ts >= _CACHE_TTL]
        for k in expired:
            del _LLM_CACHE[k]

# ---------------------------------------------------------------------------
# Prompt 模板（精简版，提升响应速度）
# ---------------------------------------------------------------------------

LESSON_PLAN_SYSTEM = """你是AI教研助手。返回JSON格式备课方案。

输出格式（只返回JSON）:
{
    "title": "课程标题",
    "teaching_objectives": {
        "knowledge": ["知识目标"],
        "ability": ["能力目标"],
        "emotion": ["情感目标"]
    },
    "key_points": ["教学重点"],
    "difficult_points": ["教学难点"],
    "teaching_process": [
        {"phase": "阶段", "duration": "时间", "activities": ["活动"], "teacher_behavior": "教师行为", "student_behavior": "学生行为"}
    ],
    "methods": ["教学方法"],
    "time_distribution": {"导入": 5, "新授": 20, "巩固": 10, "小结": 5, "作业": 5},
    "board_design": "板书设计(Markdown)",
    "reflection_hints": ["反思要点"],
    "resources_needed": ["所需资源"]
}"""

INSIGHTS_SYSTEM = """你是学情分析专家。根据班级数据生成叙事报告。

输出格式（只返回JSON）:
{
    "title": "报告标题",
    "date": "日期",
    "overview": "总览(100字内)",
    "sections": [
        {"title": "板块", "content": "内容(Markdown)", "data_highlights": ["数据点"], "icon": "图标"}
    ],
    "key_findings": ["发现1", "发现2"],
    "recommendations": [{"target": "对象", "action": "建议", "priority": "high/medium/low"}],
    "risk_students": ["风险学生"],
    "star_students": ["优秀学生"],
    "mood": "positive/neutral/concerned"
}"""

SMART_QUIZ_SYSTEM = """你是智能组卷专家。根据主题生成试卷。

输出格式（只返回JSON）:
{
    "title": "试卷标题",
    "subject": "科目",
    "total_score": 100,
    "time_limit": "45分钟",
    "questions": [
        {
            "id": 1,
            "type": "choice/fill/short_answer/comprehensive",
            "difficulty": "basic/intermediate/advanced",
            "score": 5,
            "question": "题目",
            "options": ["A. 选项1", "B. 选项2", "C. 选项3", "D. 选项4"],
            "answer": "答案",
            "explanation": "解析",
            "knowledge_point": "知识点"
        }
    ],
    "difficulty_distribution": {"basic": "40%", "intermediate": "40%", "advanced": "20%"},
    "knowledge_coverage": ["知识点"]
}"""

# ---------------------------------------------------------------------------
# 请求模型
# ---------------------------------------------------------------------------

class LessonPlanRequest(BaseModel):
    topic: str = Field(..., max_length=200, description="教学主题")
    style: str = Field("探究式", max_length=50, description="教学风格")


class SmartQuizRequest(BaseModel):
    topic: str = Field(..., max_length=200, description="教学主题")
    knowledge_points: List[str] = Field(default_factory=list, description="知识点列表")
    difficulty: str = Field("mixed", max_length=20, description="难度: mixed/basic/intermediate/advanced")
    count: int = Field(5, ge=1, le=20, description="题目数量")


# ---------------------------------------------------------------------------
# 辅助函数
# ---------------------------------------------------------------------------

def _get_llm():
    from ..services.llm_factory import LLMFactory
    return LLMFactory.get_default_llm()


async def _get_class_teaching_data(db: Session) -> Dict[str, Any]:
    """聚合班级学情数据，用于喂给LLM"""
    students = db.query(UserModel).filter(UserModel.role == "student").all()
    student_ids = [s.student_id for s in students]
    student_names = {s.student_id: s.username for s in students}

    quiz_stats = {}
    progress_stats = {}

    if student_ids:
        # 测验统计
        rows = (
            db.query(
                QuizResultModel.student_id,
                func.sum(QuizResultModel.total_questions).label("total"),
                func.sum(QuizResultModel.correct_count).label("correct"),
            )
            .filter(QuizResultModel.student_id.in_(student_ids))
            .group_by(QuizResultModel.student_id)
            .all()
        )
        for row in rows:
            total = row.total or 0
            correct = row.correct or 0
            quiz_stats[row.student_id] = {
                "total": total,
                "correct": correct,
                "accuracy": round(correct / total * 100, 1) if total > 0 else 0,
            }

        # 学习进度
        rows2 = (
            db.query(
                LearningRecordModel.student_id,
                func.count().label("records_count"),
                func.max(LearningRecordModel.created_at).label("last_active"),
            )
            .filter(LearningRecordModel.student_id.in_(student_ids))
            .group_by(LearningRecordModel.student_id)
            .all()
        )
        for row in rows2:
            progress_stats[row.student_id] = {
                "records_count": row.records_count or 0,
                "last_active": str(row.last_active) if row.last_active else None,
            }

    total_students = len(students)
    active = sum(1 for sid in student_ids if progress_stats.get(sid, {}).get("records_count", 0) > 0)
    accuracies = [v["accuracy"] for v in quiz_stats.values() if v["accuracy"] > 0]

    return {
        "total_students": total_students,
        "student_names": student_names,
        "quiz_stats": quiz_stats,
        "progress_stats": progress_stats,
        "summary": {
            "avg_accuracy": round(sum(accuracies) / len(accuracies), 1) if accuracies else 0,
            "active_students": active,
            "inactive_students": total_students - active,
            "total_quizzes": sum(v["total"] for v in quiz_stats.values()),
        },
    }


# ---------------------------------------------------------------------------
# API 端点
# ---------------------------------------------------------------------------

@router.post("/lesson-plan")
async def generate_lesson_plan(
    request: LessonPlanRequest,
    _current: str = Depends(require_teacher),
):
    """AI智能备课"""
    try:
        llm = _get_llm()
        messages = [
            {"role": "system", "content": LESSON_PLAN_SYSTEM},
            {"role": "user", "content": f"主题：{request.topic}，风格：{request.style}"},
        ]
        # 检查缓存
        cached = _get_cached(messages)
        if cached:
            return {"status": "success", "data": cached}
        result = await llm.generate_json(messages, temperature=0.3, max_tokens=2048)
        if result.get("status") == "error":
            return {"status": "success", "data": {"plan_text": result.get("raw_text", ""), "format": "markdown"}}
        _set_cache(messages, result)
        return {"status": "success", "data": result}
    except Exception as e:
        logger.error(f"Lesson plan generation failed: {e}")
        raise HTTPException(status_code=500, detail="备课方案生成失败，请稍后重试")


@router.post("/insights")
async def generate_insights(
    db: Session = Depends(get_db),
    _current: str = Depends(require_teacher),
):
    """AI学情洞察报告"""
    try:
        class_data = await _get_class_teaching_data(db)
        llm = _get_llm()
        messages = [
            {"role": "system", "content": INSIGHTS_SYSTEM},
            {"role": "user", "content": f"班级数据：{json.dumps(class_data, ensure_ascii=False, default=str)}"},
        ]
        # 检查缓存（insights 数据变化快，缓存时间短）
        cached = _get_cached(messages)
        if cached:
            return {"status": "success", "data": cached}
        result = await llm.generate_json(messages, temperature=0.3, max_tokens=2048)
        if result.get("status") == "error":
            return {"status": "success", "data": {"narrative": result.get("raw_text", ""), "format": "markdown"}}
        _set_cache(messages, result)
        return {"status": "success", "data": result}
    except Exception as e:
        logger.error(f"Insights generation failed: {e}")
        raise HTTPException(status_code=500, detail="学情洞察报告生成失败，请稍后重试")


@router.post("/smart-quiz")
async def generate_smart_quiz(
    request: SmartQuizRequest,
    _current: str = Depends(require_teacher),
):
    """AI智能组卷"""
    try:
        kp_text = "、".join(request.knowledge_points) if request.knowledge_points else "自动"
        llm = _get_llm()
        messages = [
            {"role": "system", "content": SMART_QUIZ_SYSTEM},
            {"role": "user", "content": f"主题：{request.topic}，知识点：{kp_text}，难度：{request.difficulty}，数量：{request.count}题"},
        ]
        # 检查缓存
        cached = _get_cached(messages)
        if cached:
            return {"status": "success", "data": cached}
        result = await llm.generate_json(messages, temperature=0.3, max_tokens=2048)
        if result.get("status") == "error":
            return {"status": "success", "data": {"questions_text": result.get("raw_text", ""), "format": "markdown"}}
        _set_cache(messages, result)
        return {"status": "success", "data": result}
    except Exception as e:
        logger.error(f"Smart quiz generation failed: {e}")
        raise HTTPException(status_code=500, detail="智能组卷失败，请稍后重试")
