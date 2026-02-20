import React, { useState } from 'react';

function TaskForm({ onSubmit, onCancel }) {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    deadline: '',
    estimated_time_hours: 1,
    user_priority: 'medium',
    is_graded: false,
    is_exam_related: false
  });

  const [errors, setErrors] = useState({});

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const validate = () => {
    const newErrors = {};
    
    if (!formData.title.trim()) {
      newErrors.title = 'Title is required';
    }
    
    if (!formData.deadline) {
      newErrors.deadline = 'Deadline is required';
    } else {
      const deadlineDate = new Date(formData.deadline);
      if (deadlineDate <= new Date()) {
        newErrors.deadline = 'Deadline must be in the future';
      }
    }
    
    if (formData.estimated_time_hours <= 0) {
      newErrors.estimated_time_hours = 'Estimated time must be positive';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (validate()) {
      onSubmit(formData);
    }
  };

  return (
    <form className="task-form" onSubmit={handleSubmit}>
      <h2>Create New Task</h2>
      
      <div className="form-group">
        <label htmlFor="title">Title *</label>
        <input
          type="text"
          id="title"
          name="title"
          value={formData.title}
          onChange={handleChange}
          placeholder="Enter task title"
        />
        {errors.title && <span className="error">{errors.title}</span>}
      </div>

      <div className="form-group">
        <label htmlFor="description">Description</label>
        <textarea
          id="description"
          name="description"
          value={formData.description}
          onChange={handleChange}
          placeholder="Enter task description"
          rows="3"
        />
      </div>

      <div className="form-row">
        <div className="form-group">
          <label htmlFor="deadline">Deadline *</label>
          <input
            type="datetime-local"
            id="deadline"
            name="deadline"
            value={formData.deadline}
            onChange={handleChange}
          />
          {errors.deadline && <span className="error">{errors.deadline}</span>}
        </div>

        <div className="form-group">
          <label htmlFor="estimated_time_hours">Estimated Hours *</label>
          <input
            type="number"
            id="estimated_time_hours"
            name="estimated_time_hours"
            value={formData.estimated_time_hours}
            onChange={handleChange}
            min="0.5"
            step="0.5"
          />
          {errors.estimated_time_hours && <span className="error">{errors.estimated_time_hours}</span>}
        </div>
      </div>

      <div className="form-group">
        <label htmlFor="user_priority">Priority</label>
        <select
          id="user_priority"
          name="user_priority"
          value={formData.user_priority}
          onChange={handleChange}
        >
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
        </select>
      </div>

      <div className="form-checkboxes">
        <label>
          <input
            type="checkbox"
            name="is_graded"
            checked={formData.is_graded}
            onChange={handleChange}
          />
          Graded Assignment
        </label>

        <label>
          <input
            type="checkbox"
            name="is_exam_related"
            checked={formData.is_exam_related}
            onChange={handleChange}
          />
          Exam Related
        </label>
      </div>

      <div className="form-actions">
        <button type="submit" className="btn btn-primary">Create Task</button>
        <button type="button" className="btn btn-secondary" onClick={onCancel}>Cancel</button>
      </div>
    </form>
  );
}

export default TaskForm;
