import sqlite3

conn = sqlite3.connect("Database/GalletasDeliDB.db")
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(Lotes)")
columns = cursor.fetchall()
for column in columns:
    print(column)

conn.close()
