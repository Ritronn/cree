// Popup script — manages blocked sites + stats display
document.addEventListener('DOMContentLoaded', () => {
  loadStats();
  loadSettings();
  renderBlockedSites();

  // Live stats refresh
  setInterval(loadStats, 1000);

  // Event listeners
  document.getElementById('resetSession').addEventListener('click', resetSession);
  document.getElementById('studyMode').addEventListener('change', updateStudyMode);
  document.getElementById('focusTimer').addEventListener('click', startFocusTimer);
  document.getElementById('addSiteBtn').addEventListener('click', addSite);

  // Enter key = add site
  document.getElementById('newSiteInput').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') addSite();
  });
});

// ─── Stats ──────────────────────────────────────────────────────────────
async function loadStats() {
  const data = await chrome.storage.local.get(['tabSwitchCount', 'sessionStartTime', 'attentionScore']);

  document.getElementById('tabSwitches').textContent = data.tabSwitchCount || 0;

  const sessionTime = Math.floor((Date.now() - (data.sessionStartTime || Date.now())) / 60000);
  document.getElementById('sessionTime').textContent = sessionTime + 'm';

  const score = data.attentionScore || 100;
  const el = document.getElementById('attentionScore');
  el.textContent = Math.round(score) + '%';
  el.className = 'score ' + (score >= 80 ? 'good' : score >= 60 ? 'warning' : 'danger');
}

// ─── Settings ───────────────────────────────────────────────────────────
async function loadSettings() {
  const data = await chrome.storage.local.get(['studyMode']);
  document.getElementById('studyMode').value = data.studyMode || 'focus';
  updateBlockingStatus(data.studyMode || 'focus');
}

function updateStudyMode() {
  const mode = document.getElementById('studyMode').value;
  chrome.storage.local.set({ studyMode: mode });
  chrome.runtime.sendMessage({ action: 'updateSettings', data: { studyMode: mode } });
  updateBlockingStatus(mode);
}

function updateBlockingStatus(mode) {
  const el = document.getElementById('blockingStatus');
  if (mode === 'basic') {
    el.className = 'blocking-status blocking-inactive';
    el.innerHTML = '<div class="status-dot inactive"></div><span>Blocking is OFF (Basic Mode)</span>';
  } else {
    el.className = 'blocking-status blocking-active';
    const label = mode === 'exam' ? 'Strict blocking (Exam Mode)' : 'Blocking is active (Focus Mode)';
    el.innerHTML = `<div class="status-dot active"></div><span>${label}</span>`;
  }
}

// ─── Blocked Sites CRUD ─────────────────────────────────────────────────
async function renderBlockedSites() {
  const data = await chrome.storage.local.get(['blockedSites']);
  const sites = data.blockedSites || [];
  const container = document.getElementById('siteList');

  if (sites.length === 0) {
    container.innerHTML = '<div class="empty-list">No sites blocked. Add one above!</div>';
    return;
  }

  container.innerHTML = sites.map(site => `
    <div class="site-item">
      <span class="site-name">🚫 ${site}</span>
      <button class="btn-remove" data-site="${site}" title="Remove">✕</button>
    </div>
  `).join('');

  // Wire up remove buttons
  container.querySelectorAll('.btn-remove').forEach(btn => {
    btn.addEventListener('click', () => removeSite(btn.dataset.site));
  });
}

async function addSite() {
  const input = document.getElementById('newSiteInput');
  let site = input.value.trim().toLowerCase();

  if (!site) return;

  // Clean the input: remove protocol, www, trailing slashes
  site = site.replace(/^https?:\/\//, '').replace(/^www\./, '').replace(/\/.*$/, '');

  if (!site) return;

  const data = await chrome.storage.local.get(['blockedSites']);
  const sites = data.blockedSites || [];

  // Don't add duplicates
  if (sites.includes(site)) {
    input.value = '';
    input.placeholder = 'Already blocked!';
    setTimeout(() => { input.placeholder = 'e.g. facebook.com or instagram'; }, 1500);
    return;
  }

  sites.push(site);
  await chrome.storage.local.set({ blockedSites: sites });

  // Notify background to update blocking rules
  chrome.runtime.sendMessage({ action: 'updateSettings', data: { blockedSites: sites } });

  input.value = '';
  renderBlockedSites();
}

async function removeSite(siteToRemove) {
  const data = await chrome.storage.local.get(['blockedSites']);
  const sites = (data.blockedSites || []).filter(s => s !== siteToRemove);
  await chrome.storage.local.set({ blockedSites: sites });

  // Notify background to update blocking rules
  chrome.runtime.sendMessage({ action: 'updateSettings', data: { blockedSites: sites } });

  renderBlockedSites();
}

// ─── Actions ────────────────────────────────────────────────────────────
function resetSession() {
  chrome.runtime.sendMessage({ action: 'resetSession' }, (response) => {
    if (response && response.success) loadStats();
  });
}

function startFocusTimer() {
  // Also set mode to focus if currently on basic
  const modeSelect = document.getElementById('studyMode');
  if (modeSelect.value === 'basic') {
    modeSelect.value = 'focus';
    updateStudyMode();
  }

  chrome.notifications.create({
    type: 'basic',
    iconUrl: 'icon48.png',
    title: '⏱ Focus Session Started',
    message: '25 minutes of focused work. Distracting sites are blocked!'
  });

  setTimeout(() => {
    chrome.notifications.create({
      type: 'basic',
      iconUrl: 'icon48.png',
      title: '🎉 Focus Session Complete!',
      message: 'Great job! Take a 5 minute break.'
    });
  }, 25 * 60 * 1000);
}