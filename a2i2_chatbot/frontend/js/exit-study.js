/**
 * Exit Study Handler
 * Shared functionality for exit button across all pages
 */

(function() {
  'use strict';

  // Use global config if available
  const CONFIG = window.APP_CONFIG || {
    API_URL: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
      ? 'http://localhost:8001' 
      : 'https://your-backend-url.onrender.com',
  };

  /**
   * Show exit confirmation modal
   */
  function showExitConfirmation(pageName) {
    const participantId = sessionStorage.getItem('participantId');
    
    if (!participantId) {
      // No participant ID means they haven't started yet, just go back to landing
      window.location.href = 'landing.html';
      return;
    }

    // Create modal
    const modal = document.createElement('div');
    modal.id = 'exit-modal';
    modal.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(0, 0, 0, 0.7);
      display: flex;
      justify-content: center;
      align-items: center;
      z-index: 10000;
    `;

    modal.innerHTML = `
      <div style="
        background: white;
        padding: 2rem;
        border-radius: 12px;
        max-width: 500px;
        width: 90%;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
      ">
        <h2 style="margin-top: 0; color: #ff6b35;">Exit Study?</h2>
        <p style="color: #333; line-height: 1.6;">
          Are you sure you want to exit the study? Your progress will be saved, 
          and you will receive a confirmation number.
        </p>
        <div style="display: flex; gap: 1rem; margin-top: 1.5rem;">
          <button id="confirm-exit-btn" style="
            flex: 1;
            padding: 0.75rem 1.5rem;
            background: #ff6b35;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
          ">Yes, Exit Study</button>
          <button id="cancel-exit-btn" style="
            flex: 1;
            padding: 0.75rem 1.5rem;
            background: #e0e0e0;
            color: #333;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
          ">Cancel</button>
        </div>
      </div>
    `;

    document.body.appendChild(modal);

    // Handle cancel
    document.getElementById('cancel-exit-btn').addEventListener('click', () => {
      modal.remove();
    });

    // Handle confirm exit
    document.getElementById('confirm-exit-btn').addEventListener('click', async () => {
      document.getElementById('confirm-exit-btn').disabled = true;
      document.getElementById('confirm-exit-btn').textContent = 'Exiting...';
      
      try {
        const response = await fetch(`${CONFIG.API_URL}/api/exit-study`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            participantId: participantId,
            page: pageName
          })
        });

        if (!response.ok) {
          throw new Error('Failed to exit study');
        }

        const data = await response.json();
        
        // Show confirmation number
        modal.innerHTML = `
          <div style="
            background: white;
            padding: 2rem;
            border-radius: 12px;
            max-width: 500px;
            width: 90%;
            text-align: center;
          ">
            <div style="font-size: 3rem; margin-bottom: 1rem;">✓</div>
            <h2 style="margin-top: 0; color: #4CAF50;">Thank You!</h2>
            <p style="color: #333; line-height: 1.6; margin: 1.5rem 0;">
              Your confirmation number is:
            </p>
            <div style="
              background: #f5f5f5;
              padding: 1rem;
              border-radius: 8px;
              font-size: 1.5rem;
              font-weight: bold;
              color: #ff6b35;
              margin: 1rem 0;
            ">${data.confirmation_number}</div>
            <p style="color: #666; font-size: 0.9rem;">
              Please save this number for your records.
            </p>
            <p style="color: #666; font-size: 0.9rem; margin-top: 1rem;">
              You may now close this window.
            </p>
            <button id="done-exit-btn" style="
              margin-top: 1.5rem;
              padding: 0.75rem 2rem;
              background: #ff6b35;
              color: white;
              border: none;
              border-radius: 8px;
              font-size: 1rem;
              font-weight: 600;
              cursor: pointer;
            ">Done</button>
          </div>
        `;
        
        // Add event listener to done button
        const doneBtn = modal.querySelector('#done-exit-btn');
        if (doneBtn) {
          doneBtn.addEventListener('click', () => {
            modal.remove();
          });
        }
        
        // Clear session storage
        sessionStorage.clear();
        
      } catch (error) {
        console.error('Error exiting study:', error);
        alert('Error exiting study. Please try again.');
        modal.remove();
      }
    });
  }

  /**
   * Initialize exit button on page
   */
  window.initExitButton = function(pageName) {
    // Create exit button
    const exitBtn = document.createElement('button');
    exitBtn.id = 'exit-study-btn';
    exitBtn.innerHTML = '✕ Exit Study';
    exitBtn.style.cssText = `
      position: fixed;
      top: 1rem;
      right: 1rem;
      padding: 0.5rem 1rem;
      background: rgba(255, 107, 53, 0.9);
      color: white;
      border: none;
      border-radius: 8px;
      font-size: 0.9rem;
      font-weight: 600;
      cursor: pointer;
      z-index: 10000;
      transition: background 0.2s ease;
    `;

    exitBtn.addEventListener('mouseenter', () => {
      exitBtn.style.background = 'rgba(255, 107, 53, 1)';
    });

    exitBtn.addEventListener('mouseleave', () => {
      exitBtn.style.background = 'rgba(255, 107, 53, 0.9)';
    });

    exitBtn.addEventListener('click', () => {
      showExitConfirmation(pageName);
    });

    document.body.appendChild(exitBtn);
  };

})();

