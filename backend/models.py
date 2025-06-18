from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class FlashcardModel(BaseModel):
    id: int
    chinese: str
    pinyin: str
    definitions: List[str]


class FlashcardCreateModel(BaseModel):
    chinese: str


class TextInput(BaseModel):
    chinese: str


class ExampleCreateRequest(BaseModel):
    flashcard_id: int = Field(
        ..., description="ID of the flashcard to generate examples for"
    )
    count: int = Field(..., description="Number of examples to generate", ge=1, le=10)


class ExampleModel(BaseModel):
    id: int
    flashcard_id: int
    example_text: str
    created_at: datetime


class ExamplesResponse(BaseModel):
    examples: List[ExampleModel]
    total: int
    flashcard_chinese: str


class FlashcardWithExamplesModel(BaseModel):
    id: int
    chinese: str
    pinyin: str
    definitions: List[str]
    examples: List[str] = []
    examples_count: int
