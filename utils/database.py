# python
import os
import logging
from typing import Optional
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables from .env file (if present)
load_dotenv()


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SUPABASE_URL: Optional[str] = os.getenv("SUPABASE_URL")
SUPABASE_KEY: Optional[str] = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise EnvironmentError(
        "Supabase URL and Key must be set in your .env file (SUPABASE_URL, SUPABASE_KEY)."
    )

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    logger.info("Supabase client initialized successfully.")
except Exception as exc:
    logger.exception("Failed to initialize Supabase client.")
    raise EnvironmentError("Failed to initialize Supabase client.") from exc


def get_supabase_client() -> Client:

    return supabase


__all__ = ["supabase", "get_supabase_client"]
