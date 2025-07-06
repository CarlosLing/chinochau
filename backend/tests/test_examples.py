from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from backend.tests.conftest import (
    authenticated_client,
    client,
    sample_flashcard_data,
    test_db,
    test_user,
)


class TestExampleEndpoints:
    """Test cases for example-related endpoints"""

    def test_create_examples_for_nonexistent_flashcard(
        self, authenticated_client: TestClient, test_db
    ):
        """Test creating examples for a flashcard that doesn't exist"""
        request_data = {"flashcard_id": 999, "count": 2}
        response = authenticated_client.post("/examples", json=request_data)
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @patch("backend.services.example_service.get_examples_deepseek")
    def test_create_examples_success(
        self,
        mock_deepseek,
        authenticated_client: TestClient,
        test_db,
        sample_flashcard_data,
    ):
        """Test successfully creating examples for a flashcard"""
        # Mock the DeepSeek API response
        mock_deepseek.return_value = ["你好，今天天气真好！", "你好，很高兴认识你。"]

        # First create a flashcard
        flashcard_response = authenticated_client.post(
            "/flashcards", json=sample_flashcard_data
        )
        assert flashcard_response.status_code == 200
        flashcard_id = flashcard_response.json()["id"]

        # Create examples for the flashcard
        request_data = {"flashcard_id": flashcard_id, "count": 2}

        response = authenticated_client.post("/examples", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert "examples" in data
        assert "total" in data
        assert "flashcard_chinese" in data
        assert data["flashcard_chinese"] == sample_flashcard_data["chinese"]
        assert len(data["examples"]) == 2
        assert data["total"] == 2

        # Verify the mock was called with correct parameters
        mock_deepseek.assert_called_once_with(sample_flashcard_data["chinese"], 2)

    def test_get_examples_for_nonexistent_flashcard(
        self, authenticated_client: TestClient, test_db
    ):
        """Test getting examples for a flashcard that doesn't exist"""
        response = authenticated_client.get("/examples?flashcard_id=999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_examples_no_examples_available(
        self, authenticated_client: TestClient, test_db, sample_flashcard_data
    ):
        """Test getting examples when none are available"""
        # First create a flashcard
        flashcard_response = authenticated_client.post(
            "/flashcards", json=sample_flashcard_data
        )
        assert flashcard_response.status_code == 200
        flashcard_id = flashcard_response.json()["id"]

        # Try to get examples when none exist
        response = authenticated_client.get(f"/examples?flashcard_id={flashcard_id}")
        assert response.status_code == 404
        assert "no examples available" in response.json()["detail"].lower()

    @patch("backend.services.example_service.get_examples_deepseek")
    def test_get_examples_success(
        self,
        mock_deepseek,
        authenticated_client: TestClient,
        test_db,
        sample_flashcard_data,
    ):
        """Test successfully getting examples"""
        # Mock the DeepSeek API response
        mock_deepseek.return_value = ["你好，请问现在几点了？", "你好，我是来自美国的学生。", "你好，这里的食物很好吃。"]

        # First create a flashcard
        flashcard_response = authenticated_client.post(
            "/flashcards", json=sample_flashcard_data
        )
        assert flashcard_response.status_code == 200
        flashcard_id = flashcard_response.json()["id"]

        # Create examples first
        create_request = {"flashcard_id": flashcard_id, "count": 3}
        create_response = authenticated_client.post("/examples", json=create_request)
        assert create_response.status_code == 200

        # Now get the examples
        response = authenticated_client.get(f"/examples?flashcard_id={flashcard_id}")
        assert response.status_code == 200

        data = response.json()
        assert "examples" in data
        assert "total" in data
        assert "flashcard_chinese" in data
        assert data["flashcard_chinese"] == sample_flashcard_data["chinese"]
        assert len(data["examples"]) == 3
        assert data["total"] == 3

    def test_get_flashcard_with_examples_nonexistent(
        self, authenticated_client: TestClient, test_db
    ):
        """Test getting flashcard with examples for nonexistent flashcard"""
        response = authenticated_client.get("/flashcard-with-example?flashcard_id=999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_flashcard_with_examples_no_examples(
        self, authenticated_client: TestClient, test_db, sample_flashcard_data
    ):
        """Test getting flashcard with examples when no examples exist"""
        # First create a flashcard
        flashcard_response = authenticated_client.post(
            "/flashcards", json=sample_flashcard_data
        )
        assert flashcard_response.status_code == 200
        flashcard_id = flashcard_response.json()["id"]

        # Get flashcard with examples (should return empty examples list)
        response = authenticated_client.get(
            f"/flashcard-with-example?flashcard_id={flashcard_id}"
        )
        assert response.status_code == 200

        data = response.json()
        assert data["chinese"] == sample_flashcard_data["chinese"]
        assert "examples" in data
        assert data["examples"] == []
        assert data["examples_count"] == 0

    @patch("backend.services.example_service.get_examples_deepseek")
    def test_get_flashcard_with_examples_success(
        self,
        mock_deepseek,
        authenticated_client: TestClient,
        test_db,
        sample_flashcard_data,
    ):
        """Test successfully getting flashcard with examples"""
        # Mock the DeepSeek API response
        mock_deepseek.return_value = ["你好世界！", "你好，我叫小明。"]

        # First create a flashcard
        flashcard_response = authenticated_client.post(
            "/flashcards", json=sample_flashcard_data
        )
        assert flashcard_response.status_code == 200
        flashcard_id = flashcard_response.json()["id"]

        # Create examples
        create_request = {"flashcard_id": flashcard_id, "count": 2}
        create_response = authenticated_client.post("/examples", json=create_request)
        assert create_response.status_code == 200

        # Get flashcard with examples
        response = authenticated_client.get(
            f"/flashcard-with-example?flashcard_id={flashcard_id}"
        )
        assert response.status_code == 200

        data = response.json()
        assert data["chinese"] == sample_flashcard_data["chinese"]
        assert "examples" in data
        assert len(data["examples"]) == 2
        assert data["examples_count"] == 2
        assert "pinyin" in data
        assert "definitions" in data

    @patch("backend.services.example_service.get_examples_deepseek")
    def test_create_examples_api_failure(
        self,
        mock_deepseek,
        authenticated_client: TestClient,
        test_db,
        sample_flashcard_data,
    ):
        """Test handling API failure when creating examples"""
        # Mock API failure
        mock_deepseek.side_effect = Exception("API Error")

        # First create a flashcard
        flashcard_response = authenticated_client.post(
            "/flashcards", json=sample_flashcard_data
        )
        assert flashcard_response.status_code == 200
        flashcard_id = flashcard_response.json()["id"]

        # Try to create examples (should fail gracefully)
        request_data = {"flashcard_id": flashcard_id, "count": 2}
        response = authenticated_client.post("/examples", json=request_data)
        assert response.status_code == 500
        assert "failed to generate examples" in response.json()["detail"].lower()

    @patch("backend.services.example_service.get_examples_deepseek")
    def test_create_examples_empty_response(
        self,
        mock_deepseek,
        authenticated_client: TestClient,
        test_db,
        sample_flashcard_data,
    ):
        """Test handling empty response from examples API"""
        # Mock empty response
        mock_deepseek.return_value = []

        # First create a flashcard
        flashcard_response = authenticated_client.post(
            "/flashcards", json=sample_flashcard_data
        )
        assert flashcard_response.status_code == 200
        flashcard_id = flashcard_response.json()["id"]

        # Create examples with empty response
        request_data = {"flashcard_id": flashcard_id, "count": 2}
        response = authenticated_client.post("/examples", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert data["examples"] == []
        assert data["total"] == 0
