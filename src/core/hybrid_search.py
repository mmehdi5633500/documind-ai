from rank_bm25 import BM25Okapi
import numpy as np


class HybridSearch:
    """
    Vector Search + BM25 Keyword Search combine karta hai

    Kyun?
    Vector Search = Semantic meaning samajhta hai
    BM25 = Exact keywords match karta hai

    Dono combine karke best results milte hain
    """

    def __init__(self):
        self.bm25 = None
        self.chunks = []

    def index_chunks(self, chunks: list[str]):
        """
        Chunks ko BM25 ke liye tayar karo

        BM25 ko words chahiye — tokenize karna padta hai
        """
        self.chunks = chunks

        # Har chunk ko words mein todo
        tokenized_chunks = [chunk.lower().split() for chunk in chunks]

        # BM25 index banao
        self.bm25 = BM25Okapi(tokenized_chunks)

    def bm25_search(self, query: str, top_k: int = 10) -> list[dict]:
        """
        Keyword-based search
        Exact words match karta hai
        """
        if self.bm25 is None:
            raise ValueError("Chunks not indexed yet")

        tokenized_query = query.lower().split()

        # Har chunk ko score do
        scores = self.bm25.get_scores(tokenized_query)

        # Top K results nikalo
        top_indices = np.argsort(scores)[::-1][:top_k]

        results = [
            {"chunk": self.chunks[i], "score": float(scores[i]), "index": int(i)}
            for i in top_indices
            if scores[i] > 0  # Sirf relevant results
        ]

        return results

    def combine_results(
        self, vector_results: list[str], bm25_results: list[dict], alpha: float = 0.5
    ) -> list[str]:
        """
        Vector aur BM25 results ko combine karo

        alpha = Weight balance
        alpha=0.5 → Dono equal importance
        alpha=0.7 → Vector search zyada important
        alpha=0.3 → BM25 zyada important
        """
        combined = {}

        # Vector results add karo (rank ke hisaab se score)
        for rank, chunk in enumerate(vector_results):
            score = (len(vector_results) - rank) / len(vector_results)
            combined[chunk] = combined.get(chunk, 0) + (alpha * score)

        # BM25 results add karo
        if bm25_results:
            max_bm25_score = max(r["score"] for r in bm25_results)
            for r in bm25_results:
                normalized_score = (
                    r["score"] / max_bm25_score if max_bm25_score > 0 else 0
                )
                chunk = r["chunk"]
                combined[chunk] = combined.get(chunk, 0) + (
                    (1 - alpha) * normalized_score
                )

        # Score ke hisaab se sort karo
        sorted_chunks = sorted(combined.items(), key=lambda x: x[1], reverse=True)

        return [chunk for chunk, score in sorted_chunks]
