# Dr. Shamer Bot 🤖🔔

A Discord bot that enforces proper 11:11 wish-making etiquette. Make your wishes at the right time, or face the consequences!

## What It Does

**Dr. Shamer** monitors your Discord server for wish messages and ensures everyone follows the sacred 11:11 AM rule:

- ✅ **Valid wishes**: Posted at exactly 11:11 AM London time
- 🔴 **Invalid wishes**: Posted at any other time → Get shamed + dunce role
- 🌠 **Reaction system**: React with 🌠 to valid wishes
- 🧹 **Fresh starts**: Each new valid wish clears all previous shame roles

## Features

### 🕐 Time Enforcement
- Only accepts wishes at **11:11 AM London time**
- Configurable dev channels for testing (bypasses time restriction)

### 📝 Flexible Message Detection
Accepts various wish formats:
- `11:11 make a wish 🌠`
- `make a wish`
- `wish 🌠`
- `11:11 make wish`
- And more variations!

### 🔴 Shame System
- Assigns configurable "dunce" roles to rule-breakers
- Public shame messages: *"BAD WISHES FOR [USER] FOR SEVEN YEARS!"*
- Automatic role cleanup when new valid wishes start

### ⚙️ Multi-Server Support
- Configurable shame roles per server
- Configurable dev channels per server

## Setup

### 1. Prerequisites
- Python 3.8+ (tested on python 3.10)
- [uv](https://github.com/astral-sh/uv) - Fast Python package installer (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- Discord bot token
- Server Members Intent + Message Content Intent enabled in Discord Developer Portal

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/jorenvs/discord-dr-shamer.git
cd discord-dr-shamer

# Create virtual environment and install dependencies with uv
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -r requirements.txt

# Alternative: Use uv sync if you have a pyproject.toml
# uv sync
```

### 3. Environment Setup
Create a `.env` file:
```env
DISCORD_BOT_TOKEN=your_bot_token_here
```

### 4. Configuration
Edit `bot.py` to configure your servers:

```python
# Server ID → Role ID mapping
SHAME_ROLE_CONFIG = {
    168316445569056768: 1390320164024881192,  # London server: dunce role
    1390289538613772400: 1390319545243402370,  # Your server: your role ID
}

# Server ID → Dev channel name mapping
DEV_CHANNEL_CONFIG = {
    168316445569056768: "pkl-dev",        # London server dev channel
    1390289538613772400: "dr-shamer-dev", # Your server dev channel
}
```

### 5. Bot Permissions
Ensure your bot has these permissions:
- View Server Members
- Manage Roles
- Send Messages
- Add Reactions
- Read Message History

### 6. Discord Developer Portal
Enable **Privileged Gateway Intents**:
1. Go to https://discord.com/developers/applications/
2. Select your bot → Bot section
3. Under "Privileged Gateway Intents", enable:
   - **Server Members Intent**
   - **Message Content Intent**
4. Save changes

## Usage

### Starting the Bot
```bash
# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Run the bot
python bot.py
```

### How to Make Wishes
1. **Post a wish message** at exactly 11:11 AM London time:
   ```
   11:11 make a wish 🌠
   ```

2. **Others react** with 🌠 to make their wishes

3. **Dev channel testing**: Post wishes anytime in configured dev channels

### What Happens When You Mess Up
- **Wrong time wish**: Immediate shame role + curse message
- **Late reaction**: Get shame role (if implemented)
- **Wrong time reaction**: Get shame role + curse message

## Configuration

### Adding New Servers
Add entries to both config dictionaries:

```python
SHAME_ROLE_CONFIG = {
    YOUR_SERVER_ID: YOUR_ROLE_ID,
    # Add more servers...
}

DEV_CHANNEL_CONFIG = {
    YOUR_SERVER_ID: "your-dev-channel-name",
    # Add more servers...
}
```

### Finding IDs
**Server ID**: Right-click server name → Copy Server ID (requires Developer Mode)
**Role ID**: Right-click role → Copy Role ID (requires Developer Mode)

## File Structure
```
discord-dr-shamer/
├── bot.py              # Main bot code
├── requirements.txt    # Python dependencies
├── .venv/             # Virtual environment (created by uv)
├── .env               # Environment variables (not in git)
├── .env.example       # Example environment file
├── .gitignore         # Git ignore rules
└── README.md          # This file
```

## Dependencies
- `discord.py` - Discord API wrapper
- `python-dotenv` - Environment variable management
- `pytz` - Timezone handling

## Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License
This project is licensed under the MIT License.

## Support
For issues or questions:
1. Check existing GitHub issues
2. Create a new issue with detailed description
3. Include relevant logs and error messages

---

**Remember**: Wishes are sacred. Make them at 11:11 AM or face seven years of bad wishes! 🌠🔔 