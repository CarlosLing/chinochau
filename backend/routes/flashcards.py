"""
Flashcard API routes.
"""
from typing import List

from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session

from backend.auth import get_current_active_user
from backend.db import UserDB, get_db
from backend.models import FlashcardCreateModel, FlashcardModel
from backend.services.flashcard_service import FlashcardService

router = APIRouter(prefix="/flashcards", tags=["flashcards"])


@router.get("", response_model=List[FlashcardModel])
def get_flashcards(
    current_user: UserDB = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get flashcards for the current user."""
    return FlashcardService.get_user_flashcards(db, current_user)


@router.get("/{chinese}", response_model=FlashcardModel)
def get_flashcard(
    chinese: str,
    current_user: UserDB = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get a specific flashcard by Chinese text for the current user."""
    flashcard = FlashcardService.get_flashcard_by_chinese(db, chinese, current_user)
    if flashcard:
        return flashcard
    from fastapi import HTTPException

    raise HTTPException(status_code=404, detail="Flashcard not found")


@router.post("", response_model=FlashcardModel)
async def get_or_create_flashcard(
    data: FlashcardCreateModel = Body(...),
    current_user: UserDB = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get or create a flashcard for the current user."""
    return await FlashcardService.get_or_create_flashcard(
        db, data.chinese, current_user
    )


@router.delete("/{flashcard_id}")
def delete_flashcard_by_id(
    flashcard_id: int,
    current_user: UserDB = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Delete a flashcard by ID for the current user."""
    success = FlashcardService.delete_flashcard(db, flashcard_id, current_user)
    if not success:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Flashcard not found")

    return {"message": "Flashcard deleted successfully"}
