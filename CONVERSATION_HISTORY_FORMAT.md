# Conversation History Data Format

## Overview
Conversation histories are now automatically saved to disk when a conversation ends (agreement, refusal, or max turns reached). This ensures all dialogue data, including IQL policy decisions for role-play conversations, is preserved.

## File Locations

### Individual Conversation Files
**Path:** `/survey_responses/conversations/{session_id}.json`

Each conversation is saved as a separate JSON file named by its session ID.

### Master JSONL File
**Path:** `/survey_responses/conversations/all_conversations.jsonl`

All conversations are also appended to a master JSONL file (one JSON object per line) for easy batch processing.

## Data Structure

### For Non-Role-Play Conversations (Session 1)
```json
{
  "session_id": "participant-id_nonrole_rational-informational_1234567890",
  "participant_id": "1c15a853-e96e-486c-9ba6-744d72d4b71d",
  "character": null,
  "conversation_type": "non-roleplay",
  "persuasion_strategy": "rational-informational",
  "turn_count": 5,
  "history": [
    {
      "role": "operator",
      "text": "Hello, this is the fire department. There's a wildfire near your area..."
    },
    {
      "role": "resident",
      "text": "Oh no, what should I do?"
    },
    {
      "role": "operator",
      "text": "I recommend evacuating immediately. The fire is spreading quickly..."
    }
  ],
  "iql_data": [],
  "created_at": "2025-12-24T00:32:45.123456",
  "ended_at": "2025-12-24T00:35:12.456789",
  "scenario": "A wildfire is spreading rapidly through neighborhoods near your area..."
}
```

### For Role-Play Conversations (Session 2) - WITH IQL DATA
```json
{
  "session_id": "participant-id_niki_1234567890",
  "participant_id": "1c15a853-e96e-486c-9ba6-744d72d4b71d",
  "character": "niki",
  "conversation_type": "roleplay",
  "persuasion_strategy": null,
  "turn_count": 8,
  "history": [
    {
      "role": "operator",
      "text": "Hello, this is the fire department dispatcher..."
    },
    {
      "role": "resident",
      "text": "Hi, yes I can hear you. What's happening?"
    },
    {
      "role": "operator",
      "text": "There's a wildfire approaching your area. Can you evacuate?"
    }
  ],
  "iql_data": [
    {
      "turn": 1,
      "resident_message": "Hi, yes I can hear you. What's happening?",
      "operator_response": "There's a wildfire approaching your area. Can you evacuate?",
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
    },
    {
      "turn": 2,
      "resident_message": "I can leave but I need to know which direction is safe",
      "operator_response": "Head west on Main Street. That route is clear.",
      "selected_policy": "give_direction",
      "q_values": {
        "give_direction": 0.92,
        "provide_information": 0.78,
        "offer_assistance": 0.65,
        "express_urgency": 0.55,
        "ask_question": 0.42
      },
      "judge": {
        "stance": "AGREE",
        "confidence": 0.80,
        "reasoning": "Resident is willing to evacuate and seeking guidance..."
      },
      "timestamp": "2025-12-24T00:33:15.234567"
    }
  ],
  "created_at": "2025-12-24T00:32:45.123456",
  "ended_at": "2025-12-24T00:35:30.456789",
  "scenario": "It is a regular day at home. You (Niki) are with your elderly parents..."
}
```

## IQL Data Explanation

### Fields in `iql_data` array:
- **`turn`**: The conversation turn number (resident utterance count)
- **`resident_message`**: What the participant said
- **`operator_response`**: What the AI operator responded with
- **`selected_policy`**: Which IQL policy was chosen (highest Q-value)
- **`q_values`**: Dictionary of all policies and their Q-values
  - Higher Q-value = model believes this policy is more likely to succeed
  - The policy with the highest Q-value is selected
- **`judge`**: The stance classifier's assessment
  - `stance`: AGREE, REFUSE, or NEUTRAL
  - `confidence`: How confident the classifier is (0-1)
  - `reasoning`: Explanation for the classification
- **`timestamp`**: When this turn occurred

### Available IQL Policies:
1. `provide_information` - Share facts, data, risk levels
2. `offer_assistance` - Provide help, resources, support
3. `express_urgency` - Convey time pressure, danger
4. `ask_question` - Gather information from resident
5. `give_direction` - Provide specific instructions
6. `acknowledge_concern` - Validate resident's feelings
7. `build_rapport` - Establish trust and connection

## When Conversations Are Saved

Conversations are automatically saved to disk when they end due to:
1. **Agreement** - Resident agrees to evacuation (AGREE stance, confidence ≥ 0.70)
2. **Refusal** - Repeated refusals (2 consecutive REFUSE stances)
3. **Max Turns** - Conversation reaches 15 turns

## Usage in Complete Study Export

When a participant completes the entire study (all 6 conversations), the `/api/complete-study` endpoint creates a comprehensive `CCC###.json` file in `/survey_responses/completed/` that includes:

1. **Survey responses** - Demographics, personality, moral foundations, special needs
2. **Post-surveys** - Willingness to be rescued, conversation naturalness feedback
3. **Conversation histories** - All 6 conversation transcripts with IQL data

This provides a complete record of each participant's journey through the study.

## Admin Tools

### Save Active Sessions Button
The admin panel now includes a "💾 Save Active Sessions" button that saves all currently in-memory conversation sessions to disk. This is useful for:
- Saving test data before server restarts
- Creating backups of ongoing conversations
- Development and debugging

### Viewing Statistics
The admin panel displays:
- **Conversations Completed**: Number of post-surveys submitted
- **Conversations Saved (with IQL data)**: Number of conversation history files saved to disk

## Data Analysis

Researchers can use the conversation history data to:
1. **Analyze IQL policy effectiveness** - Which policies led to agreement vs refusal?
2. **Study conversation patterns** - How do different persuasion strategies perform?
3. **Compare role-play vs non-role-play** - Do personalized characters affect outcomes?
4. **Evaluate dialogue quality** - Review natural language transcripts
5. **Understand decision-making** - Track how Q-values change over turns
6. **Correlate with demographics** - Link conversation outcomes to personality traits, moral values, etc.

## Example Research Questions

With this data, you can answer:
- Which IQL policy is most effective for different character types?
- How do Q-values evolve as the conversation progresses?
- Does the model's policy selection align with successful outcomes?
- How do persuasion strategies (rational vs emotional vs social) compare?
- Do participants with higher "openness" traits respond better to certain policies?
- Is there a correlation between moral foundations and resistance to evacuation?

