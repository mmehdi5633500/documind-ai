from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.database.connection import get_db
from src.models.document import Document
from src.models.user import User
from src.api.routes.auth import get_current_user
from src.core.embedding_generator import EmbeddingGenerator
from src.core.vector_store import VectorStore

router = APIRouter(prefix="/search", tags=["Search"])

embedder = EmbeddingGenerator()
vector_store = VectorStore()


class SearchRequest(BaseModel):
    document_id: int
    query: str
    n_results: int = 5


@router.post("/")
def search(
    request: SearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Document mein semantic search karo
    Related chunks return karo
    """
    document = (
        db.query(Document)
        .filter(Document.id == request.document_id, Document.user_id == current_user.id)
        .first()
    )

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    if not document.is_processed:
        raise HTTPException(status_code=400, detail="Document not processed yet")

    # Query embed karo
    query_embedding = embedder.generate_single(request.query)

    # Search karo
    collection_name = f"document_{request.document_id}"
    results = vector_store.search(
        collection_name=collection_name,
        query_embedding=query_embedding,
        n_results=request.n_results,
    )

    return {"query": request.query, "results": results, "count": len(results)}
