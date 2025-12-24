/**
 * Fire Rescue Chat Interface
 * Connects to IQL-based operator backend
 */

(function() {
  'use strict';

  // Configuration
  const CONFIG = window.APP_CONFIG || {
    API_URL: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
      ? 'http://localhost:8001' 
      : 'https://your-backend-url.onrender.com',
  };

  // Handle page refresh - restart this conversation only (keep all participant data)
  const perfData = performance.getEntriesByType('navigation')[0];
  if (perfData && perfData.type === 'reload') {
    console.log('🔄 Page refresh detected on chat page - restarting current conversation');
    // Keep participant ID, survey data, completedConversations, selectedCharacter
    // The page will reload with the same URL parameters and start a fresh conversation
  }

  // State
  let sessionId = null;
  let character = null;
  let participantId = null;
  let conversationEnded = false;
  let turnCount = 0;
  let utteranceCount = 0; // Track total utterances
  let operatorUtterances = []; // Track operator messages for post-survey
  let conversationNumber = 1; // Current conversation (1-6)
  let isRolePlay = false; // Whether this is a role-play conversation

  // DOM Elements
  const messagesContainer = document.getElementById('chat-messages');
  const messageInput = document.getElementById('message-input');
  const sendBtn = document.getElementById('send-btn');
  const turnCountDisplay = document.getElementById('turn-count');
  const characterInfo = document.getElementById('character-info');
  const sessionStatus = document.getElementById('session-status');
  const endModal = document.getElementById('end-modal');
  const endTitle = document.getElementById('end-title');
  const endMessage = document.getElementById('end-message');
  const closeModalBtn = document.getElementById('close-modal-btn');
  const loadingOverlay = document.getElementById('loading-overlay');

  /**
   * Update session status display
   */
  function updateSessionStatus() {
    if (!sessionStatus) return;
    
    // Use isRolePlay flag to determine session type
    if (isRolePlay) {
      sessionStatus.innerHTML = `
        <div class="session-badge">
          <span class="icon">🎭</span>
          <span>Session 2: Role-Play</span>
        </div>
        <div class="conversation-count">Conversation ${conversationNumber} of 3 (You play as ${capitalizeFirst(character)})</div>
      `;
    } else {
      sessionStatus.innerHTML = `
        <div class="session-badge">
          <span class="icon">👤</span>
          <span>Session 1: Non-Role-Play</span>
        </div>
        <div class="conversation-count">Conversation ${conversationNumber} of 3 (You play as yourself)</div>
      `;
    }
  }

  /**
   * Initialize chat on page load
   */
  async function init() {
    // Get URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    
    // Development mode: Clear session storage if ?reset=true in URL
    if (urlParams.get('reset') === 'true') {
      console.log('🔄 Reset parameter detected - clearing session storage');
      sessionStorage.clear();
      // Redirect to survey page
      window.location.href = 'survey.html';
      return;
    }
    
    // Determine conversation type and number
    const conversationType = urlParams.get('type'); // 'non-roleplay' or 'roleplay'
    conversationNumber = parseInt(urlParams.get('conversation') || '1');
    character = urlParams.get('character');
    participantId = sessionStorage.getItem('participantId');

    console.log('[INIT] URL params:', {
      type: conversationType,
      conversation: urlParams.get('conversation'),
      conversationNumber: conversationNumber,
      character: character
    });
    console.log('[INIT] Session storage completedConversations:', sessionStorage.getItem('completedConversations'));

    if (!participantId) {
      console.warn('No participant ID found in session storage');
    }

    // Update session status display
    isRolePlay = conversationType === 'roleplay' || (character && !conversationType);
    updateSessionStatus();

    // Hide character info since it's now in session status
    if (characterInfo) {
      characterInfo.style.display = 'none';
    }

    // Initialize ambient sound
    initializeAmbientSound();

    // Start chat session
    await startChatSession();

    // Event listeners
    sendBtn.addEventListener('click', sendMessage);
    messageInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
      }
    });
    closeModalBtn.addEventListener('click', () => {
      endModal.classList.add('hidden');
      // Optionally redirect
      // window.location.href = 'landing.html';
    });

    // Disable copy, cut, and paste in the message input
    messageInput.addEventListener('copy', (e) => {
      e.preventDefault();
      console.log('Copy disabled in chat');
    });
    
    messageInput.addEventListener('cut', (e) => {
      e.preventDefault();
      console.log('Cut disabled in chat');
    });
    
    messageInput.addEventListener('paste', (e) => {
      e.preventDefault();
      console.log('Paste disabled in chat');
      // Show brief feedback to user
      showBriefMessage('Please type your response directly');
    });
    
    // Disable right-click context menu on message input
    messageInput.addEventListener('contextmenu', (e) => {
      e.preventDefault();
      console.log('Context menu disabled in chat');
    });
    
    // Also prevent keyboard shortcuts (Ctrl/Cmd + C, X, V)
    messageInput.addEventListener('keydown', (e) => {
      if ((e.ctrlKey || e.metaKey) && (e.key === 'c' || e.key === 'x' || e.key === 'v')) {
        e.preventDefault();
        if (e.key === 'v') {
          showBriefMessage('Please type your response directly');
        }
        console.log(`Keyboard shortcut ${e.key} disabled in chat`);
      }
    });

    // Focus input
    messageInput.focus();
  }

  /**
   * Initialize ambient sound
   */
  function initializeAmbientSound() {
    const ambientSound = document.getElementById('ambientSound');
    const toggleSoundBtn = document.getElementById('toggleSound');
    const soundOnIcon = toggleSoundBtn.querySelector('.sound-on');
    const soundOffIcon = toggleSoundBtn.querySelector('.sound-off');
    
    if (!ambientSound || !toggleSoundBtn) {
      console.warn('Ambient sound elements not found');
      return;
    }

    let soundEnabled = true;

    // Set volume first
    ambientSound.volume = 0.3;

    // Function to start sound
    const startSound = () => {
      const playPromise = ambientSound.play();
      if (playPromise !== undefined) {
        playPromise
          .then(() => {
            console.log('Ambient sound started successfully');
            soundEnabled = true;
            soundOnIcon.classList.remove('hidden');
            soundOffIcon.classList.add('hidden');
          })
          .catch(error => {
            console.warn('Failed to start sound:', error);
            soundEnabled = false;
            soundOnIcon.classList.add('hidden');
            soundOffIcon.classList.remove('hidden');
          });
      }
    };

    // Try to autoplay immediately
    startSound();

    // If autoplay fails, try again on first user interaction
    let interactionListener = () => {
      if (!soundEnabled || ambientSound.paused) {
        console.log('Starting sound on user interaction');
        startSound();
      }
      // Remove listener after first interaction
      document.removeEventListener('click', interactionListener);
      document.removeEventListener('keydown', interactionListener);
    };

    // Add interaction listeners as fallback
    setTimeout(() => {
      if (ambientSound.paused) {
        console.log('Autoplay blocked, waiting for user interaction');
        document.addEventListener('click', interactionListener, { once: true });
        document.addEventListener('keydown', interactionListener, { once: true });
        
        // Show a subtle notification
        showSoundNotification();
      }
    }, 500);

    // Toggle sound on button click
    toggleSoundBtn.addEventListener('click', () => {
      soundEnabled = !soundEnabled;
      
      if (soundEnabled) {
        ambientSound.play();
        ambientSound.volume = 0.3;
        soundOnIcon.classList.remove('hidden');
        soundOffIcon.classList.add('hidden');
      } else {
        ambientSound.pause();
        soundOnIcon.classList.add('hidden');
        soundOffIcon.classList.remove('hidden');
      }
    });
  }

  /**
   * Show a subtle notification that sound is available
   */
  function showSoundNotification() {
    const notification = document.createElement('div');
    notification.className = 'sound-notification';
    notification.innerHTML = `
      <span>🔊</span>
      <span>Click anywhere to enable background sound</span>
    `;
    document.body.appendChild(notification);

    // Auto-hide after 5 seconds
    setTimeout(() => {
      notification.classList.add('fade-out');
      setTimeout(() => notification.remove(), 500);
    }, 5000);

    // Hide on click
    document.addEventListener('click', () => {
      if (notification.parentNode) {
        notification.classList.add('fade-out');
        setTimeout(() => notification.remove(), 500);
      }
    }, { once: true });
  }

  /**
   * Start chat session
   */
  async function startChatSession() {
    try {
      showLoading(true);
      
      // Prepare request payload based on conversation type
      let payload = {
        participantId: participantId
      };
      
      if (isRolePlay) {
        // Role-play conversation (Session 2)
        payload.character = character;
      } else {
        // Non-role-play conversation (Session 1)
        // Map conversation number to persuasion strategy
        const persuasionStrategies = {
          1: 'rational-informational',
          2: 'emotional-relational',
          3: 'social-normative'
        };
        
        payload.persuasionStrategy = persuasionStrategies[conversationNumber];
        
        // Include survey data for personalized scenario
        const surveyDataStr = sessionStorage.getItem('surveyData');
        if (surveyDataStr) {
          try {
            payload.surveyData = JSON.parse(surveyDataStr);
          } catch (e) {
            console.warn('Failed to parse survey data:', e);
          }
        }
      }
      
      console.log('[CHAT] Starting session with payload:', payload);
      
      const response = await fetch(`${CONFIG.API_URL}/api/chat/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Failed to start chat session: ${errorText}`);
      }

      const data = await response.json();
      sessionId = data.session_id;

      // Display initial operator message
      addMessage('operator', data.initial_message);

    } catch (error) {
      console.error('Error starting chat:', error);
      alert('Failed to start conversation. Please try again.');
    } finally {
      showLoading(false);
    }
  }

  /**
   * Send user message
   */
  async function sendMessage() {
    if (conversationEnded) {
      alert('Conversation has ended');
      return;
    }

    const messageText = messageInput.value.trim();
    if (!messageText) {
      return;
    }

    // Disable input
    messageInput.disabled = true;
    sendBtn.disabled = true;

    // Add message to UI
    addMessage('resident', messageText);
    messageInput.value = '';

    try {
      showLoading(true);
      const response = await fetch(`${CONFIG.API_URL}/api/chat/message`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          character: character,
          participant_id: participantId,
          message: messageText
        })
      });

      if (!response.ok) {
        throw new Error('Failed to send message');
      }

      const data = await response.json();

      // Add operator response
      addMessage('operator', data.response);

      // Update turn count
      turnCount = data.turn_count;
      updateTurnCount();

      // Check if conversation ended
      if (data.conversation_ended) {
        console.log('🛑 Conversation ended flag detected');
        handleConversationEnd(data);
      }

      // Log judge and policy info
      if (data.judge) {
        console.log('Stance:', data.judge.stance, 'Confidence:', data.judge.confidence);
      }
      if (data.policy) {
        console.log('Selected Policy:', data.policy);
      }

    } catch (error) {
      console.error('Error sending message:', error);
      alert('Failed to send message. Please try again.');
    } finally {
      showLoading(false);
      messageInput.disabled = false;
      sendBtn.disabled = false;
      messageInput.focus();
    }
  }

  /**
   * Add message to chat
   */
  function addMessage(role, text) {
    utteranceCount++;
    
    // Track operator utterances for post-survey
    if (role === 'operator') {
      operatorUtterances.push({
        number: utteranceCount,
        text: text
      });
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}-message`;
    messageDiv.setAttribute('data-utterance', utteranceCount);
    
    // Add utterance number badge
    const utteranceBadge = document.createElement('div');
    utteranceBadge.className = 'utterance-number';
    utteranceBadge.textContent = `#${utteranceCount}`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = role === 'operator' ? '🚒' : '👤';

    const content = document.createElement('div');
    content.className = 'message-content';
    
    const header = document.createElement('div');
    header.className = 'message-header';
    header.textContent = role === 'operator' ? 'Fire Department Dispatcher' : capitalizeFirst(character);

    const body = document.createElement('div');
    body.className = 'message-body';
    body.textContent = text;

    const timestamp = document.createElement('div');
    timestamp.className = 'message-timestamp';
    timestamp.textContent = new Date().toLocaleTimeString();

    content.appendChild(header);
    content.appendChild(body);
    content.appendChild(timestamp);

    messageDiv.appendChild(utteranceBadge);
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(content);

    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  /**
   * Update turn counter
   */
  function updateTurnCount() {
    turnCountDisplay.textContent = `Turn: ${turnCount} / 5`;
    
    // Visual warning when approaching limit
    if (turnCount >= 4) {
      turnCountDisplay.classList.add('warning');
    }
  }

  /**
   * Handle conversation end - show post-survey on same page
   */
  function handleConversationEnd(data) {
    console.log('📝 handleConversationEnd called');
    conversationEnded = true;
    messageInput.disabled = true;
    sendBtn.disabled = true;

    console.log('Conversation ended, will show post-survey after delay');
    console.log('Total operator utterances:', operatorUtterances.length);
    
    // Enable scrolling for the page
    document.body.classList.add('survey-active');
    const chatContainer = document.querySelector('.chat-container');
    if (chatContainer) {
      chatContainer.classList.add('survey-active');
    }
    
    // Hide chat input
    const chatInputContainer = document.getElementById('chat-input-container');
    if (chatInputContainer) {
      console.log('✓ Hiding chat input container');
      chatInputContainer.style.display = 'none';
    } else {
      console.error('❌ Chat input container not found');
    }
    
    // Wait 3 seconds for participant to read the operator's final message
    setTimeout(() => {
      // Show a brief transition message
      showTransitionMessage();
      
      // Then wait another 3.5 seconds before showing post-survey
      setTimeout(() => {
      // Show post-survey section
      const postSurveySection = document.getElementById('post-survey-section');
      if (postSurveySection) {
        console.log('✓ Post-survey section found, showing it');
        postSurveySection.classList.remove('hidden');
        
        // Populate utterance checkboxes for operator messages
        populateUtteranceCheckboxes();
        
        // Setup post-survey form handlers
        setupPostSurveyForm();
        
        // Scroll to post-survey
        setTimeout(() => {
          console.log('📍 Scrolling to post-survey section');
          postSurveySection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 300);
      } else {
        console.error('❌ Post-survey section not found!');
      }
    }, 3500); // 3.5 second delay for post-survey to appear
    }, 3000); // 3 second delay to read operator's final message
  }
  
  /**
   * Show transition message between conversation end and survey
   */
  function showTransitionMessage() {
    const messagesContainer = document.getElementById('chat-messages');
    if (!messagesContainer) return;
    
    const transitionDiv = document.createElement('div');
    transitionDiv.className = 'conversation-end-notice';
    transitionDiv.innerHTML = `
      <div class="end-notice-content">
        <div class="end-notice-icon">✓</div>
        <h3>Conversation Complete</h3>
        <p>Please take a moment to review the conversation above.</p>
        <p class="end-notice-subtext">A brief survey will appear shortly...</p>
      </div>
    `;
    
    messagesContainer.appendChild(transitionDiv);
    
    // Scroll to show the notice
    setTimeout(() => {
      transitionDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }, 100);
  }
  
  /**
   * Populate checkboxes with operator utterances
   */
  function populateUtteranceCheckboxes() {
    console.log('📋 Populating utterance checkboxes');
    const checkboxContainer = document.getElementById('utterance-checkboxes');
    if (!checkboxContainer) {
      console.error('❌ Utterance checkboxes container not found');
      return;
    }
    
    checkboxContainer.innerHTML = '';
    console.log(`Creating ${operatorUtterances.length} checkbox options`);
    
    operatorUtterances.forEach(utterance => {
      const label = document.createElement('label');
      label.className = 'checkbox-option';
      
      const checkbox = document.createElement('input');
      checkbox.type = 'checkbox';
      checkbox.name = 'unnaturalUtterances';
      checkbox.value = utterance.number;
      
      const text = document.createElement('span');
      text.textContent = `#${utterance.number}: "${utterance.text.substring(0, 60)}${utterance.text.length > 60 ? '...' : ''}"`;
      
      label.appendChild(checkbox);
      label.appendChild(text);
      checkboxContainer.appendChild(label);
    });
    
    console.log('✓ Utterance checkboxes populated');
  }
  
  /**
   * Setup post-survey form event handlers
   */
  function setupPostSurveyForm() {
    const form = document.getElementById('post-survey-form');
    if (!form) return;
    
    // Show/hide conditional fields based on responses
    const willingRadios = document.querySelectorAll('input[name="willing"]');
    const willingYesDetails = document.getElementById('willing-yes-details');
    const willingNoDetails = document.getElementById('willing-no-details');
    
    willingRadios.forEach(radio => {
      radio.addEventListener('change', () => {
        // Hide all conditional fields first
        willingYesDetails.classList.add('hidden');
        willingNoDetails.classList.add('hidden');
        
        // Show appropriate field based on selection
        if (radio.value === 'yes') {
          willingYesDetails.classList.remove('hidden');
        } else if (radio.value === 'no') {
          willingNoDetails.classList.remove('hidden');
        }
        // 'maybe' shows no conditional field
      });
    });
    
    const naturalnessRadios = document.querySelectorAll('input[name="naturalness"]');
    const unnaturalDetails = document.getElementById('unnatural-details');
    const unnaturalLabel = unnaturalDetails.querySelector('.sub-label');
    
    naturalnessRadios.forEach(radio => {
      radio.addEventListener('change', () => {
        // Show checkboxes for neutral and below
        if (radio.value === 'neutral' || 
            radio.value === 'somewhat-natural' ||
            radio.value === 'somewhat-unnatural' || 
            radio.value === 'very-unnatural') {
          unnaturalDetails.classList.remove('hidden');
          
          // Update label based on selection
          if (radio.value === 'very-natural') {
            unnaturalLabel.textContent = 'Which utterances felt particularly natural? (Optional)';
          } else if (radio.value === 'somewhat-natural') {
            unnaturalLabel.textContent = 'Which utterances could be improved? (Select all that apply)';
          } else if (radio.value === 'neutral') {
            unnaturalLabel.textContent = 'Which utterances could be improved? (Select all that apply)';
          } else {
            unnaturalLabel.textContent = 'Which utterances felt unnatural? (Select all that apply)';
          }
        } else {
          unnaturalDetails.classList.add('hidden');
        }
      });
    });
    
    // Form submission
    form.addEventListener('submit', handlePostSurveySubmit);
    
    // Enable submit button when both required questions are answered
    const submitBtn = form.querySelector('button[type="submit"]');
    const checkFormValidity = () => {
      const willing = form.querySelector('input[name="willing"]:checked');
      const naturalness = form.querySelector('input[name="naturalness"]:checked');
      
      if (willing && naturalness) {
        submitBtn.disabled = false;
        submitBtn.classList.remove('disabled');
      } else {
        submitBtn.disabled = true;
        submitBtn.classList.add('disabled');
      }
    };
    
    // Check validity on radio button changes
    const allRadios = form.querySelectorAll('input[type="radio"]');
    allRadios.forEach(radio => {
      radio.addEventListener('change', checkFormValidity);
    });
    
    // Initial check
    checkFormValidity();
  }
  
  /**
   * Handle post-survey form submission
   */
  async function handlePostSurveySubmit(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    
    // Validate required fields
    const willing = formData.get('willing');
    const naturalness = formData.get('naturalness');
    
    if (!willing) {
      alert('Please answer Question 1: Were you willing to be rescued based on this conversation?');
      // Scroll to the question
      const question1 = document.querySelector('input[name="willing"]').closest('.survey-question');
      question1.scrollIntoView({ behavior: 'smooth', block: 'center' });
      return;
    }
    
    if (!naturalness) {
      alert('Please answer Question 2: How natural and coherent did this conversation feel overall?');
      // Scroll to the question
      const question2 = document.querySelector('input[name="naturalness"]').closest('.survey-question');
      question2.scrollIntoView({ behavior: 'smooth', block: 'center' });
      return;
    }
    
    // Collect unnatural utterances
    const unnaturalUtterances = Array.from(formData.getAll('unnaturalUtterances')).map(Number);
    
    const surveyData = {
      sessionId: sessionId,
      participantId: participantId,
      character: character || 'self',  // 'self' for non-role-play, character name for role-play
      conversationNumber: parseInt(sessionStorage.getItem('completedConversations') || '0') + 1,
      timestamp: new Date().toISOString(),
      willing: willing,
      willingYesDetails: formData.get('willingYesDetails') || '',
      willingNoDetails: formData.get('willingNoDetails') || '',
      naturalness: naturalness,
      unnaturalUtterances: unnaturalUtterances
    };
    
    try {
      showLoading(true);
      
      const response = await fetch(`${CONFIG.API_URL}/api/post-survey`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(surveyData)
      });
      
      if (!response.ok) {
        throw new Error('Failed to submit post-survey');
      }
      
      console.log('Post-survey submitted successfully');
      
      // Update completed conversations count
      const currentCount = parseInt(sessionStorage.getItem('completedConversations') || '0');
      const completedConversations = currentCount + 1;
      
      console.log('[POST-SURVEY] Current count:', currentCount);
      console.log('[POST-SURVEY] New count:', completedConversations);
      console.log('[POST-SURVEY] isRolePlay:', isRolePlay);
      console.log('[POST-SURVEY] conversationNumber:', conversationNumber);
      
      sessionStorage.setItem('completedConversations', completedConversations.toString());
      
      showLoading(false);
      
      // Redirect based on conversation count
      if (completedConversations >= 6) {
        // All 6 conversations complete (3 non-role-play + 3 role-play)
        // Call complete-study endpoint to get CCC confirmation number
        try {
          const completeResponse = await fetch(`${CONFIG.API_URL}/api/complete-study`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              participantId: participantId
            })
          });

          if (completeResponse.ok) {
            const completeData = await completeResponse.json();
            // Show completion modal with confirmation number
            showCompletionModal(completeData.confirmation_number);
          } else {
            throw new Error('Failed to complete study');
          }
        } catch (error) {
          console.error('Error completing study:', error);
          alert('Study complete! Thank you for your participation.');
          window.location.href = 'landing.html';
        }
      } else if (completedConversations === 3) {
        // Completed Session 1, moving to Session 2 (character selection)
        alert('Session 1 complete! Now moving to Session 2: Role-Play conversations.');
        window.location.href = 'scenario.html';
      } else if (completedConversations < 3) {
        // Still in Session 1 (non-role-play), go directly to next conversation
        const nextConversation = completedConversations + 1;
        console.log('[REDIRECT] Going to Session 1, conversation:', nextConversation);
        alert(`Session 1: Survey submitted! Proceeding to conversation ${nextConversation} of 3.`);
        window.location.href = `chat.html?type=non-roleplay&conversation=${nextConversation}`;
      } else {
        // In Session 2 (role-play), go directly to next conversation with same character
        const nextConversation = completedConversations - 3 + 1;
        const selectedCharacter = sessionStorage.getItem('selectedCharacter');
        alert(`Survey submitted! Proceeding to conversation ${nextConversation} of 3.`);
        window.location.href = `chat.html?type=roleplay&conversation=${nextConversation}&character=${selectedCharacter}`;
      }
      
    } catch (error) {
      console.error('Error submitting post-survey:', error);
      alert('Error submitting survey. Please try again.');
      showLoading(false);
    }
  }

  /**
   * Show/hide loading overlay
   */
  function showLoading(show) {
    if (show) {
      loadingOverlay.classList.remove('hidden');
    } else {
      loadingOverlay.classList.add('hidden');
    }
  }

  /**
   * Show completion modal with confirmation number
   */
  function showCompletionModal(confirmationNumber) {
    const modal = document.createElement('div');
    modal.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(0, 0, 0, 0.8);
      display: flex;
      justify-content: center;
      align-items: center;
      z-index: 10000;
    `;

    modal.innerHTML = `
      <div style="
        background: white;
        padding: 3rem;
        border-radius: 16px;
        max-width: 600px;
        width: 90%;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
      ">
        <div style="font-size: 4rem; margin-bottom: 1rem;">🎉</div>
        <h2 style="margin-top: 0; color: #4CAF50; font-size: 2rem;">Study Complete!</h2>
        <p style="color: #333; line-height: 1.6; margin: 1.5rem 0; font-size: 1.1rem;">
          Thank you for completing all 6 conversations!<br>
          Your contribution is greatly appreciated.
        </p>
        <p style="color: #333; font-weight: 600; margin: 1rem 0;">
          Your confirmation number is:
        </p>
        <div style="
          background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
          padding: 1.5rem;
          border-radius: 12px;
          font-size: 2rem;
          font-weight: bold;
          color: white;
          margin: 1.5rem 0;
          letter-spacing: 2px;
        ">${confirmationNumber}</div>
        <p style="color: #666; font-size: 0.95rem; margin: 1rem 0;">
          Please save this number for your records.
        </p>
        <button onclick="window.location.href='landing.html'" style="
          margin-top: 2rem;
          padding: 1rem 3rem;
          background: #4CAF50;
          color: white;
          border: none;
          border-radius: 8px;
          font-size: 1.1rem;
          font-weight: 600;
          cursor: pointer;
          transition: background 0.2s ease;
        " onmouseover="this.style.background='#45a049'" onmouseout="this.style.background='#4CAF50'">
          Finish
        </button>
      </div>
    `;

    document.body.appendChild(modal);

    // Clear session storage after a delay
    setTimeout(() => {
      sessionStorage.clear();
    }, 1000);
  }

  /**
   * Show brief message to user (for paste notification)
   */
  function showBriefMessage(message) {
    // Check if notification already exists
    let notification = document.getElementById('paste-notification');
    
    if (!notification) {
      notification = document.createElement('div');
      notification.id = 'paste-notification';
      notification.style.cssText = `
        position: fixed;
        top: 20px;
        left: 50%;
        transform: translateX(-50%);
        background: #ff6b35;
        color: white;
        padding: 12px 24px;
        border-radius: 8px;
        font-size: 14px;
        font-weight: 500;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        z-index: 10000;
        opacity: 0;
        transition: opacity 0.3s ease;
      `;
      document.body.appendChild(notification);
    }
    
    notification.textContent = message;
    
    // Fade in
    setTimeout(() => {
      notification.style.opacity = '1';
    }, 10);
    
    // Fade out and remove after 2 seconds
    setTimeout(() => {
      notification.style.opacity = '0';
      setTimeout(() => {
        if (notification.parentNode) {
          notification.parentNode.removeChild(notification);
        }
      }, 300);
    }, 2000);
  }

  /**
   * Capitalize first letter
   */
  function capitalizeFirst(str) {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1);
  }

  // Initialize on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
