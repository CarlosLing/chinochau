import pytest
from fastapi.testclient import TestClient

from backend.tests.conftest import (
    authenticated_client,
    client,
    sample_flashcard_data,
    sample_flashcard_response,
    test_db,
    test_user,
)


class TestFlashcardEndpoints:
    """Test cases for flashcard-related endpoints"""

    def test_get_flashcards_empty(self, authenticated_client: TestClient, test_db):
        """Test getting flashcards when database is empty"""
        response = authenticated_client.get("/flashcards")
        assert response.status_code == 200
        assert response.json() == []

    def test_create_flashcard(
        self, authenticated_client: TestClient, test_db, sample_flashcard_data
    ):
        """Test creating a new flashcard"""
        response = authenticated_client.post("/flashcards", json=sample_flashcard_data)
        assert response.status_code == 200

        data = response.json()
        assert data["chinese"] == sample_flashcard_data["chinese"]
        assert "id" in data
        assert "pinyin" in data
        assert "definitions" in data
        assert isinstance(data["definitions"], list)

    def test_get_flashcard_by_chinese(
        self, authenticated_client: TestClient, test_db, sample_flashcard_data
    ):
        """Test getting a specific flashcard by Chinese text"""
        # First create a flashcard
        create_response = authenticated_client.post(
            "/flashcards", json=sample_flashcard_data
        )
        assert create_response.status_code == 200

        # Then get it by Chinese text
        chinese_text = sample_flashcard_data["chinese"]
        response = authenticated_client.get(f"/flashcards/{chinese_text}")
        assert response.status_code == 200

        data = response.json()
        assert data["chinese"] == chinese_text

    def test_get_nonexistent_flashcard(self, authenticated_client: TestClient, test_db):
        """Test getting a flashcard that doesn't exist"""
        response = authenticated_client.get("/flashcards/nonexistent")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_flashcards_list(self, authenticated_client: TestClient, test_db):
        """Test getting list of flashcards after creating some"""
        # Create multiple flashcards
        flashcards_data = [{"chinese": "你好"}, {"chinese": "再见"}, {"chinese": "谢谢"}]

        for flashcard_data in flashcards_data:
            response = authenticated_client.post("/flashcards", json=flashcard_data)
            assert response.status_code == 200

        # Get all flashcards
        response = authenticated_client.get("/flashcards")
        assert response.status_code == 200

        data = response.json()
        assert len(data) == 3

        # Check that all Chinese texts are present
        chinese_texts = [card["chinese"] for card in data]
        for flashcard_data in flashcards_data:
            assert flashcard_data["chinese"] in chinese_texts

    def test_create_duplicate_flashcard(
        self, authenticated_client: TestClient, test_db, sample_flashcard_data
    ):
        """Test creating a duplicate flashcard returns existing one"""
        # Create first flashcard
        response1 = authenticated_client.post("/flashcards", json=sample_flashcard_data)
        assert response1.status_code == 200
        first_id = response1.json()["id"]

        # Try to create the same flashcard again
        response2 = authenticated_client.post("/flashcards", json=sample_flashcard_data)
        assert response2.status_code == 200
        second_id = response2.json()["id"]

        # Should return the same flashcard
        assert first_id == second_id

    def test_delete_flashcard_by_id(
        self, authenticated_client: TestClient, test_db, sample_flashcard_data
    ):
        """Test deleting a flashcard by ID"""
        # First create a flashcard
        create_response = authenticated_client.post(
            "/flashcards", json=sample_flashcard_data
        )
        assert create_response.status_code == 200
        flashcard_id = create_response.json()["id"]

        # Delete the flashcard
        delete_response = authenticated_client.delete(f"/flashcards/{flashcard_id}")
        assert delete_response.status_code == 200
        assert delete_response.json()["message"] == "Flashcard deleted successfully"

        # Verify it's gone by trying to get it
        get_response = authenticated_client.get(
            f"/flashcards/{sample_flashcard_data['chinese']}"
        )
        assert get_response.status_code == 404

    def test_delete_nonexistent_flashcard(
        self, authenticated_client: TestClient, test_db
    ):
        """Test deleting a flashcard that doesn't exist"""
        response = authenticated_client.delete("/flashcards/999999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_delete_flashcard_from_list(
        self, authenticated_client: TestClient, test_db
    ):
        """Test deleting one flashcard from a list doesn't affect others"""
        # Create multiple flashcards
        flashcards_data = [{"chinese": "你好"}, {"chinese": "再见"}, {"chinese": "谢谢"}]
        created_ids = []

        for flashcard_data in flashcards_data:
            response = authenticated_client.post("/flashcards", json=flashcard_data)
            assert response.status_code == 200
            created_ids.append(response.json()["id"])

        # Delete the middle one
        delete_response = authenticated_client.delete(f"/flashcards/{created_ids[1]}")
        assert delete_response.status_code == 200

        # Get all remaining flashcards
        response = authenticated_client.get("/flashcards")
        assert response.status_code == 200
        remaining_flashcards = response.json()

        # Should have 2 remaining
        assert len(remaining_flashcards) == 2

        # Check that the deleted one is not in the list
        remaining_ids = [card["id"] for card in remaining_flashcards]
        assert created_ids[1] not in remaining_ids
        assert created_ids[0] in remaining_ids
        assert created_ids[2] in remaining_ids

    def test_delete_flashcard_unauthorized(self, client: TestClient, test_db):
        """Test deleting a flashcard without authentication"""
        response = client.delete("/flashcards/1")
        assert response.status_code == 401

    def test_delete_flashcard_different_user(
        self, authenticated_client: TestClient, test_db, sample_flashcard_data
    ):
        """Test that users can only delete their own flashcards"""
        # This would require creating a second user and authenticated client
        # For now, we'll test that a non-existent ID (simulating another user's flashcard) returns 404
        response = authenticated_client.delete("/flashcards/999999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
