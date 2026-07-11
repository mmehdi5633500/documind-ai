from sentence_transformers import SentenceTransformer
import numpy as np


class EmbeddingGenerator:
    """
    Text ko numbers (vectors) mein convert karta hai

    Kyun?
    Computer text nahi samajhta
    Numbers samajhta hai

    Similar text → Similar numbers
    "Python language" ≈ "Programming in Python"
    """

    def __init__(self):
        print("Loading embedding model...")
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        print("Embedding model loaded ✅")

    def generate(self, texts: list[str]) -> list[list[float]]:
        """
        List of texts → List of embeddings
        """
        embeddings = self.model.encode(
            texts, show_progress_bar=True, convert_to_numpy=True
        )
        return embeddings.tolist()

    def generate_single(self, text: str) -> list[float]:
        """
        Single text → Single embedding
        Sawaal ke liye use hoga
        """
        embedding = self.model.encode([text], convert_to_numpy=True)
        return embedding[0].tolist()
