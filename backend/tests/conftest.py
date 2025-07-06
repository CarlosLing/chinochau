import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.auth import create_access_token, get_password_hash
from backend.db import Base, UserDB, get_db
from backend.main import app

# Create a test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def test_db():
    """Create a fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def override_get_db():
    """Override the get_db dependency to use test database"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture
def test_user(test_db):
    """Create a test user and return user data"""
    db = TestingSessionLocal()
    try:
        # Create test user
        hashed_password = get_password_hash("testpassword")
        user = UserDB(
            email="test@example.com",
            full_name="Test User",
            hashed_password=hashed_password,
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    finally:
        db.close()


@pytest.fixture
def auth_headers(test_user):
    """Create authorization headers for test requests"""
    access_token = create_access_token(data={"sub": test_user.email})
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def authenticated_client(client, auth_headers):
    """Create a test client with authentication headers"""
    client.headers.update(auth_headers)
    return client


@pytest.fixture
def sample_flashcard_data():
    """Sample data for testing flashcard creation"""
    return {
        "chinese": "你好",
    }


@pytest.fixture
def sample_flashcard_response():
    """Sample flashcard response data"""
    return {
        "id": 1,
        "chinese": "你好",
        "pinyin": "nǐ hǎo",
        "definitions": ["hello", "hi"],
    }
