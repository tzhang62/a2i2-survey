# Emergency Response Survey System - Overview

## 📋 What Was Created

A complete web-based survey system for your emergency response study that includes:

### Frontend (4 Pages)
1. **Landing Page** (`landing.html`) - Study introduction and consent
2. **Survey Form** (`survey.html`) - Complete questionnaire with 4 sections
3. **Scenario Page** (`scenario.html`) - Fire emergency scenario introduction
4. **Chat Interface** (`chat.html`) - Existing chatbot (already implemented)

### Backend (API Endpoints)
- `POST /api/survey` - Submit survey responses
- `GET /api/survey/{participant_id}` - Retrieve survey data
- All existing chatbot endpoints remain functional

### Features Implemented

✅ **Survey Sections**
- Background Information (demographics)
- Personality Traits (Big Five, 10 questions, 5-point scale)
- Moral Foundations (12 questions, 6-point scale)
- Special Needs Assessment

✅ **Design**
- Modern, elegant UI with gradient backgrounds
- Fully responsive (mobile, tablet, desktop)
- Smooth animations and transitions
- Fire-themed scenario page with animations

✅ **Data Management**
- Unique participant IDs (UUID)
- JSON storage (individual + aggregated)
- Session management
- Anonymous data collection

✅ **Deployment Ready**
- Configured for Render backend deployment
- Can deploy frontend to Netlify or serve from backend
- CORS configured
- Environment variables support

## 🎨 Design Highlights

### Color Scheme
- **Primary**: Purple gradient (#667eea → #764ba2)
- **Accent**: Fire theme (orange/red) for scenario page
- **Clean**: White cards with subtle shadows

### User Experience
- Clear progress through study stages
- Visual feedback on selections
- Smooth transitions between pages
- Mobile-first responsive design

## 📁 File Structure

```
a2i2_survey/
├── SURVEY_QUICKSTART.md          # Quick start guide
├── SURVEY_DEPLOYMENT.md          # Deployment instructions
├── SURVEY_SYSTEM_OVERVIEW.md     # This file
├── test_survey_api.py            # API testing script
│
└── a2i2_chatbot/
    ├── frontend/
    │   ├── README.md             # Frontend documentation
    │   ├── landing.html          # Entry point
    │   ├── survey.html           # Survey questionnaire
    │   ├── scenario.html         # Scenario introduction
    │   ├── chat.html             # Chat interface (existing)
    │   ├── config.js             # Configuration
    │   │
    │   ├── styles/
    │   │   ├── landing.css       # Landing page styles
    │   │   ├── survey.css        # Survey form styles
    │   │   └── scenario.css      # Scenario page styles
    │   │
    │   └── js/
    │       ├── survey.js         # Survey form handler
    │       └── scenario.js       # Scenario page logic
    │
    ├── backend/
    │   ├── server.py             # FastAPI server (updated)
    │   ├── requirements.txt      # Python dependencies
    │   └── render.yaml           # Render config
    │
    └── survey_responses/         # Created on first submission
        ├── {uuid}.json           # Individual responses
        └── all_responses.jsonl   # Aggregated data
```

## 🚀 Getting Started

### Option 1: Quick Local Test (2 minutes)

```bash
# Terminal 1: Start backend
cd /Users/tzhang/projects/a2i2_survey/a2i2_chatbot/backend
python server.py

# Terminal 2: Serve frontend
cd /Users/tzhang/projects/a2i2_survey/a2i2_chatbot/frontend
python -m http.server 8000

# Open browser to: http://localhost:8000/landing.html
```

### Option 2: Test API Only

```bash
cd /Users/tzhang/projects/a2i2_survey
python test_survey_api.py
```

### Option 3: Deploy to Production

Follow instructions in `SURVEY_DEPLOYMENT.md`

## 📊 Survey Content

### Section 1: Background Information
- Email (optional)
- Nickname
- Age
- Gender (4 options)
- Education (5 levels)
- Occupation
- Ideology (7-point scale)

### Section 2: Personality Traits (Big Five)
10 questions measuring:
- Extraversion (communication)
- Agreeableness (cooperation)
- Conscientiousness (organization)
- Neuroticism (stress response)
- Openness (adaptability)

**Scale**: 1 (Strongly disagree) to 5 (Strongly agree)

### Section 3: Moral Foundations
12 questions measuring:
- Care/Harm
- Fairness/Cheating
- Loyalty/Betrayal
- Authority/Subversion
- Sanctity/Degradation
- Liberty/Oppression

**Scale**: 1 (Strongly disagree) to 6 (Strongly agree)

### Section 4: Special Needs
- Physical/medical conditions
- Responsibility for others
- Vehicle/assistance needs
- Free-text details

## 🔄 User Flow

```
1. Landing Page
   ↓ [Consent checkbox + Begin Study]
   
2. Survey Form
   ↓ [Complete questionnaire + Submit]
   
3. Scenario Page
   ↓ [Read scenario + Select character]
   
4. Chat Interface
   ↓ [Interact with virtual operator]
   
5. End of Study
```

## 💾 Data Storage

### Individual Files
```json
{
  "participantId": "123e4567-e89b-12d3-a456-426614174000",
  "timestamp": "2025-12-21T10:30:00Z",
  "serverTimestamp": "2025-12-21T10:30:01Z",
  "background": { ... },
  "personality": { ... },
  "moral": { ... },
  "specialNeeds": { ... }
}
```

### Aggregated File (JSONL)
One JSON object per line for easy processing with pandas, R, etc.

## 🔧 Customization

### Change Survey Questions
Edit `frontend/survey.html` and update `js/survey.js`

### Modify Styling
Edit CSS files in `frontend/styles/`

### Update API Endpoint
Edit `frontend/config.js`:
```javascript
const CONFIG = {
  API_URL: 'https://your-backend.onrender.com',
  // ...
};
```

### Add New Characters
Edit `frontend/scenario.html` character grid

## 📈 Data Analysis

### Python Example
```python
import json
import pandas as pd

# Load all responses
responses = []
with open('survey_responses/all_responses.jsonl', 'r') as f:
    for line in f:
        responses.append(json.loads(line))

# Convert to DataFrame
df = pd.DataFrame(responses)

# Analyze personality traits
personality_df = pd.json_normalize(df['personality'])
print(personality_df.describe())

# Analyze moral foundations
moral_df = pd.json_normalize(df['moral'])
print(moral_df.describe())
```

### R Example
```r
library(jsonlite)
library(tidyverse)

# Load responses
responses <- stream_in(file("survey_responses/all_responses.jsonl"))

# Extract personality data
personality <- responses %>%
  select(participantId, personality) %>%
  unnest_wider(personality)

# Summary statistics
summary(personality)
```

## 🔒 Privacy & Ethics

### Built-in Privacy Features
- Anonymous participation (email optional)
- No tracking cookies
- Local data storage
- Secure HTTPS (in production)

### Recommendations
- Obtain IRB approval before collecting data
- Provide clear consent information
- Allow participants to withdraw
- Store data securely
- Anonymize any published results

## 🧪 Testing

### Manual Testing Checklist
- [ ] Landing page loads and consent works
- [ ] Survey accepts all input types
- [ ] Survey submits successfully
- [ ] Participant receives unique ID
- [ ] Scenario page displays correctly
- [ ] Character selection works
- [ ] Chat interface launches
- [ ] Data saves to files
- [ ] Responsive design on mobile
- [ ] Works in Chrome, Firefox, Safari

### Automated Testing
Run the test script:
```bash
python test_survey_api.py
```

## 🐛 Troubleshooting

### Common Issues

**Backend won't start**
- Check if port 8001 is in use
- Verify Python dependencies installed
- Check for syntax errors in server.py

**CORS errors**
- Verify API_URL in config.js
- Check CORS settings in server.py
- Use same origin or configure properly

**Survey not submitting**
- Check browser console for errors
- Verify backend is running
- Check network tab in dev tools

**Data not saving**
- Check file permissions
- Verify survey_responses/ directory exists
- Check backend logs for errors

## 📚 Documentation

- **SURVEY_QUICKSTART.md** - Get started in 5 minutes
- **SURVEY_DEPLOYMENT.md** - Deploy to production
- **frontend/README.md** - Frontend documentation
- **test_survey_api.py** - API testing script

## 🎯 Next Steps

### Immediate (Before Testing)
1. ✅ Review survey questions
2. ✅ Test locally
3. ✅ Verify data collection
4. ✅ Check responsive design

### Before Deployment
1. Update contact email in config
2. Update API_URL for production
3. Test on multiple devices
4. Obtain IRB approval (if required)

### After Deployment
1. Monitor backend logs
2. Check data collection
3. Analyze pilot data
4. Adjust based on feedback

## 🤝 Support

### Resources
- FastAPI docs: https://fastapi.tiangolo.com
- Render docs: https://render.com/docs
- Netlify docs: https://docs.netlify.com

### Contact
For questions about this implementation:
- Check the documentation files
- Review the code comments
- Test with the provided test script

## 📝 License

[Add your license information]

## 🙏 Acknowledgments

This survey system was designed for research on emergency response communication and decision-making.

---

**Version**: 1.0.0  
**Created**: December 2025  
**Last Updated**: December 2025

