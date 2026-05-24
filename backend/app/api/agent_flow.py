"""
Agent 工作流可视化 API
提供多智能体执行过程的实时状态推送
"""
import asyncio
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from .auth import require_auth

router = APIRouter()


# ---------- 内存存储 ----------
class AgentFlowStore:
    """全局 Agent 执行状态存储（内存，按 run_id 隔离）"""

    def __init__(self):
        self._runs: Dict[str, Dict[str, Any]] = {}

    def create_run(self, run_id: str, student_id: str, task_type: str):
        self.cleanup_old()
        self._runs[run_id] = {
            "run_id": run_id,
            "student_id": student_id,
            "task_type": task_type,
            "status": "running",
            "agents": {
                "supervisor": {"status": "idle", "task": "", "log": "", "started_at": None, "completed_at": None},
                "profiler": {"status": "idle", "task": "", "log": "", "started_at": None, "completed_at": None},
                "resource_generator": {"status": "idle", "task": "", "log": "", "started_at": None, "completed_at": None},
                "path_planner": {"status": "idle", "task": "", "log": "", "started_at": None, "completed_at": None},
                "tutor": {"status": "idle", "task": "", "log": "", "started_at": None, "completed_at": None},
                "assembler": {"status": "idle", "task": "", "log": "", "started_at": None, "completed_at": None},
            },
            "logs": [],
            "final_output": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

    def push_event(self, run_id: str, node_name: str, status: str, task: str = "", log: str = ""):
        if run_id not in self._runs:
            return
        run = self._runs[run_id]
        now = datetime.now(timezone.utc).isoformat()

        agent = run["agents"].get(node_name)
        if agent:
            agent["status"] = status
            if task:
                agent["task"] = task
            if log:
                agent["log"] = log
            if status == "running":
                agent["started_at"] = now
            elif status in ("completed", "failed"):
                agent["completed_at"] = now

        run["logs"].append({
            "timestamp": now,
            "agent": node_name,
            "status": status,
            "message": task or log or f"{node_name} {status}",
        })

    def complete_run(self, run_id: str, final_output: Any = None, error: str = None):
        if run_id not in self._runs:
            return
        run = self._runs[run_id]
        run["status"] = "failed" if error else "completed"
        run["final_output"] = final_output
        if error:
            run["logs"].append({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "agent": "system",
                "status": "failed",
                "message": error,
            })

    def get_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        return self._runs.get(run_id)

    def cleanup_old(self, max_age_seconds: int = 3600):
        """清理超过 max_age_seconds 的旧 run"""
        now = datetime.now(timezone.utc)
        to_delete = []
        for rid, run in self._runs.items():
            created = run.get("created_at", "")
            if created:
                try:
                    created_dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                    if (now - created_dt).total_seconds() > max_age_seconds:
                        to_delete.append(rid)
                except (ValueError, TypeError):
                    pass
        for rid in to_delete:
            del self._runs[rid]


# 全局单例
flow_store = AgentFlowStore()


# ---------- 请求/响应模型 ----------
class AgentFlowRunRequest(BaseModel):
    student_id: str
    task_type: str  # profile_update / resource_generation / path_planning / tutoring
    context: Dict[str, Any] = {}


class AgentNodeStatus(BaseModel):
    status: str
    task: str = ""
    log: str = ""
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


class AgentFlowStatusResponse(BaseModel):
    run_id: str
    student_id: str
    task_type: str
    status: str
    agents: Dict[str, AgentNodeStatus]
    logs: List[Dict[str, Any]]
    final_output: Optional[Any] = None
    created_at: str


# ---------- 路由 ----------
@router.post("/run")
async def start_agent_flow(request: AgentFlowRunRequest, _current: str = Depends(require_auth)):
    """启动一次多智能体工作流执行"""
    run_id = str(uuid.uuid4())[:12]
    flow_store.create_run(run_id, request.student_id, request.task_type)

    # 后台执行 LangGraph
    asyncio.create_task(_execute_graph(run_id, request))

    return {"run_id": run_id, "status": "running", "task_type": request.task_type}


@router.get("/{run_id}/status")
async def get_agent_flow_status(run_id: str, _current: str = Depends(require_auth)):
    """查询工作流执行状态"""
    run = flow_store.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


async def _execute_graph(run_id: str, request: AgentFlowRunRequest):
    """后台执行 LangGraph 并推送事件"""
    try:
        from ..graph.graph import LearningGraphRunner

        runner = LearningGraphRunner()

        # 把 run_id 注入 context，让 nodes.py 里的 _push 能找到对应的 run
        ctx = dict(request.context)
        ctx["_run_id"] = run_id

        final = await runner.run(
            student_id=request.student_id,
            task_type=request.task_type,
            context=ctx,
        )

        flow_store.complete_run(run_id, final_output=final)
    except Exception as e:
        flow_store.complete_run(run_id, error=str(e))
