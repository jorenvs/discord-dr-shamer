import random
import discord

# Shame reactions with corresponding GIFs and messages
SHAME_REACTIONS = [
    {
        "gif_url": "https://storage.googleapis.com/ldn-discord-dr-shamer-gifs/shame-got.gif",
        "message": "OH! OH! BAD WISHES FOR {user}! BAD WISHES FOR {user} FOR SEVEN YEARS! 🔔🔔🔔"
    },
    {
        "gif_url": "https://storage.googleapis.com/ldn-discord-dr-shamer-gifs/hotfuzzshame.gif", 
        "message": "Play time's over, {user}! You missed the wish window and now you can cool off with the dunce hat! 🎄❄️"
    },
    {
        "gif_url": "https://storage.googleapis.com/ldn-discord-dr-shamer-gifs/shamebox.gif",
        "message": "Into the shame box with you, {user}! Learn to tell time! ⏰📦"
    },
    {
        "gif_url": "https://storage.googleapis.com/ldn-discord-dr-shamer-gifs/wishmassy.gif",
        "message": "Where's the proper timing, {user}?! You total idiot, that was your job! That wasn't very wishmassy of you! 😤🦃"
    },
    {
        "gif_url": "https://storage.googleapis.com/ldn-discord-dr-shamer-gifs/shocked-cat.gif",
        "message": "Oh wow, {user}! Did you really just try to wish after the wish time? I'm genuinely shocked! 😱⏰"
    },
    {
        "gif_url": "https://storage.googleapis.com/ldn-discord-dr-shamer-gifs/taskmaster-distance.gif",
        "message": "{user}, you missed the wish window... by some distance. Greg is disappointed. Very disappointed. 🕚📉"
    },
    {
        "gif_url": "https://storage.googleapis.com/ldn-discord-dr-shamer-gifs/drwho-late.gif",
        "message": "Well you're too late, {user}! HAAAA! The wish window has closed — and so has time itself! ⏳🔒"
    },
    {
        "gif_url": "https://storage.googleapis.com/ldn-discord-dr-shamer-gifs/pulpfiction.gif",
        "message": "Say wish again, {user}. I dare you. I double dare you! 🔫😤"
    },
]

def get_random_shame_reaction():
    """Get a random shame reaction with GIF and message"""
    return random.choice(SHAME_REACTIONS)

async def send_shame_message(channel, user_mention, london_time, wish_time, reaction_type="message"):
    """Send a randomized shame message with GIF embed"""
    # Get random reaction
    reaction = get_random_shame_reaction()
    
    # Format the base message based on type
    if reaction_type == "reaction":
        base_message = f"😤 {user_mention} tried to make a wish at {london_time} but it wasn't at {wish_time}..."
    else:
        base_message = f"😤 {user_mention} tried to start a wish at {london_time} but wishes can only be made at {wish_time}..."
    
    shame_message = reaction["message"].format(user=user_mention)
    full_message = f"{base_message} {shame_message}"
    
    # Create embed with GIF
    embed = discord.Embed(
        description=full_message,
        color=0xFF0000  # Red color for shame
    )
    embed.set_image(url=reaction["gif_url"])
    
    await channel.send(embed=embed) 