import os
from dataclasses import dataclass
from typing import List, Union
import pandas as pd
from dataclasses import fields


@dataclass
class Flashcard:
    chinese: str
    pinyin: str
    definitions: List[str]
    example: str = None


class MasterFlashcards:
    flashcards: dict

    """This class will contain the master Flashcards the main goal
    is to have caching of Flashcards to avoid reaching the Deepseek
    endpoints too often therefore saving cost"""

    def __init__(self, file="data/master.csv"):
        if file[-4:] != ".csv":
            raise ValueError("For the master datasource only '.csv' is supported")
        self._file_path = file
        if os.path.exists(file):
            self.flashcards_dataframe = pd.read_csv(file, index_col="chinese")
            if not set(self.flashcards_dataframe.columns) == {
                field.name for field in fields(Flashcard)
            }:
                print({field.name for field in fields(Flashcard)})
                raise ValueError(
                    f"Schema of the master data is invalid, {set(self.flashcards_dataframe.columns)}"
                )
        else:
            self.flashcards = {}
        self.words = self.flashcards.keys()

    def import_flashcards(self, flashcards=List[Flashcard]):
        new_flashcards = pd.DataFrame(
            [vars(card) for card in flashcards if card.chinese not in self.words]
        )
        updated_data = pd.concat([self.flashcards_dataframe, new_flashcards])
        self.flashcards_dataframe = updated_data
        self.save_flashcards()

    def save_flashcards(self):
        dataframe = pd.DataFrame.from_dict(self.flashcards, orient="index")
        dataframe.to_csv(self._file_path)

    def get(self, chinese: str) -> Union[Flashcard, None]:
        data = self.flashcards.get(chinese)
        if data is None:
            return None
        else:
            return Flashcard(chinese, **data)

    def get_flashcards_list(self) -> List[Flashcard]:
        raise NotImplementedError("TODO: Get flashcard list from a pandas dataframe")
