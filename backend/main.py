"""
Main FastAPI application entry point.
"""
from backend.auth_routes import router as auth_router
from backend.core.config import create_app
from backend.db import ensure_admin_user_exists
from backend.routes import examples, flashcards, lists, translation

# Create the FastAPI app
app = create_app()

# Include all routers
app.include_router(auth_router)
app.include_router(flashcards.router)
app.include_router(lists.router)
app.include_router(examples.router)
app.include_router(translation.router)

# Ensure admin user exists on startup
ensure_admin_user_exists()
