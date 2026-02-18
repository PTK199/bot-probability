import sqlite3
import datetime
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = 'database.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def create_user(email, password, days=7, is_admin=0):
    conn = get_db_connection()
    hashed_password = generate_password_hash(password)
    validity = datetime.datetime.now() + datetime.timedelta(days=days)
    try:
        conn.execute('INSERT INTO users (email, password, data_validade, is_admin) VALUES (?, ?, ?, ?)',
                     (email, hashed_password, validity, is_admin))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def authenticate_user(email, password):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    conn.close()
    
    if user and check_password_hash(user['password'], password):
        return dict(user)
    return None

def check_validity(email):
    conn = get_db_connection()
    user = conn.execute('SELECT data_validade FROM users WHERE email = ?', (email,)).fetchone()
    conn.close()
    
    if user:
        val_str = user['data_validade']
        try:
            if "." in val_str:
                expiry = datetime.datetime.strptime(val_str, '%Y-%m-%d %H:%M:%S.%f')
            else:
                expiry = datetime.datetime.strptime(val_str, '%Y-%m-%d %H:%M:%S')
            return expiry > datetime.datetime.now()
        except:
            return False
    return False

def extend_subscription(email, days=7):
    conn = get_db_connection()
    user = conn.execute('SELECT data_validade FROM users WHERE email = ?', (email,)).fetchone()
    
    if user:
        val_str = user['data_validade']
        try:
            if "." in val_str:
                current_expiry = datetime.datetime.strptime(val_str, '%Y-%m-%d %H:%M:%S.%f')
            else:
                current_expiry = datetime.datetime.strptime(val_str, '%Y-%m-%d %H:%M:%S')
        except:
            current_expiry = datetime.datetime.now()
            
        start_date = max(current_expiry, datetime.datetime.now())
        new_expiry = start_date + datetime.timedelta(days=days)
        
        conn.execute('UPDATE users SET data_validade = ? WHERE email = ?', (new_expiry, email))
        conn.commit()
    conn.close()
