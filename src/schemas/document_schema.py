from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class DocumentResponse(BaseModel):
    """
    Document upload hone ke baad
    Yeh response jayega
    """

    id: int
    title: str
    filename: str
    file_type: str
    file_size: int
    is_processed: bool
    chunk_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentUpdate(BaseModel):
    """
    Document ka title update karo
    """

    title: Optional[str] = None
