import os
import shutil
from typing import Optional
from app.config import settings

class StorageService:
    """
    Evidence and object storage manager.
    Supports local filesystem storage with Cloudflare R2 adapter hook.
    """

    def __init__(self):
        self.storage_dir = settings.LOCAL_STORAGE_DIR
        os.makedirs(self.storage_dir, exist_ok=True)

    def save_file(self, file_bytes: bytes, filename: str) -> str:
        """Saves file to evidence storage and returns asset URI path."""
        target_path = os.path.join(self.storage_dir, filename)
        with open(target_path, "wb") as f:
            f.write(file_bytes)
        return f"/storage/evidence/{filename}"

    def get_file_path(self, relative_path: str) -> str:
        """Resolves relative file path to absolute filesystem location."""
        filename = os.path.basename(relative_path)
        return os.path.join(self.storage_dir, filename)
