import os
import sys
import io
import sqlite3
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime, Float
from sqlalchemy.orm import declarative_base, sessionmaker

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Supabase URL directly or from .env
db_url = os.environ.get('SUPABASE_DB_URL')
if not db_url:
    print("❌ SUPABASE_DB_URL missing in .env")
    exit(1)

# Fix postgres:// to postgresql:// if needed
if db_url.startswith('postgres://'):
    db_url = db_url.replace('postgres://', 'postgresql://', 1)

print(f"📡 Connecting to Supabase PostgreSQL...")
engine = create_engine(db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define the exact SQLAlchemy Models expected by payment_system.py
class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(256))
    subscription_end = Column(DateTime, nullable=True)
    role = Column(String(20), default='user')
    reset_code = Column(String(10), nullable=True)

class Payment(Base):
    __tablename__ = 'payment'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False) 
    mp_payment_id = Column(String(50), unique=True)
    status = Column(String(20))
    amount = Column(Float)
    created_at = Column(DateTime)

# Create tables in Supabase
print("🔨 Creating tables in Supabase if they don't exist...")
Base.metadata.create_all(bind=engine)

def migrate_users():
    session = SessionLocal()
    users_to_add = {} # dict by email to avoid duplicates

    # 1. Read users from instance/users.db (the definitive new format)
    if os.path.exists('instance/users.db'):
        try:
            print("📖 Reading instance/users.db...")
            conn = sqlite3.connect('instance/users.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user")
            rows = cursor.fetchall()
            for r in rows:
                u = dict(r)
                # Parse datetime string from sqlite
                sub_end = None
                if u.get('subscription_end'):
                    try:
                        from datetime import datetime
                        sub_end = datetime.strptime(u['subscription_end'].split('.')[0], "%Y-%m-%d %H:%M:%S")
                    except:
                        pass
                
                users_to_add[u['email']] = {
                    'email': u['email'],
                    'password_hash': u.get('password_hash'),
                    'subscription_end': sub_end,
                    'role': u.get('role', 'user'),
                    'reset_code': u.get('reset_code')
                }
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
                u = dict(r)
                if u['email'] in users_to_add:
                    continue # Already loaded from instance
                
                sub_end = None
                if u.get('data_validade'):
                    try:
                        from datetime import datetime
                        sub_end = datetime.strptime(u['data_validade'].split('.')[0], "%Y-%m-%d %H:%M:%S")
                    except:
                        pass

                users_to_add[u['email']] = {
                    'email': u['email'],
                    'password_hash': u.get('password'),
                    'role': 'admin' if u.get('is_admin') == 1 else 'user',
                    'subscription_end': sub_end,
                    'reset_code': None
                }
            conn.close()
        except Exception as e:
            print(f"⚠️ Error reading database.db: {e}")

    print(f"\n🚀 Inserting {len(users_to_add)} users to Supabase PostgreSQL...")
    success_count = 0
    
    for email, data in users_to_add.items():
        # Check if exists in Supabase
        existing = session.query(User).filter(User.email == email).first()
        if existing:
            print(f"⏭️ Skipping {email} (Already in Supabase)")
            continue
            
        new_user = User(
            email=data['email'],
            password_hash=data['password_hash'],
            subscription_end=data['subscription_end'],
            role=data['role'],
            reset_code=data['reset_code']
        )
        session.add(new_user)
        try:
            session.commit()
            print(f"✅ Migrated: {email}")
            success_count += 1
        except Exception as e:
            session.rollback()
            print(f"❌ Failed to migrate {email}: {e}")

    session.close()
    print(f"\n🎉 Migration Complete: {success_count} users successfully inserted into Supabase PostgreSQL.")

if __name__ == "__main__":
    migrate_users()
