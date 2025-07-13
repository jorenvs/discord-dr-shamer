import asyncio
import re
from datetime import datetime
from .config import config, LONDON_TZ, SHAME_ROLE_CONFIG, DEV_CHANNEL_CONFIG, DEBUG_MODE_CONFIG

class WrongTimeException(Exception):
    def __init__(self, used_time):
        self.used_time = used_time
        super().__init__(f"Wrong time used: {used_time}")

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
    """Check if message is a wish format, raise exception if wrong time"""
    text = message_content.lower().strip()
    
    # Check for valid wish patterns
    has_make_wish = "make a wish" in text
    has_wish_with_star = "wish" in text and "🌠" in message_content  # Use original for emoji
    
    if not (has_make_wish or has_wish_with_star):
        return False
    
    # If it's a wish message, check for time and validate
    time_match = re.search(r'\b(\d{1,2}:\d{2})\b', text)
    if time_match:
        used_time = time_match.group(1)
        if used_time != config.WISH_TIME:
            raise WrongTimeException(used_time)
    
    return True

async def remove_shame_roles(guild, bot):
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
        members_with_role = [member for member in guild.members if role in member.roles]
        
        # Process in batches to avoid blocking the event loop
        for member in members_with_role:
            try:
                await member.remove_roles(role, reason="New wish detected - fresh start")
                print(f"{server_tag} 🧹 Removed '{role.name}' role from {member.name}")
                removed_count += 1
            except Exception as e:
                print(f"{server_tag} ❌ Failed to remove role from {member.name}: {e}")
            
            # Yield control back to event loop every few operations to prevent blocking
            if removed_count % 5 == 0:
                await asyncio.sleep(0)
        
        if removed_count > 0:
            print(f"{server_tag} ✨ Cleared dunce roles from {removed_count} users for new wish")
        else:
            print(f"{server_tag} ✨ No users had dunce roles to remove")
    except Exception as e:
        print(f"{server_tag} ❌ Error removing dunce roles: {e}")
        if "50013" in str(e):
            print(f"{server_tag} 💡 Permission error - check bot role hierarchy and permissions")

async def assign_shame_role(guild, user, bot):
    """Assign the 'dunce' role to a user"""
    server_tag = get_server_tag(guild)
    try:
        role_id = get_shame_role_id(guild.id)
        role = guild.get_role(role_id)
        if not role:
            print(f"{server_tag} ❌ Role with ID {role_id} not found in {guild.name} (Guild ID: {guild.id})")
            return False
        
        # Check if user already has the shame role
        if role in user.roles:
            print(f"{server_tag} ⏭️ {user.name} already has the '{role.name}' role - skipping shame reaction")
            return False
        
        # Check bot permissions before attempting to add role
        bot_member = guild.get_member(bot.user.id)
        if not bot_member.guild_permissions.manage_roles:
            print(f"{server_tag} ❌ Bot missing 'Manage Roles' permission")
            return False
        
        # Check role hierarchy - bot's top role must be higher than target role
        bot_top_role = bot_member.top_role
        if bot_top_role.position <= role.position:
            print(f"{server_tag} ❌ Bot role '{bot_top_role.name}' (pos: {bot_top_role.position}) is not higher than target role '{role.name}' (pos: {role.position})")
            print(f"{server_tag} 💡 Move bot role above '{role.name}' in Server Settings → Roles")
            return False
        
        # Add the role to the user
        await user.add_roles(role, reason="Failed to make a proper wish")
        print(f"{server_tag} 🔴 Added '{role.name}' role to {user.name}")
        return True
    except Exception as e:
        print(f"{server_tag} ❌ Error assigning role: {e}")
        if "50013" in str(e):
            print(f"{server_tag} 💡 Permission error - check bot role hierarchy and permissions")
        return False

 