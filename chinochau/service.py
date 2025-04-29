import pinyin
from pinyin.cedict import translate_word
from chinochau.data import Flashcard, MasterFlashcards
from chinochau.translate_google import translate_google_sync


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
        self.load_file(source_file=source_file)

    def load_file(self, source_file):
        with open(source_file, "r") as f:
            raw = f.read().replace("-", "").replace(" ", "")
            examples = raw.split("\n")
        flashcards = []
        for example in examples:
            flashcards.append(self.create_flashcard(example))

        self.flashcards = flashcards

    def create_flashcard(self, chinese: str):
        f_pinyin = pinyin.get(chinese)
        f_definition = translate_word(chinese)
        if f_definition is None and self.fill_null_definitions:
            f_definition = translate_google_sync(chinese)

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
