# Complete Survey & IQL Chat System Guide

## Overview

This system implements a complete research study flow:
1. **Survey**: Participants answer questions about demographics, personality, and moral values
2. **Matching**: System matches participants with 1-2 character profiles using weighted similarity
3. **Role-Play Selection**: Participants choose a character to role-play as (or "None")
4. **IQL Chat**: Real-time conversation with an AI operator using Implicit Q-Learning

---

## System Architecture

### Backend (`a2i2_chatbot/backend/server.py`)
- **FastAPI** server with CORS and security middleware
- **Survey endpoints**: `/api/survey` (POST), `/api/survey/{id}` (GET)
- **IQL-based chat endpoints**: 
  - `/api/chat/start` - Initialize chat session
  - `/api/chat/message` - Send message and get operator response
  - `/api/chat/history/{session_id}` - Get conversation history
- **IQL Components**:
  - `QNetworkEmbed`: Neural network for policy selection
  - `IQLSelector`: Selects best operator policy based on conversation state
  - `PolicyExampleRetriever`: Retrieves similar examples for each policy
  - `judge_resident_stance`: Judges if resident agrees/refuses/delays evacuation

### Frontend Files

#### HTML Pages
- `landing.html` - Entry point with consent form
- `survey.html` - Multi-section survey form
- `scenario.html` - Character matching and selection
- `chat.html` - Real-time IQL chat interface

#### JavaScript
- `js/survey.js` - Survey logic, validation, submission
- `js/scenario.js` - **Character matching algorithm**, selection UI
- `js/chat.js` - Chat interface, IQL backend integration
- `config.js` - API configuration

#### CSS
- `styles/landing.css`
- `styles/survey.css`
- `styles/scenario.css`
- `styles/chat.css`

---

## Character Matching Algorithm

### Similarity Formula
The system uses a **weighted similarity calculation**:

```
Similarity = Age_Match (50%) + Occupation_Match (30%) + Special_Needs_Match (20%)
```

### Implementation (`js/scenario.js`)

Each character profile defines three matching functions:

1. **`ageMatch(age)`**: Returns 0-1 based on age fit
2. **`occupationMatch(occupation)`**: Returns 0-1 based on occupation keywords
3. **`specialNeedsMatch(needs)`**: Returns 0-1 based on special needs

### Character Profiles

| Character | Age Range | Occupation Keywords | Special Needs |
|-----------|-----------|---------------------|---------------|
| **Bob** | 25-35 | tech, computer, software | None |
| **Ben** | 27-32 | computer, IT, tech | Can evacuate independently |
| **Mary** | 65+ | retired, librarian | Needs vehicle, has pet |
| **Lindsay** | 20-30 | babysitter, childcare | Responsible for children |
| **Ana** | 35-50 | caregiver, nurse | Responsible for others + vehicle |
| **Ross** | 35-50 | driver, transport | Responsible for passengers |
| **Niki** | 25-45 | Any | None |
| **Michelle** | 40-60 | homeowner, property | None |
| **Tom** | 45-60 | teacher, education | May help others |
| **Mia** | 16-19 | student | None |

### Example Calculation

**Participant Profile:**
- Age: 67
- Occupation: "retired librarian"
- Special Needs: Vehicle required, has dog

**Mary's Score:**
```
Age Match:    67 >= 65 → 1.0 × 50% = 50%
Occupation:   "retired librarian" → 1.0 × 30% = 30%
Special Need: vehicle + pet → 0.9 × 20% = 18%
─────────────────────────────────────────
TOTAL SIMILARITY:                    98%
```

**Bob's Score:**
```
Age Match:    67 not in 25-35 → 0.1 × 50% = 5%
Occupation:   no tech keywords → 0.2 × 30% = 6%
Special Need: has needs → 0.3 × 20% = 6%
─────────────────────────────────────────
TOTAL SIMILARITY:                    17%
```

### Matching Rules
1. Calculate similarity for all 10 characters
2. Sort by similarity (highest first)
3. **Filter: Keep only matches > 50%**
4. **Return top 2 matches**
5. If no matches >50%, show "No matched characters found"

---

## IQL Chat System

### How IQL Works

1. **State Encoding**: Last 3 resident messages → sentence embeddings → mean vector
2. **Policy Selection**: Q-network predicts best policy for current state
3. **Example Retrieval**: Find 2 most similar operator-resident pairs for the selected policy
4. **LLM Generation**: OpenAI generates operator response using policy style + examples
5. **Stance Judgment**: LLM judges if resident agrees/refuses/delays evacuation

### Policies
IQL model trained on different operator strategies:
- `emphasize_danger` - Stress urgency and fire risk
- `emphasize_value_of_life` - Appeal to resident's safety
- `provide_information` - Give factual updates
- `offer_assistance` - Provide specific help
- `build_rapport` - Empathetic connection
- `logical_persuasion` - Rational arguments
- etc.

### Conversation Flow

1. **Operator greets resident**
2. For each resident turn (max 5):
   - Judge resident stance
   - If AGREE (conf ≥ 0.70) and turn ≥ 3 → **Success end**
   - If REFUSE (conf ≥ 0.85) twice and turn ≥ 3 → **Failure end**
   - IQL selects best policy
   - Retrieve examples
   - Generate operator response
3. If 5 turns reached → **Hard cap end**

---

## Complete User Flow

### 1. Landing Page
- Participant reads study info
- Checks consent checkbox
- Clicks "Start Survey"

### 2. Survey Page
- **Section 1: Background** (email, name, age, gender, education, occupation, ideology)
- **Section 2: Personality** (10 Big Five items, 5-point scale)
- **Section 3: Moral Foundations** (12 items, 6-point scale)
- **Section 4: Special Needs** (physical condition, responsible for others, vehicle needs)

**Validation:**
- All fields required
- Standard deviation > 0.8 per section
- No single value >80% per section
- Survey time > 1 minute

### 3. Scenario Page (Character Matching)
- System calculates similarity for all characters
- Displays top 2 matches (>50%) with similarity badges
- Shows "None" option
- **If user selects character:** Proceed to immersive scenario
- **If user selects "None":** End with thank you message

### 4. Immersive Scenario
- Displays character-specific scenario text
- Plays ambient fire sound + phone ringing (if media files present)
- Shows "📞 Answer the Call" button
- Clicking → Redirects to chat interface

### 5. Chat Interface
- Real-time conversation with IQL operator
- Shows turn counter (X / 5)
- Operator responses adapt based on:
  - Participant's messages
  - Selected character persona
  - Conversation history
  - IQL policy selection
- Conversation ends when:
  - Resident agrees to evacuate
  - Resident refuses twice
  - 5 turns reached

---

## Deployment

### Backend Requirements
```bash
pip install fastapi uvicorn pydantic torch sentence-transformers requests numpy
```

### Environment Variables
```bash
export OPENAI_API_KEY="your-openai-api-key"
export OPENAI_MODEL="gpt-4o-mini"  # or "gpt-4"
export A2I2_BASE_DIR="/path/to/project"
```

### IQL Model Files Required
```
a2i2_chatbot/backend/
├── iql/
│   ├── label_map.json
│   └── selector/
│       └── iql_model_embed.pt
└── indexes/
    └── policies/
        ├── emphasize_danger_pairs.json
        ├── emphasize_danger_op_embeds.npy
        ├── emphasize_value_of_life_pairs.json
        ├── emphasize_value_of_life_op_embeds.npy
        └── ... (other policies)
```

### Running Locally

**Backend:**
```bash
cd a2i2_chatbot/backend
python server.py
# Server runs on http://localhost:8001
```

**Frontend:**
```bash
cd a2i2_chatbot/frontend
# Option 1: Python SimpleHTTPServer
python -m http.server 8000

# Option 2: Node.js http-server
npx http-server -p 8000

# Open http://localhost:8000/landing.html
```

### Deployment to Production

**Backend (Render):**
1. Push code to GitHub
2. Create new Web Service on Render
3. Set environment variables (OPENAI_API_KEY, etc.)
4. Deploy
5. Update `frontend/config.js` with Render URL

**Frontend (Netlify):**
1. Connect GitHub repository
2. Set publish directory: `a2i2_chatbot/frontend`
3. Deploy
4. Update CORS in `server.py` with Netlify URL

---

## Testing the System

### 1. Test Survey Submission
```javascript
// In browser console on survey.html
fetch('http://localhost:8001/api/survey', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    timestamp: new Date().toISOString(),
    background: {email: 'test@test.com', age: '67', occupation: 'retired librarian'},
    personality: {q1: '4', q2: '2', /*...*/},
    moral: {q1: '5', q2: '4', /*...*/},
    specialNeeds: {condition: 'yes', vehicle: 'yes', details: 'has dog'}
  })
})
.then(r => r.json())
.then(data => console.log('Participant ID:', data.participantId))
```

### 2. Test Character Matching
```javascript
// In browser console on scenario.html
// After submitting survey, check matched characters
const participantId = sessionStorage.getItem('participantId');
fetch(`http://localhost:8001/api/survey/${participantId}`)
  .then(r => r.json())
  .then(data => {
    const matches = matchCharacterToProfile(data);
    console.log('Top matches:', matches);
  });
```

### 3. Test IQL Chat
```bash
# Start chat session
curl -X POST http://localhost:8001/api/chat/start \
  -H "Content-Type: application/json" \
  -d '{"character": "bob", "participantId": "test-id"}'

# Send message
curl -X POST http://localhost:8001/api/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-id_bob_1234567890",
    "character": "bob",
    "message": "Im busy with work right now"
  }'
```

---

## API Reference

### Survey Endpoints

#### POST `/api/survey`
Submit survey responses.

**Request:**
```json
{
  "timestamp": "2025-12-22T10:00:00Z",
  "background": {"email": "...", "age": "...", ...},
  "personality": {"q1": "4", "q2": "3", ...},
  "moral": {"q1": "5", "q2": "4", ...},
  "specialNeeds": {"condition": "yes", ...}
}
```

**Response:**
```json
{
  "success": true,
  "participantId": "uuid-here",
  "message": "Survey submitted successfully"
}
```

#### GET `/api/survey/{participant_id}`
Retrieve survey data.

**Response:**
```json
{
  "participantId": "uuid-here",
  "serverTimestamp": "2025-12-22T10:00:00Z",
  "background": {...},
  "personality": {...},
  "moral": {...},
  "specialNeeds": {...}
}
```

### Chat Endpoints

#### POST `/api/chat/start`
Initialize chat session.

**Request:**
```json
{
  "character": "bob",
  "participantId": "uuid-here"
}
```

**Response:**
```json
{
  "session_id": "uuid_bob_1234567890",
  "initial_message": "Hello, this is the fire department...",
  "character": "bob"
}
```

#### POST `/api/chat/message`
Send resident message, get operator response.

**Request:**
```json
{
  "session_id": "uuid_bob_1234567890",
  "character": "bob",
  "message": "I'm busy right now"
}
```

**Response:**
```json
{
  "response": "I understand you're busy, but there's a wildfire...",
  "session_id": "uuid_bob_1234567890",
  "policy": "emphasize_danger",
  "turn_count": 1,
  "conversation_ended": false,
  "judge": {
    "stance": "DELAY",
    "confidence": 0.85,
    "reason": "Resident is delaying evacuation"
  },
  "q_values": {
    "emphasize_danger": 0.456,
    "provide_information": 0.234,
    ...
  }
}
```

#### GET `/api/chat/history/{session_id}`
Get conversation history.

**Response:**
```json
{
  "history": [
    {"role": "operator", "text": "Hello..."},
    {"role": "resident", "text": "I'm busy..."}
  ],
  "turn_count": 1,
  "character": "bob",
  "created_at": "2025-12-22T10:00:00Z"
}
```

---

## Troubleshooting

### IQL Model Not Loading
- **Error:** `IQL label_map.json not found`
- **Solution:** Ensure IQL model files are in `backend/iql/` directory
- **Fallback:** System will use simple fallback responses if IQL unavailable

### OpenAI API Errors
- **Error:** `OPENAI_API_KEY environment variable not set`
- **Solution:** Set environment variable before starting server
- **Check quota:** Verify OpenAI API key has available credits

### CORS Errors
- **Error:** `Access-Control-Allow-Origin` blocked
- **Solution:** 
  1. Check `server.py` CORS settings
  2. Update `allow_origins` with frontend URL
  3. Restart backend server

### Character Matching Shows No Results
- **Cause:** No characters meet >50% threshold
- **Solution:** This is expected behavior - system shows "No matches found"
- **Debug:** Check console.log for similarity scores

### Audio/Video Not Playing
- **Cause:** Browser autoplay restrictions
- **Solution:** System shows prompt to enable media
- **Alternative:** User can manually click sound/video toggle buttons

---

## Data Collection

### Survey Responses
Stored in: `survey_responses/`
- Individual files: `{participant_id}.json`
- Aggregated file: `all_responses.jsonl`

### Chat Logs
Stored in: `conversation_sessions` (in-memory)
- For production: Implement Redis or database storage
- Save to files periodically for analysis

### Analysis
```python
import json
import pandas as pd

# Load all survey responses
with open('survey_responses/all_responses.jsonl') as f:
    surveys = [json.loads(line) for line in f]

df = pd.DataFrame(surveys)
print(df.describe())
```

---

## Future Enhancements

1. **Persistent Chat Storage**: Save conversations to database
2. **Admin Dashboard**: View participant data, conversation logs
3. **A/B Testing**: Compare different IQL policies
4. **Multi-language Support**: Translate survey and chat
5. **Voice Interface**: Add speech-to-text and text-to-speech
6. **Advanced Analytics**: Visualize conversation patterns, stance changes
7. **Mobile App**: Native iOS/Android apps

---

## Credits

- **IQL Algorithm**: Based on Implicit Q-Learning research
- **Survey Instruments**: Big Five Inventory, Moral Foundations Theory
- **Frontend Design**: Fire-themed emergency response interface
- **Backend**: FastAPI + Sentence Transformers + PyTorch

---

## Support

For questions or issues:
1. Check logs: Backend terminal and browser console
2. Review this guide thoroughly
3. Test with provided examples
4. Contact research team

---

## License

Research use only. Participants' data must be anonymized and protected per IRB protocols.

