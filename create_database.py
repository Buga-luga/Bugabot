import sqlite3
import os

DB_PATH = os.getenv("DB_PATH", "database.db")

def create_and_populate_database():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS birthdays (
                user_id TEXT PRIMARY KEY,
                username TEXT NOT NULL,
                birthday TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                guild_id TEXT PRIMARY KEY,
                notification_channel TEXT
            )
        """)
        conn.commit()
        print("Database created!")

if __name__ == "__main__":
    create_and_populate_database()
