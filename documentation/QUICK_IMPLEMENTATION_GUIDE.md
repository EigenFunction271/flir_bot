# Quick Implementation Guide: Rule-Based Mood System

## 🎯 Goal
Add dynamic emotional responses using explicit IF-THEN rules that append to the system prompt.

## ⏱️ Time Estimate
- **Phase 1** (Core setup): 30 minutes
- **Phase 2** (Custom rules): 20 minutes  
- **Phase 3** (Integration): 30 minutes
- **Total**: ~1.5 hours

---

## 📝 Phase 1: Add Core Infrastructure to `characters.py`

### Step 1.1: Add Enums and Classes (After line 8)

```python
from dataclasses import dataclass, field

# After ScenarioType enum (line 8), add:

class CharacterMood(Enum):
    """Represents the emotional state of a character"""
    NEUTRAL = "neutral"
    PLEASED = "pleased"
    IMPRESSED = "impressed"
    SKEPTICAL = "skeptical"
    IMPATIENT = "impatient"
    ANNOYED = "annoyed"
    FRUSTRATED = "frustrated"
    DISAPPOINTED = "disappointed"
    DISMISSIVE = "dismissive"
    DEFENSIVE = "defensive"
    ANGRY = "angry"
    HOSTILE = "hostile"
    MANIPULATIVE = "manipulative"

@dataclass
class MoodState:
    """Tracks a character's current emotional state"""
    current_mood: CharacterMood
    intensity: float = 0.7
    reason: str = ""
    trigger_keywords: List[str] = field(default_factory=list)
    previous_mood: Optional[CharacterMood] = None
    mood_history: List[CharacterMood] = field(default_factory=list)
    
    def update_mood(self, new_mood: CharacterMood, intensity: float, reason: str, triggers: List[str] = None):
        self.mood_history.append(self.current_mood)
        self.previous_mood = self.current_mood
        self.current_mood = new_mood
        self.intensity = intensity
        self.reason = reason
        self.trigger_keywords = triggers or []
    
    def to_dict(self) -> dict:
        return {
            "current_mood": self.current_mood.value,
            "intensity": self.intensity,
            "reason": self.reason,
            "trigger_keywords": self.trigger_keywords,
            "previous_mood": self.previous_mood.value if self.previous_mood else None,
            "mood_history": [mood.value for mood in self.mood_history[-5:]]
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'MoodState':
        return cls(
            current_mood=CharacterMood(data["current_mood"]),
            intensity=data.get("intensity", 0.7),
            reason=data.get("reason", ""),
            trigger_keywords=data.get("trigger_keywords", []),
            previous_mood=CharacterMood(data["previous_mood"]) if data.get("previous_mood") else None,
            mood_history=[CharacterMood(m) for m in data.get("mood_history", [])]
        )

@dataclass
class MoodBehaviorRule:
    """A conditional rule: IF mood + triggers THEN behaviors"""
    mood: CharacterMood
    trigger_keywords: List[str]
    behaviors: List[str]
    intensity_threshold: float = 0.5
    
    def matches(self, mood_state: MoodState, user_message: str) -> bool:
        if mood_state.current_mood != self.mood:
            return False
        if mood_state.intensity < self.intensity_threshold:
            return False
        user_message_lower = user_message.lower()
        return any(keyword in user_message_lower for keyword in self.trigger_keywords)
    
    def generate_instructions(self) -> str:
        return "\n".join(f"- {behavior}" for behavior in self.behaviors)
```

### Step 1.2: Update `CharacterPersona` dataclass (line 11)

```python
@dataclass
class CharacterPersona:
    """Represents a character persona with all necessary attributes"""
    id: str
    name: str
    biography: str
    personality_traits: List[str]
    communication_style: str
    scenario_affinity: List[ScenarioType]
    reference: Optional[str] = None
    voice_id: Optional[str] = None
    
    # NEW: Rule-based mood system
    mood_behavior_rules: List[MoodBehaviorRule] = field(default_factory=list)
    default_mood: CharacterMood = CharacterMood.NEUTRAL
    
    # Keep existing __setstate__ and __post_init__ methods...
    # But ADD this to __post_init__:
    def __post_init__(self):
        # ... existing biography code ...
        
        # NEW: Initialize mood rules if not provided
        if not self.mood_behavior_rules:
            self.mood_behavior_rules = self._generate_default_mood_rules()
```

### Step 1.3: Add Methods to `CharacterPersona`

Add these methods after `generate_system_prompt` (around line 103):

```python
def _generate_default_mood_rules(self) -> List[MoodBehaviorRule]:
    """Generate default mood-based behavior rules"""
    return [
        # Copy the rules from mood_system_refactored.py
        # Lines 105-244 in the refactored file
        # I'll show key examples here:
        
        MoodBehaviorRule(
            mood=CharacterMood.ANGRY,
            trigger_keywords=["excuse", "can't", "impossible", "but", "difficult"],
            behaviors=[
                "Use CAPS to emphasize your anger",
                "Dismiss their excuses immediately",
                "Threaten consequences",
                "Question their competence",
                "Be openly hostile"
            ],
            intensity_threshold=0.7
        ),
        
        MoodBehaviorRule(
            mood=CharacterMood.FRUSTRATED,
            trigger_keywords=["excuse", "reason", "because"],
            behaviors=[
                "Use short, terse responses (5-15 words)",
                "Show visible impatience",
                "Cut them off"
            ],
            intensity_threshold=0.6
        ),
        
        # Add ~10-15 more rules here (copy from refactored file)
    ]

def get_initial_mood_for_scenario(self, scenario_context: str, character_role_context: str) -> CharacterMood:
    """Determine starting mood for scenario"""
    aggressive_traits = ["aggressive", "intimidating", "demanding", "confrontational"]
    is_aggressive = any(trait.lower() in [t.lower() for t in self.personality_traits] for trait in aggressive_traits)
    
    aggressive_keywords = ["harassment", "deadline", "unrealistic", "confronting"]
    is_conflict = any(keyword in scenario_context.lower() for keyword in aggressive_keywords)
    
    if is_aggressive and is_conflict:
        return CharacterMood.IMPATIENT
    elif is_aggressive:
        return CharacterMood.SKEPTICAL
    else:
        return CharacterMood.NEUTRAL

def generate_mood_based_instructions(self, mood_state: MoodState, user_message: str, scenario_context: str = None) -> str:
    """Generate explicit conditional instructions based on mood"""
    matching_rules = [rule for rule in self.mood_behavior_rules if rule.matches(mood_state, user_message)]
    
    if not matching_rules:
        return ""
    
    instructions = []
    instructions.append(f"\n### CURRENT EMOTIONAL STATE: {mood_state.current_mood.value.upper()} (Intensity: {mood_state.intensity:.1f})")
    
    if mood_state.reason:
        instructions.append(f"Why you feel this way: {mood_state.reason}")
    
    instructions.append("\n### BEHAVIORAL INSTRUCTIONS:")
    instructions.append("Based on your current mood and what the user just said:")
    
    for i, rule in enumerate(matching_rules, 1):
        instructions.append(f"\nRule {i} (triggered by: {', '.join(rule.trigger_keywords)}):")
        instructions.append(rule.generate_instructions())
    
    if mood_state.intensity >= 0.8:
        instructions.append("\n⚠️ YOUR EMOTIONS ARE VERY STRONG - let them significantly affect your response")
    
    if mood_state.previous_mood and mood_state.previous_mood != mood_state.current_mood:
        instructions.append(f"\n📊 Mood Transition: {mood_state.previous_mood.value} → {mood_state.current_mood.value}")
    
    return "\n".join(instructions)

def generate_dynamic_prompt(self, mood_state: MoodState, user_message: str, scenario_context: str = None, character_role_context: str = None) -> str:
    """Generate system prompt with mood-based instructions appended"""
    # Copy your existing generate_system_prompt code
    # Then at the end, before the return, add:
    
    mood_instructions = self.generate_mood_based_instructions(mood_state, user_message, scenario_context)
    
    # Add mood_instructions to the prompt (after aggressive_instructions line 95)
    # Change line 95 from:
    # {aggressive_instructions}{supportive_instructions}
    # To:
    # {aggressive_instructions}{supportive_instructions}{mood_instructions}
```

---

## 📝 Phase 2: Add Custom Rules for Key Characters

### Step 2.1: Create Helper Methods in `CharacterManager`

Add these methods to `CharacterManager` class (after line 108):

```python
def _create_marcus_custom_rules(self) -> List[MoodBehaviorRule]:
    """Marcus gets hyper-aggressive rules"""
    return [
        MoodBehaviorRule(
            mood=CharacterMood.ANGRY,
            trigger_keywords=["excuse", "can't", "impossible", "but"],
            behaviors=[
                "RAISE YOUR VOICE - use multiple words in CAPS",
                "Threaten to FIRE them or give a BAD PERFORMANCE REVIEW",
                "Say 'I don't WANT TO HEAR IT' or 'THAT'S YOUR PROBLEM'",
                "Question if they can do their job",
                "Be openly hostile - no professionalism filter"
            ],
            intensity_threshold=0.7
        ),
        MoodBehaviorRule(
            mood=CharacterMood.FRUSTRATED,
            trigger_keywords=["plan", "proposal", "data", "breakdown"],
            behaviors=[
                "Show you're caught off-guard: 'Hm.' or 'Fine.'",
                "Still tough but less aggressive",
                "Ask ONE hard question to test",
                "If answer is solid, grunt approval"
            ],
            intensity_threshold=0.6
        ),
        MoodBehaviorRule(
            mood=CharacterMood.IMPRESSED,
            trigger_keywords=["done", "completed", "solution", "results"],
            behaviors=[
                "Acknowledge in Marcus style: 'Not bad' or 'Fine'",
                "Don't be warm - still Marcus",
                "Show respect for results over excuses",
                "Soften slightly but maintain authority"
            ],
            intensity_threshold=0.6
        ),
    ]

def _create_patricia_custom_rules(self) -> List[MoodBehaviorRule]:
    """Patricia gets guilt-tripping rules"""
    return [
        MoodBehaviorRule(
            mood=CharacterMood.DISAPPOINTED,
            trigger_keywords=["can't", "space", "boundaries", "my life"],
            behaviors=[
                "Use guilt: 'After everything I've done for you...'",
                "Bring up sacrifices",
                "Make them feel like they're abandoning you",
                "Get emotional - mention feeling alone",
                "Use family loyalty as weapon"
            ],
            intensity_threshold=0.6
        ),
        MoodBehaviorRule(
            mood=CharacterMood.DEFENSIVE,
            trigger_keywords=["controlling", "manipulating", "excessive", "intrusive"],
            behaviors=[
                "Play victim immediately",
                "Say 'I'm just trying to help' or 'You're ungrateful'",
                "Cry or get emotional",
                "Turn it around: 'Why are you attacking me?'",
                "Make yourself the victim"
            ],
            intensity_threshold=0.5
        ),
    ]
```

### Step 2.2: Update Marcus and Patricia initialization (around line 116)

```python
def _initialize_characters(self):
    characters = {}
    
    # Marcus with custom rules
    characters["marcus"] = CharacterPersona(
        id="marcus",
        name="Marcus",
        biography="...",
        personality_traits=["Results-driven", "Impatient", "Demanding", "Intimidating"],
        communication_style="Direct, confrontational, deadline-focused",
        scenario_affinity=[ScenarioType.WORKPLACE],
        reference="Elon Musk",
        voice_id="elevenlabs_voice_001",
        mood_behavior_rules=self._create_marcus_custom_rules(),  # NEW!
        default_mood=CharacterMood.IMPATIENT  # NEW!
    )
    
    # Patricia with custom rules
    characters["patricia"] = CharacterPersona(
        id="patricia",
        name="Patricia",
        biography="...",
        personality_traits=["Worried", "Controlling", "Manipulative"],
        communication_style="Guilt-inducing, emotional manipulation",
        scenario_affinity=[ScenarioType.FAMILY],
        reference="Tiger Mom archetype",
        voice_id="elevenlabs_voice_005",
        mood_behavior_rules=self._create_patricia_custom_rules(),  # NEW!
        default_mood=CharacterMood.DEFENSIVE  # NEW!
    )
    
    # Other characters keep default rules (no changes needed)
    characters["sarah"] = CharacterPersona(
        # ... existing code, no mood_behavior_rules needed
    )
```

---

## 📝 Phase 3: Integration (Keep Mood Inference from Original Scaffold)

### Step 3.1: Create `mood_inference.py`

Copy `MoodInferenceSystem` from `mood_system_scaffold.py` (lines 203-318)

No changes needed! The inference system works the same way.

### Step 3.2: Update `discord_bot.py` Response Generation

Find `_generate_character_response_with_fallback` (around line 1527) and update:

```python
async def _generate_character_response_with_fallback(
    self, 
    message: str, 
    character: CharacterPersona, 
    conversation_history: List[Dict], 
    scenario_context: str = None,
    character_role_context: str = None,
    current_mood_state: MoodState = None  # NEW parameter
) -> tuple[str, MoodState]:  # NEW return type
    """Generate response with mood inference"""
    try:
        # STEP 1: Infer mood (if mood system enabled)
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
        
        # STEP 2: Generate dynamic prompt with mood instructions
        system_prompt = character.generate_dynamic_prompt(
            mood_state=updated_mood,
            user_message=message,  # NEW: needed for rule matching
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
        
    except Exception as e:
        logger.error(f"Error in mood-aware response: {e}")
        # Fallback
        system_prompt = character.generate_system_prompt(scenario_context, character_role_context)
        response = await self.groq_client.generate_response_with_history(...)
        return response, current_mood_state or MoodState(current_mood=character.default_mood)
```

### Step 3.3: Update Session Structure

Same as original scaffold - add `character_moods` to session dict.

### Step 3.4: Update `_generate_multi_character_responses`

Same as original scaffold - pass mood state to response generation.

---

## ✅ Testing

### Test 1: Marcus Escalation
```
Scenario: workplace_deadline
User: "I can't make that deadline."
Expected: Marcus FRUSTRATED → terse response

User: "It's impossible with current resources!"  
Expected: Marcus ANGRY → CAPS, threats, hostile

User: "Here's my detailed plan with timeline..."
Expected: Marcus SKEPTICAL → test them but soften

User: "Backend API ready Monday, QA parallel..."
Expected: Marcus IMPRESSED → grudging respect
```

### Test 2: Patricia Guilt Trip
```
Scenario: family_boundaries
User: "Mom, I need some boundaries."
Expected: Patricia DISAPPOINTED → guilt about sacrifices

User: "You're being too controlling."
Expected: Patricia DEFENSIVE → play victim, cry

User: "Okay fine, I'll visit this weekend."
Expected: Patricia PLEASED → warm, 'that wasn't hard'
```

---

## 🎯 What You Get

**Before:**
```
User: "I can't make that deadline."
Marcus: "That's not acceptable. Find a way."
```

**After:**
```
User: "I can't make that deadline."
Marcus (FRUSTRATED, intensity=0.7): "I don't want excuses. Figure it out."

[After another excuse]
Marcus (ANGRY, intensity=0.9): "That's YOUR problem! Either deliver or you're FIRED!"

[After solid plan]
Marcus (IMPRESSED, intensity=0.7): "Hm. Not bad. You've earned two weeks."
```

---

## 📊 Summary

1. ✅ Add 3 classes to `characters.py`: `CharacterMood`, `MoodState`, `MoodBehaviorRule`
2. ✅ Add 3 methods to `CharacterPersona`: `_generate_default_mood_rules`, `generate_mood_based_instructions`, `generate_dynamic_prompt`
3. ✅ Create custom rules for Marcus and Patricia
4. ✅ Update `_generate_character_response_with_fallback` to use moods
5. ✅ Test with a conversation

**Total Lines Added**: ~300-400 lines
**Breaking Changes**: None (backward compatible)
**Result**: Dynamic, emotionally responsive characters! 🎭

