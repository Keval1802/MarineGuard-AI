import sys
import os

# Add backend directory to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.rag.ingest import RAGIngestionPipeline

def main():
    backend_dir = os.path.join(os.path.dirname(__file__), "..", "backend")
    corpus_dir = os.path.join(backend_dir, "storage", "rag")
    os.makedirs(corpus_dir, exist_ok=True)
    manifest_path = os.path.join(corpus_dir, "manifest.json")
    
    print(f"Building RAG index from corpus directory: {corpus_dir}")
    vector_store = RAGIngestionPipeline.ingest_corpus_directory(corpus_dir, manifest_path)
    print(f"RAG index successfully built with {len(vector_store.chunks)} document chunks.")
    print(f"Manifest saved to: {manifest_path}")

if __name__ == "__main__":
    main()
