import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import psycopg2
from psycopg2.extras import DictCursor
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
print("Environment variables loaded")
print("Available environment variables:", [key for key in os.environ.keys()])

if not TOKEN:
    raise ValueError("No Discord token found. Please set the DISCORD_TOKEN environment variable.")

# Database Setup
DATABASE_URL = os.getenv('DATABASE_URL')
print("Attempting to get DATABASE_URL...")
print("DATABASE_URL value:", DATABASE_URL)

if not DATABASE_URL:
    raise ValueError("No database URL found. Please set the DATABASE_URL environment variable.")

def get_db():
    return psycopg2.connect(DATABASE_URL)

# Discord Bot Setup
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True  # Need this for slash commands
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# Database Setup
def setup_database():
    try:
        with get_db() as conn:
            with conn.cursor() as cursor:
                print("Creating database tables...")
                # Create birthdays table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS birthdays (
                        user_id TEXT PRIMARY KEY,
                        username TEXT NOT NULL,
                        birthday TEXT NOT NULL
                    )
                """)
                conn.commit()
                print("Tables created successfully")
        print("Database setup complete!")
    except Exception as e:
        print(f"Database setup error: {e}")
        raise

@tree.command(name="init_default_birthdays", description="[Admin Only] Initialize the birthday list.")
async def init_default_birthdays(interaction: discord.Interaction):
    # Check if user is admin
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You need administrator permissions to use this command!", ephemeral=True)
        return

    try:
        with get_db() as conn:
            with conn.cursor() as cursor:
                # First, clear the existing data
                cursor.execute("DELETE FROM birthdays")
                
                # Insert actual birthdays from the existing database
                default_birthdays = [
                    ("mrdanyoo", "Siiiickyooo 😷", "01-13"),
                    ("drenilin", "DR3N1", "01-27"),
                    ("ayysori", "Sori", "01-27"),
                    ("roguekilljoy", "Capo bae 4 lyfe M.Ed", "02-10"),
                    ("purepassion1992", "Willy Branch", "02-15"),
                    ("reyomustdie", "reyomustdie", "04-08"),
                    ("now_the_larch", "The Larch", "04-21"),
                    ("smolgrimbeam", "Smolnami Kento", "05-26"),
                    ("detrotsid", "Kevon", "06-21"),
                    ("coolbluekid", "kenny", "07-07"),
                    ("capo2dgod", "Cap", "07-16"),
                    ("strife_sf", "STRIFE", "08-08"),
                    ("gerald574", "LTGerald", "08-10"),
                    ("digitalbathx", "tosto sando", "08-27"),
                    ("nafenn", "I've Been a Nathy Girl", "09-02"),
                    ("bugalati", "Buga King Jr.", "09-10"),
                    ("livingonappixel", "Vintage Virgo", "09-10"),
                    ("antd19", "Andork", "09-19"),
                    ("gamer5501", "Sparking! Hector", "11-08"),
                    ("mellennium", "mel.⋆☽♡⋆", "11-12"),
                    ("e_entertainment", "e", "11-14"),
                    ("alexdagreatest", "alexthegr8", "11-17"),
                    ("nyahah", "ShirohAhAh", "12-12"),
                    ("taconips", "Miguel G", "12-11"),
                    (".teeny.tiny", "teeny tiny ♡", "12-19"),
                    ("elionardo.", "Elio", "12-20"),
                    (".10thmuse", "¡MUSA!", "12-24")
                ]
                
                for user_id, username, birthday in default_birthdays:
                    cursor.execute("""
                        INSERT INTO birthdays (user_id, username, birthday)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (user_id) DO NOTHING
                    """, (user_id, username, birthday))
                
                conn.commit()
                await interaction.response.send_message("Hi, I'm Bugabot! We have your list of birfs!")
                
                # Verify the insertions
                cursor.execute("SELECT username, birthday FROM birthdays ORDER BY birthday")
                results = cursor.fetchall()
                
                if results:
                    birthday_list = ["**Current birfdays in database:**"]
                    for username, birthday in results:
                        month, day = birthday.split('-')
                        date = datetime.strptime(birthday, '%m-%d').strftime('%B %d')
                        birthday_list.append(f"• **{username}**: {date}")
                    
                    await interaction.followup.send('\n'.join(birthday_list))
                
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        await interaction.response.send_message("There was an error initializing the birthdays. Please try again later.", ephemeral=True)

@tree.command(name="list_birthdays", description="Show all birthdays.")
async def list_birthdays(interaction: discord.Interaction):
    try:
        with get_db() as conn:
            with conn.cursor() as cursor:
                print("Fetching birthday list...")
                cursor.execute("SELECT username, birthday FROM birthdays ORDER BY birthday")
                birthdays = cursor.fetchall()
                print(f"Found {len(birthdays)} birthdays in database")

                if not birthdays:
                    await interaction.response.send_message("No birthdays have been added yet!", ephemeral=True)
                    return

                # Create a formatted list of birthdays
                birthday_list = ["**📅 Birfday List:**"]
                for username, birthday in birthdays:
                    month, day = birthday.split('-')
                    date = datetime.strptime(birthday, '%m-%d').strftime('%B %d')
                    birthday_list.append(f"• **{username}**: {date}")

                await interaction.response.send_message('\n'.join(birthday_list))
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        await interaction.response.send_message("There was an error accessing the database. Please try again later.", ephemeral=True)

@tree.command(name="add_birthday", description="Add a birthday for a user (MM/DD format)")
async def add_birthday(interaction: discord.Interaction, user: discord.User, birthday: str):
    # Check if user is admin
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You need administrator permissions to use this command!", ephemeral=True)
        return

    try:
        # Split the date and validate format
        parts = birthday.split('/')
        if len(parts) != 2:
            await interaction.response.send_message("Invalid date format! Use MM/DD (e.g., 01/31).", ephemeral=True)
            return

        month, day = parts
        # Ensure both parts are numbers and proper length
        if not (month.isdigit() and day.isdigit()):
            await interaction.response.send_message("Month and day must be numbers! Use MM/DD (e.g., 01/31).", ephemeral=True)
            return

        month_int = int(month)
        day_int = int(day)
        
        # Basic date validation
        if month_int < 1 or month_int > 12:
            await interaction.response.send_message("Invalid month! Month must be between 01 and 12.", ephemeral=True)
            return
        
        # Check days per month
        days_in_month = {
            1: 31, 2: 29, 3: 31, 4: 30, 5: 31, 6: 30,
            7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31
        }
        if day_int < 1 or day_int > days_in_month[month_int]:
            await interaction.response.send_message(f"Invalid day for month {month_int}!", ephemeral=True)
            return
            
        # Convert to MM-DD format for database
        birthday_db = f"{month_int:02d}-{day_int:02d}"
        
        with get_db() as conn:
            with conn.cursor() as cursor:
                # Add the new birthday
                cursor.execute("""
                    INSERT INTO birthdays (user_id, username, birthday)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (user_id) 
                    DO UPDATE SET username = EXCLUDED.username, birthday = EXCLUDED.birthday
                """, (str(user.id), str(user.name), birthday_db))
                
                conn.commit()
                await interaction.response.send_message(f"Added birthday for {user.mention}: {month_int:02d}/{day_int:02d}")
                
                # Show updated birthday list
                cursor.execute("SELECT username, birthday FROM birthdays ORDER BY birthday")
                results = cursor.fetchall()
                
                if results:
                    birthday_list = ["**📅 Updated Birfday List:**"]
                    for username, bday in results:
                        m, d = bday.split('-')
                        date = datetime.strptime(bday, '%m-%d').strftime('%B %d')
                        birthday_list.append(f"• **{username}**: {date}")
                    
                    await interaction.followup.send('\n'.join(birthday_list))
                
    except Exception as e:
        print(f"Error adding birthday: {e}")
        await interaction.response.send_message("There was an error saving the birthday. Please try again later.", ephemeral=True)

# Bot Startup
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    print(f"Bot ID: {bot.user.id}")
    print("Connected to servers:")
    for guild in bot.guilds:
        print(f"- {guild.name} (ID: {guild.id})")
    
    setup_database()
    try:
        print("Attempting to sync commands...")
        synced = await tree.sync()
        print(f"Successfully synced {len(synced)} command(s)!")
        print("Available commands:")
        for command in synced:
            print(f"- /{command.name}: {command.description}")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

async def main():
    print("Starting bot...")
    async with bot:
        await bot.start(TOKEN)

if __name__ == "__main__":
    print("Initializing Bugabot...")
    asyncio.run(main())
