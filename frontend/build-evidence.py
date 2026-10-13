# -*- coding: utf-8 -*-
"""佐证材料实证部分：测试数据摘要 + 系统截图 → HTML"""
import os
import glob

ASSETS = "交付材料/_assets"
shots = sorted(glob.glob(os.path.join(ASSETS, "*.png")))

shot_captions = {
    "01-登录页": "平台登录页：支持账号登录、学生注册与一键体验",
    "02-学生仪表盘": "学生仪表盘：学习进度、每日练习与知识点掌握度环形图",
    "03-学习路径": "个性化学习路径：ADPP 算法生成的 16 阶段跨学科计划与复习建议",
    "04-学习中心": "学习中心：课程目录、图文讲义、康奈尔线索栏与 AI 辅导助手三栏阅读视图",
    "05-知识冒险": "知识冒险：游戏化挑战地图与知识树成长体系",
    "06-排行榜": "多维排行榜：学习成长/连续学习/知识掌握/闯关挑战/AI 协作/进步最快六维度",
    "07-AI智能辅导": "AI 智能辅导：苏格拉底式引导对话，支持 RAG 检索增强与流式输出",
    "08-错误诊断": "错误诊断系统：语法错误/逻辑错误定位与思维误区溯源（tree-sitter 静态分析 + AI 评估）",
    "09-个人空间": "个人空间：学习时长、勋章徽章、专注度趋势与学习历史",
    "10-教师工作台": "教师工作台：全班学情概览、薄弱知识点 TOP10 与成绩分布",
    "11-学情分析": "学情分析：班级薄弱知识点分布与薄弱领域统计",
    "12-试点数据分析": "试点数据分析：实验组/对照组五维数据聚合，一键导出报告（Markdown）",
    "13-AI智能组卷": "AI 智能组卷：输入主题与知识点，AI 自动生成多题型试卷",
}

img_html = []
for fp in shots:
    name = os.path.splitext(os.path.basename(fp))[0]
    cap = shot_captions.get(name, name)
    rel = os.path.relpath(fp, "交付材料/_佐证实证").replace("\\", "/")
    img_html.append(
        f'<div class="shot"><img src="{rel}"><div class="cap">图：{cap}</div></div>'
    )
imgs = "\n".join(img_html)

test_rows = [
    ("算法层专项断言", "BKT/IRT/FSRS/MAB/GKT/NCD/时间留出评估/五层接线/趋势学习器/匹配探索", "116/116 通过"),
    ("算法接线 API 冒烟", "演示库真实数据训练 IRT/GKT/趋势学习器 + MAB 闭环回传", "38/38 通过"),
    ("后端全路由冒烟", "210 个路由逐一调用", "0 崩溃"),
    ("AIC 功能回归", "跨学科链路/试点报告/故障实验/实验日志", "29/29 通过"),
    ("数据流验证", "学习行为→画像→路径→效果全链路", "23/23 通过"),
    ("Agent/LLM 专项", "多智能体编排/降级链/防幻觉守卫", "23/23 通过"),
    ("前端 E2E", "学生端核心流程 Playwright 用例", "49/49 通过"),
    ("MNA 数值对照", "RC/RL/C 电路暂态对照教科书解析解", "9/9 通过"),
    ("真实环境部署验证", "腾讯云 + Nginx + HTTPS 生产环境", "24h 零 500，接口平均响应 <60ms"),
    ("全系统提交前实测", "24 页逐页遍历 + API 26 项 + 新用户 11 步全旅程", "零 JS 错误、零失败请求"),
]

rows_html = "\n".join(
    f"<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>" for a, b, c in test_rows
)

html = f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><style>
@page {{ size: A4; margin: 0; }}
body {{ font-family: "SimSun","Songti SC",serif; font-size: 11pt; line-height: 1.8; color:#000; margin:0; }}
h1 {{ font-family: "SimHei","Heiti SC",sans-serif; font-size: 19pt; text-align: center; margin: 4mm 0 3mm; }}
.meta {{ text-align: center; font-size: 10.5pt; color:#333; margin-bottom: 6mm; }}
h2 {{ font-family: "SimHei","Heiti SC",sans-serif; font-size: 14pt; margin: 8mm 0 3mm; border-bottom: 1.5pt solid #000; padding-bottom: 1.5mm; page-break-after: avoid; }}
p {{ margin: 0 0 2mm; text-align: justify; }}
table {{ width: 100%; border-collapse: collapse; font-size: 10pt; margin: 3mm 0; }}
th, td {{ border: 1pt solid #000; padding: 3px 6px; text-align: left; vertical-align: top; }}
th {{ font-family: "SimHei","Heiti SC",sans-serif; font-weight: bold; }}
.shot {{ page-break-inside: avoid; margin: 4mm 0 6mm; }}
.shot img {{ width: 100%; border: 0.75pt solid #000; }}
.cap {{ font-size: 9.5pt; color: #333; margin-top: 1.5mm; text-align: center; }}
</style></head><body>
<h1>佐证材料——测试验证与系统运行实证</h1>
<div class="meta">LearnLab：AI 赋能新工科跨学科学习平台 · 第八届 AIC 算法创新赛（AI+学科交叉）</div>

<h2>一、测试验证数据摘要</h2>
<p>平台全部验证脚本随源码交付（backend/scripts/），以下结果均可一键复现。另有提交前全系统实测 3 轮：24 个页面逐页遍历零 JS 错误、API 全接口 26 项通过（含越权访问 403 校验）、新用户注册到成就解锁 11 步全旅程零异常、生产环境 24 小时零 500 错误。</p>
<table>
<tr><th style="width:24%">验证项</th><th style="width:48%">范围</th><th>结果</th></tr>
{rows_html}
</table>

<h2>二、算法效果对照设计</h2>
<p>平台内置七处"传统方法 vs 算法"可量化对照点（掌握度测量/路径成本/知识追踪/掌握度传播/记忆调度/路径调整策略/选题与资源推荐），试点期间数据自动落库，用于产出应用效果的量化对比（详见技术方案（六）3）。</p>

<h2>三、系统功能实证截图</h2>
{imgs}
</body></html>"""

os.makedirs("交付材料/_佐证实证", exist_ok=True)
open("交付材料/_佐证实证/佐证实证.html", "w", encoding="utf-8", newline="\n").write(html)
print("HTML_OK, 截图数:", len(shots))
