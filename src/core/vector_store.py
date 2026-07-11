import chromadb
from chromadb.config import Settings as ChromaSettings


class VectorStore:
    """
    Embeddings store karta hai
    Similar chunks dhundta hai

    ChromaDB = Vector Database
    Normal DB numbers store nahi kar sakta efficiently
    ChromaDB specifically vectors ke liye bana hai
    """

    def __init__(self):
        # ChromaDB client banao
        self.client = chromadb.PersistentClient(
            path="data/vectordb",
        )

    def get_or_create_collection(self, collection_name: str):
        """
        Collection = Table (Normal DB mein)
        Har document ki apni collection
        """
        return self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},  # Cosine similarity use karo
        )

    def add_chunks(
        self,
        collection_name: str,
        chunks: list[str],
        embeddings: list[list[float]],
        document_id: int,
    ):
        """
        Chunks aur unki embeddings store karo
        """
        collection = self.get_or_create_collection(collection_name)

        # Unique IDs banao har chunk ke liye
        ids = [f"doc_{document_id}_chunk_{i}" for i in range(len(chunks))]

        # Metadata — Baad mein filter karne ke liye
        metadatas = [
            {"document_id": document_id, "chunk_index": i} for i in range(len(chunks))
        ]

        collection.add(
            ids=ids, embeddings=embeddings, documents=chunks, metadatas=metadatas
        )

        return len(chunks)

    def search(
        self, collection_name: str, query_embedding: list[float], n_results: int = 5
    ) -> list[str]:
        """
        Sawaal se related chunks dhundho

        query_embedding = Sawaal ka vector
        n_results = Kitne chunks chahiye
        """
        collection = self.get_or_create_collection(collection_name)

        results = collection.query(
            query_embeddings=[query_embedding], n_results=n_results
        )

        # Sirf text chunks return karo
        return results["documents"][0]

    def delete_collection(self, collection_name: str):
        """
        Document delete hone pe
        Uski collection bhi delete karo
        """
        try:
            self.client.delete_collection(collection_name)
        except Exception:
            pass
