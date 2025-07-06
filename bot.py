import discord
from discord.ext import commands
from datetime import datetime
import pytz
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

import os
from dotenv import load_dotenv
# Only load .env in development - production uses environment variables directly
if os.path.exists('.env'):
    load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.messages = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Configuration - Wish time (24-hour format HH:MM)
WISH_TIME = "11:11"

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

# Configuration - Debug mode per server (True = show debug messages)
DEBUG_MODE_CONFIG = {
    168316445569056768: False,  # London server - no debug
    1390289538613772400: True,  # JJ's test server - debug on
    1343509963812769832: True,  # The Post Office - debug on
    # Add more servers as needed - default to True for new servers
}

GIF_URL = "https://tenor.com/view/shame-septa-got-westeros-walk-of-atonement-gif-3828987465249036403"

def get_shame_role_id(guild_id):
    """Get the appropriate shame role ID for a server"""
    if guild_id not in SHAME_ROLE_CONFIG:
        print(f"❌ Guild ID {guild_id} not found in SHAME_ROLE_CONFIG")
        return None
    return SHAME_ROLE_CONFIG[guild_id]

def get_server_tag(guild):
    """Get server name tag for logging"""
    return f"[{guild.name}]" if guild else "[Unknown]"

def is_debug_mode(guild_id):
    """Check if debug mode is enabled for a server"""
    return DEBUG_MODE_CONFIG.get(guild_id, True)  # Default to True for new servers

def get_dev_channel_name(guild_id):
    """Get the appropriate dev channel name for a server"""
    return DEV_CHANNEL_CONFIG.get(guild_id, "pkl-dev")  # Default to pkl-dev

def is_wish_message(message_content):
    """Check if a message contains wish text"""
    message_lower = message_content.lower().strip()
    
    # Accept various wish message formats
    wish_variations = [
        f"{WISH_TIME} make a wish 🌠",
        f"{WISH_TIME} make a wish",
        "make a wish 🌠",
        "make a wish",
        f"{WISH_TIME} make wish 🌠",
        f"{WISH_TIME} make wish",
        "make wish 🌠",
        "make wish",
        f"{WISH_TIME} wish 🌠",
        "wish 🌠",
    ]
    
    return message_lower in wish_variations

async def remove_shame_roles(guild):
    """Remove the dunce role from all users when a new wish is detected"""
    server_tag = get_server_tag(guild)
    try:
        role_id = get_shame_role_id(guild.id)
        role = guild.get_role(role_id)
        if not role:
            print(f"{server_tag} ❌ Role with ID {role_id} not found in {guild.name} (Guild ID: {guild.id})")
            return
        
        # Check bot permissions before attempting to remove roles
        bot_member = guild.get_member(bot.user.id)
        if not bot_member.guild_permissions.manage_roles:
            print(f"{server_tag} ❌ Bot missing 'Manage Roles' permission")
            return
        
        # Check role hierarchy
        bot_top_role = bot_member.top_role
        if bot_top_role.position <= role.position:
            print(f"{server_tag} ❌ Bot role '{bot_top_role.name}' (pos: {bot_top_role.position}) is not higher than target role '{role.name}' (pos: {role.position})")
            return
        
        # Remove the role from all members who have it
        removed_count = 0
        for member in guild.members:
            if role in member.roles:
                try:
                    await member.remove_roles(role, reason="New wish detected - fresh start")
                    print(f"{server_tag} 🧹 Removed '{role.name}' role from {member.name}")
                    removed_count += 1
                except Exception as e:
                    print(f"{server_tag} ❌ Failed to remove role from {member.name}: {e}")
        
        if removed_count > 0:
            print(f"{server_tag} ✨ Cleared dunce roles from {removed_count} users for new wish")
        else:
            print(f"{server_tag} ✨ No users had dunce roles to remove")
    except Exception as e:
        print(f"{server_tag} ❌ Error removing dunce roles: {e}")
        if "50013" in str(e):
            print(f"{server_tag} 💡 Permission error - check bot role hierarchy and permissions")

async def assign_shame_role(guild, user):
    """Assign the 'dunce' role to a user"""
    server_tag = get_server_tag(guild)
    try:
        role_id = get_shame_role_id(guild.id)
        role = guild.get_role(role_id)
        if not role:
            print(f"{server_tag} ❌ Role with ID {role_id} not found in {guild.name} (Guild ID: {guild.id})")
            return
        
        # Check bot permissions before attempting to add role
        bot_member = guild.get_member(bot.user.id)
        if not bot_member.guild_permissions.manage_roles:
            print(f"{server_tag} ❌ Bot missing 'Manage Roles' permission")
            return
        
        # Check role hierarchy - bot's top role must be higher than target role
        bot_top_role = bot_member.top_role
        if bot_top_role.position <= role.position:
            print(f"{server_tag} ❌ Bot role '{bot_top_role.name}' (pos: {bot_top_role.position}) is not higher than target role '{role.name}' (pos: {role.position})")
            print(f"{server_tag} 💡 Move bot role above '{role.name}' in Server Settings → Roles")
            return
        
        # Add the role to the user
        await user.add_roles(role, reason="Failed to make a proper wish")
        print(f"{server_tag} 🔴 Added '{role.name}' role to {user.name}")
    except Exception as e:
        print(f"{server_tag} ❌ Error assigning role: {e}")
        if "50013" in str(e):
            print(f"{server_tag} 💡 Permission error - check bot role hierarchy and permissions")

@bot.event
async def on_ready():
    print(f'✅ Dr. Shamer is online as {bot.user}')
    print(f'✅ Connected to {len(bot.guilds)} servers: {", ".join([guild.name for guild in bot.guilds])}')

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Skip messages not from a guild
    if not message.guild:
        return

    server_tag = get_server_tag(message.guild)
    guild_id = message.guild.id
    london_time = datetime.now(pytz.timezone('Europe/London'))
    
    # Check if message is a wish format
    if is_wish_message(message.content):
        # Allow anytime in dev channel, otherwise only at configured wish time
        is_dev_channel = message.channel.name == get_dev_channel_name(guild_id)
        is_correct_time = london_time.strftime('%H:%M') == WISH_TIME
        
        if is_dev_channel or is_correct_time:
            print(f"{server_tag} 🎯 Detected wish message at {london_time.strftime('%H:%M')}: {message.id}")
            print(f"{server_tag} 📝 Message: '{message.content}'")
            if is_dev_channel:
                print(f"{server_tag} 📝 Dev channel - allowing wish at any time")
            
            # Remove shame roles from all users for fresh start
            await remove_shame_roles(message.guild)
            
            # Debug message for successful wish creation
            if is_debug_mode(guild_id):
                await message.channel.send(f"🐛 **DEBUG:** {message.author.mention} successfully created a wish at {london_time.strftime('%H:%M')}! 🌠")
        else:
            print(f"{server_tag} ⏰ Wish attempted at {london_time.strftime('%H:%M')} but not {WISH_TIME} - shaming user!")
            # Shame the user for making a wish at the wrong time
            await assign_shame_role(message.guild, message.author)
            await message.channel.send(f"😤 {message.author.mention} tried to start a wish at {london_time.strftime('%H:%M')} but wishes can only be made at {WISH_TIME}... OH! OH! BAD WISHES FOR {message.author.mention}! BAD WISHES FOR {message.author.mention} FOR SEVEN YEARS! 🔔🔔🔔\n\n{GIF_URL}")

    await bot.process_commands(message)

@bot.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return

    # Skip reactions not from a guild
    if not reaction.message.guild:
        return

    server_tag = get_server_tag(reaction.message.guild)
    
    # Check if this is a 🌠 reaction to a wish message
    if str(reaction.emoji) != "🌠" or not is_wish_message(reaction.message.content):
        return

    # Check if the reaction is being made at wish time + 15s buffer (or in dev channel)
    london_time = datetime.now(pytz.timezone('Europe/London'))
    is_dev_channel = reaction.message.channel.name == get_dev_channel_name(reaction.message.guild.id)
    
    # Create today's wish time and check if within 75 seconds (60s wish minute + 15s buffer)
    wish_hour, wish_minute = map(int, WISH_TIME.split(':'))
    wish_time_today = london_time.replace(hour=wish_hour, minute=wish_minute, second=0, microsecond=0)
    time_diff = (london_time - wish_time_today).total_seconds()
    is_correct_time = 0 <= time_diff <= 75
    
    if is_correct_time:
        print(f"{server_tag} 🌟 {user.name} made a wish on time at {london_time.strftime('%H:%M')}!")
        
        # Debug message for successful wish reaction
        if is_debug_mode(reaction.message.guild.id):
            await reaction.message.channel.send(f"🐛 **DEBUG:** {user.mention} successfully made a wish at {london_time.strftime('%H:%M')}! ✨")
    else:
        print(f"{server_tag} 😤 {user.name} tried to make a wish at {london_time.strftime('%H:%M')} but it wasn't at {WISH_TIME}... shame!")
        await assign_shame_role(reaction.message.guild, user)
        await reaction.message.channel.send(f"😤 {user.mention} tried to make a wish at {london_time.strftime('%H:%M')} but it wasn't at {WISH_TIME}... OH! OH! BAD WISHES FOR {user.mention}! BAD WISHES FOR {user.mention} FOR SEVEN YEARS! 🔔🔔🔔\n\n{GIF_URL}")



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