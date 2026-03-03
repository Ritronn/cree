import React, { useState, useEffect } from 'react';
import apiClient from '../api/client';
import FlashcardCard from '../components/FlashcardCard';

function FlashcardsPage({ onBack, onCustomGenClick }) {
    const [flashcards, setFlashcards] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [activeTopic, setActiveTopic] = useState(null);
    const [currentCardIndex, setCurrentCardIndex] = useState(0);

    useEffect(() => {
        fetchFlashcards();
    }, []);

    const fetchFlashcards = async () => {
        setLoading(true);
        try {
            const res = await apiClient.get('/api/flashcards/');
            // Handle DRF pagination object { count, next, previous, results: [...] }
            const cardsData = Array.isArray(res.data) ? res.data :
                (res.data && Array.isArray(res.data.results)) ? res.data.results : [];
            setFlashcards(cardsData);
            setError(null);

            // If active topic was deleted or emptied, exit sequence view
            if (activeTopic && !cardsData.some(c => c.topic === activeTopic)) {
                setActiveTopic(null);
            }
        } catch (err) {
            console.error('Failed to fetch flashcards:', err);
            setError('Failed to load flashcards. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const handleGenerateCore = async () => {
        setLoading(true);
        try {
            await apiClient.post('/api/flashcards/generate/', {
                topic: 'Core Computer Science',
                description: 'Data Structures, Algorithms, Operating Systems, Computer Networks',
                scope: 'overview'
            });
            await fetchFlashcards();
        } catch (err) {
            console.error('Failed to generate core flashcards:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleDeleteTopic = async (topic, e) => {
        e.stopPropagation();
        if (!window.confirm(`Are you sure you want to delete all cards for "${topic}"?`)) return;

        try {
            await apiClient.delete(`/api/flashcards/delete_topic/?topic=${encodeURIComponent(topic)}`);
            await fetchFlashcards();
            if (activeTopic === topic) setActiveTopic(null);
        } catch (err) {
            console.error('Failed to delete topic:', err);
        }
    };

    const groupedCards = flashcards.reduce((acc, card) => {
        const topic = card.topic || 'General';
        if (!acc[topic]) acc[topic] = [];
        acc[topic].push(card);
        return acc;
    }, {});

    const activeCards = activeTopic ? groupedCards[activeTopic] || [] : [];
    const currentCard = activeCards[currentCardIndex];

    const handleNextCard = () => {
        if (currentCardIndex < activeCards.length - 1) {
            setCurrentCardIndex(prev => prev + 1);
        } else {
            // Reached end, go back to overview or loop? Let's loop back to 0 for continuous revision.
            setCurrentCardIndex(0);
        }
    };

    return (
        <div className="flashcards-page">
            <header className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
                <div>
                    <button
                        onClick={() => activeTopic ? setActiveTopic(null) : onBack()}
                        className="roadmap-back-btn"
                        style={{ marginBottom: '0.5rem' }}
                    >
                        {activeTopic ? '← Back to Topics' : '← Back to Matrix'}
                    </button>
                    <h1>{activeTopic ? activeTopic : 'Que-Que Cards'}</h1>
                    <p style={{ color: 'var(--text-secondary)' }}>
                        {activeTopic ? 'Click the card to reveal answer and advance.' : 'Last-minute revision cards grouped by topic.'}
                    </p>
                </div>
                {!activeTopic && (
                    <button
                        className="btn btn-primary"
                        onClick={onCustomGenClick}
                        disabled={loading}
                    >
                        ✨ Create Custom Que-Que Deck
                    </button>
                )}
            </header>

            {loading && flashcards.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '5rem' }}>
                    <div className="loading-spinner"></div>
                    <p>Fetching your revision cards...</p>
                </div>
            ) : error ? (
                <div style={{ textAlign: 'center', color: 'var(--urgent-color)', padding: '5rem' }}>
                    <p>{error}</p>
                    <button className="btn" onClick={fetchFlashcards}>Retry</button>
                </div>
            ) : flashcards.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '5rem', background: 'rgba(255,255,255,0.02)', borderRadius: '20px' }}>
                    <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>📇</div>
                    <h3>No Flashcards Yet</h3>
                    <p style={{ color: 'var(--text-secondary)', maxWidth: '400px', margin: '0 auto 1.5rem' }}>
                        Generate flashcards for your tasks to see them here.
                    </p>
                    <button className="btn btn-primary" onClick={onCustomGenClick}>
                        ✨ Create Custom Que-Que Deck
                    </button>
                </div>
            ) : activeTopic && currentCard ? (
                <div className="flashcard-sequence-view" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                    <div className="sequence-progress" style={{ marginBottom: '2rem', fontSize: '1.2rem', color: 'var(--text-secondary)' }}>
                        Card {currentCardIndex + 1} of {activeCards.length}
                    </div>

                    <div key={currentCard.id} className="floating-animation">
                        {/* We use pointer-events trick or just wrap it. 
                            If FlashcardCard handles its own flip, clicking it flips it. 
                            But user requested: "if i click it then a sequence with numbering will float animation"
                            So we can let user flip it, then they click Next. We'll add a Next button. */}
                        <FlashcardCard flashcard={currentCard} />
                    </div>

                    <div style={{ marginTop: '3rem', display: 'flex', gap: '1rem' }}>
                        <button
                            className="btn btn-secondary"
                            onClick={(e) => { e.stopPropagation(); setCurrentCardIndex(prev => prev > 0 ? prev - 1 : activeCards.length - 1); }}
                        >
                            ← Previous
                        </button>
                        <button
                            className="btn btn-primary"
                            onClick={(e) => { e.stopPropagation(); handleNextCard(); }}
                        >
                            Next →
                        </button>
                    </div>
                </div>
            ) : (
                <div className="topic-clusters-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '1.5rem' }}>
                    {Object.entries(groupedCards).map(([topic, cards]) => (
                        <div
                            key={topic}
                            className="cluster-card"
                            onClick={() => { setActiveTopic(topic); setCurrentCardIndex(0); }}
                        >
                            <h2 style={{ fontSize: '1.8rem', margin: '0 0 1rem 0', color: 'var(--text-primary)', wordBreak: 'break-word' }}>
                                {topic}
                            </h2>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <span style={{ color: 'var(--accent-color)', fontWeight: 'bold' }}>{cards.length} Cards</span>
                                <button
                                    className="btn-delete-cluster"
                                    onClick={(e) => handleDeleteTopic(topic, e)}
                                    title="Delete entire topic cluster"
                                >
                                    🗑️
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}

export default FlashcardsPage;
