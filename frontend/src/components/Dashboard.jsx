import React from 'react';
import TaskCard from './TaskCard';

function Dashboard({ tasks, loading }) {
  // Ensure tasks is always an array
  const taskList = Array.isArray(tasks) ? tasks : [];
  
  // Group tasks by quadrant
  const groupedTasks = {
    urgent_important: taskList.filter(t => t.quadrant === 'urgent_important'),
    important_not_urgent: taskList.filter(t => t.quadrant === 'important_not_urgent'),
    urgent_not_important: taskList.filter(t => t.quadrant === 'urgent_not_important'),
    neither: taskList.filter(t => t.quadrant === 'neither')
  };

  const quadrants = [
    {
      key: 'urgent_important',
      title: 'Urgent & Important',
      subtitle: 'Do First',
      color: 'red'
    },
    {
      key: 'important_not_urgent',
      title: 'Important but Not Urgent',
      subtitle: 'Schedule',
      color: 'yellow'
    },
    {
      key: 'urgent_not_important',
      title: 'Urgent but Not Important',
      subtitle: 'Delegate',
      color: 'blue'
    },
    {
      key: 'neither',
      title: 'Neither Urgent nor Important',
      subtitle: 'Eliminate',
      color: 'gray'
    }
  ];

  if (loading) {
    return <div className="loading">Loading tasks...</div>;
  }

  return (
    <div className="dashboard">
      {quadrants.map(quadrant => (
        <div key={quadrant.key} className={`quadrant quadrant-${quadrant.color}`}>
          <div className="quadrant-header">
            <h2>{quadrant.title}</h2>
            <p className="quadrant-subtitle">{quadrant.subtitle}</p>
            <span className="task-count">{groupedTasks[quadrant.key].length}</span>
          </div>
          <div className="quadrant-tasks">
            {groupedTasks[quadrant.key].length === 0 ? (
              <p className="no-tasks">No tasks</p>
            ) : (
              groupedTasks[quadrant.key].map(task => (
                <TaskCard key={task.id} task={task} />
              ))
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

export default Dashboard;
