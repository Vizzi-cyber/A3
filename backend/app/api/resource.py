"""
资源生成API
对接 LangGraph 工作流，调用 resource_generator 智能体
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
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
from ..services import content_library
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


# 模拟任务存储（限制最大条目数，防止内存无限增长）
_tasks_db: Dict[str, Dict[str, Any]] = {}
_MAX_TASKS = 500


def _cleanup_old_tasks():
    """当任务数超过上限时，删除最早完成的或最旧的 pending 任务"""
    if len(_tasks_db) <= _MAX_TASKS:
        return
    # 优先删除已完成的旧任务，再删除最旧的任务
    sorted_tasks = sorted(
        _tasks_db.items(),
        key=lambda item: (item[1].get("status") != "completed", item[1].get("created_at", 0))
    )
    to_remove = len(sorted_tasks) - _MAX_TASKS
    for key, _ in sorted_tasks[:to_remove]:
        del _tasks_db[key]


@router.post("/generate", response_model=ResourceGenerationResponse)
async def generate_resource(
    request: ResourceGenerationRequest,
    background_tasks: BackgroundTasks,
    _current: str = Depends(require_auth),
):
    """生成多模态学习资源 —— 后台任务直接调用 ResourceGeneratorAgent"""
    now = datetime.now().timestamp()
    task_id = f"task_{now}"
    _cleanup_old_tasks()
    _tasks_db[task_id] = {
        "task_id": task_id,
        "status": "pending",
        "progress": 0.0,
        "resources": {},
        "message": "Task queued",
        "created_at": now,
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
async def get_task_status(task_id: str, _current: str = Depends(require_auth)):
    if task_id not in _tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    return _tasks_db[task_id]


@router.post("/document/generate", response_model=DocumentGenerateResponse)
async def generate_document(request: DocumentGenerateRequest, _current: str = Depends(require_auth)):
    """生成讲解文档 —— 优先使用内容库，否则调用 ResourceGeneratorAgent"""
    # 优先匹配内容库
    lib = content_library.get_content(request.kp_id) or content_library.get_content_by_topic(request.topic)
    if lib and lib.get("document"):
        return {
            "status": "success",
            "document": lib["document"],
            "metadata": {
                "topic": request.topic,
                "source": "content_library",
                "generated_at": datetime.now(timezone.utc).isoformat(),
            },
        }

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
            "generated_at": datetime.now(timezone.utc).isoformat(),
        },
    }


@router.post("/questions/generate", response_model=QuestionsGenerateResponse)
async def generate_questions(request: QuestionsGenerateRequest, _current: str = Depends(require_auth)):
    """生成练习题 —— 优先使用内容库，否则调用 ResourceGeneratorAgent"""
    # 优先匹配内容库
    lib = content_library.get_content(request.kp_id) or content_library.get_content_by_topic(request.topic)
    if lib and lib.get("questions"):
        questions = lib["questions"]
        return {
            "status": "success",
            "topic": request.topic,
            "count": len(questions),
            "questions": questions,
        }

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
    """生成思维导图 —— 优先使用内容库，否则调用 ResourceGeneratorAgent"""
    # 优先匹配内容库
    lib = content_library.get_content(request.kp_id) or content_library.get_content_by_topic(request.topic)
    if lib and lib.get("mindmap"):
        return {"status": "success", "mindmap": lib["mindmap"], "format": "json_tree"}

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
    """生成代码示例 —— 优先使用内容库，否则调用 ResourceGeneratorAgent"""
    # 优先匹配内容库
    lib = content_library.get_content(request.kp_id) or content_library.get_content_by_topic(request.topic)
    if lib and lib.get("code"):
        lang = request.language or "C"
        ext = "c" if lang.lower() in ("c", "c语言") else lang.lower()
        return {
            "status": "success",
            "code": lib["code"],
            "language": lang,
            "filename": f"{request.topic.lower().replace(' ', '_')}.{ext}",
        }

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


# ---------- 代码安全分析 ----------

import ast

_DANGEROUS_MODULES = {
    "os", "sys", "subprocess", "shutil", "socket", "ctypes",
    "urllib", "http", "ftplib", "telnetlib", "pathlib",
    "pickle", "marshal", "base64", "platform", "multiprocessing",
}

_DANGEROUS_CALLS = {
    "eval", "exec", "compile", "open", "input", "raw_input",
    "__import__", "breakpoint", "exit", "quit",
}


def _analyze_python_security(source: str) -> tuple[bool, str]:
    """使用 AST 分析 Python 代码中的危险操作"""
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        return False, f"Python 语法错误: {e.msg} (第{e.lineno}行)"

    for node in ast.walk(tree):
        # 禁止危险导入
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                if root in _DANGEROUS_MODULES:
                    return False, f"禁止导入系统级模块: {alias.name}"
        # 禁止 from xx import yy
        if isinstance(node, ast.ImportFrom):
            root = node.module.split(".")[0] if node.module else ""
            if root in _DANGEROUS_MODULES:
                return False, f"禁止从系统级模块导入: {node.module}"
            for alias in node.names:
                if alias.name in _DANGEROUS_CALLS:
                    return False, f"禁止导入危险函数: {alias.name}"
        # 禁止危险函数调用
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in _DANGEROUS_CALLS:
                return False, f"禁止调用危险函数: {node.func.id}()"
            # 禁止 os.system / os.popen / subprocess.run 等
            if isinstance(node.func, ast.Attribute):
                # 简单的属性链检测：只检测一层如 os.system
                if isinstance(node.func.value, ast.Name):
                    if node.func.value.id in _DANGEROUS_MODULES and node.func.attr in {
                        "system", "popen", "call", "run", "Popen", "fork", "kill",
                        "remove", "rmdir", "unlink", "rename", "replace",
                    }:
                        return False, f"禁止调用危险方法: {node.func.value.id}.{node.func.attr}()"
        # 禁止访问 __subclasses__ / __bases__ / __globals__ 等双下划线魔法属性（常用于沙箱逃逸）
        if isinstance(node, ast.Attribute):
            if node.attr.startswith("__") and node.attr.endswith("__") and node.attr not in {
                "__init__", "__str__", "__repr__", "__len__", "__eq__", "__name__", "__doc__",
                "__file__", "__class__", "__module__", "__dict__", "__slots__",
            }:
                return False, f"禁止访问魔法属性: {node.attr}"

    return True, ""


def _run_c_code(code: str) -> dict:
    """同步函数：编译并运行 C 代码（供 asyncio.to_thread 调用）"""
    import subprocess
    import tempfile
    import os
    import shutil

    gcc_path = shutil.which("gcc")
    msys2_gcc = r"C:\msys64\mingw64\bin\gcc.exe"
    if not gcc_path and os.path.exists(msys2_gcc):
        gcc_path = msys2_gcc
    if not gcc_path:
        return {
            "status": "success",
            "output": "",
            "error": "当前服务器未安装 gcc，无法编译运行 C 代码。建议将代码复制到本地 IDE（如 Dev-C++、VS Code）中运行。",
            "explanation": "C 代码需要 gcc 编译器，当前环境未提供。",
        }

    env = os.environ.copy()
    msys2_bin = r"C:\msys64\mingw64\bin"
    if msys2_bin not in env.get("PATH", ""):
        env["PATH"] = msys2_bin + os.pathsep + env.get("PATH", "")

    with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False, encoding="utf-8") as f:
        f.write(code)
        src_path = f.name
    exe_path = src_path.replace(".c", ".exe" if os.name == "nt" else "")
    output = ""
    error = ""
    try:
        compile_res = subprocess.run(
            [gcc_path, src_path, "-o", exe_path, "-finput-charset=UTF-8"],
            capture_output=True,
            text=True,
            timeout=10,
            env=env,
        )
        compile_stderr = getattr(compile_res, 'stderr', None) or ""
        if compile_res.returncode != 0:
            return {
                "status": "success",
                "output": "",
                "error": compile_stderr[:2000] or "编译失败",
                "explanation": "C 代码编译出错，请检查语法。",
            }
        run_res = subprocess.run(
            [exe_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=10,
            env=env,
        )
        run_stdout_bytes = run_res.stdout or b""
        run_stderr_bytes = run_res.stderr or b""

        def _decode(b: bytes) -> str:
            for enc in ("utf-8", "gbk", "gb2312"):
                try:
                    return b.decode(enc)
                except UnicodeDecodeError:
                    continue
            return b.decode("utf-8", errors="replace")

        run_stdout = _decode(run_stdout_bytes)
        run_stderr = _decode(run_stderr_bytes)
        output = run_stdout[:5000]
        if run_res.returncode != 0:
            error = run_stderr[:5000] or f"程序异常退出，返回码: {run_res.returncode}"
    except subprocess.TimeoutExpired:
        error = "代码执行超时（限制 10 秒）"
    except Exception as e:
        error = f"执行异常: {str(e)}"
    finally:
        for p in (src_path, exe_path):
            try:
                if p and os.path.exists(p):
                    os.remove(p)
            except Exception:
                pass
    if error:
        explanation = "代码执行过程中出现错误，请检查语法或逻辑。"
    elif output:
        explanation = "代码执行成功，上方为输出结果。"
    else:
        explanation = "代码执行完成，无输出。"
    return {"status": "success", "output": output, "error": error, "explanation": explanation}


def _run_python_code(code: str) -> dict:
    """同步函数：执行 Python 代码（供 asyncio.to_thread 调用）"""
    import subprocess
    import tempfile
    import os

    safe, reason = _analyze_python_security(code)
    if not safe:
        return {"status": "success", "output": "", "error": f"代码安全检查未通过: {reason}", "explanation": "为了安全，部分系统级操作已被禁用。"}

    blocked_keywords = ["__import__", "os.system", "os.popen", "subprocess.call", "subprocess.run",
                        "subprocess.Popen", "eval(", "exec(", "compile("]
    # 规范化空白字符，防止通过插入空格绕过检测（如 os . system）
    normalized_code = "".join(code.lower().split())
    for kw in blocked_keywords:
        if "".join(kw.lower().split()) in normalized_code:
            return {"status": "success", "output": "", "error": f"代码包含被禁止的关键字: {kw}", "explanation": "为了安全，部分系统级操作已被禁用。"}

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
        f.write(code)
        tmp_path = f.name

    output = ""
    error = ""
    try:
        result = subprocess.run(
            ["python", tmp_path],
            capture_output=True,
            text=True,
            timeout=10,
        )
        output = result.stdout[:5000]
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
        except Exception:
            pass

    explanation = ""
    if not error and output:
        explanation = "代码执行成功，上方为输出结果。"
    elif error:
        explanation = "代码执行过程中出现错误，请检查语法或逻辑。"

    return {"status": "success", "output": output, "error": error, "explanation": explanation}


@router.post("/code/execute", response_model=CodeExecuteResponse)
async def execute_code(request: CodeExecuteRequest, _current: str = Depends(require_auth)):
    """在服务器子进程中执行代码（支持 Python 和 C）"""
    code = request.code
    language = (request.language or "Python").lower()
    if not code.strip():
        return {"status": "success", "output": "", "error": "代码为空", "explanation": ""}

    if language in ("c", "c语言"):
        return await asyncio.to_thread(_run_c_code, code)
    else:
        return await asyncio.to_thread(_run_python_code, code)
