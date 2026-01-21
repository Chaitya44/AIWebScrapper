import sqlite3

# Connect to your database file
conn = sqlite3.connect('scraped_data.db')
cursor = conn.cursor()

# Grab all the data
try:
    cursor.execute("SELECT * FROM books")
    rows = cursor.fetchall()

    print(f"--- DATABASE CONTENTS ({len(rows)} items) ---")
    for row in rows:
        print(row)
except Exception as e:
    print(f"Error reading database: {e}")

conn.close()