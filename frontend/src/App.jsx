import { useState, useEffect, useCallback } from 'react';
import './App.css';
import Dashboard from './components/Dashboard';
import TaskForm from './components/TaskForm';
import RoadmapSidebar from './components/RoadmapSidebar';
import FlashcardsPage from './pages/FlashcardsPage';
import GenCardsModal from './components/GenCardsModal';
import apiClient from './api/client';

function App() {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [editingTask, setEditingTask] = useState(null);
  const [calendarStatus, setCalendarStatus] = useState(null);
  const [notification, setNotification] = useState(null);
  const [showRoadmap, setShowRoadmap] = useState(false);
  const [view, setView] = useState('matrix'); // 'matrix' | 'flashcards'
  const [flashcardPromptTask, setFlashcardPromptTask] = useState(null);
  const [googleToken, setGoogleToken] = useState(
    () => localStorage.getItem('google_calendar_token') || null
  );

  const showNotif = (msg, type = 'success') => {
    setNotification({ msg, type });
    setTimeout(() => setNotification(null), 4000);
  };

  // Check URL for Google Calendar callback params on mount
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const token = params.get('google_token');
    const calendarTask = params.get('calendar_task');
    const calendarError = params.get('calendar_error');

    if (token) {
      localStorage.setItem('google_calendar_token', token);
      setGoogleToken(token);
      showNotif('📅 Google Calendar connected!');

      // Clean URL
      window.history.replaceState({}, '', window.location.pathname);

      // If we have a task ID, auto-sync it
      if (calendarTask) {
        syncTaskToCalendar(calendarTask, token);
      }
    }

    if (calendarError) {
      showNotif(`Calendar error: ${calendarError}`, 'error');
      window.history.replaceState({}, '', window.location.pathname);
    }
  }, []);

  const syncTaskToCalendar = async (taskId, token) => {
    try {
      const response = await apiClient.post(`/api/tasks/${taskId}/sync_calendar/`, {
        access_token: token,
      });
      if (response.data && response.data.event_id) {
        setTasks(prev => prev.map(t =>
          t.id === taskId ? { ...t, google_calendar_event_id: response.data.event_id } : t
        ));
        showNotif('Task successfully synced to Google Calendar!');
      }
    } catch (err) {
      console.error('Calendar sync failed:', err);
      showNotif('Failed to sync to Google Calendar. Please reconnect.', 'error');
      // If unauthorized, clear token
      if (err.response?.status === 401 || err.response?.status === 403) {
        localStorage.removeItem('google_calendar_token');
        setGoogleToken(null);
      }
    }
  };

  // Fetch tasks from API
  const fetchTasks = useCallback(async () => {
    try {
      const res = await apiClient.get('/api/tasks/');
      const data = Array.isArray(res.data) ? res.data :
        (res.data && Array.isArray(res.data.results)) ? res.data.results : [];
      setTasks(data);
      setError(null);
    } catch (err) {
      console.error('Fetch error:', err);
      setError('Failed to connect to backend server. Please check if Django is running.');
    } finally {
      setLoading(false);
    }
  }, []);

  // Check Google Calendar status
  const fetchCalendarStatus = useCallback(async () => {
    try {
      const response = await apiClient.get('/api/calendar/status/');
      setCalendarStatus(response.data);
    } catch {
      setCalendarStatus({ configured: false });
    }
  }, []);

  const checkCalendarStatus = async () => {
    try {
      const res = await apiClient.get('/api/calendar/status/');
      setCalendarStatus(res.data);
    } catch (err) {
      setCalendarStatus({ configured: false });
    }
  };

  // Create task
  const handleCreateTask = async (formData, taskId = null) => {
    try {
      const payload = { ...formData };
      // Ensure deadline has timezone info for Django
      if (payload.deadline && !payload.deadline.includes('Z') && !payload.deadline.includes('+')) {
        payload.deadline = payload.deadline + ':00Z';
      }

      if (taskId) {
        await apiClient.patch(`/api/tasks/${taskId}/`, payload);
        showNotif('✨ Task updated and re-classified!');
      } else {
        await apiClient.post('/api/tasks/', payload);
        showNotif('✨ Task created and auto-classified!');
      }

      await fetchTasks();
      setShowForm(false);
      setEditingTask(null);
    } catch (err) {
      const errorData = err.response?.data;
      let errorMsg = taskId ? 'Failed to update task' : 'Failed to create task';
      if (errorData && typeof errorData === 'object') {
        const messages = Object.entries(errorData)
          .map(([key, val]) => `${key}: ${Array.isArray(val) ? val.join(', ') : val}`)
          .join('; ');
        if (messages) errorMsg = messages;
      }
      setError(errorMsg);
    }
  };

  const handleMoveTask = async (taskId, newQuadrant) => {
    setTasks(prev => prev.map(t =>
      t.id === taskId ? { ...t, quadrant: newQuadrant, is_manually_categorized: true } : t
    ));
    try {
      await apiClient.patch(`/api/tasks/${taskId}/move/`, { quadrant: newQuadrant });
      showNotif('Task moved successfully');
    } catch (err) {
      console.error('Move failed:', err);
      await fetchTasks();
      showNotif('Failed to move task', 'error');
    }
  };

  const handleDeleteTask = async (taskId) => {
    setTasks(prev => prev.filter(t => t.id !== taskId));
    try {
      await apiClient.delete(`/api/tasks/${taskId}/`);
      showNotif('Task deleted');
    } catch (err) {
      console.error('Delete failed:', err);
      await fetchTasks();
      showNotif('Failed to delete task', 'error');
    }
  };

  const handleToggleComplete = async (taskId, currentState) => {
    setTasks(prev => prev.map(t =>
      t.id === taskId ? { ...t, is_completed: !currentState } : t
    ));
    try {
      await apiClient.patch(`/api/tasks/${taskId}/`, { is_completed: !currentState });
      showNotif(currentState ? 'Task marked incomplete' : '✅ Task completed!');
    } catch (err) {
      await fetchTasks();
      showNotif('Failed to update task', 'error');
    }
  };

  const handleCalendarSync = async (taskId) => {
    if (googleToken) {
      try {
        const response = await apiClient.post(`/api/tasks/${taskId}/sync_calendar/`, {
          access_token: googleToken,
        });
        if (response.data.success) {
          showNotif('📅 Synced to Google Calendar!');
          await fetchTasks();
        } else if (response.data.need_auth) {
          localStorage.removeItem('google_calendar_token');
          setGoogleToken(null);
          window.open(response.data.auth_url, '_self');
        }
      } catch (err) {
        if (err.response?.status === 500) {
          localStorage.removeItem('google_calendar_token');
          setGoogleToken(null);
          showNotif('Calendar token expired. Click sync again to re-authorize.', 'info');
        } else {
          const msg = err.response?.data?.help || err.response?.data?.error || 'Calendar sync failed';
          showNotif(msg, 'error');
        }
      }
      return;
    }

    try {
      const response = await apiClient.post(`/api/tasks/${taskId}/sync_calendar/`, {});
      if (response.data.need_auth) {
        window.location.href = response.data.auth_url;
      } else if (response.data.success) {
        showNotif('📅 Synced to Google Calendar!');
        await fetchTasks();
      }
    } catch (err) {
      const msg = err.response?.data?.help || err.response?.data?.error || 'Calendar sync failed';
      showNotif(msg, 'error');
    }
  };

  const handleGenerateFlashcards = async (task, description, scope) => {
    setFlashcardPromptTask(null);
    showNotif('🪄 Analyzing & Generating Que-Que Cards...', 'info');
    try {
      const res = await apiClient.post('/api/flashcards/generate/', {
        task_id: task.id,
        topic: task.title,
        description: description,
        scope: scope
      });
      if (res.data.success) {
        showNotif(`📇 Generated ${res.data.count} revision cards!`);
      }
    } catch (err) {
      console.error('Failed to generate flashcards:', err);
      showNotif('Failed to generate cards.', 'error');
    }
  };

  const handleRoadmapAddToMatrix = (count) => {
    showNotif(`📚 Added ${count} roadmap topics to your matrix!`);
    fetchTasks();
  };

  useEffect(() => {
    fetchTasks();
    fetchCalendarStatus();
  }, [fetchTasks, fetchCalendarStatus]);

  const completedCount = tasks.filter(t => t.is_completed).length;
  const totalCount = tasks.length;
  const calendarReady = calendarStatus?.configured || !!googleToken;

  return (
    <div className={`app ${showRoadmap ? 'app-with-sidebar' : ''}`}>
      {/* Notification Toast */}
      {notification && (
        <div className={`toast toast-${notification.type}`}>
          {notification.msg}
        </div>
      )}

      {flashcardPromptTask && (
        <GenCardsModal
          task={flashcardPromptTask}
          onClose={() => setFlashcardPromptTask(null)}
          onSubmit={handleGenerateFlashcards}
        />
      )}

      <header className="app-header">
        <div className="header-left" onClick={() => setView('matrix')} style={{ cursor: 'pointer' }}>
          <div className="header-logo">⚡</div>
          <div>
            <h1>Eisenhower Matrix</h1>
            <p className="header-sub">AI-powered task prioritization</p>
          </div>
        </div>
        <div className="header-right">
          {totalCount > 0 && view === 'matrix' && (
            <div className="progress-chip">
              {completedCount}/{totalCount} done
            </div>
          )}
          {calendarReady ? (
            <div className="calendar-badge configured">
              📅 Calendar: Connected
            </div>
          ) : calendarStatus && !calendarStatus.configured ? (
            <div className="calendar-badge unconfigured" title="Add Google OAuth credentials to enable Calendar sync">
              📅 Calendar: Setup needed
            </div>
          ) : null}

          <button
            className={`btn ${view === 'flashcards' ? 'active' : ''}`}
            onClick={() => setView(view === 'flashcards' ? 'matrix' : 'flashcards')}
          >
            📇 Que-Que Cards
          </button>

          <button
            className={`btn ${showRoadmap ? 'btn-roadmap-active' : 'btn-roadmap'}`}
            onClick={() => setShowRoadmap(!showRoadmap)}
          >
            {showRoadmap ? '✕ Close Roadmap' : '🗺️ Roadmap'}
          </button>

          <button
            className="btn btn-primary"
            onClick={() => setShowForm(!showForm)}
          >
            {showForm ? '✕ Cancel' : '+ New Task'}
          </button>
        </div>
      </header>

      {error && (
        <div className="error-banner">
          <span>⚠️ {error}</span>
          <button onClick={() => setError(null)}>✕</button>
        </div>
      )}

      {showForm && (
        <div className="form-overlay" onClick={(e) => e.target === e.currentTarget && setShowForm(false)}>
          <div className="form-container">
            <TaskForm
              onSubmit={handleCreateTask}
              onCancel={() => setShowForm(false)}
            />
          </div>
        </div>
      )}

      {editingTask && (
        <div className="form-overlay" onClick={(e) => e.target === e.currentTarget && setEditingTask(null)}>
          <div className="form-container">
            <TaskForm
              initialData={editingTask}
              onSubmit={handleCreateTask}
              onCancel={() => setEditingTask(null)}
            />
          </div>
        </div>
      )}

      <div className="app-main">
        <div className="app-content">
          {view === 'matrix' ? (
            <Dashboard
              tasks={tasks}
              loading={loading}
              onMoveTask={handleMoveTask}
              onDeleteTask={handleDeleteTask}
              onToggleComplete={handleToggleComplete}
              onCalendarSync={calendarReady ? handleCalendarSync : null}
              onGenerateFlashcards={(t) => setFlashcardPromptTask(t)}
              onEditTask={(t) => setEditingTask(t)}
            />
          ) : (
            <FlashcardsPage
              onBack={() => setView('matrix')}
              onCustomGenClick={() => setFlashcardPromptTask({})}
            />
          )}
        </div>


        <RoadmapSidebar
          visible={showRoadmap}
          onClose={() => setShowRoadmap(false)}
          onAddToMatrix={handleRoadmapAddToMatrix}
        />
      </div>

      <footer className="app-footer">
        <span>Tasks auto-classified via Groq AI · Drag tasks between quadrants · Roadmaps from roadmap.sh</span>
      </footer>
    </div>
  );
}

export default App;
