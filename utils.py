import sqlite3
import os

DB_PATH = os.getenv("DB_PATH", "database.db")

# Fetch today's birthdays
def get_todays_birthdays(today):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, username FROM birthdays WHERE birthday = ?", (today,))
        return cursor.fetchall()

# Add or update a birthday
def add_or_update_birthday(user_id, username, birthday):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO birthdays (user_id, username, birthday)
            VALUES (?, ?, ?)
        """, (user_id, username, birthday))
        conn.commit()

# Remove a birthday
def remove_birthday(user_id):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM birthdays WHERE user_id = ?", (user_id,))
        conn.commit()

# Fetch and set notification channel
def get_notification_channel(guild_id):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT notification_channel FROM settings WHERE guild_id = ?", (guild_id,))
        result = cursor.fetchone()
        return result[0] if result else None

def set_notification_channel(guild_id, channel_id):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO settings (guild_id, notification_channel)
            VALUES (?, ?)
        """, (guild_id, channel_id))
        conn.commit()
