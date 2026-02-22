// Background service worker for tab monitoring
let tabSwitchCount = 0;
let currentTabId = null;
let sessionStartTime = Date.now();
let focusStartTime = Date.now();
let blockedSites = [];
let studyMode = 'basic';

// Initialize extension
chrome.runtime.onInstalled.addListener(() => {
  chrome.storage.local.set({
    tabSwitchCount: 0,
    sessionStartTime: Date.now(),
    blockedSites: ['facebook.com', 'twitter.com', 'instagram.com', 'youtube.com'],
    studyMode: 'basic',
    attentionScore: 100
  });
});

// Monitor tab switches
chrome.tabs.onActivated.addListener(async (activeInfo) => {
  if (currentTabId && currentTabId !== activeInfo.tabId) {
    tabSwitchCount++;
    
    // Calculate attention drift
    const timeSinceFocus = Date.now() - focusStartTime;
    const attentionScore = calculateAttentionScore(tabSwitchCount, timeSinceFocus);
    
    // Store data and send to content script
    chrome.storage.local.set({
      tabSwitchCount: tabSwitchCount,
      attentionScore: attentionScore
    });
    
    // Send to deployed app tabs via content script
    chrome.tabs.query({url: ["http://localhost:3000/*", "https://*.vercel.app/*"]}, (tabs) => {
      const statsData = {
        tabSwitches: tabSwitchCount,
        attentionScore: attentionScore,
        sessionTime: Math.floor((Date.now() - sessionStartTime) / 60000),
        studyMode: studyMode,
        isExtensionActive: true
      };
      
      tabs.forEach(tab => {
        chrome.tabs.sendMessage(tab.id, {
          type: 'EXTENSION_STATS',
          data: statsData
        }).catch(() => {});
      });
    });
    
    // Show nudge if attention is dropping
    if (attentionScore < 70 && tabSwitchCount > 5) {
      showFocusNudge();
    }
  }
  
  currentTabId = activeInfo.tabId;
  focusStartTime = Date.now();
});

// Send stats to web app
function sendStatsToWebApp(stats) {
  chrome.tabs.query({url: "http://localhost:3000/*"}, (tabs) => {
    tabs.forEach(tab => {
      chrome.tabs.sendMessage(tab.id, {
        type: 'EXTENSION_STATS',
        data: stats
      }).catch(() => {});
    });
  });
}

// Monitor navigation to blocked sites
chrome.webNavigation.onBeforeNavigate.addListener(async (details) => {
  if (details.frameId === 0) { // Main frame only
    const url = new URL(details.url);
    const data = await chrome.storage.local.get(['blockedSites', 'studyMode']);
    
    if (data.blockedSites && isBlocked(url.hostname, data.blockedSites, data.studyMode)) {
      chrome.tabs.update(details.tabId, {
        url: chrome.runtime.getURL('blocked.html') + '?site=' + encodeURIComponent(url.hostname)
      });
    }
  }
});

// Calculate attention score based on tab switches and time
function calculateAttentionScore(switches, timeSpent) {
  const baseScore = 100;
  const switchPenalty = switches * 2;
  const timeFactor = Math.min(timeSpent / (5 * 60 * 1000), 1); // 5 minutes max bonus
  
  return Math.max(0, Math.min(100, baseScore - switchPenalty + (timeFactor * 10)));
}

// Check if site is blocked based on study mode
function isBlocked(hostname, blockedSites, mode) {
  // Only block sites in exam mode
  if (mode !== 'exam') {
    return false;
  }
  
  const isInBlockList = blockedSites.some(site => hostname.includes(site));
  
  // In exam mode, block all social media and entertainment
  return isInBlockList || hostname.includes('reddit.com') || hostname.includes('tiktok.com');
}

// Show focus nudge notification
function showFocusNudge() {
  chrome.notifications.create({
    type: 'basic',
    iconUrl: 'icon48.png',
    title: 'Stay Focused!',
    message: 'You\'ve been switching tabs frequently. Stay focused for 5 more minutes!'
  });
}

// Reset session data
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'resetSession') {
    tabSwitchCount = 0;
    sessionStartTime = Date.now();
    focusStartTime = Date.now();
    
    chrome.storage.local.set({
      tabSwitchCount: 0,
      sessionStartTime: Date.now(),
      attentionScore: 100
    });
    
    sendResponse({success: true});
  }
  
  if (request.action === 'getStats') {
    const stats = {
      tabSwitches: tabSwitchCount,
      attentionScore: calculateAttentionScore(tabSwitchCount, Date.now() - focusStartTime),
      sessionTime: Math.floor((Date.now() - sessionStartTime) / 60000),
      studyMode: studyMode
    };
    sendResponse(stats);
  }
  
  if (request.action === 'updateSettings') {
    chrome.storage.local.set(request.data);
    blockedSites = request.data.blockedSites || blockedSites;
    studyMode = request.data.studyMode || studyMode;
    sendResponse({success: true});
  }
});