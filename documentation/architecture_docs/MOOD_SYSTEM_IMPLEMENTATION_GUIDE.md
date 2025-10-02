# 🎭 Dynamic Mood-Based Character System - Implementation Guide

This guide walks you through implementing the dynamic mood system for your Flir bot characters.

## 📊 System Overview

The mood system makes characters emotionally responsive by:
1. **Tracking emotional state** (mood, intensity, reason)
2. **Inferring mood changes** using LLM before each response
3. **Adapting responses** based on current emotional state
4. **Persisting moods** across session saves/loads

## 🎯 Key Benefits

- **More realistic characters**: They get angry, frustrated, hurt, or supportive based on user actions
- **Dynamic conversations**: Same character responds differently based on emotional state
- **Better training**: Users learn how their words affect others emotionally
- **Deeper engagement**: Characters feel alive and reactive

## 📋 Implementation Checklist

### Phase 1: Core Infrastructure (30 min)
- [ ] Copy `CharacterMood` enum to `characters.py` (after line 8)
- [ ] Copy `MoodState` dataclass to `characters.py` (after `CharacterMood`)
- [ ] Add `mood_templates` and `default_mood` fields to `CharacterPersona`
- [ ] Add `_generate_default_mood_templates()` method to `CharacterPersona`
- [ ] Add `get_initial_mood_for_scenario()` method to `CharacterPersona`
- [ ] Add `generate_dynamic_prompt()` method to `CharacterPersona`

### Phase 2: Mood Inference (20 min)
- [ ] Create `mood_inference.py` file
- [ ] Copy `MoodInferenceSystem` class from scaffold
- [ ] Test mood inference with a simple example
- [ ] Add config values to `config.py`

### Phase 3: Session Integration (45 min)
- [ ] Update session structure in `FlirBot.__init__` to include mood inference
- [ ] Update `_create_session` to initialize character moods (in `start_scenario`)
- [ ] Update `_serialize_sessions_for_json` to save mood states
- [ ] Update `_reconstruct_session` to restore mood states
- [ ] Update `_generate_character_response_with_fallback` to use mood inference
- [ ] Update `_generate_multi_character_responses` to track moods

### Phase 4: UI Enhancement (15 min)
- [ ] Add `_get_mood_color()` helper for Discord embed colors
- [ ] Add `_get_mood_emoji()` helper for mood indicators
- [ ] Update response embeds to show mood state

### Phase 5: Testing (30 min)
- [ ] Test with aggressive character (Marcus)
- [ ] Test with empathetic character (Sarah)
- [ ] Test mood persistence through save/load
- [ ] Test mood inference accuracy

## 🚀 Quick Start Implementation

### Step 1: Add Mood System to `characters.py`

```python
# At the top of characters.py, after ScenarioType
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum

class CharacterMood(Enum):
    """Represents the emotional state of a character"""
    NEUTRAL = "neutral"
    HAPPY = "happy"
    EXCITED = "excited"
    CONFIDENT = "confident"
    ANNOYED = "annoyed"
    FRUSTRATED = "frustrated"
    ANGRY = "angry"
    DEFENSIVE = "defensive"
    HURT = "hurt"
    EMPATHETIC = "empathetic"
    SUPPORTIVE = "supportive"
    MANIPULATIVE = "manipulative"
    SARCASTIC = "sarcastic"
    # Add more as needed

@dataclass
class MoodState:
    """Tracks a character's current emotional state"""
    current_mood: CharacterMood
    intensity: float = 0.7
    reason: str = ""
    previous_mood: Optional[CharacterMood] = None
    mood_history: List[CharacterMood] = field(default_factory=list)
    
    def update_mood(self, new_mood: CharacterMood, intensity: float, reason: str):
        self.mood_history.append(self.current_mood)
        self.previous_mood = self.current_mood
        self.current_mood = new_mood
        self.intensity = intensity
        self.reason = reason
    
    def to_dict(self) -> dict:
        return {
            "current_mood": self.current_mood.value,
            "intensity": self.intensity,
            "reason": self.reason,
            "previous_mood": self.previous_mood.value if self.previous_mood else None,
            "mood_history": [mood.value for mood in self.mood_history[-5:]]
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'MoodState':
        return cls(
            current_mood=CharacterMood(data["current_mood"]),
            intensity=data.get("intensity", 0.7),
            reason=data.get("reason", ""),
            previous_mood=CharacterMood(data["previous_mood"]) if data.get("previous_mood") else None,
            mood_history=[CharacterMood(m) for m in data.get("mood_history", [])]
        )
```

### Step 2: Update `CharacterPersona` dataclass

```python
@dataclass
class CharacterPersona:
    id: str
    name: str
    biography: str
    personality_traits: List[str]
    communication_style: str
    scenario_affinity: List[ScenarioType]
    reference: Optional[str] = None
    voice_id: Optional[str] = None
    
    # NEW: Mood system fields
    mood_templates: Dict[CharacterMood, str] = field(default_factory=dict)
    default_mood: CharacterMood = CharacterMood.NEUTRAL
    
    def __post_init__(self):
        if not self.mood_templates:
            self.mood_templates = self._generate_default_mood_templates()
    
    # Add all methods from the scaffold
```

### Step 3: Create `mood_inference.py`

Copy the entire `MoodInferenceSystem` class from the scaffold.

### Step 4: Update `discord_bot.py`

```python
# In FlirBot.__init__, add:
from mood_inference import MoodInferenceSystem
self.mood_inference = MoodInferenceSystem(self.groq_client)

# In start_scenario command, initialize moods:
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
    # ... existing fields ...
    "character_moods": character_moods  # NEW
}
```

### Step 5: Update Response Generation

```python
async def _generate_character_response_with_fallback(
    self, 
    message: str, 
    character: CharacterPersona, 
    conversation_history: List[Dict], 
    scenario_context: str = None,
    character_role_context: str = None,
    current_mood_state: MoodState = None  # NEW
) -> tuple[str, MoodState]:
    """Generate response with mood inference"""
    
    # STEP 1: Infer new mood
    if current_mood_state:
        updated_mood = await self.mood_inference.infer_mood(
            character=character,
            user_message=message,
            current_mood_state=current_mood_state,
            conversation_history=conversation_history,
            scenario_context=scenario_context
        )
    else:
        # Fallback for backward compatibility
        updated_mood = MoodState(current_mood=character.default_mood)
    
    # STEP 2: Generate mood-aware prompt
    system_prompt = character.generate_dynamic_prompt(
        mood_state=updated_mood,
        scenario_context=scenario_context,
        character_role_context=character_role_context
    )
    
    # STEP 3: Generate response
    response = await self.groq_client.generate_response_with_history(
        user_message=message,
        system_prompt=system_prompt,
        conversation_history=conversation_history,
        model_type="fast",
        current_character_name=character.name
    )
    
    return response, updated_mood
```

## 🧪 Testing Your Implementation

### Test 1: Basic Mood Inference

```python
# Create a test scenario
character = self.character_manager.get_character("marcus")
mood_state = MoodState(current_mood=CharacterMood.NEUTRAL, intensity=0.5, reason="Test")

# Test with aggressive message
user_message = "I need more time on this project."
updated_mood = await self.mood_inference.infer_mood(
    character=character,
    user_message=user_message,
    current_mood_state=mood_state,
    conversation_history=[],
    scenario_context="Tight deadline scenario"
)

print(f"Mood: {updated_mood.current_mood.value}")
print(f"Intensity: {updated_mood.intensity}")
print(f"Reason: {updated_mood.reason}")
# Expected: FRUSTRATED or ANGRY
```

### Test 2: Mood Persistence

```python
# Start a scenario, interact, then check if moods are saved
# Load the session and verify moods are restored
```

### Test 3: Mood-Based Responses

```python
# Compare responses with same input but different moods
# Marcus in NEUTRAL vs ANGRY should respond very differently
```

## 🎨 Customizing Character Moods

### Example: Marcus with Custom Mood Templates

```python
marcus_mood_templates = {
    CharacterMood.ANGRY: """You're FURIOUS. The user is wasting your time.
    - Use aggressive language
    - Threaten consequences (firing, performance reviews)
    - Use CAPS for emphasis
    - Be confrontational and hostile""",
    
    CharacterMood.FRUSTRATED: """You're losing patience fast.
    - Short, terse responses
    - Question their competence
    - Show visible irritation""",
    
    CharacterMood.GRUDGINGLY_RESPECTFUL: """The user earned your respect.
    - Slightly less hostile
    - Acknowledge their point (reluctantly)
    - Still maintain authority"""
}

characters["marcus"] = CharacterPersona(
    # ... other fields ...
    mood_templates=marcus_mood_templates,
    default_mood=CharacterMood.IMPATIENT  # Marcus starts impatient
)
```

## 🐛 Common Issues & Solutions

### Issue 1: Mood Inference Too Slow
**Solution**: Enable caching or reduce inference frequency
```python
# In config.py
MOOD_UPDATE_FREQUENCY = 2  # Update every 2 messages instead of every message
```

### Issue 2: Moods Not Persisting
**Solution**: Check serialization in `_serialize_sessions_for_json`
```python
# Make sure you're calling .to_dict() on MoodState objects
serialized_moods[char_id] = mood_state.to_dict()
```

### Issue 3: LLM Returns Invalid Mood
**Solution**: The `_parse_mood_response` method handles this with fallbacks

### Issue 4: Mood Changes Too Drastically
**Solution**: Add mood transition smoothing
```python
# Add to MoodState.update_mood
if self.current_mood == new_mood:
    # Mood stays same, just adjust intensity
    self.intensity = (self.intensity + intensity) / 2
```

## 📊 Performance Considerations

### Optimization Strategies

1. **Batch Mood Inference**: For multiple characters, consider parallel inference
2. **Mood Caching**: Cache mood for rapid-fire messages
3. **Smart Updates**: Only infer mood if message is significant
4. **Model Selection**: Use "fast" model for mood inference

```python
# Example: Only infer if message is long enough
if len(user_message.split()) > 5:
    updated_mood = await self.mood_inference.infer_mood(...)
else:
    updated_mood = current_mood_state  # Keep current mood
```

## 🎯 Expected Impact

After implementation, you should see:

### Before (Static):
```
User: "I can't make that deadline."
Marcus: "That's not acceptable. The deadline is firm."
```

### After (Dynamic with Mood):
```
User: "I can't make that deadline."
Marcus (FRUSTRATED, intensity=0.8): "I don't want to hear excuses. Find a way or find a new job."

[Later in conversation after user makes good point]
Marcus (GRUDGINGLY_RESPECTFUL, intensity=0.6): "Fine. You've made a valid point about the dependencies. Two weeks."
```

## 🔄 Migration Path

### Phase 1: Soft Launch (Backward Compatible)
- Implement mood system but keep old methods
- Test with flag: `MOOD_INFERENCE_ENABLED = True/False`
- Characters work with or without mood system

### Phase 2: Gradual Rollout
- Enable for specific characters first (Marcus, Patricia)
- Monitor performance and accuracy
- Gather user feedback

### Phase 3: Full Deployment
- Enable for all characters
- Remove old `generate_system_prompt` method
- Optimize based on data

## 📚 Next Steps

After basic implementation:

1. **Analytics**: Track mood distributions per character
2. **Visualization**: Show mood graph at end of scenario
3. **Advanced Moods**: Add compound moods (angry-but-respectful)
4. **Mood Memory**: Characters remember how user made them feel
5. **Scenario-Specific Moods**: Different mood sets per scenario type

## 🆘 Need Help?

Common questions:

**Q: How many moods should I define?**
A: Start with 10-15 core moods, expand based on need.

**Q: Should every character have custom mood templates?**
A: No, defaults work fine. Customize only key characters (Marcus, Patricia, Victor).

**Q: How accurate is mood inference?**
A: ~80-90% with good prompts. Monitor and adjust prompt if needed.

**Q: Can moods affect other characters?**
A: Yes! One character's anger can make another defensive. Future enhancement.

## ✅ Completion Criteria

You're done when:
- [ ] Characters show mood in embed footer
- [ ] Mood persists through save/load
- [ ] Marcus gets angrier when user makes excuses
- [ ] Sarah becomes supportive when user shows vulnerability
- [ ] Mood inference completes in <2 seconds
- [ ] No errors in logs related to mood system

---

**Created**: 2025-01-02
**Version**: 1.0
**Estimated Implementation Time**: 2-3 hours

Good luck! 🚀

