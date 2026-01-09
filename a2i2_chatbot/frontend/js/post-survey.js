/**
 * Post-Conversation Survey
 */

(function() {
  'use strict';

  // Configuration
  const CONFIG = window.APP_CONFIG || {
    API_URL: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
      ? 'http://localhost:8001' 
      : 'https://your-backend-url.onrender.com',
  };

  // State
  let sessionId = null;
  let participantId = null;
  let character = null;
  let conversationHistory = [];

  /**
   * Initialize survey
   */
  async function init() {
    // Get session info from URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    sessionId = urlParams.get('session_id');
    participantId = urlParams.get('participant_id');
    character = urlParams.get('character');

    if (!sessionId) {
      console.error('No session ID provided');
      alert('Error: Missing session information');
      return;
    }

    // Load conversation history
    await loadConversationHistory();

    // Setup event listeners
    setupEventListeners();

    // Generate utterance checkboxes
    generateUtteranceCheckboxes();
  }

  /**
   * Load conversation history
   */
  async function loadConversationHistory() {
    try {
      const response = await fetch(`${CONFIG.API_URL}/api/chat/history/${sessionId}`);
      if (response.ok) {
        const data = await response.json();
        conversationHistory = data.history || [];
        console.log('Loaded conversation history:', conversationHistory);
      }
    } catch (error) {
      console.error('Error loading conversation history:', error);
    }
  }

  /**
   * Setup event listeners
   */
  function setupEventListeners() {
    const form = document.getElementById('post-survey-form');
    
    // Question 1: Willingness to be evacuated
    const willingRadios = document.querySelectorAll('input[name="willing_rescued"]');
    willingRadios.forEach(radio => {
      radio.addEventListener('change', handleWillingChange);
    });

    // Question 2: Naturalness
    const naturalnessRadios = document.querySelectorAll('input[name="naturalness"]');
    naturalnessRadios.forEach(radio => {
      radio.addEventListener('change', handleNaturalnessChange);
    });

    // Form submission
    form.addEventListener('submit', handleSubmit);
  }

  /**
   * Handle willingness to be evacuated change
   */
  function handleWillingChange(event) {
    const value = event.target.value;
    
    // Hide all conditional fields
    document.getElementById('yes-field').style.display = 'none';
    document.getElementById('no-field').style.display = 'none';

    // Show relevant field
    if (value === 'yes') {
      document.getElementById('yes-field').style.display = 'block';
    } else if (value === 'no') {
      document.getElementById('no-field').style.display = 'block';
    }
  }

  /**
   * Handle naturalness rating change
   */
  function handleNaturalnessChange(event) {
    const value = event.target.value;
    
    // Hide all conditional fields
    document.getElementById('somewhat-field').style.display = 'none';
    document.getElementById('neutral-field').style.display = 'none';
    document.getElementById('bit-field').style.display = 'none';
    document.getElementById('not-field').style.display = 'none';

    // Show relevant field with checkboxes
    if (value === 'somewhat_natural') {
      document.getElementById('somewhat-field').style.display = 'block';
    } else if (value === 'neutral') {
      document.getElementById('neutral-field').style.display = 'block';
    } else if (value === 'bit_unnatural') {
      document.getElementById('bit-field').style.display = 'block';
    } else if (value === 'not_natural') {
      document.getElementById('not-field').style.display = 'block';
    }
  }

  /**
   * Generate utterance checkboxes based on conversation length
   */
  function generateUtteranceCheckboxes() {
    // Count total utterances (operator + resident messages)
    const utteranceCount = conversationHistory.length || 10; // Default to 10 if not loaded

    const containers = [
      'somewhat-utterances',
      'neutral-utterances',
      'bit-utterances',
      'not-utterances'
    ];

    containers.forEach(containerId => {
      const container = document.getElementById(containerId);
      if (!container) return;

      // Generate checkboxes for each utterance
      for (let i = 1; i <= utteranceCount; i++) {
        const checkboxItem = document.createElement('div');
        checkboxItem.className = 'checkbox-item';
        
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.name = `${containerId}_utterance`;
        checkbox.value = i;
        checkbox.id = `${containerId}_${i}`;
        
        const label = document.createElement('label');
        label.htmlFor = `${containerId}_${i}`;
        label.textContent = `#${i}`;
        
        checkboxItem.appendChild(checkbox);
        checkboxItem.appendChild(label);
        container.appendChild(checkboxItem);
      }
    });
  }

  /**
   * Handle form submission
   */
  async function handleSubmit(event) {
    event.preventDefault();

    const formData = new FormData(event.target);
    
    // Collect form data
    const surveyData = {
      sessionId: sessionId,
      participantId: participantId || sessionStorage.getItem('participantId'),
      character: character,
      timestamp: new Date().toISOString(),
      willingRescued: formData.get('willing_rescued'),
      yesInfluence: formData.get('yes_influence') || '',
      noConvince: formData.get('no_convince') || '',
      naturalness: formData.get('naturalness'),
      unnaturalUtterances: []
    };

    // Collect checked unnatural utterances
    const naturalnessValue = surveyData.naturalness;
    let utteranceField = null;
    
    if (naturalnessValue === 'somewhat_natural') {
      utteranceField = 'somewhat-utterances';
    } else if (naturalnessValue === 'neutral') {
      utteranceField = 'neutral-utterances';
    } else if (naturalnessValue === 'bit_unnatural') {
      utteranceField = 'bit-utterances';
    } else if (naturalnessValue === 'not_natural') {
      utteranceField = 'not-utterances';
    }

    if (utteranceField) {
      const checkboxes = document.querySelectorAll(`input[name="${utteranceField}_utterance"]:checked`);
      surveyData.unnaturalUtterances = Array.from(checkboxes).map(cb => parseInt(cb.value));
    }

    console.log('Post-survey data:', surveyData);

    // Submit to backend
    try {
      const response = await fetch(`${CONFIG.API_URL}/api/post-survey`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(surveyData)
      });

      if (response.ok) {
        console.log('Post-survey submitted successfully');
        
        // Show thank you message
        showThankYou();
      } else {
        throw new Error('Failed to submit post-survey');
      }
    } catch (error) {
      console.error('Error submitting post-survey:', error);
      
      // Still show thank you even if submission fails
      showThankYou();
    }
  }

  /**
   * Capitalize first letter
   */
  function capitalizeFirst(str) {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1);
  }

  /**
   * Show thank you message and handle next conversation
   */
  function showThankYou() {
    // Track completed conversations
    let completedConversations = parseInt(sessionStorage.getItem('completedConversations') || '0');
    completedConversations++;
    sessionStorage.setItem('completedConversations', completedConversations.toString());

    const container = document.querySelector('.survey-container');
    
    if (completedConversations < 3) {
      // More conversations to go
      const remaining = 3 - completedConversations;
      const selectedCharacter = sessionStorage.getItem('selectedCharacter');
      
      container.innerHTML = `
        <div class="survey-header">
          <h1>Thank You!</h1>
          <p class="subtitle">Conversation ${completedConversations} of 3 completed</p>
        </div>
        <div style="padding: 3rem; text-align: center;">
          <p style="font-size: 1.2rem; color: #2c3e50; margin-bottom: 2rem;">
            Your feedback has been recorded. You have ${remaining} more conversation${remaining > 1 ? 's' : ''} to complete.
          </p>
          <p style="font-size: 1rem; color: #666; margin-bottom: 2rem;">
            You will continue role-playing as <strong>${capitalizeFirst(selectedCharacter)}</strong> in the next conversation.
          </p>
          <button onclick="window.location.href='chat.html?character=${selectedCharacter}'" class="btn-submit">
            Start Next Conversation
          </button>
        </div>
      `;
    } else {
      // All 3 conversations completed
      container.innerHTML = `
        <div class="survey-header">
          <h1>🎉 Study Complete!</h1>
          <p class="subtitle">All 3 conversations completed</p>
        </div>
        <div style="padding: 3rem; text-align: center;">
          <p style="font-size: 1.3rem; color: #2c3e50; margin-bottom: 1.5rem; font-weight: 600;">
            Thank you for completing all three conversations!
          </p>
          <p style="font-size: 1.1rem; color: #666; margin-bottom: 2rem; line-height: 1.8;">
            Your participation in this research study is greatly appreciated. Your responses will help us understand how people communicate with emergency operators during fire-evacuation scenarios.
          </p>
          <p style="font-size: 1rem; color: #666; margin-bottom: 3rem;">
            You may now close this window.
          </p>
          <button onclick="window.location.href='landing.html'" class="btn-submit">
            Return to Home
          </button>
        </div>
      `;
    }
  }

  // Initialize on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();

