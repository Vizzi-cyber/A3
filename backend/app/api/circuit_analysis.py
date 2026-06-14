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


@router.post("/analyze")
async def analyze_circuit(
    request: CircuitAnalysisRequest,
    _current: str = Depends(require_auth),
):
    """AI分析电路"""
    try:
        llm = LLMFactory.get_default_llm()

        netlist_str = "\n".join(
            f"{el.name}: {el.type} between node {el.node1} and node {el.node2}, "
            f"value={el.value}"
            for el in request.netlist
        )

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
        raise HTTPException(status_code=500, detail=str(e))
