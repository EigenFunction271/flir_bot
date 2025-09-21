import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Discord Configuration
    DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
    
    # Safely parse DISCORD_GUILD_ID with error handling
    _guild_id_str = os.getenv("DISCORD_GUILD_ID", "0")
    try:
        DISCORD_GUILD_ID = int(_guild_id_str) if _guild_id_str else 0
    except ValueError:
        DISCORD_GUILD_ID = 0
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Invalid DISCORD_GUILD_ID '{_guild_id_str}', using default value 0")
    
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
    MAX_CONVERSATION_TURNS = 3
    
    @classmethod
    def validate(cls):
        """Validate that all required environment variables are set"""
        import logging
        logger = logging.getLogger(__name__)
        
        required_vars = ["DISCORD_BOT_TOKEN", "GROQ_API_KEY", "GEMINI_API_KEY"]
        missing_vars = [var for var in required_vars if not getattr(cls, var)]
        
        if missing_vars:
            logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
            logger.error("Please check your Render environment variables:")
            for var in missing_vars:
                logger.error(f"  - {var}")
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        logger.info("✅ All required environment variables are set")
        return True
