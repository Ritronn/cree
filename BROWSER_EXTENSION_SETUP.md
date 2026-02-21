# Browser Extension Setup Guide

## Overview

The browser extension monitors tab switches and blocks distracting websites during study sessions. It integrates with the backend API to track violations and maintain focus.

## Installation

### 1. Load Extension in Chrome

1. Open Chrome browser
2. Navigate to `chrome://extensions/`
3. Enable "Developer mode" (toggle in top right)
4. Click "Load unpacked"
5. Select the `browser-extension` folder from your project
6. Extension should appear in your extensions list

### 2. Pin Extension

1. Click the puzzle icon in Chrome toolbar
2. Find "MindForge Focus Extension"
3. Click the pin icon to keep it visible

## Configuration

### Update Backend URL

If your backend is not on `localhost:8000`, update the API URL in `browser-extension/background.js`:

```javascript
const API_BASE_URL = 'http://localhost:8000/api/adaptive';
```

### Blocked Sites List

Default blocked sites are defined in `background.js`. You can customize them:

```javascript
const BLOCKED_SITES = [
  'facebook.com',
  'twitter.com',
  'instagram.com',
  'youtube.com',
  'reddit.com',
  'tiktok.com',
  'netflix.com'
];
```

## How It Works

### 1. Session Activation

When a study session starts:
1. Frontend sends session ID to extension
2. Extension activates monitoring
3. Starts tracking tab switches
4. Blocks configured websites

### 2. Tab Monitoring

Extension tracks:
- Tab switches (changing active tab)
- New tab creation
- Tab navigation
- Focus changes

### 3. Website Blocking

When user tries to visit blocked site:
- Request is intercepted
- User is redirected to blocked page
- Violation is logged to backend
- Notification is shown

### 4. Heartbeat

Extension sends heartbeat every 30 seconds:
- Current tab switch count
- Blocked attempt count
- Extension active status
- Session ID

### 5. Data Sync

All events are synced to backend:
- `POST /api/adaptive/extension/heartbeat/`
- `POST /api/adaptive/extension/violation/`

## Frontend Integration

### Activate Extension

In your study session component:

```javascript
// Check if extension is installed
const checkExtension = () => {
  if (window.chrome && chrome.runtime) {
    chrome.runtime.sendMessage(
      EXTENSION_ID,
      { action: 'ping' },
      (response) => {
        if (response && response.status === 'ok') {
          console.log('Extension is installed');
        }
      }
    );
  }
};

// Start monitoring
const startExtensionMonitoring = (sessionId) => {
  if (window.chrome && chrome.runtime) {
    chrome.runtime.sendMessage(
      EXTENSION_ID,
      {
        action: 'startMonitoring',
        sessionId: sessionId
      },
      (response) => {
        console.log('Extension monitoring started:', response);
      }
    );
  }
};

// Stop monitoring
const stopExtensionMonitoring = () => {
  if (window.chrome && chrome.runtime) {
    chrome.runtime.sendMessage(
      EXTENSION_ID,
      { action: 'stopMonitoring' },
      (response) => {
        console.log('Extension monitoring stopped:', response);
      }
    );
  }
};
```

### Get Extension ID

After loading the extension:
1. Go to `chrome://extensions/`
2. Find "MindForge Focus Extension"
3. Copy the ID (long string under the name)
4. Add to your frontend code:

```javascript
const EXTENSION_ID = 'your_extension_id_here';
```

## Extension Files

### background.js
- Service worker running in background
- Handles tab monitoring
- Manages blocked sites
- Sends data to backend API

### content.js
- Runs on all web pages
- Detects copy/paste attempts
- Monitors page interactions
- Communicates with background script

### popup.html & popup.js
- Extension popup UI
- Shows current status
- Displays statistics
- Allows manual control

### blocked.html
- Page shown when site is blocked
- Explains why site is blocked
- Provides option to end session

## Testing Extension

### 1. Test Installation
1. Load extension
2. Check for errors in `chrome://extensions/`
3. Click extension icon - popup should open

### 2. Test Monitoring
1. Start a study session in the app
2. Extension should activate automatically
3. Try switching tabs - should be counted
4. Try visiting blocked site - should be blocked

### 3. Test API Integration
1. Open browser DevTools (F12)
2. Go to Network tab
3. Start study session
4. Should see POST requests to `/api/adaptive/extension/heartbeat/`

### 4. Test Blocking
1. Start study session
2. Try to visit `facebook.com`
3. Should be redirected to blocked page
4. Check backend - violation should be logged

## Troubleshooting

### Extension Not Loading
- Check manifest.json for syntax errors
- Ensure all files exist
- Check Chrome version (requires Manifest V3 support)
- Look for errors in `chrome://extensions/`

### Not Communicating with Frontend
- Check externally_connectable in manifest.json
- Verify frontend URL matches (localhost:5173)
- Check extension ID is correct
- Look for CORS errors in console

### Not Sending Data to Backend
- Verify backend is running on localhost:8000
- Check API_BASE_URL in background.js
- Look for network errors in DevTools
- Verify session ID is being passed

### Sites Not Being Blocked
- Check BLOCKED_SITES array in background.js
- Verify extension has necessary permissions
- Check if monitoring is active
- Look for errors in extension console

## Extension Console

To view extension logs:
1. Go to `chrome://extensions/`
2. Find "MindForge Focus Extension"
3. Click "Inspect views: service worker"
4. DevTools will open showing extension logs

## Permissions Explained

- **tabs**: Monitor tab switches
- **activeTab**: Access current tab info
- **storage**: Store session data
- **notifications**: Show blocking notifications
- **webNavigation**: Detect navigation events
- **host_permissions**: Access all URLs for blocking

## Data Stored

Extension stores in Chrome storage:
- Current session ID
- Tab switch count
- Blocked attempt count
- Monitoring active status
- Blocked sites list

## Privacy

- Extension only active during study sessions
- No data collected when not monitoring
- All data sent to your own backend
- No third-party tracking
- Can be disabled anytime

## Customization

### Add More Blocked Sites

Edit `background.js`:
```javascript
const BLOCKED_SITES = [
  'facebook.com',
  'twitter.com',
  'your-site.com'  // Add here
];
```

### Change Heartbeat Interval

Edit `background.js`:
```javascript
const HEARTBEAT_INTERVAL = 30000; // Change from 30s to your preference
```

### Customize Blocked Page

Edit `blocked.html` to change the appearance and message shown when a site is blocked.

## Integration with Study Session

### Automatic Activation

When user starts study session:
1. Frontend creates session via API
2. Receives session ID
3. Sends message to extension with session ID
4. Extension starts monitoring
5. Heartbeat begins

### During Session

Extension continuously:
- Counts tab switches
- Blocks distracting sites
- Sends heartbeat every 30s
- Logs violations to backend

### Session End

When user ends session:
1. Frontend sends stop message to extension
2. Extension stops monitoring
3. Sends final heartbeat
4. Clears session data

## Backend Integration

### Heartbeat Endpoint

```python
POST /api/adaptive/extension/heartbeat/
{
  "session_id": 123,
  "tab_switches": 5,
  "blocked_attempts": 2,
  "extension_active": true
}
```

### Violation Endpoint

```python
POST /api/adaptive/extension/violation/
{
  "session_id": 123,
  "event_type": "tab_switch" | "blocked_site",
  "url": "https://example.com"
}
```

### Status Endpoint

```python
GET /api/adaptive/extension/status/?session_id=123
```

## Future Enhancements

Possible improvements:
- Whitelist for allowed sites
- Time-based blocking rules
- Productivity scoring
- Focus time tracking
- Break reminders
- Custom block messages
- Site-specific time limits

## Support

If extension doesn't work:
1. Check Chrome version (must support Manifest V3)
2. Verify all permissions granted
3. Check extension console for errors
4. Ensure backend is running
5. Test API endpoints manually
6. Review network requests in DevTools

## Uninstallation

To remove extension:
1. Go to `chrome://extensions/`
2. Find "MindForge Focus Extension"
3. Click "Remove"
4. Confirm removal

Extension data will be cleared from Chrome storage.

---

**Extension Status: ✅ Ready to Use**

The extension is fully functional and integrated with the backend API. Load it in Chrome and start a study session to see it in action!
