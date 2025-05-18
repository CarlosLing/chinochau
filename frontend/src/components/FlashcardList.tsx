import React, { useEffect, useState } from 'react';
import { getAllFlashcards } from '../api/flashcards';
import type { Flashcard } from '../api/flashcards';

const FlashcardList: React.FC = () => {
  const [flashcards, setFlashcards] = useState<Flashcard[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getAllFlashcards()
      .then(setFlashcards)
      .catch((err) => setError('Failed to load flashcards'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div>Loading flashcards...</div>;
  if (error) return <div style={{ color: 'red' }}>{error}</div>;
  if (flashcards.length === 0) return <div>No flashcards found.</div>;

  return (
    <div>
      <h2>Flashcards</h2>
      <ul>
        {flashcards.map((card) => (
          <li key={card.chinese} style={{ marginBottom: 16, border: '1px solid #eee', padding: 12, borderRadius: 8 }}>
            <strong>{card.chinese}</strong> <br />
            <span style={{ color: '#888' }}>{card.pinyin}</span>
            <ul>
              {card.definitions.map((def, i) => (
                <li key={i}>{def}</li>
              ))}
            </ul>
            {card.example && <div style={{ fontStyle: 'italic', color: '#555' }}>Example: {card.example}</div>}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default FlashcardList;
