"""
学习路径API
对接 LangGraph 工作流，调用 path_planner 智能体
集成 DAG 路径规划算法
"""
import asyncio
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, List, Optional

from sqlalchemy.orm import Session
from ..models.database import get_db
from ..models.knowledge import KnowledgePointModel
from ..models.student import StudentProfileModel
from ..algorithms import DAGPathPlanner
from ..agents import PathPlannerAgent
from .auth import get_current_student_id, require_auth

router = APIRouter()

_path_planner_agent = PathPlannerAgent()


class PathGenerationRequest(BaseModel):
    """路径生成请求"""
    student_id: str
    target_topic: str
    current_knowledge: Optional[List[str]] = None
    time_constraint: Optional[int] = None
    preference: Optional[str] = None
    daily_duration: Optional[int] = None
    difficulty: Optional[int] = None


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

    # 加载学生画像用于个性化
    profile = db.query(StudentProfileModel).filter(StudentProfileModel.student_id == request.student_id).first()
    profile_dict = {
        "learning_tempo": {"weekly_study_capacity": request.daily_duration or 10},
        "weak_areas": profile.weak_areas or [] if profile else [],
        "knowledge_level": request.difficulty or 3,
        "preference": request.preference or "balanced",
    } if profile else {
        "learning_tempo": {"weekly_study_capacity": request.daily_duration or 10},
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
            timeout=15.0,
        )
        raw_path = result.get("path", {}) if isinstance(result, dict) else {}
    except asyncio.TimeoutError:
        raw_path = {}
    except Exception as e:
        raw_path = {}

    path_data = {
        "target": request.target_topic,
        "estimated_total_hours": 20,
        "stages": [
            {
                "stage_no": 1,
                "title": "基础入门与概念理解",
                "topics": [f"《{request.target_topic}》的基本概念与核心定义", "基础工具与环境搭建"],
                "hours": 5,
                "criteria": "能够清晰阐述基本概念，并成功搭建学习环境。",
                "resources": ["官方入门指南", "结构化在线课程"],
            },
            {
                "stage_no": 2,
                "title": "核心技能与知识深化",
                "topics": ["核心功能与模块详解", "常见问题与解决方案"],
                "hours": 5,
                "criteria": "能够独立运用核心功能解决中等难度的练习题。",
                "resources": ["进阶教程或书籍", "官方技术文档"],
            },
            {
                "stage_no": 3,
                "title": "实践应用与项目实战",
                "topics": ["设计并实现一个基于该主题的小型项目", "项目中的问题排查与调试"],
                "hours": 5,
                "criteria": "能够独立完成一个功能完整的小型项目。",
                "resources": ["项目案例库", "开源代码仓库"],
            },
            {
                "stage_no": 4,
                "title": "高级主题与综合提升",
                "topics": ["高级特性与优化技巧", "与其他技术的集成应用"],
                "hours": 5,
                "criteria": "能够理解并应用高级特性，对项目进行性能优化。",
                "resources": ["高级技术书籍或论文", "技术博客与会议演讲"],
            },
        ],
    }

    # 只有取到有效 stages 时才覆盖 fallback
    if raw_path and raw_path.get("stages"):
        path_data = raw_path

    return {
        "status": "success",
        "data": {
            "path_id": f"path_{request.student_id}",
            "student_id": request.student_id,
            "path": path_data,
        },
    }


@router.get("/{student_id}/current")
async def get_current_path(student_id: str):
    """获取当前学习路径"""
    return {
        "status": "success",
        "student_id": student_id,
        "current_step": 2,
        "progress": 0.25,
        "next_task": {
            "kp_id": "kp_002",
            "name": "递归终止条件",
            "action": "继续学习",
        },
        "nodes": [
            {"id": 1, "title": "机器学习概述", "status": "completed", "type": "入门", "resources": 5},
            {"id": 2, "title": "线性代数基础", "status": "completed", "type": "数学", "resources": 4},
            {"id": 3, "title": "梯度下降与优化", "status": "in-progress", "type": "核心", "resources": 8},
            {"id": 4, "title": "线性回归与逻辑回归", "status": "pending", "type": "算法", "resources": 6},
            {"id": 5, "title": "神经网络基础", "status": "locked", "type": "核心", "resources": 10},
            {"id": 6, "title": "CNN与图像识别", "status": "locked", "type": "深度学习", "resources": 7},
            {"id": 7, "title": "大模型应用开发", "status": "locked", "type": "前沿", "resources": 6},
        ],
    }


@router.post("/{student_id}/adjust")
async def adjust_path(
    student_id: str, adjustment: PathAdjustmentRequest, _current: str = Depends(require_auth)
):
    """调整学习路径 —— 直接调用 PathPlannerAgent"""
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
        pass
    except Exception:
        pass

    return {
        "status": "success",
        "message": "Path adjusted",
        "data": path_data,
    }


# ---------- DAG 路径规划算法接口 ----------

@router.post("/dag/generate")
async def generate_dag_path(request: DAGPathRequest, db: Session = Depends(get_db), _current: str = Depends(require_auth)):
    """基于DAG生成学习路径"""
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
async def adjust_dag_path(request: DAGPathAdjustRequest, _current: str = Depends(require_auth)):
    """动态调整DAG路径"""
    planner = DAGPathPlanner()
    result = planner.adjust_path(
        current_path=request.current_path,
        quiz_result=request.quiz_result,
        trend_state=request.trend_state,
    )
    return {"status": "success", "data": result}


@router.get("/dag/dependency-chain/{target_kp_id}")
async def get_dependency_chain(target_kp_id: str, db: Session = Depends(get_db)):
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
