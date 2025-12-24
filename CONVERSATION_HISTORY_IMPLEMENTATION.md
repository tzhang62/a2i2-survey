# Conversation History Saving - Implementation Summary

## ✅ What Has Been Implemented

### 1. **Automatic Conversation History Saving**
- All conversations are now saved to disk when they end
- Saved in `/survey_responses/conversations/` directory
- Each conversation gets its own JSON file: `{session_id}.json`
- All conversations also appended to `all_conversations.jsonl`

### 2. **IQL Policy Data Recording (Session 2 Only)**
For role-play conversations, the system now records:
- **Selected policy** for each turn
- **Q-values** for all policies (showing why that policy was chosen)
- **Resident message** and **operator response**
- **Judge assessment** (stance, confidence, reasoning)
- **Timestamp** for each turn

### 3. **Complete Study Export Enhancement**
When a participant completes all 6 conversations:
- The `CCC###.json` file now includes all conversation histories
- Provides a complete record: survey + post-surveys + conversation transcripts

### 4. **Admin Tools**
- **New "💾 Save Active Sessions" button** in admin panel
- Saves any in-memory conversations to disk (useful before server restarts)
- **New statistic**: "Conversations Saved (with IQL data)"

## 📁 File Structure

```
survey_responses/
├── conversations/                    # ← NEW!
│   ├── {session_id}.json            # Individual conversation files
│   └── all_conversations.jsonl      # Master file (one JSON per line)
├── completed/
│   └── CCC001.json                  # Now includes conversation histories!
├── exits/
├── post_surveys/
└── {participant-id}.json
```

## 🔧 Changes Made to Code

### `server.py`
1. **New function: `save_conversation_history(session_id, session)`**
   - Saves conversation to individual JSON file
   - Appends to master JSONL file
   - Called automatically when conversations end

2. **Updated: `get_session()`**
   - Added `iql_data` field to session storage

3. **Updated: `send_message()` endpoint**
   - Records IQL policy selection data for role-play conversations
   - Stores: turn, messages, selected_policy, q_values, judge, timestamp

4. **Updated: Conversation ending logic**
   - Calls `save_conversation_history()` before returning
   - Applied to all 3 ending conditions: max_turns, agreement, refusal

5. **Updated: `complete_study()` endpoint**
   - Now includes all conversation histories in final CCC file

6. **Updated: `get_stats()` endpoint**
   - Added `conversations_saved` count

7. **New endpoint: `POST /api/admin/save-active-sessions`**
   - Manually saves all in-memory sessions to disk
   - Useful for development/testing

### `admin.html`
1. **New button**: "💾 Save Active Sessions"
2. **New statistic display**: "Conversations Saved (with IQL data)"
3. **New function**: `saveActiveSessions()` - calls the new API endpoint

## 📊 Example Data Structure

### Session 1 (Non-Role-Play) - No IQL Data
```json
{
  "session_id": "abc123_nonrole_rational-informational_1234567890",
  "participant_id": "abc123",
  "character": null,
  "conversation_type": "non-roleplay",
  "persuasion_strategy": "rational-informational",
  "turn_count": 5,
  "history": [
    {"role": "operator", "text": "Hello, this is the fire department..."},
    {"role": "resident", "text": "What should I do?"}
  ],
  "iql_data": [],  // Empty for non-role-play
  "created_at": "2025-12-24T00:32:45.123456",
  "ended_at": "2025-12-24T00:35:12.456789"
}
```

### Session 2 (Role-Play) - WITH IQL Data
```json
{
  "session_id": "abc123_niki_1234567890",
  "participant_id": "abc123",
  "character": "niki",
  "conversation_type": "roleplay",
  "persuasion_strategy": null,
  "turn_count": 8,
  "history": [
    {"role": "operator", "text": "Hello..."},
    {"role": "resident", "text": "Hi..."}
  ],
  "iql_data": [
    {
      "turn": 1,
      "resident_message": "Hi, what's happening?",
      "operator_response": "There's a wildfire approaching...",
      "selected_policy": "provide_information",
      "q_values": {
        "provide_information": 0.85,
        "offer_assistance": 0.72,
        "express_urgency": 0.65,
        "ask_question": 0.58,
        "give_direction": 0.45
      },
      "judge": {
        "stance": "NEUTRAL",
        "confidence": 0.65,
        "reasoning": "Resident is seeking information..."
      },
      "timestamp": "2025-12-24T00:32:50.123456"
    }
    // ... more turns
  ],
  "created_at": "2025-12-24T00:32:45.123456",
  "ended_at": "2025-12-24T00:35:30.456789"
}
```

## 🧪 How to Test

### Step 1: Restart the Server
The server needs to be restarted to load the new code:

```bash
# Terminal 1 - Stop old server and start new one
cd /Users/tzhang/projects/a2i2_survey/a2i2_chatbot/backend
# Press Ctrl+C to stop the current server
python server.py
```

### Step 2: Complete a Test Conversation
1. Open the survey in your browser: `http://localhost:8000/survey.html`
2. Complete the survey
3. Go through at least one conversation to completion
4. Check for the new directory:

```bash
ls -la /Users/tzhang/projects/a2i2_survey/a2i2_chatbot/survey_responses/conversations/
```

You should see:
- Individual conversation JSON files
- `all_conversations.jsonl` file

### Step 3: Test Admin Panel
1. Open `http://localhost:8000/admin.html`
2. Enter admin key: `your-secret-admin-key-here`
3. Click "💾 Save Active Sessions" button
4. Should show: "✅ Saved X active conversation session(s) to disk!"
5. Check the "Conversations Saved (with IQL data)" statistic

### Step 4: Verify Complete Study Export
1. Complete all 6 conversations for a participant
2. Check the `CCC###.json` file in `/survey_responses/completed/`
3. Look for the new `conversations` array
4. Each conversation should have full dialogue + IQL data (for Session 2)

## 📈 What You Can Analyze Now

### For Session 1 (Non-Role-Play)
- Compare effectiveness of 3 persuasion strategies:
  1. Rational-Informational
  2. Emotional-Relational
  3. Social-Normative
- Analyze natural language patterns
- Measure conversation length and outcomes

### For Session 2 (Role-Play with IQL)
- **Policy effectiveness**: Which IQL policies lead to agreement?
- **Q-value analysis**: How does the model value different policies?
- **Policy sequences**: What policy combinations work best?
- **Character differences**: Do different characters respond to different policies?
- **Turn-by-turn evolution**: How do Q-values change as conversation progresses?

### Cross-Session Analysis
- Role-play vs non-role-play outcomes
- Personality traits correlation with policy effectiveness
- Moral foundations influence on resistance patterns
- Special needs impact on conversation strategies

## 🎯 Key Benefits

1. **No Data Loss**: Conversations saved even if server crashes
2. **Research Transparency**: Full record of what the model "thought" (Q-values)
3. **Reproducibility**: Can recreate exact conversation flow
4. **Deep Analysis**: Understand why IQL chose specific policies
5. **Complete Record**: Survey + conversations + feedback in one file

## 📝 Next Steps

1. **Restart server** to activate the new code
2. **Run test conversations** to generate sample data
3. **Verify data structure** matches your research needs
4. **Adjust fields** if you need additional data captured
5. **Deploy to production** when satisfied with local testing

## 🔍 Monitoring Tips

- Check `conversations/` directory regularly
- Monitor "Conversations Saved" statistic in admin panel
- Use "Save Active Sessions" button before deploying updates
- Backup the entire `survey_responses/` directory periodically

## 📚 Additional Documentation

See `CONVERSATION_HISTORY_FORMAT.md` for detailed data format specifications and research use cases.

---

**Status**: ✅ Implementation complete, ready for testing
**Next Action**: Restart server and run test conversation

