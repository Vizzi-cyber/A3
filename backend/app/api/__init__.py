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
from .agent_flow import router as agent_flow_router
from .gamification_tree import router as gamification_tree_router
from .gamification_challenge import router as gamification_challenge_router
from .ppt import router as ppt_router
from .knowledge_graph import router as knowledge_graph_router
from .daily_quiz import router as daily_quiz_router
from .error_catcher import router as error_catcher_router
from .misconception_tracer import router as misconception_tracer_router
from .project_decomposer import router as project_decomposer_router
from .role_matcher import router as role_matcher_router
from .collaboration_supervisor import router as collaboration_supervisor_router
from .result_evaluator import router as result_evaluator_router
from .teacher import router as teacher_router
from .knowledge_base import router as kb_router
from .onboarding import router as onboarding_router
from .path_adjustment_log_api import router as adjustment_log_router

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
router.include_router(agent_flow_router, prefix="/agent-flow", tags=["Agent工作流"])
router.include_router(gamification_tree_router, prefix="/gamification-tree", tags=["知识树成长"])
router.include_router(gamification_challenge_router, prefix="/gamification-challenge", tags=["学习挑战与排行榜"])
router.include_router(ppt_router, prefix="/ppt", tags=["PPT生成"])
router.include_router(knowledge_graph_router, prefix="/knowledge-graph", tags=["知识图谱"])
router.include_router(daily_quiz_router, prefix="/daily-quiz", tags=["每日练习"])
router.include_router(error_catcher_router, prefix="/error-catcher", tags=["错误捕捉"])
router.include_router(misconception_tracer_router, prefix="/misconception-tracer", tags=["思维溯源"])
router.include_router(project_decomposer_router, prefix="/project-decomposer", tags=["项目拆解"])
router.include_router(role_matcher_router, prefix="/role-matcher", tags=["角色匹配"])
router.include_router(collaboration_supervisor_router, prefix="/collaboration-supervisor", tags=["协作督导"])
router.include_router(result_evaluator_router, prefix="/result-evaluator", tags=["成果评估"])
router.include_router(teacher_router, prefix="/teacher", tags=["教师端"])
router.include_router(kb_router, prefix="/kb", tags=["知识库"])
router.include_router(onboarding_router, prefix="/onboarding", tags=["引导问卷"])
router.include_router(adjustment_log_router, prefix="/path-adjustment", tags=["路径调整日志"])
