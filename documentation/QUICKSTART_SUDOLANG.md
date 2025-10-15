# SudoLang Quick Start Guide

Get started with the new SudoLang implementation in 5 minutes!

## 1. Test the Implementation (2 min)

```bash
# Run the comprehensive test suite
python test_sudolang_implementation.py
```

**Expected output:**
```
╔══════════════════════════════════════════════════════════════════
║ SUDOLANG IMPLEMENTATION TEST SUITE
╚══════════════════════════════════════════════════════════════════

TEST 1: Iterative Mood Inference Pipeline
[Shows 4-step pipeline execution]

TEST 2: SudoLang-Formatted Prompts
[Validates prompt structure]

...

✅ ALL TESTS PASSED!
```

If all tests pass, you're ready to go! ✅

## 2. Try the Dev Tools (3 min)

```bash
# Start interactive dev tools
python character_dev_tools.py
```

**Try these commands:**

```bash
# List all characters
>>> /characters
Available characters: Marcus, Sarah, David, Emma, James, Alex, Jordan, ...

# Test Marcus in angry mood
>>> /test_mood marcus angry "I can't finish this"
[Shows full SudoLang prompt]

# See behavior rules for angry mood
>>> /list_rules marcus angry
[Shows all rules triggered by angry mood]

# Debug the mood inference pipeline
>>> /mood_pipeline marcus "I need more time"
📍 STEP 1 (Triggers): Found 2 triggers
📍 STEP 2 (History): Trajectory = consistent
📍 STEP 3 (Intensity): Refined to 0.6
📍 STEP 4 (Validation): Final mood = frustrated

# Compare different moods
>>> /compare marcus "excuse" angry,frustrated,skeptical
[Side-by-side comparison]
```

## 3. Integrate with Your Bot (5 min)

### Current Code (if using old system)

```python
# discord_bot.py or wherever you generate responses

# OLD WAY (still works, but deprecated)
prompt = character.generate_system_prompt(
    scenario_context=scenario_context,
    character_role_context=character_role
)
```

### Updated Code (SudoLang)

```python
# NEW WAY (recommended)
from mood_inference import MoodInferenceSystem
from gemini_client import GeminiClient

# Initialize (do this once)
gemini = GeminiClient()
mood_system = MoodInferenceSystem(gemini)

# In your message handler:
# 1. Infer mood using 4-step pipeline
updated_mood = await mood_system.infer_mood(
    character=character,
    user_message=user_message,
    current_mood_state=current_mood_state,  # Track this in session
    conversation_history=conversation_history,
    scenario_context=scenario_context
)

# 2. Generate SudoLang-formatted prompt
prompt = character.generate_dynamic_prompt(
    mood_state=updated_mood,
    user_message=user_message,
    scenario_context=scenario_context,
    character_role_context=character_role_context
)

# 3. Get LLM response (as before)
response = await gemini.generate_content(prompt)
```

### Session Management

```python
# Store mood state in session
session_data['mood_states'] = {
    character.id: updated_mood.to_dict()
}

# Restore mood state
mood_state = MoodState.from_dict(session_data['mood_states'][character.id])
```

## 4. Monitor and Debug

### Enable Logging

```python
import logging

# See mood pipeline steps
logging.basicConfig(level=logging.INFO)
```

**You'll see:**
```
📍 STEP 1 (Triggers): Found 3 triggers
📍 STEP 2 (History): Trajectory = escalating
📍 STEP 3 (Intensity): Refined to 0.8
📍 STEP 4 (Validation): Final mood = angry
✅ MOOD PIPELINE: Marcus mood updated: angry (intensity: 0.8)
```

### Use Dev Tools for Debugging

```bash
# If character not responding as expected:
python character_dev_tools.py

# Show the exact prompt being sent
>>> /show_prompt marcus angry "test message"

# Debug the mood inference
>>> /mood_pipeline marcus "user's actual message"
```

## 5. Customize (Optional)

### Add Character-Specific Rules

```python
# In characters.py, add to specific character

marcus.mood_behavior_rules.append(
    MoodBehaviorRule(
        mood=CharacterMood.ANGRY,
        trigger_keywords=["deadline", "urgent", "asap"],
        behaviors=[
            "Emphasize the time pressure",
            "Demand immediate action",
            "Use short, clipped sentences"
        ],
        intensity_threshold=0.6
    )
)
```

### Adjust Pipeline

```python
# In mood_inference.py, modify intensity calculation

# Example: Make aggressive characters even more intense
if is_aggressive:
    result["intensity"] += 0.3  # Changed from +0.1 to +0.3
```

## Common Issues

### Issue: "Module not found"
**Solution**: Make sure you're in the project directory
```bash
cd /path/to/flir_telegram
```

### Issue: "Gemini API error"
**Solution**: Check your API key in `.env`
```bash
GEMINI_API_KEY=your_key_here
```

### Issue: "Tests fail"
**Solution**: Check logs for specific error
```bash
python test_sudolang_implementation.py 2>&1 | tee test_log.txt
```

### Issue: "Character not responding as expected"
**Solution**: Use dev tools to debug
```bash
python character_dev_tools.py
>>> /show_prompt character_id mood "message"
```

## Next Steps

1. ✅ **Read Full Documentation**: `documentation/SUDOLANG_IMPLEMENTATION.md`
2. ✅ **See Before/After**: `documentation/BEFORE_AFTER_COMPARISON.md`
3. ✅ **Experiment**: Use dev tools to test different scenarios
4. ✅ **Integrate**: Update your bot code to use SudoLang prompts
5. ✅ **Monitor**: Watch logs to see pipeline in action
6. ✅ **Fine-tune**: Adjust rules based on actual responses

## Quick Reference

### Key Files
- `mood_inference.py` - 4-step mood pipeline
- `characters.py` - SudoLang prompt generation
- `character_dev_tools.py` - Interactive testing
- `test_sudolang_implementation.py` - Test suite

### Key Commands
```bash
python test_sudolang_implementation.py     # Run tests
python character_dev_tools.py              # Interactive dev tools
```

### Key Classes
```python
MoodInferenceSystem(llm_client)           # Mood pipeline
CharacterPersona.generate_dynamic_prompt() # SudoLang prompts
CharacterDevTools(llm_client)             # Dev tools
```

### Dev Tool Commands
```
/characters                                # List all
/test_mood <char> <mood> <msg>            # Test mood
/list_rules <char> [mood]                 # Show rules
/show_prompt <char> <mood> <msg>          # See prompt
/mood_pipeline <char> <msg>               # Debug pipeline
/compare <char> <msg> <moods>             # Compare moods
```

## Support

- **Documentation**: See `documentation/` folder
- **Examples**: Check `test_sudolang_implementation.py`
- **Issues**: Check logs and use dev tools to debug

---

**Ready to go!** Start with the test suite, play with dev tools, then integrate. 🚀

