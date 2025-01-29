import discord
from discord.ext import commands
from discord import app_commands
import ssl
import aiohttp
import sqlite3
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Database setup
DB_PATH = "database.db"

def setup_database():
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

# SSL Bypass for Replit
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE
connector = aiohttp.TCPConnector(ssl=ssl_context)

# Define the bot
intents = discord.Intents.default()
intents.messages = True
bot = commands.Bot(command_prefix="!", intents=intents, connector=connector)
tree = bot.tree

# Command: Add Birthday
@tree.command(name="add_birthday", description="Add or update your birthday in MM-DD format.")
async def add_birthday(interaction: discord.Interaction, birthday: str):
    if not birthday or len(birthday) != 5 or birthday[2] != "-" or not birthday.replace("-", "").isdigit():
        await interaction.response.send_message("Invalid date format! Use MM-DD.", ephemeral=True)
        return

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO birthdays (user_id, username, birthday)
            VALUES (?, ?, ?)
        """, (str(interaction.user.id), str(interaction.user.name), birthday))
        conn.commit()

    await interaction.response.send_message(f"Your birthday has been set to {birthday}, {interaction.user.mention}!")

# Command: Remove Birthday
@tree.command(name="remove_birthday", description="Remove your birthday from the database.")
async def remove_birthday(interaction: discord.Interaction):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM birthdays WHERE user_id = ?", (str(interaction.user.id),))
        conn.commit()

    await interaction.response.send_message(f"Your birthday has been removed, {interaction.user.mention}!")

# Command: List Birthdays (Admin Only)
@tree.command(name="list_birthdays", description="List all upcoming birthdays. (Admins only)")
async def list_birthdays(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        return

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username, birthday FROM birthdays ORDER BY birthday")
        rows = cursor.fetchall()

    if not rows:
        await interaction.response.send_message("No birthdays found!", ephemeral=True)
    else:
        birthday_list = "\n".join([f"{username}: {birthday}" for username, birthday in rows])
        await interaction.response.send_message(f"**Upcoming Birthdays:**\n{birthday_list}")

# Command: Set Notification Channel (Admin Only)
@tree.command(name="set_notification_channel", description="Set the channel for birthday notifications. (Admins only)")
async def set_notification_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        return

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO settings (guild_id, notification_channel)
            VALUES (?, ?)
        """, (str(interaction.guild_id), str(channel.id)))
        conn.commit()

    await interaction.response.send_message(f"Birthday notifications will be sent in {channel.mention}.")

# Check Birthdays (Daily)
async def check_birthdays():
    today = datetime.now().strftime('%m-%d')
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT b.user_id, b.username, s.notification_channel
            FROM birthdays b
            JOIN settings s ON s.guild_id = b.user_id
            WHERE b.birthday = ?
        """, (today,))
        results = cursor.fetchall()

    for user_id, username, channel_id in results:
        channel = bot.get_channel(int(channel_id))
        if channel:
            await channel.send(f"🎉 Happy Birthday, <@{user_id}>! 🎂 Have an amazing day!")

# Bot Events
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    setup_database()

    # Sync slash commands
    try:
        synced = await tree.sync()
        print(f"Synced {len(synced)} command(s).")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

bot.run(TOKEN)
