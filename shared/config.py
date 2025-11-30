"""
Configuration and API key management.
"""

import os
from pathlib import Path

def get_api_key(silent=False):
    """
    Load API key from environment variable or .env file.
    
    Args:
        silent: If True, suppress print statements
    
    Returns:
        str: The API key
        
    Raises:
        SystemExit: If API key cannot be found
    """
    api_key = ""
    
    # Try environment variable first
    try:
        key_path = Path(os.environ["GEMINI_API_KEY_FILE"])
        with key_path.open("r", encoding="utf-8") as fh:
            api_key = fh.read().strip()
        if not silent:
            print(f"✓ Loaded API key from: {key_path}")
        
    except KeyError:
        print("⚠️  GEMINI_API_KEY_FILE environment variable not set.")
        print("   Trying to load from parent directory .env file...")
        
        # Try .env file
        try:
            from dotenv import load_dotenv
            script_dir = Path(__file__).resolve().parent.parent
            dotenv_path = script_dir.parent / ".env"
            load_dotenv(dotenv_path=dotenv_path)
            
            if "GEMINI_API_KEY_FILE" in os.environ:
                key_path = Path(os.environ["GEMINI_API_KEY_FILE"])
                with key_path.open("r", encoding="utf-8") as fh:
                    api_key = fh.read().strip()
                if not silent:
                    print(f"✓ Loaded API key from .env: {key_path}")
            else:
                print("❌ GEMINI_API_KEY_FILE not found in .env file either.")
                print("\nPlease either:")
                print("1. Set environment variable: $env:GEMINI_API_KEY_FILE = 'path/to/key.txt'")
                print("2. Create a .env file in parent directory with: GEMINI_API_KEY_FILE=path/to/key.txt")
                exit(1)
                
        except ImportError:
            print("❌ python-dotenv not installed. Install with: pip install python-dotenv")
            print("\nOr set environment variable: $env:GEMINI_API_KEY_FILE = 'path/to/key.txt'")
            exit(1)
            
    except FileNotFoundError:
        print(f"❌ API key file not found: {key_path}")
        exit(1)
    
    # Set environment variables
    os.environ["GOOGLE_API_KEY"] = api_key
    os.environ["GEMINI_API_KEY"] = api_key
    
    return api_key


def get_gcs_bucket_name():
    """
    Get the GCS bucket name from environment variables.
    """
    return os.environ.get("GCS_BUCKET_NAME")


# Note: get_client() removed - ADK manages client creation internally
# Just ensure API key is in environment variables
