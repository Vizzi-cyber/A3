"""
匹配推荐API
- 学生 <-> 学习资源匹配（AIC P1-4：叠加 Thompson Sampling 探索层）
- 学生 <-> 学习路径匹配
- 资源收益反馈（闭环：/feedback 回传 → MAB 更新 → 下次匹配调序）
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Dict, Any

from sqlalchemy.orm import Session
from ..models.database import get_db
from ..models.student import StudentProfileModel
from ..models.knowledge import KnowledgePointModel
from ..algorithms import MultiDimWeightedMatcher
from ..services.algorithm_registry import (
    get_resource_bandit,
    update_resource_bandit,
    get_irt_difficulty_map,
    get_irt_ability,
)
from .auth import require_auth

router = APIRouter()


class ResourceMatchRequest(BaseModel):
    student_id: str
    resources: List[Dict[str, Any]]
    top_k: int = 5


class PathMatchRequest(BaseModel):
    student_id: str
    path_candidates: List[Dict[str, Any]]
    top_k: int = 3


class ResourceFeedbackRequest(BaseModel):
    """资源收益反馈：reward ∈ [0,1]，如曝光未点击 0.1 / 点击 0.4 / 完成 1.0"""
    student_id: str
    resource_type: str = Field(..., min_length=1, max_length=64)
    reward: float = Field(..., ge=0.0, le=1.0)


@router.post("/resources")
async def match_resources(request: ResourceMatchRequest, db: Session = Depends(get_db), _current: str = Depends(require_auth)):
    """学习资源匹配推荐（MAB 探索层：预热后按资源类型历史收益调序）"""
    profile = db.query(StudentProfileModel).filter(StudentProfileModel.student_id == request.student_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Student not found")

    # Recommendations must reference real knowledge points; discard stale or
    # synthetic candidates before scoring.
    kp_ids = {row[0] for row in db.query(KnowledgePointModel.kp_id).all()}
    request.resources = [r for r in request.resources if not r.get("kp_id") or r.get("kp_id") in kp_ids]
    if not request.resources:
        raise HTTPException(status_code=404, detail="No valid resources found in knowledge base")

    # 学生水平：knowledge_base.overall_score → 三档（与 resource_generator 同一
    # 推导口径），供 _difficulty_fit 的字符串档位回退使用
    overall_score = (profile.knowledge_base or {}).get("overall_score", 0.5)
    try:
        overall_score = float(overall_score)
    except (TypeError, ValueError):
        overall_score = 0.5
    knowledge_level = "beginner" if overall_score < 0.4 else ("intermediate" if overall_score < 0.7 else "advanced")

    profile_dict = {
        "student_id": profile.student_id,
        "knowledge_base": profile.knowledge_base or {},
        "knowledge_level": knowledge_level,
        "cognitive_style": profile.cognitive_style or {},
        "weak_areas": profile.weak_areas or [],
        "learning_goals": profile.learning_goals or [],
        "learning_tempo": profile.learning_tempo or {},
        "practical_preferences": profile.practical_preferences or {},
    }

    # AIC 算法增强：IRT 已标定时，难度适配用知识点 b 值（复合 item_id 按
    # kp 前缀聚合均值）；未标定为 None 时 matcher 回退三档匹配，向后兼容
    irt_difficulty_map = get_irt_difficulty_map()
    kp_b_map: Dict[str, float] = {}
    if irt_difficulty_map:
        agg: Dict[str, List[float]] = {}
        for item_id, b in irt_difficulty_map.items():
            try:
                agg.setdefault(str(item_id).split(":")[0], []).append(float(b))
            except (TypeError, ValueError):
                continue
        kp_b_map = {kp: sum(vals) / len(vals) for kp, vals in agg.items() if vals}

    matcher = MultiDimWeightedMatcher()
    result = matcher.match_resources(
        profile_dict,
        request.resources,
        top_k=request.top_k,
        bandit_selector=get_resource_bandit(request.student_id),
        irt_difficulty=kp_b_map or None,
        irt_ability=get_irt_ability(request.student_id),
    )
    return {"status": "success", "data": result}


@router.post("/paths")
async def match_paths(request: PathMatchRequest, db: Session = Depends(get_db), _current: str = Depends(require_auth)):
    """学习路径匹配推荐"""
    profile = db.query(StudentProfileModel).filter(StudentProfileModel.student_id == request.student_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Student not found")

    profile_dict = {
        "student_id": profile.student_id,
        "knowledge_base": profile.knowledge_base or {},
        "cognitive_style": profile.cognitive_style or {},
        "weak_areas": profile.weak_areas or [],
        "learning_goals": profile.learning_goals or [],
        "learning_tempo": profile.learning_tempo or {},
    }

    matcher = MultiDimWeightedMatcher()
    result = matcher.match_learning_paths(profile_dict, request.path_candidates, top_k=request.top_k)
    return {"status": "success", "data": result}


@router.post("/feedback")
async def resource_feedback(request: ResourceFeedbackRequest, _current: str = Depends(require_auth)):
    """资源收益反馈（闭环）：前端回传某类资源的交互收益，更新该学生的探索 MAB"""
    if request.student_id != _current:
        raise HTTPException(status_code=403, detail="Cannot update other student's feedback")
    from ..algorithms.weighted_matching import RESOURCE_ARMS
    arm = request.resource_type.strip().lower()
    if arm not in RESOURCE_ARMS:
        raise HTTPException(status_code=422, detail=f"未知资源类型: {arm}（可选：{RESOURCE_ARMS}）")
    ok = update_resource_bandit(request.student_id, arm, request.reward)
    return {"status": "success" if ok else "error", "updated": ok}
