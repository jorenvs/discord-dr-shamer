import asyncio
import discord
from datetime import datetime, time, timedelta
from .config import config, LONDON_TZ, SHAME_SUMMARY_CONFIG
from .firestore_db import get_daily_shamers
from .utils import get_server_tag
from .shame_reactions import get_random_shame_reaction

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
    
    try:
        # Convert user IDs to user mentions
        shamer_mentions = []
        for user_id in shamers:
            try:
                user = guild.get_member(int(user_id))
                if user:
                    shamer_mentions.append(user.mention)
                else:
                    # User might have left the server
                    shamer_mentions.append(f"<@{user_id}>")
            except (ValueError, TypeError):
                continue
        
        if not shamer_mentions:
            print(f"{server_tag} 😊 No valid shamers to mention - skipping shame summary")
            return
        
        # Get random shame reaction (same as individual shaming)
        reaction = get_random_shame_reaction()
        
        # Format the shame summary message (similar to individual shame messages)
        if len(shamer_mentions) == 1:
            base_message = f"🔔 **Daily Shame Summary** 🔔\n\n{shamer_mentions[0]} was shamed today for poor wish timing!"
        else:
            user_list = ", ".join(shamer_mentions)
            base_message = f"🔔 **Daily Shame Summary** 🔔\n\n{user_list} were shamed today for poor wish timing!"
        
        # Use the shame reaction message but adapted for multiple users
        if len(shamer_mentions) == 1:
            shame_message = reaction["message"].format(user=shamer_mentions[0])
        else:
            # For multiple users, adapt the message
            users_text = "you all" if len(shamer_mentions) > 2 else "you both"
            shame_message = reaction["message"].replace("{user}", users_text)
        
        full_message = f"{base_message}\n\n{shame_message}\n\nRemember: wishes must be made at **{config.WISH_TIME}** London time! ⏰"
        
        # Create embed with GIF (same as shame reactions)
        embed = discord.Embed(
            description=full_message,
            color=0xFF0000,  # Red color for shame
            timestamp=datetime.now()
        )
        embed.set_image(url=reaction["gif_url"])
        embed.set_footer(text="Daily Shame Summary")
        
        await channel.send(embed=embed)
        print(f"{server_tag} 📋 Sent daily shame summary for {len(shamer_mentions)} users")
        
    except Exception as e:
        print(f"{server_tag} ❌ Failed to send shame summary: {e}")

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
            
            try:
                # Find a suitable channel to send the summary
                # Priority: general, random, or first text channel
                target_channel = None
                
                for channel in guild.text_channels:
                    if channel.name.lower() in ['general', 'random', 'chat']:
                        target_channel = channel
                        break
                
                if not target_channel:
                    # Use the first text channel the bot can send messages to
                    for channel in guild.text_channels:
                        if channel.permissions_for(guild.me).send_messages:
                            target_channel = channel
                            break
                
                if target_channel:
                    await send_shame_summary(guild, target_channel)
                else:
                    print(f"{server_tag} ❌ No suitable channel found for shame summary")
                    
            except Exception as e:
                print(f"{server_tag} ❌ Error sending shame summary: {e}")
        
        print(f"🔔 Completed daily shame summaries")

def start_shame_summary_task(bot):
    """Start the background shame summary task"""
    return asyncio.create_task(shame_summary_task(bot)) 