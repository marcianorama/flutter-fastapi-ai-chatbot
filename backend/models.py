from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ChatRequest(BaseModel):
    session_id: str
    message: str
    model: Optional[str] = None  # Override default model if provided


class MessageRecord(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: str


class ChatResponse(BaseModel):
    reply: str
    session_id: str
    model_used: str


class HistoryResponse(BaseModel):
    session_id: str
    messages: List[MessageRecord]
    total_messages: int


class ClearResponse(BaseModel):
    session_id: str
    message: str


class HealthResponse(BaseModel):
    status: str
    app_name: str
    model: str
    version: str = "1.0.0"
