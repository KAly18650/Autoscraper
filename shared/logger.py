"""
Centralized logging configuration for Google Cloud Logging.
"""
import logging
import os
import sys

# Default to standard logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger configured for Google Cloud Logging if available.
    
    Args:
        name: The name of the logger (usually __name__)
        
    Returns:
        logging.Logger: Configured logger
    """
    logger = logging.getLogger(name)
    
    # Check if we are already set up or if we should try to setup Cloud Logging
    # We use a flag to avoid trying to setup Cloud Logging multiple times
    if getattr(get_logger, '_cloud_logging_setup', False):
        return logger

    try:
        # Only attempt to setup Cloud Logging if we have credentials
        # This prevents errors during local dev if not authenticated
        if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") or os.environ.get("GCP_PROJECT_ID"):
            from google.cloud import logging as cloud_logging
            
            client = cloud_logging.Client()
            client.setup_logging()
            get_logger._cloud_logging_setup = True
            logger.info("Google Cloud Logging enabled")
    except Exception as e:
        # Fallback to standard logging (already configured in basicConfig)
        logger.warning(f"Failed to initialize Google Cloud Logging: {e}. Using standard logging.")
        get_logger._cloud_logging_setup = True # Don't try again
        
    return logger
