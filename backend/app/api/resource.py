"""
资源生成API
对接 LangGraph 工作流，调用 resource_generator 智能体
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import asyncio

from ..core.logger import setup_logger

logger = setup_logger()

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
from sqlalchemy.orm import Session
from ..models.database import get_db, SessionLocal
from ..models.knowledge import ResourceTaskModel

router = APIRouter()

_resource_agent = ResourceGeneratorAgent()


async def _generate_with_agent(
    task: str,
    topic: str,
    lib_key: str,
    kp_id: str,
    default_content: Any,
    constraints: Optional[Dict] = None,
    extract_content=None,
) -> tuple:
    """统一的资源生成逻辑：先查内容库，再调用 Agent。返回 (content, source)"""
    lib = content_library.get_content(kp_id) or content_library.get_content_by_topic(topic)
    if lib and lib.get(lib_key):
        return lib[lib_key], "content_library"

    try:
        agent_input: Dict[str, Any] = {"task": task, "topic": topic}
        if constraints:
            agent_input["constraints"] = constraints
        result = await asyncio.wait_for(
            _resource_agent.process(agent_input),
            timeout=15.0,
        )
        if result.get("status") == "success":
            raw = result.get("content", default_content)
            if extract_content:
                extracted = extract_content(raw)
                if extracted is not None:
                    return extracted, "agent"
            elif raw is not None:
                return raw, "agent"
    except asyncio.TimeoutError:
        logger.warning(f"{task} 超时: topic={topic}")
    except Exception as e:
        logger.warning(f"{task} 异常: {e}")

    return default_content, "fallback"


class ResourceGenerationRequest(BaseModel):
    """资源生成请求"""
    student_id: str
    topic: str = Field(..., max_length=500)
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


_MAX_TASKS = 500


def _cleanup_old_tasks():
    """当任务数超过上限时，删除最早完成的或最旧的 pending 任务"""
    db = SessionLocal()
    try:
        total = db.query(ResourceTaskModel).count()
        if total <= _MAX_TASKS:
            return
        to_remove = total - _MAX_TASKS
        # 优先删除已完成的旧任务
        old_completed = (
            db.query(ResourceTaskModel)
            .filter(ResourceTaskModel.status == "completed")
            .order_by(ResourceTaskModel.created_at)
            .limit(to_remove)
            .all()
        )
        for t in old_completed:
            db.delete(t)
        db.commit()

        # 如果还不够，再删除最旧的任务
        remaining = db.query(ResourceTaskModel).count()
        if remaining > _MAX_TASKS:
            to_remove2 = remaining - _MAX_TASKS
            oldest = (
                db.query(ResourceTaskModel)
                .order_by(ResourceTaskModel.created_at)
                .limit(to_remove2)
                .all()
            )
            for t in oldest:
                db.delete(t)
            db.commit()
    except Exception as e:
        db.rollback()
        logger.warning(f"Cleanup old tasks failed: {e}")
    finally:
        db.close()


@router.post("/generate", response_model=ResourceGenerationResponse)
async def generate_resource(
    request: ResourceGenerationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    _current: str = Depends(require_auth),
):
    """生成多模态学习资源 —— 后台任务直接调用 ResourceGeneratorAgent"""
    import uuid
    task_id = f"task_{uuid.uuid4().hex[:12]}"
    _cleanup_old_tasks()
    task = ResourceTaskModel(
        task_id=task_id,
        status="pending",
        progress=0.0,
        resources={},
        message="Task queued",
    )
    db.add(task)
    db.commit()
    background_tasks.add_task(
        _execute_generation,
        task_id,
        request,
    )
    return ResourceGenerationResponse(
        task_id=task_id, status="pending", message="Resource generation task started"
    )


async def _execute_generation(task_id: str, request: ResourceGenerationRequest):
    db = SessionLocal()
    try:
        task = db.query(ResourceTaskModel).filter(ResourceTaskModel.task_id == task_id).first()
        if not task:
            logger.warning(f"Task {task_id} not found in DB")
            return
        task.status = "running"
        task.message = "Initializing agents..."
        db.commit()

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

        task.status = "completed" if results else "failed"
        task.progress = 1.0
        task.resources = results
        task.message = "Generation completed" if results else "Generation timeout or failed"
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Task {task_id} failed: {e}")
        task = db.query(ResourceTaskModel).filter(ResourceTaskModel.task_id == task_id).first()
        if task:
            task.status = "failed"
            task.message = str(e)
            db.commit()
    finally:
        db.close()


@router.get("/task/{task_id}")
async def get_task_status(task_id: str, db: Session = Depends(get_db), _current: str = Depends(require_auth)):
    task = db.query(ResourceTaskModel).filter(ResourceTaskModel.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {
        "task_id": task.task_id,
        "status": task.status,
        "progress": task.progress,
        "resources": task.resources,
        "message": task.message,
    }


@router.post("/document/generate", response_model=DocumentGenerateResponse)
async def generate_document(request: DocumentGenerateRequest, _current: str = Depends(require_auth)):
    """生成讲解文档 —— 优先使用内容库，否则调用 ResourceGeneratorAgent"""
    doc_content, source = await _generate_with_agent(
        task="generate_document",
        topic=request.topic,
        lib_key="document",
        kp_id=request.kp_id,
        default_content=f"# {request.topic}\n\n这里是生成的文档内容（fallback）。",
        constraints={"difficulty": request.difficulty},
        extract_content=lambda raw: raw if isinstance(raw, str) else None,
    )
    return {
        "status": "success",
        "document": doc_content,
        "metadata": {
            "topic": request.topic,
            "source": source,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        },
    }


@router.post("/questions/generate", response_model=QuestionsGenerateResponse)
async def generate_questions(request: QuestionsGenerateRequest, _current: str = Depends(require_auth)):
    """生成练习题 —— 优先使用内容库，否则调用 ResourceGeneratorAgent"""
    default_questions = [
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

    questions, _ = await _generate_with_agent(
        task="generate_questions",
        topic=request.topic,
        lib_key="questions",
        kp_id=request.kp_id,
        default_content=default_questions,
        constraints={"count": request.count},
        extract_content=lambda raw: raw if isinstance(raw, list) and len(raw) > 0 else None,
    )
    return {
        "status": "success",
        "topic": request.topic,
        "count": len(questions) if isinstance(questions, list) else 0,
        "questions": questions,
    }


@router.post("/mindmap/generate", response_model=MindmapGenerateResponse)
async def generate_mindmap(request: MindmapGenerateRequest, _current: str = Depends(require_auth)):
    """生成思维导图 —— 优先使用内容库，否则调用 ResourceGeneratorAgent"""
    mindmap, _ = await _generate_with_agent(
        task="generate_mindmap",
        topic=request.topic,
        lib_key="mindmap",
        kp_id=request.kp_id,
        default_content={"root": request.topic, "children": []},
        extract_content=lambda raw: raw if isinstance(raw, dict) and raw.get("root") else None,
    )
    return {"status": "success", "mindmap": mindmap, "format": "json_tree"}


@router.post("/code/generate", response_model=CodeGenerateResponse)
async def generate_code(request: CodeGenerateRequest, _current: str = Depends(require_auth)):
    """生成代码示例 —— 优先使用内容库，否则调用 ResourceGeneratorAgent"""
    code, source = await _generate_with_agent(
        task="generate_code_examples",
        topic=request.topic,
        lib_key="code",
        kp_id=request.kp_id,
        default_content=f"# {request.topic} - {request.language}\n\nprint('Hello, World!')",
        constraints={"language": request.language},
        extract_content=lambda raw: raw if isinstance(raw, str) else None,
    )
    lang = request.language or "C"
    ext = "c" if lang.lower() in ("c", "c语言") else lang.lower()
    return {
        "status": "success",
        "code": code,
        "language": lang,
        "filename": f"{request.topic.lower().replace(' ', '_')}.{ext}",
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
    "getattr", "globals", "locals", "vars", "dir",
}


def _analyze_python_security(source: str) -> tuple[bool, str]:
    """使用 AST 分析 Python 代码中的危险操作"""
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        return False, f"Python 语法错误: {e.msg} (第{e.lineno}行)"

    _ALLOWED_MAGIC = {
        "__init__", "__str__", "__repr__", "__len__", "__eq__", "__name__", "__doc__",
        "__file__", "__class__", "__module__", "__dict__", "__slots__",
        "__main__", "__future__", "__all__", "__version__",
    }

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
                if isinstance(node.func.value, ast.Name):
                    if node.func.value.id in _DANGEROUS_MODULES and node.func.attr in {
                        "system", "popen", "call", "run", "Popen", "fork", "kill",
                        "remove", "rmdir", "unlink", "rename", "replace",
                    }:
                        return False, f"禁止调用危险方法: {node.func.value.id}.{node.func.attr}()"
            # 禁止 __import__ 调用（包括间接调用）
            if isinstance(node.func, ast.Attribute) and node.func.attr == "__import__":
                return False, "禁止调用 __import__"
        # 禁止访问 __subclasses__ / __bases__ / __globals__ 等双下划线魔法属性（常用于沙箱逃逸）
        if isinstance(node, ast.Attribute):
            if node.attr.startswith("__") and node.attr.endswith("__") and node.attr not in _ALLOWED_MAGIC:
                return False, f"禁止访问魔法属性: {node.attr}"
        # 禁止 global/nonlocal 声明（防止修改外部作用域）
        if isinstance(node, (ast.Global, ast.Nonlocal)):
            return False, f"禁止使用 {'global' if isinstance(node, ast.Global) else 'nonlocal'} 声明"

    return True, ""


def _create_win_job_object(max_memory_mb: int = 128):
    """Windows: 创建 Job Object 限制子进程内存（防止内存炸弹）"""
    import ctypes

    kernel32 = ctypes.windll.kernel32
    JOB_OBJECT_LIMIT_PROCESS_MEMORY = 0x00000100
    JOB_OBJECT_LIMIT_JOB_MEMORY = 0x00000200
    JobObjectExtendedLimitInformation = 9

    class JOBOBJECT_BASIC_LIMIT_INFORMATION(ctypes.Structure):
        _fields_ = [
            ("PerProcessUserTimeLimit", ctypes.c_int64),
            ("PerJobUserTimeLimit", ctypes.c_int64),
            ("LimitFlags", ctypes.c_uint32),
            ("MinimumWorkingSetSize", ctypes.c_size_t),
            ("MaximumWorkingSetSize", ctypes.c_size_t),
            ("ActiveProcessLimit", ctypes.c_uint32),
            ("Affinity", ctypes.c_size_t),
            ("PriorityClass", ctypes.c_uint32),
            ("SchedulingClass", ctypes.c_uint32),
        ]

    class IO_COUNTERS(ctypes.Structure):
        _fields_ = [
            ("ReadOperationCount", ctypes.c_uint64),
            ("WriteOperationCount", ctypes.c_uint64),
            ("OtherOperationCount", ctypes.c_uint64),
            ("ReadTransferCount", ctypes.c_uint64),
            ("WriteTransferCount", ctypes.c_uint64),
            ("OtherTransferCount", ctypes.c_uint64),
        ]

    class JOBOBJECT_EXTENDED_LIMIT_INFORMATION(ctypes.Structure):
        _fields_ = [
            ("BasicLimitInformation", JOBOBJECT_BASIC_LIMIT_INFORMATION),
            ("IoInfo", IO_COUNTERS),
            ("ProcessMemoryLimit", ctypes.c_size_t),
            ("JobMemoryLimit", ctypes.c_size_t),
            ("PeakProcessMemoryUsed", ctypes.c_size_t),
            ("PeakJobMemoryUsed", ctypes.c_size_t),
        ]

    job = kernel32.CreateJobObjectW(None, None)
    if not job:
        return None

    info = JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
    info.BasicLimitInformation.LimitFlags = JOB_OBJECT_LIMIT_PROCESS_MEMORY | JOB_OBJECT_LIMIT_JOB_MEMORY
    info.ProcessMemoryLimit = max_memory_mb * 1024 * 1024
    info.JobMemoryLimit = max_memory_mb * 1024 * 1024

    if not kernel32.SetInformationJobObject(job, JobObjectExtendedLimitInformation,
                                             ctypes.byref(info), ctypes.sizeof(info)):
        kernel32.CloseHandle(job)
        return None
    return job


def _assign_to_job(job_handle, pid: int):
    """将子进程 PID 绑定到 Job Object"""
    import ctypes
    kernel32 = ctypes.windll.kernel32
    proc_handle = kernel32.OpenProcess(0x1F0FFF, False, pid)  # PROCESS_ALL_ACCESS
    if proc_handle:
        kernel32.AssignProcessToJobObject(job_handle, proc_handle)
        kernel32.CloseHandle(proc_handle)


def _run_c_code(code: str) -> dict:
    """同步函数：编译并运行 C 代码（供 asyncio.to_thread 调用）"""
    import subprocess
    import tempfile
    import os
    import shutil

    # 安全检查：限制代码长度（防止超大文件）
    if len(code) > 50_000:
        return {"status": "success", "output": "", "error": "代码过长（超过 50KB），已拒绝执行。", "explanation": "安全限制。"}

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

        # 资源限制：Unix 用 preexec_fn，Windows 用 Job Object
        preexec = None
        job_handle = None
        creation_flags = 0
        if os.name != "nt":
            def _set_limits():
                import resource
                resource.setrlimit(resource.RLIMIT_CPU, (5, 5))
                resource.setrlimit(resource.RLIMIT_AS, (128 * 1024 * 1024, 128 * 1024 * 1024))
                resource.setrlimit(resource.RLIMIT_NPROC, (0, 0))
            preexec = _set_limits
        else:
            job_handle = _create_win_job_object(128)
            creation_flags = 0x00000200  # CREATE_BREAKAWAY_FROM_JOB

        run_returncode = 0
        if job_handle:
            proc = subprocess.Popen(
                [exe_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                env=env, creationflags=creation_flags,
            )
            _assign_to_job(job_handle, proc.pid)
            try:
                run_stdout_bytes, run_stderr_bytes = proc.communicate(timeout=10)
                run_returncode = proc.returncode
            except subprocess.TimeoutExpired:
                proc.kill()
                run_stdout_bytes, run_stderr_bytes = proc.communicate()
                raise
            finally:
                import ctypes
                ctypes.windll.kernel32.CloseHandle(job_handle)
        else:
            run_res = subprocess.run(
                [exe_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                timeout=10, env=env, preexec_fn=preexec,
            )
            run_stdout_bytes = run_res.stdout or b""
            run_stderr_bytes = run_res.stderr or b""
            run_returncode = run_res.returncode

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
        if run_returncode != 0:
            error = run_stderr[:5000] or f"程序异常退出，返回码: {run_returncode}"
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

    # 安全检查：限制代码长度
    if len(code) > 50_000:
        return {"status": "success", "output": "", "error": "代码过长（超过 50KB），已拒绝执行。", "explanation": "安全限制。"}

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
        # 资源限制：Unix 用 preexec_fn，Windows 用 Job Object
        preexec = None
        job_handle = None
        creation_flags = 0
        if os.name != "nt":
            def _set_limits():
                import resource
                resource.setrlimit(resource.RLIMIT_CPU, (5, 5))
                resource.setrlimit(resource.RLIMIT_AS, (128 * 1024 * 1024, 128 * 1024 * 1024))
                resource.setrlimit(resource.RLIMIT_NPROC, (0, 0))
            preexec = _set_limits
        else:
            job_handle = _create_win_job_object(128)
            creation_flags = 0x00000200  # CREATE_BREAKAWAY_FROM_JOB

        if job_handle:
            proc = subprocess.Popen(
                ["python", tmp_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, creationflags=creation_flags,
            )
            _assign_to_job(job_handle, proc.pid)
            try:
                stdout, stderr = proc.communicate(timeout=10)
                output = stdout[:5000]
                error = stderr[:5000] if proc.returncode != 0 else ""
            except subprocess.TimeoutExpired:
                proc.kill()
                raise
            finally:
                import ctypes
                ctypes.windll.kernel32.CloseHandle(job_handle)
        else:
            result = subprocess.run(
                ["python", tmp_path], capture_output=True, text=True,
                timeout=10, preexec_fn=preexec,
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
