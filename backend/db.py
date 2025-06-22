import json
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

DATABASE_URL = "sqlite:///./flashcards.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship to flashcards
    flashcards = relationship(
        "FlashcardDB", back_populates="user", cascade="all, delete-orphan"
    )


class FlashcardDB(Base):
    __tablename__ = "flashcards"
    id = Column(Integer, primary_key=True, index=True)
    chinese = Column(String, index=True, nullable=False)
    pinyin = Column(String, nullable=False)
    definitions = Column(Text, nullable=False)  # Store as JSON string
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    user = relationship("UserDB", back_populates="flashcards")
    examples = relationship(
        "ExampleDB", back_populates="flashcard", cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "chinese": self.chinese,
            "pinyin": self.pinyin,
            "definitions": json.loads(self.definitions),
        }


class ExampleDB(Base):
    __tablename__ = "examples"
    id = Column(Integer, primary_key=True, index=True)
    flashcard_id = Column(Integer, ForeignKey("flashcards.id"), nullable=False)
    example_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship to flashcard
    flashcard = relationship("FlashcardDB", back_populates="examples")

    def to_dict(self):
        return {
            "id": self.id,
            "flashcard_id": self.flashcard_id,
            "example_text": self.example_text,
            "created_at": self.created_at,
        }


# Create tables
Base.metadata.create_all(bind=engine)
