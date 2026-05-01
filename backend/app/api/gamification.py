"""
游戏化学习后端API
- 积分系统
- 成就徽章系统
- 任务系统
- 排行榜
- 社交基础
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models.database import get_db
from ..models.gamification import PointsModel, AchievementModel, TaskModel, LeaderboardModel
from .auth import require_auth

router = APIRouter()


# ---------- 积分 ----------

@router.get("/{student_id}/points")
async def get_points(student_id: str, db: Session = Depends(get_db), _current: str = Depends(require_auth)):
    """获取学生积分"""
    points = db.query(PointsModel).filter(PointsModel.student_id == student_id).first()
    if not points:
        return {"status": "success", "data": {"student_id": student_id, "total_points": 0, "daily_points": 0, "weekly_points": 0}}
    return {
        "status": "success",
        "data": {
            "student_id": points.student_id,
            "total_points": points.total_points,
            "daily_points": points.daily_points,
            "weekly_points": points.weekly_points,
        },
    }


class AddPointsRequest(BaseModel):
    student_id: str
    points: int
    reason: str = ""


@router.post("/points/add")
async def add_points(request: AddPointsRequest, db: Session = Depends(get_db), _current: str = Depends(require_auth)):
    """增加积分"""
    points = db.query(PointsModel).filter(PointsModel.student_id == request.student_id).first()
    if not points:
        points = PointsModel(student_id=request.student_id, total_points=0, daily_points=0, weekly_points=0)
        db.add(points)
    points.total_points += request.points
    points.daily_points += request.points
    points.weekly_points += request.points
    db.commit()
    db.refresh(points)
    return {"status": "success", "total_points": points.total_points}


# ---------- 成就 ----------

@router.get("/{student_id}/achievements")
async def get_achievements(student_id: str, db: Session = Depends(get_db), _current: str = Depends(require_auth)):
    """获取已解锁成就"""
    achievements = db.query(AchievementModel).filter(AchievementModel.student_id == student_id).all()
    return {
        "status": "success",
        "data": [
            {
                "achievement_id": a.achievement_id,
                "name": a.name,
                "description": a.description,
                "icon": a.icon,
                "unlocked_at": a.unlocked_at.isoformat() if a.unlocked_at else None,
            }
            for a in achievements
        ],
    }


class UnlockAchievementRequest(BaseModel):
    student_id: str
    achievement_id: str
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None


@router.post("/achievements/unlock")
async def unlock_achievement(request: UnlockAchievementRequest, db: Session = Depends(get_db), _current: str = Depends(require_auth)):
    """解锁成就"""
    existing = db.query(AchievementModel).filter(
        AchievementModel.student_id == request.student_id,
        AchievementModel.achievement_id == request.achievement_id,
    ).first()
    if existing:
        return {"status": "success", "message": "Already unlocked"}
    ach = AchievementModel(
        student_id=request.student_id,
        achievement_id=request.achievement_id,
        name=request.name,
        description=request.description,
        icon=request.icon,
    )
    db.add(ach)
    db.commit()
    return {"status": "success", "message": "Achievement unlocked"}


# ---------- 任务 ----------

@router.get("/{student_id}/tasks")
async def get_tasks(student_id: str, task_type: Optional[str] = None, db: Session = Depends(get_db), _current: str = Depends(require_auth)):
    """获取任务列表"""
    query = db.query(TaskModel).filter(TaskModel.student_id == student_id)
    if task_type:
        query = query.filter(TaskModel.task_type == task_type)
    tasks = query.limit(100).all()
    return {
        "status": "success",
        "data": [
            {
                "task_id": t.task_id,
                "title": t.title,
                "description": t.description,
                "task_type": t.task_type,
                "reward_points": t.reward_points,
                "progress": t.progress,
                "completed": t.completed,
                "completed_at": t.completed_at.isoformat() if t.completed_at else None,
            }
            for t in tasks
        ],
    }


class CreateTaskRequest(BaseModel):
    student_id: str
    task_id: str
    title: str
    description: Optional[str] = None
    task_type: str = "daily"
    reward_points: int = 0


@router.post("/tasks/create")
async def create_task(request: CreateTaskRequest, db: Session = Depends(get_db), _current: str = Depends(require_auth)):
    """创建任务"""
    task = TaskModel(
        student_id=request.student_id,
        task_id=request.task_id,
        title=request.title,
        description=request.description,
        task_type=request.task_type,
        reward_points=request.reward_points,
    )
    db.add(task)
    db.commit()
    return {"status": "success", "task_id": request.task_id}


class UpdateTaskProgressRequest(BaseModel):
    student_id: str
    task_id: str
    progress: float


@router.post("/tasks/progress")
async def update_task_progress(request: UpdateTaskProgressRequest, db: Session = Depends(get_db), _current: str = Depends(require_auth)):
    """更新任务进度"""
    task = db.query(TaskModel).filter(
        TaskModel.student_id == request.student_id,
        TaskModel.task_id == request.task_id,
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.progress = min(1.0, max(0.0, request.progress))
    if task.progress >= 1.0 and not task.completed:
        task.completed = True
        task.completed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(task)
    return {"status": "success", "progress": task.progress, "completed": task.completed}


# ---------- 排行榜 ----------

@router.get("/leaderboard/{period}")
async def get_leaderboard(period: str = "weekly", limit: int = 20, db: Session = Depends(get_db), _current: str = Depends(require_auth)):
    """获取排行榜"""
    rows = (
        db.query(LeaderboardModel)
        .filter(LeaderboardModel.period == period)
        .order_by(LeaderboardModel.score.desc())
        .limit(limit)
        .all()
    )
    return {
        "status": "success",
        "period": period,
        "data": [
            {
                "rank": r.rank,
                "student_id": r.student_id,
                "score": r.score,
            }
            for r in rows
        ],
    }
