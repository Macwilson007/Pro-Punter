import sqlite3
import os

db_path = 'data/punter.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM predictions ORDER BY created_at DESC LIMIT 5")
    rows = cursor.fetchall()
    for row in rows:
        print(dict(row))
    conn.close()
else:
    print(f"DB not found at {db_path}")
