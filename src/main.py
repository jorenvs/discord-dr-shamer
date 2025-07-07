import discord
from discord.ext import commands
from datetime import datetime
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import os
from dotenv import load_dotenv

# Only load .env in development - production uses environment variables directly
if os.path.exists('.env'):
    load_dotenv()

from .config import *
from .utils import *
from .cmds import handle_bot_mention

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.messages = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

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
    
    # Check if the bot is mentioned
    if bot.user.mentioned_in(message):
        await handle_bot_mention(message, server_tag, guild_id, bot)
        return
    
    # Check if message is a wish format (with fast precheck)
    if "wish" in message.content.lower() and is_wish_message(message.content):
        # Use message creation time, not current time
        london_time = message.created_at.astimezone(LONDON_TZ)
        
        is_correct_time = london_time.strftime('%H:%M') == WISH_TIME
        
        if is_correct_time:
            print(f"{server_tag} 🎯 Detected wish message at {london_time.strftime('%H:%M')}: {message.id}")
            print(f"{server_tag} 📝 Message: '{message.content}'")
            
            # Remove shame roles from all users for fresh start
            await remove_shame_roles(message.guild, bot)
            
            # Debug message for successful wish creation
            if is_debug_mode(guild_id):
                await message.channel.send(f"🐛 **DEBUG:** {message.author.mention} successfully created a wish at {london_time.strftime('%H:%M')}! 🌠")
        else:
            print(f"{server_tag} ⏰ Wish attempted at {london_time.strftime('%H:%M')} but not {WISH_TIME} - shaming user!")
            # Shame the user for making a wish at the wrong time
            await assign_shame_role(message.guild, message.author, bot)
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
    
    # Check if this is a 🌠 reaction to a wish message (with fast precheck)
    if str(reaction.emoji) != "🌠":
        return
    
    if not ("wish" in reaction.message.content.lower() and is_wish_message(reaction.message.content)):
        return

    # Check if the reaction is being made at wish time + buffer
    london_time = datetime.now(LONDON_TZ)
    
    # Create today's wish time and check if within buffer (60s wish minute + buffer)
    wish_hour, wish_minute = map(int, WISH_TIME.split(':'))
    wish_time_today = london_time.replace(hour=wish_hour, minute=wish_minute, second=0, microsecond=0)
    time_diff = (london_time - wish_time_today).total_seconds()
    is_correct_time = 0 <= time_diff <= (60 + WISH_BUFFER_TIME)
    
    if is_correct_time:
        print(f"{server_tag} 🌟 {user.name} made a wish on time at {london_time.strftime('%H:%M')}!")
        
        # Debug message for successful wish reaction
        if is_debug_mode(reaction.message.guild.id):
            await reaction.message.channel.send(f"🐛 **DEBUG:** {user.mention} successfully made a wish at {london_time.strftime('%H:%M')}! ✨")
    else:
        print(f"{server_tag} 😤 {user.name} tried to make a wish at {london_time.strftime('%H:%M')} but it wasn't at {WISH_TIME}... shame!")
        await assign_shame_role(reaction.message.guild, user, bot)
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