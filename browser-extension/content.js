// Content script for website blocking and focus features
(function() {
  let focusOverlay = null;
  
  // Check if current site should be blocked
  checkSiteBlocking();
  
  // Listen for stats from background script
  chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.type === 'EXTENSION_STATS') {
      // Store stats in localStorage for React app
      localStorage.setItem('extensionStats', JSON.stringify(request.data));
      // Dispatch custom event
      window.dispatchEvent(new CustomEvent('extensionStatsUpdate', { detail: request.data }));
    }
    
    if (request.action === 'showFocusOverlay') {
      showFocusOverlay();
    }
    
    if (request.action === 'hideFocusOverlay') {
      hideFocusOverlay();
    }
  });
  
  async function checkSiteBlocking() {
    const data = await chrome.storage.local.get(['blockedSites', 'studyMode']);
    const hostname = window.location.hostname;
    
    if (isBlocked(hostname, data.blockedSites || [], data.studyMode || 'basic')) {
      showBlockedPage();
    }
  }
  
  function isBlocked(hostname, blockedSites, mode) {
    // Only block sites in exam mode
    if (mode !== 'exam') {
      return false;
    }
    
    const isInBlockList = blockedSites.some(site => hostname.includes(site));
    return isInBlockList || hostname.includes('reddit.com') || hostname.includes('tiktok.com');
  }
  
  function showBlockedPage() {
    document.body.innerHTML = `
      <div style="
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100vh;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-family: Arial, sans-serif;
        text-align: center;
      ">
        <h1 style="font-size: 3em; margin-bottom: 20px;">🚫 Site Blocked</h1>
        <p style="font-size: 1.2em; margin-bottom: 30px;">
          This site is blocked during your focus session.
        </p>
        <p style="font-size: 1em; opacity: 0.8;">
          Stay focused on your goals! 💪
        </p>
        <button onclick="history.back()" style="
          margin-top: 30px;
          padding: 12px 24px;
          background: rgba(255,255,255,0.2);
          border: 2px solid white;
          color: white;
          border-radius: 25px;
          cursor: pointer;
          font-size: 1em;
        ">Go Back</button>
      </div>
    `;
  }
  
  function showFocusOverlay() {
    if (focusOverlay) return;
    
    focusOverlay = document.createElement('div');
    focusOverlay.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(0,0,0,0.8);
      z-index: 999999;
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      font-family: Arial, sans-serif;
      text-align: center;
    `;
    
    focusOverlay.innerHTML = `
      <div>
        <h2>Focus Mode Active</h2>
        <p>Take a deep breath and focus on your task</p>
        <button onclick="this.parentElement.parentElement.remove()" style="
          margin-top: 20px;
          padding: 10px 20px;
          background: #4CAF50;
          color: white;
          border: none;
          border-radius: 5px;
          cursor: pointer;
        ">Continue</button>
      </div>
    `;
    
    document.body.appendChild(focusOverlay);
    
    setTimeout(() => {
      if (focusOverlay) {
        focusOverlay.remove();
        focusOverlay = null;
      }
    }, 3000);
  }
  
  function hideFocusOverlay() {
    if (focusOverlay) {
      focusOverlay.remove();
      focusOverlay = null;
    }
  }
})();