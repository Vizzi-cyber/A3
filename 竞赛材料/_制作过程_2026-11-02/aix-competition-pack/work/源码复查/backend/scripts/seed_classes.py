"""
班级维度初始化脚本（教师端班级对比/试点分组）
==============================================
1. users 表添加 class_id 列（幂等）
2. 为现有学生分配班级（默认按批次分组，可手动修改）

运行：cd backend && python scripts/seed_classes.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.database import SessionLocal, Base, engine
from app.models.user import UserModel

# 默认班级分配：student_00x → 计科2401，其余学生 → 电信2401
# 试点时可将实验组/对照组设为不同班级
DEFAULT_CLASSES = {
    "计科2401": ["student_001", "student_002", "student_003"],
    "电信2401": [],  # 其余学生自动归入
}

OTHER_CLASS = "电信2401"


def _ensure_column():
    """幂等添加 class_id 列"""
    from sqlalchemy import inspect, text
    insp = inspect(engine)
    if "class_id" not in [c["name"] for c in insp.get_columns("users")]:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE users ADD COLUMN class_id VARCHAR(64)"))
        print("[迁移] users.class_id 列已添加")
    else:
        print("[已存在] users.class_id 列")


def main():
    _ensure_column()
    db = SessionLocal()
    try:
        assigned = 0
        # 第一步：明确分配（先 commit，避免未 flush 的赋值被后续查询覆盖）
        for class_name, student_ids in DEFAULT_CLASSES.items():
            for sid in student_ids:
                user = db.query(UserModel).filter(UserModel.student_id == sid).first()
                if user:
                    user.class_id = class_name
                    assigned += 1
        db.commit()

        # 第二步：其余学生归入默认班级（教师/admin 不分配）
        others = db.query(UserModel).filter(
            UserModel.role == "student",
            UserModel.class_id.is_(None),
        ).all()
        for user in others:
            user.class_id = OTHER_CLASS
            assigned += 1

        db.commit()
        classes = db.query(UserModel.class_id).filter(
            UserModel.class_id.isnot(None),
        ).distinct().all()
        print(f"[完成] 已分配 {assigned} 名学生，班级列表: {[c[0] for c in classes]}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
