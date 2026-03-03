import sqlite3

try:
    conn = sqlite3.connect('instance/users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("--- instance/users.db ---")
    for t in tables:
        print(f"Table: {t[0]}\nSQL: {t[1]}")
        if t[0] in ['user', 'payment', 'users']:
            cursor.execute(f"SELECT * FROM {t[0]};")
            rows = cursor.fetchall()
            print(f"Rows: {rows}\n")
    conn.close()
except Exception as e:
    print(e)
