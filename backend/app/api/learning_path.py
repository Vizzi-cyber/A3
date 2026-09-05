"""
学习路径API
对接 LangGraph 工作流，调用 path_planner 智能体
集成 DAG 路径规划算法
"""
import asyncio
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

from ..core.logger import setup_logger

logger = setup_logger()

from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta, timezone
from ..models.database import get_db
from ..models.knowledge import KnowledgePointModel, LearningRecordModel
from ..models.student import StudentProfileModel
from ..models.course import CourseModel
from ..models.path_adjustment_log import PathAdjustmentLogModel
from ..algorithms import DAGPathPlanner
from ..services.algorithm_registry import (
    get_bkt_engine,
    get_strategy_bandit,
    update_strategy_bandit,
    attach_irt_to_planner,
    attach_gkt_to_planner,
)
from ..agents import PathPlannerAgent
from .auth import get_current_student_id, require_auth

router = APIRouter()

_path_planner_agent = PathPlannerAgent()


class PathGenerationRequest(BaseModel):
    """路径生成请求"""
    student_id: str
    target_topic: str = Field(..., max_length=500)
    current_knowledge: Optional[List[str]] = None
    time_constraint: Optional[int] = Field(None, ge=1, le=365)
    preference: Optional[str] = None
    daily_duration: Optional[int] = Field(None, ge=1, le=480)
    difficulty: Optional[int] = Field(None, ge=1, le=10)
    subject: Optional[str] = None


class PathAdjustmentRequest(BaseModel):
    """路径调整请求"""
    feedback: str
    current_path: Optional[Dict[str, Any]] = None


class DAGPathRequest(BaseModel):
    """DAG路径规划请求"""
    student_id: str
    target_kp_id: str
    mastery_map: Optional[Dict[str, float]] = None


class DAGPathAdjustRequest(BaseModel):
    """DAG路径动态调整请求"""
    student_id: str
    current_path: Dict[str, Any]
    quiz_result: Dict[str, Any]
    trend_state: str = "stable"


@router.post("/generate")
async def generate_learning_path(request: PathGenerationRequest, db: Session = Depends(get_db), _current: str = Depends(require_auth)):
    """生成个性化学习路径 —— 直接调用 PathPlannerAgent，避免 LangGraph 多层路由延迟"""
    if request.student_id != _current:
        raise HTTPException(status_code=403, detail="Cannot generate path for other student")

    # 加载学生画像用于个性化
    profile = db.query(StudentProfileModel).filter(StudentProfileModel.student_id == request.student_id).first()
    # daily_duration 前端传来的是分钟，转换为小时
    daily_hours = (request.daily_duration or 60) / 60.0
    weekly_study_capacity = max(1, round(daily_hours * 7))
    profile_dict = {
        "learning_tempo": {"weekly_study_capacity": weekly_study_capacity},
        "weak_areas": profile.weak_areas or [] if profile else [],
        "knowledge_level": request.difficulty or 3,
        "preference": request.preference or "balanced",
    } if profile else {
        "learning_tempo": {"weekly_study_capacity": weekly_study_capacity},
        "preference": request.preference or "balanced",
    }

    try:
        result = await asyncio.wait_for(
            _path_planner_agent.process({
                "task": "generate_path",
                "student_id": request.student_id,
                "profile": profile_dict,
                "target": request.target_topic,
            }),
            timeout=10.0,
        )
        raw_path = result.get("path", {}) if isinstance(result, dict) else {}
    except asyncio.TimeoutError:
        logger.warning(f"路径规划超时: student_id={request.student_id}")
        raw_path = {}
    except Exception as e:
        logger.warning(f"路径规划异常: {e}")
        raw_path = {}

    # 如果 agent 失败或超时，使用 DAG 算法生成路径
    if not raw_path or not raw_path.get("stages"):
        kp_query = db.query(KnowledgePointModel)
        if request.subject:
            COURSE_NAMES = {"C语言", "电路分析", "STM32嵌入式"}
            if request.subject in COURSE_NAMES:
                kp_query = kp_query.filter(KnowledgePointModel.course == request.subject)
            else:
                kp_query = kp_query.filter(KnowledgePointModel.subject == request.subject)
        kps = kp_query.all()
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
            # 默认目标为最后一个知识点
            target_text = (request.target_topic or "").lower()
            target_match = next((k for k in kps if target_text and (target_text in (k.name or "").lower() or target_text == k.kp_id.lower())), None)
            target_kp_id = (target_match or kps[-1]).kp_id
            # 使用聚合查询直接获取每个知识点的最大进度，避免加载全部记录
            since = datetime.now(timezone.utc) - timedelta(days=365)
            mastery_rows = (
                db.query(LearningRecordModel.kp_id, func.max(LearningRecordModel.progress).label("max_progress"))
                .filter(
                    LearningRecordModel.student_id == request.student_id,
                    LearningRecordModel.created_at >= since,
                )
                .group_by(LearningRecordModel.kp_id)
                .all()
            )
            mastery_map = {row.kp_id: row.max_progress or 0.0 for row in mastery_rows}
            kp_ids = {k.kp_id for k in kps}
            for kp_id in (request.current_knowledge or []):
                if kp_id in kp_ids:
                    mastery_map[kp_id] = 1.0
            # AIC 算法增强：若完整 BKT 已拟合，注入 BKT 引擎（掌握度用 EM 参数化预测，
            # 替代画像快照；未拟合时保持原逻辑，向后兼容）；IRT/GKT 同理注入
            bkt_engine = get_bkt_engine()
            if bkt_engine is not None and bkt_engine.is_fitted:
                planner.set_bkt_engine(bkt_engine)
            attach_irt_to_planner(planner)
            attach_gkt_to_planner(planner)
            dag_result = planner.plan_path(
                student_id=request.student_id,
                target_kp_id=target_kp_id,
                mastery_map=mastery_map,
                profile=profile_dict,
            )
            # 将 DAG 结果转换为前端期望的 stages 格式
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
                raw_path = {
                    "target": request.target_topic,
                    "estimated_total_hours": sum(s.get("hours", 5) for s in stages),
                    "stages": stages,
                }

    # 默认路径根据课程动态生成
    subject = request.subject or "C语言"
    if not raw_path or not raw_path.get("stages"):
        # 查询该课程的知识点，按顺序生成默认路径
        COURSE_NAMES = {"C语言", "电路分析", "STM32嵌入式"}
        if subject in COURSE_NAMES:
            fallback_kps = db.query(KnowledgePointModel).filter(KnowledgePointModel.course == subject).order_by(KnowledgePointModel.created_at.asc()).all()
        else:
            fallback_kps = db.query(KnowledgePointModel).filter(KnowledgePointModel.subject == subject).order_by(KnowledgePointModel.created_at.asc()).all()
        if fallback_kps:
            # 按4个阶段分配知识点
            chunk_size = max(1, len(fallback_kps) // 4)
            stage_names = ["基础入门与概念理解", "核心技能与知识深化", "实践应用与项目实战", "高级主题与综合提升"]
            fallback_stages = []
            for i in range(4):
                start_idx = i * chunk_size
                end_idx = start_idx + chunk_size if i < 3 else len(fallback_kps)
                chunk_kps = fallback_kps[start_idx:end_idx]
                if chunk_kps:
                    fallback_stages.append({
                        "stage_no": i + 1,
                        "title": stage_names[i] if i < len(stage_names) else f"阶段 {i + 1}",
                        "topics": [k.name for k in chunk_kps],
                        "hours": 5,
                        "criteria": "完成本阶段所有知识点的学习。",
                        "resources": ["图文讲义", "练习题", "思维导图"],
                    })
            raw_path = {
                "target": request.target_topic,
                "estimated_total_hours": sum(s.get("hours", 5) for s in fallback_stages),
                "stages": fallback_stages,
            }

    if not raw_path or not raw_path.get("stages"):
        raise HTTPException(status_code=404, detail="No learning path can be generated from available knowledge and records")
    path_data = raw_path
    '''
        "estimated_total_hours": 20,
        "stages": [
            {
                "stage_no": 1,
                "title": "基础入门与概念理解",
                "topics": [f"{subject}基础概念", "入门知识"],
                "hours": 5,
                "criteria": "能够清晰阐述基本概念，并成功搭建学习环境。",
                "resources": ["官方入门指南", "结构化在线课程"],
            },
            {
                "stage_no": 2,
                "title": "核心技能与知识深化",
                "topics": [f"{subject}核心知识", "重点内容"],
                "hours": 5,
                "criteria": "能够独立运用核心功能解决中等难度的练习题。",
                "resources": ["进阶教程或书籍", "官方技术文档"],
            },
            {
                "stage_no": 3,
                "title": "实践应用与项目实战",
                "topics": [f"{subject}实践", "综合应用"],
                "hours": 5,
                "criteria": "能够独立完成一个功能完整的小型项目。",
                "resources": ["项目案例库", "开源代码仓库"],
            },
            {
                "stage_no": 4,
                "title": "高级主题与综合提升",
                "topics": [f"{subject}高级主题", "综合提升"],
                "hours": 5,
                "criteria": "能够理解并应用高级特性，对项目进行性能优化。",
                "resources": ["高级技术书籍或论文", "技术博客与会议演讲"],
            },
        ],
    }'''

    return {
        "status": "success",
        "data": {
            "path_id": f"path_{request.student_id}",
            "student_id": request.student_id,
            "path": path_data,
        },
    }


@router.get("/{student_id}/current")
async def get_current_path(
    student_id: str,
    subject: Optional[str] = Query(None, description="课程名称，如 C语言 或 电路分析"),
    db: Session = Depends(get_db),
    _current: str = Depends(require_auth),
):
    """获取当前学习路径 —— 基于数据库知识点动态构建"""
    if student_id != _current:
        raise HTTPException(status_code=403, detail="Cannot view other student's path")
    query = db.query(KnowledgePointModel)
    if subject:
        COURSE_NAMES = {"C语言", "电路分析", "STM32嵌入式"}
        if subject in COURSE_NAMES:
            query = query.filter(KnowledgePointModel.course == subject)
        else:
            query = query.filter(KnowledgePointModel.subject == subject)
    kps = query.order_by(KnowledgePointModel.created_at.asc()).all()
    # 使用聚合查询计算每个KP的最大进度，避免加载全部记录
    since = datetime.now(timezone.utc) - timedelta(days=365)
    progress_rows = (
        db.query(LearningRecordModel.kp_id, func.max(LearningRecordModel.progress).label("max_progress"))
        .filter(
            LearningRecordModel.student_id == student_id,
            LearningRecordModel.created_at >= since,
        )
        .group_by(LearningRecordModel.kp_id)
        .all()
    )
    kp_progress: Dict[str, float] = {row.kp_id: row.max_progress or 0.0 for row in progress_rows}

    nodes = []
    for idx, kp in enumerate(kps):
        progress = kp_progress.get(kp.kp_id, 0.0)
        if progress >= 0.8:
            status = "completed"
        elif progress > 0:
            status = "in-progress"
        else:
            # 如果前置知识点都完成了，则pending；否则locked
            prereqs = kp.prerequisites or []
            if prereqs and any(kp_progress.get(p, 0.0) < 0.8 for p in prereqs):
                status = "locked"
            else:
                status = "pending"
        nodes.append({
            "id": idx + 1,
            "kp_id": kp.kp_id,
            "title": kp.name,
            "status": status,
            "type": kp.subject or "核心",
            "resources": 5,
        })

    completed_count = sum(1 for n in nodes if n["status"] == "completed")
    in_progress_count = sum(1 for n in nodes if n["status"] == "in-progress")
    current_step = completed_count + (1 if in_progress_count > 0 else 0)
    next_node = next((n for n in nodes if n["status"] in ("in-progress", "pending")), None)

    return {
        "status": "success",
        "student_id": student_id,
        "current_step": current_step,
        "progress": round(completed_count / len(nodes), 2) if nodes else 0,
        "next_task": {
            "kp_id": next_node["kp_id"] if next_node else "",
            "name": next_node["title"] if next_node else "暂无",
            "action": "继续学习",
        },
        "nodes": nodes,
    }


# ---------- DAG 路径规划算法接口 ----------
# 注意：/dag/* 路由必须先于 /{student_id}/adjust 声明——FastAPI 按声明顺序匹配，
# 否则 /dag/adjust 会被 /{student_id}/adjust 遮蔽（student_id="dag"）导致不可达。

@router.post("/dag/generate")
async def generate_dag_path(request: DAGPathRequest, db: Session = Depends(get_db), _current: str = Depends(require_auth)):
    """基于DAG生成学习路径"""
    if request.student_id != _current:
        raise HTTPException(status_code=403, detail="Cannot generate path for other student")
    # 查询所有知识点构建图
    kps = db.query(KnowledgePointModel).all()
    if not kps:
        raise HTTPException(status_code=400, detail="No knowledge points available")

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
    # AIC 算法增强：IRT 已拟合时学习成本模型的难度系数用标定 b 值；
    # GKT 已训练时掌握度做图卷积传播
    attach_irt_to_planner(planner)
    attach_gkt_to_planner(planner)

    # 检测环
    cycles = planner.detect_cycles()
    if cycles:
        raise HTTPException(status_code=400, detail=f"Knowledge graph contains cycles: {cycles}")

    profile = db.query(StudentProfileModel).filter(StudentProfileModel.student_id == request.student_id).first()
    profile_dict = {
        "weak_areas": profile.weak_areas or [] if profile else [],
    }

    mastery_map = request.mastery_map or {}
    result = planner.plan_path(
        student_id=request.student_id,
        target_kp_id=request.target_kp_id,
        mastery_map=mastery_map,
        profile=profile_dict,
    )
    return {"status": "success", "data": result}


@router.post("/dag/adjust")
async def adjust_dag_path(request: DAGPathAdjustRequest, db: Session = Depends(get_db), _current: str = Depends(require_auth)):
    """动态调整DAG路径

    AIC 算法增强：Thompson Sampling 策略选择。
    - request.quiz_result 可携带上一轮调整的 prev_strategy + reward（0-1，
      如下次测验提分比例），用于反馈更新该学生的策略 MAB（闭环）
    - 候选策略集由分数段保底，累计反馈达臂数后 MAB 在候选集内接管决策
    """
    if request.student_id != _current:
        raise HTTPException(status_code=403, detail="Cannot adjust other student's path")

    quiz_result = dict(request.quiz_result or {})
    # 闭环反馈：先回传上一轮策略的实际收益，再执行本轮调整
    prev_strategy = quiz_result.pop("prev_strategy", None)
    reward = quiz_result.pop("reward", None)
    if prev_strategy and reward is not None:
        try:
            update_strategy_bandit(request.student_id, str(prev_strategy), float(reward))
        except Exception:
            pass

    planner = DAGPathPlanner()
    result = planner.adjust_path(
        current_path=request.current_path,
        quiz_result=quiz_result,
        trend_state=request.trend_state,
        bandit_selector=get_strategy_bandit(request.student_id),
    )
    db.add(PathAdjustmentLogModel(student_id=request.student_id, trigger_type="auto", trigger_source="quiz_result", reason="DAG adjustment", old_path_snapshot=request.current_path, new_path_snapshot=result, confidence=1.0))
    db.commit()
    return {"status": "success", "data": result}


@router.post("/{student_id}/adjust")
async def adjust_path(
    student_id: str, adjustment: PathAdjustmentRequest, db: Session = Depends(get_db), _current: str = Depends(require_auth)
):
    """调整学习路径 —— 直接调用 PathPlannerAgent

    （声明顺序在 /dag/adjust 之后：避免通配路由遮蔽具体路由）
    """
    if student_id != _current:
        raise HTTPException(status_code=403, detail="Cannot adjust other student's path")
    path_data = adjustment.current_path or {}

    try:
        result = await asyncio.wait_for(
            _path_planner_agent.process({
                "task": "adjust_path",
                "student_id": student_id,
                "current_path": adjustment.current_path or {},
                "feedback": adjustment.feedback,
            }),
            timeout=15.0,
        )
        if result.get("status") == "success":
            raw = result.get("path", {})
            if raw and raw.get("stages"):
                path_data = raw
    except asyncio.TimeoutError:
        logger.warning(f"路径调整超时: student_id={student_id}")
    except Exception as e:
        logger.warning(f"路径调整异常: {e}")

    db.add(PathAdjustmentLogModel(student_id=student_id, trigger_type="manual", trigger_source="user_feedback", reason=adjustment.feedback, old_path_snapshot=adjustment.current_path or {}, new_path_snapshot=path_data, confidence=1.0 if path_data.get("stages") else 0.0))
    db.commit()
    return {
        "status": "success",
        "message": "Path adjusted",
        "data": path_data,
    }


@router.get("/dag/dependency-chain/{target_kp_id}")
async def get_dependency_chain(target_kp_id: str, db: Session = Depends(get_db), _current: str = Depends(require_auth)):
    """获取目标知识点的完整依赖链"""
    kps = db.query(KnowledgePointModel).all()
    planner = DAGPathPlanner()
    planner.build_graph([
        {
            "kp_id": k.kp_id,
            "name": k.name,
            "prerequisites": k.prerequisites or [],
        }
        for k in kps
    ])
    chain = planner._get_dependency_chain(target_kp_id)
    return {
        "status": "success",
        "target_kp_id": target_kp_id,
        "dependency_chain": chain,
        "chain_length": len(chain),
    }


# ---------- 跨学科学习链路（AIC 算法创新赛 · AI+学科交叉） ----------

@router.get("/courses")
async def list_courses(db: Session = Depends(get_db), _current: str = Depends(require_auth)):
    """学科课程元数据列表（含跨课程知识关联统计，支撑学科交叉定位）"""
    courses = db.query(CourseModel).all()
    kps = db.query(KnowledgePointModel).all()

    # 跨课程关联统计：目标课程内有多少知识点引用了其他课程的前置
    cross_stats: Dict[str, dict] = {}
    for kp in kps:
        prereqs = kp.prerequisites or []
        cross = [p for p in prereqs if p[:3] == "kp_" and p[3] != kp.kp_id[3]]
        if cross:
            stat = cross_stats.setdefault(kp.course, {"cross_count": 0, "cross_links": []})
            stat["cross_count"] += len(cross)
            stat["cross_links"].append({"kp_id": kp.kp_id, "name": kp.name, "prerequisites": cross})

    result = []
    for c in courses:
        stat = cross_stats.get(c.course_id, {"cross_count": 0, "cross_links": []})
        result.append({
            "course_id": c.course_id,
            "name": c.name,
            "discipline": c.discipline,
            "core_phases": c.core_phases or [],
            "description": c.description,
            "icon": c.icon,
            "color": c.color,
            "linked_courses": c.linked_courses or [],
            "cross_count": stat["cross_count"],
            "cross_links": stat["cross_links"],
        })
    return {"status": "success", "data": result}


class CrossDisciplinePathRequest(BaseModel):
    """跨学科综合路径请求"""
    student_id: str
    target_kp_id: str          # 跨学科目标知识点（如 kp_s05 定时器与PWM）
    mastery_map: Optional[Dict[str, float]] = None


@router.post("/cross-discipline")
async def generate_cross_discipline_path(
    request: CrossDisciplinePathRequest,
    db: Session = Depends(get_db),
    _current: str = Depends(require_auth),
):
    """跨学科综合学习路径：基于跨课程知识关联 DAG 生成路径

    核心价值：目标知识点（如 STM32 定时器PWM）的前置依赖链可跨越
    C语言（位运算/指针）与电路分析（电压波形）两门课程，
    体现"编程思维 → 电路建模 → 嵌入式实现"的跨学科学习链路。
    """
    if request.student_id != _current:
        raise HTTPException(status_code=403, detail="Cannot generate path for other student")

    kps = db.query(KnowledgePointModel).all()
    if not kps:
        raise HTTPException(status_code=400, detail="No knowledge points available")

    planner = DAGPathPlanner()
    planner.build_graph([
        {
            "kp_id": k.kp_id,
            "name": k.name,
            "subject": k.subject,
            "course": k.course,
            "difficulty": k.difficulty,
            "prerequisites": k.prerequisites or [],
            "description": k.description,
            "tags": k.tags,
        }
        for k in kps
    ])

    cycles = planner.detect_cycles()
    if cycles:
        raise HTTPException(status_code=400, detail=f"Knowledge graph contains cycles: {cycles}")

    profile = db.query(StudentProfileModel).filter(StudentProfileModel.student_id == request.student_id).first()
    profile_dict = {
        "weak_areas": profile.weak_areas or [] if profile else [],
        "learning_tempo": profile.learning_tempo or {} if profile else {},
        "preference": getattr(profile, "preference", None) or "balanced",
    }

    result = planner.plan_path(
        student_id=request.student_id,
        target_kp_id=request.target_kp_id,
        mastery_map=request.mastery_map or {},
        profile=profile_dict,
    )
    if result.get("status") != "success":
        raise HTTPException(status_code=400, detail=result.get("message", "路径生成失败"))

    # 跨学科统计：按课程统计路径中的知识点分布
    course_stats: Dict[str, int] = {}
    for stage in result.get("stages", []):
        for kp_id in stage.get("kp_ids", []):
            kp = next((k for k in kps if k.kp_id == kp_id), None)
            if kp:
                course_stats[kp.course] = course_stats.get(kp.course, 0) + 1

    target = db.query(KnowledgePointModel).filter(KnowledgePointModel.kp_id == request.target_kp_id).first()
    result["cross_discipline"] = {
        "target_course": target.course if target else None,
        "course_stats": course_stats,
        "cross_courses": sorted(course_stats.keys()),
        "is_cross_discipline": len(course_stats) > 1,
    }
    return {"status": "success", "data": result}
