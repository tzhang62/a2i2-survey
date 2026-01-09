# 📊 Enhanced Backend Logging Guide

## ✨ New Features

Your backend server now prints **all responses and policy selections** in a clear, organized format!

---

## 🟢 When a Conversation Starts

You'll see:

```
🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢
🚀 NEW CONVERSATION STARTED
🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢
   Session ID: participant_id_mia_1767937624
   Character: MIA
   Participant: 9946ab97-9bca-4772-a4b7-f1b8d2d06b2f

💬 INITIAL GREETING:
   Hi, this is fire department dispatch. We're monitoring a nearby wildfire...
🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢
```

---

## 🔵 For Each Turn

You'll see a complete breakdown:

```
================================================================================
🔵 TURN 1 | Session: 06b2f
================================================================================
👤 RESIDENT: yes I am safe
--------------------------------------------------------------------------------

🤖 IQL POLICY SELECTION:
   ⭐ Selected: MICHELLE (took 0.37s)
   📊 Q-Values:
      → michelle  : 1.1345
        niki      : 1.1337
        lindsay   : 1.1311
        ross      : 1.1310
        bob       : 1.1231

🎯 JUDGE PREDICTION:
   Stance: UNKNOWN (confidence: 0.50)
   Reason: The resident expresses feeling safe but does not provide information...

💬 OPERATOR RESPONSE (via gpt-4o-mini, 0.87s):
   It's good to hear you're safe, but you need to evacuate immediately. 
   Gather essential items and leave now. Your safety is the priority.
================================================================================
```

---

## ✅ When Resident Agrees to Evacuate

```
✅ CONVERSATION ENDING: Resident agreed to evacuate!
💬 CLOSING MESSAGE: Great! Please leave immediately and stay safe.
================================================================================
```

---

## 🚫 When Resident Repeatedly Refuses

```
🚫 CONVERSATION ENDING: Repeated refusals detected
💬 CLOSING MESSAGE: I understand your concerns. Please reconsider for your safety.
================================================================================
```

---

## 🔴 When Max Turns Reached

```
🔴 CONVERSATION ENDING: Max turns reached (15)
💬 CLOSING MESSAGE: I've shared all the critical information. Please evacuate.
================================================================================
```

---

## 📊 What You Can See Now

Every turn shows:

1. **Turn Number & Session ID** (last 5 chars for readability)
2. **Resident Message** - What the participant typed
3. **IQL Policy Selection**:
   - Which policy was selected
   - How long it took
   - Q-values for ALL 5 policies (sorted by value)
   - Arrow (→) pointing to selected policy
4. **Judge Prediction**:
   - Predicted stance (AGREE/DELAY/REFUSE/UNKNOWN)
   - Confidence score
   - Reasoning
5. **Operator Response**:
   - Full generated text
   - Which model was used
   - Generation time

---

## 🔍 Where to View This

**Look at Terminal 9** in Cursor (bottom panel)!

Or save logs to file:
```bash
tail -f /Users/tzhang/.cursor/projects/Users-tzhang-projects-a2i2-survey/terminals/9.txt
```

---

## 💾 Bonus: Extract to JSON

All this data is also being saved! Extract it anytime:

```bash
cd /Users/tzhang/projects/a2i2_survey
python extract_conversation_data.py
```

This creates a clean JSON file with all policy selections and Q-values! 📁

---

## 🎨 Why This is Better

**Before:**
```
[CHAT] Session: abc123..., Turn: 1, Resident: yes I am safe
[IQL-HF] Selected policy: michelle
[IQL-HF] Q-values: {'bob': 1.123, 'lindsay': 1.131, ...}
[CHAT] Operator: It's good to hear...
```

**Now:**
- ✅ Clear visual separation between turns
- ✅ All Q-values visible and sorted
- ✅ Judge predictions included
- ✅ Timing information
- ✅ Easy to scan with emojis and formatting
- ✅ Session ID truncated for readability

---

## 🚀 Ready to Test

1. Open http://localhost:8000
2. Complete survey
3. Select a character
4. Start chatting
5. **Watch Terminal 9** - you'll see beautiful, detailed logs! 🎉

Every message you send will trigger a complete breakdown of:
- What the resident said
- Which policy IQL selected (with all Q-values)
- What the judge predicted
- What the operator responded

**All in real-time!** ⚡

