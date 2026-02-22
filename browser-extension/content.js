// Content script — secondary blocking layer + stats bridge to React app
(function () {
  let focusOverlay = null;

  // Check blocking on page load
  checkSiteBlocking();

  // Listen for messages from background
  chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.type === 'EXTENSION_STATS') {
      // Store stats for React app (via localStorage + custom event)
      localStorage.setItem('extensionStats', JSON.stringify(request.data));
      window.dispatchEvent(new CustomEvent('extensionStatsUpdate', { detail: request.data }));
    }

    if (request.action === 'showFocusOverlay') showFocusOverlay();
    if (request.action === 'hideFocusOverlay') hideFocusOverlay();
  });

  async function checkSiteBlocking() {
    const data = await chrome.storage.local.get(['blockedSites', 'studyMode']);
    const hostname = window.location.hostname.toLowerCase().replace(/^www\./, '');
    const sites = data.blockedSites || [];
    const mode = data.studyMode || 'focus';

    if (shouldBlock(hostname, sites, mode)) {
      showBlockedPage();
    }
  }

  function shouldBlock(hostname, blockedSites, mode) {
    // Basic mode = no blocking
    if (mode === 'basic') return false;

    // Check user's custom block list — works in Focus + Exam modes
    const isInBlockList = blockedSites.some(site => {
      const cleanSite = site.toLowerCase().replace(/^www\./, '');
      return hostname.includes(cleanSite) || cleanSite.includes(hostname);
    });

    if (isInBlockList) return true;

    // Exam mode: extra social/entertainment blocks
    if (mode === 'exam') {
      const examExtraBlocks = [
        'reddit.com', 'tiktok.com', 'snapchat.com', 'discord.com',
        'twitch.tv', 'netflix.com', 'primevideo.com', 'hotstar.com',
        'spotify.com', 'pinterest.com', 'tumblr.com', 'telegram.org',
        'whatsapp.com', 'messenger.com'
      ];
      return examExtraBlocks.some(s => hostname.includes(s));
    }

    return false;
  }

  function showBlockedPage() {
    document.body.innerHTML = `
      <div style="
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100vh;
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        color: white;
        font-family: 'Segoe UI', Arial, sans-serif;
        text-align: center;
      ">
        <div style="font-size: 64px; margin-bottom: 20px;">🚫</div>
        <h1 style="font-size: 2.5em; margin-bottom: 16px; background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
          Site Blocked
        </h1>
        <p style="font-size: 1.1em; margin-bottom: 8px; color: #ccc;">
          <strong>${window.location.hostname}</strong> is blocked during your focus session.
        </p>
        <p style="font-size: 1em; opacity: 0.7; margin-bottom: 32px;">
          Stay focused on your goals! 💪 Every minute counts.
        </p>
        <button onclick="history.back()" style="
          padding: 12px 32px;
          background: linear-gradient(135deg, #667eea, #764ba2);
          border: none;
          color: white;
          border-radius: 25px;
          cursor: pointer;
          font-size: 1em;
          font-weight: 600;
          transition: all 0.3s;
        ">← Go Back</button>
      </div>
    `;
  }

  function showFocusOverlay() {
    if (focusOverlay) return;

    focusOverlay = document.createElement('div');
    focusOverlay.style.cssText = `
      position: fixed; top: 0; left: 0; width: 100%; height: 100%;
      background: rgba(0,0,0,0.85); z-index: 999999;
      display: flex; align-items: center; justify-content: center;
      color: white; font-family: 'Segoe UI', Arial, sans-serif; text-align: center;
    `;
    focusOverlay.innerHTML = `
      <div>
        <h2 style="font-size: 1.5em;">🎯 Focus Mode Active</h2>
        <p style="margin: 12px 0; opacity: 0.8;">Take a deep breath and stay on task</p>
        <button onclick="this.parentElement.parentElement.remove()" style="
          margin-top: 16px; padding: 10px 24px;
          background: #4CAF50; color: white; border: none;
          border-radius: 8px; cursor: pointer; font-size: 1em;
        ">Continue</button>
      </div>
    `;
    document.body.appendChild(focusOverlay);

    setTimeout(() => {
      if (focusOverlay) { focusOverlay.remove(); focusOverlay = null; }
    }, 3000);
  }

  function hideFocusOverlay() {
    if (focusOverlay) { focusOverlay.remove(); focusOverlay = null; }
  }
})();