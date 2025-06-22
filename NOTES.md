## TODOs:

- ✅ Add user authentication and authorization.
- Implement lists for users.
- Add integrations with HSK levels
- Add Pleco colors to pinyin.
- Add Sound in Flashcards

## Ideas:

- How do I access the database? -> Create a make command to open the SQLite database in a GUI tool like DB Browser for SQLite.

## Authentication Implementation:

### Completed Features:
- ✅ JWT-based authentication with FastAPI
- ✅ User registration and login endpoints
- ✅ Protected routes requiring authentication
- ✅ User-specific flashcard storage
- ✅ Frontend authentication with React Context
- ✅ Automatic token management and refresh
- ✅ Database migration script for existing data

### Authentication Flow:
1. Users register/login via frontend forms
2. Backend returns JWT access token
3. Frontend stores token and includes it in all requests
4. Backend validates token and associates data with authenticated user
5. All flashcards and examples are now user-specific

### Migration Steps:
1. Install dependencies: `make install`
2. Run migration: `make migrate-db`
3. Start backend: `make run-backend`
4. Start frontend: `make run-frontend`
5. Login with default user: admin@chinochau.local / admin123

### Security Notes:
- Change SECRET_KEY in production
- Change default admin password after first login
- Tokens expire after 30 minutes
- Passwords are hashed with bcrypt
