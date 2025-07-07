from . import config
from .utils import get_dev_channel_name, get_server_tag

async def handle_bot_mention(message, server_tag, guild_id, bot):
    """Handle mentions of the bot for commands"""
    # Only allow commands in dev channels
    is_dev_channel = message.channel.name == get_dev_channel_name(guild_id)
    if not is_dev_channel:
        await message.channel.send(f"⚠️ Bot commands can only be used in the dev channel: #{get_dev_channel_name(guild_id)}")
        return
    
    # Remove the bot mention and get the command
    content = message.content
    # Remove the mention (could be <@!123> or <@123>)
    content = content.replace(f"<@{bot.user.id}>", "").replace(f"<@!{bot.user.id}>", "").strip()
    
    # Parse the command
    parts = content.lower().split()
    
    if len(parts) >= 3 and parts[0] == "set" and parts[1] == "wishtime":
        await set_wish_time(message, parts[2], server_tag)
    elif len(parts) >= 3 and parts[0] == "set" and parts[1] == "buffer":
        await set_buffer_time(message, parts[2], server_tag)
    else:
        await message.channel.send(f"🤖 Available commands:\n• `@{bot.user.display_name} set wishtime HH:MM` - Set the wish time (e.g., 12:12)\n• `@{bot.user.display_name} set buffer N` - Set the buffer time in seconds (e.g., 20)")

async def set_wish_time(message, new_time, server_tag):
    """Set the wish time with basic validation"""
    # Basic validation - just check if it's HH:MM format
    if len(new_time) == 5 and new_time[2] == ':':
        old_time = config.WISH_TIME
        config.WISH_TIME = new_time
        print(f"{server_tag} ⏰ Wish time changed from {old_time} to {config.WISH_TIME} by {message.author.name}")
        await message.channel.send(f"✅ Wish time updated to **{config.WISH_TIME}**! 🕐")
    else:
        await message.channel.send(f"❌ Invalid time format! Please use HH:MM format (e.g., 12:12)")

async def set_buffer_time(message, new_buffer, server_tag):
    """Set the buffer time with basic validation"""
    # Basic validation - just check if it's a number
    if new_buffer.isdigit():
        old_buffer = config.WISH_BUFFER_TIME
        config.WISH_BUFFER_TIME = int(new_buffer)
        print(f"{server_tag} ⏱️ Buffer time changed from {old_buffer}s to {config.WISH_BUFFER_TIME}s by {message.author.name}")
        await message.channel.send(f"✅ Buffer time updated to **{config.WISH_BUFFER_TIME} seconds**! (Total window: {60 + config.WISH_BUFFER_TIME}s)")
    else:
        await message.channel.send(f"❌ Invalid number! Please use a number (e.g., 20)") 