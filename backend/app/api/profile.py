"""
学生画像API
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime

import asyncio
from sqlalchemy.orm import Session
from ..models.database import get_db
from ..models.student import StudentProfileModel
from ..agents import ProfilerAgent
from .auth import get_current_student_id, require_auth

router = APIRouter()

_profiler_agent = ProfilerAgent()


class StudentProfile(BaseModel):
    """学生画像模型"""
    student_id: str
    knowledge_base: Dict[str, Any] = {}
    cognitive_style: Dict[str, Any] = {
        "primary": "visual",
        "scores": {
            "visual": 0.8,
            "auditory": 0.5,
            "reading": 0.6,
            "kinesthetic": 0.7,
        },
    }
    weak_areas: List[str] = []
    error_patterns: List[Dict] = []
    learning_goals: List[Dict] = []
    interest_areas: List[Dict] = []
    learning_tempo: Dict[str, Any] = {
        "study_speed": "moderate",
        "optimal_session_duration": 45,
    }
    practical_preferences: Dict[str, Any] = {
        "coding_proficiency": {},
        "preferred_practice_types": [],
    }
    created_at: str = datetime.now().isoformat()
    updated_at: str = datetime.now().isoformat()


class ProfileUpdateRequest(BaseModel):
    """画像更新请求"""
    dimension: str
    updates: Dict[str, Any]
    confidence: float = 0.8
    trigger: str = "conversation"


class ProfileInitRequest(BaseModel):
    """画像初始化请求"""
    inputs: List[str]
    initial_data: Optional[Dict[str, Any]] = None


class ProfileAnalyzeRequest(BaseModel):
    """对话分析请求"""
    conversation: str


def _profile_to_dict(profile: StudentProfileModel) -> Dict[str, Any]:
    return {
        "student_id": profile.student_id,
        "knowledge_base": profile.knowledge_base or {},
        "cognitive_style": profile.cognitive_style or {},
        "weak_areas": profile.weak_areas or [],
        "error_patterns": profile.error_patterns or [],
        "learning_goals": profile.learning_goals or [],
        "interest_areas": profile.interest_areas or [],
        "learning_tempo": profile.learning_tempo or {},
        "practical_preferences": profile.practical_preferences or {},
        "created_at": profile.created_at.isoformat() if profile.created_at else datetime.now().isoformat(),
        "updated_at": profile.updated_at.isoformat() if profile.updated_at else datetime.now().isoformat(),
    }


def _get_or_create_profile(db: Session, student_id: str) -> StudentProfileModel:
    profile = db.query(StudentProfileModel).filter(StudentProfileModel.student_id == student_id).first()
    if not profile:
        profile = StudentProfileModel(student_id=student_id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


@router.get("/{student_id}")
async def get_profile(student_id: str, db: Session = Depends(get_db)):
    """获取学生画像"""
    profile = _get_or_create_profile(db, student_id)
    return {"status": "success", "data": _profile_to_dict(profile)}


@router.post("/{student_id}/update")
async def update_profile(student_id: str, request: ProfileUpdateRequest, db: Session = Depends(get_db), _current: str = Depends(require_auth)):
    """更新学生画像（本地更新 + 可选 LLM 分析）"""
    profile = db.query(StudentProfileModel).filter(StudentProfileModel.student_id == student_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Student not found")

    # 本地更新指定维度
    valid_dimensions = {"knowledge", "cognitive", "weakness", "interest", "tempo", "practice"}
    if request.dimension not in valid_dimensions:
        raise HTTPException(status_code=400, detail=f"Invalid dimension '{request.dimension}'. Valid: {valid_dimensions}")
    if request.dimension == "knowledge":
        profile.knowledge_base = {**(profile.knowledge_base or {}), **request.updates}
    elif request.dimension == "cognitive":
        profile.cognitive_style = {**(profile.cognitive_style or {}), **request.updates}
    elif request.dimension == "weakness":
        profile.weak_areas = list(set((profile.weak_areas or []) + request.updates.get("areas", [])))
        profile.error_patterns = (profile.error_patterns or []) + request.updates.get("patterns", [])
    elif request.dimension == "interest":
        profile.learning_goals = (profile.learning_goals or []) + request.updates.get("goals", [])
        profile.interest_areas = (profile.interest_areas or []) + request.updates.get("areas", [])
    elif request.dimension == "tempo":
        profile.learning_tempo = {**(profile.learning_tempo or {}), **request.updates}
    elif request.dimension == "practice":
        profile.practical_preferences = {**(profile.practical_preferences or {}), **request.updates}

    db.commit()
    db.refresh(profile)

    # 可选：调用 ProfilerAgent 做 LLM 画像分析（带超时保护）
    llm_analysis = None
    try:
        llm_result = await asyncio.wait_for(
            _profiler_agent.process({
                "action": "analyze",
                "student_id": student_id,
                "inputs": [f"更新维度 {request.dimension}: {request.updates}"],
                "current_profile": _profile_to_dict(profile),
            }),
            timeout=12.0,
        )
        if llm_result.get("status") == "success":
            llm_analysis = llm_result.get("analysis", {})
    except asyncio.TimeoutError:
        pass
    except Exception:
        pass

    return {
        "status": "success",
        "message": f"Profile dimension '{request.dimension}' updated",
        "data": _profile_to_dict(profile),
        "llm_analysis": llm_analysis,
    }


@router.get("/{student_id}/summary")
async def get_profile_summary(student_id: str, db: Session = Depends(get_db)):
    """获取画像摘要"""
    profile = db.query(StudentProfileModel).filter(StudentProfileModel.student_id == student_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Student not found")

    p = _profile_to_dict(profile)
    return {
        "status": "success",
        "summary": {
            "dominant_style": p["cognitive_style"].get("primary", "unknown"),
            "current_level": "intermediate",
            "focus_areas": p["weak_areas"][:3] if p["weak_areas"] else [],
            "weekly_study_hours": p["learning_tempo"].get("weekly_study_capacity", 10),
            "last_updated": p["updated_at"],
        },
    }


@router.post("/{student_id}/initialize")
async def initialize_profile(
    student_id: str, init_request: ProfileInitRequest, db: Session = Depends(get_db), _current: str = Depends(require_auth)
):
    """初始化学生画像（可调用 LLM 生成结构化画像）"""
    llm_profile = None

    if init_request.inputs:
        try:
            llm_result = await asyncio.wait_for(
                _profiler_agent.process({
                    "action": "initialize",
                    "student_id": student_id,
                    "inputs": init_request.inputs,
                }),
                timeout=15.0,
            )
            if llm_result.get("status") == "success":
                llm_profile = llm_result.get("profile")
        except asyncio.TimeoutError:
            pass
        except Exception:
            pass

    if llm_profile:
        # 删除旧记录（如果存在）并插入新数据
        db.query(StudentProfileModel).filter(StudentProfileModel.student_id == student_id).delete()
        new_profile = StudentProfileModel(
            student_id=student_id,
            knowledge_base=llm_profile.get("knowledge_base", {}),
            cognitive_style=llm_profile.get("cognitive_style", {}),
            weak_areas=llm_profile.get("weak_areas", []),
            error_patterns=llm_profile.get("error_patterns", []),
            learning_goals=llm_profile.get("learning_goals", []),
            interest_areas=llm_profile.get("interest_areas", []),
            learning_tempo=llm_profile.get("learning_tempo", {}),
            practical_preferences=llm_profile.get("practical_preferences", {}),
        )
        db.add(new_profile)
        db.commit()
        db.refresh(new_profile)
        profile = new_profile
    else:
        profile = _get_or_create_profile(db, student_id)
        if init_request.initial_data:
            for key, value in init_request.initial_data.items():
                if hasattr(profile, key):
                    setattr(profile, key, value)
            db.commit()
            db.refresh(profile)

    return {
        "status": "success",
        "message": "Profile initialized",
        "data": _profile_to_dict(profile),
    }


def _deep_merge(base: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
    """深度合并两个字典，update 优先级更高，但保留 base 中独有的字段"""
    result = dict(base)
    for key, value in update.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _deep_merge(result.get(key, {}), value)
        else:
            result[key] = value
    return result


def _merge_list_unique(base: List[Any], update: List[Any]) -> List[Any]:
    """合并两个列表并去重（对可序列化元素）"""
    import json
    seen = set()
    result = []
    for item in (base or []) + (update or []):
        try:
            key = json.dumps(item, sort_keys=True, ensure_ascii=False)
        except (TypeError, ValueError):
            key = str(item)
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result


def _fill_profile_defaults(profile: Dict[str, Any]) -> Dict[str, Any]:
    """确保画像包含所有必要维度的完整字段"""
    defaults = {
        "knowledge_base": {
            "overall_score": 0.5,
            "academic_level": "未知",
            "subject_strengths": [],
            "subject_weaknesses": [],
        },
        "cognitive_style": {
            "primary": "visual",
            "scores": {"visual": 0.6, "auditory": 0.4, "reading": 0.5, "kinesthetic": 0.5},
        },
        "weak_areas": [],
        "error_patterns": [],
        "learning_goals": [],
        "interest_areas": [],
        "learning_tempo": {
            "study_speed": "moderate",
            "optimal_session_duration": 45,
            "weekly_study_capacity": 10,
            "focus_score": 0.7,
        },
        "practical_preferences": {
            "coding_proficiency": {},
            "preferred_practice_types": [],
            "overall_score": 0.5,
        },
    }
    result = dict(profile)
    for key, default_val in defaults.items():
        if key not in result or result[key] is None:
            result[key] = default_val
        elif isinstance(result[key], dict) and isinstance(default_val, dict):
            for sub_key, sub_default in default_val.items():
                if sub_key not in result[key] or result[key][sub_key] is None:
                    result[key][sub_key] = sub_default
    return result


@router.post("/{student_id}/analyze-conversation")
async def analyze_conversation(
    student_id: str,
    request: ProfileAnalyzeRequest,
    db: Session = Depends(get_db),
    _current: str = Depends(require_auth),
):
    """分析学生对话内容，自动更新六维画像"""
    profile = _get_or_create_profile(db, student_id)
    current = _profile_to_dict(profile)

    llm_profile = None
    try:
        llm_result = await asyncio.wait_for(
            _profiler_agent.process({
                "action": "update",
                "student_id": student_id,
                "inputs": [request.conversation],
                "current_profile": current,
            }),
            timeout=18.0,
        )
        if llm_result.get("status") == "success":
            llm_profile = llm_result.get("profile")
    except asyncio.TimeoutError:
        pass
    except Exception:
        pass

    if llm_profile and isinstance(llm_profile, dict):
        # 先补齐 LLM 可能缺失的字段
        llm_profile = _fill_profile_defaults(llm_profile)
        # 将 LLM 分析结果安全合并到数据库
        profile.knowledge_base = _deep_merge(profile.knowledge_base or {}, llm_profile.get("knowledge_base", {}))
        profile.cognitive_style = _deep_merge(profile.cognitive_style or {}, llm_profile.get("cognitive_style", {}))
        profile.weak_areas = _merge_list_unique(profile.weak_areas, llm_profile.get("weak_areas", []))
        profile.error_patterns = _merge_list_unique(profile.error_patterns, llm_profile.get("error_patterns", []))
        profile.learning_goals = _merge_list_unique(profile.learning_goals, llm_profile.get("learning_goals", []))
        profile.interest_areas = _merge_list_unique(profile.interest_areas, llm_profile.get("interest_areas", []))
        profile.learning_tempo = _deep_merge(profile.learning_tempo or {}, llm_profile.get("learning_tempo", {}))
        profile.practical_preferences = _deep_merge(profile.practical_preferences or {}, llm_profile.get("practical_preferences", {}))
        db.commit()
        db.refresh(profile)

    return {
        "status": "success",
        "message": "画像已根据对话更新" if llm_profile else "画像未变更（LLM 未返回有效数据）",
        "data": _profile_to_dict(profile),
    }
