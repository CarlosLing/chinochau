import React, { useState } from 'react';
import { getExamples, type Flashcard } from '../api/flashcards';

interface StudyFlashcardProps {
  card: Flashcard;
}

const StudyFlashcard: React.FC<StudyFlashcardProps> = ({ card }) => {
  const [showPinyin, setShowPinyin] = useState(false);
  const [showDefinition, setShowDefinition] = useState(false);
  const [examples, setExamples] = useState<string[] | null>(null);
  const [loadingExamples, setLoadingExamples] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleGetExamples = async () => {
    setLoadingExamples(true);
    setError(null);
    try {
      const ex = await getExamples(card.chinese, 2);
      setExamples(Array.isArray(ex) ? ex : [ex]);
    } catch (err) {
      setError('Failed to fetch examples');
    } finally {
      setLoadingExamples(false);
    }
  };

  return (
    <div style={{ border: '1px solid #eee', borderRadius: 8, padding: 24, maxWidth: 400, margin: '0 auto', marginTop: 32 }}>
      <div style={{ fontSize: 32, textAlign: 'center', marginBottom: 16 }}>{card.chinese}</div>
      <div style={{ display: 'flex', justifyContent: 'center', gap: 16, marginBottom: 16 }}>
        <button onClick={() => setShowPinyin((v) => !v)}>
          {showPinyin ? 'Hide Pinyin' : 'Show Pinyin'}
        </button>
        <button onClick={() => setShowDefinition((v) => !v)}>
          {showDefinition ? 'Hide Definition' : 'Show Definition'}
        </button>
        <button onClick={handleGetExamples} disabled={loadingExamples}>
          {loadingExamples ? 'Loading...' : 'Get Examples'}
        </button>
      </div>
      {showPinyin && (
        <div style={{ fontSize: 20, color: '#888', textAlign: 'center', marginBottom: 8 }}>{card.pinyin}</div>
      )}
      {showDefinition && (
        <ul style={{ textAlign: 'left', margin: '0 auto', maxWidth: 300 }}>
          {card.definitions.map((def, i) => (
            <li key={i}>{def}</li>
          ))}
        </ul>
      )}
      {card.example && (
        <div style={{ fontStyle: 'italic', color: '#555', marginTop: 12 }}>Example: {card.example}</div>
      )}
      {examples && (
        <div style={{ marginTop: 16 }}>
          <strong>Examples:</strong>
          <ul style={{ marginTop: 4 }}>
            {examples.map((ex, i) => (
              <li key={i} style={{ fontStyle: 'italic', color: '#555' }}>{ex}</li>
            ))}
          </ul>
        </div>
      )}
      {error && <div style={{ color: 'red', marginTop: 8 }}>{error}</div>}
    </div>
  );
};

export default StudyFlashcard;
