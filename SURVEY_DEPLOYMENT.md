# Survey Deployment Guide

This guide explains how to deploy the Emergency Response Survey system to Render.

## Overview

The survey system consists of:
- **Frontend**: HTML/CSS/JavaScript survey interface
- **Backend**: FastAPI server to handle survey submissions and chatbot interactions
- **Storage**: JSON files for survey responses

## Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Browser   │─────▶│    Backend   │─────▶│   Storage   │
│  (Frontend) │      │   (FastAPI)  │      │  (JSON/DB)  │
└─────────────┘      └──────────────┘      └─────────────┘
```

## Deployment Steps

### 1. Backend Deployment to Render

#### Prerequisites
- Render account (free tier available)
- GitHub repository with your code

#### Steps

1. **Push your code to GitHub**
   ```bash
   cd /Users/tzhang/projects/a2i2_survey
   git add .
   git commit -m "Add survey system"
   git push origin main
   ```

2. **Create a new Web Service on Render**
   - Go to https://dashboard.render.com
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Configure the service:
     - **Name**: `a2i2-survey-backend`
     - **Region**: Choose closest to your users
     - **Branch**: `main`
     - **Root Directory**: `a2i2_chatbot/backend`
     - **Runtime**: `Python 3`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `uvicorn server:app --host 0.0.0.0 --port $PORT`
     - **Plan**: Free

3. **Set Environment Variables**
   In Render dashboard, add these environment variables:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `A2I2_BASE_DIR`: `/opt/render/project/src/a2i2_chatbot`
   - `PYTHON_VERSION`: `3.8.10`

4. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment to complete
   - Note your backend URL (e.g., `https://a2i2-survey-backend.onrender.com`)

### 2. Frontend Deployment

#### Option A: Deploy Frontend to Netlify (Recommended)

1. **Prepare frontend for deployment**
   - Update `frontend/config.js`:
     ```javascript
     API_URL: 'https://YOUR-BACKEND-URL.onrender.com'
     ```

2. **Deploy to Netlify**
   - Go to https://app.netlify.com
   - Drag and drop the `frontend` folder
   - Or connect your GitHub repo and set:
     - **Base directory**: `a2i2_chatbot/frontend`
     - **Build command**: (leave empty)
     - **Publish directory**: `.`

3. **Update CORS in Backend**
   - Add your Netlify URL to the CORS configuration in `backend/server.py`

#### Option B: Serve Frontend from Backend

1. **Update backend/server.py**
   ```python
   # Add this after creating the app
   app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")
   ```

2. **Update frontend/config.js**
   - Set API_URL to the same domain (relative paths)

### 3. Testing

1. **Test Survey Submission**
   ```bash
   curl -X POST https://YOUR-BACKEND-URL.onrender.com/api/survey \
     -H "Content-Type: application/json" \
     -d '{
       "timestamp": "2025-12-21T00:00:00Z",
       "background": {"email": "test@example.com"},
       "personality": {},
       "moral": {},
       "specialNeeds": {}
     }'
   ```

2. **Test Frontend**
   - Open your deployed frontend URL
   - Complete the survey
   - Verify data is saved to backend

### 4. Monitoring

1. **Check Logs on Render**
   - Go to your web service dashboard
   - Click "Logs" tab
   - Monitor for errors

2. **View Survey Responses**
   - Responses are stored in `survey_responses/` directory
   - Download `all_responses.jsonl` for analysis

## File Structure

```
a2i2_survey/
├── a2i2_chatbot/
│   ├── backend/
│   │   ├── server.py              # Main FastAPI server
│   │   ├── requirements.txt       # Python dependencies
│   │   └── render.yaml           # Render configuration
│   └── frontend/
│       ├── landing.html          # Entry point
│       ├── survey.html           # Survey form
│       ├── scenario.html         # Scenario intro
│       ├── chat.html             # Chatbot interface
│       ├── config.js             # Configuration
│       ├── styles/
│       │   ├── landing.css
│       │   ├── survey.css
│       │   └── scenario.css
│       └── js/
│           ├── survey.js
│           └── scenario.js
└── survey_responses/             # Survey data (created on first submission)
    ├── {participant-id}.json     # Individual responses
    └── all_responses.jsonl       # Aggregated responses
```

## Configuration

### Frontend Configuration (`frontend/config.js`)

```javascript
const CONFIG = {
  API_URL: 'https://YOUR-BACKEND-URL.onrender.com',
  SURVEY_TIMEOUT: 30 * 60 * 1000, // 30 minutes
  CONTACT_EMAIL: 'your-email@example.com'
};
```

### Backend Configuration

Environment variables to set on Render:
- `OPENAI_API_KEY`: Required for chatbot functionality
- `A2I2_BASE_DIR`: Base directory path (usually auto-detected)

## Data Collection

Survey responses are stored in two formats:

1. **Individual JSON files** (`survey_responses/{participant-id}.json`)
   - One file per participant
   - Easy to retrieve individual responses

2. **Aggregated JSONL file** (`survey_responses/all_responses.jsonl`)
   - One JSON object per line
   - Easy to process with data analysis tools

### Example Response Format

```json
{
  "participantId": "123e4567-e89b-12d3-a456-426614174000",
  "timestamp": "2025-12-21T10:30:00Z",
  "serverTimestamp": "2025-12-21T10:30:01Z",
  "background": {
    "email": "participant@example.com",
    "nickname": "Alex",
    "age": "25",
    "gender": "non-binary",
    "education": "college-graduate",
    "occupation": "Software Engineer",
    "ideology": "4"
  },
  "personality": {
    "q1": "4",
    "q2": "2",
    ...
  },
  "moral": {
    "q1": "5",
    "q2": "6",
    ...
  },
  "specialNeeds": {
    "condition": "no",
    "responsible": "yes",
    "vehicle": "no",
    "details": "I have a dog"
  }
}
```

## Data Analysis

To analyze survey responses:

```python
import json

# Read all responses
responses = []
with open('survey_responses/all_responses.jsonl', 'r') as f:
    for line in f:
        responses.append(json.loads(line))

# Example: Calculate average ideology score
ideology_scores = [int(r['background']['ideology']) 
                   for r in responses 
                   if r['background'].get('ideology')]
avg_ideology = sum(ideology_scores) / len(ideology_scores)
print(f"Average ideology: {avg_ideology}")
```

## Troubleshooting

### CORS Issues
- Ensure frontend URL is added to CORS configuration in `backend/server.py`
- Check browser console for CORS errors

### Survey Not Submitting
- Check network tab in browser dev tools
- Verify API_URL in `frontend/config.js` is correct
- Check backend logs on Render

### Backend Not Starting
- Check logs on Render dashboard
- Verify all required environment variables are set
- Ensure `requirements.txt` is up to date

## Security Considerations

1. **Data Privacy**
   - All responses are anonymous (no PII required)
   - Email is optional
   - Store data securely

2. **Rate Limiting**
   - Consider adding rate limiting to prevent abuse
   - Use Render's built-in DDoS protection

3. **HTTPS**
   - Render provides SSL certificates automatically
   - Always use HTTPS URLs

## Support

For questions or issues:
- Email: researcher@example.com
- GitHub Issues: [Your Repo URL]

## License

[Add your license information here]

