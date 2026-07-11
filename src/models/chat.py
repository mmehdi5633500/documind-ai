from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from src.database.connection import Base
import datetime


class Chat(Base):

    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)

    role = Column(String(50), nullable=False)

    content = Column(Text, nullable=False)

    tokens_used = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="chats")

    document = relationship("Document", back_populates="chats")
