import sqlite3
import json
import datetime


def save_dynamic_data(url, category, json_data):
    """
    Saves ANY kind of data structure to the database.
    """
    try:
        conn = sqlite3.connect('universal_scraper.db')
        cursor = conn.cursor()

        # We use a flexible table structure
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scrapes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT,
                scrape_date TEXT,
                category TEXT,
                raw_data TEXT
            )
        ''')

        # Add timestamp
        date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute('''
            INSERT INTO scrapes (url, scrape_date, category, raw_data)
            VALUES (?, ?, ?, ?)
        ''', (url, date_str, category, json_data))

        conn.commit()
        conn.close()
        print(f"✅ Saved {category} data to DB!")

    except Exception as e:
        print(f"❌ Database Error: {e}")