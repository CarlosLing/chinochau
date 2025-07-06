"""
Service layer for list operations.
"""
from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.db import FlashcardDB, ListDB, UserDB
from backend.models import FlashcardModel, ListModel, ListWithFlashcardsModel


class ListService:
    """Service class for list operations."""

    @staticmethod
    def get_user_lists(db: Session, user: UserDB) -> List[ListModel]:
        """Get all lists for a user."""
        lists = db.query(ListDB).filter(ListDB.user_id == user.id).all()
        return [ListModel(**list_item.to_dict()) for list_item in lists]

    @staticmethod
    def get_list_by_id(db: Session, list_id: int, user: UserDB) -> Optional[ListModel]:
        """Get a specific list by ID for a user."""
        list_item = (
            db.query(ListDB)
            .filter(ListDB.id == list_id, ListDB.user_id == user.id)
            .first()
        )
        if list_item:
            return ListModel(**list_item.to_dict())
        return None

    @staticmethod
    def get_list_with_flashcards(
        db: Session, list_id: int, user: UserDB
    ) -> Optional[ListWithFlashcardsModel]:
        """Get a list with all its flashcards."""
        list_item = (
            db.query(ListDB)
            .filter(ListDB.id == list_id, ListDB.user_id == user.id)
            .first()
        )
        if not list_item:
            return None

        flashcards = [FlashcardModel(**fc.to_dict()) for fc in list_item.flashcards]

        return ListWithFlashcardsModel(
            id=list_item.id,
            name=list_item.name,
            description=list_item.description,
            user_id=list_item.user_id,
            created_at=list_item.created_at,
            modified_at=list_item.modified_at,
            flashcards=flashcards,
        )

    @staticmethod
    def create_list(
        db: Session, name: str, description: str, user: UserDB
    ) -> ListModel:
        """Create a new list for a user."""
        list_db = ListDB(
            name=name,
            description=description,
            user_id=user.id,
        )
        db.add(list_db)
        db.commit()
        db.refresh(list_db)
        return ListModel(**list_db.to_dict())

    @staticmethod
    def update_list(
        db: Session, list_id: int, name: str, description: str, user: UserDB
    ) -> Optional[ListModel]:
        """Update a list."""
        list_item = (
            db.query(ListDB)
            .filter(ListDB.id == list_id, ListDB.user_id == user.id)
            .first()
        )
        if not list_item:
            return None

        if name is not None:
            list_item.name = name
        if description is not None:
            list_item.description = description
        list_item.modified_at = datetime.utcnow()

        db.commit()
        db.refresh(list_item)
        return ListModel(**list_item.to_dict())

    @staticmethod
    def delete_list(db: Session, list_id: int, user: UserDB) -> bool:
        """Delete a list."""
        list_item = (
            db.query(ListDB)
            .filter(ListDB.id == list_id, ListDB.user_id == user.id)
            .first()
        )
        if not list_item:
            return False

        db.delete(list_item)
        db.commit()
        return True

    @staticmethod
    def add_flashcard_to_list(
        db: Session, list_id: int, flashcard_id: int, user: UserDB
    ) -> bool:
        """Add a flashcard to a list."""
        # Get the list and verify it belongs to the user
        list_item = (
            db.query(ListDB)
            .filter(ListDB.id == list_id, ListDB.user_id == user.id)
            .first()
        )
        if not list_item:
            return False

        # Get the flashcard and verify it belongs to the user
        flashcard = (
            db.query(FlashcardDB)
            .filter(FlashcardDB.id == flashcard_id, FlashcardDB.user_id == user.id)
            .first()
        )
        if not flashcard:
            return False

        # Check if flashcard is already in the list
        if flashcard in list_item.flashcards:
            return True  # Already in list, consider it successful

        # Add flashcard to list
        list_item.flashcards.append(flashcard)
        list_item.modified_at = datetime.utcnow()
        db.commit()
        return True

    @staticmethod
    def remove_flashcard_from_list(
        db: Session, list_id: int, flashcard_id: int, user: UserDB
    ) -> bool:
        """Remove a flashcard from a list."""
        # Get the list and verify it belongs to the user
        list_item = (
            db.query(ListDB)
            .filter(ListDB.id == list_id, ListDB.user_id == user.id)
            .first()
        )
        if not list_item:
            return False

        # Get the flashcard and verify it belongs to the user
        flashcard = (
            db.query(FlashcardDB)
            .filter(FlashcardDB.id == flashcard_id, FlashcardDB.user_id == user.id)
            .first()
        )
        if not flashcard:
            return False

        # Check if flashcard is in the list
        if flashcard not in list_item.flashcards:
            return True  # Not in list, consider it successful

        # Remove flashcard from list
        list_item.flashcards.remove(flashcard)
        list_item.modified_at = datetime.utcnow()
        db.commit()
        return True
