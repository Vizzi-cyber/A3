"""
数据库测试数据填充脚本
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from passlib.context import CryptContext
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.database import Base
from app.models.user import UserModel
from app.models.student import StudentProfileModel
from app.models.knowledge import KnowledgePointModel, LearningRecordModel, QuizResultModel
from app.models.trend import TrendDataModel
from app.models.gamification import PointsModel, AchievementModel, TaskModel, LeaderboardModel
from app.models.log_reflection import LearningLogModel, ReflectionModel

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
engine = create_engine("sqlite:///./ai_learning.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

db = SessionLocal()

STUDENT_ID = "student_001"
STUDENT2 = "student_002"
STUDENT3 = "student_003"

# ---------- 清空旧数据（保留表结构） ----------
for tbl in [
    ReflectionModel, LearningLogModel, LeaderboardModel, TaskModel,
    AchievementModel, PointsModel, TrendDataModel, QuizResultModel,
    LearningRecordModel, KnowledgePointModel, StudentProfileModel, UserModel,
]:
    db.query(tbl).delete()
db.commit()

# ---------- 用户表 ----------
users = [
    UserModel(student_id=STUDENT_ID, username="张三", email="zhangsan@example.com",
              hashed_password=pwd_context.hash("123456"), is_active=True, role="student"),
    UserModel(student_id=STUDENT2, username="李四", email="lisi@example.com",
              hashed_password=pwd_context.hash("123456"), is_active=True, role="student"),
    UserModel(student_id=STUDENT3, username="王五", email="wangwu@example.com",
              hashed_password=pwd_context.hash("123456"), is_active=True, role="student"),
]
db.add_all(users)
db.commit()

# ---------- 学生画像 ----------
profiles = [
    StudentProfileModel(
        student_id=STUDENT_ID,
        knowledge_base={"overall_score": 82, "机器学习概述": 0.8, "线性代数": 0.6, "概率论": 0.4, "神经网络": 0.3},
        cognitive_style={"primary": "visual", "scores": {"visual": 0.85, "auditory": 0.5, "reading": 0.65, "kinesthetic": 0.75}},
        weak_areas=["概率论", "梯度下降原理", "反向传播推导"],
        error_patterns=[{"type": "概念混淆", "desc": "经常混淆梯度下降与学习率"}],
        learning_goals=[{"goal": "掌握深度学习基础", "deadline": "2026-06-01"}],
        interest_areas=["计算机视觉", "自然语言处理"],
        learning_tempo={"study_speed": "moderate", "optimal_session_duration": 45, "weekly_study_capacity": 12, "focus_score": 78},
        practical_preferences={"overall_score": 88, "coding_proficiency": {"python": 0.8, "cpp": 0.3}, "preferred_practice_types": ["代码实操", "项目实战"]},
    ),
    StudentProfileModel(
        student_id=STUDENT2,
        knowledge_base={"overall_score": 92, "机器学习概述": 0.9, "线性代数": 0.85, "概率论": 0.8},
        cognitive_style={"primary": "reading", "scores": {"visual": 0.6, "auditory": 0.4, "reading": 0.9, "kinesthetic": 0.5}},
        weak_areas=["强化学习"],
        error_patterns=[],
        learning_goals=[{"goal": "完成强化学习专项", "deadline": "2026-07-01"}],
        interest_areas=["强化学习", "博弈论"],
        learning_tempo={"study_speed": "fast", "optimal_session_duration": 60, "weekly_study_capacity": 20, "focus_score": 85},
        practical_preferences={"overall_score": 95, "coding_proficiency": {"python": 0.9, "java": 0.7}, "preferred_practice_types": ["论文阅读", "算法竞赛"]},
    ),
    StudentProfileModel(
        student_id=STUDENT3,
        knowledge_base={"overall_score": 45, "机器学习概述": 0.5, "线性代数": 0.4, "概率论": 0.3},
        cognitive_style={"primary": "kinesthetic", "scores": {"visual": 0.5, "auditory": 0.6, "reading": 0.4, "kinesthetic": 0.85}},
        weak_areas=["数学基础", "Python编程"],
        error_patterns=[{"type": "语法错误", "desc": "经常遗漏缩进"}],
        learning_goals=[{"goal": "入门人工智能", "deadline": "2026-08-01"}],
        interest_areas=["机器人", "自动驾驶"],
        learning_tempo={"study_speed": "slow", "optimal_session_duration": 30, "weekly_study_capacity": 8, "focus_score": 55},
        practical_preferences={"overall_score": 40, "coding_proficiency": {"python": 0.3, "scratch": 0.7}, "preferred_practice_types": ["视频教程", "互动练习"]},
    ),
]
db.add_all(profiles)
db.commit()

# ---------- 知识点（DAG） ----------
kps = [
    KnowledgePointModel(kp_id="kp_001", name="机器学习概述", subject="AI", difficulty=0.3,
                        prerequisites=[], description="机器学习的基本概念与分类", tags=["入门", "概念"]),
    KnowledgePointModel(kp_id="kp_002", name="线性代数基础", subject="数学", difficulty=0.4,
                        prerequisites=[], description="矩阵、向量、特征值分解", tags=["数学", "基础"]),
    KnowledgePointModel(kp_id="kp_003", name="概率论与统计", subject="数学", difficulty=0.5,
                        prerequisites=["kp_002"], description="概率分布、贝叶斯定理", tags=["数学", "基础"]),
    KnowledgePointModel(kp_id="kp_004", name="梯度下降原理", subject="优化", difficulty=0.5,
                        prerequisites=["kp_002"], description="优化算法基础", tags=["优化", "核心"]),
    KnowledgePointModel(kp_id="kp_005", name="线性回归", subject="算法", difficulty=0.4,
                        prerequisites=["kp_002", "kp_004"], description="最基础的监督学习算法", tags=["算法", "回归"]),
    KnowledgePointModel(kp_id="kp_006", name="逻辑回归", subject="算法", difficulty=0.45,
                        prerequisites=["kp_002", "kp_004"], description="分类问题的经典方法", tags=["算法", "分类"]),
    KnowledgePointModel(kp_id="kp_007", name="神经网络基础", subject="深度学习", difficulty=0.6,
                        prerequisites=["kp_005", "kp_006"], description="感知机、多层神经网络", tags=["深度学习", "核心"]),
    KnowledgePointModel(kp_id="kp_008", name="反向传播算法", subject="深度学习", difficulty=0.65,
                        prerequisites=["kp_007"], description="神经网络训练的核心算法", tags=["深度学习", "核心"]),
    KnowledgePointModel(kp_id="kp_009", name="卷积神经网络CNN", subject="深度学习", difficulty=0.7,
                        prerequisites=["kp_008"], description="图像处理的核心网络结构", tags=["深度学习", "CV"]),
    KnowledgePointModel(kp_id="kp_010", name="循环神经网络RNN", subject="深度学习", difficulty=0.7,
                        prerequisites=["kp_008"], description="序列建模的基础", tags=["深度学习", "NLP"]),
]
db.add_all(kps)
db.commit()

# ---------- 学习记录 ----------
actions = ["watch", "read", "practice", "review"]
records = []
for i in range(20):
    sid = STUDENT_ID if i % 3 == 0 else (STUDENT2 if i % 3 == 1 else STUDENT3)
    kp = kps[i % len(kps)].kp_id
    records.append(LearningRecordModel(
        record_id=f"lr_{i:03d}",
        student_id=sid,
        kp_id=kp,
        action=actions[i % len(actions)],
        duration=(i + 1) * 120,
        progress=min(1.0, (i + 1) * 0.08),
        score=60 + (i % 5) * 8,
        meta={"device": "pc"},
    ))
db.add_all(records)
db.commit()

# ---------- 测验结果 ----------
quizzes = []
for i in range(15):
    sid = STUDENT_ID if i % 3 == 0 else (STUDENT2 if i % 3 == 1 else STUDENT3)
    kp = kps[i % len(kps)].kp_id
    correct = 3 + (i % 3)
    total = 5
    quizzes.append(QuizResultModel(
        quiz_id=f"qz_{i:03d}",
        student_id=sid,
        kp_id=kp,
        total_questions=total,
        correct_count=correct,
        score=correct / total * 100,
        weak_tags=["概念混淆"] if i % 4 == 0 else [],
        time_spent=300 + i * 60,
        answers=[{"q_id": f"q_{j}", "correct": j < correct} for j in range(total)],
    ))
db.add_all(quizzes)
db.commit()

# ---------- 趋势数据 ----------
trends = []
base_date = datetime.now() - timedelta(days=14)
for i in range(14):
    d = (base_date + timedelta(days=i)).strftime("%Y-%m-%d")
    trends.append(TrendDataModel(
        student_id=STUDENT_ID,
        date=d,
        mastery_trend=0.5 + i * 0.02,
        speed_ratio=0.6 + (i % 3) * 0.05,
        time_efficiency=0.7 - (i % 5) * 0.02,
        weakness_priority=0.4 + (i % 2) * 0.1,
        stability=0.8 - (i % 7) * 0.03,
        trend_factor=-0.2 + i * 0.03,
        trend_state="growth" if i > 7 else "stable",
        predicted_mastery_3d=0.5 + i * 0.025,
        intervention="建议加强薄弱点练习" if i % 3 == 0 else None,
    ))
db.add_all(trends)
db.commit()

# ---------- 游戏化积分 ----------
points = [
    PointsModel(student_id=STUDENT_ID, total_points=1250, daily_points=120, weekly_points=450),
    PointsModel(student_id=STUDENT2, total_points=2100, daily_points=200, weekly_points=800),
    PointsModel(student_id=STUDENT3, total_points=350, daily_points=50, weekly_points=150),
]
db.add_all(points)
db.commit()

# ---------- 成就 ----------
achievements = [
    AchievementModel(student_id=STUDENT_ID, achievement_id="ach_001", name="初出茅庐", description="完成首个学习模块", icon="trophy"),
    AchievementModel(student_id=STUDENT_ID, achievement_id="ach_002", name="持之以恒", description="连续打卡7天", icon="fire"),
    AchievementModel(student_id=STUDENT_ID, achievement_id="ach_003", name="代码高手", description="完成10次代码练习", icon="code"),
    AchievementModel(student_id=STUDENT2, achievement_id="ach_001", name="初出茅庐", description="完成首个学习模块", icon="trophy"),
    AchievementModel(student_id=STUDENT2, achievement_id="ach_004", name="学霸", description="测验平均分超过90", icon="star"),
    AchievementModel(student_id=STUDENT3, achievement_id="ach_001", name="初出茅庐", description="完成首个学习模块", icon="trophy"),
]
db.add_all(achievements)
db.commit()

# ---------- 任务 ----------
tasks = [
    TaskModel(student_id=STUDENT_ID, task_id="t_001", title="阅读机器学习概述", description="完成第一章图文讲义", task_type="daily", reward_points=50, progress=1.0, completed=True, completed_at=datetime.now()),
    TaskModel(student_id=STUDENT_ID, task_id="t_002", title="完成梯度下降练习", description="完成3道相关练习题", task_type="daily", reward_points=30, progress=0.6, completed=False),
    TaskModel(student_id=STUDENT_ID, task_id="t_003", title="本周学习15小时", description="累计学习时长目标", task_type="weekly", reward_points=100, progress=0.4, completed=False),
    TaskModel(student_id=STUDENT2, task_id="t_004", title="阅读论文5篇", description="前沿论文阅读挑战", task_type="weekly", reward_points=150, progress=0.8, completed=False),
    TaskModel(student_id=STUDENT2, task_id="t_005", title="算法竞赛", description="参加一场线上算法赛", task_type="challenge", reward_points=300, progress=0.0, completed=False),
    TaskModel(student_id=STUDENT3, task_id="t_006", title="Python基础练习", description="完成Python入门教程", task_type="daily", reward_points=20, progress=0.3, completed=False),
]
db.add_all(tasks)
db.commit()

# ---------- 排行榜 ----------
leaderboard = [
    LeaderboardModel(student_id=STUDENT2, period="weekly", score=2100, rank=1),
    LeaderboardModel(student_id=STUDENT_ID, period="weekly", score=1250, rank=2),
    LeaderboardModel(student_id=STUDENT3, period="weekly", score=350, rank=3),
    LeaderboardModel(student_id=STUDENT2, period="monthly", score=8500, rank=1),
    LeaderboardModel(student_id=STUDENT_ID, period="monthly", score=5200, rank=2),
    LeaderboardModel(student_id=STUDENT3, period="monthly", score=1200, rank=3),
]
db.add_all(leaderboard)
db.commit()

# ---------- 学习日志 ----------
logs = []
for i in range(7):
    d = (datetime.now() - timedelta(days=6 - i)).strftime("%Y-%m-%d")
    logs.append(LearningLogModel(
        log_id=f"log_{STUDENT_ID}_{d}",
        student_id=STUDENT_ID,
        date=d,
        total_duration=3600 + i * 300,
        kp_count=2 + i,
        quiz_count=1 + (i % 2),
        avg_score=70 + i * 2,
        mistakes=["概念混淆"] if i % 3 == 0 else [],
        path_progress=0.1 + i * 0.05,
        completed_tasks=[f"task_{j}" for j in range(i)],
        timeline=[{"time": "10:00", "action": "read", "kp_id": "kp_001", "duration": 1800}],
    ))
db.add_all(logs)
db.commit()

# ---------- 反思记录 ----------
reflections = [
    ReflectionModel(reflection_id=f"ref_{STUDENT_ID}_2026-04-14", student_id=STUDENT_ID, date="2026-04-14",
                    content="今天学习了梯度下降，感觉对学习率的理解还不够深入，明天要多做几道题巩固。",
                    mood="neutral", tags=["学习感悟", "数学"], ai_feedback="建议通过可视化工具观察不同学习率下的收敛曲线。"),
    ReflectionModel(reflection_id=f"ref_{STUDENT_ID}_2026-04-15", student_id=STUDENT_ID, date="2026-04-15",
                    content="完成了神经网络基础的阅读，对反向传播有了初步认识，但推导过程还是有些吃力。",
                    mood="excited", tags=["深度学习", "进步"], ai_feedback="可以尝试从简单的两层网络手动推导一次。"),
    ReflectionModel(reflection_id=f"ref_{STUDENT_ID}_2026-04-16", student_id=STUDENT_ID, date="2026-04-16",
                    content="今天状态不太好，概率论的题目错了很多，有点沮丧。",
                    mood="frustrated", tags=["情绪", "概率论"], ai_feedback="低谷是正常的，建议回顾前置知识矩阵运算，建立信心。"),
    ReflectionModel(reflection_id=f"ref_{STUDENT2}_2026-04-17", student_id=STUDENT2, date="2026-04-17",
                    content="读了一篇关于Transformer的论文，非常受启发！",
                    mood="happy", tags=["论文阅读", "NLP"], ai_feedback="可以尝试复现论文中的基础实验。"),
]
db.add_all(reflections)
db.commit()

db.close()
print("[DONE] Seed data inserted successfully!")
print(f"   users: 3")
print(f"   profiles: 3")
print(f"   knowledge_points: {len(kps)}")
print(f"   learning_records: {len(records)}")
print(f"   quiz_results: {len(quizzes)}")
print(f"   trend_data: {len(trends)}")
print(f"   points: 3")
print(f"   achievements: {len(achievements)}")
print(f"   tasks: {len(tasks)}")
print(f"   leaderboard: {len(leaderboard)}")
print(f"   learning_logs: {len(logs)}")
print(f"   reflections: {len(reflections)}")
