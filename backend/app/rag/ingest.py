import os
from typing import List, Dict, Any
from app.rag.vector_store import LocalVectorStore

class RAGIngestionPipeline:
    """
    Ingest pipeline for marine reference documents:
    - Reads text files from corpus directory
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

        vector_store.add_documents(all_chunks)
        vector_store.save_index(manifest_path)
        return vector_store
