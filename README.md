# DocuMind AI

> Chat with your documents using Retrieval Augmented Generation (RAG)

DocuMind AI is a production-ready backend system that enables intelligent 
document interaction. Upload any document, and engage in context-aware 
conversations powered by state-of-the-art language models.

## 🌐 Live Demo

**Try it live:** [https://documind-ai-production-35e0.up.railway.app/docs](https://documind-ai-production-35e0.up.railway.app/docs)

Deployed on Railway with PostgreSQL for persistent storage.

---

## Architecture Overview
┌─────────────────────────────────────────────────────────┐
│                      Client Request                      │
└─────────────────────────┬───────────────────────────────┘
│
┌─────────────────────────▼───────────────────────────────┐
│                    FastAPI Backend                        │
│                                                          │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐            │
│   │   Auth   │  │Documents │  │   Chat   │            │
│   │  Routes  │  │  Routes  │  │  Routes  │            │
│   └──────────┘  └──────────┘  └──────────┘            │
└─────────────────────────┬───────────────────────────────┘
│
┌─────────────────────────▼───────────────────────────────┐
│                     RAG Pipeline                          │
│                                                          │
│  Document → Chunks → Embeddings → ChromaDB               │
│  Query → Embedding → Search → Context → LLM → Answer    │
└─────────────────────────────────────────────────────────┘

---

## Features

- **JWT Authentication** — Secure signup, login, and protected routes
- **Document Management** — Upload, manage, and delete PDF and TXT files
- **RAG Pipeline** — Intelligent document processing with semantic chunking
- **Vector Search** — ChromaDB-powered semantic similarity search
- **AI Chat** — Context-aware conversations with document memory
- **Chat History** — Persistent conversation tracking per document
- **Multi-document Support** — Isolated vector collections per document

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| API | FastAPI | High-performance REST API |
| ORM | SQLAlchemy | Database abstraction |
| Database | SQLite (Dev) / PostgreSQL (Production) |
| Vector DB | ChromaDB | Embedding storage and search |
| Embeddings | Sentence Transformers | Text vectorization |
| LLM | OpenRouter (GPT-3.5) | Response generation |
| Auth | JWT + bcrypt | Security |
| Validation | Pydantic | Request/response validation |

---

## Project Structure
documind-ai/
│
├── src/
│   ├── api/
│   │   └── routes/
│   │       ├── auth.py           # Authentication endpoints
│   │       ├── documents.py      # Document CRUD endpoints
│   │       ├── chat.py           # RAG chat endpoints
│   │       └── search.py         # Semantic search endpoint
│   │
│   ├── core/
│   │   ├── document_processor.py # Text extraction and chunking
│   │   ├── embedding_generator.py# Vector embedding generation
│   │   ├── vector_store.py       # ChromaDB operations
│   │   └── rag_pipeline.py       # End-to-end RAG orchestration
│   │
│   ├── models/
│   │   ├── user.py               # User database model
│   │   ├── document.py           # Document database model
│   │   └── chat.py               # Chat database model
│   │
│   ├── schemas/
│   │   ├── user_schema.py        # User request/response schemas
│   │   ├── document_schema.py    # Document schemas
│   │   └── chat_schema.py        # Chat schemas
│   │
│   └── database/
│       └── connection.py         # Database engine and session
│
├── data/
│   ├── uploads/                  # Uploaded documents
│   └── vectordb/                 # ChromaDB persistent storage
│
├── main.py                       # Application entry point
├── config.py                     # Environment configuration
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md

---

## Getting Started

### Prerequisites

- Python 3.10+
- OpenRouter API Key ([openrouter.ai](https://openrouter.ai))

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/documind-ai.git
cd documind-ai

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
```

### Environment Variables

```env
OPENROUTER_API_KEY=your_openrouter_api_key
SECRET_KEY=your_jwt_secret_key
```

### Run

```bash
python -m uvicorn main:app --reload
```

API will be available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## API Reference

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/auth/signup` | Register new user |
| `POST` | `/auth/login` | Login and get JWT token |
| `GET` | `/auth/profile` | Get current user profile |
| `PUT` | `/auth/profile` | Update profile |

### Documents

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/documents/upload` | Upload PDF or TXT file |
| `GET` | `/documents/` | List all documents |
| `GET` | `/documents/{id}` | Get document details |
| `PUT` | `/documents/{id}` | Update document title |
| `DELETE` | `/documents/{id}` | Delete document |

### Chat

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/chat/process/{id}` | Process document for RAG |
| `POST` | `/chat/ask` | Ask a question |
| `GET` | `/chat/history/{id}` | Get chat history |
| `DELETE` | `/chat/history/{id}` | Clear chat history |

### Search

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/search/` | Semantic search in document |

---

## RAG Pipeline
INDEXING
────────
Document Upload
→ Text Extraction (PyPDF2 / plain text)
→ Semantic Chunking (500 words, 50 overlap)
→ Embedding Generation (all-MiniLM-L6-v2)
→ ChromaDB Storage (cosine similarity index)
QUERYING
────────
User Question
→ Question Embedding
→ Semantic Search (top 5 chunks)
→ Context Assembly
→ LLM Prompt (system + context + history + question)
→ Response Generation
→ Chat History Persistence

---

## Roadmap

- [ ] Async document processing with background tasks
- [ ] PostgreSQL support for production
- [ ] Docker containerization
- [ ] AWS S3 for file storage
- [ ] DOCX file support
- [ ] Multi-language document support
- [ ] Usage analytics dashboard

---

## Author

**Muntazir Mehdi**  
AI Engineering 
[GitHub](https://github.com/mmehdi5633500)

---

## License

This project is licensed under the MIT License.