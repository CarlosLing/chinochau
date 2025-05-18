

import React, { useEffect, useState } from 'react';
import { getAllFlashcards, type Flashcard } from '../api/flashcards';
import StudyFlashcard from './StudyFlashcard';
import FlashcardMenu from './FlashcardMenu';
import AddFlashcard from './AddFlashcard';

const StudyPage: React.FC = () => {
  const [flashcards, setFlashcards] = useState<Flashcard[]>([]);
  const [current, setCurrent] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);


  useEffect(() => {
    getAllFlashcards()
      .then(setFlashcards)
      .catch(() => setError('Failed to load flashcards'))
      .finally(() => setLoading(false));
  }, []);

  const handleAdd = (card: Flashcard) => {
    setFlashcards((prev) => [...prev, card]);
    setCurrent(flashcards.length); // jump to new card
  };

  const goPrev = () => setCurrent((i) => (i === 0 ? flashcards.length - 1 : i - 1));
  const goNext = () => setCurrent((i) => (i === flashcards.length - 1 ? 0 : i + 1));

  if (loading) return <div>Loading flashcards...</div>;
  if (error) return <div style={{ color: 'red' }}>{error}</div>;
  if (flashcards.length === 0) return <div>No flashcards found.</div>;

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      <FlashcardMenu flashcards={flashcards} onSelect={setCurrent} selectedIndex={current} />
      <div style={{ flex: 1 }}>
        <h2 style={{ textAlign: 'center', marginTop: 32 }}>Study Flashcards</h2>
        <AddFlashcard onAdd={handleAdd} />
        <StudyFlashcard card={flashcards[current]} />
        <div style={{ display: 'flex', justifyContent: 'center', gap: 16, marginTop: 24 }}>
          <button onClick={goPrev}>Previous</button>
          <span>
            {current + 1} / {flashcards.length}
          </span>
          <button onClick={goNext}>Next</button>
        </div>
      </div>
    </div>
  );
};

export default StudyPage;
