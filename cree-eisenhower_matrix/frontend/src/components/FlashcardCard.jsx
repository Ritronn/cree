import React, { useState } from 'react';

function FlashcardCard({ flashcard }) {
    const [flipped, setFlipped] = useState(false);

    return (
        <div
            className={`flashcard ${flipped ? 'flipped' : ''}`}
            onClick={() => setFlipped(!flipped)}
        >
            <div className="flashcard-front">
                <span className="flashcard-topic">{flashcard.topic}</span>
                <div className="flashcard-q">{flashcard.question}</div>
                <div className="flashcard-hint" style={{ marginTop: '1rem', fontSize: '0.8rem', opacity: 0.5 }}>
                    Click to flip
                </div>
            </div>
            <div className="flashcard-back">
                <span className="flashcard-topic">{flashcard.topic}</span>
                <div className="flashcard-a">
                    {flashcard.answer.split('\n').map((line, i) => (
                        <div key={i} style={{ marginBottom: '0.5rem' }}>{line}</div>
                    ))}
                </div>
            </div>
        </div>
    );
}

export default FlashcardCard;
