"""
测试种子脚本 - 填充 student_001 的画像 / 学习记录 / 反思
- 补全 weak_areas, interest_areas, learning_tempo, practical_preferences
- 插入近 7 天 learning records
- 插入近 7 天 quizzes
- 插入 cornell/feynman/反思各 1 条（用新格式 reflection_id）
- 标记 kp_c01-kp_c03 为 completed
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime, timedelta
from app.models.database import SessionLocal
from app.models.student import StudentProfileModel
from app.models.knowledge import LearningRecordModel, QuizResultModel
from app.models.log_reflection import ReflectionModel

STUDENT_ID = "student_001"


def seed_profile(db):
    """补全画像缺失字段"""
    p = db.query(StudentProfileModel).filter(StudentProfileModel.student_id == STUDENT_ID).first()
    if not p:
        print(f"[skip] profile {STUDENT_ID} not found")
        return
    p.weak_areas = ["指针与内存", "递归函数", "动态内存管理", "结构体"]
    p.interest_areas = ["C语言程序设计", "系统开发", "数据结构"]
    p.learning_goals = ["掌握 C 语言核心语法", "完成数据结构入门", "能独立写小项目"]
    p.error_patterns = ["数组越界", "指针解引用空值", "忘记 free"]
    p.learning_tempo = {
        "study_speed": "moderate",
        "preferred_session_length": 45,
        "daily_target_minutes": 90,
    }
    p.practical_preferences = {
        "overall_score": 0.75,
        "code_practice": 0.85,
        "video_watching": 0.55,
        "reading": 0.65,
    }
    p.cognitive_style = {
        **(p.cognitive_style or {}),
        "primary": "kinesthetic",
        "secondary": "visual",
        "learning_preference": "动手实践型",
    }
    db.commit()
    print(f"[ok] profile updated: weak_areas={p.weak_areas}, tempo={p.learning_tempo}")


def seed_learning_records(db):
    """插入近 7 天的学习记录与 quiz 记录"""
    today = datetime.now()
    # 清理脚本之前生成的 seed 记录（按 record_id 前缀）
    db.query(LearningRecordModel).filter(LearningRecordModel.record_id.like("seed_lr_%")).delete()
    db.query(QuizResultModel).filter(QuizResultModel.quiz_id.like("seed_qz_%")).delete()
    db.commit()

    records = []
    quizzes = []
    kps = ["kp_c01", "kp_c02", "kp_c03", "kp_c04", "kp_c05", "kp_c06", "kp_c07"]
    actions = ["watch", "practice", "complete", "watch", "practice", "complete", "review"]
    durations = [1500, 1800, 1200, 900, 2100, 1500, 600]
    progresses = [0.6, 0.8, 1.0, 0.4, 0.7, 1.0, 0.3]

    for i in range(7):
        d = today - timedelta(days=6 - i)
        kp = kps[i]
        rec = LearningRecordModel(
            record_id=f"seed_lr_{i}_{int(d.timestamp())}",
            student_id=STUDENT_ID,
            kp_id=kp,
            action=actions[i],
            duration=durations[i],
            progress=progresses[i],
            score=70 + i * 3,
            created_at=d.replace(hour=10, minute=30, second=0, microsecond=0),
        )
        records.append(rec)
        # 同步建一个 quiz
        score = 68 + i * 4
        qz = QuizResultModel(
            quiz_id=f"seed_qz_{i}_{int(d.timestamp())}",
            student_id=STUDENT_ID,
            kp_id=kp,
            total_questions=10,
            correct_count=int(score / 10),
            score=score,
            weak_tags=["指针与内存"] if i in (0, 3) else (["递归函数"] if i in (1, 4) else ["结构体"] if i == 2 else []),
            time_spent=300,
            answers=[{"q": j, "correct": j % 2 == 0} for j in range(10)],
            created_at=d.replace(hour=11, minute=0, second=0, microsecond=0),
        )
        quizzes.append(qz)

    db.add_all(records + quizzes)
    db.commit()
    print(f"[ok] inserted {len(records)} learning records + {len(quizzes)} quizzes")


def seed_reflections(db):
    """插入 cornell/feynman/反思各一条，用新格式 reflection_id"""
    today_str = datetime.now().strftime("%Y-%m-%d")
    yesterday_str = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    # 清理本脚本之前生成的 seed 反思
    db.query(ReflectionModel).filter(ReflectionModel.reflection_id.like("seed_ref_%")).delete()
    db.commit()

    items = [
        {
            "id": f"seed_ref_{STUDENT_ID}_{today_str}_cornell_{int(datetime.now().timestamp() * 1000)}",
            "date": today_str,
            "content": '{"cues":"指针 vs 数组","notes":"指针存的是地址，数组名是首地址常量","summary":"理解差异，避免混用"}',
            "tags": ["cornell"],
            "mood": "neutral",
        },
        {
            "id": f"seed_ref_{STUDENT_ID}_{today_str}_feynman_{int(datetime.now().timestamp() * 1000) + 1}",
            "date": today_str,
            "content": "递归就像照镜子里的镜子：函数自己调自己，每次问题更小一点，直到最简单的那一层（基线条件）直接给答案，再一层层把答案传回来。",
            "tags": ["feynman"],
            "mood": "excited",
        },
        {
            "id": f"seed_ref_{STUDENT_ID}_{yesterday_str}_reflection_{int(datetime.now().timestamp() * 1000) + 2}",
            "date": yesterday_str,
            "content": "今天理解了 malloc/free 的配对，但写嵌套结构体释放顺序时还是搞错了一次，明天巩固一下。",
            "tags": ["反思", "动态内存"],
            "mood": "frustrated",
            "ai_feedback": "推荐使用结构化的 free 顺序：先释放内层指针，再释放外层；可以画一张分配图辅助理解。",
        },
        {
            "id": f"seed_ref_{STUDENT_ID}_{today_str}_notes_{int(datetime.now().timestamp() * 1000) + 3}",
            "date": today_str,
            "content": "kp_c03 - 运算符优先级：算术 > 关系 > 逻辑 > 赋值；位运算与移位常被忽视。",
            "tags": ["notes", "kp_c03"],
            "mood": "neutral",
        },
    ]
    for it in items:
        ref = ReflectionModel(
            reflection_id=it["id"],
            student_id=STUDENT_ID,
            date=it["date"],
            content=it["content"],
            mood=it["mood"],
            tags=it["tags"],
            ai_feedback=it.get("ai_feedback"),
        )
        db.add(ref)
    db.commit()
    print(f"[ok] inserted {len(items)} reflections (cornell/feynman/reflection/notes)")


def main():
    db = SessionLocal()
    try:
        seed_profile(db)
        seed_learning_records(db)
        seed_reflections(db)
        print("\n[done] seeding complete for student_001")
    finally:
        db.close()


if __name__ == "__main__":
    main()
