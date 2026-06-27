"""
STM32 课程内容 API
提供课程文档、接线图、代码工程等资源的访问
"""
import json
import logging
from pathlib import Path
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse

from ..models.database import get_db
from .auth import require_auth

logger = logging.getLogger(__name__)

router = APIRouter()

# STM32 资源根目录
STM32_DIR = Path(__file__).parent.parent.parent / "stm32"
COURSES_DIR = STM32_DIR / "courses"
PROJECTS_DIR = STM32_DIR / "STM32Project-有注释版"
WIRING_DIR = PROJECTS_DIR / "1-1 接线图"


@router.get("/courses")
async def list_courses(_current: str = Depends(require_auth)):
    """获取所有课程文档列表"""
    if not COURSES_DIR.exists():
        return {"status": "success", "data": {"courses": []}}

    courses = []
    for md_file in sorted(COURSES_DIR.glob("*.md")):
        if md_file.name in ("README.md", "INDEX.md"):
            continue
        name = md_file.stem
        try:
            with open(md_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
            title = name
            for line in lines:
                line = line.strip()
                if line.startswith("# "):
                    title = line[2:].strip()
                    break
        except Exception as e:
            logger.warning(f"课程标题读取失败: {e}")
            title = name

        courses.append({
            "id": name,
            "filename": md_file.name,
            "title": title,
        })

    return {"status": "success", "data": {"courses": courses}}


@router.get("/courses/{course_id}")
async def get_course_content(course_id: str, _current: str = Depends(require_auth)):
    """获取单个课程文档的 Markdown 内容"""
    if "/" in course_id or "\\" in course_id or ".." in course_id:
        raise HTTPException(400, "非法课程 ID")

    md_file = (COURSES_DIR / f"{course_id}.md").resolve()
    if not md_file.exists():
        matches = [m.resolve() for m in COURSES_DIR.glob(f"*{course_id}*.md")]
        if matches and str(matches[0]).startswith(str(COURSES_DIR.resolve())):
            md_file = matches[0]
        else:
            raise HTTPException(404, f"课程文档不存在: {course_id}")

    if not str(md_file).startswith(str(COURSES_DIR.resolve())):
        raise HTTPException(403, "禁止访问")

    try:
        with open(md_file, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        raise HTTPException(500, f"读取文件失败: {e}")

    title = md_file.stem
    for line in content.split("\n"):
        line = line.strip()
        if line.startswith("# "):
            title = line[2:].strip()
            break

    return {
        "status": "success",
        "data": {
            "id": course_id,
            "filename": md_file.name,
            "title": title,
            "content": content,
        },
    }


@router.get("/wiring/{image_path:path}")
async def get_wiring_diagram(image_path: str, _current: str = Depends(require_auth)):
    """获取接线图图片"""
    if not WIRING_DIR.exists():
        raise HTTPException(404, "接线图目录不存在")

    full_path = (WIRING_DIR / image_path).resolve()
    if not str(full_path).startswith(str(WIRING_DIR.resolve())):
        raise HTTPException(403, "禁止访问")

    if not full_path.exists():
        raise HTTPException(404, f"接线图不存在: {image_path}")

    return FileResponse(
        str(full_path),
        media_type="image/jpeg",
        headers={"Cache-Control": "public, max-age=86400"},
    )


@router.get("/wiring-diagrams")
async def list_wiring_diagrams(_current: str = Depends(require_auth)):
    """列出所有接线图"""
    if not WIRING_DIR.exists():
        return {"status": "success", "data": {"diagrams": []}}

    diagrams = []
    for img_file in sorted(WIRING_DIR.glob("*.jpg")):
        diagrams.append({
            "filename": img_file.name,
            "title": img_file.stem,
            "url": f"/api/v1/stm32/wiring/{img_file.name}",
        })

    return {"status": "success", "data": {"diagrams": diagrams}}


@router.get("/projects/{dirname}")
async def get_project_files(dirname: str, _current: str = Depends(require_auth)):
    """获取单个代码工程的文件列表"""
    if "/" in dirname or "\\" in dirname or ".." in dirname:
        raise HTTPException(400, "非法目录名")

    project_dir = (PROJECTS_DIR / dirname).resolve()
    if not project_dir.exists() or not project_dir.is_dir():
        raise HTTPException(404, f"代码工程不存在: {dirname}")

    if not str(project_dir).startswith(str(PROJECTS_DIR.resolve())):
        raise HTTPException(403, "禁止访问")

    files = []
    for f in sorted(project_dir.rglob("*")):
        if f.is_file():
            rel = str(f.relative_to(project_dir)).replace("\\", "/")
            files.append({
                "path": rel,
                "size": f.stat().st_size,
            })

    return {
        "status": "success",
        "data": {
            "dirname": dirname,
            "files": files,
        },
    }


@router.get("/projects")
async def list_projects(_current: str = Depends(require_auth)):
    """列出所有代码工程目录"""
    if not PROJECTS_DIR.exists():
        return {"status": "success", "data": {"projects": []}}

    projects = []
    for d in sorted(PROJECTS_DIR.iterdir()):
        if d.is_dir() and d.name not in ("1-1 接线图", "1-2 keilkill批处理"):
            file_count = sum(1 for _ in d.rglob("*") if _.is_file())
            projects.append({
                "dirname": d.name,
                "title": d.name,
                "file_count": file_count,
            })

    return {"status": "success", "data": {"projects": projects}}


@router.get("/knowledge-tree")
async def get_stm32_knowledge_tree(_current: str = Depends(require_auth)):
    """获取完整的 STM32 知识树数据"""
    kt_file = STM32_DIR / "knowledge_tree.json"
    fm_file = STM32_DIR / "frontend_mapping.json"

    if not kt_file.exists():
        raise HTTPException(404, "知识树数据文件不存在")

    try:
        with open(kt_file, "r", encoding="utf-8") as f:
            kt_data = json.load(f)
    except Exception as e:
        raise HTTPException(500, f"读取知识树数据失败: {e}")

    result = {
        "courses": kt_data.get("courses", []),
        "knowledge_points": kt_data.get("knowledge_points", []),
        "experiments": kt_data.get("experiments", []),
        "learning_paths": kt_data.get("learning_paths", []),
    }

    if fm_file.exists():
        try:
            with open(fm_file, "r", encoding="utf-8") as f:
                fm_data = json.load(f)
            result["icon_mapping"] = fm_data.get("icon_mapping", {})
            result["color_mapping"] = fm_data.get("color_mapping", {})
            result["frontend_tree"] = fm_data.get("knowledge_tree", {})
        except Exception as e:
            logger.warning(f"前端映射数据读取失败: {e}")

    return {"status": "success", "data": result}
