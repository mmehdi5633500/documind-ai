import requests
from config import settings
from src.core.document_processor import DocumentProcessor
from src.core.embedding_generator import EmbeddingGenerator
from src.core.vector_store import VectorStore


class RAGPipeline:
    """
    RAG = Retrieval Augmented Generation

    Retrieve  = Related chunks dhundho
    Augmented = LLM ko context do
    Generation = AI jawab generate kare

    Flow:
    Document Upload → Process → Embed → Store
    User Sawaal → Embed → Search → LLM → Jawab
    """

    def __init__(self):
        self.processor = DocumentProcessor()
        self.embedder = EmbeddingGenerator()
        self.vector_store = VectorStore()

    # =========================
    # DOCUMENT PROCESS
    # =========================

    def process_document(self, file_path: str, file_type: str, document_id: int) -> int:
        """
        Document ko process karke
        Vector store mein save karo

        Returns: chunk count
        """
        print(f"Processing document {document_id}...")

        # Step 1: Text extract + chunks banao
        chunks = self.processor.process(file_path, file_type)
        print(f"Created {len(chunks)} chunks")

        # Step 2: Embeddings banao
        embeddings = self.embedder.generate(chunks)
        print(f"Generated {len(embeddings)} embeddings")

        # Step 3: Vector store mein save karo
        collection_name = f"document_{document_id}"
        count = self.vector_store.add_chunks(
            collection_name=collection_name,
            chunks=chunks,
            embeddings=embeddings,
            document_id=document_id,
        )
        print(f"Stored {count} chunks in vector store ✅")

        return count

    # =========================
    # CHAT
    # =========================

    def chat(
        self, document_id: int, question: str, chat_history: list[dict] = []
    ) -> dict:
        """
        User ke sawaal ka jawab do

        1. Sawaal ko embed karo
        2. Related chunks dhundho
        3. LLM ko context + sawaal do
        4. Jawab return karo
        """

        # Step 1: Sawaal embed karo
        question_embedding = self.embedder.generate_single(question)

        # Step 2: Related chunks dhundho
        collection_name = f"document_{document_id}"
        relevant_chunks = self.vector_store.search(
            collection_name=collection_name,
            query_embedding=question_embedding,
            n_results=5,
        )

        # Step 3: Context banao
        context = "\n\n".join(relevant_chunks)

        # Step 4: LLM ko bhejo
        system_prompt = f"""You are a helpful AI assistant.
Answer questions based ONLY on the provided context.
If the answer is not in the context, say "I don't have enough information."

Context:
{context}"""

        # Chat history + naya sawaal
        messages = [{"role": "system", "content": system_prompt}]

        # Purani history add karo
        for msg in chat_history[-6:]:  # Last 6 messages
            messages.append({"role": msg["role"], "content": msg["content"]})

        # Naya sawaal
        messages.append({"role": "user", "content": question})
        # LLM call
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {settings.OPENROUTER_API_KEY}"},
            json={"model": settings.LLM_MODEL, "messages": messages},
        )

        result = response.json()
        answer = result["choices"][0]["message"]["content"]
        answer = result["choices"][0]["message"]["content"]
        tokens = result["usage"]["total_tokens"]

        return {
            "answer": answer,
            "tokens_used": tokens,
            "chunks_used": len(relevant_chunks),
        }

    # =========================
    # DELETE
    # =========================

    def delete_document(self, document_id: int):
        """
        Document delete hone pe
        Vector store se bhi hatao
        """
        collection_name = f"document_{document_id}"
        self.vector_store.delete_collection(collection_name)
