from pydantic import BaseModel, Field
from typing import Optional, Union


class DocumentGenerateRequest(BaseModel):
    student_id: str
    topic: str = Field(..., max_length=500)
    difficulty: str = "medium"
    kp_id: Optional[str] = None


class DocumentGenerateResponse(BaseModel):
    status: str
    document: str
    metadata: dict


class QuestionsGenerateRequest(BaseModel):
    student_id: str
    topic: str = Field(..., max_length=500)
    count: int = Field(5, ge=1, le=20)
    kp_id: Optional[str] = None
    subject: Optional[str] = None


class QuestionsGenerateResponse(BaseModel):
    status: str
    topic: str
    count: int
    questions: list


class MindmapGenerateRequest(BaseModel):
    student_id: str
    topic: str = Field(..., max_length=500)
    kp_id: Optional[str] = None


class MindmapGenerateResponse(BaseModel):
    status: str
    mindmap: Union[str, dict]
    format: str = "markmap"


class CodeGenerateRequest(BaseModel):
    student_id: str
    topic: str = Field(..., max_length=500)
    language: str = "Python"
    kp_id: Optional[str] = None


class CodeGenerateResponse(BaseModel):
    status: str
    code: str
    language: str
    filename: str


class CodeExecuteRequest(BaseModel):
    code: str = Field(..., max_length=50000)
    language: str = "Python"
    kp_id: Optional[str] = None


class CodeExecuteResponse(BaseModel):
    status: str
    output: str
    error: str
    explanation: str
