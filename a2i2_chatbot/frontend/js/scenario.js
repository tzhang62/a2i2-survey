// Scenario Page Handler
(function() {
  'use strict';

  console.log('=== SCENARIO.JS LOADED ===');

  let selectedCharacter = null;
  
  // API Configuration
  const CONFIG = window.APP_CONFIG || {
    API_URL: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
      ? 'http://localhost:8001' 
      : 'https://your-backend-url.onrender.com',
  };
  
  /**
   * Typewriter effect for scenario text
   */
  function typewriterEffect(element, text, speed = 50) {
    return new Promise((resolve) => {
      let i = 0;
      element.textContent = '';
      element.style.opacity = '1';
      
      function type() {
        if (i < text.length) {
          element.textContent += text.charAt(i);
          i++;
          setTimeout(type, speed);
        } else {
          resolve();
        }
      }
      type();
    });
  }

  /**
   * Display Session 1 (Non-Role-Play) scenario introduction
   */
  async function displaySession1Scenario() {
    const scenarioContent = document.querySelector('.scenario-content');
    if (!scenarioContent) return;
    
    // Get survey data for personalized scenario text
    const occupation = sessionStorage.getItem('occupation') || 'your daily activities';
    
    // Generate personalized scenario text with subtle emphasis
    const scenarioText = `A wildfire is spreading rapidly through neighborhoods near your area.\n\nYou are at home going about ${occupation} when your phone suddenly rings.\n\nThe caller ID shows the local fire department...`;
    
    // Display full-screen video with minimal UI
    scenarioContent.innerHTML = `
      <div class="fullscreen-video-container">
        <!-- Full screen video background -->
        <video class="fullscreen-video" autoplay muted loop playsinline>
          <source src="media/wildfire-scenario.mov" type="video/mp4">
        </video>
        
        <!-- Dark overlay for text readability -->
        <div class="video-overlay"></div>
        
        <!-- Scenario text (hidden initially, will appear with typewriter effect) -->
        <div class="cinematic-text" id="scenario-text" style="opacity: 0;">
        </div>
        
        <!-- Answer button (appears after text finishes) -->
        <div class="cinematic-button" id="answer-button-container" style="opacity: 0; pointer-events: none;">
          <button class="answer-call-button pulse-animation" id="answer-call-button">
            📞 Answer the Call
          </button>
        </div>
        
        <!-- Sound prompt banner -->
        <div class="sound-prompt-banner" id="sound-prompt">
          <div class="sound-prompt-content">
            <span class="sound-prompt-icon">🔊</span>
            <span class="sound-prompt-text">Click anywhere to enable sound for the full experience</span>
          </div>
        </div>
        
        <!-- Media controls (bottom corner) -->
        <div class="video-sound-controls">
          <audio id="session1-fire-ambient" loop preload="auto">
            <source src="media/fire-ambient.mp3" type="audio/mpeg">
          </audio>
          <audio id="session1-phone-ring" preload="auto">
            <source src="media/phone-ring.mp3" type="audio/mpeg">
          </audio>
          <button class="minimal-sound-button" id="sound-toggle">
            <span class="sound-icon">🔊</span>
          </button>
        </div>
      </div>
    `;
    
    // Initialize ambient sound only (NOT phone ring)
    const fireAmbient = document.getElementById('session1-fire-ambient');
    const phoneRing = document.getElementById('session1-phone-ring');
    const soundPrompt = document.getElementById('sound-prompt');
    let soundEnabled = false;
    
    // Always show the sound prompt initially
    if (soundPrompt) {
      soundPrompt.style.display = 'flex';
    }
    
    // Wait for audio to be loaded before attempting playback
    const initializeAudio = () => {
      if (fireAmbient) {
        // Ensure normal playback rate
        fireAmbient.playbackRate = 1.0;
        fireAmbient.volume = 0.3;
        
        // Wait for audio to be ready
        if (fireAmbient.readyState >= 2) {
          // Audio is loaded enough to play
          fireAmbient.play()
            .then(() => {
              console.log('Ambient sound autoplaying');
              soundEnabled = true;
            })
            .catch(e => {
              console.log('Ambient sound autoplay blocked');
              soundEnabled = false;
            });
        } else {
          // Wait for audio to be loaded
          fireAmbient.addEventListener('canplay', () => {
            fireAmbient.play()
              .then(() => {
                console.log('Ambient sound autoplaying after load');
                soundEnabled = true;
              })
              .catch(e => {
                console.log('Ambient sound autoplay blocked');
                soundEnabled = false;
              });
          }, { once: true });
        }
      }
      
      // Ensure phone ring is also at normal speed
      if (phoneRing) {
        phoneRing.playbackRate = 1.0;
        phoneRing.volume = 0.5;
      }
    };
    
    // Initialize audio with a small delay to ensure DOM is ready
    setTimeout(initializeAudio, 100);
    
    // Enable sound on user interaction
    const enableSound = () => {
      if (!soundEnabled && fireAmbient) {
        // Ensure audio is ready and at normal speed
        fireAmbient.playbackRate = 1.0;
        fireAmbient.volume = 0.3;
        
        // Function to play audio
        const playAudio = () => {
          fireAmbient.play()
            .then(() => {
              console.log('Sound enabled by user interaction');
              soundEnabled = true;
              if (soundPrompt) {
                soundPrompt.style.opacity = '0';
                setTimeout(() => {
                  soundPrompt.style.display = 'none';
                }, 500);
              }
            })
            .catch(e => console.log('Sound enable failed:', e));
        };
        
        // If audio is ready, play immediately
        if (fireAmbient.readyState >= 2) {
          playAudio();
        } else {
          // Wait for audio to be ready
          fireAmbient.addEventListener('canplay', playAudio, { once: true });
          // Force load if needed
          fireAmbient.load();
        }
      } else if (soundEnabled && soundPrompt) {
        // Sound already playing, just hide the prompt
        soundPrompt.style.opacity = '0';
        setTimeout(() => {
          soundPrompt.style.display = 'none';
        }, 500);
      }
    };
    
    // Make the banner itself clickable
    if (soundPrompt) {
      soundPrompt.addEventListener('click', enableSound);
    }
    
    // Delay attaching document-level listeners to avoid immediate triggering
    // from the navigation click
    setTimeout(() => {
      document.addEventListener('click', enableSound, { once: true });
      document.addEventListener('keydown', enableSound, { once: true });
    }, 500);
    
    // Setup sound toggle button
    const soundToggle = document.getElementById('sound-toggle');
    if (soundToggle && fireAmbient) {
      soundToggle.addEventListener('click', () => {
        if (fireAmbient.paused) {
          fireAmbient.play();
          soundToggle.querySelector('.sound-icon').textContent = '🔊';
        } else {
          fireAmbient.pause();
          soundToggle.querySelector('.sound-icon').textContent = '🔇';
        }
      });
    }
    
    // Wait 3 seconds, then start typing scenario text
    setTimeout(async () => {
      const textElement = document.getElementById('scenario-text');
      if (textElement) {
        textElement.style.transition = 'opacity 0.5s ease-in';
        textElement.style.opacity = '1';
        
        // Type out the scenario text
        await typewriterEffect(textElement, scenarioText, 40);
        
        // Wait a moment, then show button and play phone ring
        setTimeout(() => {
          const answerButtonContainer = document.getElementById('answer-button-container');
          const answerButton = document.getElementById('answer-call-button');
          
          // Fade in the answer button
          if (answerButtonContainer) {
            answerButtonContainer.style.transition = 'opacity 1s ease-in';
            answerButtonContainer.style.opacity = '1';
            
            // Enable button interaction after it's visible
            setTimeout(() => {
              answerButtonContainer.style.pointerEvents = 'auto';
              
              // Attach click handler now that button is visible and clickable
              if (answerButton) {
                answerButton.addEventListener('click', () => {
                  // Stop phone ring
                  const phoneRing = document.getElementById('session1-phone-ring');
                  if (phoneRing) phoneRing.pause();
                  
                  // Start first non-role-play conversation
                  window.location.href = 'chat.html?type=non-roleplay&conversation=1';
                });
              }
            }, 1000); // Wait for fade-in to complete
            
            // Play phone ring when button appears
            setTimeout(() => {
              const phoneRingElement = document.getElementById('session1-phone-ring');
              if (phoneRingElement) {
                // Ensure normal playback rate
                phoneRingElement.playbackRate = 1.0;
                phoneRingElement.volume = 0.5;
                phoneRingElement.play().catch(e => console.log('Phone ring autoplay blocked:', e));
              }
            }, 300); // Small delay after button appears
          }
        }, 1500);
      }
    }, 3000);
  }
  
  // Character scenario descriptions
  const SCENARIOS = {
    bob: {
      name: "Bob",
      description: "A stubborn person who prioritizes work over safety",
      scenario: "It is a regular day at home. You are working on an important computer project when your phone suddenly rings. The caller ID shows the local fire department…"
    },
    niki: {
      name: "Niki",
      description: "A cooperative person willing to follow instructions",
      scenario: "It is a regular day at home. You are relaxing with your partner when your phone suddenly rings. The caller ID shows the local fire department…"
    },
    lindsay: {
      name: "Lindsay",
      description: "A caregiver responsible for children",
      scenario: "It is a regular day. You are babysitting two young children while their parents are out. You're keeping the kids entertained when your phone suddenly rings. The caller ID shows the local fire department…"
    },
    michelle: {
      name: "Michelle",
      description: "A stubborn person determined to protect property",
      scenario: "It is a regular day at home. You and your partner have prepared well for wildfire season. When your phone suddenly rings, the caller ID shows the local fire department…"
    },
    ross: {
      name: "Ross",
      description: "A driver helping evacuate elderly people",
      scenario: "You are driving a van with elderly passengers when your vehicle breaks down on the roadside. Your passengers have mobility issues and cannot evacuate on their own. Your phone suddenly rings. The caller ID shows the local fire department…"
    },
    mary: {
      name: "Mary",
      description: "An elderly person living alone with a pet",
      scenario: "It is a regular day at home. You are reading with your small dog beside you when your phone suddenly rings. The caller ID shows the local fire department…"
    },
    ben: {
      name: "Ben",
      description: "A young professional working from home",
      scenario: "It is a regular day at home. You are working on your computer, troubleshooting a client's problem, when your phone suddenly rings. The caller ID shows the local fire department…"
    },
    ana: {
      name: "Ana",
      description: "A caregiver responsible for multiple elderly people",
      scenario: "It is a regular workday. You are at the senior center helping elderly residents with their daily activities when your phone suddenly rings. The caller ID shows the local fire department…"
    },
    tom: {
      name: "Tom",
      description: "A helpful person who wants to assist others first",
      scenario: "It is a regular day at home. You are working on a woodworking project in your garage when your phone suddenly rings. The caller ID shows the local fire department…"
    },
    mia: {
      name: "Mia",
      description: "A young student focused on a school project",
      scenario: "It is a regular day after school. You are at the robotics lab testing your project when your phone suddenly rings. The caller ID shows the local fire department…"
    }
  };

  // Handle page refresh - just reload the scenario page (keep participant data)
  const perfData = performance.getEntriesByType('navigation')[0];
  if (perfData && perfData.type === 'reload') {
    console.log('🔄 Page refresh detected on scenario page - reloading scenario');
    // Keep participant ID, survey data, and completedConversations
    // Just reload the page naturally (no redirect needed)
  }

  // Wait for DOM to be ready
  document.addEventListener('DOMContentLoaded', async function() {
    console.log('=== DOMContentLoaded Event Fired ===');
    
    // Development mode: Clear session storage if ?reset=true in URL
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('reset') === 'true') {
      console.log('🔄 Reset parameter detected - clearing session storage');
      sessionStorage.clear();
      // Redirect to survey page
      window.location.href = 'survey.html';
      return;
    }
    
    // Check if participant has completed survey
    const participantId = sessionStorage.getItem('participantId');
    console.log('Participant ID from sessionStorage:', participantId);
    
    if (!participantId) {
      console.error('❌ No participant ID found. Redirecting to survey...');
      // Uncomment to enforce survey completion
      // window.location.href = 'survey.html';
    }

    // Check which session this is
    const sessionType = urlParams.get('session');
    
    if (sessionType === '1') {
      // Session 1: Show personalized scenario introduction
      console.log('🎬 Session 1 - Non-role-play introduction');
      await displaySession1Scenario();
      return;
    } else {
      // Session 2: Show character selection (existing behavior)
      console.log('🎭 Session 2 - Character selection');
      // Load recommended scenario (updates text only, no notice shown)
      console.log('Calling loadRecommendedScenario()...');
      loadRecommendedScenario();
    }

    // Add click handlers to character cards
    const characterCards = document.querySelectorAll('.character-card');
    characterCards.forEach(card => {
      card.addEventListener('click', function() {
        const character = this.getAttribute('data-character');
        selectCharacter(character);
      });
    });

    // Don't initialize media on page load - only when scenario is shown
    // initializeMedia();
  });

  /**
   * Select a character for the scenario
   */
  window.selectCharacter = function(character) {
    selectedCharacter = character;
    
    // Update UI to show selection
    const characterCards = document.querySelectorAll('.character-card');
    characterCards.forEach(card => {
      card.classList.remove('selected');
      if (card.getAttribute('data-character') === character) {
        card.classList.add('selected');
      }
    });

    // Enable start button
    const startBtn = document.getElementById('startBtn');
    startBtn.disabled = false;
    
    console.log('Selected character:', character);
  };

  /**
   * Start the conversation
   */
  window.startConversation = function() {
    if (!selectedCharacter) {
      alert('Please select a character first');
      return;
    }

    // Store selected character in session
    sessionStorage.setItem('selectedCharacter', selectedCharacter);
    
    // Redirect to chat page for first role-play conversation
    window.location.href = `chat.html?type=roleplay&conversation=1&character=${selectedCharacter}`;
  };

  /**
   * Go back to survey page
   */
  window.goBack = function() {
    if (confirm('Are you sure you want to go back? Your progress will be lost.')) {
      window.location.href = 'survey.html';
    }
  };

  /**
   * Media control variables
   */
  let soundEnabled = false;
  let videoEnabled = false;

  /**
   * Setup media controls
   */
  function setupMediaControls() {
    const toggleSoundBtn = document.getElementById('toggleSound');
    const ambientSound = document.getElementById('ambientSound');
    const phoneRinging = document.getElementById('phoneRinging');
    
    // Check if media files are available
    const hasAmbientSound = ambientSound && ambientSound.querySelector('source');
    const hasPhoneRing = phoneRinging && phoneRinging.querySelector('source');
    
    // Toggle sound
    if (toggleSoundBtn) {
      toggleSoundBtn.addEventListener('click', function() {
        soundEnabled = !soundEnabled;
        
        if (soundEnabled) {
          // Play ambient sound
          if (hasAmbientSound) {
            ambientSound.volume = 0.3;
            ambientSound.play().catch(err => console.log('Sound play prevented:', err));
          }
          
          // Play phone ringing after 2 seconds
          if (hasPhoneRing) {
            setTimeout(() => {
              if (soundEnabled) {
                playPhoneRinging();
              }
            }, 2000);
          }
        } else {
          // Stop all sounds
          if (hasAmbientSound) ambientSound.pause();
          if (hasPhoneRing) phoneRinging.pause();
        }
        
        updateSoundButtonState();
      });
    }
  }

  /**
   * Play phone ringing sound with visual effect
   */
  function playPhoneRinging() {
    const phoneRinging = document.getElementById('phoneRinging');
    const phoneIcon = document.querySelector('.phone-icon');
    
    if (phoneRinging && phoneRinging.querySelector('source')) {
      phoneRinging.volume = 0.5;
      phoneRinging.play().catch(err => console.log('Phone ring prevented:', err));
      
      // Add visual ringing effect
      if (phoneIcon) {
        phoneIcon.classList.add('ringing');
        
        // Remove class after sound ends
        phoneRinging.onended = () => {
          phoneIcon.classList.remove('ringing');
          
          // Play again after 3 seconds if sound is still enabled
          if (soundEnabled) {
            setTimeout(() => {
              if (soundEnabled) {
                playPhoneRinging();
              }
            }, 3000);
          }
        };
      }
    }
  }

  /**
   * Add sound wave effects around phone
   */
  function addSoundWaveEffects() {
    const phoneAnimation = document.querySelector('.phone-animation');
    if (phoneAnimation && soundEnabled) {
      // Add sound wave elements
      for (let i = 0; i < 3; i++) {
        const wave = document.createElement('div');
        wave.className = 'sound-wave';
        phoneAnimation.appendChild(wave);
      }
    }
  }

  /**
   * Attempt to autoplay audio
   */
  function attemptAutoplay() {
    const ambientSound = document.getElementById('ambientSound');
    const phoneRinging = document.getElementById('phoneRinging');
    
    const hasAmbientSound = ambientSound && ambientSound.querySelector('source');
    const hasPhoneRing = phoneRinging && phoneRinging.querySelector('source');
    
    // Try to autoplay
    if (hasAmbientSound) {
      ambientSound.volume = 0.3;
      ambientSound.play().then(() => {
        console.log('Ambient sound autoplaying');
        soundEnabled = true;
        updateSoundButtonState();
        
        // Start phone ringing after 2 seconds
        if (hasPhoneRing) {
          setTimeout(() => {
            playPhoneRinging();
          }, 2000);
        }
      }).catch(err => {
        console.log('Autoplay prevented by browser. User must click sound button.');
        // Show prominent message to enable sound
        showSoundPrompt();
      });
    }
  }

  /**
   * Show prompt to enable sound
   */
  function showSoundPrompt() {
    const toggleSoundBtn = document.getElementById('toggleSound');
    if (toggleSoundBtn) {
      // Add pulsing animation
      toggleSoundBtn.style.animation = 'pulse 2s ease-in-out infinite';
      toggleSoundBtn.style.boxShadow = '0 0 20px rgba(255, 107, 53, 0.6)';
      
      // Add text prompt
      const prompt = document.createElement('div');
      prompt.style.cssText = `
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: rgba(44, 62, 80, 0.95);
        color: white;
        padding: 2rem 3rem;
        border-radius: 16px;
        text-align: center;
        z-index: 10000;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
        backdrop-filter: blur(10px);
      `;
      prompt.innerHTML = `
        <div style="font-size: 3rem; margin-bottom: 1rem;">🔊</div>
        <h2 style="margin-bottom: 1rem; font-size: 1.5rem;">Enable Sound for Full Experience</h2>
        <p style="margin-bottom: 1.5rem; opacity: 0.9;">Click the button below to hear the emergency scenario</p>
        <button onclick="this.parentElement.remove(); document.getElementById('toggleSound').click();" 
                style="background: linear-gradient(135deg, #ff6b35 0%, #e63946 100%); 
                       color: white; border: none; padding: 1rem 2rem; border-radius: 25px; 
                       font-size: 1.1rem; font-weight: 600; cursor: pointer;">
          🔊 Enable Sound
        </button>
        <p style="margin-top: 1rem; font-size: 0.9rem; opacity: 0.7;">
          <a onclick="this.closest('div').remove();" style="color: white; cursor: pointer; text-decoration: underline;">
            Continue without sound
          </a>
        </p>
      `;
      document.body.appendChild(prompt);
    }
  }

  /**
   * Update sound button state
   */
  function updateSoundButtonState() {
    const toggleSoundBtn = document.getElementById('toggleSound');
    if (toggleSoundBtn) {
      const soundOn = toggleSoundBtn.querySelector('.sound-on');
      const soundOff = toggleSoundBtn.querySelector('.sound-off');
      
      if (soundEnabled) {
        soundOn.style.display = 'none';
        soundOff.style.display = 'inline';
        toggleSoundBtn.style.animation = 'none';
        toggleSoundBtn.style.boxShadow = '';
      } else {
        soundOn.style.display = 'inline';
        soundOff.style.display = 'none';
      }
    }
  }

  /**
   * Initialize media on page load
   */
  function initializeMedia() {
    setupMediaControls();
    
    // Try autoplay after a short delay (better chance of success)
    setTimeout(() => {
      attemptAutoplay();
    }, 500);
  }

  /**
   * Calculate similarity percentage between participant and character
   * Weights: Age (50%) + Occupation (30%) + Special Needs (20%) = 100%
   */
  function calculateSimilarity(surveyData, characterProfile) {
    let ageScore = 0;
    let occupationScore = 0;
    let specialNeedsScore = 0;
    
    const age = parseInt(surveyData.background.age) || 30;
    const occupation = (surveyData.background.occupation || '').toLowerCase();
    const specialNeeds = surveyData.specialNeeds || {};
    
    // Age scoring (50% weight)
    const ageMatch = characterProfile.ageMatch(age);
    ageScore = ageMatch * 50;
    
    // Occupation scoring (30% weight)
    const occupationMatch = characterProfile.occupationMatch(occupation);
    occupationScore = occupationMatch * 30;
    
    // Special needs scoring (20% weight)
    const needsMatch = characterProfile.specialNeedsMatch(specialNeeds);
    specialNeedsScore = needsMatch * 20;
    
    return Math.round(ageScore + occupationScore + specialNeedsScore);
  }

  /**
   * Character profiles with matching criteria
   */
  const CHARACTER_PROFILES = {
    bob: {
      name: 'Bob',
      description: 'Bob is around 30 years old. He prioritizes his work over safety and ignores warnings. He is likely to refuse evacuation because he wants to focus on his work.',
      ageMatch: (age) => {
        if (age >= 25 && age <= 35) return 1.0;
        if (age >= 20 && age <= 40) return 0.7;
        if (age >= 18 && age <= 45) return 0.4;
        return 0.1;
      },
      occupationMatch: (occ) => {
        if (occ.includes('tech') || occ.includes('computer') || occ.includes('software') || occ.includes('engineer') || occ.includes('programmer')) return 1.0;
        if (occ.includes('analyst') || occ.includes('developer') || occ.includes('it')) return 0.8;
        if (occ.includes('student') || occ.includes('researcher')) return 0.5;
        return 0.2;
      },
      specialNeedsMatch: (needs) => {
        // Bob has no special needs
        if (needs.condition === 'no' && needs.responsible === 'no' && needs.vehicle === 'no') return 1.0;
        if (needs.condition === 'no' && needs.responsible === 'no') return 0.7;
        return 0.3;
      }
    },
    ben: {
      name: 'Ben',
      description: 'Ben is a 29-year-old man who works from home as a computer technician. He likes cycling, cooking, and flying drones. He is currently working on his computer while watching a bike race online. Ben can evacuate himself by e-bike or car, but could use drone guidance to find a safe route.',
      ageMatch: (age) => {
        if (age >= 27 && age <= 32) return 1.0;
        if (age >= 23 && age <= 35) return 0.8;
        if (age >= 20 && age <= 40) return 0.5;
        return 0.2;
      },
      occupationMatch: (occ) => {
        if (occ.includes('tech') || occ.includes('computer') || occ.includes('it')) return 1.0;
        if (occ.includes('engineer') || occ.includes('software')) return 0.9;
        if (occ.includes('work from home') || occ.includes('remote')) return 0.7;
        return 0.2;
      },
      specialNeedsMatch: (needs) => {
        // Ben can evacuate independently, might have pet
        if (needs.condition === 'no' && needs.responsible === 'no') return 1.0;
        if (needs.vehicle === 'no') return 0.8;
        return 0.4;
      }
    },
    mary: {
      name: 'Mary',
      description: 'Mary is an elderly person living alone with a small dog. She used to work as a librarian and now enjoys a quiet life. She moves slowly due to arthritis. She cannot drive and will need help getting to safety.',
      ageMatch: (age) => {
        if (age >= 65) return 1.0;
        if (age >= 60) return 0.8;
        if (age >= 55) return 0.5;
        return 0.1;
      },
      occupationMatch: (occ) => {
        if (occ.includes('retire') || occ.includes('librarian')) return 1.0;
        if (occ.includes('teacher') || occ.includes('education')) return 0.6;
        if (occ.includes('none') || occ.includes('not working')) return 0.7;
        return 0.3;
      },
      specialNeedsMatch: (needs) => {
        let score = 0;
        if (needs.condition === 'yes') score += 0.4;
        if (needs.vehicle === 'yes' && needs.responsible === 'no') score += 0.5;
        const details = (needs.details || '').toLowerCase();
        if (details.includes('dog') || details.includes('pet')) score += 0.1;
        return Math.min(score || 0.3, 1.0);
      }
    },
    lindsay: {
      name: 'Lindsay',
      description: 'Lindsay is a babysitter caring for two children while parents are out. She will evacuate with minimal persuasion once informed of the fire, though initially anxious about leaving without parental approval.',
      ageMatch: (age) => {
        if (age >= 20 && age <= 30) return 1.0;
        if (age >= 18 && age <= 35) return 0.7;
        if (age >= 16 && age <= 40) return 0.4;
        return 0.2;
      },
      occupationMatch: (occ) => {
        if (occ.includes('babysit') || occ.includes('nanny') || occ.includes('childcare')) return 1.0;
        if (occ.includes('care') || occ.includes('teacher') || occ.includes('education')) return 0.6;
        if (occ.includes('student')) return 0.4;
        return 0.2;
      },
      specialNeedsMatch: (needs) => {
        if (needs.responsible === 'yes') return 1.0;
        if (needs.condition === 'no' && needs.vehicle === 'no') return 0.5;
        return 0.3;
      }
    },
    ana: {
      name: 'Ana',
      description: 'Ana is a caregiver working at a senior center. She is helping elderly residents with their daily activities. She needs to help evacuate the seniors first and would need a van for group transport.',
      ageMatch: (age) => {
        if (age >= 35 && age <= 50) return 1.0;
        if (age >= 30 && age <= 55) return 0.8;
        if (age >= 25 && age <= 60) return 0.5;
        return 0.2;
      },
      occupationMatch: (occ) => {
        if (occ.includes('care') || occ.includes('nurse') || occ.includes('medical')) return 1.0;
        if (occ.includes('social') || occ.includes('health')) return 0.8;
        if (occ.includes('teacher') || occ.includes('assistant')) return 0.5;
        return 0.2;
      },
      specialNeedsMatch: (needs) => {
        if (needs.responsible === 'yes' && needs.vehicle === 'yes') return 1.0;
        if (needs.responsible === 'yes') return 0.7;
        if (needs.vehicle === 'yes') return 0.5;
        return 0.3;
      }
    },
    ross: {
      name: 'Ross',
      description: 'Ross is a van driver who was helping evacuate elderly residents when his vehicle broke down. He has passengers with mobility issues who cannot evacuate independently. He needs transport assistance.',
      ageMatch: (age) => {
        if (age >= 35 && age <= 50) return 1.0;
        if (age >= 30 && age <= 55) return 0.8;
        if (age >= 25 && age <= 60) return 0.5;
        return 0.2;
      },
      occupationMatch: (occ) => {
        if (occ.includes('driver') || occ.includes('transport')) return 1.0;
        if (occ.includes('delivery') || occ.includes('logistics')) return 0.7;
        if (occ.includes('care') || occ.includes('emergency')) return 0.5;
        return 0.2;
      },
      specialNeedsMatch: (needs) => {
        if (needs.responsible === 'yes' && needs.vehicle === 'yes') return 1.0;
        if (needs.responsible === 'yes') return 0.7;
        return 0.3;
      }
    },
    niki: {
      name: 'Niki',
      description: 'Niki is at home with a partner. Ready to cooperate and follow instructions, but needs someone to explain what is happening and what to do.',
      ageMatch: (age) => {
        if (age >= 25 && age <= 45) return 1.0;
        if (age >= 20 && age <= 50) return 0.7;
        return 0.4;
      },
      occupationMatch: (occ) => {
        // General, any occupation
        return 0.5;
      },
      specialNeedsMatch: (needs) => {
        if (needs.condition === 'no' && needs.responsible === 'no') return 1.0;
        return 0.6;
      }
    },
    michelle: {
      name: 'Michelle',
      description: 'Michelle is at home with preparations for wildfire season. Believes home preparations will protect them, skeptical of evacuation warnings.',
      ageMatch: (age) => {
        if (age >= 40 && age <= 60) return 1.0;
        if (age >= 35 && age <= 65) return 0.7;
        return 0.4;
      },
      occupationMatch: (occ) => {
        if (occ.includes('homeowner') || occ.includes('property')) return 0.8;
        return 0.4;
      },
      specialNeedsMatch: (needs) => {
        if (needs.condition === 'no' && needs.responsible === 'no') return 0.8;
        return 0.5;
      }
    },
    tom: {
      name: 'Tom',
      description: 'Tom is a high school teacher working on a woodworking project at home. Known in the community as someone who helps others. Has a truck but torn between leaving now and checking on others first.',
      ageMatch: (age) => {
        if (age >= 45 && age <= 60) return 1.0;
        if (age >= 40 && age <= 65) return 0.8;
        if (age >= 35 && age <= 70) return 0.5;
        return 0.2;
      },
      occupationMatch: (occ) => {
        if (occ.includes('teacher') || occ.includes('education')) return 1.0;
        if (occ.includes('instructor') || occ.includes('professor')) return 0.9;
        if (occ.includes('social') || occ.includes('community')) return 0.6;
        return 0.3;
      },
      specialNeedsMatch: (needs) => {
        if (needs.responsible === 'yes') return 0.7;
        if (needs.condition === 'no' && needs.vehicle === 'no') return 0.8;
        return 0.5;
      }
    },
    mia: {
      name: 'Mia',
      description: 'Mia is a high school student working on a robotics project at the school lab. Completely absorbed in testing, can drive but may want to finish work first.',
      ageMatch: (age) => {
        if (age >= 16 && age <= 19) return 1.0;
        if (age >= 15 && age <= 22) return 0.8;
        if (age >= 14 && age <= 25) return 0.5;
        return 0.1;
      },
      occupationMatch: (occ) => {
        if (occ.includes('student')) return 1.0;
        if (occ.includes('high school') || occ.includes('college')) return 0.9;
        if (occ.includes('intern') || occ.includes('research')) return 0.6;
        return 0.2;
      },
      specialNeedsMatch: (needs) => {
        if (needs.condition === 'no' && needs.responsible === 'no') return 1.0;
        return 0.6;
      }
    }
  };

  /**
   * Match participant profile to best characters
   * Returns top 2 matches with >50% similarity
   */
  function matchCharacterToProfile(surveyData) {
    if (!surveyData || !surveyData.background) {
      return []; // No matches
    }
    
    // Calculate similarity for all characters
    const similarities = {};
    for (const [charId, profile] of Object.entries(CHARACTER_PROFILES)) {
      similarities[charId] = {
        character: charId,
        name: profile.name,
        description: profile.description,
        similarity: calculateSimilarity(surveyData, profile)
      };
    }
    
    // Sort by similarity descending
    const sorted = Object.values(similarities).sort((a, b) => b.similarity - a.similarity);
    
    // Filter >50% and take top 2
    const matches = sorted.filter(m => m.similarity > 50).slice(0, 2);
    
    console.log('All similarities:', sorted);
    console.log('Top matches (>50%):', matches);
    
    return matches;
  }

  /**
   * OLD MATCHING LOGIC - REMOVED
   */
  function OLD_matchCharacterToProfile_REMOVED(surveyData) {
    if (!surveyData || !surveyData.background) {
      return 'bob'; // Default
    }
    
    const age = parseInt(surveyData.background.age) || 30;
    const gender = surveyData.background.gender || '';
    const occupation = (surveyData.background.occupation || '').toLowerCase();
    const specialNeeds = surveyData.specialNeeds || {};
    
    // OLD Scoring system for each character
    const scores = {
      bob: 0,
      niki: 0,
      lindsay: 0,
      michelle: 0,
      ross: 0,
      mary: 0,
      ben: 0,
      ana: 0,
      tom: 0,
      mia: 0
    };
    
    // OLD MATCHING REMOVED - Now using percentage-based similarity
  }

  /**
   * Load recommended characters based on survey
   * Shows top 2 matches with >50% similarity (only for first conversation)
   */
  async function loadRecommendedScenario() {
    try {
      console.log('=== Loading Recommended Scenario ===');
      
      // Check if character already selected (for conversations 2-3)
      const completedConversations = parseInt(sessionStorage.getItem('completedConversations') || '0');
      const selectedCharacter = sessionStorage.getItem('selectedCharacter');
      
      console.log('Completed conversations:', completedConversations);
      console.log('Selected character:', selectedCharacter);
      
      if (completedConversations > 3 && selectedCharacter) {
        // Already selected character in Session 2, redirect directly to chat
        const conversationInSession = completedConversations - 3 + 1;
        console.log('Character already selected, redirecting to chat:', selectedCharacter, 'conversation:', conversationInSession);
        window.location.href = `chat.html?type=roleplay&conversation=${conversationInSession}&character=${selectedCharacter}`;
        return;
      }
      
      // First conversation: show character selection
      console.log('Fetching survey data...');
      const surveyData = await fetchSurveyData();
      console.log('Survey data received:', surveyData);
      
      if (surveyData) {
        console.log('Matching character to profile...');
        const matches = matchCharacterToProfile(surveyData);
        console.log('Matches found:', matches);
        
        // Hide loading state
        hideLoadingState();
        
        if (matches.length > 0) {
          // Show role-play selection UI
          console.log('Displaying role-play selection UI');
          displayRolePlaySelection(matches, surveyData);
        } else {
          // No matches found - end process
          console.log('No matches found, displaying end message');
          displayNoMatches();
        }
      } else {
        console.error('No survey data received');
        hideLoadingState();
        showDefaultContent();
        alert('Unable to load your survey data. Please try again or contact support.');
      }
    } catch (error) {
      console.error('Error loading personalized scenario:', error);
      hideLoadingState();
      showDefaultContent();
      alert('An error occurred while loading the scenario. Please check the console for details.');
    }
  }

  /**
   * Hide loading state
   */
  function hideLoadingState() {
    const loadingState = document.getElementById('loading-state');
    if (loadingState) {
      loadingState.style.display = 'none';
    }
  }

  /**
   * Show default content (fallback)
   */
  function showDefaultContent() {
    const defaultContent = document.getElementById('default-content');
    if (defaultContent) {
      defaultContent.style.display = 'block';
    }
  }

  /**
   * Display role-play character selection
   */
  function displayRolePlaySelection(matches, surveyData) {
    const scenarioContainer = document.querySelector('.scenario-content');
    if (!scenarioContainer) {
      console.error('Scenario container not found');
      return;
    }

    // Create new selection UI (this is only shown for the first conversation)
    const selectionHTML = `
      <div class="scenario-card">
        <div class="role-play-selection">
          <h2>Part II: Role-Play Character Selection</h2>
          <p class="selection-instructions">
            Based on your previous responses, we have found the following simulated characters that match your profile. 
            Please select the character you feel is most similar to you. You will role-play as this character in all three conversations.
          </p>
          
          <div class="character-options">
            ${matches.length > 0 ? matches.map((match, index) => `
              <div class="character-option" data-character="${match.character}" data-similarity="${match.similarity}">
                <input type="radio" name="roleplay-character" id="char-${match.character}" value="${match.character}">
                <label for="char-${match.character}">
                  <div class="character-header">
                    <strong>Option ${index + 1}: Role-play as ${match.name}</strong>
                    <span class="similarity-badge">${match.similarity}% match</span>
                  </div>
                  <p class="character-description">${match.description}</p>
                </label>
              </div>
            `).join('') : '<p style="color: white; text-align: center; padding: 2rem;">No matching characters found.</p>'}
            
            <div class="character-option" data-character="none">
              <input type="radio" name="roleplay-character" id="char-none" value="none">
              <label for="char-none">
                <strong>None</strong> - I don't think any simulated characters match my profile.
              </label>
            </div>
          </div>
          
          <div class="selection-action">
            <button id="confirm-character-btn" class="btn-primary" disabled>Confirm Selection</button>
          </div>
        </div>
      </div>
    `;

    console.log('Displaying role-play selection with', matches.length, 'matches');
    scenarioContainer.innerHTML = selectionHTML;

    // Add event listeners
    const radios = document.querySelectorAll('input[name="roleplay-character"]');
    const confirmBtn = document.getElementById('confirm-character-btn');

    radios.forEach(radio => {
      radio.addEventListener('change', () => {
        confirmBtn.disabled = false;
      });
    });

    confirmBtn.addEventListener('click', () => {
      console.log('Confirm button clicked');
      const selected = document.querySelector('input[name="roleplay-character"]:checked');
      if (selected) {
        console.log('Selected character:', selected.value);
        try {
          handleCharacterSelection(selected.value, surveyData);
        } catch (error) {
          console.error('Error handling character selection:', error);
          alert('An error occurred. Please check the console for details.');
        }
      } else {
        console.warn('No character selected');
      }
    });
  }

  /**
   * Handle character selection
   */
  function handleCharacterSelection(characterId, surveyData) {
    if (characterId === 'none') {
      // End process
      displayThankYouEnd();
    } else {
      // Start role-play with selected character
      startRolePlayScenario(characterId, surveyData);
    }
  }

  /**
   * Start role-play scenario with selected character (first conversation only)
   */
  function startRolePlayScenario(characterId, surveyData) {
    console.log('Starting role-play scenario for:', characterId);
    
    try {
      // Store selected character (will be used for all 3 conversations)
      sessionStorage.setItem('selectedCharacter', characterId);

      // Show immersive scenario with media
      console.log('Showing immersive scenario for first conversation');
      
      const scenarioContainer = document.querySelector('.scenario-content');
      if (!scenarioContainer) {
        console.error('Scenario container not found');
        return;
      }

      const character = CHARACTER_PROFILES[characterId];
      const scenarioText = SCENARIOS[characterId] ? SCENARIOS[characterId].scenario : "It is a regular day when your phone suddenly rings. The caller ID shows the local fire department…";

      console.log('Displaying scenario for character:', characterId);

      scenarioContainer.innerHTML = `
        <div class="immersive-scenario">
          <div class="scenario-intro">
            ${scenarioText}
          </div>
          
          <div class="scenario-action">
            <button id="start-conversation-btn" class="btn-primary pulse-animation">
              📞 Answer the Call
            </button>
          </div>
        </div>
      `;

      // Show media controls for immersive scenario
      const mediaControls = document.querySelector('.media-controls');
      if (mediaControls) {
        mediaControls.style.display = 'block';
      }

      // Initialize media NOW - when showing the actual scenario
      // This ensures sound only plays during the immersive scenario, not during character selection
      console.log('Initializing media for immersive scenario');
      if (typeof initializeMedia === 'function') {
        initializeMedia();
      } else {
        console.warn('initializeMedia function not found');
      }

      // Add event listener for starting conversation
      const startBtn = document.getElementById('start-conversation-btn');
      if (startBtn) {
        startBtn.addEventListener('click', () => {
          console.log('Transitioning to chat for character:', characterId);
          // Transition to IQL chat interface (first role-play conversation)
          window.location.href = `chat.html?type=roleplay&conversation=1&character=${characterId}`;
        });
        console.log('Start conversation button listener added');
      } else {
        console.error('Start conversation button not found');
      }
    } catch (error) {
      console.error('Error in startRolePlayScenario:', error);
      alert('An error occurred while loading the scenario. Please try again.');
    }
  }

  /**
   * Display no matches message
   */
  function displayNoMatches() {
    const scenarioContainer = document.querySelector('.scenario-content');
    if (!scenarioContainer) return;

    scenarioContainer.innerHTML = `
      <div class="scenario-card">
        <div class="no-matches" style="color: white; text-align: center; padding: 3rem;">
          <h2 style="color: var(--fire-orange); margin-bottom: 1.5rem;">No Matching Characters Found</h2>
          <p style="font-size: 1.2rem; line-height: 1.8;">We couldn't find any simulated characters that closely match your profile (>50% similarity).</p>
          <p style="font-size: 1.2rem; line-height: 1.8;">Thank you for completing the survey.</p>
        </div>
      </div>
    `;
  }

  /**
   * Display thank you end message
   */
  function displayThankYouEnd() {
    const scenarioContainer = document.querySelector('.scenario-content');
    if (!scenarioContainer) return;

    scenarioContainer.innerHTML = `
      <div class="scenario-card">
        <div class="end-message" style="color: white; text-align: center; padding: 3rem;">
          <h2 style="color: var(--fire-orange); margin-bottom: 1.5rem;">Thank You!</h2>
          <p style="font-size: 1.2rem; line-height: 1.8;">You have chosen not to participate in the role-play conversation.</p>
          <p style="font-size: 1.2rem; line-height: 1.8;">Thank you for completing the survey. Your responses have been recorded.</p>
        </div>
      </div>
    `;
  }

  /**
   * Fetch survey data from backend
   */
  async function fetchSurveyData() {
    const participantId = sessionStorage.getItem('participantId');
    
    console.log('Fetching survey data for participant:', participantId);
    
    if (!participantId) {
      console.error('No participant ID found in sessionStorage');
      return null;
    }

    try {
      const CONFIG = window.APP_CONFIG || {
        API_URL: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
          ? 'http://localhost:8001' 
          : 'https://your-backend-url.onrender.com',
      };

      console.log('API URL:', CONFIG.API_URL);
      console.log('Fetching from:', `${CONFIG.API_URL}/api/survey/${participantId}`);

      const response = await fetch(`${CONFIG.API_URL}/api/survey/${participantId}`);
      
      console.log('Response status:', response.status);
      console.log('Response ok:', response.ok);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('Response error:', errorText);
        throw new Error(`Failed to fetch survey data: ${response.status}`);
      }

      const surveyData = await response.json();
      
      console.log('Survey data retrieved successfully:', surveyData);
      
      return surveyData;
    } catch (error) {
      console.error('Error fetching survey data:', error);
      return null;
    }
  }
})();

