"""
游戏化学习后端API
- 积分系统
- 成就徽章系统
- 任务系统
- 排行榜
- 社交基础
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime, timezone

from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models.database import get_db
from ..models.gamification import PointsModel, AchievementModel, TaskModel, LeaderboardModel
from ..models.user import UserModel
from ..services.gamification_service import ensure_points, award_points, sync_leaderboard
from .auth import require_auth

router = APIRouter()


# ---------- 积分 ----------

@router.get("/{student_id}/points")
async def get_points(student_id: str, db: Session = Depends(get_db), _current: str = Depends(require_auth)):
    """获取学生积分"""
    if student_id != _current:
        raise HTTPException(status_code=403, detail="Cannot view other student's points")
    points = ensure_points(db, student_id)
    db.commit()
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
    points: int = Field(..., ge=1, le=10000)
    reason: str = ""


@router.post("/points/add")
async def add_points(request: AddPointsRequest, db: Session = Depends(get_db), _current: str = Depends(require_auth)):
    """增加积分"""
    if request.student_id != _current:
        raise HTTPException(status_code=403, detail="Cannot add points for other student")
    total = award_points(db, request.student_id, request.points, request.reason)
    db.commit()
    return {"status": "success", "total_points": total}


# ---------- 成就 ----------

@router.get("/{student_id}/achievements")
async def get_achievements(student_id: str, db: Session = Depends(get_db), _current: str = Depends(require_auth)):
    """获取已解锁成就"""
    if student_id != _current:
        raise HTTPException(status_code=403, detail="Cannot view other student's achievements")
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
    if request.student_id != _current:
        raise HTTPException(status_code=403, detail="Cannot unlock achievement for other student")
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
    if student_id != _current:
        raise HTTPException(status_code=403, detail="Cannot view other student's tasks")
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
    task_id: str = Field(..., min_length=1, max_length=64)
    title: str = Field(..., min_length=1, max_length=256)
    description: Optional[str] = Field(None, max_length=512)
    task_type: Literal["daily", "weekly", "challenge"] = "daily"
    reward_points: int = Field(0, ge=0, le=10000)


@router.post("/tasks/create")
async def create_task(request: CreateTaskRequest, db: Session = Depends(get_db), _current: str = Depends(require_auth)):
    """创建任务"""
    if request.student_id != _current:
        raise HTTPException(status_code=403, detail="Cannot create task for other student")
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
    progress: float = Field(..., ge=0.0, le=1.0)


@router.post("/tasks/progress")
async def update_task_progress(request: UpdateTaskProgressRequest, db: Session = Depends(get_db), _current: str = Depends(require_auth)):
    """更新任务进度"""
    if request.student_id != _current:
        raise HTTPException(status_code=403, detail="Cannot update other student's task")
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
async def get_leaderboard(period: str = "weekly", limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db), _current: str = Depends(require_auth)):
    """获取排行榜。total/weekly/monthly 优先查 leaderboard 表，无数据时回退到 game_points 表。"""
    if period in ("total", "all"):
        # total: 从 game_points 直接取总积分排行
        points_rows = (
            db.query(PointsModel.student_id, PointsModel.total_points)
            .order_by(PointsModel.total_points.desc())
            .limit(limit)
            .all()
        )
        student_ids = [r.student_id for r in points_rows]
        users = db.query(UserModel.student_id, UserModel.username).filter(UserModel.student_id.in_(student_ids)).all()
        username_map = {u.student_id: u.username for u in users}
        return {
            "status": "success",
            "period": period,
            "data": [
                {
                    "rank": idx + 1,
                    "student_id": r.student_id,
                    "username": username_map.get(r.student_id, ""),
                    "points": r.total_points,
                    "streak_days": 0,
                    "level": (r.total_points or 0) // 1000 + 1,
                }
                for idx, r in enumerate(points_rows)
            ],
        }

    rows = (
        db.query(LeaderboardModel)
        .filter(LeaderboardModel.period == period)
        .order_by(LeaderboardModel.score.desc())
        .limit(limit)
        .all()
    )
    student_ids = [r.student_id for r in rows]
    users = db.query(UserModel.student_id, UserModel.username).filter(UserModel.student_id.in_(student_ids)).all()
    username_map = {u.student_id: u.username for u in users}

    points_list = db.query(PointsModel.student_id, PointsModel.total_points).filter(PointsModel.student_id.in_(student_ids)).all()
    points_map = {p.student_id: p.total_points for p in points_list}

    # 如果 leaderboard 表无数据，回退到 game_points
    if not rows:
        points_rows = (
            db.query(PointsModel.student_id, PointsModel.total_points)
            .order_by(PointsModel.total_points.desc())
            .limit(limit)
            .all()
        )
        student_ids = [r.student_id for r in points_rows]
        users = db.query(UserModel.student_id, UserModel.username).filter(UserModel.student_id.in_(student_ids)).all()
        username_map = {u.student_id: u.username for u in users}
        return {
            "status": "success",
            "period": period,
            "data": [
                {
                    "rank": idx + 1,
                    "student_id": r.student_id,
                    "username": username_map.get(r.student_id, ""),
                    "points": r.total_points,
                    "streak_days": 0,
                    "level": (r.total_points or 0) // 1000 + 1,
                }
                for idx, r in enumerate(points_rows)
            ],
        }

    return {
        "status": "success",
        "period": period,
        "data": [
            {
                "rank": idx + 1,
                "student_id": r.student_id,
                "username": username_map.get(r.student_id, ""),
                "points": r.score,
                "streak_days": 0,
                "level": (r.score or 0) // 1000 + 1,
            }
            for idx, r in enumerate(rows)
        ],
    }
