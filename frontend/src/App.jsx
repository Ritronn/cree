import { useState, useEffect } from 'react';
import './App.css';
import Dashboard from './components/Dashboard';
import TaskForm from './components/TaskForm';
import apiClient from './api/client';

function App() {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showForm, setShowForm] = useState(false);

  // Fetch tasks from API
  const fetchTasks = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiClient.get('/api/tasks/');
      // Ensure we always set an array
      const data = Array.isArray(response.data) ? response.data : [];
      setTasks(data);
    } catch (err) {
      console.error('Error fetching tasks:', err);
      setError(err.response?.data?.message || 'Failed to load tasks');
      setTasks([]); // Set empty array on error
    } finally {
      setLoading(false);
    }
  };

  // Create new task
  const handleCreateTask = async (formData) => {
    try {
      const response = await apiClient.post('/api/tasks/', formData);
      setTasks(prev => [...prev, response.data]);
      setShowForm(false);
      setError(null);
    } catch (err) {
      console.error('Error creating task:', err);
      setError(err.response?.data?.message || 'Failed to create task');
    }
  };

  // Load tasks on mount
  useEffect(() => {
    fetchTasks();
  }, []);

  return (
    <div className="App">
      <header className="app-header">
        <h1>Eisenhower Matrix Task Manager</h1>
        <button 
          className="btn btn-primary"
          onClick={() => setShowForm(!showForm)}
        >
          {showForm ? 'Cancel' : '+ New Task'}
        </button>
      </header>

      {error && (
        <div className="error-banner">
          {error}
          <button onClick={() => setError(null)}>×</button>
        </div>
      )}

      {showForm && (
        <div className="form-container">
          <TaskForm 
            onSubmit={handleCreateTask}
            onCancel={() => setShowForm(false)}
          />
        </div>
      )}

      <Dashboard tasks={tasks} loading={loading} />
    </div>
  );
}

export default App;
