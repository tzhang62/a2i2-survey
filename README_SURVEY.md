# Emergency Response Survey System

A complete web-based survey system for studying decision-making and communication during emergencies.

## 🎯 What This Is

This system allows participants to:
1. Provide consent and demographic information
2. Complete a comprehensive questionnaire (personality, moral values, special needs)
3. Experience a fire emergency scenario
4. Interact with a virtual emergency operator (AI chatbot)

## 📁 What Was Created

### Frontend Pages (HTML/CSS/JavaScript)
- ✅ `landing.html` - Study introduction and consent form
- ✅ `survey.html` - Multi-section questionnaire
- ✅ `scenario.html` - Fire emergency scenario with character selection
- ✅ `demo.html` - Interactive demo/preview page
- ✅ Responsive CSS styling for all pages
- ✅ JavaScript for form handling and validation

### Backend (Python/FastAPI)
- ✅ Survey submission endpoint (`POST /api/survey`)
- ✅ Survey retrieval endpoint (`GET /api/survey/{id}`)
- ✅ UUID generation for participants
- ✅ JSON data storage (dual format)
- ✅ All existing chatbot endpoints preserved

### Documentation
- ✅ `SURVEY_QUICKSTART.md` - Get started in 5 minutes
- ✅ `SURVEY_DEPLOYMENT.md` - Production deployment guide
- ✅ `SURVEY_SYSTEM_OVERVIEW.md` - Complete system documentation
- ✅ `VISUAL_GUIDE.md` - Visual design guide
- ✅ `frontend/README.md` - Frontend documentation
- ✅ `test_survey_api.py` - API testing script

## 🚀 Quick Start (2 Minutes)

### 1. View the Demo
```bash
# Open in browser
open /Users/tzhang/projects/a2i2_survey/a2i2_chatbot/frontend/demo.html
```

### 2. Run Locally
```bash
# Terminal 1: Start backend
cd /Users/tzhang/projects/a2i2_survey/a2i2_chatbot/backend
python server.py

# Terminal 2: Serve frontend  
cd /Users/tzhang/projects/a2i2_survey/a2i2_chatbot/frontend
python -m http.server 8000

# Open: http://localhost:8000/landing.html
```

### 3. Test the API
```bash
cd /Users/tzhang/projects/a2i2_survey
python test_survey_api.py
```

## 📊 Survey Structure

### Section 1: Background (7 questions)
- Email, nickname, age, gender
- Education, occupation, ideology

### Section 2: Personality (10 questions, 5-point scale)
- Based on Big Five personality traits
- Measures communication, cooperation, organization, stress response, adaptability

### Section 3: Moral Foundations (12 questions, 6-point scale)
- Based on Moral Foundations Theory
- Measures care, fairness, loyalty, authority, sanctity, liberty

### Section 4: Special Needs (4 questions)
- Physical/medical conditions
- Responsibility for others
- Need for assistance

**Total**: 33 data points per participant

## 🎨 Design Features

- **Modern UI**: Clean, professional design with purple gradient theme
- **Responsive**: Works on desktop, tablet, and mobile
- **Accessible**: Semantic HTML, keyboard navigation, high contrast
- **Animated**: Smooth transitions and interactive elements
- **Fire Theme**: Scenario page has fire-themed animations

## 💾 Data Storage

Survey responses are saved in two formats:

1. **Individual JSON files**: `survey_responses/{uuid}.json`
   - Easy to retrieve specific participants
   
2. **Aggregated JSONL file**: `survey_responses/all_responses.jsonl`
   - One JSON object per line
   - Easy to process with pandas/R

## 🔧 Configuration

Edit `frontend/config.js` to configure:
```javascript
const CONFIG = {
  API_URL: 'http://localhost:8001',  // Update for production
  SURVEY_TIMEOUT: 30 * 60 * 1000,    // 30 minutes
  CONTACT_EMAIL: 'your-email@example.com'
};
```

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| `SURVEY_QUICKSTART.md` | Get started in 5 minutes |
| `SURVEY_DEPLOYMENT.md` | Deploy to Render/Netlify |
| `SURVEY_SYSTEM_OVERVIEW.md` | Complete system overview |
| `VISUAL_GUIDE.md` | Visual design guide |
| `frontend/README.md` | Frontend documentation |
| `test_survey_api.py` | API testing script |

## 🌐 Deployment

### Backend (Render)
1. Push code to GitHub
2. Create Web Service on Render
3. Set environment variables
4. Deploy

### Frontend (Netlify)
1. Update API_URL in config.js
2. Drag frontend folder to Netlify
3. Done!

See `SURVEY_DEPLOYMENT.md` for detailed instructions.

## 🧪 Testing

### Manual Testing
1. Open `demo.html` to preview pages
2. Complete the survey flow
3. Check browser console for errors
4. Verify data saved in `survey_responses/`

### Automated Testing
```bash
python test_survey_api.py
```

## 📈 Data Analysis

### Python Example
```python
import json
import pandas as pd

# Load responses
responses = []
with open('survey_responses/all_responses.jsonl', 'r') as f:
    for line in f:
        responses.append(json.loads(line))

# Convert to DataFrame
df = pd.DataFrame(responses)

# Analyze
print(df['background'].apply(pd.Series).describe())
```

### R Example
```r
library(jsonlite)
library(tidyverse)

responses <- stream_in(file("survey_responses/all_responses.jsonl"))
summary(responses)
```

## 🔒 Privacy & Ethics

- ✅ Anonymous participation (email optional)
- ✅ Clear consent process
- ✅ Can withdraw anytime
- ✅ Secure data storage
- ✅ No tracking cookies
- ⚠️ Obtain IRB approval before collecting data

## 🎯 User Flow

```
Landing Page (consent)
    ↓
Survey Form (questionnaire)
    ↓
Scenario Page (character selection)
    ↓
Chat Interface (operator interaction)
```

## 📱 Browser Support

- ✅ Chrome/Edge 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Mobile browsers

## 🛠️ Tech Stack

**Frontend**:
- HTML5, CSS3, JavaScript (ES6)
- No frameworks (vanilla JS)
- Responsive design with CSS Grid/Flexbox

**Backend**:
- Python 3.8+
- FastAPI
- Pydantic for validation
- JSON storage

## 📦 File Structure

```
a2i2_survey/
├── README_SURVEY.md              # This file
├── SURVEY_QUICKSTART.md          # Quick start guide
├── SURVEY_DEPLOYMENT.md          # Deployment guide
├── SURVEY_SYSTEM_OVERVIEW.md     # System overview
├── VISUAL_GUIDE.md               # Visual guide
├── test_survey_api.py            # Testing script
│
└── a2i2_chatbot/
    ├── frontend/
    │   ├── demo.html             # Demo page
    │   ├── landing.html          # Entry point
    │   ├── survey.html           # Survey form
    │   ├── scenario.html         # Scenario page
    │   ├── chat.html             # Chat (existing)
    │   ├── config.js             # Configuration
    │   ├── styles/               # CSS files
    │   └── js/                   # JavaScript files
    │
    ├── backend/
    │   ├── server.py             # FastAPI server
    │   └── requirements.txt      # Dependencies
    │
    └── survey_responses/         # Data storage
        ├── {uuid}.json           # Individual
        └── all_responses.jsonl   # Aggregated
```

## 🚨 Important Notes

### Before Using
1. ✅ Review survey questions for your study
2. ✅ Update contact email in config
3. ✅ Test locally first
4. ✅ Obtain IRB approval (if required)
5. ✅ Update API_URL for production

### For Render Deployment
1. Update `frontend/config.js` with your Render URL
2. Set environment variables on Render
3. Update CORS settings in `backend/server.py`

## 🐛 Troubleshooting

### Backend won't start
- Check port 8001 is available
- Verify Python dependencies installed
- Check for syntax errors

### CORS errors
- Verify API_URL in config.js
- Check CORS settings in server.py
- Use same origin or configure properly

### Survey not submitting
- Check browser console
- Verify backend is running
- Check network tab in dev tools

## 📞 Support

For issues or questions:
1. Check the documentation files
2. Review code comments
3. Run test script: `python test_survey_api.py`

## ✅ What's Working

- ✅ Landing page with consent
- ✅ Complete survey form (29 questions)
- ✅ Scenario page with animations
- ✅ Character selection
- ✅ Backend API endpoints
- ✅ Data storage (JSON)
- ✅ Responsive design
- ✅ Form validation
- ✅ Session management
- ✅ Existing chat integration

## 🎉 Next Steps

1. **Test Locally**: Run the system and complete a test survey
2. **Customize**: Adjust questions, styling, or flow as needed
3. **Deploy**: Follow deployment guide for production
4. **Collect Data**: Start your study!
5. **Analyze**: Use provided examples to analyze responses

## 📄 License

[Add your license information]

## 🙏 Acknowledgments

Built for emergency response communication research.

---

**Version**: 1.0.0  
**Created**: December 2025  
**Status**: ✅ Ready to use

For detailed information, see the documentation files listed above.

