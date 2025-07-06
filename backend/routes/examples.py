"""
Example API routes.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.auth import get_current_active_user
from backend.db import UserDB, get_db
from backend.models import (
    ExampleCreateRequest,
    ExamplesResponse,
    FlashcardWithExamplesModel,
)
from backend.services.example_service import ExampleService

router = APIRouter(tags=["examples"])


@router.post("/examples", response_model=ExamplesResponse)
async def create_examples(
    request: ExampleCreateRequest,
    current_user: UserDB = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Generate and save new examples for a specific flashcard."""
    return await ExampleService.create_examples(
        db, request.flashcard_id, request.count, current_user
    )


@router.get("/examples", response_model=ExamplesResponse)
def get_saved_examples(
    flashcard_id: int,
    current_user: UserDB = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Retrieve examples for a specific flashcard from the database."""
    return ExampleService.get_examples(db, flashcard_id, current_user)


@router.get("/flashcard-with-example", response_model=FlashcardWithExamplesModel)
def get_flashcard_with_example(
    flashcard_id: int,
    current_user: UserDB = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get a specific flashcard with its examples."""
    return ExampleService.get_flashcard_with_examples(db, flashcard_id, current_user)
