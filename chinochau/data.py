import os
from dataclasses import dataclass
from typing import List
import pandas as pd


@dataclass
class Flashcard:
    chinese: str
    pinyin: str
    definitions: List[str] = None
    example: str = None


class MasterFlashcards:
    """This class will contain the master Flashcards the main goal
    is to have caching of Flashcards to avoid reaching the Deepseek
    endpoints too often therefore saving cost"""

    def __init__(self, file="data/master.csv"):
        if file[-4:] != ".csv":
            raise ValueError("For the master datasource only '.csv' is supported")
        self._file_path = file
        if os.path.exists(file):
            self.flashcards_dataframe = pd.read_csv(file)
        else:
            self.flashcards_dataframe = pd.DataFrame()

    def import_flashcards(self, flashcards=List[Flashcard]):

        new_data = pd.DataFrame([vars(card) for card in flashcards])

    def save_flashcards(self):
        self.flashcards_dataframe.to_csv(self._file_path)
