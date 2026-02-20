import React from 'react';

function TaskCard({ task }) {
  const formatDeadline = (deadline) => {
    const date = new Date(deadline);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="task-card">
      <h3>{task.title}</h3>
      {task.description && <p className="task-description">{task.description}</p>}
      <div className="task-meta">
        <div className="task-deadline">
          <strong>Due:</strong> {formatDeadline(task.deadline)}
        </div>
        <div className="task-time">
          <strong>Est:</strong> {task.estimated_time_hours}h
        </div>
      </div>
      <div className="task-scores">
        <span className="score urgency">U: {Number(task.urgency_score || 0).toFixed(2)}</span>
        <span className="score importance">I: {Number(task.importance_score || 0).toFixed(2)}</span>
      </div>
      {task.is_manually_categorized && (
        <div className="manual-badge">Manual</div>
      )}
    </div>
  );
}

export default TaskCard;
