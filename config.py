import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # App
    APP_NAME = "DocuMind AI"
    VERSION = "1.0.0"
    DEBUG = True

    # API Keys
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/documind.db")

    # JWT
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
    ALGORITHM = "HS256"
    TOKEN_EXPIRE = 30  # minutes

    # Uploads
    UPLOAD_DIR = "data/uploads"
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

    # LLM
    LLM_MODEL = "openai/gpt-3.5-turbo"

    # Embeddings
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"


settings = Settings()
