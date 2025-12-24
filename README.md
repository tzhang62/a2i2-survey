# A2I2 Emergency Response Survey System

An interactive web-based survey system for studying decision-making and communication during emergency scenarios. Features dynamic conversations powered by AI and comprehensive data collection.

## Features

- ✅ **Informed Consent**: Full IRB-compliant consent form
- ✅ **Survey System**: Collects demographics, personality traits (Big Five), moral foundations, and special needs
- ✅ **Immersive Scenarios**: Video and audio for realistic emergency situations
- ✅ **6 Conversations**: 3 non-role-play (different persuasion strategies) + 3 role-play conversations
- ✅ **IQL-Powered AI**: Intelligent operator responses using reinforcement learning
- ✅ **Post-Conversation Surveys**: Detailed feedback collection
- ✅ **Data Validation**: Prevents low-quality responses (straight-lining, too-fast completion)
- ✅ **Confirmation Numbers**: INC### for incomplete, CCC### for complete studies
- ✅ **Admin Panel**: Easy data export and statistics viewing
- ✅ **Exit Button**: Participants can exit at any time with data preservation

## Technology Stack

### Backend
- FastAPI (Python web framework)
- PyTorch (for IQL model)
- Sentence Transformers (for semantic matching)
- OpenAI API (for natural language generation)

### Frontend
- Pure HTML/CSS/JavaScript
- No build tools required
- Responsive design
- Audio/video support

### Deployment
- Backend: Render.com
- Frontend: Netlify
- Data Storage: Persistent disk on Render

## Quick Start (Local Development)

### 1. Backend Setup

```bash
cd a2i2_chatbot/backend

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp env.example .env
# Edit .env and add your OPENAI_API_KEY

# Run server
python server.py
```

Backend will run at: http://localhost:8001

### 2. Frontend Setup

```bash
cd a2i2_chatbot/frontend

# No build needed! Just serve the static files
python -m http.server 8000
```

Frontend will run at: http://localhost:8000

### 3. Access the Application

- **Survey**: http://localhost:8000/landing.html
- **Admin Panel**: http://localhost:8000/admin.html

## Deployment to Production

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

### Quick Deploy Steps:

1. **Push to GitHub**
2. **Deploy Backend to Render** (with persistent disk for data)
3. **Update frontend config.js** with your backend URL
4. **Deploy Frontend to Netlify**
5. **Access admin panel** to download data

## Data Collection

The system collects:

1. **Survey Data**
   - Demographics (age, gender, education, occupation)
   - Personality traits (Big Five)
   - Moral foundations
   - Special needs for emergency scenarios

2. **Conversation Data**
   - Full chat transcripts
   - Operator policy selections (IQL)
   - Turn counts and timestamps
   - Persuasion strategies used

3. **Post-Conversation Surveys**
   - Willingness to be rescued
   - Conversation naturalness
   - Specific utterance feedback

4. **Study Completion**
   - Complete studies: CCC### confirmation numbers
   - Incomplete exits: INC### confirmation numbers

## Data Export

### Using Admin Panel
1. Go to your-site.netlify.app/admin.html
2. Enter your ADMIN_KEY
3. Click "Download All Data (ZIP)"

### Using API
```bash
curl "https://your-backend.onrender.com/api/admin/export-data?admin_key=YOUR_KEY" -o data.zip
```

### Data Structure
```
study_data_export_TIMESTAMP.zip
├── _export_summary.json
├── {participant_id}.json (individual surveys)
├── confirmation_numbers.json
├── completed/CCC###.json (complete studies)
├── exits/INC###.json (incomplete studies)
└── post_surveys/*.json (post-conversation surveys)
```

## Configuration

### Backend Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `ADMIN_KEY`: Secret key for admin access (required)
- `OPENAI_MODEL`: Model to use (default: gpt-4o-mini)

### Frontend Configuration
Edit `frontend/config.js`:
- `API_URL`: Your backend URL
- `CONTACT_EMAIL`: Your research contact email

## Study Flow

1. **Landing Page**: Informed consent
2. **Survey**: Background questionnaire (~5 minutes)
3. **Session 1**: 3 Non-Role-Play Conversations
   - Conversation 1: Rational-Informational strategy
   - Conversation 2: Emotional-Relational strategy
   - Conversation 3: Social-Normative strategy
   - Post-survey after each
4. **Session 2**: Character Selection & 3 Role-Play Conversations
   - Select character based on survey responses
   - Role-play as selected character
   - Post-survey after each
5. **Completion**: CCC confirmation number

## Security & Privacy

- All data stored on secure Render disks
- Admin access protected by secret key
- No personal identifying information required (email optional)
- Participants can exit anytime
- Data export only via authenticated admin panel

## Support

For questions or issues:
- Check [DEPLOYMENT.md](DEPLOYMENT.md) for troubleshooting
- Review backend logs on Render dashboard
- Check browser console for frontend errors

## License

This research software is provided for academic use. Please cite appropriately if used in publications.

## Credits

Developed for USC A2I2 (Advancing AI through Inclusive Intelligence) research.

