from sqlalchemy import Column, Integer, String, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import json

DATABASE_URL = "sqlite:///./flashcards.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class FlashcardDB(Base):
    __tablename__ = "flashcards"
    id = Column(Integer, primary_key=True, index=True)
    chinese = Column(String, unique=True, index=True, nullable=False)
    pinyin = Column(String, nullable=False)
    definitions = Column(Text, nullable=False)  # Store as JSON string
    example = Column(Text, nullable=True)

    def to_dict(self):
        return {
            "chinese": self.chinese,
            "pinyin": self.pinyin,
            "definitions": json.loads(self.definitions),
            "example": self.example,
        }

# Create tables
Base.metadata.create_all(bind=engine)
