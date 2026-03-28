import sqlite3, json
conn = sqlite3.connect("db.sqlite3.backup")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
tables = [r[0] for r in cursor.fetchall()]
backup = {}
for t in tables:
    cursor.execute('SELECT * FROM "'+t+'"')
    rows = [dict(r) for r in cursor.fetchall()]
    if rows:
        backup[t] = rows
with open("data_backup.json","w") as f:
    json.dump(backup, f, ensure_ascii=False, indent=2, default=str)
conn.close()
print("Exported %d tables" % len(backup))
