import random
import discord
import os

# Shame reactions with corresponding GIFs and messages
SHAME_REACTIONS = [
    {
        "gif_path": "src/gifs/shame-got.gif",
        "message": "OH! OH! BAD WISHES FOR {user}! BAD WISHES FOR {user} FOR SEVEN YEARS! 🔔🔔🔔"
    },
    {
        "gif_path": "src/gifs/hotfuzzshame.gif", 
        "message": "Play time's over, {user}! You missed the wish window and now you can cool off with the dunce hat! 🎄❄️"
    },
    {
        "gif_path": "src/gifs/shamebox.gif",
        "message": "Into the shame box with you, {user}! Learn to tell time! ⏰📦"
    },
    {
        "gif_path": "src/gifs/wishmassy.gif",
        "message": "Where's the proper timing, {user}?! You total idiot, that was your job! That wasn't very wishmassy of you! 😤🦃"
    },
    {
        "gif_path": "src/gifs/shocked-cat.gif",
        "message": "Oh wow, {user}! Did you really just try to wish after the wish time? I'm genuinely shocked! 😱⏰"
    },
    {
        "gif_path": "src/gifs/taskmaster-distance.gif",
        "message": "{user}, you missed the wish window... by some distance. Greg is disappointed. Very disappointed. 🕚📉"
    },
    {
        "gif_path": "src/gifs/drwho-late.gif",
        "message": "Well you’re too late, {user}! HAAAA! The wish window has closed — and so has time itself! ⏳🔒"
    },
    
    

]

def get_random_shame_reaction():
    """Get a random shame reaction with GIF and message"""
    return random.choice(SHAME_REACTIONS)

async def send_shame_message(channel, user_mention, london_time, wish_time, reaction_type="message"):
    """Send a randomized shame message with GIF"""
    # Get random reaction
    reaction = get_random_shame_reaction()
    
    # Format the base message based on type
    if reaction_type == "reaction":
        base_message = f"😤 {user_mention} tried to make a wish at {london_time} but it wasn't at {wish_time}..."
    else:
        base_message = f"😤 {user_mention} tried to start a wish at {london_time} but wishes can only be made at {wish_time}..."
    
    shame_message = reaction["message"].format(user=user_mention)
    full_message = f"{base_message} {shame_message}"
    
    # Send message with GIF attachment
    gif_path = reaction["gif_path"]
    if os.path.exists(gif_path):
        with open(gif_path, 'rb') as gif_file:
            discord_file = discord.File(gif_file, filename=os.path.basename(gif_path))
            await channel.send(content=full_message, file=discord_file)
    else:
        # Fallback to message only if GIF not found
        await channel.send(full_message) 