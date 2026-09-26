"""
C语言课程内容库
从数据库 knowledge_points 表读取；单个 JSON 列损坏时跳过该字段（部分降级），
DB 无记录/异常时返回 None，由上游走 LLM 生成兜底
"""
import json
from typing import Dict, Any, Optional

from ..core.logger import setup_logger

logger = setup_logger()


def _extract_content(kp) -> Dict[str, Any]:
    """从 KnowledgePointModel 提取四类内容；单列 JSON 损坏只丢该列，不连坐整体"""
    result: Dict[str, Any] = {}
    if kp.document:
        result["document"] = kp.document
    if kp.code_example:
        result["code"] = kp.code_example
    if kp.questions:
        questions = kp.questions
        if not isinstance(questions, list):
            try:
                questions = json.loads(questions)
            except Exception:
                logger.warning(f"questions 列 JSON 损坏，跳过该字段: kp_id={kp.kp_id}")
                questions = None
        if questions:
            result["questions"] = questions
    if kp.mindmap:
        if isinstance(kp.mindmap, str) and kp.mindmap.strip().startswith("#"):
            result["mindmap"] = kp.mindmap  # markmap 缩进格式
        elif isinstance(kp.mindmap, dict):
            result["mindmap"] = kp.mindmap
        else:
            try:
                result["mindmap"] = json.loads(kp.mindmap)
            except Exception:
                logger.warning(f"mindmap 列 JSON 损坏，跳过该字段: kp_id={kp.kp_id}")
    return result


def get_content(kp_id: str, db=None) -> Optional[Dict[str, Any]]:
    """根据 kp_id 从数据库获取内容，可复用外部 db session"""
    try:
        from ..models.knowledge import KnowledgePointModel
        own_session = db is None
        if own_session:
            from ..models.database import SessionLocal
            db = SessionLocal()
        try:
            kp = db.query(KnowledgePointModel).filter(KnowledgePointModel.kp_id == kp_id).first()
            if not kp:
                return None
            return _extract_content(kp)
        finally:
            if own_session:
                db.close()
    except Exception as e:
        logger.warning(f"内容库查询失败: {e}")
        return None


def get_content_by_topic(topic: str, db=None) -> Optional[Dict[str, Any]]:
    """根据主题名称模糊匹配，可复用外部 db session"""
    try:
        from ..models.knowledge import KnowledgePointModel
        own_session = db is None
        if own_session:
            from ..models.database import SessionLocal
            db = SessionLocal()
        try:
            kp = db.query(KnowledgePointModel).filter(KnowledgePointModel.name == topic).first()
            if not kp:
                # 转义 LIKE 通配符，防止注入
                escaped = topic.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
                kp = db.query(KnowledgePointModel).filter(KnowledgePointModel.name.like(f"%{escaped}%", escape="\\")).first()
            if not kp:
                return None
            # 直接从已查询的 kp 对象提取内容，避免二次查询
            return _extract_content(kp)
        finally:
            if own_session:
                db.close()
    except Exception as e:
        logger.warning(f"内容库主题查询失败: {e}")
        return None


def has_content(kp_id: str) -> bool:
    return get_content(kp_id) is not None
