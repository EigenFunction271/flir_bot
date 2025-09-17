import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Discord Configuration
    DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
    DISCORD_GUILD_ID = int(os.getenv("DISCORD_GUILD_ID", 0))
    
    # Groq Configuration
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GROQ_BASE_URL = "https://api.groq.com/openai/v1"
    
    # Google Gemini Configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    # Model Configuration
    GROQ_MODELS = {
        "fast": "openai/gpt-oss-20b",
        "quality": "openai/gpt-oss-120b"
    }
    
    # Bot Configuration
    BOT_PREFIX = os.getenv("BOT_PREFIX", "!")
    DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"
    
    # Character Configuration
    MAX_RESPONSE_LENGTH = 500
    DEFAULT_TEMPERATURE = 0.7
    
    # Conversation Configuration
    MAX_CONVERSATION_TURNS = 5
    
    @classmethod
    def validate(cls):
        """Validate that all required environment variables are set"""
        required_vars = ["DISCORD_BOT_TOKEN", "GROQ_API_KEY", "GEMINI_API_KEY"]
        missing_vars = [var for var in required_vars if not getattr(cls, var)]
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return True
