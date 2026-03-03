import React from 'react';

function TaskCard({ task, isDragging, onDragStart, onDragEnd, onEditTask, onDelete, onToggleComplete, onCalendarSync, onGenerateFlashcards }) {
  const formatDeadline = (deadline) => {
    const date = new Date(deadline);
    const now = new Date();
    const hoursLeft = (date - now) / (1000 * 60 * 60);

    const formatted = date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });

    let urgencyClass = 'deadline-normal';
    let urgencyLabel = '';
    if (hoursLeft < 0) { urgencyClass = 'deadline-overdue'; urgencyLabel = '⚠️ Overdue'; }
    else if (hoursLeft <= 24) { urgencyClass = 'deadline-critical'; urgencyLabel = '🔥 Due soon'; }
    else if (hoursLeft <= 72) { urgencyClass = 'deadline-soon'; urgencyLabel = '⏰'; }

    return { formatted, urgencyClass, urgencyLabel };
  };

  const { formatted, urgencyClass, urgencyLabel } = formatDeadline(task.deadline);

  const urgencyPct = Math.round(Number(task.urgency_score || 0) * 100);
  const importancePct = Math.round(Number(task.importance_score || 0) * 100);

  return (
    <div
      className={`task-card ${isDragging ? 'task-card-dragging' : ''} ${task.is_completed ? 'task-completed' : ''}`}
      draggable
      onDragStart={onDragStart}
      onDragEnd={onDragEnd}
    >
      <div className="task-card-drag-handle" title="Drag to move">⠿</div>

      {task.is_manually_categorized && (
        <div className="manual-badge">Manual</div>
      )}

      <div className="task-card-body">
        <h3 className="task-title">{task.title}</h3>
        {task.description && (
          <p className="task-description">{task.description}</p>
        )}
      </div>

      <div className={`task-deadline ${urgencyClass}`}>
        <span>📅 {formatted}</span>
        {urgencyLabel && <span className="urgency-label">{urgencyLabel}</span>}
      </div>

      <div className="task-metrics">
        <div className="metric">
          <span className="metric-label">Urgency</span>
          <div className="metric-bar">
            <div className="metric-fill urgency-fill" style={{ width: `${urgencyPct}%` }} />
          </div>
          <span className="metric-value">{urgencyPct}%</span>
        </div>
        <div className="metric">
          <span className="metric-label">Importance</span>
          <div className="metric-bar">
            <div className="metric-fill importance-fill" style={{ width: `${importancePct}%` }} />
          </div>
          <span className="metric-value">{importancePct}%</span>
        </div>
      </div>

      <div className="task-meta-row">
        <span className="task-time">⏱ {task.estimated_time_hours}h</span>
      </div>

      <div className="task-actions">
        <button
          className={`action-btn ${task.is_completed ? 'btn-undo' : 'btn-complete'}`}
          onClick={onToggleComplete}
          title={task.is_completed ? 'Mark incomplete' : 'Mark complete'}
        >
          {task.is_completed ? '↩ Undo' : '✓ Done'}
        </button>

        <button
          className="action-btn btn-secondary"
          onClick={() => onEditTask(task)}
          title="Edit Task"
        >
          ✏️ Edit
        </button>

        <button
          className="btn-flashcard"
          onClick={() => onGenerateFlashcards(task)}
          title="Generate Que-Que Cards"
        >
          📇
        </button>

        {onCalendarSync && !task.google_calendar_event_id && (
          <button
            className="action-btn btn-calendar"
            onClick={onCalendarSync}
            title="Sync to Google Calendar"
          >
            📅
          </button>
        )}

        {task.google_calendar_event_id && (
          <span className="calendar-synced" title="Synced to Google Calendar">📅✓</span>
        )}

        <button
          className="action-btn btn-delete"
          onClick={() => onDelete(task.id)}
          title="Delete task"
        >
          🗑
        </button>
      </div>
    </div>
  );
}

export default TaskCard;
