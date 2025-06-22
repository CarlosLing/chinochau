import json
from datetime import datetime

from passlib.context import CryptContext
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


def ensure_admin_user_exists():
    """Ensure that an admin user exists in the database for initial setup."""

    # Default admin credentials
    ADMIN_EMAIL = "admin@chinochau.local"
    ADMIN_PASSWORD = "admin123"  # Change this after first login!
    ADMIN_NAME = "Default Admin User"

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    db = SessionLocal()
    try:
        # Check if any users exist
        user_count = db.query(UserDB).count()

        if user_count == 0:
            print("🔄 No users found, creating default admin user...")

            # Create default admin user
            hashed_password = pwd_context.hash(ADMIN_PASSWORD)
            admin_user = UserDB(
                email=ADMIN_EMAIL,
                full_name=ADMIN_NAME,
                hashed_password=hashed_password,
                is_active=True,
                created_at=datetime.utcnow(),
            )

            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)

            print(f"✅ Created default admin user:")
            print(f"   Email: {ADMIN_EMAIL}")
            print(f"   Password: {ADMIN_PASSWORD}")
            print(f"   ⚠️  Please change the password after first login!")

            return admin_user
        else:
            print(f"ℹ️  Database already has {user_count} user(s)")
            return None

    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        db.rollback()
        return None
    finally:
        db.close()


# Note: Call ensure_admin_user_exists() manually when needed
# or from the main application startup
