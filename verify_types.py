
import os
import sys
from supabase_client import get_supabase

# Force output encoding
try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

try:
    client = get_supabase()
    if client:
        print("✅ Client initialized.")
        print(f"URL: {client.url}")
        # Try to fetch 1 record from history to verify connection
        # The select method in supabase_client.py returns a list or empty list
        res = client.table("history").select(columns="count", eq_field=None, eq_value=None)
        # Note: The current select implementation in supabase_client.py might not support count easily or simple valid query without args
        # But let's try a simple listing.
        
        # Actually, let's just check if we can make a request.
        # We'll try to get 1 item.
        res = client.table("history").select()
        if isinstance(res, list):
            print("✅ Connection verified (Table 'history' access successful).")
        else:
            print(f"⚠️ Connection might have issues. Response type: {type(res)}")
    else:
        print("❌ Failed to initialize Supabase client (Missing URL/Key).")

except Exception as e:
    print(f"❌ Error verifying Supabase: {e}")
