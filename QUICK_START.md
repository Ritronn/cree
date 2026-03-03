# Quick Start - Eisenhower Matrix Integration

## ✅ Current Status
Both applications are running and integrated!

## 🚀 Access URLs

### Main Learning Platform
- **Frontend**: Check your main app (likely running on a different port)
- **Sidebar Navigation**: Click on the productivity tools in the left sidebar

### Eisenhower Matrix App
- **Frontend**: http://localhost:5174
- **Backend API**: http://localhost:8000/api

## 📋 Available Features

### 1. Eisenhower Matrix (Task Manager)
**Click**: "Eisenhower Matrix" in sidebar
- ✨ AI-powered task classification
- 📊 4-quadrant priority view
- 📅 Google Calendar sync
- 🎯 Drag & drop task management

### 2. Que Cards (Flashcards)
**Click**: "Que Cards" in sidebar
- 🤖 AI-generated study cards
- 📚 Create from any task
- 🔄 Flip to study
- 📈 Track progress

### 3. Roadmap
**Click**: "Roadmap" in sidebar
- 🗺️ Visual learning paths
- 📖 Technology roadmaps from roadmap.sh
- ✅ Convert topics to tasks
- 🎓 Track learning progress

## 🔗 Integration Details

### How It Works
1. Your main app's sidebar has 3 productivity tool buttons
2. Each button opens the Eisenhower Matrix app in a new tab
3. URL parameters control which view opens:
   - No parameter → Matrix view
   - `?tab=flashcards` → Flashcards view
   - `?tab=roadmap` → Roadmap sidebar

### API Endpoints
All features use the Django backend at `http://localhost:8000/api`:
- `/api/tasks/` - Task management
- `/api/flashcards/` - Flashcard operations
- `/api/roadmap/` - Roadmap data
- `/api/calendar/` - Google Calendar sync

## 🎨 UI Features

### Eisenhower Matrix View
- **Red Quadrant**: Urgent & Important (Do First)
- **Yellow Quadrant**: Important but Not Urgent (Schedule)
- **Blue Quadrant**: Urgent but Not Important (Delegate)
- **Gray Quadrant**: Neither (Eliminate)

### Task Actions
- ✏️ Edit task details
- 🗑️ Delete tasks
- ✅ Mark complete
- 📅 Sync to calendar
- 📇 Generate flashcards
- 🔄 Drag between quadrants

### Flashcards View
- 📚 Browse all flashcards
- 🎴 Flip cards to study
- ➕ Generate new cards
- 🗑️ Delete cards
- 📊 Track study progress

### Roadmap View
- 🗺️ Browse technology roadmaps
- 📖 View learning paths
- ➕ Add topics to matrix
- ✅ Track completion

## 💡 Quick Tips

1. **Create Your First Task**
   - Click "+ New Task" in the matrix
   - Add title, description, deadline, and estimated time
   - AI automatically categorizes it!

2. **Generate Flashcards**
   - Click the 📇 icon on any task
   - Choose scope (basic/detailed/comprehensive)
   - AI generates study cards from the task

3. **Use Roadmaps**
   - Click "🗺️ Roadmap" button
   - Select a technology (e.g., Frontend, Backend)
   - Click "Add to Matrix" to create tasks

4. **Sync to Calendar**
   - Click 📅 on any task
   - Authorize Google Calendar (first time)
   - Task automatically syncs with deadline

## 🔧 Stopping the Servers

If you need to stop the Eisenhower Matrix servers:
- Backend: Press `Ctrl+C` in the backend terminal
- Frontend: Press `Ctrl+C` in the frontend terminal

## 📚 More Information

See `EISENHOWER_INTEGRATION.md` for:
- Complete API documentation
- Configuration details
- Troubleshooting guide
- Advanced features

## 🎯 Next Steps

1. Try creating a few tasks
2. Generate flashcards from a task
3. Explore different roadmaps
4. Sync a task to Google Calendar
5. Drag tasks between quadrants

Enjoy your integrated productivity tools! 🚀
