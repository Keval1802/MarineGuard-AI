import os
from typing import List, Dict, Any
from app.rag.vector_store import LocalVectorStore

DEFAULT_BASELINE_KNOWLEDGE = [
    "MARPOL Annex I regulation 15 restricts discharge of oil or oily mixtures into the sea from oil tankers or ships of 400 gross tonnage and above. Discharges within 50 nautical miles of land or in special coastal zones are strictly prohibited.",
    "MARPOL Annex V regulates the prevention of pollution by garbage from ships. Disposal of all plastics into the sea is strictly prohibited under all circumstances.",
    "Indian Maritime Zone Act 1976 grants the Indian Coast Guard and National Oil Spill Disaster Contingency Plan (NOS-DCP) authority to enforce containment, cleanup, and vessel inspection in India's Exclusive Economic Zone (EEZ).",
    "Gulf of Khambhat oceanographic conditions feature strong semi-diurnal tidal currents up to 3.0 m/s, macro-tidal ranges exceeding 10 meters, and high estuarine sediment transport around Hazira and Surat."
]

class RAGIngestionPipeline:
    """
    Ingest pipeline for marine reference documents:
    - Reads text files from corpus directory (or uses default baseline knowledge if empty)
    - Chunks text into ~500 character segments with 100 char overlap
    - Builds local vector index
    """

    @staticmethod
    def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
        """Splits document text into overlapping window chunks."""
        chunks = []
        start = 0
        text_len = len(text)
        
        while start < text_len:
            end = min(text_len, start + chunk_size)
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            start += (chunk_size - overlap)
            
        return chunks

    @classmethod
    def ingest_corpus_directory(
        cls,
        corpus_dir: str,
        manifest_path: str
    ) -> LocalVectorStore:
        """Ingests all text documents in directory and builds vector store index."""
        vector_store = LocalVectorStore()
        all_chunks = []

        if os.path.exists(corpus_dir):
            for fname in os.listdir(corpus_dir):
                if fname.endswith(".txt"):
                    fpath = os.path.join(corpus_dir, fname)
                    with open(fpath, "r", encoding="utf-8") as f:
                        content = f.read()
                    
                    chunks = cls.chunk_text(content)
                    for c in chunks:
                        all_chunks.append({
                            "text": c,
                            "source": fname
                        })

        if not all_chunks:
            for text in DEFAULT_BASELINE_KNOWLEDGE:
                chunks = cls.chunk_text(text)
                for c in chunks:
                    all_chunks.append({
                        "text": c,
                        "source": "Default Legal & MARPOL Regulations"
                    })

        vector_store.add_documents(all_chunks)
        os.makedirs(os.path.dirname(manifest_path), exist_ok=True)
        vector_store.save_index(manifest_path)
        return vector_store
