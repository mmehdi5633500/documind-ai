import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.database.connection import Base, engine
from src.models import user, document, chat
from src.api.routes import auth, documents, chat as chat_router

# Tables banao
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="DocuMind AI",
    description="AI-powered Document Knowledge Base",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(chat_router.router)


@app.get("/")
def root():
    return {"app": "DocuMind AI", "version": "1.0.0", "status": "running"}


from src.api.routes import auth, documents, chat as chat_router, search

app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(chat_router.router)
app.include_router(search.router)
