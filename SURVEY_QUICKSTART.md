# Survey System Quick Start Guide

This guide will help you get the survey system running locally in minutes.

## Prerequisites

- Python 3.8 or higher
- Modern web browser (Chrome, Firefox, Safari, Edge)

## Quick Start (5 minutes)

### 1. Start the Backend Server

```bash
# Navigate to the backend directory
cd /Users/tzhang/projects/a2i2_survey/a2i2_chatbot/backend

# Install dependencies (if not already installed)
pip install -r requirements.txt

# Start the server
python server.py
```

The backend should now be running at `http://localhost:8001`

### 2. Open the Frontend

Open a web browser and navigate to:
```
file:///Users/tzhang/projects/a2i2_survey/a2i2_chatbot/frontend/landing.html
```

Or use Python's built-in HTTP server:
```bash
# In a new terminal, navigate to the frontend directory
cd /Users/tzhang/projects/a2i2_survey/a2i2_chatbot/frontend

# Start a simple HTTP server
python -m http.server 8000
```

Then open `http://localhost:8000/landing.html` in your browser.

### 3. Test the Survey

1. Click "Begin Study" on the landing page
2. Fill out the survey form (all fields are optional)
3. Click "Start Conversation →"
4. Select a character
5. Click "Start Conversation →" again to begin the chat

## Survey Flow

```
Landing Page → Survey Form → Scenario Page → Chat Interface
(landing.html)  (survey.html)  (scenario.html)   (chat.html)
```

## Viewing Survey Responses

Survey responses are stored in:
```
/Users/tzhang/projects/a2i2_survey/a2i2_chatbot/survey_responses/
```

Two formats:
1. **Individual files**: `{participant-id}.json`
2. **Aggregated file**: `all_responses.jsonl`

### View All Responses

```python
import json

# Read all responses
with open('a2i2_chatbot/survey_responses/all_responses.jsonl', 'r') as f:
    for line in f:
        response = json.loads(line)
        print(f"Participant: {response['participantId']}")
        print(f"Nickname: {response['background'].get('nickname', 'N/A')}")
        print("---")
```

## Testing the API

### Test Survey Submission

```bash
curl -X POST http://localhost:8001/api/survey \
  -H "Content-Type: application/json" \
  -d '{
    "timestamp": "2025-12-21T00:00:00Z",
    "background": {
      "email": "test@example.com",
      "nickname": "TestUser",
      "age": "25",
      "gender": "male",
      "education": "college-graduate",
      "occupation": "Researcher",
      "ideology": "4"
    },
    "personality": {
      "q1": "4", "q2": "3", "q3": "5", "q4": "2", "q5": "4",
      "q6": "2", "q7": "3", "q8": "4", "q9": "5", "q10": "2"
    },
    "moral": {
      "q1": "5", "q2": "6", "q3": "5", "q4": "5", "q5": "4",
      "q6": "5", "q7": "4", "q8": "5", "q9": "4", "q10": "5",
      "q11": "4", "q12": "4"
    },
    "specialNeeds": {
      "condition": "no",
      "responsible": "no",
      "vehicle": "no",
      "details": ""
    }
  }'
```

### Test Retrieving a Response

```bash
# Replace {participant-id} with an actual participant ID from the response above
curl http://localhost:8001/api/survey/{participant-id}
```

## Project Structure

```
a2i2_chatbot/
├── frontend/
│   ├── landing.html          # Study welcome page
│   ├── survey.html           # Survey questionnaire
│   ├── scenario.html         # Pre-chat scenario intro
│   ├── chat.html             # Chat interface (existing)
│   ├── config.js             # Configuration
│   ├── styles/
│   │   ├── landing.css
│   │   ├── survey.css
│   │   └── scenario.css
│   └── js/
│       ├── survey.js         # Survey form handler
│       └── scenario.js       # Scenario page logic
└── backend/
    ├── server.py             # FastAPI server (updated)
    └── requirements.txt
```

## Customization

### Update Survey Questions

Edit `frontend/survey.html` to modify questions.

### Change Styling

Edit the CSS files in `frontend/styles/`:
- `landing.css` - Landing page
- `survey.css` - Survey form
- `scenario.css` - Scenario page

### Modify API Endpoint

Update `frontend/config.js`:
```javascript
const CONFIG = {
  API_URL: 'http://your-server:8001',
  // ... other config
};
```

## Common Issues

### Backend won't start
- **Issue**: Port 8001 already in use
- **Solution**: Change port in server.py:
  ```python
  uvicorn.run(app, host="0.0.0.0", port=8002)
  ```

### CORS errors in browser console
- **Issue**: Frontend and backend on different origins
- **Solution**: CORS is already configured for localhost. If using different ports, update CORS settings in `server.py`

### Survey data not saving
- **Issue**: Directory doesn't exist
- **Solution**: The directory should be created automatically, but you can create it manually:
  ```bash
  mkdir -p a2i2_chatbot/survey_responses
  ```

## Next Steps

Once you've tested locally:

1. **Deploy to Production**: Follow the [SURVEY_DEPLOYMENT.md](SURVEY_DEPLOYMENT.md) guide
2. **Analyze Data**: Use Python/R to analyze survey responses
3. **Customize**: Modify the survey questions, styling, and flow to fit your needs

## Support

If you encounter issues:
1. Check the backend logs in the terminal
2. Check the browser console (F12) for errors
3. Verify the API URL in `config.js` is correct

## Data Privacy

- All data is stored locally by default
- No data is transmitted to external services (except OpenAI for chat functionality)
- Participants can choose to remain anonymous
- Consider IRB approval for human subjects research

## Screenshots

### Landing Page
- Welcome message and consent form

### Survey Page
- Background information
- Personality traits (10 questions, 5-point scale)
- Moral foundations (12 questions, 6-point scale)
- Special needs assessment

### Scenario Page
- Fire emergency scenario description
- Character selection
- Pre-chat instructions

### Chat Interface
- Existing chat.html interface with selected character

