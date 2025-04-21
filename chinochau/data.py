from dataclasses import dataclass
from typing import List


@dataclass
class Flashcard:
    chinese: str
    pinyin: str
    definitions: List[str] = None
    example: str = None
