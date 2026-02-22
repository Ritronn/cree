// Popup script
document.addEventListener('DOMContentLoaded', async () => {
  loadStats();
  loadSettings();
  
  // Update stats every second
  setInterval(loadStats, 1000);
  
  // Event listeners
  document.getElementById('resetSession').addEventListener('click', resetSession);
  document.getElementById('studyMode').addEventListener('change', updateStudyMode);
  document.getElementById('focusTimer').addEventListener('click', startFocusTimer);
});

async function loadStats() {
  const data = await chrome.storage.local.get(['tabSwitchCount', 'sessionStartTime', 'attentionScore']);
  
  document.getElementById('tabSwitches').textContent = data.tabSwitchCount || 0;
  
  const sessionTime = Math.floor((Date.now() - (data.sessionStartTime || Date.now())) / 60000);
  document.getElementById('sessionTime').textContent = sessionTime + 'm';
  
  const score = data.attentionScore || 100;
  const scoreElement = document.getElementById('attentionScore');
  scoreElement.textContent = Math.round(score) + '%';
  
  scoreElement.className = score >= 80 ? 'good' : score >= 60 ? 'warning' : 'danger';
}

async function loadSettings() {
  const data = await chrome.storage.local.get(['studyMode', 'blockedSites']);
  
  document.getElementById('studyMode').value = data.studyMode || 'basic';
  
  const blockedSites = data.blockedSites || [];
  document.getElementById('blockedSites').innerHTML = blockedSites.join('<br>') || 'None';
}

function resetSession() {
  chrome.runtime.sendMessage({action: 'resetSession'}, (response) => {
    if (response.success) {
      loadStats();
    }
  });
}

function updateStudyMode() {
  const mode = document.getElementById('studyMode').value;
  chrome.runtime.sendMessage({
    action: 'updateSettings',
    data: { studyMode: mode }
  });
}

function startFocusTimer() {
  chrome.notifications.create({
    type: 'basic',
    iconUrl: 'icon48.png',
    title: 'Focus Session Started',
    message: '25 minutes of focused work. Stay on task!'
  });
  
  setTimeout(() => {
    chrome.notifications.create({
      type: 'basic',
      iconUrl: 'icon48.png',
      title: 'Focus Session Complete!',
      message: 'Great job! Take a 5 minute break.'
    });
  }, 25 * 60 * 1000);
}