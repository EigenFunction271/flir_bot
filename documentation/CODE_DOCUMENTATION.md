# Flir Discord Bot - Code Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Core Components](#core-components)
4. [File Structure](#file-structure)
5. [Configuration](#configuration)
6. [Character System](#character-system)
7. [Scenario System](#scenario-system)
8. [AI Integration](#ai-integration)
9. [Session Management](#session-management)
10. [Discord Bot Implementation](#discord-bot-implementation)
11. [Error Handling](#error-handling)
12. [Deployment](#deployment)
13. [Development Guidelines](#development-guidelines)

## Project Overview

**Flir** is a Discord-based social skills training platform that uses AI-powered character personas to simulate realistic social interactions. Users practice difficult conversations in a safe, consequence-free environment through immersive role-playing scenarios.

### Key Features
- **14 Pre-defined Character Personas** with unique personalities and communication styles
- **6 Training Scenarios** across workplace, dating, and family contexts
- **Multi-Character Conversations** where multiple AI characters respond to create dynamic group interactions
- **AI-Powered Feedback** using Google Gemini Flash 2.0 for intelligent performance analysis
- **Session Management** with conversation history and turn tracking
- **Discord Integration** for seamless user experience

## Architecture

The application follows a modular architecture with clear separation of concerns:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Discord Bot   │    │  Character      │    │   Scenario      │
│   (discord_bot) │◄──►│  Manager        │◄──►│   Manager       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Session        │    │  Groq Client    │    │  Gemini Client  │
│  Management     │    │  (Character     │    │  (Feedback      │
│                 │    │   Responses)    │    │   Generation)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Core Components

### 1. Discord Bot (`discord_bot.py`)
The main application entry point that handles:
- Discord command processing
- User session management
- Multi-character response coordination
- Conversation flow control
- Feedback generation and delivery

### 2. Character System (`characters.py`)
Manages AI character personas including:
- Character definitions with personality traits
- Communication style specifications
- Scenario affinity mapping
- System prompt generation

### 3. Scenario System (`scenarios.py`)
Defines training scenarios with:
- Scenario contexts and objectives
- Character role assignments
- Difficulty levels
- Learning outcomes

### 4. AI Integration
- **Groq Client** (`groq_client.py`): Handles character response generation
- **Gemini Client** (`gemini_client.py`): Manages feedback generation and analysis

### 5. Configuration (`config.py`)
Centralized configuration management for:
- API keys and endpoints
- Bot settings
- Model parameters
- Environment validation

## File Structure

```
flir_telegram/
├── discord_bot.py          # Main bot application (1,751 lines)
├── characters.py           # Character persona definitions (408 lines)
├── scenarios.py            # Scenario definitions (604 lines)
├── groq_client.py          # Groq API integration (299 lines)
├── gemini_client.py        # Gemini API integration (490 lines)
├── config.py               # Configuration management (63 lines)
├── requirements.txt        # Python dependencies
├── render.yaml            # Render deployment configuration
├── documentation/         # Project documentation
│   ├── CODE_DOCUMENTATION.md
│   ├── flir_prd.md
│   ├── flir_project_description.md
│   └── ...
└── README.md              # Project overview and setup
```

## Configuration

### Environment Variables
The application requires the following environment variables:

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

### Configuration Class (`config.py`)
```python
class Config:
    # Discord Configuration
    DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
    DISCORD_GUILD_ID = int(os.getenv("DISCORD_GUILD_ID", "0"))
    
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
```

## Character System

### CharacterPersona Class
Each character is defined with comprehensive personality traits:

```python
@dataclass
class CharacterPersona:
    id: str
    name: str
    biography: str
    personality_traits: List[str]
    communication_style: str
    scenario_affinity: List[ScenarioType]
    reference: Optional[str] = None
    voice_id: Optional[str] = None
```

### Character Categories

#### Workplace Characters (5)
- **Marcus**: Demanding Boss (Elon Musk-like)
- **Sarah**: Supportive Coworker (Sheryl Sandberg-like)
- **David**: Competitive Colleague (Jeff Bezos-like)
- **Emma**: Creative Perfectionist (Steve Jobs-like)
- **James**: Analytical Conservative (Warren Buffett-like)

#### Dating Characters (7)
- **Alex**: Romantic Interest (Ryan Gosling-like)
- **Jordan**: Supportive Friend (Oprah Winfrey-like)
- **Sam**: Mysterious Intellectual (Keanu Reeves-like)
- **Taylor**: Energetic Adventurer (Zendaya-like)
- **Riley**: Confident Charmer (Ryan Reynolds-like)
- **Casey**: Nurturing Empath (Emma Stone-like)

#### Family Characters (2)
- **Patricia**: Overbearing Parent (Tiger Mom archetype)
- **Michael**: Understanding Sibling (Barack Obama-like)

#### Coach Character (1)
- **Kai**: AI Coach (Tony Robbins-like)

### System Prompt Generation
Characters generate dynamic system prompts based on scenario context:

```python
def generate_system_prompt(self, scenario_context: str = None, character_role_context: str = None) -> str:
    # Generates character-specific prompts with:
    # - Personality traits and communication style
    # - Scenario-specific behavior instructions
    # - Aggressive/supportive behavior based on context
    # - Response length and style guidelines
```

## Scenario System

### Scenario Class
```python
@dataclass
class Scenario:
    id: str
    name: str
    description: str
    scenario_type: ScenarioType
    characters: List[str]  # Character IDs
    objectives: List[str]
    context: str
    difficulty: str  # "beginner", "intermediate", "advanced"
    character_roles: Dict[str, str] = None
```

### Available Scenarios

#### Workplace Scenarios
1. **Unrealistic Deadline** - Practice addressing unrealistic project deadlines
2. **Giving Difficult Feedback** - Learn to deliver constructive feedback
3. **Reporting Workplace Harassment** - Navigate harassment situations
4. **Confronting Workplace Sabotage** - Handle workplace betrayal
5. **Facing Workplace Discrimination** - Address discriminatory behavior
6. **Confronting Workplace Bullying** - Stand up to workplace bullies

#### Dating Scenarios
1. **First Date Conversation** - Navigate first date interactions
2. **Defining the Relationship** - Practice "the talk" about relationship status
3. **Confronting a Ghost** - Handle being ghosted
4. **Discovering Infidelity** - Confront cheating behavior
5. **Leaving an Abusive Relationship** - End toxic relationships
6. **Escaping a Manipulative Partner** - Break free from manipulation

#### Family Scenarios
1. **Setting Family Boundaries** - Learn to set healthy boundaries
2. **Family Financial Boundaries** - Practice saying no to financial requests
3. **Confronting Family Addiction** - Address addiction issues
4. **Coming Out to Unsupportive Family** - Navigate coming out
5. **Confronting Family Manipulation** - Set boundaries with manipulative family
6. **Confronting Addiction Denial** - Handle denial about addiction

## AI Integration

### Groq Client (`groq_client.py`)
Handles character response generation with:

#### Key Features
- **Rate Limiting**: Prevents API quota exhaustion
- **Session Management**: Reuses HTTP connections for performance
- **Conversation History**: Maintains context across interactions
- **Character Memory**: Filters history for character-specific context
- **Fallback Mechanisms**: Graceful degradation when services fail

#### Response Generation
```python
async def generate_response_with_history(
    self, 
    user_message: str, 
    system_prompt: str, 
    conversation_history: List[Dict],
    model_type: str = "fast",
    current_character_name: str = None
) -> str:
    # Generates character responses with:
    # - Character-specific system prompts
    # - Filtered conversation history
    # - Rate limiting and error handling
    # - Session reuse for performance
```

### Gemini Client (`gemini_client.py`)
Manages feedback generation with:

#### Key Features
- **Structured Feedback**: Generates JSON-formatted feedback
- **Robust Parsing**: Handles malformed JSON responses
- **Field Extraction**: Extracts feedback components from text
- **Validation**: Ensures feedback completeness
- **Fallback Data**: Provides default feedback when generation fails

#### Feedback Generation
```python
async def generate_feedback(
    self, 
    conversation_history: List[Dict], 
    scenario_name: str,
    character_name: str,
    scenario_objectives: List[str],
    scenario_context: str = None,
    user_role_description: str = None
) -> dict:
    # Generates structured feedback with:
    # - Performance rating (1-10)
    # - Overall assessment
    # - Communication strengths
    # - Areas for improvement
    # - Key takeaways and actionable tips
```

## Session Management

### Session Structure
```python
session = {
    "scenario": Scenario,
    "characters": List[CharacterPersona],
    "context": str,
    "current_character": CharacterPersona,
    "conversation_history": List[Dict],
    "turn_count": int,
    "created_at": datetime
}
```

### Session Persistence
- **File-based Storage**: Sessions saved to `active_sessions.json`
- **Atomic Operations**: Temporary files prevent corruption
- **Backup System**: Automatic backup before saves
- **Expiration Handling**: 30-minute session timeout
- **Recovery**: Graceful handling of corrupted session files

### Session Lifecycle
1. **Creation**: User starts scenario with `!start <scenario_id>`
2. **Character Selection**: First character becomes current character
3. **Conversation**: Multi-character responses to user messages
4. **Turn Tracking**: Automatic conversation end after 3 turns
5. **Feedback**: AI-generated performance analysis
6. **Cleanup**: Session removal and state reset

## Discord Bot Implementation

### Bot Architecture
```python
class FlirBot(commands.Bot):
    def __init__(self):
        # Initialize components
        self.character_manager = CharacterManager()
        self.scenario_manager = ScenarioManager()
        self.groq_client = GroqClient()
        self.gemini_client = GeminiClient()
        
        # Session management
        self.active_sessions: Dict[int, Dict] = {}
        self.session_file = Path("active_sessions.json")
        
        # Error tracking
        self.error_count = 0
        self.max_errors_per_hour = 10
```

### Command System
The bot implements a comprehensive command system:

#### Scenario Commands
- `!scenarios` - List all available scenarios
- `!scenario-details <id>` - Get detailed scenario information
- `!scenarios workplace` - Filter scenarios by type

#### Character Commands
- `!characters` - List all available characters
- `!character <name>` - Get character information

#### Session Commands
- `!start <scenario_id>` - Start a scenario session
- `!end` - End current session
- `!status` - Check session status
- `!history` - View conversation history

#### Utility Commands
- `!help` - Show help message
- `!ping` - Check bot latency
- `!test` - Test API connections

### Multi-Character Response System
The bot implements sophisticated multi-character conversations:

```python
async def _generate_multi_character_responses(self, user_message: str, session: Dict, channel):
    # Generates responses from all scenario characters
    # - Sequential response generation
    # - Character-specific role context
    # - Conversation history sharing
    # - Turn counter management
    # - Error handling per character
```

### Message Handling
```python
async def on_message(self, message):
    # Handles incoming messages with:
    # - Command processing
    # - Session validation
    # - Character switching detection
    # - Input validation
    # - Multi-character response generation
    # - Turn tracking and conversation end
```

## Error Handling

### Error Boundaries
The application implements comprehensive error handling:

#### Error Tracking
```python
def handle_error(self, error: Exception, context: str = ""):
    # Centralized error handling with:
    # - Error counting and rate limiting
    # - Context logging
    # - Safe mode activation
    # - Graceful degradation
```

#### Fallback Mechanisms
- **API Failures**: Fallback to alternative responses
- **Session Corruption**: Automatic recovery and cleanup
- **Rate Limiting**: Automatic retry with backoff
- **Connection Issues**: Session persistence and recovery

#### Input Validation
```python
def validate_user_input(self, message: str) -> tuple[bool, str]:
    # Validates user input with:
    # - Length and content checks
    # - Spam detection
    # - Security filtering
    # - Command injection prevention
```

## Deployment

### Render Configuration (`render.yaml`)
```yaml
services:
  - type: web
    name: flir-discord-bot
    env: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: python discord_bot.py
    healthCheckPath: /health
    envVars:
      - key: DISCORD_BOT_TOKEN
        sync: false
      - key: GROQ_API_KEY
        sync: false
      - key: GEMINI_API_KEY
        sync: false
```

### Health Check System
```python
async def health_check(request):
    # Provides health status for monitoring
    # - Bot readiness check
    # - Timestamp information
    # - Error status reporting
```

### Graceful Shutdown
```python
async def graceful_shutdown():
    # Handles shutdown with:
    # - Session persistence
    # - Connection cleanup
    # - Resource deallocation
    # - Error logging
```

## Development Guidelines

### Code Style
- **Type Hints**: Comprehensive type annotations
- **Error Handling**: Try-catch blocks with specific error types
- **Logging**: Structured logging with context
- **Documentation**: Inline comments and docstrings

### Testing
- **API Testing**: Connection tests for all services
- **Session Testing**: State management validation
- **Character Testing**: Personality consistency checks
- **Scenario Testing**: Objective achievement validation

### Performance Considerations
- **Session Reuse**: HTTP connection pooling
- **Rate Limiting**: API quota management
- **Memory Management**: Session cleanup and garbage collection
- **Response Caching**: Character response optimization

### Security
- **Input Validation**: Comprehensive user input filtering
- **API Key Protection**: Environment variable management
- **Session Security**: File-based session encryption
- **Content Moderation**: Inappropriate content filtering

### Monitoring
- **Error Tracking**: Centralized error logging
- **Performance Metrics**: Response time monitoring
- **Usage Analytics**: Session and scenario completion tracking
- **Health Checks**: Automated system status monitoring

## Future Enhancements

### Planned Features
- **Voice Integration**: ElevenLabs TTS/STT for voice conversations
- **Progress Tracking**: User analytics and skill improvement metrics
- **Custom Characters**: User-created persona system
- **Multi-language Support**: International character personas
- **Advanced Coaching**: Real-time conversation coaching
- **Group Scenarios**: Multi-user training sessions

### Technical Improvements
- **Database Integration**: Persistent user data storage
- **Caching System**: Response and session caching
- **Load Balancing**: Horizontal scaling support
- **Microservices**: Service decomposition for scalability

---

*This documentation provides a comprehensive overview of the Flir Discord Bot codebase. For specific implementation details, refer to the individual source files and their inline documentation.*
