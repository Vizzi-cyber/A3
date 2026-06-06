"""
路径自动调整引擎
分析学习行为数据，判断是否需要调整路径
"""
import asyncio
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from ..core.logger import setup_logger

logger = setup_logger()

# 冷却时间：1小时内不重复检查
_cooldown_seconds = 3600
_last_check: dict = {}  # student_id -> timestamp

# 负面关键词
_NEGATIVE_KEYWORDS = ["太难", "不会", "困惑", "不理解", "放弃", "听不懂", "跟不上", "太简单", "无聊", "没意思", "太慢", "太累", "不想学"]
# 正面关键词
_POSITIVE_KEYWORDS = ["明白了", "理解了", "掌握了", "有趣", "清楚", "学会了", "懂了", "简单", "轻松", "有意思"]


@dataclass
class AdjustmentDecision:
    """调整决策"""
    should_adjust: bool = False
    confidence: float = 0.0
    reasons: List[str] = field(default_factory=list)
    trigger_sources: List[str] = field(default_factory=list)
    suggested_feedback: str = ""


def analyze_adjustment_need(student_id: str, db: Session) -> AdjustmentDecision:
    """分析是否需要调整路径"""
    from ..models.log_reflection import LearningLogModel, ReflectionModel
    from ..models.tutor_qa import TutorQAModel

    decision = AdjustmentDecision()

    # 检查冷却时间
    now = datetime.now(timezone.utc).timestamp()
    last = _last_check.get(student_id, 0)
    if now - last < _cooldown_seconds:
        return decision
    _last_check[student_id] = now

    signals = []

    # 1. 测验成绩趋势 (权重 0.4)
    logs = (
        db.query(LearningLogModel)
        .filter(LearningLogModel.student_id == student_id)
        .order_by(LearningLogModel.date.desc())
        .limit(10)
        .all()
    )
    if logs:
        scores = [l.avg_score for l in logs if l.avg_score > 0]
        if len(scores) >= 3:
            recent_avg = sum(scores[:3]) / 3
            overall_avg = sum(scores) / len(scores)
            if recent_avg < 50:
                signals.append(0.4)
                decision.reasons.append(f"近期测验平均分较低({recent_avg:.0f}分)")
                decision.trigger_sources.append("quiz_score_drop")
            elif overall_avg - recent_avg > 15:
                signals.append(0.3)
                decision.reasons.append(f"测验成绩下滑({overall_avg:.0f}→{recent_avg:.0f})")
                decision.trigger_sources.append("score_trend")
            else:
                signals.append(0.0)
        else:
            signals.append(0.0)
    else:
        signals.append(0.0)

    # 2. 反思关键词分析 (权重 0.3)
    reflections = (
        db.query(ReflectionModel)
        .filter(ReflectionModel.student_id == student_id)
        .order_by(ReflectionModel.created_at.desc())
        .limit(10)
        .all()
    )
    if reflections:
        neg_count = 0
        pos_count = 0
        for r in reflections:
            content = r.content or ""
            neg_count += sum(1 for kw in _NEGATIVE_KEYWORDS if kw in content)
            pos_count += sum(1 for kw in _POSITIVE_KEYWORDS if kw in content)
        frustration_score = neg_count / (pos_count + 1)
        if frustration_score > 0.6:
            signals.append(0.3)
            decision.reasons.append("学习反思显示多处困惑或挫败感")
            decision.trigger_sources.append("reflection_keywords")
        elif frustration_score < 0.1 and pos_count > 3:
            signals.append(0.0)
            # 正面反馈多，不需要调整
        else:
            signals.append(0.0)
    else:
        signals.append(0.0)

    # 3. 辅导提问频率 (权重 0.3)
    from datetime import date
    week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).date().isoformat()
    tutor_records = (
        db.query(TutorQAModel)
        .filter(
            TutorQAModel.student_id == student_id,
            TutorQAModel.created_at >= week_ago,
        )
        .all()
    )
    if tutor_records:
        freq = len(tutor_records) / 7.0
        if freq > 5:
            signals.append(0.3)
            decision.reasons.append(f"辅导提问频率较高({freq:.1f}次/天)")
            decision.trigger_sources.append("tutor_frequency")
        elif freq > 3:
            signals.append(0.15)
        else:
            signals.append(0.0)
    else:
        signals.append(0.0)

    # 综合判断
    if signals:
        total = sum(signals)
        decision.confidence = min(total, 1.0)
        decision.should_adjust = total >= 0.4

        if decision.should_adjust:
            parts = []
            if "quiz_score_drop" in decision.trigger_sources or "score_trend" in decision.trigger_sources:
                parts.append("测验成绩下滑，建议降低难度并增加基础练习")
            if "reflection_keywords" in decision.trigger_sources:
                parts.append("学习反思显示困惑，建议补充前置知识点讲解")
            if "tutor_frequency" in decision.trigger_sources:
                parts.append("辅导提问频率较高，建议放慢进度")
            decision.suggested_feedback = "；".join(parts) if parts else "根据学习行为分析，建议调整路径"

    return decision


async def maybe_check_path_adjustment(student_id: str, db: Session):
    """检查是否需要调整路径，如需要则异步执行"""
    decision = analyze_adjustment_need(student_id, db)
    if not decision.should_adjust:
        return None

    # 异步执行调整
    asyncio.create_task(_execute_adjustment(student_id, decision, db))
    return decision


async def _execute_adjustment(student_id: str, decision, db: Session):
    """执行路径调整"""
    try:
        from ..models.path_adjustment_log import PathAdjustmentLogModel
        from ..models.knowledge import KnowledgePointModel, LearningRecordModel
        from ..agents import PathPlannerAgent

        agent = PathPlannerAgent()

        # 获取当前路径快照
        from sqlalchemy import func
        kps = db.query(KnowledgePointModel).order_by(KnowledgePointModel.created_at.asc()).all()
        old_stages = []
        for idx, kp in enumerate(kps):
            old_stages.append({
                "stage_no": idx + 1,
                "title": kp.name,
                "topics": [kp.name],
                "hours": 5,
            })

        # 调用路径规划 agent
        result = await asyncio.wait_for(
            agent.process({
                "task": "adjust_path",
                "student_id": student_id,
                "current_path": {"stages": old_stages},
                "feedback": decision.suggested_feedback,
            }),
            timeout=15.0,
        )

        new_path = {}
        if result.get("status") == "success":
            new_path = result.get("path", {})

        if new_path and new_path.get("stages"):
            # 记录调整日志
            log_entry = PathAdjustmentLogModel(
                student_id=student_id,
                trigger_type="auto",
                trigger_source=", ".join(decision.trigger_sources),
                reason=decision.suggested_feedback,
                old_path_snapshot={"stages": old_stages},
                new_path_snapshot=new_path,
                confidence=decision.confidence,
            )
            db.add(log_entry)
            db.commit()
            logger.info(f"路径自动调整完成: student_id={student_id}, reason={decision.suggested_feedback}")

    except asyncio.TimeoutError:
        logger.warning(f"路径自动调整超时: student_id={student_id}")
    except Exception as e:
        logger.warning(f"路径自动调整异常: {e}")
