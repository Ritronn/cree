import React, { useState, useRef } from 'react';
import TaskCard from './TaskCard';

const QUADRANTS = [
  {
    key: 'urgent_important',
    title: 'Urgent & Important',
    subtitle: 'Do First',
    emoji: '🔴',
    color: 'red',
    tip: 'Handle these immediately — crises and deadlines',
  },
  {
    key: 'important_not_urgent',
    title: 'Important, Not Urgent',
    subtitle: 'Schedule',
    emoji: '🟡',
    color: 'yellow',
    tip: 'Plan time for these — growth and strategy',
  },
  {
    key: 'urgent_not_important',
    title: 'Urgent, Not Important',
    subtitle: 'Delegate',
    emoji: '🔵',
    color: 'blue',
    tip: 'Minimize or delegate — interruptions',
  },
  {
    key: 'neither',
    title: 'Not Urgent, Not Important',
    subtitle: 'Eliminate',
    emoji: '⚫',
    color: 'gray',
    tip: 'Cut these tasks — time wasters',
  },
];

function Dashboard({ tasks, loading, onMoveTask, onDeleteTask, onToggleComplete, onCalendarSync, onGenerateFlashcards, onEditTask }) {
  const [dragOverQuadrant, setDragOverQuadrant] = useState(null);
  const [draggingTask, setDraggingTask] = useState(null);
  const dragTaskData = useRef(null);

  const taskList = Array.isArray(tasks) ? tasks : [];
  const grouped = {};
  QUADRANTS.forEach(q => {
    grouped[q.key] = taskList.filter(t => t.quadrant === q.key);
  });

  const handleDragStart = (task) => {
    setDraggingTask(task.id);
    dragTaskData.current = task;
  };

  const handleDragEnd = () => {
    setDraggingTask(null);
    setDragOverQuadrant(null);
    dragTaskData.current = null;
  };

  const handleDragOver = (e, quadrantKey) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    setDragOverQuadrant(quadrantKey);
  };

  const handleDrop = (e, quadrantKey) => {
    e.preventDefault();
    const task = dragTaskData.current;
    if (task && task.quadrant !== quadrantKey) {
      onMoveTask(task.id, quadrantKey);
    }
    setDraggingTask(null);
    setDragOverQuadrant(null);
    dragTaskData.current = null;
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner" />
        <p>Loading tasks...</p>
      </div>
    );
  }

  return (
    <div className="dashboard">
      {QUADRANTS.map(quadrant => {
        const qTasks = grouped[quadrant.key] || [];
        const isOver = dragOverQuadrant === quadrant.key;
        const isDraggingToThis = isOver && draggingTask;

        return (
          <div
            key={quadrant.key}
            className={`quadrant quadrant-${quadrant.color} ${isDraggingToThis ? 'drop-zone-active' : ''}`}
            onDragOver={(e) => handleDragOver(e, quadrant.key)}
            onDragLeave={() => setDragOverQuadrant(null)}
            onDrop={(e) => handleDrop(e, quadrant.key)}
          >
            <div className="quadrant-header">
              <div className="quadrant-title-row">
                <span className="quadrant-emoji">{quadrant.emoji}</span>
                <div className="quadrant-text">
                  <h2>{quadrant.title}</h2>
                  <p className="quadrant-subtitle">{quadrant.subtitle}</p>
                </div>
                <span className="task-count">{qTasks.length}</span>
              </div>
              <p className="quadrant-tip">{quadrant.tip}</p>
            </div>

            <div className={`quadrant-tasks ${isDraggingToThis ? 'drop-zone-highlight' : ''}`}>
              {isDraggingToThis && (
                <div className="drop-indicator">
                  Drop here to move to "{quadrant.title}"
                </div>
              )}
              {qTasks.length === 0 && !isDraggingToThis ? (
                <p className="no-tasks">No tasks · drag one here</p>
              ) : (
                qTasks.map(task => (
                  <TaskCard
                    key={task.id}
                    task={task}
                    isDragging={draggingTask === task.id}
                    onDragStart={() => handleDragStart(task)}
                    onDragEnd={handleDragEnd}
                    onDelete={() => onDeleteTask(task.id)}
                    onToggleComplete={() => onToggleComplete(task.id, task.is_completed)}
                    onCalendarSync={onCalendarSync ? () => onCalendarSync(task.id) : null}
                    onGenerateFlashcards={onGenerateFlashcards}
                    onEditTask={onEditTask}
                  />
                ))
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}

export default Dashboard;
