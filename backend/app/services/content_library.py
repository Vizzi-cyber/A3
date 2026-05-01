"""
C语言课程内容库
优先从数据库 knowledge_points 表读取，保留本地 fallback
"""
import json
from typing import Dict, Any, Optional

# 本地 fallback（当数据库不可用时使用）
_FALLBACK_LIBRARY: Dict[str, Dict[str, Any]] = {}


def _load_fallback():
    """延迟加载 fallback 数据（避免启动时大量内存占用）"""
    global _FALLBACK_LIBRARY
    if _FALLBACK_LIBRARY:
        return
    # 若需紧急 fallback，可在此处填充硬编码数据
    # 正常流程应走数据库
    _FALLBACK_LIBRARY = {}


def get_content(kp_id: str) -> Optional[Dict[str, Any]]:
    """根据 kp_id 从数据库获取内容"""
    try:
        from ..models.database import SessionLocal
        from ..models.knowledge import KnowledgePointModel
        db = SessionLocal()
        try:
            kp = db.query(KnowledgePointModel).filter(KnowledgePointModel.kp_id == kp_id).first()
            if not kp:
                return None
            result: Dict[str, Any] = {}
            if kp.document:
                result["document"] = kp.document
            if kp.code_example:
                result["code"] = kp.code_example
            if kp.questions:
                result["questions"] = kp.questions if isinstance(kp.questions, list) else json.loads(kp.questions)
            if kp.mindmap:
                result["mindmap"] = kp.mindmap if isinstance(kp.mindmap, dict) else json.loads(kp.mindmap)
            return result
        finally:
            db.close()
    except Exception:
        _load_fallback()
        return _FALLBACK_LIBRARY.get(kp_id)


def get_content_by_topic(topic: str) -> Optional[Dict[str, Any]]:
    """根据主题名称模糊匹配"""
    try:
        from ..models.database import SessionLocal
        from ..models.knowledge import KnowledgePointModel
        db = SessionLocal()
        try:
            kp = db.query(KnowledgePointModel).filter(KnowledgePointModel.name == topic).first()
            if not kp:
                # 模糊匹配
                kp = db.query(KnowledgePointModel).filter(KnowledgePointModel.name.like(f"%{topic}%")).first()
            if not kp:
                return None
            return get_content(kp.kp_id)
        finally:
            db.close()
    except Exception:
        return None


def has_content(kp_id: str) -> bool:
    return get_content(kp_id) is not None
