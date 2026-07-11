from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ChatRequest(BaseModel):
    """
    User ne sawaal poocha
    """

    document_id: int
    message: str


class ChatResponse(BaseModel):
    """
    AI ka jawab
    """

    id: int
    role: str
    content: str
    tokens_used: int
    created_at: datetime

    class Config:
        from_attributes = True


class ChatHistory(BaseModel):
    """
    Poori chat history
    """

    document_id: int
    messages: list[ChatResponse]
