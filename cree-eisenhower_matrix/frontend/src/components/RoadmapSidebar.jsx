import React, { useState, useEffect } from 'react';
import apiClient from '../api/client';

const POPULAR_PRESETS = [
    { from: 'Python Basics', to: 'Machine Learning', emoji: '🤖' },
    { from: 'HTML/CSS', to: 'React Developer', emoji: '⚛️' },
    { from: 'Programming Basics', to: 'Full Stack Developer', emoji: '🚀' },
    { from: 'JavaScript', to: 'Node.js Backend', emoji: '🟢' },
    { from: 'Basics', to: 'DevOps Engineer', emoji: '🔧' },
    { from: 'Data Structures', to: 'System Design', emoji: '📐' },
];

function RoadmapSidebar({ onAddToMatrix, visible, onClose }) {
    const [mode, setMode] = useState('browse'); // 'browse' | 'custom' | 'result'
    const [roadmaps, setRoadmaps] = useState([]);
    const [selectedRoadmap, setSelectedRoadmap] = useState(null);
    const [roadmapData, setRoadmapData] = useState(null);
    const [fromTopic, setFromTopic] = useState('');
    const [toTopic, setToTopic] = useState('');
    const [customRoadmap, setCustomRoadmap] = useState(null);
    const [loading, setLoading] = useState(false);
    const [loadingRoadmaps, setLoadingRoadmaps] = useState(false);
    const [searchQuery, setSearchQuery] = useState('');

    // Fetch available roadmaps on mount
    useEffect(() => {
        if (visible) {
            fetchRoadmaps();
        }
    }, [visible]);

    const fetchRoadmaps = async () => {
        setLoadingRoadmaps(true);
        try {
            const res = await apiClient.get('/api/roadmap/list/');
            setRoadmaps(res.data.roadmaps || []);
        } catch {
            setRoadmaps([]);
        } finally {
            setLoadingRoadmaps(false);
        }
    };

    const fetchRoadmapData = async (slug) => {
        setLoading(true);
        try {
            const res = await apiClient.get(`/api/roadmap/data/${slug}/`);
            setRoadmapData(res.data);
            setMode('browse');
        } catch (err) {
            console.error('Failed to fetch roadmap data:', err);
            setRoadmapData(null);
        } finally {
            setLoading(false);
        }
    };

    const handleSelectRoadmap = async (roadmap) => {
        setSelectedRoadmap(roadmap);
        await fetchRoadmapData(roadmap.slug);
    };

    const handleGenerateRoadmap = async (from, to) => {
        setLoading(true);
        setFromTopic(from);
        setToTopic(to);
        try {
            const res = await apiClient.post('/api/roadmap/generate/', {
                from_topic: from,
                to_topic: to,
            });
            setCustomRoadmap(res.data);
            setMode('result');
        } catch {
            setCustomRoadmap(null);
        } finally {
            setLoading(false);
        }
    };

    const handleAddTopicsToMatrix = async (topics) => {
        try {
            const res = await apiClient.post('/api/roadmap/to-tasks/', { topics });
            if (onAddToMatrix) onAddToMatrix(res.data.created);
        } catch (err) {
            console.error('Failed to add topics to matrix:', err);
        }
    };

    const filteredRoadmaps = roadmaps.filter(r =>
        r.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        r.slug.toLowerCase().includes(searchQuery.toLowerCase())
    );

    if (!visible) return null;

    return (
        <div className="roadmap-sidebar">
            <div className="roadmap-sidebar-header">
                <div className="roadmap-sidebar-title">
                    <span className="roadmap-icon">🗺️</span>
                    <div>
                        <h2>Learning Roadmap</h2>
                        <p className="roadmap-subtitle">Powered by roadmap.sh</p>
                    </div>
                </div>
                <button className="roadmap-close-btn" onClick={onClose}>✕</button>
            </div>

            {/* Mode Tabs */}
            <div className="roadmap-tabs">
                <button
                    className={`roadmap-tab ${mode === 'browse' ? 'active' : ''}`}
                    onClick={() => setMode('browse')}
                >
                    📚 Browse
                </button>
                <button
                    className={`roadmap-tab ${mode === 'custom' ? 'active' : ''}`}
                    onClick={() => setMode('custom')}
                >
                    ✨ Custom Path
                </button>
                {customRoadmap && (
                    <button
                        className={`roadmap-tab ${mode === 'result' ? 'active' : ''}`}
                        onClick={() => setMode('result')}
                    >
                        📋 Result
                    </button>
                )}
            </div>

            <div className="roadmap-content">
                {/* Browse Mode: Show native roadmap nodes */}
                {mode === 'browse' && (
                    <div className="roadmap-browse">
                        {(!selectedRoadmap || !roadmapData) && (
                            <div className="roadmap-search">
                                <input
                                    type="text"
                                    placeholder="Search roadmaps..."
                                    value={searchQuery}
                                    onChange={(e) => setSearchQuery(e.target.value)}
                                    className="roadmap-search-input"
                                />
                            </div>
                        )}

                        {selectedRoadmap && roadmapData ? (
                            <div className="roadmap-native-view">
                                <div className="roadmap-iframe-header">
                                    <button
                                        className="roadmap-back-btn"
                                        onClick={() => { setSelectedRoadmap(null); setRoadmapData(null); }}
                                    >
                                        ← Back to list
                                    </button>
                                    <span className="roadmap-iframe-title">{selectedRoadmap.name}</span>
                                </div>
                                <div className="roadmap-nodes-list">
                                    {roadmapData.nodes && roadmapData.nodes
                                        .filter(node => {
                                            if (!node.data || !node.data.label) return false;
                                            const label = node.data.label.toLowerCase();
                                            const type = (node.type || '').toLowerCase();

                                            // Filter structural nodes
                                            if (type === 'vertical' || type === 'horizontal' || type === 'group' || type === 'section') return false;

                                            // Aggressive filtering of non-essential metadata and subjective nodes
                                            const ignorePhrases = [
                                                'node', 'roadmap.sh', 'detailed version', 'relevant tracks',
                                                'related roadmaps', 'visit ', 'learn the', 'keep learning',
                                                'how does it work', 'what is it', 'overview', 'resources',
                                                'conclusion', 'good to know', 'pre-requisites',
                                                'click here', 'read more', 'continue'
                                            ];
                                            if (ignorePhrases.some(phrase => label.includes(phrase))) return false;

                                            // Filter purely numeric labels (sometimes structural indices)
                                            if (/^\d+$/.test(label.trim())) return false;

                                            // Filter extremely short or extremely long labels (likely not topics)
                                            if (label.length < 2 || label.length > 50) return false;

                                            return true;
                                        })
                                        .map(node => (
                                            <div key={node.id} className="roadmap-node-item">
                                                <div className="node-content">
                                                    <div className="node-label">
                                                        {node.data.label}
                                                    </div>
                                                    {node.data.description && (
                                                        <div className="node-description">{node.data.description}</div>
                                                    )}
                                                </div>
                                                <button
                                                    className="node-add-btn"
                                                    onClick={() => handleAddTopicsToMatrix([{
                                                        name: node.data.label,
                                                        description: node.data.description || `Learning path for ${node.data.label}`
                                                    }])}
                                                    title="Add to Matrix"
                                                >
                                                    +
                                                </button>
                                            </div>
                                        ))}
                                </div>
                            </div>
                        ) : (
                            <div className="roadmap-list">
                                {loadingRoadmaps ? (
                                    <div className="roadmap-loading">
                                        <div className="loading-spinner" />
                                        <p>Loading roadmaps...</p>
                                    </div>
                                ) : (
                                    filteredRoadmaps.map(roadmap => (
                                        <button
                                            key={roadmap.slug}
                                            className="roadmap-list-item"
                                            onClick={() => handleSelectRoadmap(roadmap)}
                                        >
                                            <span className="roadmap-item-name">{roadmap.name}</span>
                                            <span className="roadmap-item-arrow">→</span>
                                        </button>
                                    ))
                                )}
                                {!loadingRoadmaps && filteredRoadmaps.length === 0 && (
                                    <p className="roadmap-empty">No roadmaps found matching "{searchQuery}"</p>
                                )}
                            </div>
                        )}
                    </div>
                )}

                {/* Custom Path Mode */}
                {mode === 'custom' && (
                    <div className="roadmap-custom">
                        <div className="roadmap-custom-form">
                            <h3>🎯 Create Your Learning Path</h3>
                            <p className="roadmap-custom-desc">
                                Enter your starting point and goal — AI will create a
                                personalized roadmap for you.
                            </p>

                            <div className="roadmap-input-group">
                                <label>From (starting knowledge)</label>
                                <input
                                    type="text"
                                    value={fromTopic}
                                    onChange={(e) => setFromTopic(e.target.value)}
                                    placeholder="e.g., Python Basics"
                                    className="roadmap-input"
                                />
                            </div>

                            <div className="roadmap-path-arrow">↓</div>

                            <div className="roadmap-input-group">
                                <label>To (goal)</label>
                                <input
                                    type="text"
                                    value={toTopic}
                                    onChange={(e) => setToTopic(e.target.value)}
                                    placeholder="e.g., Machine Learning"
                                    className="roadmap-input"
                                />
                            </div>

                            <button
                                className="btn btn-primary roadmap-generate-btn"
                                onClick={() => handleGenerateRoadmap(fromTopic, toTopic)}
                                disabled={loading || !fromTopic.trim() || !toTopic.trim()}
                            >
                                {loading ? '⏳ Generating...' : '🚀 Generate Roadmap'}
                            </button>
                        </div>

                        <div className="roadmap-presets">
                            <h4>Quick Presets</h4>
                            <div className="roadmap-preset-grid">
                                {POPULAR_PRESETS.map((preset, i) => (
                                    <button
                                        key={i}
                                        className="roadmap-preset-btn"
                                        onClick={() => {
                                            setFromTopic(preset.from);
                                            setToTopic(preset.to);
                                            handleGenerateRoadmap(preset.from, preset.to);
                                        }}
                                        disabled={loading}
                                    >
                                        <span className="preset-emoji">{preset.emoji}</span>
                                        <span className="preset-text">
                                            {preset.from} → {preset.to}
                                        </span>
                                    </button>
                                ))}
                            </div>
                        </div>
                    </div>
                )}

                {/* Result Mode */}
                {mode === 'result' && customRoadmap && (
                    <div className="roadmap-result">
                        <div className="roadmap-result-header">
                            <h3>{customRoadmap.title}</h3>
                            <p className="roadmap-result-desc">{customRoadmap.description}</p>
                            {customRoadmap.total_estimated_hours && (
                                <div className="roadmap-total-hours">
                                    ⏱ Total: ~{customRoadmap.total_estimated_hours}h
                                </div>
                            )}
                        </div>

                        <div className="roadmap-phases">
                            {(customRoadmap.phases || []).map((phase, pi) => (
                                <div key={pi} className="roadmap-phase">
                                    <div className="phase-header">
                                        <span className="phase-number">{phase.phase_number || pi + 1}</span>
                                        <div className="phase-info">
                                            <h4>{phase.title}</h4>
                                            <p>{phase.description}</p>
                                        </div>
                                    </div>

                                    <div className="phase-topics">
                                        {(phase.topics || []).map((topic, ti) => (
                                            <div key={ti} className="phase-topic">
                                                <div className="topic-info">
                                                    <span className="topic-name">{topic.name}</span>
                                                    <span className="topic-hours">{topic.estimated_hours}h</span>
                                                </div>
                                                <p className="topic-desc">{topic.description}</p>
                                                {topic.roadmap_url && topic.roadmap_url !== 'null' && (
                                                    <a
                                                        href={topic.roadmap_url}
                                                        target="_blank"
                                                        rel="noopener noreferrer"
                                                        className="topic-link"
                                                    >
                                                        📚 View on roadmap.sh ↗
                                                    </a>
                                                )}
                                            </div>
                                        ))}
                                    </div>

                                    <button
                                        className="phase-add-btn"
                                        onClick={() => handleAddTopicsToMatrix(phase.topics)}
                                    >
                                        ➕ Add Phase to Matrix
                                    </button>

                                    {pi < (customRoadmap.phases || []).length - 1 && (
                                        <div className="phase-connector">
                                            <div className="connector-line" />
                                            <div className="connector-dot" />
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>

                        <button
                            className="btn btn-primary roadmap-add-all-btn"
                            onClick={() => {
                                const allTopics = (customRoadmap.phases || [])
                                    .flatMap(p => p.topics || []);
                                handleAddTopicsToMatrix(allTopics);
                            }}
                        >
                            ➕ Add All Topics to Matrix ({
                                (customRoadmap.phases || []).reduce(
                                    (sum, p) => sum + (p.topics || []).length, 0
                                )
                            } tasks)
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
}

export default RoadmapSidebar;
