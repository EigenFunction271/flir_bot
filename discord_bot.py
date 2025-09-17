import discord
from discord.ext import commands
import asyncio
import logging
from typing import Optional, Dict, List
import json

from config import Config
from characters import CharacterManager, CharacterPersona, ScenarioType
from scenarios import ScenarioManager, Scenario
from groq_client import GroqClient

# Set up logging
logging.basicConfig(level=logging.INFO)
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
        
        # Initialize components
        self.character_manager = CharacterManager()
        self.scenario_manager = ScenarioManager()
        self.groq_client = GroqClient()
        
        # Active sessions: {user_id: {"scenario": Scenario, "characters": [CharacterPersona], "context": str}}
        self.active_sessions: Dict[int, Dict] = {}
        
        # Load commands
        self.load_commands()
    
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
`!scenario <id>` - Start a specific scenario
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
`!status` - Check current session status""",
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
            """Test API connections"""
            await ctx.send("🔍 Testing connections...")
            
            # Test Groq connection
            try:
                groq_working = await self.groq_client.test_connection()
                groq_status = "✅ Working" if groq_working else "❌ Failed"
            except Exception as e:
                groq_status = f"❌ Error: {str(e)}"
            
            embed = discord.Embed(
                title="🔧 Connection Test Results",
                color=0x00ff00 if groq_working else 0xff0000
            )
            embed.add_field(name="Groq API", value=groq_status, inline=False)
            
            await ctx.send(embed=embed)
        
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
                embed.set_footer(text=f"Showing 10 of {len(scenarios)} scenarios. Use !scenario <id> for details.")
            
            await ctx.send(embed=embed)
        
        @self.command(name="scenario")
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
                "current_character": None
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
            """Talk to a character"""
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
                await ctx.send(f"👤 Now talking to **{character.name}**. Send your message to continue the conversation.")
                return
            
            # Process the message
            try:
                await ctx.send(f"🤔 {character.name} is thinking...")
                
                # Generate response
                response = await self.groq_client.generate_response(
                    user_message=message,
                    system_prompt=character.generate_system_prompt(),
                    model_type="fast"  # Use fast model for now
                )
                
                # Send response
                embed = discord.Embed(
                    title=f"💬 {character.name}",
                    description=response,
                    color=0x0099ff
                )
                
                await ctx.send(embed=embed)
                
            except Exception as e:
                logger.error(f"Error generating response: {e}")
                await ctx.send(f"❌ Sorry, I encountered an error. Please try again.")
        
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
                name="👥 Available Characters",
                value=", ".join([char.name for char in session["characters"]]),
                inline=False
            )
            
            await ctx.send(embed=embed)
        
        # Handle direct messages to characters when in a session
        @self.event
        async def on_message(message):
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
                    try:
                        await message.channel.send(f"🤔 {current_char.name} is thinking...")
                        
                        response = await self.groq_client.generate_response(
                            user_message=message.content,
                            system_prompt=current_char.generate_system_prompt(),
                            model_type="fast"
                        )
                        
                        embed = discord.Embed(
                            title=f"💬 {current_char.name}",
                            description=response,
                            color=0x0099ff
                        )
                        
                        await message.channel.send(embed=embed)
                        
                    except Exception as e:
                        logger.error(f"Error in character response: {e}")
                        await message.channel.send("❌ Sorry, I encountered an error. Please try again.")

async def main():
    """Main function to run the bot"""
    try:
        # Validate configuration
        Config.validate()
        
        # Create and run bot
        bot = FlirBot()
        await bot.start(Config.DISCORD_BOT_TOKEN)
        
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
