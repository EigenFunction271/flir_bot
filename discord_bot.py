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
        
        # Error tracking
        self.error_count = 0
        self.last_error_time = None
        self.max_errors_per_hour = 10
        
        # Load commands
        self.load_commands()
    
    def load_sessions(self):
        """Load active sessions from disk"""
        try:
            if self.session_file.exists():
                with open(self.session_file, 'rb') as f:
                    self.active_sessions = pickle.load(f)
                logger.info(f"✅ Loaded {len(self.active_sessions)} active sessions")
            else:
                logger.info("No existing sessions found")
        except Exception as e:
            logger.error(f"❌ Failed to load sessions: {e}")
            self.active_sessions = {}
    
    def save_sessions(self):
        """Save active sessions to disk"""
        try:
            with open(self.session_file, 'wb') as f:
                pickle.dump(self.active_sessions, f)
            logger.debug(f"💾 Saved {len(self.active_sessions)} active sessions")
        except Exception as e:
            logger.error(f"❌ Failed to save sessions: {e}")
    
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
    
    async def _end_conversation_with_feedback(self, ctx, user_id: int, session: Dict):
        """End conversation and generate feedback with error boundaries"""
        try:
            # Send conversation end message
            embed = discord.Embed(
                title="🏁 Conversation Complete!",
                description=f"Great job completing the **{session['scenario'].name}** scenario! Generating your personalized feedback...",
                color=0xff6600
            )
            await ctx.send(embed=embed)
            
            # Generate feedback with fallback
            await ctx.send("🤖 Analyzing your conversation and generating feedback...")
            
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
            await ctx.send(embed=feedback_embed)
            
            # Clean up session
            del self.active_sessions[user_id]
            self.save_sessions()
            
        except Exception as e:
            if not self.handle_error(e, "feedback generation"):
                await ctx.send("🚨 Bot is experiencing issues. Please try again later.")
                return
            
            logger.error(f"Error generating feedback: {e}")
            await ctx.send("❌ Error generating feedback. Session ended.")
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
    
    async def _end_conversation_with_feedback_dm(self, message, user_id: int, session: Dict):
        """End conversation and generate feedback for DM with error boundaries"""
        try:
            # Send conversation end message
            embed = discord.Embed(
                title="🏁 Conversation Complete!",
                description=f"Great job completing the **{session['scenario'].name}** scenario! Generating your personalized feedback...",
                color=0xff6600
            )
            await message.channel.send(embed=embed)
            
            # Generate feedback with fallback
            await message.channel.send("🤖 Analyzing your conversation and generating feedback...")
            
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
            await message.channel.send(embed=feedback_embed)
            
            # Clean up session
            del self.active_sessions[user_id]
            self.save_sessions()
            
        except Exception as e:
            if not self.handle_error(e, "DM feedback generation"):
                await message.channel.send("🚨 Bot is experiencing issues. Please try again later.")
                return
            
            logger.error(f"Error generating feedback: {e}")
            await message.channel.send("❌ Error generating feedback. Session ended.")
            if user_id in self.active_sessions:
                del self.active_sessions[user_id]
                self.save_sessions()
    
    def load_commands(self):
        """Load all bot commands"""
        
        @self.command(name="help", aliases=["h"])
        async def help_command(ctx):
            """Show available commands"""
            embed = discord.Embed(
                title="🤖 Flir Social Skills Training Bot",
                description="Practice difficult conversations with AI characters!",
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
`!character <name>` - Get character info
`!talk <character>` - Talk to a character directly""",
                inline=False
            )
            
            embed.add_field(
                name="🎮 Session Commands",
                value="""`!start <scenario_id>` - Start a scenario
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
            
            # Create session
            self.active_sessions[user_id] = {
                "scenario": scenario,
                "characters": characters,
                "context": scenario.context,
                "current_character": None,
                "conversation_history": [],
                "turn_count": 0
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
                name="👥 Available Characters",
                value="\n".join(f"• {char.name} - {char.personality_traits[0]}" for char in characters),
                inline=False
            )
            
            embed.add_field(
                name="💬 How to Interact",
                value="Use `!talk <character_name>` to start talking to a character, or `!end` to end the session.",
                inline=False
            )
            
            await ctx.send(embed=embed)
        
        @self.command(name="talk")
        async def talk_to_character(ctx, character_name: str, *, message: str = None):
            """Talk to a character with error boundaries"""
            try:
                user_id = ctx.author.id
                
                # Check if user has an active session
                if user_id not in self.active_sessions:
                    await ctx.send("❌ You don't have an active session. Use `!start <scenario_id>` to begin a scenario.")
                    return
                
                session = self.active_sessions[user_id]
                
                # Find character
                character = None
                for char in session["characters"]:
                    if char.name.lower() == character_name.lower():
                        character = char
                        break
                
                if not character:
                    available_chars = ", ".join([char.name for char in session["characters"]])
                    await ctx.send(f"❌ Character '{character_name}' not available in this scenario. Available: {available_chars}")
                    return
                
                # If no message provided, just set current character
                if not message:
                    session["current_character"] = character
                    self.save_sessions()
                    await ctx.send(f"👤 Now talking to **{character.name}**. Send your message to continue the conversation.")
                    return
                
                # Process the message with error boundaries
                await ctx.send(f"🤔 {character.name} is thinking...")
                
                # Add user message to conversation history
                session["conversation_history"].append({
                    "role": "user",
                    "content": message,
                    "character": character.name
                })
                
                # Increment turn count
                session["turn_count"] += 1
                
                # Generate response with fallback
                response = await self._generate_character_response_with_fallback(
                    message, character, session["conversation_history"]
                )
                
                # Add character response to conversation history
                session["conversation_history"].append({
                    "role": "assistant",
                    "content": response,
                    "character": character.name
                })
                
                # Send response
                embed = discord.Embed(
                    title=f"💬 {character.name}",
                    description=response,
                    color=0x0099ff
                )
                
                # Add turn counter to embed
                turns_remaining = Config.MAX_CONVERSATION_TURNS - session["turn_count"]
                embed.set_footer(text=f"Turn {session['turn_count']}/{Config.MAX_CONVERSATION_TURNS} • {turns_remaining} turns remaining")
                
                await ctx.send(embed=embed)
                
                # Save session state
                self.save_sessions()
                
                # Check if conversation should end
                if session["turn_count"] >= Config.MAX_CONVERSATION_TURNS:
                    await self._end_conversation_with_feedback(ctx, user_id, session)
                
            except Exception as e:
                if not self.handle_error(e, "character conversation"):
                    await ctx.send("🚨 Bot is experiencing issues. Please try again later.")
                    return
                
                logger.error(f"Error in character conversation: {e}")
                await ctx.send(f"❌ Sorry, I encountered an error. Please try again.")
    
    async def _generate_character_response_with_fallback(self, message: str, character: CharacterPersona, conversation_history: List[Dict]) -> str:
        """Generate character response with fallback mechanisms"""
        try:
            # Try Groq first
            response = await self.groq_client.generate_response_with_history(
                user_message=message,
                system_prompt=character.generate_system_prompt(),
                conversation_history=conversation_history,
                model_type="fast"
            )
            return response
        except Exception as e:
            logger.warning(f"Groq response generation failed: {e}")
            
            # Fallback to basic response
            try:
                response = await self.groq_client.generate_response(
                    user_message=message,
                    system_prompt=character.generate_system_prompt(),
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
        
        @self.command(name="end")
        async def end_session(ctx):
            """End current session"""
            user_id = ctx.author.id
            
            if user_id not in self.active_sessions:
                await ctx.send("❌ You don't have an active session to end.")
                return
            
            session = self.active_sessions[user_id]
            scenario_name = session["scenario"].name
            
            del self.active_sessions[user_id]
            
            embed = discord.Embed(
                title="🏁 Session Ended",
                description=f"Your session with **{scenario_name}** has ended. Great job practicing your social skills!",
                color=0xff6600
            )
            
            await ctx.send(embed=embed)
        
        @self.command(name="status")
        async def session_status(ctx):
            """Check current session status"""
            user_id = ctx.author.id
            
            if user_id not in self.active_sessions:
                await ctx.send("❌ You don't have an active session.")
                return
            
            session = self.active_sessions[user_id]
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
        
        # Handle direct messages to characters when in a session
        @self.event
        async def on_message(message):
            try:
                # Ignore bot messages
                if message.author.bot:
                    return
                
                # Process commands first
                await self.process_commands(message)
                
                # Handle direct messages to characters
                user_id = message.author.id
                if (user_id in self.active_sessions and 
                    not message.content.startswith(Config.BOT_PREFIX) and
                    message.guild is None):  # Direct message
                    
                    session = self.active_sessions[user_id]
                    current_char = session.get("current_character")
                    
                    if current_char:
                        await message.channel.send(f"🤔 {current_char.name} is thinking...")
                        
                        # Add user message to conversation history
                        session["conversation_history"].append({
                            "role": "user",
                            "content": message.content,
                            "character": current_char.name
                        })
                        
                        # Increment turn count
                        session["turn_count"] += 1
                        
                        # Generate response with fallback
                        response = await self._generate_character_response_with_fallback(
                            message.content, current_char, session["conversation_history"]
                        )
                        
                        # Add character response to conversation history
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
                        
                        # Add turn counter to embed
                        turns_remaining = Config.MAX_CONVERSATION_TURNS - session["turn_count"]
                        embed.set_footer(text=f"Turn {session['turn_count']}/{Config.MAX_CONVERSATION_TURNS} • {turns_remaining} turns remaining")
                        
                        await message.channel.send(embed=embed)
                        
                        # Save session state
                        self.save_sessions()
                        
                        # Check if conversation should end
                        if session["turn_count"] >= Config.MAX_CONVERSATION_TURNS:
                            await self._end_conversation_with_feedback_dm(message, user_id, session)
                        
            except Exception as e:
                if not self.handle_error(e, "message handling"):
                    if message.guild is None:  # DM
                        await message.channel.send("🚨 Bot is experiencing issues. Please try again later.")
                    return
                
                logger.error(f"Error in message handling: {e}")
                if message.guild is None:  # DM
                    await message.channel.send("❌ Sorry, I encountered an error. Please try again.")

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
        
        # Add periodic session saving
        async def save_sessions_periodically():
            while True:
                await asyncio.sleep(300)  # Save every 5 minutes
                try:
                    bot.save_sessions()
                except Exception as e:
                    logger.error(f"Error saving sessions: {e}")
        
        # Start session saving task
        asyncio.create_task(save_sessions_periodically())
        
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
