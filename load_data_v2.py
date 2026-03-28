import json
from decouple import config
import pymysql

with open("data_backup.json","r") as f:
    backup = json.load(f)

conn = pymysql.connect(
    host=config("DB_HOST"),
    user=config("DB_USER"),
    password=config("DB_PASSWORD"),
    database=config("DB_NAME"),
    charset="utf8mb4"
)
cursor = conn.cursor()

# Disable foreign key checks so insert order doesn't matter
cursor.execute("SET FOREIGN_KEY_CHECKS=0")

skip_tables = ["django_migrations", "django_content_type", "auth_permission"]

# Tables that already have data - skip them
already_loaded = [
    "auth_group", "auth_user", "Customers", "Category",
    "django_session", "Organizations", "DeliveryNotes",
    "EmployeePermissions", "SystemSettings", "ModelSettings",
    "FieldSettings", "Product", "Sales"
]

for table, rows in backup.items():
    if table in skip_tables:
        continue
    if table in already_loaded:
        print("Already loaded %s, skipping" % table)
        continue
    if not rows:
        continue
    cols = list(rows[0].keys())
    placeholders = ",".join(["%s"] * len(cols))
    col_names = ",".join(["`"+c+"`" for c in cols])
    sql = "INSERT INTO `%s` (%s) VALUES (%s)" % (table, col_names, placeholders)
    count = 0
    for row in rows:
        vals = [row.get(c) for c in cols]
        try:
            cursor.execute(sql, vals)
            count += 1
        except Exception as e:
            print("  Skip %s row: %s" % (table, str(e)[:80]))
    print("Loaded %s: %d/%d rows" % (table, count, len(rows)))

cursor.execute("SET FOREIGN_KEY_CHECKS=1")
conn.commit()
conn.close()
print("Done!")
