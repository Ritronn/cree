# Eisenhower Matrix Integration Guide

## Overview
The Eisenhower Matrix project has been successfully integrated with your main adaptive learning platform. The integration uses direct URL linking to connect the two applications.

## Running Both Applications

### Backend (Django API)
```bash
cd cree-eisenhower_matrix/backend
python manage.py runserver
```
- Runs on: **http://localhost:8000**
- API Base: **http://localhost:8000/api**

### Frontend (React/Vite)
```bash
cd cree-eisenhower_matrix/frontend
npm run dev
```
- Runs on: **http://localhost:5174**

## Integration Points

### 1. Eisenhower Matrix
- **URL**: `http://localhost:5174`
- **API Endpoint**: `http://localhost:8000/api/tasks/`
- **Features**:
  - Create and manage tasks
  - Auto-categorization by urgency & importance
  - 4-quadrant view (Urgent/Important matrix)
  - Google Calendar sync
  - Drag & drop task management

### 2. Que Cards (Flashcards)
- **URL**: `http://localhost:5174?tab=flashcards`
- **API Endpoint**: `http://localhost:8000/api/flashcards/`
- **Features**:
  - AI-generated flashcards from tasks
  - Study mode with flip animations
  - Progress tracking
  - Custom flashcard generation

### 3. Roadmap
- **URL**: `http://localhost:5174?tab=roadmap`
- **API Endpoint**: `http://localhost:8000/api/roadmap/list/`
- **Features**:
  - Visual learning paths from roadmap.sh
  - Convert roadmap topics to tasks
  - Track progress through learning paths
  - Multiple technology roadmaps

## API Endpoints Summary

### Tasks API
- `GET /api/tasks/` - List all tasks
- `POST /api/tasks/` - Create new task
- `PATCH /api/tasks/{id}/` - Update task
- `DELETE /api/tasks/{id}/` - Delete task
- `POST /api/tasks/{id}/sync_calendar/` - Sync to Google Calendar
- `PATCH /api/tasks/{id}/move/` - Move task to different quadrant

### Flashcards API
- `GET /api/flashcards/` - List all flashcards
- `POST /api/flashcards/generate/` - Generate flashcards from task
- `PATCH /api/flashcards/{id}/` - Update flashcard
- `DELETE /api/flashcards/{id}/` - Delete flashcard

### Roadmap API
- `GET /api/roadmap/list/` - List available roadmaps
- `GET /api/roadmap/data/{slug}/` - Get roadmap details
- `POST /api/roadmap/generate/` - Generate roadmap
- `POST /api/roadmap/to-tasks/` - Convert roadmap topics to tasks

### Calendar API
- `GET /api/calendar/status/` - Check calendar configuration
- `GET /api/calendar/callback/` - OAuth callback handler

## Frontend Integration

The main learning platform's sidebar (`frontend/src/components/FeatureSidebar.jsx`) contains links to all three productivity tools:

```javascript
const CREE_BASE_URL = 'http://localhost:5174';
const CREE_API_URL = 'http://localhost:8000/api';
```

Each menu item opens the Eisenhower Matrix app in a new tab with the appropriate view:
- **Eisenhower Matrix**: Opens main task matrix view
- **Que Cards**: Opens with `?tab=flashcards` parameter
- **Roadmap**: Opens with `?tab=roadmap` parameter

## Configuration

### Backend Environment Variables
Located in `cree-eisenhower_matrix/backend/.env`:
- Database credentials (Supabase PostgreSQL)
- Google OAuth credentials (for Calendar sync)
- Groq API key (for AI task classification)
- Redis configuration (for Celery tasks)

### Frontend Configuration
Located in `cree-eisenhower_matrix/frontend/src/api/client.js`:
- API base URL defaults to `http://localhost:8000`
- Can be overridden with `VITE_API_BASE_URL` environment variable

## Features Overview

### AI-Powered Task Classification
Tasks are automatically categorized using Groq AI based on:
- **Urgency Score** (0.0-1.0): Calculated from deadline proximity
- **Importance Score** (0.0-1.0): Calculated from estimated time
- **Quadrant Assignment**: 
  - Urgent & Important (Do First)
  - Important but Not Urgent (Schedule)
  - Urgent but Not Important (Delegate)
  - Neither (Eliminate)

### Google Calendar Integration
- OAuth 2.0 authentication
- Sync tasks to Google Calendar
- Automatic event creation with deadlines
- Two-way sync support

### Flashcard Generation
- AI-powered flashcard creation from task descriptions
- Customizable scope (basic, detailed, comprehensive)
- Study mode with progress tracking
- Export/import capabilities

### Roadmap Integration
- Fetches learning paths from roadmap.sh
- Converts roadmap topics into actionable tasks
- Visual progress tracking
- Multiple technology domains supported

## Troubleshooting

### Backend Not Starting
- Check if port 8000 is available
- Verify database connection in `.env`
- Run migrations: `python manage.py migrate`

### Frontend Not Starting
- Check if port 5174 is available
- Clear node_modules and reinstall: `rm -rf node_modules && npm install`
- Check for conflicting processes

### CORS Issues
- Backend CORS is configured for `http://localhost:5174`
- If using different ports, update `CORS_ALLOWED_ORIGINS` in `settings.py`

### API Connection Failed
- Verify both backend and frontend are running
- Check browser console for error messages
- Ensure API_BASE_URL is correctly configured

## Next Steps

1. **User Authentication**: Currently uses demo mode without auth
2. **Data Sync**: Implement sync between learning platform and task manager
3. **Unified Dashboard**: Show task stats in main dashboard
4. **Deep Integration**: Embed components instead of external links
5. **Shared Database**: Use same database for both applications

## Support

For issues or questions:
- Check the README files in each project directory
- Review API documentation in backend code
- Check browser console for frontend errors
- Verify all environment variables are set correctly
