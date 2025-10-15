# SudoLang Implementation Guide

## Overview

This implementation combines **SudoLang's** declarative prompt structure with Python's type safety to create a hybrid approach for character behavior and mood inference.

### Key Features

1. **Iterative Mood Inference Pipeline** - Multi-step mood analysis inspired by SudoLang's `improve()` pattern
2. **SudoLang-Formatted Prompts** - Structured prompts using SudoLang's Preamble → State → Constraints → Instructions format
3. **Type-Safe Python Infrastructure** - Maintains dataclasses, enums, and serialization for production reliability
4. **Development Tools** - Interactive debugging commands similar to SudoLang's `/craft`, `/randomize`, `/list` commands

---

## Architecture

### Mood Inference Pipeline

The mood inference system now uses a **4-step iterative refinement** process:

```python
infer_mood(user_message, character, context) => {
    analyze_triggers(message) |>
    check_history(trajectory) |>
    refine_intensity(personality) |>
    validate_consistency(sanity_checks)
}
```

#### Step 1: Analyze Triggers
- Identifies keywords and behavioral patterns in user's message
- Determines preliminary mood based on triggers
- Returns: `{trigger_keywords, initial_mood, preliminary_reason}`

#### Step 2: Check History
- Analyzes mood trajectory (escalating, de-escalating, consistent)
- Considers conversation history and previous mood states
- Returns: `{trajectory, adjusted_mood, intensity, reason}`

#### Step 3: Refine Intensity
- Adjusts intensity based on character personality traits
- Aggressive characters → higher intensity (+0.1 to +0.3)
- Empathetic characters → lower intensity when user shows vulnerability
- Returns: `{mood, refined_intensity, reason}`

#### Step 4: Validate Consistency
- Non-LLM sanity checks to prevent impossible mood jumps
- Ensures mood transitions are realistic
- Returns: `{validated_mood, intensity, reason, trigger_keywords}`

### SudoLang Prompt Structure

Character prompts now follow SudoLang's declarative format:

```sudolang
# CharacterName

Roleplay as CharacterName, a character in a social skills training scenario.
Your job is to respond authentically maintaining complete character consistency.

## State {
    CurrentMood: angry
    MoodIntensity: 0.8
    MoodReason: "User keeps making excuses"
    ConversationContext: Active
    ResponseLength: 10-50 words
}

## Character Profile {
    Name: Marcus
    Personality: Results-driven, Impatient, Demanding
    CommunicationStyle: Direct, confrontational, deadline-focused
    Biography: You are a 50-year old high-functioning sociopath...
}

## Constraints {
    # Core Rules
    - ALWAYS stay in character as Marcus
    - NEVER break the fourth wall
    - NEVER repeat yourself
    
    # Behavioral Rules
    - React appropriately to user's tone
    - Remember conversation context
    - Be smart about deception attempts
}

## Emotional State {
    CurrentMood: ANGRY
    Intensity: 0.80 / 1.0
    EmotionalReason: "User keeps making excuses"
    TriggerKeywords: ["excuse", "can't", "difficult"]
}

## Active Behavioral Rules {
    Rule_1 {
        TriggeredBy: ["excuse", "can't", "impossible"]
        Mood: angry
        MinIntensity: 0.7
        
        Behaviors {
            - Use CAPS to emphasize anger
            - Interrupt or dismiss excuses immediately
            - Threaten consequences
            - Question their competence directly
        }
    }
}

## Intensity Calibration {
    Level: VERY HIGH (0.8+)
    Effect: Emotions SIGNIFICANTLY affect your response
    Guidance: "Let your strong feelings show clearly in tone and word choice"
}

## Response Instructions {
    # Output Format
    - Generate ONLY Marcus's direct dialog
    - No meta-commentary or narration
    - Sound natural, never sycophantic
    
    # Tone Calibration
    - Match communication style: Direct, confrontational
    - Reflect mood: angry at 0.8 intensity
    - Stay true to personality traits
}
```

---

## Usage

### Basic Character Interaction

```python
from characters import CharacterManager, MoodState, CharacterMood
from mood_inference import MoodInferenceSystem
from gemini_client import GeminiClient

# Initialize
gemini = GeminiClient()
char_manager = CharacterManager()
mood_system = MoodInferenceSystem(gemini)

# Get character
marcus = char_manager.get_character("marcus")

# Create initial mood
mood_state = MoodState(
    current_mood=CharacterMood.IMPATIENT,
    intensity=0.6,
    reason="Starting aggressive scenario"
)

# User says something
user_message = "I can't finish this by the deadline"

# Infer new mood (runs 4-step pipeline)
updated_mood = await mood_system.infer_mood(
    character=marcus,
    user_message=user_message,
    current_mood_state=mood_state,
    conversation_history=[],
    scenario_context="Unrealistic deadline pressure"
)

# Generate SudoLang-formatted prompt
prompt = marcus.generate_dynamic_prompt(
    mood_state=updated_mood,
    user_message=user_message,
    scenario_context="Unrealistic deadline pressure",
    character_role_context="You are the demanding boss"
)

# Send prompt to LLM for response
```

### Development Tools

The `character_dev_tools.py` module provides SudoLang-style commands for testing:

```bash
# Run interactive dev tools
python character_dev_tools.py

# Available commands:
/characters                              # List all characters
/test_mood marcus angry "I can't do it" # Test specific mood
/list_rules marcus angry                # Show behavior rules
/show_prompt marcus frustrated "..."    # Display full prompt
/mood_pipeline marcus "I need help"     # Debug mood inference
/compare marcus "excuse" angry,frustrated,skeptical
```

#### Example Dev Tool Output

```
╔══════════════════════════════════════════════════════════════════
║ TEST MOOD: Marcus in ANGRY mood
╚══════════════════════════════════════════════════════════════════

📝 User Message: "I can't finish this on time"

🎭 Character: Marcus
😤 Mood: angry (intensity: 0.7)
🎯 Scenario: Test scenario

═══════════════════════════════════════════════════════════════════
GENERATED SYSTEM PROMPT:
═══════════════════════════════════════════════════════════════════

# Marcus

Roleplay as Marcus, a character in a social skills training scenario...
[Full SudoLang prompt displayed]
```

### Testing

```bash
# Run comprehensive test suite
python test_sudolang_implementation.py
```

The test suite validates:
- ✅ Mood inference pipeline (4 steps)
- ✅ SudoLang prompt generation
- ✅ Behavior rule matching
- ✅ Dev tools functionality
- ✅ Full end-to-end integration

---

## Benefits of Hybrid Approach

### 1. LLM Parsing Clarity
**Before (Prose):**
```
You are Marcus. You are very angry right now because the user made an excuse.
When someone makes excuses, you should get confrontational and use caps...
```

**After (SudoLang):**
```sudolang
## Emotional State {
    CurrentMood: ANGRY
    Intensity: 0.80
}

## Active Behavioral Rules {
    Rule_1 {
        Behaviors {
            - Use CAPS to emphasize anger
            - Interrupt excuses immediately
        }
    }
}
```

The structured format makes it **much easier** for LLMs to parse and understand.

### 2. Iterative Refinement
The pipeline approach ensures mood inference is:
- **Consistent** - Step 4 validates against impossible transitions
- **Context-aware** - Step 2 considers conversation history
- **Personality-driven** - Step 3 adjusts for character traits
- **Accurate** - Step 1 identifies specific triggers

### 3. Python Type Safety
Unlike pure SudoLang (text-based), we maintain:
- `Enum` types for moods
- `dataclass` validation
- Serialization for session persistence
- IDE autocomplete and type checking

### 4. Debugging Power
Development tools provide instant visibility:
- See exact prompts sent to LLM
- Compare behavior across moods
- Test specific scenarios
- Debug mood pipeline step-by-step

---

## Customization

### Adding New Mood Behaviors

```python
# In characters.py, add to _generate_default_mood_rules()

MoodBehaviorRule(
    mood=CharacterMood.MANIPULATIVE,
    trigger_keywords=["vulnerable", "worried", "scared"],
    behaviors=[
        "Use their vulnerability against them",
        "Twist their words to make them doubt themselves",
        "Offer fake sympathy to gain trust",
        "Subtly shift blame to make them feel guilty"
    ],
    intensity_threshold=0.6
)
```

### Adding New Characters

Characters automatically get SudoLang formatting:

```python
characters["new_character"] = CharacterPersona(
    id="alex",
    name="Alex",
    biography="Your detailed character bio...",
    personality_traits=["Trait1", "Trait2", "Trait3"],
    communication_style="How they communicate",
    scenario_affinity=[ScenarioType.DATING],
    reference="Real person reference",
    voice_id="elevenlabs_voice_id"
)
```

The character will automatically:
- Generate SudoLang-formatted prompts
- Use the mood inference pipeline
- Inherit default mood behavior rules
- Work with dev tools

### Customizing Prompt Structure

Edit `CharacterPersona.generate_dynamic_prompt()` to modify the SudoLang template:

```python
# Add new sections
return f"""# {self.name}

## Custom Section {{
    YourField: value
    AnotherField: value
}}

{existing_sections}
"""
```

---

## Integration with Existing System

The SudoLang implementation is **backward compatible** with your existing Discord bot:

1. **Mood Inference**: Replace old `infer_mood()` calls with new pipeline (same interface)
2. **Prompt Generation**: Use `generate_dynamic_prompt()` instead of `generate_system_prompt()`
3. **Session Persistence**: `MoodState.to_dict()` and `from_dict()` unchanged

### Migration Example

**Before:**
```python
prompt = character.generate_system_prompt(
    scenario_context=scenario,
    character_role_context=role
)
```

**After:**
```python
prompt = character.generate_dynamic_prompt(
    mood_state=current_mood,
    user_message=user_msg,
    scenario_context=scenario,
    character_role_context=role
)
```

---

## Performance Considerations

### LLM Calls in Pipeline

The mood inference pipeline makes **3 LLM calls** per user message:
1. Step 1: Trigger analysis
2. Step 2: History check
3. Step 3: Intensity refinement

**Total cost per interaction**: ~3x base inference cost

### Optimization Options

1. **Cache common patterns** - If user says same thing repeatedly, cache mood result
2. **Batch processing** - Use `batch_infer_moods()` for multi-character scenarios
3. **Fast model for pipeline** - Use cheaper model for steps 1-3, main model for response
4. **Skip pipeline for neutral moods** - If already neutral and no triggers, skip inference

### Example Optimization

```python
# Use fast model for mood inference
if hasattr(llm_client, 'generate_response'):
    # GroqClient supports model_type parameter
    response = await llm_client.generate_response(
        user_message=prompt,
        system_prompt=system,
        model_type="fast"  # Uses faster/cheaper model
    )
```

---

## Monitoring and Debugging

### Enable Detailed Logging

```python
import logging
logging.basicConfig(level=logging.INFO)

# Mood pipeline logs:
# 📍 STEP 1 (Triggers): Found 3 triggers
# 📍 STEP 2 (History): Trajectory = escalating
# 📍 STEP 3 (Intensity): Refined to 0.8
# 📍 STEP 4 (Validation): Final mood = angry
```

### Use Dev Tools for Testing

```bash
python character_dev_tools.py

>>> /mood_pipeline marcus "I can't do it"
# Shows full pipeline execution with step-by-step results
```

### Review Generated Prompts

```python
from character_dev_tools import CharacterDevTools

dev_tools = CharacterDevTools(gemini_client)
prompt = dev_tools.show_prompt("marcus", "angry", "test message")
print(prompt)
```

---

## Best Practices

### 1. Tune Behavior Rules
Monitor actual character responses and adjust rules:
- If character not aggressive enough → lower `intensity_threshold`
- If behaviors too generic → add more specific trigger keywords
- If rules conflict → reorder or merge them

### 2. Monitor Mood Trajectories
Watch for unrealistic mood jumps:
- Step 4 validation catches some issues
- Add custom validation for your specific scenarios
- Log mood transitions for analysis

### 3. Optimize for Your LLM
Different models parse SudoLang differently:
- GPT-4: Excellent with structured prompts
- Claude: Very good with clear sections
- Gemini: Benefits from explicit field labels
- Adjust formatting based on your model

### 4. Balance Complexity
More rules ≠ better behavior:
- Start with default rules
- Add specific rules only when needed
- Remove rules that don't improve responses

---

## Future Enhancements

### Potential Improvements

1. **Mood Rule Learning** - Automatically generate rules from successful interactions
2. **Multi-Character Dynamics** - Mood influences between characters
3. **Emotional Memory** - Long-term emotional states beyond single session
4. **Voice Integration** - Map moods to voice tone parameters
5. **A/B Testing** - Compare SudoLang vs prose prompts systematically

### Experimental Features

```python
# Example: Multi-character mood synchronization
async def sync_character_moods(characters, event):
    """When one character reacts, others respond emotionally"""
    for char in characters:
        if char.has_relationship_with(event.source):
            char.mood_state.react_to(event)
```

---

## Troubleshooting

### Issue: Mood pipeline too slow
**Solution**: Use faster model for pipeline, main model for response

### Issue: Mood not changing appropriately
**Solution**: Check trigger keywords match user's actual language patterns

### Issue: Character breaking format
**Solution**: Review `## Constraints` section, add more explicit rules

### Issue: Behavior rules not triggering
**Solution**: Use `/mood_pipeline` command to debug step-by-step

### Issue: LLM not following SudoLang structure
**Solution**: Add more examples in prompt, or increase temperature slightly

---

## Conclusion

The hybrid SudoLang approach provides:
- ✅ **Clearer prompts** for LLM understanding
- ✅ **Iterative refinement** for accurate mood inference
- ✅ **Type safety** for production reliability
- ✅ **Development tools** for rapid testing
- ✅ **Backward compatibility** with existing system

This combines the best of both worlds: SudoLang's expressive power with Python's engineering robustness.

---

## Quick Reference

### Commands
```bash
python character_dev_tools.py          # Interactive dev tools
python test_sudolang_implementation.py # Run test suite
```

### Key Classes
- `MoodInferenceSystem` - Handles 4-step mood pipeline
- `CharacterPersona` - Generates SudoLang prompts
- `MoodBehaviorRule` - Defines mood → behavior mappings
- `CharacterDevTools` - Development commands

### Important Methods
- `infer_mood()` - Run mood inference pipeline
- `generate_dynamic_prompt()` - Create SudoLang prompt
- `generate_mood_based_instructions()` - Format mood rules

### Files Modified
- `mood_inference.py` - Added pipeline steps
- `characters.py` - Added SudoLang formatting
- `character_dev_tools.py` - NEW: Dev commands
- `test_sudolang_implementation.py` - NEW: Test suite

---

**Last Updated**: December 2024
**Implementation Version**: 1.0
**Status**: Production Ready ✅

