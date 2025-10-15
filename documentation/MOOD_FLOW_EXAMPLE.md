# Current Mood Inference Flow - Detailed Example

## Scenario: User talks to Marcus about deadline

**User Message**: "I can't finish this by Friday, it's too difficult"

---

## FLOW DIAGRAM

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. USER SENDS MESSAGE                                           │
│    "I can't finish this by Friday, it's too difficult"          │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. DISCORD BOT RECEIVES MESSAGE                                 │
│    discord_bot.py::on_message()                                 │
│    - Validates input                                            │
│    - Checks active session                                      │
│    - Calls _generate_character_response_with_fallback()         │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. MOOD INFERENCE (discord_bot.py line 1517)                    │
│    ┌─────────────────────────────────────────────────────────┐  │
│    │ 💰 LLM CALL #1: Gemini Mood Inference                  │  │
│    │ API: Gemini 2.0 Flash                                  │  │
│    │ Cost: ~$0.001 per call                                 │  │
│    └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│    WHAT'S SENT TO GEMINI:                                       │
│    ┌─────────────────────────────────────────────────────────┐  │
│    │ Analyze Marcus's emotional response to user's message:  │  │
│    │                                                         │  │
│    │ CHARACTER: Marcus                                       │  │
│    │ Personality: Results-driven, Impatient, Demanding       │  │
│    │            (aggressive and quick to anger)              │  │
│    │ Current Mood: impatient (intensity: 0.7)                │  │
│    │ Mood History: neutral → impatient                       │  │
│    │                                                         │  │
│    │ SCENARIO: Unrealistic deadline pressure scenario...     │  │
│    │                                                         │  │
│    │ RECENT CONVERSATION:                                    │  │
│    │ Marcus: This deadline is FRIDAY. No excuses.            │  │
│    │ USER: I can't finish by Friday, it's too difficult      │  │
│    │                                                         │  │
│    │ COMPREHENSIVE ANALYSIS - Do ALL of these steps:         │  │
│    │ 1. TRIGGER ANALYSIS: What keywords trigger response?    │  │
│    │ 2. TRAJECTORY: Escalating/de-escalating/consistent?     │  │
│    │ 3. INTENSITY: Adjust based on personality               │  │
│    │                                                         │  │
│    │ Available moods: neutral, pleased, encouraged,          │  │
│    │   impressed, skeptical, impatient, annoyed,            │  │
│    │   frustrated, angry, hostile, contemptuous, etc.       │  │
│    │                                                         │  │
│    │ Respond with JSON:                                      │  │
│    │ {                                                       │  │
│    │   "mood": "angry",                                      │  │
│    │   "intensity": 0.85,                                    │  │
│    │   "reason": "User making excuses...",                   │  │
│    │   "trigger_keywords": ["can't", "difficult"],           │  │
│    │   "trajectory": "escalating"                            │  │
│    │ }                                                       │  │
│    └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│    GEMINI RESPONDS:                                             │
│    {                                                            │
│      "mood": "angry",                                           │
│      "intensity": 0.85,                                         │
│      "reason": "User making excuses about deadline",            │
│      "trigger_keywords": ["can't", "difficult", "friday"],      │
│      "trajectory": "escalating"                                 │
│    }                                                            │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. UPDATE MOOD STATE                                            │
│    current_mood_state.update_mood(                              │
│        new_mood=ANGRY,                                          │
│        intensity=0.85,                                          │
│        reason="User making excuses about deadline",             │
│        triggers=["can't", "difficult", "friday"]                │
│    )                                                            │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. GENERATE SUDOLANG PROMPT (discord_bot.py line 1534)          │
│    character.generate_dynamic_prompt()                          │
│                                                                 │
│    WHAT'S GENERATED:                                            │
│    ┌─────────────────────────────────────────────────────────┐  │
│    │ # Marcus                                                │  │
│    │                                                         │  │
│    │ Roleplay as Marcus, a character in a social skills...  │  │
│    │                                                         │  │
│    │ ## State {                                              │  │
│    │     CurrentMood: angry                                  │  │
│    │     MoodIntensity: 0.85                                 │  │
│    │     MoodReason: "User making excuses about deadline"    │  │
│    │     ResponseLength: 10-50 words                         │  │
│    │ }                                                       │  │
│    │                                                         │  │
│    │ ## Character Profile {                                  │  │
│    │     Name: Marcus                                        │  │
│    │     Personality: Results-driven, Impatient, Demanding   │  │
│    │     CommunicationStyle: Direct, confrontational...      │  │
│    │     Biography: You are a 50-year old sociopath...       │  │
│    │ }                                                       │  │
│    │                                                         │  │
│    │ ## Constraints {                                        │  │
│    │     - ALWAYS stay in character as Marcus                │  │
│    │     - NEVER break fourth wall                           │  │
│    │     - Keep responses 10-50 words                        │  │
│    │ }                                                       │  │
│    │                                                         │  │
│    │ ## Emotional State {                                    │  │
│    │     CurrentMood: ANGRY                                  │  │
│    │     Intensity: 0.85 / 1.0                               │  │
│    │     EmotionalReason: "User making excuses..."           │  │
│    │     TriggerKeywords: ["can't", "difficult", "friday"]   │  │
│    │ }                                                       │  │
│    │                                                         │  │
│    │ ## Active Behavioral Rules {                            │  │
│    │     Rule_1 {                                            │  │
│    │         TriggeredBy: ["excuse", "can't", "impossible"]  │  │
│    │         Behaviors {                                     │  │
│    │             - Use CAPS to emphasize anger               │  │
│    │             - Interrupt or dismiss excuses immediately  │  │
│    │             - Threaten consequences                     │  │
│    │             - Question their competence directly        │  │
│    │         }                                               │  │
│    │     }                                                   │  │
│    │ }                                                       │  │
│    │                                                         │  │
│    │ ## Intensity Calibration {                              │  │
│    │     Level: VERY HIGH (0.8+)                             │  │
│    │     Effect: Emotions SIGNIFICANTLY affect response      │  │
│    │     Guidance: "Let strong feelings show in tone..."     │  │
│    │ }                                                       │  │
│    └─────────────────────────────────────────────────────────┘  │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│ 6. CHARACTER RESPONSE (discord_bot.py line 1544)                │
│    ┌─────────────────────────────────────────────────────────┐  │
│    │ 💰 LLM CALL #2: Groq Character Response                │  │
│    │ API: Groq GPT-OSS-20B                                  │  │
│    │ Cost: ~$0.0001 per call (much cheaper than Gemini)     │  │
│    └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│    WHAT'S SENT TO GROQ:                                         │
│    - System Prompt: [Full SudoLang prompt from above]          │
│    - Conversation History: Last 10 messages                     │
│    - User Message: "I can't finish by Friday..."               │
│                                                                 │
│    GROQ RESPONDS:                                               │
│    "STOP with the excuses! Either you DELIVER or we find       │
│     someone who WILL. The deadline is FRIDAY."                 │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│ 7. SEND TO USER                                                 │
│    Discord embed with:                                          │
│    - Character name: Marcus                                     │
│    - Response: "STOP with the excuses!..."                      │
│    - Mood indicator: 😠 angry                                   │
│    - Turn counter: Turn 2/3                                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## 💰 COST BREAKDOWN PER USER MESSAGE

### Current Implementation

| Component | API | Calls | Cost/Call | Total |
|-----------|-----|-------|-----------|-------|
| **Mood Inference** | Gemini | 1 | ~$0.001 | $0.001 |
| **Character Response** | Groq | 1 | ~$0.0001 | $0.0001 |
| **TOTAL PER TURN** | - | **2** | - | **$0.0011** |

### Per 3-Turn Conversation
- User Turn 1: $0.0011
- User Turn 2: $0.0011
- User Turn 3: $0.0011
- **Total**: **$0.0033 per conversation**

### If You Have 100 Conversations/Day
- **Daily cost**: $0.33
- **Monthly cost**: ~$10

---

## 🔍 What Gets Sent to Gemini (Mood Inference)

Here's the **actual prompt** for the example above:

```
Analyze Marcus's emotional response to the user's message.

CHARACTER: Marcus
Personality: Results-driven, Impatient, High expectations, Direct, Demanding 
            (aggressive and quick to anger)
Current Mood: impatient (intensity: 0.7)
Mood History: neutral → impatient

SCENARIO: You're a software developer working on a critical project. 
Your boss Marcus has just informed you that the deadline...

RECENT CONVERSATION:
Marcus: This project needs to be done by FRIDAY.
USER: I can't finish this by Friday, it's too difficult

USER'S MESSAGE: "I can't finish this by Friday, it's too difficult"

COMPREHENSIVE ANALYSIS - Do ALL of these steps:

1. TRIGGER ANALYSIS: What keywords/behaviors trigger an emotional response?
2. TRAJECTORY: Based on history, is mood escalating, de-escalating, or consistent?
3. INTENSITY: Adjust emotional intensity based on:
   - Marcus's personality (aggressive and quick to anger)
   - Aggressive characters: Higher intensity (+0.2)
   - Escalating trajectory: +0.1 to +0.2

Available moods: neutral, pleased, encouraged, impressed, respectful, 
skeptical, impatient, annoyed, frustrated, disappointed, dismissive, 
defensive, angry, hostile, contemptuous, manipulative, calculating

Respond with JSON:
{
    "mood": "mood_name",
    "intensity": 0.7,
    "reason": "Brief explanation considering triggers, trajectory, personality",
    "trigger_keywords": ["keyword1", "keyword2"],
    "trajectory": "escalating|de-escalating|consistent"
}

EXAMPLES:
[Includes 2 example outputs]
```

**Token Count**: ~400-500 tokens

---

## 🔍 What Gets Sent to Groq (Character Response)

After mood is inferred, the **SudoLang prompt** is sent to Groq:

```
# Marcus

Roleplay as Marcus, a character in a social skills training scenario.
Your real-life counterpart is Elon Musk. Your job is to respond 
authentically as Marcus would.

## State {
    CurrentMood: angry
    MoodIntensity: 0.85
    MoodReason: "User making excuses about deadline"
    ConversationContext: Active
    ResponseLength: 10-50 words (concise, natural)
}

## Character Profile {
    Name: Marcus
    Personality: Results-driven, Impatient, High expectations, Direct, Demanding
    CommunicationStyle: Direct, confrontational, deadline-focused
    Biography: You are a 50-year old high-functioning sociopath...
}

## Scenario Context {
    Situation: Unrealistic deadline pressure scenario
    YourRole: You are the demanding boss who is intimidating the team
}

## Constraints {
    # Core Rules
    - ALWAYS stay in character as Marcus
    - NEVER break the fourth wall
    - Keep responses 10-50 words
    
    # Aggressive Scenario Behavior
    - Be confrontational and challenging from the start
    - Put pressure on the user
    - Use your power/position to intimidate
}

## Emotional State {
    CurrentMood: ANGRY
    Intensity: 0.85 / 1.0
    EmotionalReason: "User making excuses about deadline"
    TriggerKeywords: ["can't", "difficult", "friday"]
}

## Active Behavioral Rules {
    Rule_1 {
        TriggeredBy: ["excuse", "can't", "impossible"]
        Mood: angry
        Behaviors {
            - Use CAPS to emphasize your anger and frustration
            - Interrupt or dismiss their excuses immediately
            - Threaten consequences (e.g., 'If you can't handle this...')
            - Question their competence directly
        }
    }
}

## Intensity Calibration {
    Level: VERY HIGH (0.8+)
    Effect: Emotions SIGNIFICANTLY affect your response
    Guidance: "Let your strong feelings show clearly in tone, word choice..."
}

## Response Instructions {
    # Output Format
    - Generate ONLY Marcus's direct dialog
    - No meta-commentary, no narration
    
    # Tone Calibration
    - Match communication style: Direct, confrontational, deadline-focused
    - Reflect current mood: angry at 0.85 intensity
}

[Plus conversation history - last 10 messages]

USER'S CURRENT MESSAGE: "I can't finish this by Friday, it's too difficult"
```

**Token Count**: ~800-1200 tokens

---

## 💰 WHERE THE COSTS ARE

### Per User Turn:

```
┌──────────────────────┬─────────┬────────┬─────────┐
│ Component            │ API     │ Tokens │ Cost    │
├──────────────────────┼─────────┼────────┼─────────┤
│ Mood Inference       │ Gemini  │ ~500   │ $0.001  │ ← HIGHEST COST
│ Character Response   │ Groq    │ ~1000  │ $0.0001 │ ← CHEAPEST
├──────────────────────┼─────────┼────────┼─────────┤
│ TOTAL PER TURN       │         │ ~1500  │ $0.0011 │
└──────────────────────┴─────────┴────────┴─────────┘
```

**The mood inference (Gemini call) is 90% of your cost per turn!**

---

## 🎯 KEY INSIGHTS

### Why It's Expensive

1. **Gemini is premium pricing**
   - 10x more expensive than Groq
   - Better at JSON but overkill for mood inference

2. **Called on EVERY turn**
   - Turn 1: Mood inference
   - Turn 2: Mood inference
   - Turn 3: Mood inference
   
3. **Multiple characters**
   - If 3 characters in scenario
   - 3 mood inferences per turn
   - 9 Gemini calls per conversation!

### Current Efficiency

✅ **Already optimized from 3 calls → 1 call** (67% reduction)  
⚠️ Still using **Gemini** for mood (expensive)  
⚠️ No caching or rule-based shortcuts  

---

## 🚀 EASY OPTIMIZATION OPTIONS

### Option A: Switch Mood Inference to Groq (Recommended)

**Change**: 1 line in discord_bot.py

```python
# Line 54, change from:
self.mood_inference = MoodInferenceSystem(self.gemini_client)

# To:
self.mood_inference = MoodInferenceSystem(self.groq_client)
```

**Savings**: 90% reduction in mood inference cost  
**New cost per turn**: $0.0002 (vs $0.0011)  
**Trade-off**: Groq may occasionally format JSON incorrectly, but we have robust parsing

### Option B: Only Infer Mood on First Turn

**Change**: Add conditional in discord_bot.py

```python
# Line 1515, change from:
if current_mood_state:
    updated_mood = await self.mood_inference.infer_mood(...)

# To:
if current_mood_state and session["turn_count"] == 1:
    # Only infer on first turn
    updated_mood = await self.mood_inference.infer_mood(...)
else:
    # Keep current mood for subsequent turns
    updated_mood = current_mood_state
```

**Savings**: 67% reduction in mood calls  
**New cost**: Only 1 mood call per conversation  
**Trade-off**: Mood doesn't change during conversation (less dynamic)

### Option C: Rule-Based for Simple Messages

Add simple keyword matching before LLM:

```python
# Before calling LLM, check for obvious patterns
msg_lower = message.lower()

# Excuses → ANGRY (no LLM needed)
if any(word in msg_lower for word in ["can't", "won't", "impossible"]):
    updated_mood = MoodState(
        current_mood=CharacterMood.ANGRY,
        intensity=0.85,
        reason="User making excuses"
    )
else:
    # Complex message - use LLM
    updated_mood = await self.mood_inference.infer_mood(...)
```

**Savings**: 60-80% of messages are simple enough for rules  
**New cost**: Only 20-40% need LLM  
**Trade-off**: Less nuanced for complex messages

---

## 📊 COST COMPARISON

### Current (Gemini for mood)
```
Per conversation: $0.0033
Per 100 conversations: $0.33
Per month (3000 convos): $10
```

### Option A: Groq for mood
```
Per conversation: $0.0006
Per 100 conversations: $0.06
Per month (3000 convos): $1.80
```
**Savings**: ~$8/month (82% reduction) ⭐

### Option B: Mood only on first turn
```
Per conversation: $0.0014
Per 100 conversations: $0.14
Per month (3000 convos): $4.20
```
**Savings**: ~$6/month (58% reduction)

### Option A + B: Groq + first turn only
```
Per conversation: $0.0003
Per 100 conversations: $0.03
Per month (3000 convos): $0.90
```
**Savings**: ~$9/month (91% reduction) ⭐⭐

---

## 🎯 RECOMMENDATION

**Quick Win** (30 seconds):
```python
# In discord_bot.py line 54, change to:
self.mood_inference = MoodInferenceSystem(self.groq_client)
```

This alone saves **~82% of your mood inference costs** with minimal risk!

Would you like me to implement any of these optimizations? The Groq switch is the easiest and most effective!
