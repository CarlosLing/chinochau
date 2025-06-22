import './App.css';

import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import StudyPage from './components/StudyPage';
import UserMenu from './components/UserMenu';

function App() {
  return (
    <AuthProvider>
      <div style={{ maxWidth: 1200, margin: '0 auto', padding: 16 }}>
        <ProtectedRoute>
          <UserMenu />
          <h1 style={{ textAlign: 'center' }}>Chinochau Flashcards</h1>
          <StudyPage />
        </ProtectedRoute>
      </div>
    </AuthProvider>
  );
}

export default App;
