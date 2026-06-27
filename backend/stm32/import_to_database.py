"""
STM32课程数据导入脚本
将 knowledge_tree.json 和 resources_full.json 导入到 EduForge 数据库

使用方法:
    cd backend
    python ../stm32/import_to_database.py
"""

import json
import sys
from pathlib import Path

# 添加后端路径
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from database import SessionLocal, engine, Base
from models.knowledge import Course, KnowledgePoint
from models.resource import Resource
from models.experiment import Experiment


def load_json(file_path: str) -> dict:
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def import_courses(db, data: dict):
    """导入课程数据"""
    for course_data in data.get('courses', []):
        existing = db.query(Course).filter(Course.id == course_data['id']).first()
        if existing:
            print(f"  [跳过] 课程已存在: {course_data['name']}")
            continue

        course = Course(
            id=course_data['id'],
            name=course_data['name'],
            description=course_data.get('description', ''),
            difficulty=course_data.get('difficulty', ''),
            target_major=course_data.get('target_major', '')
        )
        db.add(course)
        print(f"  [导入] 课程: {course_data['name']}")
    db.commit()


def import_knowledge_points(db, data: dict):
    """导入知识点数据"""
    for kp_data in data.get('knowledge_points', []):
        existing = db.query(KnowledgePoint).filter(KnowledgePoint.id == kp_data['id']).first()
        if existing:
            print(f"  [跳过] 知识点已存在: {kp_data['name']}")
            continue

        kp = KnowledgePoint(
            id=kp_data['id'],
            name=kp_data['name'],
            description=kp_data.get('description', ''),
            parent_id=kp_data.get('parent_id'),
            level=kp_data.get('level', 0),
            difficulty=kp_data.get('difficulty', ''),
            course_id=kp_data.get('course_id'),
            sort_order=kp_data.get('sort_order', 0),
            prerequisites=json.dumps(kp_data.get('prerequisites', []), ensure_ascii=False)
        )
        db.add(kp)
        print(f"  [导入] 知识点: {kp_data['name']}")
    db.commit()


def import_resources(db, data: dict):
    """导入资源数据"""
    for res_data in data.get('resources', []):
        existing = db.query(Resource).filter(Resource.id == res_data['id']).first()
        if existing:
            print(f"  [跳过] 资源已存在: {res_data['title']}")
            continue

        # 构建完整内容
        content = {
            'title': res_data['title'],
            'type': res_data['type'],
            'description': res_data.get('description', ''),
            'file_path': res_data.get('file_path', ''),
            'image_path': res_data.get('image_path', ''),
        }

        resource = Resource(
            id=res_data['id'],
            title=res_data['title'],
            type=res_data['type'],
            knowledge_id=res_data.get('knowledge_id'),
            difficulty=res_data.get('difficulty', ''),
            content=json.dumps(content, ensure_ascii=False),
            file_path=res_data.get('file_path', ''),
            creator=res_data.get('creator', '系统')
        )
        db.add(resource)
        print(f"  [导入] 资源: {res_data['title']}")
    db.commit()


def import_experiments(db, data: dict):
    """导入实验数据"""
    for exp_data in data.get('experiments', []):
        existing = db.query(Experiment).filter(Experiment.id == exp_data['id']).first()
        if existing:
            print(f"  [跳过] 实验已存在: {exp_data['title']}")
            continue

        experiment = Experiment(
            id=exp_data['id'],
            title=exp_data['title'],
            knowledge_id=exp_data.get('knowledge_id'),
            difficulty=exp_data.get('difficulty', ''),
            objective=exp_data.get('objective', ''),
            principle=exp_data.get('principle', ''),
            steps=json.dumps(exp_data.get('steps', []), ensure_ascii=False),
            circuit_diagram=json.dumps(exp_data.get('circuit_diagram', {}), ensure_ascii=False),
            code_template=exp_data.get('code_template', ''),
            scoring_criteria=json.dumps(exp_data.get('scoring_criteria', {}), ensure_ascii=False),
            report_template=json.dumps(exp_data.get('report_template', []), ensure_ascii=False)
        )
        db.add(experiment)
        print(f"  [导入] 实验: {exp_data['title']}")
    db.commit()


def main():
    # 数据文件路径
    stm32_dir = Path(__file__).parent
    knowledge_file = stm32_dir / 'knowledge_tree.json'
    resources_file = stm32_dir / 'resources_full.json'

    if not knowledge_file.exists():
        print(f"错误: 找不到文件 {knowledge_file}")
        return
    if not resources_file.exists():
        print(f"错误: 找不到文件 {resources_file}")
        return

    print("=" * 50)
    print("STM32课程数据导入工具")
    print("=" * 50)

    # 加载数据
    print("\n[1/4] 加载知识树数据...")
    knowledge_data = load_json(str(knowledge_file))

    print("[2/4] 加载资源数据...")
    resources_data = load_json(str(resources_file))

    # 创建数据库会话
    db = SessionLocal()

    try:
        print("\n[3/4] 导入数据到数据库...")
        print("\n  导入课程...")
        import_courses(db, knowledge_data)

        print("\n  导入知识点...")
        import_knowledge_points(db, knowledge_data)

        print("\n  导入资源...")
        import_resources(db, resources_data)

        print("\n  导入实验...")
        import_experiments(db, knowledge_data)

        print("\n[4/4] 验证数据...")
        course_count = db.query(Course).count()
        kp_count = db.query(KnowledgePoint).count()
        resource_count = db.query(Resource).count()
        exp_count = db.query(Experiment).count()

        print(f"  课程: {course_count}")
        print(f"  知识点: {kp_count}")
        print(f"  资源: {resource_count}")
        print(f"  实验: {exp_count}")

        print("\n" + "=" * 50)
        print("导入完成!")
        print("=" * 50)

    except Exception as e:
        print(f"\n错误: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == '__main__':
    main()
