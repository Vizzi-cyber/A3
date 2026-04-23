from pydantic import BaseModel
from typing import Optional


class DocumentGenerateRequest(BaseModel):
    student_id: str
    topic: str
    difficulty: str = "medium"
    kp_id: Optional[str] = None


class DocumentGenerateResponse(BaseModel):
    status: str
    document: str
    metadata: dict


class QuestionsGenerateRequest(BaseModel):
    student_id: str
    topic: str
    count: int = 5
    kp_id: Optional[str] = None


class QuestionsGenerateResponse(BaseModel):
    status: str
    topic: str
    count: int
    questions: list


class MindmapGenerateRequest(BaseModel):
    student_id: str
    topic: str
    kp_id: Optional[str] = None


class MindmapGenerateResponse(BaseModel):
    status: str
    mindmap: dict
    format: str = "json_tree"


class CodeGenerateRequest(BaseModel):
    student_id: str
    topic: str
    language: str = "Python"
    kp_id: Optional[str] = None


class CodeGenerateResponse(BaseModel):
    status: str
    code: str
    language: str
    filename: str


class CodeExecuteRequest(BaseModel):
    code: str
    language: str = "Python"
    kp_id: Optional[str] = None


class CodeExecuteResponse(BaseModel):
    status: str
    output: str
    error: str
    explanation: str
