import sqlite3

for db_name in ['users.db', 'database.db']:
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"\n--- {db_name} ---")
        for t in tables:
            print(f"Table: {t[0]}\nSQL: {t[1]}\n")
            # Fetch some rows if it's users
            if t[0] == 'users':
                cursor.execute(f"SELECT * FROM {t[0]} LIMIT 2;")
                rows = cursor.fetchall()
                print(f"Sample rows: {rows}\n")
        conn.close()
    except Exception as e:
        print(f"Error reading {db_name}: {e}")
