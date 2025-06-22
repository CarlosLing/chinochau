# Authentication Implementation Guide

## Overview

This document describes the authentication system added to the chinochau flashcard application. The system implements JWT-based authentication with user registration, login, and protected routes.

## Architecture

### Backend (FastAPI)
- **JWT Authentication**: Uses `python-jose` for token generation and validation
- **Password Hashing**: Uses `bcrypt` via `passlib` for secure password storage
- **Protected Routes**: All flashcard endpoints require authentication
- **User Management**: Users can register, login, and manage their own flashcards

### Frontend (React + TypeScript)
- **Authentication Context**: React Context provides auth state management
- **Automatic Token Management**: Tokens stored in localStorage with automatic refresh
- **Protected Routes**: Components only render when user is authenticated
- **Axios Interceptors**: Automatically add auth headers and handle auth errors

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    full_name VARCHAR,
    hashed_password VARCHAR NOT NULL,
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Updated Flashcards Table
```sql
CREATE TABLE flashcards (
    id INTEGER PRIMARY KEY,
    chinese VARCHAR NOT NULL,
    pinyin VARCHAR NOT NULL,
    definitions TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id)
);
```

## API Endpoints

### Authentication Endpoints
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user (returns JWT token)
- `GET /auth/me` - Get current user info
- `GET /auth/users` - List all users (admin only)

### Protected Endpoints
All existing flashcard endpoints now require authentication:
- `GET /flashcards` - Get user's flashcards
- `POST /flashcards` - Create flashcard for user
- `GET /flashcards/{chinese}` - Get specific user flashcard
- `POST /examples` - Create examples for user's flashcard
- `GET /examples` - Get examples for user's flashcard

## Migration Process

### For Existing Installations

1. **Install Dependencies**
   ```bash
   make install
   ```

2. **Run Migration**
   ```bash
   make migrate-db
   ```
   This will:
   - Backup existing database
   - Create users table
   - Add user_id column to flashcards
   - Create default admin user
   - Associate existing flashcards with admin user

3. **Default Credentials**
   - Email: `admin@chinochau.local`
   - Password: `admin123`
   - ⚠️ **Change these credentials after first login!**

### For New Installations
1. Install dependencies: `make install`
2. Start backend: `make run-backend`
3. Start frontend: `make run-frontend`
4. Register new user through the frontend

## Security Considerations

### Production Deployment
1. **Change Secret Key**: Update `SECRET_KEY` in `backend/auth.py`
2. **Environment Variables**: Move sensitive config to environment variables
3. **HTTPS**: Use HTTPS in production
4. **Token Expiration**: Adjust token expiration time as needed
5. **Password Policy**: Consider adding password complexity requirements

### Current Security Features
- Passwords hashed with bcrypt
- JWT tokens with expiration
- Protected routes requiring authentication
- User isolation (users can only access their own data)
- Automatic token refresh on frontend

## Usage Examples

### Backend Usage
```python
from backend.auth import get_current_active_user
from backend.db import UserDB

@app.get("/protected-endpoint")
async def protected_route(current_user: UserDB = Depends(get_current_active_user)):
    return {"message": f"Hello {current_user.email}"}
```

### Frontend Usage
```typescript
import { useAuth } from '../contexts/AuthContext';

function MyComponent() {
  const { user, logout, isLoggedIn } = useAuth();

  if (!isLoggedIn) {
    return <div>Please log in</div>;
  }

  return (
    <div>
      <h1>Welcome {user.full_name}</h1>
      <button onClick={logout}>Logout</button>
    </div>
  );
}
```

## Testing Authentication

### Test User Registration
```bash
curl -X POST "http://localhost:8000/auth/register" \
     -H "Content-Type: application/json" \
     -d '{"email": "test@example.com", "password": "testpass123", "full_name": "Test User"}'
```

### Test User Login
```bash
curl -X POST "http://localhost:8000/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=test@example.com&password=testpass123"
```

### Test Protected Endpoint
```bash
curl -X GET "http://localhost:8000/flashcards" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"
```

## Troubleshooting

### Common Issues

1. **401 Unauthorized**: Check token validity and format
2. **Import Errors**: Ensure all dependencies are installed with `poetry install`
3. **Database Errors**: Run migration script if upgrading from pre-auth version
4. **CORS Issues**: Check CORS settings in backend/main.py

### Debug Steps
1. Check backend logs for authentication errors
2. Verify token format in browser developer tools
3. Test API endpoints with curl/Postman
4. Check database schema after migration

## Future Enhancements

### Potential Improvements
- OAuth2 integration (Google, GitHub, etc.)
- Password reset functionality
- Email verification
- Role-based access control
- Session management
- Audit logging
- Rate limiting
- Two-factor authentication

### User Lists Feature
With authentication in place, implementing user-specific flashcard lists becomes straightforward:
1. Add Lists table with user_id foreign key
2. Add flashcard_list_id to flashcards table
3. Create list management endpoints
4. Update frontend to support list organization
