from pydantic import BaseModel, Field
from typing import List, Optional


class FlashcardModel(BaseModel):
    chinese: str
    pinyin: str
    definitions: List[str]
    example: Optional[str] = None


class FlashcardCreateModel(BaseModel):
    chinese: str


class TextInput(BaseModel):
    chinese: str


class ExamplesOutput(BaseModel):
    examples: List[str] = Field(
        ..., description="A list of example sentences in Chinese."
    )
