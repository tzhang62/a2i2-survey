# 💾 How to Save Your Conversation Data

## ✅ **QUICK SAVE** - Run This Command:

```bash
cd /Users/tzhang/projects/a2i2_survey
python extract_conversation_data.py
```

**That's it!** Your data is saved to:
```
conversation_data_exports/conversations_YYYYMMDD_HHMMSS.json
```

---

## 📊 What Gets Saved

Each JSON file contains:

```json
{
  "export_timestamp": "2026-01-09T05:58:37",
  "total_conversations": 1,
  "conversations": [
    {
      "session_id": "participant_id_character_timestamp",
      "character": "mia",
      "turns": [
        {
          "turn": 1,
          "resident_message": "yes I am safe",
          "policy": "michelle",           ← IQL selected policy
          "q_values": {                   ← All policy scores
            "bob": 1.123,
            "lindsay": 1.131,
            "michelle": 1.134,            ← Highest = selected
            "niki": 1.133,
            "ross": 1.131
          },
          "operator_response": "It's good to hear you're safe..."
        }
      ]
    }
  ]
}
```

---

## 📁 All Your Data Files

### 1. **Real-Time Logs** (Development Testing)
**Location**: `conversation_data_exports/conversations_*.json`  
**How to create**: `python extract_conversation_data.py`  
**Contains**: Policy selections, Q-values, messages from Terminal 7 logs

### 2. **Q-Values Log** (Turn-by-Turn)
**Location**: `a2i2_chatbot/backend/q_values_log.jsonl`  
**Auto-created**: Every time someone chats  
**Format**: One JSON object per line (JSONL)

### 3. **Completed Studies** (Production)
**Location**: `survey_responses/completed/CCC###.json`  
**Auto-created**: When participant clicks "Complete Study"  
**Contains**: Everything (survey + 3 conversations + feedback + IQL data)

### 4. **Early Exits** (Production)
**Location**: `survey_responses/exits/INC###.json`  
**Auto-created**: When participant clicks "Exit Study"  
**Contains**: Partial data (whatever was completed before exit)

### 5. **Backend Logs** (Raw Terminal Output)
**Location**: Save with this command:
```bash
tail -200 /Users/tzhang/.cursor/projects/Users-tzhang-projects-a2i2-survey/terminals/7.txt > my_logs.txt
```

---

## 🔍 Where to Find Terminal 7

**Terminal 7 is at the bottom of your Cursor window!**

1. Look at the bottom panel
2. Click the "TERMINAL 7" tab
3. Or press `` Ctrl+` `` to toggle terminal panel
4. You'll see logs like:
   ```
   [IQL-HF] Selected policy: michelle
   [IQL-HF] Q-values: {'bob': 1.123, 'lindsay': 1.131, ...}
   ```

---

## 🚀 Quick Commands

### Save Conversation Data (Recommended)
```bash
cd /Users/tzhang/projects/a2i2_survey
python extract_conversation_data.py
```

### Save Backend Logs to File
```bash
cd /Users/tzhang/projects/a2i2_survey
tail -200 /Users/tzhang/.cursor/projects/Users-tzhang-projects-a2i2-survey/terminals/7.txt > backend_logs_$(date +%Y%m%d_%H%M%S).txt
```

### Search for Policy Selections
```bash
grep "Selected policy:" /Users/tzhang/.cursor/projects/Users-tzhang-projects-a2i2-survey/terminals/7.txt
```

### Search for Q-Values
```bash
grep "Q-values:" /Users/tzhang/.cursor/projects/Users-tzhang-projects-a2i2-survey/terminals/7.txt
```

### Watch Logs in Real-Time
```bash
tail -f /Users/tzhang/.cursor/projects/Users-tzhang-projects-a2i2-survey/terminals/7.txt
```
(Press `Ctrl+C` to stop)

---

## 📊 Example: What You Just Saved

**File**: `conversation_data_exports/conversations_20260108_215837.json`

- ✅ 1 conversation extracted
- ✅ Character: mia
- ✅ 1 turn of dialogue
- ✅ Policy selected: michelle
- ✅ Q-values for all 5 policies
- ✅ Full resident message and operator response

---

## 💡 Pro Tips

1. **Run extraction after each test** to save your data
2. **Terminal 7 shows real-time logs** - watch it while testing
3. **JSON files are easy to analyze** - use Python, R, or Excel
4. **q_values_log.jsonl** is automatically updated with every chat message
5. **When study completes**, all data auto-saves to `survey_responses/`

---

## ✅ You're All Set!

Your data is automatically being:
- ✅ Logged in Terminal 7
- ✅ Saved to `q_values_log.jsonl`
- ✅ Ready to export with `python extract_conversation_data.py`
- ✅ Auto-saved when participants complete the study

**Just run the extraction script whenever you want a clean JSON export!** 🎉

