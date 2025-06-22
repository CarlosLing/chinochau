import json
from typing import List

import pinyin
from fastapi import Body, Depends, FastAPI, HTTPException
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from pinyin.cedict import translate_word
from sqlalchemy.orm import Session

from backend.auth import get_current_active_user, get_db
from backend.auth_routes import router as auth_router
from backend.db import ExampleDB, FlashcardDB, SessionLocal, UserDB
from backend.models import (
    ExampleCreateRequest,
    ExampleModel,
    ExamplesResponse,
    FlashcardCreateModel,
    FlashcardModel,
    FlashcardWithExamplesModel,
    TextInput,
)
from chinochau.deepseek import get_examples_deepseek
from chinochau.translate_google import translate_google

app = FastAPI(
    title="Chinochau API",
    description="Chinese flashcard learning API with authentication",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include authentication routes
app.include_router(auth_router)


@app.get("/flashcards", response_model=List[FlashcardModel])
def get_flashcards(
    current_user: UserDB = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get flashcards for the current user."""
    flashcards = (
        db.query(FlashcardDB).filter(FlashcardDB.user_id == current_user.id).all()
    )
    return [FlashcardModel(**f.to_dict()) for f in flashcards]


@app.get("/flashcards/{chinese}", response_model=FlashcardModel)
def get_flashcard(
    chinese: str,
    current_user: UserDB = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get a specific flashcard by Chinese text for the current user."""
    card = (
        db.query(FlashcardDB)
        .filter(FlashcardDB.chinese == chinese, FlashcardDB.user_id == current_user.id)
        .first()
    )
    if card:
        return FlashcardModel(**card.to_dict())
    raise HTTPException(status_code=404, detail="Flashcard not found")


@app.post("/flashcards", response_model=FlashcardModel)
async def get_or_create_flashcard(
    data: FlashcardCreateModel = Body(...),
    current_user: UserDB = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get or create a flashcard for the current user."""
    card = (
        db.query(FlashcardDB)
        .filter(
            FlashcardDB.chinese == data.chinese, FlashcardDB.user_id == current_user.id
        )
        .first()
    )
    if card:
        return FlashcardModel(**card.to_dict())

    # If not found, create it
    f_pinyin = await run_in_threadpool(pinyin.get, data.chinese)
    f_definition = await run_in_threadpool(translate_word, data.chinese)
    if not f_definition:
        f_definition = await translate_google(data.chinese)

    flashcard_db = FlashcardDB(
        chinese=data.chinese,
        pinyin=f_pinyin,
        definitions=json.dumps(f_definition),
        user_id=current_user.id,
    )
    db.add(flashcard_db)
    db.commit()
    db.refresh(flashcard_db)
    return FlashcardModel(**flashcard_db.to_dict())


@app.post("/translate")
async def translate_api(
    data: TextInput, current_user: UserDB = Depends(get_current_active_user)
):
    """Return the English translation(s) for a given Chinese text."""
    result = await translate_google(data.chinese)
    return {"translation": result[0]}


@app.post("/pinyin")
async def pinyin_api(
    data: TextInput, current_user: UserDB = Depends(get_current_active_user)
):
    """Return the pinyin for a given Chinese text."""
    result = await run_in_threadpool(pinyin.get, data.chinese)
    return {"pinyin": result}


@app.post("/examples", response_model=ExamplesResponse)
async def create_examples(
    request: ExampleCreateRequest,
    current_user: UserDB = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Generate and save new examples for a specific flashcard."""
    # Check if the flashcard exists and belongs to the current user
    flashcard = (
        db.query(FlashcardDB)
        .filter(
            FlashcardDB.id == request.flashcard_id,
            FlashcardDB.user_id == current_user.id,
        )
        .first()
    )
    if not flashcard:
        raise HTTPException(status_code=404, detail="Flashcard not found")

    # Generate examples using the flashcard's Chinese word
    try:
        examples_list = await run_in_threadpool(
            get_examples_deepseek, flashcard.chinese, request.count
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate examples: {str(e)}"
        )

    # Save examples to database with flashcard reference
    saved_examples = []
    for example_text in examples_list:
        example_db = ExampleDB(
            flashcard_id=request.flashcard_id, example_text=example_text
        )
        db.add(example_db)
        db.commit()
        db.refresh(example_db)
        saved_examples.append(ExampleModel(**example_db.to_dict()))

    return ExamplesResponse(
        examples=saved_examples,
        total=len(saved_examples),
        flashcard_chinese=flashcard.chinese,
    )


@app.get("/examples", response_model=ExamplesResponse)
def get_saved_examples(
    flashcard_id: int,
    current_user: UserDB = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Retrieve examples for a specific flashcard from the database."""
    flashcard = (
        db.query(FlashcardDB)
        .filter(FlashcardDB.id == flashcard_id, FlashcardDB.user_id == current_user.id)
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

    # Get the requested number of examples for this flashcard (most recent first)
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


@app.get("/flashcard-with-example", response_model=FlashcardWithExamplesModel)
def get_flashcard_with_example(
    flashcard_id: int,
    current_user: UserDB = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get a specific flashcard with its examples."""
    # Check if the flashcard exists and belongs to the current user
    flashcard = (
        db.query(FlashcardDB)
        .filter(FlashcardDB.id == flashcard_id, FlashcardDB.user_id == current_user.id)
        .first()
    )
    if not flashcard:
        raise HTTPException(status_code=404, detail="Flashcard not found")

    # Get all examples for this flashcard
    examples = db.query(ExampleDB).filter(ExampleDB.flashcard_id == flashcard.id).all()
    examples_count = len(examples)

    # Extract just the example texts
    example_texts = [example.example_text for example in examples]

    flashcard_data = flashcard.to_dict()
    flashcard_data["examples"] = example_texts
    flashcard_data["examples_count"] = examples_count

    return FlashcardWithExamplesModel(**flashcard_data)
