from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
from contextlib import asynccontextmanager
from chinochau.data import Flashcard
from chinochau.service import ChinoChau
from chinochau.deepseek import get_examples_deepseek

# Pydantic models for API
class FlashcardModel(BaseModel):
    chinese: str
    pinyin: str
    definitions: List[str]
    example: Optional[str] = None

class FlashcardCreateModel(BaseModel):
    chinese: str

# Use ChinoChau to manage flashcards for now
chinochau_service = ChinoChau(source_file="input.txt")

@asynccontextmanager
async def lifespan(app: FastAPI):
    await chinochau_service.load_file()
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/flashcards", response_model=List[FlashcardModel])
def get_flashcards():
    flashcards = []
    for i in range(len(chinochau_service)):
        card = chinochau_service.get(i)
        flashcards.append(
            FlashcardModel(
                chinese=card.chinese,
                pinyin=card.pinyin,
                definitions=card.definitions,
                example=card.example,
            )
        )
    return flashcards

@app.get("/flashcards/{chinese}", response_model=FlashcardModel)
def get_flashcard(chinese: str):
    for i in range(len(chinochau_service)):
        card = chinochau_service.get(i)
        if card.chinese == chinese:
            return FlashcardModel(
                chinese=card.chinese,
                pinyin=card.pinyin,
                definitions=card.definitions,
                example=card.example,
            )
    raise HTTPException(status_code=404, detail="Flashcard not found")

@app.post("/flashcards", response_model=FlashcardModel)
async def create_flashcard(data: FlashcardCreateModel):
    card = await chinochau_service.create_flashcard(data.chinese)
    chinochau_service.flashcards.append(card)
    chinochau_service.update_master_flashcards()
    return FlashcardModel(
        chinese=card.chinese,
        pinyin=card.pinyin,
        definitions=card.definitions,
        example=card.example,
    )

@app.get("/examples/{chinese}")
def get_examples(chinese: str, number_of_examples: int = 2):
    examples = get_examples_deepseek(chinese, number_of_examples)
    return {"examples": examples}
