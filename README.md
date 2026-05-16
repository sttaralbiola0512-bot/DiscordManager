# Discord Manager Bot 🤖

A complete Discord moderation bot with auto-moderation, anti-spam, anti-link filtering, warning system, server management, and Groq AI content analysis.

## Features

### 🛡️ Moderation
- **Auto-Moderation**: Groq AI integration for intelligent content analysis
- **Anti-Spam**: Detects and prevents spam messages
- **Anti-Link**: Automatically removes links from non-authorized members
- **Warning System**: 
  - Maximum 3 warnings before automatic kick
  - Warnings expire after 7 days
  - Warnings sent via DM to users
  - Admin can clear warnings

### 👮 Server Management Commands
- `/kick` - Kick user from server
- `/ban` - Ban user from server
- `/clear` - Clear messages (bulk delete)
- `/setname` - Change server name
- `/createrole` - Create new role
- `/assignrole` - Assign role to user
- `/removerole` - Remove role from user
- `/createchannel` - Create new channel
- `/deletechannel` - Delete channel

### ⚠️ Moderation Commands
- `/warn` - Warn a user (sends DM notification)
- `/warnings` - View user's warning history
- `/clearwarnings` - Clear all warnings for a user

### 🔧 Features
- **Flask Server**: Runs 24/7 background server for uptime
- **Secure Credentials**: Uses environment variables only, no hardcoded tokens
- **Silent Operation**: Bot performs actions without sending unnecessary messages
- **Local Database**: Stores warnings and user data

## Setup Instructions

### 1. Prerequisites
- Python 3.8+
- Discord Bot Token (from [Discord Developer Portal](https://discord.com/developers/applications))
- Groq API Key (from [Groq Console](https://console.groq.com))

### 2. Installation

```bash
# Clone the repository
git clone https://github.com/sttaralbiola0512-bot/DiscordManager.git
cd DiscordManager

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your tokens
# DISCORD_BOT_TOKEN=your_token_here
# GROQ_API_KEY=your_groq_key_here
```

### 4. Running the Bot

```bash
python main.py
```

The bot will:
- Load environment variables from `.env`
- Initialize the database
- Start Flask server in background (port 5000)
- Connect to Discord and listen for commands

## Bot Permissions Required

Make sure your bot has these permissions:
- `Administrator` (recommended for full functionality)
- `Manage Messages` (for clearing messages)
- `Manage Users` (for kick/ban)
- `Manage Roles` (for role management)
- `Manage Channels` (for channel management)
- `Send Messages`
- `Send Messages in Threads`
- `Embed Links`
- `Read Message History`

## Environment Variables

```env
DISCORD_BOT_TOKEN=your_discord_bot_token
GROQ_API_KEY=your_groq_api_key
FLASK_PORT=5000
FLASK_HOST=0.0.0.0
DEBUG=False
```

## Project Structure

```
DiscordManager/
├── main.py              # Entry point
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
├── .gitignore           # Git ignore rules
├── README.md            # This file
└── app/
    ├── __init__.py
    ├── bot.py           # Bot client setup
    ├── cogs/
    │   ├── __init__.py
    │   ├── moderation.py    # Warning and moderation commands
    │   ├── server.py        # Server management commands
    │   └── events.py        # Event handlers for auto-moderation
    ├── utils/
    │   ├── __init__.py
    │   ├── ai.py            # Groq AI content analysis
    │   ├── spam.py          # Spam detection
    │   ├── links.py         # Link detection
    │   ├── warnings.py      # Warning system management
    │   └── database.py      # Local database operations
    └── server/
        ├── __init__.py
        └── flask_app.py     # Flask background server
```

## Command Examples

### Moderation
```
/warn @user - Warn a user (max 3, auto-kick on 3rd)
/warnings @user - Check user's warnings
/clearwarnings @user - Clear all warnings
```

### Server Management
```
/kick @user reason - Kick user from server
/ban @user reason - Ban user from server
/clear 10 - Clear last 10 messages
/setname NewServerName - Change server name
/createrole RoleName - Create new role
/assignrole @user RoleName - Assign role to user
/removerole @user RoleName - Remove role from user
/createchannel ChannelName - Create new channel
/deletechannel - Delete current channel
```

## Auto-Moderation Features

### Groq AI Integration
The bot uses Groq AI to analyze message content for:
- Inappropriate language
- Spam patterns
- Malicious content
- Policy violations

### Anti-Spam
- Detects rapid message sequences
- Flags duplicate messages
- Rate-limits user messages

### Anti-Link
- Removes non-whitelisted links
- Prevents link spam
- Configurable for specific channels

## Support & Contributing

For issues, questions, or contributions, please open an issue on GitHub.

## License

MIT License - Feel free to use this bot in your projects.

## Security Note

⚠️ **NEVER** commit your `.env` file or hardcode tokens in your code. Always use environment variables.
