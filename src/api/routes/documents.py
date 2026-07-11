from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
import os
import shutil

from src.database.connection import get_db
from src.models.document import Document
from src.models.user import User
from src.schemas.document_schema import DocumentResponse, DocumentUpdate
from src.api.routes.auth import get_current_user
from config import settings

router = APIRouter(prefix="/documents", tags=["Documents"])


# =========================
# UPLOAD DOCUMENT
# =========================


@router.post(
    "/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED
)
def upload_document(
    file: UploadFile = File(...),
    title: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # File type check karo
    allowed_types = ["pdf", "txt", "docx"]
    file_extension = file.filename.split(".")[-1].lower()

    if file_extension not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed: {allowed_types}",
        )

    # File size check karo
    file.file.seek(0, 2)  # End pe jao
    file_size = file.file.tell()  # Size nikalo
    file.file.seek(0)  # Wapas start pe

    if file_size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large. Max size: 10MB",
        )

    # User ka folder banao
    user_upload_dir = os.path.join(settings.UPLOAD_DIR, str(current_user.id))
    os.makedirs(user_upload_dir, exist_ok=True)

    # File save karo
    file_path = os.path.join(user_upload_dir, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Database mein save karo
    new_document = Document(
        user_id=current_user.id,
        title=title or file.filename,
        filename=file.filename,
        file_path=file_path,
        file_type=file_extension,
        file_size=file_size,
        is_processed=False,
    )

    db.add(new_document)
    db.commit()
    db.refresh(new_document)

    return new_document


# =========================
# GET ALL DOCUMENTS
# =========================


@router.get("/", response_model=list[DocumentResponse])
def get_documents(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    documents = db.query(Document).filter(Document.user_id == current_user.id).all()

    return documents


# =========================
# GET SINGLE DOCUMENT
# =========================


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    document = (
        db.query(Document)
        .filter(Document.id == document_id, Document.user_id == current_user.id)
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
        )

    return document


# =========================
# UPDATE DOCUMENT
# =========================


@router.put("/{document_id}", response_model=DocumentResponse)
def update_document(
    document_id: int,
    update_data: DocumentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    document = (
        db.query(Document)
        .filter(Document.id == document_id, Document.user_id == current_user.id)
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
        )

    if update_data.title:
        document.title = update_data.title

    db.commit()
    db.refresh(document)

    return document


# =========================
# DELETE DOCUMENT
# =========================


@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    document = (
        db.query(Document)
        .filter(Document.id == document_id, Document.user_id == current_user.id)
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
        )

    # File bhi delete karo
    if os.path.exists(document.file_path):
        os.remove(document.file_path)

    db.delete(document)
    db.commit()

    return {"message": "Document deleted successfully"}
