import React, { useState } from 'react';
import { login as loginApi, register as registerApi, setToken, type LoginData, type RegisterData } from '../api/auth';
import { useAuth } from '../contexts/AuthContext';

interface AuthFormProps {
  onSuccess: () => void;
}

const AuthForm: React.FC<AuthFormProps> = ({ onSuccess }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    full_name: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { login } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      if (isLogin) {
        // Login
        const loginData: LoginData = {
          email: formData.email,
          password: formData.password,
        };
        const authResponse = await loginApi(loginData);
        setToken(authResponse.access_token);

        // Get user data and update context
        const { getCurrentUser } = await import('../api/auth');
        const userData = await getCurrentUser();
        login(userData, authResponse.access_token);

        onSuccess();
      } else {
        // Register
        const registerData: RegisterData = {
          email: formData.email,
          password: formData.password,
          full_name: formData.full_name || undefined,
        };
        await registerApi(registerData);

        // After successful registration, log the user in
        const loginData: LoginData = {
          email: formData.email,
          password: formData.password,
        };
        const authResponse = await loginApi(loginData);
        setToken(authResponse.access_token);

        // Get user data and update context
        const { getCurrentUser } = await import('../api/auth');
        const userData = await getCurrentUser();
        login(userData, authResponse.access_token);

        onSuccess();
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  return (
    <div style={{ maxWidth: 400, margin: '0 auto', padding: 20 }}>
      <h2>{isLogin ? 'Login' : 'Register'}</h2>
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
        <input
          type="email"
          name="email"
          placeholder="Email"
          value={formData.email}
          onChange={handleInputChange}
          required
          style={{ padding: 8, borderRadius: 4, border: '1px solid #ccc' }}
        />
        <input
          type="password"
          name="password"
          placeholder="Password"
          value={formData.password}
          onChange={handleInputChange}
          required
          minLength={6}
          style={{ padding: 8, borderRadius: 4, border: '1px solid #ccc' }}
        />
        {!isLogin && (
          <input
            type="text"
            name="full_name"
            placeholder="Full Name (optional)"
            value={formData.full_name}
            onChange={handleInputChange}
            style={{ padding: 8, borderRadius: 4, border: '1px solid #ccc' }}
          />
        )}
        <button
          type="submit"
          disabled={loading}
          style={{
            padding: '12px 16px',
            backgroundColor: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: 4,
            cursor: loading ? 'not-allowed' : 'pointer',
          }}
        >
          {loading ? 'Processing...' : isLogin ? 'Login' : 'Register'}
        </button>
        {error && (
          <div style={{ color: 'red', fontSize: 14, textAlign: 'center' }}>
            {error}
          </div>
        )}
      </form>
      <p style={{ textAlign: 'center', marginTop: 16 }}>
        {isLogin ? "Don't have an account? " : 'Already have an account? '}
        <button
          type="button"
          onClick={() => {
            setIsLogin(!isLogin);
            setError(null);
            setFormData({ email: '', password: '', full_name: '' });
          }}
          style={{
            background: 'none',
            border: 'none',
            color: '#007bff',
            cursor: 'pointer',
            textDecoration: 'underline',
          }}
        >
          {isLogin ? 'Register' : 'Login'}
        </button>
      </p>
    </div>
  );
};

export default AuthForm;
