"""
匹配推荐API
- 学生 <-> 学习资源匹配
- 学生 <-> 学习路径匹配
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any

from sqlalchemy.orm import Session
from ..models.database import get_db
from ..models.student import StudentProfileModel
from ..algorithms import MultiDimWeightedMatcher
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


@router.post("/resources")
async def match_resources(request: ResourceMatchRequest, db: Session = Depends(get_db), _current: str = Depends(require_auth)):
    """学习资源匹配推荐"""
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
        "practical_preferences": profile.practical_preferences or {},
    }

    matcher = MultiDimWeightedMatcher()
    result = matcher.match_resources(profile_dict, request.resources, top_k=request.top_k)
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
