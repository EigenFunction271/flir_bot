# 🎭 Mood System Flow Diagram

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     USER SENDS MESSAGE                       │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              DISCORD BOT (on_message handler)                │
│  • Receives user message                                     │
│  • Validates input                                           │
│  • Gets active session                                       │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│         FOR EACH CHARACTER IN SCENARIO (Sequential)          │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│               STEP 1: MOOD INFERENCE                         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ MoodInferenceSystem.infer_mood()                    │   │
│  │  • Get character's current mood                     │   │
│  │  • Analyze user message + character personality      │   │
│  │  • LLM call to infer new emotional state            │   │
│  │  • Return: {mood, intensity, reason}                │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│          STEP 2: GENERATE DYNAMIC PROMPT                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ CharacterPersona.generate_dynamic_prompt()          │   │
│  │  • Load mood template for current mood               │   │
│  │  • Apply intensity modifier                          │   │
│  │  • Add mood transition context                       │   │
│  │  • Combine with character bio + scenario             │   │
│  │  • Return: Complete system prompt                    │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│            STEP 3: GENERATE CHARACTER RESPONSE               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ GroqClient.generate_response_with_history()         │   │
│  │  • Use mood-aware system prompt                      │   │
│  │  • Include conversation history                      │   │
│  │  • Generate character's response                     │   │
│  │  • Return: Response text                             │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              STEP 4: UPDATE SESSION & DISPLAY                │
│  • Update character_moods[char_id] with new MoodState       │
│  • Add response to conversation_history                      │
│  • Create Discord embed with mood indicator                  │
│  • Send to user                                              │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                  PERSIST SESSION TO DISK                     │
│  • Serialize character moods                                 │
│  • Save to active_sessions.json                              │
└─────────────────────────────────────────────────────────────┘
```

## Detailed Mood Inference Flow

```
USER MESSAGE: "I understand the deadline, but I need help prioritizing."
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              MOOD INFERENCE PROMPT BUILT                     │
│                                                              │
│  Character: Marcus (Demanding boss)                          │
│  Current Mood: ANGRY (intensity: 0.8)                       │
│  User Message: "I understand... but I need help..."         │
│  Personality: Demanding, Impatient, Ruthless                │
│                                                              │
│  LLM Prompt: "How would Marcus feel hearing this?"          │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    LLM ANALYSIS                              │
│                                                              │
│  "Marcus would feel FRUSTRATED because:                      │
│   - User is still making excuses                            │
│   - But showing some willingness to work                     │
│   - Slight decrease in anger, still annoyed"                │
│                                                              │
│  Returns: {                                                  │
│    "mood": "frustrated",                                     │
│    "intensity": 0.7,                                         │
│    "reason": "User asking for help but still resisting"      │
│  }                                                           │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                 MOOD STATE UPDATED                           │
│                                                              │
│  Previous: ANGRY (0.8)                                       │
│  Current:  FRUSTRATED (0.7)                                  │
│  Reason:   "User asking for help but still resisting"       │
│                                                              │
│  Mood history: [NEUTRAL, IMPATIENT, ANGRY, FRUSTRATED]      │
└─────────────────────────────────────────────────────────────┘
```

## Dynamic Prompt Generation Flow

```
┌─────────────────────────────────────────────────────────────┐
│            CHARACTER DEFINITION (Static)                     │
│                                                              │
│  Name: Marcus                                                │
│  Biography: "50-year-old executive, ruthless..."            │
│  Traits: [Demanding, Impatient, Ruthless]                   │
│  Reference: Elon Musk                                        │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│            SCENARIO CONTEXT (Per Session)                    │
│                                                              │
│  Scenario: Unrealistic Deadline                             │
│  Context: "Boss moved deadline up 2 weeks..."               │
│  Role: "Demanding boss under CEO pressure..."               │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              MOOD STATE (Dynamic)                            │
│                                                              │
│  Current: FRUSTRATED                                         │
│  Intensity: 0.7                                              │
│  Reason: "User asking for help but still resisting"         │
│  Previous: ANGRY                                             │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│         MOOD TEMPLATE (Character-Specific)                   │
│                                                              │
│  FRUSTRATED Template:                                        │
│  "You're losing patience quickly. Your responses are        │
│   terse and show clear irritation. Make pointed comments    │
│   about competence."                                         │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              INTENSITY MODIFIER                              │
│                                                              │
│  Intensity: 0.7 (Moderate)                                   │
│  Modifier: "Your emotions are moderately affecting your     │
│             responses."                                      │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│            TRANSITION CONTEXT                                │
│                                                              │
│  "You were feeling ANGRY but now feel FRUSTRATED because:   │
│   User asking for help but still resisting"                 │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│          COMBINED DYNAMIC SYSTEM PROMPT                      │
│                                                              │
│  "You are Marcus. [biography] You act like Elon Musk.       │
│                                                              │
│   Current Emotional State:                                   │
│   You're losing patience quickly. Your responses are        │
│   terse and show clear irritation. Make pointed comments    │
│   about competence.                                          │
│                                                              │
│   Your emotions are moderately affecting your responses.    │
│                                                              │
│   You were feeling ANGRY but now feel FRUSTRATED because:   │
│   User asking for help but still resisting.                 │
│                                                              │
│   Guidelines: React through your current mood (frustrated)  │
│   ..."                                                       │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
                   LLM GENERATES RESPONSE
                   Using mood-aware prompt
```

## Session Persistence Flow

```
┌─────────────────────────────────────────────────────────────┐
│                   ACTIVE SESSION (RAM)                       │
│                                                              │
│  {                                                           │
│    scenario: {...},                                          │
│    characters: [...],                                        │
│    conversation_history: [...],                             │
│    character_moods: {                                        │
│      "marcus": MoodState(FRUSTRATED, 0.7, "..."),           │
│      "sarah": MoodState(EMPATHETIC, 0.8, "...")             │
│    }                                                         │
│  }                                                           │
└─────────────────────────┬───────────────────────────────────┘
                          │
                   Save triggered
                   (every 5 min or on change)
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│            SERIALIZE MOOD STATES                             │
│                                                              │
│  character_moods: {                                          │
│    "marcus": {                                               │
│      "current_mood": "frustrated",                          │
│      "intensity": 0.7,                                       │
│      "reason": "User asking but resisting",                 │
│      "previous_mood": "angry",                              │
│      "mood_history": ["neutral", "impatient", "angry"]      │
│    },                                                        │
│    "sarah": {...}                                            │
│  }                                                           │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              WRITE TO active_sessions.json                   │
│                                                              │
│  {                                                           │
│    "user_id_12345": {                                        │
│      "scenario": {...},                                      │
│      "character_moods": {                                    │
│        "marcus": {"current_mood": "frustrated", ...}         │
│      }                                                        │
│    }                                                         │
│  }                                                           │
└─────────────────────────────────────────────────────────────┘

                      BOT RESTARTS
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│             LOAD FROM active_sessions.json                   │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│          DESERIALIZE MOOD STATES                             │
│                                                              │
│  MoodState.from_dict({                                       │
│    "current_mood": "frustrated",                            │
│    "intensity": 0.7,                                         │
│    ...                                                       │
│  })                                                          │
│                                                              │
│  → MoodState(FRUSTRATED, 0.7, "...")                        │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│           SESSION RESTORED WITH MOODS                        │
│  Marcus is still FRUSTRATED where they left off!            │
└─────────────────────────────────────────────────────────────┘
```

## Example: Complete Interaction Flow

```
SCENARIO START
│
├─ User starts "workplace_deadline" scenario
│
├─ Marcus initialized: IMPATIENT (0.7) - "Starting aggressive scenario"
│
├─ Sarah initialized: NEUTRAL (0.5) - "Starting as mediator"
│
└─ Opening messages sent

TURN 1
│
├─ User: "The deadline seems really tight..."
│
├─ MARCUS PROCESSING:
│   ├─ Current mood: IMPATIENT (0.7)
│   ├─ Mood inference: → FRUSTRATED (0.8)
│   │   Reason: "User making excuses immediately"
│   ├─ Dynamic prompt generated with FRUSTRATED template
│   └─ Response: "I don't want to hear that it's tight. Just get it done."
│
└─ SARAH PROCESSING:
    ├─ Current mood: NEUTRAL (0.5)
    ├─ Mood inference: → EMPATHETIC (0.6)
    │   Reason: "User expressing concern, seems stressed"
    ├─ Dynamic prompt generated with EMPATHETIC template
    └─ Response: "I understand your concern. Let's look at priorities."

TURN 2
│
├─ User: "But Marcus, the dependencies aren't ready yet!"
│
├─ MARCUS PROCESSING:
│   ├─ Current mood: FRUSTRATED (0.8)
│   ├─ Mood inference: → ANGRY (0.9)
│   │   Reason: "User arguing back, challenged authority"
│   ├─ Dynamic prompt: ANGRY template + HIGH intensity
│   └─ Response: "That's YOUR problem to solve! Figure it out or you're FIRED!"
│
└─ SARAH PROCESSING:
    ├─ Current mood: EMPATHETIC (0.6)
    ├─ Mood inference: → WORRIED (0.7)
    │   Reason: "Marcus escalating, user might get fired"
    ├─ Dynamic prompt: WORRIED template
    └─ Response: "Marcus, wait... maybe we should discuss this calmly."

TURN 3
│
├─ User: "Marcus, I have a proposal: give me 2 weeks and I can deliver quality work with proper testing."
│
└─ MARCUS PROCESSING:
    ├─ Current mood: ANGRY (0.9)
    ├─ Mood inference: → SKEPTICAL (0.6)
    │   Reason: "User presenting solution, not just complaining. Caught off guard but suspicious"
    ├─ Dynamic prompt: SKEPTICAL template + transition from ANGRY
    │   "You were ANGRY but now SKEPTICAL - user actually proposed something concrete"
    └─ Response: "Two weeks? What makes you think I can sell that to the CEO? Explain."

SCENARIO END
│
└─ Feedback generated showing mood progression:
    "Marcus's frustration → anger → skepticism shows your approach evolved
     from making excuses to proposing solutions."
```

## Key Decision Points

### When to Infer Mood?

```
┌──────────────────────────────────────────┐
│         User sends message               │
└───────────┬──────────────────────────────┘
            │
            ▼
      ┌─────────────┐
      │ Is mood     │  NO  ─────┐
      │ inference   │            │
      │ enabled?    │            │
      └─────┬───────┘            │
            │ YES                │
            ▼                    │
      ┌─────────────┐            │
      │ Message > 5 │  NO  ──────┤
      │ words?      │            │
      └─────┬───────┘            │
            │ YES                │
            ▼                    │
      ┌─────────────┐            │
      │ Last update │  NO  ──────┤
      │ > cache     │            │
      │ duration?   │            │
      └─────┬───────┘            │
            │ YES                │
            ▼                    ▼
    [Infer new mood]    [Keep current mood]
```

### When to Use Custom Templates?

```
┌────────────────────────────────────────────────┐
│   Character has custom mood_templates?         │
└────────────┬──────────────┬────────────────────┘
             │ YES          │ NO
             ▼              ▼
    [Use custom]    [Use default template]
         │                  │
         └────────┬─────────┘
                  ▼
          Get template for mood
                  │
                  ▼
           Apply intensity
                  │
                  ▼
          Add transition context
                  │
                  ▼
          Build full prompt
```

## Performance Metrics

```
Expected timing per character response:

Mood Inference:       0.5-1.5s  ████████████░░░░
Prompt Generation:    0.01s     █
LLM Response:         1-2s      ████████████████
Total per character:  ~2-3s     ████████████████████████

Multi-character (3):  ~6-9s     (sequential)
```

---

**Tip**: Start with mood inference only for key characters (Marcus, Patricia)
to reduce latency while testing!

