from fastapi import APIRouter, Depends, HTTPException, status, Body
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from app.auth import require_user
from app.rag.retriever import MarineRAGRetriever

router = APIRouter(prefix="/rag", tags=["Retrieval-Augmented Generation (RAG)"])
rag_retriever = MarineRAGRetriever()

class RAGQueryRequest(BaseModel):
    query: str
    top_k: int = 3

@router.post("/query")
def query_rag_knowledge_base(
    request: RAGQueryRequest = Body(...),
    current_user: Dict[str, Any] = Depends(require_user)
):
    """POST /api/v1/rag/query (AUTHENTICATED) - Query RAG knowledge base for legal/SOP reference passages."""
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query string cannot be empty")
        
    passages = rag_retriever.retrieve_guidelines(request.query, top_k=request.top_k)
    return {
        "status": "success",
        "query": request.query,
        "total_results": len(passages),
        "passages": passages
    }

@router.get("/documents")
def list_rag_corpus_documents(current_user: Dict[str, Any] = Depends(require_user)):
    """GET /api/v1/rag/documents (AUTHENTICATED) - List indexed RAG corpus files."""
    chunks = rag_retriever.vector_store.chunks
    docs_summary: Dict[str, int] = {}
    for c in chunks:
        src = c.get("source", "unknown")
        docs_summary[src] = docs_summary.get(src, 0) + 1

    return {
        "status": "success",
        "total_chunks": len(chunks),
        "corpus_directory": rag_retriever.corpus_dir,
        "documents": [{"source_doc": doc, "chunks_count": count} for doc, count in docs_summary.items()]
    }

class RAGScrapeRequest(BaseModel):
    url: str
    doc_identifier: Optional[str] = None
    auto_reindex: bool = True

@router.post("/scrape")
def scrape_url_to_rag(
    request: RAGScrapeRequest = Body(...),
    current_user: Dict[str, Any] = Depends(require_user)
):
    """POST /api/v1/rag/scrape (AUTHENTICATED) - Scrape target webpage into RAG corpus & reindex."""
    import httpx
    import trafilatura
    import os
    import re

    if not request.url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="URL must start with http:// or https://")

    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
        resp = httpx.get(request.url, headers=headers, follow_redirects=True, timeout=12.0)
        if resp.status_code != 200:
            raise HTTPException(status_code=400, detail=f"Web page returned status code {resp.status_code}")

        clean_text = trafilatura.extract(resp.text)
        if not clean_text or len(clean_text.strip()) < 50:
            raise HTTPException(status_code=422, detail="Unable to extract meaningful text content from URL")

        # Compute safe filename
        safe_name = request.doc_identifier or re.sub(r'[^a-zA-Z0-9_]', '_', request.url.split("//")[-1][:30])
        filename = f"web_{safe_name}.txt"
        target_path = os.path.join(rag_retriever.corpus_dir, filename)

        file_content = f"SOURCE_URL: {request.url}\nDOCUMENT_NAME: {filename}\n\n{clean_text}"
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(file_content)

        # Re-index RAG vector store if requested
        if request.auto_reindex:
            rag_retriever.reindex()

        return {
            "status": "success",
            "message": f"Successfully ingested web page into RAG corpus file '{filename}'",
            "source_url": request.url,
            "filename": filename,
            "extracted_length": len(clean_text),
            "total_rag_chunks": len(rag_retriever.vector_store.chunks)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to scrape web asset: {str(e)}")

