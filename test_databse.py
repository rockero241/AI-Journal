import sqlite3

conn = sqlite3.connect('journal.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM entries")
rows = cursor.fetchall()
for row in rows:
    print(row)
conn.close()
