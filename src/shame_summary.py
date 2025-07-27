import asyncio
import discord
from datetime import datetime, time, timedelta
from .config import config, LONDON_TZ, SHAME_SUMMARY_CONFIG
from .firestore_db import get_daily_shamers
from .utils import get_server_tag, get_shame_summary_channel_name
from .shame_reactions import get_random_shame_reaction

# Store reference to the current shame summary task
current_shame_task = None

async def send_shame_summary(guild, channel):
    """Send daily shame summary for a guild"""
    server_tag = get_server_tag(guild)
    guild_id = guild.id
    
    # Check if shame summary is enabled for this guild
    if not SHAME_SUMMARY_CONFIG.get(guild_id, True):
        print(f"{server_tag} ⏭️ Shame summary disabled for this guild")
        return
    
    # Get today's shamers from Firestore
    shamers = get_daily_shamers(guild_id)
    
    if not shamers:
        print(f"{server_tag} 😊 No shamers today - skipping shame summary")
        return
    
    # Convert user IDs to user mentions (simple format)
    shamer_mentions = [f"<@{user_id}>" for user_id in shamers]
    
    # Get random shame reaction (same as individual shaming)
    reaction = get_random_shame_reaction()
    
    # Format the message like shame reactions
    if len(shamer_mentions) == 1:
        base_message = f"😤 {shamer_mentions[0]} tried to wish but it wasn't at {config.WISH_TIME}..."
        shame_message = reaction["message"].format(user=shamer_mentions[0])
    else:
        user_list = ", ".join(shamer_mentions)
        base_message = f"😤 {user_list} tried to wish but it wasn't at {config.WISH_TIME}..."
        # For multiple users, adapt the message
        users_text = "you all" if len(shamer_mentions) > 2 else "you both"
        shame_message = reaction["message"].replace("{user}", users_text)
    
    full_message = f"{base_message} {shame_message}"
    
    # Create embed with GIF (same as shame reactions)
    embed = discord.Embed(
        description=full_message,
        color=0xFF0000,  # Red color for shame
        timestamp=datetime.now()
    )
    embed.set_image(url=reaction["gif_url"])
    
    await channel.send(embed=embed)
    print(f"{server_tag} 📋 Sent shame summary for {len(shamer_mentions)} users")

async def wait_until_shame_time():
    """Wait until the next shame time (22:22 London time)"""
    while True:
        now = datetime.now(LONDON_TZ)
        shame_hour, shame_minute = map(int, config.SHAME_TIME.split(':'))
        
        # Calculate next shame time
        shame_time_today = now.replace(hour=shame_hour, minute=shame_minute, second=0, microsecond=0)
        
        if now >= shame_time_today:
            # If we've passed today's shame time, wait until tomorrow
            shame_time_next = shame_time_today + timedelta(days=1)
        else:
            # Wait until today's shame time
            shame_time_next = shame_time_today
        
        sleep_seconds = (shame_time_next - now).total_seconds()
        print(f"⏰ Waiting {sleep_seconds:.0f} seconds until next shame time at {shame_time_next.strftime('%H:%M')} London time")
        
        await asyncio.sleep(sleep_seconds)
        
        # Send shame summaries to all guilds
        yield

async def shame_summary_task(bot):
    """Background task that sends shame summaries at 22:22 every day"""
    print(f"🔔 Started daily shame summary task for {config.SHAME_TIME} London time")
    
    async for _ in wait_until_shame_time():
        print(f"🔔 Sending daily shame summaries at {datetime.now(LONDON_TZ).strftime('%H:%M')} London time")
        
        for guild in bot.guilds:
            server_tag = get_server_tag(guild)
            
            # Get configured channel for this guild
            channel_name = get_shame_summary_channel_name(guild.id)
            target_channel = discord.utils.get(guild.text_channels, name=channel_name)
            
            if target_channel:
                await send_shame_summary(guild, target_channel)
            else:
                print(f"{server_tag} ❌ Channel '{channel_name}' not found for shame summary")
        
        print(f"🔔 Completed daily shame summaries")

def start_shame_summary_task(bot):
    """Start the background shame summary task"""
    global current_shame_task
    current_shame_task = asyncio.create_task(shame_summary_task(bot))
    return current_shame_task

def restart_shame_summary_task(bot):
    """Restart the shame summary task (used when shame time changes)"""
    global current_shame_task
    
    # Cancel the old task
    if current_shame_task and not current_shame_task.done():
        current_shame_task.cancel()
        print(f"🔄 Cancelled old shame summary task")
    
    # Start new task
    current_shame_task = asyncio.create_task(shame_summary_task(bot))
    print(f"🔄 Started new shame summary task for {config.SHAME_TIME}")
    return current_shame_task 