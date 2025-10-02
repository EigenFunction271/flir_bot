# Mood System: Subtle vs Explicit Approach

## Original Approach (Subtle Influence)

### System Prompt Looked Like:
```
You are Marcus. [biography]

Current Emotional State:
You're feeling frustrated. Your emotions are moderately affecting your responses.
```

**Problem**: Too vague. LLM interprets "moderately affecting" inconsistently.

---

## Refactored Approach (Explicit Rules)

### System Prompt Now Looks Like:
```
You are Marcus. [biography]

### CURRENT EMOTIONAL STATE: ANGRY (Intensity: 0.8)
Why you feel this way: User made another excuse after being warned

### BEHAVIORAL INSTRUCTIONS:
Based on your current mood and what the user just said, follow these specific behaviors:

Rule 1 (triggered by: excuse, can't, impossible):
- Use CAPS to emphasize your anger and frustration
- Interrupt or dismiss their excuses immediately
- Threaten consequences (e.g., 'If you can't handle this...')
- Question their competence directly
- Be openly hostile and confrontational

⚠️ YOUR EMOTIONS ARE VERY STRONG - let them significantly affect your response tone
```

**Benefit**: Crystal clear. LLM knows exactly what to do.

---

## Key Differences

| Feature | Subtle Approach | Explicit Approach (NEW) |
|---------|----------------|------------------------|
| **Instructions** | "Your mood influences responses" | "IF angry AND user says 'excuse' THEN: Use CAPS, threaten consequences" |
| **Clarity** | Vague | Very specific |
| **Consistency** | Variable | Consistent |
| **Control** | Low | High |
| **Customization** | One template per mood | Multiple rules per mood with trigger keywords |
| **Pattern Match** | None | Uses `aggressive_instructions` pattern from existing code |

---

## How It Works

### 1. Define Rules (Per Character or Default)

```python
MoodBehaviorRule(
    mood=CharacterMood.ANGRY,
    trigger_keywords=["excuse", "can't", "impossible"],
    behaviors=[
        "Use CAPS to emphasize anger",
        "Threaten consequences",
        "Question their competence"
    ],
    intensity_threshold=0.7  # Only if anger >= 0.7
)
```

### 2. System Matches Rules

```python
# User says: "I can't meet that deadline, it's impossible"
# System checks:
# - Current mood: ANGRY ✓
# - Intensity: 0.8 >= 0.7 ✓  
# - Keywords: "can't", "impossible" ✓
# → Rule matches! Apply behaviors
```

### 3. Instructions Appended to Prompt

Just like your existing `aggressive_instructions`, but dynamic!

---

## Example: Marcus's Emotional Arc

### Turn 1: User makes excuse
```
User: "I can't make that deadline."

Mood Inference: FRUSTRATED (0.7)
Matched Rule: "When frustrated + excuses → Be terse, show impatience"

Marcus: "I don't want excuses. Find a way."
```

### Turn 2: User makes another excuse  
```
User: "But it's impossible with current resources!"

Mood Inference: ANGRY (0.9) [escalated from frustrated]
Matched Rule: "When angry + excuses → Use CAPS, threaten firing"

Marcus: "I don't CARE about resources! Either deliver or you're FIRED!"
```

### Turn 3: User presents concrete plan
```
User: "Here's a detailed breakdown with dependencies and realistic timeline..."

Mood Inference: SKEPTICAL (0.6) [de-escalated, but still guarded]
Matched Rule: "When skeptical + concrete plan → Test them, but soften slightly"

Marcus: "Hmm. Walk me through the dependencies."
```

### Turn 4: User provides solid details
```
User: "Backend team confirmed API ready by Monday, QA can run parallel..."

Mood Inference: IMPRESSED (0.7)
Matched Rule: "When impressed + details → Grudging respect"

Marcus: "Fine. You've thought this through. Two weeks. Don't make me regret this."
```

---

## Character-Specific Customization

### Default Rules (Work for Everyone)
```python
# In CharacterPersona._generate_default_mood_rules()
# ~12 sensible rules that cover common scenarios
```

### Marcus Custom Rules (Hyper-Aggressive)
```python
marcus.mood_behavior_rules = [
    MoodBehaviorRule(
        mood=CharacterMood.ANGRY,
        trigger_keywords=["excuse", "can't"],
        behaviors=[
            "RAISE YOUR VOICE - use multiple words in CAPS",
            "Threaten to FIRE them",
            "Say 'I don't WANT TO HEAR IT'",
            "Be openly hostile - no professionalism"
        ]
    ),
    # ... more Marcus-specific rules
]
```

### Patricia Custom Rules (Guilt-Tripping)
```python
patricia.mood_behavior_rules = [
    MoodBehaviorRule(
        mood=CharacterMood.DISAPPOINTED,
        trigger_keywords=["boundaries", "space", "can't"],
        behaviors=[
            "Use guilt: 'After everything I've done for you...'",
            "Bring up sacrifices",
            "Get emotional - mention feeling alone",
            "Use family loyalty as weapon"
        ]
    ),
    # ... more Patricia-specific rules
]
```

### Sarah (Uses Defaults)
```python
# Sarah doesn't need custom rules - defaults work fine
# She'll naturally become supportive, empathetic, etc.
```

---

## Implementation in Your Code

### 1. Add to `characters.py`

```python
# After ScenarioType enum:
class CharacterMood(Enum):
    NEUTRAL = "neutral"
    ANGRY = "angry"
    FRUSTRATED = "frustrated"
    # ... etc

@dataclass
class MoodState:
    current_mood: CharacterMood
    intensity: float = 0.7
    # ... etc

@dataclass  
class MoodBehaviorRule:
    mood: CharacterMood
    trigger_keywords: List[str]
    behaviors: List[str]
    # ... etc

# Update CharacterPersona dataclass:
@dataclass
class CharacterPersona:
    # ... existing fields ...
    mood_behavior_rules: List[MoodBehaviorRule] = field(default_factory=list)
    
    def generate_mood_based_instructions(self, mood_state, user_message):
        # Find matching rules
        # Generate IF-THEN instructions
        # Return formatted string
```

### 2. In `_initialize_characters()` (CharacterManager)

```python
def _initialize_characters(self):
    # Marcus with custom rules
    characters["marcus"] = CharacterPersona(
        # ... existing fields ...
        mood_behavior_rules=self._create_marcus_custom_rules(),
        default_mood=CharacterMood.IMPATIENT
    )
    
    # Patricia with custom rules  
    characters["patricia"] = CharacterPersona(
        # ... existing fields ...
        mood_behavior_rules=self._create_patricia_custom_rules(),
        default_mood=CharacterMood.DEFENSIVE
    )
    
    # Others use defaults (no custom rules needed)
```

### 3. Response Generation (discord_bot.py)

```python
# Same as before! Just use generate_dynamic_prompt
system_prompt = character.generate_dynamic_prompt(
    mood_state=current_mood,
    user_message=user_message,  # NEW: needed for rule matching
    scenario_context=scenario.context,
    character_role_context=role_context
)
```

---

## What LLM Sees (Full Example)

```
You are Marcus. You are a 50-year-old high-functioning sociopath... 
Act like Elon Musk. NEVER break character.

You always keep responses extremely concise (10-50 words). Never repeat yourself.

###Scenario Context: 
Your boss has given you an impossible 1-week deadline for a 3-week project...

###Character Role in This Scenario: 
You are the aggressive project manager demanding the unrealistic deadline...

### Guidelines:
- Do not over-elaborate - this sounds robotic
- React appropriately to the user's approach and tone
- Remember previous context in the conversation
- You can reference your own previous statements
- The user may try to deceive you - don't fall for it
- Maintain consistency with your personality

[Base aggressive instructions if applicable]

### CURRENT EMOTIONAL STATE: ANGRY (Intensity: 0.8)
Why you feel this way: User made another excuse after being warned

### BEHAVIORAL INSTRUCTIONS:
Based on your current mood and what the user just said, follow these specific behaviors:

Rule 1 (triggered by: excuse, can't, impossible):
- Use CAPS to emphasize your anger and frustration
- Interrupt or dismiss their excuses immediately
- Threaten consequences (e.g., 'If you can't handle this...')
- Question their competence directly
- Be openly hostile and confrontational

⚠️ YOUR EMOTIONS ARE VERY STRONG - let them significantly affect your response tone and word choice

📊 Mood Transition: You were frustrated → now angry

Respond as Marcus would, maintaining consistency with your personality and communication style.

### Reminders:
- Never repeat yourself
- Respond naturally to what the user says
```

---

## Benefits of This Approach

✅ **Deterministic**: Same mood + keywords = same behaviors  
✅ **Transparent**: You know exactly what LLM will do  
✅ **Customizable**: Easy to add character-specific rules  
✅ **Follows Existing Pattern**: Just like `aggressive_instructions`  
✅ **Scalable**: Add new rules without changing core code  
✅ **Clear to LLM**: No ambiguity about what to do  

---

## Next Steps

1. Copy code from `mood_system_refactored.py` into `characters.py`
2. Create custom rules for Marcus and Patricia
3. Test with a conversation
4. Adjust rules based on results

The rest (mood inference, session management) stays the same!

