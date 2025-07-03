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

# Track wishes per server
last_wish_message_id = {}  # guild_id -> message_id
wish_timestamp = {}        # guild_id -> timestamp

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

def get_server_tag(guild):
    """Get server name tag for logging"""
    return f"[{guild.name}]" if guild else "[Unknown]"

def get_dev_channel_name(guild_id):
    """Get the appropriate dev channel name for a server"""
    return DEV_CHANNEL_CONFIG.get(guild_id, "pkl-dev")  # Default to pkl-dev

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
        is_dev_channel = message.channel.name == get_dev_channel_name(guild_id)
        is_correct_time = london_time.strftime('%H:%M') == "11:11"
        
        if is_dev_channel or is_correct_time:
            print(f"{server_tag} 🎯 Detected wish message at {london_time.strftime('%H:%M')}: {message.id}")
            print(f"{server_tag} 📝 Message: '{message.content}'")
            if is_dev_channel:
                print(f"{server_tag} 📝 Dev channel - allowing wish at any time")
            
            # Remove shame roles from all users for fresh start
            await remove_shame_roles(message.guild)
            
            # Store per-server tracking
            last_wish_message_id[guild_id] = message.id
            wish_timestamp[guild_id] = london_time
        else:
            print(f"{server_tag} ⏰ Wish attempted at {london_time.strftime('%H:%M')} but not 11:11 - shaming user!")
            # Shame the user for making a wish at the wrong time
            await assign_shame_role(message.guild, message.author)
            await message.channel.send(f"😤 {message.author.mention} tried to start a wish at {london_time.strftime('%H:%M')} but wishes can only be made at 11:11 AM... OH! OH! BAD WISHES FOR {message.author.mention}! BAD WISHES FOR {message.author.mention} FOR SEVEN YEARS! 🔔🔔🔔\n\n{GIF_URL}")

    await bot.process_commands(message)

@bot.command(name='debug_permissions')
async def debug_permissions(ctx):
    """Debug command to check bot permissions and role hierarchy"""
    server_tag = get_server_tag(ctx.guild)
    
    # Only allow in dev channels
    if ctx.channel.name != get_dev_channel_name(ctx.guild.id):
        return
    
    print(f"{server_tag} 🔍 Debug permissions check requested by {ctx.author.name}")
    
    bot_member = ctx.guild.get_member(bot.user.id)
    role_id = get_shame_role_id(ctx.guild.id)
    target_role = ctx.guild.get_role(role_id)
    
    embed = discord.Embed(title="Bot Permission Debug", color=0x00ff00)
    
    # Bot permissions
    perms = bot_member.guild_permissions
    embed.add_field(
        name="Bot Permissions",
        value=f"Manage Roles: {'✅' if perms.manage_roles else '❌'}\n"
              f"View Channels: {'✅' if perms.view_channel else '❌'}\n"
              f"Send Messages: {'✅' if perms.send_messages else '❌'}",
        inline=False
    )
    
    # Role hierarchy
    bot_top_role = bot_member.top_role
    if target_role:
        hierarchy_ok = bot_top_role.position > target_role.position
        embed.add_field(
            name="Role Hierarchy",
            value=f"Bot's top role: {bot_top_role.name} (pos: {bot_top_role.position})\n"
                  f"Target role: {target_role.name} (pos: {target_role.position})\n"
                  f"Hierarchy OK: {'✅' if hierarchy_ok else '❌'}",
            inline=False
        )
    else:
        embed.add_field(
            name="Role Hierarchy",
            value=f"❌ Target role not found (ID: {role_id})",
            inline=False
        )
    
    await ctx.send(embed=embed)

@bot.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return

    # Skip reactions not from a guild
    if not reaction.message.guild:
        return

    guild_id = reaction.message.guild.id
    server_tag = get_server_tag(reaction.message.guild)
    
    # Check if this is a reaction to the current wish message for this server
    if (guild_id not in last_wish_message_id or 
        reaction.message.id != last_wish_message_id[guild_id] or 
        str(reaction.emoji) != "🌠"):
        return

    # Check if the wish was made at 11:11 AM London time
    if guild_id in wish_timestamp:
        # Convert wish_timestamp to London time (in case it was stored differently)
        wish_time_london = wish_timestamp[guild_id].astimezone(pytz.timezone('Europe/London'))
        
        if wish_time_london.strftime('%H:%M') == "11:11":
            print(f"{server_tag} 🌟 {user.name} made a wish on time at 11:11 AM!")
        else:
            print(f"{server_tag} 😤 {user.name} tried to make a wish but it wasn't at 11:11 AM... shame!")
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