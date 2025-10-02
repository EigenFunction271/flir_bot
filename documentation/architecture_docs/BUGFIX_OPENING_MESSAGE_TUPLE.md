# 🐛 Bug Fix: Opening Message Tuple Response

## Issue Description

When starting a scenario, the opening messages were displaying as tuples instead of clean text:

```
('We've moved the deadline up 2 weeks...', MoodState(current_mood=<CharacterMood.NEUTRAL: 'neutral'>, ...))
Turn 1/3 • 2 turns remaining
💬 Sarah
('Hey Marcus, thanks for the update...', MoodState(...))
```

Additionally, session saving was failing with:
```
❌ Failed to save sessions: Object of type MoodState is not JSON serializable
```

## Root Cause

The `_generate_character_response_with_fallback()` method was updated to return a tuple `(str, MoodState)` for mood tracking, but the opening message generation code was still treating it as if it only returned a string.

**Problem code (line 1249-1251):**
```python
# OLD - Treating return value as string
opening_message = await self._generate_character_response_with_fallback(
    opening_prompt, character, [], scenario.context, character_role_context
)
# opening_message is actually: ('text', MoodState(...))
```

This caused:
1. The entire tuple to be used as the message description
2. The tuple to be saved in conversation_history (causing serialization error)

## Solution

Updated the opening message generation to:
1. Properly unpack the tuple return value
2. Pass the current mood state to the function
3. Update the character's mood after generation
4. Use mood-based colors and emojis

**Fixed code (lines 1248-1279):**
```python
# Get character's initial mood
current_mood = self.active_sessions[user_id]["character_moods"].get(
    character.id,
    MoodState(current_mood=character.default_mood, intensity=0.7, reason="Starting scenario")
)

# Generate opening message with mood - UNPACK TUPLE
opening_message, updated_mood = await self._generate_character_response_with_fallback(
    message=opening_prompt,
    character=character,
    conversation_history=[],
    scenario_context=scenario.context,
    character_role_context=character_role_context,
    current_mood_state=current_mood  # Pass mood state
)

# Update mood in session
self.active_sessions[user_id]["character_moods"][character.id] = updated_mood

# Get mood color and emoji
mood_color = self._get_mood_color(updated_mood.current_mood)
mood_emoji = self._get_mood_emoji(updated_mood.current_mood)

# Create embed with clean message text
opening_embed = discord.Embed(
    title=f"💬 {character.name}",
    description=opening_message,  # Just the string, not the tuple
    color=mood_color
)

opening_embed.set_footer(text=f"{mood_emoji} {updated_mood.current_mood.value} • Turn 1/{Config.MAX_CONVERSATION_TURNS}")
```

## Changes Made

### File: `discord_bot.py`

**Lines 1248-1279** - Updated opening message generation:
- ✅ Get character's initial mood from session
- ✅ Pass `current_mood_state` parameter
- ✅ Unpack tuple: `opening_message, updated_mood = await ...`
- ✅ Update character's mood in session after generation
- ✅ Use mood-based embed color
- ✅ Add mood emoji and name to footer

## Expected Output (After Fix)

```
💬 Marcus
We've moved the deadline up 2 weeks. Get it done in a week. No excuses. If you can't, we'll find someone who can. Now, what's the plan?
⏱️ impatient • Turn 1/3

💬 Sarah
Hey Marcus, I understand the urgency. Let's review the project scope and see how we can realistically deliver quality work in this timeframe.
😐 neutral • Turn 1/3
```

## Verification

### Before Fix:
```
2025-10-02 07:29:18,219 - Generated opening message: ('We've moved the deadline...', MoodState(...))
2025-10-02 07:29:21,855 - ❌ Failed to save sessions: Object of type MoodState is not JSON serializable
```

### After Fix (Expected):
```
2025-10-02 07:29:18,219 - Generated opening message: We've moved the deadline...
2025-10-02 07:29:18,220 - 🎭 MOOD UPDATE: Marcus mood: impatient (0.7)
2025-10-02 07:29:21,855 - 💾 Saved 1 active sessions
```

## Related Issues

This same pattern needs to be checked in any other place that calls `_generate_character_response_with_fallback()`:

✅ **Multi-character responses** (line 1678) - Already fixed correctly
✅ **Fallback single character** (line 1775) - Already fixed correctly  
✅ **Opening messages** (line 1255) - NOW FIXED

## Testing

To verify the fix:
1. Start a scenario: `!start workplace_deadline`
2. Check that opening messages display cleanly (no tuples)
3. Check that embeds show mood colors and emojis
4. Verify no serialization errors in logs
5. Confirm session saves successfully

## Status

✅ **FIXED** - Opening messages now display correctly with mood tracking

---

**Date:** 2025-01-02  
**Priority:** High (User-facing bug)  
**Fixed By:** Updated opening message generation to properly handle tuple return value

