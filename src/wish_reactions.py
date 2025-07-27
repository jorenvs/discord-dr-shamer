import random
import discord
import asyncio
from .config import config

def get_server_tag(guild):
    """Get server name tag for logging"""
    return f"[{guild.name}]" if guild else "[Unknown]"

# Track successful wishers per guild
successful_wishers = {}  # guild_id -> {'users': set(), 'summary_scheduled': bool, 'channel': channel}

# Wish reactions with corresponding GIFs and messages
WISH_REACTIONS = [
    {
        "gif_url": "https://storage.googleapis.com/ldn-discord-dr-shamer-gifs/genie.gif",
        "message": "🧞‍♂️ **RUB MY LAMP AND THREE WISHES I WILL GRANT!** Your wish has been accepted! ✨"
    },
    {
        "gif_url": "https://storage.googleapis.com/ldn-discord-dr-shamer-gifs/sloth.gif", 
        "message": "🦥 Some people may be sloths, but you are not one of them. Your wish has been granted! ✨"
    },
    {
        "gif_url": "https://storage.googleapis.com/ldn-discord-dr-shamer-gifs/portal.gif",
        "message": "🟠🔵 **PORTAL ACTIVATED!** You launched yourself through the 11:11 wish portal like a test subject with perfect timing. Speedy thing goes in, speedy thing comes out... with a granted wish! 🌀"
    },
    {
        "gif_url": "https://storage.googleapis.com/ldn-discord-dr-shamer-gifs/sparkle.gif",
        "message": "✨ **PERFECTION ACHIEVED!** Your timing was impeccable. The universe takes notice. Wish granted with style! ✨"
    },
    {
        "gif_url": "https://storage.googleapis.com/ldn-discord-dr-shamer-gifs/tardis.gif",
        "message": "🌀 **TARDIS ACTIVATED!** It was 11:11 — wibbly-wobbly, wishy-washy, *wish grantedy.* Nice timing! The Doctor would be proud! 🔮"
    },
    {
        "gif_url": "https://storage.googleapis.com/ldn-discord-dr-shamer-gifs/tube.gif",
        "message": "🚇 **SCREEEECH...** Your wish arrived on time. Unlike the Central line. Miracles do happen. ✨"
    },
]

def get_random_wish_reaction():
    """Get a random wish reaction with GIF and message"""
    return random.choice(WISH_REACTIONS)

async def send_wish_reaction(channel, users):
    """Send a congratulatory summary message with random wish reaction"""
    # Get random reaction
    reaction = get_random_wish_reaction()
    
    # Format user mentions
    if len(users) == 1:
        user_list = f"{list(users)[0].mention}"
        summary_text = f"🎉 **Congratulations, {user_list} wished in time and their wish is granted!**"
    else:
        user_mentions = [user.mention for user in users]
        user_list = ", ".join(user_mentions)
        summary_text = f"🎉 **Congratulations, {user_list} wished in time and their wish is granted!**"
    
    # Combine summary with reaction message
    full_message = f"{summary_text}\n\n{reaction['message']}"
    
    # Create embed with GIF
    embed = discord.Embed(
        description=full_message,
        color=0x00FF00  # Green color for success
    )
    embed.set_image(url=reaction["gif_url"])
    
    await channel.send(embed=embed)

async def send_wish_summary(guild_id, channel):
    """Send a summary of successful wishers after a delay"""
    # Wait for the summary delay (configurable)
    await asyncio.sleep(config.WISH_SUMMARY_DELAY)
    
    if guild_id not in successful_wishers or not successful_wishers[guild_id]['users']:
        return
    
    users = successful_wishers[guild_id]['users']
    server_tag = get_server_tag(channel.guild)
    
    # Only send summary if there are users who wished in time
    if len(users) > 0:
        try:
            await send_wish_reaction(channel, users)
            print(f"{server_tag} 📋 Sent wish summary for {len(users)} users")
            
        except Exception as e:
            print(f"{server_tag} ❌ Failed to send wish summary: {e}")
    
    # Clean up the tracking data
    successful_wishers[guild_id] = {'users': set(), 'summary_scheduled': False, 'channel': None}

def track_successful_wish(guild, user, channel):
    """Track a successful wish and schedule summary if needed"""
    guild_id = guild.id
    
    # Initialize tracking for this guild if needed
    if guild_id not in successful_wishers:
        successful_wishers[guild_id] = {'users': set(), 'summary_scheduled': False, 'channel': None}
    
    # Schedule summary task if not already scheduled (this means it's a new wish window)
    if not successful_wishers[guild_id]['summary_scheduled']:
        successful_wishers[guild_id] = {'users': set(), 'summary_scheduled': True, 'channel': channel}
        server_tag = get_server_tag(guild)
        print(f"{server_tag} ⏰ Scheduled wish summary to run in {config.WISH_SUMMARY_DELAY} seconds")
        asyncio.create_task(send_wish_summary(guild_id, channel))
    
    # Add user to successful wishers
    successful_wishers[guild_id]['users'].add(user)
    successful_wishers[guild_id]['channel'] = channel

 