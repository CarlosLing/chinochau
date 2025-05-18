import axios from 'axios';

// You can set this to your backend URL, or use an environment variable
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface Flashcard {
  chinese: string;
  pinyin: string;
  definitions: string[];
  example?: string;
}

export async function getAllFlashcards(): Promise<Flashcard[]> {
  const response = await axios.get(`${API_BASE_URL}/flashcards`);
  return response.data;
}

export async function getFlashcard(chinese: string): Promise<Flashcard> {
  const response = await axios.get(`${API_BASE_URL}/flashcards/${encodeURIComponent(chinese)}`);
  return response.data;
}

export async function createOrGetFlashcard(chinese: string): Promise<Flashcard> {
  const response = await axios.post(`${API_BASE_URL}/flashcards`, { chinese });
  return response.data;
}

export async function getExamples(chinese: string, number_of_examples = 2): Promise<string> {
  const response = await axios.get(`${API_BASE_URL}/examples/${encodeURIComponent(chinese)}`, {
    params: { number_of_examples },
  });
  return response.data.examples;
}
