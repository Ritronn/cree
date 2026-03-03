import React, { useState } from 'react';

function GenCardsModal({ task, onClose, onSubmit }) {
    const [topic, setTopic] = useState(task.title || '');
    const [description, setDescription] = useState(task.description || '');
    const [scope, setScope] = useState('specific_topics');
    const isCustomDeck = !task.id; // If there's no task.id, it's a generic request

    const handleSubmit = (e) => {
        e.preventDefault();
        onSubmit({ ...task, title: topic }, description, scope);
    };

    return (
        <div className="form-overlay" onClick={(e) => e.target === e.currentTarget && onClose()}>
            <div className="form-container">
                <div className="form-header">
                    <h2>📇 Generate {isCustomDeck ? 'Custom' : ''} Que-Que Cards</h2>
                    <button type="button" className="close-btn" onClick={onClose} style={{ background: 'transparent', border: 'none', color: 'white', fontSize: '1.2rem', cursor: 'pointer', float: 'right', marginTop: '-30px' }}>✕</button>
                    {isCustomDeck && <p className="form-subtitle">Generate flashcards for any topic outside of your Matrix tasks.</p>}
                </div>

                <form onSubmit={handleSubmit} className="task-form">
                    <div className="form-group">
                        <label>Topic {isCustomDeck && '*'}</label>
                        <input
                            type="text"
                            value={topic}
                            onChange={(e) => setTopic(e.target.value)}
                            disabled={!isCustomDeck}
                            className={`form-input ${!isCustomDeck ? 'disabled' : ''}`}
                            placeholder="e.g., Python Basics, Core Networking..."
                            required={isCustomDeck}
                        />
                    </div>

                    <div className="form-group">
                        <label>Description Context (Optional)</label>
                        <textarea
                            value={description}
                            onChange={(e) => setDescription(e.target.value)}
                            placeholder="Add more details so the AI knows exactly what to cover..."
                            className="form-input"
                            rows="2"
                        />
                    </div>

                    <div className="form-group">
                        <label>Scope (How much to generate?)</label>
                        <select
                            value={scope}
                            onChange={(e) => setScope(e.target.value)}
                            className="form-select"
                        >
                            <option value="overview">Topic Overview (~3 cards)</option>
                            <option value="specific_topics">Specific Key Concepts (~5 cards)</option>
                            <option value="full_syllabus">Full Syllabus Deep-Dive (~15 cards)</option>
                        </select>
                    </div>

                    <div className="form-actions">
                        <button type="button" className="btn btn-secondary" onClick={onClose}>
                            Cancel
                        </button>
                        <button type="submit" className="btn btn-primary">
                            Generate Cards
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}

export default GenCardsModal;
