import pinyin
import os
from pinyin.cedict import translate_word
from chinochau.data import Flashcard, MasterFlashcards
from chinochau.translate_google import translate_google


class ChinoChau:
    def __init__(
        self,
        source_file,
        generate_examples: bool = False,
        fill_null_definitions: bool = True,
    ):
        self.generate_examples = generate_examples
        self.fill_null_definitions = fill_null_definitions
        self.master_flashcards = MasterFlashcards()
        self.flashcards = []  # Initialize as empty; load_file will fill it
        self.source_file = source_file  # Store for later async loading

    async def load_file(self, source_file=None):
        if source_file is None:
            source_file = self.source_file
        if os.path.exists(source_file):
            with open(source_file, "r") as f:
                raw = f.read().replace("-", "").replace(" ", "")
                examples = raw.split("\n")
            flashcards = []
            for example in examples:
                if example.strip():
                    flashcard = await self.create_flashcard(example)
                    flashcards.append(flashcard)
            self.flashcards = flashcards
        else:
            print("File not available, using all master flashcards")
            self.flashcards = self.master_flashcards.get_flashcards_list()

    async def create_flashcard(self, chinese: str) -> Flashcard:
        f_pinyin = pinyin.get(chinese)
        f_definition = translate_word(chinese)
        if f_definition is None and self.fill_null_definitions:
            f_definition = await translate_google(chinese)

        if self.generate_examples:
            raise NotImplementedError("Example generation has not been implemented yet")
        else:
            example = None

        return Flashcard(
            chinese=chinese, pinyin=f_pinyin, definitions=f_definition, example=example
        )

    def update_master_flashcards(self):
        self.master_flashcards.import_flashcards(self.flashcards)

    def get(self, index: int) -> Flashcard:
        if len(self) <= index:
            raise ValueError("Index for flashcards out of bounds")
        return self.flashcards[index]

    def __len__(self):
        return len(self.flashcards)
