import sqlite3
import os
import datetime
from supabase_client import get_supabase
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def migrate_users():
    client = get_supabase()
    if not client:
        print("❌ Supabase URL or KEY is missing from .env")
        return

    print(f"📡 Connecting to Supabase REST: {client.url}")
    
    users_to_migrate = []

    # 1. Read users from instance/users.db (the definitive new format)
    if os.path.exists('instance/users.db'):
        try:
            print("📖 Reading instance/users.db...")
            conn = sqlite3.connect('instance/users.db')
            # Get column names dynamically
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user")
            rows = cursor.fetchall()
            for r in rows:
                user_dict = dict(r)
                users_to_migrate.append(user_dict)
            conn.close()
        except Exception as e:
            print(f"⚠️ Error reading instance/users.db: {e}")

    # 2. Read users from database.db (the older format)
    if os.path.exists('database.db'):
        try:
            print("📖 Reading database.db...")
            conn = sqlite3.connect('database.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users")
            rows = cursor.fetchall()
            for r in rows:
                # Need to map old structure to new structure if columns are different
                # old: id, email, password, data_validade, is_admin
                user_dict = dict(r)
                
                # Check if this email is already loaded from instance/users.db
                if any(u['email'] == user_dict['email'] for u in users_to_migrate):
                    continue
                    
                mapped_user = {
                    'email': user_dict['email'],
                    'password_hash': user_dict.get('password', ''),
                    'role': 'admin' if user_dict.get('is_admin', 0) == 1 else 'user',
                    'subscription_end': user_dict.get('data_validade', None)
                }
                users_to_migrate.append(mapped_user)
            conn.close()
        except Exception as e:
            print(f"⚠️ Error reading database.db: {e}")

    print(f"\n🚀 Starting migration of {len(users_to_migrate)} users to Supabase REST...")
    success_count = 0
    
    for u in users_to_migrate:
        email = u.get('email')
        
        # Clean up data types for JSON
        payload = {
            'email': email,
            'password_hash': u.get('password_hash', ''),
            'role': u.get('role', 'user'),
            'subscription_end': u.get('subscription_end', None),
            'reset_code': u.get('reset_code', None)
        }
        
        res = client.table("user").upsert(payload, on_conflict="email")
        if res and res.status_code < 300:
            print(f"✅ Migrated: {email}")
            success_count += 1
        else:
            print(f"❌ Failed to migrate {email}. Response: {res.text if res else 'None'}")
            # Try to create the table if it looks like it doesn't exist
            if res and res.status_code == 404:
                print("⚠️ Table 'user' likely does not exist in Supabase REST endpoint.")
                break

    print(f"\n🎉 Migration Complete: {success_count} / {len(users_to_migrate)} users synchronized via REST.")

if __name__ == "__main__":
    migrate_users()
