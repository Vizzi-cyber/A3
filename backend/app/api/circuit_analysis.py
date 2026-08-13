"""
电路分析API - AI辅助电路分析
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from ..services.llm_factory import LLMFactory
from ..core.logger import setup_logger
from .auth import require_auth

logger = setup_logger()
router = APIRouter()


class NetlistElement(BaseModel):
    name: str
    type: str
    node1: int
    node2: int
    value: float


class CircuitAnalysisRequest(BaseModel):
    netlist: List[NetlistElement]
    node_voltages: Optional[dict] = None
    branch_currents: Optional[dict] = None
    student_question: Optional[str] = None
    student_level: str = "beginner"
    # 故障实验诊断模式
    is_diagnosis: bool = False
    fault_description: Optional[str] = None
    student_answer: Optional[str] = None
    expected_answer: Optional[str] = None


@router.post("/analyze")
async def analyze_circuit(
    request: CircuitAnalysisRequest,
    _current: str = Depends(require_auth),
):
    """AI分析电路（支持故障实验诊断评估模式）"""
    try:
        llm = LLMFactory.get_default_llm()

        netlist_str = "\n".join(
            f"{el.name}: {el.type} between node {el.node1} and node {el.node2}, "
            f"value={el.value}"
            for el in request.netlist
        )

        # ---------- 故障实验诊断模式 ----------
        if request.is_diagnosis:
            prompt = f"""你是一位电路实验课教师，正在批改学生的故障诊断实验报告。请评估学生的诊断。

电路网表：
{netlist_str}

节点电压：{request.node_voltages}
支路电流：{request.branch_currents}

实验现象描述（故障表现）：
{request.fault_description or '（未提供）'}

学生给出的故障判断：
{request.student_answer or '（未作答）'}

标准答案：
{request.expected_answer or '（未提供）'}

请提供（用Markdown格式）：
1. 判断：学生答案是否正确（先说"✅ 诊断正确"或"❌ 诊断有误"，再说明理由）
2. 故障原理讲解：这个故障为什么会导致上述现象（从电路理论解释，学生水平为{request.student_level}）
3. 排查方法：如果学生答错，给出正确的排查思路（如何用万用表/测量定位故障）
4. 知识要点：该实验考察的核心知识点"""
            messages = [{"role": "user", "content": prompt}]
            result = await llm.ainvoke(messages, temperature=0.3, max_tokens=2048)
            return {
                "status": "success",
                "analysis": result,
                "circuit_description": "故障诊断实验评估",
                "mode": "diagnosis",
            }

        # ---------- 常规电路分析模式 ----------
        prompt = f"""你是一位电路分析教学专家。请分析以下电路：

网表：
{netlist_str}

"""
        if request.node_voltages:
            prompt += f"节点电压：{request.node_voltages}\n"
        if request.branch_currents:
            prompt += f"支路电流：{request.branch_currents}\n"

        if request.student_question:
            prompt += f"\n学生提问：{request.student_question}\n"

        prompt += f"""
请提供：
1. 电路功能描述（这个电路做什么？）
2. 关键节点电压和支路电流的物理解释
3. 电路设计的优缺点
4. 学生水平为{request.student_level}，请用适合的语言解释
5. 如果有错误或不合理之处，请指出

请用Markdown格式回答。"""

        messages = [{"role": "user", "content": prompt}]
        result = await llm.ainvoke(messages, temperature=0.3, max_tokens=2048)

        return {
            "status": "success",
            "analysis": result,
            "circuit_description": f"包含 {len(request.netlist)} 个元件的电路",
        }

    except Exception as e:
        logger.error(f"Circuit analysis failed: {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")
