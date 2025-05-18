
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
import json

from fastapi import Body
from fastapi.concurrency import run_in_threadpool
from backend.db import SessionLocal, FlashcardDB
import pinyin
from pinyin.cedict import translate_word
from chinochau.translate_google import translate_google
from chinochau.deepseek import get_examples_deepseek


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class FlashcardModel(BaseModel):
    chinese: str
    pinyin: str
    definitions: List[str]
    example: Optional[str] = None

class FlashcardCreateModel(BaseModel):
    chinese: str

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
    data: FlashcardCreateModel = Body(...),
    db: Session = Depends(get_db)
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

@app.get("/examples/{chinese}")
def get_examples(chinese: str, number_of_examples: int = 2):
    examples = get_examples_deepseek(chinese, number_of_examples)
    return {"examples": examples}
