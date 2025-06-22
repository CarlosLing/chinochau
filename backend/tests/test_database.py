import pytest

from backend.db import ExampleDB, FlashcardDB
from backend.tests.conftest import TestingSessionLocal, test_db


class TestDatabaseModels:
    """Test cases for database models and operations"""

    def test_flashcard_creation(self, test_db):
        """Test creating a flashcard in the database"""
        db = TestingSessionLocal()

        flashcard = FlashcardDB(
            chinese="测试", pinyin="cè shì", definitions='["test", "testing"]'
        )

        db.add(flashcard)
        db.commit()
        db.refresh(flashcard)

        assert flashcard.id is not None
        assert flashcard.chinese == "测试"
        assert flashcard.pinyin == "cè shì"
        assert flashcard.definitions == '["test", "testing"]'

        # Test to_dict method
        flashcard_dict = flashcard.to_dict()
        assert flashcard_dict["id"] == flashcard.id
        assert flashcard_dict["chinese"] == "测试"
        assert flashcard_dict["pinyin"] == "cè shì"
        assert flashcard_dict["definitions"] == ["test", "testing"]

        db.close()

    def test_example_creation(self, test_db):
        """Test creating examples linked to a flashcard"""
        db = TestingSessionLocal()

        # First create a flashcard
        flashcard = FlashcardDB(
            chinese="学习", pinyin="xué xí", definitions='["study", "learn"]'
        )
        db.add(flashcard)
        db.commit()
        db.refresh(flashcard)

        # Create examples for the flashcard
        example1 = ExampleDB(flashcard_id=flashcard.id, example_text="我每天学习中文。")
        example2 = ExampleDB(flashcard_id=flashcard.id, example_text="学习是很重要的。")

        db.add(example1)
        db.add(example2)
        db.commit()
        db.refresh(example1)
        db.refresh(example2)

        assert example1.id is not None
        assert example1.flashcard_id == flashcard.id
        assert example1.example_text == "我每天学习中文。"
        assert example1.created_at is not None

        assert example2.id is not None
        assert example2.flashcard_id == flashcard.id
        assert example2.example_text == "学习是很重要的。"

        # Test to_dict method
        example_dict = example1.to_dict()
        assert example_dict["id"] == example1.id
        assert example_dict["flashcard_id"] == flashcard.id
        assert example_dict["example_text"] == "我每天学习中文。"
        assert example_dict["created_at"] == example1.created_at

        db.close()

    def test_flashcard_example_relationship(self, test_db):
        """Test the relationship between flashcards and examples"""
        db = TestingSessionLocal()

        # Create a flashcard
        flashcard = FlashcardDB(chinese="书", pinyin="shū", definitions='["book"]')
        db.add(flashcard)
        db.commit()
        db.refresh(flashcard)

        # Create multiple examples
        examples_data = ["这是一本好书。", "我正在读书。", "书店里有很多书。"]

        for example_text in examples_data:
            example = ExampleDB(flashcard_id=flashcard.id, example_text=example_text)
            db.add(example)

        db.commit()

        # Test the relationship
        flashcard_with_examples = (
            db.query(FlashcardDB).filter(FlashcardDB.id == flashcard.id).first()
        )
        assert len(flashcard_with_examples.examples) == 3

        example_texts = [ex.example_text for ex in flashcard_with_examples.examples]
        for expected_text in examples_data:
            assert expected_text in example_texts

        # Test reverse relationship
        first_example = flashcard_with_examples.examples[0]
        assert first_example.flashcard.chinese == "书"
        assert first_example.flashcard.id == flashcard.id

        db.close()

    def test_cascade_delete(self, test_db):
        """Test that examples are deleted when flashcard is deleted"""
        db = TestingSessionLocal()

        # Create flashcard with examples
        flashcard = FlashcardDB(
            chinese="删除", pinyin="shān chú", definitions='["delete"]'
        )
        db.add(flashcard)
        db.commit()
        db.refresh(flashcard)

        # Create examples
        example1 = ExampleDB(flashcard_id=flashcard.id, example_text="删除文件。")
        example2 = ExampleDB(flashcard_id=flashcard.id, example_text="请删除这个。")

        db.add(example1)
        db.add(example2)
        db.commit()

        # Verify examples exist
        examples_count = (
            db.query(ExampleDB).filter(ExampleDB.flashcard_id == flashcard.id).count()
        )
        assert examples_count == 2

        # Delete the flashcard
        db.delete(flashcard)
        db.commit()

        # Verify examples are also deleted (cascade)
        remaining_examples = (
            db.query(ExampleDB).filter(ExampleDB.flashcard_id == flashcard.id).count()
        )
        assert remaining_examples == 0

        db.close()
