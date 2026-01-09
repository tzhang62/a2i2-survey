# Character Matching System - Implementation Summary

## Overview
The system has been updated to:
1. **Remove** the first session (non-role-play conversation with persuasion strategies)
2. **Keep only** role-play conversations with character matching
3. **Add profile matching** before each role-play conversation
4. **Track selected characters** to prevent reuse across conversations

## Key Changes

### 1. Character Similarity Scoring (`calculate_character_similarity`)
Calculates a similarity score (0-1) between participant survey data and each character profile based on:
- **Age similarity** (weight: 2.0) - Normalized age difference
- **Occupation similarity** (weight: 1.5) - Direct, partial, or keyword matching
- **Responsibility for others** (weight: 1.5) - Caring for children, elderly, or pets
- **Mobility/communication needs** (weight: 1.0) - Special conditions
- **Vehicle needs** (weight: 1.0) - Transportation requirements

### 2. Character Profile System (`CHARACTER_PROFILES`)
Added detailed profiles for 10 characters:
- Bob (30, office worker, work-focused)
- Ben (29, computer technician, home-based)
- Mary (75, retired, elderly with pet)
- Lindsay (25, babysitter, responsible for children)
- Ana (35, caregiver, senior center worker)
- Ross (45, van driver, helps evacuate residents)
- Niki (32, homemaker, cooperative)
- Michelle (40, homeowner, skeptical)
- Tom (38, high school teacher, project-focused)
- Mia (17, high school student, robotics)

Each profile includes:
- Name, age, occupation
- Personality traits
- Key concerns
- Description

### 3. New API Endpoints

#### `/api/character-selection` (POST)
**Purpose**: Get two characters for profile matching

**Request**:
```json
{
  "participantId": "string"
}
```

**Response**:
```json
{
  "success": true,
  "characters": [
    {
      "key": "bob",
      "name": "Bob",
      "age": 30,
      "occupation": "office worker",
      "description": "Bob is around 30 years old. He prioritizes his work over safety.",
      "similarity_score": 0.85,
      "match_type": "high"
    },
    {
      "key": "mary",
      "name": "Mary",
      "age": 75,
      "occupation": "retired",
      "description": "Mary is an elderly person living alone with a small dog.",
      "similarity_score": 0.23,
      "match_type": "low"
    }
  ]
}
```

**Logic**:
- Excludes already-selected characters
- Returns character with **highest** similarity score (best match)
- Returns character with **lowest** similarity score (worst match)
- Includes similarity scores and match type for transparency

#### `/api/character-confirm` (POST)
**Purpose**: Confirm character selection and mark as used

**Request**:
```json
{
  "participantId": "string",
  "selectedCharacter": "bob"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Character bob confirmed",
  "selected_characters": ["bob"]
}
```

**Logic**:
- Adds selected character to participant's `selected_characters` list
- Prevents character from appearing in future selections
- Tracks all selections per participant

### 4. Updated `/api/chat/start` Endpoint
**Simplified to role-play only**:
- Removed persuasion strategy logic
- Removed non-role-play conversation handling
- Now requires both `character` and `participantId`
- Only creates role-play sessions

### 5. Updated `/api/chat/message` Endpoint
**Simplified to IQL-based responses only**:
- Removed persuasion strategy branching
- All conversations now use IQL policy selection
- All responses use policy retrieval and examples

### 6. Participant Data Tracking
Enhanced `participant_data` structure:
```python
{
  "participant_id": {
    "survey": {...},
    "post_surveys": [...],
    "selected_characters": ["bob", "lindsay", ...]  # NEW
  }
}
```

## Workflow for Frontend Integration

### Complete Study Flow:
```
1. Participant completes survey
   └─> POST /api/survey

2. FOR EACH CONVERSATION (repeat 3 times):
   
   a. Get character pair for matching
      └─> POST /api/character-selection
      
   b. Show profile matching page
      - Display both characters (high match vs low match)
      - Participant chooses one
      
   c. Confirm selection
      └─> POST /api/character-confirm
      
   d. Start conversation
      └─> POST /api/chat/start
      
   e. Conduct conversation
      └─> POST /api/chat/message (multiple times)
      
   f. Submit post-conversation survey
      └─> POST /api/post-survey

3. Complete study
   └─> POST /api/complete-study
```

## Removed Features
- ❌ Non-role-play conversations
- ❌ Persuasion strategies (rational-informational, emotional-relational, social-normative)
- ❌ `PERSUASION_STRATEGIES` constant
- ❌ Persuasion strategy branching in `build_prompt()`
- ❌ Non-role-play session creation

## Preserved Features
- ✅ IQL policy selection
- ✅ Policy retrieval and examples
- ✅ Dynamic greeting generation
- ✅ Stance judging (agree/refuse/delay)
- ✅ Conversation ending logic
- ✅ Survey and post-survey storage
- ✅ Email notifications
- ✅ Confirmation number system (INC/CCC)

## Example Usage

### Getting Character Match:
```javascript
// Step 1: Get character options
const response = await fetch('/api/character-selection', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ participantId: 'abc-123' })
});

const data = await response.json();
// data.characters[0] = high similarity match
// data.characters[1] = low similarity match
```

### Confirming Selection:
```javascript
// Step 2: User selects a character
const selectedChar = 'bob'; // User's choice

await fetch('/api/character-confirm', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    participantId: 'abc-123',
    selectedCharacter: selectedChar
  })
});
```

### Starting Conversation:
```javascript
// Step 3: Start conversation with selected character
const chatResponse = await fetch('/api/chat/start', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    participantId: 'abc-123',
    character: selectedChar
  })
});

const chatData = await chatResponse.json();
// chatData.session_id - use for subsequent messages
// chatData.initial_message - operator's first message
```

## Testing Recommendations

1. **Test character selection with different survey profiles**:
   - Young student (should match Mia or Ben)
   - Elderly person (should match Mary)
   - Caregiver (should match Ana, Lindsay, or Ross)
   - Office worker (should match Bob or Tom)

2. **Test character exclusion**:
   - First conversation: Should offer all 10 characters
   - Second conversation: Should exclude 1st selected character
   - Third conversation: Should exclude 1st and 2nd selected characters

3. **Test edge cases**:
   - What happens after selecting all 10 characters?
   - Missing survey data handling
   - Invalid character selection

## Notes for Frontend Developer

1. **Profile Matching Page UI**:
   - Display both characters side-by-side
   - Show: name, age, occupation, description
   - **Do NOT** show similarity scores to participants (for research integrity)
   - Use clear "Select" buttons for each character

2. **Character Display Order**:
   - Option A: Always show high match on left, low match on right
   - Option B: Randomize left/right position (to avoid bias)
   - **Recommendation**: Randomize position

3. **Error Handling**:
   - Handle "Not enough characters available" error
   - Handle missing participant ID or survey data
   - Show friendly error messages

4. **Data Flow**:
   - Store `sessionId` returned from `/api/chat/start`
   - Use same `sessionId` for all messages in that conversation
   - Track conversation count (1st, 2nd, 3rd)

## Backend Compatibility

All changes are **backward compatible** with existing data structures:
- Existing conversation sessions continue to work
- Survey data format unchanged
- Post-survey format unchanged
- Confirmation number system unchanged

## Questions?

If you need any clarifications or modifications to the matching algorithm, scoring weights, or API responses, please let me know!

