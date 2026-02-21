# Kaizer Focus Browser Extension

A Chrome extension for tab monitoring, website blocking, and focus tracking.

## Features

### ✅ Implemented (Core 2-hour build)
- **Tab Switch Monitoring**: Tracks how often you switch tabs
- **Attention Drift Score**: Calculates focus score based on behavior
- **Website Blocking**: Block distracting sites during focus sessions
- **Study Modes**: Basic and Exam modes with different restriction levels
- **Focus Nudges**: Pop-up notifications when attention drops
- **Session Tracking**: Monitor focus session duration
- **Pomodoro Timer**: 25-minute focus sessions

### 🔄 Current Capabilities
- Real-time tab switch counting
- Dynamic attention score calculation
- Customizable blocked site lists
- Study mode switching (Basic/Exam)
- Focus session reset functionality
- Beautiful blocked page with motivation

## Installation

1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode" (top right toggle)
3. Click "Load unpacked"
4. Select the `browser-extension` folder
5. The extension icon should appear in your toolbar

## Usage

### Basic Setup
1. Click the extension icon to open the popup
2. Select your study mode (Basic or Exam)
3. Start a focus session with the "Start 25min Focus" button

### Study Modes
- **Basic Mode**: Blocks major social media sites
- **Exam Mode**: High restriction mode with additional blocked sites

### Monitoring
- View real-time tab switch count
- Monitor your attention score (100% = perfect focus)
- Track session duration

## Default Blocked Sites
- facebook.com
- twitter.com  
- instagram.com
- youtube.com
- reddit.com (Exam mode only)
- tiktok.com (Exam mode only)

## Technical Details

### Files Structure
```
browser-extension/
├── manifest.json       # Extension configuration
├── background.js       # Service worker for monitoring
├── popup.html         # Extension popup interface
├── popup.js           # Popup functionality
├── content.js         # Website blocking logic
├── blocked.html       # Blocked site page
└── README.md          # This file
```

### Permissions Used
- `tabs`: Monitor tab switches
- `storage`: Save settings and stats
- `notifications`: Show focus nudges
- `webNavigation`: Detect site navigation
- `<all_urls>`: Block any website

## Integration with Main App

The extension can communicate with your main Kaizer app at `http://localhost:3000`. Users can click "Open Kaizer App" from blocked pages to return to the main platform.

## Future Enhancements (Beyond 2 hours)

- Sync with main app database
- Advanced analytics dashboard
- Custom blocked site management
- Focus streak tracking
- Productivity insights
- Team/group focus sessions
- Advanced notification customization

## Development Notes

This is a minimal viable product built in 2 hours focusing on core functionality. The extension uses Manifest V3 and modern Chrome APIs for optimal performance and security.