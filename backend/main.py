import json
from typing import List

import pinyin
from fastapi import Body, Depends, FastAPI, HTTPException
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from pinyin.cedict import translate_word
from sqlalchemy.orm import Session

from backend.db import FlashcardDB, SessionLocal
from backend.models import (
    ExamplesOutput,
    FlashcardCreateModel,
    FlashcardModel,
    TextInput,
)
from chinochau.deepseek import get_examples_deepseek
from chinochau.translate_google import translate_google

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/flashcards", response_model=List[FlashcardModel])
def get_flashcards(db: Session = Depends(get_db)):
    flashcards = db.query(FlashcardDB).all()
    return [FlashcardModel(**f.to_dict()) for f in flashcards]


@app.get("/flashcards/{chinese}", response_model=FlashcardModel)
def get_flashcard(chinese: str, db: Session = Depends(get_db)):
    card = db.query(FlashcardDB).filter(FlashcardDB.chinese == chinese).first()
    if card:
        return FlashcardModel(**card.to_dict())
    raise HTTPException(status_code=404, detail="Flashcard not found")


@app.post("/flashcards", response_model=FlashcardModel)
async def get_or_create_flashcard(
    data: FlashcardCreateModel = Body(...), db: Session = Depends(get_db)
):
    card = db.query(FlashcardDB).filter(FlashcardDB.chinese == data.chinese).first()
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
        example=None,
    )
    db.add(flashcard_db)
    db.commit()
    db.refresh(flashcard_db)
    return FlashcardModel(**flashcard_db.to_dict())


@app.get("/examples/{chinese}", response_model=ExamplesOutput)
def get_examples(chinese: str, number_of_examples: int = 2):
    examples = get_examples_deepseek(chinese, number_of_examples)
    return ExamplesOutput(examples=examples)


@app.post("/translate")
async def translate_api(data: TextInput):
    """Return the English translation(s) for a given Chinese text."""
    result = await translate_google(data.chinese)
    return {"translation": result[0]}


@app.post("/pinyin")
async def pinyin_api(data: TextInput):
    """Return the pinyin for a given Chinese text."""
    result = await run_in_threadpool(pinyin.get, data.chinese)
    return {"pinyin": result}
