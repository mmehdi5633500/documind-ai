import os
from pathlib import Path


class DocumentProcessor:
    """
    Document ko read karke
    chunks mein todta hai

    Kyun chunks?
    LLM ka context window limited hai
    Poora document ek saath nahi dete
    Relevant chunks dhundh ke dete hain
    """

    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap

    # =========================
    # MAIN FUNCTION
    # =========================

    def process(self, file_path: str, file_type: str) -> list[str]:
        """
        File padhke chunks return karo
        """
        # Text extract karo
        text = self._extract_text(file_path, file_type)

        if not text:
            raise ValueError("No text extracted from document")

        # Chunks banao
        chunks = self._create_chunks(text)

        return chunks

    # =========================
    # TEXT EXTRACT
    # =========================

    def _extract_text(self, file_path: str, file_type: str) -> str:
        """
        File type ke hisaab se text nikalo
        """
        if file_type == "txt":
            return self._read_txt(file_path)
        elif file_type == "pdf":
            return self._read_pdf(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

    def _read_txt(self, file_path: str) -> str:
        """
        Simple text file padhna
        """
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    def _read_pdf(self, file_path: str) -> str:
        """
        PDF se text nikalna
        """
        try:
            import PyPDF2

            text = ""
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            return text
        except ImportError:
            raise ImportError("PyPDF2 not installed: pip install PyPDF2")

    # =========================
    # CHUNKING
    # =========================

    def _create_chunks(self, text: str) -> list[str]:
        """
        Text ko chhote pieces mein todo

        chunk_size = 500 words per chunk
        overlap    = 50 words shared between chunks

        Kyun overlap?
        Ek chunk ka context doosre mein bhi ho
        Important info miss na ho
        """
        words = text.split()
        chunks = []
        start = 0

        while start < len(words):
            end = start + self.chunk_size
            chunk = " ".join(words[start:end])
            chunks.append(chunk)
            start = end - self.overlap  # Overlap

        return chunks
