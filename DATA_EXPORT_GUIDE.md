# Data Export Guide

## 📊 Where Your Data is Saved

Your system **automatically saves data** in several places:

### 1. **Completed Studies** (When Participant Finishes)
**Location**: `/survey_responses/completed/CCC###.json`

**Contains**:
- Survey responses
- All 3 conversations with full history
- IQL policy selections for each turn
- Q-values for each decision
- Post-survey feedback for each conversation
- Character selections
- Timestamps

**Saved when**: Participant clicks "Complete Study" at the end

### 2. **Early Exits** (When Participant Quits Early)
**Location**: `/survey_responses/exits/INC###.json`

**Contains**:
- Survey responses (if completed)
- Any conversations started (partial data)
- IQL data for completed turns
- Exit page and timestamp

**Saved when**: Participant clicks "Exit Study"

### 3. **Real-Time Q-Values Log** (Development)
**Location**: `/a2i2_chatbot/backend/q_values_log.jsonl`

**Contains**:
- Turn-by-turn policy selections
- Q-values for all policies
- Resident messages
- Judge stance predictions

**Format**: One JSON object per line (JSONL)

---

## 🔍 How to View Backend Logs (Policy Selections)

### Terminal 7 Shows Everything:

**Your Terminal 7 is already showing the logs!** Look at the bottom panel in Cursor:

```
[CHAT] Session: ..., Turn: 1, Resident: yes I am safe
[IQL-HF] Querying API for policy (character=mia)...
[IQL-HF] Selected policy: michelle          ← The policy chosen
[IQL-HF] Q-values: {                        ← All policy scores
  'bob': 1.123,
  'lindsay': 1.131,
  'michelle': 1.134,  ← Highest = selected
  'niki': 1.133,
  'ross': 1.131
}
[IQL] Selected policy: michelle (took 0.37s)
[RETRIEVAL] Got 2 examples (took 0.35s)
[OPENAI] Generated response (took 0.87s)
[CHAT] Operator: It's good to hear you're safe...
```

**Every time someone sends a message, you'll see these logs in Terminal 7!**

---

## 💾 How to Export Data

### Method 1: Export Active Sessions (While Testing)

Run this script to save current conversation data:

```bash
cd /Users/tzhang/projects/a2i2_survey/a2i2_chatbot/backend
python export_conversation_data.py
```

This creates:
```
exported_data/conversations_YYYYMMDD_HHMMSS.json
```

### Method 2: Wait for Study Completion (Production)

Data is automatically saved when participants:
- Complete the study → `survey_responses/completed/CCC###.json`
- Exit early → `survey_responses/exits/INC###.json`

### Method 3: Use Admin API (Advanced)

```bash
curl "http://localhost:8001/api/admin/export-sessions?admin_key=your-secret-admin-key-here"
```

---

## 📁 Data Structure Example

When saved, each conversation includes:

```json
{
  "session_id": "participant_id_character_timestamp",
  "character": "mia",
  "turn_count": 3,
  "history": [
    {"role": "operator", "text": "Hello, this is..."},
    {"role": "resident", "text": "yes I am safe"},
    ...
  ],
  "iql_data": [
    {
      "turn": 1,
      "resident_message": "yes I am safe",
      "operator_response": "You need to evacuate...",
      "selected_policy": "michelle",
      "q_values": {
        "bob": 1.123,
        "lindsay": 1.131,
        "michelle": 1.134,
        "niki": 1.133,
        "ross": 1.131
      },
      "judge": {
        "stance": "UNKNOWN",
        "confidence": 0.5,
        "reason": "..."
      },
      "timestamp": "2026-01-09T..."
    },
    ...
  ]
}
```

---

## 🚀 Quick Reference

### To See Logs in Real-Time:
**Look at Terminal 7** (bottom panel in Cursor) while someone chats

### To Export Current Data:
```bash
cd /Users/tzhang/projects/a2i2_survey/a2i2_chatbot/backend
python export_conversation_data.py
```

### To View Terminal 7 in Cursor:
1. Look at bottom panel
2. Click "TERMINAL 7" tab
3. Or press `` Ctrl+` `` to open terminal panel

### To Save Terminal 7 Output to File:
In a new terminal:
```bash
tail -100 /Users/tzhang/.cursor/projects/Users-tzhang-projects-a2i2-survey/terminals/7.txt > my_backend_logs.txt
```

---

## 📊 Data Files You Can Analyze

After running tests:

1. **q_values_log.jsonl** - Turn-by-turn IQL decisions
2. **exported_data/conversations_*.json** - Full conversation exports
3. **survey_responses/completed/*.json** - Completed studies
4. **survey_responses/exits/*.json** - Early exits

All include policy selections, Q-values, and conversation history! ✅

---

**Your Terminal 7 IS showing all the data you need - it's the terminal tab at the bottom of your Cursor window!** 👀

