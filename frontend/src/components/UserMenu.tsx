import React from 'react';
import { useAuth } from '../contexts/AuthContext';

const UserMenu: React.FC = () => {
  const { user, logout } = useAuth();

  if (!user) return null;

  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '8px 16px',
      backgroundColor: '#f8f9fa',
      borderBottom: '1px solid #dee2e6',
      marginBottom: 16
    }}>
      <div>
        <span style={{ fontSize: 14, color: '#6c757d' }}>Welcome, </span>
        <span style={{ fontWeight: 'bold' }}>
          {user.full_name || user.email}
        </span>
      </div>
      <button
        onClick={logout}
        style={{
          padding: '4px 12px',
          backgroundColor: '#dc3545',
          color: 'white',
          border: 'none',
          borderRadius: 4,
          cursor: 'pointer',
          fontSize: 12,
        }}
      >
        Logout
      </button>
    </div>
  );
};

export default UserMenu;
