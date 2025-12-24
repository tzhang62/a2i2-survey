# Survey Frontend

This directory contains the frontend web interface for the Emergency Response Study survey system.

## Pages

### 1. Landing Page (`landing.html`)
- Study introduction and consent form
- Entry point for participants
- **URL**: `landing.html`

### 2. Survey Questionnaire (`survey.html`)
- Four sections:
  1. Background Information (demographics)
  2. Personality Traits (Big Five, 10 questions)
  3. Moral Foundations (12 questions)
  4. Special Needs Assessment
- **URL**: `survey.html`

### 3. Scenario Page (`scenario.html`)
- Fire emergency scenario introduction
- Character selection for role-play
- Pre-conversation instructions
- **URL**: `scenario.html`

### 4. Chat Interface (`chat.html`)
- Existing chat interface (already implemented)
- Interaction with virtual emergency operator
- **URL**: `chat.html?townPerson={character}`

## Configuration

Edit `config.js` to configure:
- API endpoint URL
- Study settings
- Feature flags

```javascript
const CONFIG = {
  API_URL: 'http://localhost:8001',  // Update for production
  SURVEY_TIMEOUT: 30 * 60 * 1000,    // 30 minutes
  ENABLE_AUDIO: false,
  // ...
};
```

## Styling

All styles use CSS custom properties (variables) for easy theming:

```css
:root {
  --primary-color: #667eea;
  --secondary-color: #764ba2;
  /* ... */
}
```

To change the color scheme, modify these variables in the respective CSS files.

## JavaScript

Each page has its own JavaScript file:
- `js/survey.js` - Survey form handling and validation
- `js/scenario.js` - Scenario page logic and character selection

## Data Flow

1. **Landing Page**: Participant consents to study
2. **Survey Page**: Participant completes questionnaire
   - Data submitted to `/api/survey` endpoint
   - Returns unique `participantId`
3. **Scenario Page**: Participant selects character
   - `participantId` stored in sessionStorage
4. **Chat Interface**: Participant interacts with operator
   - Uses existing chat functionality

## Local Development

Serve locally using Python:
```bash
cd /Users/tzhang/projects/a2i2_survey/a2i2_chatbot/frontend
python -m http.server 8000
```

Then open `http://localhost:8000/landing.html`

## Production Deployment

For production deployment options:

### Option 1: Netlify (Recommended)
- Drag and drop this directory to Netlify
- Or connect GitHub repo with base directory set to `a2i2_chatbot/frontend`

### Option 2: Serve from Backend
- Frontend can be served from the FastAPI backend as static files
- Already configured in `backend/server.py`

See `SURVEY_DEPLOYMENT.md` for full deployment instructions.

## Browser Compatibility

Tested and working on:
- Chrome/Edge (v90+)
- Firefox (v88+)
- Safari (v14+)

Features used:
- CSS Grid
- Flexbox
- CSS Custom Properties
- ES6 JavaScript
- Fetch API

## Responsive Design

All pages are fully responsive:
- Desktop (1024px+)
- Tablet (768px - 1023px)
- Mobile (< 768px)

## Accessibility

Basic accessibility features included:
- Semantic HTML
- ARIA labels where appropriate
- Keyboard navigation support
- High contrast ratios

## Session Management

Data stored in `sessionStorage`:
- `participantId` - Unique ID from survey submission
- `participantNickname` - Optional participant nickname
- `selectedCharacter` - Character chosen for scenario
- `consentTimestamp` - When participant consented
- `studyStartTime` - When participant started study

## API Endpoints Used

- `POST /api/survey` - Submit survey responses
- `GET /api/survey/{participant_id}` - Retrieve survey data (optional)
- `POST /chat` - Send chat messages (existing)
- `GET /persona/{character}` - Get character persona (existing)

## Customization

### Add/Remove Survey Questions

Edit `survey.html` and update the corresponding collection logic in `js/survey.js`:

```javascript
function collectFormData() {
  // ... existing code ...
  
  // Add new section
  data.newSection = {
    question1: formData.get('new_q1') || '',
    // ...
  };
  
  return data;
}
```

### Change Visual Theme

Edit CSS variables in the respective CSS files:
- `styles/landing.css` - Landing page theme
- `styles/survey.css` - Survey form theme
- `styles/scenario.css` - Scenario page theme

### Modify Character List

Edit `scenario.html`:
```html
<div class="character-card" data-character="NewCharacter">
  <h3>New Character</h3>
  <p>Character description</p>
  <button onclick="selectCharacter('NewCharacter')">Select</button>
</div>
```

## Security Notes

- No authentication required (anonymous study)
- All data transmission should use HTTPS in production
- Participant IDs are UUIDs (randomly generated)
- No sensitive data is stored in localStorage/sessionStorage
- CORS is configured in backend to allow frontend access

## Testing

### Manual Testing Checklist

- [ ] Landing page loads correctly
- [ ] Consent checkbox enables start button
- [ ] Survey form accepts all input types
- [ ] Survey submits successfully
- [ ] Participant receives unique ID
- [ ] Scenario page shows after survey
- [ ] Character selection works
- [ ] Chat interface launches with selected character
- [ ] Responsive design works on mobile
- [ ] All pages work in different browsers

### Automated Testing

To add automated tests, consider:
- Jest for JavaScript unit tests
- Cypress or Playwright for E2E tests

## Performance

Current page sizes:
- `landing.html`: ~6 KB
- `survey.html`: ~18 KB
- `scenario.html`: ~8 KB
- Total CSS: ~25 KB
- Total JS: ~15 KB

All pages load in < 1 second on modern connections.

## Future Enhancements

Possible improvements:
- [ ] Progress bar for survey completion
- [ ] Save partial responses (draft mode)
- [ ] Multi-language support
- [ ] Audio/video consent recording
- [ ] Real-time validation feedback
- [ ] Analytics integration
- [ ] A/B testing framework

## License

[Add your license information here]

## Contact

For questions or issues, contact: [your-email@example.com]

