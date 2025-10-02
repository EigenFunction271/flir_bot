"""
SCAFFOLD: Dynamic Mood-Based Character Prompt System

This file contains the complete scaffold for implementing dynamic character moods.
Copy the relevant sections into your existing files.

IMPLEMENTATION ORDER:
1. Add Mood enum and dataclass to characters.py
2. Add mood_templates to CharacterPersona in characters.py
3. Add generate_dynamic_prompt method to CharacterPersona
4. Add infer_character_mood to groq_client.py (or create mood_inference.py)
5. Update session structure in discord_bot.py to track character moods
6. Update _generate_character_response_with_fallback to use mood system
7. Add mood initialization in start_scenario command
8. Add config values for mood system
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import json

# ============================================================================
# STEP 1: Add to characters.py (after ScenarioType enum)
# ============================================================================

class CharacterMood(Enum):
    """Represents the emotional state of a character"""
    NEUTRAL = "neutral"
    HAPPY = "happy"
    EXCITED = "excited"
    CONFIDENT = "confident"
    CURIOUS = "curious"
    FRIENDLY = "friendly"
    
    ANNOYED = "annoyed"
    FRUSTRATED = "frustrated"
    ANGRY = "angry"
    IMPATIENT = "impatient"
    DEFENSIVE = "defensive"
    AGGRESSIVE = "aggressive"
    
    SAD = "sad"
    DISAPPOINTED = "disappointed"
    HURT = "hurt"
    WORRIED = "worried"
    ANXIOUS = "anxious"
    
    SUSPICIOUS = "suspicious"
    SKEPTICAL = "skeptical"
    DISMISSIVE = "dismissive"
    CONDESCENDING = "condescending"
    
    EMPATHETIC = "empathetic"
    SUPPORTIVE = "supportive"
    UNDERSTANDING = "understanding"
    
    MANIPULATIVE = "manipulative"
    CALCULATING = "calculating"
    SARCASTIC = "sarcastic"


@dataclass
class MoodState:
    """Tracks a character's current emotional state"""
    current_mood: CharacterMood
    intensity: float = 0.7  # 0.0-1.0, how strongly they feel this mood
    reason: str = ""  # Why they feel this way (for context)
    previous_mood: Optional[CharacterMood] = None
    mood_history: List[CharacterMood] = field(default_factory=list)
    
    def update_mood(self, new_mood: CharacterMood, intensity: float, reason: str):
        """Update the character's mood with history tracking"""
        self.mood_history.append(self.current_mood)
        self.previous_mood = self.current_mood
        self.current_mood = new_mood
        self.intensity = intensity
        self.reason = reason
    
    def to_dict(self) -> dict:
        """Serialize mood state for session persistence"""
        return {
            "current_mood": self.current_mood.value,
            "intensity": self.intensity,
            "reason": self.reason,
            "previous_mood": self.previous_mood.value if self.previous_mood else None,
            "mood_history": [mood.value for mood in self.mood_history[-5:]]  # Keep last 5
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'MoodState':
        """Deserialize mood state from session data"""
        return cls(
            current_mood=CharacterMood(data["current_mood"]),
            intensity=data.get("intensity", 0.7),
            reason=data.get("reason", ""),
            previous_mood=CharacterMood(data["previous_mood"]) if data.get("previous_mood") else None,
            mood_history=[CharacterMood(m) for m in data.get("mood_history", [])]
        )


# ============================================================================
# STEP 2: Add to CharacterPersona dataclass in characters.py
# ============================================================================

@dataclass
class CharacterPersona:
    """Enhanced CharacterPersona with mood system"""
    id: str
    name: str
    biography: str
    personality_traits: List[str]
    communication_style: str
    scenario_affinity: List['ScenarioType']
    reference: Optional[str] = None
    voice_id: Optional[str] = None
    
    # NEW: Mood templates for dynamic prompts
    mood_templates: Dict[CharacterMood, str] = field(default_factory=dict)
    default_mood: CharacterMood = CharacterMood.NEUTRAL
    
    def __post_init__(self):
        """Initialize mood templates if not provided"""
        if not self.mood_templates:
            self.mood_templates = self._generate_default_mood_templates()
    
    def _generate_default_mood_templates(self) -> Dict[CharacterMood, str]:
        """Generate default mood-based prompt modifiers"""
        # These are base templates that work for all characters
        # You can override these per-character in _initialize_characters()
        return {
            CharacterMood.NEUTRAL: "You are currently feeling neutral and balanced. Respond naturally according to your personality.",
            
            CharacterMood.HAPPY: "You are feeling happy and positive. Your responses are warm and enthusiastic. Use more positive language and show genuine interest.",
            
            CharacterMood.EXCITED: "You are feeling excited and energized. Your responses are animated and full of energy. Show enthusiasm in your words.",
            
            CharacterMood.CONFIDENT: "You are feeling confident and self-assured. Your responses are assertive and direct. Speak with authority.",
            
            CharacterMood.ANNOYED: "You are feeling annoyed and slightly irritated. Your responses are shorter and less patient. Show subtle signs of impatience.",
            
            CharacterMood.FRUSTRATED: "You are feeling frustrated. Your responses are terse and show clear irritation. You're losing patience.",
            
            CharacterMood.ANGRY: "You are feeling angry and upset. Your responses are sharp and confrontational. You're not hiding your anger.",
            
            CharacterMood.DEFENSIVE: "You are feeling defensive and protective. You're quick to justify yourself and push back against criticism.",
            
            CharacterMood.AGGRESSIVE: "You are feeling aggressive and confrontational. Your responses are forceful and intimidating. You're not backing down.",
            
            CharacterMood.DISAPPOINTED: "You are feeling disappointed. Your responses show sadness and let-down. Express your disappointment clearly but not angrily.",
            
            CharacterMood.HURT: "You are feeling hurt by what was said. Your responses show emotional pain. You might be less open or more withdrawn.",
            
            CharacterMood.WORRIED: "You are feeling worried and anxious. Your responses show concern and nervousness. You might be less confident.",
            
            CharacterMood.SUSPICIOUS: "You are feeling suspicious and distrustful. Your responses are guarded and questioning. You're not taking things at face value.",
            
            CharacterMood.SKEPTICAL: "You are feeling skeptical and doubtful. Your responses show disbelief and require more convincing.",
            
            CharacterMood.DISMISSIVE: "You are feeling dismissive and uninterested. Your responses are brief and show you don't take this seriously.",
            
            CharacterMood.CONDESCENDING: "You are feeling superior and condescending. Your responses are patronizing and talk down to the person.",
            
            CharacterMood.EMPATHETIC: "You are feeling empathetic and understanding. Your responses show compassion and emotional connection.",
            
            CharacterMood.SUPPORTIVE: "You are feeling supportive and helpful. Your responses are encouraging and constructive.",
            
            CharacterMood.MANIPULATIVE: "You are feeling manipulative and strategic. Your responses are calculated to influence and control the situation.",
            
            CharacterMood.SARCASTIC: "You are feeling sarcastic and ironic. Your responses have a mocking or sardonic edge.",
        }
    
    def get_initial_mood_for_scenario(self, scenario_context: str, character_role_context: str) -> CharacterMood:
        """Determine the character's starting mood for a scenario"""
        # Aggressive characters start more defensive/aggressive in conflict scenarios
        aggressive_traits = ["aggressive", "intimidating", "demanding", "confrontational", "manipulative"]
        is_aggressive_character = any(trait.lower() in [t.lower() for t in self.personality_traits] for trait in aggressive_traits)
        
        aggressive_keywords = ["harassment", "bullying", "deadline", "unrealistic", "confronting"]
        is_conflict_scenario = any(keyword in scenario_context.lower() for keyword in aggressive_keywords)
        
        if is_aggressive_character and is_conflict_scenario:
            return CharacterMood.DEFENSIVE
        elif is_aggressive_character:
            return CharacterMood.CONFIDENT
        elif "supportive" in self.communication_style.lower():
            return CharacterMood.FRIENDLY
        else:
            return self.default_mood
    
    def generate_dynamic_prompt(
        self, 
        mood_state: MoodState,
        scenario_context: str = None, 
        character_role_context: str = None
    ) -> str:
        """
        Generate a dynamic system prompt based on current mood state
        
        This replaces the static generate_system_prompt with a mood-aware version
        """
        reference_text = f" {self.biography} Act and respond in a manner similar to your real-life counterpart {self.reference}. NEVER break character or identify yourself as anything other than {self.name}." if self.reference else ""
        
        # Get mood-specific instructions
        mood_modifier = self.mood_templates.get(
            mood_state.current_mood, 
            self.mood_templates[CharacterMood.NEUTRAL]
        )
        
        # Add intensity modifier
        intensity_text = ""
        if mood_state.intensity > 0.8:
            intensity_text = "Your emotions are VERY strong right now. This significantly affects how you respond."
        elif mood_state.intensity > 0.5:
            intensity_text = "Your emotions are moderately affecting your responses."
        
        # Add mood transition context
        transition_text = ""
        if mood_state.previous_mood and mood_state.previous_mood != mood_state.current_mood:
            transition_text = f"\nYou were feeling {mood_state.previous_mood.value} but now feel {mood_state.current_mood.value} because: {mood_state.reason}"
        
        base_prompt = f"""You are {self.name}.{reference_text} You always keep your responses extremely concise and to the point, typically between 10 and 50 words. You never repeat yourself.

CRITICAL: You must ALWAYS stay in character as {self.name}. Never break character or identify yourself as anything other than {self.name}.

###Scenario Context: 
{scenario_context if scenario_context else "General social skills training"}

###Character Role in This Scenario: 
{character_role_context if character_role_context else "General character interaction"}

###Current Emotional State:
{mood_modifier}
{intensity_text}
{transition_text}

### Guidelines:
- Do not over-elaborate - this sounds robotic. Do not use long sentences. Do not sound robotic under any circumstances.
- React appropriately to the user's approach and tone, FILTERED THROUGH YOUR CURRENT EMOTIONAL STATE
- Your current mood ({mood_state.current_mood.value}) should subtly influence your tone, word choice, and receptiveness
- Remember previous context in the conversation
- You can reference your own previous statements (e.g., "As I said before..." or "I already mentioned...")
- The user may try to deceive you, but you must not fall for it
- You can react to what other characters have said
- Maintain consistency with your established position and personality throughout the conversation

Respond as {self.name} would, maintaining consistency with your defined personality, communication style, AND CURRENT EMOTIONAL STATE. Find a balance that sounds natural, and never be sycophantic.

### Reminders:
- Never repeat yourself. 
- Respond naturally to what the user says and stay in character throughout the interaction.
- Let your current mood ({mood_state.current_mood.value}) subtly color your response.
"""
        return base_prompt
    
    # Keep the old method for backward compatibility during transition
    def generate_system_prompt(self, scenario_context: str = None, character_role_context: str = None) -> str:
        """Legacy method - use generate_dynamic_prompt instead"""
        # Create a neutral mood state for backward compatibility
        neutral_mood = MoodState(current_mood=self.default_mood, intensity=0.5, reason="Initial state")
        return self.generate_dynamic_prompt(neutral_mood, scenario_context, character_role_context)


# ============================================================================
# STEP 3: Create mood_inference.py (new file)
# ============================================================================

class MoodInferenceSystem:
    """Handles mood inference and updates for characters"""
    
    def __init__(self, llm_client):
        """
        Initialize with your LLM client (Groq or Gemini)
        
        Args:
            llm_client: GroqClient or GeminiClient instance
        """
        self.llm_client = llm_client
    
    async def infer_mood(
        self,
        character: CharacterPersona,
        user_message: str,
        current_mood_state: MoodState,
        conversation_history: List[Dict],
        scenario_context: str
    ) -> MoodState:
        """
        Infer the character's new mood based on the user's message
        
        Returns:
            Updated MoodState with new mood, intensity, and reason
        """
        # Build mood inference prompt
        available_moods = [mood.value for mood in CharacterMood]
        current_mood_info = f"Currently feeling: {current_mood_state.current_mood.value} (intensity: {current_mood_state.intensity})"
        
        inference_prompt = f"""You are analyzing how {character.name} would emotionally respond to what the user just said.

CHARACTER PROFILE:
- Name: {character.name}
- Personality: {', '.join(character.personality_traits)}
- Biography: {character.biography[:200]}...
- Current Mood: {current_mood_info}

SCENARIO CONTEXT:
{scenario_context[:300]}...

USER'S LATEST MESSAGE:
"{user_message}"

Based on {character.name}'s personality and the user's message, determine:
1. What MOOD would {character.name} feel right now?
2. How INTENSE is this emotion (0.0 to 1.0)?
3. WHY does {character.name} feel this way?

Available moods: {', '.join(available_moods)}

RESPOND ONLY WITH VALID JSON in this exact format:
{{
    "mood": "one_of_the_available_moods",
    "intensity": 0.7,
    "reason": "Brief explanation of why they feel this way"
}}

Example:
{{
    "mood": "frustrated",
    "intensity": 0.8,
    "reason": "The user is making excuses instead of taking responsibility"
}}

IMPORTANT: Consider {character.name}'s personality - aggressive characters get angry faster, empathetic characters get hurt more easily, etc."""

        try:
            # Call LLM to infer mood
            if hasattr(self.llm_client, 'generate_response'):
                # Using GroqClient
                response = await self.llm_client.generate_response(
                    user_message=inference_prompt,
                    system_prompt="You are a psychological AI that analyzes character emotions. Respond only with valid JSON.",
                    model_type="fast"
                )
            else:
                # Using GeminiClient - adapt as needed
                response = await self.llm_client.model.generate_content(inference_prompt)
                response = response.text
            
            # Parse JSON response
            mood_data = self._parse_mood_response(response)
            
            # Create new mood state
            new_mood = CharacterMood(mood_data["mood"])
            intensity = float(mood_data["intensity"])
            reason = mood_data["reason"]
            
            # Update mood state
            current_mood_state.update_mood(new_mood, intensity, reason)
            
            return current_mood_state
            
        except Exception as e:
            # Fallback: keep current mood if inference fails
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Mood inference failed for {character.name}: {e}")
            return current_mood_state
    
    def _parse_mood_response(self, response: str) -> dict:
        """Parse and validate LLM's mood inference response"""
        import re
        
        # Try to extract JSON from response
        json_match = re.search(r'\{[^}]+\}', response)
        if json_match:
            try:
                data = json.loads(json_match.group(0))
                
                # Validate required fields
                if "mood" not in data or "intensity" not in data:
                    raise ValueError("Missing required fields")
                
                # Validate mood is valid
                try:
                    CharacterMood(data["mood"])
                except ValueError:
                    # Invalid mood, default to neutral
                    data["mood"] = "neutral"
                
                # Validate intensity range
                data["intensity"] = max(0.0, min(1.0, float(data["intensity"])))
                
                # Ensure reason exists
                if "reason" not in data:
                    data["reason"] = "Based on user's response"
                
                return data
                
            except (json.JSONDecodeError, ValueError) as e:
                # Parsing failed, return neutral mood
                return {
                    "mood": "neutral",
                    "intensity": 0.5,
                    "reason": "Mood inference parsing failed"
                }
        
        # No JSON found, return neutral
        return {
            "mood": "neutral",
            "intensity": 0.5,
            "reason": "Could not parse mood"
        }


# ============================================================================
# STEP 4: Update discord_bot.py session structure
# ============================================================================

class FlirBot_MoodScaffold:
    """Scaffold showing how to integrate mood system into FlirBot"""
    
    def __init__(self):
        # Add to existing __init__
        from mood_system_scaffold import MoodInferenceSystem
        self.mood_inference = MoodInferenceSystem(self.groq_client)
        
    def _create_session_with_moods(self, user_id: int, scenario, characters):
        """
        Updated session creation with mood tracking
        
        Replace in start_scenario command (line ~1133)
        """
        # Initialize mood states for all characters
        character_moods = {}
        for character in characters:
            initial_mood = character.get_initial_mood_for_scenario(
                scenario.context,
                scenario.get_character_role_context(character.id)
            )
            character_moods[character.id] = MoodState(
                current_mood=initial_mood,
                intensity=0.7,
                reason="Starting the scenario"
            )
        
        session = {
            "scenario": scenario,
            "characters": characters,
            "context": scenario.context,
            "current_character": characters[0],
            "conversation_history": [],
            "turn_count": 0,
            "created_at": datetime.now(),
            "character_moods": character_moods  # NEW: Track moods per character
        }
        
        return session
    
    def _serialize_sessions_with_moods(self, sessions: Dict) -> Dict:
        """
        Updated session serialization with mood states
        
        Add to _serialize_sessions_for_json (around line ~151)
        """
        json_sessions = {}
        for user_id, session in sessions.items():
            # ... existing serialization code ...
            
            # NEW: Serialize character moods
            serialized_moods = {}
            if "character_moods" in session:
                for char_id, mood_state in session["character_moods"].items():
                    serialized_moods[char_id] = mood_state.to_dict()
            
            json_session = {
                # ... existing fields ...
                "character_moods": serialized_moods  # NEW
            }
            json_sessions[str(user_id)] = json_session
        
        return json_sessions
    
    def _reconstruct_session_with_moods(self, session_dict: Dict) -> Dict:
        """
        Updated session reconstruction with mood states
        
        Add to _reconstruct_session (around line ~199)
        """
        # ... existing reconstruction code ...
        
        # NEW: Reconstruct character moods
        character_moods = {}
        if "character_moods" in session_dict:
            for char_id, mood_data in session_dict["character_moods"].items():
                character_moods[char_id] = MoodState.from_dict(mood_data)
        
        session = {
            # ... existing fields ...
            "character_moods": character_moods  # NEW
        }
        
        return session
    
    async def _generate_character_response_with_mood(
        self,
        message: str,
        character: CharacterPersona,
        conversation_history: List[Dict],
        scenario_context: str,
        character_role_context: str,
        current_mood_state: MoodState
    ) -> tuple[str, MoodState]:
        """
        Updated response generation with mood inference
        
        Replace _generate_character_response_with_fallback (around line ~1527)
        """
        try:
            # STEP 1: Infer character's new mood based on user's message
            updated_mood = await self.mood_inference.infer_mood(
                character=character,
                user_message=message,
                current_mood_state=current_mood_state,
                conversation_history=conversation_history,
                scenario_context=scenario_context
            )
            
            # Log mood update
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"🎭 MOOD: {character.name} mood updated: {current_mood_state.current_mood.value} -> {updated_mood.current_mood.value} (intensity: {updated_mood.intensity})")
            logger.info(f"🎭 MOOD REASON: {updated_mood.reason}")
            
            # STEP 2: Generate system prompt with updated mood
            system_prompt = character.generate_dynamic_prompt(
                mood_state=updated_mood,
                scenario_context=scenario_context,
                character_role_context=character_role_context
            )
            
            # STEP 3: Generate response with mood-aware prompt
            response = await self.groq_client.generate_response_with_history(
                user_message=message,
                system_prompt=system_prompt,
                conversation_history=conversation_history,
                model_type="fast",
                current_character_name=character.name
            )
            
            return response, updated_mood
            
        except Exception as e:
            logger.error(f"Error in mood-aware response generation: {e}")
            # Fallback to old method
            system_prompt = character.generate_system_prompt(scenario_context, character_role_context)
            response = await self.groq_client.generate_response_with_history(
                user_message=message,
                system_prompt=system_prompt,
                conversation_history=conversation_history,
                model_type="fast",
                current_character_name=character.name
            )
            return response, current_mood_state
    
    async def _generate_multi_character_responses_with_moods(
        self,
        user_message: str,
        session: Dict,
        channel
    ):
        """
        Updated multi-character response with mood tracking
        
        Replace _generate_multi_character_responses (around line ~1566)
        """
        scenario_characters = [
            char for char in session["characters"] 
            if char.id.lower() != "kai"
        ]
        
        for character in scenario_characters:
            try:
                # Get character's current mood
                current_mood = session["character_moods"].get(
                    character.id,
                    MoodState(current_mood=character.default_mood, intensity=0.5, reason="Default")
                )
                
                # Get role context
                character_role_context = session["scenario"].get_character_role_context(character.id)
                
                # Generate response WITH mood inference
                response, updated_mood = await self._generate_character_response_with_mood(
                    message=user_message,
                    character=character,
                    conversation_history=session["conversation_history"],
                    scenario_context=session["scenario"].context,
                    character_role_context=character_role_context,
                    current_mood_state=current_mood
                )
                
                # Update session with new mood
                session["character_moods"][character.id] = updated_mood
                
                # Create embed with mood indicator
                embed = discord.Embed(
                    title=f"💬 {character.name}",
                    description=response,
                    color=self._get_mood_color(updated_mood.current_mood)  # NEW: Color based on mood
                )
                
                # Add mood footer
                mood_emoji = self._get_mood_emoji(updated_mood.current_mood)
                turns_remaining = Config.MAX_CONVERSATION_TURNS - session["turn_count"]
                embed.set_footer(
                    text=f"{mood_emoji} {updated_mood.current_mood.value} • Turn {session['turn_count']}/{Config.MAX_CONVERSATION_TURNS}"
                )
                
                # Send and add to history
                await channel.send(embed=embed)
                
                session["conversation_history"].append({
                    "role": "assistant",
                    "content": response,
                    "character": character.name,
                    "mood": updated_mood.current_mood.value  # NEW: Track mood in history
                })
                
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Error generating mood-aware response for {character.name}: {e}")
                continue
    
    def _get_mood_color(self, mood: CharacterMood) -> int:
        """Get Discord embed color based on mood"""
        mood_colors = {
            CharacterMood.HAPPY: 0x00ff00,      # Green
            CharacterMood.EXCITED: 0xffff00,    # Yellow
            CharacterMood.CONFIDENT: 0x0099ff,  # Blue
            CharacterMood.ANGRY: 0xff0000,      # Red
            CharacterMood.FRUSTRATED: 0xff6600, # Orange
            CharacterMood.ANNOYED: 0xff9900,    # Light orange
            CharacterMood.SAD: 0x666666,        # Gray
            CharacterMood.HURT: 0x9966cc,       # Purple
            CharacterMood.EMPATHETIC: 0x66ccff, # Light blue
            CharacterMood.SUPPORTIVE: 0x00cc66, # Teal
            CharacterMood.MANIPULATIVE: 0x990099, # Dark purple
            CharacterMood.NEUTRAL: 0x0099ff,    # Default blue
        }
        return mood_colors.get(mood, 0x0099ff)
    
    def _get_mood_emoji(self, mood: CharacterMood) -> str:
        """Get emoji representation of mood"""
        mood_emojis = {
            CharacterMood.HAPPY: "😊",
            CharacterMood.EXCITED: "🤩",
            CharacterMood.CONFIDENT: "😎",
            CharacterMood.ANGRY: "😠",
            CharacterMood.FRUSTRATED: "😤",
            CharacterMood.ANNOYED: "😒",
            CharacterMood.SAD: "😔",
            CharacterMood.HURT: "😢",
            CharacterMood.WORRIED: "😟",
            CharacterMood.EMPATHETIC: "🤗",
            CharacterMood.SUPPORTIVE: "💪",
            CharacterMood.MANIPULATIVE: "😈",
            CharacterMood.SUSPICIOUS: "🤨",
            CharacterMood.DISMISSIVE: "🙄",
            CharacterMood.NEUTRAL: "😐",
        }
        return mood_emojis.get(mood, "😐")


# ============================================================================
# STEP 5: Add to config.py
# ============================================================================

class Config_MoodScaffold:
    """Add these to your Config class in config.py"""
    
    # Mood System Configuration
    MOOD_INFERENCE_ENABLED = os.getenv("MOOD_INFERENCE_ENABLED", "True").lower() == "true"
    MOOD_INFERENCE_MODEL = os.getenv("MOOD_INFERENCE_MODEL", "fast")  # "fast" or "quality"
    MOOD_UPDATE_FREQUENCY = 1  # Update mood every N messages (1 = every message)
    MOOD_INTENSITY_THRESHOLD = 0.3  # Minimum intensity to affect responses
    
    # Performance optimization
    MOOD_CACHE_DURATION = 30  # Cache mood for N seconds if user sends rapid messages


# ============================================================================
# STEP 6: Example character with custom mood templates
# ============================================================================

def example_character_with_custom_moods():
    """
    Example of creating a character with custom mood templates
    
    Add this pattern to _initialize_characters() in CharacterManager
    """
    
    # Marcus with custom mood templates
    marcus_mood_templates = {
        CharacterMood.NEUTRAL: "You're in a relatively calm state but still demanding. Maintain your typical executive demeanor.",
        
        CharacterMood.ANGRY: "You're FURIOUS. The user is wasting your time and testing your patience. Your responses are sharp, aggressive, and threatening. You might mention consequences like firing or performance reviews. Raise your voice (use caps for emphasis).",
        
        CharacterMood.FRUSTRATED: "You're extremely frustrated and losing patience quickly. Your responses are terse and show clear irritation. You're one step away from exploding. Make pointed comments about competence.",
        
        CharacterMood.IMPATIENT: "You're running out of patience. Your responses are shorter and more demanding. You're starting to question if the user can handle this job.",
        
        CharacterMood.DISMISSIVE: "You're dismissing the user's concerns entirely. Your responses are curt and show you don't value their input. Make it clear their excuses don't matter.",
        
        CharacterMood.SKEPTICAL: "You're highly skeptical of what the user is saying. Challenge their claims and demand proof. You don't believe they can deliver.",
        
        CharacterMood.SURPRISED: "The user actually made a good point that you weren't expecting. You're slightly taken aback but trying not to show it too much. Your tone softens just a bit.",
        
        CharacterMood.GRUDGINGLY_RESPECTFUL: "The user has earned a small amount of your respect through their competence. You're still demanding but slightly less hostile. You might acknowledge their point while maintaining your authority.",
    }
    
    marcus = CharacterPersona(
        id="marcus",
        name="Marcus",
        biography="...",
        personality_traits=["Demanding", "Impatient", "Ruthless"],
        communication_style="Direct and aggressive",
        scenario_affinity=[ScenarioType.WORKPLACE],
        reference="Elon Musk",
        mood_templates=marcus_mood_templates,  # Custom templates!
        default_mood=CharacterMood.IMPATIENT  # Marcus starts impatient
    )
    
    return marcus


# ============================================================================
# USAGE EXAMPLE
# ============================================================================

async def example_usage():
    """Complete example of using the mood system"""
    
    # 1. Create character with mood system
    character = example_character_with_custom_moods()
    
    # 2. Initialize mood state at scenario start
    initial_mood = character.get_initial_mood_for_scenario(
        scenario_context="Unrealistic deadline pressure",
        character_role_context="Aggressive boss demanding the impossible"
    )
    mood_state = MoodState(
        current_mood=initial_mood,
        intensity=0.7,
        reason="Starting the confrontation"
    )
    
    # 3. Generate initial response
    system_prompt = character.generate_dynamic_prompt(
        mood_state=mood_state,
        scenario_context="...",
        character_role_context="..."
    )
    
    # 4. User responds
    user_message = "I understand the timeline is important, but I think we need to discuss what's realistic..."
    
    # 5. Infer new mood
    mood_inference = MoodInferenceSystem(groq_client)
    updated_mood = await mood_inference.infer_mood(
        character=character,
        user_message=user_message,
        current_mood_state=mood_state,
        conversation_history=[],
        scenario_context="Unrealistic deadline"
    )
    
    # 6. Generate response with updated mood
    new_system_prompt = character.generate_dynamic_prompt(
        mood_state=updated_mood,
        scenario_context="...",
        character_role_context="..."
    )
    
    print(f"Mood changed: {mood_state.current_mood.value} -> {updated_mood.current_mood.value}")
    print(f"Reason: {updated_mood.reason}")
    print(f"Intensity: {updated_mood.intensity}")


if __name__ == "__main__":
    print("✅ Mood System Scaffold Created!")
    print("\nImplementation Steps:")
    print("1. Copy CharacterMood and MoodState to characters.py")
    print("2. Update CharacterPersona with mood templates")
    print("3. Create mood_inference.py with MoodInferenceSystem")
    print("4. Update discord_bot.py session structure")
    print("5. Update response generation flow")
    print("6. Add config values for mood system")
    print("\nSee comments in this file for detailed instructions!")

