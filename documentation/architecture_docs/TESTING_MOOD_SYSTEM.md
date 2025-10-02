# 🧪 Testing the Mood System

## Quick Test Protocol

### Test 1: Basic Flow
```
!start workplace_deadline

Expected:
✅ Marcus opening: ⏱️ impatient (orange/gold embed)
✅ Sarah opening: 😐 neutral (blue embed)
✅ No tuple strings in messages
✅ No serialization errors in logs
```

### Test 2: Mood Escalation
```
User: "I can't make that deadline"

Expected Marcus:
✅ Mood: impatient → frustrated (😤)
✅ Color: Changes to orange
✅ Response: Short, terse, shows impatience
✅ Logs show: "🎭 MOOD UPDATE: Marcus mood: impatient → frustrated"

User: "But it's impossible!"

Expected Marcus:
✅ Mood: frustrated → angry (😠)
✅ Color: Changes to red
✅ Response: Uses CAPS, threatens consequences
✅ Logs show: "Mood Transition: frustrated → angry"
```

### Test 3: Mood De-escalation
```
User: "Here's my detailed breakdown with timeline and dependencies..."

Expected Marcus:
✅ Mood: angry → skeptical (🤨)
✅ Color: Changes to orange
✅ Response: Less hostile, asks questions, tests the plan
✅ Logs show mood change and reason

User: "Backend API ready Monday, QA parallel, database migration Friday..."

Expected Marcus:
✅ Mood: skeptical → impressed (😮)
✅ Color: Changes to green
✅ Response: Grudging approval, "Fine. Two weeks."
```

### Test 4: Self-Reference
```
Turn 1 - Marcus: "The deadline is one week."
Turn 3 - User makes good point

Expected Marcus:
✅ References past: "I said one week, but you've shown me solid data."
✅ Maintains consistency while evolving stance
```

### Test 5: Other Character Awareness
```
Turn 2:
Marcus: "I don't want excuses."
Sarah: "Marcus, let's be realistic about constraints."

Turn 3 - User agrees with Sarah

Expected Marcus:
✅ Acknowledges Sarah: "Sarah has a point, but..." or "Sarah, I hear you, but..."
✅ Responds to both user AND Sarah's input
```

### Test 6: Session Persistence
```
1. Start scenario
2. Make 1-2 exchanges
3. Check logs: "💾 Saved 1 active sessions" (no errors)
4. Restart bot
5. Verify session restores with moods intact
```

---

## 📋 Verification Checklist

### Functional Requirements
- [ ] Opening messages display clean text (no tuples)
- [ ] Embed colors change based on mood
- [ ] Footer shows mood emoji and name
- [ ] Marcus escalates when user makes excuses
- [ ] Marcus de-escalates when user presents solutions
- [ ] Sarah shows empathy/support appropriately
- [ ] Characters reference their own past statements
- [ ] Characters reference other characters' statements
- [ ] Moods persist in session saves
- [ ] No serialization errors in logs

### Performance Requirements
- [ ] Response time < 5s per character
- [ ] Mood inference completes < 2s
- [ ] No rate limit errors
- [ ] Logs are clear and informative

### Error Handling
- [ ] Mood inference failure doesn't crash bot
- [ ] Invalid moods default to neutral
- [ ] Missing mood state uses character default
- [ ] Backward compatible with old sessions

---

## 🎯 Expected Log Output

### Successful Scenario Start:
```
🎭 INIT: Marcus starting mood: impatient
🎭 INIT: Sarah starting mood: neutral
🎬 START: Generating opening message for Marcus
🎭 MOOD: Starting mood inference for Marcus
🎭 MOOD: Current state: impatient (0.7)
✅ MOOD: Marcus mood updated: impatient (intensity: 0.7)
✅ RESPONSE: Generated for Marcus in mood impatient
🎬 START: Generated opening message for Marcus: We've moved the deadline up 2 weeks...
🎬 START: ✅ Successfully sent opening message from Marcus
💾 Saved 1 active sessions
```

### Successful User Response:
```
🎭 MULTI-CHAR: Starting multi-character response generation
🎭 MULTI-CHAR: Found 2 characters to respond
🎭 MULTI-CHAR: Generating response for Marcus
🎭 MOOD: Starting mood inference for Marcus
🎭 MOOD: Current state: impatient (0.7)
🎭 MOOD: User message: 'I can't make that deadline...'
✅ MOOD: Marcus mood updated: frustrated (intensity: 0.8)
✅ MOOD: Reason: User making excuses instead of taking responsibility
✅ MOOD: Triggers: ['excuse', 'can't']
🎭 PROMPT: Generated dynamic prompt for Marcus (mood: frustrated)
✅ RESPONSE: Generated for Marcus in mood frustrated
🎭 MOOD UPDATE: Marcus mood: impatient → frustrated
🎭 MULTI-CHAR: ✅ Successfully sent response from Marcus
```

---

## 🎨 Visual Examples

### Marcus Mood Progression:

**Turn 1** [⏱️ impatient - 🟡 Gold]
```
We've moved the deadline up 2 weeks. Get it done in a week.
```

**Turn 2** [😤 frustrated - 🟠 Orange]
```
I don't want to hear that you can't. Figure it out.
```

**Turn 3** [😠 angry - 🔴 Red]
```
Stop making EXCUSES! Either deliver or you're FIRED!
```

**Turn 4** [🤨 skeptical - 🟠 Orange]
```
Hmm. Show me this plan you're talking about.
```

**Turn 5** [😮 impressed - 🟢 Green]
```
Fine. You've thought this through. Two weeks. Don't disappoint me.
```

---

## ⚠️ Common Issues

### Issue: "No mood state provided" warning
**Cause:** Old code path not passing mood state  
**Impact:** Falls back to neutral mood (safe)  
**Fix:** All code paths now updated

### Issue: Tuple showing in message
**Cause:** Not unpacking return value  
**Impact:** User sees `('text', MoodState(...))`  
**Fix:** All call sites now unpack: `response, mood = await ...`

### Issue: Serialization error
**Cause:** MoodState object in conversation_history  
**Impact:** Session save fails  
**Fix:** Only string response added to history, not tuple

---

## 🚀 Ready to Test!

The system is now production-ready. Run a scenario and you should see:
- ✅ Clean message text
- ✅ Dynamic mood colors
- ✅ Mood emojis in footer
- ✅ Emotional character responses
- ✅ Self-aware conversation
- ✅ No errors in logs

**Go ahead and test with `!start workplace_deadline`!** 🎉

