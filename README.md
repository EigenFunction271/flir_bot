# Flir Discord Bot - Social Skills Training

A Discord bot that provides AI-powered social skills training through interactive scenarios with realistic character personas. Features automatic conversation turn tracking, context retention, and AI-generated feedback using Google Gemini Flash 2.0.

## ✨ Features

- **14 Pre-defined Character Personas** with unique personalities and communication styles
- **6 Training Scenarios** across workplace, dating, and family contexts
- **Groq GPT OSS Integration** for realistic character responses
- **Google Gemini Flash 2.0** for intelligent feedback generation
- **Conversation Context Retention** - Characters remember previous interactions
- **Automatic Turn Tracking** - Conversations end after 5 turns with feedback
- **Interactive Discord Commands** for easy scenario management
- **Session Management** to track user progress

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Discord Bot Token
- Groq API Key
- Google Gemini API Key

### Local Development Setup

#### 1. Clone and Install

```bash
# Clone the repository
git clone <your-repo-url>
cd flir_telegram

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### 2. Get API Keys

**Discord Bot Token:**
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create new application → Name it "Flir Bot"
3. Go to "Bot" section → Create bot
4. Copy token → Add to `.env` file

**Groq API Key:**
1. Go to [Groq Console](https://console.groq.com/)
2. Sign up/Login → Go to API Keys
3. Create new API key → Add to `.env` file

**Google Gemini API Key:**
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create new API key → Add to `.env` file

#### 3. Configuration

```bash
# Copy environment template
cp .env.example .env
```

Edit `.env` file:

```env
# Discord Bot Configuration
DISCORD_BOT_TOKEN=your_discord_bot_token_here
DISCORD_GUILD_ID=your_discord_server_id_here

# Groq API Configuration
GROQ_API_KEY=your_groq_api_key_here

# Google Gemini Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Bot Configuration
BOT_PREFIX=!
DEBUG_MODE=True
```

#### 4. Discord Bot Setup

1. **Enable Bot Permissions:**
   - Go to Discord Developer Portal → Your Bot
   - Enable "Message Content Intent"
   - Copy invite URL with these permissions:
     - Send Messages
     - Read Message History
     - Use Slash Commands
     - Embed Links

2. **Invite Bot to Server:**
   - Use the invite URL
   - Select your server
   - Authorize the bot

#### 5. Run Locally

```bash
python discord_bot.py
```

Test with:
```
!ping
!test
!help
```

## 🌐 Production Deployment with Render

### Render Backend Hosting

#### 1. Prepare for Deployment

Create `render.yaml` in your project root:

```yaml
services:
  - type: web
    name: flir-discord-bot
    env: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: python discord_bot.py
    envVars:
      - key: DISCORD_BOT_TOKEN
        sync: false
      - key: GROQ_API_KEY
        sync: false
      - key: GEMINI_API_KEY
        sync: false
      - key: DISCORD_GUILD_ID
        value: "0"
      - key: BOT_PREFIX
        value: "!"
      - key: DEBUG_MODE
        value: "False"
```

#### 2. Deploy to Render

1. **Connect Repository:**
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New" → "Web Service"
   - Connect your GitHub repository

2. **Configure Service:**
   - **Name:** `flir-discord-bot`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python discord_bot.py`

3. **Set Environment Variables:**
   - `DISCORD_BOT_TOKEN` - Your Discord bot token
   - `GROQ_API_KEY` - Your Groq API key
   - `GEMINI_API_KEY` - Your Google Gemini API key
   - `DISCORD_GUILD_ID` - Your Discord server ID (optional)
   - `BOT_PREFIX` - `!`
   - `DEBUG_MODE` - `False`

4. **Deploy:**
   - Click "Create Web Service"
   - Wait for deployment to complete
   - Check logs for successful startup

#### 3. Alternative: Railway Deployment

Create `railway.json`:

```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python discord_bot.py",
    "healthcheckPath": "/",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

Deploy to Railway:
1. Go to [Railway](https://railway.app/)
2. Connect GitHub repository
3. Set environment variables
4. Deploy automatically

#### 4. Environment Variables for Production

```env
# Required
DISCORD_BOT_TOKEN=your_production_bot_token
GROQ_API_KEY=your_groq_api_key
GEMINI_API_KEY=your_gemini_api_key

# Optional
DISCORD_GUILD_ID=your_server_id
BOT_PREFIX=!
DEBUG_MODE=False
```

## 🎮 Available Commands

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
- `!history` - View conversation history

### Utility Commands
- `!help` - Show help message
- `!ping` - Check bot latency
- `!test` - Test API connections

## 🎯 How It Works

### Conversation Flow
1. **Start Scenario:** `!start workplace_deadline`
2. **Select Character:** `!talk Marcus`
3. **Have Conversation:** 5 turns maximum
4. **Automatic Feedback:** AI analyzes your performance
5. **Try Again:** Start new scenario to improve

### Turn Tracking
- Each user message counts as 1 turn
- Conversations automatically end after 5 turns
- Turn counter shown in each character response
- Feedback generated using conversation context

### Feedback System
- **Google Gemini Flash 2.0** analyzes your conversation
- **Strengths:** What you did well
- **Areas for Improvement:** Specific suggestions
- **Actionable Tips:** Concrete advice for future conversations
- **Objective Assessment:** How well you met scenario goals

## 👥 Character Personas

### Workplace Characters (5)
- **Marcus** - The Demanding Boss (Elon Musk-like)
- **Sarah** - The Supportive Coworker (Sheryl Sandberg-like)
- **David** - The Competitive Colleague (Jeff Bezos-like)
- **Emma** - The Creative Perfectionist (Steve Jobs-like)
- **James** - The Analytical Conservative (Warren Buffett-like)

### Dating Characters (7)
- **Alex** - The Romantic Interest (Ryan Gosling-like)
- **Jordan** - The Supportive Friend (Oprah Winfrey-like)
- **Sam** - The Mysterious Intellectual (Keanu Reeves-like)
- **Taylor** - The Energetic Adventurer (Zendaya-like)
- **Riley** - The Confident Charmer (Ryan Reynolds-like)
- **Casey** - The Nurturing Empath (Emma Stone-like)

### Family Characters (2)
- **Patricia** - The Overbearing Parent (Tiger Mom archetype)
- **Michael** - The Understanding Sibling (Barack Obama-like)

### Coach Character (1)
- **Kai** - The AI Coach (Tony Robbins-like)

## 📋 Available Scenarios

### Workplace Scenarios
1. **Unrealistic Deadline** - Practice addressing unrealistic project deadlines
2. **Giving Difficult Feedback** - Learn to deliver constructive feedback

### Dating Scenarios
1. **First Date Conversation** - Navigate first date interactions
2. **Defining the Relationship** - Practice "the talk" about relationship status

### Family Scenarios
1. **Setting Family Boundaries** - Learn to set healthy boundaries with family
2. **Family Financial Boundaries** - Practice saying no to financial requests

## 💡 Usage Example

```
!start workplace_deadline
!talk Marcus
I need to discuss the project timeline with you...

Marcus: What's the issue with the current timeline?

!talk Marcus
The deadline is too aggressive for the scope.

Marcus: I understand your concern. Let's discuss what can be done...

[After 5 turns - automatic feedback generation]
```

## 🏗️ Project Structure

```
flir_telegram/
├── discord_bot.py          # Main bot file with commands and session management
├── characters.py           # 14 character persona definitions
├── scenarios.py            # 6 scenario definitions
├── groq_client.py          # Groq GPT OSS API integration
├── gemini_client.py        # Google Gemini Flash 2.0 feedback generation
├── config.py               # Configuration management
├── requirements.txt        # Python dependencies
├── .env.example           # Environment template
├── .gitignore             # Git ignore rules
├── render.yaml            # Render deployment configuration
├── character_expansion_guide.md  # Character expansion documentation
└── README.md              # This file
```

## 🔧 Development

### Adding New Characters

1. Edit `characters.py`
2. Add new `CharacterPersona` to `CharacterManager._initialize_characters()`
3. Update scenario character lists in `scenarios.py`
4. Assign unique voice ID for future TTS integration

### Adding New Scenarios

1. Edit `scenarios.py`
2. Add new `Scenario` to `ScenarioManager._initialize_scenarios()`
3. Update character scenario affinities if needed
4. Define clear objectives for feedback generation

### Testing

```bash
# Test all API connections
!test

# Test character interaction with turn tracking
!start workplace_deadline
!talk Marcus
Hello, I need to discuss the project timeline.

# View conversation history
!history

# Check session status
!status
```

## 🚨 Troubleshooting

### Common Issues

1. **Bot not responding**: 
   - Check Discord bot token and permissions
   - Verify "Message Content Intent" is enabled
   - Ensure bot is invited to server

2. **API errors**: 
   - Verify Groq API key and rate limits
   - Check Google Gemini API key
   - Monitor API usage and quotas

3. **Character not found**: 
   - Use exact character names (case-insensitive)
   - Check available characters with `!characters`

4. **Feedback not generating**:
   - Ensure Gemini API key is valid
   - Check conversation has at least 2 turns
   - Verify API quotas and limits

### Debug Mode

Set `DEBUG_MODE=True` in `.env` for detailed logging.

### Production Monitoring

- Monitor Render/Railway logs for errors
- Set up API usage alerts
- Track conversation completion rates
- Monitor feedback generation success

## 🚀 Future Enhancements

- **Voice Integration**: ElevenLabs TTS/STT for voice conversations
- **Progress Tracking**: User analytics and skill improvement metrics
- **Custom Characters**: User-created persona system
- **Multi-language Support**: International character personas
- **Advanced Coaching**: Real-time conversation coaching
- **Group Scenarios**: Multi-user training sessions
- **Mobile App**: Native mobile application
- **Enterprise Features**: Corporate training modules

## 📊 Performance & Costs

### API Usage Estimates (1000 active users/month)
- **Groq GPT OSS**: $100-300/month
- **Google Gemini**: $50-150/month
- **Discord API**: Free
- **Hosting (Render)**: $0-25/month

### Optimization Tips
- Use Groq 20B model for faster responses
- Cache character responses for common scenarios
- Implement conversation history limits
- Monitor and optimize API usage

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and test thoroughly
4. Commit your changes: `git commit -m 'Add amazing feature'`
5. Push to the branch: `git push origin feature/amazing-feature`
6. Submit a pull request

### Development Guidelines
- Follow existing code style and patterns
- Add comprehensive error handling
- Include tests for new features
- Update documentation for changes
- Ensure all API integrations are tested

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Groq** for fast, cost-effective language model inference
- **Google** for Gemini Flash 2.0 feedback generation
- **Discord** for the bot platform and API
- **Render** for reliable hosting infrastructure
