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
    
    def __init__(self, llm_client):
        """
        Initialize with your LLM client (Groq or Gemini)
        
        Args:
            llm_client: GroqClient or GeminiClient instance
        """
        self.llm_client = llm_client
        logger.info("✅ MoodInferenceSystem initialized")
    
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
        
        Args:
            character: The character whose mood we're inferring
            user_message: What the user just said
            current_mood_state: Character's current emotional state
            conversation_history: Recent conversation context
            scenario_context: The scenario context
            
        Returns:
            Updated MoodState with new mood, intensity, reason, and trigger keywords
        """
        # Build mood inference prompt
        available_moods = [mood.value for mood in CharacterMood]
        current_mood_info = f"Currently feeling: {current_mood_state.current_mood.value} (intensity: {current_mood_state.intensity})"
        
        # Get recent conversation context (last 3-4 exchanges)
        recent_context = self._format_recent_conversation(conversation_history[-6:])
        
        inference_prompt = f"""You are analyzing how {character.name} would emotionally respond to what the user just said.

CHARACTER PROFILE:
- Name: {character.name}
- Personality: {', '.join(character.personality_traits[:5])}
- Communication Style: {character.communication_style}
- Biography: {character.biography[:300]}...
- Current Mood: {current_mood_info}

SCENARIO CONTEXT:
{scenario_context[:400]}...

RECENT CONVERSATION:
{recent_context}

USER'S LATEST MESSAGE:
"{user_message}"

Based on {character.name}'s personality and what the user just said, determine:
1. What MOOD would {character.name} feel right now?
2. How INTENSE is this emotion (0.0 to 1.0)?
3. WHY does {character.name} feel this way?
4. What KEYWORDS in the user's message triggered this mood?

Available moods: {', '.join(available_moods)}

IMPORTANT CHARACTER-SPECIFIC CONSIDERATIONS:
- If {character.name} has aggressive traits (demanding, intimidating, bullying), they escalate to anger QUICKLY
- If {character.name} has manipulative traits, they may feel calculating or manipulative when challenged
- If {character.name} has empathetic traits, they soften when users show vulnerability
- Consider the TRAJECTORY: Is the user making things better or worse?

RESPOND ONLY WITH VALID JSON in this exact format:
{{
    "mood": "one_of_the_available_moods",
    "intensity": 0.7,
    "reason": "Brief explanation of why they feel this way based on user's message",
    "trigger_keywords": ["keyword1", "keyword2"]
}}

Example 1 (User making excuses to aggressive boss):
{{
    "mood": "frustrated",
    "intensity": 0.8,
    "reason": "User is making excuses instead of taking responsibility",
    "trigger_keywords": ["excuse", "can't", "difficult"]
}}

Example 2 (User presenting solution to skeptical boss):
{{
    "mood": "skeptical",
    "intensity": 0.6,
    "reason": "User proposed something concrete but I need to verify it's not just talk",
    "trigger_keywords": ["plan", "proposal"]
}}

Example 3 (User pushed back effectively):
{{
    "mood": "impressed",
    "intensity": 0.7,
    "reason": "User stood their ground with data and didn't back down",
    "trigger_keywords": ["data", "specifically", "timeline"]
}}

CRITICAL: Consider {character.name}'s personality - aggressive characters get angry faster, empathetic characters soften more easily."""

        try:
            logger.info(f"🎭 MOOD: Inferring mood for {character.name}")
            logger.info(f"🎭 MOOD: Current state: {current_mood_state.current_mood.value} ({current_mood_state.intensity})")
            logger.info(f"🎭 MOOD: User message: '{user_message[:100]}...'")
            
            # Call LLM to infer mood
            if hasattr(self.llm_client, 'generate_response'):
                # Using GroqClient
                response = await self.llm_client.generate_response(
                    user_message=inference_prompt,
                    system_prompt="You are a psychological AI that analyzes character emotions. Respond only with valid JSON.",
                    model_type="fast"
                )
            else:
                # Using GeminiClient
                logger.info(f"🎭 MOOD: Using Gemini for mood inference")
                response = await asyncio.to_thread(
                    self.llm_client.model.generate_content,
                    inference_prompt
                )
                response = response.text
                logger.info(f"🎭 MOOD: Gemini returned response type: {type(response)}")
            
            logger.info(f"🎭 MOOD: LLM raw response (full): {response}")
            
            # Parse JSON response
            mood_data = self._parse_mood_response(response)
            
            # Create new mood state
            new_mood = CharacterMood(mood_data["mood"])
            intensity = float(mood_data["intensity"])
            reason = mood_data["reason"]
            triggers = mood_data.get("trigger_keywords", [])
            
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

