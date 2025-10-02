# Debugging Guide - Message Delivery Issues

## 🔍 Quick Diagnosis Reference

### **Log Patterns to Look For**

#### ✅ **Healthy Message Flow**
```
🎭 MULTI-CHAR: Generating response for [Character]
🎭 MULTI-CHAR: Generated response for [Character]: [preview]
🎭 MULTI-CHAR: Attempting to send response from [Character]
🎭 MULTI-CHAR: ✅ Successfully sent response from [Character]
🎭 MULTI-CHAR: Added [Character]'s response to history. New length: X
```

#### ⚠️ **Transient Failure (Recoverable)**
```
🎭 MULTI-CHAR: Generating response for Alex
🎭 MULTI-CHAR: Generated response for Alex: ...
🎭 MULTI-CHAR: Attempting to send response from Alex
🎭 MULTI-CHAR: ❌ Discord HTTP error sending Alex's message (attempt 1/3): ...
[wait 1 second]
🎭 MULTI-CHAR: ✅ Successfully sent response from Alex  ← RECOVERED
```

#### 🚨 **Critical Failure (Message Lost)**
```
🎭 MULTI-CHAR: Generated response for Alex: ...
🎭 MULTI-CHAR: ❌ Discord HTTP error sending Alex's message (attempt 1/3)
🎭 MULTI-CHAR: ❌ Discord HTTP error sending Alex's message (attempt 2/3)
🎭 MULTI-CHAR: ❌ Discord HTTP error sending Alex's message (attempt 3/3)
🎭 MULTI-CHAR: ❌ FAILED to send Alex's message after 3 attempts  ← MESSAGE LOST
🎭 MULTI-CHAR: ❌ NOT adding Alex's response to history because message send failed
```

---

## 🐛 **Common Issues & Solutions**

### **Issue 1: Messages Generated But Not Sent**

**Symptoms:**
```
🎭 MULTI-CHAR: Generated response for Alex: ...
🎭 MULTI-CHAR: Added Alex's response to history. New length: 3
[NO "Successfully sent" log]
```

**Diagnosis:** Old code bug (fixed in MESSAGE_RELIABILITY_FIX.md)

**Solution:** Update to latest version of `discord_bot.py`

---

### **Issue 2: Discord Rate Limiting**

**Symptoms:**
```
❌ Discord HTTP error sending Alex's message: HTTPException[429]: Too Many Requests
```

**Root Cause:** Sending too many messages too quickly

**Solutions:**
1. Increase delay between character messages (currently 1 second)
2. Reduce number of concurrent scenarios
3. Check Discord API rate limits in Developer Portal

**Temporary Fix:**
```python
# In discord_bot.py, increase delay
await asyncio.sleep(2)  # Increase from 1 to 2 seconds
```

---

### **Issue 3: Discord API Outage**

**Symptoms:**
```
❌ Discord HTTP error: HTTPException[500]: Internal Server Error
❌ Discord HTTP error: HTTPException[502]: Bad Gateway
❌ Discord HTTP error: HTTPException[503]: Service Unavailable
```

**Root Cause:** Discord's servers are having issues

**Solutions:**
1. Check https://discordstatus.com
2. Wait for Discord to recover
3. Retry logic will handle temporary outages

**No action needed** - Retry logic automatically handles this

---

### **Issue 4: Network Timeout**

**Symptoms:**
```
❌ Unexpected error sending Alex's message: TimeoutError
```

**Root Cause:** Network connectivity issues

**Solutions:**
1. Check server internet connection
2. Check firewall rules
3. Verify DNS resolution for discord.com

**Test:**
```bash
ping discord.com
curl -I https://discord.com/api/v10/gateway
```

---

### **Issue 5: Groq API Timeout**

**Symptoms:**
```
groq_client - ERROR - Groq API request timed out
```

**Root Cause:** Groq API slow response or network issues

**Solutions:**
1. Check Groq API status
2. Increase timeout (currently 30 seconds)
3. Switch to faster model

**Temporary Fix:**
```python
# In groq_client.py, line 116
timeout=aiohttp.ClientTimeout(total=60)  # Increase from 30 to 60
```

---

### **Issue 6: Gemini API Failure**

**Symptoms:**
```
gemini_client - ERROR - Error generating feedback with Gemini: ...
gemini_client - WARNING - Gemini rate limit reached, waiting X seconds
```

**Root Cause:** Rate limits or API issues

**Solutions:**
1. Check Gemini API quota
2. Reduce feedback generation frequency
3. Use fallback feedback (automatically happens)

**No action needed** - Fallback mechanism handles this

---

## 📊 **Monitoring Commands**

### **Check Active Sessions**
```bash
# In Discord
!debug

# In logs
grep "Active Sessions" flir_bot.log
```

### **Check Error Rate**
```bash
# Count errors in last hour
grep "$(date -d '1 hour ago' '+%Y-%m-%d %H')" flir_bot.log | grep "❌" | wc -l

# Count successful sends
grep "$(date -d '1 hour ago' '+%Y-%m-%d %H')" flir_bot.log | grep "✅ Successfully sent" | wc -l
```

### **Check Message Delivery Rate**
```bash
# Calculate success rate
SUCCESS=$(grep "✅ Successfully sent response" flir_bot.log | wc -l)
ATTEMPTS=$(grep "Attempting to send response" flir_bot.log | wc -l)
echo "scale=2; $SUCCESS * 100 / $ATTEMPTS" | bc
```

### **Find Recent Failures**
```bash
# Last 10 failed messages
grep "❌ FAILED to send" flir_bot.log | tail -10

# Last 10 retry attempts
grep "Discord HTTP error sending" flir_bot.log | tail -10
```

---

## 🔧 **Emergency Fixes**

### **If Discord API is Completely Down**

**Option 1: Fallback to Simple Text Messages**
```python
# In _generate_multi_character_responses
try:
    await channel.send(embed=embed)
except discord.HTTPException:
    # Fallback to plain text
    await channel.send(f"**{character.name}:** {response}")
```

**Option 2: Pause Message Sending**
```python
# In discord_bot.py
if self.consecutive_failures > 10:
    await ctx.send("⚠️ Bot is experiencing issues. Pausing for 5 minutes.")
    await asyncio.sleep(300)
```

### **If Groq API is Down**

**Option 1: Use Cached Responses (if implemented)**
```python
# Check cache first
if response := self.response_cache.get(message_hash):
    return response
```

**Option 2: Use Fallback Messages**
```python
# In _generate_character_response_with_fallback
return self._generate_basic_character_response(character, message)
```

### **If Everything is Failing**

**Enable Maintenance Mode:**
```python
# Set in .env
MAINTENANCE_MODE=True

# Add check in on_message
if Config.MAINTENANCE_MODE:
    await message.channel.send("🔧 Bot is under maintenance. Please try again later.")
    return
```

---

## 📞 **Escalation Path**

### **Level 1: Transient Issues** (Self-Healing)
- Retry logic handles automatically
- User receives notification if needed
- No action required

### **Level 2: Persistent Issues** (Manual Investigation)
- Check logs for patterns
- Check external service status
- Adjust configuration if needed

### **Level 3: Critical Issues** (Emergency Response)
- Multiple services down
- High error rate (>10% failures)
- User-facing impact

**Actions:**
1. Enable maintenance mode
2. Check all external dependencies
3. Rollback to previous version if needed
4. Post status update for users

---

## 📝 **Log Analysis Tools**

### **Parse Logs for Statistics**
```bash
#!/bin/bash
# save as analyze_logs.sh

LOG_FILE="flir_bot.log"

echo "=== Message Delivery Statistics ==="
GENERATED=$(grep "Generated response for" $LOG_FILE | wc -l)
SENT=$(grep "Successfully sent response from" $LOG_FILE | wc -l)
FAILED=$(grep "FAILED to send" $LOG_FILE | wc -l)
RETRIED=$(grep "attempt 2/3" $LOG_FILE | wc -l)

echo "Messages Generated: $GENERATED"
echo "Messages Sent: $SENT"
echo "Messages Failed: $FAILED"
echo "Messages Retried: $RETRIED"

if [ $GENERATED -gt 0 ]; then
    SUCCESS_RATE=$(echo "scale=2; $SENT * 100 / $GENERATED" | bc)
    echo "Success Rate: $SUCCESS_RATE%"
fi

echo ""
echo "=== Common Errors ==="
grep "❌" $LOG_FILE | grep -o "error.*" | sort | uniq -c | sort -rn | head -5
```

### **Real-Time Monitoring**
```bash
# Watch for failures in real-time
tail -f flir_bot.log | grep --line-buffered "❌"

# Watch for successful sends
tail -f flir_bot.log | grep --line-buffered "✅"

# Watch specific character
tail -f flir_bot.log | grep --line-buffered "Alex"
```

---

## 🎯 **Health Check Indicators**

### **Green (Healthy)**
- Message success rate > 99%
- Average retry count < 0.1
- No critical errors in last hour
- All API connections working

### **Yellow (Degraded)**
- Message success rate 95-99%
- Average retry count 0.1-0.5
- Occasional API timeouts
- Users receiving retry notifications

### **Red (Critical)**
- Message success rate < 95%
- Average retry count > 0.5
- Multiple API failures
- Users reporting missing messages

---

## 🔬 **Advanced Debugging**

### **Enable Debug Mode**
```env
# In .env
DEBUG_MODE=True
```

### **Increase Log Verbosity**
```python
# In discord_bot.py
logging.basicConfig(level=logging.DEBUG)
```

### **Test Specific Character**
```python
# In Discord
!test-message
!talk Alex
[Send test message]
```

### **Check Session State**
```python
# In Discord
!status
!history
```

---

## 📚 **Related Documentation**

- [MESSAGE_RELIABILITY_FIX.md](./MESSAGE_RELIABILITY_FIX.md) - Detailed fix documentation
- [CODE_DOCUMENTATION.md](./CODE_DOCUMENTATION.md) - Code structure overview
- [DEPLOYMENT.md](./DEPLOYMENT.md) - Deployment procedures

---

**Last Updated:** September 30, 2025  
**Version:** 1.0  
**Maintainer:** Development Team
