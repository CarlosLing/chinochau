"""
Service layer for flashcard operations.
"""
import json
from typing import List, Optional

import pinyin
from fastapi import HTTPException
from fastapi.concurrency import run_in_threadpool
from pinyin.cedict import translate_word
from sqlalchemy.orm import Session

from backend.db import FlashcardDB, UserDB
from backend.models import FlashcardModel
from chinochau.translate_google import translate_google


class FlashcardService:
    """Service class for flashcard operations."""

    @staticmethod
    def get_user_flashcards(db: Session, user: UserDB) -> List[FlashcardModel]:
        """Get all flashcards for a user."""
        flashcards = db.query(FlashcardDB).filter(FlashcardDB.user_id == user.id).all()
        return [FlashcardModel(**f.to_dict()) for f in flashcards]

    @staticmethod
    def get_flashcard_by_chinese(
        db: Session, chinese: str, user: UserDB
    ) -> Optional[FlashcardModel]:
        """Get a specific flashcard by Chinese text for a user."""
        card = (
            db.query(FlashcardDB)
            .filter(FlashcardDB.chinese == chinese, FlashcardDB.user_id == user.id)
            .first()
        )
        if card:
            return FlashcardModel(**card.to_dict())
        return None

    @staticmethod
    def get_flashcard_by_id(
        db: Session, flashcard_id: int, user: UserDB
    ) -> Optional[FlashcardDB]:
        """Get a flashcard by ID, ensuring it belongs to the user."""
        return (
            db.query(FlashcardDB)
            .filter(FlashcardDB.id == flashcard_id, FlashcardDB.user_id == user.id)
            .first()
        )

    @staticmethod
    async def get_or_create_flashcard(
        db: Session, chinese: str, user: UserDB
    ) -> FlashcardModel:
        """Get or create a flashcard for a user."""
        # Check if flashcard already exists
        card = (
            db.query(FlashcardDB)
            .filter(FlashcardDB.chinese == chinese, FlashcardDB.user_id == user.id)
            .first()
        )
        if card:
            return FlashcardModel(**card.to_dict())

        # Create new flashcard
        f_pinyin = await run_in_threadpool(pinyin.get, chinese)
        f_definition = await run_in_threadpool(translate_word, chinese)
        if not f_definition:
            f_definition = await translate_google(chinese)

        flashcard_db = FlashcardDB(
            chinese=chinese,
            pinyin=f_pinyin,
            definitions=json.dumps(f_definition),
            user_id=user.id,
        )
        db.add(flashcard_db)
        db.commit()
        db.refresh(flashcard_db)
        return FlashcardModel(**flashcard_db.to_dict())

    @staticmethod
    def delete_flashcard(db: Session, flashcard_id: int, user: UserDB) -> bool:
        """Delete a flashcard by ID, ensuring it belongs to the user."""
        flashcard = (
            db.query(FlashcardDB)
            .filter(FlashcardDB.id == flashcard_id, FlashcardDB.user_id == user.id)
            .first()
        )
        if not flashcard:
            return False

        db.delete(flashcard)
        db.commit()
        return True
