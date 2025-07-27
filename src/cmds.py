from .config import config
from .utils import get_dev_channel_name, get_server_tag
from .firestore_db import get_leaderboard

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
    elif len(parts) >= 3 and parts[0] == "set" and parts[1] == "shametime":
        await set_shame_time(message, parts[2], server_tag, bot)
    elif len(parts) >= 3 and parts[0] == "set" and parts[1] == "buffer":
        await set_buffer_time(message, parts[2], server_tag)
    elif len(parts) >= 3 and parts[0] == "set" and parts[1] == "summarydelay":
        await set_summary_delay(message, parts[2], server_tag)
    elif len(parts) >= 1 and parts[0] == "rank":
        await show_leaderboard(message, server_tag, guild_id)
    else:
        await message.channel.send(f"🤖 Available commands:\n• `@{bot.user.display_name} set wishtime HH:MM` - Set the wish time (e.g., 11:11)\n• `@{bot.user.display_name} set shametime HH:MM` - Set the shame summary time (e.g., 22:22)\n• `@{bot.user.display_name} set buffer N` - Set the buffer time in seconds (e.g., 20)\n• `@{bot.user.display_name} set summarydelay N` - Set the summary delay in seconds (e.g., 180)\n• `@{bot.user.display_name} rank` - Show leaderboard of top wishers and shamers")

async def set_wish_time(message, new_time, server_tag):
    """Set the wish time with basic validation"""
    # Basic validation - just check if it's HH:MM format
    if len(new_time) == 5 and new_time[2] == ':':
        old_time = config.WISH_TIME
        config.WISH_TIME = new_time
        print(f"{server_tag} ⏰ Wish time changed from {old_time} to {config.WISH_TIME} by {message.author.name}")
        await message.channel.send(f"✅ Wish time updated to **{config.WISH_TIME}**! 🕐")
    else:
        await message.channel.send(f"❌ Invalid time format! Please use HH:MM format (e.g., 11:11)")

async def set_shame_time(message, new_time, server_tag, bot):
    """Set the shame time with basic validation"""
    # Basic validation - just check if it's HH:MM format
    if len(new_time) == 5 and new_time[2] == ':':
        old_time = config.SHAME_TIME
        config.SHAME_TIME = new_time
        print(f"{server_tag} 🔔 Shame time changed from {old_time} to {config.SHAME_TIME} by {message.author.name}")
        
        # Restart the shame summary task with new time
        from .shame_summary import restart_shame_summary_task
        restart_shame_summary_task(bot)
        
        await message.channel.send(f"✅ Shame summary time updated to **{config.SHAME_TIME}**! 🔔\n⏰ Restarted background task for new time.")
    else:
        await message.channel.send(f"❌ Invalid time format! Please use HH:MM format (e.g., 22:22)")

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

async def set_summary_delay(message, new_delay, server_tag):
    """Set the summary delay with basic validation"""
    # Basic validation - just check if it's a number
    if new_delay.isdigit():
        old_delay = config.WISH_SUMMARY_DELAY
        config.WISH_SUMMARY_DELAY = int(new_delay)
        print(f"{server_tag} ⏰ Summary delay changed from {old_delay}s to {config.WISH_SUMMARY_DELAY}s by {message.author.name}")
        await message.channel.send(f"✅ Summary delay updated to **{config.WISH_SUMMARY_DELAY} seconds**!")
    else:
        await message.channel.send(f"❌ Invalid number! Please use a number (e.g., 180)")

async def show_leaderboard(message, server_tag, guild_id):
    """Show the leaderboard of top wishers and shamers"""
    try:
        leaderboard = get_leaderboard(guild_id)
        
        top_wishers = leaderboard["top_wishers"][:10]  # Top 10
        top_shamers = leaderboard["top_shamers"][:10]  # Top 10
        
        # Format the leaderboard message
        embed_description = "🏆 **Wish & Shame Leaderboard** 🏆\n\n"
        
        # Top Wishers section
        embed_description += "✨ **Top Wishers:**\n"
        if top_wishers:
            for i, (user_id, count) in enumerate(top_wishers, 1):
                try:
                    user = message.guild.get_member(int(user_id))
                    display_name = user.display_name if user else f"<@{user_id}>"
                except (ValueError, TypeError):
                    display_name = f"<@{user_id}>"
                
                medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                embed_description += f"{medal} {display_name}: {count} day(s)\n"
        else:
            embed_description += "No wishers yet!\n"
        
        # Top Shamers section
        embed_description += "\n🔔 **Top Shamers:**\n"
        if top_shamers:
            for i, (user_id, count) in enumerate(top_shamers, 1):
                try:
                    user = message.guild.get_member(int(user_id))
                    display_name = user.display_name if user else f"<@{user_id}>"
                except (ValueError, TypeError):
                    display_name = f"<@{user_id}>"
                
                medal = "💩" if i == 1 else "🤡" if i == 2 else "😤" if i == 3 else f"{i}."
                embed_description += f"{medal} {display_name}: {count} day(s)\n"
        else:
            embed_description += "No shamers yet!\n"
        
        embed_description += f"\n*Each day counts as 1 point maximum*"
        
        # Create and send embed
        import discord
        embed = discord.Embed(
            description=embed_description,
            color=0x00FF00,
            timestamp=message.created_at
        )
        embed.set_footer(text="Leaderboard")
        
        await message.channel.send(embed=embed)
        print(f"{server_tag} 📊 Sent leaderboard to {message.author.name}")
        
    except Exception as e:
        print(f"{server_tag} ❌ Failed to show leaderboard: {e}")
        await message.channel.send(f"❌ Failed to retrieve leaderboard. Please try again later.")