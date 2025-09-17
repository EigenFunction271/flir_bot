# Flir Discord Bot Setup Guide

## Step-by-Step Implementation Guide

### Phase 1: Environment Setup (15 minutes)

#### 1.1 Install Dependencies
```bash
pip install -r requirements.txt
```

#### 1.2 Get API Keys

**Discord Bot Token:**
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" → Name it "Flir Bot"
3. Go to "Bot" section → Click "Add Bot"
4. Copy the token → Add to `.env` file

**Groq API Key:**
1. Go to [Groq Console](https://console.groq.com/)
2. Sign up/Login → Go to API Keys
3. Create new API key → Add to `.env` file

#### 1.3 Configure Environment
```bash
# Copy the example file
cp .env.example .env

# Edit .env with your actual values
DISCORD_BOT_TOKEN=your_actual_token_here
GROQ_API_KEY=your_actual_key_here
DISCORD_GUILD_ID=your_server_id_here
```

### Phase 2: Discord Bot Setup (10 minutes)

#### 2.1 Bot Permissions
In Discord Developer Portal → Bot section:
- Enable "Message Content Intent"
- Copy the bot invite URL
- Add these permissions: Send Messages, Read Message History, Use Slash Commands

#### 2.2 Invite Bot to Server
1. Use the invite URL from step 2.1
2. Select your server
3. Authorize the bot

### Phase 3: Test Basic Functionality (10 minutes)

#### 3.1 Start the Bot
```bash
python discord_bot.py
```

#### 3.2 Test Commands
In your Discord server:
```
!ping
!test
!help
!scenarios
```

#### 3.3 Test Character Interaction
```
!start workplace_deadline
!talk Marcus
Hello, I need to discuss the project timeline with you.
```

### Phase 4: Verify All Features (15 minutes)

#### 4.1 Test All Scenarios
```
!scenarios workplace
!scenarios dating  
!scenarios family
!scenario workplace_deadline
```

#### 4.2 Test All Characters
```
!characters
!character Marcus
!character Sarah
```

#### 4.3 Test Session Management
```
!start workplace_deadline
!status
!talk Sarah
!end
```

## Quick Test Script

Create `test_bot.py` to verify everything works:

```python
import asyncio
from groq_client import GroqClient
from characters import CharacterManager
from scenarios import ScenarioManager

async def test_setup():
    print("🔍 Testing Flir Bot Setup...")
    
    # Test Groq connection
    try:
        groq = GroqClient()
        result = await groq.test_connection()
        print(f"✅ Groq API: {'Working' if result else 'Failed'}")
    except Exception as e:
        print(f"❌ Groq API Error: {e}")
    
    # Test character system
    try:
        char_manager = CharacterManager()
        characters = char_manager.list_all_characters()
        print(f"✅ Characters: {len(characters)} loaded")
    except Exception as e:
        print(f"❌ Character System Error: {e}")
    
    # Test scenario system
    try:
        scenario_manager = ScenarioManager()
        scenarios = scenario_manager.list_all_scenarios()
        print(f"✅ Scenarios: {len(scenarios)} loaded")
    except Exception as e:
        print(f"❌ Scenario System Error: {e}")
    
    print("🎉 Setup test complete!")

if __name__ == "__main__":
    asyncio.run(test_setup())
```

Run the test:
```bash
python test_bot.py
```

## Troubleshooting

### Common Issues

**1. "Missing required environment variables"**
- Check your `.env` file exists and has correct values
- Ensure no extra spaces around the `=` sign

**2. "Groq API error"**
- Verify your API key is correct
- Check if you have API credits available
- Ensure you're using the correct model names

**3. "Bot not responding"**
- Check bot token is correct
- Verify bot has "Message Content Intent" enabled
- Ensure bot is invited to your server with proper permissions

**4. "Character not found"**
- Use exact character names (case-insensitive)
- Check available characters with `!characters`

### Debug Mode

Enable debug logging by setting in `.env`:
```
DEBUG_MODE=True
```

## Next Steps

Once basic functionality is working:

1. **Customize Characters**: Edit personality traits in `characters.py`
2. **Add Scenarios**: Create new scenarios in `scenarios.py`
3. **Test Interactions**: Try different conversation flows
4. **Monitor Performance**: Check response times and quality
5. **Plan Voice Integration**: Prepare for ElevenLabs TTS/STT integration

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify all API keys and permissions
3. Test individual components with the test script
4. Check Discord bot logs for error messages
