from supabase import Client, create_client
from dotenv import load_dotenv
import os
load_dotenv()

supabase_key=os.environ.get("SUPABASE_KEY")
supabase_url=os.environ.get("SUPABASE_URL")

supabase:Client =create_client(supabase_url,supabase_key)
