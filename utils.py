import sqlite3

DB_PATH = "database.db"

# Fetch today's birthdays
def get_todays_birthdays(today):
    """
    Retrieve the list of user IDs and birthdays that match today's date.
    :param today: Current date in MM-DD format.
    :return: List of tuples [(user_id, username)]
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, username FROM birthdays WHERE birthday = ?", (today,))
        return cursor.fetchall()

# Add or update a birthday
def add_or_update_birthday(user_id, username, birthday):
    """
    Add a new birthday or update an existing one.
    :param user_id: Discord user ID.
    :param username: Discord username for reference.
    :param birthday: Birthday in MM-DD format.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO birthdays (user_id, username, birthday)
            VALUES (?, ?, ?)
        """, (user_id, username, birthday))
        conn.commit()

# Delete a birthday
def remove_birthday(user_id):
    """
    Remove a birthday entry by user ID.
    :param user_id: Discord user ID.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM birthdays WHERE user_id = ?", (user_id,))
        conn.commit()

# Fetch the notification channel for a guild
def get_notification_channel(guild_id):
    """
    Get the notification channel for a specific guild.
    :param guild_id: Discord server (guild) ID.
    :return: Channel ID as a string, or None if not set.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT notification_channel FROM settings WHERE guild_id = ?", (guild_id,))
        result = cursor.fetchone()
        return result[0] if result else None

# Set the notification channel for a guild
def set_notification_channel(guild_id, channel_id):
    """
    Set the notification channel for birthday messages.
    :param guild_id: Discord server (guild) ID.
    :param channel_id: Discord channel ID.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO settings (guild_id, notification_channel)
            VALUES (?, ?)
        """, (guild_id, channel_id))
        conn.commit()
