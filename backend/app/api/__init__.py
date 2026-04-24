"""
API路由模块
"""
from fastapi import APIRouter

from .profile import router as profile_router
from .resource import router as resource_router
from .learning_path import router as path_router
from .tutor import router as tutor_router
from .auth import router as auth_router
from .knowledge import router as knowledge_router
from .learning_data import router as learning_data_router
from .trend import router as trend_router
from .matching import router as matching_router
from .gamification import router as gamification_router
from .log_reflection import router as log_reflection_router
from .monitoring import router as monitoring_router
from .image import router as image_router
from .dashboard import router as dashboard_router
from .favorites import router as favorites_router
from .ocr import router as ocr_router

router = APIRouter()

router.include_router(auth_router, prefix="/auth", tags=["用户权限"])
router.include_router(profile_router, prefix="/profile", tags=["学生画像"])
router.include_router(resource_router, prefix="/resource", tags=["资源生成"])
router.include_router(path_router, prefix="/learning-path", tags=["学习路径"])
router.include_router(tutor_router, prefix="/tutor", tags=["智能辅导"])
router.include_router(knowledge_router, prefix="/knowledge", tags=["知识点管理"])
router.include_router(learning_data_router, prefix="/learning-data", tags=["学习数据上报"])
router.include_router(trend_router, prefix="/trend", tags=["学习趋势与评估"])
router.include_router(matching_router, prefix="/matching", tags=["匹配推荐"])
router.include_router(gamification_router, prefix="/gamification", tags=["游戏化学习"])
router.include_router(log_reflection_router, prefix="/log-reflection", tags=["学习日志与反思"])
router.include_router(monitoring_router, prefix="/monitoring", tags=["系统监控"])
router.include_router(image_router, prefix="/image", tags=["文生图"])
router.include_router(ocr_router, prefix="/ocr", tags=["OCR识图"])
router.include_router(dashboard_router, prefix="/dashboard", tags=["仪表盘"])
router.include_router(favorites_router, prefix="/favorites", tags=["收藏夹"])
