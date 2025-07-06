"""
List API routes.
"""
from typing import List

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.auth import get_current_active_user
from backend.db import UserDB, get_db
from backend.models import (
    ListCreateModel,
    ListModel,
    ListUpdateModel,
    ListWithFlashcardsModel,
)
from backend.services.list_service import ListService

router = APIRouter(prefix="/lists", tags=["lists"])


@router.get("", response_model=List[ListModel])
def get_lists(
    current_user: UserDB = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get all lists for the current user."""
    return ListService.get_user_lists(db, current_user)


@router.get("/{list_id}", response_model=ListModel)
def get_list(
    list_id: int,
    current_user: UserDB = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get a specific list by ID for the current user."""
    list_item = ListService.get_list_by_id(db, list_id, current_user)
    if not list_item:
        raise HTTPException(status_code=404, detail="List not found")
    return list_item


@router.get("/{list_id}/flashcards", response_model=ListWithFlashcardsModel)
def get_list_with_flashcards(
    list_id: int,
    current_user: UserDB = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get a list with all its flashcards."""
    list_item = ListService.get_list_with_flashcards(db, list_id, current_user)
    if not list_item:
        raise HTTPException(status_code=404, detail="List not found")
    return list_item


@router.post("", response_model=ListModel)
def create_list(
    data: ListCreateModel = Body(...),
    current_user: UserDB = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a new list for the current user."""
    return ListService.create_list(db, data.name, data.description, current_user)


@router.put("/{list_id}", response_model=ListModel)
def update_list(
    list_id: int,
    data: ListUpdateModel = Body(...),
    current_user: UserDB = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update a list for the current user."""
    list_item = ListService.update_list(
        db, list_id, data.name, data.description, current_user
    )
    if not list_item:
        raise HTTPException(status_code=404, detail="List not found")
    return list_item


@router.delete("/{list_id}")
def delete_list(
    list_id: int,
    current_user: UserDB = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Delete a list for the current user."""
    success = ListService.delete_list(db, list_id, current_user)
    if not success:
        raise HTTPException(status_code=404, detail="List not found")
    return {"message": "List deleted successfully"}


@router.post("/{list_id}/flashcards/{flashcard_id}")
def add_flashcard_to_list(
    list_id: int,
    flashcard_id: int,
    current_user: UserDB = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Add a flashcard to a list."""
    success = ListService.add_flashcard_to_list(db, list_id, flashcard_id, current_user)
    if not success:
        raise HTTPException(status_code=404, detail="List or flashcard not found")
    return {"message": "Flashcard added to list successfully"}


@router.delete("/{list_id}/flashcards/{flashcard_id}")
def remove_flashcard_from_list(
    list_id: int,
    flashcard_id: int,
    current_user: UserDB = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Remove a flashcard from a list."""
    success = ListService.remove_flashcard_from_list(
        db, list_id, flashcard_id, current_user
    )
    if not success:
        raise HTTPException(status_code=404, detail="List or flashcard not found")
    return {"message": "Flashcard removed from list successfully"}
