# Data Storage Refactor - Complete Summary

## ✅ What Was Changed

### 1. **Audio Fix** 🎵
Fixed the slow audio playback issue when clicking the sound banner on Session 1 scenario page.

**Before:**
- Audio would play slowly or with delay when clicking the sound prompt banner
- Didn't check if audio was ready or reset playback rate

**After:**
- Ensures `playbackRate = 1.0` for normal speed
- Checks audio `readyState` before playing
- Waits for `canplay` event if audio isn't ready
- Forces load if needed

### 2. **Consolidated Data Structure** 📁
Completely refactored data storage to save ONE JSON file per participant instead of multiple scattered files.

#### **Old Structure (Complex):**
```
survey_responses/
├── {participant-id}.json                    # Individual survey files
├── all_responses.jsonl                      # Master survey JSONL
├── post_surveys/
│   ├── post_{session_id}.json              # Individual post-survey files
│   └── all_post_surveys.jsonl              # Master post-survey JSONL
├── conversations/
│   ├── {session_id}.json                   # Individual conversation files
│   └── all_conversations.jsonl             # Master conversation JSONL
├── completed/
│   └── CCC001.json                         # Only had survey + post-surveys
└── exits/
    └── INC001.json                         # Only had survey data
```

#### **New Structure (Simple):**
```
survey_responses/
├── completed/
│   └── CCC001.json                         # Has: survey + conversations + post-surveys
├── exits/
│   └── INC001.json                         # Has: survey + conversations + post-surveys
└── confirmation_numbers.json               # Tracking INC/CCC numbers
```

## 🔄 How It Works Now

### **Data Flow:**

1. **Survey Submission (`/api/survey`)**
   - Stores survey in memory: `participant_data[participant_id]`
   - Returns `participant_id`
   - **No file created**

2. **Post-Survey Submission (`/api/post-survey`)**
   - Stores in memory: `participant_data[participant_id]["post_surveys"]`
   - **No file created**

3. **Conversations**
   - All conversation data stays in `conversation_sessions` dictionary
   - IQL data (policies, Q-values, judgments) stored in `session["iql_data"]`
   - **No files created during conversation**

4. **Exit Study (`/api/exit-study`)**
   - Gathers ALL data from memory:
     - Survey from `participant_data`
     - Post-surveys from `participant_data`
     - Conversations from `conversation_sessions` (with IQL data)
   - Saves everything to ONE file: `exits/INC###.json`
   - Cleans up memory

5. **Complete Study (`/api/complete-study`)**
   - Gathers ALL data from memory:
     - Survey from `participant_data`
     - All 6 post-surveys from `participant_data`
     - All 6 conversations from `conversation_sessions` (with IQL data)
   - Saves everything to ONE file: `completed/CCC###.json`
   - Cleans up memory

## 📊 File Structure Examples

### **Completed Study File (CCC###.json):**
```json
{
  "confirmation_number": "CCC001",
  "participant_id": "abc-123-def-456",
  "status": "complete",
  "completion_timestamp": "2025-12-24T10:30:00",
  "survey": {
    "background": {...},
    "personality": {...},
    "moral": {...},
    "specialNeeds": {...}
  },
  "conversations": [
    {
      "session_id": "abc-123_nonrole_rational-informational_1234567890",
      "conversation_type": "non-roleplay",
      "persuasion_strategy": "rational-informational",
      "history": [...],
      "iql_data": [],  // Empty for non-role-play
      "turn_count": 5,
      "created_at": "2025-12-24T10:15:00",
      "ended_at": "2025-12-24T10:18:00"
    },
    {
      "session_id": "abc-123_niki_1234567891",
      "conversation_type": "roleplay",
      "character": "niki",
      "history": [...],
      "iql_data": [  // Full IQL tracking for role-play
        {
          "turn": 1,
          "resident_message": "What should I do?",
          "operator_response": "Please evacuate...",
          "selected_policy": "express_urgency",
          "q_values": {
            "express_urgency": 0.92,
            "provide_information": 0.78,
            "give_direction": 0.65
          },
          "judge": {
            "stance": "NEUTRAL",
            "confidence": 0.70
          }
        }
      ],
      "turn_count": 8
    }
    // ... all 6 conversations
  ],
  "post_surveys": [
    {
      "conversationNumber": 1,
      "willing": "yes",
      "naturalness": "very-natural"
    }
    // ... all 6 post-surveys
  ]
}
```

### **Exit File (INC###.json):**
Same structure as above, but with:
- `"status": "incomplete"`
- `"exit_page"`: Where they exited
- Partial conversations and post-surveys (whatever was completed)

## 🎯 Benefits

1. **Cleaner Data**: One file per participant - easy to find everything
2. **Complete Picture**: All conversations with IQL data in one place
3. **Easy Analysis**: Load ONE file to analyze a participant's entire journey
4. **No Data Loss**: Everything in memory until explicitly saved
5. **Simpler Backup**: Just backup `completed/` and `exits/` folders

## 🔧 Code Changes Summary

### **Backend (`server.py`):**
1. Added `participant_data = {}` dictionary for in-memory storage
2. Modified `/api/survey` - stores in memory only
3. Modified `/api/post-survey` - stores in memory only
4. Removed `save_conversation_history()` function
5. Removed individual file saves from conversation endings
6. Updated `/api/exit-study` - gathers all data from memory
7. Updated `/api/complete-study` - gathers all data from memory
8. Updated `/api/survey/{id}` - reads from memory
9. Updated `/api/admin/stats` - new statistics
10. Removed `/api/admin/save-active-sessions` endpoint

### **Frontend (`admin.html`):**
1. Removed "💾 Save Active Sessions" button
2. Updated statistics display:
   - "Total Participants"
   - "Complete Studies (CCC)"
   - "Incomplete Exits (INC)"
   - "Active Participants (in memory)"
   - "Active Sessions (conversations)"
3. Removed `saveActiveSessions()` function
4. Updated `displayStats()` function

### **Frontend (`scenario.js`):**
1. Fixed `enableSound()` function to properly handle audio playback

## 🧪 How to Test

### **Step 1: Restart the Server**
```bash
cd /Users/tzhang/projects/a2i2_survey/a2i2_chatbot/backend
# Stop the current server (Ctrl+C in Terminal 1)
python server.py
```

### **Step 2: Complete a Full Study**
1. Open `http://localhost:8000/survey.html`
2. Complete the survey
3. Complete all 6 conversations
4. Complete all 6 post-surveys
5. Get CCC confirmation number

### **Step 3: Verify the Data**
```bash
# Check the completed file
cat /Users/tzhang/projects/a2i2_survey/a2i2_chatbot/survey_responses/completed/CCC002.json
```

You should see ONE file with:
- ✅ Survey data
- ✅ All 6 conversations (with IQL data for role-play)
- ✅ All 6 post-surveys
- ✅ Confirmation number

### **Step 4: Test Early Exit**
1. Start a new survey
2. Exit midway (click Exit Study button)
3. Get INC confirmation number
4. Check the exits folder

```bash
cat /Users/tzhang/projects/a2i2_survey/a2i2_chatbot/survey_responses/exits/INC00X.json
```

Should contain whatever data was completed before exit.

### **Step 5: Test Admin Panel**
1. Open `http://localhost:8000/admin.html`
2. Login with admin key: `your-secret-admin-key-here`
3. Check statistics:
   - Total Participants
   - Completed Studies
   - Incomplete Exits
   - Active Participants
   - Active Sessions

## ⚠️ Important Notes

1. **Data in Memory**: Participant data stays in memory until exit or completion
2. **Server Restart**: If server crashes, active participants lose data (need to restart)
3. **Production**: For production, consider using Redis or database instead of in-memory dictionaries
4. **Backup**: The old scattered files still exist - you can manually delete them after verifying the new system works

## 🗑️ Optional: Cleanup Old Files

After verifying the new system works, you can clean up old files:

```bash
cd /Users/tzhang/projects/a2i2_survey/a2i2_chatbot/survey_responses

# Remove old structure (BE CAREFUL - make backup first!)
rm -f *.json  # Individual survey files
rm -f all_responses.jsonl
rm -rf post_surveys/
rm -rf conversations/
```

Keep:
- ✅ `completed/` folder
- ✅ `exits/` folder
- ✅ `confirmation_numbers.json`

## 📝 Data Analysis

Now you can analyze participant data easily:

```python
import json

# Load a completed study
with open('survey_responses/completed/CCC001.json', 'r') as f:
    participant = json.load(f)

# Access everything
survey = participant['survey']
conversations = participant['conversations']  # All 6
post_surveys = participant['post_surveys']    # All 6

# Analyze IQL data for role-play conversations
for conv in conversations:
    if conv['conversation_type'] == 'roleplay':
        for turn in conv['iql_data']:
            policy = turn['selected_policy']
            q_values = turn['q_values']
            print(f"Turn {turn['turn']}: Used {policy} (Q={q_values[policy]:.2f})")
```

## ✨ Summary

**Before**: 3+ directories, 10+ files per participant, scattered data
**After**: 2 directories, 1 file per participant, all data in one place

**Result**: Cleaner, simpler, more maintainable! 🎉

