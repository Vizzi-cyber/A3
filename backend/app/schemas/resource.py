from pydantic import BaseModel
from typing import Optional


class DocumentGenerateRequest(BaseModel):
    student_id: str
    topic: str
    difficulty: str = "medium"


class DocumentGenerateResponse(BaseModel):
    status: str
    document: str
    metadata: dict


class QuestionsGenerateRequest(BaseModel):
    student_id: str
    topic: str
    count: int = 5


class QuestionsGenerateResponse(BaseModel):
    status: str
    topic: str
    count: int
    questions: list


class MindmapGenerateRequest(BaseModel):
    student_id: str
    topic: str


class MindmapGenerateResponse(BaseModel):
    status: str
    mindmap: dict
    format: str = "json_tree"


class CodeGenerateRequest(BaseModel):
    student_id: str
    topic: str
    language: str = "Python"


class CodeGenerateResponse(BaseModel):
    status: str
    code: str
    language: str
    filename: str


class CodeExecuteRequest(BaseModel):
    code: str
    language: str = "Python"


class CodeExecuteResponse(BaseModel):
    status: str
    output: str
    error: str
    explanation: str
