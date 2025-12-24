// Survey Form Handler
(function() {
  'use strict';

  console.log('=== SURVEY.JS LOADED ===');

  // Use global config if available, otherwise use default
  const CONFIG = window.APP_CONFIG || {
    API_URL: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
      ? 'http://localhost:8001' 
      : 'https://your-backend-url.onrender.com',
  };

  console.log('API_URL configured as:', CONFIG.API_URL);

  // Handle page refresh - clear only survey-specific data, keep nothing
  const perfData = performance.getEntriesByType('navigation')[0];
  if (perfData && perfData.type === 'reload') {
    console.log('🔄 Page refresh detected on survey page - clearing all data and restarting survey');
    sessionStorage.clear();
    // Page will reload with clean state
  }

  // Use real keyboard typing sound
  let typingAudio = null;
  let audioInitialized = false;

  // Preload audio immediately to avoid delay
  function preloadAudio() {
    if (!typingAudio) {
      console.log('Preloading audio...');
      typingAudio = new Audio('media/keyboard-typing-fast-371229.mp3');
      typingAudio.volume = 0.3;
      typingAudio.loop = true;
      typingAudio.playbackRate = 1.0;
      typingAudio.preload = 'auto'; // Preload the audio
      
      typingAudio.addEventListener('canplaythrough', () => {
        console.log('Audio ready to play');
      });
      
      typingAudio.addEventListener('error', (e) => {
        console.error('Audio error:', e);
      });
      
      // Trigger loading
      typingAudio.load();
    }
  }

  function initAudio() {
    console.log('initAudio called, current state:', { typingAudio: !!typingAudio, audioInitialized });
    
    // Ensure audio is preloaded
    if (!typingAudio) {
      preloadAudio();
    }
    
    // Try to play and immediately pause to "unlock" audio
    console.log('Attempting to play audio...');
    const playPromise = typingAudio.play();
    if (playPromise !== undefined) {
      return playPromise.then(() => {
        console.log('Audio play successful, pausing...');
        typingAudio.pause();
        typingAudio.currentTime = 0;
        audioInitialized = true;
        console.log('Audio initialized successfully!');
        return true;
      }).catch(e => {
        console.log('Audio init failed:', e);
        audioInitialized = false;
        return false;
      });
    }
    return Promise.resolve(false);
  }

  function playTypingSound() {
    console.log('playTypingSound called, state:', { 
      hasAudio: !!typingAudio, 
      initialized: audioInitialized, 
      paused: typingAudio ? typingAudio.paused : 'no audio' 
    });
    
    if (!typingAudio) {
      console.log('Cannot play - audio not loaded');
      return;
    }
    
    try {
      // If not already playing, start the audio immediately
      if (typingAudio.paused) {
        console.log('Starting audio playback...');
        typingAudio.currentTime = 0;
        
        // Start playing immediately without waiting for initialization check
        const playPromise = typingAudio.play();
        if (playPromise !== undefined) {
          playPromise.then(() => {
            console.log('Audio playing successfully!');
            audioInitialized = true;
          }).catch(e => {
            console.error('Audio playback failed:', e);
            // Audio might be blocked by browser, but don't stop typing
          });
        }
      } else {
        console.log('Audio already playing');
      }
    } catch (e) {
      console.error('Audio playback exception:', e);
    }
  }
  
  function stopTypingSound() {
    console.log('stopTypingSound called');
    if (typingAudio && !typingAudio.paused) {
      console.log('Stopping audio...');
      typingAudio.pause();
      typingAudio.currentTime = 0;
    }
  }

  // Show a prompt to enable sound
  function showAudioPrompt() {
    // Check if prompt already exists
    if (document.getElementById('audio-prompt')) {
      return;
    }
    
    const prompt = document.createElement('div');
    prompt.id = 'audio-prompt';
    prompt.style.cssText = `
      position: fixed;
      top: 4rem;
      left: 50%;
      transform: translateX(-50%);
      z-index: 1000;
      background: linear-gradient(135deg, #ff6b35 0%, #ff8555 100%);
      color: white;
      padding: 1rem 2rem;
      border-radius: 50px;
      box-shadow: 0 8px 30px rgba(255, 107, 53, 0.6);
      font-size: 1rem;
      font-weight: 600;
      cursor: pointer;
      transition: transform 0.2s ease, opacity 0.3s ease;
      animation: slideDown 0.5s ease-out, pulse 2s ease-in-out infinite 1s;
    `;
    prompt.innerHTML = `
      <span style="font-size: 1.3rem; margin-right: 0.5rem;">🔊</span>
      <span>Click anywhere to enable sounds for the full experience</span>
    `;
    document.body.appendChild(prompt);
    
    prompt.addEventListener('mouseenter', () => {
      prompt.style.transform = 'translateX(-50%) scale(1.05)';
    });
    
    prompt.addEventListener('mouseleave', () => {
      prompt.style.transform = 'translateX(-50%) scale(1)';
    });
    
    const enableAudio = async () => {
      console.log('Enabling audio after user interaction...');
      
      // Check if prompt still exists and is visible
      if (!prompt.parentNode) {
        console.log('Prompt already removed');
        return;
      }
      
      await initAudio();
      console.log('Audio initialized, initialized flag:', audioInitialized);
      prompt.style.opacity = '0';
      setTimeout(() => {
        if (prompt.parentNode) {
          prompt.remove();
        }
      }, 300);
    };
    
    // Also make the prompt itself clickable
    prompt.addEventListener('click', enableAudio);
    
    // Delay attaching document-level listeners to avoid immediate triggering
    // from the navigation click
    setTimeout(() => {
      document.addEventListener('click', enableAudio, { once: true });
      document.addEventListener('keydown', enableAudio, { once: true });
    }, 500);
  }

  // Typewriter effect function with sound and cursor
  function typeWriter(element, text, speed = 30) {
    return new Promise((resolve) => {
      try {
        let i = 0;
        element.textContent = '';
        element.style.opacity = '1';
        
        // Add cursor span
        const cursor = document.createElement('span');
        cursor.className = 'typing-cursor';
        cursor.textContent = '|';
        element.appendChild(cursor);
        
        // Start typing sound immediately, don't wait
        playTypingSound();
        
        function type() {
          try {
            if (i < text.length) {
              // Insert character before cursor
              const currentText = text.substring(0, i + 1);
              element.textContent = currentText;
              element.appendChild(cursor);
              
              i++;
              setTimeout(type, speed);
            } else {
              // Stop typing sound when done
              stopTypingSound();
              // Remove cursor when done
              cursor.remove();
              resolve();
            }
          } catch (e) {
            console.error('Error in type function:', e);
            stopTypingSound();
            // Show full text immediately if error
            element.textContent = text;
            element.style.opacity = '1';
            resolve();
          }
        }
        type();
      } catch (e) {
        console.error('Error in typeWriter:', e);
        stopTypingSound();
        // Fallback: show text immediately
        element.textContent = text;
        element.style.opacity = '1';
        resolve();
      }
    });
  }

  // Initialize typewriter animations
  async function initTypewriterAnimations() {
    console.log('Starting typewriter animations...');
    
    // Always show the audio prompt initially to inform users
    showAudioPrompt();
    
    // Try to initialize audio in the background
    initAudio().then(ready => {
      console.log('Audio initialization result:', ready);
    }).catch(e => {
      console.log('Audio init error:', e);
    });
    
    const welcomeH1 = document.querySelector('.welcome-section h1');
    const introParagraphs = document.querySelectorAll('.intro-text');
    const warningBanner = document.querySelector('.warning-banner');
    
    console.log('Found elements:', { welcomeH1, introParagraphs: introParagraphs.length, warningBanner });
    
    if (welcomeH1) {
      const h1Text = welcomeH1.textContent;
      console.log('Typing h1:', h1Text);
      await typeWriter(welcomeH1, h1Text, 150);
      await new Promise(resolve => setTimeout(resolve, 300)); // Small pause
    }
    
    for (const para of introParagraphs) {
      const paraText = para.textContent.trim();
      console.log('Typing paragraph:', paraText.substring(0, 50) + '...');
      await typeWriter(para, paraText, 50);
      await new Promise(resolve => setTimeout(resolve, 300)); // Small pause between paragraphs
    }
    
    // Show the warning banner after welcome section is done
    if (warningBanner) {
      warningBanner.style.display = 'flex';
      await new Promise(resolve => setTimeout(resolve, 500)); // Pause before banner
      
      const h4 = warningBanner.querySelector('.content h4');
      const p = warningBanner.querySelector('.content p');
      
      if (h4) {
        const h4Text = h4.textContent;
        console.log('Typing banner h4:', h4Text);
        await typeWriter(h4, h4Text, 100);
        await new Promise(resolve => setTimeout(resolve, 300)); // Small pause
      }
      
      if (p) {
        const pText = p.textContent.trim();
        console.log('Typing banner p:', pText.substring(0, 50) + '...');
        await typeWriter(p, pText, 40);
      }
    }
    
    console.log('Typewriter animations complete!');
  }

  // Preload audio immediately (don't wait for user interaction)
  preloadAudio();

  // Trigger backend model preloading when survey page loads
  function triggerModelPreload() {
    console.log('🔄 Triggering backend model preload...');
    fetch(`${CONFIG.API_URL}/api/preload-models`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    })
    .then(res => res.json())
    .then(data => {
      console.log('✅ Backend preload started:', data.message);
    })
    .catch(err => {
      console.warn('⚠️ Preload request failed (non-critical):', err);
    });
  }

  // Wait for DOM to be ready
  document.addEventListener('DOMContentLoaded', function() {
    console.log('=== SURVEY DOM READY ===');
    
    // Trigger model preloading immediately (will be ready by Session 2)
    triggerModelPreload();
    
    // Create temporary participant ID if doesn't exist (for exit tracking)
    if (!sessionStorage.getItem('participantId')) {
      const tempId = 'temp_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
      sessionStorage.setItem('participantId', tempId);
      console.log('Generated temporary participant ID:', tempId);
    }
    
    // Start typewriter animations
    initTypewriterAnimations();
    
    // Development mode: Clear session storage if ?reset=true in URL
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('reset') === 'true') {
      console.log('🔄 Reset parameter detected - clearing session storage');
      sessionStorage.clear();
      // Remove the reset parameter from URL
      window.history.replaceState({}, document.title, window.location.pathname);
      console.log('✓ Session storage cleared');
    }
    const form = document.getElementById('surveyForm');
    const loadingOverlay = document.getElementById('loadingOverlay');

    if (!form) {
      console.error('Survey form not found');
      return;
    }

    // Record survey start time
    if (!sessionStorage.getItem('surveyStartTime')) {
      sessionStorage.setItem('surveyStartTime', Date.now());
    }

    // Form submission handler
    form.addEventListener('submit', async function(e) {
      e.preventDefault();
      
      console.log('=== SURVEY FORM SUBMITTED ===');
      
      // Collect form data
      const formData = collectFormData();
      console.log('Form data collected:', formData);
      
      // Validate form
      if (!validateForm(formData)) {
        console.log('❌ Form validation failed');
        // Validation errors are shown in showValidationErrors function
        return;
      }
      
      console.log('✓ Form validation passed');

      // Show loading overlay
      loadingOverlay.classList.remove('hidden');

      try {
        console.log('Submitting to backend...');
        // Submit to backend
        const response = await submitSurvey(formData);
        console.log('Backend response:', response);
        
        if (response.success) {
          console.log('✓ Survey submitted successfully');
          console.log('Participant ID:', response.participantId);
          
          // Store participant ID in session storage
          sessionStorage.setItem('participantId', response.participantId);
          sessionStorage.setItem('participantNickname', formData.background.nickname || 'Participant');
          
          // Initialize conversation tracking (start fresh)
          sessionStorage.setItem('completedConversations', '0');
          
          console.log('✓ Stored in sessionStorage');
          console.log('✓ Initialized completedConversations to 0');
          
          // NEW FLOW: Start with non-role-play conversations (1-3), then role-play conversations (4-6)
          // After survey, redirect to scenario page to show Session 1 introduction
          console.log('Redirecting to Session 1 scenario introduction...');
          window.location.href = 'scenario.html?session=1';
        } else {
          throw new Error(response.message || 'Failed to submit survey');
        }
      } catch (error) {
        console.error('❌ Error submitting survey:', error);
        alert('There was an error submitting your survey. Please try again.');
        loadingOverlay.classList.add('hidden');
      }
    });

    // Add smooth scroll behavior for better UX
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
      anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
          target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      });
    });

    // Add visual feedback for radio button selections
    setupRadioFeedback();
    
    // Mark questions as answered
    setupAnsweredTracking();
  });

  /**
   * Collect all form data into a structured object
   */
  function collectFormData() {
    const form = document.getElementById('surveyForm');
    const formData = new FormData(form);
    
    const data = {
      timestamp: new Date().toISOString(),
      background: {
        email: formData.get('email') || '',
        nickname: formData.get('nickname') || '',
        age: formData.get('age') || '',
        gender: formData.get('gender') || '',
        education: formData.get('education') || '',
        occupation: formData.get('occupation') || '',
        ideology: formData.get('ideology') || ''
      },
      personality: {},
      moral: {},
      specialNeeds: {
        condition: formData.get('special_needs_condition') || '',
        responsible: formData.get('special_needs_responsible') || '',
        vehicle: formData.get('special_needs_vehicle') || '',
        details: formData.get('special_needs_details') || ''
      }
    };

    // Collect personality trait responses (10 questions)
    for (let i = 1; i <= 10; i++) {
      data.personality[`q${i}`] = formData.get(`personality_${i}`) || '';
    }

    // Collect moral foundation responses (12 questions)
    for (let i = 1; i <= 12; i++) {
      data.moral[`q${i}`] = formData.get(`moral_${i}`) || '';
    }

    return data;
  }

  /**
   * Calculate standard deviation of responses
   */
  function calculateStandardDeviation(values) {
    const n = values.length;
    if (n === 0) return 0;
    
    const mean = values.reduce((sum, val) => sum + val, 0) / n;
    const squaredDiffs = values.map(val => Math.pow(val - mean, 2));
    const variance = squaredDiffs.reduce((sum, val) => sum + val, 0) / n;
    
    return Math.sqrt(variance);
  }

  /**
   * Check for dominant response pattern (one value appears too frequently)
   */
  function checkDominantResponse(values, threshold = 0.8) {
    const counts = {};
    values.forEach(v => counts[v] = (counts[v] || 0) + 1);
    
    const maxCount = Math.max(...Object.values(counts));
    const dominantValue = Object.keys(counts).find(k => counts[k] === maxCount);
    
    return {
      isDominant: maxCount / values.length > threshold,
      percentage: Math.round((maxCount / values.length) * 100),
      value: dominantValue,
      count: maxCount,
      total: values.length
    };
  }

  /**
   * Enhanced form validation with statistical checks
   */
  function validateForm(data) {
    const errors = [];
    
    // Check required fields
    if (!data.background.email || data.background.email.trim() === '') {
      errors.push('Please enter your email address');
    } else {
      // Validate email format
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(data.background.email)) {
        errors.push('Please enter a valid email address');
      }
    }
    
    if (!data.background.nickname || data.background.nickname.trim() === '') {
      errors.push('Please enter a nickname');
    }
    
    if (!data.background.age || data.background.age.trim() === '') {
      errors.push('Please enter your age');
    }
    
    if (!data.background.gender) {
      errors.push('Please select your gender');
    }
    
    if (!data.background.education) {
      errors.push('Please select your education level');
    }
    
    if (!data.background.ideology) {
      errors.push('Please select your ideology on the scale');
    }
    
    // Check all personality questions are answered
    const personalityAnswers = Object.values(data.personality);
    if (personalityAnswers.length !== 10 || personalityAnswers.some(v => !v)) {
      errors.push('Please answer all 10 personality trait questions');
    }
    
    // Check all moral foundation questions are answered
    const moralAnswers = Object.values(data.moral);
    if (moralAnswers.length !== 12 || moralAnswers.some(v => !v)) {
      errors.push('Please answer all 12 moral foundation questions');
    }
    
    // Check special needs questions
    if (!data.specialNeeds.condition) {
      errors.push('Please answer the physical/medical condition question');
    }
    
    if (!data.specialNeeds.responsible) {
      errors.push('Please answer the responsibility for others question');
    }
    
    if (!data.specialNeeds.vehicle) {
      errors.push('Please answer the vehicle/assistance question');
    }
    
    // ENHANCED VALIDATION: Check personality questions quality
    if (personalityAnswers.length === 10 && personalityAnswers.every(v => v)) {
      const personalityValues = personalityAnswers.map(v => parseInt(v));
      
      // Check 1: All same (original check)
      const uniqueValues = new Set(personalityValues);
      if (uniqueValues.size === 1) {
        errors.push('⚠️ You have selected the same response for all personality questions. Please review your answers to ensure they accurately reflect your traits.');
      }
      
      // Check 2: Standard deviation must be > 0.8
      const stdDev = calculateStandardDeviation(personalityValues);
      if (stdDev < 0.8) {
        errors.push(`⚠️ Your personality responses show very little variation (SD: ${stdDev.toFixed(2)}). Please ensure each answer reflects your genuine traits. Try to use more of the rating scale.`);
      }
      
      // Check 3: No single value should appear in >80% of responses
      const dominantCheck = checkDominantResponse(personalityValues, 0.8);
      if (dominantCheck.isDominant) {
        errors.push(`⚠️ You selected "${dominantCheck.value}" for ${dominantCheck.percentage}% (${dominantCheck.count}/${dominantCheck.total}) of personality questions. Please use the full scale to reflect the variety in your traits.`);
      }
    }
    
    // REMOVED: Enhanced validation for moral foundation questions
    // Moral foundations may naturally have similar responses, so we only check that all questions are answered
    // The personality section still has enhanced validation to ensure quality responses
    
    // ENHANCED VALIDATION: Check survey completion time
    const startTime = parseInt(sessionStorage.getItem('surveyStartTime'));
    if (startTime) {
      const timeSpent = (Date.now() - startTime) / 1000; // seconds
      const minTime = 60; // 1 minute
      
      if (timeSpent < minTime) {
        errors.push(`⚠️ You completed the survey in ${Math.round(timeSpent)} seconds. Please take more time to read each question carefully and respond thoughtfully. This ensures high-quality research data.`);
      }
    }
    
    // Show errors if any
    if (errors.length > 0) {
      showValidationErrors(errors);
      return false;
    }
    
    return true;
  }
  
  /**
   * Display validation errors to user
   */
  function showValidationErrors(errors) {
    const errorHtml = `
      <div style="
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: white;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        max-width: 500px;
        z-index: 10000;
      ">
        <h3 style="color: #e74c3c; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem;">
          <span style="font-size: 1.5rem;">⚠️</span>
          Please Complete the Survey
        </h3>
        <ul style="color: #2c3e50; line-height: 1.8; margin-bottom: 1.5rem; padding-left: 1.5rem;">
          ${errors.map(error => `<li>${error}</li>`).join('')}
        </ul>
        <button onclick="this.parentElement.remove()" style="
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          border: none;
          padding: 0.75rem 2rem;
          border-radius: 25px;
          cursor: pointer;
          font-size: 1rem;
          font-weight: 600;
          width: 100%;
        ">
          Got it, I'll review my answers
        </button>
      </div>
      <div onclick="this.previousElementSibling.remove(); this.remove();" style="
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0,0,0,0.5);
        z-index: 9999;
      "></div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', errorHtml);
    
    // Scroll to first unanswered section
    setTimeout(() => {
      const firstEmptyField = document.querySelector('input:invalid, input[type="radio"]:not(:checked), select:invalid');
      if (firstEmptyField) {
        const section = firstEmptyField.closest('.form-section');
        if (section) {
          section.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      }
    }, 100);
  }

  /**
   * Submit survey data to backend
   */
  async function submitSurvey(data) {
    const apiUrl = `${CONFIG.API_URL}/api/survey`;
    console.log('API URL:', apiUrl);
    console.log('Sending POST request...');
    
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data)
    });

    console.log('Response status:', response.status);
    console.log('Response ok:', response.ok);

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Response error:', errorText);
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const responseData = await response.json();
    return responseData;
  }

  /**
   * Setup visual feedback for radio button selections
   */
  function setupRadioFeedback() {
    // Add animation when radio buttons are selected
    const radioInputs = document.querySelectorAll('input[type="radio"]');
    
    radioInputs.forEach(radio => {
      radio.addEventListener('change', function() {
        const parentContainer = this.closest('.likert-question, .form-group');
        if (parentContainer) {
          // Add a subtle flash effect
          parentContainer.style.transition = 'background-color 0.3s ease';
          const originalBg = window.getComputedStyle(parentContainer).backgroundColor;
          parentContainer.style.backgroundColor = 'rgba(52, 152, 219, 0.1)';
          
          setTimeout(() => {
            parentContainer.style.backgroundColor = originalBg;
          }, 300);
        }
      });
    });
  }

  /**
   * Progress tracking (optional enhancement)
   */
  function trackProgress() {
    const allInputs = document.querySelectorAll('input[type="radio"], input[type="text"], input[type="email"], input[type="number"], select, textarea');
    let answered = 0;
    
    allInputs.forEach(input => {
      if (input.type === 'radio') {
        const name = input.name;
        if (document.querySelector(`input[name="${name}"]:checked`)) {
          answered++;
        }
      } else if (input.value.trim() !== '') {
        answered++;
      }
    });

    const total = allInputs.length;
    const percentage = Math.round((answered / total) * 100);
    
    return { answered, total, percentage };
  }

  /**
   * Setup tracking for answered questions
   */
  function setupAnsweredTracking() {
    // Track Likert scale questions
    const likertQuestions = document.querySelectorAll('.likert-question');
    
    likertQuestions.forEach(question => {
      const radios = question.querySelectorAll('input[type="radio"]');
      
      radios.forEach(radio => {
        radio.addEventListener('change', function() {
          // Mark question as answered
          question.classList.add('answered');
          
          // Check the entire question group
          const name = this.name;
          const isAnswered = document.querySelector(`input[name="${name}"]:checked`) !== null;
          
          if (isAnswered) {
            question.classList.add('answered');
          } else {
            question.classList.remove('answered');
          }
        });
      });
    });
    
    // Track other required fields
    const requiredFields = document.querySelectorAll('input[required], select[required]');
    requiredFields.forEach(field => {
      field.addEventListener('change', function() {
        if (this.value.trim() !== '') {
          this.style.borderColor = '#27ae60';
        } else {
          this.style.borderColor = '';
        }
      });
    });
  }

  // Export for potential use by other scripts
  window.SurveyHandler = {
    collectFormData,
    validateForm,
    submitSurvey,
    trackProgress
  };
})();

