import React, { useState } from 'react';
import { createOrGetFlashcard, type Flashcard } from '../api/flashcards';

interface AddFlashcardProps {
  onAdd: (card: Flashcard) => void;
}

const AddFlashcard: React.FC<AddFlashcardProps> = ({ onAdd }) => {
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const card = await createOrGetFlashcard(input.trim());
      onAdd(card);
      setInput('');
    } catch (err) {
      setError('Failed to add flashcard');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleAdd} style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
      <input
        type="text"
        value={input}
        onChange={e => setInput(e.target.value)}
        placeholder="Add new Chinese word"
        disabled={loading}
        style={{ flex: 1, padding: 8, borderRadius: 4, border: '1px solid #ccc' }}
      />
      <button type="submit" disabled={loading || !input.trim()} style={{ padding: '8px 16px' }}>
        {loading ? 'Adding...' : 'Add'}
      </button>
      {error && <span style={{ color: 'red', marginLeft: 8 }}>{error}</span>}
    </form>
  );
};

export default AddFlashcard;
