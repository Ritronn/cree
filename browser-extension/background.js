// Background service worker for tab monitoring & website blocking
let tabSwitchCount = 0;
let currentTabId = null;
let sessionStartTime = Date.now();
let focusStartTime = Date.now();
let blockedSites = [];
let studyMode = 'focus';

// ─── Initialize ─────────────────────────────────────────────────────────
chrome.runtime.onInstalled.addListener(() => {
  chrome.storage.local.set({
    tabSwitchCount: 0,
    sessionStartTime: Date.now(),
    blockedSites: ['facebook.com', 'twitter.com', 'instagram.com', 'reddit.com', 'tiktok.com'],
    studyMode: 'focus',
    attentionScore: 100
  });
  console.log('[MindForge] Extension installed — default sites blocked');
});

// Load persisted settings on startup
chrome.storage.local.get(['blockedSites', 'studyMode'], (data) => {
  blockedSites = data.blockedSites || [];
  studyMode = data.studyMode || 'focus';
  console.log('[MindForge] Loaded settings:', { blockedSites, studyMode });
});

// ─── Tab Switch Monitoring ──────────────────────────────────────────────
chrome.tabs.onActivated.addListener(async (activeInfo) => {
  if (currentTabId && currentTabId !== activeInfo.tabId) {
    tabSwitchCount++;

    const timeSinceFocus = Date.now() - focusStartTime;
    const attentionScore = calculateAttentionScore(tabSwitchCount, timeSinceFocus);

    chrome.storage.local.set({
      tabSwitchCount: tabSwitchCount,
      attentionScore: attentionScore
    });

    // Send stats to the web app tabs
    chrome.tabs.query({ url: ["http://localhost:3000/*", "http://localhost:5173/*", "https://*.vercel.app/*"] }, (tabs) => {
      const statsData = {
        tabSwitches: tabSwitchCount,
        attentionScore: attentionScore,
        sessionTime: Math.floor((Date.now() - sessionStartTime) / 60000),
        studyMode: studyMode,
        isExtensionActive: true
      };
      tabs.forEach(tab => {
        chrome.tabs.sendMessage(tab.id, { type: 'EXTENSION_STATS', data: statsData }).catch(() => { });
      });
    });

    // Focus nudge
    if (attentionScore < 70 && tabSwitchCount > 5) {
      showFocusNudge();
    }
  }

  currentTabId = activeInfo.tabId;
  focusStartTime = Date.now();
});

// ─── Website Blocking (webNavigation) ───────────────────────────────────
chrome.webNavigation.onBeforeNavigate.addListener(async (details) => {
  if (details.frameId !== 0) return; // Main frame only

  try {
    const url = new URL(details.url);
    // Skip chrome:// and extension pages
    if (url.protocol === 'chrome:' || url.protocol === 'chrome-extension:') return;

    const data = await chrome.storage.local.get(['blockedSites', 'studyMode']);
    const sites = data.blockedSites || [];
    const mode = data.studyMode || 'focus';

    if (shouldBlock(url.hostname, url.href, sites, mode)) {
      console.log(`[MindForge] 🚫 Blocking: ${url.hostname}`);
      chrome.tabs.update(details.tabId, {
        url: chrome.runtime.getURL('blocked.html') + '?site=' + encodeURIComponent(url.hostname)
      });
    }
  } catch (e) {
    // Invalid URL, ignore
  }
});

// ─── Blocking Logic ─────────────────────────────────────────────────────
function shouldBlock(hostname, fullUrl, blockedSites, mode) {
  // Basic mode = no blocking at all
  if (mode === 'basic') return false;

  // Normalize hostname
  hostname = hostname.toLowerCase().replace(/^www\./, '');

  // Check user's custom block list — works in both Focus and Exam modes
  const isInBlockList = blockedSites.some(site => {
    const cleanSite = site.toLowerCase().replace(/^www\./, '');
    // Match if hostname contains the blocked site name
    // e.g. "facebook.com" matches "m.facebook.com", "www.facebook.com"
    // e.g. "instagram" matches "instagram.com", "www.instagram.com"
    return hostname.includes(cleanSite) || cleanSite.includes(hostname);
  });

  if (isInBlockList) return true;

  // Exam mode: also block common distractions not in the user's list
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

// ─── Attention Score ────────────────────────────────────────────────────
function calculateAttentionScore(switches, timeSpent) {
  const baseScore = 100;
  const switchPenalty = switches * 2;
  const timeFactor = Math.min(timeSpent / (5 * 60 * 1000), 1);
  return Math.max(0, Math.min(100, baseScore - switchPenalty + (timeFactor * 10)));
}

// ─── Focus Nudge ────────────────────────────────────────────────────────
function showFocusNudge() {
  chrome.notifications.create({
    type: 'basic',
    iconUrl: 'icon48.png',
    title: '🎯 Stay Focused!',
    message: "You've been switching tabs frequently. Stay focused for 5 more minutes!"
  });
}

// ─── Message Handler ────────────────────────────────────────────────────
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
    sendResponse({ success: true });
  }

  if (request.action === 'getStats') {
    sendResponse({
      tabSwitches: tabSwitchCount,
      attentionScore: calculateAttentionScore(tabSwitchCount, Date.now() - focusStartTime),
      sessionTime: Math.floor((Date.now() - sessionStartTime) / 60000),
      studyMode: studyMode
    });
  }

  if (request.action === 'updateSettings') {
    const newData = request.data || {};
    chrome.storage.local.set(newData);

    if (newData.blockedSites) {
      blockedSites = newData.blockedSites;
      console.log('[MindForge] Updated blocked sites:', blockedSites);
    }
    if (newData.studyMode) {
      studyMode = newData.studyMode;
      console.log('[MindForge] Study mode changed to:', studyMode);
    }
    sendResponse({ success: true });
  }

  return true; // Keep message channel open for async responses
});