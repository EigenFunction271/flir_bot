# Flir Discord Bot - Social Skills Training

A Discord bot that provides AI-powered social skills training through interactive scenarios with realistic character personas.

## Features

- **7 Pre-defined Character Personas** with unique personalities and communication styles
- **6 Training Scenarios** across workplace, dating, and family contexts
- **Groq GPT OSS Integration** for realistic character responses
- **Interactive Discord Commands** for easy scenario management
- **Session Management** to track user progress

## Quick Start

### 1. Prerequisites

- Python 3.8+
- Discord Bot Token
- Groq API Key

### 2. Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd flir_telegram

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
```

### 3. Configuration

Edit `.env` file with your credentials:

```env
# Discord Bot Configuration
DISCORD_BOT_TOKEN=your_discord_bot_token_here
DISCORD_GUILD_ID=your_discord_server_id_here

# Groq API Configuration
GROQ_API_KEY=your_groq_api_key_here

# Bot Configuration
BOT_PREFIX=!
DEBUG_MODE=True
```

### 4. Discord Bot Setup

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to "Bot" section and create a bot
4. Copy the bot token to your `.env` file
5. Enable "Message Content Intent" in bot settings
6. Invite bot to your server with appropriate permissions

### 5. Run the Bot

```bash
python discord_bot.py
```

## Available Commands

### Scenario Commands
- `!scenarios` - List all available scenarios
- `!scenario <id>` - Get details about a specific scenario
- `!scenarios workplace` - List workplace scenarios
- `!scenarios dating` - List dating scenarios
- `!scenarios family` - List family scenarios

### Character Commands
- `!characters` - List all available characters
- `!character <name>` - Get detailed character information
- `!talk <character>` - Talk to a character directly

### Session Commands
- `!start <scenario_id>` - Start a scenario session
- `!end` - End current session
- `!status` - Check current session status

### Utility Commands
- `!help` - Show help message
- `!ping` - Check bot latency
- `!test` - Test API connections

## Character Personas

### Workplace Characters
- **Marcus** - The Demanding Boss (Elon Musk-like)
- **Sarah** - The Supportive Coworker (Sheryl Sandberg-like)

### Dating Characters
- **Alex** - The Romantic Interest (Ryan Gosling-like)
- **Jordan** - The Supportive Friend (Oprah Winfrey-like)

### Family Characters
- **Patricia** - The Overbearing Parent (Tiger Mom archetype)
- **Michael** - The Understanding Sibling (Barack Obama-like)

### Coach Character
- **Kai** - The AI Coach (Tony Robbins-like)

## Available Scenarios

### Workplace Scenarios
1. **Unrealistic Deadline** - Practice addressing unrealistic project deadlines
2. **Giving Difficult Feedback** - Learn to deliver constructive feedback

### Dating Scenarios
1. **First Date Conversation** - Navigate first date interactions
2. **Defining the Relationship** - Practice "the talk" about relationship status

### Family Scenarios
1. **Setting Family Boundaries** - Learn to set healthy boundaries with family
2. **Family Financial Boundaries** - Practice saying no to financial requests

## Usage Example

```
!start workplace_deadline
!talk Marcus
I need to discuss the project timeline with you...
```

## Project Structure

```
flir_telegram/
├── discord_bot.py          # Main bot file
├── characters.py           # Character persona definitions
├── scenarios.py            # Scenario definitions
├── groq_client.py          # Groq API integration
├── config.py               # Configuration management
├── requirements.txt        # Python dependencies
├── .env.example           # Environment template
└── README.md              # This file
```

## Development

### Adding New Characters

1. Edit `characters.py`
2. Add new `CharacterPersona` to `CharacterManager._initialize_characters()`
3. Update scenario character lists in `scenarios.py`

### Adding New Scenarios

1. Edit `scenarios.py`
2. Add new `Scenario` to `ScenarioManager._initialize_scenarios()`
3. Update character scenario affinities if needed

### Testing

```bash
# Test API connections
!test

# Test character interaction
!start workplace_deadline
!talk Marcus
Hello, I need to discuss the project timeline.
```

## Troubleshooting

### Common Issues

1. **Bot not responding**: Check bot token and permissions
2. **API errors**: Verify Groq API key and rate limits
3. **Character not found**: Ensure character name matches exactly

### Debug Mode

Set `DEBUG_MODE=True` in `.env` for detailed logging.

## Future Enhancements

- Voice integration with ElevenLabs
- Progress tracking and analytics
- Custom character creation
- Multi-language support
- Advanced coaching features

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

[Add your license here]
