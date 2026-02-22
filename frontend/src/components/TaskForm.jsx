import React, { useState, useEffect } from 'react';

function TaskForm({ onSubmit, onCancel, initialData }) {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    deadline: '',
    estimated_time_hours: 1,
  });
  const [errors, setErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (initialData) {
      // Format deadline for datetime-local input (YYYY-MM-DDThh:mm)
      let formattedDeadline = '';
      if (initialData.deadline) {
        const d = new Date(initialData.deadline);
        // Account for timezone offset to display correctly in input
        const offset = d.getTimezoneOffset() * 60000;
        formattedDeadline = new Date(d.getTime() - offset).toISOString().slice(0, 16);
      }

      setFormData({
        title: initialData.title || '',
        description: initialData.description || '',
        deadline: formattedDeadline,
        estimated_time_hours: initialData.estimated_time_hours || 1,
      });
    }
  }, [initialData]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
    // Clear error on change
    if (errors[name]) setErrors(prev => ({ ...prev, [name]: null }));
  };

  const validate = () => {
    const newErrors = {};
    if (!formData.title.trim()) {
      newErrors.title = 'Title is required';
    }
    if (!formData.deadline) {
      newErrors.deadline = 'Deadline is required';
    } else if (!initialData && new Date(formData.deadline) <= new Date()) {
      // Only enforce future deadline for *new* tasks
      newErrors.deadline = 'Deadline must be in the future';
    }
    if (!formData.estimated_time_hours || Number(formData.estimated_time_hours) <= 0) {
      newErrors.estimated_time_hours = 'Must be greater than 0';
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;
    setSubmitting(true);
    try {
      await onSubmit(formData, initialData?.id);
    } finally {
      setSubmitting(false);
    }
  };

  // Minimum datetime = now (only strictly enforced in UI for new tasks, though HTML5 min attribute is strict)
  const minDatetime = initialData ? undefined : new Date(Date.now() + 60000).toISOString().slice(0, 16);

  return (
    <form className="task-form" onSubmit={handleSubmit}>
      <div className="form-header">
        <h2>{initialData ? '✏️ Edit Task' : '✨ Create New Task'}</h2>
        <p className="form-subtitle">
          {initialData ? 'Update details. AI will re-classify if needed.' : 'AI will auto-classify into the Eisenhower Matrix'}
        </p>
      </div>

      <div className="form-group">
        <label htmlFor="title">Task Title *</label>
        <input
          type="text"
          id="title"
          name="title"
          value={formData.title}
          onChange={handleChange}
          placeholder="e.g. Prepare project presentation"
          autoFocus
          className={errors.title ? 'input-error' : ''}
        />
        {errors.title && <span className="error">{errors.title}</span>}
      </div>

      <div className="form-group">
        <label htmlFor="description">Description <span className="optional">(optional)</span></label>
        <textarea
          id="description"
          name="description"
          value={formData.description}
          onChange={handleChange}
          placeholder="Add details to help the AI classify this task better..."
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
            min={minDatetime}
            className={errors.deadline ? 'input-error' : ''}
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
            max="100"
            step="0.5"
            className={errors.estimated_time_hours ? 'input-error' : ''}
          />
          {errors.estimated_time_hours && <span className="error">{errors.estimated_time_hours}</span>}
        </div>
      </div>

      <div className="ai-notice">
        <span className="ai-icon">🤖</span>
        <span>The AI will automatically determine urgency, importance, and assign the right quadrant based on your deadline and task description.</span>
      </div>

      <div className="form-actions">
        <button type="submit" className="btn btn-primary" disabled={submitting}>
          {submitting ? '⏳ Classifying...' : (initialData ? 'Update & Re-Classify' : '✨ Create & Classify')}
        </button>
        <button type="button" className="btn btn-secondary" onClick={onCancel}>
          Cancel
        </button>
      </div>
    </form>
  );
}

export default TaskForm;

