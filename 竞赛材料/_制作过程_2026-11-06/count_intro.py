# -*- coding: utf-8 -*-
text = (
    "新工科课堂有三个老问题：学生基础参差却共用一份教案，实验设备有限且试错成本高，"
    "C 语言、电路、嵌入式三门课各教各的。LearnLab 让 12 个教育智能体协同应对："
    "五层算法（IRT 测量→BKT/GKT 建模→FSRS 记忆→MAB 决策→大模型解释）实时计算每个学生的掌握状态与学习路径；"
    "浏览器端 MNA 电路仿真把实验变成零成本、可反复试错的虚拟环境，AI 再叠加故障诊断；"
    "同一套错误诊断入口贯通三门课。系统已上线（www.dreamlast.cn），"
    "116 项算法断言与 211 个路由冒烟通过，真实试点前测 20 份、后测 17 份已回收，"
    "满意度 100%，配对测验均分提升 15.8 分。"
)

print("total chars:", len(text))
print("non-space:", len(text.replace(" ", "")))
print("cjk:", sum(1 for c in text if '\u4e00' <= c <= '\u9fff'))
