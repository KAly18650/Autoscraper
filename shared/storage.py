"""
Storage utility for Google Cloud Storage with local fallback.
"""
import os
from typing import Optional, List
from .config import get_gcs_bucket_name
from .logger import get_logger

logger = get_logger(__name__)

class StorageManager:
    def __init__(self):
        self.bucket_name = get_gcs_bucket_name()
        self.client = None
        self.bucket = None
        
        if self.bucket_name:
            try:
                from google.cloud import storage
                self.client = storage.Client()
                self.bucket = self.client.bucket(self.bucket_name)
                logger.info(f"StorageManager initialized with GCS bucket: {self.bucket_name}")
            except Exception as e:
                logger.error(f"Failed to initialize GCS client: {e}")
                self.bucket_name = None
        else:
            logger.info("No GCS bucket configured. Using local storage only.")

    def save_content(self, path: str, content: str) -> bool:
        """
        Save content to storage (GCS if configured).
        
        Args:
            path: Relative path (e.g. 'scrapers/example_com.py')
            content: String content to save
            
        Returns:
            bool: True if successful
        """
        # Always save locally as backup/cache
        try:
            local_path = self._get_local_path(path)
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            with open(local_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            logger.error(f"Failed to save locally to {path}: {e}")
            if not self.bucket: # If no bucket, this is a fatal error
                return False

        # Save to GCS if configured
        if self.bucket:
            try:
                blob = self.bucket.blob(path)
                blob.upload_from_string(content)
                logger.info(f"Saved to GCS: gs://{self.bucket_name}/{path}")
                return True
            except Exception as e:
                logger.error(f"Failed to save to GCS {path}: {e}")
                return False
        
        return True

    def read_content(self, path: str) -> Optional[str]:
        """
        Read content from storage. Tries GCS first, then local.
        
        Args:
            path: Relative path
            
        Returns:
            str: Content or None if not found
        """
        # Try GCS first if configured
        if self.bucket:
            try:
                blob = self.bucket.blob(path)
                if blob.exists():
                    content = blob.download_as_text()
                    # Update local cache
                    self._save_local_cache(path, content)
                    return content
            except Exception as e:
                logger.warning(f"Failed to read from GCS {path}: {e}")
        
        # Fallback to local
        try:
            local_path = self._get_local_path(path)
            if os.path.exists(local_path):
                with open(local_path, 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception as e:
            logger.error(f"Failed to read local file {path}: {e}")
            
        return None

    def exists(self, path: str) -> bool:
        """Check if file exists."""
        if self.bucket:
            try:
                blob = self.bucket.blob(path)
                return blob.exists()
            except:
                pass
        
        return os.path.exists(self._get_local_path(path))

    def list_files(self, prefix: str) -> List[str]:
        """List files with prefix."""
        files = set()
        
        # List GCS
        if self.bucket:
            try:
                blobs = self.client.list_blobs(self.bucket_name, prefix=prefix)
                for blob in blobs:
                    files.add(blob.name)
            except Exception as e:
                logger.error(f"Failed to list GCS files: {e}")

        # List local
        local_dir = self._get_local_path(prefix)
        # Handle case where prefix includes part of filename
        dir_path = os.path.dirname(local_dir)
        if os.path.exists(dir_path):
            for root, _, filenames in os.walk(dir_path):
                for filename in filenames:
                    # Reconstruct relative path
                    abs_path = os.path.join(root, filename)
                    rel_path = self._get_relative_path(abs_path)
                    if rel_path.startswith(prefix):
                        files.add(rel_path)
                        
        return list(files)

    def _get_local_path(self, path: str) -> str:
        """Convert relative path to absolute local path in scraper_repository."""
        repo_root = os.path.join(os.path.dirname(os.path.dirname(__file__)), "scraper_repository")
        return os.path.join(repo_root, path)

    def _get_relative_path(self, abs_path: str) -> str:
        """Convert absolute local path to relative path."""
        repo_root = os.path.join(os.path.dirname(os.path.dirname(__file__)), "scraper_repository")
        return os.path.relpath(abs_path, repo_root).replace('\\', '/')

    def _save_local_cache(self, path: str, content: str):
        """Helper to save downloaded content to local cache."""
        try:
            local_path = self._get_local_path(path)
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            with open(local_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            logger.warning(f"Failed to update local cache for {path}: {e}")

# Global instance
storage = StorageManager()
