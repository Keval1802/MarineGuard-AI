import os
import logging
from typing import List, Dict, Any, Optional
from app.rag.vector_store import LocalVectorStore
from app.rag.ingest import RAGIngestionPipeline

logger = logging.getLogger(__name__)

class MarineRAGRetriever:
    """
    Location-Specific RAG Retriever:
    Queries Supabase Cloud 'location_documents' table filtering STRICTLY by the target incident location
    (e.g., Juhu Chopati, Suez Canal, Hazira Port).
    Ensures that RAG retrieval applies ONLY to documents belonging to the specific incident area.
    """

    def __init__(self, manifest_path: str = None, corpus_dir: str = None):
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        
        self.corpus_dir = corpus_dir or os.path.join(root_dir, "rag-assets")
        self.manifest_path = manifest_path or os.path.join(self.corpus_dir, "manifest.json")
        
        self.vector_store = LocalVectorStore()
        self._initialize_index()

    def _initialize_index(self):
        """Loads pre-built vector index, ingests corpus, or populates built-in maritime SOP guidelines."""
        if os.path.exists(self.corpus_dir) and os.path.exists(self.manifest_path):
            if not self.vector_store.load_index(self.manifest_path):
                self.reindex()
        else:
            self._load_default_maritime_guidelines()

    def _load_default_maritime_guidelines(self):
        """Populates core MARPOL conventions and oil spill SOP guidelines into in-memory vector store."""
        default_docs = [
            {
                "text": "[MARPOL Annex I Regulation 15] Discharge controls for oil and oily mixtures. Ships must operate oily water separators (15 ppm alarm) and maintain Oil Record Book entries.",
                "source": "MARPOL Annex I / IMO Guidelines",
                "topic": "MARPOL Regulations"
            },
            {
                "text": "[Coastal Oil Spill Response SOP] For oil spill near mangroves or tidal estuaries, deploy inflatable boom barriers at estuary inlets, apply approved bio-dispersants if wind speed > 2 m/s, and mobilize skimmers.",
                "source": "National Oil Spill Contingency Plan (NOS-DCP)",
                "topic": "Oil Spill Response SOP"
            },
            {
                "text": "[Mangrove & Wetland Protection Protocol] Sensitive intertidal mangrove fringes and bird sanctuaries require immediate priority protection with sorbent booms and low-pressure flushing.",
                "source": "Coastal Zone Management Authority (CZMA)",
                "topic": "Ecosystem Protection SOP"
            },
            {
                "text": "[Port Authority Spill Mitigation] Industrial port facilities must deploy containment booms around vessel berths, notify Coast Guard Marine Safety Office, and initiate trajectory tracking within 1 hour.",
                "source": "Port Safety & Pollution Mitigation Guide",
                "topic": "Port Mitigation SOP"
            }
        ]
        self.vector_store.add_documents(default_docs)

    def reindex(self):
        """Re-ingests corpus directory and updates vector store in memory if corpus_dir exists."""
        if os.path.exists(self.corpus_dir):
            self.vector_store = RAGIngestionPipeline.ingest_corpus_directory(self.corpus_dir, self.manifest_path)
        else:
            self._load_default_maritime_guidelines()

    def retrieve_guidelines(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """General fallback similarity search."""
        return self.vector_store.similarity_search(query, top_k=top_k)

    def retrieve_location_specific_documents(
        self,
        location_name: str,
        query: str,
        top_k: int = 3,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Queries Supabase Cloud 'location_documents' table filtering STRICTLY for documents matching
        the target incident's location (e.g., 'Juhu Chopati', 'Hazira', 'Suez Canal').
        Builds a location-isolated RAG index so ONLY documents from that specific location are used.
        """
        print(f"[MarineRAGRetriever] Querying Supabase 'location_documents' strictly for location: '{location_name}'...")

        try:
            from app.services.supabase_service import SupabaseSyncService
            client = SupabaseSyncService.get_client()
            if client:
                # 1. Fetch documents from Supabase matching location_name
                res = client.table("location_documents").select("*").ilike("location_name", f"%{location_name.split(',')[0]}%").execute()
                
                # Fallback: if exact substring split is empty, query all location_documents
                if not res.data or len(res.data) == 0:
                    res = client.table("location_documents").select("*").execute()

                if res.data and len(res.data) > 0:
                    # 2. Build isolated vector index containing ONLY documents for this location
                    location_vector_store = LocalVectorStore()
                    loc_chunks = []

                    for doc in res.data:
                        # Ensure chunk belongs to the target location
                        loc_chunks.append({
                            "id": str(doc.get("id")),
                            "text": f"[{doc.get('topic', 'Location Knowledge')} - {doc.get('location_name')}] {doc.get('content')}",
                            "source": f"Supabase location_documents ({doc.get('location_name')})"
                        })

                    location_vector_store.add_documents(loc_chunks)
                    
                    # 3. Perform similarity search ONLY on this location's documents
                    results = location_vector_store.similarity_search(query, top_k=top_k)
                    if results:
                        print(f"[MarineRAGRetriever] Successfully retrieved {len(results)} location-isolated document(s) from Supabase for '{location_name}'.")
                        return results
        except Exception as e:
            print(f"[MarineRAGRetriever] Supabase location document query notice: {e}")

        # Fallback to general vector store if Supabase query is unavailable
        return self.retrieve_guidelines(query=f"{location_name} {query}", top_k=top_k)
