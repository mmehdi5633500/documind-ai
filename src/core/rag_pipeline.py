import requests
from config import settings
from src.core.document_processor import DocumentProcessor
from src.core.embedding_generator import EmbeddingGenerator
from src.core.vector_store import VectorStore
from src.core.hybrid_search import HybridSearch


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
        self.hybrid_search = HybridSearch()

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
        User ke sawaal ka jawab do — Hybrid Search se
        """

        collection_name = f"document_{document_id}"

        # ================================
        # STEP 1 — VECTOR SEARCH
        # ================================
        question_embedding = self.embedder.generate_single(question)

        vector_chunks = self.vector_store.search(
            collection_name=collection_name,
            query_embedding=question_embedding,
            n_results=15,
        )

        # ================================
        # STEP 2 — BM25 SEARCH
        # ================================
        all_chunks = self.vector_store.get_all_chunks(collection_name)
        self.hybrid_search.index_chunks(all_chunks)

        bm25_results = self.hybrid_search.bm25_search(query=question, top_k=15)

        # ================================
        # STEP 3 — COMBINE RESULTS
        # ================================
        combined_chunks = self.hybrid_search.combine_results(
            vector_results=vector_chunks, bm25_results=bm25_results, alpha=0.5
        )

        relevant_chunks = combined_chunks[:10]

        # ================================
        # STEP 4 — LLM KO BHEJO
        # ================================
        context = "\n\n".join(relevant_chunks)

        system_prompt = f"""You are a helpful AI assistant.
    Answer questions based ONLY on the provided context.
    If the answer is not in the context, say "I don't have enough information."

    Context:
    {context}"""

        messages = [{"role": "system", "content": system_prompt}]

        for msg in chat_history[-6:]:
            messages.append({"role": msg["role"], "content": msg["content"]})

        messages.append({"role": "user", "content": question})

        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {settings.OPENROUTER_API_KEY}"},
            json={"model": settings.LLM_MODEL, "messages": messages},
        )

        result = response.json()
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
