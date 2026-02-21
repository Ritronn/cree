# Complete Study System Requirements

## Overview
Build a comprehensive study session management system with proctoring, testing, and personalized recommendations.

## Core Features

### 1. Dashboard
- Show all study sessions created in the last week
- Display completion progress bar (tests given / total tests)
- Limit: Max 3 study sessions per day
- Block new sessions if previous tests not completed
- Show session status (pending test, completed, in progress)

### 2. Study Session Creation
- User provides workspace name only
- Two preset options:
  - Recommended: 2 hours study, 20 min break
  - Standard: 50 minutes study, 10 min break
- Option to end session anytime
- Upload files: PDF, DOCX, PPT

### 3. Browser Extension Integration
- Auto-activate extension when study window loads
- Track tab switching
- Block specified websites
- Count violations

### 4. Study Window
- Proper layout with all controls
- File upload area
- Timer display
- Break management
- End session button
- Extension status indicator

### 5. Test Generation (Post-Session)
- Send all uploaded files to Grok AI
- Generate 20-25 questions
- Test available for 6 hours after session ends
- Test attached to specific study session

### 6. Test Window (AMCAT-style)
- Left section: Question display (large)
- Right top: Camera feed (OpenCV)
- Right bottom: Question navigator
  - Green: Attempted
  - Red: Not attempted
- Full proctoring enabled

### 7. Test Submission & Results
- Auto-calculate score
- Send email report (using email API)
- Identify weak areas (e.g., "Python loops")
- Store weak points in database

### 8. Weak Point Analysis Model
- Store all weak areas per user
- Track topics with low scores
- Build user weakness profile

### 9. Course Recommendations
- Use WebScrappingModule scraper
- Suggest courses for weak areas
- Recommend YouTube playlists
- Suggest articles
- Display in frontend

## Technical Requirements

### Backend
- Study session limits (3 per day)
- Test generation with Grok AI
- Email integration
- Weak point tracking model
- Course recommendation integration
- File processing (PDF, DOCX, PPT)

### Frontend
- Modern dashboard
- Study session creation flow
- Study window with extension integration
- AMCAT-style test interface
- Camera integration
- Results display
- Recommendations page

### Integration
- Browser extension communication
- OpenCV for camera monitoring
- Email service (SendGrid/similar)
- Web scraping for recommendations
