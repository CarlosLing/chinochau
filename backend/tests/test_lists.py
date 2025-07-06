import pytest
from fastapi.testclient import TestClient

from backend.tests.conftest import (
    authenticated_client,
    client,
    sample_flashcard_data,
    test_db,
    test_user,
)


class TestListEndpoints:
    """Test cases for list-related endpoints"""

    def test_get_lists_empty(self, authenticated_client: TestClient, test_db):
        """Test getting lists when database is empty"""
        response = authenticated_client.get("/lists")
        assert response.status_code == 200
        assert response.json() == []

    def test_create_list(self, authenticated_client: TestClient, test_db):
        """Test creating a new list"""
        list_data = {"name": "My First List", "description": "A test list"}
        response = authenticated_client.post("/lists", json=list_data)
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == list_data["name"]
        assert data["description"] == list_data["description"]
        assert "id" in data
        assert "created_at" in data
        assert "modified_at" in data
        assert data["flashcard_count"] == 0
        assert data["flashcard_ids"] == []

    def test_create_list_minimal(self, authenticated_client: TestClient, test_db):
        """Test creating a list with minimal data"""
        list_data = {"name": "Minimal List"}
        response = authenticated_client.post("/lists", json=list_data)
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == list_data["name"]
        assert data["description"] == ""

    def test_get_list_by_id(self, authenticated_client: TestClient, test_db):
        """Test getting a specific list by ID"""
        # First create a list
        list_data = {"name": "Test List", "description": "Test description"}
        create_response = authenticated_client.post("/lists", json=list_data)
        assert create_response.status_code == 200
        list_id = create_response.json()["id"]

        # Then get it by ID
        response = authenticated_client.get(f"/lists/{list_id}")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == list_id
        assert data["name"] == list_data["name"]

    def test_get_nonexistent_list(self, authenticated_client: TestClient, test_db):
        """Test getting a list that doesn't exist"""
        response = authenticated_client.get("/lists/999999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_update_list(self, authenticated_client: TestClient, test_db):
        """Test updating a list"""
        # Create a list
        list_data = {"name": "Original Name", "description": "Original description"}
        create_response = authenticated_client.post("/lists", json=list_data)
        assert create_response.status_code == 200
        list_id = create_response.json()["id"]

        # Update the list
        update_data = {"name": "Updated Name", "description": "Updated description"}
        response = authenticated_client.put(f"/lists/{list_id}", json=update_data)
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["description"] == update_data["description"]

    def test_delete_list(self, authenticated_client: TestClient, test_db):
        """Test deleting a list"""
        # Create a list
        list_data = {"name": "To Be Deleted", "description": "This will be deleted"}
        create_response = authenticated_client.post("/lists", json=list_data)
        assert create_response.status_code == 200
        list_id = create_response.json()["id"]

        # Delete the list
        delete_response = authenticated_client.delete(f"/lists/{list_id}")
        assert delete_response.status_code == 200
        assert delete_response.json()["message"] == "List deleted successfully"

        # Verify it's gone
        get_response = authenticated_client.get(f"/lists/{list_id}")
        assert get_response.status_code == 404

    def test_add_flashcard_to_list(
        self, authenticated_client: TestClient, test_db, sample_flashcard_data
    ):
        """Test adding a flashcard to a list"""
        # Create a list
        list_data = {"name": "Flashcard List", "description": "List for flashcards"}
        list_response = authenticated_client.post("/lists", json=list_data)
        assert list_response.status_code == 200
        list_id = list_response.json()["id"]

        # Create a flashcard
        flashcard_response = authenticated_client.post(
            "/flashcards", json=sample_flashcard_data
        )
        assert flashcard_response.status_code == 200
        flashcard_id = flashcard_response.json()["id"]

        # Add flashcard to list
        response = authenticated_client.post(
            f"/lists/{list_id}/flashcards/{flashcard_id}"
        )
        assert response.status_code == 200
        assert response.json()["message"] == "Flashcard added to list successfully"

        # Verify the flashcard is in the list
        list_response = authenticated_client.get(f"/lists/{list_id}/flashcards")
        assert list_response.status_code == 200
        flashcards = list_response.json()["flashcards"]
        assert len(flashcards) == 1
        assert flashcards[0]["id"] == flashcard_id

    def test_remove_flashcard_from_list(
        self, authenticated_client: TestClient, test_db, sample_flashcard_data
    ):
        """Test removing a flashcard from a list"""
        # Create a list
        list_data = {"name": "Flashcard List", "description": "List for flashcards"}
        list_response = authenticated_client.post("/lists", json=list_data)
        assert list_response.status_code == 200
        list_id = list_response.json()["id"]

        # Create a flashcard
        flashcard_response = authenticated_client.post(
            "/flashcards", json=sample_flashcard_data
        )
        assert flashcard_response.status_code == 200
        flashcard_id = flashcard_response.json()["id"]

        # Add flashcard to list
        authenticated_client.post(f"/lists/{list_id}/flashcards/{flashcard_id}")

        # Remove flashcard from list
        response = authenticated_client.delete(
            f"/lists/{list_id}/flashcards/{flashcard_id}"
        )
        assert response.status_code == 200
        assert response.json()["message"] == "Flashcard removed from list successfully"
        assert response.status_code == 200
        assert response.json()["message"] == "Flashcard removed from list successfully"

        # Verify the flashcard is no longer in the list
        list_response = authenticated_client.get(f"/lists/{list_id}/flashcards")
        assert list_response.status_code == 200
        flashcards = list_response.json()["flashcards"]
        assert len(flashcards) == 0

    def test_get_list_with_multiple_flashcards(
        self, authenticated_client: TestClient, test_db
    ):
        """Test getting a list with multiple flashcards"""
        # Create a list
        list_data = {
            "name": "Multi Flashcard List",
            "description": "Multiple flashcards",
        }
        list_response = authenticated_client.post("/lists", json=list_data)
        assert list_response.status_code == 200
        list_id = list_response.json()["id"]

        # Create multiple flashcards and add them to the list
        flashcard_data_list = [{"chinese": "你好"}, {"chinese": "再见"}, {"chinese": "谢谢"}]
        flashcard_ids = []

        for flashcard_data in flashcard_data_list:
            flashcard_response = authenticated_client.post(
                "/flashcards", json=flashcard_data
            )
            assert flashcard_response.status_code == 200
            flashcard_id = flashcard_response.json()["id"]
            flashcard_ids.append(flashcard_id)

            # Add to list
            authenticated_client.post(f"/lists/{list_id}/flashcards/{flashcard_id}")

        # Get list with flashcards
        response = authenticated_client.get(f"/lists/{list_id}/flashcards")
        assert response.status_code == 200

        data = response.json()
        assert len(data["flashcards"]) == 3

        # Check that all flashcards are present
        returned_ids = [fc["id"] for fc in data["flashcards"]]
        for flashcard_id in flashcard_ids:
            assert flashcard_id in returned_ids

    def test_list_operations_unauthorized(self, client: TestClient, test_db):
        """Test list operations without authentication"""
        # Test creating a list without auth
        list_data = {"name": "Unauthorized List"}
        response = client.post("/lists", json=list_data)
        assert response.status_code == 401

        # Test getting lists without auth
        response = client.get("/lists")
        assert response.status_code == 401

        # Test deleting a list without auth
        response = client.delete("/lists/1")
        assert response.status_code == 401

    def test_add_nonexistent_flashcard_to_list(
        self, authenticated_client: TestClient, test_db
    ):
        """Test adding a non-existent flashcard to a list"""
        # Create a list
        list_data = {"name": "Test List", "description": "Test"}
        list_response = authenticated_client.post("/lists", json=list_data)
        assert list_response.status_code == 200
        list_id = list_response.json()["id"]

        # Try to add non-existent flashcard
        response = authenticated_client.post(f"/lists/{list_id}/flashcards/999999")
        assert response.status_code == 404

    def test_add_flashcard_to_nonexistent_list(
        self, authenticated_client: TestClient, test_db, sample_flashcard_data
    ):
        """Test adding a flashcard to a non-existent list"""
        # Create a flashcard
        flashcard_response = authenticated_client.post(
            "/flashcards", json=sample_flashcard_data
        )
        assert flashcard_response.status_code == 200
        flashcard_id = flashcard_response.json()["id"]

        # Try to add to non-existent list
        response = authenticated_client.post(f"/lists/999999/flashcards/{flashcard_id}")
        assert response.status_code == 404
