import sqlite3
conn = sqlite3.connect('data/pro_punter.db')
c = conn.cursor()
c.execute("SELECT COUNT(*) FROM matches")
print(f"Matches: {c.fetchone()[0]}")
c.execute("SELECT league, COUNT(*) as cnt FROM matches GROUP BY league ORDER BY cnt DESC")
for row in c.fetchall():
    print(f"  {row[0]}: {row[1]}")
conn.close()
