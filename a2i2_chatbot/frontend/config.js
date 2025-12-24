// Configuration for the survey application
const CONFIG = {
  // API URL - update this after deployment to Render
  API_URL: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8001' 
    : 'https://a2i2-survey-backend.onrender.com', // No trailing slash!
  
  // Application settings
  SURVEY_TIMEOUT: 30 * 60 * 1000, // 30 minutes in milliseconds
  MAX_SURVEY_ATTEMPTS: 3,
  
  // Feature flags
  ENABLE_AUDIO: false, // Set to true if you add ambient sounds
  ENABLE_PROGRESS_TRACKING: true,
  
  // Study information
  STUDY_NAME: 'Emergency Response Study',
  STUDY_VERSION: '1.0.0',
  CONTACT_EMAIL: 'tzhang62@usc.edu' // Update with your email
};

// Make config globally available
window.APP_CONFIG = CONFIG;
