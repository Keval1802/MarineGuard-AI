import os
from typing import Optional, Dict, Any
from app.config import settings
from supabase import create_client, Client

class SupabaseService:
    """
    Supabase Cloud Integration Service (Database PostgREST, Storage, Auth).
    Provides seamless production database interaction when deployed or connected.
    """
    _client: Optional[Client] = None

    @classmethod
    def get_client(cls) -> Client:
        if cls._client is None:
            url = settings.SUPABASE_URL
            key = settings.SUPABASE_SERVICE_ROLE_KEY or settings.SUPABASE_ANON_KEY or os.getenv("SUPABASE_ANON_KEY", "")
            cls._client = create_client(url, key)
        return cls._client

    @classmethod
    def upsert_incident(cls, incident_data: Dict[str, Any]) -> Dict[str, Any]:
        """Upsert incident record into Supabase PostgreSQL table."""
        client = cls.get_client()
        res = client.table("incidents").upsert(incident_data).execute()
        return res.data

    @classmethod
    def upload_evidence_artifact(cls, file_path: str, filename: str) -> Optional[str]:
        """Upload evidence image artifact to Supabase Storage bucket 'marineguard-evidence'."""
        if not os.path.exists(file_path):
            return None
        client = cls.get_client()
        try:
            with open(file_path, "rb") as f:
                res = client.storage.from_(settings.R2_BUCKET_NAME).upload(
                    path=filename,
                    file=f.read(),
                    file_options={"content-type": "image/png", "x-upsert": "true"}
                )
            # Construct public URL
            public_url = f"{settings.SUPABASE_URL}/storage/v1/object/public/{settings.R2_BUCKET_NAME}/{filename}"
            return public_url
        except Exception as e:
            print(f"[SupabaseService] Evidence upload note: {e}")
            return None
