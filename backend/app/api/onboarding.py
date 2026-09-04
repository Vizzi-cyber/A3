"""
引导问卷 API
首次登录时收集用户信息，生成初始学习路径
"""
import asyncio
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional
from sqlalchemy.orm import Session

from ..core.logger import setup_logger

logger = setup_logger()

from ..models.database import get_db
from ..models.student import StudentProfileModel
from ..models.path_adjustment_log import PathAdjustmentLogModel
from ..models.knowledge import KnowledgePointModel, LearningRecordModel
from ..agents import PathPlannerAgent
from ..algorithms import DAGPathPlanner
from .auth import require_auth

router = APIRouter()

_path_planner_agent = PathPlannerAgent()


class OnboardingAnswers(BaseModel):
    """引导问卷答案"""
    c_knowledge_level: int = Field(..., ge=1, le=5, description="C语言基础水平: 1=零基础, 5=较熟悉")
    difficulty_preference: int = Field(..., ge=1, le=10, description="难度偏好: 1=轻松, 10=挑战")
    daily_duration: int = Field(..., ge=15, le=240, description="每日学习时长(分钟)")
    learning_goal: str = Field(..., description="学习目标: exam_prep/skill_build/project/exploration")
    learning_style: str = Field(..., description="学习风格: theory/practice/balanced")


@router.get("/check")
async def check_onboarding(db: Session = Depends(get_db), _current: str = Depends(require_auth)):
    """检查是否已完成引导问卷"""
    profile = db.query(StudentProfileModel).filter(
        StudentProfileModel.student_id == _current
    ).first()
    completed = profile.onboarding_completed if profile else False
    return {"status": "success", "completed": completed}


@router.post("/submit")
async def submit_onboarding(
    answers: OnboardingAnswers,
    db: Session = Depends(get_db),
    _current: str = Depends(require_auth),
):
    """提交引导问卷，更新画像并生成初始路径"""
    profile = db.query(StudentProfileModel).filter(
        StudentProfileModel.student_id == _current
    ).first()
    if not profile:
        profile = StudentProfileModel(student_id=_current)
        db.add(profile)

    # 根据答案更新画像
    # 知识基础
    knowledge_score = answers.c_knowledge_level / 5.0 * 0.8 + 0.1
    profile.knowledge_base = {
        **(profile.knowledge_base or {}),
        "overall_score": knowledge_score,
        "academic_level": ["零基础", "入门", "基础", "进阶", "熟练"][answers.c_knowledge_level - 1],
    }

    # 学习节奏
    study_speed = "slow" if answers.c_knowledge_level <= 2 else ("moderate" if answers.c_knowledge_level <= 3 else "fast")
    profile.learning_tempo = {
        **(profile.learning_tempo or {}),
        "study_speed": study_speed,
        "optimal_session_duration": min(answers.daily_duration, 90),
        "weekly_study_capacity": answers.daily_duration * 5 / 60,
    }

    # 认知风格
    style_map = {"theory": "reading", "practice": "kinesthetic", "balanced": "visual"}
    profile.cognitive_style = {
        **(profile.cognitive_style or {}),
        "primary": style_map.get(answers.learning_style, "visual"),
    }

    # 学习目标
    goal_map = {
        "exam_prep": "考试备考",
        "skill_build": "技能提升",
        "project": "项目实战",
        "exploration": "探索兴趣",
    }
    profile.learning_goals = [goal_map.get(answers.learning_goal, "技能提升")]

    # 实践偏好
    practice_score = 0.3 if answers.learning_style == "theory" else (0.7 if answers.learning_style == "practice" else 0.5)
    profile.practical_preferences = {
        **(profile.practical_preferences or {}),
        "overall_score": practice_score,
    }

    profile.onboarding_completed = True
    db.commit()

    # 生成初始路径
    path_data = None

    # 尝试 LLM 路径规划
    try:
        result = await asyncio.wait_for(
            _path_planner_agent.process({
                "task": "generate_path",
                "student_id": _current,
                "profile": {
                    "learning_tempo": profile.learning_tempo,
                    "weak_areas": profile.weak_areas or [],
                    "knowledge_level": answers.difficulty_preference,
                    "preference": answers.learning_style,
                },
                "target": "掌握 C语言程序设计与数据结构基础",
            }),
            timeout=10.0,
        )
        raw_path = result.get("path", {}) if isinstance(result, dict) else {}
        if raw_path and raw_path.get("stages"):
            path_data = raw_path
    except asyncio.TimeoutError:
        logger.warning(f"引导问卷路径规划超时: student_id={_current}")
    except Exception as e:
        logger.warning(f"引导问卷路径规划异常: {e}")

    # 降级到 DAG 算法
    if not path_data:
        kps = db.query(KnowledgePointModel).all()
        if kps:
            planner = DAGPathPlanner()
            planner.build_graph([
                {
                    "kp_id": k.kp_id,
                    "name": k.name,
                    "subject": k.subject,
                    "difficulty": k.difficulty,
                    "prerequisites": k.prerequisites or [],
                    "description": k.description,
                    "tags": k.tags,
                }
                for k in kps
            ])
            # AIC 算法增强：IRT 已拟合时学习成本模型的难度系数用标定 b 值
            try:
                from ..services.algorithm_registry import attach_irt_to_planner
                attach_irt_to_planner(planner)
            except Exception:
                pass
            target_kp_id = kps[-1].kp_id
            from datetime import datetime, timedelta, timezone
            from sqlalchemy import func
            since = datetime.now(timezone.utc) - timedelta(days=365)
            mastery_rows = (
                db.query(LearningRecordModel.kp_id, func.max(LearningRecordModel.progress).label("max_progress"))
                .filter(
                    LearningRecordModel.student_id == _current,
                    LearningRecordModel.created_at >= since,
                )
                .group_by(LearningRecordModel.kp_id)
                .all()
            )
            mastery_map = {row.kp_id: row.max_progress or 0.0 for row in mastery_rows}
            dag_result = planner.plan_path(
                student_id=_current,
                target_kp_id=target_kp_id,
                mastery_map=mastery_map,
                profile={
                    "weak_areas": profile.weak_areas or [],
                    "knowledge_level": answers.difficulty_preference,
                },
            )
            stages = []
            stage_names = ["基础巩固", "核心知识", "进阶深化", "综合实战"]
            for idx, stage in enumerate(dag_result.get("stages", [])):
                stages.append({
                    "stage_no": idx + 1,
                    "title": stage.get("title") or (stage_names[idx] if idx < len(stage_names) else f"阶段 {idx + 1}"),
                    "topics": stage.get("topics", stage.get("kp_ids", [])),
                    "hours": stage.get("hours", 5),
                    "criteria": stage.get("criteria", "完成本阶段所有知识点学习"),
                    "resources": stage.get("resources", []),
                })
            if stages:
                path_data = {
                    "target": "掌握 C语言程序设计与数据结构基础",
                    "estimated_total_hours": sum(s.get("hours", 5) for s in stages),
                    "stages": stages,
                }

    # 兜底默认路径
    if not path_data:
        path_data = {
            "target": "掌握 C语言程序设计与数据结构基础",
            "estimated_total_hours": 20,
            "stages": [
                {"stage_no": 1, "title": "基础入门与概念理解", "topics": ["C语言概述", "数据类型与变量"], "hours": 5, "criteria": "理解基本概念", "resources": ["文档", "视频"]},
                {"stage_no": 2, "title": "核心技能与知识深化", "topics": ["控制结构", "数组与字符串", "函数"], "hours": 5, "criteria": "独立完成练习", "resources": ["教程", "文档"]},
                {"stage_no": 3, "title": "实践应用与项目实战", "topics": ["指针与内存管理", "结构体"], "hours": 5, "criteria": "完成小型项目", "resources": ["项目案例", "代码仓库"]},
                {"stage_no": 4, "title": "高级主题与综合提升", "topics": ["文件操作", "预处理", "动态内存"], "hours": 5, "criteria": "理解高级特性", "resources": ["高级书籍", "技术博客"]},
            ],
        }

    # 记录调整日志
    log_entry = PathAdjustmentLogModel(
        student_id=_current,
        trigger_type="onboarding",
        trigger_source="user_onboarding",
        reason=f"用户完成引导问卷，C语言基础={answers.c_knowledge_level}级，难度偏好={answers.difficulty_preference}，学习风格={answers.learning_style}",
        new_path_snapshot=path_data,
        confidence=0.8,
    )
    db.add(log_entry)
    db.commit()

    return {
        "status": "success",
        "data": {
            "path": path_data,
            "profile": {
                "knowledge_base": profile.knowledge_base,
                "learning_tempo": profile.learning_tempo,
                "cognitive_style": profile.cognitive_style,
                "learning_goals": profile.learning_goals,
                "practical_preferences": profile.practical_preferences,
            },
        },
    }
