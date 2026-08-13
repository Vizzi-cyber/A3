"""
跨学科数据注入脚本（AIC算法创新赛 · AI+学科交叉）
==================================================
1. 为 knowledge_points 注入跨课程前置依赖（跨学科学习链路）
2. 初始化 courses 学科元数据表（学科定位、核心环节、学科交叉说明）

幂等设计：可重复运行，已存在的关联不会重复添加。

运行：cd backend && python scripts/seed_cross_discipline.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.database import SessionLocal, Base, engine
from app.models.knowledge import KnowledgePointModel
from app.models.course import CourseModel


def _ensure_tables():
    """确保数据表存在（courses 为新表，未走应用启动流程时需手动建表）"""
    # 导入全部模型确保注册到 metadata
    import app.models  # noqa: F401
    Base.metadata.create_all(engine)

# ============================================================
# 跨课程前置依赖（9条）
# 体现"编程思维 → 电路建模 → 嵌入式实现"的跨学科学习链路
# 格式: 目标知识点 <- 跨学科前置知识点
# ============================================================
CROSS_PREREQUISITES = [
    # --- 编程思维 → 嵌入式实现（C语言 × STM32）---
    ("kp_s01", "kp_c10", "STM32基础入门依赖C语言指针：嵌入式开发中的寄存器操作与内存地址管理"),
    ("kp_s02", "kp_c16", "GPIO输出控制依赖C语言位运算：寄存器置位/清零操作"),
    ("kp_s03", "kp_c16", "GPIO输入检测依赖C语言位运算：按键读取与位掩码判断"),
    ("kp_s04", "kp_c08", "OLED显示模块依赖C语言字符串：字符显示与格式化输出"),
    ("kp_s07", "kp_c11", "DMA数据转运依赖C语言指针与数组：内存搬运与缓冲区操作"),
    ("kp_s08", "kp_c10", "UART串口通信依赖C语言指针：协议帧解析与数据缓冲区"),
    # --- 电路建模 → 嵌入式实现（电路分析 × STM32）---
    ("kp_s05", "kp_e01", "定时器与PWM依赖电路基本概念：电压波形与占空比物理意义"),
    ("kp_s06", "kp_e02", "ADC模数转换依赖电阻串并联：分压采样电路原理"),
    # --- 编程思维 → 电路建模（C语言 × 电路分析）---
    ("kp_e03", "kp_c07", "支路电流法依赖C语言数组：线性方程组的数组建模与求解"),
]

# ============================================================
# 学科课程元数据（3门课，对应新工科"计算机+电子信息"交叉定位）
# ============================================================
COURSES = [
    {
        "course_id": "C语言",
        "name": "C语言程序设计",
        "discipline": "计算机科学与技术",
        "core_phases": ["教学实践", "自主学习"],
        "description": "计算机科学与技术专业核心基础课，为嵌入式系统开发提供编程基础（指针、位运算、数组）",
        "icon": "💻",
        "color": "#1677ff",
        "linked_courses": [
            {"course": "STM32嵌入式", "link": "编程思维→嵌入式实现：指针/位运算/数组是嵌入式开发的直接编程基础"},
            {"course": "电路分析", "link": "编程思维→电路建模：线性方程组的数组建模与数值求解"},
        ],
    },
    {
        "course_id": "电路分析",
        "name": "电路分析基础",
        "discipline": "电子信息工程",
        "core_phases": ["实验实训", "理论学习"],
        "description": "电子信息类专业核心基础课，结合浏览器端MNA仿真与AI诊断实现虚拟实验实训",
        "icon": "⚡",
        "color": "#fa541c",
        "linked_courses": [
            {"course": "STM32嵌入式", "link": "电路建模→嵌入式实现：分压采样（ADC）、电压波形（PWM）是外围电路设计基础"},
            {"course": "C语言", "link": "编程思维→电路建模：方程组建模与数值计算"},
        ],
    },
    {
        "course_id": "STM32嵌入式",
        "name": "STM32嵌入式系统开发",
        "discipline": "计算机科学与技术 × 电子信息工程（交叉）",
        "core_phases": ["实验实训", "自主学习"],
        "description": "新工科交叉实践课，衔接C语言编程与电路分析，面向真实嵌入式系统开发",
        "icon": "🔧",
        "color": "#52c41a",
        "linked_courses": [
            {"course": "C语言", "link": "嵌入式实现←编程思维：全部外设编程均基于C语言核心语法"},
            {"course": "电路分析", "link": "嵌入式实现←电路建模：外围电路设计基于电路分析基础"},
        ],
    },
]


def main():
    _ensure_tables()
    db = SessionLocal()
    try:
        # ---------- 1. 注入跨课程前置依赖 ----------
        added = 0
        for target, prereq, reason in CROSS_PREREQUISITES:
            kp = db.query(KnowledgePointModel).filter(
                KnowledgePointModel.kp_id == target
            ).first()
            if not kp:
                print(f"[跳过] 知识点 {target} 不存在")
                continue
            prereqs = list(kp.prerequisites or [])
            if prereq not in prereqs:
                prereqs.append(prereq)
                kp.prerequisites = prereqs
                added += 1
                print(f"[注入] {target} <- {prereq} ({reason})")
            else:
                print(f"[已存在] {target} <- {prereq}")

        # ---------- 2. 初始化课程元数据 ----------
        for c in COURSES:
            existing = db.query(CourseModel).filter(
                CourseModel.course_id == c["course_id"]
            ).first()
            if existing:
                for k, v in c.items():
                    setattr(existing, k, v)
                print(f"[更新] 课程元数据: {c['course_id']}")
            else:
                db.add(CourseModel(**c))
                print(f"[新增] 课程元数据: {c['course_id']}")

        db.commit()
        print(f"\n完成：新增跨课程依赖 {added} 条，课程元数据 {len(COURSES)} 门")
    finally:
        db.close()


if __name__ == "__main__":
    main()
