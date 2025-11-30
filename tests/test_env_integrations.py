"""Utility script to verify .env secrets for logging and storage integrations."""

import json
import os
from datetime import datetime
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional dependency
    load_dotenv = None


def _seed_env_from_file() -> bool:
    """Load .env values even if python-dotenv is unavailable."""
    env_path = Path(__file__).resolve().parent / ".env"
    if not env_path.exists():
        return False

    if load_dotenv:
        return bool(load_dotenv(dotenv_path=env_path))

    # Manual parser fallback - values in .env OVERRIDE existing env vars
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ[key] = value
    return True


DOTENV_USED = _seed_env_from_file()

# Normalize common alias names so the rest of the project can rely on them
project_id = os.environ.get("GCP_PROJECT_ID") or os.environ.get("GOOGLE_CLOUD_PROJECT") or os.environ.get("PROJECT_ID")
bucket_name = os.environ.get("GCS_BUCKET_NAME") or os.environ.get("GOOGLE_CLOUD_STORAGE_BUCKET") or os.environ.get("BUCKET_NAME")

if project_id and not os.environ.get("GOOGLE_CLOUD_PROJECT"):
    os.environ["GOOGLE_CLOUD_PROJECT"] = project_id

if project_id and not os.environ.get("GCP_PROJECT_ID"):
    os.environ["GCP_PROJECT_ID"] = project_id

if bucket_name and not os.environ.get("GCS_BUCKET_NAME"):
    os.environ["GCS_BUCKET_NAME"] = bucket_name

from shared.config import get_api_key, get_gcs_bucket_name
from shared.logger import get_logger
from shared.storage import storage

logger = get_logger("env-healthcheck")


def check_api_key():
    """Ensure Gemini/Gemini API key can be loaded."""
    try:
        api_key = get_api_key(silent=True)
        return bool(api_key), "Loaded API key"
    except SystemExit:
        return False, "API key missing or unreadable"
    except Exception as exc:  # pragma: no cover - defensive
        return False, f"API key error: {exc}"


def check_logging():
    """Emit a test log entry (verify in Cloud Logging)."""
    message = f"Env health check log at {datetime.utcnow().isoformat()}"
    logger.info(message)
    return True, message


def check_storage():
    """Write + read a file via the storage abstraction."""
    bucket = get_gcs_bucket_name()
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    test_rel_path = f"healthchecks/env_test_{timestamp}.txt"
    payload = json.dumps({
        "timestamp": timestamp,
        "bucket": bucket,
        "note": "If storage is configured, this file should exist in the bucket."
    }, indent=2)

    save_ok = storage.save_content(test_rel_path, payload)
    read_back = storage.read_content(test_rel_path)
    return save_ok and bool(read_back), {
        "bucket": bucket or "(not configured)",
        "path": test_rel_path,
        "local_cache_exists": read_back is not None
    }


def main():
    results = {
        "dotenv_used": DOTENV_USED,
        "env_vars": {
            "GEMINI_API_KEY": bool(os.environ.get("GEMINI_API_KEY")),
            "GOOGLE_APPLICATION_CREDENTIALS": os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"),
            "GCS_BUCKET_NAME": os.environ.get("GCS_BUCKET_NAME"),
            "GCP_PROJECT_ID": os.environ.get("GCP_PROJECT_ID")
        }
    }

    ok_api, api_msg = check_api_key()
    ok_log, log_msg = check_logging()
    ok_storage, storage_details = check_storage()

    results["api_key"] = {"ok": ok_api, "message": api_msg}
    results["logging"] = {"ok": ok_log, "message": log_msg}
    results["storage"] = {"ok": ok_storage, "details": storage_details}

    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
