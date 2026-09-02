"""
知识库 API - 文件夹和笔记 CRUD、搜索、WikiLink、自动整理
"""
import re
import time
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError

from ..models.database import get_db
from ..models.kb_note import KBFolderModel, KBNoteModel
from ..models.knowledge import KnowledgePointModel
from ..services.rag_search import RAGSearchEngine
from .auth import require_auth

router = APIRouter()

# WikiLink 正则：匹配 [[Target]]、[[Target#section]]、[[Target|alias]]
WIKILINK_REGEX = re.compile(r'\[\[([^\[\]|#]+?)(?:#[^\[\]|]*)?(?:\|[^\[\]]*?)?\]\]')


# ---------- Schemas ----------

class FolderCreate(BaseModel):
    name: str
    parent_id: Optional[str] = None


class FolderRename(BaseModel):
    name: str


class NoteCreate(BaseModel):
    title: str
    content: str = ""
    folder_id: Optional[str] = None


class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    folder_id: Optional[str] = None


# ---------- Folders ----------

@router.post("/folders")
async def create_folder(request: FolderCreate, db: Session = Depends(get_db), _current: str = Depends(require_auth)):
    folder_id = f"kb_folder_{_current}_{int(time.time() * 1000)}"
    folder = KBFolderModel(
        folder_id=folder_id,
        student_id=_current,
        name=request.name,
        parent_id=request.parent_id,
    )
    db.add(folder)
    db.commit()
    db.refresh(folder)
    return {"status": "success", "data": {
        "folder_id": folder.folder_id,
        "name": folder.name,
        "parent_id": folder.parent_id,
        "created_at": folder.created_at.isoformat() if folder.created_at else None,
    }}


@router.get("/folders")
async def list_folders(db: Session = Depends(get_db), _current: str = Depends(require_auth)):
    folders = db.query(KBFolderModel).filter(KBFolderModel.student_id == _current).all()
    return {"status": "success", "data": [
        {
            "folder_id": f.folder_id,
            "name": f.name,
            "parent_id": f.parent_id,
            "created_at": f.created_at.isoformat() if f.created_at else None,
        }
        for f in folders
    ]}


@router.put("/folders/{folder_id}")
async def rename_folder(folder_id: str, request: FolderRename, db: Session = Depends(get_db), _current: str = Depends(require_auth)):
    folder = db.query(KBFolderModel).filter(
        KBFolderModel.folder_id == folder_id,
        KBFolderModel.student_id == _current,
    ).first()
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    folder.name = request.name
    db.commit()
    return {"status": "success"}


@router.delete("/folders/{folder_id}")
async def delete_folder(folder_id: str, db: Session = Depends(get_db), _current: str = Depends(require_auth)):
    folder = db.query(KBFolderModel).filter(
        KBFolderModel.folder_id == folder_id,
        KBFolderModel.student_id == _current,
    ).first()
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    # 将子文件夹移到根目录
    db.query(KBFolderModel).filter(KBFolderModel.parent_id == folder_id).update({"parent_id": folder.parent_id})
    # 将笔记移到根目录
    db.query(KBNoteModel).filter(KBNoteModel.folder_id == folder_id).update({"folder_id": None})
    db.delete(folder)
    db.commit()
    return {"status": "success"}


# ---------- Notes ----------

@router.post("/notes")
async def create_note(request: NoteCreate, db: Session = Depends(get_db), _current: str = Depends(require_auth)):
    note_id = f"kb_note_{_current}_{int(time.time() * 1000)}"
    note = KBNoteModel(
        note_id=note_id,
        student_id=_current,
        title=request.title,
        content=request.content,
        folder_id=request.folder_id,
    )
    db.add(note)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="该学生已有同名笔记")
    db.refresh(note)
    return {"status": "success", "data": {
        "note_id": note.note_id,
        "title": note.title,
        "content": note.content,
        "folder_id": note.folder_id,
        "created_at": note.created_at.isoformat() if note.created_at else None,
        "updated_at": note.updated_at.isoformat() if note.updated_at else None,
    }}


@router.get("/notes")
async def list_notes(folder_id: Optional[str] = Query(None), db: Session = Depends(get_db), _current: str = Depends(require_auth)):
    query = db.query(KBNoteModel).filter(KBNoteModel.student_id == _current)
    if folder_id:
        query = query.filter(KBNoteModel.folder_id == folder_id)
    notes = query.order_by(KBNoteModel.updated_at.desc()).all()
    return {"status": "success", "data": [
        {
            "note_id": n.note_id,
            "title": n.title,
            "content_preview": (n.content or "")[:200],
            "folder_id": n.folder_id,
            "updated_at": n.updated_at.isoformat() if n.updated_at else None,
        }
        for n in notes
    ]}


@router.get("/notes/search")
async def search_notes(q: str = Query(...), db: Session = Depends(get_db), _current: str = Depends(require_auth)):
    pattern = f"%{q}%"
    notes = db.query(KBNoteModel).filter(
        KBNoteModel.student_id == _current,
        or_(KBNoteModel.title.like(pattern), KBNoteModel.content.like(pattern)),
    ).order_by(KBNoteModel.updated_at.desc()).limit(50).all()
    return {"status": "success", "data": [
        {
            "note_id": n.note_id,
            "title": n.title,
            "content_preview": (n.content or "")[:200],
            "folder_id": n.folder_id,
            "updated_at": n.updated_at.isoformat() if n.updated_at else None,
        }
        for n in notes
    ]}


@router.get("/rag/search")
async def rag_search_notes(q: str = Query(...), top_k: int = Query(8), db: Session = Depends(get_db), _current: str = Depends(require_auth)):
    """RAG 语义检索：BM25 概率检索模型 + jieba 中文分词，按相关度排序并返回命中片段。"""
    notes = (
        db.query(KBNoteModel)
        .filter(KBNoteModel.student_id == _current)
        .order_by(KBNoteModel.updated_at.desc())
        .all()
    )
    engine = RAGSearchEngine()
    engine.build([
        {
            "note_id": n.note_id,
            "title": n.title,
            "content": n.content or "",
            "folder_id": n.folder_id,
            "updated_at": n.updated_at.isoformat() if n.updated_at else None,
        }
        for n in notes
    ])
    results = engine.search(q, top_k=top_k)
    return {"status": "success", "data": {"query": q, "results": results, "total_notes": len(notes)}}


@router.get("/notes/{note_id}")
async def get_note(note_id: str, db: Session = Depends(get_db), _current: str = Depends(require_auth)):
    note = db.query(KBNoteModel).filter(
        KBNoteModel.note_id == note_id,
        KBNoteModel.student_id == _current,
    ).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return {"status": "success", "data": {
        "note_id": note.note_id,
        "title": note.title,
        "content": note.content,
        "folder_id": note.folder_id,
        "created_at": note.created_at.isoformat() if note.created_at else None,
        "updated_at": note.updated_at.isoformat() if note.updated_at else None,
    }}


@router.put("/notes/{note_id}")
async def update_note(note_id: str, request: NoteUpdate, db: Session = Depends(get_db), _current: str = Depends(require_auth)):
    note = db.query(KBNoteModel).filter(
        KBNoteModel.note_id == note_id,
        KBNoteModel.student_id == _current,
    ).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    if request.title is not None:
        note.title = request.title
    if request.content is not None:
        note.content = request.content
    if request.folder_id is not None:
        note.folder_id = request.folder_id
    db.commit()
    db.refresh(note)
    return {"status": "success", "data": {
        "note_id": note.note_id,
        "title": note.title,
        "content": note.content,
        "folder_id": note.folder_id,
        "updated_at": note.updated_at.isoformat() if note.updated_at else None,
    }}


@router.delete("/notes/{note_id}")
async def delete_note(note_id: str, db: Session = Depends(get_db), _current: str = Depends(require_auth)):
    note = db.query(KBNoteModel).filter(
        KBNoteModel.note_id == note_id,
        KBNoteModel.student_id == _current,
    ).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    db.delete(note)
    db.commit()
    return {"status": "success"}


# ---------- Wikilink ----------

def _extract_wikilinks(content: str) -> List[str]:
    targets = WIKILINK_REGEX.findall(content)
    return list(set(t.strip() for t in targets if t.strip()))


@router.get("/wikilink/backlinks/{note_id}")
async def get_backlinks(note_id: str, db: Session = Depends(get_db), _current: str = Depends(require_auth)):
    current_note = db.query(KBNoteModel).filter(
        KBNoteModel.note_id == note_id,
        KBNoteModel.student_id == _current,
    ).first()
    if not current_note:
        raise HTTPException(status_code=404, detail="Note not found")

    all_notes = db.query(KBNoteModel).filter(KBNoteModel.student_id == _current).all()
    backlinks = []
    for n in all_notes:
        if n.note_id == note_id:
            continue
        targets = _extract_wikilinks(n.content or "")
        if current_note.title in targets:
            # 提取包含链接的行作为摘录
            excerpt = ""
            for line in (n.content or "").split("\n"):
                if f"[[{current_note.title}" in line:
                    excerpt = line.strip()[:120]
                    break
            backlinks.append({
                "note_id": n.note_id,
                "title": n.title,
                "excerpt": excerpt,
            })
    return {"status": "success", "data": backlinks}


@router.get("/wikilink/graph")
async def get_graph(db: Session = Depends(get_db), _current: str = Depends(require_auth)):
    notes = db.query(KBNoteModel).filter(KBNoteModel.student_id == _current).all()
    nodes = [{"id": n.note_id, "title": n.title} for n in notes]
    note_title_map = {n.title: n.note_id for n in notes}
    edges = []
    for n in notes:
        targets = _extract_wikilinks(n.content or "")
        for t in targets:
            target_id = note_title_map.get(t)
            if target_id and target_id != n.note_id:
                edges.append({"source": n.note_id, "target": target_id})
    return {"status": "success", "data": {"nodes": nodes, "edges": edges}}


# ---------- 自动整理 ----------

class AutoOrganizeRequest(BaseModel):
    """自动整理请求"""
    kp_id: str
    title: str
    content: str
    tags: List[str] = []
    subject: str = "C语言"
    action: str = "learn"  # learn / quiz / review


def _find_or_create_folder(db: Session, student_id: str, name: str, parent_id: Optional[str] = None) -> str:
    """查找或创建文件夹，返回 folder_id"""
    folder = db.query(KBFolderModel).filter(
        KBFolderModel.student_id == student_id,
        KBFolderModel.name == name,
        KBFolderModel.parent_id == parent_id,
    ).first()
    if folder:
        return folder.folder_id

    folder_id = f"kb_folder_{student_id}_{int(time.time() * 1000)}"
    folder = KBFolderModel(
        folder_id=folder_id,
        student_id=student_id,
        name=name,
        parent_id=parent_id,
    )
    db.add(folder)
    db.flush()
    return folder_id


def _find_or_create_note(db: Session, student_id: str, title: str, folder_id: Optional[str] = None) -> KBNoteModel:
    """查找或创建笔记，返回笔记对象（并发安全）"""
    from sqlalchemy.exc import IntegrityError

    note = db.query(KBNoteModel).filter(
        KBNoteModel.student_id == student_id,
        KBNoteModel.title == title,
    ).first()
    if note:
        return note

    note_id = f"kb_note_{student_id}_{int(time.time() * 1000)}"
    note = KBNoteModel(
        note_id=note_id,
        student_id=student_id,
        title=title,
        content="",
        folder_id=folder_id,
    )
    db.add(note)
    try:
        db.flush()
    except IntegrityError:
        # 并发冲突：另一个请求已创建同名笔记，回退并返回已有记录
        db.rollback()
        note = db.query(KBNoteModel).filter(
            KBNoteModel.student_id == student_id,
            KBNoteModel.title == title,
        ).first()
        if note:
            return note
        # 极端情况：重试一次
        note_id = f"kb_note_{student_id}_{int(time.time() * 1000)}_retry"
        note = KBNoteModel(
            note_id=note_id,
            student_id=student_id,
            title=title,
            content="",
            folder_id=folder_id,
        )
        db.add(note)
        db.flush()
    return note


def _append_to_note(note: KBNoteModel, section_title: str, content: str, action: str):
    """向笔记追加内容（自动去重）"""
    existing = note.content or ""

    # 去重检查：如果 content 已存在于笔记中，跳过追加
    # 提取内容中的关键标识行作为去重依据（取前 3 行非空内容）
    content_lines = [l for l in content.strip().split("\n") if l.strip()]
    dedup_key = "\n".join(content_lines[:3]).strip()
    if dedup_key and dedup_key in existing:
        return

    # 检查是否已有该章节
    if f"## {section_title}" in existing:
        # 在章节末尾追加
        parts = existing.split(f"## {section_title}")
        if len(parts) == 2:
            # 找到下一个 ## 或文件末尾
            next_section_idx = parts[1].find("\n## ")
            if next_section_idx == -1:
                # 没有下一个章节，追加到末尾
                parts[1] = parts[1] + f"\n\n### 学习记录\n{content}\n"
            else:
                # 在下一个章节前插入
                parts[1] = parts[1][:next_section_idx] + f"\n\n### 学习记录\n{content}\n" + parts[1][next_section_idx:]
            note.content = parts[0] + f"## {section_title}" + parts[1]
    else:
        # 新增章节
        if existing:
            note.content = existing + f"\n\n## {section_title}\n\n{content}\n"
        else:
            note.content = f"## {section_title}\n\n{content}\n"


@router.post("/auto-organize")
async def auto_organize(request: AutoOrganizeRequest, db: Session = Depends(get_db), _current: str = Depends(require_auth)):
    """自动整理学习内容到知识库"""
    # 1. 获取知识点信息
    kp = db.query(KnowledgePointModel).filter(KnowledgePointModel.kp_id == request.kp_id).first()
    subject = kp.subject if kp else request.subject
    tags = kp.tags if kp and kp.tags else request.tags

    # 2. 创建或获取学科文件夹
    subject_folder_id = _find_or_create_folder(db, _current, subject)

    # 3. 创建或获取标签子文件夹（如果有标签）
    folder_id = subject_folder_id
    if tags:
        tag_name = tags[0]  # 使用第一个标签作为子文件夹
        tag_folder_id = _find_or_create_folder(db, _current, tag_name, subject_folder_id)
        folder_id = tag_folder_id

    # 4. 查找或创建笔记
    note = _find_or_create_note(db, _current, request.title, folder_id)

    # 5. 根据操作类型追加内容（自动检测关联笔记添加 WikiLink）
    from datetime import datetime, timezone
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")

    # 自动检测关联笔记，添加 WikiLink
    related_links = []
    if request.content:
        all_notes = db.query(KBNoteModel).filter(
            KBNoteModel.student_id == _current,
            KBNoteModel.note_id != note.note_id,
        ).all()
        for other in all_notes:
            if other.title and other.title in request.content:
                related_links.append(f"[[{other.title}]]")

    if request.action == "learn":
        section_title = "学习笔记"
        content = f"**学习时间**: {timestamp}\n\n{request.content}"
    elif request.action == "quiz":
        section_title = "测验记录"
        content = f"**测验时间**: {timestamp}\n\n{request.content}"
    elif request.action == "review":
        section_title = "复习记录"
        content = f"**复习时间**: {timestamp}\n\n{request.content}"
    else:
        section_title = "学习记录"
        content = f"**时间**: {timestamp}\n\n{request.content}"

    if related_links:
        content += "\n\n**关联笔记**：" + "、".join(related_links[:5])

    _append_to_note(note, section_title, content, request.action)

    # 6. 更新笔记的 folder_id（如果还没有）
    if not note.folder_id:
        note.folder_id = folder_id

    db.commit()
    db.refresh(note)

    return {
        "status": "success",
        "data": {
            "note_id": note.note_id,
            "title": note.title,
            "folder_id": note.folder_id,
        }
    }


@router.post("/batch-organize")
async def batch_organize(items: List[AutoOrganizeRequest], db: Session = Depends(get_db), _current: str = Depends(require_auth)):
    """批量整理学习内容"""
    results = []
    for item in items:
        result = await auto_organize(item, db, _current)
        results.append(result["data"])
    return {"status": "success", "data": results}


# ---------- 笔记 Agent 分析并存入知识库 ----------

class AnalyzeAndSaveRequest(BaseModel):
    """笔记分析并存入知识库请求"""
    content: str
    kp_id: Optional[str] = None
    title: Optional[str] = None


@router.post("/analyze-and-save")
async def analyze_and_save(request: AnalyzeAndSaveRequest, db: Session = Depends(get_db), _current: str = Depends(require_auth)):
    """将笔记内容经 LLM 分析后自动存入知识库"""
    from datetime import datetime, timezone
    from ..services.llm_factory import LLMFactory

    content = request.content.strip()
    if not content:
        raise HTTPException(status_code=400, detail="笔记内容不能为空")

    # 1. 用 LLM 分析笔记，提取关键知识点
    analyzed = content
    try:
        llm = LLMFactory.get_llm()
        prompt = (
            "你是一个学习助手。请分析以下学习笔记，提取关键知识点并整理成结构化的 Markdown 格式。\n"
            "要求：\n"
            "1. 保留原始内容的核心信息\n"
            "2. 用 Markdown 标题和列表组织\n"
            "3. 如果有代码示例，用代码块包裹\n"
            "4. 如果有错误或困惑，标注出来\n"
            "5. 输出简洁，不要添加多余的解释\n\n"
            f"笔记内容：\n{content}"
        )
        resp = await llm.chat.completions.create(
            model=llm.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1024,
        )
        analyzed = resp.choices[0].message.content.strip()
    except Exception:
        # LLM 不可用时直接使用原始内容
        analyzed = content

    # 2. 确定标题
    title = request.title or content[:30].replace("\n", " ")

    # 3. 获取知识点信息（如果有 kp_id）
    kp = None
    subject = "学习笔记"
    tags: List[str] = []
    if request.kp_id:
        kp = db.query(KnowledgePointModel).filter(KnowledgePointModel.kp_id == request.kp_id).first()
        if kp:
            subject = kp.subject or subject
            tags = kp.tags or tags

    # 4. 创建文件夹层级
    subject_folder_id = _find_or_create_folder(db, _current, subject)
    folder_id = subject_folder_id
    if tags:
        tag_folder_id = _find_or_create_folder(db, _current, tags[0], subject_folder_id)
        folder_id = tag_folder_id

    # 5. 创建或查找笔记并追加内容
    note = _find_or_create_note(db, _current, title, folder_id)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
    section_content = f"**记录时间**: {timestamp}\n\n{analyzed}"
    _append_to_note(note, "学习笔记", section_content, "learn")

    if not note.folder_id:
        note.folder_id = folder_id

    db.commit()
    db.refresh(note)

    return {
        "status": "success",
        "data": {
            "note_id": note.note_id,
            "title": note.title,
            "folder_id": note.folder_id,
            "analyzed": analyzed != content,
        }
    }
