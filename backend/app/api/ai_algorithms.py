"""
AI 算法增强 API（AIC 算法创新赛核心模块）

暴露四大算法引擎：
  - BKT 知识追踪  ：完整贝叶斯知识追踪（pyBKT），EM 参数估计 + AUC 验证
  - IRT 认知诊断  ：1PL/2PL 能力 θ 与题目难度 b 标定（MAP 联合估计）
  - FSRS 记忆调度 ：间隔重复复习队列（fsrs），状态持久化到 memory_cards 表
  - MAB 自适应选题：Thompson Sampling 选题（mabwiser），探索-利用权衡

设计说明：
  - BKT / IRT 拟合为一次性 POST（数据更新后可重新拟合），结果缓存于进程内；
  - FSRS 卡片持久化到数据库（memory_cards），重启不丢失；
  - MAB 选题器按学生维度维护在进程内（演示/比赛够用，生产可换 Redis 等）。
"""
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..algorithms.bkt_engine import BKTEngine
from ..algorithms.irt_diagnoser import IRTDiagnoser
from ..algorithms.memory_scheduler import FSRSMemoryScheduler
from ..algorithms.bandit_selector import ThompsonSamplingSelector
from ..models.database import get_db
from ..models.knowledge import KnowledgePointModel, QuizResultModel
from ..models.memory import MemoryCardModel
from ..core.logger import setup_logger
from ..services.algorithm_registry import (
    get_bkt_engine, set_bkt_engine, get_irt_diagnoser, set_irt_diagnoser,
)
from .auth import require_auth

logger = setup_logger()
router = APIRouter()

# ---------------------------------------------------------------------------
# 进程内算法实例（BKT/IRT 存共享注册表，MAB 按学生维度）
# ---------------------------------------------------------------------------
_bandit_selectors: Dict[str, ThompsonSamplingSelector] = {}


def _load_quiz_records(db: Session) -> List[Dict[str, Any]]:
    """从 quiz_results 表加载全部作答记录（含逐题 answers）。"""
    rows = db.query(QuizResultModel).all()
    return [
        {
            "student_id": r.student_id,
            "kp_id": r.kp_id,
            "answers": r.answers or [],
            "score": r.score,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ]


def _load_memory_scheduler(db: Session, student_id: str) -> FSRSMemoryScheduler:
    """从数据库恢复（或新建）某学生的 FSRS 调度器。"""
    scheduler = FSRSMemoryScheduler()
    rows = db.query(MemoryCardModel).filter(
        MemoryCardModel.student_id == student_id
    ).all()
    for r in rows:
        scheduler.restore_card(r.student_id, r.kp_id, r.card_json)
    return scheduler


def _save_memory_card(db: Session, student_id: str, kp_id: str, card_json: str) -> None:
    row = db.query(MemoryCardModel).filter(
        MemoryCardModel.student_id == student_id,
        MemoryCardModel.kp_id == kp_id,
    ).first()
    if row is None:
        row = MemoryCardModel(student_id=student_id, kp_id=kp_id, card_json=card_json)
        db.add(row)
    else:
        row.card_json = card_json
    db.commit()


# ---------------------------------------------------------------------------
# 请求模型
# ---------------------------------------------------------------------------
class MemoryReviewRequest(BaseModel):
    kp_id: str = Field(..., min_length=1, max_length=64)
    rating: str = Field(..., description="again / hard / good / easy")


class BanditSelectRequest(BaseModel):
    arms: List[str] = Field(..., min_length=1, max_length=200)
    k: int = Field(1, ge=1, le=20)
    exclude: Optional[List[str]] = None


class BanditUpdateRequest(BaseModel):
    arms: List[str] = Field(..., min_length=1, max_length=200)
    arm: str = Field(..., min_length=1)
    reward: float = Field(..., ge=0.0, le=1.0)


class IRTFitRequest(BaseModel):
    model: str = Field("2pl", description="1pl / 2pl")


# ---------------------------------------------------------------------------
# BKT 知识追踪
# ---------------------------------------------------------------------------
@router.post("/bkt/fit")
async def bkt_fit(
    db: Session = Depends(get_db),
    _auth: str = Depends(require_auth),
):
    """拟合完整 BKT 模型（EM 参数估计），返回参数与 AUC。"""
    records = _load_quiz_records(db)
    engine = BKTEngine()
    result = engine.fit(records)
    if result["status"] == "success":
        set_bkt_engine(engine)
    result["data_source"] = "quiz_results"
    result["message"] = (
        "完整 BKT（EM 估计）已就绪；对比「简化 BKT」的预测 AUC 可作应用效果数据"
    )
    return {"status": result["status"], "data": result}


@router.get("/bkt/mastery/{student_id}")
async def bkt_mastery(
    student_id: str,
    db: Session = Depends(get_db),
    _auth: str = Depends(require_auth),
):
    """查询学生各知识点掌握度（BKT 后验概率）。"""
    _bkt_engine = get_bkt_engine()
    if _bkt_engine is None or not _bkt_engine.is_fitted:
        raise HTTPException(status_code=409, detail="BKT 模型尚未拟合，请先 POST /algorithms/bkt/fit")
    kp_ids = [k.kp_id for k in db.query(KnowledgePointModel).all()]
    mastery = _bkt_engine.estimate_mastery_map(student_id, kp_ids)
    return {
        "status": "success",
        "data": {
            "student_id": student_id,
            "mastery_map": mastery,
            "params": _bkt_engine.get_params(),
            "auc": _bkt_engine.evaluate_auc(),
        },
    }


# ---------------------------------------------------------------------------
# IRT 认知诊断
# ---------------------------------------------------------------------------
@router.post("/irt/fit")
async def irt_fit(
    request: IRTFitRequest,
    db: Session = Depends(get_db),
    _auth: str = Depends(require_auth),
):
    """拟合 IRT 模型（1PL/2PL MAP 估计），返回学生能力与题目难度。"""
    records = _load_quiz_records(db)
    # 逐题展开为 (student_id, item_id, correct)
    item_records = []
    for r in records:
        answers = r.get("answers") or []
        if answers:
            for a in answers:
                item_records.append({
                    "student_id": r["student_id"],
                    "item_id": f"{r['kp_id']}:{a.get('q_id', 'q')}",
                    "correct": bool(a.get("correct", False)),
                })
        else:
            item_records.append({
                "student_id": r["student_id"],
                "item_id": r["kp_id"],
                "correct": (r.get("score") or 0) >= 60,
            })
    diagnoser = IRTDiagnoser(model=request.model)
    result = diagnoser.fit(item_records)
    if result["status"] == "success":
        set_irt_diagnoser(diagnoser)
    return {"status": result["status"], "data": result}


@router.get("/irt/ability/{student_id}")
async def irt_ability(
    student_id: str,
    _auth: str = Depends(require_auth),
):
    """查询学生 IRT 能力值 θ（替代加权平均分）。"""
    _irt_diagnoser = get_irt_diagnoser()
    if _irt_diagnoser is None or not _irt_diagnoser.is_fitted:
        raise HTTPException(status_code=409, detail="IRT 模型尚未拟合，请先 POST /algorithms/irt/fit")
    ability = _irt_diagnoser.estimate_ability(student_id)
    if ability is None:
        raise HTTPException(status_code=404, detail=f"未找到学生 {student_id} 的能力估计")
    return {
        "status": "success",
        "data": {
            "student_id": student_id,
            "ability_theta": ability,
            "model": _irt_diagnoser.model,
            "all_abilities": _irt_diagnoser.ability_map,
        },
    }


@router.get("/irt/difficulty")
async def irt_difficulty(
    _auth: str = Depends(require_auth),
):
    """查询题目/知识点难度标定（IRT b 值，替代人工难度 1-5）。"""
    _irt_diagnoser = get_irt_diagnoser()
    if _irt_diagnoser is None or not _irt_diagnoser.is_fitted:
        raise HTTPException(status_code=409, detail="IRT 模型尚未拟合，请先 POST /algorithms/irt/fit")
    return {
        "status": "success",
        "data": {
            "model": _irt_diagnoser.model,
            "difficulty": _irt_diagnoser.difficulty_map,
            "discrimination": {
                i: _irt_diagnoser.get_item_discrimination(i)
                for i in _irt_diagnoser.difficulty_map
            },
        },
    }


# ---------------------------------------------------------------------------
# FSRS 间隔重复记忆调度
# ---------------------------------------------------------------------------
@router.post("/memory/review")
async def memory_review(
    request: MemoryReviewRequest,
    db: Session = Depends(get_db),
    student_id: str = Depends(require_auth),
):
    """执行一次复习，更新 FSRS 记忆状态并持久化。"""
    scheduler = _load_memory_scheduler(db, student_id)
    try:
        info = scheduler.review(student_id, request.kp_id, request.rating)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    # 持久化：导出该卡片的 fsrs 序列化 JSON 到 memory_cards 表
    card_json = scheduler.get_card_json(student_id, request.kp_id) or "{}"
    _save_memory_card(db, student_id, request.kp_id, card_json)
    return {"status": "success", "data": info}


@router.get("/memory/card/{student_id}/{kp_id}")
async def memory_card(
    student_id: str,
    kp_id: str,
    db: Session = Depends(get_db),
    _auth: str = Depends(require_auth),
):
    """查询记忆卡片状态（难度/稳定性/可提取性/下次复习）。"""
    scheduler = _load_memory_scheduler(db, student_id)
    card = scheduler.get_card(student_id, kp_id)
    if card is None:
        card = scheduler.ensure_card(student_id, kp_id)
    return {"status": "success", "data": card}


@router.get("/memory/due/{student_id}")
async def memory_due(
    student_id: str,
    db: Session = Depends(get_db),
    _auth: str = Depends(require_auth),
):
    """查询到期复习队列（FSRS 计算的最优复习时刻）。"""
    scheduler = _load_memory_scheduler(db, student_id)
    due = scheduler.get_due_cards(student_id)
    return {"status": "success", "data": {"student_id": student_id, "due_cards": due, "count": len(due)}}


# ---------------------------------------------------------------------------
# MAB 自适应选题（Thompson Sampling）
# ---------------------------------------------------------------------------
@router.post("/bandit/select")
async def bandit_select(
    request: BanditSelectRequest,
    _auth: str = Depends(require_auth),
):
    """按 Thompson Sampling 选择 k 个候选（题目/资源）。"""
    selector = _bandit_selectors.setdefault(
        _auth, ThompsonSamplingSelector(arms=request.arms)
    )
    picked = selector.select(k=request.k, exclude=request.exclude)
    return {
        "status": "success",
        "data": {
            "picked": picked,
            "expectations": selector.get_expectations(),
            "n_updates": len(selector._decisions),
        },
    }


@router.post("/bandit/update")
async def bandit_update(
    request: BanditUpdateRequest,
    _auth: str = Depends(require_auth),
):
    """反馈被选臂的收益，更新 MAB 策略。"""
    selector = _bandit_selectors.setdefault(
        _auth, ThompsonSamplingSelector(arms=request.arms)
    )
    selector.update(request.arm, request.reward)
    return {
        "status": "success",
        "data": {
            "arm": request.arm,
            "reward": request.reward,
            "expectations": selector.get_expectations(),
            "stats": selector.get_stats(),
        },
    }


@router.get("/status")
async def ai_algorithms_status(
    _auth: str = Depends(require_auth),
):
    """算法模块状态总览。"""
    return {
        "status": "success",
        "data": {
            "bkt": {
                "fitted": get_bkt_engine() is not None and get_bkt_engine().is_fitted,
                "skills": get_bkt_engine().skills if get_bkt_engine() and get_bkt_engine().is_fitted else [],
                "auc": get_bkt_engine().evaluate_auc() if get_bkt_engine() and get_bkt_engine().is_fitted else None,
            },
            "irt": {
                "fitted": get_irt_diagnoser() is not None and get_irt_diagnoser().is_fitted,
                "model": get_irt_diagnoser().model if get_irt_diagnoser() and get_irt_diagnoser().is_fitted else None,
                "students": len(get_irt_diagnoser().ability_map) if get_irt_diagnoser() and get_irt_diagnoser().is_fitted else 0,
                "items": len(get_irt_diagnoser().difficulty_map) if get_irt_diagnoser() and get_irt_diagnoser().is_fitted else 0,
            },
            "memory": {"engine": "FSRS", "note": "卡片持久化于 memory_cards 表"},
            "bandit": {"active_selectors": len(_bandit_selectors)},
        },
    }
