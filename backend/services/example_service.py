"""
Service layer for example operations.
"""
from typing import List

from fastapi import HTTPException
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session

from backend.db import ExampleDB, FlashcardDB, UserDB
from backend.models import ExampleModel, ExamplesResponse, FlashcardWithExamplesModel
from chinochau.deepseek import get_examples_deepseek


class ExampleService:
    """Service class for example operations."""

    @staticmethod
    async def create_examples(
        db: Session, flashcard_id: int, count: int, user: UserDB
    ) -> ExamplesResponse:
        """Generate and save new examples for a flashcard."""
        # Check if the flashcard exists and belongs to the current user
        flashcard = (
            db.query(FlashcardDB)
            .filter(
                FlashcardDB.id == flashcard_id,
                FlashcardDB.user_id == user.id,
            )
            .first()
        )
        if not flashcard:
            raise HTTPException(status_code=404, detail="Flashcard not found")

        # Generate examples using the flashcard's Chinese word
        try:
            examples_list = await run_in_threadpool(
                get_examples_deepseek, flashcard.chinese, count
            )
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to generate examples: {str(e)}"
            )

        # Save examples to database with flashcard reference
        saved_examples = []
        for example_text in examples_list:
            example_db = ExampleDB(flashcard_id=flashcard_id, example_text=example_text)
            db.add(example_db)
            db.commit()
            db.refresh(example_db)
            saved_examples.append(ExampleModel(**example_db.to_dict()))

        return ExamplesResponse(
            examples=saved_examples,
            total=len(saved_examples),
            flashcard_chinese=flashcard.chinese,
        )

    @staticmethod
    def get_examples(db: Session, flashcard_id: int, user: UserDB) -> ExamplesResponse:
        """Retrieve examples for a specific flashcard from the database."""
        flashcard = (
            db.query(FlashcardDB)
            .filter(FlashcardDB.id == flashcard_id, FlashcardDB.user_id == user.id)
            .first()
        )
        if not flashcard:
            raise HTTPException(status_code=404, detail="Flashcard not found")

        total_examples = (
            db.query(ExampleDB).filter(ExampleDB.flashcard_id == flashcard_id).count()
        )

        if total_examples == 0:
            raise HTTPException(
                status_code=404,
                detail=f"No examples available for flashcard '{flashcard.chinese}'. Please generate some examples first using the POST /examples endpoint.",
            )

        # Get examples for this flashcard (ordered by creation time)
        examples = (
            db.query(ExampleDB)
            .filter(ExampleDB.flashcard_id == flashcard_id)
            .order_by(ExampleDB.created_at.asc())
            .all()
        )

        example_models = [ExampleModel(**example.to_dict()) for example in examples]

        return ExamplesResponse(
            examples=example_models,
            total=total_examples,
            flashcard_chinese=flashcard.chinese,
        )

    @staticmethod
    def get_flashcard_with_examples(
        db: Session, flashcard_id: int, user: UserDB
    ) -> FlashcardWithExamplesModel:
        """Get a specific flashcard with its examples."""
        # Check if the flashcard exists and belongs to the current user
        flashcard = (
            db.query(FlashcardDB)
            .filter(FlashcardDB.id == flashcard_id, FlashcardDB.user_id == user.id)
            .first()
        )
        if not flashcard:
            raise HTTPException(status_code=404, detail="Flashcard not found")

        # Get all examples for this flashcard
        examples = (
            db.query(ExampleDB).filter(ExampleDB.flashcard_id == flashcard.id).all()
        )
        examples_count = len(examples)

        # Extract just the example texts
        example_texts = [example.example_text for example in examples]

        flashcard_data = flashcard.to_dict()
        flashcard_data["examples"] = example_texts
        flashcard_data["examples_count"] = examples_count

        return FlashcardWithExamplesModel(**flashcard_data)
