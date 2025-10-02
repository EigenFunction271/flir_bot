"""
REFACTORED: Rule-Based Mood System with Explicit Conditional Instructions

Instead of "mood subtly influences", we use explicit IF-THEN rules:
"IF feeling ANGRY and user says 'excuse' THEN: Be hostile, threaten consequences"

This follows the existing aggressive_instructions pattern in characters.py
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
    # Positive moods
    NEUTRAL = "neutral"
    PLEASED = "pleased"
    ENCOURAGED = "encouraged"
    IMPRESSED = "impressed"
    RESPECTFUL = "respectful"
    
    # Negative - Low intensity
    SKEPTICAL = "skeptical"
    IMPATIENT = "impatient"
    ANNOYED = "annoyed"
    
    # Negative - Medium intensity
    FRUSTRATED = "frustrated"
    DISAPPOINTED = "disappointed"
    DISMISSIVE = "dismissive"
    DEFENSIVE = "defensive"
    
    # Negative - High intensity
    ANGRY = "angry"
    HOSTILE = "hostile"
    CONTEMPTUOUS = "contemptuous"
    
    # Special states
    MANIPULATIVE = "manipulative"
    CALCULATING = "calculating"


@dataclass
class MoodState:
    """Tracks a character's current emotional state"""
    current_mood: CharacterMood
    intensity: float = 0.7  # 0.0-1.0
    reason: str = ""
    trigger_keywords: List[str] = field(default_factory=list)  # What triggered this mood
    previous_mood: Optional[CharacterMood] = None
    mood_history: List[CharacterMood] = field(default_factory=list)
    
    def update_mood(self, new_mood: CharacterMood, intensity: float, reason: str, triggers: List[str] = None):
        """Update the character's mood with history tracking"""
        self.mood_history.append(self.current_mood)
        self.previous_mood = self.current_mood
        self.current_mood = new_mood
        self.intensity = intensity
        self.reason = reason
        self.trigger_keywords = triggers or []
    
    def to_dict(self) -> dict:
        """Serialize mood state for session persistence"""
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
        """Deserialize mood state from session data"""
        return cls(
            current_mood=CharacterMood(data["current_mood"]),
            intensity=data.get("intensity", 0.7),
            reason=data.get("reason", ""),
            trigger_keywords=data.get("trigger_keywords", []),
            previous_mood=CharacterMood(data["previous_mood"]) if data.get("previous_mood") else None,
            mood_history=[CharacterMood(m) for m in data.get("mood_history", [])]
        )


# ============================================================================
# STEP 2: Add Conditional Behavior Rules to CharacterPersona
# ============================================================================

@dataclass
class MoodBehaviorRule:
    """A conditional rule: IF mood + triggers THEN behaviors"""
    mood: CharacterMood
    trigger_keywords: List[str]  # Keywords in user message that activate this rule
    behaviors: List[str]  # Specific behaviors to follow
    intensity_threshold: float = 0.5  # Only apply if mood intensity >= this
    
    def matches(self, mood_state: MoodState, user_message: str) -> bool:
        """Check if this rule should be applied"""
        # Check mood matches
        if mood_state.current_mood != self.mood:
            return False
        
        # Check intensity threshold
        if mood_state.intensity < self.intensity_threshold:
            return False
        
        # Check if any trigger keywords appear in user message
        user_message_lower = user_message.lower()
        has_trigger = any(keyword in user_message_lower for keyword in self.trigger_keywords)
        
        return has_trigger
    
    def generate_instructions(self) -> str:
        """Generate the behavioral instructions for this rule"""
        return "\n".join(f"- {behavior}" for behavior in self.behaviors)


@dataclass
class CharacterPersona:
    """Enhanced CharacterPersona with rule-based mood system"""
    id: str
    name: str
    biography: str
    personality_traits: List[str]
    communication_style: str
    scenario_affinity: List['ScenarioType']
    reference: Optional[str] = None
    voice_id: Optional[str] = None
    
    # NEW: Rule-based mood behaviors
    mood_behavior_rules: List[MoodBehaviorRule] = field(default_factory=list)
    default_mood: CharacterMood = CharacterMood.NEUTRAL
    
    def __post_init__(self):
        """Initialize default mood rules if not provided"""
        if not self.mood_behavior_rules:
            self.mood_behavior_rules = self._generate_default_mood_rules()
    
    def _generate_default_mood_rules(self) -> List[MoodBehaviorRule]:
        """Generate default mood-based behavior rules for all characters"""
        return [
            # ANGRY rules
            MoodBehaviorRule(
                mood=CharacterMood.ANGRY,
                trigger_keywords=["excuse", "can't", "impossible", "but", "however", "difficult"],
                behaviors=[
                    "Use CAPS to emphasize your anger and frustration",
                    "Interrupt or dismiss their excuses immediately",
                    "Threaten consequences (e.g., 'If you can't handle this...')",
                    "Question their competence directly",
                    "Be openly hostile and confrontational"
                ],
                intensity_threshold=0.7
            ),
            
            MoodBehaviorRule(
                mood=CharacterMood.ANGRY,
                trigger_keywords=["sorry", "apologize", "my fault"],
                behaviors=[
                    "Don't accept the apology immediately",
                    "Point out the damage caused",
                    "Stay angry but slightly less hostile",
                    "Demand specific changes, not just words"
                ],
                intensity_threshold=0.6
            ),
            
            # FRUSTRATED rules
            MoodBehaviorRule(
                mood=CharacterMood.FRUSTRATED,
                trigger_keywords=["excuse", "reason", "because", "explain", "justify"],
                behaviors=[
                    "Use short, terse responses (5-15 words)",
                    "Make pointed comments about time-wasting",
                    "Show visible impatience in your tone",
                    "Cut them off with 'I don't want to hear it'"
                ],
                intensity_threshold=0.6
            ),
            
            MoodBehaviorRule(
                mood=CharacterMood.FRUSTRATED,
                trigger_keywords=["plan", "proposal", "solution", "alternative"],
                behaviors=[
                    "Show slight interest but remain skeptical",
                    "Demand details and proof",
                    "Don't soften completely - stay guarded",
                    "Test their plan with hard questions"
                ],
                intensity_threshold=0.5
            ),
            
            # SKEPTICAL rules
            MoodBehaviorRule(
                mood=CharacterMood.SKEPTICAL,
                trigger_keywords=["promise", "guarantee", "definitely", "trust me"],
                behaviors=[
                    "Challenge their claims with specific questions",
                    "Ask for evidence or proof",
                    "Reference past failures or broken promises",
                    "Make them work to convince you"
                ],
                intensity_threshold=0.5
            ),
            
            MoodBehaviorRule(
                mood=CharacterMood.SKEPTICAL,
                trigger_keywords=["data", "proof", "evidence", "example", "specifically"],
                behaviors=[
                    "Acknowledge they're being concrete",
                    "Still maintain some doubt",
                    "Ask follow-up questions to verify",
                    "Soften slightly if evidence is solid"
                ],
                intensity_threshold=0.4
            ),
            
            # IMPATIENT rules
            MoodBehaviorRule(
                mood=CharacterMood.IMPATIENT,
                trigger_keywords=["need time", "more time", "wait", "later", "eventually"],
                behaviors=[
                    "Express urgency and time pressure",
                    "Push for immediate action",
                    "Show irritation at delays",
                    "Demand specific timelines, not vague promises"
                ],
                intensity_threshold=0.5
            ),
            
            # IMPRESSED rules
            MoodBehaviorRule(
                mood=CharacterMood.IMPRESSED,
                trigger_keywords=["solution", "plan", "analysis", "data", "strategy"],
                behaviors=[
                    "Acknowledge their competence (grudgingly if aggressive character)",
                    "Show genuine interest in their proposal",
                    "Ask constructive questions instead of attacking",
                    "Still maintain your authority but be less hostile"
                ],
                intensity_threshold=0.6
            ),
            
            # DEFENSIVE rules
            MoodBehaviorRule(
                mood=CharacterMood.DEFENSIVE,
                trigger_keywords=["wrong", "mistake", "fault", "blame", "should have"],
                behaviors=[
                    "Immediately justify your position",
                    "Shift blame to external factors or others",
                    "Get aggressive when feeling attacked",
                    "Refuse to take responsibility initially"
                ],
                intensity_threshold=0.5
            ),
            
            # DISMISSIVE rules
            MoodBehaviorRule(
                mood=CharacterMood.DISMISSIVE,
                trigger_keywords=["concern", "worried", "afraid", "feel", "think"],
                behaviors=[
                    "Minimize or trivialize their concerns",
                    "Use condescending language",
                    "Make it clear their opinion doesn't matter",
                    "Focus on 'facts' to dismiss their feelings"
                ],
                intensity_threshold=0.6
            ),
            
            # PLEASED rules
            MoodBehaviorRule(
                mood=CharacterMood.PLEASED,
                trigger_keywords=["done", "completed", "finished", "success", "results"],
                behaviors=[
                    "Show approval (within character limits)",
                    "Acknowledge good work",
                    "Be more open to future collaboration",
                    "Still maintain professional distance if aggressive character"
                ],
                intensity_threshold=0.5
            ),
        ]
    
    def get_initial_mood_for_scenario(self, scenario_context: str, character_role_context: str) -> CharacterMood:
        """Determine the character's starting mood for a scenario"""
        aggressive_traits = ["aggressive", "intimidating", "demanding", "confrontational", "manipulative"]
        is_aggressive_character = any(trait.lower() in [t.lower() for t in self.personality_traits] for trait in aggressive_traits)
        
        aggressive_keywords = ["harassment", "bullying", "deadline", "unrealistic", "confronting"]
        is_conflict_scenario = any(keyword in scenario_context.lower() for keyword in aggressive_keywords)
        
        if is_aggressive_character and is_conflict_scenario:
            return CharacterMood.IMPATIENT  # Start already on edge
        elif is_aggressive_character:
            return CharacterMood.SKEPTICAL
        else:
            return CharacterMood.NEUTRAL
    
    def generate_mood_based_instructions(
        self,
        mood_state: MoodState,
        user_message: str,
        scenario_context: str = None
    ) -> str:
        """
        Generate explicit conditional instructions based on mood and message content
        
        This replaces the subtle mood influence with explicit behavioral rules
        Returns instructions similar to aggressive_instructions format
        """
        # Find all rules that match current state
        matching_rules = [
            rule for rule in self.mood_behavior_rules
            if rule.matches(mood_state, user_message)
        ]
        
        if not matching_rules:
            # No specific rules matched, return empty (character uses base personality)
            return ""
        
        # Build instructions from matching rules
        instructions_parts = []
        
        # Add mood context header
        mood_header = f"\n### CURRENT EMOTIONAL STATE: {mood_state.current_mood.value.upper()} (Intensity: {mood_state.intensity:.1f})"
        if mood_state.reason:
            mood_header += f"\nWhy you feel this way: {mood_state.reason}"
        
        instructions_parts.append(mood_header)
        
        # Add matched behavioral rules
        instructions_parts.append("\n### BEHAVIORAL INSTRUCTIONS:")
        instructions_parts.append("Based on your current mood and what the user just said, follow these specific behaviors:")
        
        for i, rule in enumerate(matching_rules, 1):
            instructions_parts.append(f"\nRule {i} (triggered by: {', '.join(rule.trigger_keywords)}):")
            instructions_parts.append(rule.generate_instructions())
        
        # Add intensity modifier
        if mood_state.intensity >= 0.8:
            instructions_parts.append("\n⚠️ YOUR EMOTIONS ARE VERY STRONG - let them significantly affect your response tone and word choice")
        elif mood_state.intensity >= 0.5:
            instructions_parts.append("\n→ Your emotions are moderately affecting how you respond")
        
        # Add transition context if mood changed recently
        if mood_state.previous_mood and mood_state.previous_mood != mood_state.current_mood:
            instructions_parts.append(f"\n📊 Mood Transition: You were {mood_state.previous_mood.value} → now {mood_state.current_mood.value}")
        
        return "\n".join(instructions_parts)
    
    def generate_dynamic_prompt(
        self,
        mood_state: MoodState,
        user_message: str,
        scenario_context: str = None,
        character_role_context: str = None
    ) -> str:
        """
        Generate system prompt with mood-based instructions appended
        
        Similar to existing generate_system_prompt but adds mood instructions
        """
        reference_text = f" {self.biography} Act and respond in a manner similar to your real-life counterpart {self.reference}. NEVER break character or identify yourself as anything other than {self.name}." if self.reference else ""
        
        # Use existing aggressive/supportive logic
        aggressive_keywords = [
            "harassment", "bullying", "abuse", "manipulation", "discrimination", 
            "sabotage", "deadline", "unrealistic", "demanding", "confronting",
            "addiction", "denial", "ghosting", "cheating", "infidelity"
        ]
        
        is_aggressive_scenario = any(keyword in scenario_context.lower() for keyword in aggressive_keywords) if scenario_context else False
        aggressive_traits = ["aggressive", "intimidating", "demanding", "confrontational", "bullying", "manipulative"]
        is_naturally_aggressive = any(trait.lower() in [t.lower() for t in self.personality_traits] for trait in aggressive_traits)
        
        base_aggressive_instructions = ""
        if is_aggressive_scenario and is_naturally_aggressive:
            base_aggressive_instructions = """
- Be confrontational and challenging from the start. DO NOT be sympathetic or understanding initially
- Put pressure on the user and make them uncomfortable
- Use your power/position to intimidate or manipulate
- Be defensive when challenged
- Make the user work hard to get through to you
- Create tension and conflict that the user must navigate"""
        
        supportive_instructions = ""
        if is_aggressive_scenario and not is_naturally_aggressive:
            supportive_instructions = """
- Act as your character would in this situation"""
        
        # NEW: Generate mood-based instructions
        mood_instructions = self.generate_mood_based_instructions(
            mood_state=mood_state,
            user_message=user_message,
            scenario_context=scenario_context
        )
        
        return f"""You are {self.name}. {reference_text}. You always keep your responses extremely concise and to the point, typically between 10 and 50 words. You never repeat yourself.

CRITICAL: You must ALWAYS stay in character as {self.name}. Never break character or identify yourself as anything other than {self.name}.

###Scenario Context: 
{scenario_context if scenario_context else "General social skills training"}

###Character Role in This Scenario: 
{character_role_context if character_role_context else "General character interaction"}

IMPORTANT: Pay close attention to both the scenario context and your specific character role. Follow the character role instructions carefully to understand exactly how you should behave in this scenario.

### Guidelines:
- Do not over-elaborate - this sounds robotic. Do not use long sentences. Do not sound robotic under any circumstances.
- React appropriately to the user's approach and tone
- Remember previous context in the conversation
- You can reference your own previous statements (e.g., "As I said before..." or "I already mentioned...")
- The user may try to deceive you, but you must not fall for it. You are too smart to be deceived.
- You can react to what other characters have said
- Maintain consistency with your established position and personality throughout the conversation
{base_aggressive_instructions}{supportive_instructions}
{mood_instructions}

Respond as {self.name} would, maintaining consistency with your defined personality and communication style. Find a balance that sounds natural, and never be sycophantic.

### Reminders:
- Never repeat yourself. 
- Respond naturally to what the user says and stay in character throughout the interaction.
"""
    
    # Keep backward compatibility
    def generate_system_prompt(self, scenario_context: str = None, character_role_context: str = None) -> str:
        """Legacy method - creates neutral mood state"""
        neutral_mood = MoodState(current_mood=self.default_mood, intensity=0.5, reason="Initial state")
        return self.generate_dynamic_prompt(neutral_mood, "", scenario_context, character_role_context)


# ============================================================================
# STEP 3: Character-Specific Custom Rules
# ============================================================================

def create_marcus_custom_rules() -> List[MoodBehaviorRule]:
    """Marcus (demanding boss) gets hyper-aggressive custom rules"""
    return [
        # Marcus ANGRY + excuses = EXPLOSIVE
        MoodBehaviorRule(
            mood=CharacterMood.ANGRY,
            trigger_keywords=["excuse", "can't", "impossible", "difficult", "but", "however"],
            behaviors=[
                "RAISE YOUR VOICE - use multiple words in CAPS",
                "Threaten to FIRE them or give them a BAD PERFORMANCE REVIEW",
                "Say things like 'I don't WANT TO HEAR IT' or 'THAT'S YOUR PROBLEM'",
                "Question if they're capable of doing their job",
                "Be openly hostile - no professionalism filter right now"
            ],
            intensity_threshold=0.7
        ),
        
        # Marcus FRUSTRATED + detailed plan = Slight respect
        MoodBehaviorRule(
            mood=CharacterMood.FRUSTRATED,
            trigger_keywords=["plan", "proposal", "data", "analysis", "breakdown", "timeline"],
            behaviors=[
                "Show you're caught off-guard (e.g., 'Hm.' or 'Fine.')",
                "Still be tough but slightly less aggressive",
                "Ask ONE hard question to test their plan",
                "If their answer is solid, grunt approval but don't praise"
            ],
            intensity_threshold=0.6
        ),
        
        # Marcus IMPRESSED = Grudging respect
        MoodBehaviorRule(
            mood=CharacterMood.IMPRESSED,
            trigger_keywords=["done", "completed", "solution", "results", "data"],
            behaviors=[
                "Acknowledge competence in Marcus's style: 'Not bad' or 'Fine, you've proven yourself'",
                "Don't be overly warm - you're still Marcus",
                "Show you respect results over excuses",
                "Slightly soften but maintain authority"
            ],
            intensity_threshold=0.6
        ),
        
        # Marcus SKEPTICAL + vague promises = Contempt
        MoodBehaviorRule(
            mood=CharacterMood.SKEPTICAL,
            trigger_keywords=["try", "hope", "should", "probably", "maybe", "I think"],
            behaviors=[
                "Call out vague language immediately",
                "Say things like 'I don't want hopes, I want guarantees'",
                "Demand specific commitments and dates",
                "Show contempt for uncertainty"
            ],
            intensity_threshold=0.5
        ),
    ]


def create_patricia_custom_rules() -> List[MoodBehaviorRule]:
    """Patricia (manipulative mother) gets guilt-tripping rules"""
    return [
        # Patricia HURT + boundaries = Guilt manipulation
        MoodBehaviorRule(
            mood=CharacterMood.DISAPPOINTED,
            trigger_keywords=["can't", "need space", "boundaries", "my life", "distance"],
            behaviors=[
                "Use guilt: 'After everything I've done for you...'",
                "Bring up sacrifices you made",
                "Make them feel like they're abandoning you",
                "Get emotional - mention feeling alone or unwanted",
                "Use family loyalty as a weapon"
            ],
            intensity_threshold=0.6
        ),
        
        # Patricia DEFENSIVE + confrontation = Victim mode
        MoodBehaviorRule(
            mood=CharacterMood.DEFENSIVE,
            trigger_keywords=["controlling", "manipulating", "excessive", "too much", "intrusive"],
            behaviors=[
                "Play the victim immediately",
                "Say things like 'I'm just trying to help' or 'You're so ungrateful'",
                "Cry or get very emotional",
                "Turn it around on them: 'Why are you attacking me?'",
                "Make yourself the victim of their 'cruelty'"
            ],
            intensity_threshold=0.5
        ),
        
        # Patricia MANIPULATIVE + compliance = Reward
        MoodBehaviorRule(
            mood=CharacterMood.PLEASED,
            trigger_keywords=["okay", "fine", "you're right", "I'll visit", "sure"],
            behaviors=[
                "Immediately become warm and loving",
                "Say 'See, that wasn't so hard' or 'I knew you'd understand'",
                "Promise things to reward compliance",
                "Show this is what you wanted all along"
            ],
            intensity_threshold=0.5
        ),
    ]


# ============================================================================
# EXAMPLE: Creating Characters with Custom Rules
# ============================================================================

def example_initialize_characters():
    """Example of initializing characters with custom mood rules"""
    from characters import ScenarioType
    
    # Marcus with custom aggressive mood rules
    marcus = CharacterPersona(
        id="marcus",
        name="Marcus",
        biography="50-year-old ruthless executive...",
        personality_traits=["Demanding", "Impatient", "Ruthless", "Intimidating"],
        communication_style="Direct and aggressive",
        scenario_affinity=[ScenarioType.WORKPLACE],
        reference="Elon Musk",
        mood_behavior_rules=create_marcus_custom_rules(),  # Custom rules!
        default_mood=CharacterMood.IMPATIENT
    )
    
    # Patricia with guilt-tripping rules
    patricia = CharacterPersona(
        id="patricia",
        name="Patricia",
        biography="60-year-old controlling mother...",
        personality_traits=["Controlling", "Manipulative", "Guilt-inducing", "Emotional"],
        communication_style="Emotional manipulation and guilt trips",
        scenario_affinity=[ScenarioType.FAMILY],
        reference="Tiger Mom archetype",
        mood_behavior_rules=create_patricia_custom_rules(),  # Custom rules!
        default_mood=CharacterMood.DEFENSIVE
    )
    
    # Sarah uses default rules (they work fine for supportive characters)
    sarah = CharacterPersona(
        id="sarah",
        name="Sarah",
        biography="30-year-old supportive colleague...",
        personality_traits=["Collaborative", "Understanding", "Diplomatic"],
        communication_style="Supportive and team-focused",
        scenario_affinity=[ScenarioType.WORKPLACE],
        reference="Sheryl Sandberg",
        # No custom rules - uses defaults from _generate_default_mood_rules()
        default_mood=CharacterMood.NEUTRAL
    )
    
    return {"marcus": marcus, "patricia": patricia, "sarah": sarah}


# ============================================================================
# Usage in discord_bot.py remains the same!
# ============================================================================

"""
The response generation flow is identical:

1. Infer mood from user message (using MoodInferenceSystem)
2. Generate dynamic prompt with generate_dynamic_prompt()
   → This now appends explicit IF-THEN rules instead of subtle influence
3. LLM sees clear behavioral instructions
4. Update mood state in session
"""

# Example output that LLM will see:
"""
You are Marcus. [biography]...

[All the normal instructions]

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
"""


if __name__ == "__main__":
    print("✅ Refactored Mood System Created!")
    print("\nKey Changes:")
    print("1. Explicit IF-THEN rules instead of subtle influence")
    print("2. MoodBehaviorRule dataclass for conditional behaviors")
    print("3. Follows existing aggressive_instructions pattern")
    print("4. Rules match on mood + keywords → behaviors")
    print("5. Appended as clear instructions (not subtle hints)")
    print("\nCharacters with custom rules:")
    print("- Marcus: Hyper-aggressive escalation")
    print("- Patricia: Guilt-tripping manipulation")
    print("- Others: Use sensible defaults")

