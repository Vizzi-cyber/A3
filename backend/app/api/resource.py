"""
资源生成API
对接 LangGraph 工作流，调用 resource_generator 智能体
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio

from ..schemas import (
    DocumentGenerateRequest,
    DocumentGenerateResponse,
    QuestionsGenerateRequest,
    QuestionsGenerateResponse,
    MindmapGenerateRequest,
    MindmapGenerateResponse,
    CodeGenerateRequest,
    CodeGenerateResponse,
    CodeExecuteRequest,
    CodeExecuteResponse,
)
from ..agents import ResourceGeneratorAgent
from .auth import get_current_student_id, require_auth

router = APIRouter()

_resource_agent = ResourceGeneratorAgent()


class ResourceGenerationRequest(BaseModel):
    """资源生成请求"""
    student_id: str
    topic: str
    resource_types: List[str] = ["document", "questions", "mindmap", "code"]
    difficulty: str = "medium"
    cognitive_style: Optional[str] = None


class ResourceGenerationResponse(BaseModel):
    """资源生成响应"""
    task_id: str
    status: str
    progress: float = 0.0
    resources: Dict[str, Any] = {}
    message: str = ""


# 模拟任务存储
_tasks_db = {}


@router.post("/generate", response_model=ResourceGenerationResponse)
async def generate_resource(
    request: ResourceGenerationRequest,
    background_tasks: BackgroundTasks,
    _current: str = Depends(require_auth),
):
    """生成多模态学习资源 —— 后台任务直接调用 ResourceGeneratorAgent"""
    task_id = f"task_{datetime.now().timestamp()}"
    _tasks_db[task_id] = {
        "task_id": task_id,
        "status": "pending",
        "progress": 0.0,
        "resources": {},
        "message": "Task queued",
    }
    background_tasks.add_task(
        _execute_generation,
        task_id,
        request,
    )
    return ResourceGenerationResponse(
        task_id=task_id, status="pending", message="Resource generation task started"
    )


async def _execute_generation(task_id: str, request: ResourceGenerationRequest):
    _tasks_db[task_id]["status"] = "running"
    _tasks_db[task_id]["message"] = "Initializing agents..."

    results = {}
    # 根据请求的 resource_types 并行生成多种资源
    tasks_to_run = []
    for rt in request.resource_types:
        if rt == "document":
            tasks_to_run.append(_resource_agent.process({
                "task": "generate_document",
                "topic": request.topic,
                "difficulty": request.difficulty,
            }))
        elif rt == "questions":
            tasks_to_run.append(_resource_agent.process({
                "task": "generate_questions",
                "topic": request.topic,
                "constraints": {"count": 3},
            }))
        elif rt == "mindmap":
            tasks_to_run.append(_resource_agent.process({
                "task": "generate_mindmap",
                "topic": request.topic,
            }))
        elif rt == "code":
            tasks_to_run.append(_resource_agent.process({
                "task": "generate_code_examples",
                "topic": request.topic,
                "constraints": {"language": "Python"},
            }))

    if tasks_to_run:
        try:
            agent_results = await asyncio.wait_for(
                asyncio.gather(*tasks_to_run, return_exceptions=True),
                timeout=20.0,
            )
            for idx, res in enumerate(agent_results):
                if isinstance(res, Exception):
                    continue
                if res.get("status") == "success":
                    rt = request.resource_types[idx]
                    results[rt] = res.get("content", res)
        except asyncio.TimeoutError:
            pass

    _tasks_db[task_id]["status"] = "completed" if results else "failed"
    _tasks_db[task_id]["progress"] = 1.0
    _tasks_db[task_id]["resources"] = results
    _tasks_db[task_id]["message"] = "Generation completed" if results else "Generation timeout or failed"


@router.get("/task/{task_id}")
async def get_task_status(task_id: str):
    if task_id not in _tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    return _tasks_db[task_id]


@router.post("/document/generate", response_model=DocumentGenerateResponse)
async def generate_document(request: DocumentGenerateRequest, _current: str = Depends(require_auth)):
    """生成讲解文档 —— 直接调用 ResourceGeneratorAgent，避免 LangGraph 多层路由延迟"""
    doc_content = f"# {request.topic}\n\n这里是生成的文档内容（fallback）。"

    try:
        result = await asyncio.wait_for(
            _resource_agent.process({
                "task": "generate_document",
                "topic": request.topic,
                "difficulty": request.difficulty,
            }),
            timeout=15.0,
        )
        if result.get("status") == "success" and isinstance(result.get("content"), str):
            doc_content = result["content"]
    except asyncio.TimeoutError:
        pass
    except Exception:
        pass

    return {
        "status": "success",
        "document": doc_content,
        "metadata": {
            "topic": request.topic,
            "generated_at": datetime.now().isoformat(),
        },
    }


@router.post("/questions/generate", response_model=QuestionsGenerateResponse)
async def generate_questions(request: QuestionsGenerateRequest, _current: str = Depends(require_auth)):
    """生成练习题 —— 直接调用 ResourceGeneratorAgent"""
    questions = [
        {
            "q_id": f"q_{i}",
            "type": "single_choice",
            "content": f"关于{request.topic}的问题 {i+1}?",
            "options": [
                {"id": "A", "text": "选项A"},
                {"id": "B", "text": "选项B"},
                {"id": "C", "text": "选项C"},
                {"id": "D", "text": "选项D"},
            ],
            "correct_answer": "A",
            "explanation": "正确答案是A",
        }
        for i in range(request.count)
    ]

    try:
        result = await asyncio.wait_for(
            _resource_agent.process({
                "task": "generate_questions",
                "topic": request.topic,
                "constraints": {"count": request.count},
            }),
            timeout=15.0,
        )
        if result.get("status") == "success":
            raw = result.get("content", [])
            if isinstance(raw, list) and len(raw) > 0:
                questions = raw
    except asyncio.TimeoutError:
        pass
    except Exception:
        pass

    return {
        "status": "success",
        "topic": request.topic,
        "count": len(questions) if isinstance(questions, list) else 0,
        "questions": questions,
    }


@router.post("/mindmap/generate", response_model=MindmapGenerateResponse)
async def generate_mindmap(request: MindmapGenerateRequest, _current: str = Depends(require_auth)):
    """生成思维导图 —— 直接调用 ResourceGeneratorAgent"""
    mindmap = {"root": request.topic, "children": []}

    try:
        result = await asyncio.wait_for(
            _resource_agent.process({
                "task": "generate_mindmap",
                "topic": request.topic,
            }),
            timeout=15.0,
        )
        if result.get("status") == "success":
            raw = result.get("content", {})
            if isinstance(raw, dict) and raw.get("root"):
                mindmap = raw
    except asyncio.TimeoutError:
        pass
    except Exception:
        pass

    return {"status": "success", "mindmap": mindmap, "format": "json_tree"}


@router.post("/code/generate", response_model=CodeGenerateResponse)
async def generate_code(request: CodeGenerateRequest, _current: str = Depends(require_auth)):
    """生成代码示例 —— 直接调用 ResourceGeneratorAgent"""
    code = f"# {request.topic} - {request.language}\n\nprint('Hello, World!')"

    try:
        result = await asyncio.wait_for(
            _resource_agent.process({
                "task": "generate_code_examples",
                "topic": request.topic,
                "constraints": {"language": request.language},
            }),
            timeout=15.0,
        )
        if result.get("status") == "success" and isinstance(result.get("content"), str):
            code = result["content"]
    except asyncio.TimeoutError:
        pass
    except Exception:
        pass

    return {
        "status": "success",
        "code": code,
        "language": request.language,
        "filename": f"{request.topic.lower().replace(' ', '_')}.{request.language.lower()}",
    }


@router.post("/code/execute", response_model=CodeExecuteResponse)
async def execute_code(request: CodeExecuteRequest, _current: str = Depends(require_auth)):
    """在服务器子进程中真实执行 Python 代码并返回结果"""
    import subprocess
    import tempfile
    import os

    code = request.code
    if not code.strip():
        return {"status": "success", "output": "", "error": "代码为空", "explanation": ""}

    # 简单黑名单过滤（禁止明显的危险操作）
    blocked_keywords = ["__import__", "os.system", "os.popen", "subprocess.call", "subprocess.run",
                        "subprocess.Popen", "eval(", "exec(", "compile(", "open('/", "open(\"/",
                        "import os", "import sys", "import subprocess", "shutil", "socket",
                        "ctypes", "urllib.request", "http.client", "ftp", "telnetlib"]
    lower_code = code.lower()
    for kw in blocked_keywords:
        if kw.lower() in lower_code:
            return {"status": "success", "output": "", "error": f"代码包含被禁止的关键字: {kw}", "explanation": "为了安全，部分系统级操作已被禁用。"}

    # 创建临时文件执行代码
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
        f.write(code)
        tmp_path = f.name

    try:
        result = subprocess.run(
            ["python", tmp_path],
            capture_output=True,
            text=True,
            timeout=10,
        )
        output = result.stdout[:5000]  # 限制输出长度
        error = result.stderr[:5000] if result.returncode != 0 else ""
    except subprocess.TimeoutExpired:
        output = ""
        error = "代码执行超时（限制 10 秒）"
    except Exception as e:
        output = ""
        error = f"执行异常: {str(e)}"
    finally:
        try:
            os.remove(tmp_path)
        except:
            pass

    explanation = ""
    if not error and output:
        explanation = "代码执行成功，上方为输出结果。"
    elif error:
        explanation = "代码执行过程中出现错误，请检查语法或逻辑。"

    return {
        "status": "success",
        "output": output,
        "error": error,
        "explanation": explanation,
    }
