# backend/models.py файл с моделями Pydantic для запросов и ответов API
from pydantic import BaseModel
from typing import Optional, Dict, Any

class CompileRequest(BaseModel):
    code: str
    language: str
    taskId: Optional[str] = None

class CompileResponse(BaseModel):
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    error: Optional[str] = None
    metrics: Optional[dict] = None

class AssessRequest(BaseModel):
    taskId: str
    code: str
    runResult: Optional[Dict[str, Any]] = None
    final: Optional[bool] = False

class AssessResponse(BaseModel):
    score: int
    comment: str
    issues: Optional[list] = []
    reportUrl: Optional[str] = None

class ChatMessage(BaseModel):
    role: str  # "system" | "assistant" | "user"
    content: str
    timestamp: float

class AntiCheatEvent(BaseModel):
    eventType: str  # "paste" | "tab_switch" | "window_blur"
    timestamp: int
    taskId: str

class AntiCheatAnalyze(BaseModel):
    taskId: str
    code: str
    codeLength: int
    timestamp: int
    taskDescription: str