import discord
from discord.ext import commands
from datetime import datetime
import pytz
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

import os
from dotenv import load_dotenv
load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.messages = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

last_wish_message_id = None
wish_timestamp = None

# Configuration - Map server IDs to role IDs
SHAME_ROLE_CONFIG = {
    168316445569056768: 1390320164024881192,  # London server: dunce role
    1390289538613772400: 1390319545243402370, # JJ's test server
    1343509963812769832: 1390424931388362874, # The Post Office
    # Add more servers as needed
}

# Configuration - Map server IDs to dev channel names
DEV_CHANNEL_CONFIG = {
    168316445569056768: "pkl-dev",        # London server
    1390289538613772400: "dr-shamer-dev",  # JJ's test server
    1343509963812769832: "dr-shamer-dev",  # The Post Office
    # Add more servers as needed
}

GIF_URL = "https://tenor.com/view/shame-septa-got-westeros-walk-of-atonement-gif-3828987465249036403"

def get_shame_role_id(guild_id):
    """Get the appropriate shame role ID for a server"""
    if guild_id not in SHAME_ROLE_CONFIG:
        print(f"❌ Guild ID {guild_id} not found in SHAME_ROLE_CONFIG")
        return None
    return SHAME_ROLE_CONFIG[guild_id]

def get_dev_channel_name(guild_id):
    """Get the appropriate dev channel name for a server"""
    return DEV_CHANNEL_CONFIG.get(guild_id, "pkl-dev")  # Default to pkl-dev

async def remove_shame_roles(guild):
    """Remove the dunce role from all users when a new wish is detected"""
    try:
        role_id = get_shame_role_id(guild.id)
        role = guild.get_role(role_id)
        if not role:
            print(f"❌ Role with ID {role_id} not found in {guild.name} (Guild ID: {guild.id})")
            return
        
        # Remove the role from all members who have it
        removed_count = 0
        for member in guild.members:
            if role in member.roles:
                try:
                    await member.remove_roles(role, reason="New wish detected - fresh start")
                    print(f"🧹 Removed '{role.name}' role from {member.name}")
                    removed_count += 1
                except Exception as e:
                    print(f"❌ Failed to remove role from {member.name}: {e}")
        
        if removed_count > 0:
            print(f"✨ Cleared dunce roles from {removed_count} users for new wish")
        else:
            print("✨ No users had dunce roles to remove")
    except Exception as e:
        print(f"❌ Error removing dunce roles: {e}")

async def assign_shame_role(guild, user):
    """Assign the 'dunce' role to a user"""
    try:
        role_id = get_shame_role_id(guild.id)
        role = guild.get_role(role_id)
        if not role:
            print(f"❌ Role with ID {role_id} not found in {guild.name} (Guild ID: {guild.id})")
            return
        
        # Add the role to the user
        await user.add_roles(role, reason="Failed to make a proper wish")
        print(f"🔴 Added '{role.name}' role to {user.name}")
    except Exception as e:
        print(f"❌ Error assigning role: {e}")

@bot.event
async def on_ready():
    print(f'✅ Dr. Shamer is online as {bot.user}')

@bot.event
async def on_message(message):
    global last_wish_message_id, wish_timestamp

    if message.author.bot:
        return

    london_time = datetime.now(pytz.timezone('Europe/London'))
    
    # Check if message is a wish format (various variations)
    message_lower = message.content.lower().strip()
    
    # Accept various wish message formats
    wish_variations = [
        "11:11 make a wish 🌠",
        "11:11 make a wish",
        "make a wish 🌠",
        "make a wish",
        "11:11 make wish 🌠",
        "11:11 make wish",
        "make wish 🌠",
        "make wish",
        "11:11 wish 🌠",
        "wish 🌠",
    ]
    
    if message_lower in wish_variations:
        # Allow anytime in dev channel, otherwise only at 11:11 AM
        is_dev_channel = message.channel.name == get_dev_channel_name(message.guild.id)
        is_correct_time = london_time.strftime('%H:%M') == "11:11"
        
        if is_dev_channel or is_correct_time:
            print(f"🎯 Detected wish message at {london_time.strftime('%H:%M')}: {message.id}")
            print(f"📝 Message: '{message.content}'")
            if is_dev_channel:
                print("📝 Dev channel - allowing wish at any time")
            
            # Remove shame roles from all users for fresh start
            await remove_shame_roles(message.guild)
            
            last_wish_message_id = message.id
            wish_timestamp = london_time
        else:
            print(f"⏰ Wish attempted at {london_time.strftime('%H:%M')} but not 11:11 - shaming user!")
            # Shame the user for making a wish at the wrong time
            await assign_shame_role(message.guild, message.author)
            await message.channel.send(f"😤 {message.author.mention} tried to start a wish at {london_time.strftime('%H:%M')} but wishes can only be made at 11:11 AM... OH! OH! BAD WISHES FOR {message.author.mention}! BAD WISHES FOR {message.author.mention} FOR SEVEN YEARS! 🔔🔔🔔\n\n{GIF_URL}")

    await bot.process_commands(message)

@bot.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return

    if reaction.message.id != last_wish_message_id or str(reaction.emoji) != "🌠":
        return

    # Check if the wish was made at 11:11 AM London time
    if wish_timestamp:
        # Convert wish_timestamp to London time (in case it was stored differently)
        wish_time_london = wish_timestamp.astimezone(pytz.timezone('Europe/London'))
        
        if wish_time_london.strftime('%H:%M') == "11:11":
            print(f"🌟 {user.name} made a wish on time at 11:11 AM!")
        else:
            print(f"😤 {user.name} tried to make a wish but it wasn't at 11:11 AM... shame!")
            await assign_shame_role(reaction.message.guild, user)
            await reaction.message.channel.send(f"😤 {user.mention} tried to make a wish but it wasn't at 11:11 AM... OH! OH! BAD WISHES FOR {user.mention}! BAD WISHES FOR {user.mention} FOR SEVEN YEARS! 🔔🔔🔔\n\n{GIF_URL}")



class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'OK')
    
    def log_message(self, format, *args):
        pass  # Suppress logs

def start_health_server():
    port = int(os.getenv('PORT', 8080))
    HTTPServer(('', port), HealthCheckHandler).serve_forever()

if __name__ == "__main__":
    # Start health check server in background thread
    health_thread = threading.Thread(target=start_health_server, daemon=True)
    health_thread.start()
    
    bot_token = os.getenv("DISCORD_BOT_TOKEN")
    bot.run(bot_token)
