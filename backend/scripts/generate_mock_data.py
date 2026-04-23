"""
生成模拟数据脚本
为 demo 学生填充 quiz_results、learning_records、learning_logs、student_trends
game_tasks、game_achievements、game_points、leaderboard 等表
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import random
import uuid
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.database import SessionLocal, engine
from app.models.knowledge import QuizResultModel, LearningRecordModel
from app.models.log_reflection import LearningLogModel
from app.models.trend import TrendDataModel
from app.models.gamification import PointsModel, AchievementModel, TaskModel, LeaderboardModel
from app.models.student import StudentProfileModel

STUDENT_IDS = ['student_001', 'student_002', 'student_003']
KP_IDS = ['kp_c01', 'kp_c02', 'kp_c03', 'kp_c04', 'kp_c05', 'kp_c06', 'kp_c07', 'kp_c08', 'kp_c09', 'kp_c10']
WEAK_TAGS_POOL = ['指针', '数组', '函数', '递归', '内存管理', '结构体', '文件操作', '预处理指令']

def ensure_profile(db: Session, student_id: str):
    p = db.query(StudentProfileModel).filter(StudentProfileModel.student_id == student_id).first()
    if not p:
        p = StudentProfileModel(
            student_id=student_id,
            knowledge_base={'kp_c01': 0.9, 'kp_c02': 0.8, 'kp_c03': 0.6},
            cognitive_style={'primary': 'visual', 'secondary': 'kinesthetic'},
            weak_areas=['指针', '递归', '内存管理'],
            error_patterns=['数组越界', '指针空引用'],
            learning_goals=['掌握C语言基础', '通过期末考试'],
            interest_areas=['嵌入式开发', '操作系统'],
            learning_tempo={'expected_daily_kps': 3, 'optimal_session_duration': 45, 'weekly_study_capacity': 10},
            practical_preferences={'ide': 'VS Code', 'os': 'Windows'},
        )
        db.add(p)
        db.commit()

def generate_quiz_results(db: Session, student_id: str):
    """生成12条测验记录，分数逐步上升"""
    base_date = datetime.now() - timedelta(days=14)
    records = []
    for i in range(12):
        kp_id = KP_IDS[i % len(KP_IDS)]
        score = min(100, max(40, 45 + i * 4 + random.randint(-5, 5)))
        correct = int(score / 100 * 5)
        weak_count = max(0, 3 - i // 4)
        weak_tags = random.sample(WEAK_TAGS_POOL, weak_count) if weak_count > 0 else []
        records.append(QuizResultModel(
            quiz_id=f"quiz_{student_id}_{i+1:03d}",
            student_id=student_id,
            kp_id=kp_id,
            total_questions=5,
            correct_count=correct,
            score=round(score, 1),
            weak_tags=weak_tags,
            time_spent=random.randint(180, 600),
            answers=[{"q_idx": j, "correct": j < correct} for j in range(5)],
            created_at=base_date + timedelta(days=i, hours=random.randint(8, 20)),
        ))
    db.add_all(records)
    db.commit()

def generate_learning_records(db: Session, student_id: str):
    """生成30条学习记录，覆盖14天"""
    base_date = datetime.now() - timedelta(days=13)
    actions = ['watch', 'read', 'practice', 'review']
    records = []
    for i in range(30):
        day_offset = i // 3
        kp_id = KP_IDS[i % len(KP_IDS)]
        action = actions[i % len(actions)]
        duration = random.randint(300, 1800)
        progress = min(1.0, max(0.1, 0.2 + i * 0.03))
        records.append(LearningRecordModel(
            record_id=f"rec_{student_id}_{i+1:03d}",
            student_id=student_id,
            kp_id=kp_id,
            action=action,
            duration=duration,
            progress=round(progress, 2),
            score=random.randint(60, 100) if action == 'practice' else None,
            meta={"source": "mock"},
            created_at=base_date + timedelta(days=day_offset, hours=random.randint(8, 22), minutes=random.randint(0, 59)),
        ))
    db.add_all(records)
    db.commit()

def generate_learning_logs(db: Session, student_id: str):
    """生成14天学习日志"""
    base_date = datetime.now() - timedelta(days=13)
    logs = []
    for i in range(14):
        date_str = (base_date + timedelta(days=i)).strftime('%Y-%m-%d')
        kp_count = random.randint(1, 4)
        quiz_count = 1 if i % 3 == 0 else 0
        avg_score = random.randint(60, 95)
        logs.append(LearningLogModel(
            log_id=f"log_{student_id}_{date_str}",
            student_id=student_id,
            date=date_str,
            total_duration=random.randint(1800, 7200),
            kp_count=kp_count,
            quiz_count=quiz_count,
            avg_score=round(avg_score, 1),
            mistakes=random.sample(WEAK_TAGS_POOL, random.randint(0, 2)),
            path_progress=round(min(1.0, i / 14), 2),
            completed_tasks=[f"task_{j}" for j in range(random.randint(0, 3))],
            timeline=[
                {"time": f"{h:02d}:00", "action": random.choice(['read', 'practice']), "kp_id": random.choice(KP_IDS), "duration": random.randint(300, 600)}
                for h in range(9, 18, 3)
            ],
        ))
    db.add_all(logs)
    db.commit()

def generate_student_trends(db: Session, student_id: str):
    """生成7天趋势数据"""
    base_date = datetime.now() - timedelta(days=6)
    trends = []
    for i in range(7):
        date_str = (base_date + timedelta(days=i)).strftime('%Y-%m-%d')
        mastery = round(random.uniform(0.4, 0.85), 4)
        speed = round(random.uniform(-0.3, 0.6), 4)
        efficiency = round(random.uniform(-0.2, 0.5), 4)
        weakness = round(random.uniform(-0.5, 0.3), 4)
        stability = round(random.uniform(0.1, 0.8), 4)
        trend_factor = round(
            mastery * 0.40 + speed * 0.20 + efficiency * 0.15 + weakness * 0.15 + stability * 0.10, 4
        )
        state = "growth" if trend_factor >= 0.3 else "warning" if trend_factor <= -0.4 else "decline" if trend_factor <= -0.15 else "stable"
        trends.append(TrendDataModel(
            student_id=student_id,
            date=date_str,
            mastery_trend=mastery,
            speed_ratio=speed,
            time_efficiency=efficiency,
            weakness_priority=weakness,
            stability=stability,
            trend_factor=trend_factor,
            trend_state=state,
            predicted_mastery_3d=round(min(100, max(0, 50 + trend_factor * 50 + random.randint(-5, 5))), 2),
            intervention="保持当前学习节奏" if state == "growth" else "建议复习薄弱知识点" if state == "decline" else "注意学习连续性",
            details={"mock": True, "day_index": i},
        ))
    db.add_all(trends)
    db.commit()

def generate_gamification(db: Session, student_id: str):
    """生成游戏化数据"""
    # 积分
    points = PointsModel(
        student_id=student_id,
        total_points=random.randint(200, 800),
        daily_points=random.randint(10, 100),
        weekly_points=random.randint(50, 300),
    )
    db.add(points)

    # 成就
    achievements = [
        AchievementModel(student_id=student_id, achievement_id='ach_001', name='初出茅庐', description='完成首次学习', icon='/badges/badge1.png'),
        AchievementModel(student_id=student_id, achievement_id='ach_002', name='代码能手', description='成功运行第一段代码', icon='/badges/badge2.png'),
    ]
    db.add_all(achievements)

    # 任务
    tasks = [
        TaskModel(student_id=student_id, task_id='task_daily_1', title='阅读图文讲义', description='完成今日C语言讲义阅读', task_type='daily', reward_points=20, progress=0.3, completed=False),
        TaskModel(student_id=student_id, task_id='task_daily_2', title='提交代码练习', description='运行并提交一段C代码', task_type='daily', reward_points=30, progress=0.0, completed=False),
        TaskModel(student_id=student_id, task_id='task_weekly_1', title='完成本周测验', description='完成3次知识点测验', task_type='weekly', reward_points=50, progress=0.6, completed=False),
        TaskModel(student_id=student_id, task_id='task_challenge_1', title='指针专项突破', description='指针与内存管理专项练习', task_type='challenge', reward_points=100, progress=0.1, completed=False),
    ]
    db.add_all(tasks)

    # 排行榜
    leaderboard = LeaderboardModel(
        student_id=student_id,
        period='weekly',
        score=random.randint(100, 500),
        rank=random.randint(1, 10),
    )
    db.add(leaderboard)
    db.commit()

def clear_mock_data(db: Session, student_id: str):
    """清空该学生的旧模拟数据"""
    db.query(QuizResultModel).filter(QuizResultModel.student_id == student_id).delete()
    db.query(LearningRecordModel).filter(LearningRecordModel.student_id == student_id).delete()
    db.query(LearningLogModel).filter(LearningLogModel.student_id == student_id).delete()
    db.query(TrendDataModel).filter(TrendDataModel.student_id == student_id).delete()
    db.query(PointsModel).filter(PointsModel.student_id == student_id).delete()
    db.query(AchievementModel).filter(AchievementModel.student_id == student_id).delete()
    db.query(TaskModel).filter(TaskModel.student_id == student_id).delete()
    db.query(LeaderboardModel).filter(LeaderboardModel.student_id == student_id).delete()
    db.commit()

def main():
    db = SessionLocal()
    try:
        for sid in STUDENT_IDS:
            print(f"[Mock] 正在生成学生 {sid} 的模拟数据...")
            clear_mock_data(db, sid)
            ensure_profile(db, sid)
            generate_quiz_results(db, sid)
            generate_learning_records(db, sid)
            generate_learning_logs(db, sid)
            generate_student_trends(db, sid)
            generate_gamification(db, sid)
            print(f"[Mock] 学生 {sid} 模拟数据生成完成")
        print("[Mock] 所有模拟数据生成完毕")
    finally:
        db.close()

if __name__ == '__main__':
    main()
