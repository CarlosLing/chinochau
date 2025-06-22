import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import AuthForm from './AuthForm';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { isLoggedIn, loading } = useAuth();

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <div>Loading...</div>
      </div>
    );
  }

  if (!isLoggedIn) {
    return <AuthForm onSuccess={() => window.location.reload()} />;
  }

  return <>{children}</>;
};

export default ProtectedRoute;
