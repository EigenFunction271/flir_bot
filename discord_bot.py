import discord
from discord.ext import commands
import asyncio
import logging
from typing import Optional, Dict, List, Any
import json
import os
from aiohttp import web
import threading
import traceback
from datetime import datetime, timedelta
import pickle
from pathlib import Path
import re

from config import Config
from characters import CharacterManager, CharacterPersona, ScenarioType
from scenarios import ScenarioManager, Scenario
from groq_client import GroqClient
from gemini_client import GeminiClient

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('flir_bot.log')
    ]
)
logger = logging.getLogger(__name__)

class FlirBot(commands.Bot):
    """Main Discord bot for Flir social skills training"""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        
        super().__init__(
            command_prefix=Config.BOT_PREFIX,
            intents=intents,
            help_command=None
        )
        
        # Initialize components with error handling
        try:
            self.character_manager = CharacterManager()
            self.scenario_manager = ScenarioManager()
            self.groq_client = GroqClient()
            self.gemini_client = GeminiClient()
            logger.info("✅ All components initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize components: {e}")
            raise
        
        # Active sessions with persistence
        self.active_sessions: Dict[int, Dict] = {}
        self.session_file = Path("active_sessions.pkl")
        self.load_sessions()
        
        # Session timeout (30 minutes)
        self.session_timeout = 30 * 60  # 30 minutes in seconds
        
        # Error tracking
        self.error_count = 0
        self.last_error_time = None
        self.max_errors_per_hour = 10
        
        # Load commands
        self.load_commands()
    
    def load_sessions(self):
        """Load active sessions from disk and validate them"""
        try:
            if self.session_file.exists():
                # Check file size to avoid loading corrupted files
                file_size = self.session_file.stat().st_size
                if file_size == 0:
                    logger.warning("Session file is empty, starting with empty sessions")
                    self.active_sessions = {}
                    return
                
                if file_size > 10 * 1024 * 1024:  # 10MB limit
                    logger.error("Session file too large, starting with empty sessions")
                    self.active_sessions = {}
                    return
                
                with open(self.session_file, 'rb') as f:
                    self.active_sessions = pickle.load(f)
                
                # Validate session structure
                if not isinstance(self.active_sessions, dict):
                    logger.error("Invalid session file format, starting with empty sessions")
                    self.active_sessions = {}
                    return
                
                # Validate and clean up expired sessions
                expired_sessions = []
                for user_id, session in self.active_sessions.items():
                    if not isinstance(session, dict):
                        logger.warning(f"Invalid session format for user {user_id}, removing")
                        expired_sessions.append(user_id)
                        continue
                    
                    if self._is_session_expired(session):
                        expired_sessions.append(user_id)
                
                # Remove expired sessions
                for user_id in expired_sessions:
                    del self.active_sessions[user_id]
                    logger.info(f"🗑️ Removed expired session for user {user_id}")
                
                if expired_sessions:
                    self.save_sessions()  # Save cleaned sessions
                
                logger.info(f"✅ Loaded {len(self.active_sessions)} active sessions")
            else:
                logger.info("No existing sessions found")
        except (pickle.PickleError, EOFError, FileNotFoundError) as e:
            logger.error(f"❌ Failed to load sessions (corrupted file): {e}")
            # Backup corrupted file
            if self.session_file.exists():
                backup_file = self.session_file.with_suffix('.bak')
                self.session_file.rename(backup_file)
                logger.info(f"Backed up corrupted session file to {backup_file}")
            self.active_sessions = {}
        except Exception as e:
            logger.error(f"❌ Failed to load sessions: {e}")
            self.active_sessions = {}
    
    def _is_session_expired(self, session: Dict) -> bool:
        """Check if a session has expired"""
        if "created_at" not in session:
            # Old sessions without timestamp are considered expired
            return True
        
        created_at = session["created_at"]
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        
        return (datetime.now() - created_at).total_seconds() > self.session_timeout
    
    def save_sessions(self):
        """Save active sessions to disk"""
        try:
            # Create backup before saving
            if self.session_file.exists():
                backup_file = self.session_file.with_suffix('.bak')
                self.session_file.rename(backup_file)
            
            # Save to temporary file first, then rename (atomic operation)
            temp_file = self.session_file.with_suffix('.tmp')
            with open(temp_file, 'wb') as f:
                pickle.dump(self.active_sessions, f)
            
            # Atomic rename
            temp_file.rename(self.session_file)
            logger.debug(f"💾 Saved {len(self.active_sessions)} active sessions")
            
        except Exception as e:
            logger.error(f"❌ Failed to save sessions: {e}")
            # Try to restore backup if it exists
            backup_file = self.session_file.with_suffix('.bak')
            if backup_file.exists():
                try:
                    backup_file.rename(self.session_file)
                    logger.info("Restored session backup after save failure")
                except Exception as restore_error:
                    logger.error(f"Failed to restore backup: {restore_error}")
    
    def check_error_rate(self) -> bool:
        """Check if error rate is too high"""
        now = datetime.now()
        if self.last_error_time and (now - self.last_error_time) < timedelta(hours=1):
            if self.error_count >= self.max_errors_per_hour:
                logger.critical(f"🚨 Error rate too high: {self.error_count} errors in the last hour")
                return False
        else:
            # Reset counter if more than an hour has passed
            self.error_count = 0
            self.last_error_time = now
        return True
    
    def handle_error(self, error: Exception, context: str = ""):
        """Centralized error handling"""
        self.error_count += 1
        self.last_error_time = datetime.now()
        
        logger.error(f"❌ Error in {context}: {str(error)}")
        logger.error(f"📊 Error count: {self.error_count}")
        
        if not self.check_error_rate():
            logger.critical("🚨 Bot entering safe mode due to high error rate")
            return False
        return True
    
    def validate_user_input(self, message: str) -> tuple[bool, str]:
        """
        Validate user input for safety and length
        
        Returns:
            tuple: (is_valid, error_message)
        """
        if not message or not message.strip():
            return False, "Message cannot be empty"
        
        if len(message) > 2000:  # Discord message limit
            return False, "Message is too long (max 2000 characters)"
        
        if len(message.strip()) < 1:
            return False, "Message must contain at least one character"
        
        # Basic content filtering
        dangerous_patterns = [
            r'<script.*?>',  # Script tags
            r'javascript:',  # JavaScript URLs
            r'data:text/html',  # Data URLs
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                return False, "Message contains potentially unsafe content"
        
        return True, ""
    
    def detect_character_switch(self, message: str, available_characters: List) -> Optional[Any]:
        """
        Detect if the user is trying to switch to a different character by name
        
        Args:
            message: The user's message
            available_characters: List of available character objects
            
        Returns:
            Character object if a switch is detected, None otherwise
        """
        message_lower = message.lower()
        
        # Phrases that indicate the user is correcting or addressing a character, not switching
        correction_phrases = [
            "you're not", "you are not", "youre not", "youre not",
            "that's not", "thats not", "that is not",
            "wrong", "incorrect", "mistake",
            "stop", "don't", "dont"
        ]
        
        # Check if this is a correction rather than a switch request
        is_correction = any(phrase in message_lower for phrase in correction_phrases)
        if is_correction:
            logger.info(f"🔄 SWITCH: Detected correction phrase, not switching characters")
            return None
        
        # Look for explicit switch requests
        switch_phrases = [
            "talk to", "speak to", "switch to", "i want to talk to",
            "let me talk to", "can i talk to", "i need to talk to"
        ]
        
        has_switch_phrase = any(phrase in message_lower for phrase in switch_phrases)
        
        # Look for character names in the message
        for character in available_characters:
            char_name_lower = character.name.lower()
            
            # Check for direct name mentions
            if char_name_lower in message_lower:
                # Make sure it's not just a partial match in the middle of a word
                import re
                pattern = r'\b' + re.escape(char_name_lower) + r'\b'
                if re.search(pattern, message_lower):
                    # Only switch if there's an explicit switch phrase OR if it's a simple name mention
                    if has_switch_phrase or (len(message_lower.split()) <= 3 and char_name_lower in message_lower.split()):
                        logger.info(f"🔄 SWITCH: Detected switch request to {character.name}")
                        return character
                    else:
                        logger.info(f"🔄 SWITCH: Character {character.name} mentioned but no switch phrase detected")
        
        return None
    
    async def _end_conversation_with_feedback(self, ctx_or_message, user_id: int, session: Dict):
        """End conversation and generate feedback with error boundaries"""
        try:
            # Send conversation end message
            embed = discord.Embed(
                title="🏁 Conversation Complete!",
                description=f"Great job completing the **{session['scenario'].name}** scenario! Generating your personalized feedback...",
                color=0xff6600
            )
            # Handle both ctx and message objects
            if hasattr(ctx_or_message, 'send'):
                await ctx_or_message.send(embed=embed)
            else:
                await ctx_or_message.channel.send(embed=embed)
            
            # Generate feedback with fallback
            if hasattr(ctx_or_message, 'send'):
                await ctx_or_message.send("🤖 Analyzing your conversation and generating feedback...")
            else:
                await ctx_or_message.channel.send("🤖 Analyzing your conversation and generating feedback...")
            
            current_character = session.get("current_character")
            character_name = current_character.name if current_character else "Unknown"
            
            feedback = await self._generate_feedback_with_fallback(
                session["conversation_history"],
                session["scenario"].name,
                character_name,
                session["scenario"].objectives
            )
            
            # Send feedback
            feedback_embed = discord.Embed(
                title="📊 Your Performance Feedback",
                description=f"**Scenario:** {session['scenario'].name}\n**Character:** {character_name}\n**Turns:** {session['turn_count']}",
                color=0x00ff00
            )
            
            # Split feedback into chunks if too long
            if len(feedback) > 2000:
                # Split by sections
                sections = feedback.split('\n\n')
                for section in sections[:3]:  # Show first 3 sections
                    if section.strip():
                        feedback_embed.add_field(
                            name="📝 Feedback",
                            value=section[:1000] + "..." if len(section) > 1000 else section,
                            inline=False
                        )
            else:
                feedback_embed.add_field(
                    name="📝 Feedback",
                    value=feedback,
                    inline=False
                )
            
            feedback_embed.set_footer(text="Use !start <scenario_id> to try another scenario!")
            if hasattr(ctx_or_message, 'send'):
                await ctx_or_message.send(embed=feedback_embed)
            else:
                await ctx_or_message.channel.send(embed=feedback_embed)
            
            # Clean up session
            del self.active_sessions[user_id]
            self.save_sessions()
            
        except Exception as e:
            if not self.handle_error(e, "feedback generation"):
                if hasattr(ctx_or_message, 'send'):
                    await ctx_or_message.send("🚨 Bot is experiencing issues. Please try again later.")
                else:
                    await ctx_or_message.channel.send("🚨 Bot is experiencing issues. Please try again later.")
                return
            
            logger.error(f"Error generating feedback: {e}")
            if hasattr(ctx_or_message, 'send'):
                await ctx_or_message.send("❌ Error generating feedback. Session ended.")
            else:
                await ctx_or_message.channel.send("❌ Error generating feedback. Session ended.")
            if user_id in self.active_sessions:
                del self.active_sessions[user_id]
                self.save_sessions()
    
    async def _generate_feedback_with_fallback(self, conversation_history: List[Dict], scenario_name: str, character_name: str, objectives: List[str]) -> str:
        """Generate feedback with fallback mechanisms"""
        try:
            # Try Gemini first
            feedback = await self.gemini_client.generate_feedback(
                conversation_history=conversation_history,
                scenario_name=scenario_name,
                character_name=character_name,
                scenario_objectives=objectives
            )
            return feedback
        except Exception as e:
            logger.warning(f"Gemini feedback generation failed: {e}")
            
            # Fallback to Groq
            try:
                feedback_prompt = f"""Provide constructive feedback on this social skills conversation:

Scenario: {scenario_name}
Character: {character_name}
Objectives: {', '.join(objectives)}

Conversation:
{self._format_conversation_for_feedback(conversation_history)}

Give feedback on:
1. Communication strengths
2. Areas for improvement  
3. Key takeaways
4. Overall assessment

Keep it constructive and specific."""
                
                feedback = await self.groq_client.generate_response(
                    user_message=feedback_prompt,
                    system_prompt="You are a social skills coach providing constructive feedback.",
                    model_type="fast"
                )
                return feedback
            except Exception as e2:
                logger.error(f"Groq fallback also failed: {e2}")
                
                # Final fallback - basic feedback
                return self._generate_basic_feedback(conversation_history, scenario_name, character_name)
    
    def _format_conversation_for_feedback(self, conversation_history: List[Dict]) -> str:
        """Format conversation history for feedback analysis"""
        formatted = []
        for msg in conversation_history:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            character = msg.get("character", "")
            
            if role == "user":
                formatted.append(f"USER: {content}")
            elif role == "assistant":
                formatted.append(f"{character}: {content}")
        
        return "\n".join(formatted)
    
    def _generate_basic_feedback(self, conversation_history: List[Dict], scenario_name: str, character_name: str) -> str:
        """Generate basic feedback when all AI services fail"""
        turn_count = len([msg for msg in conversation_history if msg.get("role") == "user"])
        
        return f"""**Basic Feedback for {scenario_name}**

**Conversation Summary:**
- You completed {turn_count} turns with {character_name}
- Scenario: {scenario_name}

**General Tips:**
- Practice active listening and asking follow-up questions
- Be authentic and genuine in your responses
- Pay attention to the other person's emotional cues
- Practice setting boundaries when needed

**Next Steps:**
- Try the scenario again with a different approach
- Focus on one specific skill you want to improve
- Consider practicing with different characters

*Note: Advanced feedback analysis is temporarily unavailable.*"""
    
    
    def load_commands(self):
        """Load all bot commands"""
        logger.info("🔧 Loading bot commands...")
        
        @self.command(name="help", aliases=["h"])
        async def help_command(ctx):
            """Show available commands"""
            embed = discord.Embed(
                title="🤖 Flir Social Skills Training Bot",
                description="Practice difficult conversations with AI characters! Multiple characters will respond to create dynamic group conversations.",
                color=0x00ff00
            )
            
            embed.add_field(
                name="📋 Scenario Commands",
                value="""`!scenarios` - List all available scenarios
`!scenario-details <id>` - Get detailed scenario info
`!scenarios workplace` - List workplace scenarios
`!scenarios dating` - List dating scenarios
`!scenarios family` - List family scenarios""",
                inline=False
            )
            
            embed.add_field(
                name="👥 Character Commands",
                value="""`!characters` - List all characters
`!character <name>` - Get character info""",
                inline=False
            )
            
            embed.add_field(
                name="🎮 Session Commands",
                value="""`!start <scenario_id>` - Start a scenario (character will message you first!)
`!end` - End current session
`!status` - Check current session status
`!history` - View conversation history""",
                inline=False
            )
            
            embed.add_field(
                name="ℹ️ Info Commands",
                value="""`!help` - Show this help message
`!ping` - Check bot status
`!test` - Test API connections""",
                inline=False
            )
            
            await ctx.send(embed=embed)
        
        @self.command(name="ping")
        async def ping(ctx):
            """Check bot latency"""
            latency = round(self.latency * 1000)
            await ctx.send(f"🏓 Pong! Latency: {latency}ms")
        
        @self.command(name="debug")
        async def debug_info(ctx):
            """Show debug information about the bot"""
            embed = discord.Embed(
                title="🔧 Debug Information",
                color=0x0099ff
            )
            
            # List all registered commands
            commands = [cmd.name for cmd in self.commands]
            embed.add_field(
                name="📋 Registered Commands",
                value=", ".join(commands) if commands else "No commands found",
                inline=False
            )
            
            # Bot prefix
            embed.add_field(
                name="🔤 Bot Prefix",
                value=f"`{Config.BOT_PREFIX}`",
                inline=True
            )
            
            # Active sessions count
            embed.add_field(
                name="👥 Active Sessions",
                value=str(len(self.active_sessions)),
                inline=True
            )
            
            # Error count
            embed.add_field(
                name="❌ Error Count",
                value=str(self.error_count),
                inline=True
            )
            
            await ctx.send(embed=embed)
        
        @self.command(name="test-message")
        async def test_message_handling(ctx):
            """Test message handling and session state"""
            user_id = ctx.author.id
            
            embed = discord.Embed(
                title="🧪 Message Handling Test",
                color=0x0099ff
            )
            
            # Check if user has active session
            has_session = user_id in self.active_sessions
            embed.add_field(
                name="📊 Has Active Session",
                value="✅ Yes" if has_session else "❌ No",
                inline=True
            )
            
            if has_session:
                session = self.active_sessions[user_id]
                current_char = session.get("current_character")
                embed.add_field(
                    name="🎭 Current Character",
                    value=current_char.name if current_char else "None",
                    inline=True
                )
                embed.add_field(
                    name="🎬 Scenario",
                    value=session.get("scenario", {}).get("name", "Unknown"),
                    inline=True
                )
                embed.add_field(
                    name="🔄 Turn Count",
                    value=str(session.get("turn_count", 0)),
                    inline=True
                )
            
            embed.add_field(
                name="🔤 Bot Prefix",
                value=f"`{Config.BOT_PREFIX}`",
                inline=True
            )
            
            embed.add_field(
                name="📨 Message Channel",
                value="DM" if ctx.guild is None else f"#{ctx.channel.name}",
                inline=True
            )
            
            await ctx.send(embed=embed)
        
        @self.command(name="test")
        async def test_connections(ctx):
            """Test API connections with error boundaries"""
            try:
                await ctx.send("🔍 Testing connections...")
                
                # Test Groq connection
                groq_working = False
                try:
                    groq_working = await self.groq_client.test_connection()
                    groq_status = "✅ Working" if groq_working else "❌ Failed"
                except Exception as e:
                    groq_status = f"❌ Error: {str(e)}"
                    self.handle_error(e, "Groq connection test")
                
                # Test Gemini connection
                gemini_working = False
                try:
                    gemini_working = await self.gemini_client.test_connection()
                    gemini_status = "✅ Working" if gemini_working else "❌ Failed"
                except Exception as e:
                    gemini_status = f"❌ Error: {str(e)}"
                    self.handle_error(e, "Gemini connection test")
                
                all_working = groq_working and gemini_working
                
                embed = discord.Embed(
                    title="🔧 Connection Test Results",
                    color=0x00ff00 if all_working else 0xff0000
                )
                embed.add_field(name="Groq API", value=groq_status, inline=False)
                embed.add_field(name="Gemini API", value=gemini_status, inline=False)
                
                if all_working:
                    embed.add_field(name="Status", value="🎉 All systems ready for social skills training!", inline=False)
                else:
                    embed.add_field(name="Status", value="⚠️ Some services unavailable. Check your API keys.", inline=False)
                
                await ctx.send(embed=embed)
                
            except Exception as e:
                if not self.handle_error(e, "connection test"):
                    await ctx.send("🚨 Bot is experiencing issues. Please try again later.")
                    return
                
                logger.error(f"Error in connection test: {e}")
                await ctx.send("❌ Error testing connections. Please try again later.")
        
        @self.command(name="scenarios", aliases=["scenario"])
        async def list_scenarios(ctx, scenario_type: str = None):
            """List available scenarios"""
            if scenario_type:
                # Filter by type
                try:
                    scenario_enum = ScenarioType(scenario_type.lower())
                    scenarios = self.scenario_manager.get_scenarios_by_type(scenario_enum)
                except ValueError:
                    await ctx.send(f"❌ Invalid scenario type. Use: workplace, dating, or family")
                    return
            else:
                scenarios = self.scenario_manager.list_all_scenarios()
            
            if not scenarios:
                await ctx.send("❌ No scenarios found.")
                return
            
            embed = discord.Embed(
                title=f"📋 Available Scenarios ({len(scenarios)})",
                color=0x0099ff
            )
            
            for scenario in scenarios[:10]:  # Limit to 10 to avoid message length issues
                embed.add_field(
                    name=f"`{scenario.id}` - {scenario.name}",
                    value=f"*{scenario.description}*\n**Difficulty:** {scenario.difficulty.title()}",
                    inline=False
                )
            
            if len(scenarios) > 10:
                embed.set_footer(text=f"Showing 10 of {len(scenarios)} scenarios. Use !scenario-details <id> for details.")
            
            await ctx.send(embed=embed)
        
        @self.command(name="scenario-details", aliases=["scenario-info"])
        async def scenario_details(ctx, scenario_id: str):
            """Get detailed information about a specific scenario"""
            scenario = self.scenario_manager.get_scenario(scenario_id)
            if not scenario:
                await ctx.send(f"❌ Scenario '{scenario_id}' not found. Use `!scenarios` to see available scenarios.")
                return
            
            summary = self.scenario_manager.get_scenario_summary(scenario_id)
            
            embed = discord.Embed(
                title=f"📋 {scenario.name}",
                description=scenario.description,
                color=0x0099ff
            )
            
            embed.add_field(
                name="🎯 Objectives",
                value="\n".join(f"• {obj}" for obj in scenario.objectives),
                inline=False
            )
            
            embed.add_field(
                name="👥 Characters",
                value=", ".join(scenario.characters),
                inline=True
            )
            
            embed.add_field(
                name="📊 Difficulty",
                value=scenario.difficulty.title(),
                inline=True
            )
            
            embed.add_field(
                name="🎮 Start Scenario",
                value=f"Use `!start {scenario_id}` to begin",
                inline=False
            )
            
            await ctx.send(embed=embed)
        
        @self.command(name="characters", aliases=["character"])
        async def list_characters(ctx, character_name: str = None):
            """List all characters or get character details"""
            if character_name:
                character = self.character_manager.get_character_by_name(character_name)
                if not character:
                    await ctx.send(f"❌ Character '{character_name}' not found.")
                    return
                
                embed = discord.Embed(
                    title=f"👤 {character.name}",
                    color=0xff9900
                )
                
                embed.add_field(
                    name="🎭 Personality Traits",
                    value=", ".join(character.personality_traits),
                    inline=False
                )
                
                embed.add_field(
                    name="💬 Communication Style",
                    value=character.communication_style,
                    inline=False
                )
                
                embed.add_field(
                    name="🎯 Scenario Types",
                    value=", ".join([t.value for t in character.scenario_affinity]),
                    inline=False
                )
                
                if character.reference:
                    embed.add_field(
                        name="🎬 Reference",
                        value=character.reference,
                        inline=True
                    )
                
            else:
                characters = self.character_manager.list_all_characters()
                
                embed = discord.Embed(
                    title=f"👥 Available Characters ({len(characters)})",
                    color=0xff9900
                )
                
                for char in characters:
                    embed.add_field(
                        name=char.name,
                        value=f"*{', '.join(char.personality_traits[:3])}...*",
                        inline=True
                    )
            
            await ctx.send(embed=embed)
        
        @self.command(name="start")
        async def start_scenario(ctx, scenario_id: str):
            """Start a scenario session"""
            user_id = ctx.author.id
            
            # Check if user already has an active session
            if user_id in self.active_sessions:
                await ctx.send("❌ You already have an active session. Use `!end` to end it first.")
                return
            
            # Get scenario
            scenario = self.scenario_manager.get_scenario(scenario_id)
            if not scenario:
                await ctx.send(f"❌ Scenario '{scenario_id}' not found. Use `!scenarios` to see available scenarios.")
                return
            
            # Get characters for this scenario
            characters = []
            for char_id in scenario.characters:
                char = self.character_manager.get_character(char_id)
                if char:
                    characters.append(char)
            
            if not characters:
                await ctx.send("❌ No valid characters found for this scenario.")
                return
            
            # Select the first character as the key character
            key_character = characters[0]
            
            # Create session with the key character already selected
            self.active_sessions[user_id] = {
                "scenario": scenario,
                "characters": characters,
                "context": scenario.context,
                "current_character": key_character,
                "conversation_history": [],
                "turn_count": 0,
                "created_at": datetime.now()
            }
            
            # Send scenario introduction
            embed = discord.Embed(
                title=f"🎬 Starting: {scenario.name}",
                description=scenario.description,
                color=0x00ff00
            )
            
            embed.add_field(
                name="📝 Context",
                value=scenario.context[:1000] + "..." if len(scenario.context) > 1000 else scenario.context,
                inline=False
            )
            
            embed.add_field(
                name="🎯 Objectives",
                value="\n".join(f"• {obj}" for obj in scenario.objectives),
                inline=False
            )
            
            embed.add_field(
                name="👤 Key Character",
                value=f"**{key_character.name}** - {key_character.personality_traits[0]}",
                inline=False
            )
            
            embed.add_field(
                name="💬 How to Interact",
                value=f"**All characters** will send you opening messages to start the conversation. Respond directly to their messages in DMs! All characters will respond to your messages, creating dynamic group conversations.",
                inline=False
            )
            
            await ctx.send(embed=embed)
            
            # Generate and send opening messages from all characters
            try:
                # Send opening messages to user's DM
                try:
                    dm_channel = await ctx.author.create_dm()
                    
                    # Get all characters in the scenario except coach
                    scenario_characters = []
                    for char_id in scenario.characters:
                        if char_id.lower() != "kai":  # Exclude coach
                            character = self.character_manager.get_character(char_id)
                            if character:
                                scenario_characters.append(character)
                    
                    # Generate opening message from each character
                    for character in scenario_characters:
                        try:
                            # Create opening message prompt for this character
                            opening_prompt = f"""Start the conversation by sending an opening message to the user. This should be the first thing you say to them in this scenario. Be authentic to your character and set the tone for the interaction.

Scenario: {scenario.name}
Context: {scenario.context}

This is the start of a social skills training conversation. Be true to your character's personality and communication style."""
                            
                            # Generate opening message with scenario context
                            opening_message = await self._generate_character_response_with_fallback(
                                opening_prompt, character, [], scenario.context
                            )
                            
                            # Add the opening message to conversation history
                            self.active_sessions[user_id]["conversation_history"].append({
                                "role": "assistant",
                                "content": opening_message,
                                "character": character.name
                            })
                            
                            # Create embed for this character's opening message
                            opening_embed = discord.Embed(
                                title=f"💬 {character.name}",
                                description=opening_message,
                                color=0x0099ff
                            )
                            
                            opening_embed.set_footer(text=f"Turn 1/{Config.MAX_CONVERSATION_TURNS} • {Config.MAX_CONVERSATION_TURNS - 1} turns remaining")
                            
                            await dm_channel.send(embed=opening_embed)
                            
                            # Small delay between character messages for better flow
                            await asyncio.sleep(1)
                            
                        except Exception as e:
                            logger.error(f"Error generating opening message for character {character.name}: {e}")
                            continue
                    
                    # Save session state
                    self.save_sessions()
                    
                    # Send confirmation in the original channel
                    character_names = [char.name for char in scenario_characters]
                    await ctx.send(f"✅ **{', '.join(character_names)}** have sent you opening messages! Check your DMs to continue the conversation.")
                    
                except discord.Forbidden:
                    await ctx.send(f"❌ I couldn't send you a DM. Please check your privacy settings and allow DMs from server members.")
                    
            except Exception as e:
                logger.error(f"Error generating opening messages: {e}")
                await ctx.send(f"❌ Error starting the conversation. Please try again.")
        
        @self.command(name="status")
        async def session_status(ctx):
            """Check current session status"""
            user_id = ctx.author.id
            
            if user_id not in self.active_sessions:
                await ctx.send("❌ You don't have an active session.")
                return
            
            session = self.active_sessions[user_id]
            
            # Validate session structure
            if not isinstance(session, dict) or "scenario" not in session:
                logger.error(f"Invalid session structure for user {user_id}")
                del self.active_sessions[user_id]
                await ctx.send("❌ Your session is corrupted. Please start a new scenario.")
                return
            
            scenario = session["scenario"]
            current_char = session.get("current_character")
            
            embed = discord.Embed(
                title="📊 Session Status",
                color=0x00ff00
            )
            
            embed.add_field(
                name="🎬 Current Scenario",
                value=scenario.name,
                inline=True
            )
            
            embed.add_field(
                name="👤 Current Character",
                value=current_char.name if current_char else "None selected",
                inline=True
            )
            
            embed.add_field(
                name="🔄 Turn Count",
                value=f"{session['turn_count']}/{Config.MAX_CONVERSATION_TURNS}",
                inline=True
            )
            
            embed.add_field(
                name="👥 Available Characters",
                value=", ".join([char.name for char in session["characters"]]),
                inline=False
            )
            
            await ctx.send(embed=embed)
        
        @self.command(name="history", aliases=["chat"])
        async def conversation_history(ctx):
            """View conversation history for current session"""
            user_id = ctx.author.id
            
            if user_id not in self.active_sessions:
                await ctx.send("❌ You don't have an active session.")
                return
            
            session = self.active_sessions[user_id]
            
            # Validate session structure
            if not isinstance(session, dict) or "scenario" not in session:
                logger.error(f"Invalid session structure for user {user_id}")
                del self.active_sessions[user_id]
                await ctx.send("❌ Your session is corrupted. Please start a new scenario.")
                return
            
            history = session.get("conversation_history", [])
            
            if not history:
                await ctx.send("📝 No conversation history yet. Start talking to a character!")
                return
            
            embed = discord.Embed(
                title="📝 Conversation History",
                description=f"**Scenario:** {session['scenario'].name}",
                color=0x0099ff
            )
            
            # Show last 10 messages to avoid embed limits
            recent_history = history[-10:] if len(history) > 10 else history
            
            for i, msg in enumerate(recent_history, 1):
                role_emoji = "👤" if msg["role"] == "user" else "🤖"
                character_name = msg.get("character", "Unknown")
                
                # Truncate long messages
                content = msg["content"]
                if len(content) > 200:
                    content = content[:200] + "..."
                
                embed.add_field(
                    name=f"{role_emoji} {character_name if msg['role'] == 'assistant' else 'You'}",
                    value=content,
                    inline=False
                )
            
            if len(history) > 10:
                embed.set_footer(text=f"Showing last 10 of {len(history)} messages")
            
            await ctx.send(embed=embed)
        
        @self.command(name="end")
        async def end_session(ctx):
            """End current session"""
            user_id = ctx.author.id
            logger.info(f"🔍 END COMMAND: User {user_id} ({ctx.author.name}) called !end")
            
            if user_id not in self.active_sessions:
                logger.warning(f"⚠️ END COMMAND: User {user_id} has no active session to end")
                await ctx.send("❌ You don't have an active session to end.")
                return
            
            session = self.active_sessions[user_id]
            
            # Validate session structure
            if not isinstance(session, dict) or "scenario" not in session:
                logger.error(f"Invalid session structure for user {user_id}")
                del self.active_sessions[user_id]
                await ctx.send("❌ Your session is corrupted. Please start a new scenario.")
                return
            
            scenario_name = session["scenario"].name
            
            # Clean up session
            del self.active_sessions[user_id]
            self.save_sessions()  # Save the updated sessions
            
            embed = discord.Embed(
                title="🏁 Session Ended",
                description=f"Your session with **{scenario_name}** has ended. Great job practicing your social skills!",
                color=0xff6600
            )
            
            await ctx.send(embed=embed)
        
        logger.info("✅ All bot commands loaded successfully")
    
    async def on_message(self, message):
        try:
            # Ignore bot messages
            if message.author.bot:
                return
            
            logger.info(f"📨 MESSAGE: Received message from {message.author.name} ({message.author.id}): '{message.content[:100]}...' in {message.guild.name if message.guild else 'DM'}")
        
            # Process commands first
            await self.process_commands(message)
            logger.info(f"✅ MESSAGE: Processed commands for message from {message.author.name}")
        
            # Handle direct messages to characters
            user_id = message.author.id
            logger.info(f"🔍 MESSAGE: Checking if user {user_id} has active session and message is not a command")
            logger.info(f"📊 MESSAGE: User in active sessions: {user_id in self.active_sessions}")
            logger.info(f"📊 MESSAGE: Message starts with prefix '{Config.BOT_PREFIX}': {message.content.startswith(Config.BOT_PREFIX)}")
            logger.info(f"📊 MESSAGE: Is DM: {message.guild is None}")
            
            if (user_id in self.active_sessions and 
                not message.content.startswith(Config.BOT_PREFIX) and
                message.guild is None):  # Direct message only
            
                session = self.active_sessions[user_id]
                
                # Validate session structure
                if not isinstance(session, dict) or "scenario" not in session:
                    logger.error(f"Invalid session structure for user {user_id}")
                    del self.active_sessions[user_id]
                    await message.channel.send("❌ Your session is corrupted. Please start a new scenario.")
                    return
                
                current_char = session.get("current_character")
                available_characters = session.get("characters", [])
                logger.info(f"🎭 MESSAGE: Current character for user {user_id}: {current_char.name if current_char else 'None'}")
                
                # Check if user is trying to switch to a different character
                target_character = self.detect_character_switch(message.content, available_characters)
                
                if target_character and target_character != current_char:
                    # User is switching to a different character
                    logger.info(f"🔄 MESSAGE: User {user_id} switching from {current_char.name if current_char else 'None'} to {target_character.name}")
                    session["current_character"] = target_character
                    current_char = target_character
                    self.save_sessions()
                    
                    # Send confirmation of character switch
                    await message.channel.send(f"👤 Now talking to **{target_character.name}**")
                
                if current_char:
                    # Validate user input
                    logger.info(f"🔍 MESSAGE: Validating user input: '{message.content[:50]}...'")
                    is_valid, error_msg = self.validate_user_input(message.content)
                    if not is_valid:
                        logger.warning(f"❌ MESSAGE: Input validation failed: {error_msg}")
                        await message.channel.send(f"❌ {error_msg}")
                        return
                    logger.info(f"✅ MESSAGE: Input validation passed")
                    
                    logger.info(f"🤔 MESSAGE: Sending thinking message for {current_char.name}")
                    await message.channel.send(f"🤔 {current_char.name} is thinking...")
                
                    # Add user message to conversation history
                    session["conversation_history"].append({
                        "role": "user",
                        "content": message.content,
                        "character": current_char.name
                    })
                    logger.info(f"📝 MESSAGE: Added user message to conversation history. Total messages: {len(session['conversation_history'])}")
                
                    # Increment turn count
                    session["turn_count"] += 1
                    logger.info(f"🔄 MESSAGE: Incremented turn count to {session['turn_count']}")
                
                    # Generate responses from all characters in the scenario (except coach)
                    logger.info(f"🎭 MESSAGE: Starting multi-character response generation for {len(session['scenario'].characters)} characters")
                    await self._generate_multi_character_responses(
                        message.content, session, message.channel
                    )
                    logger.info(f"✅ MESSAGE: Completed multi-character response generation")
                
                    # Save session state
                    self.save_sessions()
                
                    # Check if conversation should end
                    if session["turn_count"] >= Config.MAX_CONVERSATION_TURNS:
                        await self._end_conversation_with_feedback(message, user_id, session)
                
        except Exception as e:
            if not self.handle_error(e, "message handling"):
                if message.guild is None:  # DM
                    await message.channel.send("🚨 Bot is experiencing issues. Please try again later.")
                return
        
            logger.error(f"Error in message handling: {e}")
            if message.guild is None:  # DM
                await message.channel.send("❌ Sorry, I encountered an error. Please try again.")
    
    async def _generate_character_response_with_fallback(self, message: str, character: CharacterPersona, conversation_history: List[Dict], scenario_context: str = None, character_role_context: str = None) -> str:
        """Generate character response with fallback mechanisms"""
        try:
            # Generate character-specific system prompt with role context
            system_prompt = character.generate_system_prompt(scenario_context, character_role_context)
            logger.info(f"🎭 SYSTEM: Generated system prompt for {character.name}: {system_prompt[:100]}...")
            if character_role_context:
                logger.info(f"🎭 ROLE: Character role context for {character.name}: {character_role_context[:100]}...")
            
            # Try Groq first with character-specific memory
            response = await self.groq_client.generate_response_with_history(
                user_message=message,
                system_prompt=system_prompt,
                conversation_history=conversation_history,
                model_type="fast",
                current_character_name=character.name
            )
            return response
        except Exception as e:
            logger.warning(f"Groq response generation failed: {e}")
            
            # Fallback to basic response (without history)
            try:
                response = await self.groq_client.generate_response(
                    user_message=message,
                    system_prompt=system_prompt,
                    model_type="fast"
                )
                return response
            except Exception as e2:
                logger.error(f"Groq fallback also failed: {e2}")
                
                # Final fallback - basic response
                return self._generate_basic_character_response(character, message)
    
    def _generate_basic_character_response(self, character: CharacterPersona, message: str) -> str:
        """Generate basic character response when all AI services fail"""
        return f"*{character.name} is having trouble responding right now. They seem to be thinking about what you said: '{message[:50]}...'*"
    
    async def _generate_multi_character_responses(self, user_message: str, session: Dict, channel):
        """Generate responses from all characters in the scenario (except coach)"""
        try:
            logger.info(f"🎭 MULTI-CHAR: Starting multi-character response generation")
            logger.info(f"🎭 MULTI-CHAR: Scenario characters: {session['scenario'].characters}")
            logger.info(f"🎭 MULTI-CHAR: Current conversation history length: {len(session['conversation_history'])}")
            
            # Get all characters in the scenario except coach
            scenario_characters = []
            for char_id in session["scenario"].characters:
                logger.info(f"🎭 MULTI-CHAR: Processing character ID: {char_id}")
                if char_id.lower() != "kai":  # Exclude coach
                    character = self.character_manager.get_character(char_id)
                    if character:
                        scenario_characters.append(character)
                        logger.info(f"🎭 MULTI-CHAR: Added character: {character.name}")
                    else:
                        logger.warning(f"🎭 MULTI-CHAR: Character not found: {char_id}")
                else:
                    logger.info(f"🎭 MULTI-CHAR: Excluded coach character: {char_id}")
            
            logger.info(f"🎭 MULTI-CHAR: Found {len(scenario_characters)} characters to respond")
            
            if not scenario_characters:
                logger.warning("No characters found for multi-character response")
                return
            
            # Generate responses from each character SEQUENTIALLY
            # This ensures each character sees previous character responses in the same turn
            for character in scenario_characters:
                try:
                    logger.info(f"🎭 MULTI-CHAR: Generating response for {character.name}")
                    logger.info(f"🎭 MULTI-CHAR: Current conversation history length: {len(session['conversation_history'])}")
                    
                    # Get character-specific role context from scenario
                    character_role_context = session["scenario"].get_character_role_context(character.id)
                    
                    # Generate response for this character using CURRENT conversation history
                    response = await self._generate_character_response_with_fallback(
                        user_message, character, session["conversation_history"], session["scenario"].context, character_role_context
                    )
                    logger.info(f"🎭 MULTI-CHAR: Generated response for {character.name}: {response[:50]}...")
                    
                    # Add character response to conversation history IMMEDIATELY
                    # This ensures the next character sees this response
                    session["conversation_history"].append({
                        "role": "assistant",
                        "content": response,
                        "character": character.name
                    })
                    logger.info(f"🎭 MULTI-CHAR: Added {character.name}'s response to history. New length: {len(session['conversation_history'])}")
                    
                    # Create embed for this character's response
                    embed = discord.Embed(
                        title=f"💬 {character.name}",
                        description=response,
                        color=0x0099ff
                    )
                    
                    # Add turn counter to embed
                    turns_remaining = Config.MAX_CONVERSATION_TURNS - session["turn_count"]
                    embed.set_footer(text=f"Turn {session['turn_count']}/{Config.MAX_CONVERSATION_TURNS} • {turns_remaining} turns remaining")
                    
                    # Send the response
                    logger.info(f"🎭 MULTI-CHAR: Sending response from {character.name}")
                    await channel.send(embed=embed)
                    logger.info(f"🎭 MULTI-CHAR: Successfully sent response from {character.name}")
                    
                    # Small delay between character responses for better flow
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Error generating response for character {character.name}: {e}")
                    # Continue with other characters even if one fails
                    continue
                    
        except Exception as e:
            logger.error(f"Error in multi-character response generation: {e}")
            # Fallback to single character response
            current_char = session.get("current_character")
            if current_char:
                character_role_context = session["scenario"].get_character_role_context(current_char.id)
                response = await self._generate_character_response_with_fallback(
                    user_message, current_char, session["conversation_history"], session["scenario"].context, character_role_context
                )
                
                session["conversation_history"].append({
                    "role": "assistant",
                    "content": response,
                    "character": current_char.name
                })
                
                embed = discord.Embed(
                    title=f"💬 {current_char.name}",
                    description=response,
                    color=0x0099ff
                )
                
                turns_remaining = Config.MAX_CONVERSATION_TURNS - session["turn_count"]
                embed.set_footer(text=f"Turn {session['turn_count']}/{Config.MAX_CONVERSATION_TURNS} • {turns_remaining} turns remaining")
                
                await channel.send(embed=embed)

async def health_check(request):
    """Health check endpoint for Render with error boundaries"""
    try:
        # Basic health check
        status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "bot_ready": True,
            "message": "Flir Bot is running!"
        }
        
        return web.json_response(status, status=200)
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return web.json_response(
            {"status": "unhealthy", "error": str(e)}, 
            status=500
        )

async def start_web_server():
    """Start a simple web server for health checks with error boundaries"""
    try:
        app = web.Application()
        app.router.add_get('/', health_check)
        app.router.add_get('/health', health_check)
        
        runner = web.AppRunner(app)
        await runner.setup()
        
        port = int(os.getenv('PORT', 8000))
        site = web.TCPSite(runner, '0.0.0.0', port)
        await site.start()
        logger.info(f"✅ Health check server started on port {port}")
    except Exception as e:
        logger.error(f"Failed to start web server: {e}")
        raise

async def main():
    """Main function to run the bot with error boundaries"""
    try:
        # Validate configuration
        Config.validate()
        logger.info("✅ Configuration validated successfully")
        
        # Start health check server
        await start_web_server()
        logger.info("✅ Health check server started")
        
        # Create and run bot
        bot = FlirBot()
        logger.info("✅ Bot initialized successfully")
        logger.info(f"📋 Bot has {len(bot.commands)} commands registered")
        logger.info(f"🔤 Bot prefix: '{Config.BOT_PREFIX}'")
        
        # Add periodic session saving and cleanup
        async def save_sessions_periodically():
            while True:
                await asyncio.sleep(300)  # Save every 5 minutes
                try:
                    bot.save_sessions()
                except Exception as e:
                    logger.error(f"Error saving sessions: {e}")
        
        async def cleanup_expired_sessions():
            while True:
                await asyncio.sleep(600)  # Check every 10 minutes
                try:
                    expired_sessions = []
                    for user_id, session in bot.active_sessions.items():
                        if bot._is_session_expired(session):
                            expired_sessions.append(user_id)
                    
                    if expired_sessions:
                        for user_id in expired_sessions:
                            del bot.active_sessions[user_id]
                            logger.info(f"🗑️ Cleaned up expired session for user {user_id}")
                        bot.save_sessions()
                except Exception as e:
                    logger.error(f"Error cleaning up sessions: {e}")
        
        # Start background tasks
        asyncio.create_task(save_sessions_periodically())
        asyncio.create_task(cleanup_expired_sessions())
        
        # Add graceful shutdown handler
        async def graceful_shutdown():
            logger.info("🔄 Gracefully shutting down bot...")
            try:
                # Save all active sessions
                bot.save_sessions()
                logger.info("✅ Sessions saved successfully")
                
                # Close HTTP sessions
                if hasattr(bot, 'groq_client'):
                    await bot.groq_client.close()
                
                # Close bot connection
                await bot.close()
                logger.info("✅ Bot shutdown complete")
            except Exception as e:
                logger.error(f"Error during shutdown: {e}")
        
        # Register shutdown handler
        import signal
        import sys
        
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating graceful shutdown...")
            asyncio.create_task(graceful_shutdown())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Start the bot
        await bot.start(Config.DISCORD_BOT_TOKEN)
        
    except Exception as e:
        logger.critical(f"Failed to start bot: {e}")
        logger.critical(f"Traceback: {traceback.format_exc()}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
