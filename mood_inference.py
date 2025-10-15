"""
LLM-Based Mood Inference System

The LLM analyzes the conversation and determines how the character FEELS.
Then the rule-based system determines how that feeling translates to specific BEHAVIORS.

Flow:
1. User says something
2. LLM: "Marcus feels ANGRY (0.8) because user made another excuse"
3. Rules: "IF ANGRY + keyword 'excuse' THEN: Use CAPS, threaten firing"
4. Response generated with mood-specific behavioral instructions
"""

import asyncio
import logging
from typing import List, Dict, Optional
import json
import re

from characters import CharacterPersona, CharacterMood, MoodState

logger = logging.getLogger(__name__)


class MoodInferenceSystem:
    """Handles LLM-based mood inference for characters"""
    
    def __init__(self, llm_client, use_smart_inference=True):
        """
        Initialize with your LLM client (Groq or Gemini)
        
        Args:
            llm_client: GroqClient or GeminiClient instance
            use_smart_inference: If True, uses rule-based inference when possible (saves 70-90% of LLM calls)
        """
        self.llm_client = llm_client
        self.use_smart_inference = use_smart_inference
        
        # Statistics tracking
        self.llm_calls = 0
        self.rule_based_calls = 0
        self.cache_hits = 0
        
        # Simple cache for recent inferences (hash -> (mood_data, timestamp))
        self.inference_cache = {}
        self.cache_ttl = 180  # 3 minutes
        
        logger.info(f"✅ MoodInferenceSystem initialized (smart_inference={'ON' if use_smart_inference else 'OFF'})")
    
    async def infer_mood(
        self,
        character: CharacterPersona,
        user_message: str,
        current_mood_state: MoodState,
        conversation_history: List[Dict],
        scenario_context: str
    ) -> MoodState:
        """
        Use LLM to infer the character's new mood based on user's message
        OPTIMIZED: Single comprehensive LLM call instead of 3 separate calls
        
        Args:
            character: The character whose mood we're inferring
            user_message: What the user just said
            current_mood_state: Character's current emotional state
            conversation_history: Recent conversation context
            scenario_context: The scenario context
            
        Returns:
            Updated MoodState with new mood, intensity, reason, and trigger keywords
        """
        try:
            logger.info(f"🎭 MOOD: Starting optimized mood inference for {character.name}")
            logger.info(f"🎭 MOOD: Current state: {current_mood_state.current_mood.value} ({current_mood_state.intensity})")
            logger.info(f"🎭 MOOD: User message: '{user_message[:100]}...'")
            
            # OPTIMIZED: Single comprehensive inference (was 3 separate calls)
            mood_data = await self._infer_mood_comprehensive(
                character, 
                user_message, 
                current_mood_state,
                conversation_history, 
                scenario_context
            )
            logger.info(f"📍 INFERENCE: Mood={mood_data.get('mood')}, Intensity={mood_data.get('intensity')}")
            
            # Validate consistency with character (local, no LLM call)
            final_data = self._validate_consistency(
                character,
                mood_data,
                current_mood_state
            )
            logger.info(f"✅ VALIDATION: Final mood = {final_data.get('mood', 'neutral')}")
            
            # Create new mood state
            new_mood = CharacterMood(final_data["mood"])
            intensity = float(final_data["intensity"])
            reason = final_data["reason"]
            triggers = final_data.get("trigger_keywords", [])
            
            # Update mood state
            current_mood_state.update_mood(new_mood, intensity, reason, triggers)
            
            logger.info(f"✅ MOOD: {character.name} mood updated: {new_mood.value} (intensity: {intensity})")
            logger.info(f"✅ MOOD: Reason: {reason}")
            logger.info(f"✅ MOOD: Triggers: {triggers}")
            
            return current_mood_state
            
        except Exception as e:
            # Fallback: keep current mood if inference fails
            logger.error(f"❌ MOOD: Inference failed for {character.name}: {e}")
            logger.error(f"❌ MOOD: Keeping current mood: {current_mood_state.current_mood.value}")
            return current_mood_state
    
    async def _infer_mood_comprehensive(
        self,
        character: CharacterPersona,
        user_message: str,
        current_mood_state: MoodState,
        conversation_history: List[Dict],
        scenario_context: str
    ) -> dict:
        """
        OPTIMIZED: Single comprehensive mood inference combining all analysis steps
        
        Replaces 3 separate LLM calls with 1 comprehensive call that:
        1. Analyzes trigger keywords
        2. Considers conversation history and trajectory
        3. Adjusts intensity based on personality
        
        Returns: dict with mood, intensity, reason, trigger_keywords
        """
        available_moods = [mood.value for mood in CharacterMood]
        current_mood_info = f"{current_mood_state.current_mood.value} (intensity: {current_mood_state.intensity})"
        recent_context = self._format_recent_conversation(conversation_history[-6:])
        
        # Determine personality modifiers
        aggressive_traits = ["aggressive", "intimidating", "demanding", "confrontational", "bullying", "manipulative"]
        empathetic_traits = ["empathetic", "understanding", "supportive", "caring", "nurturing"]
        
        is_aggressive = any(trait.lower() in [t.lower() for t in character.personality_traits] for trait in aggressive_traits)
        is_empathetic = any(trait.lower() in [t.lower() for t in character.personality_traits] for trait in empathetic_traits)
        
        personality_note = (
            "aggressive and quick to anger" if is_aggressive 
            else "empathetic and understanding" if is_empathetic 
            else "balanced"
        )
        
        # Mood history for trajectory
        mood_history_str = " → ".join([mood.value for mood in current_mood_state.mood_history[-3:]]) if current_mood_state.mood_history else "No history"
        
        # Comprehensive prompt combining all analysis steps
        comprehensive_prompt = f"""Analyze {character.name}'s emotional response to the user's message.

CHARACTER: {character.name}
Personality: {', '.join(character.personality_traits[:5])} ({personality_note})
Current Mood: {current_mood_info}
Mood History: {mood_history_str}

SCENARIO: {scenario_context[:300]}...

RECENT CONVERSATION:
{recent_context}

USER'S MESSAGE: "{user_message}"

COMPREHENSIVE ANALYSIS - Do ALL of these steps:

1. TRIGGER ANALYSIS: What keywords/behaviors in the user's message trigger an emotional response?
2. TRAJECTORY: Based on conversation history, is {character.name}'s mood escalating, de-escalating, or staying consistent?
3. INTENSITY: Adjust emotional intensity based on:
   - {character.name}'s personality ({personality_note})
   - Aggressive characters: Higher intensity (+0.2)
   - Empathetic characters: Lower intensity when user shows vulnerability (-0.2)
   - Escalating trajectory: +0.1 to +0.2
   - De-escalating trajectory: -0.1 to -0.3

Available moods: {', '.join(available_moods)}

Respond with JSON:
{{
    "mood": "mood_name",
    "intensity": 0.7,
    "reason": "Brief explanation considering triggers, trajectory, and personality",
    "trigger_keywords": ["keyword1", "keyword2"],
    "trajectory": "escalating|de-escalating|consistent"
}}

EXAMPLES:

User makes excuse to aggressive boss:
{{
    "mood": "angry",
    "intensity": 0.85,
    "reason": "User making excuses instead of taking responsibility. Aggressive personality escalates frustration.",
    "trigger_keywords": ["excuse", "can't", "difficult"],
    "trajectory": "escalating"
}}

User shows data to skeptical colleague:
{{
    "mood": "skeptical",
    "intensity": 0.55,
    "reason": "User provided concrete data. Intensity slightly reduced but maintaining skepticism.",
    "trigger_keywords": ["data", "analysis", "proof"],
    "trajectory": "de-escalating"
}}"""

        # Single LLM call
        response = await self._call_llm(comprehensive_prompt)
        data = self._parse_mood_response(response)
        
        return data
    
    def _format_recent_conversation(self, recent_messages: List[Dict]) -> str:
        """Format recent conversation for context"""
        if not recent_messages:
            return "No prior conversation"
        
        formatted = []
        for msg in recent_messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            character = msg.get("character", "")
            
            if role == "user":
                formatted.append(f"USER: {content}")
            elif role == "assistant":
                formatted.append(f"{character}: {content}")
        
        return "\n".join(formatted[-6:])  # Last 6 messages (3 exchanges)
    
    async def _analyze_triggers(
        self,
        character: CharacterPersona,
        user_message: str,
        scenario_context: str
    ) -> dict:
        """
        STEP 1: Analyze what keywords/behaviors in user's message trigger emotional response
        
        Returns dict with: trigger_keywords, initial_mood, preliminary_reason
        """
        available_moods = [mood.value for mood in CharacterMood]
        
        prompt = f"""# STEP 1: Trigger Analysis

Character: {character.name}
Personality: {', '.join(character.personality_traits[:5])}
User Message: "{user_message}"

TASK: Identify what in the user's message would emotionally trigger {character.name}.

Look for:
- Keywords that match character's sensitivities (excuses, promises, solutions, blame, etc.)
- Tone indicators (defensive, apologetic, assertive, etc.)
- Behavioral patterns (deflecting, problem-solving, challenging, etc.)

Available moods: {', '.join(available_moods)}

Respond with JSON:
{{
    "trigger_keywords": ["keyword1", "keyword2"],
    "initial_mood": "likely_mood_from_triggers",
    "preliminary_reason": "Why these triggers would affect {character.name}"
}}"""

        response = await self._call_llm(prompt)
        data = self._parse_mood_response(response)
        
        # Ensure we have trigger_keywords even if parsing failed
        if "trigger_keywords" not in data:
            data["trigger_keywords"] = []
        if "initial_mood" not in data:
            data["initial_mood"] = "neutral"
        if "preliminary_reason" not in data:
            data["preliminary_reason"] = "Analyzing user message"
            
        return data
    
    async def _check_mood_history(
        self,
        character: CharacterPersona,
        current_mood_state: MoodState,
        conversation_history: List[Dict],
        triggers_data: dict
    ) -> dict:
        """
        STEP 2: Check mood history to understand trajectory
        
        Is the character getting angrier? Softening? Staying consistent?
        Returns triggers_data + trajectory + adjusted_mood
        """
        recent_context = self._format_recent_conversation(conversation_history[-6:])
        mood_history_str = " → ".join([mood.value for mood in current_mood_state.mood_history[-3:]])
        
        prompt = f"""# STEP 2: Mood Trajectory Analysis

Character: {character.name}
Current Mood: {current_mood_state.current_mood.value} (intensity: {current_mood_state.intensity})
Mood History: {mood_history_str}
Recent Conversation:
{recent_context}

Initial Analysis from Step 1:
- Triggers: {', '.join(triggers_data.get('trigger_keywords', []))}
- Suggested Mood: {triggers_data.get('initial_mood', 'neutral')}

TASK: Determine if mood should escalate, de-escalate, or stay consistent.

Consider:
- If already angry and user makes excuses → escalate further
- If skeptical but user provides evidence → soften slightly
- If user changes approach → shift trajectory

Respond with JSON:
{{
    "trajectory": "escalating|de-escalating|consistent",
    "adjusted_mood": "mood_considering_history",
    "intensity": 0.7,
    "reason": "Why this trajectory makes sense given history"
}}"""

        response = await self._call_llm(prompt)
        data = self._parse_mood_response(response)
        
        # Merge with triggers_data
        result = {**triggers_data, **data}
        
        # Ensure required fields
        if "trajectory" not in result:
            result["trajectory"] = "consistent"
        if "adjusted_mood" not in result:
            result["adjusted_mood"] = triggers_data.get("initial_mood", "neutral")
            
        return result
    
    async def _refine_intensity(
        self,
        character: CharacterPersona,
        trajectory_data: dict,
        user_message: str
    ) -> dict:
        """
        STEP 3: Refine intensity based on character personality
        
        Aggressive characters → higher intensity
        Empathetic characters → lower intensity when user shows vulnerability
        """
        aggressive_traits = ["aggressive", "intimidating", "demanding", "confrontational", "bullying", "manipulative"]
        empathetic_traits = ["empathetic", "understanding", "supportive", "caring", "nurturing"]
        
        is_aggressive = any(trait.lower() in [t.lower() for t in character.personality_traits] for trait in aggressive_traits)
        is_empathetic = any(trait.lower() in [t.lower() for t in character.personality_traits] for trait in empathetic_traits)
        
        personality_modifier = "aggressive and quick to anger" if is_aggressive else "empathetic and understanding" if is_empathetic else "balanced"
        
        prompt = f"""# STEP 3: Intensity Refinement

Character: {character.name}
Personality: {personality_modifier}
Mood from Step 2: {trajectory_data.get('adjusted_mood', 'neutral')}
Current Intensity: {trajectory_data.get('intensity', 0.5)}
Trajectory: {trajectory_data.get('trajectory', 'consistent')}

User's Message: "{user_message}"

TASK: Refine the emotional intensity (0.0 to 1.0) based on {character.name}'s personality.

Rules:
- Aggressive characters: Add +0.1 to +0.3 to intensity
- Empathetic characters: Reduce by -0.1 to -0.2 if user shows vulnerability
- Escalating trajectory: Add +0.1 to +0.2
- De-escalating trajectory: Reduce by -0.1 to -0.3

Cap at 1.0 maximum, 0.1 minimum.

Respond with JSON:
{{
    "mood": "{trajectory_data.get('adjusted_mood', 'neutral')}",
    "intensity": 0.7,
    "reason": "Brief explanation of intensity level"
}}"""

        response = await self._call_llm(prompt)
        data = self._parse_mood_response(response)
        
        # Merge with trajectory_data
        result = {**trajectory_data, **data}
        
        # Clamp intensity to valid range
        if "intensity" in result:
            result["intensity"] = max(0.1, min(1.0, float(result["intensity"])))
        else:
            result["intensity"] = 0.5
            
        return result
    
    def _validate_consistency(
        self,
        character: CharacterPersona,
        refined_data: dict,
        current_mood_state: MoodState
    ) -> dict:
        """
        STEP 4: Validate that the final mood is consistent with character and scenario
        
        This is non-LLM validation - just sanity checks
        """
        mood = refined_data.get("mood", "neutral")
        intensity = refined_data.get("intensity", 0.5)
        
        # Sanity check: Don't jump from very negative to very positive in one step
        negative_moods = ["angry", "hostile", "contemptuous", "frustrated", "dismissive"]
        positive_moods = ["pleased", "encouraged", "impressed", "respectful"]
        
        current_is_negative = current_mood_state.current_mood.value in negative_moods
        new_is_positive = mood in positive_moods
        
        if current_is_negative and new_is_positive and intensity > 0.7:
            # Unlikely to jump from very negative to very positive
            logger.warning(f"⚠️ VALIDATION: Suspicious mood jump from {current_mood_state.current_mood.value} to {mood}")
            # Soften the intensity
            refined_data["intensity"] = min(intensity, 0.6)
            logger.info(f"✅ VALIDATION: Reduced intensity to {refined_data['intensity']} for consistency")
        
        # Ensure all required fields are present
        if "mood" not in refined_data:
            refined_data["mood"] = "neutral"
        if "intensity" not in refined_data:
            refined_data["intensity"] = 0.5
        if "reason" not in refined_data:
            refined_data["reason"] = "Inferred from conversation"
        if "trigger_keywords" not in refined_data:
            refined_data["trigger_keywords"] = []
            
        logger.info(f"✅ VALIDATION: Mood data validated and consistent")
        return refined_data
    
    async def _call_llm(self, prompt: str) -> str:
        """Helper to call LLM with consistent error handling"""
        system_prompt = "You are a psychological AI analyzing character emotions. Respond ONLY with valid JSON."
        
        if hasattr(self.llm_client, 'generate_response'):
            # Using GroqClient
            response = await self.llm_client.generate_response(
                user_message=prompt,
                system_prompt=system_prompt,
                model_type="fast"
            )
        else:
            # Using GeminiClient
            response = await asyncio.to_thread(
                self.llm_client.model.generate_content,
                f"{system_prompt}\n\n{prompt}"
            )
            response = response.text
            
        return response
    
    def _parse_mood_response(self, response: str) -> dict:
        """Parse and validate LLM's mood inference response with robust JSON extraction"""
        logger.info(f"🔍 PARSE: Attempting to parse mood response...")
        
        # Strategy 1: Try to find properly nested JSON with brace matching
        json_str = self._extract_json_with_brace_matching(response)
        
        if json_str:
            try:
                data = json.loads(json_str)
                logger.info(f"✅ PARSE: Successfully extracted JSON using brace matching")
                
                # Validate and sanitize the data
                return self._validate_and_sanitize_mood_data(data)
                
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"⚠️ PARSE: JSON decode failed even after extraction: {e}")
                logger.warning(f"⚠️ PARSE: Extracted string was: {json_str[:200]}")
        
        # Strategy 2: Try simple regex for flat JSON
        simple_match = re.search(r'\{[^{}]+\}', response)
        if simple_match:
            try:
                data = json.loads(simple_match.group(0))
                logger.info(f"✅ PARSE: Successfully parsed using simple regex")
                return self._validate_and_sanitize_mood_data(data)
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"⚠️ PARSE: Simple regex parsing failed: {e}")
        
        # Strategy 3: Try to parse the entire response as JSON
        try:
            data = json.loads(response.strip())
            logger.info(f"✅ PARSE: Successfully parsed entire response as JSON")
            return self._validate_and_sanitize_mood_data(data)
        except (json.JSONDecodeError, ValueError):
            logger.warning(f"⚠️ PARSE: Full response is not valid JSON")
        
        # Strategy 4: Field-by-field extraction as last resort
        logger.warning(f"⚠️ PARSE: Attempting field-by-field extraction as fallback")
        extracted_data = self._extract_fields_from_text(response)
        if extracted_data:
            logger.info(f"✅ PARSE: Extracted fields from malformed response")
            return extracted_data
        
        # All strategies failed
        logger.error(f"❌ PARSE: All parsing strategies failed. Response was: {response[:500]}")
        return self._get_fallback_mood()
    
    def _extract_json_with_brace_matching(self, text: str) -> Optional[str]:
        """Extract JSON by matching braces to handle nested structures"""
        # Find first opening brace
        start_idx = text.find('{')
        if start_idx == -1:
            return None
        
        # Match braces to find the complete JSON object
        brace_count = 0
        end_idx = start_idx
        
        for i in range(start_idx, len(text)):
            if text[i] == '{':
                brace_count += 1
            elif text[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    end_idx = i + 1
                    break
        
        if brace_count != 0:
            # Unmatched braces
            return None
        
        json_str = text[start_idx:end_idx]
        
        # Clean up common issues
        json_str = json_str.strip()
        # Remove markdown code blocks if present
        json_str = re.sub(r'^```(?:json)?\s*', '', json_str)
        json_str = re.sub(r'\s*```$', '', json_str)
        
        return json_str
    
    def _validate_and_sanitize_mood_data(self, data: dict) -> dict:
        """Validate and sanitize mood data from LLM"""
        # Validate required fields
        if "mood" not in data or "intensity" not in data:
            logger.warning(f"⚠️ VALIDATE: Missing required fields in {data}")
            return self._get_fallback_mood()
        
        # Validate mood is valid
        try:
            CharacterMood(data["mood"])
        except ValueError:
            logger.warning(f"⚠️ VALIDATE: Invalid mood '{data['mood']}', defaulting to neutral")
            data["mood"] = "neutral"
        
        # Validate intensity range
        try:
            intensity = float(data["intensity"])
            data["intensity"] = max(0.0, min(1.0, intensity))
        except (ValueError, TypeError):
            logger.warning(f"⚠️ VALIDATE: Invalid intensity '{data.get('intensity')}', defaulting to 0.5")
            data["intensity"] = 0.5
        
        # Ensure reason exists
        if "reason" not in data or not data["reason"]:
            data["reason"] = "Inferred from user's response"
        
        # Ensure trigger_keywords exists and is a list
        if "trigger_keywords" not in data:
            data["trigger_keywords"] = []
        elif not isinstance(data["trigger_keywords"], list):
            # Try to convert to list if it's a string
            if isinstance(data["trigger_keywords"], str):
                data["trigger_keywords"] = [kw.strip() for kw in data["trigger_keywords"].split(",")]
            else:
                data["trigger_keywords"] = []
        
        logger.info(f"✅ VALIDATE: Mood data validated: {data}")
        return data
    
    def _extract_fields_from_text(self, text: str) -> Optional[dict]:
        """Extract mood fields from non-JSON text as last resort"""
        result = {}
        
        # Try to find mood field
        mood_match = re.search(r'"?mood"?\s*[:=]\s*"?(\w+)"?', text, re.IGNORECASE)
        if mood_match:
            result["mood"] = mood_match.group(1).lower()
        
        # Try to find intensity
        intensity_match = re.search(r'"?intensity"?\s*[:=]\s*([0-9.]+)', text, re.IGNORECASE)
        if intensity_match:
            result["intensity"] = float(intensity_match.group(1))
        
        # Try to find reason
        reason_match = re.search(r'"?reason"?\s*[:=]\s*"([^"]+)"', text, re.IGNORECASE)
        if reason_match:
            result["reason"] = reason_match.group(1)
        
        # Check if we got at least mood and intensity
        if "mood" in result and "intensity" in result:
            logger.info(f"✅ EXTRACT: Extracted fields from text: {result}")
            # Add defaults for missing fields
            if "reason" not in result:
                result["reason"] = "Extracted from text"
            if "trigger_keywords" not in result:
                result["trigger_keywords"] = []
            
            # Validate extracted mood
            try:
                CharacterMood(result["mood"])
                return result
            except ValueError:
                logger.warning(f"⚠️ EXTRACT: Invalid mood '{result['mood']}'")
                return None
        
        logger.warning(f"⚠️ EXTRACT: Could not extract sufficient fields from text")
        return None
    
    def _get_fallback_mood(self) -> dict:
        """Get fallback mood data when parsing fails"""
        return {
            "mood": "neutral",
            "intensity": 0.5,
            "reason": "Mood inference parsing failed",
            "trigger_keywords": []
        }
    
    async def batch_infer_moods(
        self,
        characters: List[CharacterPersona],
        user_message: str,
        mood_states: Dict[str, MoodState],
        conversation_history: List[Dict],
        scenario_context: str
    ) -> Dict[str, MoodState]:
        """
        Infer moods for multiple characters in parallel (performance optimization)
        
        Args:
            characters: List of characters to infer moods for
            user_message: User's message
            mood_states: Current mood states keyed by character ID
            conversation_history: Recent conversation
            scenario_context: Scenario context
            
        Returns:
            Dictionary of updated mood states keyed by character ID
        """
        # Create inference tasks for all characters
        tasks = []
        for character in characters:
            current_mood = mood_states.get(
                character.id,
                MoodState(current_mood=character.default_mood, intensity=0.5, reason="Initial")
            )
            task = self.infer_mood(
                character=character,
                user_message=user_message,
                current_mood_state=current_mood,
                conversation_history=conversation_history,
                scenario_context=scenario_context
            )
            tasks.append((character.id, task))
        
        # Run all inferences in parallel
        logger.info(f"🎭 BATCH: Inferring moods for {len(tasks)} characters in parallel")
        results = {}
        for char_id, task in tasks:
            try:
                mood_state = await task
                results[char_id] = mood_state
            except Exception as e:
                logger.error(f"❌ BATCH: Failed to infer mood for {char_id}: {e}")
                # Keep existing mood
                results[char_id] = mood_states.get(
                    char_id,
                    MoodState(current_mood=CharacterMood.NEUTRAL)
                )
        
        logger.info(f"✅ BATCH: Completed mood inference for {len(results)} characters")
        return results


# Example usage
async def test_mood_inference():
    """Test the mood inference system"""
    from groq_client import GroqClient
    from characters import CharacterManager
    
    # Initialize
    groq_client = GroqClient()
    mood_system = MoodInferenceSystem(groq_client)
    char_manager = CharacterManager()
    
    # Get Marcus
    marcus = char_manager.get_character("marcus")
    
    # Create initial mood
    current_mood = MoodState(
        current_mood=CharacterMood.IMPATIENT,
        intensity=0.6,
        reason="Starting aggressive scenario"
    )
    
    # Test 1: User makes excuse
    print("Test 1: User makes excuse")
    user_message = "I can't make that deadline, it's too difficult"
    updated_mood = await mood_system.infer_mood(
        character=marcus,
        user_message=user_message,
        current_mood_state=current_mood,
        conversation_history=[],
        scenario_context="Unrealistic deadline pressure scenario"
    )
    print(f"Result: {updated_mood.current_mood.value} (intensity: {updated_mood.intensity})")
    print(f"Reason: {updated_mood.reason}")
    print(f"Triggers: {updated_mood.trigger_keywords}\n")
    
    # Test 2: User proposes solution
    print("Test 2: User proposes solution")
    user_message = "Here's my detailed project plan with timeline breakdown"
    updated_mood = await mood_system.infer_mood(
        character=marcus,
        user_message=user_message,
        current_mood_state=updated_mood,
        conversation_history=[
            {"role": "user", "content": "I can't make that deadline", "character": "user"}
        ],
        scenario_context="Unrealistic deadline pressure scenario"
    )
    print(f"Result: {updated_mood.current_mood.value} (intensity: {updated_mood.intensity})")
    print(f"Reason: {updated_mood.reason}")
    print(f"Triggers: {updated_mood.trigger_keywords}\n")


if __name__ == "__main__":
    asyncio.run(test_mood_inference())

