# 🎭 Mood System Architecture

## Overview

The mood system uses a **hybrid approach**:
- **LLM determines WHAT the character feels** (flexible, context-aware)
- **Rules determine HOW that feeling manifests** (deterministic, controllable)

---

## 🔄 Complete Flow

```
1. USER SENDS MESSAGE
   ↓
2. LLM MOOD INFERENCE (mood_inference.py)
   → Analyzes: character personality + user message + conversation history
   → Returns: {mood: "angry", intensity: 0.8, reason: "...", triggers: ["excuse", "can't"]}
   ↓
3. RULE MATCHING (characters.py)
   → Checks: IF mood="angry" AND user said "excuse" AND intensity >= 0.7
   → Finds matching behavioral rules
   ↓
4. INSTRUCTION GENERATION (characters.py)
   → Appends explicit behaviors to system prompt
   → "Use CAPS to emphasize anger"
   → "Threaten consequences"
   ↓
5. LLM RESPONSE GENERATION
   → Follows the mood-specific behavioral instructions
   → Generates character response
```

---

## 📊 Component Breakdown

### Component 1: LLM Mood Inference (`mood_inference.py`)

**Purpose**: Determine how the character FEELS

```python
# LLM analyzes conversation and returns:
{
    "mood": "frustrated",           # What emotion
    "intensity": 0.8,                # How strongly (0.0-1.0)
    "reason": "User made excuses",   # Why they feel this
    "trigger_keywords": ["excuse"]   # What triggered it
}
```

**Advantages**:
- ✅ Context-aware (considers personality, history, scenario)
- ✅ Nuanced (can detect subtle mood shifts)
- ✅ Adaptive (responds to unpredictable user input)
- ✅ Character-specific (Marcus escalates faster than Sarah)

**How it works**:
```python
mood_system = MoodInferenceSystem(groq_client)
updated_mood = await mood_system.infer_mood(
    character=marcus,
    user_message="I can't make that deadline",
    current_mood_state=current_mood,
    conversation_history=history,
    scenario_context=context
)
# Returns: FRUSTRATED (0.8) - "User making excuses"
```

---

### Component 2: Rule-Based Behaviors (`characters.py`)

**Purpose**: Determine how the feeling translates to ACTIONS

```python
MoodBehaviorRule(
    mood=CharacterMood.FRUSTRATED,
    trigger_keywords=["excuse", "can't"],
    behaviors=[
        "Use short, terse responses (5-15 words)",
        "Show visible impatience in your tone",
        "Cut them off with 'I don't want to hear it'"
    ],
    intensity_threshold=0.6
)
```

**Advantages**:
- ✅ Deterministic (same mood + keywords = same behaviors)
- ✅ Controllable (you define exact behaviors)
- ✅ Customizable per character (Marcus vs Patricia)
- ✅ Transparent (you know what LLM will do)

**How it works**:
```python
# After LLM determines mood, rules generate instructions:
instructions = character.generate_mood_based_instructions(
    mood_state=updated_mood,      # From LLM
    user_message=user_message,    # To match keywords
    scenario_context=context
)

# Returns explicit instructions appended to prompt:
"""
### CURRENT EMOTIONAL STATE: FRUSTRATED (Intensity: 0.8)
Why you feel this way: User making excuses

### BEHAVIORAL INSTRUCTIONS:
Rule 1 (triggered by: excuse, can't):
- Use short, terse responses (5-15 words)
- Show visible impatience in your tone
- Cut them off with 'I don't want to hear it'

⚠️ YOUR EMOTIONS ARE VERY STRONG
"""
```

---

## 🎯 Why This Hybrid Approach?

### ❌ Pure LLM Approach (What We Avoided)
```
Prompt: "You feel frustrated. Let that affect your response."
Problem: Too vague, inconsistent results
```

### ❌ Pure Rules Approach (What We Avoided)
```
IF user says "excuse" THEN feel angry
Problem: Not context-aware, misses nuance
```

### ✅ Hybrid Approach (What We Built)
```
1. LLM: "Marcus feels FRUSTRATED (0.8) because user made excuses again"
2. Rules: "IF FRUSTRATED + 'excuse' → Use terse responses, show impatience"
3. Result: Consistent behavior based on smart mood inference
```

---

## 📝 Complete Example

### Setup
```python
# In discord_bot.py
from mood_inference import MoodInferenceSystem

# Initialize in __init__
self.mood_inference = MoodInferenceSystem(self.groq_client)

# Initialize mood states in session
session["character_moods"] = {
    "marcus": MoodState(
        current_mood=CharacterMood.IMPATIENT,
        intensity=0.7,
        reason="Starting aggressive scenario"
    )
}
```

### Turn 1: User Makes Excuse

**User**: "I can't make that deadline"

**Step 1 - LLM Inference**:
```python
updated_mood = await self.mood_inference.infer_mood(
    character=marcus,
    user_message="I can't make that deadline",
    current_mood_state=session["character_moods"]["marcus"],
    conversation_history=session["conversation_history"],
    scenario_context=session["scenario"].context
)
# LLM returns: FRUSTRATED (0.7) - "User making excuses"
```

**Step 2 - Rule Matching**:
```python
# System finds matching rule:
# MoodBehaviorRule(
#     mood=FRUSTRATED,
#     trigger_keywords=["can't", "excuse"],  ✓ matches "can't"
#     intensity_threshold=0.6                 ✓ 0.7 >= 0.6
# )
```

**Step 3 - Instruction Generation**:
```python
instructions = marcus.generate_mood_based_instructions(
    mood_state=updated_mood,
    user_message="I can't make that deadline"
)
# Generates:
"""
### CURRENT EMOTIONAL STATE: FRUSTRATED (0.7)
### BEHAVIORAL INSTRUCTIONS:
- Use short, terse responses
- Show visible impatience
"""
```

**Step 4 - Dynamic Prompt**:
```python
system_prompt = marcus.generate_dynamic_prompt(
    mood_state=updated_mood,
    user_message="I can't make that deadline",
    scenario_context=context
)
# Appends instructions to base prompt
```

**Step 5 - Response**:
```
Marcus: "I don't want to hear that. Find a way."
```

---

### Turn 2: User Makes Another Excuse

**User**: "But it's impossible with current resources!"

**Step 1 - LLM Inference**:
```python
# LLM sees:
# - Previous mood: FRUSTRATED (0.7)
# - User still making excuses
# - Marcus's personality: aggressive, escalates quickly

# Returns: ANGRY (0.9) - "User continues making excuses after warning"
```

**Step 2 - Rule Matching**:
```python
# Matches ANGRY rule:
# trigger_keywords=["impossible", "but", "excuse"]  ✓
# intensity_threshold=0.7                           ✓ 0.9 >= 0.7
```

**Step 3 - Instructions**:
```
### BEHAVIORAL INSTRUCTIONS:
- Use CAPS to emphasize your anger
- Threaten consequences
- Question their competence
- Be openly hostile

⚠️ YOUR EMOTIONS ARE VERY STRONG
📊 Mood Transition: frustrated → angry
```

**Step 4 - Response**:
```
Marcus: "That's YOUR problem to solve! Either deliver or you're FIRED!"
```

---

### Turn 3: User Proposes Solution

**User**: "Here's my detailed breakdown with realistic timeline and dependencies"

**Step 1 - LLM Inference**:
```python
# LLM sees:
# - Previous mood: ANGRY (0.9)
# - User now presenting solution, not excuses
# - Caught Marcus off-guard

# Returns: SKEPTICAL (0.6) - "User proposed solution, need to verify"
```

**Step 2 - Rule Matching**:
```python
# Matches SKEPTICAL rule:
# trigger_keywords=["breakdown", "timeline", "plan"]  ✓
# But different rule for SKEPTICAL + concrete data:
# Behaviors: "Acknowledge they're being concrete, soften slightly"
```

**Step 3 - Response**:
```
Marcus: "Hmm. Walk me through the dependencies."
```

---

## 🎨 Customization Examples

### Default Rules (Work for Everyone)
```python
# In characters.py - CharacterPersona._generate_default_mood_rules()
# ~11 rules covering common emotional responses
```

### Marcus Custom Rules (Hyper-Aggressive)
```python
# In characters.py - CharacterManager._create_marcus_custom_rules()
MoodBehaviorRule(
    mood=CharacterMood.ANGRY,
    trigger_keywords=["excuse", "can't"],
    behaviors=[
        "RAISE YOUR VOICE - use multiple words in CAPS",
        "Threaten to FIRE them",
        "Question if they can do their job"
    ],
    intensity_threshold=0.7
)
```

### Patricia Custom Rules (Guilt-Tripping)
```python
MoodBehaviorRule(
    mood=CharacterMood.DISAPPOINTED,
    trigger_keywords=["boundaries", "space", "can't"],
    behaviors=[
        "Use guilt: 'After everything I've done for you...'",
        "Bring up sacrifices",
        "Get emotional - mention feeling alone"
    ]
)
```

---

## 🔧 Integration in discord_bot.py

### Modified Response Generation
```python
async def _generate_character_response_with_fallback(
    self,
    message: str,
    character: CharacterPersona,
    conversation_history: List[Dict],
    scenario_context: str,
    character_role_context: str,
    current_mood_state: MoodState  # NEW
) -> tuple[str, MoodState]:  # NEW return type
    
    # STEP 1: LLM infers mood
    updated_mood = await self.mood_inference.infer_mood(
        character=character,
        user_message=message,
        current_mood_state=current_mood_state,
        conversation_history=conversation_history,
        scenario_context=scenario_context
    )
    
    # STEP 2: Generate prompt with mood-based rules
    system_prompt = character.generate_dynamic_prompt(
        mood_state=updated_mood,
        user_message=message,  # For rule matching
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

---

## 📊 Performance Characteristics

### Latency per Character Response:
```
LLM Mood Inference:  0.5-1.5s  ████████████░░░░
Rule Matching:       0.01s     █
Prompt Generation:   0.01s     █
LLM Response:        1-2s      ████████████████
─────────────────────────────────────────────
Total per character: ~2-3s
```

### Optimization Strategies:
1. **Parallel inference** for multiple characters
2. **Cache moods** for rapid-fire messages (30s window)
3. **Skip inference** for very short messages
4. **Use "fast" model** for mood inference

---

## ✅ Benefits of This Architecture

1. **Smart Mood Detection** - LLM understands context
2. **Consistent Behaviors** - Rules ensure predictable actions
3. **Easy to Debug** - You can see exactly what rules fired
4. **Customizable** - Add character-specific rules easily
5. **Backward Compatible** - Old system still works
6. **Transparent** - Clear logs show mood inference → rule matching → response

---

## 🚀 Next Steps

**Phase 1**: ✅ COMPLETE - Core infrastructure added
**Phase 2**: Add custom rules for Marcus and Patricia
**Phase 3**: Integrate mood inference into discord_bot.py
**Phase 4**: Test and refine based on real conversations

---

## 🎯 Key Takeaway

> **The LLM is the brain (determines feelings), the rules are the nervous system (determines actions)**

This gives you the best of both worlds:
- Flexible, context-aware emotional intelligence
- Deterministic, controllable behavioral outputs

