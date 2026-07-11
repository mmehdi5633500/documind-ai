from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.database.connection import get_db
from src.models.document import Document
from src.models.chat import Chat
from src.models.user import User
from src.schemas.chat_schema import ChatRequest, ChatResponse, ChatHistory
from src.api.routes.auth import get_current_user
from src.core.rag_pipeline import RAGPipeline

router = APIRouter(prefix="/chat", tags=["Chat"])

# RAG Pipeline — ek baar banao
rag = RAGPipeline()


# =========================
# DOCUMENT PROCESS KARO
# =========================


@router.post("/process/{document_id}")
def process_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Document upload ke baad
    Yeh route call karo
    Embeddings ban jayengi
    """
    # Document dhundho
    document = (
        db.query(Document)
        .filter(Document.id == document_id, Document.user_id == current_user.id)
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
        )

    if document.is_processed:
        return {"message": "Document already processed"}

    # Process karo
    chunk_count = rag.process_document(
        file_path=document.file_path,
        file_type=document.file_type,
        document_id=document.id,
    )

    # DB update karo
    document.is_processed = True
    document.chunk_count = chunk_count
    db.commit()

    return {"message": "Document processed successfully", "chunk_count": chunk_count}


# =========================
# CHAT WITH DOCUMENT
# =========================


@router.post("/ask", response_model=ChatResponse)
def ask_question(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Document ke baare mein sawaal poocho
    """
    # Document check karo
    document = (
        db.query(Document)
        .filter(Document.id == request.document_id, Document.user_id == current_user.id)
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
        )

    if not document.is_processed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document not processed yet. Call /chat/process/{id} first",
        )

    # Chat history lo
    history = (
        db.query(Chat)
        .filter(
            Chat.document_id == request.document_id, Chat.user_id == current_user.id
        )
        .order_by(Chat.created_at)
        .all()
    )

    history_list = [{"role": h.role, "content": h.content} for h in history]

    # RAG se jawab lo
    result = rag.chat(
        document_id=request.document_id,
        question=request.message,
        chat_history=history_list,
    )

    # User message save karo
    user_message = Chat(
        user_id=current_user.id,
        document_id=request.document_id,
        role="user",
        content=request.message,
        tokens_used=0,
    )
    db.add(user_message)

    # AI response save karo
    ai_message = Chat(
        user_id=current_user.id,
        document_id=request.document_id,
        role="assistant",
        content=result["answer"],
        tokens_used=result["tokens_used"],
    )
    db.add(ai_message)
    db.commit()
    db.refresh(ai_message)

    return ai_message


# =========================
# CHAT HISTORY
# =========================


@router.get("/history/{document_id}")
def get_chat_history(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Document ki poori chat history
    """
    document = (
        db.query(Document)
        .filter(Document.id == document_id, Document.user_id == current_user.id)
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
        )

    messages = (
        db.query(Chat)
        .filter(Chat.document_id == document_id, Chat.user_id == current_user.id)
        .order_by(Chat.created_at)
        .all()
    )

    return {
        "document_id": document_id,
        "document_title": document.title,
        "messages": messages,
    }


# =========================
# CLEAR CHAT HISTORY
# =========================


@router.delete("/history/{document_id}")
def clear_chat_history(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Chat history delete karo
    """
    db.query(Chat).filter(
        Chat.document_id == document_id, Chat.user_id == current_user.id
    ).delete()

    db.commit()

    return {"message": "Chat history cleared"}
