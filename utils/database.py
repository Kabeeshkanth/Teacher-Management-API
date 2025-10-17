import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

# Check if the environment variables are set
if not url or not key:
    raise EnvironmentError("Supabase URL and Key must be set in your .env file.")

# Initialize the Supabase client
supabase: Client = create_client(url, key)

print("Supabase client initialized successfully.")