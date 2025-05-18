import React from 'react';
import { type Flashcard } from '../api/flashcards';

interface FlashcardMenuProps {
  flashcards: Flashcard[];
  onSelect: (index: number) => void;
  selectedIndex: number;
}

const FlashcardMenu: React.FC<FlashcardMenuProps> = ({ flashcards, onSelect, selectedIndex }) => {

  return (
    <nav style={{ width: 120, borderRight: '1px solid #eee', height: '100vh', overflowY: 'auto', background: '#fafafa' }}>
      <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
        {flashcards.map((card, idx) => (
          <li key={card.chinese}>
            <button
              style={{
                width: '100%',
                padding: '8px 4px',
                background: idx === selectedIndex ? '#e0e7ff' : 'transparent',
                border: 'none',
                textAlign: 'left',
                cursor: 'pointer',
                fontWeight: idx === selectedIndex ? 'bold' : 'normal',
                color: '#222',
                outline: 'none',
              }}
              onClick={() => onSelect(idx)}
            >
              {card.chinese}
            </button>
          </li>
        ))}
      </ul>
    </nav>
  );
};

export default FlashcardMenu;
