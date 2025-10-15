"""
Development and Debugging Tools for Character System

Provides SudoLang-style commands for testing and debugging character behaviors:
- /test_mood [character] [mood] [message] - Test specific mood response
- /craft_response [character] [scenario] - Generate response with reasoning shown
- /list_rules [character] [mood] - Show active mood behavior rules
- /show_prompt [character] [mood] [message] - Display the full system prompt
- /mood_pipeline [character] [message] - Show step-by-step mood inference
"""

import asyncio
import logging
from typing import Optional, Dict, List
from characters import CharacterManager, CharacterMood, MoodState, CharacterPersona
from mood_inference import MoodInferenceSystem

logger = logging.getLogger(__name__)


class CharacterDevTools:
    """Development tools for testing and debugging character system"""
    
    def __init__(self, llm_client):
        """
        Initialize with LLM client for testing
        
        Args:
            llm_client: GeminiClient or GroqClient instance
        """
        self.char_manager = CharacterManager()
        self.mood_system = MoodInferenceSystem(llm_client)
        self.llm_client = llm_client
        logger.info("✅ CharacterDevTools initialized")
    
    def list_characters(self) -> List[str]:
        """List all available characters"""
        return self.char_manager.get_character_names()
    
    def test_mood(
        self,
        character_id: str,
        mood: str,
        user_message: str,
        scenario_context: str = "Test scenario"
    ) -> str:
        """
        /test_mood - Test how character responds in a specific mood
        
        Args:
            character_id: Character ID (e.g., "marcus")
            mood: Mood to test (e.g., "angry", "skeptical")
            user_message: Sample user message
            scenario_context: Scenario context
            
        Returns:
            Formatted output showing the character's response behavior
        """
        character = self.char_manager.get_character(character_id)
        if not character:
            return f"❌ Character '{character_id}' not found"
        
        try:
            mood_enum = CharacterMood(mood.lower())
        except ValueError:
            available = [m.value for m in CharacterMood]
            return f"❌ Invalid mood '{mood}'. Available: {', '.join(available)}"
        
        # Create mood state
        mood_state = MoodState(
            current_mood=mood_enum,
            intensity=0.7,
            reason=f"Testing {mood} mood",
            trigger_keywords=["test"]
        )
        
        # Generate prompt
        prompt = character.generate_dynamic_prompt(
            mood_state=mood_state,
            user_message=user_message,
            scenario_context=scenario_context,
            character_role_context="Test character interaction"
        )
        
        # Format output
        output = f"""
╔══════════════════════════════════════════════════════════════════
║ TEST MOOD: {character.name} in {mood.upper()} mood
╚══════════════════════════════════════════════════════════════════

📝 User Message: "{user_message}"

🎭 Character: {character.name}
😤 Mood: {mood_enum.value} (intensity: 0.7)
🎯 Scenario: {scenario_context}

═══════════════════════════════════════════════════════════════════
GENERATED SYSTEM PROMPT:
═══════════════════════════════════════════════════════════════════

{prompt}

═══════════════════════════════════════════════════════════════════
"""
        return output
    
    def list_rules(
        self,
        character_id: str,
        mood: Optional[str] = None
    ) -> str:
        """
        /list_rules - List mood behavior rules for a character
        
        Args:
            character_id: Character ID
            mood: Optional specific mood to filter by
            
        Returns:
            Formatted list of behavior rules
        """
        character = self.char_manager.get_character(character_id)
        if not character:
            return f"❌ Character '{character_id}' not found"
        
        # Filter rules by mood if specified
        rules = character.mood_behavior_rules
        if mood:
            try:
                mood_enum = CharacterMood(mood.lower())
                rules = [r for r in rules if r.mood == mood_enum]
            except ValueError:
                return f"❌ Invalid mood '{mood}'"
        
        # Format output
        output = f"""
╔══════════════════════════════════════════════════════════════════
║ MOOD BEHAVIOR RULES: {character.name}
╚══════════════════════════════════════════════════════════════════

Total Rules: {len(rules)}
{f"Filtered by Mood: {mood.upper()}" if mood else "Showing All Moods"}

"""
        
        for i, rule in enumerate(rules, 1):
            output += f"""───────────────────────────────────────────────────────────────────
Rule #{i}: {rule.mood.value.upper()}
───────────────────────────────────────────────────────────────────
Triggers: {', '.join(f'"{kw}"' for kw in rule.trigger_keywords)}
Min Intensity: {rule.intensity_threshold}

Behaviors:
"""
            for behavior in rule.behaviors:
                output += f"  • {behavior}\n"
            output += "\n"
        
        return output
    
    def show_prompt(
        self,
        character_id: str,
        mood: str,
        user_message: str,
        scenario_context: str = "Test scenario",
        intensity: float = 0.7
    ) -> str:
        """
        /show_prompt - Display full system prompt for debugging
        
        Args:
            character_id: Character ID
            mood: Mood state
            user_message: User's message
            scenario_context: Scenario context
            intensity: Mood intensity (0.0-1.0)
            
        Returns:
            The complete system prompt as it would be sent to LLM
        """
        character = self.char_manager.get_character(character_id)
        if not character:
            return f"❌ Character '{character_id}' not found"
        
        try:
            mood_enum = CharacterMood(mood.lower())
        except ValueError:
            return f"❌ Invalid mood '{mood}'"
        
        # Create mood state
        mood_state = MoodState(
            current_mood=mood_enum,
            intensity=intensity,
            reason=f"Testing with intensity {intensity}",
            trigger_keywords=user_message.lower().split()[:3]
        )
        
        # Generate full prompt
        prompt = character.generate_dynamic_prompt(
            mood_state=mood_state,
            user_message=user_message,
            scenario_context=scenario_context,
            character_role_context="Debugging test"
        )
        
        return f"""
╔══════════════════════════════════════════════════════════════════
║ FULL SYSTEM PROMPT
╚══════════════════════════════════════════════════════════════════

{prompt}

═══════════════════════════════════════════════════════════════════
Prompt Length: {len(prompt)} characters
═══════════════════════════════════════════════════════════════════
"""
    
    async def mood_pipeline_debug(
        self,
        character_id: str,
        user_message: str,
        scenario_context: str = "Test scenario",
        conversation_history: Optional[List[Dict]] = None
    ) -> str:
        """
        /mood_pipeline - Show step-by-step mood inference with detailed logging
        
        Args:
            character_id: Character ID
            user_message: User's message
            scenario_context: Scenario context
            conversation_history: Optional conversation history
            
        Returns:
            Detailed breakdown of the mood inference pipeline
        """
        character = self.char_manager.get_character(character_id)
        if not character:
            return f"❌ Character '{character_id}' not found"
        
        # Initialize mood state
        initial_mood = MoodState(
            current_mood=character.default_mood,
            intensity=0.5,
            reason="Initial state"
        )
        
        history = conversation_history or []
        
        output = f"""
╔══════════════════════════════════════════════════════════════════
║ MOOD INFERENCE PIPELINE: {character.name}
╚══════════════════════════════════════════════════════════════════

📝 User Message: "{user_message}"
🎯 Scenario: {scenario_context}
🎭 Character: {character.name}
😐 Initial Mood: {initial_mood.current_mood.value} (intensity: {initial_mood.intensity})

═══════════════════════════════════════════════════════════════════
RUNNING PIPELINE...
═══════════════════════════════════════════════════════════════════

"""
        
        try:
            # Run the pipeline
            updated_mood = await self.mood_system.infer_mood(
                character=character,
                user_message=user_message,
                current_mood_state=initial_mood,
                conversation_history=history,
                scenario_context=scenario_context
            )
            
            output += f"""
✅ PIPELINE COMPLETE

═══════════════════════════════════════════════════════════════════
FINAL RESULTS:
═══════════════════════════════════════════════════════════════════

Final Mood: {updated_mood.current_mood.value.upper()}
Intensity: {updated_mood.intensity:.2f} / 1.0
Reason: {updated_mood.reason}
Triggers: {', '.join(f'"{kw}"' for kw in updated_mood.trigger_keywords)}

Mood Change: {initial_mood.current_mood.value} → {updated_mood.current_mood.value}
Intensity Change: {initial_mood.intensity:.2f} → {updated_mood.intensity:.2f}

═══════════════════════════════════════════════════════════════════

Check the logs above for detailed step-by-step analysis:
  📍 STEP 1: Trigger Analysis
  📍 STEP 2: Mood History Check
  📍 STEP 3: Intensity Refinement
  📍 STEP 4: Consistency Validation
"""
            
        except Exception as e:
            output += f"""
❌ PIPELINE FAILED

Error: {str(e)}

Check logs for details.
"""
        
        return output
    
    def compare_moods(
        self,
        character_id: str,
        user_message: str,
        moods: List[str],
        scenario_context: str = "Test scenario"
    ) -> str:
        """
        Compare how character behaves across different moods
        
        Args:
            character_id: Character ID
            user_message: User message to test with
            moods: List of moods to compare
            scenario_context: Scenario context
            
        Returns:
            Side-by-side comparison of behavioral rules
        """
        character = self.char_manager.get_character(character_id)
        if not character:
            return f"❌ Character '{character_id}' not found"
        
        output = f"""
╔══════════════════════════════════════════════════════════════════
║ MOOD COMPARISON: {character.name}
╚══════════════════════════════════════════════════════════════════

📝 User Message: "{user_message}"
🎯 Comparing Moods: {', '.join(moods)}

"""
        
        for mood_str in moods:
            try:
                mood_enum = CharacterMood(mood_str.lower())
            except ValueError:
                output += f"⚠️ Skipping invalid mood: {mood_str}\n"
                continue
            
            # Create mood state
            mood_state = MoodState(
                current_mood=mood_enum,
                intensity=0.7,
                reason=f"Testing {mood_str}",
                trigger_keywords=[]
            )
            
            # Get matching rules
            matching_rules = [
                rule for rule in character.mood_behavior_rules
                if rule.matches(mood_state, user_message)
            ]
            
            output += f"""
═══════════════════════════════════════════════════════════════════
😤 MOOD: {mood_enum.value.upper()}
═══════════════════════════════════════════════════════════════════

Active Rules: {len(matching_rules)}

"""
            if matching_rules:
                for rule in matching_rules:
                    output += f"""Triggered by: {', '.join(rule.trigger_keywords)}
Behaviors:
"""
                    for behavior in rule.behaviors:
                        output += f"  • {behavior}\n"
                    output += "\n"
            else:
                output += "  No specific rules triggered - uses base personality\n"
        
        return output


# Example usage / CLI interface
async def main():
    """Interactive CLI for character dev tools"""
    import sys
    from gemini_client import GeminiClient
    
    # Initialize
    logging.basicConfig(level=logging.INFO)
    gemini = GeminiClient()
    dev_tools = CharacterDevTools(gemini)
    
    print("╔══════════════════════════════════════════════════════════════════")
    print("║ CHARACTER DEVELOPMENT TOOLS")
    print("╚══════════════════════════════════════════════════════════════════")
    print()
    print("Available commands:")
    print("  /characters - List all characters")
    print("  /test_mood <character> <mood> <message> - Test mood response")
    print("  /list_rules <character> [mood] - Show behavior rules")
    print("  /show_prompt <character> <mood> <message> - Display full prompt")
    print("  /mood_pipeline <character> <message> - Debug mood inference")
    print("  /compare <character> <message> <mood1,mood2,...> - Compare moods")
    print("  /exit - Quit")
    print()
    
    while True:
        try:
            cmd = input(">>> ").strip()
            
            if not cmd:
                continue
            
            if cmd == "/exit":
                break
            
            if cmd == "/characters":
                chars = dev_tools.list_characters()
                print(f"Available characters: {', '.join(chars)}\n")
                continue
            
            parts = cmd.split(maxsplit=3)
            command = parts[0]
            
            if command == "/test_mood" and len(parts) >= 4:
                char_id, mood, message = parts[1], parts[2], parts[3]
                result = dev_tools.test_mood(char_id, mood, message)
                print(result)
            
            elif command == "/list_rules" and len(parts) >= 2:
                char_id = parts[1]
                mood = parts[2] if len(parts) >= 3 else None
                result = dev_tools.list_rules(char_id, mood)
                print(result)
            
            elif command == "/show_prompt" and len(parts) >= 4:
                char_id, mood, message = parts[1], parts[2], parts[3]
                result = dev_tools.show_prompt(char_id, mood, message)
                print(result)
            
            elif command == "/mood_pipeline" and len(parts) >= 3:
                char_id, message = parts[1], parts[2]
                result = await dev_tools.mood_pipeline_debug(char_id, message)
                print(result)
            
            elif command == "/compare" and len(parts) >= 4:
                char_id, message, moods_str = parts[1], parts[2], parts[3]
                moods = [m.strip() for m in moods_str.split(',')]
                result = dev_tools.compare_moods(char_id, message, moods)
                print(result)
            
            else:
                print("❌ Unknown command or invalid syntax")
                print("Type /characters to list available characters")
        
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            logger.exception("Command failed")


if __name__ == "__main__":
    asyncio.run(main())

