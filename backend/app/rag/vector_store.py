import os
import json
import math
from typing import List, Dict, Any, Tuple, Optional

class LocalVectorStore:
    """
    Lightweight, deterministic local Vector Store for RAG document retrieval.
    Computes TF-IDF vector similarity over chunked marine documents.
    Supports JSON serialization for offline pre-built index deployment (Section 33 & 43).
    """

    def __init__(self):
        self.chunks: List[Dict[str, Any]] = []
        self.vocab: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}

    def _tokenize(self, text: str) -> List[str]:
        words = text.lower().replace("-", " ").replace("\n", " ").split()
        return [w.strip(".,();:\"'") for w in words if len(w) > 2]

    def add_document(self, doc_id: str, text: str, metadata: Optional[Dict[str, Any]] = None):
        """Adds a single dynamic document chunk and updates TF-IDF vector index."""
        meta = metadata or {}
        new_chunk = {
            "id": doc_id,
            "text": text,
            "source": meta.get("source", "Dynamic Location Scraper"),
            "topic": meta.get("topic", "Location Knowledge")
        }
        # Check if already present to prevent duplicate chunks
        existing = [c for c in self.chunks if c.get("id") == doc_id or c.get("text") == text]
        if not existing:
            self.chunks.append(new_chunk)
            self.add_documents(list(self.chunks))

    def add_documents(self, chunk_list: List[Dict[str, Any]]):
        """Adds text chunks and computes vocabulary TF-IDF representation."""
        self.chunks = chunk_list
        doc_count = len(self.chunks)
        if doc_count == 0:
            return

        # Build vocabulary & Document Frequency (DF)
        df: Dict[str, int] = {}
        for chunk in self.chunks:
            tokens = set(self._tokenize(chunk["text"]))
            chunk["tokens"] = list(tokens)
            for t in tokens:
                df[t] = df.get(t, 0) + 1

        # Calculate Inverse Document Frequency (IDF)
        self.idf = {t: math.log((1.0 + doc_count) / (1.0 + count)) + 1.0 for t, count in df.items()}
        vocab_words = sorted(list(self.idf.keys()))
        self.vocab = {w: idx for idx, w in enumerate(vocab_words)}

        # Build chunk TF-IDF vectors
        for chunk in self.chunks:
            tokens = self._tokenize(chunk["text"])
            tf: Dict[str, float] = {}
            for t in tokens:
                tf[t] = tf.get(t, 0.0) + 1.0
            
            vec = {}
            norm_sq = 0.0
            for t, val in tf.items():
                if t in self.idf:
                    score = (val / len(tokens)) * self.idf[t]
                    vec[t] = score
                    norm_sq += score * score

            chunk["vector"] = vec
            chunk["norm"] = math.sqrt(norm_sq) if norm_sq > 0 else 1.0

    def similarity_search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Queries vector store and returns top_k relevant document chunks."""
        q_tokens = self._tokenize(query)
        if not q_tokens or not self.chunks:
            return []

        q_tf: Dict[str, float] = {}
        for t in q_tokens:
            q_tf[t] = q_tf.get(t, 0.0) + 1.0

        q_vec = {}
        q_norm_sq = 0.0
        for t, val in q_tf.items():
            if t in self.idf:
                score = (val / len(q_tokens)) * self.idf[t]
                q_vec[t] = score
                q_norm_sq += score * score

        q_norm = math.sqrt(q_norm_sq) if q_norm_sq > 0 else 1.0

        scores = []
        for chunk in self.chunks:
            dot_product = 0.0
            c_vec = chunk.get("vector", {})
            for t, q_val in q_vec.items():
                if t in c_vec:
                    dot_product += q_val * c_vec[t]

            cosine_sim = dot_product / (q_norm * chunk.get("norm", 1.0))
            if cosine_sim > 0.05:
                scores.append((cosine_sim, chunk))

        scores.sort(key=lambda x: x[0], reverse=True)
        return [
            {
                "text": item[1]["text"],
                "source": item[1]["source"],
                "score": round(item[0], 3)
            }
            for item in scores[:top_k]
        ]

    def save_index(self, filepath: str):
        """Saves vector index to JSON manifest file for versioned deployment."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        serializable_chunks = [
            {"text": c["text"], "source": c["source"]}
            for c in self.chunks
        ]
        data = {
            "chunks": serializable_chunks,
            "idf": self.idf
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load_index(self, filepath: str) -> bool:
        """Loads pre-built vector index from manifest file."""
        if not os.path.exists(filepath):
            return False
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.add_documents(data.get("chunks", []))
        return True
